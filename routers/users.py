from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schema.user_schema import UserCreate, UserLogin, UserLoginResponse, UserResponse, UserUpdate
from crud import user_crud
from utils.security import create_access_token

# la ruta  raiz de cada users endpoint seria http://<api>/users
router = APIRouter(
    prefix="/users",
    tags=["Autenticación y Perfil de Usuario"]
)

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


@router.get("/user", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna la información de un usuario en específico, dado su id.
    """
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_user

@router.get("/user-bemail", response_model=UserResponse)
def get_user(email: str, db: Session = Depends(get_db)):
    """
    Retorna la información de un usuario en específico, dado su email.
    """
    db_user = user_crud.get_user_by_email(db, email=email);
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_user

@router.patch("/user", response_model=UserResponse)
def update_user(user_update: UserUpdate, user_id: int, db: Session = Depends(get_db)):
    """
    Actualiza datos del perfil de usuario.
    """
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user_crud.update_user(db=db, db_user=db_user, user_update=user_update)

@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Elimina completamente un usuario de la base de datos.
    """
    success = user_crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return
