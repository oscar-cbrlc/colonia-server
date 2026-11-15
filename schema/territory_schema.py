from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from schema.achievement_schema import AchievementResponse
from schema.started_challenges_schema import StartedChallengeResponse
from config import settings
class TerritoryBase(BaseModel):
    territory_id: str
    points: Decimal

class TerritoryCreate(BaseModel):
    territory_id: str
    health_points: int = settings.base_territory_health
    team_id: Optional[int] = None

class TerritoryUpdate(BaseModel):
    territory_id: str
    team_id: Optional[int] = None
    health_points: Decimal = settings.base_territory_health

class TerritoryOwnerResponse(BaseModel):
    team_id: int
    team_name: str
    team_color: int
    model_config = ConfigDict(from_attributes=True)

class TerritoryResponse(BaseModel):
    territory_id: str
    health_points: Decimal
    team: Optional[TerritoryOwnerResponse] = None
    model_config = ConfigDict(from_attributes=True)

class TerritoryImpactResult(BaseModel):
    territory_id: str
    team: Optional[TerritoryOwnerResponse]
    health_points: Decimal
    action: Literal["attack", "defend", "capture"]