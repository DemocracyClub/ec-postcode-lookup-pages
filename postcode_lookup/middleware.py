from starlette.requests import HTTPConnection
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


class BasicAuthMiddleware:
    def __init__(self, app: ASGIApp, enable_auth: bool) -> None:
        self.enable_auth = enable_auth
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        conn = HTTPConnection(scope)

        if not self.enable_auth:
            await self.app(scope, receive, send)
            return

        required_auth_header = "Basic ZGM6ZGM="  # "dc:dc" in base64

        # Check for authorization header:
        auth_header = conn.headers.get("Authorization")
        if auth_header and auth_header == required_auth_header:
            await self.app(scope, receive, send)
            return

        # If authorization fails, return 401 Unauthorized and prompt for credentials
        response = Response(
            "Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Restricted"'},
        )
        await response(scope, receive, send)
        return
