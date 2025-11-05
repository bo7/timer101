"""
FastAPI main application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import init_db
from .routers import (
    auth_router,
    customers_router,
    locations_router,
    worktimes_router,
    admin_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - modern FastAPI approach"""
    # Startup
    init_db()
    yield
    # Shutdown (cleanup if needed)


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Zeit Erfassung API - Time Tracking System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
app.include_router(locations_router)
app.include_router(worktimes_router)
app.include_router(admin_router)


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
