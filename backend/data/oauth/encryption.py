"""
Token Encryption Module
Handles encryption and decryption of OAuth tokens using Fernet symmetric encryption.
Encryption key is loaded from AWS SSM Parameter Store.
"""

import os
import logging
import boto3
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class TokenEncryption:
    """Handles encryption and decryption of OAuth tokens."""

    def __init__(self):
        """Initialize encryption by loading key from AWS SSM Parameter Store."""
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')
        ssm_client = boto3.client('ssm', region_name=region)
        param_name = '/noisemaker/oauth_encryption_key'

        try:
            response = ssm_client.get_parameter(
                Name=param_name,
                WithDecryption=True
            )
            key_value = response['Parameter']['Value']
            encryption_key = key_value.encode('utf-8')
            Fernet(encryption_key)  # Validate key format
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
