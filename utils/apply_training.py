from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from model import models
from schema.territory_schema import (
    TerritoryCreate,
    TerritoryOwnerResponse,
    UserImpactResult,
    TerritoryListUpdate,
    TerritoryImpactResult,
    TerritoryImpactResponse,
    TrainingResult
)
from schema.challenge_schema import Challenge_metrics
from crud.territory_crud import create_territory, get_locked_territory
from routers.boosts import get_existing_boost
from crud.boost_inventory_crud import remove_boost_from_inventory
from decimal import Decimal, ROUND_HALF_UP
from config import settings
from utils.achievement_tracker import check_achievements
from utils.response_builder import build_achievement_response, build_started_challenge_response
from utils.challenge_tracker import check_challenges
from utils.user_leveling_system import give_training_xp
from enums.enum_types import Boost_Type

def apply_points(territory: models.Territory, user_team: int, points: Decimal) -> str:
    """Determina la acción realizada sobre el territorio y se realizan calculos de puntaje"""
    current_health = Decimal(territory.health_points or 0)

    if territory.team_id == user_team:
        territory.health_points = min(
            settings.max_territory_health,
            current_health + points)
        return "defend"

    remaining_health = current_health - points

    if remaining_health <= 0:
        territory.team_id = user_team
        territory.health_points = min(
            settings.max_territory_health,
            settings.base_territory_health + abs(remaining_health))
        return "capture"

    territory.health_points = remaining_health
    return "attack"

def round_points(points: Decimal) -> Decimal:
    return points.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

# To do: Add challenge metric for complete route
def get_challenge_metrics(impact_progress: TerritoryListUpdate, territories_captured: int) -> Challenge_metrics:
    """Obtiene datos de todas las métricas de progreso para los desafíos"""
    return Challenge_metrics(
        total_time = impact_progress.total_time,
        walk_time = impact_progress.seconds_walk,
        run_time = impact_progress.seconds_run,
        bike_time = impact_progress.seconds_bike,
        total_distance = impact_progress.total_distance,
        walk_distance = impact_progress.meters_walk,
        run_distance = impact_progress.meters_run,
        bike_distance = impact_progress.meters_bike,
        captured_territories = territories_captured
    )

def apply_training_impact(
        db: Session,
        current_user: models.Users,
        impact_in: TerritoryListUpdate
    ) -> TerritoryImpactResponse:
    
    """Aplica un paquete de entrenamiento completo en una sola transaccion."""
    territory_results: list[TerritoryImpactResult] = []
    total_attack_points = 0
    total_defence_points = 0
    territories_captured = 0

    score_multiplier = 1
    boost_id = impact_in.boost_id
    
    if(boost_id is not None):
        db_boost = get_existing_boost(boost_id, db)
        removed = remove_boost_from_inventory(db, current_user, boost_id)

        if removed is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Potenciador no disponible en inventario",
            )
            
        if(db_boost.boost_type == Boost_Type.score):
            score_multiplier = db_boost.boost_effect
        
    try:
        # Bloquea al usuario
        locked_user = (
            db.query(models.Users)
            .filter(
                models.Users.user_id == current_user.user_id
            )
            .with_for_update()
            .one()
        )

        # Orden fijo para reducir posibilidad de deadlocks
        territories = sorted(
            impact_in.territories,
            key=lambda x: x.territory_id
        )

        for territory_input in territories:
            territory = get_locked_territory(db, territory_input.territory_id)

            if territory is None:
                new_territory = TerritoryCreate(
                    territory_id = territory_input.territory_id
                )
                territory = create_territory(db, new_territory)

            points = round_points(territory_input.points) * score_multiplier
            action = apply_points(territory, locked_user.user_team, points)

            match action:
                case "defend":
                    total_defence_points += points
                case "attack":
                    total_attack_points += points
                case "capture":
                    territories_captured += 1
                    total_attack_points += points

            # Obtener información del equipo
            team = None
            if territory.team_id is not None:
                team = (
                    db.query(models.Team)
                    .filter(
                        models.Team.team_id ==
                        territory.team_id
                    )
                    .first()
                )

            team_response = None
            if team:
                team_response = TerritoryOwnerResponse(
                    team_id = team.team_id,
                    team_name = team.team_name,
                    team_color = team.team_color
                )

            territory_results.append(
                TerritoryImpactResult(
                    territory_id = territory.territory_id,
                    team = team_response,
                    health_points = territory.health_points,
                    action = action
                )
            )

        # Actualiza estadísticas del usuario
        locked_user.total_distance = (
            Decimal(locked_user.total_distance or 0)
            + impact_in.total_distance
        )

        locked_user.total_time = (
            int(locked_user.total_time or 0)
            + impact_in.total_time
        )

        locked_user.total_attack = (
            int(locked_user.total_attack or 0)
            + total_attack_points
        )

        locked_user.total_defence = (
            int(locked_user.total_defence or 0)
            + total_defence_points
        )
        locked_user.territories_captured = (
            int(locked_user.territories_captured or 0)
            + territories_captured
        )

        unlocked_achievements = check_achievements(db, locked_user)
        challenge_progress = get_challenge_metrics(impact_in, territories_captured)
        progressed_challenges = check_challenges(db, current_user, challenge_progress)
        training = give_training_xp(current_user, challenge_progress)
        db.commit()
        
        achievements_results = [
            build_achievement_response(achievement)
            for achievement in unlocked_achievements
        ]

        challenges_results = [
            build_started_challenge_response(db, db_started_challenge, None)
            for db_started_challenge in progressed_challenges
        ]

        return TerritoryImpactResponse(
            user = UserImpactResult(
                user_id = locked_user.user_id,
                user_name = locked_user.user_name,
                total_distance = locked_user.total_distance,
                total_time = locked_user.total_time,
                total_territories = locked_user.territories_captured,
                total_attack = locked_user.total_attack,
                total_defence = locked_user.total_defence
            ),
            training = training,
            territories = territory_results,
            achievements = achievements_results,
            challenges = challenges_results
        )

    except Exception:
        db.rollback()
        raise