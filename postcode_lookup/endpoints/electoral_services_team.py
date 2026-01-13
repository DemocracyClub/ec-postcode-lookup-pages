import functools
import os

from dc_api_client import (
    ApiError,
    BaseAPIClient,
    InvalidPostcodeException,
    InvalidUPRNException,
    LiveAPIBackend,
    MockAPIBackend,
    SandboxAPIBackend,
)
from endpoints.utils import results_context
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from utils import get_loader


async def base_postcode_endpoint(
    request: Request, backend: BaseAPIClient = None
):
    if not backend:
        raise ValueError("Must specify a backend")

    postcode = request.query_params.get("postcode-search", None)
    if not postcode:
        raise Exception("oh noes - TODO")

    if postcode == "FA1LL":
        return Response(status_code=400)
    if postcode == "FA2LL":
        assert False

    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_postcode(postcode)
    except (InvalidPostcodeException, ApiError):
        raise Exception("oh noes - TODO")

    context = results_context(
        api_response,
        request,
        postcode,
        f"electoral_services_{backend.URL_PREFIX}",
    )

    template_name = "electoral_services_team_results.html"
    if (
        context["api_response"].address_picker
        and not context["api_response"].electoral_services
    ):
        template_name = "address_picker.html"

    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return JSONResponse({"json": "data"})

    return get_loader(request).TemplateResponse(
        request,
        template_name,
        context=context,
    )


live_postcode_view = functools.partial(
    base_postcode_endpoint, backend=LiveAPIBackend
)
sandbox_postcode_view = functools.partial(
    base_postcode_endpoint, backend=SandboxAPIBackend
)
mock_postcode_view = functools.partial(
    base_postcode_endpoint, backend=MockAPIBackend
)


async def base_uprn_endpoint(request: Request, backend: BaseAPIClient = None):
    if not backend:
        raise ValueError("Must specify a backend")

    uprn = request.path_params["uprn"]
    postcode = request.path_params["postcode"]

    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_uprn(uprn)
    except (InvalidUPRNException, ApiError):
        raise Exception("oh noes - TODO")

    context = results_context(
        api_response,
        request,
        postcode,
        f"electoral_services_{backend.URL_PREFIX}",
    )

    template_name = "electoral_services_team_results.html"
    if (
        context["api_response"].address_picker
        and not context["api_response"].electoral_services
    ):
        template_name = "address_picker.html"

    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return JSONResponse({"json": "data"})

    return get_loader(request).TemplateResponse(
        request,
        template_name,
        context=context,
    )


live_uprn_view = functools.partial(base_uprn_endpoint, backend=LiveAPIBackend)
sandbox_uprn_view = functools.partial(
    base_uprn_endpoint, backend=SandboxAPIBackend
)
