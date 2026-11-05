from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    notification_message: str
    notification_type: int

class NotificationCreate(NotificationBase):
    user_id: Optional[int]

class NotificationResponse(BaseModel):
    notification_id: int
    notification_type: str
    notification_message: str
    notification_date: datetime
    model_config = ConfigDict(from_attributes=True)