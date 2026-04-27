# Thesis-Configuration

Step-by-step guide to configure a **Raspberry Pi 5** for the thesis:
**"NB-IoT Enabled Rice Monitoring System Using Raspberry Pi V5 and Computer Vision"**

---

## Context / Original Prompt

> My thesis involves rice paddy monitoring using Raspberry Pi 5, a USB web camera, a temperature and humidity sensor, and a soil moisture sensor. I used Edge Impulse to train my computer vision model.
>
> - I already have a computer vision model
> - I need to configure and code (especially the sensors) in VSCode
> - I need to configure it where I don't have to start all over again whenever the WiFi/internet changes, especially since I'll have to integrate NB-IoT on it if my modules arrive.
> - I'll be using digital pins for the soil moisture sensor as of now since I don't have an ADC module yet
> - It's not sure yet, but I think I'll use SIM7080G NB-IoT and a GOMO card for CAT-M1 since PLDT haven't answered me for months in regards to their NB-IoT SIM card.

---

## Project Overview

| Component | Details |
|---|---|
| **Board** | Raspberry Pi 5 (headless, 64-bit OS) |
| **Computer Vision** | Edge Impulse FOMO model (`.eim`, Linux AARCH64) — interim deployment (F1 46.1%), will retrain after hardware integration |
| **Camera** | USB Webcam (`/dev/video0`) |
| **Temp / Humidity** | DHT22 sensor on GPIO4 |
| **Soil Moisture** | Digital output (DO) pin on GPIO17 — no ADC needed for now |
| **Future ADC** | ADS1115 (16-bit, I2C) for analog soil moisture readings |
| **Connectivity** | WiFi (primary) → NB-IoT via SIM7080G + GOMO CAT-M1 SIM (future, for field deployment) |
| **Dev Workflow** | VS Code Remote-SSH into the Pi |
| **Project Dir** | `~/thesis/` on the Pi |

### Key Design Decisions

1. **WiFi portability** — NetworkManager is pre-configured with every WiFi network you'll use (home, school, lab, hotspot). The Pi auto-connects to the highest-priority available network on boot. You never have to reconfigure when moving locations.

2. **Digital soil moisture (no ADC)** — The soil moisture sensor module's DO (digital output) pin is connected directly to GPIO17. It reads HIGH (dry) or LOW (wet). The threshold is adjusted with the potentiometer on the sensor module. When the ADS1115 ADC arrives, change one setting in `config/settings.py` to switch to analog mode.

3. **NB-IoT future-proofing** — The SIM7080G module (with GOMO CAT-M1 SIM) will be added as the lowest-priority network fallback. The code already has NB-IoT stubs in `src/transmit.py`. NetworkManager will handle automatic failover from WiFi → NB-IoT.

---

## Materials Needed

### Hardware
1. Laptop (for development)
2. Raspberry Pi 5
3. USB-C Power Supply (5V 5A recommended)
4. Micro SD Card (minimum 32 GB)
5. SD Card Reader
6. USB Web Camera
7. DHT22 Temperature and Humidity Sensor
8. Soil Moisture Sensor Module (with digital output pin)
9. Jumper Wires
10. *(Future)* ADS1115 ADC Module (16-bit, I2C) — for analog soil moisture
11. *(Future)* SIM7080G NB-IoT Module + GOMO CAT-M1 SIM

