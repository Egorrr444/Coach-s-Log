from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.group import Group
from app.models.training import Training
from app.schemas.training import TrainingCreate, TrainingResponse, TrainingUpdate

router = APIRouter(prefix="/trainings", tags=["Trainings"])


@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED)
def create_training(training_data: TrainingCreate, db: Session = Depends(get_db)):
    group = db.get(Group, training_data.group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    training = Training(
        group_id=training_data.group_id,
        training_date=training_data.training_date,
        training_time=training_data.training_time,
        topic=training_data.topic,
    )

    db.add(training)
    db.commit()
    db.refresh(training)
    return training


@router.get("/", response_model=list[TrainingResponse])
def get_trainings(db: Session = Depends(get_db)):
    trainings = db.query(Training).all()
    return trainings


@router.get("/{training_id}", response_model=TrainingResponse)
def get_training(training_id: int, db: Session = Depends(get_db)):
    training = db.get(Training, training_id)
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )
    return training


@router.put("/{training_id}", response_model=TrainingResponse)
def update_training(training_id: int, training_data: TrainingUpdate, db: Session = Depends(get_db)):
    training = db.get(Training, training_id)
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    update_data = training_data.model_dump(exclude_unset=True)

    if "group_id" in update_data:
        group = db.get(Group, update_data["group_id"])
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )

    for field, value in update_data.items():
        setattr(training, field, value)

    db.commit()
    db.refresh(training)
    return training


@router.delete("/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training(training_id: int, db: Session = Depends(get_db)):
    training = db.get(Training, training_id)
    if training is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )

    db.delete(training)
    db.commit()