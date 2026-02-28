"""
NOiSEMaKER Schedule Engine

Determines which (song_id, platform) pairs should be posted on a given schedule day.
This is the brain of the posting schedule — pure scheduling logic, no I/O.

Modes:
    1 song:  Every platform posts that song every day.
             Content can be posted TWICE to same platform before regeneration.

    2 songs: Daily alternation per platform — no platform posts the same song
             two days in a row. Uses odd/even schedule_day.
             Content can be posted TWICE to same platform before regeneration.

    3 songs: Uses the 14-day grid from schedule_grids.py. Each platform slot
             is assigned a position (A/B/C) mapped to songs sorted by age.
             Content can be posted ONCE per platform before regeneration.

Notes:
    - Extended promo songs ($10/month) are NOT handled here — they have a
      separate 3-day rotation system.
    - All position assignment for 3-song mode uses sort-by-days_in_promotion,
      NOT the get_position() helper.
"""

from scheduler.schedule_grids import THREE_SONG_GRIDS


def get_tomorrows_posts(user_data: dict) -> list[dict]:
    """
    Given a user's scheduling data, return the list of posts for the next day.

    Args:
        user_data: dict containing:
            - active_songs: list of dicts with "song_id" and "days_in_promotion"
            - connected_platforms: list of platform name strings (index 0 = P1, etc.)
            - schedule_day: int (1-14, current position in the cycle)

    Returns:
        List of {"song_id": str, "platform": str} dicts.
    """
    active_songs = user_data.get("active_songs", [])
    connected_platforms = user_data.get("connected_platforms", [])
    schedule_day = user_data.get("schedule_day", 1)
    song_count = len(active_songs)

    if song_count == 0 or not connected_platforms:
        return []

    if song_count == 1:
        return _one_song_schedule(active_songs[0], connected_platforms)

    if song_count == 2:
        return _two_song_schedule(active_songs, connected_platforms, schedule_day)

    if song_count == 3:
        return _three_song_schedule(active_songs, connected_platforms, schedule_day)

    return []


def _one_song_schedule(song: dict, platforms: list[str]) -> list[dict]:
    """Every platform posts the single active song."""
    return [{"song_id": song["song_id"], "platform": p} for p in platforms]


def _two_song_schedule(
    songs: list[dict], platforms: list[str], schedule_day: int
) -> list[dict]:
    """
    Daily alternation — no platform posts the same song twice in a row.

    Songs sorted by days_in_promotion ascending (youngest first).
    Odd schedule_day: P1,P3,P5,P7 get songs[0]; P2,P4,P6,P8 get songs[1].
    Even schedule_day: flipped.
    """
    sorted_songs = sorted(songs, key=lambda s: s["days_in_promotion"])
    is_odd_day = schedule_day % 2 == 1
    posts = []

    for i, platform in enumerate(platforms):
        # P1=index 0, P3=index 2, P5=index 4, P7=index 6 → 0-based even indices
        is_odd_platform = i % 2 == 0

        if is_odd_day:
            song = sorted_songs[0] if is_odd_platform else sorted_songs[1]
        else:
            song = sorted_songs[1] if is_odd_platform else sorted_songs[0]

        posts.append({"song_id": song["song_id"], "platform": platform})

    return posts


def _three_song_schedule(
    songs: list[dict], platforms: list[str], schedule_day: int
) -> list[dict]:
    """
    Uses the 14-day grid from schedule_grids.py.

    Songs sorted by days_in_promotion ascending:
        Youngest = A, Middle = B, Oldest = C
    """
    platform_count = len(platforms)
    grid = THREE_SONG_GRIDS.get(platform_count)

    if grid is None:
        return []

    row = grid.get(schedule_day)
    if row is None:
        return []

    sorted_songs = sorted(songs, key=lambda s: s["days_in_promotion"])
    position_map = {
        "A": sorted_songs[0],
        "B": sorted_songs[1],
        "C": sorted_songs[2],
    }

    posts = []
    for i, position in enumerate(row):
        if i < len(platforms):
            song = position_map[position]
            posts.append({"song_id": song["song_id"], "platform": platforms[i]})

    return posts


def get_position(days_in_promotion: int) -> str | None:
    """
    Map days_in_promotion to a lifecycle position label.

    Used for display/dashboard purposes only — NOT used for schedule assignment.

    Returns:
        "A" (Upcoming):  days 1-14
        "B" (Live):      days 15-28
        "C" (Twilight):  days 29-42
        None (Retired):  days 43+
    """
    if 1 <= days_in_promotion <= 14:
        return "A"
    if 15 <= days_in_promotion <= 28:
        return "B"
    if 29 <= days_in_promotion <= 42:
        return "C"
    return None


def increment_schedule_day(current_day: int) -> int:
    """Advance the schedule day by 1, cycling back to 1 after 14."""
    if current_day >= 14:
        return 1
    return current_day + 1
