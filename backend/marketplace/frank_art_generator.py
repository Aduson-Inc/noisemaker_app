"""
Frank Art Generator for Marketplace
====================================

Generates 4 high-quality Frank Art pieces daily using Stable Diffusion XL 1.0 Base.
Runs as AWS Lambda triggered by EventBridge at 9 PM UTC daily.

Three rotating lists advance by 1 each day:
- ART_STYLES: 7 styles
- ARTIST_STYLES: 11 artists
- COLORS: 58 entries (dark, none, bright, none pattern)

This creates massive variety before any combination repeats.
"""

import os
import json
import time
import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import Dict, Tuple, Optional
import boto3
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
S3_BUCKET = os.environ.get('S3_BUCKET', 'noisemakerpromobydoowopp')

# HuggingFace token - cached after first fetch
_huggingface_token_cache = None


def get_huggingface_token() -> str:
    """
    Fetch HuggingFace token from AWS SSM Parameter Store.
    Cached after first fetch for performance.
    """
    global _huggingface_token_cache

    if _huggingface_token_cache:
        return _huggingface_token_cache

    # Check environment variable first (local testing)
    env_token = os.environ.get('HUGGINGFACE_TOKEN')
    if env_token:
        logger.info("Using HuggingFace token from environment variable")
        _huggingface_token_cache = env_token
        return _huggingface_token_cache

    # Fetch from SSM Parameter Store
    try:
        logger.info("Fetching HuggingFace token from SSM...")
        ssm_client = boto3.client('ssm', region_name=AWS_REGION)
        response = ssm_client.get_parameter(
            Name='/noisemaker/huggingface_token',
            WithDecryption=True
        )
        _huggingface_token_cache = response['Parameter']['Value']
        logger.info("HuggingFace token loaded from SSM")
        return _huggingface_token_cache
    except Exception as e:
        logger.error(f"Failed to get HuggingFace token from SSM: {e}")
        raise


# Generation settings
IMAGES_PER_RUN = 4
ORIGINAL_SIZE = (2000, 2000)
MOBILE_SIZE = (600, 600)
THUMBNAIL_SIZE = (200, 200)

# S3 folder structure
S3_ORIGINAL_FOLDER = 'ArtSellingONLY/original/'
S3_MOBILE_FOLDER = 'ArtSellingONLY/mobile/'
S3_THUMBNAIL_FOLDER = 'ArtSellingONLY/thumbnails/'
S3_STATE_FILE = 'ArtSellingONLY/state.json'

# Pool management
MAX_POOL_SIZE = 250

# =============================================================================
# ROTATING LISTS
# =============================================================================

# Art styles (7 total) - advances by 1 each day
ART_STYLES = [
    "Impressionism",
    "Cubism",
    "Surrealism",
    "Art Deco",
    "Minimalist",
    "Abstract Expressionism",
    "Vaporwave"
]

# Artist styles (11 total) - advances by 1 each day
ARTIST_STYLES = [
    "Jean-Michel Basquiat",
    "Georges Braque",
    "Georgia Theologoe",
    "Ernst Ludwig Kirchner",
    "Malgorzata Kmiec",
    "Pascal Blanche",
    "Kazimir Malevich",
    "Yayoi Kusama",
    "Nives Palmic",
    "Finn Campbell-Norman",
    "Elena Kotliarker"
]

