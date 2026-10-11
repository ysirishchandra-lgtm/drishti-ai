"""Comprehensive unit and integration test suite for DRISHTI-AI backend.

Covers:
1. Health endpoint & model status verification
2. Valid image upload & usability heuristic calculation
3. Invalid / non-image file rejection
4. Corrupted image rejection
5. Unsupported format rejection (e.g. GIF)
6. Oversized image rejection (> 15 MB)
7. Screening record retrieval (GET /screenings/{id})
8. Screening history pagination (GET /screenings)
9. Model-unavailable behavior on analysis trigger
10. Consistent error formatting and no stack trace exposure
"""
import io
import os
import tempfile
import pytest
from PIL import Image
from fastapi.testclient import TestClient

# Point test suite to an isolated temporary SQLite database before importing app
temp_dir = tempfile.mkdtemp()
test_db_path = os.path.join(temp_dir, "test_drishti.db")
os.environ["DRISHTI_DB_PATH"] = test_db_path

from app.main import app
from app.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database schema is created for test session."""
    init_db(test_db_path)
    yield
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass


@pytest.fixture
def client():
    """Provide a TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


def create_synthetic_image(width=500, height=500, img_format="JPEG", color=(180, 80, 50)):
    """Helper to generate a safe in-memory synthetic test image without patient data."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=img_format)
    buf.seek(0)
    return buf.getvalue()


# -------------------------------------------------------------
# Test 1: Health Endpoint & Model Status
# -------------------------------------------------------------
def test_health_endpoint(client):
    """GET /health must return ok status, correct project metadata, and model readiness."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "DRISHTI-AI"
    assert data["version"] == "0.1.0"
    assert data["model_status"] in ("ready", "not_configured")
    if data["model_status"] == "ready":
        assert data["model_name"] == "RetinaExplain_AI_v2_final"
    assert "No DR" in data["supported_classes"]
    assert "Proliferative DR" in data["supported_classes"]
    assert "timestamp" in data


# -------------------------------------------------------------
# Test 2: Valid Image Upload (JPEG, PNG, WebP)
# -------------------------------------------------------------
def test_upload_valid_jpeg(client):
    """POST /api/v1/screenings/upload must accept a valid JPEG and compute usability heuristics."""
    jpeg_bytes = create_synthetic_image(width=600, height=600, img_format="JPEG")
    files = {"file": ("test_fundus.jpg", jpeg_bytes, "image/jpeg")}
    
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert "screening_id" in data
    assert data["file_name"] == "test_fundus.jpg"
    assert data["validation_passed"] is True
    assert data["mime_type"] == "image/jpeg"
    assert data["model_status"] in ("ready", "not_configured")
    assert data["human_review_status"] == "pending"
    assert data["follow_up_status"] == "none"

    # Verify extracted usability heuristics
    quality = data["image_quality"]
    assert quality["width"] == 600
    assert quality["height"] == 600
    assert quality["format"] == "JPEG"
    assert quality["aspect_ratio"] == 1.0
    assert "mean_brightness" in quality
    assert "contrast_std" in quality
    assert quality["heuristic_status"] in ("acceptable", "borderline", "unusable")
    assert "disclaimer" in quality


