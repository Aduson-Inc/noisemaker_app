"""
TikTok OAuth Handler
Uses TikTok's v2 API with standard refresh_token flow.
Video-focused platform with unique API conventions.
Note: TikTok uses 'client_key' instead of 'client_id' in API params.
"""

import logging
from typing import Dict, Any, Tuple

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class TikTokOAuth(BasePlatformOAuth):
    """TikTok OAuth via TikTok v2 API."""

    PLATFORM_NAME = 'tiktok'
    AUTH_URL = 'https://www.tiktok.com/v2/auth/authorize'
    TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'
    SCOPES = ['video.upload', 'user.info.basic']
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'bearer'
    REFRESH_METHOD = 'refresh_token'

    def build_auth_params(self, credentials: Dict[str, str],
                          state: str, redirect_uri: str) -> Dict[str, str]:
        """TikTok uses 'client_key' instead of 'client_id'."""
        return {
            'client_key': credentials['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ','.join(self.SCOPES),  # TikTok uses comma-separated scopes
        }

    def build_token_request(self, credentials: Dict[str, str], code: str,
                            redirect_uri: str,
                            state_data: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """TikTok uses 'client_key' instead of 'client_id' for token exchange."""
        token_data = {
            'client_key': credentials['client_id'],
            'client_secret': credentials['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        headers = {'Accept': 'application/json'}
        return token_data, headers

    def build_refresh_request(self, credentials: Dict[str, str],
                              connection: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """TikTok refresh also uses 'client_key'."""
        refresh_token_encrypted = connection.get('refresh_token', '')
        if not refresh_token_encrypted:
            raise ValueError("No refresh token available for tiktok")

        token_data = {
            'client_key': credentials['client_id'],
            'client_secret': credentials['client_secret'],
            'refresh_token': self.encryptor.decrypt(refresh_token_encrypted),
            'grant_type': 'refresh_token',
        }
        headers = {'Accept': 'application/json'}
        return token_data, headers

    def get_user_info_url(self) -> str:
        return 'https://open.tiktokapis.com/v2/user/info/?fields=open_id,display_name'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """TikTok nests user data under data.user."""
        user = response_data.get('data', {}).get('user', {})
        return {
            'id': user.get('open_id', ''),
            'username': user.get('display_name', ''),
            'account_type': 'personal',
        }
