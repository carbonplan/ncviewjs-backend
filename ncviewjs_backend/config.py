import typing

import pydantic

from .logging import get_logger

logger = get_logger()


class Settings(pydantic.BaseSettings):
    environment: typing.Literal['dev', 'prod'] = 'dev'
    testing: bool = False
    database_url: pydantic.AnyUrl = None


def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()
