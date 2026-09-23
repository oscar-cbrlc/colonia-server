from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.boost_inventory_schema import BoostInventoryUpdate

def get_boost_inventory(db: Session,  user_id: int):
    """Busca el inventario de potenciadores de un usuario dado su id."""
    return (
        db.query(models.BoostInventory, models.Boost)
        .join(
            models.Boost,
            models.BoostInventory.boost_id == models.Boost.boost_id
        )
        .filter(models.BoostInventory.user_id == user_id)
        .all()
    )

def get_user_boost(db: Session, user_id: int, boost_id: int):
    """Busca un potenciador en inventario por identificador de usuario y potenciador."""
    return (
        db.query(models.BoostInventory)
        .filter(models.BoostInventory.user_id == user_id and models.BoostInventory.boost_id == boost_id)
        .first()
    )

def add_boost_to_inventory(db: Session, current_user: models.Users, boost_id: int):
    """Agrega un potenciador por identificador al inventario del usuario autentificado."""
    db_inventory = get_user_boost(db, current_user.user_id, boost_id)
    db_inventory.boost_amount += 1

    db.commit()
    db.refresh(db_inventory)

def remove_boost_from_inventory(db: Session, current_user: models.Users, boost_id: int):
    """Remueve un potenciador por identificador del inventario del usuario autentificado."""
    db_inventory = get_user_boost(db, current_user.user_id, boost_id)
    if(db_inventory.boost_amount > 0):
        db_inventory.boost_amount -= 1
        return True
    else:
        return False 

def update_user_boost_inventory(db: Session, db_boost_inv: models.BoostInventory, boost_in: BoostInventoryUpdate):
    """Actualiza las cantidad de un potenciador en inventario."""
    update_data = boost_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_boost_inv, field, value)

    db.commit()
    db.refresh(db_boost_inv)
    return db_boost_inv