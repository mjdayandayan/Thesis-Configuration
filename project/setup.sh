#!/bin/bash
# Rice Paddy Monitoring System — One-command setup
# Usage: cd ~/thesis && bash setup.sh
#
# This script:
#   1. Installs system-level dependencies (apt)
#   2. Creates a Python virtual environment (if not exists)
#   3. Installs all Python packages from requirements.txt
#   4. Creates project directories
#   5. Verifies the installation

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "=================================================="
echo " Rice Paddy Monitoring System — Setup"
echo "=================================================="
echo ""

# --- 1. System dependencies ---
echo "[1/5] Installing system dependencies..."
sudo apt update -qq
sudo apt install -y -qq libcap-dev v4l-utils libopencv-dev python3-opencv python3-venv > /dev/null 2>&1
echo "      Done."

# --- 2. Virtual environment ---
echo "[2/5] Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "      Created venv at $VENV_DIR"
else
    echo "      venv already exists — skipping creation."
fi
source "$VENV_DIR/bin/activate"

# --- 3. Python packages ---
echo "[3/5] Installing Python packages..."
pip install --upgrade pip --quiet
pip install -r "$PROJECT_DIR/requirements.txt" --quiet
echo "      Done."

# --- 4. Project directories ---
echo "[4/5] Creating project directories..."
mkdir -p "$PROJECT_DIR/src" "$PROJECT_DIR/config" "$PROJECT_DIR/logs" \
         "$PROJECT_DIR/data" "$PROJECT_DIR/models" "$PROJECT_DIR/data/retraining_frames"
touch "$PROJECT_DIR/src/__init__.py"
echo "      Done."

# --- 5. Verify ---
echo "[5/5] Verifying installation..."
echo ""
python3 -c "
import cv2
import minimalmodbus
import serial
import numpy
import PIL
import paho.mqtt
import requests

print('  cv2 (OpenCV)      :', cv2.__version__)
print('  minimalmodbus      :', minimalmodbus.__version__)
print('  pyserial           :', serial.__version__)
print('  numpy              :', numpy.__version__)
print('  pillow             :', PIL.__version__)
print('  paho-mqtt          : OK')
print('  requests           :', requests.__version__)
"

echo ""
echo "=================================================="
echo " Setup complete!"
echo " Activate with:  source venv/bin/activate"
echo " Run with:       python3 src/main.py --once"
echo "=================================================="
