import base64
import bcrypt
import hashlib
import hmac
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

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def create_access_token(data: dict) -> str:
    """Crea un JWT firmado con HS256."""
    expires_delta = timedelta(minutes=settings.jwt_expires_minutes)
    expire = datetime.now(timezone.utc) + expires_delta

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = data.copy()
    payload["exp"] = int(expire.timestamp())

    encoded_header = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    secret = settings.jwt_secret or settings.api_key
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def _base64url_decode(data: str) -> bytes:
    '''Decodificador Base64URL para verificar Token''' 
    padding = "=" * (-len(data) % 4)

    return base64.urlsafe_b64decode(data + padding)

def verify_access_token(token: str) -> dict:
    '''Verifica validez del token, retorna payload del mismo'''
    try:
        
        #Verificar partes Header.Payload.Signature
        parts = token.split(".")

        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido, partes diferentes."
            )

        encoded_header, encoded_payload, encoded_signature = parts

        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

        secret = settings.jwt_secret or settings.api_key

        expected_signature = _base64url_encode(
            hmac.new(
                secret.encode("utf-8"),
                signing_input,
                hashlib.sha256
            ).digest()
        )

        # Comparación de token
        if not hmac.compare_digest(expected_signature, encoded_signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma del token inválida"
            )

        # Leer payload
        payload = json.loads(
            _base64url_decode(encoded_payload).decode("utf-8")
        )

        # Verificar expiración
        if payload.get("exp") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sin fecha de expiración"
            )
        
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        if payload["exp"] < current_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )

        return payload

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )