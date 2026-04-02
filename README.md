# Thesis-Configuration

How to configure Raspberry Pi 5 for thesis **"NB-IoT Enabled Rice Monitoring System Using Raspberry Pi V5 and Computer Vision"**

## Project Overview
- **Computer Vision**: Edge Impulse model (.eim) for rice paddy disease/health detection
- **Sensors**: DHT22 (temperature/humidity) + Soil Moisture Sensor (digital output)
- **Camera**: USB Webcam
- **Connectivity**: WiFi (primary) → NB-IoT (future, for field deployment)
- **Project Directory on Pi**: `~/thesis/`

## Materials Needed
1. Laptop
2. Raspberry Pi V5
3. Power Supply (USB-C, 5V 5A recommended)
4. Micro SD Card (Minimum 32 GB)
5. SD Card Reader
6. USB Web Camera
7. Soil Moisture Sensor (module with digital output pin)
8. DHT22 Temperature and Humidity Sensor
9. Jumper Wires
10. *(Future)* ADS1115 ADC Module (16-bit, I2C) — for analog soil moisture readings
11. *(Future)* NB-IoT Module + SIM

## Software Needed
1. Raspberry Pi Imager
2. Command Prompt / PowerShell
3. Visual Studio Code (with Remote-SSH extension)
4. Edge Impulse account (model already trained)

## Configuration Steps
Follow the numbered files in order:
1. **Raspberry Pi Configuration** — Flash OS and initial setup
2. **Command Prompt Configuration** — SSH access, system updates, multi-WiFi setup
3. **Hardware Setup** — Wiring diagram and pin connections
4. **Development Environment Setup** — Python venv, dependencies
5. **VSCode Configuration** — Remote-SSH development workflow
6. **Running and Testing** — Deploy model, test components, run system
7. **Sensor Calibration** — Calibrate soil moisture thresholds
8. **NB-IoT Integration** — Future connectivity module

## Current Setup Mode
- **Soil Moisture**: Using **digital output (DO)** pin → GPIO reads HIGH/LOW (no ADC needed)
- When ADC module arrives, switch to analog mode in `config/settings.py`
