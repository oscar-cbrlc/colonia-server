from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from crud import user_crud
from utils.security import verify_access_token
from model import models

security = HTTPBearer()

# Obtener id de usuario autenticado
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
    ) -> models.Users:

    # Token enviado por el cliente
    token = credentials.credentials

    # Verificar JWT
    payload = verify_access_token(token)

    # Obtener el user_id almacenado en el token
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, usuario no encontrado"
        )

    # Buscar usuario en PostgreSQL
    db_user = user_crud.get_user_by_id(
        db,
        user_id=int(user_id)
    )

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    return db_user