### Software
1. [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Command Prompt / PowerShell
3. [Visual Studio Code](https://code.visualstudio.com/) with Remote-SSH extension
4. [Edge Impulse](https://www.edgeimpulse.com/) account (model already trained)

---

## Configuration Steps

Follow the numbered files in this repository **in order**:

### Step 1 — Raspberry Pi Configuration
Flash Raspberry Pi OS (64-bit) to the SD card using Raspberry Pi Imager. Set hostname (`trio`), username/password (`pi`/`raspberrypi`), WiFi credentials, and enable SSH. Insert the SD card and boot the Pi headless.

### Step 2 — Command Prompt Configuration
SSH into the Pi (`ssh pi@trio.local`). Run system updates. **Configure multiple WiFi networks** using `nmcli` so the Pi auto-connects wherever you take it — home, school, lab, or mobile hotspot. Set priorities so the preferred network is used first. Create a reference file for future NB-IoT integration.

### Step 3 — Hardware Setup
Wire the components:
- **DHT22**: 3.3V (Pin 1) → VCC, GPIO4 (Pin 7) → DATA, GND (Pin 9) → GND
- **Soil Moisture (digital)**: 3.3V (Pin 17) → VCC, GND (Pin 20) → GND, GPIO17 (Pin 11) → DO
- **USB Webcam**: Plug into any USB port
- **Future ADS1115**: SDA (Pin 3), SCL (Pin 5), 3.3V, GND → ADS1115; AO from soil sensor → A0

Enable I2C via `raspi-config` (for future ADC). Test the webcam with `v4l2-ctl --list-devices`.

### Step 4 — Development Environment Setup
Create the project directory (`~/thesis/`), set up a Python virtual environment, and install all dependencies:
- `adafruit-circuitpython-dht` — DHT22 sensor
- `RPi.GPIO` — digital GPIO for soil moisture
- `opencv-python-headless` — camera/image processing
- `edge_impulse_linux` — model inference
- `paho-mqtt`, `requests` — data transmission

Create the project folder structure: `src/`, `config/`, `models/`, `logs/`, `data/`.

### Step 5 — VSCode Configuration
Install the **Remote-SSH** extension in VS Code. Connect to `pi@trio.local`, open `/home/pi/thesis`, and select the venv Python interpreter. Deploy project files from the `project/` folder in this repo (via SCP or direct copy). If WiFi changes and you lose connection, just reconnect — the Pi auto-connects to saved networks and all files are preserved.

### Step 6 — Running and Testing
Download the Edge Impulse model (Linux AARCH64 `.eim`) and copy it to `~/thesis/models/`. Make it executable. Test each component individually:
- DHT22 sensor readings
- Soil moisture digital output
- Camera frame capture
- Edge Impulse inference

Run the full system: `python3 src/main.py --once` (single reading) or `python3 src/main.py` (continuous). Optionally set up a `systemd` service for auto-start on boot.

### Step 7 — Sensor Calibration
**Soil moisture (digital mode):** Adjust the potentiometer on the sensor module until it reliably switches between wet/dry at your desired threshold. Run the calibration test script to verify.

**DHT22:** No calibration needed — just verify readings are reasonable.

**Future analog calibration:** When ADS1115 arrives, run the calibration script to record raw ADC values for dry air and water, then update `config/settings.py`.

### Step 8 — NB-IoT Integration (Future)
When the **SIM7080G** module and **GOMO CAT-M1 SIM** arrive:
1. Connect via USB (appears as `/dev/ttyUSB0`) or UART
2. Install `pyserial`, test AT commands
3. Add NB-IoT as the lowest-priority network via `nmcli`
4. Update `config/settings.py` with NB-IoT settings
5. Update `src/transmit.py` with SIM7080G AT command sequences
6. The system auto-falls back to NB-IoT when WiFi is unavailable

---

## Project Structure (on the Pi)

```
~/thesis/
├── venv/                            # Python virtual environment
├── models/
│   └── your-edge-impulse-model.eim  # Edge Impulse model file
├── src/
│   ├── __init__.py
│   ├── sensors.py                   # DHT22 + soil moisture (digital/analog)
│   ├── camera.py                    # USB webcam capture
│   ├── inference.py                 # Edge Impulse model inference
│   ├── transmit.py                  # Data transmission (WiFi/NB-IoT)
│   └── main.py                      # Main monitoring loop
├── config/
│   └── settings.py                  # All configuration in one place
├── logs/                            # Runtime logs
├── data/                            # Saved sensor data and images
│   └── retraining_frames/           # Raw frames for Edge Impulse retraining
└── requirements.txt                 # Python dependencies
```

---

## Quick Reference

| Task | Command |
|---|---|
| SSH into Pi | `ssh pi@trio.local` |
| Activate venv | `cd ~/thesis && source venv/bin/activate` |
| Test sensors | `python3 src/sensors.py` |
| Test camera | `python3 src/camera.py` |
| Single reading | `python3 src/main.py --once` |
| Continuous monitoring | `python3 src/main.py` |
| Check service status | `sudo systemctl status thesis.service` |
| View live logs | `journalctl -u thesis.service -f` |
| List saved WiFi networks | `nmcli connection show` |
| Add a new WiFi network | `sudo nmcli connection add type wifi ifname wlan0 con-name "NAME" ssid "SSID"` |

---

## Current Setup Mode
- **Edge Impulse Model**: Interim FOMO MobileNetV2 0.35 (F1 46.1%) — deployed for hardware integration testing
- **Retraining Plan**: The system automatically saves camera frames from the Pi to `~/thesis/data/retraining_frames/`. Upload these to Edge Impulse as new training data, then retrain with improved settings (FOMO MobileNetV2 0.1, 416×416 input, learned optimizer, 150 cycles, LR 0.001). Swap the new `.eim` file — no code changes needed.
- **Soil Moisture**: Using **digital output (DO)** pin → GPIO reads HIGH/LOW (no ADC needed)
- When ADC module arrives, change `SOIL_SENSOR_MODE = "analog"` in `config/settings.py`
- **NB-IoT**: Stubs ready in code. Activate when SIM7080G + GOMO SIM arrive
