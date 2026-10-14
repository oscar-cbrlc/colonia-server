from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.reward_schema import RewardCreate, RewardUpdate

def get_all_rewards(db: Session):
    """Retorna el catalogo de recompensas ordenado por identificador."""
    return (
        db.query(models.Reward)
        .order_by(models.Reward.reward_id)
        .all()
    )

def get_reward_by_id(db: Session, reward_id: int):
    """Busca una recompensa por su identificador."""
    return (
        db.query(models.Reward)
        .filter(models.Reward.reward_id == reward_id)
        .first()
    )

def create_reward(db: Session, reward_in: RewardCreate):
    """Crea una recompensa en el catalogo."""
    db_reward = models.Reward(**reward_in.model_dump())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

def update_reward(db: Session, db_reward: models.Reward, reward_in: RewardUpdate):
    """Actualiza solamente los campos recibidos de una recompensa."""
    update_data = reward_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_reward, field, value)

    db.commit()
    db.refresh(db_reward)
    return db_reward

def delete_reward(db: Session, reward_id: int):
    """Elimina una recompensa y deja que PostgreSQL aplique sus cascadas."""
    db.execute(delete(models.Reward).where(models.Reward.reward_id == reward_id))
    db.commit()