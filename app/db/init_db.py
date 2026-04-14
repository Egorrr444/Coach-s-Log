from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import *  # noqa: F401,F403
from app.models.trainer import Trainer


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_trainer()


def seed_trainer():
    db: Session = SessionLocal()
    try:
        trainer = db.query(Trainer).first()
        if trainer is None:
            trainer = Trainer(full_name="Главный тренер")
            db.add(trainer)
            db.commit()
    finally:
        db.close()