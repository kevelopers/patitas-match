from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    role = Column(String, index=True)
    name = Column(String)
    phone = Column(String)

    preference = relationship("UserPreference", back_populates="user", uselist=False)
    animals = relationship("Animal", back_populates="foundation")
    reported_rescues = relationship(
        "RescueReport",
        foreign_keys="[RescueReport.reporter_id]",
        back_populates="reporter",
    )
    handled_rescues = relationship(
        "RescueReport",
        foreign_keys="[RescueReport.rescuer_id]",
        back_populates="rescuer",
    )
    matches = relationship("Match", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    preferred_size = Column(String)
    preferred_energy = Column(String)
    has_yard = Column(Boolean, default=False)

    user = relationship("User", back_populates="preference")
