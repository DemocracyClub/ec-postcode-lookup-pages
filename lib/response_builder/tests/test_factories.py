from response_builder.v1.factories.councils import RegistrationFactory


def test_registration_factory_smoke_test():
    factory = RegistrationFactory()
    assert list(factory.build().dict().keys()) == [
        "address",
        "postcode",
        "email",
        "phone",
        "website",
    ]
