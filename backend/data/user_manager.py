"""
User Manager Module
Handles user profiles, subscriptions, onboarding, milestones, and art tokens.
All operations target the noisemaker-users DynamoDB table.
Milestone history is stored in the noisemaker-milestones table.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json

from .dynamodb_client import dynamodb_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserManager:
    """
    Comprehensive user management system for subscription and profile data.
    
    Features:
    - User profile management
    - Subscription tier handling
    - Usage tracking and limits
    - Account status management
    - Integration with auth system
    """
    
    def __init__(self):
        """Initialize user manager."""
        self.table_name = 'noisemaker-users'
        
        # Subscription tier configurations
        self.subscription_tiers = {
    'talent': {
        'monthly_price': 25,
        'max_active_songs': 3,
        'platforms_limit': 2,
        'fire_mode_enabled': True,
        'ai_captions_enabled': True,
        'milestone_notifications': True
    },
    'star': {
        'monthly_price': 40,
        'max_active_songs': 3,
        'platforms_limit': 5,
        'fire_mode_enabled': True,
        'ai_captions_enabled': True,
        'milestone_notifications': True,
        'priority_support': True
    },
    'legend': {
        'monthly_price': 60,
        'max_active_songs': 3,
        'platforms_limit': 8,
        'fire_mode_enabled': True,
        'ai_captions_enabled': True,
        'milestone_notifications': True,
        'priority_support': True,
        'custom_branding': True
    }
}
        
        logger.info("User manager initialized")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile information.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[Dict[str, Any]]: User profile or None if not found
        """
        try:
            key = {'user_id': user_id}
            user_data = dynamodb_client.get_item(self.table_name, key)
            
            if user_data:
                # Remove sensitive information
                safe_user_data = {k: v for k, v in user_data.items() 
                                if k not in ['password_hash', 'password_salt']}
                logger.debug(f"Retrieved profile for user {user_id}")
                return safe_user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user profile information.
        
        Args:
            user_id (str): User identifier
            updates (Dict[str, Any]): Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove sensitive fields that shouldn't be updated this way
            safe_updates = {k: v for k, v in updates.items() 
                          if k not in ['password_hash', 'password_salt', 'user_id']}
            
            key = {'user_id': user_id}
            success = dynamodb_client.update_item(self.table_name, key, safe_updates)
            
            if success:
                logger.info(f"Updated profile for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating user profile for {user_id}: {str(e)}")
            return False
    
    def get_user_subscription_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's subscription information and limits.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[Dict[str, Any]]: Subscription info or None if not found
        """
        try:
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return None
            
            subscription_tier = user_data.get('subscription_tier', 'talent')
            tier_config = self.subscription_tiers.get(subscription_tier, self.subscription_tiers['talent'])
            
            subscription_info = {
                'user_id': user_id,
                'subscription_tier': subscription_tier,
                'tier_config': tier_config,
                'account_status': user_data.get('account_status', 'active'),
                'subscription_start': user_data.get('subscription_start', ''),
                'subscription_expires': user_data.get('subscription_expires', ''),
                'usage_this_month': self._get_usage_this_month(user_id),
                'limits': {
                    'max_active_songs': tier_config['max_active_songs'],
                    'platforms_limit': tier_config['platforms_limit']
                }
            }
            
            return subscription_info
            
        except Exception as e:
            logger.error(f"Error getting subscription info for user {user_id}: {str(e)}")
            return None
    
    def update_subscription_tier(self, user_id: str, new_tier: str) -> bool:
        """
        Update user's subscription tier.
        
        Args:
            user_id (str): User identifier
            new_tier (str): New subscription tier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if new_tier not in self.subscription_tiers:
                logger.error(f"Invalid subscription tier: {new_tier}")
                return False
            
            updates = {
                'subscription_tier': new_tier,
                'subscription_updated': datetime.now().isoformat()
            }
            
            success = self.update_user_profile(user_id, updates)
            
            if success:
                logger.info(f"Updated subscription tier to {new_tier} for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating subscription tier for user {user_id}: {str(e)}")
            return False
    
    def track_post_usage(self, user_id: str, post_count: int = 1) -> bool:
        """
        Track user's post usage for the current month.
        
        Args:
            user_id (str): User identifier
            post_count (int): Number of posts to add to usage
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_month = datetime.now().strftime('%Y-%m')
            usage_key = f"usage_{current_month}"
            
            # Get current usage
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return False
            
            current_usage = user_data.get(usage_key, 0)
            new_usage = current_usage + post_count
            
            updates = {
                usage_key: new_usage,
                'last_post_date': datetime.now().isoformat()
            }
            
            return self.update_user_profile(user_id, updates)
            
        except Exception as e:
            logger.error(f"Error tracking post usage for user {user_id}: {str(e)}")
            return False
    
    def check_usage_limits(self, user_id: str, requested_posts: int = 1) -> Dict[str, Any]:
        """
        Check if user can make requested number of posts within their limits.
        
        Args:
            user_id (str): User identifier
            requested_posts (int): Number of posts requested
            
        Returns:
            Dict[str, Any]: Usage check results
        """
        try:
            subscription_info = self.get_user_subscription_info(user_id)
            if not subscription_info:
                return {
                    'allowed': False,
                    'reason': 'User subscription info not found'
                }
            
            # Check account status
            if subscription_info['account_status'] != 'active':
                return {
                    'allowed': False,
                    'reason': f"Account status: {subscription_info['account_status']}"
                }

            # No monthly limit - posts determined by daily schedule (1 post Mon-Thu/Sun, 2 posts Fri-Sat per platform)
            # Posts are automatically calculated based on subscription tier's platforms_limit
            current_usage = subscription_info['usage_this_month']

            return {
                'allowed': True,
                'current_usage': current_usage,
                'note': 'Posts limited by daily schedule, not monthly cap'
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {str(e)}")
            return {
                'allowed': False,
                'reason': f'Error checking limits: {str(e)}'
            }
    
    def _get_usage_this_month(self, user_id: str) -> int:
        """
        Get user's post usage for current month.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            int: Posts used this month
        """
        try:
            current_month = datetime.now().strftime('%Y-%m')
            usage_key = f"usage_{current_month}"
            
            user_data = self.get_user_profile(user_id)
            if user_data:
                return user_data.get(usage_key, 0)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error getting usage for user {user_id}: {str(e)}")
            return 0
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Set user preferences and settings.
        
        Args:
            user_id (str): User identifier
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate preferences structure
            valid_preferences = {
                'timezone': preferences.get('timezone', 'America/New_York'),
                'platforms_enabled': preferences.get('platforms_enabled', ['instagram']),
                'post_times_preferred': preferences.get('post_times_preferred', ['morning', 'evening']),
                'ai_captions_enabled': preferences.get('ai_captions_enabled', True),
                'milestone_notifications': preferences.get('milestone_notifications', True),
                'notification_phone': preferences.get('notification_phone', ''),
                'notification_email': preferences.get('notification_email', ''),
                'sms_enabled': preferences.get('sms_enabled', False)
            }
            
            updates = {
                'preferences': valid_preferences,
                'preferences_updated': datetime.now().isoformat()
            }
            
            success = self.update_user_profile(user_id, updates)
            
            if success:
                logger.info(f"Updated preferences for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting preferences for user {user_id}: {str(e)}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences with defaults.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Dict[str, Any]: User preferences
        """
        try:
            user_data = self.get_user_profile(user_id)
            if user_data and 'preferences' in user_data:
                return user_data['preferences']
            
            # Return default preferences
            return {
                'timezone': 'America/New_York',
                'platforms_enabled': ['instagram'],
                'post_times_preferred': ['morning', 'evening'],
                'ai_captions_enabled': True,
                'milestone_notifications': True,
                'notification_phone': '',
                'notification_email': '',
                'sms_enabled': False
            }
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
            return {}
    
    def set_user_platform_selection(self, user_id: str, selected_platforms: List[str]) -> Dict[str, Any]:
        """
        Set user's selected social media platforms with validation.
        
        Args:
            user_id (str): User identifier
            selected_platforms (List[str]): List of platform names to enable
            
        Returns:
            Dict[str, Any]: Result with success status and platform info
        """
        try:
            # Import platform validation (using direct list for now)
            ALL_PLATFORMS = ['instagram', 'twitter', 'facebook', 'youtube', 'tiktok', 'reddit', 'discord', 'threads']
            
            def validate_platform_selection(platforms):
                return {p: p in ALL_PLATFORMS for p in platforms}
            
            # Validate platform selection
            validation_results = validate_platform_selection(selected_platforms)
            invalid_platforms = [p for p, valid in validation_results.items() if not valid]
            
            if invalid_platforms:
                return {
                    'success': False,
                    'error': f"Invalid platforms: {invalid_platforms}",
                    'valid_platforms': ALL_PLATFORMS
                }
            
            # Check subscription limits
            subscription_info = self.get_user_subscription_info(user_id)
            if not subscription_info:
                return {
                    'success': False,
                    'error': 'User subscription info not found'
                }
            
            platform_limit = subscription_info['limits']['platforms_limit']
            
            if len(selected_platforms) > platform_limit:
                return {
                    'success': False,
                    'error': f'Platform limit exceeded. Tier allows {platform_limit} platforms, you selected {len(selected_platforms)}',
                    'platform_limit': platform_limit,
                    'selected_count': len(selected_platforms)
                }
            
            # Update user preferences
            current_preferences = self.get_user_preferences(user_id)
            current_preferences['platforms_enabled'] = selected_platforms
            
            success = self.set_user_preferences(user_id, current_preferences)
            
            if success:
                return {
                    'success': True,
                    'platforms_enabled': selected_platforms,
                    'platform_count': len(selected_platforms),
                    'platform_limit': platform_limit,
                    'remaining_slots': platform_limit - len(selected_platforms)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save platform preferences'
                }
                
        except Exception as e:
            logger.error(f"Error setting platform selection for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
    
    def get_user_platform_selection(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current platform selection with subscription context.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Dict[str, Any]: Current platform selection and limits
        """
        try:
            ALL_PLATFORMS = ['instagram', 'twitter', 'facebook', 'youtube', 'tiktok', 'reddit', 'discord', 'threads']
            
            preferences = self.get_user_preferences(user_id)
            subscription_info = self.get_user_subscription_info(user_id)
            
            if not subscription_info:
                return {
                    'success': False,
                    'error': 'User subscription info not found'
                }
            
            enabled_platforms = preferences.get('platforms_enabled', ['instagram'])
            platform_limit = subscription_info['limits']['platforms_limit']
            
            return {
                'success': True,
                'platforms_enabled': enabled_platforms,
                'platform_count': len(enabled_platforms),
                'platform_limit': platform_limit,
                'remaining_slots': platform_limit - len(enabled_platforms),
                'all_available_platforms': ALL_PLATFORMS,
                'subscription_tier': subscription_info['subscription_tier']
            }
            
        except Exception as e:
            logger.error(f"Error getting platform selection for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
    
    def add_platform_to_user(self, user_id: str, platform: str) -> Dict[str, Any]:
        """
        Add a single platform to user's selection.
        
        Args:
            user_id (str): User identifier
            platform (str): Platform name to add
            
        Returns:
            Dict[str, Any]: Result with updated platform list
        """
        try:
            current_selection = self.get_user_platform_selection(user_id)
            
            if not current_selection['success']:
                return current_selection
            
            current_platforms = current_selection['platforms_enabled']
            
            if platform in current_platforms:
                return {
                    'success': False,
                    'error': f'Platform {platform} already enabled',
                    'platforms_enabled': current_platforms
                }
            
            new_platforms = current_platforms + [platform]
            return self.set_user_platform_selection(user_id, new_platforms)
            
        except Exception as e:
            logger.error(f"Error adding platform {platform} for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
    
    def remove_platform_from_user(self, user_id: str, platform: str) -> Dict[str, Any]:
        """
        Remove a platform from user's selection.
        
        Args:
            user_id (str): User identifier
            platform (str): Platform name to remove
            
        Returns:
            Dict[str, Any]: Result with updated platform list
        """
        try:
            current_selection = self.get_user_platform_selection(user_id)
            
            if not current_selection['success']:
                return current_selection
            
            current_platforms = current_selection['platforms_enabled']
            
            if platform not in current_platforms:
                return {
                    'success': False,
                    'error': f'Platform {platform} not currently enabled',
                    'platforms_enabled': current_platforms
                }
            
            new_platforms = [p for p in current_platforms if p != platform]
            return self.set_user_platform_selection(user_id, new_platforms)
            
        except Exception as e:
            logger.error(f"Error removing platform {platform} for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }

    def mark_spotify_connected(self, user_id: str, artist_id: str) -> Dict[str, Any]:
        """
        Mark that user has connected their Spotify account.
        Called after successful OAuth flow.

        Args:
            user_id (str): User identifier
            artist_id (str): Spotify artist ID

        Returns:
            Dict: Success status
        """
        try:
            logger.info(f"Marking Spotify connected for user: {user_id}, artist: {artist_id}")

            updates = {
                'spotify_connected': True,
                'spotify_artist_id': artist_id,
                'spotify_connection_date': datetime.now().isoformat()
            }

            success = self.update_user_profile(user_id, updates)

            if success:
                logger.info(f"Spotify connected for user: {user_id}")
                return {
                    'success': True,
                    'message': 'Spotify account connected successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update user profile'
                }

        except Exception as e:
            logger.error(f"Error marking Spotify connected for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def deactivate_user_account(self, user_id: str, reason: str = 'user_request') -> bool:
        """
        Deactivate user account.
        
        Args:
            user_id (str): User identifier
            reason (str): Reason for deactivation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            updates = {
                'account_status': 'inactive',
                'deactivated_at': datetime.now().isoformat(),
                'deactivation_reason': reason
            }
            
            success = self.update_user_profile(user_id, updates)
            
            if success:
                logger.info(f"Deactivated account for user {user_id}, reason: {reason}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deactivating account for user {user_id}: {str(e)}")
            return False
    
    def reactivate_user_account(self, user_id: str) -> bool:
        """
        Reactivate user account.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            updates = {
                'account_status': 'active',
                'reactivated_at': datetime.now().isoformat(),
                'deactivation_reason': ''
            }
            
            success = self.update_user_profile(user_id, updates)
            
            if success:
                logger.info(f"Reactivated account for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error reactivating account for user {user_id}: {str(e)}")
            return False

    # ============================================================================
    # ONBOARDING STATUS MANAGEMENT
    # ============================================================================

    # Valid onboarding status values (in order of progression)
    ONBOARDING_STATUSES = [
        'account_created',      # Just signed up (OAuth or email)
        'tier_pending',         # Needs to select subscription tier
        'payment_pending',      # Selected tier, awaiting Stripe payment
        'platforms_pending',    # Paid, needs to select platforms
        'platforms_connecting', # Selected platforms, connecting OAuth
        'songs_pending',        # Platforms connected, needs to add songs
        'complete'              # Fully onboarded, ready for dashboard
    ]

    def initialize_onboarding(self, user_id: str, initial_status: str = 'tier_pending') -> Dict[str, Any]:
        """
        Initialize onboarding tracking for a new user.
        Called immediately after user account creation.

        Args:
            user_id: User's unique identifier
            initial_status: Starting onboarding status (default: tier_pending)

        Returns:
            Dict with success status and onboarding info
        """
        try:
            logger.info(f"Initializing onboarding for user: {user_id}")

            if initial_status not in self.ONBOARDING_STATUSES:
                return {
                    'success': False,
                    'error': f'Invalid onboarding status: {initial_status}'
                }

            key = {'user_id': user_id}
            updates = {
                'onboarding_status': initial_status,
                'onboarding_started_at': datetime.utcnow().isoformat(),
                'onboarding_last_updated': datetime.utcnow().isoformat(),
                'onboarding_completed_at': ''
            }

            success = dynamodb_client.update_item(self.table_name, key, updates)

            if success:
                logger.info(f"Onboarding initialized for user: {user_id} with status: {initial_status}")
                return {
                    'success': True,
                    'onboarding_status': initial_status,
                    'message': 'Onboarding initialized'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initialize onboarding'
                }

        except Exception as e:
            logger.error(f"Error initializing onboarding for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_onboarding_status(self, user_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update user's onboarding status.

        Args:
            user_id: User's unique identifier
            new_status: New onboarding status value

        Returns:
            Dict with success status and updated info
        """
        try:
            logger.info(f"Updating onboarding status for user {user_id} to: {new_status}")

            if new_status not in self.ONBOARDING_STATUSES:
                return {
                    'success': False,
                    'error': f'Invalid onboarding status: {new_status}',
                    'valid_statuses': self.ONBOARDING_STATUSES
                }

            key = {'user_id': user_id}
            updates = {
                'onboarding_status': new_status,
                'onboarding_last_updated': datetime.utcnow().isoformat()
            }

            # If completing onboarding, set completion timestamp
            if new_status == 'complete':
                updates['onboarding_completed_at'] = datetime.utcnow().isoformat()

            success = dynamodb_client.update_item(self.table_name, key, updates)

            if success:
                logger.info(f"Onboarding status updated for user {user_id}: {new_status}")
                return {
                    'success': True,
                    'onboarding_status': new_status,
                    'message': f'Onboarding status updated to {new_status}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update onboarding status'
                }

        except Exception as e:
            logger.error(f"Error updating onboarding status for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current onboarding status and progress.

        Args:
            user_id: User's unique identifier

        Returns:
            Dict with onboarding status info
        """
        try:
            user_data = self.get_user_profile(user_id)

            if not user_data:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            current_status = user_data.get('onboarding_status', 'account_created')

            # Calculate progress percentage
            if current_status in self.ONBOARDING_STATUSES:
                current_index = self.ONBOARDING_STATUSES.index(current_status)
                progress_percent = int((current_index / (len(self.ONBOARDING_STATUSES) - 1)) * 100)
            else:
                progress_percent = 0

            return {
                'success': True,
                'user_id': user_id,
                'onboarding_status': current_status,
                'is_complete': current_status == 'complete',
                'progress_percent': progress_percent,
                'next_step': self._get_next_onboarding_step(current_status),
                'started_at': user_data.get('onboarding_started_at', ''),
                'last_updated': user_data.get('onboarding_last_updated', ''),
                'completed_at': user_data.get('onboarding_completed_at', '')
            }

        except Exception as e:
            logger.error(f"Error getting onboarding status for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_next_onboarding_step(self, current_status: str) -> Optional[str]:
        """Get the next onboarding step based on current status."""
        if current_status not in self.ONBOARDING_STATUSES:
            return 'tier_pending'

        current_index = self.ONBOARDING_STATUSES.index(current_status)
        if current_index < len(self.ONBOARDING_STATUSES) - 1:
            return self.ONBOARDING_STATUSES[current_index + 1]
        return None  # Already complete

    # ============================================================================
    # MILESTONE TRACKING
    # ============================================================================

    # Milestone types and configuration
    MILESTONE_TYPES = {
        # FIRST PAYMENT
        'first_payment': {
            'category': 'payment',
            'description': 'First successful subscription payment',
            'media_type': 'video',
            'one_time': True,
            'threshold': None,  # Triggered by payment event, not a number
        },
        # FOLLOWER GROWTH (relative to signup count)
        'followers_100': {'category': 'followers', 'description': 'Gained 100 followers', 'media_type': 'video', 'one_time': True, 'threshold': 100},
        'followers_250': {'category': 'followers', 'description': 'Gained 250 followers', 'media_type': 'jingle', 'one_time': True, 'threshold': 250},
        'followers_500': {'category': 'followers', 'description': 'Gained 500 followers', 'media_type': 'video', 'one_time': True, 'threshold': 500},
        'followers_750': {'category': 'followers', 'description': 'Gained 750 followers', 'media_type': 'jingle', 'one_time': True, 'threshold': 750},
        'followers_1000': {'category': 'followers', 'description': 'Gained 1,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 1000},
        'followers_1500': {'category': 'followers', 'description': 'Gained 1,500 followers', 'media_type': 'jingle', 'one_time': True, 'threshold': 1500},
        'followers_2000': {'category': 'followers', 'description': 'Gained 2,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 2000},
        'followers_3000': {'category': 'followers', 'description': 'Gained 3,000 followers', 'media_type': 'jingle', 'one_time': True, 'threshold': 3000},
        'followers_5000': {'category': 'followers', 'description': 'Gained 5,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 5000},
        'followers_10000': {'category': 'followers', 'description': 'Gained 10,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 10000},
        'followers_25000': {'category': 'followers', 'description': 'Gained 25,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 25000},
        'followers_50000': {'category': 'followers', 'description': 'Gained 50,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 50000},
        'followers_100000': {'category': 'followers', 'description': 'Gained 100,000 followers', 'media_type': 'video', 'one_time': True, 'threshold': 100000},
        # SONG POPULARITY (per song, can trigger multiple times for different songs)
        'song_popularity_5': {'category': 'popularity', 'description': 'Song reached popularity 5', 'media_type': 'jingle', 'one_time': False, 'threshold': 5},
        'song_popularity_10': {'category': 'popularity', 'description': 'Song reached popularity 10', 'media_type': 'jingle', 'one_time': False, 'threshold': 10},
        'song_popularity_15': {'category': 'popularity', 'description': 'Song reached popularity 15', 'media_type': 'video', 'one_time': False, 'threshold': 15},
        'song_popularity_20': {'category': 'popularity', 'description': 'Song reached popularity 20', 'media_type': 'video', 'one_time': False, 'threshold': 20},
        'song_popularity_25': {'category': 'popularity', 'description': 'Song reached popularity 25', 'media_type': 'video', 'one_time': False, 'threshold': 25},
        'song_popularity_30': {'category': 'popularity', 'description': 'Song reached popularity 30', 'media_type': 'video', 'one_time': False, 'threshold': 30},
        # FIRE MODE
        'first_fire_mode': {'category': 'fire_mode', 'description': 'First song entered Fire Mode', 'media_type': 'video', 'one_time': True, 'threshold': 1},
        'fire_mode_3': {'category': 'fire_mode', 'description': '3 songs have been on fire', 'media_type': 'jingle', 'one_time': True, 'threshold': 3},
        'fire_mode_10': {'category': 'fire_mode', 'description': '10 songs have been on fire', 'media_type': 'video', 'one_time': True, 'threshold': 10},
        # POSTING ACTIVITY
        'posts_100': {'category': 'posts', 'description': '100 posts made', 'media_type': 'jingle', 'one_time': True, 'threshold': 100},
        'posts_500': {'category': 'posts', 'description': '500 posts made', 'media_type': 'video', 'one_time': True, 'threshold': 500},
        'posts_1000': {'category': 'posts', 'description': '1,000 posts made', 'media_type': 'video', 'one_time': True, 'threshold': 1000},
        # LONGEVITY
        'active_3_months': {'category': 'longevity', 'description': '3 months active', 'media_type': 'jingle', 'one_time': True, 'threshold': 90},
        'active_6_months': {'category': 'longevity', 'description': '6 months active', 'media_type': 'video', 'one_time': True, 'threshold': 180},
        'active_1_year': {'category': 'longevity', 'description': '1 year active', 'media_type': 'video', 'one_time': True, 'threshold': 365},
    }

    S3_BUCKET = 'noisemakerpromobydoowopp'

    def initialize_milestones(self, user_id: str) -> Dict[str, Any]:
        """Initialize milestone tracking for a new user."""
        try:
            logger.info(f"Initializing milestones for user: {user_id}")
            key = {'user_id': user_id}
            updates = {
                'pending_milestone': None,
                'total_fire_modes': 0,
                'total_posts': 0,
                'milestones_initialized_at': datetime.utcnow().isoformat()
            }
            success = dynamodb_client.update_item(self.table_name, key, updates)
            if success:
                logger.info(f"Milestones initialized for user: {user_id}")
                return {'success': True, 'message': 'Milestones initialized'}
            return {'success': False, 'error': 'Failed to initialize milestones'}
        except Exception as e:
            logger.error(f"Error initializing milestones for {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def achieve_milestone(self, user_id: str, milestone_type: str, song_id: str = None) -> Dict[str, Any]:
        """
        Mark a milestone as achieved. Writes to milestones table and sets pending_milestone on user profile.
        song_id is required for song_popularity milestones (per-song tracking).
        """
        try:
            logger.info(f"Achieving milestone {milestone_type} for user: {user_id}")
            if milestone_type not in self.MILESTONE_TYPES:
                return {'success': False, 'error': f'Invalid milestone type: {milestone_type}'}

            milestone_config = self.MILESTONE_TYPES[milestone_type]

            # For one_time milestones, check if already achieved
            if milestone_config['one_time']:
                existing = dynamodb_client.get_item(
                    'noisemaker-milestones',
                    {'user_id': user_id, 'milestone_type': milestone_type}
                )
                if existing:
                    logger.info(f"Milestone {milestone_type} already achieved for user {user_id}")
                    return {'success': True, 'already_achieved': True}

            # For per-song milestones, check this specific song
            if milestone_config['category'] == 'popularity' and song_id:
                sk = f"{milestone_type}#{song_id}"
                existing = dynamodb_client.get_item(
                    'noisemaker-milestones',
                    {'user_id': user_id, 'milestone_type': sk}
                )
                if existing:
                    return {'success': True, 'already_achieved': True}
            else:
                sk = milestone_type

            # Write to milestones table
            achieved_at = datetime.utcnow().isoformat()
            milestone_record = {
                'user_id': user_id,
                'milestone_type': sk,
                'category': milestone_config['category'],
                'media_type': milestone_config['media_type'],
                'achieved_at': achieved_at,
                'song_id': song_id
            }
            dynamodb_client.put_item('noisemaker-milestones', milestone_record)

            # Set as pending on user profile (frontend will see this and play the video/jingle)
            video_url = self._get_milestone_video_url(milestone_type)
            self.update_user_profile(user_id, {
                'pending_milestone': {
                    'milestone_type': milestone_type,
                    'description': milestone_config['description'],
                    'media_type': milestone_config['media_type'],
                    'video_url': video_url,
                    'achieved_at': achieved_at,
                    'song_id': song_id
                }
            })

            logger.info(f"Milestone {milestone_type} achieved for user {user_id}")
            return {
                'success': True,
                'milestone_type': milestone_type,
                'video_url': video_url,
                'media_type': milestone_config['media_type']
            }
        except Exception as e:
            logger.error(f"Error achieving milestone {milestone_type} for {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def mark_milestone_video_played(self, user_id: str, milestone_type: str = None) -> Dict[str, Any]:
        """Clear pending milestone after video/jingle has played."""
        try:
            success = self.update_user_profile(user_id, {'pending_milestone': None})
            if success:
                return {'success': True, 'message': 'Milestone video marked as played'}
            return {'success': False, 'error': 'Failed to clear pending milestone'}
        except Exception as e:
            logger.error(f"Error clearing pending milestone for {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_pending_milestone(self, user_id: str) -> Dict[str, Any]:
        """Get pending milestone for user (if any)."""
        try:
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return {'success': False, 'error': 'User not found'}
            pending = user_data.get('pending_milestone')
            if pending:
                return {'success': True, 'has_pending': True, **pending}
            return {'success': True, 'has_pending': False, 'milestone_type': None, 'video_url': None}
        except Exception as e:
            logger.error(f"Error getting pending milestone for {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_milestone_video_url(self, milestone_type: str) -> Optional[str]:
        """Generate presigned S3 URL for milestone video/jingle."""
        try:
            if milestone_type not in self.MILESTONE_TYPES:
                return None
            s3_key = f"Milestones/milestone_{milestone_type}/milestone_{milestone_type}.MP4"
            import boto3
            s3_client = boto3.client('s3', region_name='us-east-2')
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.S3_BUCKET, 'Key': s3_key},
                ExpiresIn=3600
            )
        except Exception as e:
            logger.error(f"Error generating presigned URL for {milestone_type}: {e}")
            return None

    def get_all_active_users(self) -> List[str]:
        """
        Get list of all active user IDs (for system operations).

        Returns:
            List[str]: List of active user IDs
        """
        try:
            # This is a scan operation - use carefully
            users = dynamodb_client.scan_table(
                self.table_name,
                filter_expression='account_status = :status',
                expression_values={':status': 'active'}
            )

            user_ids = [user['user_id'] for user in users if 'user_id' in user]

            logger.info(f"Retrieved {len(user_ids)} active users")
            return user_ids

        except Exception as e:
            logger.error(f"Error getting all active users: {str(e)}")
            return []

    # ============================================================================
    # FRANK'S GARAGE - ART TOKENS
    # ============================================================================

    # Token configuration
    ART_TOKENS_SIGNUP = 3       # Tokens awarded on signup
    ART_TOKENS_PER_SONG = 3     # Tokens awarded per song upload
    ART_TOKENS_MAX = 12         # Maximum tokens from song uploads

    def initialize_art_tokens(self, user_id: str, initial_tokens: int = 3) -> Dict[str, Any]:
        """
        Initialize art tokens for a new user (called on signup).
        Awards initial signup bonus tokens.

        Args:
            user_id: User's unique identifier
            initial_tokens: Number of tokens to award (default: 3)

        Returns:
            Dict with success status and token info
        """
        try:
            logger.info(f"Initializing art tokens for user: {user_id} with {initial_tokens} tokens")

            key = {'user_id': user_id}
            updates = {
                'art_tokens': initial_tokens,
                'art_tokens_total_earned': initial_tokens,
                'art_tokens_total_spent': 0,
                'art_tokens_from_songs': 0,
                'art_tokens_initialized_at': datetime.utcnow().isoformat(),
                'art_tokens_last_updated': datetime.utcnow().isoformat()
            }

            success = dynamodb_client.update_item(self.table_name, key, updates)

            if success:
                logger.info(f"Art tokens initialized for user: {user_id} - Balance: {initial_tokens}")
                return {
                    'success': True,
                    'message': f'Awarded {initial_tokens} art tokens for signup',
                    'art_tokens': initial_tokens
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initialize art tokens'
                }

        except Exception as e:
            logger.error(f"Error initializing art tokens for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_art_tokens(self, user_id: str) -> int:
        """
        Get user's current art token balance.

        Args:
            user_id: User's unique identifier

        Returns:
            int: Current token balance (0 if not found)
        """
        try:
            user_data = self.get_user_profile(user_id)
            if user_data:
                return int(user_data.get('art_tokens', 0))
            return 0

        except Exception as e:
            logger.error(f"Error getting art tokens for {user_id}: {str(e)}")
            return 0

    def get_art_token_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed art token information for a user.

        Args:
            user_id: User's unique identifier

        Returns:
            Dict with full token info
        """
        try:
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            return {
                'success': True,
                'user_id': user_id,
                'art_tokens': int(user_data.get('art_tokens', 0)),
                'art_tokens_total_earned': int(user_data.get('art_tokens_total_earned', 0)),
                'art_tokens_total_spent': int(user_data.get('art_tokens_total_spent', 0)),
                'art_tokens_from_songs': int(user_data.get('art_tokens_from_songs', 0)),
                'art_tokens_last_updated': user_data.get('art_tokens_last_updated', '')
            }

        except Exception as e:
            logger.error(f"Error getting art token info for {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def add_art_tokens_for_song(self, user_id: str) -> Dict[str, Any]:
        """
        Award art tokens when user uploads a song.
        Awards 3 tokens per song, but song-based tokens are capped at 12.

        Args:
            user_id: User's unique identifier

        Returns:
            Dict with success status and new balance
        """
        try:
            logger.info(f"Awarding art tokens for song upload to user: {user_id}")

            # Get current token info
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            current_tokens = int(user_data.get('art_tokens', 0))
            tokens_from_songs = int(user_data.get('art_tokens_from_songs', 0))
            total_earned = int(user_data.get('art_tokens_total_earned', 0))

            # Check if song-based tokens are at max (12 from songs)
            if tokens_from_songs >= self.ART_TOKENS_MAX:
                logger.info(f"User {user_id} already at max song tokens ({self.ART_TOKENS_MAX})")
                return {
                    'success': True,
                    'tokens_awarded': 0,
                    'art_tokens': current_tokens,
                    'message': f'Already at maximum tokens from songs ({self.ART_TOKENS_MAX})',
                    'at_song_cap': True
                }

            # Calculate tokens to award (3, but respect cap)
            tokens_to_add = min(self.ART_TOKENS_PER_SONG, self.ART_TOKENS_MAX - tokens_from_songs)

            # Update token counts
            new_balance = current_tokens + tokens_to_add
            new_from_songs = tokens_from_songs + tokens_to_add
            new_total_earned = total_earned + tokens_to_add

            key = {'user_id': user_id}
            updates = {
                'art_tokens': new_balance,
                'art_tokens_from_songs': new_from_songs,
                'art_tokens_total_earned': new_total_earned,
                'art_tokens_last_updated': datetime.utcnow().isoformat()
            }

            success = dynamodb_client.update_item(self.table_name, key, updates)

            if success:
                logger.info(f"Awarded {tokens_to_add} art tokens to user {user_id} for song upload. New balance: {new_balance}")
                return {
                    'success': True,
                    'tokens_awarded': tokens_to_add,
                    'art_tokens': new_balance,
                    'art_tokens_from_songs': new_from_songs,
                    'message': f'Awarded {tokens_to_add} art tokens for song upload',
                    'at_song_cap': new_from_songs >= self.ART_TOKENS_MAX
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to award art tokens'
                }

        except Exception as e:
            logger.error(f"Error awarding art tokens for song to {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def deduct_art_token(self, user_id: str) -> Dict[str, Any]:
        """
        Deduct one art token for a free download.

        Args:
            user_id: User's unique identifier

        Returns:
            Dict with success status and new balance
        """
        try:
            logger.info(f"Deducting art token for free download from user: {user_id}")

            # Get current balance
            user_data = self.get_user_profile(user_id)
            if not user_data:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            current_tokens = int(user_data.get('art_tokens', 0))
            total_spent = int(user_data.get('art_tokens_total_spent', 0))

            # Check if user has tokens
            if current_tokens < 1:
                logger.warning(f"User {user_id} has no art tokens available")
                return {
                    'success': False,
                    'error': 'No art tokens available',
                    'art_tokens': 0
                }

            # Deduct token
            new_balance = current_tokens - 1
            new_total_spent = total_spent + 1

            key = {'user_id': user_id}
            updates = {
                'art_tokens': new_balance,
                'art_tokens_total_spent': new_total_spent,
                'art_tokens_last_updated': datetime.utcnow().isoformat()
            }

            success = dynamodb_client.update_item(self.table_name, key, updates)

            if success:
                logger.info(f"Deducted 1 art token from user {user_id}. New balance: {new_balance}")
                return {
                    'success': True,
                    'tokens_deducted': 1,
                    'art_tokens': new_balance,
                    'message': 'Token deducted for free download'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to deduct art token'
                }

        except Exception as e:
            logger.error(f"Error deducting art token from {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global user manager instance
user_manager = UserManager()


# Convenience functions for easy integration
def get_user_info(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile information."""
    return user_manager.get_user_profile(user_id)


def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user subscription information."""
    return user_manager.get_user_subscription_info(user_id)


def check_user_limits(user_id: str, posts: int = 1) -> Dict[str, Any]:
    """Check user's usage limits."""
    return user_manager.check_usage_limits(user_id, posts)


def track_user_posts(user_id: str, count: int = 1) -> bool:
    """Track user's post usage."""
    return user_manager.track_post_usage(user_id, count)


def set_user_platforms(user_id: str, platforms: List[str]) -> Dict[str, Any]:
    """Set user's platform selection."""
    return user_manager.set_user_platform_selection(user_id, platforms)


def get_user_platforms(user_id: str) -> Dict[str, Any]:
    """Get user's current platform selection."""
    return user_manager.get_user_platform_selection(user_id)


def add_user_platform(user_id: str, platform: str) -> Dict[str, Any]:
    """Add a platform to user's selection."""
    return user_manager.add_platform_to_user(user_id, platform)


def remove_user_platform(user_id: str, platform: str) -> Dict[str, Any]:
    """Remove a platform from user's selection."""
    return user_manager.remove_platform_from_user(user_id, platform)


# Onboarding convenience functions
def init_user_onboarding(user_id: str, initial_status: str = 'tier_pending') -> Dict[str, Any]:
    """Initialize onboarding for a new user."""
    return user_manager.initialize_onboarding(user_id, initial_status)


def update_user_onboarding(user_id: str, new_status: str) -> Dict[str, Any]:
    """Update user's onboarding status."""
    return user_manager.update_onboarding_status(user_id, new_status)


def get_user_onboarding(user_id: str) -> Dict[str, Any]:
    """Get user's onboarding status and progress."""
    return user_manager.get_onboarding_status(user_id)


# Milestone convenience functions
def init_user_milestones(user_id: str) -> Dict[str, Any]:
    """Initialize milestone tracking for a new user."""
    return user_manager.initialize_milestones(user_id)


def achieve_user_milestone(user_id: str, milestone_type: str, song_id: str = None) -> Dict[str, Any]:
    """Mark a milestone as achieved for a user."""
    return user_manager.achieve_milestone(user_id, milestone_type, song_id)


def mark_milestone_viewed(user_id: str, milestone_type: str = None) -> Dict[str, Any]:
    """Mark a milestone video as played."""
    return user_manager.mark_milestone_video_played(user_id, milestone_type)


def get_user_pending_milestone(user_id: str) -> Dict[str, Any]:
    """Get user's next pending milestone."""
    return user_manager.get_pending_milestone(user_id)


# Frank's Garage art token convenience functions
def init_user_art_tokens(user_id: str, initial_tokens: int = 3) -> Dict[str, Any]:
    """Initialize art tokens for a new user (called on signup)."""
    return user_manager.initialize_art_tokens(user_id, initial_tokens)


def get_user_art_tokens(user_id: str) -> int:
    """Get user's current art token balance."""
    return user_manager.get_art_tokens(user_id)


def get_user_art_token_info(user_id: str) -> Dict[str, Any]:
    """Get detailed art token information for a user."""
    return user_manager.get_art_token_info(user_id)


def award_art_tokens_for_song(user_id: str) -> Dict[str, Any]:
    """Award art tokens when user uploads a song (3 tokens, max 12 from songs)."""
    return user_manager.add_art_tokens_for_song(user_id)


def deduct_user_art_token(user_id: str) -> Dict[str, Any]:
    """Deduct one art token for a free download."""
    return user_manager.deduct_art_token(user_id)
