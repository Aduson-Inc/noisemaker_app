"""
Configuration Package
Centralized configuration management for the Spotify promotion system.

Author: Senior Python Backend Engineer
"""

from .platform_config import (
    SUPPORTED_PLATFORMS,
    ALL_PLATFORMS,
    get_platform_list,
    get_platform_config,
    get_recommended_platforms,
    validate_platform_selection
)

__all__ = [
    'SUPPORTED_PLATFORMS',
    'ALL_PLATFORMS',
    'get_platform_list',
    'get_platform_config',
    'get_recommended_platforms',
    'validate_platform_selection'
]