"""AI Model Service boundary for DRISHTI-AI.

Integrates Rudra's trained Diabetic Retinopathy classification model artifact
(EfficientNetB0 backbone, 5-class DR stage classification) and genuine Grad-CAM
explainability.

STRICT CLINICAL PROTOCOL:
- Status reports 'not_configured' if model weights are absent.
- Status reports 'error' if model loading fails.
- Never returns fabricated class predictions or fake confidence values.
- Raw model scores are research-prototype indicators, not calibrated clinical probabilities.
"""
from abc import ABC, abstractmethod
import io
import logging
import os
import re
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger("drishti.model_service")

# Verified label mapping from DRISHTI_1.ipynb training code & class weights
TARGET_CLASSES: List[str] = [
    "No DR",             # Class 0: class_0_no_dr
    "Mild",              # Class 1: class_1_mild
    "Moderate",          # Class 2: class_2_moderate
    "Severe",            # Class 3: class_3_severe
    "Proliferative DR",  # Class 4: class_4_proliferative_dr
]

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "models",
    "RetinaExplain_AI_v2_final.keras"
)


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


def _apply_jet_colormap(gray_heatmap: np.ndarray) -> np.ndarray:
    """Map normalized [0, 1] 2D grayscale array to an RGB heatmap using Jet colormap."""
    # Lookup table for Jet colormap (256 RGB values)
    x = np.clip(gray_heatmap, 0.0, 1.0)
    r = np.clip(1.5 - np.abs(4.0 * x - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * x - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * x - 1.0), 0.0, 1.0)
    rgb = np.stack([r, g, b], axis=-1) * 255.0
    return rgb.astype(np.uint8)


