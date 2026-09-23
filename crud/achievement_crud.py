from sqlalchemy.orm import Session
from model import models
from sqlalchemy import delete
from schema.achievement_schema import AchievementCreate, AchievementUpdate

def get_all_achievements(db: Session):
    """Retorna la lista de todos los logros, ordenada por identificador."""
    return (
        db.query(models.Achievement)
        .order_by(models.Achievement.achievement_id)
        .all()
    )

def get_achievement_by_id(db: Session, achievement_id: int):
    """Busca un logro por su identificador."""
    return (
        db.query(models.Achievement)
        .filter(models.Achievement.achievement_id == achievement_id)
        .first()
    )

def create_achievement(db: Session, achievement_in: AchievementCreate):
    """Crea un logro nuevo."""
    db_boost = models.Achievement(**achievement_in.model_dump())
    db.add(db_boost)
    db.commit()
    db.refresh(db_boost)
    return db_boost

def update_achievement(db: Session, db_achievement: models.Achievement, achievement_in: AchievementUpdate):
    """Actualiza solamente los campos recibidos de un logro."""
    update_data = achievement_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_achievement, field, value)

    db.commit()
    db.refresh(db_achievement)
    return db_achievement

def delete_achievement(db: Session, achievement_id: int):
    """Elimina un logro y deja que PostgreSQL aplique sus cascadas."""
    db.execute(delete(models.Achievement).where(models.Achievement.achievement_id == achievement_id))
    db.commit()