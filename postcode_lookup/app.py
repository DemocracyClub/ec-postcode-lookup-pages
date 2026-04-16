import os
from pathlib import Path

import endpoints.election_information
import endpoints.electoral_services_team
import endpoints.utils
from mangum import Mangum
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import HTTPConnection
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette_babel import LocaleMiddleware, get_translator
from utils import ForwardedForMiddleware, i18nMiddleware

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


def redirect(route_name):
    async def endpoint(request):
        url = request.url_for(route_name)
        return RedirectResponse(url)

    return endpoint


util_routes = [
    Route("/", endpoint=endpoints.utils.redirect_root_to_postcode_form),
    Route("/sections/{section}/", endpoint=endpoints.utils.section_tester),
    Route("/failover", endpoint=endpoints.utils.failover, name="failover"),
    Route(
        "/design-system",
        endpoint=endpoints.utils.design_system_view,
        name="design_system_view",
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

election_information_routes = [
    # Live, EN
    Route(
        "/i-am-a/voter/your-election-information",
        endpoint=endpoints.election_information.live_postcode_form,
        name="live_postcode_form_en",
    ),
    Route(
        "/polling-stations/address/{postcode}/{uprn}",
        endpoint=endpoints.election_information.live_uprn_view,
        name="live_uprn_en",
    ),
    Route(
        "/polling-stations",
        endpoint=endpoints.election_information.live_postcode_view,
        name="live_postcode_en",
    ),
    # Live, CY
    Route(
        "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
        endpoint=endpoints.election_information.live_postcode_form,
        name="live_postcode_form_cy",
    ),
    Route(
        # TODO: this should be
        # "/cy/polling-stations/address/{postcode}/{uprn}",
        "/cy/polling-stations/{postcode}/{uprn}",
        endpoint=endpoints.election_information.live_uprn_view,
        name="live_uprn_cy",
    ),
    Route(
        "/cy/polling-stations",
        endpoint=endpoints.election_information.live_postcode_view,
        name="live_postcode_cy",
    ),
    # Sandbox, EN
    Route(
        "/sandbox/i-am-a/voter/your-election-information",
        endpoint=endpoints.election_information.sandbox_postcode_form,
        name="sandbox_postcode_form_en",
    ),
    Route(
        "/sandbox/polling-stations/address/{postcode}/{uprn}",
        endpoint=endpoints.election_information.sandbox_uprn_view,
        name="sandbox_uprn_en",
    ),
    Route(
        "/sandbox/polling-stations",
        endpoint=endpoints.election_information.sandbox_postcode_view,
        name="sandbox_postcode_en",
    ),
    # Sandbox, CY
    Route(
        "/cy/sandbox/i-am-a/voter/your-election-information",
        endpoint=endpoints.election_information.sandbox_postcode_form,
        name="sandbox_postcode_form_cy",
    ),
    Route(
        "/cy/sandbox/polling-stations/address/{postcode}/{uprn}",
        endpoint=endpoints.election_information.sandbox_uprn_view,
        name="sandbox_uprn_cy",
    ),
    Route(
        "/cy/sandbox/polling-stations",
        endpoint=endpoints.election_information.sandbox_postcode_view,
        name="sandbox_postcode_cy",
    ),
    # Mock
    Route(
        "/mock/polling-stations",
        endpoint=endpoints.election_information.mock_postcode_view,
        name="mock_postcode_en",
    ),
    Route(
        "/cy/mock/polling-stations",
        endpoint=endpoints.election_information.mock_postcode_view,
        name="mock_postcode_cy",
    ),
]

electoral_services_team_routes = [
    # Live, EN
    Route(
        "/voting-and-elections/get-help-with-my-vote",
        endpoint=endpoints.electoral_services_team.live_postcode_form,
        name="electoral_services_live_postcode_form_en",
    ),
    Route(
        "/voting-and-elections/get-help-with-my-vote/postcode",
        endpoint=redirect("electoral_services_live_postcode_form_en"),
    ),
    Route(
        "/voting-and-elections/get-help-with-my-vote/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.live_postcode_view,
        name="electoral_services_live_postcode_en",
    ),
    Route(
        "/voting-and-elections/get-help-with-my-vote/address",
        endpoint=redirect("electoral_services_live_postcode_form_en"),
    ),
    Route(
        "/voting-and-elections/get-help-with-my-vote/address/{postcode}/{uprn}",
        endpoint=endpoints.electoral_services_team.live_uprn_view,
        name="electoral_services_live_uprn_en",
    ),
    # Live, CY
    Route(
        "/cy/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais",
        endpoint=endpoints.electoral_services_team.live_postcode_form,
        name="electoral_services_live_postcode_form_cy",
    ),
    Route(
        "/cy/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/postcode",
        endpoint=redirect("electoral_services_live_postcode_form_cy"),
    ),
    Route(
        "/cy/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.live_postcode_view,
        name="electoral_services_live_postcode_cy",
    ),
    Route(
        "/cy/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/address",
        endpoint=redirect("electoral_services_live_postcode_form_cy"),
    ),
    Route(
        "/cy/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/address/{postcode}/{uprn}",
        endpoint=endpoints.electoral_services_team.live_uprn_view,
        name="electoral_services_live_uprn_cy",
    ),
    # Sandbox, EN
    Route(
        "/sandbox/voting-and-elections/get-help-with-my-vote/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.sandbox_postcode_view,
        name="electoral_services_sandbox_postcode_en",
    ),
    Route(
        "/sandbox/voting-and-elections/get-help-with-my-vote/address/{postcode}/{uprn}",
        endpoint=endpoints.electoral_services_team.sandbox_uprn_view,
        name="electoral_services_sandbox_uprn_en",
    ),
    # Sandbox, CY
    Route(
        "/cy/sandbox/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.sandbox_postcode_view,
        name="electoral_services_sandbox_postcode_cy",
    ),
    Route(
        "/cy/sandbox/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/address/{postcode}/{uprn}",
        endpoint=endpoints.electoral_services_team.sandbox_uprn_view,
        name="electoral_services_sandbox_uprn_cy",
    ),
    # Mock
    Route(
        "/mock/voting-and-elections/get-help-with-my-vote/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.mock_postcode_view,
        name="electoral_services_mock_postcode_en",
    ),
    Route(
        "/cy/mock/pleidleisio-ac-etholiadau/cael-help-gyda-fy-mhleidlais/postcode/{postcode}",
        endpoint=endpoints.electoral_services_team.mock_postcode_view,
        name="electoral_services_mock_postcode_cy",
    ),
]

routes = (
    util_routes + election_information_routes + electoral_services_team_routes
)

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
