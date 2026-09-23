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
)
from crud.territory_crud import create_territory, get_locked_territory
from routers.boosts import get_existing_boost
from crud.boost_inventory_crud import remove_boost_from_inventory
from decimal import Decimal, ROUND_HALF_UP
from config import settings
from utils.achievement_tracker import check_achievements
from utils.response_builder import build_achievement_response
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

def apply_training_impact(
        db: Session,
        current_user: models.Users,
        impact_in: TerritoryListUpdate
    ) -> TerritoryImpactResponse:
    
    """Aplica un paquete de entrenamiento completo en una sola transaccion."""
    results: list[TerritoryImpactResult] = []
    total_attack_points = 0
    total_defence_points = 0
    territories_captured = 0

    score_multiplier = 1
    boost_id = impact_in.boost_id
    if(boost_id is not None):
        db_boost = get_existing_boost(boost_id, db)
        removed = remove_boost_from_inventory(db, current_user, boost_id)
        if not removed:
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

        # Actualiza estadísticas de distancia y tiempo
        locked_user.total_distance = (
            Decimal(locked_user.total_distance or 0)
            + impact_in.total_distance
        )

        locked_user.total_time = (
            int(locked_user.total_time or 0)
            + impact_in.total_time
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

            results.append(
                TerritoryImpactResult(
                    territory_id = territory.territory_id,
                    team = team_response,
                    health_points = territory.health_points,
                    action = action
                )
            )

        # Actualiza estadísticas de usuario relacionadas a puntaje
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
        db.commit()
        
        achievements_results = [
            build_achievement_response(achievement)
            for achievement in unlocked_achievements
        ]

        return TerritoryImpactResponse(
            user = UserImpactResult(
                user_id = locked_user.user_id,
                user_name = locked_user.user_name,
                total_distance = locked_user.total_distance,
                total_time = locked_user.total_time
            ),
            territories = results,
            achievements = achievements_results
        )

    except Exception:
        db.rollback()
        raise