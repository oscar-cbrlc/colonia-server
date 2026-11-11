from sqlalchemy.orm import Session
from fastapi import HTTPException
from model import models
from config import settings
from crud import avatar_item_crud, item_bundle_crud, avatar_inventory_crud
from schema.avatar_inventory_schema import AvatarInventoryResponse
from utils.response_builder import build_avatar_inventory_response

def process_purchase(db: Session, db_user: models.Users, db_offer: models.StoreCatalog):
    """Reduce monedas a la cuenta del usuario y otorga los objetos comprados"""

    offer_items_ids = []
    
    if db_offer.avatar_item_id is not None:
        db_item = avatar_item_crud.get_item_by_id(db, db_offer.avatar_item_id)
        if db_item is None:
            raise HTTPException(
                status_code=404,
                detail="El objeto de la oferta no existe."
            )
        offer_items_ids = [db_item.avatar_item_id]

    elif db_offer.bundle_id is not None:
        items = item_bundle_crud.get_items_in_bundle(db, db_offer.bundle_id)
        if not items:
            raise HTTPException(
                status_code=409,
                detail="El paquete no contiene objetos."
            )
        offer_items_ids = [
            db_item.avatar_item_id
            for db_item in items
        ]

    else:
        raise HTTPException(
            status_code=409,
            detail="La oferta no tiene un objeto o paquete asociado."
        )

    user_inventory = avatar_inventory_crud.get_avatar_inventory(db, db_user.user_id)
    owned_item_ids = {
        avatar_item.avatar_item_id
        for _, avatar_item in user_inventory
    }

    duplicated_items = owned_item_ids.intersection(offer_items_ids)
    if duplicated_items:
        raise HTTPException(
            status_code=409,
            detail="Ya posees uno o más objetos de esta oferta."
        )

    db_user.coin_amount -= db_offer.offer_price

    for item_id in offer_items_ids:
        avatar_inventory_crud.add_item_to_inventory(db, db_user, item_id)
    
