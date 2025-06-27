import datetime
import json
import os
import re
import subprocess

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


@pytest.mark.parametrize(
    "path",
    URLS_TO_CHECK,
)
def test_accessibility(page, uvicorn_server, subtests, path):
    url = f"{uvicorn_server}{path}"
    env = os.environ.copy()
    env["CHROME_PATH"] = page.context.browser.browser_type.executable_path
    command = [
        "npx",
        "lighthouse",
        url,
        "--quiet",
        "--chrome-flags=--headless --no-sandbox --disable-setuid-sandbox --disable-gpu --ignore-certificate-errors",
        "--disable-cpu-throttling",
        "--disable-network-throttling",
        "--only-categories='accessibility'",
        "--disable-full-page-screenshot",
        "--output=json",
    ]
    raw_report = subprocess.run(
        command, env=env, check=True, capture_output=True, text=True
    )
    report = json.loads(raw_report.stdout)
    categories = report["categories"]
    audits = report["audits"]

    SCORE_THRESHOLD = 0.99

    for category_key, category_data in categories.items():
        score = category_data.get("score", 1.0)
        category_title = category_data.get("title", category_key)

        # Collect failed audits
        failing_details = []
        for ref in category_data.get("auditRefs", []):
            audit_id = ref["id"]
            audit = audits.get(audit_id)
            if not audit:
                continue
            audit_score = audit.get("score")
            if audit_score is not None and audit_score < SCORE_THRESHOLD:
                title = audit.get("title", audit_id)
                description = audit.get("description", "").strip()
                items = []
                for item in audit.get("details", {}).get("items"):
                    items.append(f"""
                        - {item["node"]["selector"]}:
                            {item["node"]["explanation"]}
                    """)
                failing_details.append(
                    f"- {title}\n  {description}\n {'\n'.join(items)}"
                )

        if score < SCORE_THRESHOLD:
            with subtests.test(msg=f"{category_key} score"):
                detail = (
                    "\n".join(failing_details)
                    if failing_details
                    else "No specific audit failures found."
                )
                raise AssertionError(
                    f"[{category_title}] score was {score}, expected at least {SCORE_THRESHOLD}\n\n"
                    f"Failing audits:\n{detail}\n\n"
                )
