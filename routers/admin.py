from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import user_crud, team_crud
from utils.auth import get_current_user
from model import models
from enums.enum_types import UserType

router = APIRouter(
    prefix="/admin",
    tags=["Operaciones de administrador"]
)

@router.delete("/users/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        current_user: models.Users = Depends(get_current_user),  
        db: Session = Depends(get_db)
    ):
    """
    Elimina completamente un usuario de la base de datos.
    """
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden realizar esta acción."
        )
    
    db_user = user_crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return

@router.delete("/team/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
        team_id: int,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """
    Remueve a los usuarios de un equipo y luego lo elimina.
    """
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden realizar esta acción."
        )
    
    db_team = team_crud.admin_delete(db, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return