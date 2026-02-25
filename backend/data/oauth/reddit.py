"""
Reddit OAuth Handler
Uses OAuth 2.0 with HTTP Basic Authentication for token exchange and refresh.
Reddit requires client credentials sent as a Basic Auth header (base64-encoded
client_id:client_secret) rather than in the POST body. Also requires
duration=permanent in the auth URL to receive a refresh_token.

For posting, use praw (Python Reddit API Wrapper) with the stored refresh_token:
    import praw
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        user_agent='noisemaker:v1.0 (by /u/noisemaker)'
    )
    subreddit = reddit.subreddit('musicpromotion')
    subreddit.submit(title='Check out this track', url='https://...')
"""

import base64
import logging
from typing import Dict, Any, Tuple

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class RedditOAuth(BasePlatformOAuth):
    """Reddit OAuth 2.0 with HTTP Basic Auth for token exchange."""

    PLATFORM_NAME = 'reddit'
    AUTH_URL = 'https://www.reddit.com/api/v1/authorize'
    TOKEN_URL = 'https://www.reddit.com/api/v1/access_token'
    SCOPES = ['submit', 'read', 'identity']
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'bearer'
    REFRESH_METHOD = 'refresh_token'

    def _build_basic_auth_header(self, credentials: Dict[str, str]) -> str:
        """Build HTTP Basic Auth header value from client credentials."""
        auth_string = f"{credentials['client_id']}:{credentials['client_secret']}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()
        return f'Basic {auth_bytes}'

    def build_auth_params(self, credentials: Dict[str, str],
                          state: str, redirect_uri: str) -> Dict[str, str]:
        """Add duration=permanent to get a refresh_token from Reddit."""
        return {
            'client_id': credentials['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(self.SCOPES),
            'duration': 'permanent',
        }

    def build_token_request(self, credentials: Dict[str, str], code: str,
                            redirect_uri: str,
                            state_data: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """
        Reddit requires credentials as Basic Auth header, not in POST body.
        """
        token_data = {
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        headers = {
            'Accept': 'application/json',
            'Authorization': self._build_basic_auth_header(credentials),
        }
        return token_data, headers

    def build_refresh_request(self, credentials: Dict[str, str],
                              connection: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """Reddit refresh also uses Basic Auth header, not body credentials."""
        refresh_token_encrypted = connection.get('refresh_token', '')
        if not refresh_token_encrypted:
            raise ValueError("No refresh token available for reddit")

        token_data = {
            'refresh_token': self.encryptor.decrypt(refresh_token_encrypted),
            'grant_type': 'refresh_token',
        }
        headers = {
            'Accept': 'application/json',
            'Authorization': self._build_basic_auth_header(credentials),
        }
        return token_data, headers

    def get_user_info_url(self) -> str:
        return 'https://oauth.reddit.com/api/v1/me'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reddit returns user data flat at the top level with 'name' not 'username'."""
        return {
            'id': response_data.get('id', ''),
            'username': response_data.get('name', ''),
            'account_type': 'personal',
        }
