"""
NutriVision - TensorFlow Lite Classifier

Optional TFLite model integration for lightweight food classification.
For the academic prototype, this provides:

1. A framework for loading and running TFLite models
2. A simple label-based food category classifier
3. Demo mode that returns plausible results without a real model

In a production system, you would train a custom model to:
- Classify food images vs non-food images
- Detect food label regions
- Categorize food types

For the final year project, this demonstrates the TFLite integration
architecture. A real .tflite model file can be plugged in later.
"""

import numpy as np
from typing import Optional
import os


# Default food categories for demo classification
FOOD_CATEGORIES = [
    "packaged_food", "fresh_produce", "beverage", "dairy",
    "snack", "cereal", "condiment", "frozen_food",
    "bakery", "canned_food", "meat", "seafood",
]


class TFLiteClassifier:
    """
    TensorFlow Lite model wrapper for food classification.

    Supports:
    - Loading .tflite model files
    - Running inference on preprocessed images
    - Demo mode (no model needed) for academic prototype
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.interpreter = None
        self._loaded = False
        self.labels = FOOD_CATEGORIES

    def load_model(self) -> bool:
        """
        Attempt to load a TFLite model from disk.

        Returns:
            True if model loaded successfully, False otherwise
        """
        if not self.model_path or not os.path.exists(self.model_path):
            print("[TFLite] No model file found - using demo mode")
            return False

        try:
            # Try importing tflite_runtime first (lighter)
            try:
                from tflite_runtime.interpreter import Interpreter
            except ImportError:
                # Fall back to full TensorFlow
                try:
                    from tensorflow.lite.python.interpreter import Interpreter
                except ImportError:
                    print("[TFLite] Neither tflite-runtime nor tensorflow installed")
                    return False

            self.interpreter = Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self._loaded = True
            print(f"[TFLite] Model loaded from {self.model_path}")
            return True

        except Exception as e:
            print(f"[TFLite] Failed to load model: {e}")
            return False

    def classify(self, image: np.ndarray) -> dict:
        """
        Classify a food image.

        Args:
            image: Preprocessed image as numpy array

        Returns:
            Dict with 'label', 'confidence', 'all_scores', 'model_loaded'
        """
        if self._loaded and self.interpreter:
            return self._run_inference(image)
        else:
            return self._demo_classify(image)

    def _run_inference(self, image: np.ndarray) -> dict:
        """Run actual TFLite model inference."""
        try:
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()

            # Resize image to model's expected input shape
            input_shape = input_details[0]["shape"]
            h, w = input_shape[1], input_shape[2]
            import cv2
            resized = cv2.resize(image, (w, h))

            # Prepare input tensor
            input_data = np.expand_dims(resized, axis=0).astype(
                input_details[0]["dtype"]
            )

            # Run inference
            self.interpreter.set_tensor(input_details[0]["index"], input_data)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(output_details[0]["index"])

            # Get top prediction
            scores = output_data[0]
            top_idx = np.argmax(scores)

            return {
                "label": self.labels[top_idx] if top_idx < len(self.labels) else "unknown",
                "confidence": float(scores[top_idx]),
                "all_scores": {
                    self.labels[i]: float(scores[i])
                    for i in range(min(len(scores), len(self.labels)))
                },
                "model_loaded": True,
            }

        except Exception as e:
            print(f"[TFLite] Inference error: {e}")
            return self._demo_classify(image)

    def _demo_classify(self, image: np.ndarray) -> dict:
        """
        Demo classification without a real model.
        Uses simple heuristics based on image properties.
        """
        # Use image properties for plausible demo output
        if image is not None and len(image.shape) >= 2:
            h, w = image.shape[:2]
            # Simple heuristic: use pixel statistics
            mean_val = np.mean(image) if image.size > 0 else 128

            # Pick a category based on image brightness (demo purposes)
            idx = int(mean_val) % len(self.labels)
            confidence = 0.65 + (mean_val % 30) / 100.0
        else:
            idx = 0
            confidence = 0.50

        return {
            "label": self.labels[idx],
            "confidence": round(min(confidence, 0.95), 2),
            "all_scores": {},
            "model_loaded": False,
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded
