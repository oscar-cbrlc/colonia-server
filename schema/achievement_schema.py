from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from config import settings

class AchievementBase(BaseModel):
    achievement_name: str
    achievement_desc: str
    achievement_type: int
    achievement_objective: int
    achievement_image: str

class AchievementCreate(AchievementBase):
    pass

class AchievementUpdate(BaseModel):
    achievement_name: Optional[str] = None
    achievement_desc: Optional[str] = None
    achievement_type: int
    achievement_objective: int
    achievement_image: Optional[str] = None
    
class AchievementResponse(BaseModel):
    achievement_id: int
    achievement_name: str
    achievement_desc: str
    achievement_type: str
    achievement_objective: int
    achievement_image: str
    model_config = ConfigDict(from_attributes=True)
