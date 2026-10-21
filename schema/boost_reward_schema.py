from pydantic import BaseModel, ConfigDict
from typing import Optional
from schema.boost_schema import BoostResponse

class BoostRewardBase(BaseModel):
    challenge_id: int
    boost_id: int

class BoostRewardCreate(BoostRewardBase):
    boost_amount: Optional[int] = None

class BoostRewardUpdate(BaseModel):
    boost_id: int
    boost_amount: Optional[int] = None

class BoostRewardResponse(BaseModel):
    boost: BoostResponse
    boost_amount: int

    model_config = ConfigDict(from_attributes=True)
