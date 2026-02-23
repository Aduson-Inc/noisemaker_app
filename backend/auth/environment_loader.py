"""
Environment Variable Loader Module
Centralized AWS Parameter Store integration for NOiSEMaKER.
All app secrets are stored under /noisemaker/ path.

Version: 2.0
"""

import boto3
import logging
from typing import Dict, Optional, Any
from botocore.exceptions import ClientError, NoCredentialsError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_PATH = "/noisemaker"


class EnvironmentLoader:
    """
    Centralized parameter loader using AWS Systems Manager Parameter Store.
    All secrets stored under /noisemaker/ path.
    """
    
    def __init__(self):
        try:
            self.ssm_client = boto3.client('ssm', region_name='us-east-2')
            self._cache = {}
            logger.info("Environment loader initialized")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter from /noisemaker/{key}."""
        if key in self._cache:
            return self._cache[key]
        
        try:
            path = f"{BASE_PATH}/{key}"
            response = self.ssm_client.get_parameter(
                Name=path,
                WithDecryption=True
            )
            value = response['Parameter']['Value']
            self._cache[key] = value
            logger.info(f"Retrieved parameter: {key}")
            return value
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                logger.warning(f"Parameter not found: {key}, using default")
                return default
            logger.error(f"Error getting {key}: {str(e)}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error getting {key}: {str(e)}")
            return default
    
    def get_all(self) -> Dict[str, str]:
        """Get all parameters under /noisemaker/."""
        try:
            params = {}
            paginator = self.ssm_client.get_paginator('get_parameters_by_path')
            
            for page in paginator.paginate(
                Path=BASE_PATH,
                Recursive=True,
                WithDecryption=True
            ):
                for param in page['Parameters']:
                    key = param['Name'].replace(f"{BASE_PATH}/", "")
                    params[key] = param['Value']
                    self._cache[key] = param['Value']
            
            logger.info(f"Retrieved {len(params)} parameters")
            return params
        except Exception as e:
            logger.error(f"Error getting all parameters: {str(e)}")
            return {}
    
    def clear_cache(self):
        """Clear the parameter cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stripe_config(self) -> Dict[str, str]:
        """Get all Stripe configuration."""
        return {
            'secret_key': self.get('stripe_secret_key', ''),
            'publishable_key': self.get('stripe_publishable_key', ''),
            'webhook_secret': self.get('stripe_webhook_secret', ''),
            'price_talent': self.get('stripe_price_talent', ''),
            'price_star': self.get('stripe_price_star', ''),
            'price_legend': self.get('stripe_price_legend', ''),
            'price_artwork_single': self.get('stripe_price_artwork_single', ''),
            'price_artwork_5pack': self.get('stripe_price_artwork_5pack', ''),
            'price_artwork_15pack': self.get('stripe_price_artwork_15pack', ''),
        }
    
    def get_platform_credentials(self, platform: str) -> Dict[str, str]:
        """Get OAuth credentials for a platform."""
        return {
            'client_id': self.get(f'{platform}_client_id', ''),
            'client_secret': self.get(f'{platform}_client_secret', ''),
        }
    
    def get_grok_api_key(self) -> str:
        return self.get('grok_api_key', '')
    
    def get_huggingface_token(self) -> str:
        return self.get('huggingface_token', '')
    
    def get_jwt_secret(self) -> str:
        secret = self.get('jwt_secret_key', '')
        if not secret:
            raise RuntimeError("JWT secret key not found in Parameter Store.")
        return secret
    
    def get_discord_webhook_url(self) -> str:
        return self.get('discord_webhook_url', '')


# Global instance
env_loader = EnvironmentLoader()


def get_param(key: str, default: Any = None) -> Any:
    return env_loader.get(key, default)


def get_stripe_config() -> Dict[str, str]:
    return env_loader.get_stripe_config()


def get_platform_credentials(platform: str) -> Dict[str, str]:
    return env_loader.get_platform_credentials(platform)
