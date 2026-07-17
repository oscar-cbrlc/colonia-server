from sqlalchemy.orm import Session
from model import models
from schema.team_schema import TeamCreate, TeamUpdate

def get_all_teams(db: Session, limit=100):
    """Retorna todos los equipos con un límite."""
    return db.query(models.Team).limit(limit).all()

def get_team_by_id(db: Session, team_id: int):
    """Busca un equipo por su ID único."""
    return db.query(models.Team).filter(models.Team.team_id == team_id).first()

def get_team_by_name(db: Session, team_name: str):
    """Busca un equipo por su nombre."""
    return db.query(models.Team).filter(models.Team.team_name == team_name).first()

def create_team(db: Session, team_in: TeamCreate):
    """Crea un nuevo equipo en la base de datos"""
    
    db_team = models.Team(
        team_name = team_in.team_name,
        team_description = team_in.team_description,
        team_color = team_in.team_color,
        access_type = team_in.access_type
    )
    db.add(db_team)
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

def delete_team(db: Session, team_id: int) -> bool:
    """Elimina permanentemente a un equipo de la base de datos."""
    db_team = db.query(models.Team).filter(models.Team.team_id == team_id).first()
    if not db_team:
        return False
        
    db.delete(db_team)
    db.commit()
    return True