# Save as: image_resizer_web.py
import streamlit as st
from PIL import Image, ImageEnhance
import io
import zipfile

st.set_page_config(page_title="3 PNG Resizer",
    page_icon="🖼️",
    layout="wide")

st.title("Resize One Image → Three PNG Sizes (20 / 200 / 2048 px)")

uploaded_file = st.file_uploader("Upload an image (or drag & drop)", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file)
    st.image(image, caption="Original image", use_column_width=True)

    # Controls
    col1, col2, col3 = st.columns(3)
    sharpen = col1.slider("Sharpening strength (0 = none, 3 = strong)", 0.0, 3.0, 1.2, 0.1)

    st.subheader("Crop (pixels after resize) — leave 0 for no crop")
    crop_col1, crop_col2, crop_col3, crop_col4 = st.columns(4)
    crop_left   = crop_col1.number_input("Left",   value=0, min_value=0)
    crop_top    = crop_col2.number_input("Top",    value=0, min_value=0)
    crop_width  = crop_col3.number_input("Width",  value=0, min_value=0)
    crop_height = crop_col4.number_input("Height", value=0, min_value=0)

    rotation_options = ["None", "90° clockwise", "180°", "270° clockwise", "Flip horizontal", "Flip vertical"]
    rotation = st.selectbox("Rotate / Flip", rotation_options)

    if st.button("Generate 3 PNGs", type="primary"):
        with st.spinner("Processing..."):
            outputs = []
            for width in [20, 200, 2048]:
                # Resize
                h = int(image.height * width / image.width)
                resized = image.resize((width, h), Image.LANCZOS)

                # Sharpen
                if sharpen > 0:
                    resized = ImageEnhance.Sharpness(resized).enhance(1 + sharpen)

                # Crop
                if crop_width > 0 and crop_height > 0:
                    resized = resized.crop((crop_left, crop_top, crop_left + crop_width, crop_top + crop_height))

                # Rotate
                if rotation == "90° clockwise":
                    resized = resized.transpose(Image.ROTATE_90)
                elif rotation == "180°":
                    resized = resized.transpose(Image.ROTATE_180)
                elif rotation == "270° clockwise":
                    resized = resized.transpose(Image.ROTATE_270)
                elif rotation == "Flip horizontal":
                    resized = resized.transpose(Image.FLIP_LEFT_RIGHT)
                elif rotation == "Flip vertical":
                    resized = resized.transpose(Image.FLIP_TOP_BOTTOM)

                # Save to bytes
                buf = io.BytesIO()
                resized.save(buf, format="PNG")
                buf.seek(0)
                outputs.append((f"{width}px.png", buf.getvalue()))

            # Create ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, data in outputs:
                    zip_file.writestr(filename, data)

            zip_buffer.seek(0)

            st.success("Done! Download your 3 PNGs below.")
            st.download_button(
                label="Download all 3 PNGs (ZIP)",
                data=zip_buffer,
                file_name="3_resized_images.zip",
                mime="application/zip"
            )

            # Optional: show previews
            st.subheader("Previews")
            cols = st.columns(3)
            for i, (name, buf) in enumerate(outputs):
                img = Image.open(io.BytesIO(buf))

                cols[i].image(img, caption=name, use_column_width=True)
