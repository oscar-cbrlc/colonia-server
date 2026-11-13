from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from model import models
from schema.team_request_schema import UserRequestResponse, TeamRequestResponse
from schema.notification_schema import NotificationCreate
from utils.auth import get_current_user
from crud import team_request_crud, user_crud, team_crud
from routers.notification import create_user_notification
from enums.enum_types import TeamRole, Notification_Type
from routers.team import check_team_user_limit

router = APIRouter(
    prefix="/teamRequest",
    tags=["Solicitudes de Equipo"]
)

def request_exists(db: Session, user_id: int, team_id: int):
    """Verifica si existe una solicitud para ingresar al equipo del id realizada por parte el usuario del id"""
    db_request = team_request_crud.get_request_by_id(db, user_id, team_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    return db_request

def verify_user_permission(user: models.Users):
    """Verifica si el usuario tiene permiso para aceptar o rechazar solicitudes"""
    if not user_crud.is_moderator(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los moderadores pueden realizar esta operación."
        )
    
@router.post("/", response_model=UserRequestResponse, status_code=status.HTTP_201_CREATED)
def register(
        team_id: int,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """
    Registra una solicitud nueva.
    """
    if current_user.user_team is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya pertenece a un equipo."
        )
    
    db_request = team_request_crud.create_request(db, current_user, team_id)
    db_team = team_crud.get_team_by_id(db, team_id)

    return {
        "request_timestamp": db_request.request_timestamp,
        "team": db_team
    }

@router.get("/me", response_model=List[UserRequestResponse])
def get_all_my_request(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Retorna las solicitudes realizadas por el usuario.
    """
    results = team_request_crud.get_all_my_request(db,current_user)

    return [
        {
            "request_timestamp": request.request_timestamp,
            "team": team
        }
        for request, team in results
    ]

@router.get("/team/me", response_model=List[TeamRequestResponse])
def get_all_request_for_team(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Retorna la información de todas las solicitudes del equipo del usuario.
    """
    if not user_crud.is_moderator(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo los moderadores pueden realizar esta acción."
        )
    
    results = team_request_crud.get_all_request_for_team(db,current_user)

    return [
        {
            "request_timestamp": request.request_timestamp,
            "user": user
        }
        for request, user in results
    ]

@router.patch("/{user_id}/accept", response_model=TeamRequestResponse)
def accept_request(
        user_id: int, 
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Acepta una solicitud enviada al equipo dada su id.
    Elimina el resto de solicitudes del usuario.
    """

    db_request = request_exists(db, user_id, current_user.user_team)
    verify_user_permission(current_user)
    
    check_team_user_limit(current_user.user_team)
    create_user_notification(db, current_user.user_team, Notification_Type.join_team_request_accepted, user_id)

    db_user = user_crud.get_user_by_id(db, db_request.user_id)
    user_crud.assign_user_to_team(db, db_user, current_user.user_team, TeamRole.member)
    team_request_crud.delete_all_requests_by_user(db, db_request.user_id)
    return {
            "request_timestamp": db_request.request_timestamp,
            "user": db_user
        }

@router.patch("/{user_id}/reject", response_model=TeamRequestResponse)
def reject_request(
        user_id: int, 
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Rechaza una solicitud enviada al equipo dada su id.
    """  

    db_request = request_exists(db, user_id, current_user.user_team)
    verify_user_permission(current_user)

    create_user_notification(db, current_user.user_team, Notification_Type.join_team_request_denied, user_id)

    db_user = user_crud.get_user_by_id(db, db_request.user_id)
    team_request_crud.delete_request(db, user_id, current_user.user_team)
    return {
            "request_timestamp": db_request.request_timestamp,
            "user": db_user
        }

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
        team_id: int,
        current_user: models.Users = Depends(get_current_user),  
        db: Session = Depends(get_db)
    ):
    """
    Elimina solicitudes del usuario autenticado.
    """
    db_request = request_exists(db, current_user.user_id, team_id)
    team_request_crud.delete_request(db, db_request.user_id, team_id)
    return

