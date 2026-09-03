from sqlalchemy.orm import Session
from model import models
from schema.team_schema import TeamCreate, TeamUpdate, TeamStats
from crud import user_crud, territory_crud
from fastapi import HTTPException, status
from enums.enum_types import TeamRole
from typing import Optional

def get_all_teams(db: Session, limit: Optional[int]):
    """Retorna todos los equipos con un límite."""
    if (limit != None):
        return db.query(models.Team).limit(limit).all()
    else:
        return db.query(models.Team).all()

def get_team_by_id(db: Session, team_id: int):
    """Busca un equipo por su ID único."""
    return db.query(models.Team).filter(models.Team.team_id == team_id).first()

def get_team_by_name(db: Session, team_name: str):
    """Busca un equipo por su nombre."""
    return db.query(models.Team).filter(models.Team.team_name == team_name).first()

def search_teams_by_name(
        db: Session,
        team_name: str,
        limit: int
    ):
    """
    Busca equipos cuyo nombre contenga el texto indicado.
    """

    return (
        db.query(models.Team)
        .filter(models.Team.team_name.ilike(f"%{team_name}%"))
        .order_by(models.Team.team_name)
        .limit(limit)
        .all()
    )

def get_team_stats(db: Session, team_id: int):
    """Obtiene las estadisticas de un equipo."""

    db_territories = territory_crud.get_all_team_territories(db, team_id)
    db_users = user_crud.get_all_team_users(db, team_id)

    user_count = len(db_users)
    territory_count = len(db_territories)

    territory_pts = 0
    for territory in db_territories:
        territory_pts += territory.health_points

    return TeamStats(
        member_count = user_count,
        territories_controlled = territory_count,
        total_defense_points = territory_pts
    )

def create_team(db: Session, current_user: models.Users, team_in: TeamCreate):
    """Crea un nuevo equipo en la base de datos"""
    find_team = get_team_by_name(db, team_name=team_in.team_name)
    if find_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de equipo ya registrado"
        )

    db_team = models.Team(
        team_name = team_in.team_name,
        team_description = team_in.team_description,
        team_color = team_in.team_color,
        is_public = team_in.is_public
    )
    db.add(db_team)
    db.flush()

    user_crud.assign_user_to_team(db, current_user, db_team.team_id, TeamRole.leader)
    db.commit()
    db.refresh(db_team)

    return db_team

def update_team(db: Session, db_team: models.Team, team_update: TeamUpdate):
    """Actualiza la información del equipo."""
    # convierte el Schema TeamUpdate en diccionario excluyendo lo que no se envió
    update_data = team_update.model_dump(exclude_unset=True)
    
    # se actualizan cada uno de los cambios
    for key, value in update_data.items():
        setattr(db_team, key, value)
        
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_team(db: Session, current_user: models.Users):
    """Elimina permanentemente a un equipo de la base de datos."""
    team_id = current_user.user_team
    db_team = get_team_by_id(db, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    
    if not user_crud.is_leader(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo el líder puede eliminar el equipo."
        )
    
    members = user_crud.get_all_team_users(db, team_id)
    if len(members) > 1:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un equipo que aún tiene miembros."
        )
    
    user_crud.remove_user_from_team(db, current_user, is_kick=False)
    db.flush()
    db.delete(db_team)
    db.commit()

def remove_all_team_users(db: Session, team_id: int):
    """Remueve todos los usuarios de un equipo"""
    team_users = user_crud.get_all_team_users(db, team_id)
    for user in team_users:
        user_crud.remove_user_from_team(db, user, is_kick=True)
    return team_users

def admin_delete(db: Session, team_id: int):
    """Remueve todos los usuarios de un equipo y lo elimina"""

    db_team = db.query(models.Team).filter(models.Team.team_id == team_id).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    
    remove_all_team_users(db, team_id)
    db.delete(db_team)
    db.commit()
    