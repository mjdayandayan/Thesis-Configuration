"""
Smart Recommendations Engine for the Rice Field Monitor.
Analyzes recent sensor readings and generates actionable farmer tips.
"""


def generate_recommendations(readings):
    """Analyze recent readings and return a list of recommendation dicts.

    Each recommendation has: icon, title, message, priority ('high', 'medium', 'low').
    Returns at most 4 recommendations, sorted by priority.
    """
    if not readings or len(readings) < 2:
        return []

    tips = []
    latest = readings[0]

    # --- 1. Moisture trend analysis ---
    moistures = [r.get('soil_moisture') for r in readings if r.get('soil_moisture') is not None]
    if len(moistures) >= 3:
        recent_avg = sum(moistures[:3]) / 3
        older_avg = sum(moistures[3:min(8, len(moistures))]) / max(1, len(moistures[3:8]))
        drop = older_avg - recent_avg

        if drop > 10:
            tips.append({
                'icon': '💧',
                'title': 'Moisture Dropping Fast',
                'message': f'Water level dropped {drop:.0f}% recently. Consider irrigating the field soon.',
                'priority': 'high',
            })
        elif latest.get('soil_moisture', 100) < 45:
            tips.append({
                'icon': '🚿',
                'title': 'Soil is Getting Dry',
                'message': 'Water level is below 45%. Schedule irrigation to keep rice healthy.',
                'priority': 'high',
            })
        elif recent_avg > 75:
            tips.append({
                'icon': '💧',
                'title': 'Moisture is High',
                'message': 'Water levels are above 75%. Ensure proper drainage to prevent root rot.',
                'priority': 'low',
            })

    # --- 2. Temperature analysis ---
    temp = latest.get('soil_temperature')
    if temp is not None:
        if temp > 33:
            tips.append({
                'icon': '🔥',
                'title': 'High Soil Temperature',
                'message': f'Temperature is {temp}°C. Consider watering to cool the soil or provide shade.',
                'priority': 'high',
            })
        elif temp < 20:
            tips.append({
                'icon': '❄️',
                'title': 'Low Soil Temperature',
                'message': f'Temperature is {temp}°C. Growth may slow down — monitor closely.',
                'priority': 'medium',
            })
        elif 25 <= temp <= 30:
            tips.append({
                'icon': '✅',
                'title': 'Temperature is Ideal',
                'message': f'Soil temperature ({temp}°C) is in the optimal range for rice growth.',
                'priority': 'low',
            })

    # --- 3. pH trend analysis ---
    ph_vals = [r.get('ph') for r in readings if r.get('ph') is not None]
    if len(ph_vals) >= 3:
        ph_recent = sum(ph_vals[:3]) / 3
        if ph_recent < 5.5:
            tips.append({
                'icon': '🧪',
                'title': 'Soil Becoming Acidic',
                'message': f'Average pH is {ph_recent:.1f}. Consider applying agricultural lime to raise pH.',
                'priority': 'high',
            })
        elif ph_recent > 7.0:
            tips.append({
                'icon': '🧪',
                'title': 'Soil Becoming Alkaline',
                'message': f'Average pH is {ph_recent:.1f}. Adding organic compost can help lower pH.',
                'priority': 'medium',
            })

    # --- 4. EC / nutrient analysis ---
    ec = latest.get('ec')
    if ec is not None:
        if ec < 250:
            tips.append({
                'icon': '🧬',
                'title': 'Low Nutrient Levels',
                'message': 'EC is low — the soil may need fertilizer to support healthy growth.',
                'priority': 'medium',
            })
        elif ec > 1800:
            tips.append({
                'icon': '🧬',
                'title': 'High Nutrient Concentration',
                'message': 'EC is high — reduce fertilizer and flush with water if needed.',
                'priority': 'medium',
            })

    # --- 5. Growth stage specific tips ---
    stage = (latest.get('prediction_label') or '').lower()
    if 'vegetative' in stage:
        tips.append({
            'icon': '🌱',
            'title': 'Vegetative Stage Tips',
            'message': 'Ensure adequate nitrogen fertilizer and maintain water level at 2-5 cm.',
            'priority': 'low',
        })
    elif 'heading' in stage:
        tips.append({
            'icon': '🌿',
            'title': 'Heading Stage Tips',
            'message': 'Maintain consistent water supply. This stage is sensitive to drought stress.',
            'priority': 'low',
        })
    elif 'flowering' in stage:
        tips.append({
            'icon': '🌸',
            'title': 'Flowering Stage — Critical!',
            'message': 'Keep water at 5 cm depth. Avoid pesticide spraying during flowering.',
            'priority': 'medium',
        })
    elif 'maturing' in stage:
        tips.append({
            'icon': '🌾',
            'title': 'Approaching Harvest',
            'message': 'Start draining water 2-3 weeks before expected harvest date.',
            'priority': 'low',
        })
    elif 'weed' in stage:
        tips.append({
            'icon': '🚨',
            'title': 'Weed Growth Detected',
            'message': 'Remove weeds promptly — they compete for nutrients and reduce yield.',
            'priority': 'high',
        })

    # --- 6. All-good message if nothing is wrong ---
    high_count = sum(1 for t in tips if t['priority'] == 'high')
    if high_count == 0 and len(tips) < 2:
        tips.append({
            'icon': '👍',
            'title': 'Field Looks Healthy',
            'message': 'All soil conditions are within safe range. Keep monitoring!',
            'priority': 'low',
        })

    # Sort: high > medium > low, then limit to 4
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    tips.sort(key=lambda t: priority_order.get(t['priority'], 3))
    return tips[:4]
