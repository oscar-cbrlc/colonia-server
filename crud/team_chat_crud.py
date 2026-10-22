from sqlalchemy.orm import Session
from model import models
from schema.team_chat_schema import MessageCreate
from fastapi import HTTPException, status
from enums.enum_types import Message_Type

def create_user_message(db: Session, current_user: models.Users, message_in: MessageCreate):
    """Crea un nuevo mensaje de chat en la base de datos por parte del usuario"""
    db_message = models.TeamChat(
        user_id = current_user.user_id,
        team_id = current_user.user_team,
        chat_message = message_in.chat_message
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message

def create_system_message(db: Session, current_user: models.Users, message_type: int):
    """Crea un nuevo mensaje de chat en la base de datos por parte del sistema"""
    db_message = models.TeamChat(
        user_id = current_user.user_id,
        team_id = current_user.user_team,
        chat_message = Message_Type(message_type).name,
        message_type = message_type
    )
    db.add(db_message)
    db.flush()
    return db_message

def get_message_by_id(db: Session, message_id: int):
    """Busca un mensaje por su ID."""
    return (
        db.query(models.TeamChat)
        .filter(
            models.TeamChat.message_id == message_id,
        )
        .first()
    )

def get_all_team_messages(db: Session, current_user: models.Users):
    """Obtiene todos los mensajes del equipo al que pertenece el usuario."""
    return (
        db.query(models.TeamChat)
        .filter(
            models.TeamChat.team_id == current_user.user_team,
        )
        .order_by(
            models.TeamChat.message_date.desc()
        )
        .all()
    )

def delete_message(db: Session, message_id: int):
    """Elimina un mensaje de chat de la base de datos."""
    db_message = get_message_by_id(db, message_id)

    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
        
    db.delete(db_message)
    db.commit()
