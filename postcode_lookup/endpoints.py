import datetime
import functools
import os

from dateutil.parser import parse
from dc_api_client import (
    ApiError,
    BaseAPIClient,
    InvalidPostcodeException,
    InvalidUPRNException,
    LiveAPIBackend,
    MockAPIBackend,
    SandboxAPIBackend,
)
from markupsafe import Markup
from mock_responses import example_responses
from response_builder.v1.builders.ballots import StockLocalBallotBuilder
from response_builder.v1.generated_responses.candidates import all_candidates
from response_builder.v1.models.base import CancellationReason, RootModel
from response_builder.v1.sandbox import SANDBOX_POSTCODES
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from template_sorter import TemplateSorter
from utils import get_loader


async def base_postcode_form(request: Request, backend: BaseAPIClient = None):
    return get_loader(request).TemplateResponse(
        request, "index.html", context={"url_prefix": backend.URL_PREFIX}
    )


live_postcode_form = functools.partial(
    base_postcode_form, backend=LiveAPIBackend
)
sandbox_postcode_form = functools.partial(
    base_postcode_form, backend=SandboxAPIBackend
)
mock_postcode_form = functools.partial(
    base_postcode_form, backend=MockAPIBackend
)


async def base_postcode_endpoint(
    request: Request, backend: BaseAPIClient = None
):
    """
    Endpoint that handles postcode queries.

    There are three options for this endpoint:

    1. The postcode is invalid. In this case, redirect back to the postcode form
    2. The postcode is valid and there is an address picker. In this case, show the address picker
    3. The postcode is valid and there isn't an address picker. In this case show the postcode page.

    Supports "plugable" backends for swapping in the sandbox and mock backends.

    This function should not be used directly, rather pick one of the `functools.partial` functions defined below
    """
    if not backend:
        raise ValueError("Must specify a backend")

    postcode = request.query_params.get("postcode-search", None)
    if not postcode:
        return RedirectResponse(
            request.url_for(backend.URL_PREFIX + "_postcode_form_en")
        )

    if postcode == "FA1LL":
        return Response(status_code=400)
    if postcode == "FA2LL":
        assert False

    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_postcode(postcode)
    except (InvalidPostcodeException, ApiError) as e:
        query_param = (
            "api-error" if isinstance(e, ApiError) else "invalid-postcode"
        )
        return RedirectResponse(
            request.url_for(
                backend.URL_PREFIX + "_postcode_form_en"
            ).include_query_params(**{query_param: 1})
        )

    context = results_context(api_response, request, postcode, backend)

    template_sorter = TemplateSorter(context["api_response"])
    context["template_sorter"] = template_sorter
    template_name = template_sorter.main_template_name
    if context["api_response"].address_picker:
        template_name = "address_picker.html"

    return get_loader(request).TemplateResponse(
        request, template_name, context=context
    )


# Use functools.partial to create a view function per backend
live_postcode_view = functools.partial(
    base_postcode_endpoint, backend=LiveAPIBackend
)
sandbox_postcode_view = functools.partial(
    base_postcode_endpoint, backend=SandboxAPIBackend
)
mock_postcode_view = functools.partial(
    base_postcode_endpoint, backend=MockAPIBackend
)


async def base_uprn_endpoint(request: Request, backend=None):
    """
    Endpoint that handles UPRN views.

    Supports "plugable" backends for swapping in the sandbox and mock backends.

    This function should not be used directly, rather pick one of the `functools.partial` functions defined below
    """
    if not backend:
        raise ValueError("Must specify a backend")
    uprn = request.path_params["uprn"]
    postcode = request.path_params["postcode"]
    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_uprn(uprn)
    except (InvalidUPRNException, ApiError) as e:
        query_param = "api-error" if isinstance(e, ApiError) else "invalid-uprn"
        return RedirectResponse(
            request.url_for(
                backend.URL_PREFIX + "_postcode_form_en"
            ).include_query_params(**{query_param: 1})
        )
    context = results_context(api_response, request, postcode, backend)

    template_sorter = TemplateSorter(context["api_response"])
    context["template_sorter"] = template_sorter
    template_name = template_sorter.main_template_name
    if context["api_response"].address_picker:
        template_name = "address_picker.html"
    return get_loader(request).TemplateResponse(
        request, template_name, context=context
    )


live_uprn_view = functools.partial(base_uprn_endpoint, backend=LiveAPIBackend)
sandbox_uprn_view = functools.partial(
    base_uprn_endpoint, backend=SandboxAPIBackend
)


def results_context(api_response, request, postcode, backend):
    api_json = api_response

    context = {}
    context["api_response"] = RootModel.from_api_response(api_json)
    context["postcode"] = postcode
    context["uprn"] = request.path_params.get("uprn", None)
    context["url_prefix"] = backend.URL_PREFIX
    if context["uprn"]:
        context["route_name"] = "uprn"
    else:
        context["route_name"] = "postcode"

    if api_response.get("parl_recall_petition"):
        context["parl_recall_petition"] = api_response["parl_recall_petition"]
        if "signing_start" in context["parl_recall_petition"]:
            context["parl_recall_petition"]["signing_start"] = parse(
                context["parl_recall_petition"]["signing_start"]
            )
        if "signing_end" in context["parl_recall_petition"]:
            context["parl_recall_petition"]["signing_end"] = parse(
                context["parl_recall_petition"]["signing_end"]
            )
    context["current_date"] = str(datetime.date.today())

    return context


def get_ballot_stages(poll_open_date):
    return {
        "Polling day": poll_open_date,
        "After SOPNs": poll_open_date + datetime.timedelta(days=20),
        "Before SOPNs": poll_open_date + datetime.timedelta(days=35),
    }


async def redirect_root_to_postcode_form(request: Request):
    """
    We don't respond to "/" on the live site, but when in dev mode it's handy
    to load the dev server and see something useful at the root.

    This view will respond to the "/" url and show a handy page of links
    that this project does serve.

    NOTE: this will only show if we're in debug mode. If not, it'll raise a 404
    """
    if not request.app.debug:
        return Response(status_code=404)

    poll_open_date = datetime.date.today()
    ballot_stages = get_ballot_stages(poll_open_date)

    return get_loader(request).TemplateResponse(
        request,
        "debug_page.html",
        context={
            "sandbox_postcodes": SANDBOX_POSTCODES,
            "mock_postcodes": example_responses,
            "ballot_stages": ballot_stages,
        },
    )


def failover(request: Request):
    return Response(status_code=400)


async def section_tester(request: Request):
    template_name = "section_tester.html"

    sections = []

    if request.path_params["section"] == "cancellation_reasons":
        base_ballot = StockLocalBallotBuilder().with_candidates(all_candidates)
        for cancellation_reason in CancellationReason:
            ballot = base_ballot.with_cancellation_reason(
                cancellation_reason
            ).build()
            template = get_loader(request).TemplateResponse(
                request,
                "includes/cancellation_reasons.html",
                context={
                    "initial_poll_date": ballot.poll_open_date,
                    "ballot": ballot,
                },
            )

            sections.append(
                {
                    "content": Markup(template.body.decode()).replace(
                        "\\n", ""
                    ),
                    "title": cancellation_reason.name,
                }
            )

    return get_loader(request).TemplateResponse(
        request,
        template_name,
        context={
            "sections": sections,
        },
    )


async def design_system_view(request: Request):
    return get_loader(request).TemplateResponse(
        request,
        "design_system.html",
    )
