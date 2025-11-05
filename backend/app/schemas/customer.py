"""
Customer schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str = Field(..., min_length=1, max_length=200)
    customer_number: str = Field(..., min_length=1, max_length=50)


class CustomerCreate(CustomerBase):
    """Customer creation schema"""
    active: bool = True


class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerSearch(BaseModel):
    """Customer search result"""
    id: int
    name: str
    customer_number: str

    class Config:
        from_attributes = True
