from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserCreate, UserLogin, UserLoginResponse, UserResponse, UserUpdate
from crud import user_crud
from utils.security import create_access_token
from typing import List, Optional

# la ruta  raiz de cada users endpoint seria http://<api>/users
router = APIRouter(
    prefix="/users",
    tags=["Perfil de Usuario"]
)


@router.get("/user", response_model=UserResponse)
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

@router.get("/", response_model=List[UserResponse])
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
    
@router.patch("/user", response_model=UserResponse)
def update_user(user_update: UserUpdate, user_id: int, db: Session = Depends(get_db)):
    """
    Actualiza datos del perfil de usuario.
    """
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user_crud.update_user(db=db, db_user=db_user, user_update=user_update)

@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Elimina completamente un usuario de la base de datos.
    """
    success = user_crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return

