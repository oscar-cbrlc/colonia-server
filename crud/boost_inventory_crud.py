from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.boost_inventory_schema import BoostInventoryUpdate

def get_user_boost_inventory(db: Session, user_id: int):
    """Busca un inventario de potenciadores por identificador de usuario."""
    return (
        db.query(models.BoostInventory)
        .filter(models.BoostInventory.user_id == user_id)
    )

def get_user_boost(db: Session, user_id: int, boost_id: int):
    """Busca un potenciador en inventario por identificador de usuario y potenciador."""
    return (
        db.query(models.BoostInventory)
        .filter(models.BoostInventory.user_id == user_id and models.BoostInventory.boost_id == boost_id)
        .first()
    )

def update_user_boost_inventory(db: Session, db_boost_inv: models.BoostInventory, boost_in: BoostInventoryUpdate):
    """Actualiza las cantidad de un potenciador en inventario."""
    update_data = boost_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_boost_inv, field, value)

    db.commit()
    db.refresh(db_boost_inv)
    return db_boost_inv