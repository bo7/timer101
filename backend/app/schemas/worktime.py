"""
Worktime schemas
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date, time
from typing import Optional


class WorktimeBase(BaseModel):
    """Base worktime schema"""
    customer_id: int
    baustelle_id: int
    lv_entry_id: Optional[int] = None
    date: date

    # Hours mode fields
    worked_hours: Optional[int] = Field(None, ge=1, le=8)

    # Times mode fields
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: Optional[int] = Field(None, ge=0, le=480)  # Max 8 hours break

    freitext_description: Optional[str] = None
    is_regie: bool = False
    materials_used: Optional[str] = None
    picture_path: Optional[str] = None

    @field_validator('freitext_description')
    @classmethod
    def freitext_required_if_no_lv(cls, v, info):
        """If no lv_entry_id, freitext must be provided"""
        if info.data.get('lv_entry_id') is None and not v:
            raise ValueError('freitext_description required when no lv_entry selected')
        return v

    @model_validator(mode='after')
    def validate_time_mode(self):
        """Ensure either worked_hours OR (start_time + end_time) is provided"""
        has_hours = self.worked_hours is not None
        has_times = self.start_time is not None and self.end_time is not None

        if not has_hours and not has_times:
            raise ValueError('Either worked_hours or start_time+end_time must be provided')

        if has_hours and has_times:
            raise ValueError('Provide either worked_hours or start_time+end_time, not both')

        return self


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
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: Optional[int] = Field(None, ge=0, le=480)
    freitext_description: Optional[str] = None
    is_regie: Optional[bool] = None
    materials_used: Optional[str] = None
    picture_path: Optional[str] = None


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
