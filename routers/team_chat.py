from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.team_chat_schema import MessageCreate, MessageResponse
from utils.auth import get_current_user
from crud import team_chat_crud, user_crud
from typing import List
from model import models
from enums.enum_types import TeamRole
from utils.response_builder import build_chat_message_data

router = APIRouter(
    prefix="/teamChat",
    tags=["Chat de Equipo"]
)

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(
        message_in: MessageCreate,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Registra un mensaje nuevo."""
    if current_user.user_team is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no pertenece a un equipo."
        )
    
    db_message = team_chat_crud.create_message(db, current_user, message_in, False)
    return build_chat_message_data(db, db_message)

@router.get("/", response_model=List[MessageResponse])
def get_all_team_messages(
        current_user: models.Users = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    """Retorna la información de todos los mensajes de chat del equipo del usuario."""
    if current_user.user_team is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no pertenece a un equipo."
        )

    messages = team_chat_crud.get_all_team_messages(db, current_user)

    return [
        build_chat_message_data(db, message)
        for message in messages
    ]

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
        message_id: int,
        current_user: models.Users = Depends(get_current_user),  
        db: Session = Depends(get_db)
    ):
    """
    Elimina mensajes del chat de equipo.
    El usuario autentificado unicamente puede eliminar sus propios mensajes.
    Usuarios de equipo del tipo moderador pueden eliminar mensajes de otros usuarios.
    """
    db_message = team_chat_crud.get_message_by_id(db, message_id)
    
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )

    if(db_message.is_from_system):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No es posible eliminar un mensaje del sistema"
        )
    
    if (current_user.user_id != db_message.user_id and 
        current_user.team_role < TeamRole.leader):

        if(current_user.team_role < TeamRole.moderator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el lider y los moderadores de equipo pueden eliminar mensajes de otros usuarios."
            )

        message_user = user_crud.get_user_by_id(db_message.user_id)
        if(message_user.team_role == TeamRole.moderator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el lider del equipo puede eliminar mensajes de otros moderadores."
            )
        
    team_chat_crud.delete_message(db, message_id)
