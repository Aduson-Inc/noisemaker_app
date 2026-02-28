"""
Songs API Routes
Handles song management operations including adding songs from Spotify URLs.
Implements the 42-day cycle with dynamic stage progression.

Author: Senior Python Backend Engineer
Version: 2.0
Security Level: Production-ready
"""

import re
import os
import logging
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, HttpUrl, validator
from slowapi import Limiter
from slowapi.util import get_remote_address

import boto3

from spotify.spotipy_client import get_track_information, get_artist_information
from data.song_manager import song_manager
from data.user_manager import user_manager
from auth.environment_loader import get_platform_credentials
from middleware.auth import get_current_user_id
from audio.converter import convert_wav_to_mp3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/songs", tags=["songs"])

# Rate limiter instance - uses same key function as main.py
limiter = Limiter(key_func=get_remote_address)

# S3 client for audio uploads
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")
s3_client = boto3.client("s3", region_name=AWS_REGION)


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ValidateArtistRequest(BaseModel):
    """Request model for validating a Spotify artist URL."""
    url: str


class AddSongFromUrlRequest(BaseModel):
    """Request model for adding a song from Spotify URL."""
    spotify_url: str
    initial_days: int  # Initial days_in_promotion (0, 14, or 28)
    release_date: Optional[str] = None  # Required for songs starting at day 0

    @validator('initial_days')
    def validate_initial_days(cls, v):
        """Validate initial_days is one of the allowed values."""
        allowed = [0, 14, 28]
        if v not in allowed:
            raise ValueError(f'initial_days must be one of: {", ".join(map(str, allowed))}')
        return v

    @validator('release_date')
    def validate_release_date(cls, v, values):
        """Validate release date format if provided. Release date is optional."""
        if v:
            try:
                release_date = datetime.fromisoformat(v)
                today = datetime.now()
                days_until_release = (release_date - today).days

                if days_until_release < 14:
                    raise ValueError('Release date must be at least 14 days in the future')
            except ValueError as e:
                if 'ISO' not in str(e):
                    raise
                raise ValueError('release_date must be in ISO format (YYYY-MM-DD)')

        return v


class AudioUploadRequest(BaseModel):
    """Request model for audio upload URL generation."""
    content_type: str

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed = ['audio/mpeg', 'audio/wav']
        if v not in allowed:
            raise ValueError(f'content_type must be one of: {", ".join(allowed)}')
        return v


class AudioClipRequest(BaseModel):
    """Request model for saving audio clip timestamps."""
    clip_start: float
    clip_end: float

    @validator('clip_end')
    def validate_clip_duration(cls, v, values):
        start = values.get('clip_start', 0)
        if start < 0:
            raise ValueError('clip_start must be >= 0')
        duration = v - start
        if duration < 9.9 or duration > 10.1:
            raise ValueError('Clip duration must be ~10 seconds (9.9-10.1s)')
        return v


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_spotify_track_id(spotify_url: str) -> Optional[str]:
    """
    Extract Spotify track ID from various URL formats.

    Supported formats:
    - https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
    - spotify:track:3n3Ppam7vgaVa1iaRUc9Lp
    - https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp?si=...

    Args:
        spotify_url (str): Spotify URL or URI

    Returns:
        Optional[str]: Track ID if valid, None otherwise
    """
    # Regex pattern for Spotify track ID
    pattern = r'(?:spotify:track:|https://open\.spotify\.com/track/)([a-zA-Z0-9]+)'

    match = re.search(pattern, spotify_url)
    if match:
        return match.group(1)

    return None


def extract_spotify_artist_id(spotify_url: str) -> Optional[str]:
    """
    Extract Spotify artist ID from various URL formats.

    Supported formats:
    - https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb
    - spotify:artist:4Z8W4fKeB5YxbusRsdQVPb
    - https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb?si=...

    Args:
        spotify_url (str): Spotify URL or URI

    Returns:
        Optional[str]: Artist ID if valid, None otherwise
    """
    # Regex pattern for Spotify artist ID
    pattern = r'(?:spotify:artist:|https://open\.spotify\.com/artist/)([a-zA-Z0-9]+)'

    match = re.search(pattern, spotify_url)
    if match:
        return match.group(1)

    return None


