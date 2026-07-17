from pydantic import BaseModel, ConfigDict
from typing import Optional

class TeamBase(BaseModel):
    team_name: str
    team_color: int
    access_type: int

# Creación de equipo
class TeamCreate(TeamBase):
    team_description: Optional[str] = None

# Actualizar información de equipo
class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    team_description: Optional[str] = None
    team_color: Optional[int] = None
    access_type: Optional[int] = None

class TeamResponse(TeamBase):
    team_id: int
    team_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)