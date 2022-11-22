import pydantic
from tortoise.contrib.pydantic import pydantic_model_creator

from .tortoise import Store

StoreSchema = pydantic_model_creator(Store, name='Store')


class StorePayloadSchema(pydantic.BaseModel):
    url: pydantic.AnyUrl
