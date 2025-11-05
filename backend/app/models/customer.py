"""
Customer model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Customer(Base):
    """Customer/Client model"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    customer_number = Column(String(50), unique=True, nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    locations = relationship("Location", back_populates="customer", cascade="all, delete-orphan")
    worktimes = relationship("Worktime", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', number='{self.customer_number}')>"
