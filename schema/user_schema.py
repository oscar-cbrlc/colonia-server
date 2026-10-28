from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from schema.obtained_achievements_schema import AchievementDetails
from schema.avatar_item_schema import AvatarItemResponse

class UserBase(BaseModel):
    email: EmailStr
    user_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    password: Optional[str] = None

    total_distance: Optional[float] = None
    total_time: Optional[float] = None
    total_attack: Optional[int] = None
    total_defence: Optional[int] = None
    territories_captured: Optional[int] = None
    
    user_team: Optional[int] = None
    team_role: Optional[int] = None
    
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    avatar_color: Optional[int] = None
    
    coin_amount: Optional[int] = None
    user_thumbnail: Optional[str] = None

class UserAvatarUpdate(BaseModel):
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    avatar_color: Optional[int] = None

class UserAvatarResponse(BaseModel):
    user_thumbnail: Optional[str] = None
    model_url: str
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    avatar_color: int

class AvatarUpdateResponse(BaseModel):
    user_thumbnail: Optional[str] = None
    model_url: str
    avatar_head: Optional[AvatarItemResponse] = None
    avatar_neck: Optional[AvatarItemResponse] = None
    avatar_body: Optional[AvatarItemResponse] = None
    avatar_footwear: Optional[AvatarItemResponse] = None
    avatar_color: int

class UserStatsResponse(BaseModel):
    user_level: int = 0
    user_xp: int = 0
    total_distance: float = 0.0
    total_time: float = 0.0
    total_attack: int = 0
    total_defence: int = 0
    territories_captured: int = 0

class UserTeamResponse(BaseModel):
    team_id: int
    team_name: str
    team_role: str
    team_color: int

class UserBaseResponse(BaseModel):
    user_id: int
    user_name: str
    avatar: UserAvatarResponse
    stats: UserStatsResponse
    team: Optional[UserTeamResponse]
    achievements: list[AchievementDetails]
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    email: str
    user_type: str
    coin_amount: int
    avatar: UserAvatarResponse
    xp_for_next_level: int
    stats: UserStatsResponse
    team: Optional[UserTeamResponse]
    achievements: list[AchievementDetails]
    
    model_config = ConfigDict(from_attributes=True)

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
