from sqlalchemy.orm import Session
from sqlalchemy import insert, delete
from model import models
from schema.item_bundle_schema import ItemBundleCreate

def get_items_in_bundle(db: Session,  bundle_id: int):
    """Busca la lista de items pertenecientes al bundle con el identificador proporcionado."""
    return (
        db.query(models.AvatarItem)
        .join(
            models.t_item_bundle,
            models.t_item_bundle.c.avatar_item_id == models.AvatarItem.avatar_item_id
       )
        .filter(models.t_item_bundle.c.bundle_id == bundle_id)
        .all()
    )

def add_item_to_bundle(db: Session, bundle_id: int, avatar_item_id: int):
    """Agrega un objeto de avatar por identificador al paquete del identificador proporcionado."""
    item_bundle_in = ItemBundleCreate(
        avatar_item_id = avatar_item_id,
        bundle_id = bundle_id,
    )

    query = insert(models.t_item_bundle).values(
        **item_bundle_in.model_dump()
    )
    db.execute(query)
    db.flush()