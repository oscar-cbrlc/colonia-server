from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserResponse
from schema.team_schema import TeamCreate, TeamResponse, TeamModelResponse, TeamUpdate, TeamStats
from utils.auth import get_current_user
from crud import team_crud, user_crud
from typing import List
from model import models

router = APIRouter(
    prefix="/teams",
    tags=["Perfil de equipo"]
)

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def register(
        team_in: TeamCreate,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """
    Registra un nuevo equipo, validando que el nombre no este ya registrado y asignando el usuario actual como su lider
    """

    db_team = team_crud.create_team(db, current_user, team_in)
    team_stats = team_crud.get_team_stats(db, db_team.team_id)
    db_users = user_crud.get_team_members_response(db, db_team.team_id)
 
    return {
        "team_id": db_team.team_id,
        "team_name": db_team.team_name,
        "team_description": db_team.team_description,
        "team_color": db_team.team_color,
        "is_public": db_team.is_public,
        "stats": team_stats,
        "members": db_users
    }

@router.get("/", response_model=List[TeamModelResponse])
def get_all_teams(limit: int | None = None, db: Session = Depends(get_db)):
    """Retorna la información de todos los equipos."""
    db_teams = team_crud.get_all_teams(db, limit)
    db_users = user_crud.get_team_members_response(db, team_id)

    return [
        {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "team_color": team.team_color,
            "is_public": team.is_public,
            "stats": team_crud.get_team_stats(db, team.team_id),
        }
        for team in db_teams
    ]

@router.get("/search-name", response_model=List[TeamModelResponse])
def search_teams_by_name(
        team_name: str,
        limit: int = 100,
        db: Session = Depends(get_db)
    ):
    """
        Retorna los equipos cuyo nombre contenga el texto enviado.
    """
    db_teams = team_crud.search_teams_by_name(db, team_name, limit)
    if not db_teams:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay equipos con ese nombre"
            )

    return [
        {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "team_color": team.team_color,
            "is_public": team.is_public,
            "stats": team_crud.get_team_stats(db, team.team_id),
        }
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
    
    team_stats = team_crud.get_team_stats(db, team_id)
    db_users = user_crud.get_team_members_response(db, team_id)
    
    return {
        "team_id": db_team.team_id,
        "team_name": db_team.team_name,
        "team_description": db_team.team_description,
        "team_color": db_team.team_color,
        "is_public": db_team.is_public,
        "stats": team_stats,
        "members": db_users
    }
    
@router.patch("/", response_model=TeamModelResponse)
def update_team(
        team_update: TeamUpdate, 
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """
    Actualiza datos del perfil de equipo.
    """
    team_id = current_user.user_team
    db_team = team_crud.get_team_by_id(db, team_id=team_id)
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
    return team_crud.update_team(db=db, db_team=db_team, team_update=team_update)

@router.delete("/mine", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """
    Elimina el equipo del usuario autenticado de la base de datos.
    """
    team_crud.delete_team(db, current_user)

@router.patch("/{team_id}/me/join", response_model=UserResponse)
def join_team(
        team_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Inscribe al usuario autenticado en un equipo, actualizando user.team_id.
    """
    return user_crud.user_join_team(db, current_user, team_id)

@router.patch("/me/leave", response_model=UserResponse)
def leave_team(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Elimina al usuario autenticado de su equipo, actualizando user.user_team en Null
    """
    return user_crud.exit_team(db, current_user)

@router.patch("/members/{user_id}/kick", response_model=UserResponse)
def kick_from_team(
        user_id: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Elimina a un usuario de su equipo, actualizando user.user_team en Null.
    """
    if not user_crud.is_moderator(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo moderadores pueden realizar esta acción"
        )
    return user_crud.kick_from_team(db, current_user, user_id)

@router.patch("/members/{user_id}/role", response_model=UserResponse)
def update_team_role(
        user_id: int,
        team_role: int,
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """
    Actualiza el rol de equipo de un usuario, actualizando user.team_role.
    """
    if not user_crud.is_leader(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo el lider pueden realizar esta acción"
        )
    return user_crud.change_team_role(db, current_user, user_id, team_role)

