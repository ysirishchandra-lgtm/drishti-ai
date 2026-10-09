"""Screenings API Router for DRISHTI-AI v1."""
from datetime import datetime, timezone
import os
import uuid
from typing import Optional
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.database import get_screening, init_db, list_screenings, save_screening
from app.schemas.screening import (
    ScreeningAnalyzeResponse,
    ScreeningListResponse,
    ScreeningRecord,
    ScreeningUploadResponse,
)
from app.services.image_service import (
    ImageValidationError,
    ImageValidationService,
    MAX_IMAGE_SIZE_BYTES,
)
from app.services.model_service import ModelServiceUnavailableError, model_service

router = APIRouter(prefix="/screenings", tags=["Screenings"])


@router.post(
    "/upload",
    response_model=ScreeningUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and validate a retinal fundus image"
)
async def upload_screening_image(
    file: UploadFile = File(..., description="Retinal fundus image (JPEG, PNG, or WebP)")
):
    """Accept a retinal image upload, enforce strict format and dimension validations,

    extract technical usability heuristics, and generate a persistent screening record.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    # Read bytes with streaming size guard to prevent memory exhaustion
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded image exceeds maximum allowable limit of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    # Validate image decoding and technical usability heuristics
    try:
        val_result = ImageValidationService.validate_and_decode(
            image_bytes=content,
            declared_filename=file.filename,
            declared_content_type=file.content_type
        )
    except ImageValidationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message
        )
    except Exception as exc:
        # Prevent stack trace leakage
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to process uploaded image file. Please verify it is a valid, uncorrupted image."
        )

    # Generate a unique screening reference ID
    screening_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    # Prepare screening record
    record = {
        "screening_id": screening_id,
        "created_at": created_at.isoformat(),
        "file_name": os.path.basename(file.filename),
        "file_size_bytes": val_result.file_size_bytes,
        "mime_type": val_result.mime_type,
        "validation_passed": True,
        "image_quality": val_result.quality_metrics.model_dump(),
        "model_status": model_service.get_status(),
        "analysis_available": False,
        "prediction": None,
        "confidence": None,
        "class_probabilities": None,
        "gradcam_available": False,
        "human_review_status": "pending",
        "follow_up_status": "none",
        "notes": None,
    }

    # Persist in SQLite
    save_screening(record)

    message = "Image successfully verified and usability heuristics extracted."
    if val_result.quality_metrics.heuristic_status != "acceptable":
        message += " Note: Heuristic flags detected (e.g. contrast/illumination). Clinical technician review suggested."

    return ScreeningUploadResponse(
        screening_id=screening_id,
        created_at=created_at,
        file_name=os.path.basename(file.filename),
        file_size_bytes=val_result.file_size_bytes,
        mime_type=val_result.mime_type,
        validation_passed=True,
        image_quality=val_result.quality_metrics,
        model_status=model_service.get_status(),
        human_review_status="pending",
        follow_up_status="none",
        message=message
    )


@router.post(
    "/{screening_id}/analyze",
    response_model=ScreeningAnalyzeResponse,
    summary="Trigger AI inference for screening record"
)
async def analyze_screening(screening_id: str):
    """Run model inference on screening record if a verified model is loaded.

    If model is not configured, returns clean model-unavailable status without
    fabricating medical predictions.
    """
    record = get_screening(screening_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening record '{screening_id}' not found."
        )

    # Check if AI model is ready
    if not model_service.is_configured():
        return ScreeningAnalyzeResponse(
            screening_id=screening_id,
            model_status="not_configured",
            analysis_available=False,
            prediction=None,
            confidence=None,
            class_probabilities=None,
            gradcam_available=False,
            gradcam_url=None,
            message="Diabetic Retinopathy AI model is not configured. Awaiting verified model weights and evaluation from AI lead (Rudra)."
        )

    # When model is configured:
    try:
        # Stub for future integration when Rudra provides weights
        return ScreeningAnalyzeResponse(
            screening_id=screening_id,
            model_status="ready",
            analysis_available=False,
            message="Model loaded but pipeline execution pending."
        )
    except ModelServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message
        )


@router.get(
    "/{screening_id}",
    response_model=ScreeningRecord,
    summary="Retrieve screening record details"
)
async def get_screening_record(screening_id: str):
    """Fetch screening record details, quality metrics, and analysis status."""
    record = get_screening(screening_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening record '{screening_id}' not found."
        )
    return record


@router.get(
    "",
    response_model=ScreeningListResponse,
    summary="List historical screening records"
)
async def list_screening_records(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page")
):
    """Retrieve paginated list of historical screenings, ordered newest to oldest."""
    total, items = list_screenings(page=page, page_size=page_size)
    return ScreeningListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
