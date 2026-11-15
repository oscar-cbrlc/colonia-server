from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from model import models
from sqlalchemy import text
from model import models
from uuid import UUID
from schema.user_training_schema import UserTrainingCreate, UserTrainingResponse
from config import settings

def get_training_by_id(db: Session, user_id: int, training_uuid: UUID):
    """Retorna un entrenamiento por sus identificadores."""
    return (
        db.query(models.UserTraining)
        .filter(
            models.UserTraining.user_id == user_id,
            models.UserTraining.training_uuid == training_uid
        )
        .first()
    )

def get_user_trainings(db: Session, user_id: int):
    """Retorna todos los entrenamientos realizados por el usuario del identificador."""
    return (
        db.query(models.UserTraining)
        .filter(
            models.UserTraining.user_id == user_id
        )
        .order_by(models.UserTraining.started_at)
        .all()
    )

def create_training(db: Session, training_data):
    stmt = (
        insert(models.UserTraining)
        .values(**training_data)
        .on_conflict_do_nothing(
            index_elements=[
                models.UserTraining.user_id,
                models.UserTraining.training_uuid
            ]
        )
        .returning(models.UserTraining.training_uuid)
    )

    return db.execute(stmt).scalar_one_or_none()