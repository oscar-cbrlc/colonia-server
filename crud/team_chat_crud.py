from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from model import models
from enums.enum_types import Message_Type
from utils.message_encryption_system import encrypt_message

def create_user_message(db: Session, current_user: models.Users, message_in: str):
    """Crea un nuevo mensaje de chat en la base de datos por parte del usuario"""
    
    encrypted_msg = encrypt_message(
        message = message_in,
        team_id = current_user.user_team,
        user_id = current_user.user_id,
        triggered_by = None,
        message_type = Message_Type.user_message
        )

    db_message = models.TeamChat(
        user_id = current_user.user_id,
        team_id = current_user.user_team,
        chat_message = encrypted_msg
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def create_system_message(
    db: Session, 
    user_id: int,
    team_id: int,
    user_trigger:int, 
    message_type: int
):
    """Crea un nuevo mensaje de chat en la base de datos por parte del sistema"""

    encrypted_msg = encrypt_message(
        message = Message_Type(message_type).name,
        team_id = team_id,
        user_id = user_id,
        triggered_by= user_trigger,
        message_type = message_type
    )

    db_message = models.TeamChat(
        user_id = user_id,
        team_id = team_id,
        chat_message = encrypted_msg,
        message_type = message_type,
        triggered_by = user_trigger
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
