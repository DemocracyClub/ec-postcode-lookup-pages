import re

import pytest
from playwright.sync_api import Page

URLS_TO_CHECK = [
    # TODO: remove these once the new URLs are live
    "/i-am-a/voter/your-election-information",
    "/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad",
    # New URLS
    "/voting-and-elections/your-election-information",
    "/cy/pleidleisio-ac-etholiadau/gwybodaeth-etholiad",
    "/sandbox/polling-stations?postcode-search=AA11AA",
    "/cy/sandbox/polling-stations?postcode-search=AA11AA",
]


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
        assert response.status == 200

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
        assert not message.text, "Found browser console output"

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
