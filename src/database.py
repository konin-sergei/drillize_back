# /src/database.py

import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config import settings

# Создаем движок базы данных
engine = create_async_engine(settings.DATABASE_URL, echo=False)


# Настройка уровня логирования для SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Создаем сессию
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


# Базовый класс для моделей
Base = declarative_base()


# Зависимость для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


