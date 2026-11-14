from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserLoginResponse
from schema.user_session_schema import UserSessionCreate, UserTokensResponse
from crud import user_crud
from crud.user_session_crud import create_login_session, rotate_refresh_token, revoke_user_session
from typing import List, Optional
from utils.response_builder import get_user_response
from model import models
from utils.firebase_auth import get_firebase_identity

router = APIRouter(
    prefix="/session",
    tags=["Autenticación de Usuario"]
)

@router.post("/login", response_model = UserLoginResponse)
def login(
    firebase_identity: dict[str, str] = Depends(get_firebase_identity),
    db: Session = Depends(get_db),
):
    """Exchanges a verified Firebase ID token for API session tokens."""
    db_user, _ = user_crud.resolve_firebase_user(
        db,
        email=firebase_identity["email"],
        firebase_uid=firebase_identity["uid"],
    )
    tokens = create_login_session(db, db_user.user_id)
    user_response = get_user_response(db, db_user)
    return {**tokens, "user": user_response}

@router.post("/refresh", response_model = UserTokensResponse)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    return rotate_refresh_token(db, refresh_token)

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    """Cierra la sesión del usuario."""
    revoke_user_session(db, refresh_token)