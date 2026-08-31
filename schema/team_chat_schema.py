from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    chat_message: str

class MessageUserResponse(BaseModel):
    user_id: int
    user_thumbnail: Optional[str] = None
    username: str
    role: str

class MessageResponse(BaseModel):
    message_id: int
    chat_message: str
    message_date: datetime
    is_from_system: bool
    user: Optional[MessageUserResponse] = None
    model_config = ConfigDict(from_attributes=True)
