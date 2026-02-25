"""
Platform OAuth Manager — Thin re-export shim.
All logic has been split into backend/data/oauth/ (8 platform files + base class).
This file exists solely to preserve existing imports.
"""

from .oauth import (
    oauth_manager,
    connect_platform,
    handle_platform_callback,
    get_platform_token,
    disconnect_platform,
    get_platform_connections,
)
