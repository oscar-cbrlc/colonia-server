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

class TerritoryListUpdate(BaseModel):
    total_distance: Decimal
    total_time: int
    timestamp: datetime
    boost_id: Optional[int] = None
    territories: list[TerritoryBase]
    seconds_walk: int
    seconds_run: int
    seconds_bike: int
    meters_walk: Decimal
    meters_run: Decimal
    meters_bike: Decimal
    
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

class UserImpactResult(BaseModel):
    user_id: int
    user_name: str
    total_distance: Decimal
    total_time: int
    total_territories: int
    total_attack: int
    total_defence: int
    model_config = ConfigDict(from_attributes=True)

class TrainingResult(BaseModel):
    time_xp: int
    distance_xp: int
    territories_xp: int
    total_xp: int

class TerritoryImpactResult(BaseModel):
    territory_id: str
    team: Optional[TerritoryOwnerResponse]
    health_points: Decimal
    action: Literal["attack", "defend", "capture"]

class TerritoryImpactResponse(BaseModel):
    user: UserImpactResult
    training: TrainingResult
    territories: list[TerritoryImpactResult]
    achievements: Optional[list[AchievementResponse]] = None
    challenges: Optional[list[StartedChallengeResponse]] = None