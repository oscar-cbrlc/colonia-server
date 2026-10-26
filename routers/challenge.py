from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from schema.challenge_schema import ChallengeCreate, ChallengeUpdate, ChallengeResponse
from crud import user_crud, challenge_crud, active_challenges_crud, boost_reward_crud
from database import get_db
from model import models
from utils.auth import get_current_user
from utils.response_builder import build_challenge_response

router = APIRouter(
    prefix="/challenge",
    tags=["Desafíos de entrenamiento"]
)

def require_admin(current_user: models.Users = Depends(get_current_user),) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user

def get_existing_challenge(challenge_id: int, db: Session) -> models.Challenge:
    db_challenge = challenge_crud.get_challenge_by_id(db, challenge_id)
    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desafìo no encontrado",
        )
    return db_challenge

def get_active_challenge(active_challenge_id: int, db: Session) -> models.Challenge:
    db_active_challenge = active_challenges_crud.get_active_challenge_by_id(db, active_challenge_id)
    if db_active_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desafìo no se encuentra activo actualmente.",
        )
    return db_active_challenge

@router.post("/", response_model = ChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge(
    challenge_in: ChallengeCreate, 
    _: models.Users = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Crea un nuevo desafío. Requiere permisos de administrador"""

    db_challenge = challenge_crud.create_challenge(db, challenge_in)
    for boost_reward in challenge_in.boosts_reward:
        boost_reward.challenge_id = db_challenge.challenge_id
        boost_reward_crud.create_boost_reward(db, boost_reward)
    
    db.commit()
    return build_challenge_response(db, db_challenge)

@router.get("/", response_model = list[ChallengeResponse])
def list_challenges(db: Session = Depends(get_db)):
    """Retorna la lista de desafiós almacenados."""
    results = challenge_crud.get_all_challenges(db)
    return[
        build_challenge_response(db, db_challenge)
        for db_challenge in results
    ]

@router.get("/{challenge_id}", response_model = ChallengeResponse)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Retorna un desafío por su identificador."""
    db_challenge = get_existing_challenge(challenge_id, db)
    return build_challenge_response(db, db_challenge)

@router.patch("/{challenge_id}", response_model = ChallengeResponse)
def update_challenge(
        challenge_id: int,
        challenge_in: ChallengeUpdate,
        _: models.Users = Depends(require_admin),
        db: Session = Depends(get_db)
    ):
    """Actualiza un desafío. Requiere permisos de administrador."""
    db_challenge = get_existing_challenge(challenge_id, db)
    result = challenge_crud.update_challenge(db, db_challenge, challenge_in)
    return build_challenge_response(db, result)

@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
        challenge_id: int,
        _: models.Users = Depends(require_admin),
        db: Session = Depends(get_db)
    ):
    """Elimina un desafío. Requiere permisos de administrador."""
    db_challenge = get_existing_challenge(challenge_id, db)
    challenge_crud.delete_challenge(db, db_challenge.challenge_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
