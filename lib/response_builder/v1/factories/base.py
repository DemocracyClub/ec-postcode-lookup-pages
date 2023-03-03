from datetime import date
from typing import TypeVar, Generic, Optional

from faker import Faker
from pydantic import BaseModel, HttpUrl
from pydantic.main import ModelMetaclass

from response_builder.v1.models.base import RootModel

FactoryTypes = BaseModel
T = TypeVar("T", bound=FactoryTypes)


class BaseModelFactory(Generic[T]):
    __model__: BaseModel = BaseModel
    __fake_defaults__ = True
    __faker_providers__ = []

    def __init__(self):
        self.faker = Faker()
        for provider in self.__faker_providers__:
            self.faker.add_provider(provider)

    def fake_single_field(self, field_data):
        if field_data.allow_none:
            return None
        if field_data.default is not None:
            return field_data.default
        if field_data.default_factory is not None:
            return field_data.default_factory()
        if field_data.type_ == str:
            return self.faker.pystr()
        if field_data.type_ == list:
            return []
        if field_data.type_ == dict:
            return self.faker.pydict()
        if field_data.type_ == date:
            return self.faker.date_this_decade()
        if field_data.type_ == HttpUrl:
            return self.faker.url()

    def populate_faker_fields(self, fields, skip):
        faked_fields = {}
        for field_name, field_data in fields.items():
            if not field_name in skip:
                faked_fields[field_name] = self.fake_single_field(field_data)
        return faked_fields

    def build(self, **kwargs):
        model_fields = self.__model__.__fields__
        skip = list(kwargs.keys())
        for attr in dir(self):
            if attr.startswith("__"):
                continue
            if attr in kwargs:
                continue
            attr_obj = getattr(self, attr)
            if isinstance(attr_obj, BaseField):
                value = attr_obj.build(self, attr)
                kwargs[attr] = value
            elif isinstance(attr_obj, ModelMetaclass):
                raise ValueError(
                    "models must be instantiated on the Factory class"
                )
            elif isinstance(attr_obj, type(self)):
                value = attr_obj.build()
            elif isinstance(attr_obj, BaseModel):
                value = attr_obj
                kwargs[attr] = value
            elif isinstance(attr_obj, BaseModelFactory):
                value = attr_obj.build(**kwargs)
                kwargs[attr] = value
            elif attr in model_fields:
                kwargs[attr] = attr_obj

        if self.__fake_defaults__:
            fake_data = self.populate_faker_fields(model_fields, skip=skip)
            fake_data.update(**kwargs)
            kwargs = fake_data

        return self.__model__.parse_obj(kwargs)


class BaseField:
    parent: Optional[BaseModelFactory] = None

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def build(self, parent, field_name):
        return self.get_value()


class LiteralFactoryField(BaseField):
    ...


class MethodFactoryField(BaseField):
    ...


class FakerFactoryField(BaseField):
    def build(self, parent, field_name):
        return getattr(parent.faker, self.value)()


class RootModelFactory(BaseModelFactory):
    __model__ = RootModel()
