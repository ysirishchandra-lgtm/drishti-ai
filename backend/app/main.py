"""DRISHTI-AI FastAPI Application Entry Point.

Project: DRISHTI-AI
Team: SPARK
Purpose: Explainable AI-based diabetic retinopathy screening support for rural India.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os
from typing import List

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api import api_v1_router
from app.database import init_db
from app.schemas.screening import ErrorResponse, HealthResponse
from app.services.model_service import model_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("drishti.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to run startup and shutdown tasks."""
    logger.info("Initializing DRISHTI-AI backend services and database schema...")
    init_db()
    logger.info(f"Database schema initialized. AI model status: {model_service.get_status()}")
    yield
    logger.info("Shutting down DRISHTI-AI backend services...")


app = FastAPI(
    title="DRISHTI-AI API",
    description=(
        "Explainable AI-based diabetic retinopathy screening support backend for rural India. "
        "Built for Team SPARK. Designed for primary health worker decision-support."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration strictly allowing local frontend development servers
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check & AI model availability",
    tags=["System"]
)
async def health_check():
    """Verify backend operational status, versioning, and AI model readiness.

    Reports 'not_configured' for the model until verified weights are supplied.
    """
    model_meta = model_service.get_metadata()
    return HealthResponse(
        status="ok",
        project="DRISHTI-AI",
        version=__version__,
        model_status=model_meta["model_status"],
        model_name=model_meta["model_name"],
        supported_classes=model_meta["supported_classes"],
        timestamp=datetime.now(timezone.utc)
    )


# Include API v1 Router
app.include_router(api_v1_router)


# Global exception handler to prevent path or stack trace leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact system support.",
            "code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# Mount static frontend assets if available (prefer production dist if built)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

target_static_dir = frontend_dist if (os.path.isdir(frontend_dist) and os.path.isfile(os.path.join(frontend_dist, "index.html"))) else frontend_dir

if os.path.isdir(target_static_dir) and os.path.isfile(os.path.join(target_static_dir, "index.html")):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=target_static_dir, html=True), name="frontend")
