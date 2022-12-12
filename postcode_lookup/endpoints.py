import functools

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from dc_api_client import InvalidPostcodeException, SandboxAPIBackend, LiveAPIBackend
from response_builder.v1.models.base import RootModel
from response_builder.v1.sandbox import SANDBOX_POSTCODES

from utils import is_welsh, get_loader


async def postcode_form(request: Request):
    form_action = request.url_for("postcode_en")
    if is_welsh(request.url.path):
        form_action = request.url_for("postcode_cy")
    response = get_loader(request).TemplateResponse(
        "index.html", {"request": request, "form_action": form_action}
    )
    return response


async def base_postcode_endpoint(request: Request, backend=None):
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
    postcode = request.query_params["postcode-search"]
    try:
        api_response = backend(api_key="foo").get_postcode(postcode)
    except InvalidPostcodeException:
        return RedirectResponse(
            request.url_for("postcode_form_en") + "?invalid-postcode=1"
        )
    context = results_context(api_response)
    context["request"] = request
    return get_loader(request).TemplateResponse("result.html", context)


# Use functools.partial to create a view function per backend
live_postcode_view = functools.partial(base_postcode_endpoint, backend=LiveAPIBackend)
sandbox_postcode_view = functools.partial(base_postcode_endpoint, backend=SandboxAPIBackend)
# TODO: mock_postcode_view = functools.partial(base_postcode_endpoint, backend=MockAPIBackend)


async def uprn(request):
    return get_loader(request).TemplateResponse(
        "uprn.html", {"request": request}
    )


def results_context(api_response):
    api_json = api_response
    if api_json["address_picker"]:
        # TODO
        return {}

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
        "debug_page.html", {
            "request": request,
            "sandbox_postcodes": SANDBOX_POSTCODES
        }
    )
