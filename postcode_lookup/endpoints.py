import functools
import os

from dateutil.parser import parse
from dc_api_client import (
    BaseAPIClient,
    InvalidPostcodeException,
    InvalidUPRNException,
    LiveAPIBackend,
    SandboxAPIBackend,
)
from response_builder.v1.models.base import RootModel
from response_builder.v1.sandbox import SANDBOX_POSTCODES
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from utils import get_loader


async def base_postcode_form(request: Request, backend: BaseAPIClient = None):
    return get_loader(request).TemplateResponse(
        "index.html", {"request": request, "url_prefix": backend.URL_PREFIX}
    )


live_postcode_form = functools.partial(
    base_postcode_form, backend=LiveAPIBackend
)
sandbox_postcode_form = functools.partial(
    base_postcode_form, backend=SandboxAPIBackend
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
            api_key=os.environ.get("API_KEY", "ec-postcode-testing")
        ).get_postcode(postcode)
    except InvalidPostcodeException:
        return RedirectResponse(
            request.url_for(
                backend.URL_PREFIX + "_postcode_form_en"
            ).include_query_params(**{"invalid-postcode": 1})
        )
    context = results_context(api_response)
    context["request"] = request
    context["postcode"] = postcode
    context["url_prefix"] = backend.URL_PREFIX
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
    template_name = "result.html"
    if context["api_response"].address_picker:
        template_name = "address_picker.html"
    return get_loader(request).TemplateResponse(template_name, context)


# Use functools.partial to create a view function per backend
live_postcode_view = functools.partial(
    base_postcode_endpoint, backend=LiveAPIBackend
)
sandbox_postcode_view = functools.partial(
    base_postcode_endpoint, backend=SandboxAPIBackend
)


# TODO: mock_postcode_view = functools.partial(base_postcode_endpoint, backend=MockAPIBackend)


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
            api_key=os.environ.get("API_KEY", "ec-postcode-testing")
        ).get_uprn(uprn)
    except InvalidUPRNException:
        return RedirectResponse(
            request.url_for(
                backend.URL_PREFIX + "_postcode_form_en"
            ).include_query_params(**{"invalid-uprn": 1})
        )
    context = results_context(api_response)
    context["request"] = request
    context["postcode"] = postcode
    context["url_prefix"] = backend.URL_PREFIX
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
    template_name = "uprn.html"
    if context["api_response"].address_picker:
        template_name = "address_picker.html"
    return get_loader(request).TemplateResponse(template_name, context)


live_uprn_view = functools.partial(base_uprn_endpoint, backend=LiveAPIBackend)
sandbox_uprn_view = functools.partial(
    base_uprn_endpoint, backend=SandboxAPIBackend
)


def results_context(api_response):
    api_json = api_response
    return {
        "api_response": RootModel.from_api_response(api_json),
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

    return get_loader(request).TemplateResponse(
        "debug_page.html",
        {"request": request, "sandbox_postcodes": SANDBOX_POSTCODES},
    )


def failover(request: Request):
    return Response(status_code=400)