# Colors (58 total) - advances by 1 each day
# Pattern: dark, none, bright, none, dark, none, bright, none...
# 15 dark colors interleaved with 14 bright colors, each followed by none
COLORS = [
    # Cycle 1
    "deep black and charcoal",      # Day 0: dark 1
    None,                            # Day 1: none
    "vibrant red and white",         # Day 2: bright 1
    None,                            # Day 3: none
    # Cycle 2
    "midnight blue and dark navy",   # Day 4: dark 2
    None,                            # Day 5: none
    "electric blue and cyan",        # Day 6: bright 2
    None,                            # Day 7: none
    # Cycle 3
    "dark crimson and blood red",    # Day 8: dark 3
    None,                            # Day 9: none
    "golden yellow and cream",       # Day 10: bright 3
    None,                            # Day 11: none
    # Cycle 4
    "obsidian and shadow",           # Day 12: dark 4
    None,                            # Day 13: none
    "neon pink and hot magenta",     # Day 14: bright 4
    None,                            # Day 15: none
    # Cycle 5
    "deep forest green and black",   # Day 16: dark 5
    None,                            # Day 17: none
    "bright orange and coral",       # Day 18: bright 5
    None,                            # Day 19: none
    # Cycle 6
    "dark burgundy and wine",        # Day 20: dark 6
    None,                            # Day 21: none
    "lime green and yellow",         # Day 22: bright 6
    None,                            # Day 23: none
    # Cycle 7
    "pitch black and dark gold",     # Day 24: dark 7
    None,                            # Day 25: none
    "sky blue and white",            # Day 26: bright 7
    None,                            # Day 27: none
    # Cycle 8
    "charcoal grey and iron",        # Day 28: dark 8
    None,                            # Day 29: none
    "bright purple and lavender",    # Day 30: bright 8
    None,                            # Day 31: none
    # Cycle 9
    "deep purple and black",         # Day 32: dark 9
    None,                            # Day 33: none
    "sunny yellow and orange",       # Day 34: bright 9
    None,                            # Day 35: none
    # Cycle 10
    "dark maroon and onyx",          # Day 36: dark 10
    None,                            # Day 37: none
    "turquoise and aqua",            # Day 38: bright 10
    None,                            # Day 39: none
    # Cycle 11
    "midnight green and coal",       # Day 40: dark 11
    None,                            # Day 41: none
    "vivid red and pink",            # Day 42: bright 11
    None,                            # Day 43: none
    # Cycle 12
    "dark indigo and slate",         # Day 44: dark 12
    None,                            # Day 45: none
    "bright green and lime",         # Day 46: bright 12
    None,                            # Day 47: none
    # Cycle 13
    "black and burnt sienna",        # Day 48: dark 13
    None,                            # Day 49: none
    "electric purple and neon blue", # Day 50: bright 13
    None,                            # Day 51: none
    # Cycle 14
    "deep brown and shadow",         # Day 52: dark 14
    None,                            # Day 53: none
    "coral and peach",               # Day 54: bright 14
    None,                            # Day 55: none
    # Cycle 15 (final dark, no more brights)
    "dark olive and graphite",       # Day 56: dark 15
    None,                            # Day 57: none
]

# S3 client - uses IAM role credentials in Lambda
s3_client = boto3.client('s3', region_name=AWS_REGION)


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def load_state() -> Dict:
    """Load generation state from S3."""
    try:
        logger.info("Loading state from S3...")
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_STATE_FILE)
        state = json.loads(response['Body'].read().decode('utf-8'))

        # Ensure all indices exist (backwards compatibility)
        if 'art_style_index' not in state:
            state['art_style_index'] = 0
        if 'artist_index' not in state:
            state['artist_index'] = state.get('style_index', 0)
        if 'color_index' not in state:
            state['color_index'] = 0
        if 'day_counter' not in state:
            state['day_counter'] = 0

        logger.info(f"State loaded: Day {state['day_counter']}, Art Style #{state['art_style_index']}, Artist #{state['artist_index']}, Color #{state['color_index']}")
        return state
    except s3_client.exceptions.NoSuchKey:
        logger.info("No existing state found, initializing...")
        return {
            'art_style_index': 0,
            'artist_index': 0,
            'color_index': 0,
            'day_counter': 0,
            'last_run': None
        }
    except Exception as e:
        logger.error(f"Error loading state: {e}")
        raise


def save_state(state: Dict) -> None:
    """Save generation state to S3."""
    try:
        logger.info("Saving state to S3...")
        state['last_run'] = datetime.utcnow().isoformat()

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_STATE_FILE,
            Body=json.dumps(state, indent=2),
            ContentType='application/json'
        )
        logger.info("State saved successfully")
    except Exception as e:
        logger.error(f"Error saving state: {e}")
        raise


