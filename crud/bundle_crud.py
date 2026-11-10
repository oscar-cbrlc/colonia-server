from sqlalchemy import delete
from sqlalchemy.orm import Session
from model import models
from schema.bundle_schema import BundleCreate, BundleUpdate

def get_all_bundles(db: Session):
    """Retorna el catalogo de paquetes de items de avatar ordenado por identificador."""
    return (
        db.query(models.Bundle)
        .order_by(models.Bundle.bundle_id)
        .all()
    )

def get_bundle_by_id(db: Session, bundle_id: int):
    """Busca un paquete de items de avatar por su identificador."""
    return (
        db.query(models.Bundle)
        .filter(models.Bundle.bundle_id == bundle_id)
        .first()
    )

def create_bundle(db: Session, bundle_in: BundleCreate):
    """Crea un paquete de items de avatar en el catalogo."""
    db_bundle = models.Bundle(**bundle_in.model_dump())
    db.add(db_bundle)
    db.flush()
    return db_bundle

def update_bundle(db: Session, db_bundle: models.Bundle, item_in: BundleUpdate):
    """Actualiza solamente los campos recibidos de un paquete de items de avatar."""
    update_data = item_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_bundle, field, value)

    db.commit()
    db.refresh(db_bundle)
    return db_bundle

def delete_bundle(db: Session, bundle_id: int):
    """Elimina un paquete de item de avatar."""
    db.execute(delete(models.Bundle).where(models.Bundle.bundle_id == bundle_id))
    db.commit()