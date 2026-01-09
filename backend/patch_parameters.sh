#!/bin/bash

# ============================================
# NOiSEMaKER Parameter Store Migration Script
# Migrates from /users/tresch/ and /spotify-promo/ to /noisemaker/
# ============================================

set -e
BACKEND_DIR=~/projects/backend

echo "Starting parameter migration..."

# ============================================
# 1. REPLACE environment_loader.py
# ============================================
echo "1/8 Replacing environment_loader.py..."

cat << 'ENVLOADER' > $BACKEND_DIR/auth/environment_loader.py
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
        return self.get('jwt_secret_key', 'fallback-secret-for-dev')
    
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
ENVLOADER

echo "   Done."

# ============================================
# 2. UPDATE middleware/auth.py
# ============================================
echo "2/8 Updating middleware/auth.py..."

sed -i "s|get_app_parameter('jwt-secret-key'|env_loader.get_jwt_secret(|g" $BACKEND_DIR/middleware/auth.py

echo "   Done."

# ============================================
# 3. UPDATE data/platform_oauth_manager.py
# ============================================
echo "3/8 Updating data/platform_oauth_manager.py..."

sed -i "s|Name=f'/spotify-promo/{platform}/oauth-client-id'|Name=f'/noisemaker/{platform}_client_id'|g" $BACKEND_DIR/data/platform_oauth_manager.py
sed -i "s|Name=f'/spotify-promo/{platform}/oauth-client-secret'|Name=f'/noisemaker/{platform}_client_secret'|g" $BACKEND_DIR/data/platform_oauth_manager.py

echo "   Done."

# ============================================
# 4. UPDATE content/caption_generator.py
# ============================================
echo "4/8 Updating content/caption_generator.py..."

sed -i "s|'/spotify-promo/grok-api-key'|'/noisemaker/grok_api_key'|g" $BACKEND_DIR/content/caption_generator.py
sed -i "s|'/spotify-promo/grok-api-url'|'/noisemaker/grok_api_url'|g" $BACKEND_DIR/content/caption_generator.py

echo "   Done."

# ============================================
# 5. UPDATE content/content_integration.py
# ============================================
echo "5/8 Updating content/content_integration.py..."

sed -i "s|'/spotify-promo/content-generation-queue-url'|'/noisemaker/content_generation_queue_url'|g" $BACKEND_DIR/content/content_integration.py

echo "   Done."

# ============================================
# 6. UPDATE community/reddit_engagement.py
# ============================================
echo "6/8 Updating community/reddit_engagement.py..."

sed -i "s|'/spotify-promo/reddit/client-id'|'/noisemaker/reddit_client_id'|g" $BACKEND_DIR/community/reddit_engagement.py
sed -i "s|'/spotify-promo/reddit/client-secret'|'/noisemaker/reddit_client_secret'|g" $BACKEND_DIR/community/reddit_engagement.py
sed -i "s|'/spotify-promo/reddit/user-agent'|'/noisemaker/reddit_user_agent'|g" $BACKEND_DIR/community/reddit_engagement.py

echo "   Done."

# ============================================
# 7. UPDATE community/discord_engagement.py
# ============================================
echo "7/8 Updating community/discord_engagement.py..."

sed -i "s|'/spotify-promo/discord/bot-token'|'/noisemaker/discord_bot_token'|g" $BACKEND_DIR/community/discord_engagement.py

echo "   Done."

# ============================================
# 8. UPDATE marketplace/daily_album_art_generator.py
# ============================================
echo "8/8 Updating marketplace/daily_album_art_generator.py..."

# This file uses env_loader.get_user_parameters - needs to use get_all() instead
sed -i "s|env_loader.get_user_parameters(USER_ID)|env_loader.get_all()|g" $BACKEND_DIR/marketplace/daily_album_art_generator.py

echo "   Done."

echo ""
echo "============================================"
echo "Migration complete!"
echo "============================================"
echo ""
echo "Files updated:"
echo "  - auth/environment_loader.py (replaced)"
echo "  - middleware/auth.py"
echo "  - data/platform_oauth_manager.py"
echo "  - content/caption_generator.py"
echo "  - content/content_integration.py"
echo "  - community/reddit_engagement.py"
echo "  - community/discord_engagement.py"
echo "  - marketplace/daily_album_art_generator.py"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Test locally"
echo "  3. Commit: git add -A && git commit -m 'refactor: Migrate to /noisemaker/ parameter path'"
echo "  4. Push and redeploy backend"
