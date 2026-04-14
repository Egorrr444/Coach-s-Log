from typing import TYPE_CHECKING
from datetime import date, time
from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.group import Group


class Training(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)

    training_date: Mapped[date] = mapped_column(Date, nullable=False)
    training_time: Mapped[time] = mapped_column(Time, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    group: Mapped["Group"] = relationship(back_populates="trainings")
    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="training",
        cascade="all, delete-orphan"
    )
