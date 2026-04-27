"""
RS485 5-in-1 soil sensor interface (pH, Temperature, Humidity, EC, Moisture).
Communicates via Modbus RTU over a USB-to-RS485 adapter.
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.settings import (
    RS485_PORT, RS485_BAUDRATE, RS485_SLAVE_ADDRESS, RS485_TIMEOUT,
    RS485_REG_MOISTURE, RS485_NUM_REGISTERS
)


class SoilSensorRS485:
    """
    RS485 5-in-1 soil sensor (pH, Temperature, Humidity, EC, Moisture).

    Requires: pip install minimalmodbus pyserial
    """

    def __init__(self, port=RS485_PORT, baudrate=RS485_BAUDRATE,
                 address=RS485_SLAVE_ADDRESS, timeout=RS485_TIMEOUT):
        self.available = False
        try:
            import minimalmodbus

            self.instrument = minimalmodbus.Instrument(port, address)
            self.instrument.serial.baudrate = baudrate
            self.instrument.serial.timeout = timeout
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            self.instrument.serial.stopbits = 1
            self.instrument.mode = minimalmodbus.MODE_RTU
            self.available = True
        except Exception as e:
            print(f"[SENSOR] RS485 soil sensor not available: {e}")
            print(f"[SENSOR] The system will continue without soil data.")
            self.instrument = None

    def read(self, retries=3):
        """
        Read all 5 values from the sensor.
        Returns dict with moisture, temperature, ec, ph, humidity.

        Register mapping (adjust in settings.py if your sensor differs):
          0x0000: Moisture    (value / 10 = %)
          0x0001: Temperature (value / 10 = °C)
          0x0002: EC          (value = µS/cm, no division)
          0x0003: pH          (value / 10)
          0x0004: Humidity    (value / 10 = %)
        """
        for attempt in range(retries):
            if not self.available:
                return None
            try:
                registers = self.instrument.read_registers(
                    RS485_REG_MOISTURE,
                    RS485_NUM_REGISTERS,
                    functioncode=3
                )

                return {
                    'soil_moisture': round(registers[0] / 10.0, 1),    # %
                    'soil_temperature': round(registers[1] / 10.0, 1), # °C
                    'ec': registers[2],                                 # µS/cm
                    'ph': round(registers[3] / 10.0, 1),
                    'soil_humidity': round(registers[4] / 10.0, 1),    # %
                }

            except Exception as e:
                print(f"RS485 read attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        print("RS485 sensor: all retries failed")
        return None

    def read_single(self, register_address, scale=10.0):
        """Read a single register value. Useful for debugging."""
        if not self.available:
            return None
        raw = self.instrument.read_register(register_address, functioncode=3)
        return round(raw / scale, 1)

    def cleanup(self):
        if hasattr(self, 'instrument') and self.instrument and self.instrument.serial.is_open:
            self.instrument.serial.close()


# --- Run directly to test ---
if __name__ == "__main__":
    print("Testing RS485 5-in-1 Soil Sensor...")
    sensor = SoilSensorRS485()
    if not sensor.available:
        print("  Sensor not connected — skipping test.")
    else:
        result = sensor.read()
        if result:
            print(f"  Soil Moisture:  {result['soil_moisture']}%")
            print(f"  Soil Temp:      {result['soil_temperature']}°C")
            print(f"  EC:             {result['ec']} µS/cm")
            print(f"  pH:             {result['ph']}")
            print(f"  Soil Humidity:  {result['soil_humidity']}%")
        else:
            print("  Sensor read failed — check wiring and USB-to-RS485 adapter")
    sensor.cleanup()