# =============================================================================
# PROMPT GENERATION
# =============================================================================

def get_current_prompt(state: Dict) -> Tuple[str, str, Optional[str], str]:
    """
    Generate prompt based on current state.

    Returns:
        Tuple of (art_style, artist, colors, full_prompt)
    """
    art_style = ART_STYLES[state['art_style_index']]
    artist = ARTIST_STYLES[state['artist_index']]
    colors = COLORS[state['color_index']]

    if colors:
        prompt = f"create a {art_style} background graphic in the style of {artist} using {colors}"
    else:
        prompt = f"create a {art_style} background graphic in the style of {artist}"

    return art_style, artist, colors, prompt


def advance_state(state: Dict) -> Dict:
    """
    Advance all indices by 1 (wrapping at list end).
    Each list is a different length, creating unique combinations.
    """
    state['day_counter'] += 1
    state['art_style_index'] = (state['art_style_index'] + 1) % len(ART_STYLES)
    state['artist_index'] = (state['artist_index'] + 1) % len(ARTIST_STYLES)
    state['color_index'] = (state['color_index'] + 1) % len(COLORS)

    return state


# =============================================================================
# IMAGE GENERATION
# =============================================================================

def generate_image(prompt: str, retry_count: int = 2) -> Optional[Image.Image]:
    """
    Generate image using HuggingFace SDXL API.
    Includes retry logic for rate limits and model loading.
    """
    try:
        from huggingface_hub import InferenceClient

        logger.info(f"Generating image: {prompt[:60]}...")

        token = get_huggingface_token()

        client = InferenceClient(
            provider="nscale",
            api_key=token,
        )

        image = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            negative_prompt="blurry, low quality, watermark, text, logo, signature, distorted",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=2000,
            width=2000,
        )

        logger.info(f"Image generated: {image.size}")
        return image

    except Exception as e:
        error_msg = str(e).lower()

        # Retry on rate limit or model loading
        if retry_count > 0 and ("429" in error_msg or "rate limit" in error_msg or "503" in error_msg or "loading" in error_msg):
            logger.warning(f"Retrying in 20s... ({retry_count} retries left)")
            time.sleep(20)
            return generate_image(prompt, retry_count - 1)

        logger.error(f"Image generation failed: {e}")
        return None


