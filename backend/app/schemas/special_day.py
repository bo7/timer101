"""
SpecialDay schemas
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class SpecialDayBase(BaseModel):
    """Base special day schema"""
    user_id: int
    date: date
    day_type: str = Field(..., pattern="^(Urlaub|Krank|Feiertag|Sonstiges)$")
    description: Optional[str] = None


class SpecialDayCreate(SpecialDayBase):
    """Special day creation schema"""
    pass


class SpecialDayUpdate(BaseModel):
    """Special day update schema"""
    user_id: Optional[int] = None
    date: Optional[date] = None
    day_type: Optional[str] = Field(None, pattern="^(Urlaub|Krank|Feiertag|Sonstiges)$")
    description: Optional[str] = None


class SpecialDayResponse(SpecialDayBase):
    """Special day response schema"""
    id: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True


class SpecialDayWithNames(SpecialDayResponse):
    """Special day response with user names"""
    user_username: Optional[str] = None
    user_first_name: Optional[str] = None
    user_last_name: Optional[str] = None
    creator_username: Optional[str] = None

    class Config:
        from_attributes = True
