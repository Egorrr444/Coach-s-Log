from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    group_id: int


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    group_id: int | None = None


class StudentResponse(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)