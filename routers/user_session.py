from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserLogin, UserLoginResponse
from schema.user_session_schema import UserSessionCreate, UserTokensResponse
from crud import user_crud
from crud.user_session_crud import create_user_session, rotate_refresh_token, revoke_user_session
from utils.security import create_access_token, create_refresh_token, verify_refresh_token
from typing import List, Optional
from utils.response_builder import get_user_response
from model import models

router = APIRouter(
    prefix="/session",
    tags=["Autenticación de Usuario"]
)

@router.post("/login", response_model = UserLoginResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Valida el correo y contrasena de un usuario."""
    db_user = user_crud.authenticate_user(
        db,
        user_in.email,
        user_in.password
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos"
        )
    
    token_data = {
        "sub": str(db_user.user_id)
    }
    access_token = create_access_token(token_data)
    refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(token_data)

    user_session = UserSessionCreate(
        user_id = db_user.user_id,
        jti = refresh_jti,
        expires_at = refresh_expires_at
    )
    create_user_session(db, user_session)
    db.commit()

    user_response = get_user_response(db, db_user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/refresh", response_model = UserTokensResponse)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    return rotate_refresh_token(db, refresh_token)

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    """Cierra la sesión del usuario."""
    revoke_user_session(db, refresh_token)