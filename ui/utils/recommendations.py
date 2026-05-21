"""
Smart Recommendations Engine for the Rice Field Monitor.
Analyzes recent sensor readings and generates actionable farmer tips.
Uses growth-stage-specific NPK thresholds based on academic literature.

References:
  - Dobermann, A., & Fairhurst, T. (2000). Rice: Nutrient disorders & nutrient management. IRRI.
  - Shrestha, J., Kandel, M., Subedi, S., & Shah, K. K. (2020). Role of nutrients in rice. Agrica, 9(1), 53–62.
  - Sulaeman, Y., et al. (2024). Developing and testing a portable soil nutrient detector. Computers, 13(8), 209.
"""

# NPK thresholds by rice growth stage (mg/kg)
# These represent optimal available soil concentrations required to maximize yield.
NPK_THRESHOLDS = {
    "vegetative": {
        "n_min": 30, "n_max": 50,
        "p_min": 20, "p_max": 35,
        "k_min": 80, "k_max": 120,
        "label": "Vegetative (Early Tillering to Active Tillering)",
        "focus": "Promotes active root development, leaf area expansion, and high tiller numbers.",
    },
    "heading": {
        "n_min": 20, "n_max": 35,
        "p_min": 15, "p_max": 25,
        "k_min": 100, "k_max": 150,
        "label": "Heading (Panicle Initiation & Booting)",
        "focus": "Shift from structural growth to reproduction. Requires high K to boost spikelet numbers and prevent lodging.",
    },
    "flowering": {
        "n_min": 15, "n_max": 25,
        "p_min": 15, "p_max": 20,
        "k_min": 90, "k_max": 130,
        "label": "Flowering (Anthesis & Pollination)",
        "focus": "P accelerates clean flowering timelines, while K powers cellular transport for upcoming grain filling.",
    },
    "maturing": {
        "n_min": 0, "n_max": 15,
        "p_min": 10, "p_max": 15,
        "k_min": 60, "k_max": 90,
        "label": "Maturing (Milky to Golden Ripe Stage)",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
    "mature": {
        "n_min": 0, "n_max": 15,
        "p_min": 10, "p_max": 15,
        "k_min": 60, "k_max": 90,
        "label": "Maturing (Milky to Golden Ripe Stage)",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
    "ripening": {
        "n_min": 0, "n_max": 15,
        "p_min": 10, "p_max": 15,
        "k_min": 60, "k_max": 90,
        "label": "Maturing (Milky to Golden Ripe Stage)",
        "focus": "High Nitrogen is actively discouraged as it delays maturation, increases green grains, and invites pests.",
    },
}


def get_npk_thresholds(stage):
    """Get NPK thresholds for the given growth stage. Returns None if stage is unknown."""
    if not stage:
        return None
    stage_lower = stage.lower().strip()
    return NPK_THRESHOLDS.get(stage_lower)


def evaluate_npk(stage, nitrogen=None, phosphorus=None, potassium=None):
    """
    Evaluate NPK readings against the thresholds for the current growth stage.

    Args:
        stage: Growth stage label (from model prediction)
        nitrogen: Soil nitrogen reading in mg/kg (or None)
        phosphorus: Soil phosphorus reading in mg/kg (or None)
        potassium: Soil potassium reading in mg/kg (or None)

    Returns:
        List of recommendation dicts with nutrient-specific advice.
    """
    thresholds = get_npk_thresholds(stage)
    if not thresholds:
        return []

    tips = []

    if nitrogen is not None:
        if nitrogen < thresholds["n_min"]:
            tips.append({
                'icon': '🧪',
                'title': f'Low Nitrogen for {thresholds["label"]}',
                'message': (
                    f'N is {nitrogen} mg/kg (optimal: {thresholds["n_min"]}–{thresholds["n_max"]} mg/kg). '
                    f'Apply nitrogen fertilizer (e.g., urea) to support growth at this stage.'
                ),
                'priority': 'high',
            })
        elif nitrogen > thresholds["n_max"]:
            severity = 'high' if stage.lower() in ('maturing', 'mature', 'ripening') else 'medium'
            tips.append({
                'icon': '⚠️',
                'title': f'Excess Nitrogen for {thresholds["label"]}',
                'message': (
                    f'N is {nitrogen} mg/kg (optimal: {thresholds["n_min"]}–{thresholds["n_max"]} mg/kg). '
                    f'{thresholds["focus"]}'
                ),
                'priority': severity,
            })

    if phosphorus is not None:
        if phosphorus < thresholds["p_min"]:
            tips.append({
                'icon': '🧪',
                'title': f'Low Phosphorus for {thresholds["label"]}',
                'message': (
                    f'P is {phosphorus} mg/kg (optimal: {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg). '
                    f'Consider applying phosphorus fertilizer (e.g., DAP or superphosphate).'
                ),
                'priority': 'high',
            })
        elif phosphorus > thresholds["p_max"]:
            tips.append({
                'icon': '⚠️',
                'title': f'Excess Phosphorus for {thresholds["label"]}',
                'message': (
                    f'P is {phosphorus} mg/kg (optimal: {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg). '
                    f'Reduce phosphorus application to avoid nutrient imbalance.'
                ),
                'priority': 'medium',
            })

    if potassium is not None:
        if potassium < thresholds["k_min"]:
            severity = 'high' if stage.lower() in ('heading', 'flowering') else 'medium'
            tips.append({
                'icon': '🧪',
                'title': f'Low Potassium for {thresholds["label"]}',
                'message': (
                    f'K is {potassium} mg/kg (optimal: {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg). '
                    f'Apply potassium fertilizer (e.g., muriate of potash). {thresholds["focus"]}'
                ),
                'priority': severity,
            })
        elif potassium > thresholds["k_max"]:
            tips.append({
                'icon': '⚠️',
                'title': f'Excess Potassium for {thresholds["label"]}',
                'message': (
                    f'K is {potassium} mg/kg (optimal: {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg). '
                    f'Reduce potassium application.'
                ),
                'priority': 'low',
            })

    return tips


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

    # --- 5. Growth stage specific NPK thresholds ---
    stage = (latest.get('prediction_label') or '').lower()
    thresholds = get_npk_thresholds(stage)

    # If NPK readings are available, evaluate against stage thresholds
    nitrogen = latest.get('nitrogen')
    phosphorus = latest.get('phosphorus')
    potassium = latest.get('potassium')

    if thresholds and any(v is not None for v in [nitrogen, phosphorus, potassium]):
        npk_tips = evaluate_npk(stage, nitrogen, phosphorus, potassium)
        tips.extend(npk_tips)
    elif thresholds:
        # No direct NPK readings — provide stage-specific guidance using thresholds
        if 'vegetative' in stage:
            tips.append({
                'icon': '🌱',
                'title': 'Vegetative Stage — High N Demand',
                'message': (
                    f'Optimal soil nutrients: N {thresholds["n_min"]}–{thresholds["n_max"]} mg/kg, '
                    f'P {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg, '
                    f'K {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg. '
                    f'Ensure adequate nitrogen and maintain water at 2–5 cm.'
                ),
                'priority': 'medium',
            })
        elif 'heading' in stage:
            tips.append({
                'icon': '🌿',
                'title': 'Heading Stage — High K Demand',
                'message': (
                    f'Optimal soil nutrients: N {thresholds["n_min"]}–{thresholds["n_max"]} mg/kg, '
                    f'P {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg, '
                    f'K {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg. '
                    f'Maintain consistent water supply — sensitive to drought stress.'
                ),
                'priority': 'medium',
            })
        elif 'flowering' in stage:
            tips.append({
                'icon': '🌸',
                'title': 'Flowering Stage — Steady P & K Needed',
                'message': (
                    f'Optimal soil nutrients: N {thresholds["n_min"]}–{thresholds["n_max"]} mg/kg, '
                    f'P {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg, '
                    f'K {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg. '
                    f'Keep water at 5 cm depth. Avoid pesticide spraying during flowering.'
                ),
                'priority': 'medium',
            })
        elif 'matur' in stage or 'ripen' in stage:
            tips.append({
                'icon': '🌾',
                'title': 'Maturing Stage — Reduce Nitrogen',
                'message': (
                    f'Optimal soil nutrients: N < {thresholds["n_max"]} mg/kg, '
                    f'P {thresholds["p_min"]}–{thresholds["p_max"]} mg/kg, '
                    f'K {thresholds["k_min"]}–{thresholds["k_max"]} mg/kg. '
                    f'High N delays maturation. Start draining water 2–3 weeks before harvest.'
                ),
                'priority': 'medium',
            })
    else:
        # No thresholds match (unknown stage) — fallback generic tips
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
        elif 'matur' in stage or 'ripen' in stage:
            tips.append({
                'icon': '🌾',
                'title': 'Approaching Harvest',
                'message': 'Start draining water 2-3 weeks before expected harvest date.',
                'priority': 'low',
            })

    if 'weed' in stage:
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
