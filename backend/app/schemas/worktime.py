"""
Worktime schemas
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class WorktimeBase(BaseModel):
    """Base worktime schema"""
    customer_id: int
    location_id: int
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    break_minutes: int = Field(default=0, ge=0)

    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v, info):
        """Validate that end_time is after start_time"""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @field_validator('break_minutes')
    @classmethod
    def break_not_too_long(cls, v, info):
        """Validate that break is not longer than total time"""
        if 'start_time' in info.data and 'end_time' in info.data:
            total_minutes = (info.data['end_time'] - info.data['start_time']).total_seconds() / 60
            if v >= total_minutes:
                raise ValueError('break_minutes cannot be longer than or equal to total time')
        return v


class WorktimeCreate(WorktimeBase):
    """Worktime creation schema"""
    pass


class WorktimeUpdate(BaseModel):
    """Worktime update schema - all fields optional"""
    customer_id: Optional[int] = None
    location_id: Optional[int] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_minutes: Optional[int] = Field(default=None, ge=0)

    @field_validator('end_time')
    @classmethod
    def end_after_start(cls, v, info):
        """Validate that end_time is after start_time if both provided"""
        if v is not None and 'start_time' in info.data and info.data['start_time'] is not None:
            if v <= info.data['start_time']:
                raise ValueError('end_time must be after start_time')
        return v


class WorktimeResponse(WorktimeBase):
    """Worktime response schema"""
    id: int
    user_id: int
    worked_minutes: int
    processed: bool
    created_at: datetime
    updated_at: datetime

    # Nested data
    customer_name: Optional[str] = None
    location_name: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True
