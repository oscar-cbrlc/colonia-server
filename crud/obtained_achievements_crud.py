from sqlalchemy.orm import Session
from model import models

def get_my_achievement_list(db: Session, current_user: models.Users):
    """Retorna la lista de todos los logros del jugador, ordenada por fecha de adquisición."""
    return (
        db.query(models.ObtainedAchievements, models.Achievement)
        .join(
            models.Achievement,
            models.ObtainedAchievements.achievement_id == models.Achievement.achievement_id
        )
        .filter(models.ObtainedAchievements.user_id == current_user.user_id)
        .order_by(models.ObtainedAchievements.achievement_acquisition_date.desc())
        .all()
    )

def get_locked_achievements(db: Session, current_user: models.Users):
    """Retorna la lista de logros que el jugador aun no obtiene."""
    obtained = (
        db.query(models.ObtainedAchievements.achievement_id)
        .filter(
            models.ObtainedAchievements.user_id == current_user.user_id,
            models.ObtainedAchievements.achievement_id == models.Achievement.achievement_id
        )
        .exists()
    )

    return (
        db.query(models.Achievement)
        .filter(~obtained)
        .all()
    )

def assign_achievement(db: Session, current_user: models.Users, db_achievement: models.Achievement):
    """Asigna un logro a un jugador"""
    db_obtained_achievement = models.ObtainedAchievements(
        achievement_id = db_achievement.achievement_id,
        user_id = current_user.user_id
    )
    db.add(db_obtained_achievement)
    db.flush()