class DRModelService(AbstractDRModelService):
    """Production implementation managing Keras model loading, preprocessing, inference, and Grad-CAM."""

    def __init__(self, model_weights_path: Optional[str] = None):
        self.model_weights_path = model_weights_path or os.getenv("DRISHTI_MODEL_PATH", DEFAULT_MODEL_PATH)
        self._model = None
        self._gradcam_submodel = None
        self._gap_layer = None
        self._dropout_layer = None
        self._dense_layer = None
        self._status = "not_configured"
        self._gradcam_available = False
        self._classes = TARGET_CLASSES
        self._init_error: Optional[str] = None

        if self.model_weights_path and os.path.exists(self.model_weights_path):
            self._load_model()
        else:
            self._status = "not_configured"
            logger.info("DRISHTI AI Model artifact not found at default path. Model status: not_configured.")

    def _load_model(self) -> None:
        """Safely load Keras model artifact once during startup."""
        try:
            # Set TensorFlow environment flags for quiet initialization
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
            os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
            import keras
            import tensorflow as tf

            logger.info(f"Loading Keras model from {self.model_weights_path}...")
            # Load with compile=False for pure inference
            self._model = keras.models.load_model(self.model_weights_path, compile=False)
            
            # Verify input shape
            expected_input = (None, 224, 224, 3)
            if hasattr(self._model, "input_shape") and self._model.input_shape != expected_input:
                logger.warning(f"Unexpected model input shape: {self._model.input_shape}, expected: {expected_input}")

            # Verify output classes
            output_shape = getattr(self._model, "output_shape", None)
            if output_shape and output_shape[-1] != len(self._classes):
                raise ValueError(
                    f"Model output dimension {output_shape[-1]} does not match expected {len(self._classes)} classes."
                )

            # Inspect and initialize Grad-CAM submodel if architecture matches
            try:
                backbone = self._model.get_layer("efficientnetb0")
                top_conv = backbone.get_layer("top_activation")
                self._gradcam_submodel = keras.Model(
                    inputs=backbone.input,
                    outputs=top_conv.output
                )
                self._gap_layer = self._model.get_layer("global_average_pooling2d_1")
                self._dropout_layer = self._model.get_layer("dropout_1")
                self._dense_layer = self._model.get_layer("dense_1")
                self._gradcam_available = True
                logger.info("Grad-CAM feature submodel successfully configured.")
            except Exception as cam_exc:
                self._gradcam_available = False
                logger.warning(f"Grad-CAM feature layers could not be resolved: {cam_exc}. Explainability disabled.")

            self._status = "ready"
            self._init_error = None
            logger.info(f"Model successfully loaded. Status: ready. Classes: {self._classes}")

        except Exception as exc:
            self._status = "error"
            self._model = None
            self._gradcam_submodel = None
            self._gradcam_available = False
            self._init_error = str(exc)
            logger.error(f"Failed to load AI model artifact: {exc}", exc_info=True)

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
            "model_name": "RetinaExplain_AI_v2_final" if self.is_configured() else None,
            "supported_classes": self._classes,
            "weights_configured": bool(self.model_weights_path and os.path.exists(self.model_weights_path)),
            "gradcam_supported": self._gradcam_available,
        }

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """Run DR inference on validated fundus image.
        
        Preprocessing adheres to Rudra's validated training pipeline:
        - Decode image, convert to RGB.
        - Bilinear resize to (224, 224).
        - Cast to float32 NumPy array in range [0, 255].
        - Input array shape: (1, 224, 224, 3).
        - EfficientNetB0 backbone handles internal rescaling/normalization.
        """
        if not self.is_configured():
            raise ModelServiceUnavailableError(
                "Diabetic Retinopathy AI model is not configured. "
                "Awaiting verified model weights and evaluation from AI lead (Rudra)."
            )

        try:
            # 1. Decode image bytes with Pillow
            stream = io.BytesIO(image_bytes)
            img = Image.open(stream).convert("RGB")
            
            # 2. Resize to model's expected input dimensions
            img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
            
            # 3. Convert to float32 array in [0, 255] range (do NOT divide by 255)
            arr = np.array(img_resized, dtype=np.float32)
            tensor_input = np.expand_dims(arr, axis=0)  # Shape: (1, 224, 224, 3)

            # 4. Execute forward pass
            preds = self._model(tensor_input, training=False).numpy()

            # 5. Output sanity checks
            if not np.all(np.isfinite(preds)):
                raise ValueError("Model inference produced non-finite values (NaN or Inf).")

            if preds.shape != (1, len(self._classes)):
                raise ValueError(f"Inference output shape {preds.shape} does not match (1, {len(self._classes)}).")

            probabilities = preds[0]
            # Ensure proper probability distribution
            prob_sum = float(np.sum(probabilities))
            if prob_sum <= 0 or not np.isclose(prob_sum, 1.0, atol=0.05):
                # Apply softmax if logits were returned
                exp_p = np.exp(probabilities - np.max(probabilities))
                probabilities = exp_p / np.sum(exp_p)

            pred_idx = int(np.argmax(probabilities))
            confidence = round(float(probabilities[pred_idx]), 4)
            predicted_class = self._classes[pred_idx]

            class_probabilities = {
                cls_name: round(float(prob), 4)
                for cls_name, prob in zip(self._classes, probabilities)
            }

            return {
                "prediction": predicted_class,
                "confidence": confidence,
                "class_probabilities": class_probabilities,
                "predicted_index": pred_idx,
                "model_status": "ready",
                "model_name": "RetinaExplain_AI_v2_final",
                "gradcam_available": self._gradcam_available,
            }

        except ModelServiceUnavailableError:
            raise
        except Exception as exc:
            logger.error(f"Inference execution failed: {str(exc)}", exc_info=True)
            raise RuntimeError("Model inference failed to process the image.") from exc

    def generate_gradcam(self, image_bytes: bytes, target_class: Optional[int] = None) -> Optional[bytes]:
        """Generate genuine Grad-CAM activation heatmap overlay bytes.
        
        Computes gradients of the target class score with respect to the
        top convolutional activation layer ('top_activation') in EfficientNetB0.
        """
        if not self.is_configured() or not self._gradcam_available or self._gradcam_submodel is None:
            return None

        try:
            import tensorflow as tf

            # 1. Decode original image
            stream = io.BytesIO(image_bytes)
            orig_img = Image.open(stream).convert("RGB")
            orig_w, orig_h = orig_img.size

            # 2. Resize to (224, 224)
            img_resized = orig_img.resize((224, 224), Image.Resampling.BILINEAR)
            arr = np.array(img_resized, dtype=np.float32)
            tensor_input = np.expand_dims(arr, axis=0)

            # 3. Compute gradients via GradientTape
            with tf.GradientTape() as tape:
                inputs_tf = tf.cast(tensor_input, tf.float32)
                conv_out = self._gradcam_submodel(inputs_tf)
                tape.watch(conv_out)
                
                pooled = self._gap_layer(conv_out)
                drop = self._dropout_layer(pooled, training=False)
                preds = self._dense_layer(drop)

                if target_class is None:
                    target_class = int(tf.argmax(preds[0]))
                
                loss = preds[:, target_class]

            grads = tape.gradient(loss, conv_out)
            if grads is None:
                logger.warning("Grad-CAM tape returned None for gradients.")
                return None

            # 4. Global average pooling of gradients
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_out[0]), axis=-1)
            
            # 5. Apply ReLU and normalize
            heatmap = tf.maximum(heatmap, 0)
            max_val = tf.reduce_max(heatmap)
            if max_val > 0:
                heatmap = heatmap / max_val
            heatmap_np = heatmap.numpy()  # Shape: (7, 7)

            # 6. Resize heatmap to original image dimensions
            heatmap_pil = Image.fromarray((heatmap_np * 255.0).astype(np.uint8))
            heatmap_resized = heatmap_pil.resize((orig_w, orig_h), Image.Resampling.BILINEAR)
            heatmap_norm = np.array(heatmap_resized, dtype=np.float32) / 255.0

            # 7. Apply Jet colormap
            colored_heatmap = _apply_jet_colormap(heatmap_norm)  # (orig_h, orig_w, 3)

            # 8. Alpha blend (60% original image + 40% heatmap)
            orig_np = np.array(orig_img, dtype=np.float32)
            blended = (0.6 * orig_np + 0.4 * colored_heatmap).clip(0, 255).astype(np.uint8)

            # 9. Encode to PNG bytes
            out_img = Image.fromarray(blended)
            out_io = io.BytesIO()
            out_img.save(out_io, format="PNG")
            return out_io.getvalue()

        except Exception as exc:
            logger.error(f"Grad-CAM generation failed: {exc}", exc_info=True)
            return None


# Global singleton instance for application runtime
model_service = DRModelService()
