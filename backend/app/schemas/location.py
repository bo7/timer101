"""
Location schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LocationBase(BaseModel):
    """Base location schema"""
    customer_id: int
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None


class LocationCreate(LocationBase):
    """Location creation schema"""
    active: bool = True


class LocationResponse(LocationBase):
    """Location response schema"""
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
