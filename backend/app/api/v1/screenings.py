"""Screenings API Router for DRISHTI-AI v1."""
from datetime import datetime, timezone
import logging
import os
import uuid
from typing import Optional
from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile, status

from app.database import (
    get_screening,
    init_db,
    list_screenings,
    save_screening,
    update_screening_analysis,
)
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
    delete_screening_image,
    read_gradcam_image,
    read_screening_image,
    save_gradcam_image,
    save_screening_image,
)
from app.services.model_service import ModelServiceUnavailableError, model_service

logger = logging.getLogger("drishti.screenings")

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

    extract technical usability heuristics, securely retain image for analysis,
    and generate a persistent screening record.
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
    except Exception:
        # Prevent stack trace leakage
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to process uploaded image file. Please verify it is a valid, uncorrupted image."
        )

    # Generate a unique screening reference ID
    screening_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    # Secure local storage: persist image bytes for analysis pipeline
    try:
        save_screening_image(screening_id, content, val_result.format)
    except Exception as exc:
        logger.error(f"Failed to save image bytes for screening {screening_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store uploaded image for processing."
        )

    # Prepare screening metadata record
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

    # Persist in SQLite with rollback on failure
    try:
        save_screening(record)
    except Exception as exc:
        delete_screening_image(screening_id)
        logger.error(f"Failed to persist screening record {screening_id} in SQLite: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database persistence error while recording screening metadata."
        )

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
            model_status=model_service.get_status(),
            analysis_available=False,
            prediction=None,
            confidence=None,
            class_probabilities=None,
            gradcam_available=False,
            gradcam_url=None,
            message="Diabetic Retinopathy AI model is not configured. Awaiting verified model weights and evaluation from AI lead (Rudra)."
        )

    # Read image bytes from local secure storage
    image_bytes = read_screening_image(screening_id)
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stored image for screening record '{screening_id}' not found. Please re-upload the image."
        )

    # Execute real model inference
    try:
        inf_result = model_service.predict(image_bytes)
    except ModelServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message
        )
    except Exception as exc:
        logger.error(f"Inference error for screening {screening_id}: {exc}", exc_info=True)
        # Update record with error status
        update_screening_analysis(screening_id, {
            "model_status": "error",
            "analysis_available": False,
            "prediction": None,
            "confidence": None,
            "class_probabilities": None,
            "gradcam_available": False,
            "notes": "Model inference failed during processing."
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model inference failed to process the image."
        )

    # Generate genuine Grad-CAM heatmap visualization if supported
    gradcam_available = False
    gradcam_url = None
    if inf_result.get("gradcam_available"):
        try:
            gradcam_bytes = model_service.generate_gradcam(
                image_bytes=image_bytes,
                target_class=inf_result.get("predicted_index")
            )
            if gradcam_bytes:
                save_gradcam_image(screening_id, gradcam_bytes)
                gradcam_available = True
                gradcam_url = f"/api/v1/screenings/{screening_id}/gradcam"
        except Exception as cam_exc:
            logger.warning(f"Grad-CAM generation failed for screening {screening_id}: {cam_exc}")
            gradcam_available = False
            gradcam_url = None

    # Persist analysis results against existing SQLite record without duplicating
    update_screening_analysis(screening_id, {
        "model_status": "ready",
        "analysis_available": True,
        "prediction": inf_result["prediction"],
        "confidence": inf_result["confidence"],
        "class_probabilities": inf_result["class_probabilities"],
        "gradcam_available": gradcam_available,
        "notes": None
    })

    return ScreeningAnalyzeResponse(
        screening_id=screening_id,
        model_status="ready",
        analysis_available=True,
        prediction=inf_result["prediction"],
        confidence=inf_result["confidence"],
        class_probabilities=inf_result["class_probabilities"],
        gradcam_available=gradcam_available,
        gradcam_url=gradcam_url,
        message="Model inference completed successfully using verified DR classifier."
    )


@router.get(
    "/{screening_id}/gradcam",
    summary="Retrieve generated Grad-CAM heatmap overlay image"
)
async def get_screening_gradcam(screening_id: str):
    """Serve the genuine Grad-CAM activation heatmap overlay as a PNG image."""
    record = get_screening(screening_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening record '{screening_id}' not found."
        )

    gradcam_bytes = read_gradcam_image(screening_id)
    if not gradcam_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grad-CAM visualization is not available for this screening."
        )

    return Response(
        content=gradcam_bytes,
        media_type="image/png",
        headers={"Cache-Control": "private, max-age=3600"}
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
