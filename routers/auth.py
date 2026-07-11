from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserCreate, UserLogin, UserLoginResponse, UserResponse, UserUpdate
from crud import user_crud
from utils.security import create_access_token
from typing import List, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/auth",
    tags=["Registro y Autenticación"]
)

security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario, validando que el correo no esté ya registrado
    """
    db_user = user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico ya registrado"
        )
    return user_crud.create_user(db=db, user_in=user_in)


@router.post("/login", response_model=UserLoginResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Valida el correo y contrasena de un usuario.
    """
    db_user = user_crud.authenticate_user(
        db=db,
        email=user_in.email,
        password=user_in.password
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos"
        )
    access_token = create_access_token(
        data={
            "sub": str(db_user.user_id),
            "email": db_user.email
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/firebase", response_model=dict)
async def auth_with_firebase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    id_token = credentials.credentials
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falta el token de ID de Firebase."
        )

    #if id_token == "mock_test_user":
        #return {
            #"email": "testplayer@mail.com",
            #"provider_uid": "mock-uid-12345"
        #}
        
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get("email")
        provider_uid = decoded_token.get("uid")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not valid token"
            )

        db_user = db.query(Users).filter(Users.email == email).first()

        if not db_user:
            return {
                "is_new_user": True,
                "email": email,
                "provider_uid": provider_uid,
                "access_token": None,
                "user": None
            }

        access_token = create_access_token(
            data={
                "sub": str(db_user.user_id),
                "email": db_user.email
            }
        )
        
        return {
            "is_new_user": False,
            "email": email,
            "provider_uid": provider_uid,
            "access_token": access_token,
            "user": UserResponse.from_orm(db_user)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )

