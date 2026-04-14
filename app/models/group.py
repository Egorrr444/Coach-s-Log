from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainers.id"), nullable=False)

    price_per_training: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    subscription_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    trainer: Mapped["Trainer"] = relationship(back_populates="groups")
    students: Mapped[list["Student"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan"
    )
    trainings: Mapped[list["Training"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan"
    )