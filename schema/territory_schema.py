from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
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
    territories: list[TerritoryBase]
    
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
    model_config = ConfigDict(from_attributes=True)

class TerritoryImpactResult(BaseModel):
    territory_id: str
    team: Optional[TerritoryOwnerResponse]
    health_points: Decimal
    action: Literal["attack", "defend", "capture"]

class TerritoryImpactResponse(BaseModel):
    user: UserImpactResult
    territories: list[TerritoryImpactResult]