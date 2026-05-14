"""
Data transmission module — sends sensor data and images to Supabase.
Falls back to generic HTTP POST if Supabase is not configured.
"""

import json
import os
import subprocess
import requests

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import SERVER_URL, SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET


class DataTransmitter:
    """Sends monitoring data to Supabase (primary) or a generic HTTP endpoint (fallback)."""

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        self.supabase_bucket = SUPABASE_BUCKET
        self.server_url = SERVER_URL

    @property
    def is_configured(self):
        """Check if any transmission target is configured."""
        return bool(self.supabase_url and self.supabase_key) or bool(self.server_url)

    def send(self, data):
        """Send data to configured target. Returns True on success."""
        # Primary: Supabase
        if self.supabase_url and self.supabase_key:
            return self._send_to_supabase(data)

        # Fallback: generic HTTP POST
        if self.server_url:
            return self._send_http(data)

        print("[Transmit] No target configured — set SUPABASE_URL/KEY in config/settings.py")
        return False

    def _send_to_supabase(self, data):
        """Upload image to Supabase Storage + insert reading to Supabase table."""
        try:
            # Upload image if available
            image_url = None
            image_path = data.get('image_path')
            if image_path and os.path.exists(image_path):
                image_url = self._upload_image(image_path)

            # Flatten nested data for the readings table
            soil = data.get('soil_data') or {}
            prediction = data.get('prediction') or {}

            record = {
                'timestamp': data.get('timestamp'),
                'soil_moisture': soil.get('soil_moisture'),
                'soil_temperature': soil.get('soil_temperature'),
                'ec': soil.get('ec'),
                'ph': soil.get('ph'),
                'soil_humidity': soil.get('soil_humidity'),
                'prediction_label': prediction.get('label'),
                'prediction_confidence': prediction.get('confidence'),
                'detections': data.get('detections', []),
                'image_url': image_url,
                'alerts': data.get('alerts', [])
            }

            response = requests.post(
                f"{self.supabase_url}/rest/v1/readings",
                headers={
                    'apikey': self.supabase_key,
                    'Authorization': f'Bearer {self.supabase_key}',
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                json=record,
                timeout=15
            )

            if response.status_code == 201:
                print("[Supabase] Data sent successfully")
                return True
            else:
                print(f"[Supabase] Insert failed ({response.status_code}): {response.text}")
                return False

        except Exception as e:
            print(f"[Supabase] Send failed: {e}")
            return False

    def _upload_image(self, image_path):
        """Upload image to Supabase Storage. Returns public URL or None."""
        try:
            filename = os.path.basename(image_path)
            with open(image_path, 'rb') as f:
                response = requests.post(
                    f"{self.supabase_url}/storage/v1/object/{self.supabase_bucket}/{filename}",
                    headers={
                        'apikey': self.supabase_key,
                        'Authorization': f'Bearer {self.supabase_key}',
                        'Content-Type': 'image/jpeg',
                        'x-upsert': 'true'
                    },
                    data=f,
                    timeout=30
                )

            if response.status_code in (200, 201):
                public_url = (
                    f"{self.supabase_url}/storage/v1/object/public/"
                    f"{self.supabase_bucket}/{filename}"
                )
                return public_url
            else:
                print(f"[Supabase] Image upload failed ({response.status_code}): {response.text}")
                return None

        except Exception as e:
            print(f"[Supabase] Image upload error: {e}")
            return None

    def _send_http(self, data):
        """Send data via generic HTTP POST (fallback)."""
        try:
            response = requests.post(self.server_url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[HTTP] Send failed: {e}")
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
