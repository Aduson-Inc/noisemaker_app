"""
NOiSEMaKER Model Router
========================

Deterministic routing script ("The Root Router") that sends tasks to the
most cost-effective AI model without human intervention.

Each task type (vision analysis, background generation, captioning, template
analysis) maps to a provider + model + SSM key. When provider is "PLACEHOLDER",
the router falls back to existing behavior:
    - background_generator: HuggingFace FLUX.1-schnell (EXISTING)
    - caption_llm: Grok API (EXISTING)
    - vision_analyzer: PLACEHOLDER — callers fall back to PIL ColorAnalyzer
    - template_analyzer: PLACEHOLDER — callers fall back to hardcoded presets

To swap in a real model later:
    1. Update the SSM parameter value in AWS
    2. Change provider and model_id in MODEL_CONFIG
    3. No other code changes needed — the router handles dispatch
"""

import logging
import os
import time
from typing import Optional

import boto3
import requests
from PIL import Image

logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# PLACEHOLDER = model not yet decided. Router falls back to existing behavior.
# Grep for "PLACEHOLDER" to find all undecided models.

MODEL_CONFIG = {
    "vision_analyzer": {
        "provider": "PLACEHOLDER",      # e.g., "openai", "google", "huggingface"
        "model_id": "PLACEHOLDER",      # e.g., "gpt-4o-mini", "gemini-2.0-flash"
        "description": "Lightweight vision model for color/mood analysis",
        "ssm_param": "/noisemaker/vision_model_api_key",  # TO BE CREATED
    },
    "background_generator": {
        "provider": "huggingface",      # EXISTING — already works
        "model_id": "black-forest-labs/FLUX.1-schnell",
        "description": "Fast abstract background generation",
        "ssm_param": "/noisemaker/huggingface_token",     # EXISTS
    },
    "caption_llm": {
        "provider": "grok",             # EXISTING — already works
        "model_id": "grok-beta",
        "description": "High-tier reasoning LLM for captions",
        "ssm_param": "/noisemaker/grok_api_key",          # EXISTS
    },
    "template_analyzer": {
        "provider": "PLACEHOLDER",      # e.g., "openai", "google"
        "model_id": "PLACEHOLDER",      # Vision LLM for bounding box extraction
        "description": "Analyzes uploaded templates to extract coordinates",
        "ssm_param": "/noisemaker/template_vision_api_key",  # TO BE CREATED
    },
}


# =============================================================================
# LAZY-LOADED CREDENTIALS
# =============================================================================

_ssm_client = None
_cached_params = {}


def _get_ssm_client():
    global _ssm_client
    if _ssm_client is None:
        _ssm_client = boto3.client("ssm", region_name=AWS_REGION)
    return _ssm_client


