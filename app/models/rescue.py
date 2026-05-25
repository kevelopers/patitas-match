from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
)
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
    rescuer_id = Column(String, ForeignKey("users.id"), nullable=True)
    urgency = Column(String, default="medium", nullable=False)
    breed_mix = Column(String, nullable=True)
    detected_mood = Column(String, nullable=True)
    physical_condition = Column(String, nullable=True)
    first_aid_advice = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reporter = relationship(
        "User", back_populates="reported_rescues", foreign_keys=[reporter_id]
    )
    likes = relationship(
        "RescueLike", back_populates="report", cascade="all, delete-orphan"
    )


class RescueLike(Base):
    __tablename__ = "rescue_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("rescue_reports.id"), nullable=False)

    report = relationship("RescueReport", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("user_id", "report_id", name="unique_user_report_like"),
    )
