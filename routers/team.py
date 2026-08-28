from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserResponse
from schema.team_schema import TeamCreate, TeamResponse, TeamModelResponse, TeamUpdate, TeamStats
from utils.auth import get_current_user
from crud import team_crud, user_crud
from typing import List
from model import models
from enums.enum_types import TeamRole
from utils.response_builder import get_user_response, build_team_data

router = APIRouter(
    prefix="/teams",
    tags=["Perfil de equipo"]
)

def user_in_team(db: Session, user_id: int, team_id: int):
    user_db = user_crud.get_user_by_id(db, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if(user_db.user_team != team_id):
        raise HTTPException(
            status_code=403,
            detail="Usuario no pertenece al equipo"
        )
    return user_db

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def register(
        team_in: TeamCreate,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Registra un nuevo equipo, validando que el nombre no este ya registrado y asignando el usuario actual como su lider"""

    db_team = team_crud.create_team(db, current_user, team_in)
    return build_team_data(db, db_team, details= True)

@router.get("/", response_model=List[TeamModelResponse])
def get_all_teams(limit: int | None = None, db: Session = Depends(get_db)):
    """Retorna la información de todos los equipos."""
    db_teams = team_crud.get_all_teams(db, limit)

    return [
        build_team_data(db, team, details = False)
        for team in db_teams
    ]

@router.get("/search-name", response_model=List[TeamModelResponse])
def search_teams_by_name(
        team_name: str,
        limit: int = 100,
        db: Session = Depends(get_db)
    ):
    """Retorna los equipos cuyo nombre contenga el texto enviado."""
    db_teams = team_crud.search_teams_by_name(db, team_name, limit)
    if not db_teams:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay equipos con ese nombre"
            )

    return [
        build_team_data(db, team, details = False)
        for team in db_teams
    ]

@router.get("/{team_id}", response_model=TeamResponse)
def get_team_by_id(team_id: int, db: Session = Depends(get_db)):
    """Retorna la información completa de un equipo en específico, dado su id."""

    db_team = team_crud.get_team_by_id(db, team_id=team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    
    return build_team_data(db, db_team, details= True)
    
@router.patch("/", response_model=TeamModelResponse)
def update_team(
        team_update: TeamUpdate, 
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Actualiza datos del perfil de equipo."""
    team_id = current_user.user_team
    db_team = team_crud.get_team_by_id(db, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    if not user_crud.is_moderator(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo el lider pueden realizar esta acción"
        )
    team_crud.update_team(db, db_team, team_update)
    return build_team_data(db, db_team, details= True)

@router.delete("/mine", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Elimina el equipo del usuario autenticado de la base de datos."""
    team_crud.delete_team(db, current_user)

@router.patch("/{team_id}/me/join", response_model=UserResponse)
def join_team(
        team_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Inscribe al usuario autenticado en un equipo, actualizando user.team_id."""
    user_crud.assign_user_to_team(db, current_user, team_id, TeamRole.member)
    return get_user_response(db, current_user)

@router.patch("/me/leave", response_model=UserResponse)
def leave_team(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Elimina al usuario autenticado de su equipo, actualizando user.user_team en Null"""
    user_crud.remove_user_from_team(db, current_user)
    return get_user_response(db, current_user)

@router.patch("/members/{user_id}/kick", response_model=TeamResponse)
def kick_from_team(
        user_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Elimina al usuario seleccionado de su equipo, actualizando user.user_team en Null."""
    if not user_crud.is_moderator(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo moderadores pueden realizar esta acción"
        )
    
    user_db = user_in_team(db, user_id, current_user.user_team)
    user_crud.remove_user_from_team(db, user_db)

    db_team = team_crud.get_team_by_id(db, current_user.user_team)
    return build_team_data(db, db_team, details= True)

@router.patch("/members/{user_id}/promote", response_model=TeamResponse)
def promote_member(
        user_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Promueve el rol de equipo de un usuario, dado su id."""
    if not user_crud.is_leader(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo el lider pueden realizar esta acción"
        )
    user_db = user_in_team(db, user_id, current_user.user_team)
    user_crud.promote_team_role(db, current_user, user_db)

    db_team = team_crud.get_team_by_id(db, current_user.user_team)
    return build_team_data(db, db_team, details= True)

@router.patch("/members/{user_id}/demote", response_model=TeamResponse)
def demote_member(
        user_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Denigra el rol de equipo de un usuario, dado su id."""
    if not user_crud.is_leader(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo el lider pueden realizar esta acción"
        )
    user_db = user_in_team(db, user_id, current_user.user_team)
    user_crud.demote_team_role(db, user_db)

    db_team = team_crud.get_team_by_id(db, current_user.user_team)
    return build_team_data(db, db_team, details= True)