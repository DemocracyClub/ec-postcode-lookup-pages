"""

# Make pytest fixtures from Factories 

pydantic_factories's register_fixture decorator turns a factory into a pytest fixture,
however there's no nice way to import them into a project without importing the base class.

This makes it look, to editors and linters, like the classes are being unused, but the imports 
are required to register the decorator.

We also can't use the factory directly.

Below we create sub-classes of all the factories we want and decorate them to turn them
into fixtures. Being in this file also means they're auto-loaded in tests. 
"""

from pydantic_factories.plugins.pytest_plugin import register_fixture

from response_builder.v1.factories.councils import (
    RegistrationFactory,
    ElectoralServicesFactory,
)


@register_fixture(name="registration_factory")
class RegistrationFixture(RegistrationFactory):
    ...


@register_fixture(name="electoral_services_factory")
class ElectoralServicesFixture(ElectoralServicesFactory):
    ...
