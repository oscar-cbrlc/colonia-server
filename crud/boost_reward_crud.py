from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.boost_reward_schema import BoostRewardCreate, BoostRewardUpdate

def get_boosts_by_challenge_id(db: Session, challenge_id: int):
    """Busca los potenciadores que son otorgados al completar el desafío asignado al identificador."""
    return (
        db.query(models.ChallengeBoosts, models.Boost)
        .join(
            models.Boost,
            models.ChallengeBoosts.boost_id == models.Boost.boost_id
        )
        .filter(models.ChallengeBoosts.challenge_id == challenge_id)
        .all()
    )

def create_boost_reward(db: Session, reward_in: BoostRewardCreate):
    """Crea una recompensa de potenciador."""
    db_boost_reward = models.ChallengeBoosts(**reward_in.model_dump())
    db.add(db_boost_reward)
    db.commit()
    db.refresh(db_boost_reward)
    return db_boost_reward

def update_boost_reward(db: Session, db_boost_reward: models.ChallengeBoosts, reward_in: BoostRewardUpdate):
    """Actualiza los potenciadores que son otorgados como recompensa en un desafio."""
    update_data = reward_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_boost_reward, field, value)

    db.commit()
    db.refresh(db_boost_reward)
    return db_boost_reward

def delete_boost_reward(db: Session, challenge_id: int, boost_id: int):
    """Elimina una recompensa de potenciadores."""
    db.execute(
        delete(models.ChallengeBoosts)
        .where(
            models.ChallengeBoosts.challenge_id == challenge_id,
            models.ChallengeBoosts.booster_id == boost_id
        )
    )
    db.commit()