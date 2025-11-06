"""
BaustelleRate schemas
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class BaustelleRateBase(BaseModel):
    """Base baustelle rate schema"""
    baustelle_id: int
    employee_type: str = Field(..., pattern="^(Geselle|Meister|Polier)$")
    hourly_rate: Decimal = Field(..., ge=0, decimal_places=2)
    valid_from: date


class BaustelleRateCreate(BaustelleRateBase):
    """Baustelle rate creation schema"""
    valid_to: Optional[date] = None


class BaustelleRateUpdate(BaseModel):
    """Baustelle rate update schema"""
    employee_type: Optional[str] = Field(None, pattern="^(Geselle|Meister|Polier)$")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class BaustelleRateResponse(BaustelleRateBase):
    """Baustelle rate response schema"""
    id: int
    valid_to: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BaustelleRateWithNames(BaustelleRateResponse):
    """Baustelle rate response with related names"""
    baustelle_name: Optional[str] = None
    customer_name: Optional[str] = None

    class Config:
        from_attributes = True
