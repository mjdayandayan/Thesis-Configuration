# Rice Monitoring System — Raspberry Pi 5 Setup Guide

> **Thesis:** "Rice Monitoring System Using Raspberry Pi V5 and Computer Vision"

---

## QUICKSTART (For Co-Researchers)

> **Already have the Pi, hardware, and this repo?** Follow this fast track. Each step references a detailed guide if you get stuck.

### Prerequisites
- Raspberry Pi 5 with Raspberry Pi OS 64-bit on SD card
- Logitech C922 Pro webcam + RS485 soil sensor + USB-to-RS485 adapter + 12V supply
- Laptop on the **same WiFi** as the Pi

### 1. Flash & Boot the Pi (5 min)
Use Raspberry Pi Imager → choose **Pi 5**, **Raspberry Pi OS 64-bit**, configure:
- Hostname: `trio` | Username: `pi` | Password: `raspberrypi`
- Enable SSH, enter your WiFi credentials
- Flash, insert SD card, power on the Pi
- *Detailed guide:* `1. Raspberry Pi Configuration.md`

### 2. SSH In & Set Up WiFi (5 min)
```bash
ssh pi@trio.local                   # password: raspberrypi
sudo apt update && sudo apt upgrade -y
```
Add any extra WiFi networks (home, school, hotspot) using `nmcli`:
```bash
sudo nmcli dev wifi connect "WiFi-Name" password "WiFi-Password"
```
- *Detailed guide:* `2. Command Prompt Configuration.md`

### 3. Wire the Hardware (10 min)
| Component | Action |
|---|---|
| **Webcam** | Plug into any Pi USB port |
| **Soil sensor Brown wire** | → USB-to-RS485 adapter **A+** |
| **Soil sensor Blue wire** | → USB-to-RS485 adapter **B-** |
| **Soil sensor Red wire** | → 12V supply **+** |
| **Soil sensor Black wire** | → 12V supply **-** |
| **USB-to-RS485 adapter** | Plug into Pi USB port |

> Power OFF the Pi before wiring. Yellow wire is optional (shield ground).
- *Detailed guide:* `3. Hardware Setup.md`

### 4. Install Software (10 min)
```bash
ssh pi@trio.local
mkdir -p ~/thesis
```
On your **laptop**, copy the project files:
```bash
scp -r project/* pi@trio.local:~/thesis/
```
Back on the **Pi**:
```bash
cd ~/thesis
bash setup.sh        # Installs everything — takes ~5-10 min
source venv/bin/activate
```
- *Detailed guide:* `4. Development Environment Setup.md`

### 5. Deploy the AI Model (2 min)
The model file is in `project/src/model/`. Copy it to the Pi:
```bash
scp "project/src/model/rice-growth-monitoring-c922-runner-linux-aarch64-ethos-v1-impulse-#1.eim" pi@trio.local:~/thesis/models/
```
On the Pi, make it executable:
```bash
chmod +x ~/thesis/models/rice-growth-monitoring-c922-runner-linux-aarch64-ethos-v1-impulse-#1.eim
```
> `MODEL_PATH` in `config/settings.py` is already set to this filename. No edits needed.

### 6. Test Each Component (5 min)
On the Pi (with `venv` activated and `cd ~/thesis`):

**Soil sensor** (make sure 12V is ON):
```bash
python3 -c "
from src.sensors import SoilSensorRS485
s = SoilSensorRS485(); r = s.read()
print(r) if r else print('FAIL: check wiring/12V')
s.cleanup()
"
```

**Camera**:
```bash
python3 -c "
from src.camera import Camera
c = Camera(); f = c.capture_frame()
print(f'OK: {f.shape}') if f is not None else print('FAIL: replug camera')
c.release()
"
```

**AI model** (needs both camera and model file):
```bash
python3 src/main.py --once
```

### 7. Run the System
```bash
# Single reading (quick test)
python3 src/main.py --once

# Continuous monitoring
python3 src/main.py          # Ctrl+C to stop
```

