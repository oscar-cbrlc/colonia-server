from sqlalchemy import delete
from sqlalchemy.orm import Session

from model import models
from schema.boost_schema import BoostCreate, BoostUpdate


def get_boosts(db: Session, skip: int = 0, limit: int = 100):
    """Retorna el catalogo de potenciadores ordenado por identificador."""
    return (
        db.query(models.Boost)
        .order_by(models.Boost.boost_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_boost_by_id(db: Session, boost_id: int):
    """Busca un potenciador por su identificador."""
    return (
        db.query(models.Boost)
        .filter(models.Boost.boost_id == boost_id)
        .first()
    )


def create_boost(db: Session, boost_in: BoostCreate):
    """Crea un potenciador en el catalogo."""
    db_boost = models.Boost(**boost_in.model_dump())
    db.add(db_boost)
    db.commit()
    db.refresh(db_boost)
    return db_boost


def update_boost(db: Session, db_boost: models.Boost, boost_in: BoostUpdate):
    """Actualiza solamente los campos recibidos de un potenciador."""
    update_data = boost_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(db_boost, field, value)

    db.commit()
    db.refresh(db_boost)
    return db_boost


def delete_boost(db: Session, boost_id: int):
    """Elimina un potenciador y deja que PostgreSQL aplique sus cascadas."""
    db.execute(delete(models.Boost).where(models.Boost.boost_id == boost_id))
    db.commit()
