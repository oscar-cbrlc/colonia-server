from sqlalchemy.orm import Session
from model import models
from config import settings
from crud.obtained_achievements_crud import get_locked_achievements, assign_achievement
from enums.enum_types import Achievement_Type

def check_achievements(db: Session, current_user: models.Users) -> list[models.Achievement]:
    """Verifica si los logros bloqueados deben ser asignados al usuario."""
    locked = get_locked_achievements(db, current_user.user_id)
    unlocked = []

    for achievement in locked:
        if validate_achievement(current_user, achievement):
            assign_achievement(db, current_user, achievement)
            unlocked.append(achievement)

    return unlocked

def validate_achievement(current_user: models.Users, db_achievement: models.Achievement) -> bool:
    """Verifica si un logro debe ser asignado, en base a su tipo y objetivo"""
    total_distance = current_user.total_distance
    total_time = current_user.total_time
    total_attack_points = current_user.total_attack
    total_defence_points = current_user.total_defence
    territories_captured = current_user.territories_captured

    objective = db_achievement.achievement_objective
    type = db_achievement.achievement_type
    
    match type:
        case Achievement_Type.total_distance:
            if (total_distance >= objective):
                return True

        case Achievement_Type.total_time:
            if (total_time >= objective):
                return True
            
        case Achievement_Type.total_attack:
            if (total_attack_points >= objective):
                return True
            
        case Achievement_Type.total_defense:
            if (total_defence_points >= objective):
                return True

        case Achievement_Type.captured_territories:
             if (territories_captured >= objective):
                return True
    return False
