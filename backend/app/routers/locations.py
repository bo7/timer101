"""
Locations router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.location import Location
from ..schemas.location import LocationResponse

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("", response_model=List[LocationResponse])
def get_locations(
    customer_id: int = Query(..., description="Customer ID to filter locations"),
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all locations for a specific customer
    """
    query = db.query(Location).filter(Location.customer_id == customer_id)

    if active_only:
        query = query.filter(Location.active == True)

    locations = query.all()
    return locations


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific location by ID
    """
    location = db.query(Location).filter(Location.id == location_id).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    return location
