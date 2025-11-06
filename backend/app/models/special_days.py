"""
SpecialDays model for tracking holidays, vacation, sick days, etc.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class SpecialDay(Base):
    """Special days tracking (holidays, vacation, sick days)"""

    __tablename__ = "special_days"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    day_type = Column(String(20), nullable=False)  # "Urlaub", "Krank", "Feiertag", "Sonstiges"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="special_days")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<SpecialDay(id={self.id}, user_id={self.user_id}, date={self.date}, type='{self.day_type}')>"
