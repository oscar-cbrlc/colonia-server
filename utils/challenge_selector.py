from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
from model import models
from datetime import datetime, timedelta, timezone
import random 
from crud.challenge_crud import get_all_challenges
from crud.active_challenges_crud import get_all_active_challenges, get_expired_challenges
from enums.enum_types import Difficulty_Type, Objective_Type

def get_challenges(
        db: Session,
        excluded_ids: set[int] | None = None
    ) -> list[models.Challenge]:
    """Obtiene una lista de desafíos para ser activados"""

    excluded_ids = excluded_ids or set()

    quotas = {
        Difficulty_Type.easy: 2,
        Difficulty_Type.normal: 2,
        Difficulty_Type.hard: 1,
    }
    selected = {difficulty: [] for difficulty in quotas}

    challenges = [
        challenge
        for challenge in get_all_challenges(db)
        if (
            challenge.challenge_id not in excluded_ids and
            challenge.objective_type != Objective_Type.route
        )
    ]
    random.shuffle(challenges)

    for challenge in challenges:
        difficulty = challenge.challenge_difficulty

        if difficulty not in quotas:
            continue

        if len(selected[difficulty]) < quotas[difficulty]:
            selected[difficulty].append(challenge)

    return [
        challenge
        for difficulty in quotas
        for challenge in selected[difficulty]
    ]

def activate_challenges(db: Session, challenges: list[models.Challenge]):
    """Realiza la activación de una lista de desafíos"""
    now = datetime.now(timezone.utc)
    end_date = (now + timedelta(days=6)).replace(
        hour=23,
        minute=59,
        second=0,
        microsecond=0
    )
    for challenge in challenges:
        db_active_challenge = models.ActiveChallenges(
            challenge_id = challenge.challenge_id,
            challenge_start_date = now,
            challenge_end_date = end_date
        )
        db.add(db_active_challenge)

def delete_active_challenges(db: Session):
    """Elimina los desafíos activos cuya fecha de expiración ha pasado"""
    expired_challenges = get_expired_challenges(db)
    for challenge in expired_challenges:
        db.delete(challenge)

    return expired_challenges

def select_weekly_challenges(db:Session):
    """Realiza el eliminado y selección de desafíos"""

    try:
        expired = delete_active_challenges(db)
        active_challenges = get_all_active_challenges(db)
        active_ids = {
            active_challenge.challenge_id
            for active_challenge in active_challenges
        }

        new_challenges = get_challenges(db, active_ids)
        activate_challenges(db, new_challenges)
        db.commit()

        print(
            f"Desafíos expirados eliminados: {len(expired)}. "
            f"Desafíos nuevos activados: {len(new_challenges)}."
        )

    except Exception:
        db.rollback()
        raise

def main():
    db = SessionLocal()
    try:
        select_weekly_challenges(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()