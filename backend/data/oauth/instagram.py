"""
Instagram OAuth Handler
Uses Meta's Graph API with long-lived token exchange (60-day tokens).
Requires Instagram Business/Creator account for content publishing.
"""

import logging
from typing import Dict, Any

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class InstagramOAuth(BasePlatformOAuth):
    """Instagram OAuth via Meta Graph API."""

    PLATFORM_NAME = 'instagram'
    AUTH_URL = 'https://api.instagram.com/oauth/authorize'
    TOKEN_URL = 'https://api.instagram.com/oauth/access_token'
    SCOPES = ['instagram_content_publish', 'instagram_basic', 'pages_read_engagement']
    REQUIRES_BUSINESS_ACCOUNT = True
    TOKEN_TYPE = 'long_lived'
    REFRESH_METHOD = 'exchange'

    def get_user_info_url(self) -> str:
        return 'https://graph.instagram.com/me?fields=id,username,account_type'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': response_data.get('id', ''),
            'username': response_data.get('username', ''),
            'account_type': response_data.get('account_type', 'personal'),
        }
