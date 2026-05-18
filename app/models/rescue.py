from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class RescueReport(Base):
    __tablename__ = "rescue_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    rescuer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ai_tags = Column(String)
    location = Column(String)
    status = Column(String, default="pending")

    reporter = relationship(
        "User", foreign_keys=[reporter_id], back_populates="reported_rescues"
    )
    rescuer = relationship(
        "User", foreign_keys=[rescuer_id], back_populates="handled_rescues"
    )
