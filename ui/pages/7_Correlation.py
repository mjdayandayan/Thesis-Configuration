import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils.supabase_client import fetch_recent_readings
from utils.correlation import compute_correlations, interpret_correlation, DISPLAY_NAMES


def generate_mock_readings(n=50):
    """Generate realistic mock soil sensor readings with natural correlations."""
    rng = np.random.default_rng(42)
    base_temp = 28 + rng.normal(0, 2, n)
    base_moisture = 55 + rng.normal(0, 8, n)
    # Humidity correlates positively with moisture
    base_humidity = 0.6 * base_moisture + 20 + rng.normal(0, 4, n)
    # pH weakly anti-correlates with EC
    base_ec = 1.2 + rng.normal(0, 0.3, n)
    base_ph = 6.5 - 0.4 * (base_ec - 1.2) + rng.normal(0, 0.3, n)

    now = datetime.utcnow()
    readings = []
    for i in range(n):
        readings.append({
            "timestamp": (now - timedelta(minutes=30 * (n - i))).isoformat(),
            "soil_temperature": round(float(np.clip(base_temp[i], 20, 40)), 1),
            "soil_moisture": round(float(np.clip(base_moisture[i], 20, 90)), 1),
            "soil_humidity": round(float(np.clip(base_humidity[i], 30, 95)), 1),
            "ec": round(float(np.clip(base_ec[i], 0.2, 3.0)), 2),
            "ph": round(float(np.clip(base_ph[i], 4.0, 9.0)), 2),
        })
    return readings

st.set_page_config(page_title="Sensor Correlation", page_icon="🔗", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .page-hdr {
        background: linear-gradient(135deg, #6A1B9A 0%, #8E24AA 40%, #AB47BC 100%);
        color: white; padding: 28px 36px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-hdr h1 { margin: 0; font-size: 1.8rem; font-weight: 700; }
    .page-hdr p { opacity: 0.85; margin-top: 4px; font-size: 0.95rem; }
    .insight-card {
        background: rgba(255,255,255,0.9); border-radius: 14px;
        border: 1px solid rgba(0,0,0,0.06); padding: 14px 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.03); margin-bottom: 10px;
    }
    .insight-card .corr-val { font-weight: 700; font-size: 1.1rem; }
    .insight-card .corr-text { font-size: 0.85rem; color: #616161; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-hdr">'
    '<h1>🔗 Sensor Correlation Analysis</h1>'
    '<p>Discover relationships between your soil parameters</p>'
    '</div>',
    unsafe_allow_html=True
)

# Time window & data source
col_w, col_m = st.columns([2, 1])
with col_w:
    window = st.selectbox("Time Window", [20, 30, 50], index=1, format_func=lambda x: f"Last {x} readings")

readings = fetch_recent_readings(limit=window)
use_mock = not readings or len(readings) < 3

with col_m:
    if use_mock:
        st.info("No live data — using demo data")
    else:
        use_mock = st.toggle("Use demo data", value=False)

if use_mock:
    readings = generate_mock_readings(n=window)

corr, count = compute_correlations(readings)
if corr is None:
    st.warning("Not enough valid data for correlation.")
    st.stop()

label = "demo" if use_mock else "live"
st.caption(f"Based on **{count}** {label} readings")

# --- Heatmap ---
labels = list(corr.columns)
z = corr.values.tolist()

fig = go.Figure(data=go.Heatmap(
    z=z,
    x=labels,
    y=labels,
    colorscale=[
        [0, '#f44336'],
        [0.25, '#FF9800'],
        [0.5, '#EEEEEE'],
        [0.75, '#66BB6A'],
        [1, '#1B5E20'],
    ],
    zmid=0,
    zmin=-1,
    zmax=1,
    text=[[f'{v:.2f}' for v in row] for row in z],
    texttemplate='%{text}',
    textfont=dict(size=14, color='#212121'),
    hovertemplate='%{x} vs %{y}: r = %{z:.3f}<extra></extra>',
    colorbar=dict(
        title=dict(text='r', side='right'),
        tickvals=[-1, -0.5, 0, 0.5, 1],
        ticktext=['-1.0', '-0.5', '0', '0.5', '1.0'],
    ),
))
fig.update_layout(
    height=420,
    margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(side='bottom'),
    yaxis=dict(autorange='reversed'),
)
st.plotly_chart(fig, width="stretch")

# --- Key Insights ---
st.markdown("#### 💡 Key Insights")

# Extract significant correlations (|r| > 0.3, off-diagonal)
insights = []
seen = set()
for i, row_label in enumerate(labels):
    for j, col_label in enumerate(labels):
        if i >= j:
            continue
        r_val = corr.iloc[i, j]
        if abs(r_val) >= 0.3:
            key = tuple(sorted([row_label, col_label]))
            if key not in seen:
                seen.add(key)
                insights.append((row_label, col_label, r_val))

insights.sort(key=lambda x: abs(x[2]), reverse=True)

if insights:
    for p1, p2, r_val in insights:
        interp = interpret_correlation(r_val, p1, p2)
        color = '#4CAF50' if r_val > 0 else '#f44336'
        icon = '📈' if r_val > 0 else '📉'
        st.markdown(
            f'<div class="insight-card">'
            f'<span style="font-size:1.2rem;">{icon}</span> '
            f'<b>{p1}</b> vs <b>{p2}</b>'
            f'<span class="corr-val" style="color:{color}; margin-left:12px;">r = {r_val:.3f}</span>'
            f'<div class="corr-text">{interp}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
else:
    st.info("No significant correlations found (|r| < 0.3). This may change with more data.")

# --- Guide ---
st.markdown("---")
st.markdown("##### Reading the Correlation Matrix")
st.markdown(
    "- **r = +1.0**: Perfect positive — both parameters rise and fall together\n"
    "- **r = 0**: No linear relationship\n"
    "- **r = -1.0**: Perfect negative — one rises as the other falls\n\n"
    "**Significance guide:** |r| > 0.6 = Strong, 0.3–0.6 = Moderate, < 0.3 = Weak"
)
