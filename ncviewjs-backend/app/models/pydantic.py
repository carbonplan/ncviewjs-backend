import hashlib

import pydantic
from tortoise.contrib.pydantic import pydantic_model_creator

from .tortoise import Store

StoreSchema = pydantic_model_creator(Store, name='Store')


class StorePayloadSchema(pydantic.BaseModel):
    url: pydantic.AnyUrl


class SanitizedURL(pydantic.BaseModel):
    url: pydantic.AnyUrl
    protocol: str
    bucket: str
    key: str

    @pydantic.root_validator
    def _remove_trailing_slash(cls, values):
        for item in ['key', 'bucket', 'url']:
            values[item] = values[item].strip('/')
        return values

    @property
    def md5_id(self):
        # compute MD5 ID from bucket and key and return it
        return hashlib.md5(f"{self.bucket}/{self.key}".encode()).hexdigest()
