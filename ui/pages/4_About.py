import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem !important; }
    .page-header {
        background: linear-gradient(135deg, #37474f 0%, #455a64 40%, #607d8b 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .info-card {
        background: white; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 16px;
        border: 1px solid rgba(0,0,0,0.06);
    }
    .info-card h3 { margin: 0 0 12px; color: #212121; font-size: 1.1rem; }
    .info-card p { color: #616161; font-size: 0.9rem; line-height: 1.6; margin: 0; }
    .hw-item {
        display: flex; align-items: center; gap: 12px;
        padding: 12px 0; border-bottom: 1px solid #f5f5f5;
    }
    .hw-item:last-child { border-bottom: none; }
    .hw-item .hw-icon { font-size: 1.5rem; }
    .hw-item .hw-name { font-weight: 600; color: #212121; }
    .hw-item .hw-desc { font-size: 0.8rem; color: #9e9e9e; }
    .flow-step {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 0;
    }
    .flow-step .flow-num {
        width: 28px; height: 28px; border-radius: 50%;
        background: #4CAF50; color: white; display: flex;
        align-items: center; justify-content: center;
        font-size: 0.8rem; font-weight: 700; flex-shrink: 0;
    }
    .flow-step .flow-text { font-size: 0.9rem; color: #424242; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-header">'
    '<h1>ℹ️ About This System</h1>'
    '<p>IoT-Enabled Rice Growth Detection & Soil Nutrient Monitoring</p>'
    '</div>',
    unsafe_allow_html=True
)

# --- How it Works ---
col_how, col_hw = st.columns(2)

with col_how:
    st.markdown(
        '<div class="info-card">'
        '<h3>🔄 How It Works</h3>'
        '<div class="flow-step"><div class="flow-num">1</div>'
        '<div class="flow-text"><b>Sensors read soil</b> — moisture, temperature, pH, nutrients, humidity every 5 minutes</div></div>'
        '<div class="flow-step"><div class="flow-num">2</div>'
        '<div class="flow-text"><b>Camera captures</b> a photo of the rice field</div></div>'
        '<div class="flow-step"><div class="flow-num">3</div>'
        '<div class="flow-text"><b>AI analyzes</b> the photo to detect growth stage or weeds</div></div>'
        '<div class="flow-step"><div class="flow-num">4</div>'
        '<div class="flow-text"><b>Data is sent</b> to the cloud (Supabase)</div></div>'
        '<div class="flow-step"><div class="flow-num">5</div>'
        '<div class="flow-text"><b>Dashboard displays</b> everything in real-time for the farmer</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

with col_hw:
    st.markdown(
        '<div class="info-card">'
        '<h3>🔧 Hardware Components</h3>'
        '<div class="hw-item"><div class="hw-icon">🖥️</div><div>'
        '<div class="hw-name">Raspberry Pi 5</div>'
        '<div class="hw-desc">Main processing unit deployed in the field</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">📷</div><div>'
        '<div class="hw-name">Logitech C922 Pro HD</div>'
        '<div class="hw-desc">1080p webcam for rice field image capture</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🌡️</div><div>'
        '<div class="hw-name">RS485 5-in-1 Soil Sensor</div>'
        '<div class="hw-desc">Measures moisture, temp, pH, EC, humidity via Modbus RTU</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🔌</div><div>'
        '<div class="hw-name">USB-to-RS485 Adapter</div>'
        '<div class="hw-desc">Protocol bridge between Pi and soil sensor</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">⚡</div><div>'
        '<div class="hw-name">12V DC Power Supply</div>'
        '<div class="hw-desc">Powers the soil sensor (separate from Pi)</div>'
        '</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

# --- AI Model + Growth Stages ---
col_ai, col_stages = st.columns(2)

with col_ai:
    st.markdown(
        '<div class="info-card">'
        '<h3>🤖 AI Model</h3>'
        '<p><b>YOLO-Pro</b> (Edge Impulse)<br>'
        'Architecture: Attention with SiLU, nano variant<br>'
        'Parameters: 2.4 million<br>'
        'Training: 200 cycles, LR 0.001, pretrained weights<br>'
        'Augmentation: Medium spatial & color<br>'
        'Confidence threshold: 40%</p>'
        '</div>',
        unsafe_allow_html=True
    )

with col_stages:
    st.markdown(
        '<div class="info-card">'
        '<h3>🌾 Detection Classes</h3>'
        '<div class="hw-item"><div class="hw-icon">🌱</div><div>'
        '<div class="hw-name">Vegetative Stage</div>'
        '<div class="hw-desc">Growing leaves and tillers</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🌿</div><div>'
        '<div class="hw-name">Heading Stage</div>'
        '<div class="hw-desc">Panicle developing inside the stem</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🌸</div><div>'
        '<div class="hw-name">Flowering Stage</div>'
        '<div class="hw-desc">Critical pollination phase</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🌾</div><div>'
        '<div class="hw-name">Maturing Stage</div>'
        '<div class="hw-desc">Grains filling — near harvest</div>'
        '</div></div>'
        '<div class="hw-item"><div class="hw-icon">🚨</div><div>'
        '<div class="hw-name">Weed Growth</div>'
        '<div class="hw-desc">Unwanted vegetation detected</div>'
        '</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

# --- Soil Thresholds ---
st.markdown(
    '<div class="info-card">'
    '<h3>📏 Safe Soil Ranges for Rice</h3>'
    '<p>The system alerts you when readings go outside these ranges:</p>'
    '</div>',
    unsafe_allow_html=True
)

thresh_data = {
    'Parameter': ['💧 Soil Moisture', '🌡️ Temperature', '🧪 pH', '🧬 EC (Nutrients)', '💨 Humidity'],
    'Min': ['40%', '18°C', '5.5', '200 µS/cm', '40%'],
    'Max': ['100%', '35°C', '7.0', '2,000 µS/cm', '90%'],
    'What it means': [
        'How much water is in the soil',
        'How hot or cold the soil is',
        'How acidic or alkaline the soil is',
        'How much dissolved nutrients are present',
        'Moisture in the air at soil level',
    ],
}
import pandas as pd
st.dataframe(pd.DataFrame(thresh_data), use_container_width=True, hide_index=True)

# --- Tech Stack ---
st.markdown("---")
st.markdown(
    '<div class="info-card">'
    '<h3>🛠️ Technology Stack</h3>'
    '<p>'
    '<b>Field Device:</b> Python, OpenCV, Edge Impulse, MinimalModbus, Supabase REST API<br>'
    '<b>Cloud:</b> Supabase (PostgreSQL + Storage)<br>'
    '<b>Dashboard:</b> Streamlit, Plotly, Pandas<br>'
    '<b>Weather:</b> Open-Meteo API (free, no key required)'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)
