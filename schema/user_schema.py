from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# todos comparten las credenciales de identificación
class UserBase(BaseModel):
    email: EmailStr
    user_type: int
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
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None
    

# Respuesta de la API. No se devuelve password
class UserResponse(UserBase):
    user_id: int
    user_type: int
    user_team: Optional[int] = None
    team_role: Optional[int] = None
    
    total_distance: float = 0.0
    total_time: int = 0
    
    avatar_head: Optional[int] = None
    avatar_neck: Optional[int] = None
    avatar_body: Optional[int] = None
    avatar_footwear: Optional[int] = None

    # siempre en los Response
    model_config = ConfigDict(from_attributes=True)
