from pydantic import BaseModel, ConfigDict
from typing import Optional
from schema.reward_schema import RewardResponse
from decimal import Decimal

class ChallengeBase(BaseModel):
    challege_reward: int
    objective_type: int
    objective_condition: dict
    challenge_difficulty: int

class ChallengeCreate(ChallengeBase):
    challenge_name: Optional[str] = None

class ChallengeUpdate(BaseModel):
    challenge_name: Optional[str] = None
    challege_reward: Optional[int] = None
    objective_type: Optional[int] = None
    objective_condition: Optional[dict] = None
    challenge_difficulty: Optional[int] = None

class ChallengeResponse(BaseModel):
    challenge_id: int
    challenge_name: Optional[str] = None
    challege_reward: RewardResponse
    objective_type: str
    objective_condition: dict
    challenge_difficulty: str
    challenge_xp_reward: int
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
    # To do: Add route metric
