"""
Discord Handler
Discord does NOT use OAuth. Users provide a webhook URL directly.
Posting is a simple POST request to the webhook URL.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..dynamodb_client import dynamodb_client
from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class DiscordOAuth(BasePlatformOAuth):
    """Discord webhook handler — no OAuth flow."""

    PLATFORM_NAME = 'discord'
    AUTH_URL = ''
    TOKEN_URL = ''
    SCOPES = []
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'webhook'
    REFRESH_METHOD = None

    def initiate_oauth(self, user_id: str, redirect_uri: str) -> Dict[str, Any]:
        """Discord doesn't use OAuth."""
        return {
            'success': False,
            'error': 'Discord uses webhook URLs. Please provide webhook URL directly.',
        }

    def handle_callback(self, user_id: str, code: str,
                        state: str, redirect_uri: str) -> Dict[str, Any]:
        """Discord doesn't use OAuth callbacks."""
        return {'success': False, 'error': 'Discord does not use OAuth callbacks.'}

    def refresh_token(self, user_id: str) -> bool:
        """Webhooks don't expire — no refresh needed."""
        return True

    def add_webhook(self, user_id: str, webhook_url: str,
                    server_name: str = '') -> Dict[str, Any]:
        """
        Store a Discord webhook URL for the user.
        Args:
            user_id: User identifier.
            webhook_url: Discord webhook URL from user's server settings.
            server_name: Optional server/channel name for display.
        Returns:
            Dict with success status.
        """
        if not webhook_url.startswith('https://discord.com/api/webhooks/'):
            return {'success': False, 'error': 'Invalid Discord webhook URL format'}

        connection_data = {
            'user_id': user_id,
            'platform': 'discord',
            'access_token': self.encryptor.encrypt(webhook_url),
            'refresh_token': '',
            'token_expires_at': (datetime.utcnow() + timedelta(days=3650)).isoformat(),
            'connected_at': datetime.utcnow().isoformat(),
            'last_refreshed': datetime.utcnow().isoformat(),
            'platform_user_id': '',
            'platform_username': server_name,
            'account_type': 'webhook',
            'scopes': [],
            'status': 'active',
        }

        success = dynamodb_client.put_item(self.table_name, connection_data)
        if success:
            logger.info(f"Added Discord webhook for user {user_id}")
            return {'success': True, 'platform': 'discord'}
        return {'success': False, 'error': 'Failed to save webhook'}
