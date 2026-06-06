"""
app.py
------
A simple Streamlit web UI for the Copywriting & Ads Agent.

The user enters an advertising brief (product, audience, platform, key points,
optional brand tone). On submit, the app:
  1. Generates persuasive, platform-specific ad copy (Headline, Body, CTA)
     using Google Gemini through the Microsoft Agent Framework.
  2. Generates a matching advertising graphic/image with Gemini's image model.

Both the copy and the image are shown back in the browser.

Run it from the terminal:
    streamlit run app.py
"""

import asyncio
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Reuse the agent + image logic so we have a single source of truth.
from copywriting_ads_agent import generate_ad_copy
from image_generator import generate_ad_image

# Folder that contains this script, used to locate the local `.env` file.
BASE_DIR = Path(__file__).parent

# Load the GEMINI_API_KEY (same key as Assignment 1) from the `.env` file that
# lives next to this script, so the key is available no matter where Streamlit
# is launched from.
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Copywriting & Ads Agent",
    page_icon="📣",
    layout="centered",
)

st.title("📣 Copywriting & Ads Agent")
st.caption(
    "Powered by Google Gemini and the Microsoft Agent Framework. "
    "Describe your product and the agent writes the ad copy and generates "
    "a matching graphic."
)


# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
# Using a form means the agent only runs when the user clicks the button
# (not on every keystroke).
with st.form("ad_form"):
    product = st.text_input(
        "Product / Service",
        placeholder="e.g. EcoSip reusable water bottle",
    )
    audience = st.text_input(
        "Target Audience",
        placeholder="e.g. health-conscious young professionals",
    )
    platform = st.selectbox(
        "Advertising Platform",
        ["Facebook", "Google", "LinkedIn"],
    )
    key_points = st.text_area(
        "Key Points / Benefits (optional)",
        placeholder="e.g. keeps drinks cold for 24h, plastic-free, lightweight",
    )
    brand_tone = st.text_input(
        "Brand Tone / Voice (optional)",
        placeholder="e.g. playful, premium, professional",
    )
    make_image = st.checkbox("Also generate an ad graphic/image", value=True)
    submitted = st.form_submit_button("Generate Ad")


# ---------------------------------------------------------------------------
# Handle submission
# ---------------------------------------------------------------------------
if submitted:
    if not product.strip() or not audience.strip():
        # Guard against missing required inputs.
        st.warning("Please provide at least a product and a target audience.")
    else:
        # 1) Generate the ad copy.
        with st.spinner("Writing ad copy, please wait..."):
            try:
                copy = asyncio.run(
                    generate_ad_copy(
                        product.strip(),
                        audience.strip(),
                        platform,
                        key_points.strip(),
                        brand_tone.strip(),
                    )
                )
                st.subheader("Ad Copy")
                # Render as Markdown so headings/labels display nicely.
                st.markdown(copy)
            except Exception as error:
                st.error(f"Could not generate ad copy: {error}")

        # 2) Generate the matching graphic (optional).
        if make_image:
            with st.spinner("Generating ad graphic, please wait..."):
                try:
                    # `generate_ad_image` returns (image_bytes, engine_label).
                    image_bytes, engine = generate_ad_image(
                        product.strip(),
                        audience.strip(),
                        platform,
                        key_points.strip(),
                    )
                    st.subheader("Ad Graphic")
                    st.caption(f"Image engine: {engine}")
                    st.image(image_bytes, caption=f"Ad image for {product}")
                    # Let the user download the generated image.
                    st.download_button(
                        "Download image",
                        data=image_bytes,
                        file_name="ad_image.png",
                        mime="image/png",
                    )
                except Exception as error:
                    st.error(f"Could not generate the ad graphic: {error}")
