import os
from pathlib import Path

from endpoints import (
    design_system_view,
    failover,
    live_postcode_form,
    live_postcode_view,
    live_uprn_view,
    mock_postcode_view,
    redirect_root_to_postcode_form,
    sandbox_postcode_form,
    sandbox_postcode_view,
    sandbox_uprn_view,
    section_tester,
)
from mangum import Mangum
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import HTTPConnection
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_babel import LocaleMiddleware, get_translator
from utils import ForwardedForMiddleware, i18nMiddleware

from postcode_lookup.endpoints import (
    mock_contact_details_form,
    mock_contact_details_results,
)

environment = os.environ.get("DC_ENVIRONMENT", "local")

if sentry_dsn := os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            AwsLambdaIntegration(),
        ],
    )

routes = [
    Route("/", endpoint=redirect_root_to_postcode_form),
    Route("/sections/{section}/", endpoint=section_tester),
    Route("/failover", endpoint=failover, name="failover"),
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
        "/sandbox/i-am-a/voter/your-election-information",
        endpoint=sandbox_postcode_form,
        name="sandbox_postcode_form_en",
    ),
    Route(
        "/sandbox/cy/i-am-a/voter/your-election-information",
        endpoint=sandbox_postcode_form,
        name="sandbox_postcode_form_cy",
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
    # Mock
    Route(
        "/mock/polling-stations",
        endpoint=mock_postcode_view,
        name="mock_postcode_en",
    ),
    Route(
        "/cy/mock/polling-stations",
        endpoint=mock_postcode_view,
        name="mock_postcode_cy",
    ),
    # Contact details
    Route(
        "/mock/i-am-a/voter/find-contact-details",
        endpoint=mock_contact_details_form,
        name="mock_contact_details_view",
    ),
    Route(
        "/mock/i-am-a/voter/contact-details",
        endpoint=mock_contact_details_results,
        name="mock_contact_details_en",
    ),
    Route(
        "/design-system",
        endpoint=design_system_view,
        name="design_system_view",
    ),
    # Route(
    #     "/mock/polling-stations/{postcode}/{uprn}",
    #     endpoint=sandbox_uprn_view,
    #     name="sandbox_uprn_en",
    # ),
    # Route(
    #     "/cy/sandbox/polling-stations/{postcode}/{uprn}",
    #     endpoint=sandbox_uprn_view,
    #     name="sandbox_uprn_cy",
    # ),
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

shared_translator = get_translator()  # process global instance
shared_translator.load_from_directories([Path(__file__).parent / "locale"])


def current_language_selector(conn: HTTPConnection) -> str | None:
    return conn.scope["current_language"]


app = Starlette(
    debug=(environment != "production"),
    routes=routes,
    middleware=[
        Middleware(i18nMiddleware),
        Middleware(
            LocaleMiddleware,
            locales=["en", "cy"],
            default_locale="en",
            selectors=[current_language_selector],
        ),
        Middleware(ForwardedForMiddleware),
    ],
)

handler = Mangum(app)
