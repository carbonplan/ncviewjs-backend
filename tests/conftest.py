import os

import pytest
from fastapi.testclient import TestClient

from ncviewjs_backend.config import Settings, get_settings
from ncviewjs_backend.main import create_application


def get_settings_override():
    return Settings(testing=1, database_url=os.environ.get("DATABASE_URL"))


@pytest.fixture(scope="module")
def test_app():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_app_with_db():
    app = create_application()
    app.dependency_overrides[get_settings] = get_settings_override

    with TestClient(app) as test_client:
        yield test_client
