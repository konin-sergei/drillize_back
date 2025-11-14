# src/config.py

import logging
import os
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = str(Path(__file__).resolve().parent.parent)
PATH_ENV_FILE = f"{BASE_DIR}/.env"

class Settings(BaseSettings):
    SERVER_TYPE: str = ""
    GOOGLE_CAPTCHA_V3_SECRET_KEY: str = ""
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    REDIS_URL: str = ""
    UPLOAD_DIRECTORY: str = ""
    SENTRY_DSN: str = ""
    STATIC_DIR: str = ""
    LOG_DIR: str = ""
    MEDIA_DIR: str = ""
    CORS_ORIGINS: str = ""
    OPENAI_ORGANIZATION: str = ""
    OPENAI_KEY: str = ""
    DEBUG: bool = False

    SERVICE_EMAIL_HOST: str = ""
    SERVICE_EMAIL_PORT: str = ""
    SERVICE_EMAIL_USER: str = ""
    SERVICE_EMAIL_PASSWORD: str = ""

    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0

    BASE_DIR: Path = BASE_DIR

    FILE_SETTINGS: Dict[str, Dict[str, Any]] = {
        'audio': {
            'extensions': {"mp3"},
            'max_size': 200 * 1024 * 1024  # 200 MB
        },
        'image': {
            'extensions': {"jpg", "jpeg", "png", "gif", "bmp", "tiff"},
            'max_size': 100 * 1024 * 1024  # 100 MB
        },
        'video': {
            'extensions': {"mp4", "avi", "mov", "mkv"},
            'max_size': 8 * 1024 * 1024 * 1024  # 8 GB
        }
    }

    model_config = SettingsConfigDict(
        env_file=PATH_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Создаём экземпляр настроек
settings = Settings()

# Создаём директорию для логов, если её нет
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Глобальный логгер
LOG_FILE = os.path.join(settings.LOG_DIR, 'app.log')

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,  # Включаем DEBUG при разработке
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("drillize")  # Логгер для всего приложения

# Создание директории, если она не существует
Path(settings.UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

