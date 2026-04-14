from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdateStatus

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    student = db.get(Student, payment_data.student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    payment = Payment(
        student_id=payment_data.student_id,
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        receipt_image=payment_data.receipt_image,
        status="pending",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    payments = db.query(Payment).order_by(Payment.id).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.patch("/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    payment_data: PaymentUpdateStatus,
    db: Session = Depends(get_db)
):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    payment.status = payment_data.status

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/student/{student_id}", response_model=list[PaymentResponse])
def get_student_payments(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    payments = (
        db.query(Payment)
        .filter(Payment.student_id == student_id)
        .order_by(Payment.id)
        .all()
    )
    return payments