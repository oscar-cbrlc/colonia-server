from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from crud import user_crud, team_crud, challenge_crud, boost_reward_crud, active_challenges_crud
from schema.active_challenges_schema import EventCreate, ActiveChallengeCreate, ActiveChallengeResponse
from utils.auth import get_current_user
from utils.response_builder import build_active_challenge_response
from model import models
from enums.enum_types import UserType

router = APIRouter(
    prefix="/admin",
    tags=["Operaciones de administrador"]
)

def require_admin(current_user: models.Users = Depends(get_current_user),) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user

@router.post("/activeChallenge/events", response_model = ActiveChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate, 
    _: models.Users = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Crea un evento nuevo. Requiere permisos de administrador"""
    challenge_in = event_in.challenge
    db_challenge = challenge_crud.create_challenge(db, challenge_in)

    for boost_reward in challenge_in.boosts_reward:
        boost_reward.challenge_id = db_challenge.challenge_id
        boost_reward_crud.create_boost_reward(db, boost_reward)

    active_challenge_in = ActiveChallengeCreate(
        challenge_id = db_challenge.challenge_id,
        challenge_start_date = event_in.challenge_start_date,
        challenge_end_date = event_in.challenge_end_date
    )

    db_active_challenge = active_challenges_crud.create_active_challenge(db, active_challenge_in)
    return build_active_challenge_response(db, db_active_challenge)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        current_user: models.Users = Depends(require_admin),
        db: Session = Depends(get_db)
    ):
    """
    Elimina completamente un usuario de la base de datos.
    """
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden realizar esta acción."
        )
    
    db_user = user_crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return

@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
        team_id: int,
        current_user: models.Users = Depends(require_admin),
        db: Session = Depends(get_db)
    ):
    """
    Remueve a los usuarios de un equipo y luego lo elimina.
    """
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden realizar esta acción."
        )
    
    db_team = team_crud.admin_delete(db, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return