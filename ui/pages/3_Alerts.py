import streamlit as st
import pandas as pd
from utils.supabase_client import fetch_recent_readings

st.set_page_config(page_title="Alerts", page_icon="🔔", layout="wide")

st.title("🔔 Alert Log")
st.caption("Sensor threshold violations and warnings")

# Fetch recent readings and filter for alerts
readings = fetch_recent_readings(limit=200)

if not readings:
    st.info("No data available yet.")
    st.stop()

# Extract readings that have alerts
alert_readings = []
for r in readings:
    alerts = r.get('alerts')
    if alerts and len(alerts) > 0:
        for alert_msg in alerts:
            alert_readings.append({
                'timestamp': r.get('timestamp'),
                'alert': alert_msg,
                'detection': r.get('prediction_label', 'N/A')
            })

if not alert_readings:
    st.success("✅ No alerts recorded. All sensor readings are within normal thresholds.")
    st.stop()

# --- Summary ---
st.subheader("Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Alerts", len(alert_readings))

with col2:
    # Count unique alert types
    alert_types = set()
    for a in alert_readings:
        msg = a['alert'].upper()
        if 'MOISTURE' in msg:
            alert_types.add('Moisture')
        elif 'TEMP' in msg:
            alert_types.add('Temperature')
        elif 'PH' in msg:
            alert_types.add('pH')
        elif 'EC' in msg:
            alert_types.add('EC')
    st.metric("Alert Types", len(alert_types))

with col3:
    # Most recent alert time
    st.metric("Latest Alert", alert_readings[0]['timestamp'][:16] if alert_readings else "N/A")

# --- Alert Types Breakdown ---
st.subheader("Alert Types")
type_list = []
for a in alert_readings:
    msg = a['alert'].upper()
    if 'MOISTURE' in msg:
        type_list.append('Low Moisture')
    elif 'LOW SOIL TEMP' in msg:
        type_list.append('Low Temperature')
    elif 'HIGH SOIL TEMP' in msg:
        type_list.append('High Temperature')
    elif 'LOW SOIL PH' in msg or 'LOW PH' in msg:
        type_list.append('Low pH')
    elif 'HIGH SOIL PH' in msg or 'HIGH PH' in msg:
        type_list.append('High pH')
    elif 'LOW SOIL EC' in msg or 'LOW EC' in msg:
        type_list.append('Low EC')
    elif 'HIGH SOIL EC' in msg or 'HIGH EC' in msg:
        type_list.append('High EC')
    else:
        type_list.append('Other')

if type_list:
    type_counts = pd.Series(type_list).value_counts()
    st.bar_chart(type_counts)

# --- Alert History Table ---
st.subheader("Alert History")
df = pd.DataFrame(alert_readings)
st.dataframe(
    df.rename(columns={
        'timestamp': 'Time',
        'alert': 'Alert Message',
        'detection': 'Growth Stage'
    }),
    use_container_width=True,
    hide_index=True
)