def _get_ssm_param(param_name: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch a value from SSM Parameter Store with in-memory caching."""
    if param_name in _cached_params:
        return _cached_params[param_name]
    try:
        value = _get_ssm_client().get_parameter(
            Name=param_name, WithDecryption=True
        )["Parameter"]["Value"]
        if value and value != "PLACEHOLDER_NOT_CONFIGURED":
            _cached_params[param_name] = value
            return value
        logger.warning(f"SSM param {param_name} is placeholder — not configured")
        return default
    except Exception as e:
        if default is not None:
            logger.warning(f"SSM param {param_name} not found, using default")
            return default
        logger.error(f"Failed to load SSM param {param_name}: {e}")
        return None


# =============================================================================
# PUBLIC API
# =============================================================================

def get_model_config(task: str) -> dict:
    """Return provider/model/key config for a task type.

    Args:
        task: One of "vision_analyzer", "background_generator",
              "caption_llm", "template_analyzer"

    Returns:
        Config dict with provider, model_id, description, ssm_param
    """
    if task not in MODEL_CONFIG:
        raise ValueError(
            f"Unknown task type: {task}. Valid: {list(MODEL_CONFIG.keys())}"
        )
    return MODEL_CONFIG[task]


def call_image_generator(
    prompt: str, width: int, height: int, retry_count: int = 2
) -> Optional[Image.Image]:
    """Generate an image via the configured background_generator model.

    Currently routes to HuggingFace FLUX.1-schnell.
    Same retry logic as the original content_generator._generate_background().

    Args:
        prompt: Text prompt for image generation
        width: Output image width
        height: Output image height
        retry_count: Number of retries on transient errors

    Returns:
        PIL Image or None on failure
    """
    config = MODEL_CONFIG["background_generator"]

    if config["provider"] == "PLACEHOLDER":
        logger.warning("background_generator is PLACEHOLDER — no image generation")
        return None

    api_key = _get_ssm_param(config["ssm_param"])
    if not api_key:
        return None

    if config["provider"] == "huggingface":
        return _call_huggingface_image(
            api_key, config["model_id"], prompt, width, height, retry_count
        )

    # Future providers (Nano Banana Pro, Recraft, Flux Pro, etc.) go here
    logger.error(f"Unsupported image provider: {config['provider']}")
    return None


def call_text_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.7,
) -> Optional[str]:
    """Call the configured caption LLM with system + user prompt.

    Currently routes to Grok API.
    Returns the raw response text — caller handles parsing.

    Args:
        system_prompt: System role content
        user_prompt: User role content
        max_tokens: Max response tokens
        temperature: Sampling temperature

    Returns:
        Response text string or None on failure
    """
    config = MODEL_CONFIG["caption_llm"]

    if config["provider"] == "PLACEHOLDER":
        logger.warning("caption_llm is PLACEHOLDER — no text generation")
        return None

    api_key = _get_ssm_param(config["ssm_param"])
    if not api_key:
        return None

    if config["provider"] == "grok":
        return _call_grok_text(
            api_key, config["model_id"], system_prompt, user_prompt,
            max_tokens, temperature
        )

    # Future providers (Claude, GPT-5, Gemini, etc.) go here
    logger.error(f"Unsupported text provider: {config['provider']}")
    return None


def call_vision_model(image_bytes: bytes, prompt: str) -> Optional[str]:
    """Call the configured vision model to analyze an image.

    Currently PLACEHOLDER — returns None so callers fall back to
    PIL-based ColorAnalyzer output formatted as prose.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG)
        prompt: Analysis prompt (e.g., "Describe the color palette and mood...")

    Returns:
        Plain-text analysis string, or None if PLACEHOLDER/failure
    """
    config = MODEL_CONFIG["vision_analyzer"]

    if config["provider"] == "PLACEHOLDER":
        logger.info("vision_analyzer is PLACEHOLDER — caller should use ColorAnalyzer fallback")
        return None

    api_key = _get_ssm_param(config["ssm_param"])
    if not api_key:
        return None

    # Future vision providers (OpenAI gpt-4o-mini, Gemini Flash, etc.) go here
    logger.error(f"Unsupported vision provider: {config['provider']}")
    return None


def call_template_analyzer(image_bytes: bytes, prompt: str) -> Optional[str]:
    """Call the configured template analyzer to extract bounding boxes.

    Currently PLACEHOLDER — returns None so callers use hardcoded default presets.

    Args:
        image_bytes: Raw image bytes of the master template
        prompt: Extraction prompt (e.g., "Identify bounding boxes for album art, text...")

    Returns:
        JSON string of coordinates, or None if PLACEHOLDER/failure
    """
    config = MODEL_CONFIG["template_analyzer"]

    if config["provider"] == "PLACEHOLDER":
        logger.info("template_analyzer is PLACEHOLDER — caller should use default preset")
        return None

    api_key = _get_ssm_param(config["ssm_param"])
    if not api_key:
        return None

    # Future template analyzer providers go here
    logger.error(f"Unsupported template analyzer provider: {config['provider']}")
    return None


# =============================================================================
# PROVIDER IMPLEMENTATIONS (PRIVATE)
# =============================================================================

def _call_huggingface_image(
    api_key: str,
    model_id: str,
    prompt: str,
    width: int,
    height: int,
    retry_count: int,
) -> Optional[Image.Image]:
    """Generate image via HuggingFace Inference API.

    Same retry logic as the original content_generator._generate_background():
    retries on queue/timeout/503/429 errors with 30s backoff.
    """
    try:
        from huggingface_hub import InferenceClient

        logger.info(f"[model_router] HuggingFace image gen: {prompt[:80]}...")

        client = InferenceClient(api_key=api_key)
        image = client.text_to_image(prompt=prompt, model=model_id)

        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        logger.info(f"[model_router] Image generated: {image.size}")
        return image

    except Exception as e:
        error_msg = str(e).lower()
        if retry_count > 0 and any(
            k in error_msg for k in ("queue", "timeout", "503", "429")
        ):
            logger.warning(
                f"[model_router] Retrying in 30s... ({retry_count} retries left)"
            )
            time.sleep(30)
            return _call_huggingface_image(
                api_key, model_id, prompt, width, height, retry_count - 1
            )

        logger.error(f"[model_router] HuggingFace image gen failed: {e}")
        return None


def _call_grok_text(
    api_key: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
) -> Optional[str]:
    """Call Grok AI chat completions API.

    Uses the same endpoint and payload format as caption_generator._call_grok_ai().
    """
    try:
        grok_url = _get_ssm_param(
            "/noisemaker/grok_api_url",
            default="https://api.grok.ai/v1/chat/completions",
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = requests.post(grok_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        logger.error(
            f"[model_router] Grok API error: {response.status_code} - {response.text}"
        )
        return None

    except Exception as e:
        logger.error(f"[model_router] Grok API call failed: {e}")
        return None
