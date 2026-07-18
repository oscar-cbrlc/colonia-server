from sqlalchemy.orm import Session
from model import models
from schema.user_schema import UserCreate, UserUpdate
from utils.security import hash_password, verify_password
from fastapi import HTTPException, status
from enums.enum_types import TeamRole, UserType

def get_all_users(db: Session, limit=100):
    """Retorna todos los usuarios con un límite."""
    return db.query(models.Users).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(models.Users).filter(models.Users.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Busca un usuario por su ID único."""
    return db.query(models.Users).filter(models.Users.user_id == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    """Valida las credenciales de un usuario por correo y contrasena."""
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user

def create_user(db: Session, user_in: UserCreate):
    """Crea un nuevo usuario en la base de datos aplicando hash a su contraseña."""
    hashed_pwd = hash_password(user_in.password)
    
    db_user = models.Users(
        email=user_in.email,
        user_name=user_in.user_name,
        password_hash=hashed_pwd,
        user_type = UserType.player
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
        update_data.pop("password")
    
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

def get_all_team_users(db: Session, team_id: int, limit=25):
    """Retorna todos los usuarios pertenecientes a un equipo."""
    return (
        db.query(models.Users)
        .filter(models.Users.user_team == team_id)
        .order_by(models.Users.team_role.desc(),
                  models.Users.user_name)
        .limit(limit)
        .all()
    )

def count_team_members(db: Session, team_id: int):
    return (
        db.query(models.Users)
        .filter(models.Users.user_team == team_id)
        .count()
    )

def assign_user_to_team(db_user: models.Users, team_id: int, team_role: TeamRole):
    """
    Asigna un usuario al equipo seleccionado.
    """
    db_user.user_team = team_id
    db_user.team_role = team_role

def user_join_team(db: Session, db_user: models.Users, team_id: int):
    assign_user_to_team(db_user, team_id, TeamRole.member)

    db.commit()
    db.refresh(db_user)
    return db_user

def is_leader(db_user: models.Users):
    role_id = db_user.team_role

    if(role_id == TeamRole.leader):
        return True
    else:
        return False
    
def is_moderator(db_user: models.Users):
    role_id = db_user.team_role

    if(role_id > TeamRole.member):
        return True
    else:
        return False
    
def is_admin(db_user: models.Users):
    user_type = db_user.user_type

    if(user_type == UserType.admin):
        return True
    else:
        return False

def update_team_role(db_user: models.Users, new_role: TeamRole):
    """
    Actualiza el rol de un usuario dentro de un equipo.
    """
    db_user.team_role = new_role
    return db_user

def transfer_team_leadership(leader: models.Users, user: models.Users):
    """
    Transfiere rol de liderazgo de un equipo a otro usuario.
    """
    update_team_role(leader, TeamRole.moderator)
    return update_team_role(user, TeamRole.leader)

def change_team_role(db: Session,  leader: models.Users, user_id: int ,new_role: TeamRole):
    """
    Cambia el rol de un usuario dentro de un equipo por parte del lider.
    """
    if not is_leader(leader):
        raise HTTPException(
            status_code=403,
            detail="Solo el lider pueden realizar esta acción"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )
    
    leader_team = leader.user_team
    user_team = user.user_team
    if(leader_team != user_team):
        raise HTTPException(
            status_code=403,
            detail="Usuario no pertenece a este equipo."
        )
    
    if(leader.user_id == user.user_id):
        raise HTTPException(
            status_code=403,
            detail="Lider no puede cambiar su rol sin promover a alguien más."
        )
    
    try:
        TeamRole(new_role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Rol no válido."
        )
    
    if(new_role == TeamRole.leader):
        db_user = transfer_team_leadership(leader, user)
    else:
        db_user = update_team_role(user, new_role)

    db.commit()
    db.refresh(db_user)
    return db_user
    
def remove_user_from_team(db_user: models.Users):
    """
    Remueve un usuario del equipo seleccionado.
    """
    db_user.user_team = None
    db_user.team_role = None
    return db_user

def exit_team(db: Session, db_user: models.Users):
    """
    Remueve al usuario del equipo al que pertenece.
    """
    remove_user_from_team(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def kick_from_team(db: Session, db_user: models.Users, user_id: int):
    """
    Remueve a un usuario de su equipo por parte de moderación.
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )
    remove_user_from_team(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

    
