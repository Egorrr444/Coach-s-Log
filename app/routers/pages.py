from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.models.training import Training
from app.db.session import get_db
from app.models.group import Group
from app.models.student import Student
from app.models.training import Training
from app.models.attendance import Attendance
from app.models.training import Training

from datetime import date

from fastapi import File, Form, UploadFile
from app.models.payment import Payment

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@router.get("/groups-page", response_class=HTMLResponse)
def groups_page(request: Request, db: Session = Depends(get_db)):
    groups = db.query(Group).order_by(Group.id).all()

    return templates.TemplateResponse(
        request=request,
        name="groups/list.html",
        context={
            "request": request,
            "groups": groups,
        },
    )

@router.get("/students-page", response_class=HTMLResponse)
def students_page(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.id).all()

    return templates.TemplateResponse(
        request=request,
        name="students/list.html",
        context={
            "request": request,
            "students": students,
        },
    )

@router.get("/trainings-page", response_class=HTMLResponse)
def trainings_page(request: Request, db: Session = Depends(get_db)):
    trainings = db.query(Training).order_by(Training.id).all()

    return templates.TemplateResponse(
        request=request,
        name="trainings/list.html",
        context={
            "request": request,
            "trainings": trainings,
        },
    )

@router.get("/attendance-page/{training_id}", response_class=HTMLResponse)
def attendance_page(training_id: int, request: Request, db: Session = Depends(get_db)):

    training = db.get(Training, training_id)

    students = db.query(Student).filter(Student.group_id == training.group_id).all()
    attendance_records = db.query(Attendance).filter(Attendance.training_id == training_id).all()

    attendance_map = {a.student_id: a.status for a in attendance_records}

    data = {
        "training_id": training.id,
        "students": [
            {
                "student_id": s.id,
                "full_name": s.full_name,
                "status": attendance_map.get(s.id)
            }
            for s in students
        ]
    }

    return templates.TemplateResponse(
        request=request,
        name="attendance/page.html",
        context={
            "request": request,
            "data": data
        },
    )

@router.post("/attendance-submit/{training_id}")
async def submit_attendance(training_id: int, request: Request, db: Session = Depends(get_db)):

    form = await request.form()

    students = db.query(Student).all()
    existing = db.query(Attendance).filter(Attendance.training_id == training_id).all()

    existing_map = {(a.student_id): a for a in existing}

    for s in students:
        key = f"student_{s.id}"
        status = "present" if key in form else "absent"

        if s.id in existing_map:
            existing_map[s.id].status = status
        else:
            db.add(Attendance(
                training_id=training_id,
                student_id=s.id,
                status=status
            ))

    db.commit()

    return RedirectResponse(
        url=f"/attendance-page/{training_id}",
        status_code=303
    )

    # все остальные — absent
    response = requests.get(f"http://127.0.0.1:8000/attendance/training/{training_id}")
    data = response.json()

    marked_ids = {item["student_id"] for item in items}

    for s in data["students"]:
        if s["student_id"] not in marked_ids:
            items.append({
                "student_id": s["student_id"],
                "status": "absent"
            })

    requests.post(
        f"http://127.0.0.1:8000/attendance/training/{training_id}",
        json={"items": items}
    )

    return RedirectResponse(
        url=f"/attendance-page/{training_id}",
        status_code=303
    )

@router.get("/payments-page", response_class=HTMLResponse)
def payments_page(request: Request, db: Session = Depends(get_db)):
    payments = db.query(Payment).order_by(Payment.id.desc()).all()
    students = db.query(Student).order_by(Student.id).all()

    return templates.TemplateResponse(
        request=request,
        name="payments/list.html",
        context={
            "request": request,
            "payments": payments,
            "students": students,
            "today": date.today().isoformat(),
        },
    )


@router.post("/payments-page/create")
async def create_payment_from_page(
    student_id: int = Form(...),
    amount: float = Form(...),
    payment_date: str = Form(...),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    student = db.get(Student, student_id)
    if student is None:
        return RedirectResponse(url="/payments-page", status_code=303)

    payment = Payment(
        student_id=student_id,
        amount=amount,
        payment_date=date.fromisoformat(payment_date),
        status="pending",
        receipt_image=None,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    if file and file.filename:
        import os
        import shutil
        from uuid import uuid4

        receipts_dir = "media/receipts"
        os.makedirs(receipts_dir, exist_ok=True)

        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
        _, ext = os.path.splitext(file.filename.lower())

        if ext in allowed_extensions:
            unique_filename = f"{uuid4().hex}{ext}"
            file_path = os.path.join(receipts_dir, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            payment.receipt_image = file_path
            db.commit()

    return RedirectResponse(url="/payments-page", status_code=303)


@router.post("/payments-page/{payment_id}/approve")
def approve_payment_from_page(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is not None:
        payment.status = "approved"
        db.commit()

    return RedirectResponse(url="/payments-page", status_code=303)


@router.post("/payments-page/{payment_id}/reject")
def reject_payment_from_page(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is not None:
        payment.status = "rejected"
        db.commit()

    return RedirectResponse(url="/payments-page", status_code=303)