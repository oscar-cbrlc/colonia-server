from fastapi import APIRouter, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from crud import avatar_item_crud, avatar_inventory_crud, user_crud
from database import get_db
from model import models
from schema.user_schema import UserAvatarUpdate, AvatarUpdateResponse
from schema.avatar_item_schema import AvatarItemResponse
from schema.avatar_inventory_schema import AvatarInventoryResponse
from utils.auth import get_current_user
from utils.response_builder import build_avatar_item_response, build_avatar_inventory_response, build_avatar_update_response

router = APIRouter(
    prefix="/avatar",
    tags=["Avatar"],
)

@router.get("/", response_model=list[AvatarItemResponse])
def list_avatar_items(db: Session = Depends(get_db)):
    """Retorna el catalogo de items de avatar."""
    results = avatar_item_crud.get_all_items(db)
    return[
        build_avatar_item_response(db_avatar_item)
        for db_avatar_item in results
    ]

@router.get("/users/me/inventory", response_model=list[AvatarInventoryResponse])
def list_my_avatar_inventory(
    current_user: models.Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna el inventario de items del jugador autentificado."""
    results = avatar_inventory_crud.get_avatar_inventory(db, current_user.user_id)
    return[
        build_avatar_inventory_response(db_inventory, db_avatar_item)
        for db_inventory, db_avatar_item  in results
    ]

@router.patch("/users/me", response_model=AvatarUpdateResponse)
def update_avatar(
    avatar_update: UserAvatarUpdate, 
    current_user: models.Users = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Actualiza datos del avatar del usuario autenticado."""
    db_user = user_crud.update_user_avatar(db, current_user, avatar_update)
    return build_avatar_update_response(db, db_user)