"""
Admin user management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_admin_user, get_password_hash
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/admin/api/users", tags=["Admin - Users"])


@router.get("", response_model=List[UserResponse])
def get_all_users(
    include_deleted: bool = False,
    employee_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    query = db.query(User)

    if not include_deleted:
        query = query.filter(User.deleted_at.is_(None))

    if employee_type:
        query = query.filter(User.employee_type == employee_type)

    return query.order_by(User.username).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new user (admin only)"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Validate employee_type
    if user_data.employee_type and user_data.employee_type not in ["Geselle", "Meister", "Polier"]:
        raise HTTPException(status_code=400, detail="Invalid employee_type")

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_admin=user_data.is_admin,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        employee_type=user_data.employee_type
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is soft deleted
    if user.deleted_at:
        raise HTTPException(status_code=400, detail="Cannot update deleted user")

    # Update fields if provided
    if user_data.username is not None:
        # Check if new username already exists
        existing = db.query(User).filter(
            and_(User.username == user_data.username, User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_data.username

    if user_data.email is not None:
        # Check if new email already exists
        existing = db.query(User).filter(
            and_(User.email == user_data.email, User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data.email

    if user_data.password is not None:
        user.password_hash = get_password_hash(user_data.password)

    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin

    if user_data.first_name is not None:
        user.first_name = user_data.first_name

    if user_data.last_name is not None:
        user.last_name = user_data.last_name

    if user_data.employee_type is not None:
        if user_data.employee_type and user_data.employee_type not in ["Geselle", "Meister", "Polier"]:
            raise HTTPException(status_code=400, detail="Invalid employee_type")
        user.employee_type = user_data.employee_type

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Soft delete a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.deleted_at:
        raise HTTPException(status_code=400, detail="User already deleted")

    # Don't allow deleting yourself
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    # Soft delete
    user.deleted_at = datetime.utcnow()
    user.deleted_by = current_admin.id

    db.commit()

    return None


@router.post("/{user_id}/restore", response_model=UserResponse)
def restore_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Restore a soft-deleted user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.deleted_at:
        raise HTTPException(status_code=400, detail="User is not deleted")

    # Restore
    user.deleted_at = None
    user.deleted_by = None

    db.commit()
    db.refresh(user)

    return user
