from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    foundation_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    animal_type = Column(String)
    size = Column(String)
    energy_level = Column(String)
    status = Column(String, default="available")

    foundation = relationship("User", back_populates="animals")
    match = relationship("Match", back_populates="animal", uselist=False)