### 8. Start the Web Dashboard (on your laptop)
```bash
cd ui
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

### Quick Troubleshooting

| Problem | Fix |
|---|---|
| Can't SSH to `trio.local` | Pi not on same WiFi. Wait 1-2 min after boot. |
| Sensor returns None/zeros | Check 12V is ON. Try swapping A+ and B- wires. |
| Camera fails | Unplug/replug webcam. Try `CAMERA_INDEX = 1` in settings. |
| `ModuleNotFoundError` | Run `source venv/bin/activate` first. |
| Model file error | Check `chmod +x` was run. Verify filename matches `MODEL_PATH`. |

---

> **Need more detail on any step?** Read the numbered guide files (1–7) in this repo. They explain every command in depth.

---

This guide walks you through **everything** — from a fresh Raspberry Pi to a working rice paddy monitoring system. Each step is numbered and explained. Follow them **in order**.

---

## What Does This System Do?

This system monitors rice paddies using:

1. **A Logitech C922 Pro webcam** — takes photos of the rice field
2. **A soil sensor** — measures 5 soil properties (moisture, temperature, humidity, pH, electrical conductivity)
3. **A Raspberry Pi 5** — the small computer that runs everything, processes the photos with an AI model (Edge Impulse), and sends the data over WiFi

The AI model (FOMO MobileNetV2 0.35) identifies the growth stage of the rice (flowering, heading, mature, ripening) from camera images.

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
| 6 | **Logitech C922 Pro HD Stream Webcam** | Takes photos of the rice field (1080p, autofocus, glass lens, IR-cut filter) |
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
| **8** | `README.md → Dashboard` | Set up Supabase and run the Streamlit web dashboard | ~20 min |

---

## Project Structure (What's on the Pi)

After setup, the project folder on the Pi (`~/thesis/`) looks like this:

```
~/thesis/
├── setup.sh                         # One-command setup script (Step 4)
├── requirements.txt                 # List of Python packages to install
├── venv/                            # Python virtual environment (auto-created)
├── models/
│   └── rice-growth-monitoring-c922-runner-linux-aarch64-ethos-v1-impulse-#1.eim  # The AI model file from Edge Impulse
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

The **web dashboard** (on your laptop, not on the Pi) is in the `ui/` folder:

```
ui/
├── app.py                           # Main dashboard page (metrics, detection, recent readings)
├── requirements.txt                 # Python packages for the dashboard
├── supabase_setup.sql               # SQL to create the database table (run once in Supabase)
├── .streamlit/
│   ├── config.toml                  # Streamlit theme and server settings
│   ├── secrets.toml                 # Supabase credentials (DO NOT commit to git)
│   └── secrets.toml.example         # Template — copy to secrets.toml and fill in your keys
├── pages/
│   ├── 1_Historical_Data.py         # Soil sensor trend charts over time
│   ├── 2_Camera_Gallery.py          # Grid view of captured field images
│   └── 3_Alerts.py                  # Alert log for threshold violations
└── utils/
    ├── __init__.py
    └── supabase_client.py           # Supabase connection and data queries
```

> **You don't need to create these manually.** The setup script (`setup.sh`) in Step 4 creates the Pi-side folders for you. The `ui/` folder is already in this repository.

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
| **Start the web dashboard** | `cd ui && streamlit run app.py` | **On your laptop** |
| Open dashboard in browser | Visit `http://localhost:8501` | **On your laptop** |

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
| Dashboard shows "No data received yet" | The Pi hasn't sent any data to Supabase yet. Run `python3 src/main.py --once` on the Pi to send a test reading. |
| Dashboard shows a Supabase connection error | Check that `ui/.streamlit/secrets.toml` has the correct `SUPABASE_URL` and `SUPABASE_KEY`. Also check that the Pi's `config/settings.py` has the same values. |
| Dashboard doesn't show images | Make sure the `field-images` Storage bucket exists in Supabase with public SELECT and INSERT policies. |

