import streamlit as st
import os
from googletrans import Translator
from PIL import Image
import numpy as np
import cv2
import yagmail

# ✅ This must be FIRST and only once
st.set_page_config(
    page_title="ARQONZ GLOBAL PVT LTD",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://streamlit.io/support',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': "# Tile Calculator Chatbot\n\nBuilt with 💡 by Indhumathi V"
    }
)

# --- Set Background Image (Improved for readability) ---
st.markdown('''
    <style>
    .stApp {
        background-image: url("https://i.imgur.com/O6aYYuV.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Make text area readable by adding background to content block */
    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 12px;
    }
    </style>
''', unsafe_allow_html=True)


# --- Tile Calculation Function ---
def calculate_tiles(area, tile_length, tile_width, unit="sqft"):
    if unit == "sqm":
        area *= 10.7639  # Convert sqm to sqft
    tile_area = (tile_length / 12) * (tile_width / 12)  # Inches to sqft
    total_tiles = area / tile_area
    total_tiles_buffer = total_tiles * 1.10  # 10% extra
    tiles_per_box = 10
    total_boxes = total_tiles_buffer / tiles_per_box
    return round(total_tiles_buffer), round(total_boxes)

# --- Send Estimate via Email ---
def send_estimate_email(to_email, tiles, boxes):
    body = f"""Hello,

Here is your tile estimate:

- Total Tiles Required: {tiles}
- Total Boxes Required: {boxes}
(Including 10% buffer)

Thanks for using our Tile Calculator Bot!
"""
    try:
        yag = yagmail.SMTP("your_email@gmail.com", "your_app_password")  # Replace with actual credentials
        yag.send(to=to_email, subject="Your Tile Estimate", contents=body)
        return True
    except Exception as e:
        return str(e)

# --- Translate Text Function ---
def translate_text(text, dest_lang):
    if dest_lang == "en":
        return text
    translator = Translator()
    try:
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except:
        return text

# --- Detect Area from Image ---
def detect_area_from_image(image_path):
    img = cv2.imread(image_path, 0)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    area_pixels = np.sum(thresh == 255)
    area_sqft = area_pixels / 929.0304
    return round(area_sqft, 2)

# --- Streamlit App UI ---
st.title("🧱 Tile Calculator Chatbot")

# --- Language Selection ---
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
st.session_state.lang = st.selectbox("🌐 Select Language / மொழியைத் தேர்ந்தெடுக்கவும்", ["en", "ta", "hi", "fr", "es"], index=["en", "ta", "hi", "fr", "es"].index(st.session_state.lang))
translate = lambda txt: translate_text(txt, st.session_state.lang)

st.markdown(translate("Welcome! Let me help you calculate how many tiles you need.👇"))

# --- Session State Initialization ---
defaults = {
    'step': 1,
    'tile_type': "",
    'area': 0,
    'unit': "sqft",
    'tile_size': (12, 12),
    'result': None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Step 1: Choose Tile Type ---
if st.session_state.step == 1:
    st.subheader(translate("Are you looking for floor or wall tiles?"))
    if st.button(translate("🧱 Floor")):
        st.session_state.tile_type = "floor"
        st.session_state.step = 2
    if st.button(translate("🧱 Wall")):
        st.session_state.tile_type = "wall"
        st.session_state.step = 2

# --- Step 2: Area Input ---
elif st.session_state.step == 2:
    st.subheader(translate("📐 How do you want to input the area to cover?"))
    st.markdown("### " + translate("🔢 Manual Area Entry"))
    area_manual = st.number_input(translate("Enter area"), min_value=1.0)
    unit = st.radio(translate("Unit"), ["sqft", "sqm"], horizontal=True)

    st.markdown("### " + translate("🖼️ Upload a floor image (Optional)"))
    uploaded_file = st.file_uploader(translate("Upload image"), type=["jpg", "jpeg", "png"])
    use_image = st.checkbox(translate("✅ Use uploaded image to estimate area"))

    if st.button(translate("Next ➡️")):
        if uploaded_file and use_image:
            image_path = f"temp_{uploaded_file.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.read())
            area_est = detect_area_from_image(image_path)
            os.remove(image_path)
            st.success(translate(f"🧠 Estimated area from image: {area_est} sq.ft"))
            st.session_state.area = area_est
            st.session_state.unit = "sqft"
        else:
            st.session_state.area = area_manual
            st.session_state.unit = unit
        st.session_state.step = 3

# --- Step 3: Tile Size ---
elif st.session_state.step == 3:
    st.subheader(translate("What is the tile size?"))
    size_dict = {
        "12 x 12": (12, 12),
        "24 x 24": (24, 24),
        "18 x 12": (18, 12),
        "36 x 18": (36, 18)
    }
    size_option = st.selectbox(translate("Choose tile size (in inches)"), size_dict.keys())
    st.session_state.tile_size = size_dict[size_option]
    if st.button(translate("Calculate Tiles 📊")):
        total_tiles, total_boxes = calculate_tiles(
            st.session_state.area,
            *st.session_state.tile_size,
            st.session_state.unit
        )
        st.session_state.result = (total_tiles, total_boxes)
        st.session_state.step = 4

# --- Step 4: Result ---
elif st.session_state.step == 4:
    tiles, boxes = st.session_state.result
    st.success(translate(f"✅ You will need approximately {tiles} tiles (~{boxes} boxes)."))
    st.caption(translate("Including 10% buffer for wastage."))

    if st.button(translate("🎨 Show Suggestions")):
        st.info(translate(f"Suggested {st.session_state.tile_type} tiles:"))
        if st.session_state.tile_type == "floor":
            st.write(translate("- Granite Matte Tile – ₹45/sq.ft"))
            st.write(translate("- Anti-skid Ceramic Tile – ₹35/sq.ft"))
        else:
            st.write(translate("- Glossy Wall Tile – ₹30/sq.ft"))
            st.write(translate("- Designer Mosaic Tile – ₹50/sq.ft"))

    st.subheader(translate("Get your estimate via email"))
    email = st.text_input(translate("Enter your email"))
    if st.button(translate("📧 Email me this estimate")):
        if email:
            status = send_estimate_email(email, tiles, boxes)
            if status is True:
                st.success(translate("✅ Estimate emailed successfully!"))
            else:
                st.error(translate(f"❌ Error: {status}"))

    if st.button(translate("🔁 Start Over")):
        for key in st.session_state.keys():
            del st.session_state[key]
