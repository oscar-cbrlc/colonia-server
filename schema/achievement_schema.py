from pydantic import BaseModel, ConfigDict
from typing import Optional

class AchievementBase(BaseModel):
    achievement_name: str
    achievement_type: int
    achievement_objective: int

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    achievement_name: Optional[str] = None
    achievement_type: int
    achievement_objective: int
    
class AchievementResponse(BaseModel):
    achievement_id: int
    achievement_name: str
    achievement_type: str
    achievement_objective: int
    model_config = ConfigDict(from_attributes=True)
