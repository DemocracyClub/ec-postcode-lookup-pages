import datetime
import re

import pytest
from endpoints import get_ballot_stages
from mock_responses import example_responses
from playwright.sync_api import Page

URLS_TO_CHECK = [
    "/i-am-a/voter/your-election-information",
    "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
    "/sandbox/polling-stations?postcode-search=AA11AA",
    "/cy/sandbox/polling-stations?postcode-search=AA11AA",
]
for postcode, details in example_responses.items():
    if details["response"].build().dates:
        for date in get_ballot_stages(datetime.date.today()).values():
            URLS_TO_CHECK.append(
                f"/mock/polling-stations?postcode-search={postcode}&baseline_date={date}"
            )
    else:
        URLS_TO_CHECK.append(
            f"/mock/polling-stations?postcode-search={postcode}"
        )


@pytest.mark.parametrize(
    "path",
    URLS_TO_CHECK,
)
def test_pages_not_requesting_404(path, page: Page, uvicorn_server):
    """
    Spins up an instance of the app and uses Playwright to test if
    the app is requesting URLs that don't exist

    """

    def response_handler(response):
        assert response.status in (200, 204)

    page.on("response", response_handler)
    page.goto(url=str(f"{uvicorn_server}{path}"))


@pytest.mark.parametrize(
    "path",
    URLS_TO_CHECK,
)
def test_pages_no_console_output(path, page: Page, uvicorn_server):
    """
    Spins up an instance of the app and uses Playwright to test if
    the app is requesting URLs that don't exist

    """

    def console_handler(message):
        if "Third-party cookie will be blocked" in message.text:
            return
        assert not message.text, f"Found browser console output: {message.text}"

    page.on("console", console_handler)
    page.goto(url=str(f"{uvicorn_server}{path}"))


@pytest.mark.parametrize(
    "path",
    URLS_TO_CHECK,
)
def test_screenshot_tested_urls(path, page, uvicorn_server):
    page.goto(url=str(f"{uvicorn_server}{path}"))
    filename = re.sub(r"[^a-z]", "-", path.lower())
    page.screenshot(
        path=f"test-reports/screenshots/{filename}.png", full_page=True
    )


def test_query_params_in_translate_url(page, uvicorn_server):
    page.goto(
        url=str(
            f"{uvicorn_server}/sandbox/polling-stations?postcode-search=AA11AA"
        )
    )

    assert (
        "/cy/sandbox/polling-stations?postcode-search=AA11AA" in page.content()
    )


def test_query_params_missing(page, uvicorn_server):
    response = page.goto(url=str(f"{uvicorn_server}/sandbox/polling-stations"))
    assert response.status == 200
    assert response.url.endswith("/i-am-a/voter/your-election-information")
