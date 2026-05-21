from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class RescueReport(Base):
    __tablename__ = "rescue_reports"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    image_url = Column(String)
    ai_tags = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reporter = relationship(
        "User", foreign_keys=[reporter_id], back_populates="reported_rescues"
    )
