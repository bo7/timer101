"""
BaustelleRate model for tracking hourly rates per construction site
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class BaustelleRate(Base):
    """Hourly rate per construction site and employee type"""

    __tablename__ = "baustelle_rates"

    id = Column(Integer, primary_key=True, index=True)
    baustelle_id = Column(Integer, ForeignKey("baustellen.id", ondelete="CASCADE"), nullable=False)
    employee_type = Column(String(20), nullable=False)  # "Geselle", "Meister", "Polier"
    hourly_rate = Column(Numeric(10, 2), nullable=False)  # Euro per hour
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)  # NULL means current rate
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    baustelle = relationship("Baustelle", back_populates="rates")

    def __repr__(self):
        return f"<BaustelleRate(id={self.id}, baustelle_id={self.baustelle_id}, type='{self.employee_type}', rate={self.hourly_rate})>"
