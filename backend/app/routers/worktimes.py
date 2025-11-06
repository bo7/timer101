"""
Worktimes router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.worktime import Worktime
from ..models.customer import Customer
from ..models.baustelle import Baustelle
from ..models.leistungsverzeichnis import LeistungsverzeichnisEntry
from ..schemas.worktime import WorktimeCreate, WorktimeUpdate, WorktimeResponse

router = APIRouter(prefix="/api/worktimes", tags=["worktimes"])


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
        query = query.filter(Worktime.date == date_filter)

    worktimes = query.order_by(Worktime.date.desc(), Worktime.created_at.desc()).offset(skip).limit(limit).all()

    # Enrich with related data
    result = []
    for wt in worktimes:
        wt_dict = {
            "id": wt.id,
            "user_id": wt.user_id,
            "customer_id": wt.customer_id,
            "baustelle_id": wt.baustelle_id,
            "lv_entry_id": wt.lv_entry_id,
            "date": wt.date,
            "worked_hours": wt.worked_hours,
            "freitext_description": wt.freitext_description,
            "processed": wt.processed,
            "created_at": wt.created_at,
            "updated_at": wt.updated_at,
            "customer_name": wt.customer.name if wt.customer else None,
            "baustelle_name": wt.baustelle.name if wt.baustelle else None,
            "lv_position_number": wt.lv_entry.position_number if wt.lv_entry else None,
            "lv_description": wt.lv_entry.description if wt.lv_entry else None,
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
        "baustelle_name": worktime.baustelle.name if worktime.baustelle else None,
        "lv_position_number": worktime.lv_entry.position_number if worktime.lv_entry else None,
        "lv_description": worktime.lv_entry.description if worktime.lv_entry else None,
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

    # Verify baustelle exists and belongs to customer
    baustelle = db.query(Baustelle).filter(Baustelle.id == worktime.baustelle_id).first()
    if not baustelle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baustelle not found"
        )
    if baustelle.customer_id != worktime.customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Baustelle does not belong to the selected customer"
        )

    # Verify LV entry if provided
    if worktime.lv_entry_id:
        lv_entry = db.query(LeistungsverzeichnisEntry).filter(
            LeistungsverzeichnisEntry.id == worktime.lv_entry_id
        ).first()
        if not lv_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LV entry not found"
            )
        if lv_entry.baustelle_id != worktime.baustelle_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LV entry does not belong to the selected baustelle"
            )

    # Create worktime entry
    db_worktime = Worktime(
        user_id=current_user.id,
        customer_id=worktime.customer_id,
        baustelle_id=worktime.baustelle_id,
        lv_entry_id=worktime.lv_entry_id,
        date=worktime.date,
        worked_hours=worktime.worked_hours,
        freitext_description=worktime.freitext_description,
        processed=False
    )

    db.add(db_worktime)
    db.commit()
    db.refresh(db_worktime)

    # Enrich with related data
    wt_dict = {
        **db_worktime.__dict__,
        "customer_name": db_worktime.customer.name,
        "baustelle_name": db_worktime.baustelle.name,
        "lv_position_number": db_worktime.lv_entry.position_number if db_worktime.lv_entry else None,
        "lv_description": db_worktime.lv_entry.description if db_worktime.lv_entry else None,
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

    # Verify baustelle if being updated
    if 'baustelle_id' in update_data:
        baustelle = db.query(Baustelle).filter(Baustelle.id == update_data['baustelle_id']).first()
        if not baustelle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Baustelle not found"
            )
        if 'customer_id' in update_data and baustelle.customer_id != update_data['customer_id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baustelle does not belong to the selected customer"
            )

    # Verify LV entry if being updated
    if 'lv_entry_id' in update_data and update_data['lv_entry_id'] is not None:
        lv_entry = db.query(LeistungsverzeichnisEntry).filter(
            LeistungsverzeichnisEntry.id == update_data['lv_entry_id']
        ).first()
        if not lv_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LV entry not found"
            )

    for field, value in update_data.items():
        setattr(db_worktime, field, value)

    db.commit()
    db.refresh(db_worktime)

    # Enrich with related data
    wt_dict = {
        **db_worktime.__dict__,
        "customer_name": db_worktime.customer.name,
        "baustelle_name": db_worktime.baustelle.name,
        "lv_position_number": db_worktime.lv_entry.position_number if db_worktime.lv_entry else None,
        "lv_description": db_worktime.lv_entry.description if db_worktime.lv_entry else None,
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
