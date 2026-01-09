"""
User Authentication Module
Secure user session management and authentication for self-hosted SaaS.
No external frameworks - pure Python with AWS integration.

Author: Senior Python Backend Engineer
Version: 1.0
Security Level: Production-ready
"""

import hashlib
import secrets
import time
import os
from typing import Optional, Dict, Any, Tuple
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserAuth:
    """
    Secure user authentication system using AWS DynamoDB for session storage.

    Features:
    - Secure password hashing with salt
    - Session token management
    - Rate limiting protection
    - Audit logging
    - No external dependencies beyond AWS
    """

    def __init__(self, table_name: str = 'noisemaker-users'):
        """
        Initialize authentication system.

        Args:
            table_name (str): DynamoDB table name for user storage
        """
        try:
            # CRITICAL: Explicitly set region for production
            region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')
            self.dynamodb = boto3.resource('dynamodb', region_name=region)
            self.table = self.dynamodb.Table(table_name)
            self.email_reservations_table = self.dynamodb.Table('noisemaker-email-reservations')
            self.session_duration = 86400  # 24 hours in seconds
            self.max_login_attempts = 5
            logger.info(f"UserAuth initialized with table: {table_name} in region: {region}")
        except Exception as e:
            logger.error(f"Failed to initialize UserAuth: {str(e)}")
            raise

    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Securely hash password with salt using PBKDF2-SHA256.

        Args:
            password (str): Plain text password
            salt (str, optional): Hex-encoded salt. Generated if not provided.

        Returns:
            Tuple[str, str]: (hashed_password_hex, salt_hex)
        """
        if salt is None:
            salt = secrets.token_hex(32)

        # Hash with 100k iterations for security
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )

        return hashed.hex(), salt

    def _generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(64)

    def _get_current_timestamp(self) -> int:
        """Get current Unix timestamp"""
        return int(time.time())

    def _increment_login_attempts(self, user_id: str) -> None:
        """Increment failed login attempt counter"""
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET login_attempts = login_attempts + :inc',
                ExpressionAttributeValues={':inc': 1}
            )
        except Exception as e:
            logger.error(f"Failed to increment login attempts for {user_id}: {str(e)}")

    def _cleanup_email_reservation(self, email: str) -> None:
        """Remove email reservation if user creation failed."""
        try:
            self.email_reservations_table.delete_item(Key={'email': email})
            logger.info(f"Cleaned up email reservation for {email}")
        except Exception as e:
            logger.error(f"Failed to cleanup email reservation for {email}: {str(e)}")

    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        tier: str = 'talent'
    ) -> Optional[str]:
        """
        Create new user account with atomic email uniqueness check.

        Uses email reservation table to prevent race conditions where two
        simultaneous signups with the same email could both succeed.

        Args:
            email (str): User email address
            password (str): Plain text password (will be hashed)
            name (str): User's full name (artist/band name)
            tier (str): Subscription tier

        Returns:
            Optional[str]: User ID if successful, None if email taken or error
        """
        email_lower = email.lower()
        user_id = secrets.token_urlsafe(16)
        timestamp = self._get_current_timestamp()

        # Step 1: Reserve email atomically
        # This fails with ConditionalCheckFailedException if email already exists
        try:
            self.email_reservations_table.put_item(
                Item={
                    'email': email_lower,
                    'user_id': user_id,
                    'created_at': timestamp
                },
                ConditionExpression='attribute_not_exists(email)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Email already registered: {email_lower}")
                return None  # Email taken - atomic check failed
            logger.error(f"AWS error reserving email {email_lower}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reserving email {email_lower}: {str(e)}")
            return None

        # Step 2: Create user (email is now reserved)
        try:
            password_hash, password_salt = self._hash_password(password)

            user_item = {
                'user_id': user_id,
                'email': email_lower,
                'password_hash': password_hash,
                'password_salt': password_salt,
                'name': name,
                'created_at': timestamp,
                'last_login': 0,
                'login_attempts': 0,
                'account_status': 'active',
                'subscription_tier': tier,
                'session_token': None,
                'session_expires': 0
            }

            self.table.put_item(Item=user_item)
            logger.info(f"Created new user: {user_id} ({email_lower})")
            return user_id

        except ClientError as e:
            logger.error(f"AWS error creating user: {str(e)}")
            self._cleanup_email_reservation(email_lower)
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self._cleanup_email_reservation(email_lower)
            return None

    def get_user_id_by_email(self, email: str) -> Optional[str]:
        """
        Look up user_id by email address using Global Secondary Index (GSI).

        Uses the 'email-index' GSI for efficient O(1) lookups instead of
        full table scans. This is critical for production scale.

        GSI Configuration:
        - Index Name: email-index
        - Partition Key: email (String)
        - Projection: ALL

        Args:
            email (str): User email address

        Returns:
            Optional[str]: User ID if found, None otherwise
        """
        try:
            # Use GSI query for efficient email lookup (O(1) vs O(n) scan)
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email.lower()},
                Limit=1  # Email should be unique, only need first match
            )

            if response.get('Items'):
                user_id = response['Items'][0].get('user_id')
                logger.info(f"Found user_id {user_id} for email {email}")
                return user_id

            logger.info(f"No user found for email {email}")
            return None

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            # Fallback to scan if GSI doesn't exist yet (during migration)
            if error_code == 'ValidationException' and 'email-index' in str(e):
                logger.warning("email-index GSI not found, falling back to scan")
                return self._get_user_id_by_email_scan(email)
            logger.error(f"AWS error looking up email {email}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error looking up email {email}: {str(e)}")
            return None

    def _get_user_id_by_email_scan(self, email: str) -> Optional[str]:
        """
        Fallback method using table scan (for migration period only).

        This is kept as a fallback during the GSI migration period.
        Once email-index GSI is deployed, this can be removed.
        """
        try:
            response = self.table.scan(
                FilterExpression=Attr('email').eq(email.lower())
            )

            if response.get('Items'):
                user_id = response['Items'][0].get('user_id')
                logger.info(f"Found user_id {user_id} for email {email} (via scan fallback)")
                return user_id

            return None

        except Exception as e:
            logger.error(f"Scan fallback error for email {email}: {str(e)}")
            return None

    def authenticate_user(self, user_id: str, password: str) -> Optional[str]:
        """
        Authenticate user and return session token.

        Args:
            user_id (str): User identifier
            password (str): Plain text password

        Returns:
            Optional[str]: Session token if authentication successful, None otherwise
        """
        try:
            # Get user from database
            response = self.table.get_item(Key={'user_id': user_id})

            if 'Item' not in response:
                logger.warning(f"Authentication failed: User {user_id} not found")
                return None

            user = response['Item']

            # Check account status
            if user.get('account_status') != 'active':
                logger.warning(f"Authentication failed: User {user_id} account inactive")
                return None

            # Check rate limiting
            if user.get('login_attempts', 0) >= self.max_login_attempts:
                logger.warning(f"Authentication failed: User {user_id} exceeded login attempts")
                return None

            # Verify password
            stored_hash = user.get('password_hash')
            salt = user.get('password_salt')

            if not stored_hash or not salt:
                logger.error(f"Authentication failed: Invalid password data for user {user_id}")
                return None

            hashed_password, _ = self._hash_password(password, salt)

            if hashed_password != stored_hash:
                # Increment failed attempts
                self._increment_login_attempts(user_id)
                logger.warning(f"Authentication failed: Invalid password for user {user_id}")
                return None

            # Generate session token
            session_token = self._generate_session_token()
            session_expires = self._get_current_timestamp() + self.session_duration

            # Update user session data
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET session_token = :token, session_expires = :expires, last_login = :login, login_attempts = :attempts',
                ExpressionAttributeValues={
                    ':token': session_token,
                    ':expires': session_expires,
                    ':login': self._get_current_timestamp(),
                    ':attempts': 0  # Reset attempts on successful login
                }
            )

            logger.info(f"User {user_id} authenticated successfully")
            return session_token

        except ClientError as e:
            logger.error(f"AWS error authenticating user {user_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error authenticating user {user_id}: {str(e)}")
            return None

    def validate_session(self, user_id: str, session_token: str) -> bool:
        """
        Validate user session token.

        Args:
            user_id (str): User identifier
            session_token (str): Session token to validate

        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            response = self.table.get_item(Key={'user_id': user_id})

            if 'Item' not in response:
                return False

            user = response['Item']

            # Check if session token matches
            if user.get('session_token') != session_token:
                logger.warning(f"Session validation failed: Token mismatch for user {user_id}")
                return False

            # Check if session has expired
            if user.get('session_expires', 0) < self._get_current_timestamp():
                logger.warning(f"Session validation failed: Expired session for user {user_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating session for {user_id}: {str(e)}")
            return False

    def logout_user(self, user_id: str) -> bool:
        """
        Logout user by invalidating session token.

        Args:
            user_id (str): User identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET session_token = :null, session_expires = :zero',
                ExpressionAttributeValues={
                    ':null': None,
                    ':zero': 0
                }
            )

            logger.info(f"User {user_id} logged out successfully")
            return True

        except Exception as e:
            logger.error(f"Error logging out user {user_id}: {str(e)}")
            return False
