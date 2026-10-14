from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.avatar_item_schema import ItemCreate, ItemUpdate

def get_all_items(db: Session):
    """Retorna el catalogo de items de avatar ordenado por identificador."""
    return (
        db.query(models.AvatarItem)
        .order_by(models.AvatarItem.avatar_item_id)
        .all()
    )

def get_item_by_id(db: Session, avatar_item_id: int):
    """Busca un item de avatar por su identificador."""
    return (
        db.query(models.AvatarItem)
        .filter(models.AvatarItem.avatar_item_id == avatar_item_id)
        .first()
    )

def create_avatar_item(db: Session, avatar_item_in: ItemCreate):
    """Crea un item de avatar en el catalogo."""
    db_item = models.AvatarItem(**avatar_item_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_boost(db: Session, db_item: models.AvatarItem, item_in: ItemUpdate):
    """Actualiza solamente los campos recibidos de un potenciador."""
    update_data = item_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item

def delete_boost(db: Session, avatar_item_id: int):
    """Elimina un item de avatar y deja que PostgreSQL aplique sus cascadas."""
    db.execute(delete(models.AvatarItem).where(models.AvatarItem.avatar_item_id == avatar_item_id))
    db.commit()