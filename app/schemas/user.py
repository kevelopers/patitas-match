from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class UserPreferenceBase(BaseModel):
    preferred_size: List[str] = []
    preferred_energy: List[str] = []
    preferred_age: List[str] = []
    has_yard: bool = False


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    user_id: str
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    id: str
    role: str
    name: str
    phone: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    preferences: Optional[UserPreferenceResponse] = None
    model_config = ConfigDict(from_attributes=True)
