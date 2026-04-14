from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    student_id: int
    amount: float = Field(..., ge=0)
    payment_date: date
    receipt_image: str | None = Field(default=None, max_length=255)


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|rejected)$")


class PaymentResponse(PaymentBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)