from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from schema.active_challenges_schema import ActiveChallengeCreate, ActiveChallengeUpdate, ActiveChallengeResponse
from schema.started_challenges_schema import StartedChallengeResponse
from crud import user_crud, active_challenges_crud
from database import get_db
from model import models
from utils.auth import get_current_user
from utils.response_builder import(
    build_active_challenge_response,
    get_active_challenges_data, 
    get_started_challenges_data, 
    get_active_events_data,
    get_started_events_data
) 

router = APIRouter(
    prefix="/activeChallenge",
    tags=["Desafíos de entrenamiento activos"]
)

def require_admin(current_user: models.Users = Depends(get_current_user),) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user

def get_existing_active_challenge(active_challenge_id: int, db: Session) -> models.ActiveChallenges:
    db_active_challenge = active_challenges_crud.get_active_challenge_by_id(db, active_challenge_id)
    if db_active_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desafìo no encontrado",
        )
    return db_active_challenge

@router.get("/", response_model = list[ActiveChallengeResponse])
def list_active_challenges(db: Session = Depends(get_db)):
    """Retorna la lista de desafiós activos actualmente."""
    results = active_challenges_crud.get_all_active_challenges(db)
    return[
        build_active_challenge_response(db, db_active_challenge)
        for db_active_challenge in results
    ]

@router.get("/events", response_model = list[ActiveChallengeResponse])
def list_events(db: Session = Depends(get_db)):
    """Retorna la lista de desafíos de tipo evento programados."""
    results = active_challenges_crud.get_all_events(db)
    return[
        build_active_challenge_response(db, db_active_challenge)
        for db_active_challenge in results
    ]

@router.get("/{challenge_id}", response_model = ActiveChallengeResponse)
def get_active_challenge(active_challenge_id: int, db: Session = Depends(get_db)):
    """Retorna un desafío activo por medio de su identificador."""
    db_active_challenge = get_existing_active_challenge(active_challenge_id, db)
    return build_active_challenge_response(db, db_active_challenge)

@router.post("/{challenge_id}", response_model = ActiveChallengeResponse, status_code=status.HTTP_201_CREATED)
def activate_challenge(
    active_challenge_in: ActiveChallengeCreate, 
    _: models.Users = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    """Activa un desafío para los usuarios. Requiere permisos de administrador"""
    db_active_challenge = active_challenges_crud.create_active_challenge(db, active_challenge_in)
    return build_active_challenge_response(db, db_active_challenge)

@router.patch("/{challenge_id}", response_model = ActiveChallengeResponse)
def update_active_challenges(
        active_challenge_id: int,
        active_challenge_in: ActiveChallengeUpdate,
        _: models.Users = Depends(require_admin),
        db: Session = Depends(get_db)
    ):
    """Actualiza un desafío. Requiere permisos de administrador."""
    db_active_challenge = get_existing_active_challenge(active_challenge_id, db)
    result = active_challenges_crud.update_active_challenge(db, db_active_challenge, active_challenge_in)
    return build_active_challenge_response(db, result)

@router.get("/mine/progress", response_model = list[StartedChallengeResponse])
def list_challenge_progress(
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    """Retorna la lista de progreso del jugador en los desafiós activos actualmente."""
    started = get_started_challenges_data(db, current_user)
    active = get_active_challenges_data(db, current_user)

    return started + active

@router.get("/events/mine/progress", response_model = list[StartedChallengeResponse])
def list_event_progress(
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
    """Retorna la lista de progreso del jugador en los eventos activos actualmente."""
    started = get_started_events_data(db, current_user)
    active = get_active_events_data(db, current_user)

    return started + active