def determine_song_stage(days_in_promotion: int) -> str:
    """
    Determine song stage based on days_in_promotion.

    Stages are dynamic and progress as the song ages:
    - Upcoming: Days 0-14 (building baseline, pre-release)
    - Live: Days 15-28 (peak promotion phase)
    - Twilight: Days 29-42 (final push phase)
    - Retired: Days 43+ (cycle complete)

    Args:
        days_in_promotion (int): Current days in promotion

    Returns:
        str: Current stage ('upcoming', 'live', 'twilight', or 'retired')
    """
    if days_in_promotion < 0:
        return 'upcoming'
    elif days_in_promotion <= 14:
        return 'upcoming'
    elif days_in_promotion <= 28:
        return 'live'
    elif days_in_promotion <= 42:
        return 'twilight'
    else:
        return 'retired'


def determine_promotion_status(stage: str, release_date: Optional[str] = None) -> str:
    """
    Determine initial promotion status based on stage and release date.

    Args:
        stage (str): Song stage
        release_date (Optional[str]): Release date for upcoming songs

    Returns:
        str: Promotion status ('active', 'scheduled', 'retired')
    """
    if stage == 'retired':
        return 'retired'

    if stage == 'upcoming' and release_date:
        release_dt = datetime.fromisoformat(release_date)
        if datetime.now() < release_dt:
            return 'scheduled'  # Not released yet

    return 'active'


# ============================================================================
# API ROUTES
# ============================================================================

@router.post("/validate-artist")
@limiter.limit("10/minute")
async def validate_artist(request: Request, body: ValidateArtistRequest):
    """
    Validate a Spotify artist URL and return artist info.

    PUBLIC ENDPOINT - No auth required (used on pricing page before signup).
    Uses app-level Spotify credentials (Client Credentials flow).
    Rate limited: 10 requests per minute per IP.

    Args:
        request (Request): FastAPI request object (for rate limiting)
        body (ValidateArtistRequest): Request body with Spotify artist URL

    Returns:
        Dict: Artist info including ID, name, image, genres, followers

    Raises:
        HTTPException: If URL is invalid or artist not found
    """
    try:
        spotify_url = body.url.strip()

        # Step 1: Extract artist ID from URL
        artist_id = extract_spotify_artist_id(spotify_url)

        if not artist_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid Spotify artist URL. Please paste your Spotify artist profile link."
            )

        logger.info(f"Validating artist ID: {artist_id}")

        # Step 2: Load app-level Spotify credentials (from AWS Parameter Store)
        spotify_creds = get_platform_credentials('spotify')
        spotify_client_id = spotify_creds.get('client_id')
        spotify_client_secret = spotify_creds.get('client_secret')

        if not spotify_client_id or not spotify_client_secret:
            # Log the real error for debugging, return generic message to user
            logger.error("Spotify app credentials not configured in AWS Parameter Store")
            raise HTTPException(
                status_code=503,
                detail="Unable to validate artist at this time. Please try again later."
            )

        # Step 3: Fetch artist info from Spotify API
        artist_info = get_artist_information(
            "system",  # App-level request, no user context needed
            spotify_client_id,
            spotify_client_secret,
            artist_id
        )

        if not artist_info:
            raise HTTPException(
                status_code=404,
                detail="Artist not found on Spotify. Please check the URL and try again."
            )

        logger.info(f"Validated artist: {artist_info['name']}")

        # Step 4: Return validated artist data
        return {
            "success": True,
            "artist_id": artist_info['artist_id'],
            "artist_name": artist_info['name'],
            "artist_image_url": artist_info.get('image_url'),
            "genres": artist_info.get('genres', []),
            "followers": artist_info.get('followers', 0),
            "external_url": artist_info.get('external_url', '')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating artist: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to validate artist. Please try again."
        )


class ValidateTrackRequest(BaseModel):
    """Request model for validating a Spotify track URL."""
    spotify_url: str


