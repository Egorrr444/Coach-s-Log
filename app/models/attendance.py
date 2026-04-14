from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="absent")

    training: Mapped["Training"] = relationship(back_populates="attendances")
    student: Mapped["Student"] = relationship(back_populates="attendances")

    __table_args__ = (
        UniqueConstraint("training_id", "student_id", name="uq_training_student"),
    )