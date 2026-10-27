from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from schema.avatar_item_schema import AvatarItemResponse

class AvatarInventoryCreate(BaseModel):
    avatar_item_id: int
    user_id: int
    item_acquisition_date: datetime

class AvatarInventoryResponse(BaseModel):
    item: AvatarItemResponse
    item_adquisition_date: datetime
    model_config = ConfigDict(from_attributes=True)