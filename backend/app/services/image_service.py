"""Image validation and usability heuristic services for DRISHTI-AI.

IMPORTANT CLINICAL NOTE:
The heuristic metrics computed here (mean brightness, contrast range, dimension sanity)
are technical checks intended solely to filter out corrupted, blank, or improperly formatted
uploads. They do NOT constitute or guarantee a clinically validated retinal-image quality evaluation.
"""
from dataclasses import dataclass
import io
import math
import os
from typing import List, Optional, Tuple
from PIL import Image, ImageOps, ImageStat

from app.schemas.screening import ImageQualityMetrics


# Maximum allowed upload size: 15 megabytes
MAX_IMAGE_SIZE_BYTES: int = 15 * 1024 * 1024
# Supported formats and their permitted mime types
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}

# Dimension constraints to reject tiny/corrupted thumbnails or extreme files
MIN_DIMENSION_PX: int = 200
MAX_DIMENSION_PX: int = 10000

# Magic number signatures
MAGIC_NUMBERS = [
    (b"\xff\xd8\xff", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"RIFF", "WEBP"),  # Note: bytes 8-11 are WEBP
]


class ImageValidationError(Exception):
    """Raised when an uploaded image fails validation."""
    def __init__(self, message: str, code: str = "IMAGE_VALIDATION_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


@dataclass
class ValidationResult:
    """Encapsulates validated image metadata and usability heuristics."""
    is_valid: bool
    format: str
    mime_type: str
    width: int
    height: int
    file_size_bytes: int
    quality_metrics: ImageQualityMetrics
    image_bytes: bytes


class ImageValidationService:
    """Modular service for validating image integrity, format, and technical usability."""

    @staticmethod
    def inspect_magic_bytes(header: bytes) -> Optional[str]:
        """Detect true format from magic byte signatures without trusting user-supplied headers."""
        if header.startswith(b"\xff\xd8\xff"):
            return "JPEG"
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return "PNG"
        if header.startswith(b"RIFF") and len(header) >= 12 and header[8:12] == b"WEBP":
            return "WEBP"
        return None

    @classmethod
    def validate_and_decode(
        cls,
        image_bytes: bytes,
        declared_filename: str,
        declared_content_type: Optional[str] = None
    ) -> ValidationResult:
        """Thoroughly inspect, decode, and extract usability metrics from image bytes.

        Raises:
            ImageValidationError if the image exceeds size, is corrupted, or has an unsupported format.
        """
        # 1. Enforce file size limits
        size_bytes = len(image_bytes)
        if size_bytes == 0:
            raise ImageValidationError("Uploaded file is empty (0 bytes).", code="EMPTY_FILE", status_code=400)
        if size_bytes > MAX_IMAGE_SIZE_BYTES:
            max_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
            raise ImageValidationError(
                f"File size ({size_bytes / (1024 * 1024):.2f} MB) exceeds maximum allowed limit ({max_mb:.0f} MB).",
                code="FILE_TOO_LARGE",
                status_code=413
            )

        # 2. Inspect magic numbers to verify genuine binary signature
        detected_format = cls.inspect_magic_bytes(image_bytes[:16])
        if not detected_format or detected_format not in ALLOWED_FORMATS:
            raise ImageValidationError(
                "Unsupported or unrecognized file format. Allowed formats are JPEG, PNG, and WebP.",
                code="UNSUPPORTED_FORMAT",
                status_code=415
            )

        # 3. Decode image and verify integrity using Pillow
        try:
            # First pass: Pillow verify
            stream = io.BytesIO(image_bytes)
            img = Image.open(stream)
            img.verify()
        except Exception:
            raise ImageValidationError(
                "Uploaded file is corrupted or could not be decoded as a valid image.",
                code="CORRUPT_IMAGE",
                status_code=400
            )

        # Second pass: Full decode to ensure pixel arrays and metadata can be loaded
        try:
            stream = io.BytesIO(image_bytes)
            img = Image.open(stream)
            img.load()  # Force load pixel data
        except Exception:
            raise ImageValidationError(
                "Failed to render image pixel data. File may be truncated or corrupted.",
                code="DECODE_FAILURE",
                status_code=400
            )

        width, height = img.size
        actual_format = (img.format or detected_format).upper()

        # 4. Dimension checks
        if width < MIN_DIMENSION_PX or height < MIN_DIMENSION_PX:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height} px) are smaller than required minimum ({MIN_DIMENSION_PX}x{MIN_DIMENSION_PX} px).",
                code="DIMENSIONS_TOO_SMALL",
                status_code=400
            )

        if width > MAX_DIMENSION_PX or height > MAX_DIMENSION_PX:
            raise ImageValidationError(
                f"Image dimensions ({width}x{height} px) exceed maximum permitted size ({MAX_DIMENSION_PX} px).",
                code="DIMENSIONS_TOO_LARGE",
                status_code=400
            )

        # 5. Extract technical usability heuristics (non-clinical)
        quality_metrics = cls._compute_quality_heuristics(img, width, height, actual_format)

        mime_type = "image/jpeg"
        if actual_format == "PNG":
            mime_type = "image/png"
        elif actual_format == "WEBP":
            mime_type = "image/webp"

        return ValidationResult(
            is_valid=True,
            format=actual_format,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size_bytes=size_bytes,
            quality_metrics=quality_metrics,
            image_bytes=image_bytes
        )

    @classmethod
    def _compute_quality_heuristics(
        cls,
        img: Image.Image,
        width: int,
        height: int,
        img_format: str
    ) -> ImageQualityMetrics:
        """Compute preliminary image metrics: brightness, contrast standard deviation, and aspect ratio."""
        rejection_reasons: List[str] = []
        aspect_ratio = round(width / float(height), 3) if height > 0 else 1.0

        # Convert to grayscale for consistent illumination/contrast measurement
        gray_img = ImageOps.grayscale(img)
        stat = ImageStat.Stat(gray_img)
        mean_brightness = round(float(stat.mean[0]), 2)
        contrast_std = round(float(stat.stddev[0]), 2)

        # Preliminary heuristic thresholds
        # Note: Extremely dark (< 15) or overexposed (> 240) images indicate severe illumination issues
        if mean_brightness < 15:
            rejection_reasons.append("Severe underexposure / very dark image detected.")
        elif mean_brightness > 240:
            rejection_reasons.append("Severe overexposure / washed out image detected.")

        if contrast_std < 10:
            rejection_reasons.append("Extremely low contrast / uniform image detected.")

        if rejection_reasons:
            heuristic_status = "borderline" if len(rejection_reasons) == 1 else "unusable"
        else:
            heuristic_status = "acceptable"

        channels = 1 if img.mode == "L" else (4 if img.mode == "RGBA" else 3)

        return ImageQualityMetrics(
            width=width,
            height=height,
            format=img_format,
            channels=channels,
            aspect_ratio=aspect_ratio,
            mean_brightness=mean_brightness,
            contrast_std=contrast_std,
            heuristic_status=heuristic_status,
            rejection_reasons=rejection_reasons,
            disclaimer="Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation."
        )
