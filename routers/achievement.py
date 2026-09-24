from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from crud import user_crud, achievement_crud, obtained_achievements_crud
from schema.achievement_schema import AchievementCreate, AchievementUpdate, AchievementResponse
from schema.obtained_achievements_schema import AchievementDetails
from database import get_db
from model import models
from utils.auth import get_current_user
from utils.response_builder import build_achievement_response, get_achievement_details, get_obtained_achievements_data, get_locked_achievements_data

router = APIRouter(
    prefix="/achievement",
    tags=["Logros del jugador"]
)

def require_admin(current_user: models.Users = Depends(get_current_user),) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user

def get_existing_achievement(achievement_id: int, db: Session) -> models.Boost:
    db_achievement = achievement_crud.get_boost_by_id(db, achievement_id)
    if db_achievement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logro no encontrado",
        )
    return db_achievement

@router.post("/", response_model = AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(achievement_in: AchievementCreate, _: models.Users = Depends(require_admin), db: Session = Depends(get_db),):
    """Crea un nuevo logro. Requiere permisos de administrador"""

    db_achievement = achievement_crud.create_achievement(db, achievement_in)
    return build_achievement_response(db_achievement)

@router.get("/", response_model = list[AchievementResponse])
def list_achievements(db: Session = Depends(get_db),):
    """Retorna la lista de logros disponibles."""
    results = achievement_crud.get_all_achievements(db)
    return[
        build_achievement_response(db_achievement)
        for db_achievement in results
    ]

@router.get("/{achievement_id}", response_model = AchievementResponse)
def get_achievement(achievement_id: int, db: Session = Depends(get_db)):
    """Retorna un logro por su identificador."""
    db_achievement = get_existing_achievement(achievement_id, db)
    return build_achievement_response(db_achievement)

@router.patch("/{achievement_id}", response_model=AchievementResponse)
def update_achievement(
        achievement_id: int,
        achievement_in: AchievementUpdate,
        _: models.Users = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
    """Actualiza un logro. Requiere permisos de administrador."""
    db_achievement = get_existing_achievement(achievement_id, db)
    result = achievement_crud.update_achievement(db, db_achievement, achievement_in)
    return build_achievement_response(result)

@router.delete("/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(
        achievement_id: int,
        _: models.Users = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
    """Elimina un logro. Requiere permisos de administrador."""
    db_achievement = get_existing_achievement(achievement_id, db)
    achievement_crud.delete_achievement(db, db_achievement.boost_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/users/me/obtained", response_model=list[AchievementDetails])
def get_my_achievements(
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Retorna la lista de logros del usuario autentificado."""
    obtained = get_obtained_achievements_data(db, current_user.user_id)
    locked = get_locked_achievements_data(db, current_user.user_id)

    return  obtained + locked

