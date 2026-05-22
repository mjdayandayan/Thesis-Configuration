import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
from utils.supabase_client import fetch_readings_range

st.set_page_config(page_title="Soil Trends", page_icon="📈", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem !important; }
    .page-header {
        background: linear-gradient(135deg, #1565c0 0%, #1976d2 40%, #42a5f5 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .stat-pill {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(0,0,0,0.04); padding: 8px 16px; border-radius: 12px;
        font-weight: 600; font-size: 0.9rem;
    }
    .stat-pill .num { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-header">'
    '<h1>📈 Soil Trends</h1>'
    '<p>Track how your soil conditions change over time</p>'
    '</div>',
    unsafe_allow_html=True
)

# Simple period selector
period = st.radio(
    "Time period:",
    ["Last 24 Hours", "Last 3 Days", "Last 7 Days", "Custom"],
    horizontal=True,
    index=0
)

if period == "Last 24 Hours":
    start_date = date.today() - timedelta(days=1)
    end_date = date.today()
elif period == "Last 3 Days":
    start_date = date.today() - timedelta(days=3)
    end_date = date.today()
elif period == "Last 7 Days":
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()
else:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("To", value=date.today())

if start_date > end_date:
    st.error("Start date must be before end date.")
    st.stop()

data = fetch_readings_range(
    datetime.combine(start_date, datetime.min.time()),
    datetime.combine(end_date, datetime.max.time())
)

if not data:
    st.markdown(
        "<div style='text-align:center; padding:60px 20px;'>"
        "<div style='font-size:3rem;'>📊</div>"
        "<h3 style='color:#424242;'>No data for this period</h3>"
        "<p style='color:#9e9e9e;'>Try a different date range or wait for more sensor readings.</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# --- Quick stats ---
sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    st.markdown(f'<div class="stat-pill">📊 <span class="num">{len(df)}</span> readings</div>', unsafe_allow_html=True)
with sc2:
    if 'soil_moisture' in df.columns:
        avg_m = df['soil_moisture'].mean()
        st.markdown(f'<div class="stat-pill">💧 Avg <span class="num">{avg_m:.0f}%</span></div>', unsafe_allow_html=True)
with sc3:
    if 'soil_temperature' in df.columns:
        avg_t = df['soil_temperature'].mean()
        st.markdown(f'<div class="stat-pill">🌡️ Avg <span class="num">{avg_t:.1f}°C</span></div>', unsafe_allow_html=True)
with sc4:
    if 'ph' in df.columns:
        avg_p = df['ph'].mean()
        st.markdown(f'<div class="stat-pill">🧪 Avg pH <span class="num">{avg_p:.1f}</span></div>', unsafe_allow_html=True)
with sc5:
    # CSV download button
    export_cols = ['timestamp', 'soil_moisture', 'soil_temperature', 'ph', 'ec',
                   'soil_humidity', 'prediction_label', 'prediction_confidence']
    export_available = [c for c in export_cols if c in df.columns]
    csv_df = df[export_available].copy()
    csv_df.columns = ['Time', 'Moisture %', 'Temp °C', 'pH', 'EC µS/cm',
                       'Humidity %', 'Growth Stage', 'Confidence'][:len(export_available)]
    csv_data = csv_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"soil_data_{start_date}_{end_date}.csv",
        mime="text/csv",
        width="stretch",
    )

st.markdown("")


# --- Premium chart helper ---
def make_chart(df, col, title, unit, safe_low, safe_high, color, fill_color):
    if col not in df.columns:
        return None
    fig = go.Figure()
    # Safe zone band
    fig.add_hrect(y0=safe_low, y1=safe_high, fillcolor="rgba(76,175,80,0.06)",
                  line_width=0)
    fig.add_hline(y=safe_low, line=dict(color='rgba(76,175,80,0.3)', width=1, dash='dot'))
    fig.add_hline(y=safe_high, line=dict(color='rgba(76,175,80,0.3)', width=1, dash='dot'))
    # Area fill
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df[col],
        mode='lines', name=title,
        line=dict(color=color, width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate=f'<b>%{{y:.1f}}</b> {unit}<br>%{{x|%b %d, %I:%M %p}}<extra></extra>'
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=f'<b>{title}</b>', font=dict(size=14, color='#424242'), x=0.02),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#bdbdbd')),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.04)', tickfont=dict(size=10, color='#bdbdbd'),
                   title=''),
        hovermode='x unified',
        showlegend=False,
    )
    # Add safe range annotation
    fig.add_annotation(
        x=df['timestamp'].iloc[0], y=safe_high,
        text=f"Safe: {safe_low}–{safe_high} {unit}",
        showarrow=False, font=dict(size=9, color='#81c784'),
        xanchor='left', yanchor='bottom'
    )
    return fig


# --- Charts in 2x2 grid ---
col_a, col_b = st.columns(2)

with col_a:
    fig = make_chart(df, 'soil_moisture', '💧 Water Level', '%', 40, 80,
                     '#2196F3', 'rgba(33,150,243,0.08)')
    if fig:
        st.plotly_chart(fig, width="stretch")

with col_b:
    fig = make_chart(df, 'soil_temperature', '🌡️ Temperature', '°C', 18, 35,
                     '#FF7043', 'rgba(255,112,67,0.08)')
    if fig:
        st.plotly_chart(fig, width="stretch")

col_c, col_d = st.columns(2)

with col_c:
    fig = make_chart(df, 'ph', '🧪 Soil Acidity (pH)', 'pH', 5.5, 7.0,
                     '#AB47BC', 'rgba(171,71,188,0.08)')
    if fig:
        st.plotly_chart(fig, width="stretch")

with col_d:
    fig = make_chart(df, 'ec', '🧬 Soil Nutrients', 'µS/cm', 200, 2000,
                     '#26A69A', 'rgba(38,166,154,0.08)')
    if fig:
        st.plotly_chart(fig, width="stretch")

# --- Growth Stages ---
st.markdown("---")
st.markdown("### 🌾 Growth Stage Distribution")

labels = df['prediction_label'].dropna()
if not labels.empty:
    label_counts = labels.value_counts().reset_index()
    label_counts.columns = ['Stage', 'Count']
    label_counts['Stage'] = label_counts['Stage'].str.replace('_', ' ').str.title()

    colors = {
        'Vegetative Stage': '#66BB6A', 'Heading Stage': '#42A5F5',
        'Flowering Stage': '#AB47BC', 'Maturing Stage': '#FFA726',
        'Weed Growth': '#EF5350',
    }

    fig = go.Figure()
    for _, row in label_counts.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Count']], y=[row['Stage']],
            orientation='h', name=row['Stage'],
            marker=dict(color=colors.get(row['Stage'], '#90A4AE'),
                        cornerradius=6),
            text=f"  {row['Count']}x", textposition='outside',
            hovertemplate=f"<b>{row['Stage']}</b>: {row['Count']} detections<extra></extra>"
        ))
    fig.update_layout(
        showlegend=False, height=220,
        margin=dict(l=10, r=40, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        barmode='stack',
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("No growth stage detections in this period.")
