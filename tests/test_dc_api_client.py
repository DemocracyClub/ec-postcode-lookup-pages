import httpx
import pytest

from dc_api_client import (
    InvalidPostcodeException,
    LiveAPIBackend,
    valid_postcode,
)
from endpoints import base_postcode_endpoint
from response_builder.v1.models.base import RootModel
from utils import date_format


@pytest.mark.parametrize(
    "endpoint_name",
    [
        "postcode_form_en",
        "postcode_form_cy",
    ],
)
def test_get_postcode_form(app_client, endpoint_name):
    url = app_client.app.url_path_for(endpoint_name)
    resp = app_client.get(url)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_postcode_endpoint_without_backend_raises(app_client):
    with pytest.raises(ValueError):
        await base_postcode_endpoint(request=None)


def test_get_url(respx_mock):
    respx_mock.get(
        "https://developers.democracyclub.org.uk/api/v1/postcode/SE228DJ/?auth_token=test&utm_source=ec_postcode_lookup"
    ).mock(return_value=httpx.Response(200, json={}))
    client = LiveAPIBackend(api_key="test")
    client.get_postcode("SE22 8DJ")


def test_get_postcode_endpoint(respx_mock, app_client):
    respx_mock.get(
        "https://developers.democracyclub.org.uk/api/v1/postcode/SE228DJ/?auth_token=foo&utm_source=ec_postcode_lookup"
    ).mock(return_value=httpx.Response(200, json=RootModel().dict()))
    resp = app_client.get(
        app_client.app.url_path_for("postcode_en"),
        params={"postcode-search": "SE228DJ"},
        follow_redirects=False,
    )
    assert resp.status_code == 200
    assert "There are no upcoming elections in your area" in resp.text


def test_get_invalid_postcode_api_client(respx_mock):
    client = LiveAPIBackend(api_key="test")
    with pytest.raises(InvalidPostcodeException):
        client.get_postcode("FAIL")


def test_get_invalid_postcode_frontend(respx_mock, app_client):
    resp = app_client.get(
        "/polling-stations",
        params={"postcode-search": "FAIL"},
        follow_redirects=False,
    )
    assert resp.status_code == 307


@pytest.mark.parametrize(
    "postcode,valid",
    [
        ("SW1A1AA", True),
        ("FooBar", False),
        (None, False),
        ("", False),
        (1, False),
        (1.1, False),
    ],
)
def test_valid_postcode(postcode, valid):
    assert valid_postcode(postcode) == valid


def test_date_format():
    assert date_format("2019-12-12") == "Thursday 12 December 2019"


def test_x_forward_headers(app_client):
    resp = app_client.get(app_client.app.url_path_for("postcode_form_en"))
    assert "example.com" not in resp.text
    resp = app_client.get(
        app_client.app.url_path_for("postcode_form_en"),
        headers={"X-FORWARDED-HOST": "example.com"},
    )
    assert "example.com" in resp.text
