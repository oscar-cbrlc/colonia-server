from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from schema.boost_reward_schema import BoostRewardCreate, BoostRewardResponse
from schema.avatar_item_schema import AvatarItemResponse

class ChallengeBase(BaseModel):
    objective_type: int
    objective_condition: dict
    challenge_difficulty: int
    boosts_reward: list[BoostRewardCreate]

class ChallengeCreate(ChallengeBase):
    challenge_name: Optional[str] = None
    avatar_item_id: Optional[int] = None

class ChallengeUpdate(BaseModel):
    challenge_name: Optional[str] = None
    objective_type: Optional[int] = None
    objective_condition: Optional[dict] = None
    challenge_difficulty: Optional[int] = None
    avatar_item_id: Optional[int] = None

class ChallengeResponse(BaseModel):
    challenge_id: int
    challenge_name: Optional[str] = None
    objective_type: str
    objective_condition: dict
    challenge_difficulty: str
    challenge_xp_reward: int   
    boost_reward: list[BoostRewardResponse]
    item_reward: Optional[AvatarItemResponse] = None
    model_config = ConfigDict(from_attributes=True)

class Challenge_metrics(BaseModel):
    total_time: int
    walk_time: int
    run_time: int
    bike_time: int
    total_distance: Decimal
    walk_distance: Decimal
    run_distance: Decimal
    bike_distance: Decimal
    captured_territories: int
    traversed_territories : set