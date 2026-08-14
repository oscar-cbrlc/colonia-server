from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

import h3
from sqlalchemy import text
from sqlalchemy.orm import Session

from model import models
from schema.territory_schema import (
    TerritoryImpactRequest,
    TerritoryImpactResponse,
    TerritoryImpactResult,
)


H3_RESOLUTION = 10
BASE_TERRITORY_HEALTH = 1000
MAX_TERRITORY_HEALTH = 5000


def _group_points_by_territory(
    impact_in: TerritoryImpactRequest,
) -> dict[str, Decimal]:
    points_by_h3: dict[str, Decimal] = defaultdict(Decimal)

    for node in impact_in.nodes:
        h3_index = h3.latlng_to_cell(node.lat, node.lon, H3_RESOLUTION)
        points_by_h3[h3_index] += node.points

    return dict(points_by_h3)


def _round_points(points: Decimal) -> int:
    """Convierte los puntos acumulados al entero que almacena PostgreSQL."""
    return max(1, int(points.quantize(Decimal("1"), rounding=ROUND_HALF_UP)))


def _get_locked_territory(db: Session, h3_index: str):
    # Evita que dos peticiones creen o modifiquen el mismo cuadrante a la vez.
    db.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:h3_index))"),
        {"h3_index": h3_index},
    )

    return (
        db.query(models.Territory)
        .filter(models.Territory.location["h3_index"].astext == h3_index)
        .with_for_update()
        .first()
    )


def _apply_points(
    territory: models.Territory,
    user_team: int,
    points: int,
) -> str:
    if territory.team_id == user_team:
        territory.health_points = min(
            MAX_TERRITORY_HEALTH,
            territory.health_points + points,
        )
        return "defend"

    remaining_health = territory.health_points - points
    if remaining_health < 0:
        territory.team_id = user_team
        territory.health_points = min(
            MAX_TERRITORY_HEALTH,
            BASE_TERRITORY_HEALTH + abs(remaining_health),
        )
        return "capture"

    territory.health_points = remaining_health
    return "attack"


def apply_training_impact(
    db: Session,
    current_user: models.Users,
    impact_in: TerritoryImpactRequest,
) -> TerritoryImpactResponse:
    """Aplica un paquete de entrenamiento completo en una sola transaccion."""
    points_by_h3 = _group_points_by_territory(impact_in)
    results: list[TerritoryImpactResult] = []

    try:
        locked_user = (
            db.query(models.Users)
            .filter(models.Users.user_id == current_user.user_id)
            .with_for_update()
            .one()
        )

        locked_user.total_distance = (
            Decimal(locked_user.total_distance or 0) + impact_in.total_distance
        )
        locked_user.total_time = (
            Decimal(locked_user.total_time or 0) + impact_in.duration_seconds
        )

        # El orden fijo de los bloqueos reduce el riesgo de interbloqueos.
        for h3_index in sorted(points_by_h3):
            points = _round_points(points_by_h3[h3_index])
            territory = _get_locked_territory(db, h3_index)

            if territory is None:
                territory = models.Territory(
                    location={"h3_index": h3_index},
                    health_points=BASE_TERRITORY_HEALTH,
                    team_id=None,
                )
                db.add(territory)
                db.flush()

            action = _apply_points(territory, locked_user.user_team, points)
            results.append(
                TerritoryImpactResult(
                    territory_id=territory.territory_id,
                    h3_index=h3_index,
                    team_id=territory.team_id,
                    health_points=territory.health_points,
                    points_applied=points,
                    action=action,
                )
            )

        db.commit()
        return TerritoryImpactResponse(
            user_id=locked_user.user_id,
            total_distance=float(locked_user.total_distance),
            total_time=float(locked_user.total_time),
            territories=results,
        )
    except Exception:
        db.rollback()
        raise
