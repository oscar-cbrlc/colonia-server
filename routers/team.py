from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.team_schema import TeamCreate, TeamResponse, TeamUpdate
from crud import team_crud
from typing import List, Optional

router = APIRouter(
    prefix="/team",
    tags=["Perfil de equipo"]
)

@router.post("/register", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def register(team_in: TeamCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo equipo, validando que el nombre no este ya registrado
    """
    db_team = team_crud.get_team_by_name(db, name=team_in.team_name)
    if db_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de equipo ya registrado"
        )
    return team_crud.create_team(db=db, team_in=team_in)

@router.get("/team", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de un usuario en específico, dado su id.
    """
    db_team = team_crud.get_team_by_id(db, team_id==team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return db_team

@router.get("/", response_model=List[TeamResponse])
async def get_teams(
        id: Optional[int] = None,
        name: Optional[str] = None,
        limit: int = 100,
        db: Session = Depends(get_db) 
    ):
    """
    Retorna uno o más equipos: uno si se filtra por id o email, o todos (limite 100) si no.
    """
    if id is not None:
        db_team = team_crud.get_team_by_id(db, team_id=id)
        if not db_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado"
            )
        return [db_team]
    elif name is not None:
        db_team = team_crud.get_team_by_name(db, team_name=name)
        if not db_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado"
            )
        return [db_team]
    else:
        db_teams = team_crud.get_all_teams(db, limit=limit)
        return db_teams
    
@router.patch("/team", response_model=TeamResponse)
def update_team(teamUpdate: TeamUpdate, team_id: int, db: Session = Depends(get_db)):
    """
    Actualiza datos del perfil de equipo.
    """
    db_team = team_crud.get_team_by_id(db, team_id=team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return team_crud.update_team(db=db, db_team=db_team, team_update=teamUpdate)

@router.delete("/team", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """
    Elimina completamente un equipo de la base de datos.
    """
    success = team_crud.delete_team(db=db, team_id=team_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return