from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.store_offer_schema import StoreOfferCreate, StoreOfferUpdate

def get_all_offers(db: Session):
    """Retorna el catalogo de ofertas en la tienda ordenado por identificador."""
    return (
        db.query(models.StoreCatalog)
        .order_by(models.StoreCatalog.offer_id)
        .all()
    )

def get_offer_by_id(db: Session, offer_id: int):
    """Busca una oferta de la tienda por su identificador."""
    return (
        db.query(models.StoreCatalog)
        .filter(models.StoreCatalog.offer_id == offer_id)
        .first()
    )

def create_offer(db: Session, offer_in: StoreOfferCreate):
    """Crea una oferta de tienda en el catalogo."""
    db_offer = models.Bundle(**offer_in.model_dump())
    db.add(db_offer)
    db.flush()
    return db_offer

def update_offer(db: Session, db_offer: models.StoreCatalog, item_in: StoreOfferUpdate):
    """Actualiza solamente los campos recibidos de una oferta de tienda."""
    update_data = item_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_offer, field, value)

    db.commit()
    db.refresh(db_offer)
    return db_offer

def delete_offer(db: Session, offer_id: int):
    """Elimina una oferta de tienda de la base de datos."""
    db.execute(delete(models.StoreCatalog).where(models.StoreCatalog.offer_id == offer_id))
    db.commit()