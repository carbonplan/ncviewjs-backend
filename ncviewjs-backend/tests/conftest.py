import os

import pytest
from app.config import Settings, get_settings
from fastapi.testclient import TestClient

from app import main


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_URL"))


@pytest.fixture(scope="module")
def test_app():
    main.app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(main.app) as test_client:
        yield test_client
