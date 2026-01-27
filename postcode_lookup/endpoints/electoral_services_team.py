import functools
import json
import os
from urllib.parse import quote

from dc_api_client import (
    ApiError,
    BaseAPIClient,
    InvalidPostcodeException,
    InvalidUPRNException,
    LiveAPIBackend,
    MockAPIBackend,
    SandboxAPIBackend,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette_babel.translator import gettext as _
from utils import get_loader, results_context


def preprocess_api_response(data, request, postcode, url_prefix):
    # only show address picker if the postcode is split between more than one council
    if data["electoral_services"]:
        data["addresses"] = []
        data["address_picker"] = False

    # re-write address picker URLs
    for address in data["addresses"]:
        address["url"] = str(
            request.url_for(
                url_prefix + "_uprn_" + request.scope["current_language"],
                postcode=quote(postcode, safe=""),
                uprn=quote(address["slug"], safe=""),
            )
        )

    # strip fields we don't need
    fields = [
        "address_picker",
        "addresses",
        "electoral_services",
        "registration",
        "postcode_location",
    ]
    return {k: v for k, v in data.items() if k in fields}


async def base_postcode_form(request: Request, backend: BaseAPIClient = None):
    url_prefix = f"electoral_services_{backend.URL_PREFIX}"
    return get_loader(request).TemplateResponse(
        request,
        "electoral_services_team_search.html",
        context={
            "url_prefix": url_prefix,
            "js_strings": json.dumps(
                {
                    "postcode_input_error_message": _(
                        "Please enter a valid UK postcode, e.g., SW1A 1AA."
                    )
                }
            ),
        },
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


def base_postcode_json(
    request: Request, backend: BaseAPIClient, postcode: str, url_prefix: str
):
    if not postcode:
        return JSONResponse({"error": "invalid postcode"}, status_code=400)

    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_postcode(postcode)
    except (InvalidPostcodeException, ApiError) as e:
        return JSONResponse({"error": str(e)}, status_code=e.status_code)

    api_response = preprocess_api_response(
        api_response, request, postcode, url_prefix
    )
    return JSONResponse(api_response)


def base_postcode_html(
    request: Request, backend: BaseAPIClient, postcode: str, url_prefix: str
):
    if not postcode:
        return RedirectResponse(
            request.url_for(url_prefix + "_postcode_form_en")
        )

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
                url_prefix + "_postcode_form_en"
            ).include_query_params(**{query_param: 1})
        )

    api_response = preprocess_api_response(
        api_response, request, postcode, url_prefix
    )

    context = results_context(api_response, request, postcode, url_prefix)

    template_name = "electoral_services_team_results.html"
    if context["api_response"].address_picker:
        template_name = "address_picker.html"

    return get_loader(request).TemplateResponse(
        request, template_name, context=context
    )


async def base_postcode_endpoint(
    request: Request, backend: BaseAPIClient = None
):
    if not backend:
        raise ValueError("Must specify a backend")

    url_prefix = f"electoral_services_{backend.URL_PREFIX}"
    postcode = request.query_params.get("postcode-search", None)
    format_ = request.query_params.get("format", "html")

    if postcode == "FA1LL":
        return Response(status_code=400)
    if postcode == "FA2LL":
        assert False

    if format_ == "json":
        return base_postcode_json(request, backend, postcode, url_prefix)

    return base_postcode_html(request, backend, postcode, url_prefix)


live_postcode_view = functools.partial(
    base_postcode_endpoint, backend=LiveAPIBackend
)
sandbox_postcode_view = functools.partial(
    base_postcode_endpoint, backend=SandboxAPIBackend
)
mock_postcode_view = functools.partial(
    base_postcode_endpoint, backend=MockAPIBackend
)


def base_uprn_json(
    request: Request,
    backend: BaseAPIClient,
    postcode: str,
    uprn: str,
    url_prefix: str,
):
    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_uprn(uprn)
    except (InvalidUPRNException, ApiError) as e:
        return JSONResponse({"error": str(e)}, status_code=e.status_code)

    api_response = preprocess_api_response(
        api_response, request, postcode, url_prefix
    )
    return JSONResponse(api_response)


def base_uprn_html(
    request: Request,
    backend: BaseAPIClient,
    postcode: str,
    uprn: str,
    url_prefix: str,
):
    try:
        api_response = backend(
            api_key=os.environ.get("API_KEY", "ec-postcode-testing"),
            request=request,
        ).get_uprn(uprn)
    except (InvalidUPRNException, ApiError) as e:
        query_param = "api-error" if isinstance(e, ApiError) else "invalid-uprn"
        return RedirectResponse(
            request.url_for(
                url_prefix + "_postcode_form_en"
            ).include_query_params(**{query_param: 1})
        )

    api_response = preprocess_api_response(
        api_response, request, postcode, url_prefix
    )

    context = results_context(api_response, request, postcode, url_prefix)

    template_name = "electoral_services_team_results.html"
    if context["api_response"].address_picker:
        template_name = "address_picker.html"

    return get_loader(request).TemplateResponse(
        request, template_name, context=context
    )


async def base_uprn_endpoint(request: Request, backend: BaseAPIClient = None):
    if not backend:
        raise ValueError("Must specify a backend")

    url_prefix = f"electoral_services_{backend.URL_PREFIX}"
    uprn = request.path_params["uprn"]
    postcode = request.path_params["postcode"]
    format_ = request.query_params.get("format", "html")

    if format_ == "json":
        return base_uprn_json(request, backend, postcode, uprn, url_prefix)
    return base_uprn_html(request, backend, postcode, uprn, url_prefix)


live_uprn_view = functools.partial(base_uprn_endpoint, backend=LiveAPIBackend)
sandbox_uprn_view = functools.partial(
    base_uprn_endpoint, backend=SandboxAPIBackend
)
