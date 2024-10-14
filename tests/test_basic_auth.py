import importlib

import app
import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "environment,status_code",
    [("development", 401), ("staging", 401), ("production", 200)],
)
def test_basic_auth(monkeypatch, environment, status_code):
    monkeypatch.setenv("DC_ENVIRONMENT", environment)
    # We reload the app here because the original import happens before the monkeypatched DC_ENVIRONMENT
    # variable and therefore it wouldn't see the new env variable when its called in the TestClient's instantiation
    importlib.reload(app)

    with TestClient(app=app.app) as client:
        resp = client.get("/")
        assert resp.status_code == status_code
