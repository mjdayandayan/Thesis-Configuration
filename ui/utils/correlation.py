"""
Sensor Correlation Engine — Pearson correlation between soil parameters.
"""

import pandas as pd
import numpy as np


SENSOR_COLS = ['soil_moisture', 'soil_temperature', 'ph', 'ec', 'soil_humidity']
DISPLAY_NAMES = {
    'soil_moisture': 'Moisture',
    'soil_temperature': 'Temperature',
    'ph': 'pH',
    'ec': 'EC',
    'soil_humidity': 'Humidity',
}


def compute_correlations(readings):
    """Compute Pearson correlation matrix from a list of reading dicts.
    Returns (corr_matrix DataFrame, count of readings used).
    """
    df = pd.DataFrame(readings)
    available = [c for c in SENSOR_COLS if c in df.columns]
    if len(available) < 2:
        return None, 0
    sub = df[available].apply(pd.to_numeric, errors='coerce').dropna()
    if len(sub) < 3:
        return None, len(sub)
    corr = sub.corr()
    corr = corr.rename(index=DISPLAY_NAMES, columns=DISPLAY_NAMES)
    return corr, len(sub)


def interpret_correlation(r, param1, param2):
    """Return a plain-English interpretation of a correlation coefficient."""
    strength = abs(r)
    if strength < 0.3:
        desc = 'Weak'
    elif strength < 0.6:
        desc = 'Moderate'
    else:
        desc = 'Strong'
    direction = 'positive' if r > 0 else 'negative'

    EXPLANATIONS = {
        ('Moisture', 'Temperature'): 'Higher moisture may cool soil via evaporation.',
        ('Temperature', 'Moisture'): 'Higher moisture may cool soil via evaporation.',
        ('pH', 'EC'): 'Nutrient concentrations can affect soil acidity.',
        ('EC', 'pH'): 'Nutrient concentrations can affect soil acidity.',
        ('Moisture', 'Humidity'): 'Wetter soil increases near-surface humidity.',
        ('Humidity', 'Moisture'): 'Wetter soil increases near-surface humidity.',
        ('Moisture', 'EC'): 'Irrigation dilutes soil nutrients (EC).',
        ('EC', 'Moisture'): 'Irrigation dilutes soil nutrients (EC).',
        ('Temperature', 'Humidity'): 'Warm soil promotes moisture evaporation.',
        ('Humidity', 'Temperature'): 'Warm soil promotes moisture evaporation.',
    }
    explanation = EXPLANATIONS.get((param1, param2), '')
    return f'{desc} {direction} (r = {r:.2f}). {explanation}'.strip()
