"""AI Model Service boundary for DRISHTI-AI.

IMPORTANT BOUNDARY CONTRACT:
This module defines the clean boundary between the web application backend (Sirish)
and the AI/ML pipeline (Rudra).

STRICT POLICY:
- When no verified weights are loaded, status MUST report 'not_configured'.
- NEVER return fabricated class predictions or fake confidence percentages.
- Rudra can implement model weight loading, custom preprocessing, and Grad-CAM
  generation inside this class without touching API routes.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import os


TARGET_CLASSES: List[str] = [
    "No DR",             # Class 0: No apparent retinopathy
    "Mild",              # Class 1: Microaneurysms only
    "Moderate",          # Class 2: More than microaneurysms, less than severe
    "Severe",            # Class 3: >20 intraretinal hemorrhages in 4 quadrants, venous beading in 2, or IRMA in 1
    "Proliferative DR",  # Class 4: Neovascularization, vitreous/preretinal hemorrhage
]


class ModelServiceUnavailableError(Exception):
    """Raised when inference is requested but no model has been loaded/configured."""
    def __init__(self, message: str = "AI Model is not configured. Awaiting verified model weights."):
        super().__init__(message)
        self.message = message


class AbstractDRModelService(ABC):
    """Abstract base interface defining expectations for DR classification and explainability."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if verified model weights are successfully loaded in memory."""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Return 'not_configured', 'ready', or 'error'."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return information about model architecture, version, weights path, and classes."""
        pass

    @abstractmethod
    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """Execute inference on fundus image bytes.
        
        Must raise ModelServiceUnavailableError if not configured.
        """
        pass

    @abstractmethod
    def generate_gradcam(self, image_bytes: bytes, target_class: Optional[int] = None) -> Optional[bytes]:
        """Generate Grad-CAM activation heatmap bytes for explainability visualization."""
        pass


class DRModelService(AbstractDRModelService):
    """Default implementation maintaining model state and serving inference boundary."""

    def __init__(self, model_weights_path: Optional[str] = None):
        self.model_weights_path = model_weights_path or os.getenv("DRISHTI_MODEL_PATH")
        self._model = None
        self._status = "not_configured"
        self._classes = TARGET_CLASSES

        # Attempt to load if path provided
        if self.model_weights_path and os.path.exists(self.model_weights_path):
            self._load_model()
        else:
            self._status = "not_configured"

    def _load_model(self) -> None:
        """Placeholder hook for Rudra to initialize model weights (e.g., PyTorch / ONNX / TorchScript)."""
        # Note for Rudra:
        # Load weights, verify tensor shapes, and assign self._model
        # self._model = ...
        # self._status = "ready"
        pass

    def is_configured(self) -> bool:
        """Check whether verified model is ready."""
        return self._status == "ready" and self._model is not None

    def get_status(self) -> str:
        """Return current status: 'not_configured', 'ready', or 'error'."""
        return self._status

    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata for health/info endpoints."""
        return {
            "model_status": self._status,
            "model_name": None if not self.is_configured() else "verified_dr_model",
            "supported_classes": self._classes,
            "weights_configured": bool(self.model_weights_path),
        }

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """Run DR inference on validated fundus image.
        
        Raises ModelServiceUnavailableError if no model is loaded.
        NEVER returns fake or synthetic predictions.
        """
        if not self.is_configured():
            raise ModelServiceUnavailableError(
                "Diabetic Retinopathy AI model is not configured. "
                "Awaiting verified model weights and evaluation from AI lead (Rudra)."
            )

        # Implementation for Rudra when model is loaded:
        # 1. Preprocess image_bytes (resize, normalize)
        # 2. Run inference -> logits
        # 3. Apply softmax -> class probabilities
        # 4. Return genuine prediction dictionary
        raise NotImplementedError("Real model inference logic will be supplied once weights are verified.")

    def generate_gradcam(self, image_bytes: bytes, target_class: Optional[int] = None) -> Optional[bytes]:
        """Generate Grad-CAM heatmap visualization.
        
        Returns None when model is not configured.
        """
        if not self.is_configured():
            return None
        return None


# Global singleton instance for the application runtime
model_service = DRModelService()
