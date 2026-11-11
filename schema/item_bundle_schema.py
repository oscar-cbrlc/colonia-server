from pydantic import BaseModel
from schema.avatar_item_schema import AvatarItemResponse
from schema.bundle_schema import BundleResponse

class ItemBundleCreate(BaseModel):
    avatar_item_id: int
    bundle_id: int

class ItemBundleResponse(BaseModel):
    bundle: BundleResponse
    avatar_items: list[AvatarItemResponse]