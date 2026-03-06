"""
NOiSEMaKER Asset Pipeline
==========================

Orchestrates artwork analysis and background generation for the content pipeline.
Implements Spec Sections 3.1 (Asset Fetch & Color Analysis) and 3.2 (Background
Expansion).

Step 1: Vision-based color/mood analysis of album artwork
    - Routes to vision model via model_router
    - Falls back to PIL ColorAnalyzer when vision model is PLACEHOLDER

Step 2: Background expansion with mood-injected prompts
    - Injects plain-speech mood analysis + strict negative prompts
    - Routes to image generator via model_router (currently FLUX.1-schnell)

Both steps produce inputs consumed by the template engine for final compositing.
"""

import logging
import os
from io import BytesIO
from typing import Optional

import boto3
from PIL import Image

from content.image_processor import ColorAnalyzer
from content.model_router import call_vision_model, call_image_generator

logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")

s3_client = boto3.client("s3", region_name=AWS_REGION)

# Reuse the global ColorAnalyzer instance from image_processor
_color_analyzer = ColorAnalyzer()

# Art style + artist rotation lists (from content_generator.py)
ART_STYLES = [
    "Abstract geometric",
    "Cubism",
    "Surrealism",
    "Art Deco",
    "Minimalist",
    "Abstract Expressionism",
    "Vaporwave",
]

ARTIST_STYLES = [
    "Jean-Michel Basquiat",
    "Georges Braque",
    "Mark Rothko",
    "Ernst Ludwig Kirchner",
    "Malgorzata Kmiec",
    "Pascal Blanche",
    "Kazimir Malevich",
    "Yayoi Kusama",
    "Willem de Kooning",
    "Finn Campbell-Norman",
    "Elena Kotliarker",
]

# Negative prompt applied to ALL background generations (Spec Section 3.2)
NEGATIVE_PROMPT_SUFFIX = "no human figures, no text, no morphing, no album art"


# =============================================================================
# PUBLIC API
# =============================================================================

def analyze_artwork(song_data: dict) -> dict:
    """Analyze album artwork for color palette and mood.

    Tries the vision model first (via model_router). If PLACEHOLDER or fails,
    falls back to PIL ColorAnalyzer and formats the output as prose.

    Args:
        song_data: Dict with cached_artwork_s3_key (and optionally color_palette)

    Returns:
        Dict with keys:
            mood_description: str — plain-speech mood/color description
            color_palette_hex: list[str] — hex color strings
            brightness: float — 0.0 (dark) to 1.0 (light)
            temperature: str — "warm", "cool", or "neutral"
    """
    s3_key = song_data.get("cached_artwork_s3_key")
    if not s3_key:
        logger.warning("No cached_artwork_s3_key — using default analysis")
        return _default_analysis()

    # Download artwork from S3
    image_bytes = _download_from_s3(s3_key)
    if not image_bytes:
        return _default_analysis()

    # Try vision model for rich mood description
    vision_result = call_vision_model(
        image_bytes,
        "Describe the color palette and emotional mood of this album artwork "
        "in plain speech. No hex codes. Focus on the dominant colors, overall "
        "atmosphere, and emotional tone the artwork conveys.",
    )

    if vision_result:
        # Vision model returned a real analysis — also get hex colors from PIL
        pil_analysis = _analyze_with_pil(image_bytes)
        return {
            "mood_description": vision_result,
            "color_palette_hex": pil_analysis["color_palette_hex"],
            "brightness": pil_analysis["brightness"],
            "temperature": pil_analysis["temperature"],
        }

    # Fallback: PIL-only analysis formatted as prose
    return _analyze_with_pil(image_bytes)


