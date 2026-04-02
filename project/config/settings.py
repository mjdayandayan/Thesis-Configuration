"""
Configuration settings for Rice Paddy Monitoring System
Edit these values for your specific setup.
"""

# =============================================================
# SENSOR CONFIGURATION
# =============================================================

# DHT22 Temperature/Humidity Sensor
DHT_PIN = 4  # GPIO4 (Physical Pin 7)

# Soil Moisture Sensor Mode
# "digital" = use digital output pin (no ADC needed)
# "analog"  = use ADS1115 ADC (requires I2C + adafruit-circuitpython-ads1x15)
SOIL_SENSOR_MODE = "digital"

# Digital mode settings
SOIL_DIGITAL_PIN = 17  # GPIO17 (Physical Pin 11) — connected to sensor DO pin

# Analog mode settings (for when ADS1115 arrives)
SOIL_MOISTURE_CHANNEL = 0  # ADS1115 channel (A0)
SOIL_DRY = 20000   # ADC value in dry air (calibrate with Step 7)
SOIL_WET = 8000    # ADC value in water (calibrate with Step 7)

# =============================================================
# CAMERA CONFIGURATION
# =============================================================

CAMERA_INDEX = 0       # Usually 0 for first USB webcam
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# =============================================================
# EDGE IMPULSE MODEL
# =============================================================

MODEL_PATH = "/home/pi/thesis/models/your-model.eim"

# =============================================================
# DATA LOGGING
# =============================================================

LOG_INTERVAL_SECONDS = 300  # Log every 5 minutes
DATA_DIR = "/home/pi/thesis/data"
LOG_DIR = "/home/pi/thesis/logs"

# =============================================================
# ALERT THRESHOLDS (adjust for rice paddy requirements)
# =============================================================

TEMP_MIN = 20.0       # °C — below this is too cold
TEMP_MAX = 35.0       # °C — above this is too hot
HUMIDITY_MIN = 60.0   # % — too dry for rice
HUMIDITY_MAX = 90.0   # % — acceptable upper range
SOIL_MOISTURE_MIN = 40.0  # % — paddy rice needs wet soil (analog mode only)

# =============================================================
# DATA TRANSMISSION
# =============================================================

# "wifi", "nbiot", or "auto" (auto-detect best available)
TRANSMISSION_MODE = "wifi"

# Server endpoint (set when you have a server ready)
SERVER_URL = None

# NB-IoT settings (configure when module arrives)
NBIOT_ENABLED = False
NBIOT_PORT = "/dev/ttyUSB0"
NBIOT_BAUD = 115200
NBIOT_APN = ""
