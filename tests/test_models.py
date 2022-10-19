
def test_electoral_services_eq_registration(
    electoral_services_factory, registration_factory
):
    es = electoral_services_factory(council_id="FOO")
    reg = registration_factory(council_id="FOO")

    assert es == reg

    other_reg = registration_factory(council_id="BAR")

    assert es != other_reg
