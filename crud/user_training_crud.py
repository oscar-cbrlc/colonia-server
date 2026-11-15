from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
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
            models.UserTraining.training_uuid == training_uuid
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
    """
    Inserta un entrenamiento nuevo en la base de datos
    Si se detecta algún problema durante la inserción se detiene el proceso.
    """
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

def update_training_results(
    db_training: models.UserTraining,
    captured_territories: int,
    training_attack: int,
    training_defence: int,
    processing_result: dict
):
    """Actualiza campos que son resultado del procesado del entrenamiento seleccionado"""
    db_training.captured_territories = captured_territories
    db_training.training_attack = training_attack
    db_training.training_defence = training_defence
    db_training.processing_result = processing_result
    return db_training