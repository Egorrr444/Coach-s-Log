from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.payment import Payment
from app.models.student import Student
from app.models.training import Training
from app.schemas.finance import StudentFinanceResponse

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.get("/student/{student_id}", response_model=StudentFinanceResponse)
def get_student_finance(
    student_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    group = student.group

    visits_count = (
        db.query(Attendance)
        .join(Training, Attendance.training_id == Training.id)
        .filter(
            Attendance.student_id == student_id,
            Attendance.status == "present",
            Training.training_date >= date(year, month, 1),
            Training.training_date < (
                date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            ),
        )
        .count()
    )

    price_per_training = Decimal(group.price_per_training)
    accrued_amount = price_per_training * visits_count

    paid_amount = (
        db.query(Payment)
        .filter(
            Payment.student_id == student_id,
            Payment.status == "approved",
            Payment.payment_date >= date(year, month, 1),
            Payment.payment_date < (
                date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            ),
        )
        .all()
    )

    total_paid = sum(Decimal(payment.amount) for payment in paid_amount)
    debt_amount = accrued_amount - total_paid

    return StudentFinanceResponse(
        student_id=student.id,
        student_name=student.full_name,
        group_id=group.id,
        group_name=group.name,
        year=year,
        month=month,
        visits_count=visits_count,
        price_per_training=float(price_per_training),
        accrued_amount=float(accrued_amount),
        paid_amount=float(total_paid),
        debt_amount=float(debt_amount),
    )