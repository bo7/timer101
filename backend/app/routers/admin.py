"""
Admin router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models.user import User
from ..models.worktime import Worktime
from ..schemas.user import UserResponse
from ..schemas.worktime import WorktimeResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all users (admin only)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/worktimes/{worktime_id}/process", response_model=WorktimeResponse)
def process_worktime(
    worktime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Mark a worktime entry as processed (admin only)
    """
    worktime = db.query(Worktime).filter(Worktime.id == worktime_id).first()

    if not worktime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worktime entry not found"
        )

    worktime.processed = True
    db.commit()
    db.refresh(worktime)

    # Enrich with related data
    wt_dict = {
        **worktime.__dict__,
        "customer_name": worktime.customer.name if worktime.customer else None,
        "baustelle_name": worktime.baustelle.name if worktime.baustelle else None,
        "lv_position_number": worktime.lv_entry.position_number if worktime.lv_entry else None,
        "lv_description": worktime.lv_entry.description if worktime.lv_entry else None,
        "username": worktime.user.username if worktime.user else None
    }

    return WorktimeResponse(**wt_dict)


@router.put("/worktimes/{worktime_id}/unprocess", response_model=WorktimeResponse)
def unprocess_worktime(
    worktime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Mark a worktime entry as not processed (admin only)
    """
    worktime = db.query(Worktime).filter(Worktime.id == worktime_id).first()

    if not worktime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worktime entry not found"
        )

    worktime.processed = False
    db.commit()
    db.refresh(worktime)

    # Enrich with related data
    wt_dict = {
        **worktime.__dict__,
        "customer_name": worktime.customer.name if worktime.customer else None,
        "baustelle_name": worktime.baustelle.name if worktime.baustelle else None,
        "lv_position_number": worktime.lv_entry.position_number if worktime.lv_entry else None,
        "lv_description": worktime.lv_entry.description if worktime.lv_entry else None,
        "username": worktime.user.username if worktime.user else None
    }

    return WorktimeResponse(**wt_dict)