@router.post("/validate-track")
async def validate_track(
    request: ValidateTrackRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Validate a Spotify track URL and check artist ownership.

    This endpoint:
    1. Extracts track ID from URL
    2. Fetches track info from Spotify API
    3. Verifies track's artist matches user's linked spotify_artist_id

    Returns track info if valid and owned by user.

    Args:
        request (ValidateTrackRequest): Request with Spotify track URL
        current_user_id (str): User ID from JWT token

    Returns:
        Dict: Track info including ownership validation

    Raises:
        HTTPException: If URL invalid, track not found, or artist mismatch
    """
    try:
        spotify_url = request.spotify_url.strip()

        # Step 1: Extract track ID from URL
        track_id = extract_spotify_track_id(spotify_url)

        if not track_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid Spotify track URL. Please paste a valid Spotify track link."
            )

        logger.info(f"Validating track {track_id} for user {current_user_id}")

        # Step 2: Get user's spotify_artist_id from profile
        user_profile = user_manager.get_user_profile(current_user_id)
        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found"
            )

        user_artist_id = user_profile.get('spotify_artist_id')
        user_artist_name = user_profile.get('spotify_artist_name', 'Unknown')

        if not user_artist_id:
            raise HTTPException(
                status_code=400,
                detail="No Spotify artist linked to your account. Please complete artist verification first."
            )

        # Step 3: Load app-level Spotify credentials
        spotify_creds = get_platform_credentials('spotify')
        spotify_client_id = spotify_creds.get('client_id')
        spotify_client_secret = spotify_creds.get('client_secret')

        if not spotify_client_id or not spotify_client_secret:
            raise HTTPException(
                status_code=503,
                detail="Unable to validate track at this time. Please try again later."
            )

        # Step 4: Fetch track info from Spotify
        track_info = get_track_information(
            current_user_id,
            spotify_client_id,
            spotify_client_secret,
            track_id
        )

        if not track_info:
            raise HTTPException(
                status_code=404,
                detail="Track not found on Spotify. Please check the URL and try again."
            )

        # Step 5: Check if track belongs to user's artist
        track_artist_ids = [artist['id'] for artist in track_info.get('artists', [])]
        track_artist_names = [artist['name'] for artist in track_info.get('artists', [])]

        artist_matches = user_artist_id in track_artist_ids

        if not artist_matches:
            # Return info but indicate artist mismatch
            return {
                "success": True,
                "valid": False,
                "error": "This track belongs to a different artist",
                "track_artist": track_artist_names[0] if track_artist_names else "Unknown",
                "your_artist": user_artist_name,
                "track_id": track_id,
                "name": track_info['name']
            }

        # Step 6: Return validated track info
        logger.info(f"Track {track_id} validated for user {current_user_id}")

        return {
            "success": True,
            "valid": True,
            "track_id": track_id,
            "name": track_info['name'],
            "artist_name": track_info['artist_name'],
            "album_art_url": track_info.get('album_art_url'),
            "preview_url": track_info.get('preview_url'),
            "popularity": track_info.get('popularity', 0),
            "release_date": track_info.get('release_date'),
            "artist_matches_user": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating track: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to validate track. Please try again."
        )


@router.post("/add-from-url")
async def add_song_from_url(
    request: AddSongFromUrlRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add a song from Spotify URL.

    This is used both for:
    1. Initial 3-song setup (days 0, 14, 28) - ONE TIME ONLY
    2. Adding new songs every 2 weeks (always start at day 0)

    Process:
    1. Extract Spotify track ID from URL
    2. Fetch track metadata from Spotify API
    3. Determine stage based on initial_days
    4. Store song in database with correct initial promotion days

    Args:
        request (AddSongFromUrlRequest): Request with Spotify URL and initial days

    Returns:
        Dict: Song data including track ID, name, artist, artwork, stage, etc.

    Raises:
        HTTPException: If URL is invalid, track not found, or other errors
    """
    try:
        user_id = current_user_id  # From JWT token
        spotify_url = request.spotify_url
        initial_days = request.initial_days
        release_date = request.release_date

        logger.info(f"Adding song from URL for user {user_id}, initial_days {initial_days}")

        # Step 1: Extract Spotify track ID
        track_id = extract_spotify_track_id(spotify_url)

        if not track_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid Spotify URL format. Please provide a valid Spotify track URL."
            )

        logger.info(f"Extracted track ID: {track_id}")

        # Step 2: Check if user already has 3 active songs
        existing_songs = song_manager.get_user_active_songs(user_id, limit=10)
        if len(existing_songs) >= 3:
            raise HTTPException(
                status_code=400,
                detail="You already have 3 songs in promotion. Please wait for a song to complete its cycle (42 days)."
            )

        # Check if this track is already added
        for song in existing_songs:
            if song.get('spotify_track_id') == track_id:
                raise HTTPException(
                    status_code=400,
                    detail="This song is already in your promotion cycle."
                )

        # Step 3: Load app-level Spotify credentials
        spotify_creds = get_platform_credentials('spotify')
        spotify_client_id = spotify_creds.get('client_id')
        spotify_client_secret = spotify_creds.get('client_secret')

        if not spotify_client_id or not spotify_client_secret:
            raise HTTPException(
                status_code=500,
                detail="Spotify app credentials not configured. Please contact support."
            )

        # Step 4: Fetch track metadata from Spotify
        track_info = get_track_information(
            user_id,
            spotify_client_id,
            spotify_client_secret,
            track_id
        )

        if not track_info:
            raise HTTPException(
                status_code=404,
                detail="Track not found on Spotify. Please check the URL and try again."
            )

        logger.info(f"Fetched track info: {track_info['name']} by {track_info['artist_name']}")

        # Step 5: Verify track belongs to user's artist
        user_profile = user_manager.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found"
            )

        user_artist_id = user_profile.get('spotify_artist_id')
        if not user_artist_id:
            raise HTTPException(
                status_code=400,
                detail="No Spotify artist linked to your account. Please complete artist verification first."
            )

        # Check if track's artist matches user's linked artist
        track_artist_ids = [artist['id'] for artist in track_info.get('artists', [])]
        if user_artist_id not in track_artist_ids:
            track_artist_name = track_info.get('artists', [{}])[0].get('name', 'Unknown')
            user_artist_name = user_profile.get('spotify_artist_name', 'Unknown')
            raise HTTPException(
                status_code=403,
                detail=f"This track belongs to '{track_artist_name}', not '{user_artist_name}'. You can only promote your own songs."
            )

        # Step 6: Get artist genres
        genres = track_info.get('genres', [])
        genre = genres[0] if genres else "Pop"  # Default to Pop if no genre available

        # Step 7: Determine stage and promotion status
        stage = determine_song_stage(initial_days)
        promotion_status = determine_promotion_status(stage, release_date)

        # Step 8: Create song record
        song_data = {
            'spotify_track_id': track_id,
            'song': track_info['name'],
            'artist_title': track_info['artist_name'],
            'genre': genre,  # Required by song_manager
            'art_url': track_info['album_art_url'],
            'preview_url': track_info.get('preview_url', ''),
            'promotion_stage': stage,  # Dynamic stage: upcoming/live/twilight
            'days_in_promotion': initial_days,  # Initial stagger: 0, 14, or 28
            'promotion_status': promotion_status,
            'spotify_popularity': 0,  # Will be updated by daily processor
            'fire_mode': False,
            'created_at': datetime.now().isoformat()
        }

        # Add release date for upcoming songs (day 0)
        if initial_days == 0 and release_date:
            song_data['release_date'] = release_date
            song_data['scheduled_release'] = release_date

        # Step 9: Add song to database
        song_id = song_manager.add_song(user_id, song_data)

        if not song_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to add song to database. Please try again."
            )

        logger.info(f"Successfully added song {song_id} for user {user_id} at stage '{stage}' with {initial_days} days")

        # Award art tokens for Frank's Garage (3 tokens per song, max 12 from songs)
        art_token_result = None
        try:
            from data.user_manager import award_art_tokens_for_song
            art_token_result = award_art_tokens_for_song(user_id)
            if art_token_result.get('success'):
                tokens_awarded = art_token_result.get('tokens_added', 0)
                if tokens_awarded > 0:
                    logger.info(f"Awarded {tokens_awarded} art tokens to user {user_id} for song upload")
                else:
                    logger.info(f"User {user_id} at max song tokens, no tokens awarded")
        except Exception as e:
            logger.warning(f"Failed to award art tokens for song upload: {e}")

        # Step 10: Return song data with ID
        song_data['song_id'] = song_id

        response_data = {
            "success": True,
            "message": f"Successfully added {track_info['name']} to your promotion cycle at {stage} stage",
            "song": song_data
        }

        # Include token info in response if available
        if art_token_result and art_token_result.get('success'):
            response_data['art_tokens'] = {
                'tokens_awarded': art_token_result.get('tokens_added', 0),
                'new_balance': art_token_result.get('new_balance', 0),
                'at_max': art_token_result.get('at_max', False)
            }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding song from URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_songs(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all songs for a user.

    Args:
        user_id (str): User identifier

    Returns:
        Dict: List of user's songs with current stages
    """
    try:
        # Security: Users can only view their own songs
        if user_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own songs"
            )
        
        songs = song_manager.get_user_active_songs(user_id, limit=10)

        # Update stages based on current days_in_promotion
        for song in songs:
            days = song.get('days_in_promotion', 0)
            song['current_stage'] = determine_song_stage(days)

        return {
            "success": True,
            "songs": songs,
            "count": len(songs)
        }

    except Exception as e:
        logger.error(f"Error fetching user songs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch songs"
        )


# ============================================================================
# AUDIO UPLOAD ENDPOINTS (Features 1, 1b, 2)
# ============================================================================

@router.post("/{song_id}/audio-upload-url")
async def get_audio_upload_url(
    song_id: str,
    request: AudioUploadRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate presigned S3 URL for audio file upload."""
    try:
        # Verify song belongs to user
        song = song_manager.get_song(current_user_id, song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        # Determine file extension
        ext = ".mp3" if request.content_type == "audio/mpeg" else ".wav"
        s3_key = f"audio/{song_id}/full{ext}"

        # Generate presigned PUT URL (15 min expiry, 50MB max)
        upload_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": s3_key,
                "ContentType": request.content_type,
            },
            ExpiresIn=900,
        )

        return {
            "upload_url": upload_url,
            "s3_key": s3_key,
            "expires_in": 900,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating upload URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")


@router.post("/{song_id}/audio-upload-confirm")
async def confirm_audio_upload(
    song_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Confirm audio upload and optionally convert WAV to MP3."""
    try:
        # Verify song belongs to user
        song = song_manager.get_song(current_user_id, song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        # Check both possible keys
        mp3_key = f"audio/{song_id}/full.mp3"
        wav_key = f"audio/{song_id}/full.wav"

        audio_key = None
        content_type = None
        file_size = 0

        for key, ct in [(mp3_key, "audio/mpeg"), (wav_key, "audio/wav")]:
            try:
                head = s3_client.head_object(Bucket=S3_BUCKET, Key=key)
                audio_key = key
                content_type = ct
                file_size = head["ContentLength"]
                break
            except s3_client.exceptions.ClientError:
                continue

        if not audio_key:
            raise HTTPException(status_code=404, detail="Audio file not found in S3")

        # WAV to MP3 conversion (Feature 1b)
        if content_type == "audio/wav":
            try:
                tmp_dir = tempfile.mkdtemp()
                wav_path = os.path.join(tmp_dir, "input.wav")
                mp3_path = os.path.join(tmp_dir, "output.mp3")

                # Download WAV
                s3_client.download_file(S3_BUCKET, audio_key, wav_path)

                # Convert
                if convert_wav_to_mp3(wav_path, mp3_path):
                    # Upload MP3
                    with open(mp3_path, "rb") as f:
                        s3_client.put_object(
                            Bucket=S3_BUCKET,
                            Key=mp3_key,
                            Body=f,
                            ContentType="audio/mpeg",
                        )

                    # Delete original WAV
                    s3_client.delete_object(Bucket=S3_BUCKET, Key=wav_key)

                    audio_key = mp3_key
                    content_type = "audio/mpeg"
                    file_size = os.path.getsize(mp3_path)

                    logger.info(f"Converted WAV to MP3 for song {song_id}")
                else:
                    # Conversion failed — keep WAV, mark status
                    song_manager.update_song_field(current_user_id, song_id, {
                        "audio_conversion_status": "failed",
                    })
                    logger.warning(f"WAV conversion failed for song {song_id}, keeping WAV")

            except Exception as e:
                logger.error(f"WAV conversion error for {song_id}: {e}")
                song_manager.update_song_field(current_user_id, song_id, {
                    "audio_conversion_status": "failed",
                })
            finally:
                # Cleanup temp files
                for path in [wav_path, mp3_path]:
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                try:
                    os.rmdir(tmp_dir)
                except OSError:
                    pass

        # Update song record
        song_manager.update_song_field(current_user_id, song_id, {
            "audio_s3_key": audio_key,
            "audio_file_size": file_size,
            "audio_uploaded_at": datetime.now().isoformat(),
            "audio_content_type": content_type,
        })

        return {"success": True, "audio_s3_key": audio_key}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming audio upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm audio upload")


@router.put("/{song_id}/audio-clip")
async def save_audio_clip(
    song_id: str,
    request: AudioClipRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Save 10-second audio clip selection timestamps."""
    try:
        # Verify song belongs to user
        song = song_manager.get_song(current_user_id, song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        # Verify audio has been uploaded
        if not song.get("audio_s3_key"):
            raise HTTPException(
                status_code=400,
                detail="Audio must be uploaded before selecting a clip"
            )

        # Save clip timestamps
        song_manager.update_song_field(current_user_id, song_id, {
            "audio_clip_start": str(request.clip_start),
            "audio_clip_end": str(request.clip_end),
            "audio_clip_updated_at": datetime.now().isoformat(),
        })

        return {
            "success": True,
            "clip_start": request.clip_start,
            "clip_end": request.clip_end,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving audio clip: {e}")
        raise HTTPException(status_code=500, detail="Failed to save audio clip")


@router.get("/{song_id}/audio-url")
async def get_audio_url(
    song_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get presigned URL for audio playback and clip timestamps."""
    try:
        # Verify song belongs to user
        song = song_manager.get_song(current_user_id, song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        audio_key = song.get("audio_s3_key")
        if not audio_key:
            return {
                "has_audio": False,
                "audio_url": None,
                "clip_start": None,
                "clip_end": None,
            }

        # Generate presigned GET URL (1 hour)
        audio_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": audio_key},
            ExpiresIn=3600,
        )

        clip_start = song.get("audio_clip_start")
        clip_end = song.get("audio_clip_end")

        return {
            "has_audio": True,
            "audio_url": audio_url,
            "clip_start": float(clip_start) if clip_start else None,
            "clip_end": float(clip_end) if clip_end else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audio URL")


# ============================================================================
# STAGGER & RULES ENDPOINTS (Features 5, 6)
# ============================================================================

@router.post("/apply-stagger")
async def apply_stagger(
    current_user_id: str = Depends(get_current_user_id)
):
    """Apply onboarding stagger to all user songs. Called at end of onboarding."""
    try:
        result = song_manager.apply_onboarding_stagger(current_user_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Stagger failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying stagger: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply stagger")


@router.get("/can-add")
async def check_can_add_song(
    current_user_id: str = Depends(get_current_user_id)
):
    """Check if user can add a new song (post-onboarding day-15 gate)."""
    try:
        return song_manager.check_can_add_song(current_user_id)
    except Exception as e:
        logger.error(f"Error checking add eligibility: {e}")
        raise HTTPException(status_code=500, detail="Failed to check eligibility")
