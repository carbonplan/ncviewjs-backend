import hashlib

import pydantic


class StorePayload(pydantic.BaseModel):
    url: str
    force: bool = False


class SanitizedURL(pydantic.BaseModel):
    url: str
    protocol: str
    bucket: str
    key: str

    @pydantic.root_validator
    def remove_slashes(cls, values: dict) -> dict:
        for item in {"bucket", "key", "url"}:
            values[item] = values[item].strip("/")

        return values

    @property
    def md5_id(self) -> str:
        # Compute MD5 ID from bucket and key and return it
        return hashlib.md5(f"{self.bucket}/{self.key}".encode()).hexdigest()
