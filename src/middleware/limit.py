# /src/middleware/limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi import FastAPI, Request

from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)
from slowapi.errors import RateLimitExceeded

async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Возвращает кастомное сообщение о превышении лимита"""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )
