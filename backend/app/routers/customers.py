"""
Customers router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.customer import Customer
from ..schemas.customer import CustomerResponse, CustomerSearch

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all customers (paginated)
    """
    query = db.query(Customer)

    if active_only:
        query = query.filter(Customer.active == True)

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/search", response_model=List[CustomerSearch])
def search_customers(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search customers by name or customer number (AJAX endpoint)
    """
    # Search in name and customer_number (case-insensitive)
    search_pattern = f"%{q}%"
    customers = db.query(Customer).filter(
        Customer.active == True
    ).filter(
        (Customer.name.ilike(search_pattern)) |
        (Customer.customer_number.ilike(search_pattern))
    ).limit(limit).all()

    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific customer by ID
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer
