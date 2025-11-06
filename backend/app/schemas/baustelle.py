"""
Baustelle schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BaustelleBase(BaseModel):
    """Base baustelle schema"""
    customer_id: int
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None


class BaustelleCreate(BaustelleBase):
    """Baustelle creation schema"""
    active: bool = True


class BaustelleResponse(BaustelleBase):
    """Baustelle response schema"""
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
