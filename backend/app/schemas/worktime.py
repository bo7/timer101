"""
Worktime schemas
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional


class WorktimeBase(BaseModel):
    """Base worktime schema"""
    customer_id: int
    baustelle_id: int
    lv_entry_id: Optional[int] = None
    date: date
    worked_hours: int = Field(..., ge=1, le=8)
    freitext_description: Optional[str] = None

    @field_validator('freitext_description')
    @classmethod
    def freitext_required_if_no_lv(cls, v, info):
        """If no lv_entry_id, freitext must be provided"""
        if info.data.get('lv_entry_id') is None and not v:
            raise ValueError('freitext_description required when no lv_entry selected')
        return v


class WorktimeCreate(WorktimeBase):
    """Worktime creation schema"""
    pass


class WorktimeUpdate(BaseModel):
    """Worktime update schema - all fields optional"""
    customer_id: Optional[int] = None
    baustelle_id: Optional[int] = None
    lv_entry_id: Optional[int] = None
    date: Optional[date] = None
    worked_hours: Optional[int] = Field(None, ge=1, le=8)
    freitext_description: Optional[str] = None


class WorktimeResponse(WorktimeBase):
    """Worktime response schema"""
    id: int
    user_id: int
    processed: bool
    created_at: datetime
    updated_at: datetime

    # Nested data
    customer_name: Optional[str] = None
    baustelle_name: Optional[str] = None
    lv_position_number: Optional[str] = None
    lv_description: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True
