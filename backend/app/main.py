"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import init_db
from .routers import (
    auth_router,
    customers_router,
    baustellen_router,
    lv_router,
    worktimes_router,
    admin_router
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Zeit Erfassung API - Time Tracking System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(baustellen_router)
app.include_router(lv_router)
app.include_router(worktimes_router)
app.include_router(admin_router)


@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Zeit Erfassung API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
