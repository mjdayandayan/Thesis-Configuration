import streamlit as st
from utils.supabase_client import fetch_images

st.set_page_config(page_title="Camera Gallery", page_icon="📷", layout="wide")

st.title("📷 Camera Gallery")
st.caption("Recent field captures from the Logitech C922 Pro")

# Number of images to load
num_images = st.slider("Number of images to load", 4, 50, 12)

images = fetch_images(limit=num_images)

if not images:
    st.info("No images captured yet. The Raspberry Pi will upload field photos once running.")
    st.stop()

# Display in grid (3 columns)
cols_per_row = 3
for i in range(0, len(images), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx < len(images):
            img = images[idx]
            with col:
                if img.get('image_url'):
                    label = img.get('prediction_label', 'N/A')
                    conf = img.get('prediction_confidence')
                    caption = f"{img.get('timestamp', '')}"
                    if label:
                        caption += f" | {label}"
                    if conf:
                        caption += f" ({conf:.1%})"
                    st.image(img['image_url'], caption=caption,
                             use_container_width=True)
