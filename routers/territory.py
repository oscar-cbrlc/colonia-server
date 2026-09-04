from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.territory_schema import (
    TerritoryCreate, 
    TerritoryUpdate, 
    TerritoryResponse, 
    TerritoryListUpdate,
    TerritoryImpactResponse
)
from crud import territory_crud
from typing import List
from utils.auth import get_current_user
from model import models

router = APIRouter(
    prefix="/territory",
    tags=["Territorios"]
)

@router.post("/", response_model=TerritoryResponse, status_code=status.HTTP_201_CREATED)
def register(
        territory_in: TerritoryCreate,
        db: Session = Depends(get_db)
    ):
    """
    Registra un nuevo territorio
    """
    return territory_crud.create_territory(db, territory_in)

@router.get("/{territory_id}", response_model=TerritoryResponse)
def get_territory(territory_id: str, db: Session = Depends(get_db)):
    """
    Retorna la información de un territorio, dado su id.
    """
    result = territory_crud.get_territory_by_id(db, territory_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorio no encontrado"
        )
    
    db_territory, db_team = result
    return {
        "territory_id": db_territory.territory_id,
        "health_points": db_territory.health_points,
        "team": db_team
    }

@router.get("/", response_model=List[TerritoryResponse])
def get_all_territories(limit: int | None = None, db: Session = Depends(get_db)):
    """
    Retorna la información de todos los territorios.
    """
    results = territory_crud.get_all_territories(db, limit)
    if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El equipo no posee territorios"
            )
    
    return [
        {
            "territory_id": territory.territory_id,
            "health_points": territory.health_points,
            "team": team
        }
        for territory, team in results
    ]

@router.patch("/", response_model=TerritoryResponse)
def update_territory(territory_update: TerritoryUpdate,db: Session = Depends(get_db)):
    """
    Actualiza datos de un territorio.
    """
    territory_id = territory_update.territory_id
    db_territory = territory_crud.get_territory_model_by_id(db,territory_id)

    if not db_territory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorio no encontrado"
        )
    
    territory_crud.update_territory(db, db_territory, territory_update)
    result = territory_crud.get_territory_by_id(db, territory_id)
    db_territory, db_team = result

    return {
        "territory_id": db_territory.territory_id,
        "health_points": db_territory.health_points,
        "team": db_team
    }

@router.patch("/apply-points",response_model=TerritoryImpactResponse)
def apply_territory_impact(
        impact_in: TerritoryListUpdate,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Aplica los puntos obtenidos durante una sesiónde entrenamiento a los territorios recorridos."""
    if current_user.user_team is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no pertenece a ningún equipo."
        )

    return territory_crud.apply_training_impact(db, current_user, impact_in)