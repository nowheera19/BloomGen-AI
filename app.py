
import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
from io import BytesIO
import tempfile
import os
import time

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="BloomGen AI",
    page_icon="🌸",
    layout="wide"
)

# Your current Google Colab Gradio URL
GRADIO_URL = "https://eecba4f4e25806eef9.gradio.live/"

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f6, #f3e8ff, #fff7ed);
}
.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    color: #a21caf;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #6b456e;
    margin-bottom: 25px;
}
.stButton > button {
    width: 100%;
    background-color: #c026d3;
    color: white;
    border-radius: 12px;
    padding: 12px;
    font-weight: bold;
    border: none;
}
.stButton > button:hover {
    background-color: #a21caf;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="main-title">🌸 BloomGen AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Transform your flower photos into beautiful AI artwork!</div>',
    unsafe_allow_html=True
)

st.info(
    "Upload a flower photo, choose an artistic style, "
    "and let AI transform your image."
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🌷 About BloomGen AI")
    st.write(
        "BloomGen AI uses Stable Diffusion Image-to-Image "
        "to transform an existing flower photo into a new style."
    )

    st.markdown("### Available styles")
    st.write("🌺 Vibrant")
    st.write("🌸 Pastel")
    st.write("🦄 Fantasy")
    st.write("📷 Realistic")

    st.markdown("---")
    st.caption("AI model runs on Google Colab GPU.")

# ---------------- INPUT SECTION ----------------
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📤 Upload Your Flower")

    uploaded_file = st.file_uploader(
        "Choose a flower image",
        type=["jpg", "jpeg", "png", "webp"]
    )

    style = st.selectbox(
        "🎨 Choose your style",
        ["Vibrant", "Pastel", "Fantasy", "Realistic"]
    )

    strength = st.slider(
        "✨ Transformation strength",
        min_value=0.2,
        max_value=0.9,
        value=0.65,
        step=0.05,
        help="Higher strength changes the original image more."
    )

    generate = st.button("🌸 Generate AI Flower")

# ---------------- PREVIEW ----------------
if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGB")
        with right_col:
            st.subheader("🖼️ Original Image")
            st.image(
                original_image,
                caption="Your uploaded flower",
                use_container_width=True
            )
    except Exception:
        st.error("Could not read this image. Please upload another one.")

# ---------------- AI IMAGE GENERATION ----------------
if generate:
    if uploaded_file is None:
        st.warning("Please upload a flower image first.")
    else:
        temporary_path = None

        try:
            with st.spinner(
                "🌷 Connecting to BloomGen AI and generating your image..."
            ):
                # Save uploaded image temporarily
                image_bytes = uploaded_file.getvalue()

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".png"
                ) as temporary_file:
                    temporary_file.write(image_bytes)
                    temporary_path = temporary_file.name

                # Connect to the live Gradio app
                client = Client(GRADIO_URL)

                # Send image, style, and strength to Google Colab
                result = client.predict(
                    handle_file(temporary_path),
                    style,
                    strength,
                    api_name="/transform_flower"
                )

                # Gradio returns an image filepath or URL
                if isinstance(result, str):
                    if result.startswith(("http://", "https://")):
                        import requests
                        response = requests.get(result, timeout=60)
                        response.raise_for_status()
                        generated_image = Image.open(
                            BytesIO(response.content)
                        ).convert("RGB")
                    else:
                        generated_image = Image.open(result).convert("RGB")
                else:
                    generated_image = Image.open(result).convert("RGB")

            st.success("Your AI flower image is ready! 🌸")

            st.subheader("✨ BloomGen AI Result")
            st.image(
                generated_image,
                caption=f"Generated style: {style}",
                use_container_width=True
            )

            # Download generated image
            output_buffer = BytesIO()
            generated_image.save(output_buffer, format="PNG")

            st.download_button(
                label="⬇️ Download Your AI Flower",
                data=output_buffer.getvalue(),
                file_name="bloomgen_ai_flower.png",
                mime="image/png"
            )

        except Exception as error:
            st.error("Could not generate the image.")

            st.warning(
                "Check that your Google Colab notebook is still running "
                "and that the Gradio link is active."
            )

            with st.expander("Technical error details"):
                st.code(str(error))

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<center>Made with 💗 using Python, Streamlit, "
    "Stable Diffusion and Google Colab</center>",
    unsafe_allow_html=True
)
