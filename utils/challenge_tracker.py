from sqlalchemy.orm import Session
from model import models
from config import settings
from decimal import Decimal
from datetime import datetime, timezone
from schema.challenge_schema import Challenge_metrics
from schema.territory_schema import TerritoryBase
from crud.challenge_crud import get_challenge_by_id
from crud.started_challenges_crud import (
    get_active_challenges,
    get_active_events,
    get_user_started_challenges, 
    get_user_started_challenge_by_id, 
    assign_active_challenge
)
from enums.enum_types import Objective_Type
from utils.reward_system import give_challenge_reward

def check_challenges(
        db: Session, 
        current_user: models.Users, 
        challenge_progress: Challenge_metrics
    ) -> list[models.StartedChallenges]:
    """
    Verifica si se debe asignar progreso a los desafíos activos o ya iniciados del jugador.
    Retorna unicamente los desafíos que hayan sido progresados.
    """
    progressed = check_started_challenges(db, current_user, challenge_progress)
    started = get_new_started_challenges(db, current_user, challenge_progress)

    return progressed + started

def check_started_challenges(
        db: Session, 
        current_user: models.Users, 
        progress: Challenge_metrics
    ) -> list[models.StartedChallenges]:
    """Verifica si se realiza progreso en los desafíos ya iniciados por el usuario."""
    started = get_user_started_challenges(db, current_user)
    progressed = []

    for started_challenge, active_challenge in started:
        if is_challenge_progressed(db, current_user, active_challenge, started_challenge, progress):
            progressed.append(started_challenge)

    return progressed

def get_new_started_challenges(
        db: Session, 
        current_user: models.Users, 
        progress: Challenge_metrics
    ) -> list[models.StartedChallenges]:
    """Verifica si se realiza progreso en desafíos aun no iniciados por el usuario."""
    not_started_challenges = get_active_challenges(db, current_user)
    not_started_events = get_active_events(db, current_user)
    not_started = not_started_challenges + not_started_events
    started = []

    for active_challenge in not_started:
        if is_challenge_progressed(db, current_user, active_challenge, None, progress):
            db_started_challenge = get_user_started_challenge_by_id(db, current_user, active_challenge)
            started.append(db_started_challenge)
    return started

def is_challenge_active(db_active_challenge: models.ActiveChallenges):
    """Verifica si un desafío activo ha iniciado y aún no expira"""
    now = datetime.now(timezone.utc)
    start_date = db_active_challenge.challenge_start_date
    expire_date = db_active_challenge.challenge_end_date

    if(start_date > now ) or (now > expire_date):
        return False
    return True

def is_challenge_progressed(
        db: Session,
        current_user: models.Users, 
        db_active_challenge: models.ActiveChallenges, 
        db_started_challenge: models.StartedChallenges,
        progress_data: Challenge_metrics) -> bool:
    """Verifica si un desafío es progresado, aumentando el progreso correspondiente si es el caso"""

    if is_challenge_active(db_active_challenge) is False:
        return False

    if db_started_challenge is not None:
        if db_started_challenge.is_complete:
            return False
    
    challenge_id = db_active_challenge.challenge_id
    db_challenge = get_challenge_by_id(db, challenge_id)
    objective = db_challenge.objective_condition
    objective_type = db_challenge.objective_type
    progress = 0
    match objective_type:
        case Objective_Type.total_time:
            progress = progress_data.total_time
            objective = objective['total_time']
            
        case Objective_Type.walk_time:
            progress = progress_data.walk_time
            objective = objective['walk_time']
            
        case Objective_Type.run_time:
            progress = progress_data.run_time
            objective = objective['run_time']
            
        case Objective_Type.bike_time:
            progress = progress_data.bike_time
            objective = objective['bike_time']
            
        case Objective_Type.total_distance:
            progress = progress_data.total_distance
            objective = objective['total_distance']
            
        case Objective_Type.walk_distance:
            progress = progress_data.walk_distance
            objective = objective['walk_distance']
            
        case Objective_Type.run_distance:
            progress = progress_data.run_distance
            objective = objective['run_distance']
            
        case Objective_Type.bike_distance:
            progress = progress_data.bike_distance
            objective = objective['bike_distance']
            
        case Objective_Type.captured_territories:
            progress = progress_data.captured_territories
            objective = objective['captured_territories'] 

        case Objective_Type.route:
            traversed_territories = progress_data.traversed_territories
            target_territories = objective['route']
            if is_route_traversed(traversed_territories, target_territories):
                progress = 1
                objective = 1

    if progress > 0:
        progress_challenge(db, current_user, db_challenge, db_active_challenge, db_started_challenge, progress, objective)
        return True
    
    return False

def progress_challenge(
        db: Session,
        current_user: models.Users,
        db_challenge: models.Challenge, 
        db_active_challenge: models.ActiveChallenges, 
        db_started_challenge: models.StartedChallenges,
        progress: int | Decimal,
        objective: Decimal
    ):
    """Asigna progreso a un desafío."""
    if db_started_challenge is None:
        db_started_challenge = assign_active_challenge(db, current_user, db_active_challenge, progress)
    else:
        db_started_challenge.progress += progress

    if db_started_challenge.progress >= objective:
        db_started_challenge.progress = objective
        db_started_challenge.is_complete = True
        give_challenge_reward(db, current_user, db_challenge)

def is_route_traversed(
        traversed_territories: set,
        target_territories: list[str]
    ):
    """Verifica si todos los territorios de una ruta han sido atravesados"""
    set_target_territories = set(target_territories)
    result = all(x in set_target_territories for x in traversed_territories)
    return result