from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    foundation_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    animal_type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    energy_level = Column(String, nullable=False)
    age = Column(String, nullable=False)
    status = Column(String, default="available", nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    foundation = relationship("User", back_populates="animals")
    follow_up_logs = relationship(
        "AnimalFollowUpLog",
        back_populates="animal",
        cascade="all, delete-orphan",
    )
    matches = relationship("Match", back_populates="animal")


class AnimalFollowUpLog(Base):
    __tablename__ = "animal_follow_up_logs"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    animal = relationship("Animal", back_populates="follow_up_logs")
