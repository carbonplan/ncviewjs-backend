import enum

import pydantic
from sqlmodel import Field, Relationship, SQLModel


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


class Dataset(DatasetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    rechunk_runs: list["RechunkRun"] = Relationship(back_populates="dataset")


class DatasetRead(DatasetBase):
    id: int


class RechunkRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    error_message: str | None
    status: Status = Status.queued
    outcome: Outcome | None = None
    rechunked_dataset: pydantic.HttpUrl | None = None
    dataset: Dataset | None = Relationship(back_populates="rechunk_runs")
    dataset_id: int | None = Field(default=None, foreign_key="dataset.id")


class DatasetWithRechunkRuns(DatasetRead):
    rechunk_runs: list[RechunkRun] | None = []
