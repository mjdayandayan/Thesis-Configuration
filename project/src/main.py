"""
Main monitoring loop for Rice Paddy Monitoring System.
Reads sensors, captures images, runs inference, logs data.
"""

import argparse
import json
import os
import sys
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import (
    LOG_INTERVAL_SECONDS, DATA_DIR, LOG_DIR, MODEL_PATH,
    SAVE_RETRAINING_FRAMES, RETRAINING_DIR, RETRAINING_INTERVAL,
    SOIL_MOISTURE_MIN, SOIL_PH_MIN, SOIL_PH_MAX,
    SOIL_EC_MIN, SOIL_EC_MAX, SOIL_TEMP_MIN, SOIL_TEMP_MAX
)
from src.sensors import SoilSensorRS485
from src.camera import Camera
from src.transmit import DataTransmitter

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Counter for retraining frame capture
_capture_count = 0


def save_retraining_frame(frame):
    """Save raw camera frame for future Edge Impulse retraining uploads."""
    global _capture_count
    _capture_count += 1
    if _capture_count % RETRAINING_INTERVAL != 0:
        return None
    os.makedirs(RETRAINING_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(RETRAINING_DIR, f"field_{timestamp}.jpg")
    import cv2
    cv2.imwrite(filepath, frame)
    logger.info(f"Saved retraining frame: {filepath}")
    return filepath


def check_alerts(data):
    """Check RS485 sensor readings against thresholds and return alert messages."""
    alerts = []
    soil = data.get('soil_data', {})
    if not isinstance(soil, dict):
        return alerts

    moisture = soil.get('soil_moisture')
    if moisture is not None and moisture < SOIL_MOISTURE_MIN:
        alerts.append(f"LOW SOIL MOISTURE: {moisture}% (min: {SOIL_MOISTURE_MIN}%)")

    soil_temp = soil.get('soil_temperature')
    if soil_temp is not None:
        if soil_temp < SOIL_TEMP_MIN:
            alerts.append(f"LOW SOIL TEMP: {soil_temp}°C (min: {SOIL_TEMP_MIN}°C)")
        elif soil_temp > SOIL_TEMP_MAX:
            alerts.append(f"HIGH SOIL TEMP: {soil_temp}°C (max: {SOIL_TEMP_MAX}°C)")

    ph = soil.get('ph')
    if ph is not None:
        if ph < SOIL_PH_MIN:
            alerts.append(f"LOW SOIL pH: {ph} (min: {SOIL_PH_MIN})")
        elif ph > SOIL_PH_MAX:
            alerts.append(f"HIGH SOIL pH: {ph} (max: {SOIL_PH_MAX})")

    ec = soil.get('ec')
    if ec is not None:
        if ec < SOIL_EC_MIN:
            alerts.append(f"LOW SOIL EC: {ec} µS/cm (min: {SOIL_EC_MIN})")
        elif ec > SOIL_EC_MAX:
            alerts.append(f"HIGH SOIL EC: {ec} µS/cm (max: {SOIL_EC_MAX})")

    return alerts


def save_data(data):
    """Save a reading to a JSON lines file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"readings_{date_str}.jsonl")

    with open(filepath, 'a') as f:
        f.write(json.dumps(data) + '\n')


def run_once(soil, camera, model, transmitter):
    """Take a single complete reading."""
    timestamp = datetime.now().isoformat()
    data = {'timestamp': timestamp}

    # Read RS485 soil sensor
    if soil.available:
        soil_data = soil.read()
        data['soil_data'] = soil_data
        if soil_data:
            logger.info(
                f"RS485 Soil: moisture={soil_data.get('soil_moisture')}%, "
                f"temp={soil_data.get('soil_temperature')}°C, "
                f"EC={soil_data.get('ec')} µS/cm, "
                f"pH={soil_data.get('ph')}, "
                f"humidity={soil_data.get('soil_humidity')}%"
            )
        else:
            logger.warning("Soil sensor read failed")
    else:
        data['soil_data'] = None

    # Capture image and run inference
    frame = camera.capture_frame()
    if frame is not None:
        img_path = camera.save_frame(frame)
        data['image_path'] = img_path

        # Save raw frames for future model retraining
        if SAVE_RETRAINING_FRAMES:
            save_retraining_frame(frame)

        if model is not None:
            try:
                result = model.classify(frame)
                label, confidence = model.get_top_prediction(result)
                detections = model.get_all_detections(result)
                data['prediction'] = {'label': label, 'confidence': round(confidence, 4)}
                data['detections'] = detections
                logger.info(f"Inference: {label} ({confidence:.2%}) — {len(detections)} detection(s)")
            except Exception as e:
                logger.error(f"Inference error: {e}")
    else:
        logger.warning("Camera capture failed")

    # Check alerts
    alerts = check_alerts(data)
    if alerts:
        data['alerts'] = alerts
        for alert in alerts:
            logger.warning(f"ALERT: {alert}")

    # Save locally
    save_data(data)

    # Transmit to Supabase (or fallback server)
    if transmitter.is_configured:
        transmitter.send(data)

    return data


def main():
    parser = argparse.ArgumentParser(description="Rice Paddy Monitoring System")
    parser.add_argument('--once', action='store_true', help="Take a single reading and exit")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("Rice Paddy Monitoring System Starting")
    logger.info("=" * 50)

    # Initialize components
    soil = SoilSensorRS485()
    if soil.available:
        logger.info("RS485 soil sensor: connected")
    else:
        logger.warning("RS485 soil sensor: NOT AVAILABLE — running without soil data")
    camera = Camera()
    transmitter = DataTransmitter()

    model = None
    if os.path.exists(MODEL_PATH):
        try:
            from src.inference import ModelInference
            model = ModelInference()
        except Exception as e:
            logger.warning(f"Could not load model: {e}. Running without inference.")
    else:
        logger.warning(f"Model not found at {MODEL_PATH}. Running without inference.")

    try:
        if args.once:
            data = run_once(soil, camera, model, transmitter)
            print(json.dumps(data, indent=2))
        else:
            logger.info(f"Continuous monitoring — interval: {LOG_INTERVAL_SECONDS}s")
            while True:
                run_once(soil, camera, model, transmitter)
                time.sleep(LOG_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        soil.cleanup()
        camera.release()
        if model:
            model.close()
        logger.info("All resources cleaned up. Goodbye.")


if __name__ == "__main__":
    main()
