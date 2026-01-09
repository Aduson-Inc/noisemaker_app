"""
Marketplace Module - Frank's Garage
Manages the Frank Art marketplace system for AI-generated artwork.

IMPORTANT: Frank Art is SEPARATE from album artwork collected from user songs.
- Frank Art = AI-generated art sold in the marketplace
- Album Art = Artwork from user's Spotify songs (separate system)
"""

from .frank_art_manager import FrankArtManager, get_frank_art_manager
from .artwork_analytics import ArtworkAnalyticsManager
from .frank_art_integration import FrankArtIntegration

# Initialize singleton instances (lazy loaded)
frank_art_manager = get_frank_art_manager()
analytics_manager = ArtworkAnalyticsManager()
frank_art_integration = FrankArtIntegration()

# Backwards compatibility aliases
artwork_manager = frank_art_manager
album_artwork_integration = frank_art_integration
AlbumArtworkManager = FrankArtManager
AlbumArtworkIntegration = FrankArtIntegration

__all__ = [
    # New names
    'frank_art_manager',
    'analytics_manager',
    'frank_art_integration',
    'FrankArtManager',
    'ArtworkAnalyticsManager',
    'FrankArtIntegration',
    'get_frank_art_manager',
    # Backwards compatibility
    'artwork_manager',
    'album_artwork_integration',
    'AlbumArtworkManager',
    'AlbumArtworkIntegration',
]
