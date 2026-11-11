from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional
from typing_extensions import Self
from decimal import Decimal
from schema.avatar_item_schema import AvatarItemResponse
from schema.item_bundle_schema import ItemBundleResponse

class StoreOfferBase(BaseModel):
    offer_type: int
    offer_price: Decimal

class StoreOfferCreate(StoreOfferBase):
    avatar_item_id: Optional[int]
    bundle_id: Optional[int]

    @model_validator(mode='after')
    def check_offer_items(self) -> Self:
        if self.avatar_item_id is None or self.bundle_id is None:
            raise ValueError('Tiene que haber al menos un item en la oferta')
        return self

class StoreOfferUpdate(BaseModel):
    offer_type: Optional[int]
    offer_price: Optional[Decimal] 
    avatar_item_id: Optional[int]
    bundle_id: Optional[int]

class StoreOfferResponse(BaseModel):
    offer_id: int
    offer_name: str
    offer_type: str
    offer_image: str
    offer_price: Decimal
    avatar_item: Optional[AvatarItemResponse]
    bundle: Optional[ItemBundleResponse]
    model_config = ConfigDict(from_attributes=True)