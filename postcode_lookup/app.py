from pathlib import Path

from mangum import Mangum
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, Mount

from starlette.staticfiles import StaticFiles

from endpoints import (
    live_postcode_view,
    redirect_root_to_postcode_form,
    sandbox_postcode_view,
    failover,
    live_uprn_view,
    sandbox_uprn_view,
    live_postcode_form,
)
from utils import i18nMiddleware, ForwardedForMiddleware

routes = [
    Route("/", endpoint=redirect_root_to_postcode_form),
    Route("/failover", endpoint=failover),
    Route(
        "/i-am-a/voter/your-election-information",
        endpoint=live_postcode_form,
        name="live_postcode_form_en",
    ),
    Route(
        "/polling-stations/address/{postcode}/{uprn}",
        endpoint=live_uprn_view,
        name="live_uprn_en",
    ),
    Route(
        "/polling-stations",
        endpoint=live_postcode_view,
        name="live_postcode_en",
    ),
    Route(
        "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
        endpoint=live_postcode_form,
        name="live_postcode_form_cy",
    ),
    Route(
        "/cy/polling-stations/{postcode}/{uprn}",
        endpoint=live_uprn_view,
        name="live_uprn_cy",
    ),
    Route(
        "/cy/polling-stations",
        endpoint=live_postcode_view,
        name="live_postcode_cy",
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
    Route(
        "/sandbox/polling-stations/{postcode}/{uprn}",
        endpoint=sandbox_uprn_view,
        name="sandbox_uprn_en",
    ),
    Route(
        "/cy/sandbox/polling-stations/{postcode}/{uprn}",
        endpoint=sandbox_uprn_view,
        name="sandbox_uprn_cy",
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
