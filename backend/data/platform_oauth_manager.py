"""
Platform OAuth Manager
Handles OAuth 2.0 authentication and token management for all social media platforms.
Each USER connects their own accounts - this is a SaaS application.
CRITICAL: This module manages user-specific OAuth tokens, NOT app-level tokens.
All tokens are stored per-user in DynamoDB and encrypted at rest.
Author: Senior Python Backend Engineer
Version: 1.0
Security Level: In Development
"""
import os
import boto3
import json
import logging
import secrets
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
from cryptography.fernet import Fernet
import base64
import requests
from .dynamodb_client import dynamodb_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenEncryption:
    """Handles encryption and decryption of OAuth tokens."""

    def __init__(self):
        """Initialize encryption by loading key from AWS SSM Parameter Store."""
        import boto3
        import os
        from cryptography.fernet import Fernet

        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
        ssm_client = boto3.client('ssm', region_name=region)

        param_name = '/noisemaker/oauth_encryption_key'  # Confirm this matches your exact parameter name

        try:
            response = ssm_client.get_parameter(
                Name=param_name,
                WithDecryption=True
            )
            key_value = response['Parameter']['Value']
            encryption_key = key_value.encode('utf-8')

            # Quick validation that it's a valid Fernet key
            Fernet(encryption_key)

            logger.info(f"Loaded encryption key from SSM: {param_name}")
            self.cipher = Fernet(encryption_key)

        except ssm_client.exceptions.ParameterNotFound:
            logger.critical(f"Encryption key not found in SSM: {param_name}")
            raise RuntimeError(f"Missing SSM parameter: {param_name}")

        except Exception as e:
            logger.critical(f"Failed to load encryption key: {str(e)}")
            raise RuntimeError(f"Invalid encryption key in SSM: {str(e)}")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        if not ciphertext:
            return ""
        return self.cipher.decrypt(ciphertext.encode()).decode()


