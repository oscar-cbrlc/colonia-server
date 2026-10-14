from sqlalchemy.orm import Session
from sqlalchemy import delete
from model import models
from schema.active_challenges_schema import ActiveChallengeCreate, ActiveChallengeUpdate

def get_all_active_challenges(db: Session):
    """Retorna todos los desafíos activos."""
    return db.query(models.ActiveChallenges).all()

def get_active_challenge_by_id(db: Session, active_challenge_id: int):
    """Busca un desafío activo por su ID único."""
    return db.query(models.ActiveChallenges).filter(models.ActiveChallenges.active_challenge_id == active_challenge_id).first()

def create_active_challenge(db: Session, active_challenge_in: ActiveChallengeCreate):
    """Crea un nuevo desafío activo en la base de datos"""
    db_active_challenge = models.ActiveChallenges(
        challenge_id = active_challenge_in.challenge_id,
        challenge_start_date = active_challenge_in.challenge_start_date,
        challenge_end_date = active_challenge_in.challenge_end_date
    )
    db.add(db_active_challenge)
    db.commit()
    db.refresh(db_active_challenge)
    return db_active_challenge

def update_active_challenge(
        db: Session, 
        db_active_challenge: models.ActiveChallenges, 
        active_challenge_update: ActiveChallengeUpdate
    ):
    """Actualiza la información de un desafío activo."""
    update_data = active_challenge_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_active_challenge, key, value)
        
    db.commit()
    db.refresh(db_active_challenge)
    return db_active_challenge

def delete_active_challenge(db: Session, active_challenge_id: int):
    """Elimina un desafío activo de la base de datos."""
    db.execute(
        delete(models.ActiveChallenges)
        .where(models.ActiveChallenges.active_challenge_id == active_challenge_id)
    )
    db.commit()