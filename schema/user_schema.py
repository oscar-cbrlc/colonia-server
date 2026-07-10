from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# todos comparten las credenciales de identificación
class UserBase(BaseModel):
    email: EmailStr
    user_name: str

# para la creación de un usuario, solo se permite email, username y password
class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# para actualización del usuario
class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    password: Optional[str] = None

    total_distance: Optional[float] = None
    total_time: Optional[float] = None
    
    user_team: Optional[int] = None
    team_role: Optional[int] = None
    
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    avatar_color: Optional[int] = None
    
    coin_amount: Optional[int] = None
    user_thumbnail: Optional[str] = None

# Respuesta de la API. No se devuelve password
class UserResponse(UserBase):
    user_id: int
    user_type: int
    user_team: Optional[int] = None
    team_role: Optional[int] = None
    
    total_distance: float = 0.0
    total_time: float = 0.0
    
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    avatar_color: int = 13398016

    coin_amount: int = 0
    user_thumbnail: Optional[str] = None

    # siempre en los Response
    model_config = ConfigDict(from_attributes=True)

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
