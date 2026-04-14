from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.training import Training
from app.schemas.attendance import (
    AttendanceBulkCreate,
    AttendanceResponse,
    TrainingAttendanceResponse,
    TrainingAttendanceStudent,
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/training/{training_id}", response_model=TrainingAttendanceResponse)
def get_training_attendance(training_id: int, db: Session = Depends(get_db)):
    training = db.get(Training, training_id)
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    students = db.query(Student).filter(Student.group_id == training.group_id).all()
    attendance_records = db.query(Attendance).filter(Attendance.training_id == training_id).all()

    attendance_map = {record.student_id: record.status for record in attendance_records}

    result_students = [
        TrainingAttendanceStudent(
            student_id=student.id,
            full_name=student.full_name,
            status=attendance_map.get(student.id)
        )
        for student in students
    ]

    return TrainingAttendanceResponse(
        training_id=training.id,
        group_id=training.group_id,
        students=result_students
    )


@router.post("/training/{training_id}", response_model=list[AttendanceResponse], status_code=status.HTTP_201_CREATED)
def save_training_attendance(
    training_id: int,
    attendance_data: AttendanceBulkCreate,
    db: Session = Depends(get_db)
):
    training = db.get(Training, training_id)
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    students = db.query(Student).filter(Student.group_id == training.group_id).all()
    group_student_ids = {student.id for student in students}

    saved_records = []

    for item in attendance_data.items:
        if item.student_id not in group_student_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {item.student_id} does not belong to this training group"
            )

        attendance = (
            db.query(Attendance)
            .filter(
                Attendance.training_id == training_id,
                Attendance.student_id == item.student_id
            )
            .first()
        )

        if attendance is None:
            attendance = Attendance(
                training_id=training_id,
                student_id=item.student_id,
                status=item.status,
            )
            db.add(attendance)
        else:
            attendance.status = item.status

        saved_records.append(attendance)

    db.commit()

    for record in saved_records:
        db.refresh(record)

    return saved_records