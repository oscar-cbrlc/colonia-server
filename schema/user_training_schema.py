from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional
from schema.achievement_schema import AchievementResponse
from schema.started_challenges_schema import StartedChallengeResponse
from schema.territory_schema import TerritoryBase, TerritoryImpactResult
from schema.boost_schema import BoostResponse

class UserTrainingBase(BaseModel):
    training_uuid: UUID
    total_distance: int
    total_time: int
    territories: list[TerritoryBase]
    timestamp: datetime

class UserTrainingCreate(UserTrainingBase):
    boost_id: Optional[int] = None
    seconds_walk: Optional[int] = 0
    seconds_run: Optional[int] = 0
    seconds_bike: Optional[int] = 0
    meters_walk: Optional[int] = 0
    meters_run: Optional[int] = 0
    meters_bike: Optional[int] = 0

class UserStatsResult(BaseModel):
    user_id: int
    user_name: str
    total_distance: Decimal
    total_time: int
    total_territories: int
    total_attack: int
    total_defence: int
    model_config = ConfigDict(from_attributes=True)

class TrainingXPResult(BaseModel):
    time_xp: int
    distance_xp: int
    territories_xp: int
    total_xp: int

class TrainingResult(BaseModel):
    training_uuid: UUID
    user: UserStatsResult
    training: TrainingXPResult
    territories: list[TerritoryImpactResult]
    achievements: Optional[list[AchievementResponse]] = None
    challenges: Optional[list[StartedChallengeResponse]] = None

class UserTrainingResponse(BaseModel):
    user_id: int
    training_uuid: UUID
    training_distance: int
    training_time: int
    seconds_walk: int
    seconds_run: int
    seconds_bike: int
    meters_walk: int
    meters_run: int
    meters_bike: int
    captured_territories: int
    boost: BoostResponse
    training_attack: int
    training_defence: int
    started_at: datetime
    model_config = ConfigDict(from_attributes=True)