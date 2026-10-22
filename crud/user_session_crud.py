from sqlalchemy.orm import Session
from model import models
from schema.user_session_schema import UserSessionCreate
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from utils.security import create_access_token, create_refresh_token, verify_refresh_token

def create_user_session(db: Session, session_in: UserSessionCreate):
    """Crea una nueva sesión de usuario en la base de datos."""
    db_user_session = models.UserSession(
        user_id = session_in.user_id,
        jti = session_in.jti,
        expires_at = session_in.expires_at
    )

    db.add(db_user_session)
    db.flush()

def get_user_session_by_jti(db: Session, jti: str, user_id: int | None = None):
    """Obtiene una sesión de usuario por su jti."""
    query  = (
        db.query(models.UserSession)
        .filter(models.UserSession.jti == jti)
    )

    if user_id is not None:
        query = query.filter(
            models.UserSession.user_id == user_id
        )

    db_session = query.first()

    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no encontrada."
        )
    return db_session

def rotate_refresh_token(db: Session, refresh_token: str) -> dict:
    """Permite la rotación de refresh tokens."""

    payload = verify_refresh_token(refresh_token)
    user_id = int(payload["sub"])
    old_jti = payload["jti"]

    # Buscar la sesión y bloquearla durante la transacción
    session = (
        db.query(models.UserSession)
        .filter(
            models.UserSession.user_id == user_id,
            models.UserSession.jti == old_jti
        )
        .with_for_update()
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no encontrada."
        )

    now = datetime.now(timezone.utc)

    # Detectar reutilización de un refresh token revocado
    if session.revoked_at is not None:

        # Invalidar las sesiones activas del usuario
        (
            db.query(models.UserSession)
            .filter(
                models.UserSession.user_id == user_id,
                models.UserSession.revoked_at.is_(None)
            )
            .update(
                {models.UserSession.revoked_at: now},
                synchronize_session=False
            )
        )
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reutilizado. Sesión invalidada."
        )

    # Verificar expiración registrada en la base de datos
    if session.expires_at <= now:
        session.revoked_at = now
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada."
        )

    # Revocar el refresh token anterior
    session.revoked_at = now

    # Crear los nuevos tokens
    token_data = {
        "sub": str(user_id)
    }
    new_access_token = create_access_token(token_data)
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(token_data)

    new_session = UserSessionCreate(
        user_id = user_id,
        jti = new_jti,
        expires_at = new_expires_at
    )
    create_user_session(db, new_session)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

def revoke_user_session(db: Session, refresh_token: str):
    """Revoca la validez de una sesión de usuario."""
    payload = verify_refresh_token(refresh_token)
    user_id = int(payload["sub"])
    jti = payload["jti"]

    db_session = (
        db.query(models.UserSession)
        .filter(
            models.UserSession.user_id == user_id,
            models.UserSession.jti == jti,
            models.UserSession.revoked_at.is_(None)
        )
        .first()
    )

    if db_session:
        db_session.revoked_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "message": "Sesión cerrada correctamente."
    }