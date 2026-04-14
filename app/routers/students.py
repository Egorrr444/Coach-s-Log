from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.group import Group
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    group = db.get(Group, student_data.group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    student = Student(
        full_name=student_data.full_name,
        phone=student_data.phone,
        group_id=student_data.group_id,
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    update_data = student_data.model_dump(exclude_unset=True)

    if "group_id" in update_data:
        group = db.get(Group, update_data["group_id"])
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()