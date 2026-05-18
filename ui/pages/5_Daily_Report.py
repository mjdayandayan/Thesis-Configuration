import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time
from utils.supabase_client import fetch_readings_range

st.set_page_config(page_title="Daily Report", page_icon="📋", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem !important; }
    .page-header {
        background: linear-gradient(135deg, #00695c 0%, #00897b 40%, #26a69a 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .report-card {
        background: white; border-radius: 16px; padding: 22px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 12px;
        border: 1px solid rgba(0,0,0,0.06);
    }
    .report-card h4 { margin: 0 0 8px; font-size: 1rem; color: #424242; }
    .report-stat {
        display: flex; align-items: baseline; gap: 8px;
    }
    .report-stat .big { font-size: 2rem; font-weight: 700; }
    .report-stat .unit { font-size: 0.85rem; color: #9e9e9e; }
    .report-range {
        display: flex; gap: 16px; margin-top: 8px; font-size: 0.8rem; color: #9e9e9e;
    }
    .grade-badge {
        display: inline-block; padding: 4px 14px; border-radius: 12px;
        font-weight: 600; font-size: 0.85rem;
    }
    .grade-a { background: #e8f5e9; color: #2e7d32; }
    .grade-b { background: #fff3e0; color: #e65100; }
    .grade-c { background: #ffebee; color: #c62828; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-header">'
    '<h1>📋 Daily Report</h1>'
    '<p>Auto-generated daily field summary</p>'
    '</div>',
    unsafe_allow_html=True
)

# Date picker
selected_date = st.date_input("Select date:", value=date.today())

# Fetch data for the selected day
start_dt = datetime.combine(selected_date, time.min)
end_dt = datetime.combine(selected_date, time.max)
data = fetch_readings_range(start_dt, end_dt)

if not data:
    st.markdown(
        "<div style='text-align:center; padding:60px 20px;'>"
        "<div style='font-size:3rem;'>📋</div>"
        f"<h3 style='color:#424242;'>No data for {selected_date.strftime('%B %d, %Y')}</h3>"
        "<p style='color:#9e9e9e;'>No readings were recorded on this date.</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
total_readings = len(df)

# --- Grade the day ---
def grade_metric(series, low, high):
    if series.empty:
        return 'N/A', 0
    in_range = ((series >= low) & (series <= high)).sum()
    pct = in_range / len(series) * 100
    return pct

grades = {}
if 'soil_moisture' in df.columns:
    grades['moisture'] = grade_metric(df['soil_moisture'].dropna(), 40, 80)
if 'soil_temperature' in df.columns:
    grades['temp'] = grade_metric(df['soil_temperature'].dropna(), 18, 35)
if 'ph' in df.columns:
    grades['ph'] = grade_metric(df['ph'].dropna(), 5.5, 7.0)
if 'ec' in df.columns:
    grades['ec'] = grade_metric(df['ec'].dropna(), 200, 2000)

overall = sum(grades.values()) / max(len(grades), 1)
if overall >= 80:
    grade_label, grade_cls = 'Excellent', 'grade-a'
elif overall >= 50:
    grade_label, grade_cls = 'Fair', 'grade-b'
else:
    grade_label, grade_cls = 'Needs Attention', 'grade-c'

# --- Summary header ---
st.markdown(f"### {selected_date.strftime('%A, %B %d, %Y')}")

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(
        f'<div class="report-card"><h4>📊 Total Readings</h4>'
        f'<div class="report-stat"><span class="big">{total_readings}</span>'
        f'<span class="unit">data points</span></div></div>',
        unsafe_allow_html=True
    )
with sc2:
    st.markdown(
        f'<div class="report-card"><h4>🏆 Day Grade</h4>'
        f'<div class="report-stat"><span class="grade-badge {grade_cls}">{grade_label}</span></div>'
        f'<div class="report-range">{overall:.0f}% readings in safe range</div></div>',
        unsafe_allow_html=True
    )
with sc3:
    # Alert count
    alert_count = sum(1 for r in data if r.get('alerts') and len(r['alerts']) > 0)
    st.markdown(
        f'<div class="report-card"><h4>🔔 Alerts</h4>'
        f'<div class="report-stat"><span class="big" style="color:{"#f44336" if alert_count > 0 else "#4CAF50"}">{alert_count}</span>'
        f'<span class="unit">{"issues found" if alert_count > 0 else "all clear"}</span></div></div>',
        unsafe_allow_html=True
    )
with sc4:
    # Most common stage
    stages = df['prediction_label'].dropna()
    if not stages.empty:
        top_stage = stages.mode().iloc[0].replace('_', ' ').title()
    else:
        top_stage = 'N/A'
    st.markdown(
        f'<div class="report-card"><h4>🌾 Primary Stage</h4>'
        f'<div class="report-stat"><span class="big" style="font-size:1.3rem;">{top_stage}</span></div></div>',
        unsafe_allow_html=True
    )

st.markdown("")

# --- Soil parameter summaries ---
st.markdown("### Soil Summary")

def make_summary_card(icon, name, series, unit, low, high, color):
    if series.empty:
        return
    avg = series.mean()
    mn = series.min()
    mx = series.max()
    in_range_pct = grade_metric(series, low, high)
    if in_range_pct >= 80:
        status_cls = 'grade-a'
        status_text = 'Healthy'
    elif in_range_pct >= 50:
        status_cls = 'grade-b'
        status_text = 'Watch'
    else:
        status_cls = 'grade-c'
        status_text = 'Alert'

    st.markdown(
        f'<div class="report-card">'
        f'<h4>{icon} {name} <span class="grade-badge {status_cls}" style="font-size:0.75rem;">{status_text}</span></h4>'
        f'<div class="report-stat"><span class="big" style="color:{color};">{avg:.1f}</span>'
        f'<span class="unit">{unit} avg</span></div>'
        f'<div class="report-range">'
        f'<span>Low: {mn:.1f}{unit}</span>'
        f'<span>High: {mx:.1f}{unit}</span>'
        f'<span>In range: {in_range_pct:.0f}%</span>'
        f'</div></div>',
        unsafe_allow_html=True
    )

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    if 'soil_moisture' in df.columns:
        make_summary_card('💧', 'Water Level', df['soil_moisture'].dropna(), '%', 40, 80, '#2196F3')
with sc2:
    if 'soil_temperature' in df.columns:
        make_summary_card('🌡️', 'Temperature', df['soil_temperature'].dropna(), '°C', 18, 35, '#FF7043')
with sc3:
    if 'ph' in df.columns:
        make_summary_card('🧪', 'Soil pH', df['ph'].dropna(), '', 5.5, 7.0, '#AB47BC')
with sc4:
    if 'ec' in df.columns:
        make_summary_card('🧬', 'Nutrients', df['ec'].dropna(), ' µS/cm', 200, 2000, '#26A69A')

# --- Hourly trend chart ---
st.markdown("")
st.markdown("### Hourly Trends")

df['hour'] = df['timestamp'].dt.hour
hourly = df.groupby('hour').agg({
    'soil_moisture': 'mean',
    'soil_temperature': 'mean',
    'ph': 'mean',
}).reset_index()

if not hourly.empty:
    fig = go.Figure()
    for col, color, name in [
        ('soil_moisture', '#2196F3', 'Moisture %'),
        ('soil_temperature', '#FF7043', 'Temp °C'),
        ('ph', '#AB47BC', 'pH'),
    ]:
        if col in hourly.columns:
            fig.add_trace(go.Bar(
                x=hourly['hour'], y=hourly[col],
                name=name, marker_color=color,
                opacity=0.8,
                hovertemplate=f'{name}: %{{y:.1f}}<br>Hour: %{{x}}:00<extra></extra>'
            ))
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Hour of Day', dtick=2, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.04)'),
        barmode='group',
        legend=dict(orientation='h', yanchor='top', y=1.15, xanchor='center', x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Growth Stage breakdown ---
if not stages.empty:
    st.markdown("### Growth Stages Detected")
    stage_counts = stages.value_counts()
    for stage_name, count in stage_counts.items():
        pct = count / len(stages) * 100
        display_name = stage_name.replace('_', ' ').title()
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">'
            f'<span style="font-weight:600; width:140px;">{display_name}</span>'
            f'<div style="flex:1; background:#f5f5f5; border-radius:6px; height:20px; overflow:hidden;">'
            f'<div style="background:#4CAF50; height:100%; width:{pct}%; border-radius:6px;"></div></div>'
            f'<span style="color:#9e9e9e; font-size:0.8rem; width:60px;">{count}x ({pct:.0f}%)</span>'
            f'</div>',
            unsafe_allow_html=True
        )
