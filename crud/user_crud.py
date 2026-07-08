from sqlalchemy.orm import Session
from model import models
from schema.user_schema import UserCreate, UserUpdate
from utils.security import hash_password

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(models.Users).filter(models.Users.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Busca un usuario por su ID único."""
    return db.query(models.Users).filter(models.Users.user_id == user_id).first()

def create_user(db: Session, user_in: UserCreate):
    """Crea un nuevo usuario en la base de datos aplicando hash a su contraseña."""
    hashed_pwd = hash_password(user_in.password)
    
    db_user = models.Users(
        email=user_in.email,
        user_name=user_in.user_name,
        user_type=user_in.user_type,
        password_hash=hashed_pwd,
        total_distance=0.0,
        total_time=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.Users, user_update: UserUpdate):
    """Actualiza la información del perfil del usuario."""
    # convierte el Schema UserUpdate en diccionario excluyendo lo que no se envió
    update_data = user_update.model_dump(exclude_unset=True)
    
    # si el usuario quiere actualizar su contraseña, se aplica Hash primero
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hash_password(update_data["password"])
    
    # se actualizan cada uno de los cambios
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina permanentemente a un usuario de la base de datos.
    Retorna True si la eliminación fue exitosa, o False si el usuario no existía.
    """
    db_user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not db_user:
        return False
        
    db.delete(db_user)
    db.commit()
    return True