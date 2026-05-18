import streamlit as st
from utils.supabase_client import fetch_images

st.set_page_config(page_title="Field Photos", page_icon="📷", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .block-container { padding-top: 1.5rem !important; }
    .page-header {
        background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 40%, #ab47bc 100%);
        color: white; padding: 24px 32px; border-radius: 20px; margin-bottom: 24px;
    }
    .page-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .page-header p { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }
    .photo-card {
        border-radius: 16px;
        overflow: hidden;
        background: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin-bottom: 16px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .photo-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
    .photo-meta {
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .photo-meta .time { color: #9e9e9e; font-size: 0.8rem; }
    .photo-meta .stage-tag {
        background: #e8f5e9; color: #2e7d32;
        padding: 3px 10px; border-radius: 10px;
        font-size: 0.75rem; font-weight: 600;
    }
    .weed-tag { background: #ffebee !important; color: #c62828 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-header">'
    '<h1>📷 Field Photos</h1>'
    '<p>AI-captured images from your rice field</p>'
    '</div>',
    unsafe_allow_html=True
)

images = fetch_images(limit=12)

if not images:
    st.markdown(
        "<div style='text-align:center; padding:80px 20px;'>"
        "<div style='font-size:4rem; margin-bottom:16px;'>📷</div>"
        "<h2 style='color:#424242; font-weight:600;'>No Photos Yet</h2>"
        "<p style='color:#9e9e9e; max-width:400px; margin:8px auto;'>"
        "Field photos will appear here once the camera starts capturing.</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

st.markdown(f"<p style='color:#9e9e9e; font-size:0.85rem;'>Showing {len(images)} most recent captures</p>",
            unsafe_allow_html=True)

# Display in grid (2 columns for bigger, clearer photos)
cols_per_row = 2
for i in range(0, len(images), cols_per_row):
    cols = st.columns(cols_per_row, gap="medium")
    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(images):
            img = images[idx]
            with col:
                if img.get('image_url'):
                    label = img.get('prediction_label', '')
                    ts = img.get('timestamp', '')
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                        ts_display = dt.strftime('%b %d, %I:%M %p')
                    except Exception:
                        ts_display = str(ts)[:16]

                    stage_display = label.replace('_', ' ').title() if label else 'Unknown'
                    tag_cls = 'weed-tag' if 'weed' in label.lower() else ''

                    st.image(img['image_url'], use_container_width=True)
                    st.markdown(
                        f'<div class="photo-meta">'
                        f'<span class="time">{ts_display}</span>'
                        f'<span class="stage-tag {tag_cls}">{stage_display}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
