from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class TeamBase(BaseModel):
    team_name: str
    team_color: int
    is_public: bool

class TeamCreate(TeamBase):
    team_description: Optional[str] = None

class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    team_description: Optional[str] = None
    team_color: Optional[int] = None
    is_public: Optional[bool] = None

class TeamStats(BaseModel):
    member_count: int
    territories_controlled: int
    total_defense_points: float

class TeamMember(BaseModel):
    user_id: int
    user_name: str
    user_thumbnail: Optional[str] = None
    team_role: str

    model_config = ConfigDict(from_attributes=True)

class TeamModelResponse(TeamBase):
    team_id: int
    stats: Optional[TeamStats] = None
    
    model_config = ConfigDict(from_attributes=True)

class TeamResponse(TeamBase):
    team_id: int
    team_description: Optional[str] = None
    stats: TeamStats
    members: List[TeamMember]

    model_config = ConfigDict(from_attributes=True)