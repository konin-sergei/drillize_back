# src/main.py

from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src import models
from src.api import users, auth, lessons, init
from src.api.contents import contents, contents_text, contents_file
from src.config import logger
from src.config import settings
from src.database import engine
from src.pages.service import router as router_service
from src.pages.site import router as router_site


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск FastAPI")
    # async with engine.begin() as conn:
    #     await conn.run_sync(models.Base.metadata.create_all)
    yield  # Yield control back to the application
    logger.info("Завершение FastAPI")


# Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

from src.middleware.limit import limiter, custom_rate_limit_handler

# Инициализация FastAPI с использованием lifespan
app = FastAPI(lifespan=lifespan)

# Добавляем middleware для обработки лимитов
app.add_middleware(SlowAPIMiddleware)

# Обработчик ошибки при превышении лимита
app.state.limiter = limiter


app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

if settings.DEBUG:
    settings.CORS_ORIGINS = ["*"]

# settings.CORS_ORIGINS = [
# 	"http://127.0.0.1:7000",
# 	"http://localhost:7000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.requests import HTTPConnection


# Публичные маршруты, которые не требуют аутентификации
PUBLIC_PATHS = ["/", "/courses", "/static_back", "/media", "/docs", "/openapi.json", "/redoc"]


# Определяем кастомный AuthenticationBackend
class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        # В режиме разработки всегда разрешаем доступ
        # Проверяем, является ли путь публичным
        path = conn.url.path
        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS):
            # Для публичных маршрутов возвращаем анонимного пользователя
            # с credentials, чтобы не 
            return AuthCredentials(["public", "authenticated"]), SimpleUser("anonymous")
        
        # Для остальных маршрутов тоже разрешаем доступ в режиме разработки
        # В реальном коде логика аутентификации должна проверять заголовки, куки или токены
        user = SimpleUser("test@example.com")  # Тестовый пользователь
        return AuthCredentials(["authenticated"]), user


# # Добавляем middleware
# # В режиме разработки можно временно отключить AuthenticationMiddleware
# # если он блокирует доступ к публичным маршрутам
# if not settings.DEBUG:
#     # В продакшене используем AuthenticationMiddleware
#     app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
# else:
#     # В режиме разработки можно отключить, если возникают проблемы с 403
#     # Раскомментируйте следующую строку, если AuthenticationMiddleware блокирует доступ:
#     # app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
#     pass

# Подключение статических файлов и медиа
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")
app.mount("/static_back", StaticFiles(directory="public/static_back"), name="static_back")

# Подключение маршрутов
# app.include_router(auth.router, tags=["auth"])
# app.include_router(users.router, prefix="", tags=["users"])
# app.include_router(lessons.router, prefix="", tags=["lessons"])
# app.include_router(init.router, prefix="", tags=["init"])
app.include_router(router_site, tags=["HTML site"])
# app.include_router(router_service, tags=["HTML service"])
# app.include_router(contents.router, prefix="", tags=["contents"])
# app.include_router(contents_text.router, prefix="", tags=["contents_text"])
# app.include_router(contents_file.router, prefix="", tags=["contents_file"])

from src.filters.main_filters import format_sum_accuracy_0  # Импортируем фильтр

# Шаблоны Jinja2
templates = Jinja2Templates(directory="templates")

templates.env.filters["format_sum_accuracy_0"] = format_sum_accuracy_0


# так тоже не работает
# import jinja2
# env = jinja2.Environment()
# env.filters["format_sum_accuracy_0"] = format_sum_accuracy_0

# Middleware для логирования запросов и ошибок
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")  # Логирование запросов
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")  # Логирование ответов
        return response
    except Exception as e:
        logger.error(f"Unhandled exception during request: {str(e)}", exc_info=True)
        raise


# Обработчик ошибок HTTP
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error occurred: {exc.detail} (status: {exc.status_code}) | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Обработчик неожиданных ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# Обработчик ошибок 404 (возвращает JSON)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"404 Not Found: {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"},
    )


if __name__ == '__main__':
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=7000)
    # uvicorn.run(app, host="192.168.1.127", port=7000)
    uvicorn.run(app, host="127.0.0.1", port=7000)
