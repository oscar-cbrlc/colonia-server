from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from schema.challenge_schema import ChallengeCreate, ChallengeResponse

class ActiveChallengeBase(BaseModel):
    challenge_id: int
    challenge_start_date: datetime
    challenge_end_date: datetime

class ActiveChallengeCreate(ActiveChallengeBase):
    pass

class ActiveChallengeUpdate(BaseModel):
    challenge_id: Optional[int]
    challenge_start_date: Optional[datetime]
    challenge_end_date: Optional[datetime]

class ActiveChallengeResponse(BaseModel):
    active_challenge_id: int
    challenge: ChallengeResponse
    challenge_start_date: datetime
    challenge_end_date: datetime

    model_config = ConfigDict(from_attributes=True)

class EventCreate(BaseModel):
    challenge: ChallengeCreate
    challenge_start_date: datetime
    challenge_end_date: datetime