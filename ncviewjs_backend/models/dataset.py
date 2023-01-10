import datetime
import enum

import pydantic
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class Status(str, enum.Enum):
    completed = "completed"
    in_progress = "in_progress"
    queued = "queued"


class Outcome(str, enum.Enum):
    action_required = "action_required"
    cancelled = "cancelled"
    failure = "failure"
    neutral = "neutral"
    skipped = "skipped"
    stale = "stale"
    success = "success"
    timed_out = "timed_out"


class DatasetBase(SQLModel):
    url: str
    md5_id: str
    protocol: str
    key: str
    bucket: str
    cf_axes: dict[str, dict] | None = Field(default={}, sa_column=Column(JSON))
    last_accessed: datetime.datetime | None = Field(
        default_factory=datetime.datetime.utcnow, nullable=True
    )
    size: str | None = None


class Dataset(DatasetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rechunk_runs: list["RechunkRun"] = Relationship(back_populates="dataset")


class DatasetRead(DatasetBase):
    id: int


class RechunkRunBase(SQLModel):
    error_message: str | None
    error_message_traceback: str | None
    status: Status = Status.queued
    outcome: Outcome | None = None
    rechunked_dataset: pydantic.HttpUrl | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None


class RechunkRun(RechunkRunBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dataset: Dataset | None = Relationship(back_populates="rechunk_runs")
    dataset_id: int | None = Field(default=None, foreign_key="dataset.id")


class RechunkRunRead(RechunkRunBase):
    id: int
    dataset: DatasetRead


class RechunkRunWithoutDataset(RechunkRunBase):
    id: int


class DatasetWithRechunkRuns(DatasetRead):
    rechunk_runs: list[RechunkRunWithoutDataset] | None = []


class RechunkRunPayload(pydantic.BaseModel):
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None
    rechunked_dataset: pydantic.HttpUrl | None
    error_message: str | None
    error_message_traceback: str | None
    status: Status | None
    outcome: Outcome | None

    @pydantic.root_validator(pre=True)
    def update_dataset_url(cls, values) -> dict:
        from ..helpers import s3_to_https

        for item in {'rechunked_dataset'}:
            if values[item] is not None and values[item].startswith('s3://'):
                values[item] = s3_to_https(s3_url=values[item])

        return values
