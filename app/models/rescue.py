from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class RescueReport(Base):
    __tablename__ = "rescue_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    ai_tags = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    likes_count = Column(Integer, default=0)
    status = Column(String, default="pending", nullable=False)
    allied_foundation_id = Column(String, ForeignKey("users.id"), nullable=True)
    external_shelter_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reporter = relationship(
        "User", back_populates="reported_rescues", foreign_keys=[reporter_id]
    )
