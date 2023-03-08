import uvicorn
from multiprocessing import Process
from random import randrange

import pytest
from starlette.testclient import TestClient

from app import app


@pytest.fixture(scope="function")
def app_client() -> TestClient:
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
def uvicorn_server():
    port = randrange(8010, 8100)
    proc = Process(
        target=uvicorn.run,
        args=("app:app",),
        kwargs={
            "host": "127.0.0.1",
            "port": port,
            "workers": 1,
            "access_log": False,
            "log_level": "critical",
        },
    )
    proc.start()
    import time

    time.sleep(0.3)
    yield f"http://localhost:{port}"
    proc.kill()
