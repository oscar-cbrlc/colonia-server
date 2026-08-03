from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from crud import boost_crud, user_crud
from database import get_db
from model import models
from schema.boost_schema import BoostCreate, BoostResponse, BoostUpdate
from utils.auth import get_current_user


router = APIRouter(
    prefix="/boosts",
    tags=["Potenciadores"],
)


def require_admin(
    current_user: models.Users = Depends(get_current_user),
) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user


def get_existing_boost(boost_id: int, db: Session) -> models.Boost:
    db_boost = boost_crud.get_boost_by_id(db, boost_id)
    if db_boost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potenciador no encontrado",
        )
    return db_boost


@router.get("", response_model=list[BoostResponse])
def list_boosts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retorna el catalogo de potenciadores."""
    return boost_crud.get_boosts(db, skip=skip, limit=limit)


@router.get("/{boost_id}", response_model=BoostResponse)
def get_boost(boost_id: int, db: Session = Depends(get_db)):
    """Retorna un potenciador por su identificador."""
    return get_existing_boost(boost_id, db)


@router.post("", response_model=BoostResponse, status_code=status.HTTP_201_CREATED)
def create_boost(
    boost_in: BoostCreate,
    _: models.Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Crea un potenciador. Requiere permisos de administrador."""
    return boost_crud.create_boost(db, boost_in)


@router.patch("/{boost_id}", response_model=BoostResponse)
def update_boost(
    boost_id: int,
    boost_in: BoostUpdate,
    _: models.Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Actualiza un potenciador. Requiere permisos de administrador."""
    db_boost = get_existing_boost(boost_id, db)
    return boost_crud.update_boost(db, db_boost, boost_in)


@router.delete("/{boost_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_boost(
    boost_id: int,
    _: models.Users = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Elimina un potenciador. Requiere permisos de administrador."""
    db_boost = get_existing_boost(boost_id, db)
    boost_crud.delete_boost(db, db_boost.boost_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
