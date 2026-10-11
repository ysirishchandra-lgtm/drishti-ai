"""Unit tests for DRISHTI-AI Model Service and Explainability."""
import io
import os
import pytest
import numpy as np
from PIL import Image

from app.services.model_service import (
    DRModelService,
    ModelServiceUnavailableError,
    TARGET_CLASSES,
    _apply_jet_colormap,
)


@pytest.fixture
def model_service_instance():
    """Return loaded DRModelService instance using repository model weights."""
    return DRModelService()


def create_test_retina_image(width=512, height=512, color=(160, 60, 40)):
    """Generate in-memory synthetic retina test image bytes."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_model_service_load_success(model_service_instance):
    """Model service loads successfully with verified weights."""
    assert model_service_instance.is_configured() is True
    assert model_service_instance.get_status() == "ready"
    meta = model_service_instance.get_metadata()
    assert meta["model_name"] == "RetinaExplain_AI_v2_final"
    assert meta["supported_classes"] == TARGET_CLASSES
    assert meta["gradcam_supported"] is True


def test_model_service_unconfigured_behavior():
    """Unconfigured model service reports 'not_configured' and raises clean error."""
    unconf_service = DRModelService(model_weights_path="non_existent_path.keras")
    assert unconf_service.is_configured() is False
    assert unconf_service.get_status() == "not_configured"
    
    with pytest.raises(ModelServiceUnavailableError) as exc_info:
        unconf_service.predict(b"dummy")
    assert "not configured" in str(exc_info.value).lower()

    assert unconf_service.generate_gradcam(b"dummy") is None


def test_real_model_inference_output_shape_and_classes(model_service_instance):
    """Real inference returns exact 5 classes with valid normalized probabilities."""
    img_bytes = create_test_retina_image()
    result = model_service_instance.predict(img_bytes)

    assert result["model_status"] == "ready"
    assert result["prediction"] in TARGET_CLASSES
    assert 0 <= result["predicted_index"] < 5
    assert 0.0 <= result["confidence"] <= 1.0

    probs = result["class_probabilities"]
    assert len(probs) == 5
    for cls_name in TARGET_CLASSES:
        assert cls_name in probs
        assert 0.0 <= probs[cls_name] <= 1.0

    prob_sum = sum(probs.values())
    assert 0.99 <= prob_sum <= 1.01


def test_genuine_gradcam_generation(model_service_instance):
    """Genuine Grad-CAM generates non-empty PNG overlay image matching original size."""
    img_bytes = create_test_retina_image(width=300, height=300)
    cam_bytes = model_service_instance.generate_gradcam(img_bytes, target_class=0)

    assert cam_bytes is not None
    assert len(cam_bytes) > 200

    cam_img = Image.open(io.BytesIO(cam_bytes))
    assert cam_img.format == "PNG"
    assert cam_img.size == (300, 300)


def test_jet_colormap_mapping():
    """Jet colormap helper produces valid RGB array within [0, 255]."""
    gray = np.linspace(0.0, 1.0, 100).reshape((10, 10))
    colored = _apply_jet_colormap(gray)
    assert colored.shape == (10, 10, 3)
    assert colored.dtype == np.uint8
    assert colored.min() >= 0
    assert colored.max() <= 255
