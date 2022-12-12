from pydantic import BaseModel, Field

from response_builder.v1.models.base import RootModel


class BaseBuilder(BaseModel):
    root_model: RootModel = Field(default_factory=RootModel)

    def response(self):
        return self.root_model.dict()
