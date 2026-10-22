from sqlalchemy.orm import Session
from sqlalchemy import delete
from model import models
from schema.challenge_schema import ChallengeCreate, ChallengeUpdate

def get_all_challenges(db: Session):
    """Retorna todos los desafíos almacenados."""
    return db.query(models.Challenge).all()

def get_challenge_by_id(db: Session, challenge_id: int):
    """Busca un desafío por su ID único."""
    return db.query(models.Challenge).filter(models.Challenge.challenge_id == challenge_id).first()

def create_challenge(db: Session, challenge_in: ChallengeCreate):
    """Crea un nuevo desafío en la base de datos"""
    challenge_name = None
    if challenge_in.challenge_name is not None:
        challenge_name = challenge_in.challenge_name
    
    db_challenge = models.Challenge(
        challenge_name = challenge_name,
        challenge_reward = challenge_in.challege_reward,
        objective_type = challenge_in.objective_type,
        objective_condition = challenge_in.objective_condition,
        challenge_difficulty = challenge_in.challenge_difficulty
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def update_challenge(db: Session, db_challenge: models.Challenge, challenge_update: ChallengeUpdate):
    """Actualiza la información de un desafío."""
    update_data = challenge_update.model_dump(exclude_unset=True)
    
    # se actualizan cada uno de los cambios
    for key, value in update_data.items():
        setattr(db_challenge, key, value)
        
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def delete_challenge(db: Session, challenge_id: int):
    """Elimina permanentemente a un desafío de la base de datos."""
    db.execute(delete(models.Challenge).where(models.Challenge.challenge_id == challenge_id))
    db.commit()