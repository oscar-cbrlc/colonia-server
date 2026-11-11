from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from sqlalchemy.orm import Session
from database import get_db
from model import models
from crud import store_offer_crud, user_crud, avatar_inventory_crud
from schema.store_offer_schema import StoreOfferResponse
from schema.avatar_inventory_schema import AvatarInventoryResponse
from utils.auth import get_current_user
from utils.response_builder import build_store_offer_response, build_avatar_inventory_response
from utils.store_manager import process_purchase

router = APIRouter(
    prefix="/store",
    tags=["Tienda"],
)

def require_admin(current_user: models.Users = Depends(get_current_user),) -> models.Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta accion",
        )
    return current_user

@router.get("/", response_model=list[StoreOfferResponse])
def list_store_catalog(db: Session = Depends(get_db),):
    """Retorna el catalogo de ofertas de tienda."""
    results = store_offer_crud.get_all_offers(db)
    return[
        build_store_offer_response(db, db_offer)
        for db_offer in results
    ]

@router.patch("/{offer_id}", response_model=list[AvatarInventoryResponse])
def buy_store_offer(
        offer_id: int,
        current_user: models.Users = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    """Compra una oferta de tienda y asigna al inventario los items que contiene."""
    try:
        db_user = (
            db.query(models.Users)
            .filter(models.Users.user_id == current_user.user_id)
            .populate_existing()
            .with_for_update()
            .one_or_none()
        )

        db_offer = (
            db.query(models.StoreCatalog)
            .filter(models.StoreCatalog.offer_id == offer_id)
            .populate_existing()
            .with_for_update()
            .one_or_none()
        )

        if db_user.coin_amount < db_offer.offer_price:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Saldo insuficiente."
            )

        process_purchase(db, db_user, db_offer)

        db.flush()
        db.commit()
        
        user_inventory = avatar_inventory_crud.get_avatar_inventory(db, current_user.user_id)
        return[
            build_avatar_inventory_response(db_inventory, db_avatar_item)
            for db_inventory, db_avatar_item in user_inventory
        ]
    
    except Exception:
        db.rollback()
        raise
            