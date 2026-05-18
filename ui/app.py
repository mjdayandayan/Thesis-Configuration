import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.supabase_client import fetch_recent_readings
from utils.recommendations import generate_recommendations
from utils.weather import fetch_weather

st.set_page_config(
    page_title="Rice Field Monitor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    .block-container { padding-top: 1.5rem !important; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 40%, #43a047 100%);
        color: white;
        padding: 28px 36px;
        border-radius: 20px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .hero-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; }
    .hero-banner .subtitle { opacity: 0.85; margin-top: 4px; font-size: 0.95rem; }
    .hero-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 12px;
    }
    .hero-status .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
    .dot-green { background: #69f0ae; box-shadow: 0 0 8px #69f0ae; }
    .dot-yellow { background: #ffd54f; box-shadow: 0 0 8px #ffd54f; }
    .dot-red { background: #ef5350; box-shadow: 0 0 8px #ef5350; }

    /* Glass cards */
    .glass-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .glass-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.08); }
    .glass-card .card-icon { font-size: 1.5rem; margin-bottom: 4px; }
    .glass-card .card-label { color: #757575; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .glass-card .card-value { font-size: 1.7rem; font-weight: 700; color: #212121; margin: 4px 0; }
    .glass-card .card-badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-good { background: #e8f5e9; color: #2e7d32; }
    .badge-warn { background: #fff3e0; color: #e65100; }
    .badge-bad  { background: #ffebee; color: #c62828; }

    /* Growth stage */
    .stage-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .stage-card::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.15);
        border-radius: 50%;
    }
    .stage-card .stage-icon { font-size: 3.5rem; }
    .stage-card h2 { margin: 8px 0 4px; color: #1b5e20; font-size: 1.5rem; }
    .stage-card p { color: #388e3c; font-size: 0.9rem; margin: 0; }
    .stage-card .conf-bar { margin-top: 14px; }

    /* Progress timeline */
    .timeline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
    }
    .tl-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    .tl-step::before {
        content: '';
        position: absolute;
        top: 16px;
        left: -50%;
        right: 50%;
        height: 3px;
        background: #e0e0e0;
        z-index: 0;
    }
    .tl-step:first-child::before { display: none; }
    .tl-step.active::before { background: #4CAF50; }
    .tl-step.completed::before { background: #4CAF50; }
    .tl-dot {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        z-index: 1;
        background: #e0e0e0;
        color: #9e9e9e;
    }
    .tl-step.active .tl-dot { background: #4CAF50; color: white; box-shadow: 0 0 12px rgba(76,175,80,0.4); }
    .tl-step.completed .tl-dot { background: #81c784; color: white; }
    .tl-label { font-size: 0.7rem; color: #9e9e9e; margin-top: 6px; text-align: center; font-weight: 500; }
    .tl-step.active .tl-label { color: #2e7d32; font-weight: 600; }
    .tl-step.completed .tl-label { color: #66bb6a; }

    /* Section header */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #424242;
        margin: 24px 0 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Score ring container */
    .score-container { text-align: center; }

    /* Hide default streamlit padding on dataframe */
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

    /* Weather widget */
    .weather-bar {
        display: flex;
        align-items: center;
        gap: 20px;
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 14px;
        padding: 14px 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.03);
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    .weather-bar .weather-item {
        display: flex; align-items: center; gap: 6px;
        font-size: 0.85rem; color: #616161; font-weight: 500;
    }
    .weather-bar .weather-main {
        font-size: 1rem; font-weight: 600; color: #424242;
    }

    /* Recommendation cards */
    .rec-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.03);
        transition: transform 0.15s;
    }
    .rec-card:hover { transform: translateY(-2px); }
    .rec-card .rec-icon { font-size: 1.3rem; }
    .rec-card .rec-title { font-weight: 600; font-size: 0.9rem; color: #212121; }
    .rec-card .rec-msg { font-size: 0.82rem; color: #757575; margin-top: 4px; }
    .rec-card.priority-high { border-left: 4px solid #f44336; }
    .rec-card.priority-medium { border-left: 4px solid #FF9800; }
    .rec-card.priority-low { border-left: 4px solid #4CAF50; }

    /* Growth stage transition log */
    .transition-log {
        display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px;
    }
    .transition-item {
        background: rgba(255,255,255,0.85);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 0.8rem;
        display: flex; flex-direction: column; align-items: center;
    }
    .transition-item .t-icon { font-size: 1.3rem; }
    .transition-item .t-stage { font-weight: 600; color: #424242; margin-top: 2px; }
    .transition-item .t-date { color: #9e9e9e; font-size: 0.72rem; }



    /* Mobile responsive */
    @media (max-width: 768px) {
        .hero-banner { padding: 20px 20px; border-radius: 14px; }
        .hero-banner h1 { font-size: 1.3rem; }
        .glass-card .card-value { font-size: 1.3rem; }
        .glass-card { padding: 14px 16px; }
        .stage-card { padding: 20px; }
        .stage-card .stage-icon { font-size: 2.5rem; }
        .stage-card h2 { font-size: 1.2rem; }
        .weather-bar { padding: 10px 14px; gap: 12px; }
        .timeline { gap: 4px; }
        .tl-dot { width: 26px; height: 26px; font-size: 0.75rem; }
        .tl-label { font-size: 0.6rem; }
    }

    /* Dark mode support */
    [data-theme="dark"] .glass-card,
    [data-theme="dark"] .weather-bar,
    [data-theme="dark"] .rec-card {
        background: rgba(30,30,30,0.85);
        border-color: rgba(255,255,255,0.08);
    }
    [data-theme="dark"] .glass-card .card-label,
    [data-theme="dark"] .rec-card .rec-msg { color: #bdbdbd; }
    [data-theme="dark"] .glass-card .card-value,
    [data-theme="dark"] .rec-card .rec-title { color: #e0e0e0; }
    [data-theme="dark"] .section-header { color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🌾 Rice Field Monitor")
    st.caption("Smart IoT monitoring system")
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    auto_refresh = st.toggle("⚡ Live Mode (auto-refresh)", value=False)
    if auto_refresh:
        st.caption("Refreshing every 30 seconds")

# --- Auto-refresh ---
if auto_refresh:
    st.markdown(
        '<meta http-equiv="refresh" content="30">',
        unsafe_allow_html=True
    )

# --- Fetch data ---
recent = fetch_recent_readings(limit=20)

if not recent:
    st.markdown(
        '<div class="hero-banner">'
        '<h1>🌾 Rice Field Monitor</h1>'
        '<p class="subtitle">Smart monitoring for your rice field</p>'
        '<div class="hero-status"><span class="dot dot-yellow"></span> Waiting for sensor data...</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align:center; padding:80px 20px;'>"
        "<div style='font-size:4rem; margin-bottom:16px;'>📡</div>"
        "<h2 style='color:#424242; font-weight:600;'>Setting Up...</h2>"
        "<p style='color:#9e9e9e; max-width:400px; margin:8px auto;'>"
        "Your field monitor will appear here once the Raspberry Pi starts sending data.</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

latest = recent[0]
previous = recent[1] if len(recent) > 1 else None

# --- Hero Banner ---
last_time = latest.get('timestamp', '')
status_html = ''
if last_time:
    try:
        last_dt = datetime.fromisoformat(str(last_time).replace('Z', '+00:00'))
        now = datetime.now(last_dt.tzinfo) if last_dt.tzinfo else datetime.now()
        diff = now - last_dt
        if diff < timedelta(minutes=10):
            status_html = '<div class="hero-status"><span class="dot dot-green"></span> Live — sensors active</div>'
        elif diff < timedelta(hours=1):
            mins = diff.seconds // 60
            status_html = f'<div class="hero-status"><span class="dot dot-yellow"></span> Last update {mins}m ago</div>'
        else:
            status_html = '<div class="hero-status"><span class="dot dot-red"></span> Sensor offline</div>'
    except Exception:
        pass

st.markdown(
    f'<div class="hero-banner">'
    f'<h1>🌾 Rice Field Monitor</h1>'
    f'<p class="subtitle">Real-time soil & growth monitoring for your rice field</p>'
    f'{status_html}'
    f'</div>',
    unsafe_allow_html=True
)

# ========== WEATHER BAR ==========
try:
    lat = st.secrets.get("LATITUDE", 8.2)
    lon = st.secrets.get("LONGITUDE", 123.85)
except Exception:
    lat, lon = 8.2, 123.85

weather = fetch_weather(latitude=lat, longitude=lon)
if weather.get('ok'):
    w_items = (
        f'<span class="weather-main">{weather["icon"]} {weather["description"]}</span>'
        f'<span class="weather-item">🌡️ {weather["temperature"]}°C outdoor</span>'
        f'<span class="weather-item">💧 {weather["humidity"]}% humidity</span>'
        f'<span class="weather-item">🌧️ {weather["precipitation"]} mm rain</span>'
        f'<span class="weather-item">💨 {weather["wind_speed"]} km/h wind</span>'
    )
    st.markdown(f'<div class="weather-bar">{w_items}</div>', unsafe_allow_html=True)

# ========== ROW 1: Health Score + Growth Stage + Photo ==========
col_score, col_stage, col_photo = st.columns([1, 1.2, 1.3])

# --- Field Health Score ---
def calc_health_score(data):
    """Calculate 0-100 health score from soil readings."""
    scores = []
    m = data.get('soil_moisture')
    if m is not None:
        if 40 <= m <= 80:
            scores.append(100)
        elif 30 <= m < 40 or 80 < m <= 90:
            scores.append(60)
        else:
            scores.append(20)
    t = data.get('soil_temperature')
    if t is not None:
        if 18 <= t <= 35:
            scores.append(100)
        elif 15 <= t < 18 or 35 < t <= 38:
            scores.append(60)
        else:
            scores.append(20)
    p = data.get('ph')
    if p is not None:
        if 5.5 <= p <= 7.0:
            scores.append(100)
        elif 5.0 <= p < 5.5 or 7.0 < p <= 7.5:
            scores.append(60)
        else:
            scores.append(20)
    e = data.get('ec')
    if e is not None:
        if 200 <= e <= 2000:
            scores.append(100)
        elif 100 <= e < 200 or 2000 < e <= 2500:
            scores.append(60)
        else:
            scores.append(20)
    return round(sum(scores) / len(scores)) if scores else 0

health = calc_health_score(latest)

with col_score:
    if health >= 80:
        gauge_color = "#4CAF50"
        health_label = "Excellent"
    elif health >= 60:
        gauge_color = "#FF9800"
        health_label = "Fair"
    else:
        gauge_color = "#f44336"
        health_label = "Needs Care"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        number=dict(suffix="", font=dict(size=42, color=gauge_color)),
        gauge=dict(
            axis=dict(range=[0, 100], showticklabels=False, dtick=25),
            bar=dict(color=gauge_color, thickness=0.3),
            bgcolor="rgba(0,0,0,0.03)",
            borderwidth=0,
            steps=[
                dict(range=[0, 40], color="rgba(244,67,54,0.08)"),
                dict(range=[40, 70], color="rgba(255,152,0,0.08)"),
                dict(range=[70, 100], color="rgba(76,175,80,0.08)"),
            ],
        ),
        title=dict(text=f"<b>Field Health</b><br><span style='font-size:0.85rem;color:{gauge_color}'>{health_label}</span>",
                   font=dict(size=14)),
    ))
    fig.update_layout(
        height=210, margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True, key="health_gauge")

# --- Growth Stage ---
label = latest.get('prediction_label', '')
confidence = latest.get('prediction_confidence', 0)

STAGE_INFO = {
    'vegetative stage': ('🌱', 'Vegetative Stage', 'Growing leaves and tillers', 1),
    'heading stage': ('🌿', 'Heading Stage', 'Panicle developing in stem', 2),
    'flowering stage': ('🌸', 'Flowering Stage', 'Critical flowering phase', 3),
    'maturing stage': ('🌾', 'Maturing Stage', 'Almost ready for harvest!', 4),
    'weed growth': ('🚨', 'Weed Detected', 'Weeds need removal', 0),
}

icon, stage_name, stage_desc, stage_idx = STAGE_INFO.get(
    label.lower() if label else '',
    ('🔍', 'Scanning...', 'Analyzing growth stage', 0)
)

with col_stage:
    conf_pct = int((confidence or 0) * 100)
    st.markdown(
        f'<div class="stage-card">'
        f'<div class="stage-icon">{icon}</div>'
        f'<h2>{stage_name}</h2>'
        f'<p>{stage_desc}</p>'
        f'<div class="conf-bar">'
        f'<div style="background:rgba(0,0,0,0.08); border-radius:10px; height:8px; overflow:hidden; margin-top:8px;">'
        f'<div style="background:#2e7d32; height:100%; width:{conf_pct}%; border-radius:10px;"></div>'
        f'</div>'
        f'<span style="font-size:0.75rem; color:#558b2f;">{conf_pct}% confidence</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_photo:
    image_url = latest.get('image_url')
    if image_url:
        st.image(image_url, caption="Latest field capture", use_container_width=True)
    else:
        st.markdown(
            "<div style='text-align:center; padding:55px 20px; background:linear-gradient(135deg,#f5f5f5,#eeeeee); "
            "border-radius:16px; border:2px dashed #e0e0e0;'>"
            "<div style='font-size:2.5rem; margin-bottom:8px;'>📷</div>"
            "<p style='color:#9e9e9e; font-weight:500;'>Awaiting field photo</p></div>",
            unsafe_allow_html=True
        )

# --- Growth Progress Timeline ---
stages_timeline = [
    ('🌱', 'Vegetative'),
    ('🌿', 'Heading'),
    ('🌸', 'Flowering'),
    ('🌾', 'Maturing'),
]

tl_html = '<div class="timeline">'
for i, (s_icon, s_label) in enumerate(stages_timeline):
    if i + 1 < stage_idx:
        cls = 'completed'
    elif i + 1 == stage_idx:
        cls = 'active'
    else:
        cls = ''
    tl_html += (
        f'<div class="tl-step {cls}">'
        f'<div class="tl-dot">{s_icon}</div>'
        f'<div class="tl-label">{s_label}</div>'
        f'</div>'
    )
tl_html += '</div>'
st.markdown(tl_html, unsafe_allow_html=True)

# ========== ROW 2: Soil Health Gauges ==========
st.markdown('<div class="section-header">🌍 Soil Conditions</div>', unsafe_allow_html=True)


def soil_status(value, low, high):
    if value is None:
        return "No Data", "warn"
    if low <= value <= high:
        return "Good", "good"
    elif abs(value - low) <= (high - low) * 0.2 or abs(value - high) <= (high - low) * 0.2:
        return "Watch", "warn"
    else:
        return "Alert", "bad"


def make_soil_card(icon, label, value, unit, low, high, color):
    status, cls = soil_status(value, low, high)
    pct = 0
    if value is not None and high > low:
        pct = min(100, max(0, (value - low) / (high - low) * 100))
    return (
        f'<div class="glass-card">'
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-label">{label}</div>'
        f'<div class="card-value" style="color:{color};">{value}{unit}</div>'
        f'<span class="card-badge badge-{cls}">{status}</span>'
        f'<div style="background:rgba(0,0,0,0.05); border-radius:6px; height:6px; margin-top:10px; overflow:hidden;">'
        f'<div style="background:{color}; height:100%; width:{pct}%; border-radius:6px; '
        f'transition:width 0.5s;"></div></div>'
        f'</div>'
    )


c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(make_soil_card(
        '💧', 'Water Level',
        latest.get('soil_moisture'), '%', 40, 80, '#2196F3'
    ), unsafe_allow_html=True)

with c2:
    st.markdown(make_soil_card(
        '🌡️', 'Temperature',
        latest.get('soil_temperature'), '°C', 18, 35, '#FF7043'
    ), unsafe_allow_html=True)

with c3:
    st.markdown(make_soil_card(
        '🧪', 'Soil pH',
        latest.get('ph'), '', 5.5, 7.0, '#AB47BC'
    ), unsafe_allow_html=True)

with c4:
    st.markdown(make_soil_card(
        '🧬', 'Nutrients',
        latest.get('ec'), '', 200, 2000, '#26A69A'
    ), unsafe_allow_html=True)

with c5:
    st.markdown(make_soil_card(
        '💨', 'Humidity',
        latest.get('soil_humidity'), '%', 40, 90, '#78909C'
    ), unsafe_allow_html=True)

# ========== ROW 3: Sparkline Trends + Recent Table ==========
st.markdown("")
col_chart, col_table = st.columns([1.2, 1])

with col_chart:
    st.markdown('<div class="section-header">📈 Last 20 Readings</div>', unsafe_allow_html=True)
    df_trend = pd.DataFrame(recent[::-1])  # oldest first for chart
    if 'timestamp' in df_trend.columns and 'soil_moisture' in df_trend.columns:
        df_trend['timestamp'] = pd.to_datetime(df_trend['timestamp'])
        fig = go.Figure()
        for col_name, color, name in [
            ('soil_moisture', '#2196F3', 'Water'),
            ('soil_temperature', '#FF7043', 'Temp'),
            ('ph', '#AB47BC', 'pH'),
        ]:
            if col_name in df_trend.columns:
                # Normalize to 0-100 for overlay
                vals = df_trend[col_name].dropna()
                if len(vals) > 0:
                    vmin, vmax = vals.min(), vals.max()
                    if vmax > vmin:
                        norm = ((vals - vmin) / (vmax - vmin)) * 100
                    else:
                        norm = vals * 0 + 50
                    fig.add_trace(go.Scatter(
                        x=df_trend['timestamp'], y=norm,
                        mode='lines',
                        name=name,
                        line=dict(color=color, width=2.5, shape='spline'),
                        hovertemplate=f'{name}: %{{customdata:.1f}}<extra></extra>',
                        customdata=vals,
                    ))
        fig.update_layout(
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False, range=[-5, 105]),
            legend=dict(orientation='h', yanchor='top', y=1.15, xanchor='center', x=0.5,
                        font=dict(size=11)),
            hovermode='x unified',
        )
        st.plotly_chart(fig, use_container_width=True, key="sparklines")

with col_table:
    st.markdown('<div class="section-header">📋 Recent Readings</div>', unsafe_allow_html=True)
    df_table = pd.DataFrame(recent[:8])
    display_cols = {
        'timestamp': 'Time',
        'soil_moisture': 'Water',
        'soil_temperature': 'Temp',
        'ph': 'pH',
        'prediction_label': 'Stage',
    }
    available = {k: v for k, v in display_cols.items() if k in df_table.columns}
    if available:
        show_df = df_table[list(available.keys())].rename(columns=available)
        if 'Stage' in show_df.columns:
            show_df['Stage'] = show_df['Stage'].str.replace('_', ' ').str.title()
        if 'Time' in show_df.columns:
            show_df['Time'] = pd.to_datetime(show_df['Time']).dt.strftime('%I:%M %p')
        st.dataframe(show_df, use_container_width=True, hide_index=True, height=260)

# ========== ROW 4: Smart Recommendations ==========
st.markdown("")
st.markdown('<div class="section-header">💡 Smart Recommendations</div>', unsafe_allow_html=True)

tips = generate_recommendations(recent)
if tips:
    rec_cols = st.columns(len(tips))
    for i, tip in enumerate(tips):
        with rec_cols[i]:
            st.markdown(
                f'<div class="rec-card priority-{tip["priority"]}">'
                f'<div class="rec-icon">{tip["icon"]}</div>'
                f'<div class="rec-title">{tip["title"]}</div>'
                f'<div class="rec-msg">{tip["message"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

# ========== ROW 5: Growth Stage Transition Log ==========
st.markdown("")
st.markdown('<div class="section-header">🕐 Growth Stage Timeline</div>', unsafe_allow_html=True)

# Find first occurrence of each growth stage from readings (oldest first)
stage_order = ['vegetative stage', 'heading stage', 'flowering stage', 'maturing stage', 'weed growth']
stage_icons = {'vegetative stage': '🌱', 'heading stage': '🌿', 'flowering stage': '🌸', 'maturing stage': '🌾', 'weed growth': '🚨'}
stage_names = {'vegetative stage': 'Vegetative', 'heading stage': 'Heading', 'flowering stage': 'Flowering', 'maturing stage': 'Maturing', 'weed growth': 'Weed'}

first_seen = {}
for r in reversed(recent):  # oldest first
    s = (r.get('prediction_label') or '').lower()
    if s in stage_order and s not in first_seen:
        ts = r.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
            first_seen[s] = dt.strftime('%b %d, %I:%M %p')
        except Exception:
            first_seen[s] = str(ts)[:16]

if first_seen:
    tl_html = '<div class="transition-log">'
    for s in stage_order:
        if s in first_seen:
            tl_html += (
                f'<div class="transition-item">'
                f'<div class="t-icon">{stage_icons[s]}</div>'
                f'<div class="t-stage">{stage_names[s]}</div>'
                f'<div class="t-date">First seen: {first_seen[s]}</div>'
                f'</div>'
            )
    tl_html += '</div>'
    st.markdown(tl_html, unsafe_allow_html=True)
else:
    st.caption("Stage transitions will appear here as the system detects different growth stages.")
