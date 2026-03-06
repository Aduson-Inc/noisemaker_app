"""
NOiSEMaKER Template Engine
============================

Programmatic rendering engine + dynamic template ingestion system.
Implements Spec Sections 4 (Rendering Engine) and 5 (Template Ingestion).

Components:
    1. Template JSON Preset format — structured layer definitions
    2. Template storage — DynamoDB (noisemaker-templates) + S3
    3. Template ingestion — Vision LLM analyzes uploaded designs (PLACEHOLDER)
    4. Static renderer — PIL-based compositing for image platforms
    5. Video renderer — FFmpeg-based layering for TikTok/YouTube/Reels

Font resolution order:
    1. S3: templates/fonts/{family}.otf
    2. Local: frontend/public/fonts/{family}.otf
    3. System: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf (Lambda)
    4. PIL default font (ultimate fallback)
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

import boto3
from PIL import Image, ImageDraw, ImageFont

from content.model_router import call_template_analyzer

logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")

_s3_client = None
_dynamodb = None


def _get_s3():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name=AWS_REGION)
    return _s3_client


def _get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return _dynamodb


# =============================================================================
# DEFAULT TEMPLATE PRESETS
# =============================================================================

# These match the existing content_generator.py compositing layout.
# Used when no custom templates exist or vision analyzer is PLACEHOLDER.

DEFAULT_PRESETS = {
    "square_1080": {
        "template_id": "default-square-1080",
        "name": "Default Square",
        "canvas": {"width": 1080, "height": 1080},
        "platform": "all",
        "aspect_ratio": "1:1",
        "layers": [
            {
                "type": "background",
                "source": "generated",
                "animation": {"type": "pan_zoom", "duration_sec": 10, "easing": "ease-in-out"},
            },
            {
                "type": "album_art",
                "position": {"x": 216, "y": 216},
                "size": {"width": 648, "height": 648},
                "border_radius": 0,
            },
            {
                "type": "text",
                "field": "song_title",
                "position": {"x": 540, "y": 900},
                "font": {"family": "DejaVuSans-Bold", "size": 43, "weight": "bold", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 2},
            },
            {
                "type": "text",
                "field": "artist_name",
                "position": {"x": 540, "y": 954},
                "font": {"family": "DejaVuSans", "size": 32, "weight": "regular", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 1},
            },
        ],
    },
    "landscape_1200x675": {
        "template_id": "default-landscape-1200x675",
        "name": "Default Landscape (Twitter/Discord)",
        "canvas": {"width": 1200, "height": 675},
        "platform": "all",
        "aspect_ratio": "16:9",
        "layers": [
            {
                "type": "background",
                "source": "generated",
                "animation": {"type": "pan_zoom", "duration_sec": 10, "easing": "ease-in-out"},
            },
            {
                "type": "album_art",
                "position": {"x": 398, "y": 35},
                "size": {"width": 405, "height": 405},
                "border_radius": 0,
            },
            {
                "type": "text",
                "field": "song_title",
                "position": {"x": 600, "y": 480},
                "font": {"family": "DejaVuSans-Bold", "size": 27, "weight": "bold", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 2},
            },
            {
                "type": "text",
                "field": "artist_name",
                "position": {"x": 600, "y": 520},
                "font": {"family": "DejaVuSans", "size": 20, "weight": "regular", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 1},
            },
        ],
    },
    "landscape_1200x630": {
        "template_id": "default-landscape-1200x630",
        "name": "Default Landscape (Facebook/Reddit)",
        "canvas": {"width": 1200, "height": 630},
        "platform": "all",
        "aspect_ratio": "1.9:1",
        "layers": [
            {
                "type": "background",
                "source": "generated",
                "animation": {"type": "pan_zoom", "duration_sec": 10, "easing": "ease-in-out"},
            },
            {
                "type": "album_art",
                "position": {"x": 402, "y": 18},
                "size": {"width": 378, "height": 378},
                "border_radius": 0,
            },
            {
                "type": "text",
                "field": "song_title",
                "position": {"x": 600, "y": 430},
                "font": {"family": "DejaVuSans-Bold", "size": 25, "weight": "bold", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 2},
            },
            {
                "type": "text",
                "field": "artist_name",
                "position": {"x": 600, "y": 468},
                "font": {"family": "DejaVuSans", "size": 19, "weight": "regular", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 1},
            },
        ],
    },
    "portrait_1080x1920": {
        "template_id": "default-portrait-1080x1920",
        "name": "Default Portrait (TikTok/YouTube Shorts/Reels)",
        "canvas": {"width": 1080, "height": 1920},
        "platform": "all",
        "aspect_ratio": "9:16",
        "layers": [
            {
                "type": "background",
                "source": "generated",
                "animation": {"type": "pan_zoom", "duration_sec": 10, "easing": "ease-in-out"},
            },
            {
                "type": "album_art",
                "position": {"x": 190, "y": 460},
                "size": {"width": 700, "height": 700},
                "border_radius": 12,
            },
            {
                "type": "text",
                "field": "song_title",
                "position": {"x": 540, "y": 1220},
                "font": {"family": "DejaVuSans-Bold", "size": 48, "weight": "bold", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 2},
            },
            {
                "type": "text",
                "field": "artist_name",
                "position": {"x": 540, "y": 1290},
                "font": {"family": "DejaVuSans", "size": 36, "weight": "regular", "color": "#FFFFFF"},
                "alignment": "center",
                "stroke": {"color": "#000000", "width": 1},
            },
        ],
    },
}

# Maps platform sizes to default preset keys
SIZE_TO_PRESET = {
    (1080, 1080): "square_1080",
    (1200, 675): "landscape_1200x675",
    (1200, 630): "landscape_1200x630",
    (1080, 1920): "portrait_1080x1920",
}


# =============================================================================
# TEMPLATE SELECTION
# =============================================================================

def select_template(
    platform: str, canvas_size: tuple[int, int]
) -> dict:
    """Select a template for the given platform and canvas size.

    First checks DynamoDB for custom active templates matching the platform.
    Falls back to default presets if none found or table doesn't exist.

    Args:
        platform: Target platform name
        canvas_size: (width, height) tuple

    Returns:
        Template JSON preset dict
    """
    # Try custom templates from DynamoDB
    custom = _fetch_custom_template(platform, canvas_size)
    if custom:
        return custom

    # Fall back to default presets based on canvas size
    preset_key = SIZE_TO_PRESET.get(canvas_size, "square_1080")
    logger.info(f"Using default preset: {preset_key} for {platform}")
    return DEFAULT_PRESETS[preset_key]


def _fetch_custom_template(
    platform: str, canvas_size: tuple[int, int]
) -> Optional[dict]:
    """Fetch an active custom template from noisemaker-templates table."""
    try:
        table = _get_dynamodb().Table("noisemaker-templates")
        # Scan for active templates matching platform (or "all")
        response = table.scan(
            FilterExpression=(
                boto3.dynamodb.conditions.Attr("is_active").eq(True)
                & (
                    boto3.dynamodb.conditions.Attr("platform").eq(platform)
                    | boto3.dynamodb.conditions.Attr("platform").eq("all")
                )
            ),
            Limit=10,
        )
        items = response.get("Items", [])
        if not items:
            return None

        # Find one matching canvas size
        w, h = canvas_size
        for item in items:
            layout = json.loads(item.get("layout_json", "{}"))
            canvas = layout.get("canvas", {})
            if canvas.get("width") == w and canvas.get("height") == h:
                logger.info(f"Using custom template: {item.get('name', item['template_id'])}")
                return layout

        return None

    except Exception as e:
        # Table might not exist yet — that's fine
        logger.debug(f"Custom template fetch failed (non-critical): {e}")
        return None


# =============================================================================
# TEMPLATE INGESTION
# =============================================================================

def ingest_template(
    image_bytes: bytes, name: str, platform: str, aspect_ratio: str = "1:1"
) -> dict:
    """Ingest a new template by analyzing it with a vision model.

    Uploads the master image to S3, calls the template analyzer to extract
    bounding box coordinates, and saves the resulting JSON preset to DynamoDB.

    If template_analyzer is PLACEHOLDER, uses the closest default preset.

    Args:
        image_bytes: Raw PNG/SVG bytes of the master design
        name: Human-readable template name
        platform: Target platform or "all"
        aspect_ratio: Canvas aspect ratio string (e.g., "1:1", "9:16")

    Returns:
        Dict with template_id and status
    """
    template_id = str(uuid.uuid4())

    # Upload master image to S3
    master_key = f"templates/{template_id}_master.png"
    try:
        _get_s3().put_object(
            Bucket=S3_BUCKET,
            Key=master_key,
            Body=image_bytes,
            ContentType="image/png",
        )
    except Exception as e:
        logger.error(f"Failed to upload master template to S3: {e}")
        return {"template_id": template_id, "status": "error", "error": str(e)}

    # Try vision model for bounding box extraction
    analysis_prompt = (
        "Analyze this design template. Identify the bounding box coordinates for: "
        "album artwork area, song title text, artist name text. "
        "Return as JSON with x, y, width, height for each element, "
        "plus font sizes and alignment. Use pixel coordinates."
    )
    vision_result = call_template_analyzer(image_bytes, analysis_prompt)

    if vision_result:
        # Parse vision model output into template JSON
        try:
            layout_json = _parse_vision_to_layout(vision_result, template_id)
        except Exception as e:
            logger.warning(f"Failed to parse vision analysis, using default: {e}")
            layout_json = _default_layout_for_ratio(aspect_ratio, template_id)
    else:
        # PLACEHOLDER — use default layout matching aspect ratio
        layout_json = _default_layout_for_ratio(aspect_ratio, template_id)

    # Save to DynamoDB
    try:
        table = _get_dynamodb().Table("noisemaker-templates")
        table.put_item(Item={
            "template_id": template_id,
            "name": name,
            "layout_json": json.dumps(layout_json),
            "platform": platform,
            "aspect_ratio": aspect_ratio,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "preview_s3_key": "",
            "master_s3_key": master_key,
        })
        logger.info(f"Template ingested: {template_id} ({name})")
        return {"template_id": template_id, "status": "created"}
    except Exception as e:
        logger.error(f"Failed to save template to DynamoDB: {e}")
        return {"template_id": template_id, "status": "error", "error": str(e)}


def _default_layout_for_ratio(aspect_ratio: str, template_id: str) -> dict:
    """Return a default layout matching the given aspect ratio."""
    ratio_map = {
        "1:1": "square_1080",
        "16:9": "landscape_1200x675",
        "1.9:1": "landscape_1200x630",
        "9:16": "portrait_1080x1920",
    }
    preset_key = ratio_map.get(aspect_ratio, "square_1080")
    layout = dict(DEFAULT_PRESETS[preset_key])
    layout["template_id"] = template_id
    return layout


def _parse_vision_to_layout(vision_json_str: str, template_id: str) -> dict:
    """Parse vision model JSON output into template layout format.

    This will be fleshed out when a real vision model is connected.
    For now, it attempts to parse the JSON and map to our layer format.
    """
    parsed = json.loads(vision_json_str)
    # Future: map parsed bounding boxes to our layer format
    # For now, return the parsed data as-is with template_id
    parsed["template_id"] = template_id
    return parsed


# =============================================================================
# STATIC RENDERER (PIL)
# =============================================================================

def render_static(template_json: dict, assets: dict) -> Optional[bytes]:
    """Render a static promotional image from template + assets.

    Composites layers in order: background → album art → text overlays.

    Args:
        template_json: Template JSON preset dict with canvas and layers
        assets: Dict with keys:
            background: PIL Image (generated background)
            artwork: PIL Image (album art, RGBA)
            song_title: str
            artist_name: str

    Returns:
        JPEG bytes of the final composited image, or None on failure
    """
    try:
        canvas_cfg = template_json.get("canvas", {"width": 1080, "height": 1080})
        width = canvas_cfg["width"]
        height = canvas_cfg["height"]

        # Start with background
        background = assets.get("background")
        if background is None:
            logger.error("No background image provided")
            return None

        canvas = background.convert("RGBA")
        if canvas.size != (width, height):
            canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)

        # Process layers in order
        for layer in template_json.get("layers", []):
            layer_type = layer.get("type")

            if layer_type == "background":
                continue  # Already applied

            elif layer_type == "album_art":
                canvas = _apply_album_art_layer(canvas, layer, assets)

            elif layer_type == "text":
                canvas = _apply_text_layer(canvas, layer, assets)

        # Convert to RGB and return as JPEG bytes
        final = canvas.convert("RGB")
        buffer = BytesIO()
        final.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Static render failed: {e}")
        return None


def _apply_album_art_layer(
    canvas: Image.Image, layer: dict, assets: dict
) -> Image.Image:
    """Paste album art onto canvas at template-specified position/size."""
    artwork = assets.get("artwork")
    if artwork is None:
        return canvas

    pos = layer.get("position", {"x": 0, "y": 0})
    size = layer.get("size", {"width": 648, "height": 648})

    art_resized = artwork.resize(
        (size["width"], size["height"]), Image.Resampling.LANCZOS
    )

    # Apply border radius if specified
    border_radius = layer.get("border_radius", 0)
    if border_radius > 0:
        art_resized = _apply_rounded_corners(art_resized, border_radius)

    canvas.paste(art_resized, (pos["x"], pos["y"]), art_resized)
    return canvas


def _apply_text_layer(
    canvas: Image.Image, layer: dict, assets: dict
) -> Image.Image:
    """Draw text onto canvas at template-specified position with font config."""
    field = layer.get("field", "")
    text = assets.get(field, "")
    if not text:
        return canvas

    pos = layer.get("position", {"x": 0, "y": 0})
    font_cfg = layer.get("font", {})
    alignment = layer.get("alignment", "center")
    stroke_cfg = layer.get("stroke", {})

    font = _resolve_font(
        font_cfg.get("family", ""),
        font_cfg.get("size", 32),
        font_cfg.get("weight", "regular"),
    )

    draw = ImageDraw.Draw(canvas)

    # Calculate x position based on alignment
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]

    if alignment == "center":
        x = pos["x"] - text_w // 2
    elif alignment == "right":
        x = pos["x"] - text_w
    else:
        x = pos["x"]

    y = pos["y"]

    # Draw with optional stroke
    stroke_width = stroke_cfg.get("width", 0)
    stroke_color = stroke_cfg.get("color", "#000000")
    text_color = font_cfg.get("color", "#FFFFFF")

    draw.text(
        (x, y),
        text,
        fill=text_color,
        font=font,
        stroke_width=stroke_width,
        stroke_fill=stroke_color if stroke_width > 0 else None,
    )

    return canvas


def _apply_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """Apply rounded corners to an RGBA image."""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (image.size[0] - 1, image.size[1] - 1)],
        radius=radius,
        fill=255,
    )
    image.putalpha(mask)
    return image


def _resolve_font(family: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    """Resolve font by family name, checking multiple locations.

    Resolution order:
        1. frontend/public/fonts/{family}.otf
        2. System DejaVuSans fonts (Lambda-friendly)
        3. PIL default font
    """
    # Map common family names to filenames
    family_lower = family.lower().replace(" ", "")

    # Check frontend fonts directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_dir = os.path.join(base_dir, "..", "frontend", "public", "fonts")

    candidates = [
        os.path.join(font_dir, f"{family}.otf"),
        os.path.join(font_dir, f"{family}.ttf"),
    ]

    # System fonts (Linux/Lambda)
    if "bold" in family_lower or weight == "bold":
        candidates.append("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    candidates.append("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    # Windows system fonts
    winfonts = os.environ.get("WINDIR", r"C:\Windows")
    candidates.append(os.path.join(winfonts, "Fonts", "arial.ttf"))
    candidates.append(os.path.join(winfonts, "Fonts", "arialbd.ttf"))

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue

    # Ultimate fallback
    return ImageFont.load_default()


# =============================================================================
# VIDEO RENDERER (FFmpeg)
# =============================================================================

def render_video(
    template_json: dict, assets: dict, audio_s3_key: Optional[str] = None
) -> Optional[bytes]:
    """Render a promotional video from template + assets using FFmpeg.

    Builds an FFmpeg filter_complex that layers background (with pan/zoom),
    album art overlay, and text overlays. Optionally adds a 10-second audio clip.

    Requires FFmpeg to be installed and on PATH.

    Args:
        template_json: Template JSON preset dict
        assets: Dict with background (PIL), artwork (PIL), song_title, artist_name
        audio_s3_key: Optional S3 key for 10-second audio clip

    Returns:
        MP4 bytes or None if FFmpeg unavailable/fails
    """
    if not shutil.which("ffmpeg"):
        logger.warning("FFmpeg not found — video rendering unavailable")
        return None

    tmpdir = tempfile.mkdtemp(prefix="nm_video_")

    try:
        canvas_cfg = template_json.get("canvas", {"width": 1080, "height": 1920})
        width = canvas_cfg["width"]
        height = canvas_cfg["height"]
        duration = 10  # seconds — matches audio clip length

        # Save background to temp file
        bg = assets.get("background")
        if bg is None:
            return None
        bg_path = os.path.join(tmpdir, "bg.jpg")
        bg_rgb = bg.convert("RGB")
        if bg_rgb.size != (width, height):
            bg_rgb = bg_rgb.resize((width, height), Image.Resampling.LANCZOS)
        bg_rgb.save(bg_path, format="JPEG", quality=90)

        # Save album art to temp file
        artwork = assets.get("artwork")
        art_path = os.path.join(tmpdir, "art.png")
        if artwork:
            artwork.save(art_path, format="PNG")

        # Download audio if provided
        audio_path = None
        if audio_s3_key:
            audio_path = os.path.join(tmpdir, "audio.mp3")
            try:
                _get_s3().download_file(S3_BUCKET, audio_s3_key, audio_path)
            except Exception as e:
                logger.warning(f"Audio download failed, rendering without audio: {e}")
                audio_path = None

        output_path = os.path.join(tmpdir, "output.mp4")

        # Build FFmpeg command
        cmd = _build_ffmpeg_command(
            bg_path, art_path, audio_path, output_path,
            template_json, width, height, duration, assets,
        )

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"FFmpeg render failed: {result.stderr[:500]}")
            return None

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error("FFmpeg output is empty")
            return None

        with open(output_path, "rb") as f:
            video_bytes = f.read()

        logger.info(f"Video rendered: {len(video_bytes)} bytes")
        return video_bytes

    except subprocess.TimeoutExpired:
        logger.error("FFmpeg render timed out (120s)")
        return None
    except Exception as e:
        logger.error(f"Video render error: {e}")
        return None
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


def _build_ffmpeg_command(
    bg_path: str,
    art_path: str,
    audio_path: Optional[str],
    output_path: str,
    template_json: dict,
    width: int,
    height: int,
    duration: int,
    assets: dict,
) -> list[str]:
    """Build the FFmpeg command with filter_complex for video assembly."""
    # Find album art layer config
    art_layer = None
    text_layers = []
    bg_animation = None

    for layer in template_json.get("layers", []):
        if layer["type"] == "background":
            bg_animation = layer.get("animation", {})
        elif layer["type"] == "album_art":
            art_layer = layer
        elif layer["type"] == "text":
            text_layers.append(layer)

    # Build filter_complex
    filters = []

    # Background: subtle zoom effect via zoompan
    zoom_type = bg_animation.get("type", "pan_zoom") if bg_animation else "pan_zoom"
    if zoom_type == "pan_zoom":
        fps = 30
        total_frames = duration * fps
        filters.append(
            f"[0:v]loop=loop={total_frames}:size=1:start=0,"
            f"zoompan=z='min(zoom+0.0005,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={width}x{height}:fps={fps}[bg]"
        )
    else:
        fps = 30
        total_frames = duration * fps
        filters.append(
            f"[0:v]loop=loop={total_frames}:size=1:start=0,"
            f"scale={width}:{height},fps={fps}[bg]"
        )

    current_stream = "bg"

    # Album art overlay
    if art_layer and os.path.exists(art_path):
        pos = art_layer.get("position", {"x": 0, "y": 0})
        size = art_layer.get("size", {"width": 648, "height": 648})
        filters.append(
            f"[1:v]scale={size['width']}:{size['height']}[art]"
        )
        filters.append(
            f"[{current_stream}][art]overlay={pos['x']}:{pos['y']}[v1]"
        )
        current_stream = "v1"

    # Text overlays via drawtext filter
    for i, text_layer in enumerate(text_layers):
        field = text_layer.get("field", "")
        text = assets.get(field, "")
        if not text:
            continue

        font_cfg = text_layer.get("font", {})
        pos = text_layer.get("position", {"x": 0, "y": 0})
        stroke_cfg = text_layer.get("stroke", {})
        alignment = text_layer.get("alignment", "center")

        # Escape text for FFmpeg drawtext
        escaped_text = text.replace("'", "'\\''").replace(":", "\\:")

        # Build drawtext filter
        font_size = font_cfg.get("size", 32)
        font_color = font_cfg.get("color", "white").replace("#", "0x")
        border_w = stroke_cfg.get("width", 0)

        # Calculate x expression for alignment
        if alignment == "center":
            x_expr = f"(w-text_w)/2"
        elif alignment == "right":
            x_expr = f"w-text_w-{pos['x']}"
        else:
            x_expr = str(pos["x"])

        drawtext = (
            f"drawtext=text='{escaped_text}'"
            f":fontsize={font_size}"
            f":fontcolor={font_color}"
            f":x={x_expr}:y={pos['y']}"
            f":borderw={border_w}"
        )

        next_stream = f"v{i + 2}"
        filters.append(f"[{current_stream}]{drawtext}[{next_stream}]")
        current_stream = next_stream

    filter_complex = ";".join(filters)

    # Build command
    cmd = ["ffmpeg", "-y"]

    # Input: background image
    cmd.extend(["-i", bg_path])

    # Input: album art (if available)
    if art_layer and os.path.exists(art_path):
        cmd.extend(["-i", art_path])

    # Input: audio (if available)
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", audio_path])

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", f"[{current_stream}]",
    ])

    # Map audio if present
    if audio_path and os.path.exists(audio_path):
        audio_input_idx = 2 if (art_layer and os.path.exists(art_path)) else 1
        cmd.extend(["-map", f"{audio_input_idx}:a"])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-t", str(duration),
    ])

    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])

    cmd.append(output_path)

    return cmd
