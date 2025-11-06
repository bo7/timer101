"""
Baustelle model (construction site)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Baustelle(Base):
    """Construction site model"""

    __tablename__ = "baustellen"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="baustellen")
    worktimes = relationship("Worktime", back_populates="baustelle")
    lv_entries = relationship("LeistungsverzeichnisEntry", back_populates="baustelle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Baustelle(id={self.id}, name='{self.name}', customer_id={self.customer_id})>"
