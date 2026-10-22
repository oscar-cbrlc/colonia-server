from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    chat_message: str

class MessageUserResponse(BaseModel):
    user_id: int
    user_thumbnail: Optional[str] = None
    username: str
    role: Optional[str] = None

class MessageResponse(BaseModel):
    message_id: int
    chat_message: str
    message_date: datetime
    message_type: str
    user: Optional[MessageUserResponse] = None
    model_config = ConfigDict(from_attributes=True)
