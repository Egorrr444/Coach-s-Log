from pydantic import BaseModel, ConfigDict, Field


class AttendanceItem(BaseModel):
    student_id: int
    status: str = Field(..., pattern="^(present|absent)$")


class AttendanceBulkCreate(BaseModel):
    items: list[AttendanceItem]


class AttendanceResponse(BaseModel):
    id: int
    training_id: int
    student_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class TrainingAttendanceStudent(BaseModel):
    student_id: int
    full_name: str
    status: str | None = None


class TrainingAttendanceResponse(BaseModel):
    training_id: int
    group_id: int
    students: list[TrainingAttendanceStudent]