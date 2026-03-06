"""
NOiSEMaKER RAG Pipeline
========================

Builds rich context for caption generation by retrieving artist data
from existing DynamoDB tables.

Phase 1 (Current): Song metadata enrichment
    - Queries noisemaker-songs for genre, popularity, fire mode status
    - Queries noisemaker-baselines for popularity history
    - Queries noisemaker-posting-history for past caption patterns
    - Returns a context string injected into the caption LLM prompt

Phase 2 (Future): Chatbot + Vector DB
    - Placeholder for when user-facing chatbot is built
    - Will query vector DB for artist personality/preferences from chat history
    - See VECTOR_DB_CONFIG placeholder below
"""

import logging
import os
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")

_dynamodb = None


def _get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return _dynamodb


# =============================================================================
# PHASE 2 PLACEHOLDER — Vector DB for Chatbot History
# =============================================================================

# PLACEHOLDER — not implemented until chatbot exists
# Grep for "PLACEHOLDER" to find all undecided integrations
VECTOR_DB_CONFIG = {
    "provider": "PLACEHOLDER",      # e.g., "pinecone", "chromadb", "pgvector"
    "collection": "artist_vibes",
    "ssm_param": "/noisemaker/vector_db_api_key",  # TO BE CREATED
}


async def retrieve_artist_vibe(user_id: str) -> str:
    """Retrieve chatbot conversation history for caption personalization.

    PLACEHOLDER: When chatbot exists, this will query the vector DB
    for the artist's personality traits, genre preferences, and
    marketing style from their chat history.

    Returns:
        Context string from chat history, or empty string if not available
    """
    if VECTOR_DB_CONFIG["provider"] == "PLACEHOLDER":
        logger.info("Vector DB is PLACEHOLDER — no chatbot context available")
        return ""

    # Future vector DB query implementation goes here
    return ""


# =============================================================================
# PHASE 1 — Song Metadata Enrichment (ACTIVE)
# =============================================================================

def build_caption_context(user_id: str, song_data: dict) -> str:
    """Build rich context string for caption generation from existing data.

    Gathers data from multiple DynamoDB tables to give the caption LLM
    detailed context about the artist, song, and promotion state.

    Args:
        user_id: The user's ID
        song_data: Dict with song_id, song_name, artist_name, genre, etc.

    Returns:
        Context string ready for injection into caption LLM prompt.
        Returns minimal context on any failure (never raises).
    """
    parts = []

    # Core song info (always available from song_data)
    artist = song_data.get("artist_name", "Unknown Artist")
    title = song_data.get("song_name", "Unknown Track")
    genre = song_data.get("genre", "Music")
    parts.append(f"Artist: {artist}")
    parts.append(f"Track: {title}")
    parts.append(f"Genre: {genre}")

    # Promotion state
    day = song_data.get("day_in_promotion")
    if day is not None:
        parts.append(f"Day {day} of 42-day promotion cycle")

    stage = song_data.get("stage_of_promotion")
    if stage:
        parts.append(f"Promotion stage: {stage}")

    # Fire mode status
    fire_mode = song_data.get("fire_mode_active", False)
    if fire_mode:
        parts.append("FIRE MODE ACTIVE — song is trending, maximize urgency")

    # Spotify popularity
    popularity = song_data.get("song_popularity")
    if popularity is not None and int(popularity) > 0:
        parts.append(f"Spotify popularity score: {popularity}/100")

    # Enrich with data from other tables
    song_id = song_data.get("song_id", "")

    # Get popularity baseline/trend
    baseline_context = _get_baseline_context(user_id)
    if baseline_context:
        parts.append(baseline_context)

    # Get posting history patterns
    history_context = _get_posting_history_context(user_id)
    if history_context:
        parts.append(history_context)

    # Get all songs for genre spread
    genre_context = _get_genre_context(user_id, song_id)
    if genre_context:
        parts.append(genre_context)

    return "\n".join(parts)


# =============================================================================
# PRIVATE DATA FETCHERS
# =============================================================================

def _get_baseline_context(user_id: str) -> Optional[str]:
    """Fetch latest popularity baseline for trend context."""
    try:
        table = _get_dynamodb().Table("noisemaker-baselines")
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,  # newest first
            Limit=1,
        )
        items = response.get("Items", [])
        if not items:
            return None

        baseline = items[0]
        avg_pop = baseline.get("average_popularity")
        if avg_pop is not None and float(avg_pop) > 0:
            return f"Average popularity baseline: {avg_pop}"
        return None

    except Exception as e:
        logger.debug(f"Baseline fetch failed (non-critical): {e}")
        return None


def _get_posting_history_context(user_id: str) -> Optional[str]:
    """Fetch recent posting history for pattern awareness."""
    try:
        table = _get_dynamodb().Table("noisemaker-posting-history")
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=5,
        )
        items = response.get("Items", [])
        if not items:
            return None

        platforms_used = set()
        for item in items:
            platform = item.get("platform")
            if platform:
                platforms_used.add(platform)

        if platforms_used:
            return f"Recently posted to: {', '.join(sorted(platforms_used))}"
        return None

    except Exception as e:
        logger.debug(f"Posting history fetch failed (non-critical): {e}")
        return None


def _get_genre_context(user_id: str, current_song_id: str) -> Optional[str]:
    """Fetch all user songs to identify genre spread and catalog depth."""
    try:
        table = _get_dynamodb().Table("noisemaker-songs")
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
        )
        items = response.get("Items", [])
        if len(items) <= 1:
            return None

        genres = set()
        active_count = 0
        for item in items:
            genre = item.get("genre")
            if genre:
                genres.add(genre)
            status = item.get("status", "")
            if status == "active":
                active_count += 1

        parts = []
        if len(genres) > 1:
            parts.append(f"Artist genres: {', '.join(sorted(genres))}")
        if active_count > 1:
            parts.append(f"Active songs in promotion: {active_count}")

        return "; ".join(parts) if parts else None

    except Exception as e:
        logger.debug(f"Genre context fetch failed (non-critical): {e}")
        return None
