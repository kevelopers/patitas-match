from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    animal_id = Column(Integer, ForeignKey("animals.id"))
    match_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="matches")
    animal = relationship("Animal", back_populates="match")