def generate_background(
    mood_analysis: dict,
    platform: str,
    platform_size: tuple[int, int],
    content_id_int: int,
) -> Optional[Image.Image]:
    """Generate an AI background image enriched with mood analysis.

    Builds a prompt from the mood description + art style rotation + negative
    prompts, then routes to the image generator via model_router.

    Args:
        mood_analysis: Dict from analyze_artwork() with mood_description, color_palette_hex
        platform: Target platform name (for logging)
        platform_size: (width, height) tuple for the target platform
        content_id_int: Integer derived from content UUID for deterministic style rotation

    Returns:
        PIL Image or None on failure
    """
    width, height = platform_size

    # Deterministic art style + artist selection (same logic as content_generator)
    art_style = ART_STYLES[content_id_int % len(ART_STYLES)]
    artist = ARTIST_STYLES[content_id_int % len(ARTIST_STYLES)]

    # Build prompt with mood injection
    mood_desc = mood_analysis.get("mood_description", "")
    color_hex = mood_analysis.get("color_palette_hex", [])
    color_str = ", ".join(color_hex) if color_hex else "vibrant colors"

    if mood_desc and mood_desc != _DEFAULT_MOOD:
        # Rich mood description available (from vision model or formatted PIL)
        prompt = (
            f"create a {art_style} background graphic "
            f"in the style of {artist}, "
            f"inspired by this mood: {mood_desc}, "
            f"using colors: {color_str}, "
            f"{NEGATIVE_PROMPT_SUFFIX}"
        )
    else:
        # Minimal fallback prompt (matches original content_generator behavior)
        prompt = (
            f"create a {art_style} background graphic "
            f"in the style of {artist} using {color_str}"
        )

    logger.info(f"[asset_pipeline] Generating {platform} background ({width}x{height})")
    return call_image_generator(prompt, width, height)


def download_artwork_from_s3(s3_key: str) -> Optional[Image.Image]:
    """Download cached song artwork from S3 as a PIL Image.

    Public wrapper used by the content generator for compositing.
    """
    image_bytes = _download_from_s3(s3_key)
    if not image_bytes:
        return None
    try:
        return Image.open(BytesIO(image_bytes)).convert("RGBA")
    except Exception as e:
        logger.error(f"Failed to open artwork image: {e}")
        return None


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

_DEFAULT_MOOD = "Neutral tones with a balanced atmosphere"


def _download_from_s3(s3_key: str) -> Optional[bytes]:
    """Download a file from S3 and return raw bytes."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return response["Body"].read()
    except Exception as e:
        logger.error(f"Failed to download from S3 ({s3_key}): {e}")
        return None


def _analyze_with_pil(image_bytes: bytes) -> dict:
    """Run PIL ColorAnalyzer on image bytes and format as structured result.

    Converts the hex-based analysis into a plain-speech mood description
    so downstream prompt building has consistent input regardless of source.
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Save to temp path for ColorAnalyzer (it expects path or URL)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            image.save(tmp, format="JPEG")
            tmp_path = tmp.name

        analysis = _color_analyzer.analyze_album_art(tmp_path)

        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        # Extract structured data
        hex_colors = analysis.get("dominant_colors", ["#808080"])
        brightness = analysis.get("brightness", 0.5)
        temperature = analysis.get("color_temperature", "neutral")
        primary = analysis.get("primary_color", "#808080")

        # Format as plain-speech mood description
        brightness_word = "dark" if brightness < 0.4 else "bright" if brightness > 0.7 else "medium"
        mood_description = (
            f"A {brightness_word}, {temperature}-toned composition "
            f"dominated by {primary} with accents of "
            f"{', '.join(hex_colors[1:3]) if len(hex_colors) > 1 else 'subtle variation'}"
        )

        return {
            "mood_description": mood_description,
            "color_palette_hex": hex_colors[:5],
            "brightness": brightness,
            "temperature": temperature,
        }

    except Exception as e:
        logger.error(f"PIL color analysis failed: {e}")
        return _default_analysis()


def _default_analysis() -> dict:
    """Return safe defaults when artwork analysis fails entirely."""
    return {
        "mood_description": _DEFAULT_MOOD,
        "color_palette_hex": ["#808080", "#404040", "#c0c0c0"],
        "brightness": 0.5,
        "temperature": "neutral",
    }
