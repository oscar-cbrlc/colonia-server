from sqlalchemy.orm import Session
from model import models
from schema.notification_schema import NotificationCreate
from fastapi import HTTPException, status

def create_notification(db: Session, notification_in: NotificationCreate):
    """Crea una nueva notificación en la base de datos"""
    db_notification = models.Notification(
        user_id = notification_in.user_id,
        notification_type = notification_in.notification_type,
        notification_message = notification_in.notification_message
    )

    db.add(db_notification)
    db.flush()
    return db_notification

def get_notification_by_id(db: Session, notification_id: int):
    """Busca una notificación por su ID."""
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.notification_id == notification_id,
        )
        .first()
    )

def get_all_user_notifications(db: Session, user_id: int):
    """Busca todas las notificaciones para un usuario."""
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == user_id,
        )
        .all()
    )

def get_all_notificacions_by_type(db: Session, notification_type: int):
    """Busca todas las notificaciones de un mismo tipo."""
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.notification_type == notification_type,
        )
        .all()
    )

def delete_notification(db: Session, notification_id: int):
    """Elimina una notificación de la base de datos."""
    db_notification = get_notification_by_id(db, notification_id)

    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    db.delete(db_notification)
    db.commit()