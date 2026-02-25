"""
Base Platform OAuth Module
Provides the BasePlatformOAuth class that all platform-specific OAuth handlers extend.
Contains shared infrastructure: state management, token storage, credential loading,
and the high-level OAuth flow methods (initiate, callback, refresh, revoke).

Bug fixes applied:
- H5: _validate_state no longer deletes state record; separate _delete_state method added.
       handle_callback reads code_verifier from state_data BEFORE deleting state.
- M8: _get_credentials uses a single try/except for both client_id and client_secret.
"""

import os
import secrets
import hashlib
import base64
import logging
import requests
import boto3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from ..dynamodb_client import dynamodb_client
from .encryption import TokenEncryption

logger = logging.getLogger(__name__)


class BasePlatformOAuth:
    """
    Base class for platform-specific OAuth 2.0 handlers.
    Subclasses override class-level config and hook methods.
    High-level flow methods (initiate_oauth, handle_callback, etc.) are NOT overridden.
    """

    # --- Config attributes (override in subclasses) ---
    PLATFORM_NAME: str = ''
    AUTH_URL: str = ''
    TOKEN_URL: str = ''
    SCOPES: List[str] = []
    REQUIRES_BUSINESS_ACCOUNT: bool = False
    TOKEN_TYPE: str = 'bearer'
    REFRESH_METHOD: str = 'refresh_token'  # 'refresh_token' or 'exchange'

    # --- Shared infrastructure ---
    table_name: str = 'noisemaker-platform-connections'
    state_table: str = 'noisemaker-oauth-states'

    def __init__(self, encryptor: TokenEncryption):
        self.encryptor = encryptor
        self._ssm_client = None
        self._credentials_cache: Dict[str, str] = {}

    # ─────────────────────────────────────────────
    # SSM / Credentials (M8 fix: single try/except)
    # ─────────────────────────────────────────────

    @property
    def ssm_client(self):
        """Lazy-loaded SSM client."""
        if self._ssm_client is None:
            region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
            self._ssm_client = boto3.client('ssm', region_name=region)
        return self._ssm_client

    def _get_credentials(self) -> Dict[str, str]:
        """
        Get OAuth app credentials from SSM Parameter Store.
        M8 fix: single try/except for both params.
        """
        if self._credentials_cache:
            return self._credentials_cache

        platform = self.PLATFORM_NAME
        try:
            client_id = self.ssm_client.get_parameter(
                Name=f'/noisemaker/{platform}_client_id',
                WithDecryption=True
            )['Parameter']['Value']

            client_secret = self.ssm_client.get_parameter(
                Name=f'/noisemaker/{platform}_client_secret',
                WithDecryption=True
            )['Parameter']['Value']
        except Exception as e:
            logger.error(f"Failed to get OAuth credentials for {platform}: {e}")
            raise ValueError(f"OAuth credentials not configured for {platform}")

        self._credentials_cache = {
            'client_id': client_id,
            'client_secret': client_secret,
        }
        return self._credentials_cache

    # ─────────────────────────────────────────────
    # State / CSRF Management (H5 fix)
    # ─────────────────────────────────────────────

    def _generate_state(self, user_id: str) -> str:
        """Generate CSRF state token, store in DynamoDB with 10-min expiry."""
        state = secrets.token_urlsafe(32)
        state_data = {
            'state': state,
            'user_id': user_id,
            'platform': self.PLATFORM_NAME,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
        }
        try:
            dynamodb_client.put_item(self.state_table, state_data)
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
        return state

    def _validate_state(self, state: str, user_id: str) -> Optional[Dict]:
        """
        Validate CSRF state token.
        H5 FIX: Does NOT delete state. Caller must call _delete_state() after
        consuming state_data (e.g., after extracting code_verifier for PKCE).
        """
        try:
            key = {'state': state}
            state_data = dynamodb_client.get_item(self.state_table, key)

            if not state_data:
                logger.warning(f"State not found: {state}")
                return None

            expires_at = datetime.fromisoformat(state_data['expires_at'])
            if datetime.utcnow() > expires_at:
                logger.warning(f"State expired: {state}")
                dynamodb_client.delete_item(self.state_table, key)
                return None

            if state_data['user_id'] != user_id or state_data['platform'] != self.PLATFORM_NAME:
                logger.warning(f"State mismatch for user {user_id}, platform {self.PLATFORM_NAME}")
                return None

            return state_data

        except Exception as e:
            logger.error(f"Error validating state: {e}")
            return None

    def _delete_state(self, state: str) -> None:
        """Delete state record after it's been fully consumed."""
        try:
            dynamodb_client.delete_item(self.state_table, {'state': state})
        except Exception as e:
            logger.error(f"Failed to delete OAuth state {state}: {e}")

    # ─────────────────────────────────────────────
    # PKCE (used by Twitter and potentially others)
    # ─────────────────────────────────────────────

    def _generate_pkce_challenge(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge. Returns (code_verifier, code_challenge)."""
        code_verifier = secrets.token_urlsafe(64)
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip('=')
        return code_verifier, code_challenge

    # ─────────────────────────────────────────────
    # Token Storage
    # ─────────────────────────────────────────────

    def _store_connection(self, user_id: str, access_token: str,
                          refresh_token: str, expires_in: int,
                          platform_user_info: Dict[str, Any]) -> bool:
        """Encrypt tokens and store platform connection in DynamoDB."""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        connection_data = {
            'user_id': user_id,
            'platform': self.PLATFORM_NAME,
            'access_token': self.encryptor.encrypt(access_token),
            'refresh_token': self.encryptor.encrypt(refresh_token) if refresh_token else '',
            'token_expires_at': expires_at.isoformat(),
            'connected_at': datetime.utcnow().isoformat(),
            'last_refreshed': datetime.utcnow().isoformat(),
            'platform_user_id': platform_user_info.get('id', ''),
            'platform_username': platform_user_info.get('username', ''),
            'account_type': platform_user_info.get('account_type', 'personal'),
            'scopes': self.SCOPES,
            'status': 'active',
        }
        return dynamodb_client.put_item(self.table_name, connection_data)

    def _get_connection(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get platform connection record from DynamoDB."""
        key = {'user_id': user_id, 'platform': self.PLATFORM_NAME}
        return dynamodb_client.get_item(self.table_name, key)

    def _update_tokens(self, user_id: str, new_access_token: str,
                       new_refresh_token: str, expires_in: int) -> bool:
        """Update encrypted tokens in DynamoDB."""
        key = {'user_id': user_id, 'platform': self.PLATFORM_NAME}
        updates = {
            'access_token': self.encryptor.encrypt(new_access_token),
            'refresh_token': self.encryptor.encrypt(new_refresh_token),
            'token_expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
            'last_refreshed': datetime.utcnow().isoformat(),
        }
        return dynamodb_client.update_item(self.table_name, key, updates)

    # ─────────────────────────────────────────────
    # Hook methods (override in subclasses)
    # ─────────────────────────────────────────────

    def build_auth_params(self, credentials: Dict[str, str],
                          state: str, redirect_uri: str) -> Dict[str, str]:
        """Build query params for authorization URL. Override for platform-specific params."""
        return {
            'client_id': credentials['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(self.SCOPES),
        }

    def build_token_request(self, credentials: Dict[str, str], code: str,
                            redirect_uri: str,
                            state_data: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """Build POST body + headers for token exchange. Override for PKCE, basic auth, etc."""
        token_data = {
            'client_id': credentials['client_id'],
            'client_secret': credentials['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        headers = {'Accept': 'application/json'}
        return token_data, headers

    def get_user_info_url(self) -> str:
        """Return platform's user info API endpoint. Override in each subclass."""
        return ''

    def parse_user_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse platform-specific user info into {id, username, account_type}."""
        return {
            'id': response_data.get('id', ''),
            'username': response_data.get('username', response_data.get('name', '')),
            'account_type': response_data.get('account_type', 'personal'),
        }

    def build_refresh_request(self, credentials: Dict[str, str],
                              connection: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """Build POST body + headers for token refresh."""
        headers = {'Accept': 'application/json'}

        if self.REFRESH_METHOD == 'refresh_token':
            refresh_token_encrypted = connection.get('refresh_token', '')
            if not refresh_token_encrypted:
                raise ValueError(f"No refresh token available for {self.PLATFORM_NAME}")
            token_data = {
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'refresh_token': self.encryptor.decrypt(refresh_token_encrypted),
                'grant_type': 'refresh_token',
            }
            return token_data, headers

        elif self.REFRESH_METHOD == 'exchange':
            token_data = {
                'grant_type': 'fb_exchange_token',
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'fb_exchange_token': self.encryptor.decrypt(connection['access_token']),
            }
            return token_data, headers

        raise ValueError(f"Unknown refresh method: {self.REFRESH_METHOD}")

    # ─────────────────────────────────────────────
    # High-level flow methods (NOT overridden)
    # ─────────────────────────────────────────────

    def initiate_oauth(self, user_id: str, redirect_uri: str) -> Dict[str, Any]:
        """Build auth URL and return {success, auth_url, state, platform}."""
        try:
            if not self.AUTH_URL:
                return {'success': False, 'error': f'{self.PLATFORM_NAME} does not support OAuth.'}

            credentials = self._get_credentials()
            state = self._generate_state(user_id)
            params = self.build_auth_params(credentials, state, redirect_uri)
            authorization_url = f"{self.AUTH_URL}?{urlencode(params)}"

            logger.info(f"Initiated OAuth for user {user_id}, platform {self.PLATFORM_NAME}")
            return {
                'success': True,
                'auth_url': authorization_url,
                'state': state,
                'platform': self.PLATFORM_NAME,
            }

        except Exception as e:
            logger.error(f"Error initiating OAuth for {self.PLATFORM_NAME}: {e}")
            return {'success': False, 'error': str(e)}

    def handle_callback(self, user_id: str, code: str,
                        state: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Handle OAuth callback: validate state, exchange code, fetch user info, store connection.
        H5 FIX: state is deleted AFTER code_verifier is consumed by build_token_request.
        """
        try:
            state_data = self._validate_state(state, user_id)
            if not state_data:
                return {'success': False, 'error': 'Invalid or expired state token (CSRF protection)'}

            credentials = self._get_credentials()

            # Build token request — subclass extracts code_verifier from state_data here
            token_data, headers = self.build_token_request(
                credentials, code, redirect_uri, state_data
            )

            # H5 FIX: delete state AFTER state_data fully consumed
            self._delete_state(state)

            response = requests.post(self.TOKEN_URL, data=token_data,
                                     headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Token exchange failed for {self.PLATFORM_NAME}: {response.text}")
                return {'success': False, 'error': f'Token exchange failed: {response.status_code}'}

            token_response = response.json()
            access_token = token_response.get('access_token')
            refresh_token_value = token_response.get('refresh_token', '')
            expires_in = token_response.get('expires_in', 3600)

            if not access_token:
                return {'success': False, 'error': 'No access token in response'}

            platform_user_info = self._fetch_user_info(access_token)

            success = self._store_connection(
                user_id, access_token, refresh_token_value,
                expires_in, platform_user_info,
            )

            if success:
                logger.info(f"Successfully connected {self.PLATFORM_NAME} for user {user_id}")
                return {
                    'success': True,
                    'platform': self.PLATFORM_NAME,
                    'username': platform_user_info.get('username', ''),
                    'account_type': platform_user_info.get('account_type', ''),
                }
            return {'success': False, 'error': 'Failed to save connection to database'}

        except Exception as e:
            logger.error(f"Error handling OAuth callback for {self.PLATFORM_NAME}: {e}")
            return {'success': False, 'error': str(e)}

    def _fetch_user_info(self, access_token: str) -> Dict[str, Any]:
        """Fetch and parse user info from platform API using hook methods."""
        url = self.get_user_info_url()
        if not url:
            return {}
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return self.parse_user_info(response.json())
            return {}
        except Exception as e:
            logger.error(f"Error getting user info from {self.PLATFORM_NAME}: {e}")
            return {}

    def refresh_token(self, user_id: str) -> bool:
        """Refresh expired access token using platform-specific refresh flow."""
        try:
            connection = self._get_connection(user_id)
            if not connection:
                logger.error(f"No connection found for user {user_id}, platform {self.PLATFORM_NAME}")
                return False

            credentials = self._get_credentials()
            token_data, headers = self.build_refresh_request(credentials, connection)

            response = requests.post(self.TOKEN_URL, data=token_data,
                                     headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Token refresh failed for {self.PLATFORM_NAME}: {response.text}")
                return False

            token_response = response.json()
            new_access_token = token_response.get('access_token')
            if not new_access_token:
                return False

            if self.REFRESH_METHOD == 'refresh_token':
                old_refresh = self.encryptor.decrypt(connection.get('refresh_token', ''))
                new_refresh = token_response.get('refresh_token', old_refresh)
            else:
                new_refresh = ''

            expires_in = token_response.get('expires_in', 3600)
            success = self._update_tokens(user_id, new_access_token, new_refresh, expires_in)

            if success:
                logger.info(f"Refreshed token for user {user_id}, platform {self.PLATFORM_NAME}")
            return success

        except Exception as e:
            logger.error(f"Error refreshing token for {self.PLATFORM_NAME}: {e}")
            return False

    def get_user_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get valid access token, auto-refreshes if expired/expiring within 5 min."""
        try:
            connection = self._get_connection(user_id)
            if not connection:
                return None

            expires_at = datetime.fromisoformat(connection['token_expires_at'])
            if datetime.utcnow() >= expires_at - timedelta(minutes=5):
                if not self.refresh_token(user_id):
                    key = {'user_id': user_id, 'platform': self.PLATFORM_NAME}
                    dynamodb_client.update_item(self.table_name, key, {'status': 'token_expired'})
                    return None
                connection = self._get_connection(user_id)
                if not connection:
                    return None

            return {
                'access_token': self.encryptor.decrypt(connection['access_token']),
                'platform_user_id': connection.get('platform_user_id', ''),
                'platform_username': connection.get('platform_username', ''),
                'account_type': connection.get('account_type', ''),
                'scopes': connection.get('scopes', []),
            }

        except Exception as e:
            logger.error(f"Error getting user token for {self.PLATFORM_NAME}: {e}")
            return None

    def revoke_connection(self, user_id: str) -> bool:
        """Delete platform connection from DynamoDB."""
        try:
            key = {'user_id': user_id, 'platform': self.PLATFORM_NAME}
            success = dynamodb_client.delete_item(self.table_name, key)
            if success:
                logger.info(f"Revoked connection for user {user_id}, platform {self.PLATFORM_NAME}")
            return success
        except Exception as e:
            logger.error(f"Error revoking connection for {self.PLATFORM_NAME}: {e}")
            return False
