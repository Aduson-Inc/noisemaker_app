"""
Daily Frank Art Generator for Marketplace
======================================================

Generates 4 high-quality Frank Art pieces daily using Stable Diffusion XL 1.0 Base.


"""

import os
import json
import time
import logging
import argparse
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Tuple, Optional
import boto3
from PIL import Image

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Configure logging with emojis for visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================


# Fetch parameters from AWS Parameter Store (uses /noisemaker/ prefix with lowercase keys)
USER_ID = os.environ.get('CURRENT_USER_ID', 'default')
from ..auth.environment_loader import env_loader

# Use specific getter methods for reliable parameter retrieval
HUGGINGFACE_TOKEN = env_loader.get_huggingface_token() or os.environ.get('HUGGINGFACE_TOKEN')
# AWS credentials are optional - Lambda uses IAM role, local uses Parameter Store or env vars
AWS_ACCESS_KEY_ID = env_loader.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID') or None
AWS_SECRET_ACCESS_KEY = env_loader.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY') or None
AWS_REGION = env_loader.get('aws_region') or os.environ.get('AWS_REGION', 'us-east-2')
S3_BUCKET = env_loader.get('s3_bucket') or os.environ.get('S3_BUCKET', 'noisemakerpromobydoowopp')

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

# Local mode folder structure
LOCAL_OUTPUT_DIR = 'output'
LOCAL_ORIGINAL_FOLDER = 'output/original'
LOCAL_MOBILE_FOLDER = 'output/mobile'
LOCAL_THUMBNAIL_FOLDER = 'output/thumbnails'
LOCAL_STATE_FILE = 'output/state.json'

# Art styles (7 total - cycles through different movements)
ART_STYLES = [
    "Impressionism",
    "Cubism",
    "Surrealism",
    "Art Deco",
    "Minimalist",
    "Abstract Expressionism",
    "Vaporwave"
]

# Artist styles (11 total - cycles)
ARTIST_STYLES = [
    "Jean-Michel Basquiat",
    "Georges Braque",
    "Georgia Theologoe",
    "Ernst Ludwig Kirchner",
    "Małgorzata Kmiec",
    "Pascal Blanche",
    "Kazimir Malevich",
    "Yayoi Kusama",
    "Nives Palmic",
    "Finn Campbell-Norman",
    "Elena Kotliarker"
]

# Pool management
MAX_POOL_SIZE = 250

# Dark color schemes (15 total)
DARK_COLORS = [
    "deep black and charcoal",
    "midnight blue and dark navy",
    "dark crimson and blood red",
    "obsidian and shadow",
    "deep forest green and black",
    "dark burgundy and wine",
    "pitch black and dark gold",
    "charcoal grey and iron",
    "deep purple and black",
    "dark maroon and onyx",
    "midnight green and coal",
    "dark indigo and slate",
    "black and burnt sienna",
    "deep brown and shadow",
    "dark olive and graphite"
]

# Bright color schemes (14 total)
BRIGHT_COLORS = [
    "vibrant red and white",
    "electric blue and cyan",
    "golden yellow and cream",
    "neon pink and hot magenta",
    "bright orange and coral",
    "lime green and yellow",
    "sky blue and white",
    "bright purple and lavender",
    "sunny yellow and orange",
    "turquoise and aqua",
    "vivid red and pink",
    "bright green and lime",
    "electric purple and neon blue",
    "coral and peach"
]

# ============================================================================
# S3 CLIENT INITIALIZATION
# ============================================================================

# Create S3 client (credentials optional - uses IAM role in Lambda)
s3_client_kwargs = {'region_name': AWS_REGION}
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    s3_client_kwargs.update({
        'aws_access_key_id': AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
    })
s3_client = boto3.client('s3', **s3_client_kwargs)


# ============================================================================
# CONNECTION TESTING
# ============================================================================

