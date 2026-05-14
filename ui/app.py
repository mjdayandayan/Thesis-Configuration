import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.supabase_client import fetch_recent_readings

st.set_page_config(
    page_title="Rice Growth Monitor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    st.title("🌾 Rice Monitor")
    st.caption("IoT-Enabled Rice Growth Detection & Soil Nutrient Monitoring")
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.markdown("""
    **Hardware:**
    - Raspberry Pi 5
    - Logitech C922 Pro
    - RS485 5-in-1 Soil Sensor

    **AI Model:**
    - YOLO-Pro (Edge Impulse)
    - Attention with SiLU, nano 2.4M
    - 6 classes detection
    """)

# --- Main Content ---
st.title("🌾 Rice Growth Monitoring Dashboard")

# Fetch data
recent = fetch_recent_readings(limit=20)

if not recent:
    st.info("📡 No data received yet. Waiting for the Raspberry Pi to send its first reading...")
    st.stop()

latest = recent[0]
previous = recent[1] if len(recent) > 1 else None

# --- System Status ---
last_time = latest.get('timestamp', '')
if last_time:
    try:
        if isinstance(last_time, str):
            last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
        else:
            last_dt = last_time
        now = datetime.now(last_dt.tzinfo) if last_dt.tzinfo else datetime.now()
        diff = now - last_dt
        if diff < timedelta(minutes=10):
            st.success(f"✅ System online — last reading {diff.seconds // 60} min ago")
        elif diff < timedelta(hours=1):
            st.warning(f"⚠️ Last reading was {diff.seconds // 60} minutes ago")
        else:
            st.error(f"❌ No recent data — last reading at {last_time}")
    except Exception:
        st.caption(f"Last reading: {last_time}")

# --- Key Metrics ---
st.subheader("📊 Latest Sensor Readings")


def calc_delta(key):
    if previous and latest.get(key) is not None and previous.get(key) is not None:
        d = round(latest[key] - previous[key], 1)
        return f"{d:+g}"
    return None


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    val = latest.get('soil_moisture')
    st.metric("💧 Soil Moisture", f"{val}%" if val is not None else "N/A",
              delta=calc_delta('soil_moisture'))
with col2:
    val = latest.get('soil_temperature')
    st.metric("🌡️ Soil Temp", f"{val}°C" if val is not None else "N/A",
              delta=calc_delta('soil_temperature'))
with col3:
    val = latest.get('ph')
    st.metric("⚗️ pH", f"{val}" if val is not None else "N/A",
              delta=calc_delta('ph'))
with col4:
    val = latest.get('ec')
    st.metric("⚡ EC", f"{val} µS/cm" if val is not None else "N/A",
              delta=calc_delta('ec'))
with col5:
    val = latest.get('soil_humidity')
    st.metric("💨 Humidity", f"{val}%" if val is not None else "N/A",
              delta=calc_delta('soil_humidity'))

# --- AI Detection ---
st.subheader("🤖 Growth Stage Detection")

col_pred, col_img = st.columns([1, 2])

with col_pred:
    label = latest.get('prediction_label')
    confidence = latest.get('prediction_confidence')

    if label:
        st.metric("Detected Stage", label.replace('_', ' ').title())
        if confidence:
            st.progress(confidence, text=f"Confidence: {confidence:.1%}")
    else:
        st.metric("Detected Stage", "No detection")

    # Detection distribution from recent data
    st.caption("Recent detection distribution:")
    labels = [r.get('prediction_label') for r in recent if r.get('prediction_label')]
    if labels:
        label_counts = pd.Series(labels).value_counts()
        st.bar_chart(label_counts)

with col_img:
    image_url = latest.get('image_url')
    if image_url:
        st.image(image_url,
                 caption=f"Latest capture — {latest.get('timestamp', '')}",
                 use_container_width=True)
    else:
        st.info("📷 No image available for the latest reading")

# --- Recent Readings Table ---
st.subheader("📋 Recent Readings")

df = pd.DataFrame(recent)
display_cols = [
    'timestamp', 'soil_moisture', 'soil_temperature', 'ph', 'ec',
    'soil_humidity', 'prediction_label', 'prediction_confidence'
]
available_cols = [c for c in display_cols if c in df.columns]

if available_cols:
    st.dataframe(
        df[available_cols].rename(columns={
            'timestamp': 'Time',
            'soil_moisture': 'Moisture (%)',
            'soil_temperature': 'Temp (°C)',
            'ph': 'pH',
            'ec': 'EC (µS/cm)',
            'soil_humidity': 'Humidity (%)',
            'prediction_label': 'Detection',
            'prediction_confidence': 'Confidence'
        }),
        use_container_width=True,
        hide_index=True
    )
