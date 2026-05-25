from sqlalchemy import Column, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    size_preference = Column(String, nullable=True)
    energy_preference = Column(String, nullable=True)
    stage_preference = Column(String, nullable=True)
    has_yard = Column(Boolean, default=False)

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    animals = relationship("Animal", back_populates="foundation")
    reported_rescues = relationship(
        "RescueReport",
        foreign_keys="[RescueReport.reporter_id]",
        back_populates="reporter",
    )
    matches = relationship("Match", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    preferred_size = Column(JSON, default=list)
    preferred_energy = Column(JSON, default=list)
    preferred_age = Column(JSON, default=list)
    has_yard = Column(Boolean, default=False)

    user = relationship("User", back_populates="preferences")
