from fastapi import APIRouter
from app.routers import analytics_router, insights_router
from app.routers import additional_router

# Create a main router that includes all sub-routers
api_router = APIRouter()

# Include analytics router
api_router.include_router(
    analytics_router.router,
    prefix="/analytics",
    tags=["Analytics"]
)

# Include insights router
api_router.include_router(
    insights_router.router,
    prefix="/insights",
    tags=["Insights"]
)

# Include Additional router
api_router.include_router(
    additional_router.router,
    prefix="/additional",
    tags=["Additional"]
)

# Add more routers here as needed
# api_router.include_router(other_router.router, prefix="/other", tags=["Other"])
