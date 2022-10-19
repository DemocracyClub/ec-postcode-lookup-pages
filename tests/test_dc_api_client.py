import httpx

from dc_api_client import DCAPI


def test_get_url(respx_mock):
    respx_mock.get(
        "https://developers.democracyclub.org.uk/v1/postcode/SE228DJ/?auth_token=test&utm_source=ec_postcode_lookup"
    ).mock(return_value=httpx.Response(200))
    client = DCAPI(api_key="test")
    client.get_postcode("SE22 8DJ")
