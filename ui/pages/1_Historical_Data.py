import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from utils.supabase_client import fetch_readings_range

st.set_page_config(page_title="Historical Data", page_icon="📊", layout="wide")

st.title("📊 Historical Sensor Data")
st.caption("View soil sensor trends over time")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=date.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("End date", value=date.today())

if start_date > end_date:
    st.error("Start date must be before end date")
    st.stop()

# Fetch data
data = fetch_readings_range(
    datetime.combine(start_date, datetime.min.time()),
    datetime.combine(end_date, datetime.max.time())
)

if not data:
    st.info("No data available for the selected date range.")
    st.stop()

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- Soil Parameter Charts ---
st.subheader("Soil Parameters Over Time")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💧 Moisture", "🌡️ Temperature", "⚗️ pH", "⚡ EC", "💨 Humidity"
])

with tab1:
    if 'soil_moisture' in df.columns:
        fig = px.line(df, x='timestamp', y='soil_moisture',
                      title='Soil Moisture (%)',
                      labels={'timestamp': 'Time', 'soil_moisture': 'Moisture (%)'})
        fig.add_hline(y=40, line_dash="dash", line_color="red",
                      annotation_text="Min threshold (40%)")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if 'soil_temperature' in df.columns:
        fig = px.line(df, x='timestamp', y='soil_temperature',
                      title='Soil Temperature (°C)',
                      labels={'timestamp': 'Time', 'soil_temperature': 'Temperature (°C)'})
        fig.add_hline(y=18, line_dash="dash", line_color="blue",
                      annotation_text="Min (18°C)")
        fig.add_hline(y=35, line_dash="dash", line_color="red",
                      annotation_text="Max (35°C)")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if 'ph' in df.columns:
        fig = px.line(df, x='timestamp', y='ph',
                      title='Soil pH',
                      labels={'timestamp': 'Time', 'ph': 'pH'})
        fig.add_hline(y=5.5, line_dash="dash", line_color="blue",
                      annotation_text="Min (5.5)")
        fig.add_hline(y=7.0, line_dash="dash", line_color="red",
                      annotation_text="Max (7.0)")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    if 'ec' in df.columns:
        fig = px.line(df, x='timestamp', y='ec',
                      title='Electrical Conductivity (µS/cm)',
                      labels={'timestamp': 'Time', 'ec': 'EC (µS/cm)'})
        fig.add_hline(y=200, line_dash="dash", line_color="blue",
                      annotation_text="Min (200)")
        fig.add_hline(y=2000, line_dash="dash", line_color="red",
                      annotation_text="Max (2000)")
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    if 'soil_humidity' in df.columns:
        fig = px.line(df, x='timestamp', y='soil_humidity',
                      title='Soil Humidity (%)',
                      labels={'timestamp': 'Time', 'soil_humidity': 'Humidity (%)'})
        st.plotly_chart(fig, use_container_width=True)

# --- Growth Stage Distribution ---
st.subheader("Growth Stage Detection Distribution")

labels = df['prediction_label'].dropna()
if not labels.empty:
    label_counts = labels.value_counts().reset_index()
    label_counts.columns = ['Stage', 'Count']
    fig = px.pie(label_counts, values='Count', names='Stage',
                 title='Detection Distribution')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No detection data available for the selected range.")
