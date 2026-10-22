from pydantic import BaseModel, ConfigDict
from typing import Optional

class ItemBase(BaseModel):
    item_name: str
    item_type: int
    item_image: str
    item_url: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_type: Optional[int] = None
    item_image: Optional[str] = None
    item_url: Optional[str] = None

class AvatarItemResponse(BaseModel):
    avatar_item_id: int
    item_name: str
    item_type: str
    item_image: str
    item_url: str

    model_config = ConfigDict(from_attributes=True)

