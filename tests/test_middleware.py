from middleware import BasicAuthMiddleware
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient


def create_app(enable_auth):
    async def homepage(request):
        return PlainTextResponse("Hello, world!")

    routes = [Route("/", endpoint=homepage)]
    app = Starlette(routes=routes)

    app.add_middleware(BasicAuthMiddleware, enable_auth=enable_auth)
    return app


def test_no_auth_required():
    app = create_app(enable_auth=False)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, world!"


def test_auth_required_success():
    app = create_app(enable_auth=True)
    client = TestClient(app)
    response = client.get("/", headers={"Authorization": "Basic ZGM6ZGM="})
    assert response.status_code == 200
    assert response.text == "Hello, world!"


def test_auth_required_failure():
    app = create_app(enable_auth=True)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Restricted"'
    assert response.text == "Unauthorized"


def test_auth_required_invalid_credentials():
    app = create_app(enable_auth=True)
    client = TestClient(app)
    response = client.get("/", headers={"Authorization": "Basic invalid"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Restricted"'
    assert response.text == "Unauthorized"
