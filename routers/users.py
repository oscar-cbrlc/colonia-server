from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserCreate, UserLogin, UserLoginResponse, UserResponse, UserUpdate
from crud import user_crud
from utils.security import create_access_token
from typing import List, Optional
from utils.auth import get_current_user
from model import models

# la ruta  raiz de cada users endpoint seria http://<api>/users
router = APIRouter(
    prefix="/users",
    tags=["Autenticación y Perfil de Usuario"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario, validando que el correo no esté ya registrado
    """
    db_user = user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico ya registrado"
        )
    return user_crud.create_user(db=db, user_in=user_in)

@router.post("/login", response_model=UserLoginResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Valida el correo y contrasena de un usuario.
    """
    db_user = user_crud.authenticate_user(
        db=db,
        email=user_in.email,
        password=user_in.password
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos"
        )
    access_token = create_access_token(
        data={
            "sub": str(db_user.user_id),
            "email": db_user.email
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/getUser", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de un usuario en específico, dado su id.
    """
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_user

@router.get("/getUsers", response_model=List[UserResponse])
async def get_users(
        id: Optional[int] = None,
        email: Optional[str] = None,
        limit: int = 100,
        db: Session = Depends(get_db) 
    ):
    """
    Retorna uno o más usuarios: uno si se filtra por id o email, o todos (limite 100) si no.
    """
    if id is not None:
        db_user = user_crud.get_user_by_id(db, user_id=id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return [db_user]
    elif email is not None:
        db_user = user_crud.get_user_by_email(db, email=email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return [db_user]
    else:
        db_users = user_crud.get_all_users(db, limit=limit)
        return db_users
    
@router.patch("/update", response_model=UserResponse)
def update_user(
        user_update: UserUpdate, 
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Actualiza datos del perfil de usuario.
    """
    user_id = current_user
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user_crud.update_user(db=db, db_user=db_user, user_update=user_update)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        current_user: models.Users = Depends(get_current_user),  
        db: Session = Depends(get_db)
    ):
    """
    Elimina completamente un usuario de la base de datos.
    """
    user_id = current_user.user_id
    db_user = user_crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return