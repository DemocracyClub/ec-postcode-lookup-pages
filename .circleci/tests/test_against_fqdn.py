import os

import httpx
import pytest
from response_builder.v1.sandbox import SANDBOX_POSTCODES

FAILOVER_COMMENT = "DC failover page"
STATIC_PAGE_COMMENT = "<!-- Static page content -->"


def make_request(url):
    req = httpx.get(url, timeout=20)
    req.raise_for_status()
    return req


@pytest.fixture(scope="session")
def fqdn():
    if FQDN := os.environ.get("FQDN"):
        return FQDN
    raise ValueError("FQDN environment variable required")


@pytest.mark.parametrize("postcode", SANDBOX_POSTCODES.keys())
def test_sandbox_responses(fqdn, postcode):
    if "electoralcommission.org.uk" in fqdn:
        return
    url = f"https://{fqdn}/sandbox/polling-stations?postcode-search={postcode}"
    req = make_request(url)
    assert FAILOVER_COMMENT not in req.text


def test_failover_page(fqdn):
    url = f"https://{fqdn}/polling-stations?postcode-search=FA1LL&Submit+Postcode="
    req = make_request(url)
    assert FAILOVER_COMMENT in req.text


def test_smoke_test_live_api(fqdn):
    url = f"https://{fqdn}/polling-stations?postcode-search=SW1A1AA&Submit+Postcode="
    req = make_request(url)
    assert FAILOVER_COMMENT not in req.text


def test_postcode_form_en(fqdn):
    url = f"https://{fqdn}/i-am-a/voter/your-election-information"
    req = make_request(url)
    assert STATIC_PAGE_COMMENT in req.text
    assert FAILOVER_COMMENT not in req.text


def test_postcode_form_cy(fqdn):
    url = f"https://{fqdn}/cy/rwyf-yneg-pleidleisiwr/pleidleisiwr/gwybodaeth-etholiad"
    req = make_request(url)
    assert STATIC_PAGE_COMMENT in req.text
    assert FAILOVER_COMMENT not in req.text