def resize_image(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """Resize image using high-quality LANCZOS resampling."""
    return image.resize(size, Image.Resampling.LANCZOS)


def upload_to_s3(image: Image.Image, s3_key: str, metadata: Dict) -> bool:
    """Upload PIL Image to S3."""
    try:
        buffer = BytesIO()
        image.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=buffer,
            ContentType='image/png',
            Metadata=metadata
        )

        logger.info(f"Uploaded: s3://{S3_BUCKET}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return False


# =============================================================================
# DYNAMODB
# =============================================================================

def get_pool_count() -> int:
    """Get current count of unpurchased artworks."""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')
        response = table.scan(
            Select='COUNT',
            FilterExpression='#purchased = :false',
            ExpressionAttributeNames={'#purchased': 'is_purchased'},
            ExpressionAttributeValues={':false': False}
        )
        return response.get('Count', 0)
    except Exception as e:
        logger.warning(f"Could not get pool count: {e}")
        return 0


def store_metadata(artwork_id: str, filename: str, prompt: str,
                   art_style: str, artist: str, colors: Optional[str]) -> bool:
    """Store artwork metadata in DynamoDB."""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')

        item = {
            'artwork_id': artwork_id,
            'filename': filename,
            's3_key_thumbnail': f'{S3_THUMBNAIL_FOLDER}{filename}',
            's3_key_mobile': f'{S3_MOBILE_FOLDER}{filename}',
            's3_key_original': f'{S3_ORIGINAL_FOLDER}{filename}',
            'upload_date': datetime.utcnow().isoformat(),
            'download_count': 0,
            'is_purchased': False,
            'prompt_used': prompt,
            'art_style': art_style,
            'artist_style': artist,
            'color_scheme': colors if colors else 'none',
            'created_at': datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)
        logger.info(f"Metadata stored: {artwork_id}")
        return True
    except Exception as e:
        logger.error(f"Metadata storage failed: {e}")
        return False


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def generate_daily_artwork() -> Dict:
    """
    Main generation function. Generates 4 images and uploads to S3.
    """
    logger.info("=" * 60)
    logger.info("FRANK ART GENERATOR - Starting")
    logger.info("=" * 60)

    # Check pool size
    current_pool = get_pool_count()
    logger.info(f"Pool size: {current_pool}/{MAX_POOL_SIZE}")

    if current_pool >= MAX_POOL_SIZE:
        logger.info("Pool at capacity - skipping generation")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'images_generated': 0,
                'reason': 'Pool at capacity',
                'pool_count': current_pool
            })
        }

    # Load state
    state = load_state()

    # Get current prompt settings
    art_style, artist, colors, prompt = get_current_prompt(state)

    logger.info(f"Art Style: {art_style}")
    logger.info(f"Artist: {artist}")
    logger.info(f"Colors: {colors if colors else 'None'}")
    logger.info(f"Prompt: {prompt}")

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    successful = 0
    artwork_ids = []

    # Generate 4 images
    for i in range(1, IMAGES_PER_RUN + 1):
        logger.info(f"--- Image {i}/{IMAGES_PER_RUN} ---")

        # Generate
        original = generate_image(prompt)
        if original is None:
            logger.error(f"Image {i} failed, skipping")
            continue

        # Ensure correct size
        if original.size != ORIGINAL_SIZE:
            original = resize_image(original, ORIGINAL_SIZE)

        # Create resized versions
        mobile = resize_image(original, MOBILE_SIZE)
        thumbnail = resize_image(original, THUMBNAIL_SIZE)

        # Generate IDs
        artwork_id = str(uuid.uuid4())
        filename = f"{artwork_id}.png"

        metadata = {
            'artwork-id': artwork_id,
            'generation-date': datetime.utcnow().isoformat(),
            'batch-timestamp': timestamp
        }

        # Upload all 3 sizes
        success = True
        success &= upload_to_s3(original, S3_ORIGINAL_FOLDER + filename, metadata)
        success &= upload_to_s3(mobile, S3_MOBILE_FOLDER + filename, metadata)
        success &= upload_to_s3(thumbnail, S3_THUMBNAIL_FOLDER + filename, metadata)

        if success:
            if store_metadata(artwork_id, filename, prompt, art_style, artist, colors):
                successful += 1
                artwork_ids.append(artwork_id)
                logger.info(f"Image {i} complete: {artwork_id}")

    # Advance state
    new_state = advance_state(state)
    save_state(new_state)

    # Preview next run
    next_style, next_artist, next_colors, _ = get_current_prompt(new_state)
    logger.info(f"Next run: {next_style} / {next_artist} / {next_colors if next_colors else 'None'}")

    logger.info("=" * 60)
    logger.info(f"COMPLETE: {successful}/{IMAGES_PER_RUN} images")
    logger.info("=" * 60)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'images_generated': successful,
            'artwork_ids': artwork_ids,
            'art_style': art_style,
            'artist': artist,
            'colors': colors,
            'timestamp': timestamp,
            'pool_count': current_pool + successful
        })
    }


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def lambda_handler(event, context):
    """AWS Lambda entry point. Called by EventBridge at 9 PM UTC daily."""
    try:
        return generate_daily_artwork()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


# =============================================================================
# LOCAL TESTING
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FRANK ART GENERATOR - Local Test")
    print("=" * 60)

    try:
        token = get_huggingface_token()
        print(f"HuggingFace token: {token[:10]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nSet HUGGINGFACE_TOKEN env var or configure AWS credentials for SSM")
        exit(1)

    print(f"Region: {AWS_REGION}")
    print(f"Bucket: {S3_BUCKET}")
    print(f"Colors list length: {len(COLORS)} entries")
    print()

    result = generate_daily_artwork()
    print(json.dumps(result, indent=2))
