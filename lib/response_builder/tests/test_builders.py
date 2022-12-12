from datetime import datetime, date
from typing import List, Union

from pydantic import BaseModel, UUID4
from pydantic_factories import ModelFactory

from response_builder.v1.builders import BaseBuilder


def test_builder():
    builder = BaseBuilder()
    print(builder.root_model.schema_json(indent=4))

    class Person(BaseModel):
        id: UUID4
        name: str
        hobbies: List[str]
        age: Union[float, int]
        birthday: Union[datetime, date]

    class PersonFactory(ModelFactory):
        __model__ = Person

    PersonFactory.build()
