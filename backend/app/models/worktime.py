"""
Worktime model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, CheckConstraint, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Worktime(Base):
    """Time tracking entry model"""

    __tablename__ = "worktimes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    baustelle_id = Column(Integer, ForeignKey("baustellen.id", ondelete="RESTRICT"), nullable=False, index=True)
    lv_entry_id = Column(Integer, ForeignKey("leistungsverzeichnis_entries.id", ondelete="RESTRICT"), nullable=True, index=True)

    date = Column(Date, nullable=False, index=True)  # Work date

    # Hours mode (simple)
    worked_hours = Column(Integer, nullable=True)  # 1-8 hours (nullable for times mode)

    # Times mode (detailed)
    start_time = Column(Time, nullable=True)  # Start time
    end_time = Column(Time, nullable=True)  # End time
    break_minutes = Column(Integer, nullable=True, default=0)  # Break in minutes

    freitext_description = Column(Text)  # Only used when lv_entry is "Freitext"

    # Regie fields
    is_regie = Column(Boolean, default=False, nullable=False)  # Regie work flag
    materials_used = Column(Text)  # Materials used (only for Regie)
    picture_path = Column(String(500))  # Path to uploaded picture

    processed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="worktimes")
    customer = relationship("Customer", back_populates="worktimes")
    baustelle = relationship("Baustelle", back_populates="worktimes")
    lv_entry = relationship("LeistungsverzeichnisEntry", back_populates="worktimes")

    # No table constraints needed - validation done at application level

    def __repr__(self):
        return f"<Worktime(id={self.id}, user_id={self.user_id}, date={self.date}, hours={self.worked_hours})>"
