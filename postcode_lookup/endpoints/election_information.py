import functools
import json
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
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_babel.translator import gettext as _
from template_sorter import TemplateSorter
from utils import get_loader, results_context


async def base_postcode_form(request: Request, backend: BaseAPIClient = None):
    return get_loader(request).TemplateResponse(
        request,
        "index.html",
        context={
            "url_prefix": backend.URL_PREFIX,
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

    context = results_context(
        api_response, request, postcode, backend.URL_PREFIX
    )

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
    context = results_context(
        api_response, request, postcode, backend.URL_PREFIX
    )

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
