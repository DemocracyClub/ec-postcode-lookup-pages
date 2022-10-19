from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

import sys
sys.path.append(str(Path(__file__).parent.absolute()))

from models import ElectoralServices, Registration

from dc_api_client import DCAPI

root = Path(__file__).parent

templates = Jinja2Templates(directory=root / "templates")


def results_contest(api_response):
    return {
        "electoral_services": ElectoralServices.from_api(api_response.json()),
        "registration": Registration.from_api(api_response.json())
    }


async def index(request):
    return templates.TemplateResponse("index.html", {"request": request})


async def postcode(request):
    postcode = request.path_params["postcode"]
    api_response = DCAPI(api_key="foo").get_postcode(postcode)
    context = results_contest(api_response)
    context["request"] = request
    return templates.TemplateResponse(
        "postcode.html", context
    )


async def uprn(request):
    return templates.TemplateResponse("uprn.html", {"request": request})


routes = [
    Route("/", endpoint=index),
    Route("/{postcode}/", endpoint=postcode),
    Route("/{uprn}/", endpoint=uprn),
    Mount("/static", StaticFiles(directory=root / "static"), name="static"),
]

app = Starlette(debug=True, routes=routes)
