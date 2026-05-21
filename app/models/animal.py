from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    foundation_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    animal_type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    energy_level = Column(String, nullable=False)
    age = Column(String)
    status = Column(String, default="available")

    foundation = relationship("User", back_populates="animals")
    match = relationship("Match", back_populates="animal")
