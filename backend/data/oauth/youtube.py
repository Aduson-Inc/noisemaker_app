"""
YouTube OAuth Handler
Uses Google's OAuth 2.0 with offline access to obtain a refresh_token.
Requires access_type=offline and prompt=consent in the auth URL to ensure
the refresh_token is always returned (Google only sends it on first consent
or when prompt=consent is explicitly set).

For video uploads, use google-api-python-client with resumable uploads:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials(token=access_token)
    youtube = build('youtube', 'v3', credentials=creds)
    request = youtube.videos().insert(
        part='snippet,status',
        body={...},
        media_body=MediaFileUpload('video.mp4', resumable=True)
    )
    response = request.execute()
"""

import logging
from typing import Dict, Any

from .base import BasePlatformOAuth

logger = logging.getLogger(__name__)


class YouTubeOAuth(BasePlatformOAuth):
    """YouTube OAuth via Google OAuth 2.0 with offline access."""

    PLATFORM_NAME = 'youtube'
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
    ]
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'bearer'
    REFRESH_METHOD = 'refresh_token'

    def build_auth_params(self, credentials: Dict[str, str],
                          state: str, redirect_uri: str) -> Dict[str, str]:
        """
        Add access_type=offline and prompt=consent to ensure Google returns
        a refresh_token. Without these, Google only sends refresh_token on
        the very first authorization.
        """
        return {
            'client_id': credentials['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(self.SCOPES),
            'access_type': 'offline',
            'prompt': 'consent',
        }

    def get_user_info_url(self) -> str:
        return 'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """YouTube returns channel data under items[0]."""
        items = response_data.get('items', [])
        if items:
            channel = items[0]
            snippet = channel.get('snippet', {})
            return {
                'id': channel.get('id', ''),
                'username': snippet.get('title', ''),
                'account_type': 'channel',
            }
        return {'id': '', 'username': '', 'account_type': 'channel'}
