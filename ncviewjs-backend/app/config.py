import logging
import typing

import pydantic

logger = logging.getLogger('uvicorn')


class Settings(pydantic.BaseSettings):
    environment: typing.Literal['dev', 'staging', 'production'] = 'dev'
    testing: bool = False


def get_settings() -> pydantic.BaseSettings:
    logger.info('Loading config settigns from the environment...')
    return Settings()
