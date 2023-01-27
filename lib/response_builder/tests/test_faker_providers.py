from unittest import mock

from faker import Faker

from response_builder.v1.factories.faker_providers import (
    make_ward_name,
    UKCouncilNamesProvider,
)


def test_make_ward_name():
    with mock.patch("random.randrange", return_value=1):
        # We should have two words
        name = make_ward_name()
        assert " " in name

    with mock.patch("random.randrange", return_value=31):
        # Slash in name
        name = make_ward_name()
        assert "/" in name

    with mock.patch("random.randrange", return_value=36):
        # Thing-with-other names
        name = make_ward_name()
        assert "-with-" in name

    with mock.patch("random.randrange", return_value=21):
        # Thing-with-other names
        name = make_ward_name()
        assert " & " in name


def test_faker_prodiver():
    faker = Faker("en_GB")
    faker.add_provider(UKCouncilNamesProvider)
    # Not much we can test here as the return value is a random string,
    # but at least calling it will act as a smoke test
    assert type(faker.ward_name()) == str

    organisation_name = faker.organisation_name()
    assert organisation_name.lower() in faker.council_website()
    assert organisation_name.lower() in faker.council_email()
    assert organisation_name in faker.council_address()
