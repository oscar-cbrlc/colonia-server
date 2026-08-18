from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class TerritoryBase(BaseModel):
    health_points: int

# Creación de territorio
class TerritoryCreate(TerritoryBase):
    pass

# Actualizar información de territorio
class TerritoryUpdate(BaseModel):
    territory_id: int
    health_points: int
    team_id: Optional[int] = None

class TerritoryResponse(TerritoryBase):
    territory_id: int
    team_id: Optional[int] = None
    team_name: Optional[str] = None
    team_color: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)