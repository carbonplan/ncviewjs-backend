import typing

import pydantic

from .logging import get_logger

logger = get_logger()


class Settings(pydantic.BaseSettings):
    environment: typing.Literal['dev', 'prod'] = 'dev'
    testing: bool = False
    database_url: pydantic.AnyUrl = None
    scratch_bucket: pydantic.AnyUrl | pydantic.DirectoryPath = (
        's3://carbonplan-data-viewer-staging/tmp'
    )
    staging_bucket: pydantic.AnyUrl | pydantic.DirectoryPath = 's3://carbonplan-data-viewer-staging'
    production_bucket: pydantic.AnyUrl | pydantic.DirectoryPath = (
        's3://carbonplan-data-viewer-production'
    )

    @pydantic.validator('database_url', pre=True)
    def database_url_from_env(cls, value: str) -> str:
        # Fix Heroku's incompatible postgres database uri
        # https://stackoverflow.com/a/67754795/3266235
        if value is not None and value.startswith('postgres://'):
            logger.info('Fixing Heroku\'s incompatible postgres database uri')
            return value.replace('postgres://', 'postgresql://', 1)
        return value


def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()
