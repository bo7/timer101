"""
Worktime model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Worktime(Base):
    """Time tracking entry model"""

    __tablename__ = "worktimes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    break_minutes = Column(Integer, default=0, nullable=False)
    worked_minutes = Column(Integer, nullable=False)
    processed = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="worktimes")
    customer = relationship("Customer", back_populates="worktimes")
    location = relationship("Location", back_populates="worktimes")

    # Check constraints
    __table_args__ = (
        CheckConstraint('break_minutes >= 0', name='check_break_positive'),
        CheckConstraint('worked_minutes > 0', name='check_worked_positive'),
    )

    def __repr__(self):
        return f"<Worktime(id={self.id}, user_id={self.user_id}, date={self.start_time.date()})>"
