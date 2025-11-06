"""
User model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """User model for employees and admins"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # New fields for admin interface
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    employee_type = Column(String(20), nullable=True)  # "Geselle", "Meister", "Polier"

    # Soft delete support
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    worktimes = relationship("Worktime", back_populates="user", cascade="all, delete-orphan")
    deleted_by_user = relationship("User", remote_side=[id], foreign_keys=[deleted_by])

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', admin={self.is_admin})>"
