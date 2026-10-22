from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional

class BoostBase(BaseModel):
    boost_effect: Decimal
    boost_type: int

class BoostCreate(BoostBase):
    pass

class BoostUpdate(BaseModel):
    boost_effect: Optional[Decimal]
    boost_type: Optional[int]

class BoostResponse(BaseModel):
    boost_id: int
    boost_effect: Decimal
    boost_type: str

    model_config = ConfigDict(from_attributes=True)
