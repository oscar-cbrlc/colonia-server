from model import models
from math import ceil, floor
from config import settings
from schema.challenge_schema import Challenge_metrics
from schema.territory_schema import TrainingResult

exp_base = settings.exp_level_base

def get_user_level(user: models.Users):
    """Calcula el nivel del usuario en base a sus puntos de experiencia."""
    user_xp = user.user_exp
    user_level = 0
    total_exp = 0
    exp_for_next_level = 0

    for level in range(1, 101):
        exp_for_level = ceil(level/5) * exp_base
        total_exp += exp_for_level

        if (user_xp >= total_exp):
            user_level = level
        else:
            exp_for_next_level = total_exp - user_xp
            break

    return user_level, exp_for_next_level

def give_user_xp(current_user: models.Users, exp_reward: int):
    """Otorga al usuario autentificado la cantidad de exp seleccioanada"""
    current_user.user_exp += exp_reward

def give_training_xp(current_user: models.Users, training_progress: Challenge_metrics):
    """Otorga al usuario autentificado experiencia por sus actividades de entrenamiento"""

    total_time = training_progress.total_time
    total_distance = training_progress.total_distance
    captured_territories = training_progress.captured_territories

    time_xp = floor(total_time / 60) * settings.time_xp
    distance_xp = floor(total_distance / 100) * settings.distance_xp
    territories_xp = captured_territories * settings.territories_xp

    training_xp = time_xp + distance_xp + territories_xp
    give_user_xp(current_user, training_xp)

    return TrainingResult(
        time_xp = time_xp,
        distance_xp = distance_xp,
        territories_xp = territories_xp,
        total_xp = training_xp
    )

