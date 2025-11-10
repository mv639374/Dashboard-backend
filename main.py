from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logger import setup_logger, log_app_startup, log_app_shutdown
from app.routers.analytics_router import router as analytics_router

# Setup logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    log_app_startup()
    yield
    # Shutdown
    log_app_shutdown()


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers directly (without the api_router wrapper to avoid double prefix)
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return JSONResponse(
        content={
            "message": "Welcome to AEO/GEO Analytics API",
            "version": settings.API_VERSION,
            "status": "operational",
            "docs": "/docs"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "message": "Backend is running smoothly! 🚀"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
