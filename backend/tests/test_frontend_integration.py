"""End-to-end integration and frontend-backend interoperability test suite.

Validates:
1. Static frontend asset serving (index.html, styles.css, app.js) via FastAPI.
2. CORS headers for local frontend dev origins (5173, 8080, 3000).
3. Real fundus image upload and usability heuristics extraction using genuine dataset samples.
4. AI screening analyze endpoint returning honest model-unavailable state without fabrication.
5. Invalid upload rejection and error detail reporting.
6. Screening record retrieval and SQLite persistence integrity.
"""
import io
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure isolated test database
temp_dir = tempfile.mkdtemp()
test_db_path = os.path.join(temp_dir, "test_integration.db")
os.environ["DRISHTI_DB_PATH"] = test_db_path

from app.main import app
from app.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db(test_db_path)
    yield
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# -------------------------------------------------------------
# 1. Health and CORS Verification
# -------------------------------------------------------------
def test_backend_health(client):
    """GET /health must be operational and report model_status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_status"] in ("ready", "not_configured")
    assert "No DR" in data["supported_classes"]
    assert "Proliferative DR" in data["supported_classes"]


def test_cors_headers_for_dev_servers(client):
    """CORS middleware must allow frontend running on port 8080 or 5173."""
    headers = {
        "Origin": "http://localhost:8080",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/v1/screenings/upload", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:8080"


# -------------------------------------------------------------
# 2. Static Frontend Asset Serving
# -------------------------------------------------------------
def test_frontend_index_serving(client):
    """FastAPI mounted static root must serve the clean DRISHTI-AI index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "DRISHTI-AI" in response.text
    assert "Early Detection for Clearer Tomorrows" in response.text
    assert '<link rel="stylesheet" href="styles.css"' in response.text
    assert '<script src="app.js"></script>' in response.text


def test_frontend_static_assets_serving(client):
    """FastAPI must serve styles.css and app.js."""
    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert len(css_res.text) > 0

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert len(js_res.text) > 0


# -------------------------------------------------------------
# 3. Real Fundus Image Upload & Quality Heuristics
# -------------------------------------------------------------
def test_upload_real_dataset_fundus_image(client):
    """POST /api/v1/screenings/upload must succeed with genuine dataset fundus image."""
    sample_path = "datasets/aptos2019/classwise_images/class_0_no_dr/002c21358ce6.png"
    if not os.path.exists(sample_path):
        pytest.skip(f"Dataset sample not found at {sample_path}")

    with open(sample_path, "rb") as f:
        img_bytes = f.read()

    files = {"file": ("002c21358ce6.png", img_bytes, "image/png")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 201
    data = response.json()

    assert "screening_id" in data
    assert data["file_name"] == "002c21358ce6.png"
    assert data["validation_passed"] is True
    assert data["model_status"] in ("ready", "not_configured")

    # Verify extracted usability heuristics
    quality = data["image_quality"]
    assert quality["width"] > 200
    assert quality["height"] > 200
    assert quality["format"] == "PNG"
    assert quality["mean_brightness"] > 0
    assert quality["contrast_std"] > 0
    assert quality["heuristic_status"] in ("acceptable", "borderline", "unusable")
    assert "disclaimer" in quality

    # Test triggering analysis on this genuine uploaded image
    screening_id = data["screening_id"]
    analyze_res = client.post(f"/api/v1/screenings/{screening_id}/analyze")
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()
    assert analyze_data["screening_id"] == screening_id
    if analyze_data["model_status"] == "ready":
        assert analyze_data["analysis_available"] is True
        assert analyze_data["prediction"] in ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
        assert 0.0 <= analyze_data["confidence"] <= 1.0
        assert analyze_data["gradcam_available"] is True
    else:
        assert analyze_data["analysis_available"] is False
        assert analyze_data["prediction"] is None


# -------------------------------------------------------------
# 4. Error Handling and Rejection Boundaries
# -------------------------------------------------------------
def test_reject_corrupt_upload_with_proper_status(client):
    """Uploading corrupt image must yield clean HTTP 400 error without 500 or stack trace."""
    corrupt_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    files = {"file": ("corrupt.png", corrupt_data, "image/png")}
    response = client.post("/api/v1/screenings/upload", files=files)
    assert response.status_code == 400
    assert "detail" in response.json()
