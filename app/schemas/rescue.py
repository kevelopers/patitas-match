from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RescueReportBase(BaseModel):
    reporter_id: str
    location: str


class RescueReportCreate(RescueReportBase):
    pass


class RescueReportResponse(RescueReportBase):
    id: int
    image_url: Optional[str] = None
    ai_tags: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
