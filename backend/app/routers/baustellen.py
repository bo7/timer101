"""
Baustellen router (construction sites)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.baustelle import Baustelle
from ..schemas.baustelle import BaustelleResponse

router = APIRouter(prefix="/api/baustellen", tags=["baustellen"])


@router.get("", response_model=List[BaustelleResponse])
def get_baustellen(
    customer_id: int = Query(..., description="Customer ID to filter baustellen"),
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all baustellen (construction sites) for a specific customer
    """
    query = db.query(Baustelle).filter(Baustelle.customer_id == customer_id)

    if active_only:
        query = query.filter(Baustelle.active == True)

    baustellen = query.all()
    return baustellen


@router.get("/{baustelle_id}", response_model=BaustelleResponse)
def get_baustelle(
    baustelle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific baustelle by ID
    """
    baustelle = db.query(Baustelle).filter(Baustelle.id == baustelle_id).first()

    if not baustelle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baustelle not found"
        )

    return baustelle
