from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

class BoostInventoryUpdate(BaseModel):
    boost_amount: int

class BoostInventoryResponse(BaseModel):
    boost_id: int
    inventory_quantity: int
    boost_name: str
    boost_description: str
    boost_effect: Decimal
    model_config = ConfigDict(from_attributes=True)