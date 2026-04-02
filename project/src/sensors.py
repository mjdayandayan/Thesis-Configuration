"""
Sensor interfaces for DHT22 (temperature/humidity) and soil moisture.
Supports both digital GPIO mode (no ADC) and analog ADS1115 mode.
"""

import time
import board
import adafruit_dht

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import (
    DHT_PIN, SOIL_SENSOR_MODE, SOIL_DIGITAL_PIN,
    SOIL_MOISTURE_CHANNEL, SOIL_DRY, SOIL_WET
)


class DHTSensor:
    """Interface for DHT22 temperature and humidity sensor."""

    def __init__(self, pin=DHT_PIN):
        self.pin = getattr(board, f"D{pin}")
        self.sensor = adafruit_dht.DHT22(self.pin, use_pulseio=False)
        self._last_temp = None
        self._last_humidity = None

    def read(self, retries=3):
        """
        Read temperature and humidity with retry logic.
        Returns dict {'temperature': float, 'humidity': float} or None.
        """
        for attempt in range(retries):
            try:
                temperature = self.sensor.temperature
                humidity = self.sensor.humidity

                if temperature is not None and humidity is not None:
                    self._last_temp = round(temperature, 2)
                    self._last_humidity = round(humidity, 2)
                    return {
                        'temperature': self._last_temp,
                        'humidity': self._last_humidity
                    }
            except RuntimeError as e:
                print(f"DHT read attempt {attempt + 1} failed: {e}")
                time.sleep(2)
            except Exception as e:
                print(f"Unexpected DHT error: {e}")
                time.sleep(2)

        if self._last_temp is not None:
            print("Returning cached DHT values")
            return {
                'temperature': self._last_temp,
                'humidity': self._last_humidity
            }
        return None

    def cleanup(self):
        self.sensor.exit()


class SoilMoistureSensor:
    """
    Soil moisture sensor using DIGITAL output (DO) pin.
    Reads GPIO: LOW = wet, HIGH = dry (most common modules).
    No ADC required — connect the sensor module's DO pin to a GPIO pin.
    """

    def __init__(self, pin=SOIL_DIGITAL_PIN):
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def read(self):
        """
        Read digital soil moisture value.
        Returns dict with 'status' ('wet'/'dry') and 'digital_value' (0 or 1).
        """
        value = self.GPIO.input(self.pin)
        # Most modules: LOW (0) = wet, HIGH (1) = dry
        status = "dry" if value == 1 else "wet"
        return {
            'status': status,
            'digital_value': value
        }

    def is_wet(self):
        return self.GPIO.input(self.pin) == 0

    def cleanup(self):
        self.GPIO.cleanup(self.pin)


class SoilMoistureSensorAnalog:
    """
    Soil moisture sensor using ADS1115 ADC (analog mode).
    Use this class when you have the ADS1115 module connected via I2C.
    """

    def __init__(self, channel=SOIL_MOISTURE_CHANNEL):
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.channel = AnalogIn(self.ads, getattr(ADS, f"P{channel}"))
        self.dry_value = SOIL_DRY
        self.wet_value = SOIL_WET

    def read_raw(self):
        return self.channel.value

    def read_voltage(self):
        return self.channel.voltage

    def read_percentage(self):
        raw = self.read_raw()
        percentage = (self.dry_value - raw) / (self.dry_value - self.wet_value) * 100
        return round(max(0, min(100, percentage)), 2)

    def read(self):
        return {
            'raw': self.read_raw(),
            'voltage': round(self.read_voltage(), 3),
            'percentage': self.read_percentage()
        }

    def cleanup(self):
        pass


def get_soil_sensor():
    """Factory function — returns the correct soil sensor based on settings."""
    if SOIL_SENSOR_MODE == "analog":
        return SoilMoistureSensorAnalog()
    return SoilMoistureSensor()


# --- Run directly to test ---
if __name__ == "__main__":
    print("Testing DHT22 sensor...")
    dht = DHTSensor()
    result = dht.read()
    if result:
        print(f"  Temperature: {result['temperature']}°C")
        print(f"  Humidity: {result['humidity']}%")
    else:
        print("  DHT22 read failed")
    dht.cleanup()

    print(f"\nTesting soil moisture sensor (mode: {SOIL_SENSOR_MODE})...")
    soil = get_soil_sensor()
    result = soil.read()
    print(f"  Result: {result}")
    soil.cleanup()
