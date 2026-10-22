import bcrypt
import jwt
import secrets
import json
from datetime import datetime, timedelta, timezone
from config import settings
from fastapi import HTTPException, status

def hash_password(password: str) -> str:
    """Encripta la contraseña en un hash"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara contraseña sin encriptar con un hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

ALGORITHM = "HS256"
SECRET_KEY = settings.jwt_secret or settings.api_key

def create_token(
        data: dict,
        expires_delta: timedelta,
        token_type: str,
        jti: str | None = None
    ) -> tuple[str, str]:
    """Genera un JWT firmado con HS256."""

    now = datetime.now(timezone.utc)
    token_jti = jti or secrets.token_urlsafe(32)

    payload = data.copy()
    payload.update({
        "iat": now,
        "exp": now + expires_delta,
        "jti": token_jti,
        "type": token_type
    })

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm = ALGORITHM
    )
    return token, token_jti

def create_access_token(data: dict) -> str:
    """Crea un Access Token."""
    token, _ =  create_token(
        data = data,
        expires_delta = timedelta(
            minutes = settings.access_token_expires_minutes
        ),
        token_type="access"
    )
    return token

def create_refresh_token(data: dict) -> tuple[str, str, datetime]:
    """Crea un Refresh Token."""
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days = settings.refresh_token_expires_days)
    )
    token, jti = create_token(
        data = data,
        expires_delta = timedelta(days = settings.refresh_token_expires_days),
        token_type="refresh"
    )
    return token, jti, expires_at

def verify_token(token: str, expected_type: str) -> dict:
    """Verifica validez del JWT, retorna payload del mismo."""
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require": [
                    "exp",
                    "iat",
                    "sub",
                    "jti",
                    "type"
                ]
            }
        )

        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido."
            )
        return payload

    except HTTPException:
        raise

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )

def verify_access_token(token: str) -> dict:
    """Verifica validez de un Access Token."""
    return verify_token(token,expected_type="access")

def verify_refresh_token(token: str) -> dict:
    """Verifica validez de un Refresh Token."""
    return verify_token(token,expected_type="refresh")