from pathlib import Path

from mangum import Mangum
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, Mount

from starlette.staticfiles import StaticFiles

from endpoints import postcode_form, live_postcode_view, uprn, redirect_root_to_postcode_form, sandbox_postcode_view
from utils import i18nMiddleware, ForwardedForMiddleware

routes = [
    Route("/", endpoint=redirect_root_to_postcode_form),
    Route(
        "/i-am-a/voter/your-election-information",
        endpoint=postcode_form,
        name="postcode_form_en",
    ),
    Route("/polling-stations/{postcode}/{uprn}", endpoint=uprn),
    Route("/polling-stations", endpoint=live_postcode_view, name="postcode_en"),
    Route(
        "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
        endpoint=postcode_form,
        name="postcode_form_cy",
    ),
    Route("/cy/polling-stations/{postcode}/{uprn}", endpoint=uprn),
    Route(
        "/cy/polling-stations", endpoint=live_postcode_view, name="postcode_cy"
    ),
    # Sandbox
    Route(
        "/sandbox/polling-stations",
        endpoint=sandbox_postcode_view,
        name="sandbox_postcode_en",
    ),
    Route(
        "/cy/sandbox/polling-stations",
        endpoint=sandbox_postcode_view,
        name="sandbox_postcode_cy",
    ),
    Mount(
        "/themes/",
        app=StaticFiles(directory=Path(__file__).parent / "themes"),
        name="themes",
    ),
    Mount(
        "/static/",
        app=StaticFiles(directory=Path(__file__).parent / "static"),
        name="static",
    ),
]

app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(i18nMiddleware),
        Middleware(ForwardedForMiddleware),
    ],
)

handler = Mangum(app)
