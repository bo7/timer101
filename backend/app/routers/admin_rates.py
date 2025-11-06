"""
Admin baustelle rates management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models.user import User
from ..models.baustelle import Baustelle
from ..models.baustelle_rate import BaustelleRate
from ..schemas.baustelle_rate import (
    BaustelleRateCreate,
    BaustelleRateUpdate,
    BaustelleRateResponse,
    BaustelleRateWithNames
)

router = APIRouter(prefix="/admin/api/rates", tags=["Admin - Rates"])


@router.get("", response_model=List[BaustelleRateWithNames])
def get_all_rates(
    baustelle_id: Optional[int] = None,
    employee_type: Optional[str] = None,
    current_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all baustelle rates (admin only)"""
    query = db.query(
        BaustelleRate,
        Baustelle.name.label("baustelle_name")
    ).join(Baustelle, BaustelleRate.baustelle_id == Baustelle.id)

    if baustelle_id:
        query = query.filter(BaustelleRate.baustelle_id == baustelle_id)

    if employee_type:
        query = query.filter(BaustelleRate.employee_type == employee_type)

    if current_only:
        query = query.filter(BaustelleRate.valid_to.is_(None))

    results = query.order_by(
        Baustelle.name,
        BaustelleRate.employee_type,
        BaustelleRate.valid_from.desc()
    ).all()

    # Transform results
    rates_with_names = []
    for rate, baustelle_name in results:
        rate_dict = {
            "id": rate.id,
            "baustelle_id": rate.baustelle_id,
            "employee_type": rate.employee_type,
            "hourly_rate": rate.hourly_rate,
            "valid_from": rate.valid_from,
            "valid_to": rate.valid_to,
            "created_at": rate.created_at,
            "baustelle_name": baustelle_name
        }
        rates_with_names.append(BaustelleRateWithNames(**rate_dict))

    return rates_with_names


@router.get("/{rate_id}", response_model=BaustelleRateResponse)
def get_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific rate by ID (admin only)"""
    rate = db.query(BaustelleRate).filter(BaustelleRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


@router.post("", response_model=BaustelleRateResponse, status_code=status.HTTP_201_CREATED)
def create_rate(
    rate_data: BaustelleRateCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new baustelle rate (admin only)"""
    # Check if baustelle exists
    baustelle = db.query(Baustelle).filter(Baustelle.id == rate_data.baustelle_id).first()
    if not baustelle:
        raise HTTPException(status_code=404, detail="Baustelle not found")

    # Check for overlapping rates
    existing_rate = db.query(BaustelleRate).filter(
        and_(
            BaustelleRate.baustelle_id == rate_data.baustelle_id,
            BaustelleRate.employee_type == rate_data.employee_type,
            BaustelleRate.valid_to.is_(None)
        )
    ).first()

    if existing_rate:
        # Close the old rate
        existing_rate.valid_to = rate_data.valid_from

    # Create new rate
    new_rate = BaustelleRate(
        baustelle_id=rate_data.baustelle_id,
        employee_type=rate_data.employee_type,
        hourly_rate=rate_data.hourly_rate,
        valid_from=rate_data.valid_from,
        valid_to=rate_data.valid_to
    )

    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)

    return new_rate


@router.put("/{rate_id}", response_model=BaustelleRateResponse)
def update_rate(
    rate_id: int,
    rate_data: BaustelleRateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a baustelle rate (admin only)"""
    rate = db.query(BaustelleRate).filter(BaustelleRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    # Update fields if provided
    if rate_data.employee_type is not None:
        rate.employee_type = rate_data.employee_type

    if rate_data.hourly_rate is not None:
        rate.hourly_rate = rate_data.hourly_rate

    if rate_data.valid_from is not None:
        rate.valid_from = rate_data.valid_from

    if rate_data.valid_to is not None:
        rate.valid_to = rate_data.valid_to

    db.commit()
    db.refresh(rate)

    return rate


@router.delete("/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a baustelle rate (admin only)"""
    rate = db.query(BaustelleRate).filter(BaustelleRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    db.delete(rate)
    db.commit()

    return None


@router.get("/baustelle/{baustelle_id}/current", response_model=List[BaustelleRateResponse])
def get_current_rates_for_baustelle(
    baustelle_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get current rates for a specific baustelle (admin only)"""
    # Check if baustelle exists
    baustelle = db.query(Baustelle).filter(Baustelle.id == baustelle_id).first()
    if not baustelle:
        raise HTTPException(status_code=404, detail="Baustelle not found")

    rates = db.query(BaustelleRate).filter(
        and_(
            BaustelleRate.baustelle_id == baustelle_id,
            BaustelleRate.valid_to.is_(None)
        )
    ).order_by(BaustelleRate.employee_type).all()

    return rates
