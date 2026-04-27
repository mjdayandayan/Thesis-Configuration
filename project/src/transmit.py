"""
Data transmission module — sends data via WiFi.
"""

import json
import subprocess

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import TRANSMISSION_MODE, SERVER_URL


class DataTransmitter:
    """Handles data transmission to remote server via WiFi."""

    def __init__(self, mode=TRANSMISSION_MODE):
        self.mode = mode
        self.server_url = SERVER_URL

    def send(self, data):
        """Send data via WiFi (HTTP POST)."""
        if not self.server_url:
            print(f"[WiFi] No server URL configured. Data: {json.dumps(data)[:100]}...")
            return False

        import requests
        try:
            response = requests.post(
                self.server_url,
                json=data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[WiFi] Send failed: {e}")
            return False

    def check_connection(self):
        """Check if network connection is available."""
        try:
            subprocess.check_call(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
