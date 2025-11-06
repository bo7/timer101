"""
Leistungsverzeichnis schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LVEntryBase(BaseModel):
    """Base LV entry schema"""
    baustelle_id: int
    position_number: Optional[str] = Field(None, max_length=50)
    description: str = Field(..., min_length=1)
    unit: Optional[str] = Field(None, max_length=50)
    is_freitext: bool = False


class LVEntryCreate(LVEntryBase):
    """LV entry creation schema"""
    active: bool = True


class LVEntryResponse(LVEntryBase):
    """LV entry response schema"""
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LVEntrySearch(BaseModel):
    """LV entry search response - minimal for autocomplete"""
    id: int
    position_number: Optional[str]
    description: str
    unit: Optional[str]
    is_freitext: bool

    class Config:
        from_attributes = True
