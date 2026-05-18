"""
Weather Context for the Rice Field Monitor.
Fetches current weather from Open-Meteo API (free, no API key needed).
"""

import streamlit as st
import requests


@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_weather(latitude=8.2, longitude=123.85):
    """Fetch current weather from Open-Meteo API.

    Default coordinates: Clarin, Misamis Occidental (adjust in secrets.toml).
    Returns dict with temperature, humidity, rain, wind, description.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
            f"&timezone=auto"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get('current', {})

        # Map WMO weather codes to descriptions
        code = current.get('weather_code', 0)
        weather_desc = _weather_code_to_text(code)
        weather_icon = _weather_code_to_icon(code)

        return {
            'temperature': current.get('temperature_2m'),
            'humidity': current.get('relative_humidity_2m'),
            'precipitation': current.get('precipitation', 0),
            'wind_speed': current.get('wind_speed_10m'),
            'description': weather_desc,
            'icon': weather_icon,
            'ok': True,
        }
    except Exception:
        return {'ok': False}


def _weather_code_to_text(code):
    """Convert WMO weather code to human-readable text."""
    mapping = {
        0: 'Clear sky',
        1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Foggy', 48: 'Foggy',
        51: 'Light drizzle', 53: 'Drizzle', 55: 'Heavy drizzle',
        61: 'Light rain', 63: 'Rain', 65: 'Heavy rain',
        71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
        80: 'Light showers', 81: 'Showers', 82: 'Heavy showers',
        95: 'Thunderstorm', 96: 'Thunderstorm w/ hail', 99: 'Severe thunderstorm',
    }
    return mapping.get(code, 'Unknown')


def _weather_code_to_icon(code):
    """Convert WMO weather code to emoji icon."""
    if code == 0:
        return '☀️'
    elif code <= 3:
        return '⛅'
    elif code <= 48:
        return '🌫️'
    elif code <= 55:
        return '🌦️'
    elif code <= 65:
        return '🌧️'
    elif code <= 75:
        return '❄️'
    elif code <= 82:
        return '🌧️'
    elif code >= 95:
        return '⛈️'
    return '🌤️'
