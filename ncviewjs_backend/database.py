import typing

from sqlmodel import Session, create_engine

from .config import get_settings


def get_session() -> Session:
    with Session(get_engine()) as session:
        yield session


def get_engine() -> typing.Any:
    settings = get_settings()
    return create_engine(settings.database_url, connect_args={"options": "-c timezone=utc"})
