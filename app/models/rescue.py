from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class RescueReport(Base):
    __tablename__ = "rescue_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    location = Column(String, nullable=False)
    ai_tags = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    likes_count = Column(Integer, default=0)

    reporter = relationship("User")
