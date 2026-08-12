from pydantic import BaseModel, ConfigDict
from typing import Optional

class BoostInventoryBase(BaseModel):
    user_id: int
    boost_id: int
    boost_amount: int

# Actualizar información de inventario
class BoostInventoryUpdate(BaseModel):
    boost_amount: int

class BoostInventoryResponse(BoostInventoryBase):
    model_config = ConfigDict(from_attributes=True)