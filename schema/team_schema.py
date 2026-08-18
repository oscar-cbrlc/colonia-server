from pydantic import BaseModel, ConfigDict
from typing import Optional

class TeamBase(BaseModel):
    team_name: str
    team_color: int
    is_public: bool

# Creación de equipo
class TeamCreate(TeamBase):
    team_description: Optional[str] = None

# Actualizar información de equipo
class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    team_description: Optional[str] = None
    team_color: Optional[int] = None
    is_public: Optional[bool] = None

class TeamResponse(TeamBase):
    team_id: int
    team_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)