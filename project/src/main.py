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
    LOG_INTERVAL_SECONDS, DATA_DIR, LOG_DIR,
    TEMP_MIN, TEMP_MAX, HUMIDITY_MIN, HUMIDITY_MAX,
    SOIL_MOISTURE_MIN, SOIL_SENSOR_MODE, MODEL_PATH
)
from src.sensors import DHTSensor, get_soil_sensor
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


def check_alerts(data):
    """Check sensor readings against thresholds and return alert messages."""
    alerts = []
    temp = data.get('temperature')
    humidity = data.get('humidity')

    if temp is not None:
        if temp < TEMP_MIN:
            alerts.append(f"LOW TEMPERATURE: {temp}°C (min: {TEMP_MIN}°C)")
        elif temp > TEMP_MAX:
            alerts.append(f"HIGH TEMPERATURE: {temp}°C (max: {TEMP_MAX}°C)")

    if humidity is not None:
        if humidity < HUMIDITY_MIN:
            alerts.append(f"LOW HUMIDITY: {humidity}% (min: {HUMIDITY_MIN}%)")
        elif humidity > HUMIDITY_MAX:
            alerts.append(f"HIGH HUMIDITY: {humidity}% (max: {HUMIDITY_MAX}%)")

    soil = data.get('soil_moisture', {})
    if SOIL_SENSOR_MODE == "digital" and soil.get('status') == 'dry':
        alerts.append("SOIL IS DRY — rice paddy needs water!")
    elif SOIL_SENSOR_MODE == "analog":
        pct = soil.get('percentage')
        if pct is not None and pct < SOIL_MOISTURE_MIN:
            alerts.append(f"LOW SOIL MOISTURE: {pct}% (min: {SOIL_MOISTURE_MIN}%)")

    return alerts


def save_data(data):
    """Save a reading to a JSON lines file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"readings_{date_str}.jsonl")

    with open(filepath, 'a') as f:
        f.write(json.dumps(data) + '\n')


def run_once(dht, soil, camera, model, transmitter):
    """Take a single complete reading."""
    timestamp = datetime.now().isoformat()
    data = {'timestamp': timestamp}

    # Read DHT22
    dht_data = dht.read()
    if dht_data:
        data['temperature'] = dht_data['temperature']
        data['humidity'] = dht_data['humidity']
        logger.info(f"DHT22: {dht_data['temperature']}°C, {dht_data['humidity']}%")
    else:
        logger.warning("DHT22 read failed")

    # Read soil moisture
    soil_data = soil.read()
    data['soil_moisture'] = soil_data
    logger.info(f"Soil: {soil_data}")

    # Capture image and run inference
    frame = camera.capture_frame()
    if frame is not None:
        img_path = camera.save_frame(frame)
        data['image_path'] = img_path

        if model is not None:
            try:
                result = model.classify(frame)
                label, confidence = model.get_top_prediction(result)
                data['prediction'] = {'label': label, 'confidence': round(confidence, 4)}
                logger.info(f"Inference: {label} ({confidence:.2%})")
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

    # Transmit (if server configured)
    if transmitter.server_url:
        transmitter.send(data)

    return data


def main():
    parser = argparse.ArgumentParser(description="Rice Paddy Monitoring System")
    parser.add_argument('--once', action='store_true', help="Take a single reading and exit")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("Rice Paddy Monitoring System Starting")
    logger.info(f"Soil sensor mode: {SOIL_SENSOR_MODE}")
    logger.info("=" * 50)

    # Initialize components
    dht = DHTSensor()
    soil = get_soil_sensor()
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
            data = run_once(dht, soil, camera, model, transmitter)
            print(json.dumps(data, indent=2))
        else:
            logger.info(f"Continuous monitoring — interval: {LOG_INTERVAL_SECONDS}s")
            while True:
                run_once(dht, soil, camera, model, transmitter)
                time.sleep(LOG_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        dht.cleanup()
        soil.cleanup()
        camera.release()
        if model:
            model.close()
        logger.info("All resources cleaned up. Goodbye.")


if __name__ == "__main__":
    main()
