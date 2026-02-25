"""
OAuth Package
Factory + convenience functions that provide the same API as the old
platform_oauth_manager.py. All existing imports continue to work.
"""

import logging
from typing import Dict, Any, Optional

from .encryption import TokenEncryption
from .instagram import InstagramOAuth
from .facebook import FacebookOAuth
from .twitter import TwitterOAuth
from .tiktok import TikTokOAuth
from .youtube import YouTubeOAuth
from .reddit import RedditOAuth
from .discord import DiscordOAuth
from .threads import ThreadsOAuth

logger = logging.getLogger(__name__)

# Single shared encryptor instance
_encryptor = TokenEncryption()

# Platform handler registry — one instance per platform
PLATFORM_HANDLERS = {
    'instagram': InstagramOAuth(_encryptor),
    'facebook': FacebookOAuth(_encryptor),
    'twitter': TwitterOAuth(_encryptor),
    'tiktok': TikTokOAuth(_encryptor),
    'youtube': YouTubeOAuth(_encryptor),
    'reddit': RedditOAuth(_encryptor),
    'discord': DiscordOAuth(_encryptor),
    'threads': ThreadsOAuth(_encryptor),
}


class OAuthManager:
    """
    Facade that dispatches to platform-specific handlers.
    Drop-in replacement for the old PlatformOAuthManager class.
    Accepts 'platform' as a parameter and routes to the correct handler.
    """

    def _get_handler(self, platform: str):
        handler = PLATFORM_HANDLERS.get(platform)
        if not handler:
            raise ValueError(f"Unsupported platform: {platform}")
        return handler

    def initiate_oauth(self, user_id: str, platform: str,
                       redirect_uri: str) -> Dict[str, Any]:
        return self._get_handler(platform).initiate_oauth(user_id, redirect_uri)

    def handle_callback(self, user_id: str, platform: str, code: str,
                        state: str, redirect_uri: str) -> Dict[str, Any]:
        return self._get_handler(platform).handle_callback(
            user_id, code, state, redirect_uri
        )

    def get_user_token(self, user_id: str,
                       platform: str) -> Optional[Dict[str, Any]]:
        return self._get_handler(platform).get_user_token(user_id)

    def refresh_token(self, user_id: str, platform: str) -> bool:
        return self._get_handler(platform).refresh_token(user_id)

    def revoke_connection(self, user_id: str, platform: str) -> bool:
        return self._get_handler(platform).revoke_connection(user_id)

    def add_discord_webhook(self, user_id: str, webhook_url: str,
                            server_name: str = '') -> Dict[str, Any]:
        return self._get_handler('discord').add_webhook(
            user_id, webhook_url, server_name
        )

    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get connection status for all platforms."""
        status = {}
        for platform_name, handler in PLATFORM_HANDLERS.items():
            connection = handler._get_connection(user_id)
            if connection:
                status[platform_name] = {
                    'connected': True,
                    'username': connection.get('platform_username', ''),
                    'account_type': connection.get('account_type', ''),
                    'connected_at': connection.get('connected_at', ''),
                    'status': connection.get('status', 'active'),
                }
            else:
                status[platform_name] = {'connected': False}
        return status


# Global instance
oauth_manager = OAuthManager()


# Convenience functions (same signatures as old platform_oauth_manager.py)
def connect_platform(user_id: str, platform: str,
                     redirect_uri: str) -> Dict[str, Any]:
    """Initiate OAuth connection for a platform."""
    return oauth_manager.initiate_oauth(user_id, platform, redirect_uri)


def handle_platform_callback(user_id: str, platform: str, code: str,
                              state: str, redirect_uri: str) -> Dict[str, Any]:
    """Handle OAuth callback."""
    return oauth_manager.handle_callback(user_id, platform, code, state, redirect_uri)


def get_platform_token(user_id: str,
                       platform: str) -> Optional[Dict[str, Any]]:
    """Get valid platform token (auto-refreshes if needed)."""
    return oauth_manager.get_user_token(user_id, platform)


def disconnect_platform(user_id: str, platform: str) -> bool:
    """Disconnect a platform."""
    return oauth_manager.revoke_connection(user_id, platform)


def get_platform_connections(user_id: str) -> Dict[str, Any]:
    """Get all platform connection statuses."""
    return oauth_manager.get_connection_status(user_id)
