from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class BoostInventoryUpdate(BaseModel):
    boost_amount: int

class BoostInventoryResponse(BaseModel):
    boost_id: int
    boost_type: str
    inventory_quantity: int
    boost_effect: Decimal
    model_config = ConfigDict(from_attributes=True)