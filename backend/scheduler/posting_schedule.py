# Paste the OPTIMAL_POSTING_TIMES code
# Save: Ctrl+O, Enter, Ctrl+X

"""
Optimal Posting Time Windows
Defines 4 random optimal times per platform for post scheduling.
"""

import random

OPTIMAL_POSTING_TIMES = {
    'instagram': ['09:00', '13:00', '17:00', '20:00'],
    'twitter': ['08:00', '12:00', '17:00', '21:00'],
    'facebook': ['09:00', '13:00', '19:00', '21:00'],
    'youtube': ['14:00', '17:00', '19:00', '21:00'],
    'tiktok': ['07:00', '16:00', '19:00', '21:00'],
    'reddit': ['08:00', '12:00', '18:00', '22:00'],
    'discord': ['10:00', '15:00', '19:00', '22:00'],
    'threads': ['09:00', '13:00', '18:00', '21:00']
}

def select_random_posting_time(platform: str) -> str:
    """
    Select random optimal time for platform.
    
    Args:
        platform (str): Platform name
        
    Returns:
        str: Time in HH:MM format
    """
    if platform not in OPTIMAL_POSTING_TIMES:
        return '21:00'  # Default to 9 PM
    
    return random.choice(OPTIMAL_POSTING_TIMES[platform])
