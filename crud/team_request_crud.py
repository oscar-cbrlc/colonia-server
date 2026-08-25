from sqlalchemy.orm import Session
from model import models
from schema.team_request_schema import RequestCreate
from crud import user_crud
from fastapi import HTTPException, status

def get_request_by_id(db: Session, user_id: int, team_id: int):
    """Busca una solicitudes por su ID."""
    return (
        db.query(models.TeamRequest)
        .filter(
            models.TeamRequest.user_id == user_id,
            models.TeamRequest.team_id == team_id
        )
        .first()
    )

def get_all_my_request(db: Session, current_user: models.Users):
    """Busca todas las solicitudes del usuario."""
    return (
        db.query(models.TeamRequest, models.Team)
        .join(
            models.Team,
            models.TeamRequest.team_id == models.Team.team_id
        )
        .filter(
            models.TeamRequest.user_id == current_user.user_id
        )
        .order_by(
            models.TeamRequest.request_timestamp.desc()
        )
        .all()
    )

def get_all_request_for_team(db: Session, current_user: models.Users):
    """Retorna todas las solicitudes del equipo del usuario."""
    return (
        db.query(models.TeamRequest, models.Users)
        .join(
            models.Users,
            models.TeamRequest.user_id == models.Users.user_id
        )
        .filter(
            models.TeamRequest.team_id == current_user.user_team
        )
        .order_by(
            models.TeamRequest.request_timestamp.desc()
        )
        .all()
    )

def create_request(db: Session, current_user: models.Users, request_in: RequestCreate):
    """Crea una nueva solicitud en la base de datos"""

    db_request = models.TeamRequest(
        user_id = current_user.user_id,
        team_id = request_in.team_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return db_request

def delete_request(db: Session, user_id: int, team_id: int):
    """
    Elimina una solicitud de la base de datos.
    """
    db_request = get_request_by_id(db, user_id, team_id)

    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
        
    db.delete(db_request)
    db.commit()

def delete_all_requests_by_user(db: Session, user_id: int) -> int:
    """
    Elimina todas las solicitudes de un usuario.
    """

    user_requests = (
        db.query(models.TeamRequest)
        .filter(
            models.TeamRequest.user_id == user_id
        )
        .all()
    )

    for request in user_requests:
        delete_request(db, user_id, request.team_id)
    
    return True