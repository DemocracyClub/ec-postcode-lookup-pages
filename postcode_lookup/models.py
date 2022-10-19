from dataclasses import dataclass


@dataclass
class BaseOrganisation:
    name: str
    council_id: str
    email: str
    phone: str
    website: str
    postcode: str
    address: str
    identifiers: list
    nation: str

    def __eq__(self, o: "BaseOrganisation") -> bool:
        return self.council_id == o.council_id


@dataclass(eq=False)
class ElectoralServices(BaseOrganisation):
    @classmethod
    def from_api(cls, api_json):
        if "electoral_services" in api_json:
            return cls(**api_json["electoral_services"])


@dataclass(eq=False)
class Registration(BaseOrganisation):
    @classmethod
    def from_api(cls, api_json):
        if "registration" in api_json:
            return cls(**api_json["registration"])
