"""
Admin dashboard and reports endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from calendar import monthrange

from ..core.database import get_db
from ..core.security import get_current_admin_user
from ..models.user import User
from ..models.customer import Customer
from ..models.baustelle import Baustelle
from ..models.worktime import Worktime
from ..models.baustelle_rate import BaustelleRate
from ..models.special_days import SpecialDay
from ..schemas.admin import (
    DashboardStats,
    UserStatsDetail,
    BaustelleCostAnalysis,
    CompletenessCheck,
    MonthlyReport
)

router = APIRouter(prefix="/admin/api/dashboard", tags=["Admin - Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get dashboard statistics (admin only)"""
    # Get current month
    today = date.today()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, monthrange(today.year, today.month)[1])

    # Count users
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.deleted_at.is_(None)).count()
    deleted_users = db.query(User).filter(User.deleted_at.isnot(None)).count()

    # Count customers
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.active == True).count()

    # Count baustellen
    total_baustellen = db.query(Baustelle).count()
    active_baustellen = db.query(Baustelle).filter(Baustelle.active == True).count()

    # Count worktimes this month
    worktimes_this_month = db.query(Worktime).filter(
        and_(
            Worktime.date >= first_day,
            Worktime.date <= last_day
        )
    ).count()

    # Sum hours this month
    total_hours = db.query(func.sum(Worktime.worked_hours)).filter(
        and_(
            Worktime.date >= first_day,
            Worktime.date <= last_day
        )
    ).scalar() or 0

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        deleted_users=deleted_users,
        total_customers=total_customers,
        active_customers=active_customers,
        total_baustellen=total_baustellen,
        active_baustellen=active_baustellen,
        total_worktimes_this_month=worktimes_this_month,
        total_hours_this_month=total_hours
    )


@router.get("/user-stats", response_model=List[UserStatsDetail])
def get_user_stats(
    year: int,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get detailed user statistics for a period (admin only)"""
    # Build date filters
    if month:
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
    else:
        first_day = date(year, 1, 1)
        last_day = date(year, 12, 31)

    # Get all active users
    users = db.query(User).filter(User.deleted_at.is_(None)).all()

    user_stats = []
    for user in users:
        # Count worktimes
        worktimes = db.query(Worktime).filter(
            and_(
                Worktime.user_id == user.id,
                Worktime.date >= first_day,
                Worktime.date <= last_day
            )
        ).all()

        total_hours = sum(wt.worked_hours for wt in worktimes)
        unique_dates = len(set(wt.date for wt in worktimes))

        # Count special days
        special_days_count = db.query(SpecialDay).filter(
            and_(
                SpecialDay.user_id == user.id,
                SpecialDay.date >= first_day,
                SpecialDay.date <= last_day
            )
        ).count()

        user_stats.append(UserStatsDetail(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            employee_type=user.employee_type,
            total_hours=total_hours,
            total_days_worked=unique_dates,
            total_special_days=special_days_count
        ))

    return user_stats


@router.get("/baustelle-costs", response_model=List[BaustelleCostAnalysis])
def get_baustelle_costs(
    year: int,
    month: Optional[int] = None,
    baustelle_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get cost analysis per baustelle (admin only)"""
    # Build date filters
    if month:
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
    else:
        first_day = date(year, 1, 1)
        last_day = date(year, 12, 31)

    # Get baustellen
    query = db.query(Baustelle)
    if baustelle_id:
        query = query.filter(Baustelle.id == baustelle_id)
    baustellen = query.all()

    cost_analyses = []
    for baustelle in baustellen:
        # Get worktimes for this baustelle
        worktimes = db.query(Worktime, User).join(
            User, Worktime.user_id == User.id
        ).filter(
            and_(
                Worktime.baustelle_id == baustelle.id,
                Worktime.date >= first_day,
                Worktime.date <= last_day
            )
        ).all()

        if not worktimes:
            continue

        total_hours = 0
        cost_breakdown = {}

        for worktime, user in worktimes:
            employee_type = user.employee_type or "Geselle"  # Default to Geselle
            total_hours += worktime.worked_hours

            # Get rate for this employee type on this date
            rate = db.query(BaustelleRate).filter(
                and_(
                    BaustelleRate.baustelle_id == baustelle.id,
                    BaustelleRate.employee_type == employee_type,
                    BaustelleRate.valid_from <= worktime.date,
                    or_(
                        BaustelleRate.valid_to.is_(None),
                        BaustelleRate.valid_to >= worktime.date
                    )
                )
            ).first()

            if rate:
                hourly_rate = rate.hourly_rate
            else:
                # Default rates if no rate found
                hourly_rate = Decimal("40.00")

            cost = Decimal(worktime.worked_hours) * hourly_rate

            if employee_type not in cost_breakdown:
                cost_breakdown[employee_type] = Decimal("0.00")
            cost_breakdown[employee_type] += cost

        total_cost = sum(cost_breakdown.values())

        # Get customer name
        customer = db.query(Customer).filter(Customer.id == baustelle.customer_id).first()

        cost_analyses.append(BaustelleCostAnalysis(
            baustelle_id=baustelle.id,
            baustelle_name=baustelle.name,
            customer_name=customer.name if customer else "Unknown",
            total_hours=total_hours,
            cost_breakdown=cost_breakdown,
            total_cost=total_cost
        ))

    return cost_analyses


@router.get("/completeness-check", response_model=List[CompletenessCheck])
def check_completeness(
    year: int,
    month: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Check for missing time entries (admin only)"""
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Get users to check
    query = db.query(User).filter(User.deleted_at.is_(None))
    if user_id:
        query = query.filter(User.id == user_id)
    users = query.all()

    completeness_checks = []

    for user in users:
        # Check each day in the month
        current_date = first_day
        while current_date <= last_day:
            is_workday = current_date.weekday() < 5  # Monday=0, Friday=4

            # Check if there's a worktime entry
            has_worktime = db.query(Worktime).filter(
                and_(
                    Worktime.user_id == user.id,
                    Worktime.date == current_date
                )
            ).first() is not None

            # Check if there's a special day entry
            has_special_day = db.query(SpecialDay).filter(
                and_(
                    SpecialDay.user_id == user.id,
                    SpecialDay.date == current_date
                )
            ).first() is not None

            # Determine status
            if not is_workday:
                status = "weekend"
            elif has_worktime or has_special_day:
                status = "complete"
            else:
                status = "missing"

            # Only include missing entries or current/future dates
            if status == "missing" or current_date >= date.today():
                completeness_checks.append(CompletenessCheck(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    date=current_date,
                    is_workday=is_workday,
                    has_worktime=has_worktime,
                    has_special_day=has_special_day,
                    status=status
                ))

            current_date += timedelta(days=1)

    return completeness_checks


@router.get("/monthly-report", response_model=MonthlyReport)
def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get comprehensive monthly report (admin only)"""
    # Get user stats
    user_stats = get_user_stats(year=year, month=month, db=db, current_admin=current_admin)

    # Get baustelle costs
    baustelle_costs = get_baustelle_costs(year=year, month=month, db=db, current_admin=current_admin)

    # Get completeness
    completeness = check_completeness(year=year, month=month, db=db, current_admin=current_admin)

    # Calculate totals
    total_hours = sum(stat.total_hours for stat in user_stats)
    total_cost = sum(cost.total_cost for cost in baustelle_costs)

    return MonthlyReport(
        month=f"{year}-{month:02d}",
        total_hours=total_hours,
        total_cost=total_cost,
        user_stats=user_stats,
        baustelle_costs=baustelle_costs,
        completeness=[c for c in completeness if c.status == "missing"]
    )
