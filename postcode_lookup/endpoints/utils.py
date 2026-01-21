import datetime

from markupsafe import Markup
from mock_responses import example_responses
from response_builder.v1.builders.ballots import StockLocalBallotBuilder
from response_builder.v1.generated_responses.candidates import all_candidates
from response_builder.v1.models.base import CancellationReason
from response_builder.v1.sandbox import SANDBOX_POSTCODES
from starlette.requests import Request
from starlette.responses import Response
from utils import get_loader


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
