"""
API routers
"""
from .auth import router as auth_router
from .customers import router as customers_router
from .baustellen import router as baustellen_router
from .leistungsverzeichnis import router as lv_router
from .worktimes import router as worktimes_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "customers_router",
    "baustellen_router",
    "lv_router",
    "worktimes_router",
    "admin_router"
]
