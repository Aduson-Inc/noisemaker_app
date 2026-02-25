"""
Threads OAuth Handler
Uses Meta's Threads API with long-lived token exchange (60-day tokens).
"""

import logging
from typing import Dict, Any

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class ThreadsOAuth(BasePlatformOAuth):
    """Threads OAuth via Meta Threads API."""

    PLATFORM_NAME = 'threads'
    AUTH_URL = 'https://threads.net/oauth/authorize'
    TOKEN_URL = 'https://graph.threads.net/oauth/access_token'
    SCOPES = ['threads_basic', 'threads_content_publish']
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'long_lived'
    REFRESH_METHOD = 'exchange'

    def get_user_info_url(self) -> str:
        return 'https://graph.threads.net/me?fields=id,username'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': response_data.get('id', ''),
            'username': response_data.get('username', ''),
            'account_type': 'personal',
        }
