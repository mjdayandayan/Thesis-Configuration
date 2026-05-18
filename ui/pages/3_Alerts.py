import streamlit as st
import pandas as pd
from utils.supabase_client import fetch_recent_readings

st.set_page_config(page_title="Notifications", page_icon="🔔", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem !important; }
    .page-header {
        background: linear-gradient(135deg, #e65100 0%, #ff6d00 40%, #ff9100 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .page-header-ok {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 40%, #66bb6a 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header-ok h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header-ok p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .alert-card {
        background: white;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border-left: 5px solid #FF9800;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .alert-card:hover { transform: translateX(4px); box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .alert-card.critical { border-left-color: #f44336; }
    .alert-icon { font-size: 1.5rem; flex-shrink: 0; margin-top: 2px; }
    .alert-body { flex: 1; }
    .alert-body .msg { font-weight: 600; color: #212121; font-size: 0.95rem; }
    .alert-body .time { color: #bdbdbd; font-size: 0.8rem; margin-top: 4px; }
    .alert-body .tip { color: #9e9e9e; font-size: 0.8rem; margin-top: 2px; font-style: italic; }
    .summary-card {
        background: white; border-radius: 16px; padding: 20px; text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }
    .summary-card .num { font-size: 2rem; font-weight: 700; }
    .summary-card .label { color: #9e9e9e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .all-clear {
        text-align: center; padding: 80px 20px;
    }
    .all-clear .icon { font-size: 4rem; margin-bottom: 12px; }
    .all-clear h2 { color: #2e7d32; font-weight: 700; margin: 0; }
    .all-clear p { color: #9e9e9e; max-width: 400px; margin: 8px auto 0; }
</style>
""", unsafe_allow_html=True)

readings = fetch_recent_readings(limit=200)

if not readings:
    st.info("No data available yet.")
    st.stop()

# Parse alerts with friendly messages and tips
ALERT_MAP = {
    'MOISTURE': {
        'icon': '💧',
        'msg': 'Soil is too dry',
        'tip': 'Consider irrigating or watering the field',
        'severity': 'warning',
    },
    'HIGH.*TEMP': {
        'icon': '🔥',
        'msg': 'Soil temperature is too high',
        'tip': 'Provide shade or increase water to cool the soil',
        'severity': 'critical',
    },
    'LOW.*TEMP': {
        'icon': '❄️',
        'msg': 'Soil temperature is too low',
        'tip': 'This may slow growth — monitor closely',
        'severity': 'warning',
    },
    'LOW.*PH': {
        'icon': '🧪',
        'msg': 'Soil is too acidic',
        'tip': 'Consider applying lime to raise pH levels',
        'severity': 'warning',
    },
    'HIGH.*PH': {
        'icon': '🧪',
        'msg': 'Soil is too alkaline',
        'tip': 'Consider adding sulfur or organic matter',
        'severity': 'warning',
    },
    'EC': {
        'icon': '🧬',
        'msg': 'Unusual nutrient levels',
        'tip': 'Check fertilizer application rates',
        'severity': 'warning',
    },
}

import re
alert_readings = []
for r in readings:
    alerts = r.get('alerts')
    if alerts and len(alerts) > 0:
        for alert_msg in alerts:
            upper = alert_msg.upper()
            matched = False
            for pattern, info in ALERT_MAP.items():
                if re.search(pattern, upper):
                    ts = r.get('timestamp', '')
                    try:
                        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                        ts_display = dt.strftime('%b %d, %I:%M %p')
                    except Exception:
                        ts_display = str(ts)[:16]
                    from datetime import datetime
                    alert_readings.append({
                        'time': ts_display,
                        'icon': info['icon'],
                        'msg': info['msg'],
                        'tip': info['tip'],
                        'severity': info['severity'],
                        'raw': alert_msg,
                    })
                    matched = True
                    break
            if not matched:
                ts = r.get('timestamp', '')
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                    ts_display = dt.strftime('%b %d, %I:%M %p')
                except Exception:
                    ts_display = str(ts)[:16]
                alert_readings.append({
                    'time': ts_display,
                    'icon': '⚠️',
                    'msg': alert_msg,
                    'tip': '',
                    'severity': 'warning',
                    'raw': alert_msg,
                })

if not alert_readings:
    st.markdown(
        '<div class="page-header-ok">'
        '<h1>🔔 Notifications</h1>'
        '<p>Your field status and soil alerts</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="all-clear">'
        '<div class="icon">✅</div>'
        '<h2>All Clear!</h2>'
        '<p>Every soil reading is within the healthy range. Your field is doing great.</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.stop()

# --- Header with alert count ---
total = len(alert_readings)
critical = sum(1 for a in alert_readings if a['severity'] == 'critical')

st.markdown(
    f'<div class="page-header">'
    f'<h1>🔔 Notifications</h1>'
    f'<p>{total} alert{"s" if total != 1 else ""} found in recent readings</p>'
    f'</div>',
    unsafe_allow_html=True
)

# --- Notification sound for critical alerts ---
if critical > 0:
    st.markdown(
        '<audio autoplay>'
        '<source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">'
        '</audio>',
        unsafe_allow_html=True
    )

# --- Summary cards ---
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(
        f'<div class="summary-card">'
        f'<div class="num" style="color:#FF9800;">{total}</div>'
        f'<div class="label">Total Alerts</div></div>',
        unsafe_allow_html=True
    )
with s2:
    st.markdown(
        f'<div class="summary-card">'
        f'<div class="num" style="color:#f44336;">{critical}</div>'
        f'<div class="label">Critical</div></div>',
        unsafe_allow_html=True
    )
with s3:
    types = len(set(a['msg'] for a in alert_readings))
    st.markdown(
        f'<div class="summary-card">'
        f'<div class="num" style="color:#1976d2;">{types}</div>'
        f'<div class="label">Alert Types</div></div>',
        unsafe_allow_html=True
    )

st.markdown("")

# --- Alert cards ---
for alert in alert_readings[:25]:
    crit_cls = 'critical' if alert['severity'] == 'critical' else ''
    tip_html = f'<div class="tip">💡 {alert["tip"]}</div>' if alert['tip'] else ''
    st.markdown(
        f'<div class="alert-card {crit_cls}">'
        f'<div class="alert-icon">{alert["icon"]}</div>'
        f'<div class="alert-body">'
        f'<div class="msg">{alert["msg"]}</div>'
        f'<div class="time">{alert["time"]}</div>'
        f'{tip_html}'
        f'</div></div>',
        unsafe_allow_html=True
    )

if total > 25:
    st.caption(f"Showing 25 of {total} alerts.")
