"""Pydantic schemas for DRISHTI-AI backend API contracts."""
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health and AI runtime availability."""
    status: str = Field(default="ok", description="Overall backend service status")
    project: str = Field(default="DRISHTI-AI", description="Project identifier")
    version: str = Field(default="0.1.0", description="API semantic version")
    model_status: str = Field(
        default="not_configured",
        description="Current AI model readiness: 'not_configured', 'ready', or 'error'"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Identified model checkpoint name if configured"
    )
    supported_classes: List[str] = Field(
        default_factory=lambda: ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"],
        description="Target DR grading classes (to be validated against model weights)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current server UTC timestamp"
    )


class ImageQualityMetrics(BaseModel):
    """Preliminary technical image usability metrics (non-clinical heuristics)."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    format: str = Field(..., description="Detected image format (JPEG, PNG, WEBP)")
    channels: int = Field(default=3, description="Color channels")
    aspect_ratio: float = Field(..., description="Aspect ratio (width / height)")
    mean_brightness: float = Field(..., description="Estimated mean brightness (0-255)")
    contrast_std: float = Field(..., description="Standard deviation of pixel intensities")
    heuristic_status: str = Field(
        ...,
        description="Heuristic usability status: 'acceptable', 'borderline', 'unusable'"
    )
    rejection_reasons: List[str] = Field(
        default_factory=list,
        description="List of flags if image failed basic usability heuristic thresholds"
    )
    disclaimer: str = Field(
        default="Preliminary technical usability heuristics only. Not a clinically validated image quality certification.",
        description="Regulatory / clinical scope limitation"
    )


class ScreeningUploadResponse(BaseModel):
    """Response returned upon successful upload and image decoding."""
    screening_id: str = Field(..., description="Unique screening reference identifier (UUID4)")
    created_at: datetime = Field(..., description="Creation timestamp in UTC")
    file_name: str = Field(..., description="Sanitized client filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="Verified MIME type")
    validation_passed: bool = Field(..., description="Whether structural validation succeeded")
    image_quality: ImageQualityMetrics = Field(..., description="Extracted heuristic metrics")
    model_status: str = Field(default="not_configured", description="State of AI model")
    human_review_status: str = Field(default="pending", description="Status of clinical review")
    follow_up_status: str = Field(default="none", description="Referral / follow-up action status")
    message: str = Field(..., description="Human-readable status summary")


class ScreeningAnalyzeResponse(BaseModel):
    """Response returned when triggering AI analysis for a screening record."""
    screening_id: str = Field(..., description="Screening identifier")
    model_status: str = Field(..., description="Current status of AI model")
    analysis_available: bool = Field(
        default=False,
        description="True only if genuine model inference was performed"
    )
    prediction: Optional[str] = Field(
        default=None,
        description="Predicted DR grade (omitted when model is not configured)"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Predicted class probability (omitted when model is not configured)"
    )
    class_probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Full distribution over DR classes"
    )
    gradcam_available: bool = Field(
        default=False,
        description="Whether Grad-CAM explanation heatmap was generated"
    )
    gradcam_url: Optional[str] = Field(
        default=None,
        description="Path or URL to Grad-CAM heatmap visualization if generated"
    )
    message: str = Field(..., description="Explanation of analysis status or absence of model")


class ScreeningRecord(BaseModel):
    """Full persistent screening record."""
    screening_id: str
    created_at: datetime
    file_name: str
    file_size_bytes: int
    mime_type: str
    validation_passed: bool
    image_quality: ImageQualityMetrics
    model_status: str = "not_configured"
    analysis_available: bool = False
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    class_probabilities: Optional[Dict[str, float]] = None
    gradcam_available: bool = False
    human_review_status: str = "pending"
    follow_up_status: str = "none"
    notes: Optional[str] = None


class ScreeningListResponse(BaseModel):
    """Paginated list of historical screening records."""
    total: int = Field(..., description="Total count of records")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of records per page")
    items: List[ScreeningRecord] = Field(..., description="List of screening records")


class ErrorResponse(BaseModel):
    """Consistent API error format."""
    detail: str = Field(..., description="Detailed description of the error")
    code: str = Field(..., description="Machine-readable error code")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error timestamp in UTC"
    )
