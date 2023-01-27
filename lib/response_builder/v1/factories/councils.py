from faker import Faker
from pydantic_factories import ModelFactory

from response_builder.v1.factories.faker_providers import UKCouncilNamesProvider
from response_builder.v1.models.councils import Registration, ElectoralServices

faker: Faker = Faker("en_GB")
faker.add_provider(UKCouncilNamesProvider)


class RegistrationFactory(ModelFactory):
    __model__ = Registration

    address = faker.council_address
    phone = faker.phone_number
    website = faker.council_website
    postcode = faker.postcode
    email = faker.council_email


class ElectoralServicesFactory(ModelFactory):
    __model__ = ElectoralServices

    address = faker.council_address
    phone = faker.phone_number
    website = faker.council_website
    postcode = faker.postcode
    email = faker.council_email


NuneatonElectoralServices = ElectoralServices.from_ec_api(
    json_data="""{
    "code": "NUN",
    "official_name": "Nuneaton and Bedworth Borough Council",
    "electoral_services": [
      {
        "address": "Electoral Registration Officer\\nTown Hall\\nCoton Road\\nNuneaton",
        "postcode": "CV11 5AA",
        "tel": [
          "024 7637 6230"
        ],
        "email": "electoralreg@nuneatonandbedworth.gov.uk",
        "website": "http://www.nuneatonandbedworth.gov.uk/"
      }
    ],
    "registration": null,
    "identifiers": [
      "E07000219"
    ]
  }"""
)
