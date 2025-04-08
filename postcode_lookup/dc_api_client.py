import re
from abc import ABC, abstractmethod
from copy import deepcopy
from urllib.parse import urljoin

import httpx
from mock_responses import example_responses
from response_builder.v1.builders.base import RootBuilder
from response_builder.v1.models.base import RootModel
from response_builder.v1.sandbox import SANDBOX_BASE_URL, SANDBOX_POSTCODES
from starlette.requests import Request


class InvalidPostcodeException(Exception): ...


class InvalidUPRNException(Exception): ...


class ApiError(Exception):
    """
    Custom exception class to represent errors encountered while interacting with the API.
    """


def valid_postcode(postcode: str):
    postcode = str(postcode)[:10]
    if not postcode:
        return False
    outcode_pattern = "[A-PR-UWYZ]([0-9]{1,2}|([A-HIK-Y][0-9](|[0-9]|[ABEHMNPRVWXY]))|[0-9][A-HJKSTUW])"
    incode_pattern = "[0-9][ABD-HJLNP-UW-Z]{2}"
    postcode_regex = re.compile(
        r"^(GIR 0AA|{} {})$".format(outcode_pattern, incode_pattern)
    )
    space_regex = re.compile(r" *(%s)$" % incode_pattern)

    postcode = postcode.upper().strip()

    postcode = space_regex.sub(r" \1", postcode)
    if not postcode_regex.search(postcode):
        return False
    return True


class BaseAPIClient(ABC):
    URL_PREFIX = None

    def __init__(self, api_key: str, request: Request):
        self.api_key = api_key
        self.request = request
        self.api_version = "v1"
        assert self.URL_PREFIX is not None, "URL_PREFIX must be set on backend"

    @property
    def get_base_url(self):
        if not hasattr(self, "BASE_URL"):
            raise ValueError("BASE_URL required on APIClient classes")
        return f"{self.BASE_URL}/api/{self.api_version}/"

    @property
    def default_params(self) -> dict:
        return {
            "auth_token": self.api_key,
            "utm_source": "ec_postcode_lookup",
            "recall_petition": "1",
        }

    def _get(self, endpoint, params=None):
        if not params:
            params = {}

        if not endpoint.endswith("/"):
            endpoint = f"{endpoint}/"

        params.update(self.default_params)
        url = urljoin(self.get_base_url, endpoint)
        req = httpx.get(url, params=params)
        if req.status_code == 400:
            raise InvalidPostcodeException
        req.raise_for_status()
        return req

    @abstractmethod
    def get_postcode(self, postcode: str) -> dict: ...

    @abstractmethod
    def get_uprn(self, uprn: str) -> dict: ...


class LiveAPIBackend(BaseAPIClient):
    BASE_URL = "https://developers.democracyclub.org.uk"
    URL_PREFIX = "live"

    def get_postcode(self, postcode: str) -> dict:
        postcode = postcode[:10].upper().replace(" ", "")
        if valid_postcode(postcode):
            try:
                return self._get(endpoint=f"postcode/{postcode}/").json()
            except httpx.HTTPError:
                raise ApiError
        raise InvalidPostcodeException

    def get_uprn(self, uprn: str) -> dict:
        try:
            return self._get(endpoint=f"address/{uprn}/").json()
        except httpx.HTTPError:
            raise InvalidUPRNException


class SandboxAPIBackend(BaseAPIClient):
    POSTCODES = SANDBOX_POSTCODES
    BASE_URL = SANDBOX_BASE_URL
    URL_PREFIX = "sandbox"

    def get_postcode(self, postcode: str) -> dict:
        if postcode not in self.POSTCODES:
            raise InvalidPostcodeException

        response_dict = self._get(endpoint=f"sandbox/postcode/{postcode}/")
        return RootModel.parse_obj(response_dict.json()).dict()

    def get_uprn(self, uprn: str) -> dict:
        response_dict = self._get(endpoint=f"sandbox/address/{uprn}/")
        return RootModel.parse_obj(response_dict.json()).dict()


class MockAPIBackend(BaseAPIClient):
    def get_mock_response(self, postcode):
        builder: RootBuilder = example_responses[postcode]["response"]
        if baseline_date := self.request.query_params.get("baseline_date"):
            builder = deepcopy(builder)
            builder = builder.set_date_baseline(baseline_date)
        return builder.build().dict()

    def get_uprn(self, uprn: str) -> dict:
        return self.get_mock_response(uprn)

    def get_postcode(self, postcode: str) -> dict:
        return self.get_mock_response(postcode)

    POSTCODES = example_responses
    URL_PREFIX = "mock"
