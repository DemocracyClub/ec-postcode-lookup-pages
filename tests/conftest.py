import pytest

from models import ElectoralServices, Registration


def _org_factory(org_type, **kwargs):
    if not kwargs:
        kwargs = {}
    defaults = {
        "council_id": "ABC",
        "name": "Foo",
        "email": "foo@bar.com",
        "phone": "0123456789",
        "website": "https://foo.com",
        "postcode": "SW1A1AA",
        "address": "123 Foo Town",
        "identifiers": [
            "E123456",
        ],
        "nation": "England",
    }
    defaults.update(kwargs)

    return org_type(**defaults)


@pytest.fixture
def electoral_services_factory():
    def _fact(**kwargs):
        return _org_factory(ElectoralServices, **kwargs)
    return _fact


@pytest.fixture
def registration_factory():
    def _fact(**kwargs):
        return _org_factory(Registration, **kwargs)

    return _fact
