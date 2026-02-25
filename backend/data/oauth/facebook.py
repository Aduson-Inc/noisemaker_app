"""
Facebook OAuth Handler
Uses Meta's Graph API with long-lived token exchange (60-day tokens).
Posts to Facebook Pages on behalf of users.
"""

import logging
from typing import Dict, Any

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class FacebookOAuth(BasePlatformOAuth):
    """Facebook OAuth via Meta Graph API."""

    PLATFORM_NAME = 'facebook'
    AUTH_URL = 'https://www.facebook.com/v18.0/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    SCOPES = ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list']
    REQUIRES_BUSINESS_ACCOUNT = True
    TOKEN_TYPE = 'long_lived'
    REFRESH_METHOD = 'exchange'

    def get_user_info_url(self) -> str:
        return 'https://graph.facebook.com/me?fields=id,name'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': response_data.get('id', ''),
            'username': response_data.get('name', ''),
            'account_type': 'page',
        }
