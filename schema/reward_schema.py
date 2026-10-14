from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from typing_extensions import Self
from enums.enum_types import Reward_Type
from schema.boost_schema import BoostResponse
from schema.avatar_item_schema import AvatarItemResponse

class RewardBase(BaseModel):
    reward_type: int
    reward_amount: int = Field(ge=1)
    reward_item: int
    reward_boost: int

    @model_validator(mode='after')
    def check_reward_selected(self) -> Self:
        if self.reward_item is None and self.reward_boost is None:
            raise ValueError('Reward not selected')
        
        match self.reward_type:
            case Reward_Type.boost:
                if self.reward_boost is None or self.reward_item is not None:
                    raise ValueError('Reward type does not match')
                
            case Reward_Type.avatar_Item:
                if self.reward_boost is not None or self.reward_item is None:
                    raise ValueError('Reward type does not match')
                
            case Reward_Type.boost_and_item:
                if self.reward_boost is None or self.reward_item is None:
                    raise ValueError('Reward type does not match')
        return self

class RewardCreate(RewardBase):
    reward_item: Optional[int] = None
    reward_boost: Optional[int] = None

class RewardUpdate(RewardBase):
    reward_amount: Optional[int] = None
    reward_item: Optional[int] = None
    reward_boost: Optional[int] = None

class RewardResponse(BaseModel):
    reward_id: int
    reward_type: str
    reward_amount: int
    reward_item: Optional[AvatarItemResponse]
    reward_boost: Optional[BoostResponse]

    model_config = ConfigDict(from_attributes=True)