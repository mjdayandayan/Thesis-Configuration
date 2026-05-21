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
# RS485 NPK SOIL SENSOR (Nitrogen + Phosphorus + Potassium)
# =============================================================
# Sensor: RS485 NPK Soil Nutrient Sensor (separate from 5-in-1)
# Some 7-in-1 sensors include NPK in the same device.
# Set NPK_SENSOR_ENABLED = False if you don't have this sensor.
#
# Wiring: Same RS485 bus (A+/B-) but different slave address.
# If using the same adapter, change NPK_SLAVE_ADDRESS to differ from above.

NPK_SENSOR_ENABLED = True          # Set False to disable NPK sensor
NPK_PORT = "/dev/ttyUSB0"          # Same bus or separate adapter
NPK_BAUDRATE = 4800
NPK_SLAVE_ADDRESS = 2              # Different address from 5-in-1 sensor
NPK_TIMEOUT = 1

# NPK register addresses (common defaults for RS485 NPK sensors)
# Typical output: mg/kg (no division needed, raw value = mg/kg)
NPK_REG_NITROGEN = 0x001E         # Nitrogen register (value = mg/kg)
NPK_REG_PHOSPHORUS = 0x001F       # Phosphorus register (value = mg/kg)
NPK_REG_POTASSIUM = 0x0020        # Potassium register (value = mg/kg)
NPK_NUM_REGISTERS = 3             # N, P, K consecutive registers

# =============================================================
# CAMERA CONFIGURATION
# =============================================================

# Webcam: Logitech C922 Pro HD Stream Webcam
# - 1080p Full HD, glass lens, autofocus, IR-cut filter
# - USB plug-and-play (UVC compliant), RPi 5 compatible
CAMERA_INDEX = 0       # Usually 0 for first USB webcam
CAMERA_WIDTH = 1920    # C922 Full HD 1080p — higher res = better retraining frames
CAMERA_HEIGHT = 1080

# =============================================================
# EDGE IMPULSE MODEL
# =============================================================

# Current model: FOMO (MobileNetV2 0.35) — Edge Impulse
# Architecture: FOMO object detection (centroid-based)
# Classes: flowering, heading, mature, ripening
# Training: 100 cycles, LR 0.005, data augmentation enabled, 320x320 RGB
# Quantized int8 — F1: 0.64, Precision: 0.68, Recall: 0.59
# When you retrain, just swap the .eim file — no code changes needed.
MODEL_PATH = "/home/pi/thesis/models/rice-growth-monitoring-c922-runner-linux-aarch64-ethos-v1-impulse-#1.eim"
CONFIDENCE_THRESHOLD = 0.3  # FOMO with lower recall — use lower threshold to catch more detections

# =============================================================
# RETRAINING DATA CAPTURE
# =============================================================

# Save raw camera frames for uploading to Edge Impulse later.
# These 1080p frames from the Logitech C922 will significantly
# improve FOMO model accuracy when used as additional training data.
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
# NPK THRESHOLDS BY RICE GROWTH STAGE (mg/kg)
# =============================================================
# Based on: Dobermann & Fairhurst (2000); Shrestha et al. (2020);
#           Sulaeman et al. (2024)
# These represent optimal available soil concentrations (mg/kg) required
# to maximize yield and prevent nutrient deficiencies at each stage.
#
# Format: { "stage": {"n_min", "n_max", "p_min", "p_max", "k_min", "k_max"} }

NPK_THRESHOLDS = {
    "vegetative": {
        "n_min": 30, "n_max": 50,    # High N for leaf/tiller growth
        "p_min": 20, "p_max": 35,    # Root development
        "k_min": 80, "k_max": 120,   # Moderate K
        "description": "Early Tillering to Active Tillering",
        "focus": "Promotes active root development, leaf area expansion, and high tiller numbers.",
    },
    "heading": {
        "n_min": 20, "n_max": 35,    # N tapering slightly
        "p_min": 15, "p_max": 25,    # Moderate P
        "k_min": 100, "k_max": 150,  # High K for stalk strength
        "description": "Panicle Initiation & Booting",
        "focus": "Shift from structural growth to reproduction. Requires high K to boost spikelet numbers and prevent lodging.",
    },
    "flowering": {
        "n_min": 15, "n_max": 25,    # Moderate N for flag leaf
        "p_min": 15, "p_max": 20,    # Steady P for pollination
        "k_min": 90, "k_max": 130,   # Steady K for grain filling
        "description": "Anthesis & Pollination",
        "focus": "P accelerates clean flowering timelines, while K powers cellular transport for upcoming grain filling.",
    },
    "maturing": {
        "n_min": 0, "n_max": 15,     # Low N — high N delays maturation
        "p_min": 10, "p_max": 15,    # Reduced P
        "k_min": 60, "k_max": 90,    # Reduced K
        "description": "Milky to Golden Ripe Stage",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
    # Alias: model may output "mature" instead of "maturing"
    "mature": {
        "n_min": 0, "n_max": 15,
        "p_min": 10, "p_max": 15,
        "k_min": 60, "k_max": 90,
        "description": "Milky to Golden Ripe Stage",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
    # Alias: model may output "ripening"
    "ripening": {
        "n_min": 0, "n_max": 15,
        "p_min": 10, "p_max": 15,
        "k_min": 60, "k_max": 90,
        "description": "Milky to Golden Ripe Stage",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
}

# =============================================================
# DATA TRANSMISSION — SUPABASE
# =============================================================
# The RPi sends sensor data and images to Supabase.
# The Streamlit dashboard reads from the same Supabase project.
#
# To get these values:
#   1. Go to https://supabase.com/dashboard
#   2. Open your project
#   3. Go to Settings → API
#   4. Copy the "Project URL" and "anon/public" key

SUPABASE_URL = "https://wzxddmszyerunowrivhk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eGRkbXN6eWVydW5vd3JpdmhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg3NjI3NzgsImV4cCI6MjA5NDMzODc3OH0.CT1z0Exy0qQrOCSQpBZvS1nGYdoJ-0w3d9_iILA4aF8"
SUPABASE_BUCKET = "field-images"  # Storage bucket name for camera images

# Fallback: generic HTTP POST endpoint (if not using Supabase)
SERVER_URL = None
