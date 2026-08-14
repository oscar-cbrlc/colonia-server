from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class TrainingNodeImpact(BaseModel):
    """Nodo completado durante una sesion de entrenamiento."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    points: Decimal = Field(gt=0, le=1000000)
    timestamp: datetime


class TerritoryImpactRequest(BaseModel):
    """Paquete generado al finalizar una sesion de entrenamiento."""

    total_distance: Decimal = Field(ge=0, le=1000000)
    duration_seconds: int = Field(ge=0, le=604800)
    nodes: list[TrainingNodeImpact] = Field(min_length=1, max_length=2000)


class TerritoryImpactResult(BaseModel):
    territory_id: int
    h3_index: str
    team_id: int | None
    health_points: int
    points_applied: int
    action: Literal["attack", "defend", "capture"]


class TerritoryImpactResponse(BaseModel):
    user_id: int
    total_distance: float
    total_time: float
    territories: list[TerritoryImpactResult]
