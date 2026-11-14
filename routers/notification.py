from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.notification_schema import NotificationCreate, NotificationResponse
from utils.auth import get_current_user
from crud import notification_crud, team_crud
from typing import List
from model import models
from enums.enum_types import Notification_Type

router = APIRouter(
    prefix="/notification",
    tags=["Notificaciones"]
)

def create_user_notification(db: Session, team_id: int, notification_type: int, user_id: int):
    """Crea una notificación para un usuario de acuerdo a la operación de solicitud realizada"""
    db_team = team_crud.get_team_by_id(db, team_id)

    notification_in = NotificationCreate(
        notification_message = db_team.team_name,
        notification_type = notification_type,
        user_id = user_id
    )
    notification_crud.create_notification(db, notification_in)

def create_global_notification(db: Session, event_name: str, notification_type: int):
    """Crea una notificación global para todos los usuarios"""
    notification_in = NotificationCreate(
        notification_message = event_name,
        notification_type = notification_type,
        user_id = None
    )
    notification_crud.create_notification(db, notification_in)

@router.get("/mine", response_model=List[NotificationResponse])
def get_all_my_notifications(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Retorna la información de todos las notificaciones del usuario."""
    from utils.response_builder import build_notification_response

    user_notifications = notification_crud.get_all_user_notifications(db, current_user.user_id)
    global_notifications = notification_crud.get_all_notificacions_by_type(db, Notification_Type.global_notification)
    notifications = user_notifications + global_notifications

    return [
        build_notification_response(db, notification)
        for notification in notifications
    ]

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
        notification_id: int,
        current_user: models.Users = Depends(get_current_user),  
        db: Session = Depends(get_db)
    ):
    """
    Elimina notificaciones.
    El usuario autentificado unicamente puede eliminar sus propias notificaciones.
    """
    db_notification = notification_crud.get_notification_by_id(db, notification_id)
    
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )

    if(db_notification.user_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No es posible eliminar notificaciones de otros usuarios"
        )
        
    notification_crud.delete_notification(db, notification_id)