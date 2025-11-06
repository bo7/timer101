"""
Admin-specific schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_users: int
    active_users: int
    deleted_users: int
    total_customers: int
    active_customers: int
    total_baustellen: int
    active_baustellen: int
    total_worktimes_this_month: int
    total_hours_this_month: int


class UserStatsDetail(BaseModel):
    """Detailed user statistics"""
    user_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_type: Optional[str] = None
    total_hours: int
    total_days_worked: int
    total_special_days: int


class BaustelleCostAnalysis(BaseModel):
    """Cost analysis for a baustelle"""
    baustelle_id: int
    baustelle_name: str
    customer_name: str
    total_hours: int
    cost_breakdown: Dict[str, Decimal]  # {"Geselle": 1200.00, "Meister": 3250.00}
    total_cost: Decimal


class CompletenessCheck(BaseModel):
    """Check for missing time entries"""
    user_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date: date
    is_workday: bool
    has_worktime: bool
    has_special_day: bool
    status: str  # "complete", "missing", "weekend"


class MonthlyReport(BaseModel):
    """Monthly report summary"""
    month: str  # "2025-11"
    total_hours: int
    total_cost: Decimal
    user_stats: List[UserStatsDetail]
    baustelle_costs: List[BaustelleCostAnalysis]
    completeness: List[CompletenessCheck]
