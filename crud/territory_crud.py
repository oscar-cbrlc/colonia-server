from sqlalchemy.orm import Session
from model import models
from schema.territory_schema import TerritoryCreate, TerritoryUpdate
from crud import team_crud
from typing import Optional

def get_territory_by_id(db: Session, territory_id: int):
    """Busca un territorio por su ID único."""
    return (
        db.query(
            models.Territory.territory_id,
            models.Territory.health_points,
            models.Territory.team_id,
            models.Team.team_name,
            models.Team.team_color
        )
        .outerjoin(
            models.Team,
            models.Territory.team_id == models.Team.team_id
        )
        .filter(
            models.Territory.territory_id == territory_id
        )
        .first()
    )

def get_all_territories(db: Session, limit: Optional[int] = None):
    """Retorna información de todos los territorios."""
    if(limit != None):
        return(
            db.query(
                models.Territory.territory_id,
                models.Territory.health_points,
                models.Territory.team_id,
                models.Team.team_name,
                models.Team.team_color
            )
            .outerjoin(
                models.Team,
                models.Territory.team_id == models.Team.team_id
            )
            .limit(limit)
        )
    else:
        return(
            db.query(
                models.Territory.territory_id,
                models.Territory.health_points,
                models.Territory.team_id,
                models.Team.team_name,
                models.Team.team_color
            )
            .outerjoin(
                models.Team,
                models.Territory.team_id == models.Team.team_id
            )
            .all()
        )

def create_territory(db: Session, territory_in: TerritoryCreate):
    """Crea un nuevo territorio en la base de datos"""
    
    db_territory = models.Territory(
        health_points = territory_in.health_points
    )
    db.add(db_territory)
    db.commit()
    db.refresh(db_territory)

    return db_territory

def update_territory(db: Session, db_territory: models.Territory, territory_update: TerritoryUpdate):
    """Actualiza la información del territorio."""
    # convierte el Schema TeamUpdate en diccionario excluyendo lo que no se envió
    update_data = territory_update.model_dump(exclude_unset=True)
    
    # se actualizan cada uno de los cambios
    for key, value in update_data.items():
        setattr(db_territory, key, value)
        
    db.commit()
    db.refresh(db_territory)
    return db_territory
