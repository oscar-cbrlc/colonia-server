from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class TerritoryCreate(BaseModel):
    team_id: Optional[int] = None
    health_points: int

class TerritoryUpdate(BaseModel):
    territory_id: str
    health_points: int
    team_id: Optional[int] = None

class TerritoryOwnerResponse(BaseModel):
    team_id: int
    team_name: str
    team_color: int

    model_config = ConfigDict(from_attributes=True)

class TerritoryResponse(BaseModel):
    territory_id: str
    health_points: int
    team: Optional[TerritoryOwnerResponse] = None
    model_config = ConfigDict(from_attributes=True)