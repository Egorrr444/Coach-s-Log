from datetime import date, time
from pydantic import BaseModel, Field, ConfigDict


class TrainingBase(BaseModel):
    group_id: int
    training_date: date
    training_time: time
    topic: str | None = Field(default=None, max_length=255)


class TrainingCreate(TrainingBase):
    pass


class TrainingUpdate(BaseModel):
    group_id: int | None = None
    training_date: date | None = None
    training_time: time | None = None
    topic: str | None = Field(default=None, max_length=255)


class TrainingResponse(TrainingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)