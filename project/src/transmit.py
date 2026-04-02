"""
Data transmission module — supports WiFi and NB-IoT.
"""

import json
import subprocess

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import TRANSMISSION_MODE, SERVER_URL


class DataTransmitter:
    """Handles data transmission to remote server."""

    def __init__(self, mode=TRANSMISSION_MODE):
        self.mode = mode
        self.server_url = SERVER_URL

    def send(self, data):
        """Send data using the configured mode."""
        active = self._get_active_connection() if self.mode == "auto" else self.mode

        if active == "nbiot":
            return self._send_nbiot(data)
        else:
            return self._send_wifi(data)

    def _send_wifi(self, data):
        """Send via WiFi (HTTP POST)."""
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

    def _send_nbiot(self, data):
        """Send via NB-IoT. Implement when module arrives."""
        print(f"[NB-IoT] Not yet implemented. Data: {json.dumps(data)[:100]}...")
        return False

    def check_connection(self):
        """Check if any network connection is available."""
        try:
            subprocess.check_call(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_active_connection(self):
        """Detect which network type is currently active."""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'TYPE,STATE', 'connection', 'show', '--active'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split('\n'):
                if 'ethernet:activated' in line:
                    return 'wifi'  # treat ethernet same as wifi for transmission
                if 'wifi:activated' in line:
                    return 'wifi'
                if 'gsm:activated' in line:
                    return 'nbiot'
        except Exception:
            pass
        return 'wifi'  # default fallback
