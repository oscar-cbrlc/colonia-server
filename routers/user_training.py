from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from model import models
from schema.user_training_schema import UserTrainingCreate, TrainingResult, UserTrainingResponse
from crud import user_training_crud
from typing import List
from uuid import UUID
from utils.auth import get_current_user
from utils.apply_training import apply_training_impact
from utils.response_builder import build_user_training_response

router = APIRouter(
    prefix="/userTraining",
    tags=["Entrenamientos de Usuario"]
)

@router.get("/mine", response_model=List[UserTrainingResponse])
def get_all_my_trainings(
    current_user: models.Users = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Retorna la información de todos los entrenamientos del usuario autentificado."""
    results = user_training_crud.get_user_trainings(db, current_user.user_id)
    return[
        build_user_training_response(db, db_training)
        for db_training in results
    ]
    
@router.get("/users/{user_id}/userTraining{training_uuid}", response_model=UserTrainingResponse)
def get_training(user_id: int, training_uuid: UUID, db: Session = Depends(get_db)):
    """Retorna la información de un entrenamiento, dado el id del usuario y el uuid del entrenamiento."""
    db_training = user_training_crud.get_training_by_id(db, user_id, training_uuid)
    if not db_training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrenamiento no encontrado"
        )
    build_user_training_response(db, db_training)

@router.post("/",response_model=TrainingResult)
def process_training(
        impact_in: UserTrainingCreate,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Procesa y valida un entrenamiento del usuario autentificado."""
    return apply_training_impact(db, current_user, impact_in)



