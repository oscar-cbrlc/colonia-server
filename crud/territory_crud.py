from sqlalchemy.orm import Session
from model import models
from schema.territory_schema import TerritoryCreate, TerritoryUpdate
from crud import team_crud
from typing import Optional

def get_territory_model_by_id(db: Session, territory_id: str):
    """
    Retorna únicamente el modelo del territorio.
    """
    return (
        db.query(models.Territory)
        .filter(
            models.Territory.territory_id == territory_id
        )
        .first()
    )

def get_territory_by_id(db: Session, territory_id: str):
    """Retorna información de un territorio por su ID único."""
    return (
        db.query(models.Territory, models.Team)
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

    query = (
        db.query(models.Territory, models.Team)
        .outerjoin(
            models.Team,
            models.Territory.team_id == models.Team.team_id
            )
        )
    
    if(limit is not None):
        query = query.limit(limit)

    return query

def create_territory(db: Session, territory_in: TerritoryCreate):
    """Crea un nuevo territorio en la base de datos"""
    
    db_territory = models.Territory(
        team_id = territory_in.team_id,
        health_points = territory_in.health_points
    )
    db.add(db_territory)
    db.commit()
    db.refresh(db_territory)

    return db_territory

def update_territory(db: Session, db_territory: models.Territory, territory_update: TerritoryUpdate):
    """Actualiza la información del territorio."""

    update_data = territory_update.model_dump(
        exclude_unset=True,
        exclude={"territory_id"}
    )
    
    for key, value in update_data.items():
        setattr(db_territory, key, value)

    db.commit()
    db.refresh(db_territory)

    return db_territory
