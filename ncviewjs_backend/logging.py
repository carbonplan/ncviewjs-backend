import logging

from .config import get_settings


def get_logger() -> logging.Logger:
    settings = get_settings()
    if settings.environment == 'prod':
        return logging.getLogger("gunicorn")
    return logging.getLogger("uvicorn")
