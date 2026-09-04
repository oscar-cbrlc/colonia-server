from sqlalchemy.orm import Session
from sqlalchemy import text
from model import models
from schema.territory_schema import (
    TerritoryCreate,
    TerritoryUpdate,
    TerritoryOwnerResponse,
    UserImpactResult,
    TerritoryListUpdate,
    TerritoryImpactResult,
    TerritoryImpactResponse,
)
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from config import settings

def get_territory_model_by_id(db: Session, territory_id: str):
    """Retorna únicamente el modelo del territorio."""
    return (
        db.query(models.Territory)
        .filter(
            models.Territory.territory_id == territory_id
        )
        .first()
    )

def get_territory_by_id(db: Session, territory_id: str):
    """Retorna información de un territorio por su ID único."""
    return (
        db.query(models.Territory, models.Team)
        .outerjoin(
            models.Team,
            models.Territory.team_id == models.Team.team_id
        )
        .filter(
            models.Territory.territory_id == territory_id
        )
        .first()
    )

def get_all_territories(db: Session, limit: Optional[int] = None):
    """Retorna información de todos los territorios."""
    query = (
        db.query(models.Territory, models.Team)
        .outerjoin(
            models.Team,
            models.Territory.team_id == models.Team.team_id
            )
        )
    if(limit is not None):
        query = query.limit(limit)

    return query

def get_all_team_territories(db: Session, team_id: int):
    """Retorna información de todos los territorios de un equipo."""
    return (
        db.query(models.Territory)
        .filter(
            models.Territory.team_id == team_id
        )
        .all()
    )

def create_territory(db: Session, territory_in: TerritoryCreate):
    """Crea un nuevo territorio en la base de datos"""
    db_territory = models.Territory(
        territory_id = territory_in.territory_id,
        team_id = territory_in.team_id,
        health_points = territory_in.health_points
    )
    db.add(db_territory)
    db.commit()
    db.refresh(db_territory)

    return db_territory

def update_territory(
        db: Session,
        current_user: models.Users,
        db_territory: models.Territory, 
        territory_update: TerritoryUpdate
    ):
    """
    Aplica puntos a un territorio y determina si la acción 
    es ataque, defensa o captura.
    """
    update_data = territory_update.model_dump(
        exclude_unset=True,
        exclude={"territory_id"}
    )
    
    for key, value in update_data.items():
        setattr(db_territory, key, value)

    db.commit()
    db.refresh(db_territory)

    return db_territory

def get_locked_territory(db: Session,territory_id: str):
    """Obtiene y bloquea un territorio para evitar modificaciones simultáneas."""
    return (
        db.query(models.Territory)
        .filter(
            models.Territory.territory_id == territory_id
        )
        .with_for_update()
        .first()
    )

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

        # Actualiza estadísticas del usuario
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
                continue

            points = round_points(territory_input.points)
            action = apply_points(territory,locked_user.user_team,points)

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
                    team_id=team.team_id,
                    team_name=team.team_name,
                    team_color=team.team_color
                )

            results.append(
                TerritoryImpactResult(
                    territory_id=territory.territory_id,
                    team=team_response,
                    health_points=territory.health_points,
                    action=action
                )
            )
        db.commit()

        return TerritoryImpactResponse(
            user=UserImpactResult(
                user_id=locked_user.user_id,
                user_name=locked_user.user_name,
                total_distance=locked_user.total_distance,
                total_time=locked_user.total_time
            ),
            territories=results
        )

    except Exception:
        db.rollback()
        raise