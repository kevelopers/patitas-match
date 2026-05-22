from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="matches")
    animal = relationship("Animal", back_populates="matches")


class Rejection(Base):
    __tablename__ = "rejections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
