import logging


def get_logger() -> logging.Logger:
    return logging.Logger("uvicorn")
