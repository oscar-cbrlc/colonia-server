from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud import territory_crud
from database import get_db
from model import models
from schema.territory_schema import TerritoryImpactRequest, TerritoryImpactResponse
from utils.auth import get_current_user


router = APIRouter(
    prefix="/territories",
    tags=["Territorios"],
)


@router.post("/impact", response_model=TerritoryImpactResponse)
def apply_training_impact(
    impact_in: TerritoryImpactRequest,
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Procesa puntos y cuadrantes al terminar una sesion de entrenamiento."""
    if current_user.user_team is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario debe pertenecer a un equipo para impactar territorios",
        )

    return territory_crud.apply_training_impact(db, current_user, impact_in)
