from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserPreferenceBase(BaseModel):
    preferred_size: str
    preferred_energy: str
    has_yard: bool


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    id: int
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
    id: str
    preference: Optional[UserPreferenceResponse] = None
    model_config = ConfigDict(from_attributes=True)
