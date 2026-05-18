from pydantic import BaseModel, ConfigDict
from typing import Optional


class RescueReportBase(BaseModel):
    location: str
    ai_tags: Optional[str] = None


class RescueReportCreate(RescueReportBase):
    pass


class RescueReportResponse(RescueReportBase):
    id: int
    reporter_id: int
    rescuer_id: Optional[int] = None
    status: str
    model_config = ConfigDict(from_attributes=True)
