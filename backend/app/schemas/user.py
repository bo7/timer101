"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)
    is_admin: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_type: Optional[str] = None  # "Geselle", "Meister", "Polier"


class UserUpdate(BaseModel):
    """User update schema (all fields optional)"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_admin: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_type: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_admin: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_type: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
