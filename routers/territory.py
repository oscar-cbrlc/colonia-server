from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.territory_schema import TerritoryCreate, TerritoryUpdate, TerritoryResponse
from schema.team_schema import TeamResponse
from crud import territory_crud, team_crud
from typing import List, Optional
from model import models

router = APIRouter(
    prefix="/territory",
    tags=["Territorios"]
)

@router.post("/register", response_model=TerritoryResponse, status_code=status.HTTP_201_CREATED)
def register(
        territory_in: TerritoryCreate,
        db: Session = Depends(get_db)
    ):
    """
    Registra un nuevo territorio
    """
    return territory_crud.create_territory(db, territory_in)

@router.get("/getbyId", response_model=TerritoryResponse)
def get_territory(territory_id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de un territorio, dado su id.
    """
    db_territory = territory_crud.get_territory_by_id(db, territory_id)
    if not db_territory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorio no encontrado"
        )
    return db_territory

@router.get("/getAll", response_model=List[TerritoryResponse])
def get_all_territories(limit: int | None = None, db: Session = Depends(get_db)):
    """
    Retorna la información de todos los territorios.
    """
    db_territories = territory_crud.get_all_territories(db, limit)
    return db_territories

@router.patch("/update", response_model=TerritoryResponse)
def update_territory(
        territory_update: TerritoryUpdate, 
        db: Session = Depends(get_db)
    ):
    """
    Actualiza datos de un territorio.
    """
    territory_id = territory_update.territory_id
    db_territory = territory_crud.get_territory_by_id(db, territory_id)
    if not db_territory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Territorio no encontrado"
        )
    return territory_crud.update_territory(db, db_territory, territory_update)