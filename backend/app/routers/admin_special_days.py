"""
Admin special days management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models.user import User
from ..models.special_days import SpecialDay
from ..schemas.special_day import (
    SpecialDayCreate,
    SpecialDayUpdate,
    SpecialDayResponse,
    SpecialDayWithNames
)

router = APIRouter(prefix="/admin/api/special-days", tags=["Admin - Special Days"])


@router.get("", response_model=List[SpecialDayWithNames])
def get_all_special_days(
    user_id: Optional[int] = None,
    day_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all special days (admin only)"""
    query = db.query(
        SpecialDay,
        User.username.label("user_username"),
        User.first_name.label("user_first_name"),
        User.last_name.label("user_last_name")
    ).join(User, SpecialDay.user_id == User.id)

    if user_id:
        query = query.filter(SpecialDay.user_id == user_id)

    if day_type:
        query = query.filter(SpecialDay.day_type == day_type)

    if from_date:
        query = query.filter(SpecialDay.date >= from_date)

    if to_date:
        query = query.filter(SpecialDay.date <= to_date)

    results = query.order_by(SpecialDay.date.desc()).all()

    # Transform results
    special_days_with_names = []
    for special_day, user_username, user_first_name, user_last_name in results:
        day_dict = {
            "id": special_day.id,
            "user_id": special_day.user_id,
            "date": special_day.date,
            "day_type": special_day.day_type,
            "description": special_day.description,
            "created_at": special_day.created_at,
            "created_by": special_day.created_by,
            "user_username": user_username,
            "user_first_name": user_first_name,
            "user_last_name": user_last_name
        }
        special_days_with_names.append(SpecialDayWithNames(**day_dict))

    return special_days_with_names


@router.get("/{special_day_id}", response_model=SpecialDayResponse)
def get_special_day(
    special_day_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific special day by ID (admin only)"""
    special_day = db.query(SpecialDay).filter(SpecialDay.id == special_day_id).first()
    if not special_day:
        raise HTTPException(status_code=404, detail="Special day not found")
    return special_day


@router.post("", response_model=SpecialDayResponse, status_code=status.HTTP_201_CREATED)
def create_special_day(
    special_day_data: SpecialDayCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new special day (admin only)"""
    # Check if user exists
    user = db.query(User).filter(User.id == special_day_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if special day already exists for this user and date
    existing = db.query(SpecialDay).filter(
        and_(
            SpecialDay.user_id == special_day_data.user_id,
            SpecialDay.date == special_day_data.date
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Special day already exists for this user and date"
        )

    # Create new special day
    new_special_day = SpecialDay(
        user_id=special_day_data.user_id,
        date=special_day_data.date,
        day_type=special_day_data.day_type,
        description=special_day_data.description,
        created_by=current_admin.id
    )

    db.add(new_special_day)
    db.commit()
    db.refresh(new_special_day)

    return new_special_day


@router.put("/{special_day_id}", response_model=SpecialDayResponse)
def update_special_day(
    special_day_id: int,
    special_day_data: SpecialDayUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a special day (admin only)"""
    special_day = db.query(SpecialDay).filter(SpecialDay.id == special_day_id).first()
    if not special_day:
        raise HTTPException(status_code=404, detail="Special day not found")

    # Update fields if provided
    if special_day_data.user_id is not None:
        # Check if user exists
        user = db.query(User).filter(User.id == special_day_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        special_day.user_id = special_day_data.user_id

    if special_day_data.date is not None:
        special_day.date = special_day_data.date

    if special_day_data.day_type is not None:
        special_day.day_type = special_day_data.day_type

    if special_day_data.description is not None:
        special_day.description = special_day_data.description

    db.commit()
    db.refresh(special_day)

    return special_day


@router.delete("/{special_day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_special_day(
    special_day_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a special day (admin only)"""
    special_day = db.query(SpecialDay).filter(SpecialDay.id == special_day_id).first()
    if not special_day:
        raise HTTPException(status_code=404, detail="Special day not found")

    db.delete(special_day)
    db.commit()

    return None


@router.get("/user/{user_id}/summary")
def get_user_special_days_summary(
    user_id: int,
    year: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get summary of special days for a user in a year (admin only)"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get special days for the year
    from_date = date(year, 1, 1)
    to_date = date(year, 12, 31)

    special_days = db.query(SpecialDay).filter(
        and_(
            SpecialDay.user_id == user_id,
            SpecialDay.date >= from_date,
            SpecialDay.date <= to_date
        )
    ).all()

    # Count by type
    summary = {
        "user_id": user_id,
        "username": user.username,
        "year": year,
        "total": len(special_days),
        "Urlaub": sum(1 for sd in special_days if sd.day_type == "Urlaub"),
        "Krank": sum(1 for sd in special_days if sd.day_type == "Krank"),
        "Feiertag": sum(1 for sd in special_days if sd.day_type == "Feiertag"),
        "Sonstiges": sum(1 for sd in special_days if sd.day_type == "Sonstiges")
    }

    return summary
