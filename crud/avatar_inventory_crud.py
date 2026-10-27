from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from model import models
from schema.avatar_inventory_schema import AvatarInventoryCreate
from datetime import datetime, timezone

def get_avatar_inventory(db: Session,  user_id: int):
    """Busca el inventario de avatar de un usuario dado su id."""
    return (
        db.query(models.AvatarInventory, models.AvatarItem)
        .join(
            models.AvatarItem,
            models.AvatarInventory.avatar_item_id == models.AvatarItem.avatar_item_id
        )
        .filter(models.AvatarInventory.user_id == user_id)
        .all()
    )

def add_item_to_inventory(db: Session, current_user: models.Users, avatar_item_id: int):
    """Otorga un objeto de avatar por identificador al usuario autentificado."""
    avatar_inventory_in = AvatarInventoryCreate(
        avatar_item_id = avatar_item_id,
        user_id = current_user.user_id,
        item_acquisition_date = datetime.now(timezone.utc)
    )
    db_avatar_inventory = models.AvatarInventory(**avatar_inventory_in.model_dump())
    db.add(db_avatar_inventory)
    db.flush()