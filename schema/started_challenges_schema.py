from pydantic import BaseModel, ConfigDict
from typing import Optional
from schema.active_challenges_schema import ActiveChallengeResponse

class StartedChallengeUpdate(BaseModel):
    progress: int
    is_complete: Optional[bool]

class StartedChallengeResponse(BaseModel):
    active_challenge: ActiveChallengeResponse
    progress: int
    is_complete: bool
    model_config = ConfigDict(from_attributes=True)