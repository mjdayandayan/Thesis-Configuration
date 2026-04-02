"""
USB webcam interface for image capture.
"""

import cv2
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, DATA_DIR


class Camera:
    """USB webcam capture interface."""

    def __init__(self, index=CAMERA_INDEX, width=CAMERA_WIDTH, height=CAMERA_HEIGHT):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capture_frame(self):
        """Capture a single frame. Returns numpy array (BGR) or None."""
        ret, frame = self.cap.read()
        if ret:
            return frame
        print("Failed to capture frame")
        return None

    def save_frame(self, frame, filepath=None):
        """Save a frame to disk. Auto-generates filename if not provided."""
        if filepath is None:
            os.makedirs(DATA_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(DATA_DIR, f"capture_{timestamp}.jpg")

        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        cv2.imwrite(filepath, frame)
        return filepath

    def release(self):
        """Release the camera."""
        if self.cap.isOpened():
            self.cap.release()


# --- Run directly to test ---
if __name__ == "__main__":
    print("Testing camera capture...")
    cam = Camera()
    frame = cam.capture_frame()
    if frame is not None:
        print(f"  Captured frame: {frame.shape}")
        path = cam.save_frame(frame)
        print(f"  Saved to: {path}")
    else:
        print("  Camera capture failed")
    cam.release()
