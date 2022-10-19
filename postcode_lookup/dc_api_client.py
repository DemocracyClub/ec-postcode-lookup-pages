from urllib.parse import urljoin

import httpx


class DCAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_version = "v1"
        # TODO: Take API base URL from env / param
        self.base_url = f"https://developers.democracyclub.org.uk/api/{self.api_version}/"

    @property
    def default_params(self) -> dict:
        return {"auth_token": self.api_key, "utm_source": "ec_postcode_lookup"}

    def _get(self, endpoint, params=None):
        if not params:
            params = {}

        if not endpoint.endswith("/"):
            endpoint = f"{endpoint}/"

        params.update(self.default_params)
        url = urljoin(self.base_url, endpoint)
        req = httpx.get(url, params=params)
        req.raise_for_status()
        return req

    def get_postcode(self, postcode: str):
        postcode = postcode[:10].upper().replace(" ", "")
        return self._get(endpoint=f"postcode/{postcode}/")
