"""
Leistungsverzeichnis router (work items/positions)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.leistungsverzeichnis import LeistungsverzeichnisEntry
from ..schemas.leistungsverzeichnis import LVEntryResponse, LVEntrySearch, LVEntryCreate

router = APIRouter(prefix="/api/lv", tags=["leistungsverzeichnis"])


@router.get("/search", response_model=List[LVEntrySearch])
def search_lv_entries(
    baustelle_id: int = Query(..., description="Baustelle ID to filter entries"),
    q: str = Query("", description="Search query for description or position number"),
    active_only: bool = True,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search LV entries for a specific baustelle (for autocomplete)
    Always includes "Freitext" entry if exists
    """
    query = db.query(LeistungsverzeichnisEntry).filter(
        LeistungsverzeichnisEntry.baustelle_id == baustelle_id
    )

    if active_only:
        query = query.filter(LeistungsverzeichnisEntry.active == True)

    # Search in description or position number
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                LeistungsverzeichnisEntry.description.ilike(search_term),
                LeistungsverzeichnisEntry.position_number.ilike(search_term)
            )
        )

    # Always show Freitext first if it exists
    query = query.order_by(
        LeistungsverzeichnisEntry.is_freitext.desc(),
        LeistungsverzeichnisEntry.position_number
    )

    entries = query.limit(limit).all()
    return entries


@router.get("", response_model=List[LVEntryResponse])
def get_lv_entries(
    baustelle_id: int = Query(..., description="Baustelle ID to filter entries"),
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all LV entries for a specific baustelle
    """
    query = db.query(LeistungsverzeichnisEntry).filter(
        LeistungsverzeichnisEntry.baustelle_id == baustelle_id
    )

    if active_only:
        query = query.filter(LeistungsverzeichnisEntry.active == True)

    query = query.order_by(LeistungsverzeichnisEntry.position_number)

    entries = query.all()
    return entries


@router.get("/{lv_id}", response_model=LVEntryResponse)
def get_lv_entry(
    lv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific LV entry by ID
    """
    entry = db.query(LeistungsverzeichnisEntry).filter(
        LeistungsverzeichnisEntry.id == lv_id
    ).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LV entry not found"
        )

    return entry


@router.post("", response_model=LVEntryResponse, status_code=status.HTTP_201_CREATED)
def create_lv_entry(
    entry: LVEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new LV entry (admin only in production)
    """
    new_entry = LeistungsverzeichnisEntry(**entry.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry
