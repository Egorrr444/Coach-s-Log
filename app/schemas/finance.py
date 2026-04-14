from pydantic import BaseModel


class StudentFinanceResponse(BaseModel):
    student_id: int
    student_name: str
    group_id: int
    group_name: str
    year: int
    month: int
    visits_count: int
    price_per_training: float
    accrued_amount: float
    paid_amount: float
    debt_amount: float