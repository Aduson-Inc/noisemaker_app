"""
Twitter/X OAuth Handler
Uses OAuth 2.0 with PKCE (Proof Key for Code Exchange) as required by
Twitter's v2 API. Generates code_verifier/code_challenge during auth initiation,
stores code_verifier in the DynamoDB state record, and includes it in the token
exchange request.

For posting tweets, use tweepy.Client with the stored access_token:
    import tweepy
    client = tweepy.Client(access_token=access_token)
    client.create_tweet(text="Hello world")
"""

import logging
from typing import Dict, Any, Tuple

from .base import BasePlatformOAuth
from ..dynamodb_client import dynamodb_client

logger = logging.getLogger(__name__)


class TwitterOAuth(BasePlatformOAuth):
    """Twitter/X OAuth 2.0 with PKCE flow."""

    PLATFORM_NAME = 'twitter'
    AUTH_URL = 'https://twitter.com/i/oauth2/authorize'
    TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
    SCOPES = ['tweet.write', 'tweet.read', 'users.read', 'offline.access']
    REQUIRES_BUSINESS_ACCOUNT = False
    TOKEN_TYPE = 'bearer'
    REFRESH_METHOD = 'refresh_token'

    def build_auth_params(self, credentials: Dict[str, str],
                          state: str, redirect_uri: str) -> Dict[str, str]:
        """
        Build auth params with PKCE code_challenge.
        Generates code_verifier, stores it in the DynamoDB state record so
        handle_callback can read it from state_data during token exchange.
        """
        code_verifier, code_challenge = self._generate_pkce_challenge()

        # Store code_verifier in the existing state record
        state_key = {'state': state}
        state_data = dynamodb_client.get_item(self.state_table, state_key)
        if state_data:
            state_data['code_verifier'] = code_verifier
            dynamodb_client.put_item(self.state_table, state_data)
        else:
            logger.error(f"Could not find state record to store code_verifier: {state}")

        return {
            'client_id': credentials['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(self.SCOPES),
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        }

    def build_token_request(self, credentials: Dict[str, str], code: str,
                            redirect_uri: str,
                            state_data: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """
        Build token exchange request with PKCE code_verifier.
        H5 fix: state_data is available here because _validate_state no longer
        deletes the state record — _delete_state is called after this method.
        """
        token_data = {
            'client_id': credentials['client_id'],
            'client_secret': credentials['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }

        code_verifier = state_data.get('code_verifier')
        if code_verifier:
            token_data['code_verifier'] = code_verifier
        else:
            logger.warning("No code_verifier found in state_data for Twitter PKCE flow")

        headers = {'Accept': 'application/json'}
        return token_data, headers

    def get_user_info_url(self) -> str:
        return 'https://api.twitter.com/2/users/me'

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Twitter nests user data under 'data' key."""
        user_data = response_data.get('data', {})
        return {
            'id': user_data.get('id', ''),
            'username': user_data.get('username', ''),
            'account_type': 'personal',
        }
