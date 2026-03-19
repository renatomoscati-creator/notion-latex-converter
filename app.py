# app.py
import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from PIL import Image as PILImage
import io

from converter.llm_client import get_client, convert_text_to_latex, convert_image_to_latex, ConversionError
from converter.image_processor import preprocess_image, encode_image_to_base64
from converter.normalizer import normalize_display_delimiters, _strip_existing_delimiters

load_dotenv()

# ── Paste component (custom, no external package) ─────────────────────────────
_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "components", "paste_image")
_paste_component = components.declare_component("paste_image", path=_COMPONENT_DIR)

def paste_image_zone(key=None):
    """Renders a paste zone and returns base64 image string when an image is pasted."""
    return _paste_component(key=key, default=None)

st.set_page_config(page_title="Notion LaTeX Converter", layout="centered")
st.title("Notion LaTeX Converter")

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("latex_output", ""), ("confidence_score", 1.0), ("is_low_confidence", False),
             ("pasted_b64", None), ("upload_pasted_b64", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Output format toggle ──────────────────────────────────────────────────────
output_mode_label = st.radio(
    "Output format",
    options=["Block  ( $$ ... $$ )", "Inline  ( \\( ... \\) )"],
    horizontal=True,
)
output_mode = "block" if "Block" in output_mode_label else "inline"

# ── Input tabs ────────────────────────────────────────────────────────────────
tab_text, tab_upload, tab_paste = st.tabs(["Text / Formula", "Image Upload", "Paste Image"])

input_image = None
convert_text_btn = False
convert_image_btn = False
convert_paste_btn = False
user_text = ""

with tab_text:
    user_text = st.text_area(
        "Describe or type your math expression:",
        placeholder="e.g. x squared plus y squared equals z squared\nor: integral from 0 to 1 of x squared dx\nor: \\frac{a+b}{c}",
        height=120,
    )
    convert_text_btn = st.button("Convert Text to LaTeX", type="primary")

with tab_upload:
    uploaded_file = st.file_uploader("Upload PNG or JPG", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        img = PILImage.open(uploaded_file)
        st.image(img, caption="Uploaded image", use_container_width=True)
        input_image = img
    convert_image_btn = st.button("Convert Image to LaTeX", type="primary", key="convert_upload")

with tab_paste:
    b64_result = paste_image_zone(key="paste_zone")

    # Store latest paste in session state
    if b64_result and b64_result != st.session_state.pasted_b64:
        st.session_state.pasted_b64 = b64_result

    # Show preview of pasted image
    if st.session_state.pasted_b64:
        try:
            img_bytes = base64.b64decode(st.session_state.pasted_b64)
            pasted_img = PILImage.open(io.BytesIO(img_bytes))
            input_image = pasted_img
        except Exception:
            st.error("Could not decode pasted image.")

    convert_paste_btn = st.button("Convert Pasted Image to LaTeX", type="primary", key="convert_paste")


# ── Conversion helpers ────────────────────────────────────────────────────────
def run_text_conversion():
    if not user_text.strip():
        st.warning("Please enter some text first.")
        return
    try:
        client = get_client()
        with st.spinner("Converting..."):
            result = convert_text_to_latex(client, user_text, output_mode)
        st.session_state.latex_output = result["latex"]
        st.session_state.confidence_score = result["confidence"]
        st.session_state.is_low_confidence = result["confidence"] < 0.6
    except ConversionError as e:
        st.error(f"Conversion failed: {e}")
    except EnvironmentError as e:
        st.error(str(e))


def run_image_conversion(image):
    if image is None:
        st.warning("Please provide an image first.")
        return
    try:
        client = get_client()
        with st.spinner("Analyzing image..."):
            processed = preprocess_image(image)
            b64, media_type = encode_image_to_base64(processed)
            result = convert_image_to_latex(client, b64, media_type, output_mode)
        st.session_state.latex_output = result["latex"]
        st.session_state.confidence_score = result["confidence"]
        st.session_state.is_low_confidence = result["confidence"] < 0.6
    except ConversionError as e:
        st.error(f"Conversion failed: {e}")
    except EnvironmentError as e:
        st.error(str(e))


if convert_text_btn:
    run_text_conversion()
if convert_image_btn:
    run_image_conversion(input_image)
if convert_paste_btn:
    if st.session_state.pasted_b64:
        try:
            img_bytes = base64.b64decode(st.session_state.pasted_b64)
            pasted_img = PILImage.open(io.BytesIO(img_bytes))
            run_image_conversion(pasted_img)
        except Exception as e:
            st.error(f"Could not process pasted image: {e}")
    else:
        st.warning("Paste an image first.")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.latex_output:
    st.divider()
    st.subheader("Result")

    if st.session_state.is_low_confidence:
        st.warning("⚠️ Low confidence — the result may be inaccurate. Review and edit before using.")

    inner = _strip_existing_delimiters(st.session_state.latex_output)
    wrapped = normalize_display_delimiters(inner, output_mode)
    st.session_state.latex_output = wrapped

    st.markdown("**Preview:**")
    try:
        st.latex(inner)
    except Exception:
        st.info("Preview unavailable for this expression.")

    st.markdown("**LaTeX output** (click copy icon to copy):")
    st.code(wrapped, language=None)

    edited = st.text_area("Edit if needed:", value=wrapped, height=100, key="edit_area")
    if st.button("Re-render Preview"):
        inner_edited = _strip_existing_delimiters(edited)
        try:
            st.latex(inner_edited)
        except Exception:
            st.info("Preview unavailable for this expression.")
        st.code(edited, language=None)

    st.markdown(f"**Confidence:** {int(st.session_state.confidence_score * 100)}%")
    st.progress(st.session_state.confidence_score)
