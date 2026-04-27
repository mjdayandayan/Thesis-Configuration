"""
Configuration settings for Rice Paddy Monitoring System
Edit these values for your specific setup.
"""

# =============================================================
# RS485 5-IN-1 SOIL SENSOR (pH + Temp + Humidity + EC + Moisture)
# =============================================================
# Sensor: RS485 Output 5Pin Probes Soil Sensor with Cable 2M
# Protocol: Modbus RTU over RS485
# Connection: USB-to-RS485 adapter → Raspberry Pi USB port
#
# Wiring:
#   Sensor Brown  → RS485 adapter A+ (Data+)
#   Sensor Blue   → RS485 adapter B- (Data-)
#   Sensor Black  → Power supply GND
#   Sensor Red    → Power supply 12V (or 5–24V depending on model)
#   Sensor Yellow → (shield/ground, optional)
#
# The USB-to-RS485 adapter appears as /dev/ttyUSB0 (or /dev/ttyUSB1)

RS485_PORT = "/dev/ttyUSB0"       # Serial port for USB-to-RS485 adapter
RS485_BAUDRATE = 4800             # Common default; check sensor datasheet (4800 or 9600)
RS485_SLAVE_ADDRESS = 1           # Modbus slave address (default 0x01, check datasheet)
RS485_TIMEOUT = 1                 # Serial timeout in seconds

# Modbus register addresses (ADJUST THESE to match your sensor's datasheet)
# These are common defaults for RS485 5-in-1 soil sensors.
# The register addresses and data format vary by manufacturer.
RS485_REG_MOISTURE = 0x0000       # Soil moisture register (value / 10 = %)
RS485_REG_TEMPERATURE = 0x0001   # Soil temperature register (value / 10 = °C)
RS485_REG_EC = 0x0002            # Electrical conductivity register (value = µS/cm)
RS485_REG_PH = 0x0003            # pH register (value / 10 = pH)
RS485_REG_HUMIDITY = 0x0004      # Soil humidity register (value / 10 = %)
RS485_NUM_REGISTERS = 5          # Number of consecutive registers to read

# =============================================================
# CAMERA CONFIGURATION
# =============================================================

# Webcam: USB Web Camera A4Tech
CAMERA_INDEX = 0       # Usually 0 for first USB webcam
CAMERA_WIDTH = 640     # Higher res = better retraining frames
CAMERA_HEIGHT = 480

# =============================================================
# EDGE IMPULSE MODEL
# =============================================================

# Current model: FOMO MobileNetV2 0.35 (interim, F1 46.1%)
# Will be replaced after retraining with improved settings.
# When you retrain, just swap the .eim file — no code changes needed.
MODEL_PATH = "/home/pi/thesis/models/your-model.eim"
CONFIDENCE_THRESHOLD = 0.6  # Ignore predictions below this confidence

# =============================================================
# RETRAINING DATA CAPTURE
# =============================================================

# Save raw camera frames for uploading to Edge Impulse later.
# These frames from the real deployment camera will significantly
# improve model accuracy when used as additional training data.
SAVE_RETRAINING_FRAMES = True
RETRAINING_DIR = "/home/pi/thesis/data/retraining_frames"
RETRAINING_INTERVAL = 10  # Save every Nth capture (1 = every, 10 = every 10th)

# =============================================================
# DATA LOGGING
# =============================================================

LOG_INTERVAL_SECONDS = 300  # Log every 5 minutes
DATA_DIR = "/home/pi/thesis/data"
LOG_DIR = "/home/pi/thesis/logs"

# =============================================================
# ALERT THRESHOLDS (adjust for rice paddy requirements)
# =============================================================

# RS485 5-in-1 sensor thresholds
SOIL_MOISTURE_MIN = 40.0      # % — paddy rice needs wet soil
SOIL_PH_MIN = 5.5             # Ideal rice paddy pH range: 5.5–7.0
SOIL_PH_MAX = 7.0
SOIL_EC_MIN = 200             # µS/cm — minimum EC for rice
SOIL_EC_MAX = 2000            # µS/cm — above this indicates salinity issues
SOIL_TEMP_MIN = 18.0          # °C — soil too cold for rice
SOIL_TEMP_MAX = 35.0          # °C — soil too hot

# =============================================================
# DATA TRANSMISSION
# =============================================================

TRANSMISSION_MODE = "wifi"

# Server endpoint (set when you have a server ready)
SERVER_URL = None
