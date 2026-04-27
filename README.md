# Rice Monitoring System — Raspberry Pi 5 Setup Guide

> **Thesis:** "Rice Monitoring System Using Raspberry Pi V5 and Computer Vision"

This guide walks you through **everything** — from a fresh Raspberry Pi to a working rice paddy monitoring system. Each step is numbered and explained. Follow them **in order**.

---

## What Does This System Do?

This system monitors rice paddies using:

1. **A USB webcam (A4Tech)** — takes photos of the rice field
2. **A soil sensor** — measures 5 soil properties (moisture, temperature, humidity, pH, electrical conductivity)
3. **A Raspberry Pi 5** — the small computer that runs everything, processes the photos with an AI model (Edge Impulse), and sends the data over WiFi

The AI model identifies the growth stage of the rice (booting, flowering, maturing, vegetative) and detects weed growth from camera images.

---

## What You Need Before Starting

### Hardware (physical items)

| # | Item | What It's For |
|---|---|---|
| 1 | **Laptop or Desktop PC** | You'll use this to set up and control the Pi remotely |
| 2 | **Raspberry Pi 5** | The small computer that runs the monitoring system |
| 3 | **USB-C Power Supply** (5V 5A) | Powers the Raspberry Pi |
| 4 | **Micro SD Card** (32 GB or larger) | Storage for the Pi's operating system and your project |
| 5 | **SD Card Reader** | Plugs into your laptop so you can write the OS to the SD card |
| 6 | **USB Web Camera (A4Tech)** | Takes photos of the rice field |
| 7 | **RS485 5-in-1 Soil Sensor** | Measures pH, temperature, humidity, EC, and moisture of the soil |
| 8 | **USB-to-RS485 Adapter** | Connects the soil sensor to the Pi (the Pi can't read RS485 directly) |
| 9 | **12V DC Power Supply** | Powers the soil sensor (it needs more power than the Pi can provide) |
| 10 | **Jumper Wires** | For connecting wires between components |

### Software (download these to your laptop)

| # | Software | Download Link | What It's For |
|---|---|---|---|
| 1 | **Raspberry Pi Imager** | [raspberrypi.com/software](https://www.raspberrypi.com/software/) | Writes the operating system to the SD card |
| 2 | **Visual Studio Code (VS Code)** | [code.visualstudio.com](https://code.visualstudio.com/) | Code editor — you'll use it to edit files on the Pi remotely |
| 3 | **Edge Impulse account** | [edgeimpulse.com](https://www.edgeimpulse.com/) | Where the AI model is trained (already done) |

> **Tip:** You do NOT need a monitor, keyboard, or mouse for the Raspberry Pi. Everything is done remotely from your laptop. This is called **"headless"** mode.

---

## Steps Overview

Follow the numbered files in this repository **in order**. Do NOT skip steps.

| Step | File | What You'll Do | Time |
|---|---|---|---|
| **1** | `1. Raspberry Pi Configuration` | Write the operating system to the SD card and boot the Pi for the first time | ~15 min |
| **2** | `2. Command Prompt Configuration` | Connect to the Pi from your laptop, update it, and set up WiFi networks | ~20 min |
| **3** | `3. Hardware Setup` | Plug in the webcam and wire the soil sensor | ~15 min |
| **4** | `4. Development Environment Setup` | Install all the software the project needs on the Pi | ~10 min |
| **5** | `5. VSCode Configuration` | Set up VS Code on your laptop to edit code on the Pi remotely | ~10 min |
| **6** | `6. Running and Testing` | Deploy the AI model, test each component, run the full system | ~30 min |
| **7** | `7. Sensor Calibration` | Verify the soil sensor is giving correct readings | ~10 min |

---

## Project Structure (What's on the Pi)

After setup, the project folder on the Pi (`~/thesis/`) looks like this:

```
~/thesis/
├── setup.sh                         # One-command setup script (Step 4)
├── requirements.txt                 # List of Python packages to install
├── venv/                            # Python virtual environment (auto-created)
├── models/
│   └── your-model.eim               # The AI model file from Edge Impulse
├── src/
│   ├── __init__.py                  # (required by Python — don't delete)
│   ├── sensors.py                   # Code that reads the RS485 soil sensor
│   ├── camera.py                    # Code that captures webcam photos
│   ├── inference.py                 # Code that runs the AI model on photos
│   ├── transmit.py                  # Code that sends data over WiFi
│   └── main.py                      # The main program that ties everything together
├── config/
│   └── settings.py                  # All settings in one place (sensor ports, thresholds, etc.)
├── logs/                            # System logs (created automatically)
└── data/                            # Saved sensor data and captured images
    └── retraining_frames/           # Photos saved for retraining the AI model later
```

> **You don't need to create this manually.** The setup script (`setup.sh`) in Step 4 creates all these folders for you.

---

## Quick Reference (Cheat Sheet)

Once everything is set up, here are the commands you'll use most often. Run these on the Pi (via SSH or VS Code terminal):

| What You Want to Do | Command | Where to Run |
|---|---|---|
| Connect to the Pi from your laptop | `ssh pi@trio.local` | Your laptop's terminal |
| Activate the Python environment | `cd ~/thesis && source venv/bin/activate` | On the Pi |
| Test the soil sensor | `python3 src/sensors.py` | On the Pi |
| Test the camera | `python3 src/camera.py` | On the Pi |
| Take a single reading (quick test) | `python3 src/main.py --once` | On the Pi |
| Start continuous monitoring | `python3 src/main.py` | On the Pi |
| Stop continuous monitoring | Press `Ctrl+C` | On the Pi |
| Check if auto-start service is running | `sudo systemctl status thesis.service` | On the Pi |
| View live system logs | `journalctl -u thesis.service -f` | On the Pi |
| See saved WiFi networks | `nmcli connection show` | On the Pi |

---

## Troubleshooting (Common Problems)

| Problem | Solution |
|---|---|
| `ssh: Could not resolve hostname trio.local` | The Pi isn't on the same WiFi as your laptop. Make sure both devices are connected to the same network. Wait 1–2 minutes after powering on the Pi. |
| `Permission denied (publickey,password)` | You typed the wrong password. The default is `raspberrypi`. |
| Pi won't connect to WiFi after moving locations | You need to pre-configure WiFi networks in Step 2. The Pi can only connect to networks it already knows about. |
| `ModuleNotFoundError: No module named 'xxx'` | You forgot to activate the virtual environment. Run: `cd ~/thesis && source venv/bin/activate` |
| Soil sensor returns `None` or all zeros | Check wiring (Step 3). Make sure the 12V power supply is plugged in. Try swapping the A+ and B- wires. |
| Camera test says "Failed to capture" | Unplug and re-plug the USB webcam. Run `v4l2-ctl --list-devices` to check if the Pi sees it. |
| VS Code can't connect to Pi | Make sure the Pi is powered on and connected to WiFi. Try `ssh pi@trio.local` from your laptop's terminal first. |

