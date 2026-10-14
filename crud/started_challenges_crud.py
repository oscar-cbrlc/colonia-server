from sqlalchemy.orm import Session
from sqlalchemy import delete
from model import models
from schema.started_challenges_schema import StartedChallengeUpdate, StartedChallengeResponse

def get_user_started_challenges(db: Session, current_user: models.Users):
    """Retorna la lista de todos los desafiíos ya iniciados de un jugador."""
    return (
        db.query(models.StartedChallenges, models.ActiveChallenges)
        .join(
            models.ActiveChallenges,
            models.StartedChallenges.active_challenge_id == models.ActiveChallenges.active_challenge_id
        )
        .filter(models.StartedChallenges.user_id == current_user.user_id)
        .all()
    )

def get_active_challenges(db: Session, current_user: models.Users):
    """Retorna la lista de desafíos activos que un jugador aun no inicía."""
    obtained = (
        db.query(models.StartedChallenges.active_challenge_id)
        .filter(
            models.StartedChallenges.user_id == current_user.user_id,
            models.StartedChallenges.active_challenge_id == models.ActiveChallenges.active_challenge_id
        )
        .exists()
    )
    return (
        db.query(models.ActiveChallenges)
        .filter(~obtained)
        .all()
    )

def get_user_started_challenge_by_id(db: Session, current_user: models.Users, db_active_challenge: models.ActiveChallenges):
    """Busca un desafío iniciado de un usuario, usando el modelo del desafí activo."""
    return (
        db.query(models.StartedChallenges)
        .filter(
            models.StartedChallenges.active_challenge_id == db_active_challenge.active_challenge_id,
            models.StartedChallenges.user_id == current_user.user_id
        )
        .first()
    )

def assign_active_challenge(
        db: Session, 
        current_user: models.Users, 
        active_challenge: models.ActiveChallenges,
        progress: int):
    """Asigna un desafío iniciado a un usuario en la base de datos"""
    db_started_challenge = models.StartedChallenges(
        active_challenge_id = active_challenge.active_challenge_id,
        user_id = current_user.user_id,
        progress = progress
    )
    db.add(db_started_challenge)
    db.flush()
    return db_started_challenge

def update_active_challenge(
        db: Session, 
        db_started_challenge: models.StartedChallenges, 
        started_challenge_update: StartedChallengeUpdate
    ):
    """Actualiza la información de un desafío asginado al usuario."""
    update_data = started_challenge_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_started_challenge, key, value)
        
    db.commit()
    db.refresh(db_started_challenge)
    return db_started_challenge

def delete_active_challenge(db: Session, started_challenge_id: int):
    """Elimina un desafío iniciado de un usuario de la base de datos."""
    db.execute(
        delete(models.StartedChallenges)
        .where(models.StartedChallenges.active_challenge_id == started_challenge_id)
    )
    db.commit()