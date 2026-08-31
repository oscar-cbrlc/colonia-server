from sqlalchemy.orm import Session
from model import models
from schema.team_chat_schema import MessageCreate
from fastapi import HTTPException, status

def create_message(db: Session, current_user: models.Users, message_in: MessageCreate, from_system:bool):
    """Crea un nuevo mensaje de chat en la base de datos"""

    db_message = models.TeamChat(
        team_id = current_user.user_team,
        chat_message = message_in.chat_message,
        is_from_system = from_system
    )

    if not from_system:
        db_message.user_id = current_user.user_id

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

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
