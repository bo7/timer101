"""
Worktimes router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.worktime import Worktime
from ..models.customer import Customer
from ..models.location import Location
from ..schemas.worktime import WorktimeCreate, WorktimeUpdate, WorktimeResponse

router = APIRouter(prefix="/api/worktimes", tags=["worktimes"])


def calculate_worked_minutes(start_time: datetime, end_time: datetime, break_minutes: int) -> int:
    """Calculate worked minutes from start, end, and break"""
    total_minutes = int((end_time - start_time).total_seconds() / 60)
    return total_minutes - break_minutes


@router.get("", response_model=List[WorktimeResponse])
def get_worktimes(
    date_filter: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get worktimes for current user, optionally filtered by date
    """
    query = db.query(Worktime).filter(Worktime.user_id == current_user.id)

    # Filter by date if provided
    if date_filter:
        start_of_day = datetime.combine(date_filter, time.min)
        end_of_day = datetime.combine(date_filter, time.max)
        query = query.filter(
            Worktime.start_time >= start_of_day,
            Worktime.start_time <= end_of_day
        )

    worktimes = query.order_by(Worktime.start_time.desc()).offset(skip).limit(limit).all()

    # Enrich with related data
    result = []
    for wt in worktimes:
        wt_dict = {
            "id": wt.id,
            "user_id": wt.user_id,
            "customer_id": wt.customer_id,
            "location_id": wt.location_id,
            "description": wt.description,
            "start_time": wt.start_time,
            "end_time": wt.end_time,
            "break_minutes": wt.break_minutes,
            "worked_minutes": wt.worked_minutes,
            "processed": wt.processed,
            "created_at": wt.created_at,
            "updated_at": wt.updated_at,
            "customer_name": wt.customer.name if wt.customer else None,
            "location_name": wt.location.name if wt.location else None,
            "username": wt.user.username if wt.user else None
        }
        result.append(WorktimeResponse(**wt_dict))

    return result


@router.get("/{worktime_id}", response_model=WorktimeResponse)
def get_worktime(
    worktime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific worktime entry
    """
    worktime = db.query(Worktime).filter(
        Worktime.id == worktime_id,
        Worktime.user_id == current_user.id
    ).first()

    if not worktime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worktime entry not found"
        )

    # Enrich with related data
    wt_dict = {
        **worktime.__dict__,
        "customer_name": worktime.customer.name if worktime.customer else None,
        "location_name": worktime.location.name if worktime.location else None,
        "username": worktime.user.username if worktime.user else None
    }

    return WorktimeResponse(**wt_dict)


@router.post("", response_model=WorktimeResponse, status_code=status.HTTP_201_CREATED)
def create_worktime(
    worktime: WorktimeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new worktime entry
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == worktime.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Verify location exists and belongs to customer
    location = db.query(Location).filter(Location.id == worktime.location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    if location.customer_id != worktime.customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location does not belong to the selected customer"
        )

    # Calculate worked minutes
    worked_minutes = calculate_worked_minutes(
        worktime.start_time,
        worktime.end_time,
        worktime.break_minutes
    )

    # Create worktime entry
    db_worktime = Worktime(
        user_id=current_user.id,
        customer_id=worktime.customer_id,
        location_id=worktime.location_id,
        description=worktime.description,
        start_time=worktime.start_time,
        end_time=worktime.end_time,
        break_minutes=worktime.break_minutes,
        worked_minutes=worked_minutes,
        processed=False
    )

    db.add(db_worktime)
    db.commit()
    db.refresh(db_worktime)

    # Enrich with related data
    wt_dict = {
        **db_worktime.__dict__,
        "customer_name": db_worktime.customer.name,
        "location_name": db_worktime.location.name,
        "username": db_worktime.user.username
    }

    return WorktimeResponse(**wt_dict)


@router.put("/{worktime_id}", response_model=WorktimeResponse)
def update_worktime(
    worktime_id: int,
    worktime_update: WorktimeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a worktime entry (only if not processed)
    """
    # Get existing worktime
    db_worktime = db.query(Worktime).filter(
        Worktime.id == worktime_id,
        Worktime.user_id == current_user.id
    ).first()

    if not db_worktime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worktime entry not found"
        )

    # Check if processed
    if db_worktime.processed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update processed worktime entry"
        )

    # Update fields
    update_data = worktime_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_worktime, field, value)

    # Recalculate worked minutes if time fields changed
    if any(field in update_data for field in ['start_time', 'end_time', 'break_minutes']):
        db_worktime.worked_minutes = calculate_worked_minutes(
            db_worktime.start_time,
            db_worktime.end_time,
            db_worktime.break_minutes
        )

    db.commit()
    db.refresh(db_worktime)

    # Enrich with related data
    wt_dict = {
        **db_worktime.__dict__,
        "customer_name": db_worktime.customer.name,
        "location_name": db_worktime.location.name,
        "username": db_worktime.user.username
    }

    return WorktimeResponse(**wt_dict)


@router.delete("/{worktime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worktime(
    worktime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a worktime entry (only if not processed)
    """
    # Get existing worktime
    db_worktime = db.query(Worktime).filter(
        Worktime.id == worktime_id,
        Worktime.user_id == current_user.id
    ).first()

    if not db_worktime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worktime entry not found"
        )

    # Check if processed
    if db_worktime.processed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete processed worktime entry"
        )

    db.delete(db_worktime)
    db.commit()

    return None
