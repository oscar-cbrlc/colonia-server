from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserSessionBase(BaseModel):
    user_id: int
    jti: str
    expires_at: datetime

class UserSessionCreate(UserSessionBase):
    pass

class UserTokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserSessionResponse(BaseModel):
    session_id: int
    user_id: int
    jti: str
    created_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
