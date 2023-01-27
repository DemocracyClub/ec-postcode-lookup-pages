import pytest
from pydantic_factories.plugins.pytest_plugin import register_fixture
from starlette.testclient import TestClient

from app import app
from response_builder.v1.factories.councils import (
    RegistrationFactory,
    ElectoralServicesFactory,
)


@pytest.fixture(scope="function")
def app_client() -> TestClient:
    with TestClient(app=app) as client:
        yield client
