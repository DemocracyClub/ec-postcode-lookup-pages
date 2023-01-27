import json
from typing import Any

from pydantic import BaseModel, Field, EmailStr, HttpUrl


class ElectoralServices(BaseModel):
    council_id: str = Field(..., description="GSS code for this council")
    name: str = Field(..., description="Name of this council")
    nation: str = Field(..., description="Name of nation")
    address: str = Field(..., description="Contact address for this council")
    postcode: str = Field(
        ...,
        description="Postcode component of contact address for this council",
    )
    email: EmailStr = Field(
        ...,
        description="Contact email address for this council's Electoral Services team",
    )
    phone: str = Field(
        ...,
        description="Telephone number for this council's Electoral Services team",
    )
    website: HttpUrl = Field(..., description="URL for this council's website")

    def __eq__(self, other: Any) -> bool:
        # TODO: Find a better way to do this, maybe by adding to the aggregator API?
        this_address = self.dict().get("address")
        try:
            other_address = other.dict()["address"]
        except AttributeError:
            return False
        return this_address == other_address

    @classmethod
    def from_ec_api(cls, json_data):
        def _nation_from_gss(gss):
            gss_prefix = gss[0]
            nations_lookup = {
                "E": "England",
                "W": "Wales",
                "S": "Scotland",
                "N": "Northern Ireland",
            }
            return nations_lookup.get(gss_prefix)

        data = json.loads(json_data)
        cleaned = {}
        cleaned["council_id"] = data["code"]
        cleaned["name"] = data["official_name"]
        cleaned["address"] = data["electoral_services"][0]["address"]
        cleaned["postcode"] = data["electoral_services"][0]["postcode"]
        cleaned["email"] = data["electoral_services"][0]["email"]
        cleaned["website"] = data["electoral_services"][0]["website"]
        cleaned["phone"] = data["electoral_services"][0]["tel"][0]
        cleaned["nation"] = _nation_from_gss(data["identifiers"][0])
        return cls(**cleaned)


class Registration(BaseModel):
    """
    Sometimes the contact information for registration and proxy voting is
    different to the electoral services contact details. Use these if they
    exist and your users might have questions about voter registration.

    """

    address: str = Field(..., description="Contact address for this council")
    postcode: str = Field(
        ...,
        description="Postcode component of contact address for this council",
    )
    email: EmailStr = Field(
        ...,
        description="Contact email address for this council's Electoral Services team",
    )
    phone: str = Field(
        ...,
        description="Telephone number for this council's Electoral Services team",
    )
    website: HttpUrl = Field(..., description="URL for this council's website")

    def __eq__(self, other: Any) -> bool:
        this_address = self.dict().get("address")
        try:
            other_address = other.dict()["address"]
        except AttributeError:
            return False
        return this_address == other_address
