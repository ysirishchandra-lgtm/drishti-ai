"""API v1 Router package."""
from fastapi import APIRouter
from app.api.v1.screenings import router as screenings_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(screenings_router)

__all__ = ["api_v1_router"]
