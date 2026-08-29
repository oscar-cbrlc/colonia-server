from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.team_request_schema import RequestCreate, UserRequestResponse, TeamRequestResponse
from utils.auth import get_current_user
from crud import team_request_crud, user_crud, team_crud
from typing import List
from model import models
from enums.enum_types import TeamRole

router = APIRouter(
    prefix="/teamRequest",
    tags=["Solicitudes de Equipo"]
)

@router.post("/", response_model=UserRequestResponse, status_code=status.HTTP_201_CREATED)
def register(
        request_in: RequestCreate,
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
    
    db_request = team_request_crud.create_request(db, current_user, request_in)
    db_team = team_crud.get_team_by_id(
        db,
        db_request.team_id
    )

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

    db_request = team_request_crud.get_request_by_id(db, user_id, current_user.user_team)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )

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

    db_request = team_request_crud.get_request_by_id(db, user_id, current_user.user_team)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    # Todo: Enviar notificación Solicitud denegada

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
    db_request = team_request_crud.get_request_by_id(db, current_user.user_id, team_id)
    
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    user_id = current_user.user_id
    if (user_id != db_request.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solicitud no pertenece a usuario."
        )
    
    team_request_crud.delete_request(db, current_user.user_id, team_id)
    return

