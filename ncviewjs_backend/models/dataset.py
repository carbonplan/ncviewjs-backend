from sqlmodel import Field, SQLModel


class Dataset(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    md5_id: str
    protocol: str
    key: str
    bucket: str
