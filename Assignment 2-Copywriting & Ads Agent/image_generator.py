"""
image_generator.py
------------------
Generates an advertising graphic/image for the ad (as per the topic).

Image generation strategy
-------------------------
1. **Primary: Google Gemini image model** - uses the *same* GEMINI_API_KEY as
   the text agent / Assignment 1. This is the preferred (AI photo) engine, but
   Gemini's image models are NOT available on the free tier (they return HTTP
   429 with `limit: 0` unless billing is enabled on the Google project).
2. **Fallback: local Pillow ad creative** - if Gemini image generation is
   unavailable, we compose a clean, topic-specific ad poster locally with
   Pillow (product headline, key benefit, platform badge, CTA). This needs no
   API key or network, so the demo ALWAYS produces a graphic for the ad.

The text ad copy itself is still produced on Gemini with the exact same LLM
config as Assignment 1 (see `copywriting_ads_agent.py`).

`generate_ad_image()` returns a tuple of (png_bytes, engine_label) and also
saves a copy of the image to the `generated_images/` folder.
"""

import hashlib
import io
import os
import textwrap
from pathlib import Path

# Google's native GenAI SDK, used for the primary (Gemini) image attempt.
from google import genai
from google.genai import types

# Pillow, used for the always-available local ad-creative fallback.
from PIL import Image, ImageDraw, ImageFont


# Preferred Gemini image-generation model (used when the key has image quota).
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

# Folder that contains this script, used to save generated images.
BASE_DIR = Path(__file__).parent

# Where generated ad images are written to.
OUTPUT_DIR = BASE_DIR / "generated_images"


def build_image_prompt(
    product: str,
    audience: str,
    platform: str,
    key_points: str = "",
) -> str:
    """
    Turn the advertising brief into a clear, visual prompt for the image model.
    We describe a clean, professional advertising graphic with no real text
    baked in (text/logos in AI images often look garbled), so the generated
    copy stays the source of truth for words.
    """
    prompt = (
        f"Create a high-quality, professional advertising graphic for: {product}. "
        f"The ad targets {audience} and will run on {platform}. "
    )
    if key_points.strip():
        prompt += f"Visually highlight these benefits: {key_points}. "
    prompt += (
        "Use modern, eye-catching, brand-friendly visuals with vibrant colors "
        "and clean composition suitable for a marketing campaign. "
        "Avoid heavy or garbled on-image text; focus on imagery and mood."
    )
    return prompt


def _generate_via_gemini(prompt: str) -> bytes:
    """
    Try to generate an image with Gemini using the same GEMINI_API_KEY.
    Raises on any error (e.g. free-tier quota of 0), so the caller can fall back.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    # Create a GenAI client authenticated with the same Gemini key.
    client = genai.Client(api_key=api_key)

    # Gemini image models require both TEXT and IMAGE response modalities.
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    # Walk the response parts and pull out the first inline image payload.
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return part.inline_data.data

    raise RuntimeError("Gemini did not return an image.")


def _load_font(size: int, bold: bool = False):
    """Load a TrueType font, falling back to Pillow's default if unavailable."""
    candidates = (
        ["arialbd.ttf", "Arial_Bold.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _brand_colors(seed: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Derive a deterministic two-color gradient from the product name."""
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    hue = int(digest[:2], 16)  # 0-255, used to vary the palette per product
    top = ((hue + 30) % 256, (hue * 3) % 200 + 30, 200)
    bottom = ((hue + 90) % 256, (hue * 5) % 150 + 40, 120)
    return top, bottom


def _generate_via_pillow(
    product: str,
    audience: str,
    platform: str,
    key_points: str = "",
) -> bytes:
    """
    Compose a clean, topic-specific advertising poster locally with Pillow.
    Always works offline (no API key, no network) so the demo never fails.
    """
    width, height = 1024, 1024
    top_color, bottom_color = _brand_colors(product)

    image = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(image)

    # Vertical gradient background.
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Platform badge (top-left pill).
    badge_font = _load_font(34, bold=True)
    badge_text = platform.upper()
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle(
        [60, 60, 60 + bw + 60, 60 + bh + 36], radius=24, fill=(255, 255, 255)
    )
    draw.text((90, 78), badge_text, font=badge_font, fill=bottom_color)

    # Headline = product name, wrapped and centered.
    headline_font = _load_font(78, bold=True)
    wrapped = textwrap.fill(product, width=18)
    draw.multiline_text(
        (width // 2, 400),
        wrapped,
        font=headline_font,
        fill=(255, 255, 255),
        anchor="mm",
        align="center",
        spacing=12,
    )

    # Sub-headline = first key benefit (if provided).
    if key_points.strip():
        sub = key_points.split(",")[0].strip().capitalize()
        sub_font = _load_font(40)
        draw.multiline_text(
            (width // 2, 600),
            textwrap.fill(sub, width=30),
            font=sub_font,
            fill=(245, 245, 245),
            anchor="mm",
            align="center",
            spacing=8,
        )

    # Call-to-action pill near the bottom.
    cta_font = _load_font(44, bold=True)
    cta_text = "Learn More"
    cbbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cw, ch = cbbox[2] - cbbox[0], cbbox[3] - cbbox[1]
    cx0 = (width - (cw + 100)) // 2
    draw.rounded_rectangle(
        [cx0, 820, cx0 + cw + 100, 820 + ch + 50], radius=40, fill=(255, 255, 255)
    )
    draw.text(
        (width // 2, 820 + (ch + 50) // 2),
        cta_text,
        font=cta_font,
        fill=bottom_color,
        anchor="mm",
    )

    # Encode to PNG bytes.
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_ad_image(
    product: str,
    audience: str,
    platform: str,
    key_points: str = "",
) -> tuple[bytes, str]:
    """
    Generate an advertising image for the given brief.

    Returns a tuple of (image_bytes, engine_label) where engine_label is either
    "Gemini (AI image)" or "Local Pillow ad creative". The image is also saved
    into the `generated_images/` folder for convenience.
    """
    prompt = build_image_prompt(product, audience, platform, key_points)

    # 1) Try Gemini first (same key as Assignment 1).
    try:
        image_bytes = _generate_via_gemini(prompt)
        engine = "Gemini (AI image)"
    except Exception as gemini_error:
        # 2) Gemini image gen unavailable (e.g. free-tier quota of 0) -> fall back
        #    to a locally composed ad creative that always works.
        print(f"Gemini image generation unavailable, using local fallback: {gemini_error}")
        image_bytes = _generate_via_pillow(product, audience, platform, key_points)
        engine = "Local Pillow ad creative"

    # Save a copy to disk so the user keeps the asset.
    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in product)[:40] or "ad"
    output_path = OUTPUT_DIR / f"{safe_name}.png"
    output_path.write_bytes(image_bytes)

    return image_bytes, engine


if __name__ == "__main__":
    # Simple manual test: generate one image from a sample brief.
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
    data, used_engine = generate_ad_image(
        product="EcoSip reusable water bottle",
        audience="health-conscious young professionals",
        platform="Facebook",
        key_points="keeps drinks cold for 24 hours, plastic-free, lightweight",
    )
    print(f"Generated image: {len(data)} bytes via {used_engine}, saved to {OUTPUT_DIR}")