def test_upload_valid_png(client):
    """POST /api/v1/screenings/upload must accept a valid PNG image."""
    png_bytes = create_synthetic_image(width=400, height=400, img_format="PNG")
    files = {"file": ("fundus_sample.png", png_bytes, "image/png")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["image_quality"]["format"] == "PNG"
    assert data["mime_type"] == "image/png"


def test_upload_valid_webp(client):
    """POST /api/v1/screenings/upload must accept a valid WebP image."""
    webp_bytes = create_synthetic_image(width=300, height=300, img_format="WEBP")
    files = {"file": ("fundus_sample.webp", webp_bytes, "image/webp")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["image_quality"]["format"] == "WEBP"
    assert data["mime_type"] == "image/webp"


# -------------------------------------------------------------
# Test 3: Reject Non-Image Files
# -------------------------------------------------------------
def test_reject_text_file_as_image(client):
    """Uploading plain text or script files must be rejected with 415 or 400."""
    fake_content = b"This is a text file masquerading as an image."
    files = {"file": ("fake.jpg", fake_content, "image/jpeg")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code in (400, 415)
    assert "Unsupported" in response.json()["detail"] or "corrupted" in response.json()["detail"]


# -------------------------------------------------------------
# Test 4: Reject Corrupted Image
# -------------------------------------------------------------
def test_reject_corrupted_image(client):
    """Uploading a file with valid JPEG magic bytes but corrupted payload must be rejected."""
    corrupted = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 50  # Truncated header
    files = {"file": ("corrupt.jpg", corrupted, "image/jpeg")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower() or "decode" in response.json()["detail"].lower()


# -------------------------------------------------------------
# Test 5: Reject Unsupported Image Format (e.g. GIF)
# -------------------------------------------------------------
def test_reject_unsupported_gif_format(client):
    """GIF files must be rejected because they are not approved clinical formats (JPEG, PNG, WEBP)."""
    img = Image.new("RGB", (300, 300), color=(100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, format="GIF")
    files = {"file": ("sample.gif", buf.getvalue(), "image/gif")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 415
    assert "Unsupported or unrecognized" in response.json()["detail"]


# -------------------------------------------------------------
# Test 6: Reject Sub-Minimum Dimensions
# -------------------------------------------------------------
def test_reject_small_dimensions(client):
    """Images with dimensions smaller than 200x200 px must be rejected."""
    tiny_img = create_synthetic_image(width=100, height=100, img_format="JPEG")
    files = {"file": ("tiny.jpg", tiny_img, "image/jpeg")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 400
    assert "smaller than required minimum" in response.json()["detail"]


# -------------------------------------------------------------
# Test 7: Reject Oversized Image (> 15 MB)
# -------------------------------------------------------------
def test_reject_oversized_payload(client):
    """Files exceeding 15MB must be rejected with HTTP 413."""
    oversized_data = b"\x00" * (16 * 1024 * 1024)  # 16 MB
    files = {"file": ("huge.jpg", oversized_data, "image/jpeg")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 413
    assert "exceeds maximum allowable limit" in response.json()["detail"]


# -------------------------------------------------------------
# Test 8: Analysis Trigger When Model Not Configured
# -------------------------------------------------------------
def test_analyze_when_model_not_configured(client, monkeypatch):
    """POST /api/v1/screenings/{id}/analyze must NOT fabricate predictions when model is not configured."""
    from app.services.model_service import model_service
    monkeypatch.setattr(model_service, "is_configured", lambda: False)
    monkeypatch.setattr(model_service, "get_status", lambda: "not_configured")

    # First upload an image
    jpeg_bytes = create_synthetic_image(width=500, height=500, img_format="JPEG")
    files = {"file": ("test_analysis.jpg", jpeg_bytes, "image/jpeg")}
    upload_res = client.post("/api/v1/screenings/upload", files=files)
    screening_id = upload_res.json()["screening_id"]

    # Trigger analysis
    analyze_res = client.post(f"/api/v1/screenings/{screening_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["screening_id"] == screening_id
    assert data["model_status"] == "not_configured"
    assert data["analysis_available"] is False
    assert data["prediction"] is None
    assert data["confidence"] is None
    assert data["class_probabilities"] is None
    assert "Awaiting verified model weights" in data["message"]


def test_analyze_with_verified_model(client):
    """POST /api/v1/screenings/{id}/analyze runs genuine inference and produces Grad-CAM when model is ready."""
    jpeg_bytes = create_synthetic_image(width=500, height=500, img_format="JPEG")
    files = {"file": ("test_real_infer.jpg", jpeg_bytes, "image/jpeg")}
    upload_res = client.post("/api/v1/screenings/upload", files=files)
    screening_id = upload_res.json()["screening_id"]

    analyze_res = client.post(f"/api/v1/screenings/{screening_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    assert data["screening_id"] == screening_id
    assert data["model_status"] == "ready"
    assert data["analysis_available"] is True
    assert data["prediction"] in ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["class_probabilities"]) == 5
    assert data["gradcam_available"] is True
    assert data["gradcam_url"] == f"/api/v1/screenings/{screening_id}/gradcam"

    # Test GET gradcam endpoint
    cam_res = client.get(data["gradcam_url"])
    assert cam_res.status_code == 200
    assert cam_res.headers["content-type"] == "image/png"
    assert len(cam_res.content) > 100

    # Verify database persistence
    get_res = client.get(f"/api/v1/screenings/{screening_id}")
    assert get_res.status_code == 200
    rec = get_res.json()
    assert rec["analysis_available"] is True
    assert rec["prediction"] == data["prediction"]
    assert rec["gradcam_available"] is True



def test_analyze_nonexistent_screening(client):
    """Attempting to analyze a non-existent screening ID must return 404."""
    response = client.post("/api/v1/screenings/non-existent-id/analyze")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# -------------------------------------------------------------
# Test 9: Get Specific Screening Record
# -------------------------------------------------------------
def test_get_screening_by_id(client):
    """GET /api/v1/screenings/{id} must retrieve the persistent record from database."""
    jpeg_bytes = create_synthetic_image(width=500, height=500, img_format="JPEG")
    files = {"file": ("retrieval_test.jpg", jpeg_bytes, "image/jpeg")}
    upload_res = client.post("/api/v1/screenings/upload", files=files)
    screening_id = upload_res.json()["screening_id"]

    get_res = client.get(f"/api/v1/screenings/{screening_id}")
    assert get_res.status_code == 200
    record = get_res.json()
    assert record["screening_id"] == screening_id
    assert record["file_name"] == "retrieval_test.jpg"
    assert record["image_quality"]["width"] == 500
    assert record["human_review_status"] == "pending"


def test_get_nonexistent_screening(client):
    """GET /api/v1/screenings/{id} for missing ID must return 404."""
    response = client.get("/api/v1/screenings/missing-uuid-1234")
    assert response.status_code == 404


# -------------------------------------------------------------
# Test 10: List Screenings with Pagination
# -------------------------------------------------------------
def test_list_screenings_pagination(client):
    """GET /api/v1/screenings must return paginated list of screenings."""
    response = client.get("/api/v1/screenings?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert isinstance(data["items"], list)
    assert data["total"] >= 1
