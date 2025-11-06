"""
API routers
"""
from .auth import router as auth_router
from .customers import router as customers_router
from .baustellen import router as baustellen_router
from .leistungsverzeichnis import router as lv_router
from .worktimes import router as worktimes_router
from .admin import router as admin_router
from .admin_users import router as admin_users_router
from .admin_rates import router as admin_rates_router
from .admin_special_days import router as admin_special_days_router
from .admin_dashboard import router as admin_dashboard_router
from .uploads import router as uploads_router

__all__ = [
    "auth_router",
    "customers_router",
    "baustellen_router",
    "lv_router",
    "worktimes_router",
    "admin_router",
    "admin_users_router",
    "admin_rates_router",
    "admin_special_days_router",
    "admin_dashboard_router",
    "uploads_router"
]
