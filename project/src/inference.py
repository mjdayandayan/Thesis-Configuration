"""
Edge Impulse model inference for rice paddy disease/health detection.
"""

import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import MODEL_PATH, CONFIDENCE_THRESHOLD


class ModelInference:
    """Wrapper for Edge Impulse Linux model inference (FOMO object detection)."""

    def __init__(self, model_path=MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Download from Edge Impulse (Deployment → Linux AARCH64) "
                "and place in ~/thesis/models/"
            )

        from edge_impulse_linux.image import ImageImpulseRunner
        self.runner = ImageImpulseRunner(model_path)
        self.model_info = self.runner.init()
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        print(f"Model loaded: {self.model_info['project']['name']}")
        print(f"  Labels: {self.model_info['model_parameters']['labels']}")
        print(f"  Confidence threshold: {self.confidence_threshold}")

    def classify(self, frame):
        """
        Run inference on a camera frame.

        Args:
            frame: BGR numpy array from OpenCV

        Returns:
            dict with 'results' (list of label/value pairs) and 'timing' info
        """
        # Edge Impulse expects RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get model input dimensions
        input_width = self.model_info['model_parameters']['image_input_width']
        input_height = self.model_info['model_parameters']['image_input_height']

        # Resize to model input size
        img_resized = cv2.resize(img_rgb, (input_width, input_height))

        # Flatten to 1D array of features
        features = np.array(img_resized).flatten().tolist()

        # Run inference
        result = self.runner.classify(features)
        return result

    def get_top_prediction(self, result):
        """
        Get the label with the highest confidence from classify() output.
        Handles both FOMO (bounding_boxes) and classification output formats.
        """
        # FOMO returns bounding_boxes
        bboxes = result.get('result', {}).get('bounding_boxes', [])
        if bboxes:
            # Filter by confidence threshold
            filtered = [b for b in bboxes if b['value'] >= self.confidence_threshold]
            if not filtered:
                return None, 0.0

            # Count detections per label, track max confidence
            label_counts = {}
            label_max_conf = {}
            for b in filtered:
                lbl = b['label']
                label_counts[lbl] = label_counts.get(lbl, 0) + 1
                label_max_conf[lbl] = max(label_max_conf.get(lbl, 0), b['value'])

            # Return the label with the most detections
            top_label = max(label_counts, key=label_counts.get)
            return top_label, label_max_conf[top_label]

        # Fallback: classification format (non-FOMO models)
        classifications = result.get('result', {}).get('classification', {})
        if classifications:
            top_label = max(classifications, key=classifications.get)
            return top_label, classifications[top_label]

        return None, 0.0

    def get_all_detections(self, result):
        """
        Get all FOMO detections above the confidence threshold.
        Returns list of dicts: [{'label': str, 'confidence': float, 'x': int, 'y': int}, ...]
        """
        bboxes = result.get('result', {}).get('bounding_boxes', [])
        return [
            {
                'label': b['label'],
                'confidence': round(b['value'], 4),
                'x': b['x'],
                'y': b['y'],
                'width': b['width'],
                'height': b['height']
            }
            for b in bboxes if b['value'] >= self.confidence_threshold
        ]

    def close(self):
        self.runner.stop()


# --- Run directly to test ---
if __name__ == "__main__":
    print("Testing Edge Impulse model inference...")
    try:
        model = ModelInference()

        from camera import Camera
        cam = Camera()
        frame = cam.capture_frame()

        if frame is not None:
            result = model.classify(frame)
            label, confidence = model.get_top_prediction(result)
            print(f"  Top prediction: {label} ({confidence:.2%})")
            print(f"  Full result: {result}")
        else:
            print("  No frame captured")

        cam.release()
        model.close()
    except FileNotFoundError as e:
        print(f"  {e}")
    except ImportError:
        print("  edge_impulse_linux not installed. Run: pip install edge_impulse_linux")
