from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ObtainedAchievementCreate(BaseModel):
    achievement_id: int
    user_id: int

class AchievementDetails(BaseModel):
    achievement_id: int
    achievement_name: str
    achievement_type: str
    achievement_objective: int
    achievement_acquisition_date: Optional[datetime] = None