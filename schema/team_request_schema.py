from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class RequestCreate(BaseModel):
    team_id: int

class RequestTeamResponse(BaseModel):
    team_id: int
    team_name: str
    team_color: int

class RequestUserResponse(BaseModel):
    user_id: int
    user_name: str
    user_thumbnail: Optional[str] = None

class TeamRequestResponse(BaseModel):
    request_timestamp: datetime
    user: RequestUserResponse

    model_config = ConfigDict(from_attributes=True)

class UserRequestResponse(BaseModel):
    request_timestamp: datetime
    team: RequestTeamResponse

    model_config = ConfigDict(from_attributes=True)