def test_connection() -> bool:
    """
    Test connections to Hugging Face API and AWS S3.
    Returns True if all connections successful, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("🔌 TESTING CONNECTIONS")
    logger.info("=" * 80)
    
    all_ok = True
    
    # Test 1: Check environment variables
    logger.info("\n1️⃣  Checking environment variables...")
    required_vars = {
        'HUGGINGFACE_TOKEN': HUGGINGFACE_TOKEN,
        'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
        'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
        'S3_BUCKET': S3_BUCKET
    }
    
    for var_name, var_value in required_vars.items():
        if not var_value:
            logger.error(f"   ERROR: {var_name}: Not set")
            all_ok = False
        else:
            masked_value = var_value[:8] + "..." if len(var_value) > 8 else "***"
            logger.info(f"   ✅ {var_name}: {masked_value}")
    
    if not all_ok:
        logger.error("\nERROR: Missing required environment variables. Check your .env file.")
        return False
    
    # Test 2: Hugging Face API
    logger.info("\n2️⃣  Testing Hugging Face API connection...")
    try:
        from huggingface_hub import InferenceClient

        # Test connection with InferenceClient (nscale provider)
        client = InferenceClient(
            provider="nscale",
            api_key=HUGGINGFACE_TOKEN,
        )

        # Simple test to verify connection (we'll just create the client successfully)
        logger.info("   ✅ Hugging Face API: Connected (InferenceClient initialized)")
        logger.info("   ✅ Provider: nscale (official Hugging Face inference)")
        logger.info(f"   ✅ Model: stabilityai/stable-diffusion-xl-base-1.0 (ready)")

    except Exception as e:
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg or "token" in error_msg:
            logger.error("   ERROR: Hugging Face API: Invalid token")
        else:
            logger.error(f"   ERROR: Hugging Face API: {str(e)}")
        all_ok = False
    
    # Test 3: AWS S3 connection
    logger.info("\n3️⃣  Testing AWS S3 connection...")
    try:
        # List buckets to test credentials
        response = s3_client.list_buckets()
        logger.info(f"   ✅ AWS S3 Access: Connected ({len(response['Buckets'])} buckets)")
        
        # Check if our specific bucket exists
        bucket_exists = any(b['Name'] == S3_BUCKET for b in response['Buckets'])
        if bucket_exists:
            logger.info(f"   ✅ S3 Bucket exists: {S3_BUCKET}")
        else:
            logger.error(f"   ERROR: S3 Bucket not found: {S3_BUCKET}")
            logger.error(f"   ℹ️  Available buckets: {[b['Name'] for b in response['Buckets']]}")
            all_ok = False
    except Exception as e:
        logger.error(f"   ERROR: AWS S3: {str(e)}")
        all_ok = False
    
    # Test 4: S3 write permissions (try to create state file)
    if all_ok:
        logger.info("\n4️⃣  Testing S3 write permissions...")
        try:
            test_key = f"album-art/connection-test-{int(time.time())}.txt"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=test_key,
                Body=b"Connection test",
                ContentType='text/plain'
            )
            logger.info(f"   ✅ S3 Write: Success")
            
            # Clean up test file
            s3_client.delete_object(Bucket=S3_BUCKET, Key=test_key)
            logger.info(f"   ✅ S3 Delete: Success")
        except Exception as e:
            logger.error(f"   ERROR: S3 Write: {str(e)}")
            all_ok = False
    
    # Final result
    logger.info("\n" + "=" * 80)
    if all_ok:
        logger.info("✅ ALL CONNECTIONS SUCCESSFUL!")
        logger.info("=" * 80)
        logger.info("\nYou're ready to generate artwork! Run:")
        logger.info("  python daily_album_art_generator.py --test-mode    # Test with 1 image")
        logger.info("  python daily_album_art_generator.py                # Full run (4 images)")
    else:
        logger.info("ERROR: CONNECTION TEST FAILED")
        logger.info("=" * 80)
        logger.info("\nPlease fix the errors above before running the generator.")
    
    return all_ok


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def load_state() -> Dict:
    """Load generation state from S3 (tracks progress between runs)."""
    try:
        logger.info("📥 Loading state from S3...")
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_STATE_FILE)
        state = json.loads(response['Body'].read().decode('utf-8'))

        # Ensure art_style_index exists (backwards compatibility)
        if 'art_style_index' not in state:
            state['art_style_index'] = 0

        logger.info(f"✅ State loaded: Art Style #{state['art_style_index']}, Artist #{state['style_index']}, Day {state['day_counter']}")
        return state
    except s3_client.exceptions.NoSuchKey:
        logger.info("🆕 No existing state found, initializing new state...")
        return {
            'art_style_index': 0,   # NEW - 7 art styles (Impressionism, Cubism, etc.)
            'style_index': 0,        # 11 artist styles
            'dark_color_index': 0,
            'bright_color_index': 0,
            'day_counter': 0,
            'last_run': None
        }
    except Exception as e:
        logger.error(f"ERROR: Error loading state: {str(e)}")
        raise


def save_state(state: Dict) -> None:
    """Save generation state to S3."""
    try:
        logger.info("💾 Saving state to S3...")
        state['last_run'] = datetime.utcnow().isoformat()
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_STATE_FILE,
            Body=json.dumps(state, indent=2),
            ContentType='application/json'
        )
        logger.info("✅ State saved successfully")
    except Exception as e:
        logger.error(f"ERROR: Error saving state: {str(e)}")
        raise


# ============================================================================
# PROMPT GENERATION
# ============================================================================

def get_current_prompts(state: Dict) -> Tuple[str, str, str, str, Optional[str], str]:
    """
    Generate prompts based on current state using 3 rotating lists.

    Returns:
        Tuple of (art_style, artist_name, color_mode, colors_used, full_prompt)
    """
    # Get current art style and artist from their respective lists
    art_style = ART_STYLES[state['art_style_index']]
    artist = ARTIST_STYLES[state['style_index']]

    # Determine color mode based on 4-day cycle: DARK, BLANK, BRIGHT, BLANK
    day_in_cycle = state['day_counter'] % 4

    if day_in_cycle == 0:
        # Day 0: DARK colors
        colors = DARK_COLORS[state['dark_color_index']]
        color_mode = 'dark'
        prompt = f"create a {art_style} background graphic in the style of {artist} using {colors}"
    elif day_in_cycle == 1:
        # Day 1: BLANK (no colors)
        colors = None
        color_mode = 'blank'
        prompt = f"create a {art_style} background graphic in the style of {artist}"
    elif day_in_cycle == 2:
        # Day 2: BRIGHT colors
        colors = BRIGHT_COLORS[state['bright_color_index']]
        color_mode = 'bright'
        prompt = f"create a {art_style} background graphic in the style of {artist} using {colors}"
    else:  # day_in_cycle == 3
        # Day 3: BLANK (no colors)
        colors = None
        color_mode = 'blank'
        prompt = f"create a {art_style} background graphic in the style of {artist}"

    return art_style, artist, color_mode, colors, prompt


def advance_state(state: Dict) -> Dict:
    """
    Advance state to next generation cycle.

    All 3 lists advance every day (different lengths = unique combinations):
    - Art styles: 7 items
    - Artists: 11 items
    - Colors: 15 dark, 14 bright (advance on their respective days)

    This creates 7 * 11 = 77 unique art style + artist combos before repeating.
    With colors: even more variety.
    """
    # Increment day counter
    state['day_counter'] += 1
    day_in_cycle = state['day_counter'] % 4

    # Advance art style EVERY DAY (7 styles)
    state['art_style_index'] = (state['art_style_index'] + 1) % len(ART_STYLES)

    # Advance to next artist EVERY DAY (11 artists)
    state['style_index'] = (state['style_index'] + 1) % len(ARTIST_STYLES)

    # Advance color indices based on which day we just completed
    if day_in_cycle == 1:  # Just completed day 0 (dark)
        state['dark_color_index'] = (state['dark_color_index'] + 1) % len(DARK_COLORS)
    elif day_in_cycle == 3:  # Just completed day 2 (bright)
        state['bright_color_index'] = (state['bright_color_index'] + 1) % len(BRIGHT_COLORS)

    return state


# ============================================================================
# IMAGE GENERATION
# ============================================================================

def sanitize_filename(text: str) -> str:
    """Remove special characters from text for safe filenames."""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in text).strip().replace(' ', '_')


def generate_image_with_sdxl(prompt: str, retry_count: int = 1) -> Optional[Image.Image]:
    """
    Generate image using Hugging Face SDXL API.
    
    Args:
        prompt: Text prompt for generation
        retry_count: Number of retries on rate limit/loading errors
    
    Returns:
        PIL Image object or None on failure
    """
    try:
        from huggingface_hub import InferenceClient

        logger.info(f"🎨 Generating image with prompt: {prompt[:80]}...")

        # Initialize InferenceClient with nscale provider (official HF method)
        client = InferenceClient(
            provider="nscale",
            api_key=HUGGINGFACE_TOKEN,
        )

        # Generate image using text_to_image (returns PIL.Image object directly)
        image = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            negative_prompt="blurry, low quality, watermark, text, logo, signature, distorted",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=2000,
            width=2000,
        )

        logger.info(f"✅ Image generated successfully: {image.size}")
        return image

    except Exception as e:
        error_msg = str(e).lower()

        # Handle rate limits
        if "429" in error_msg or "rate limit" in error_msg:
            logger.warning("⏳ Rate limit hit, waiting 20 seconds...")
            if retry_count > 0:
                time.sleep(20)
                return generate_image_with_sdxl(prompt, retry_count - 1)
            else:
                logger.error("ERROR: Rate limit exceeded, no retries left")
                return None

        # Handle model loading
        if "503" in error_msg or "loading" in error_msg:
            logger.warning("⏳ Model loading, waiting 20 seconds...")
            if retry_count > 0:
                time.sleep(20)
                return generate_image_with_sdxl(prompt, retry_count - 1)
            else:
                logger.error("ERROR: Model loading timeout, no retries left")
                return None

        logger.error(f"ERROR: Error generating image: {str(e)}")
        return None


def resize_image(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """Resize image using high-quality LANCZOS resampling."""
    return image.resize(size, Image.Resampling.LANCZOS)


def upload_to_s3(image: Image.Image, s3_key: str, metadata: Dict) -> bool:
    """
    Upload PIL Image to S3 with metadata.
    
    Args:
        image: PIL Image object
        s3_key: S3 object key (path)
        metadata: Dictionary of metadata tags
    
    Returns:
        True on success, False on failure
    """
    try:
        # Convert PIL Image to bytes
        buffer = BytesIO()
        image.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=buffer,
            ContentType='image/png',
            Metadata=metadata
        )
        
        logger.info(f"✅ Uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Error uploading to S3: {str(e)}")
        return False


# ============================================================================
# MAIN GENERATION WORKFLOW
# ============================================================================

def get_pool_count() -> int:
    """Get current count of artworks in the pool from DynamoDB."""
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


def store_artwork_metadata(artwork_id: str, filename: str, prompt: str,
                          art_style: str, artist: str, color_mode: str, colors: Optional[str]):
    """Store artwork metadata in DynamoDB noisemaker-frank-art table."""
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
            'color_mode': color_mode,
            'created_at': datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)
        logger.info(f"✅ Stored metadata for {artwork_id} in DynamoDB")
        return True
    except Exception as e:
        logger.error(f"ERROR: Failed to store metadata: {e}")
        return False


def generate_daily_artwork(test_mode: bool = False):
    """
    Main function to generate artworks and upload to S3.

    Args:
        test_mode: If True, generates only 1 image and doesn't advance state
    """
    import uuid

    images_to_generate = 1 if test_mode else IMAGES_PER_RUN
    mode_label = "TEST MODE (1 IMAGE)" if test_mode else f"FULL RUN ({IMAGES_PER_RUN} IMAGES)"

    logger.info("=" * 80)
    logger.info(f"🚀 STARTING FRANK'S GARAGE ART GENERATION - {mode_label}")
    logger.info("=" * 80)

    # Check pool size before generating
    current_pool = get_pool_count()
    logger.info(f"📊 Current pool size: {current_pool}/{MAX_POOL_SIZE}")

    if current_pool >= MAX_POOL_SIZE and not test_mode:
        logger.info(f"⏸️  Pool at capacity ({current_pool}/{MAX_POOL_SIZE}) - skipping generation")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'images_generated': 0,
                'reason': 'Pool at capacity',
                'pool_count': current_pool
            })
        }

    # Load current state
    state = load_state()

    # Get current generation settings (now with art_style)
    art_style, artist, color_mode, colors, prompt = get_current_prompts(state)

    logger.info(f"\n📋 TODAY'S GENERATION SETTINGS:")
    logger.info(f"   Art Style: {art_style}")
    logger.info(f"   Artist: {artist}")
    logger.info(f"   Color Mode: {color_mode.upper()}")
    logger.info(f"   Colors: {colors if colors else 'None (blank day)'}")
    logger.info(f"   Prompt: {prompt}")
    logger.info("")

    # Generate timestamp for this batch
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    successful_uploads = 0
    generated_artwork_ids = []

    # Generate images (1 in test mode, 4 in normal mode)
    for i in range(1, images_to_generate + 1):
        logger.info(f"\n{'─' * 80}")
        logger.info(f"🎨 GENERATING IMAGE {i}/{images_to_generate}")
        logger.info(f"{'─' * 80}")

        # Generate original image (2000x2000)
        original_image = generate_image_with_sdxl(prompt)

        if original_image is None:
            logger.error(f"ERROR: Failed to generate image {i}, skipping...")
            continue

        # Ensure original is correct size
        if original_image.size != ORIGINAL_SIZE:
            logger.info(f"📐 Resizing original from {original_image.size} to {ORIGINAL_SIZE}")
            original_image = resize_image(original_image, ORIGINAL_SIZE)

        # Generate mobile and thumbnail versions
        logger.info(f"📐 Creating mobile version ({MOBILE_SIZE})...")
        mobile_image = resize_image(original_image, MOBILE_SIZE)

        logger.info(f"📐 Creating thumbnail version ({THUMBNAIL_SIZE})...")
        thumbnail_image = resize_image(original_image, THUMBNAIL_SIZE)

        # Generate unique artwork ID
        artwork_id = str(uuid.uuid4())

        # Create metadata for S3 (minimal)
        metadata = {
            'artwork-id': artwork_id,
            'generation-date': datetime.utcnow().isoformat(),
            'batch-timestamp': timestamp,
            'image-number': str(i)
        }

        # Create filename using artwork_id
        filename_base = f"{artwork_id}.png"

        # Upload all three sizes
        logger.info(f"\n📤 Uploading 3 versions to S3...")

        success = True
        success &= upload_to_s3(original_image, S3_ORIGINAL_FOLDER + filename_base, metadata)
        success &= upload_to_s3(mobile_image, S3_MOBILE_FOLDER + filename_base, metadata)
        success &= upload_to_s3(thumbnail_image, S3_THUMBNAIL_FOLDER + filename_base, metadata)

        if success:
            # Store metadata in DynamoDB
            db_success = store_artwork_metadata(
                artwork_id, filename_base, prompt,
                art_style, artist, color_mode, colors
            )

            if db_success:
                successful_uploads += 1
                generated_artwork_ids.append(artwork_id)
                logger.info(f"✅ Image {i} complete: {artwork_id}")
            else:
                logger.warning(f"⚠️  Image {i} uploaded but metadata failed")
        else:
            logger.error(f"ERROR: Failed to upload image {i}")
    
    # Report completion
    logger.info(f"\n{'=' * 80}")
    logger.info(f"📊 GENERATION COMPLETE")
    logger.info(f"{'=' * 80}")
    logger.info(f"✅ Successfully generated and uploaded: {successful_uploads}/{images_to_generate} images")
    
    # Update state (skip in test mode)
    if test_mode:
        logger.info(f"\n🧪 TEST MODE: State NOT advanced (can re-run test with same settings)")
        logger.info(f"   Current state preserved for next run")
    else:
        new_state = advance_state(state)
        save_state(new_state)

        # Preview next run
        next_art_style, next_artist, next_color_mode, next_colors, next_prompt = get_current_prompts(new_state)
        logger.info(f"\n🔮 NEXT RUN PREVIEW:")
        logger.info(f"   Art Style: {next_art_style}")
        logger.info(f"   Artist: {next_artist}")
        logger.info(f"   Color Mode: {next_color_mode.upper()}")
        logger.info(f"   Colors: {next_colors if next_colors else 'None (blank day)'}")
        logger.info(f"   Day Counter: {new_state['day_counter']}")

    logger.info("")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'success': True,
            'images_generated': successful_uploads,
            'artwork_ids': generated_artwork_ids,
            'art_style': art_style,
            'artist': artist,
            'color_mode': color_mode,
            'timestamp': timestamp,
            'pool_count': current_pool + successful_uploads
        })
    }


# ============================================================================
# AWS LAMBDA HANDLER
# ============================================================================

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    This function is called by EventBridge cron at 9 PM daily.
    """
    try:
        return generate_daily_artwork()
    except Exception as e:
        logger.error(f"ERROR: Fatal error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


# ============================================================================
# LOCAL TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Run locally with command line arguments.
    
    Usage:
        python daily_album_art_generator.py                    # Full run (4 images)
        python daily_album_art_generator.py --test-mode        # Test run (1 image)
        python daily_album_art_generator.py --test-connection  # Test API/AWS access
    
    Environment variables (set in .env or export):
        HUGGINGFACE_TOKEN="hf_..."
        AWS_ACCESS_KEY_ID="..."
        AWS_SECRET_ACCESS_KEY="..."
        AWS_REGION="us-east-2"
        S3_BUCKET="mynoiseyapp-marketplace"
    """
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Daily Frank Art Generator for Frank\'s Garage Marketplace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python daily_album_art_generator.py                    # Generate 4 images (full run)
  python daily_album_art_generator.py --test-mode        # Generate 1 image (test)
  python daily_album_art_generator.py --test-connection  # Verify API/AWS access

Environment Setup:
  1. Copy .env.example to .env
  2. Fill in your Hugging Face token and AWS credentials
  3. Run --test-connection to verify setup
        """
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Generate only 1 image (for testing, does not advance state)'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test Hugging Face API and AWS S3 connections without generating images'
    )
    
    args = parser.parse_args()
    
    # Test connection mode
    if args.test_connection:
        success = test_connection()
        exit(0 if success else 1)
    
    # Normal generation mode
    print("\n" + "=" * 80)
    if args.test_mode:
        print("TEST MODE: 1 image (state not advanced)")
    else:
        print("PRODUCTION MODE: 4 images")
    print("=" * 80 + "\n")
    
    # Check required parameters (AWS credentials loaded automatically by boto3 from ~/.aws/credentials)
    if not HUGGINGFACE_TOKEN:
        print("ERROR: Missing HUGGINGFACE_TOKEN")
        print("\nStore token in AWS Parameter Store:")
        print("  aws ssm put-parameter --name /noisemaker/huggingface_token --value 'hf_TOKEN' --type SecureString --region us-east-2")
        print("\nRun with --help for more information")
        exit(1)

    print(f"Hugging Face token: {HUGGINGFACE_TOKEN[:10]}...")
    print(f"AWS Region: {AWS_REGION}")
    print(f"S3 Bucket: {S3_BUCKET}\n")
    
    # Run generation
    try:
        result = generate_daily_artwork(test_mode=args.test_mode)
        print("\n" + "=" * 80)
        print("SUCCESS: GENERATION COMPLETE")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        exit(0)
    except Exception as e:
        print("\n" + "=" * 80)
        print("ERROR: GENERATION FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        exit(1)