class PlatformOAuthManager:
    """
    Manages OAuth 2.0 authentication for all social media platforms.
    Features:
    - User-specific token storage (SaaS model)
    - CSRF protection with state parameter
    - Automatic token refresh
    - Token encryption at rest
    - Support for 8 platforms
    - Graceful error handling
    """

    # Platform OAuth configurations
    PLATFORM_CONFIGS = {
        'instagram': {
            'auth_url': 'https://api.instagram.com/oauth/authorize',
            'token_url': 'https://api.instagram.com/oauth/access_token',
            'scopes': ['instagram_content_publish', 'instagram_basic', 'pages_read_engagement'],
            'requires_business_account': True,
            'token_type': 'long_lived',  # 60 days
            'refresh_method': 'exchange'
        },
        'facebook': {
            'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
            'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
            'scopes': ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list'],
            'requires_business_account': True,
            'token_type': 'long_lived',  # 60 days
            'refresh_method': 'exchange'
        },
        'twitter': {
            'auth_url': 'https://twitter.com/i/oauth2/authorize',
            'token_url': 'https://api.twitter.com/2/oauth2/token',
            'scopes': ['tweet.write', 'tweet.read', 'users.read', 'offline.access'],
            'requires_business_account': False,
            'token_type': 'bearer',
            'refresh_method': 'refresh_token',
            'uses_pkce': True
        },
        'tiktok': {
            'auth_url': 'https://www.tiktok.com/v2/auth/authorize',
            'token_url': 'https://open.tiktokapis.com/v2/oauth/token/',
            'scopes': ['video.upload', 'user.info.basic'],
            'requires_business_account': False,
            'token_type': 'bearer',
            'refresh_method': 'refresh_token'
        },
        'youtube': {
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/youtube.upload',
                       'https://www.googleapis.com/auth/youtube'],
            'requires_business_account': False,
            'token_type': 'bearer',
            'refresh_method': 'refresh_token'
        },
        'reddit': {
            'auth_url': 'https://www.reddit.com/api/v1/authorize',
            'token_url': 'https://www.reddit.com/api/v1/access_token',
            'scopes': ['submit', 'read', 'identity'],
            'requires_business_account': False,
            'token_type': 'bearer',
            'refresh_method': 'refresh_token',
            'duration': 'permanent'
        },
        'discord': {
            # Discord uses webhooks - no OAuth needed for posting
            'auth_url': None,
            'token_url': None,
            'scopes': [],
            'requires_business_account': False,
            'token_type': 'webhook',
            'refresh_method': None
        },
        'threads': {
            'auth_url': 'https://threads.net/oauth/authorize',
            'token_url': 'https://graph.threads.net/oauth/access_token',
            'scopes': ['threads_basic', 'threads_content_publish'],
            'requires_business_account': False,
            'token_type': 'long_lived',
            'refresh_method': 'exchange'
        }
    }

    def __init__(self):
        """Initialize OAuth manager."""
        self.table_name = 'noisemaker-platform-connections'
        self.state_table = 'noisemaker-oauth-states'
        self.encryptor = TokenEncryption()
        # Get OAuth credentials from Parameter Store
        self._ssm_client = None
        self._oauth_credentials = {}
        logger.info("Platform OAuth Manager initialized")

    @property
    def ssm_client(self):
        """Lazy loading of SSM client."""
        if self._ssm_client is None:
            region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
            self._ssm_client = boto3.client('ssm', region_name=region)
        return self._ssm_client

    def _get_platform_credentials(self, platform: str) -> Dict[str, str]:
        """
        Get OAuth app credentials for platform from Parameter Store.
        These are the APP credentials (client_id, client_secret),
        NOT user tokens. User tokens are stored in DynamoDB.
        """
        if platform in self._oauth_credentials:
            return self._oauth_credentials[platform]

        # Discord uses webhooks, no OAuth credentials needed
        if platform == 'discord':
            return {}

        credentials = {}
        # Get client_id
        try:
            credentials['client_id'] = self.ssm_client.get_parameter(
                Name=f'/noisemaker/{platform}_client_id',
                WithDecryption=True
            )['Parameter']['Value']
        except Exception as e:
            logger.error(f"Failed to get client_id for {platform}: {e}")
            raise ValueError(f"OAuth credentials not configured for {platform}")

        # Get client_secret
        try:
            credentials['client_secret'] = self.ssm_client.get_parameter(
                Name=f'/noisemaker/{platform}_client_secret',
                WithDecryption=True
            )['Parameter']['Value']
        except Exception as e:
            logger.error(f"Failed to get client_secret for {platform}: {e}")
            raise ValueError(f"OAuth credentials not configured for {platform}")

        # Cache credentials
        self._oauth_credentials[platform] = credentials
        return credentials

    def _generate_state(self, user_id: str, platform: str) -> str:
        """
        Generate CSRF state token.
        Args:
            user_id: User identifier
            platform: Platform name
        Returns:
            Secure random state string
        """
        # Generate cryptographically secure random state
        state = secrets.token_urlsafe(32)
        # Store state in DynamoDB with 10-minute expiration
        state_data = {
            'state': state,
            'user_id': user_id,
            'platform': platform,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        try:
            dynamodb_client.put_item(self.state_table, state_data)
            logger.debug(f"Generated OAuth state for user {user_id}, platform {platform}")
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")
            # Continue anyway - state validation will fail gracefully
        return state

    def _validate_state(self, state: str, user_id: str, platform: str) -> Optional[Dict]:
        """
        Validate CSRF state token.
        Args:
            state: State token from callback
            user_id: User identifier
            platform: Platform name
        Returns:
            state_data dict if valid, None otherwise
        """
        try:
            # Get state from DynamoDB
            key = {'state': state}
            state_data = dynamodb_client.get_item(self.state_table, key)
            if not state_data:
                logger.warning(f"State not found: {state}")
                return None
            # Check expiration
            expires_at = datetime.fromisoformat(state_data['expires_at'])
            if datetime.utcnow() > expires_at:
                logger.warning(f"State expired: {state}")
                dynamodb_client.delete_item(self.state_table, key)
                return None
            # Validate user_id and platform match
            if state_data['user_id'] != user_id or state_data['platform'] != platform:
                logger.warning(f"State mismatch for user {user_id}, platform {platform}")
                return None
            # Delete state after successful validation (one-time use)
            dynamodb_client.delete_item(self.state_table, key)
            return state_data
        except Exception as e:
            logger.error(f"Error validating state: {e}")
            return None

    def _generate_pkce_challenge(self) -> Tuple[str, str]:
        """
        Generate PKCE code verifier and challenge for OAuth 2.0 with PKCE.
        Used by Twitter.
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (43-128 characters)
        code_verifier = secrets.token_urlsafe(64)
        # Generate code challenge (SHA256 hash of verifier, base64 encoded)
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode().rstrip('=')
        return code_verifier, code_challenge

    def initiate_oauth(self, user_id: str, platform: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Initiate OAuth flow for a platform.
        Args:
            user_id: User identifier
            platform: Platform name (instagram, twitter, etc.)
            redirect_uri: OAuth callback URL
        Returns:
            Dict with 'authorization_url' and 'state'
        """
        try:
            if platform not in self.PLATFORM_CONFIGS:
                return {
                    'success': False,
                    'error': f'Unsupported platform: {platform}'
                }
            config = self.PLATFORM_CONFIGS[platform]
            # Discord uses webhooks, not OAuth
            if platform == 'discord':
                return {
                    'success': False,
                    'error': 'Discord uses webhook URLs. Please provide webhook URL directly.'
                }
            # Get platform OAuth credentials
            credentials = self._get_platform_credentials(platform)
            # Generate CSRF state
            state = self._generate_state(user_id, platform)
            # Build authorization URL
            params = {
                'client_id': credentials['client_id'],
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'state': state,
                'scope': ' '.join(config['scopes'])
            }
            # Platform-specific parameters
            if platform == 'reddit':
                params['duration'] = 'permanent'  # Get refresh token
            if platform == 'twitter' and config.get('uses_pkce'):
                # Generate PKCE challenge for Twitter
                code_verifier, code_challenge = self._generate_pkce_challenge()
                params['code_challenge'] = code_challenge
                params['code_challenge_method'] = 'S256'
                # Store code_verifier for token exchange
                state_key = {'state': state}
                state_data = dynamodb_client.get_item(self.state_table, state_key)
                if state_data:
                    state_data['code_verifier'] = code_verifier
                    dynamodb_client.put_item(self.state_table, state_data)
            authorization_url = f"{config['auth_url']}?{urlencode(params)}"
            logger.info(f"Initiated OAuth for user {user_id}, platform {platform}")
            return {
                'success': True,
                'auth_url': authorization_url,
                'state': state,
                'platform': platform
            }
        except Exception as e:
            logger.error(f"Error initiating OAuth for {platform}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def handle_callback(self, user_id: str, platform: str, code: str,
                        state: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.
        Args:
            user_id: User identifier
            platform: Platform name
            code: Authorization code from callback
            state: State parameter for CSRF protection
            redirect_uri: OAuth callback URL (must match initiate_oauth)
        Returns:
            Dict with success status and connection info
        """
        try:
            # Validate state for CSRF protection
            state_data = self._validate_state(state, user_id, platform)
            if not state_data:
                return {
                    'success': False,
                    'error': 'Invalid or expired state token (CSRF protection)'
                }
            config = self.PLATFORM_CONFIGS[platform]
            credentials = self._get_platform_credentials(platform)
            # Prepare token exchange request
            token_data = {
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            # Add PKCE code_verifier for Twitter (stored in state_data during initiate_oauth)
            if platform == 'twitter' and config.get('uses_pkce'):
                if state_data.get('code_verifier'):
                    token_data['code_verifier'] = state_data['code_verifier']
            # Exchange code for tokens
            headers = {'Accept': 'application/json'}
            # Reddit requires basic auth
            if platform == 'reddit':
                import base64
                auth_string = f"{credentials['client_id']}:{credentials['client_secret']}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers['Authorization'] = f'Basic {auth_bytes}'
                # Remove client credentials from body for Reddit
                del token_data['client_id']
                del token_data['client_secret']
            response = requests.post(
                config['token_url'],
                data=token_data,
                headers=headers,
                timeout=30
            )
            if response.status_code != 200:
                logger.error(f"Token exchange failed for {platform}: {response.text}")
                return {
                    'success': False,
                    'error': f'Token exchange failed: {response.status_code}'
                }
            token_response = response.json()
            # Extract tokens
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token', '')
            expires_in = token_response.get('expires_in', 3600)
            if not access_token:
                return {
                    'success': False,
                    'error': 'No access token in response'
                }
            # Get user info from platform
            platform_user_info = self._get_platform_user_info(platform, access_token)
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            # Store encrypted tokens in DynamoDB
            connection_data = {
                'user_id': user_id,
                'platform': platform,
                'access_token': self.encryptor.encrypt(access_token),
                'refresh_token': self.encryptor.encrypt(refresh_token) if refresh_token else '',
                'token_expires_at': expires_at.isoformat(),
                'connected_at': datetime.utcnow().isoformat(),
                'last_refreshed': datetime.utcnow().isoformat(),
                'platform_user_id': platform_user_info.get('id', ''),
                'platform_username': platform_user_info.get('username', ''),
                'account_type': platform_user_info.get('account_type', 'personal'),
                'scopes': config['scopes'],
                'status': 'active'
            }
            # Save to DynamoDB
            success = dynamodb_client.put_item(self.table_name, connection_data)
            if success:
                logger.info(f"Successfully connected {platform} for user {user_id}")
                return {
                    'success': True,
                    'platform': platform,
                    'username': platform_user_info.get('username', ''),
                    'account_type': platform_user_info.get('account_type', '')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save connection to database'
                }
        except Exception as e:
            logger.error(f"Error handling OAuth callback for {platform}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_platform_user_info(self, platform: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information from platform API.
        Args:
            platform: Platform name
            access_token: Valid access token
        Returns:
            Dict with user info
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            endpoints = {
                'instagram': 'https://graph.instagram.com/me?fields=id,username,account_type',
                'facebook': 'https://graph.facebook.com/me?fields=id,name',
                'twitter': 'https://api.twitter.com/2/users/me',
                'tiktok': 'https://open.tiktokapis.com/v2/user/info/',
                'youtube': 'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true',
                'reddit': 'https://oauth.reddit.com/api/v1/me',
                'threads': 'https://graph.threads.net/me?fields=id,username'
            }
            if platform not in endpoints:
                return {}
            response = requests.get(endpoints[platform], headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Normalize response format
                if platform == 'twitter':
                    user_data = data.get('data', {})
                    return {
                        'id': user_data.get('id', ''),
                        'username': user_data.get('username', '')
                    }
                elif platform == 'youtube':
                    items = data.get('items', [])
                    if items:
                        snippet = items[0].get('snippet', {})
                        return {
                            'id': items[0].get('id', ''),
                            'username': snippet.get('title', '')
                        }
                elif platform == 'reddit':
                    return {
                        'id': data.get('id', ''),
                        'username': data.get('name', '')
                    }
                else:
                    return {
                        'id': data.get('id', ''),
                        'username': data.get('username', data.get('name', '')),
                        'account_type': data.get('account_type', 'personal')
                    }
            return {}
        except Exception as e:
            logger.error(f"Error getting user info from {platform}: {e}")
            return {}

    def refresh_token(self, user_id: str, platform: str) -> bool:
        """
        Refresh expired access token.
        Args:
            user_id: User identifier
            platform: Platform name
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current connection
            key = {'user_id': user_id, 'platform': platform}
            connection = dynamodb_client.get_item(self.table_name, key)
            if not connection:
                logger.error(f"No connection found for user {user_id}, platform {platform}")
                return False
            config = self.PLATFORM_CONFIGS[platform]
            credentials = self._get_platform_credentials(platform)
            # Decrypt refresh token
            refresh_token_encrypted = connection.get('refresh_token', '')
            if not refresh_token_encrypted:
                logger.error(f"No refresh token available for {platform}")
                return False
            refresh_token = self.encryptor.decrypt(refresh_token_encrypted)
            # Prepare refresh request
            if config.get('refresh_method') == 'refresh_token':
                # Standard refresh token flow (Twitter, YouTube, Reddit, TikTok)
                token_data = {
                    'client_id': credentials['client_id'],
                    'client_secret': credentials['client_secret'],
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                }
            elif config.get('refresh_method') == 'exchange':
                # Long-lived token exchange (Instagram, Facebook, Threads)
                token_data = {
                    'grant_type': 'fb_exchange_token',
                    'client_id': credentials['client_id'],
                    'client_secret': credentials['client_secret'],
                    'fb_exchange_token': self.encryptor.decrypt(connection['access_token'])
                }
            else:
                logger.error(f"Unknown refresh method for {platform}")
                return False
            # Make refresh request
            headers = {'Accept': 'application/json'}
            # Reddit requires basic auth
            if platform == 'reddit':
                import base64
                auth_string = f"{credentials['client_id']}:{credentials['client_secret']}"
                auth_bytes = base64.b64encode(auth_string.encode()).decode()
                headers['Authorization'] = f'Basic {auth_bytes}'
                del token_data['client_id']
                del token_data['client_secret']
            response = requests.post(
                config['token_url'],
                data=token_data,
                headers=headers,
                timeout=30
            )
            if response.status_code != 200:
                logger.error(f"Token refresh failed for {platform}: {response.text}")
                return False
            token_response = response.json()
            # Update connection with new tokens
            new_access_token = token_response.get('access_token')
            new_refresh_token = token_response.get('refresh_token', refresh_token)
            expires_in = token_response.get('expires_in', 3600)
            if not new_access_token:
                return False
            # Update in DynamoDB
            updates = {
                'access_token': self.encryptor.encrypt(new_access_token),
                'refresh_token': self.encryptor.encrypt(new_refresh_token),
                'token_expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
                'last_refreshed': datetime.utcnow().isoformat()
            }
            success = dynamodb_client.update_item(self.table_name, key, updates)
            if success:
                logger.info(f"Successfully refreshed token for user {user_id}, platform {platform}")
            return success
        except Exception as e:
            logger.error(f"Error refreshing token for {platform}: {e}")
            return False

    def get_user_token(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get valid access token for user's platform connection.
        Automatically refreshes if expired.
        Args:
            user_id: User identifier
            platform: Platform name
        Returns:
            Dict with decrypted token data, or None if not connected
        """
        try:
            # Get connection from DynamoDB
            key = {'user_id': user_id, 'platform': platform}
            connection = dynamodb_client.get_item(self.table_name, key)
            if not connection:
                logger.debug(f"No connection found for user {user_id}, platform {platform}")
                return None
            # Check if token is expired
            expires_at = datetime.fromisoformat(connection['token_expires_at'])
            # Refresh if token expires within 5 minutes
            if datetime.utcnow() >= expires_at - timedelta(minutes=5):
                logger.info(f"Token expired or expiring soon for {platform}, refreshing...")
                if not self.refresh_token(user_id, platform):
                    logger.error(f"Failed to refresh token for {platform}")
                    # Mark connection as inactive
                    dynamodb_client.update_item(
                        self.table_name,
                        key,
                        {'status': 'token_expired'}
                    )
                    return None
                # Get updated connection
                connection = dynamodb_client.get_item(self.table_name, key)
                if not connection:
                    return None
            # Decrypt and return token
            return {
                'access_token': self.encryptor.decrypt(connection['access_token']),
                'platform_user_id': connection.get('platform_user_id', ''),
                'platform_username': connection.get('platform_username', ''),
                'account_type': connection.get('account_type', ''),
                'scopes': connection.get('scopes', [])
            }
        except Exception as e:
            logger.error(f"Error getting user token for {platform}: {e}")
            return None

    def revoke_connection(self, user_id: str, platform: str) -> bool:
        """
        Revoke/disconnect a platform connection.
        Args:
            user_id: User identifier
            platform: Platform name
        Returns:
            True if successful, False otherwise
        """
        try:
            key = {'user_id': user_id, 'platform': platform}
            # Optionally revoke token on platform side
            # (Implementation depends on platform API)
            # Delete from DynamoDB
            success = dynamodb_client.delete_item(self.table_name, key)
            if success:
                logger.info(f"Revoked connection for user {user_id}, platform {platform}")
            return success
        except Exception as e:
            logger.error(f"Error revoking connection for {platform}: {e}")
            return False

    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get connection status for all platforms.
        Args:
            user_id: User identifier
        Returns:
            Dict with status for each platform
        """
        try:
            status = {}
            for platform in self.PLATFORM_CONFIGS.keys():
                key = {'user_id': user_id, 'platform': platform}
                connection = dynamodb_client.get_item(self.table_name, key)
                if connection:
                    status[platform] = {
                        'connected': True,
                        'username': connection.get('platform_username', ''),
                        'account_type': connection.get('account_type', ''),
                        'connected_at': connection.get('connected_at', ''),
                        'status': connection.get('status', 'active')
                    }
                else:
                    status[platform] = {
                        'connected': False
                    }
            return status
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return {}

    def add_discord_webhook(self, user_id: str, webhook_url: str,
                            server_name: str = '') -> Dict[str, Any]:
        """
        Add Discord webhook URL (Discord doesn't use OAuth).
        Args:
            user_id: User identifier
            webhook_url: Discord webhook URL
            server_name: Optional server name
        Returns:
            Dict with success status
        """
        try:
            # Validate webhook URL format
            if not webhook_url.startswith('https://discord.com/api/webhooks/'):
                return {
                    'success': False,
                    'error': 'Invalid Discord webhook URL format'
                }
            # Store webhook URL (encrypted)
            connection_data = {
                'user_id': user_id,
                'platform': 'discord',
                'access_token': self.encryptor.encrypt(webhook_url),
                'refresh_token': '',
                'token_expires_at': (datetime.utcnow() + timedelta(days=365*10)).isoformat(),  # Webhooks don't expire
                'connected_at': datetime.utcnow().isoformat(),
                'last_refreshed': datetime.utcnow().isoformat(),
                'platform_user_id': '',
                'platform_username': server_name,
                'account_type': 'webhook',
                'scopes': [],
                'status': 'active'
            }
            success = dynamodb_client.put_item(self.table_name, connection_data)
            if success:
                logger.info(f"Added Discord webhook for user {user_id}")
                return {
                    'success': True,
                    'platform': 'discord'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save webhook'
                }
        except Exception as e:
            logger.error(f"Error adding Discord webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Global OAuth manager instance
oauth_manager = PlatformOAuthManager()


# Convenience functions
def connect_platform(user_id: str, platform: str, redirect_uri: str) -> Dict[str, Any]:
    """Initiate OAuth connection for a platform."""
    return oauth_manager.initiate_oauth(user_id, platform, redirect_uri)


def handle_platform_callback(user_id: str, platform: str, code: str,
                             state: str, redirect_uri: str) -> Dict[str, Any]:
    """Handle OAuth callback."""
    return oauth_manager.handle_callback(user_id, platform, code, state, redirect_uri)


def get_platform_token(user_id: str, platform: str) -> Optional[Dict[str, Any]]:
    """Get valid platform token (auto-refreshes if needed)."""
    return oauth_manager.get_user_token(user_id, platform)


def disconnect_platform(user_id: str, platform: str) -> bool:
    """Disconnect a platform."""
    return oauth_manager.revoke_connection(user_id, platform)


def get_platform_connections(user_id: str) -> Dict[str, Any]:
    """Get all platform connection statuses."""
    return oauth_manager.get_connection_status(user_id)
