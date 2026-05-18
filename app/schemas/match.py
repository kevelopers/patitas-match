from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MatchBase(BaseModel):
    animal_id: int


class MatchCreate(MatchBase):
    pass


class MatchResponse(MatchBase):
    id: int
    user_id: int
    match_date: datetime
    model_config = ConfigDict(from_attributes=True)
