"""
NOiSEMaKER 14-Day Posting Schedule Grids

Pure data module — no logic, no imports, no classes, no functions.

Only used when a user has exactly 3 active songs (positions A, B, C).
- For 2 songs: daily alternation per platform (handled in schedule_engine.py)
- For 1 song: every platform every day (handled in schedule_engine.py)

Structure:
    THREE_SONG_GRIDS[platform_count][day_number] = [position_per_slot, ...]

    - platform_count: number of connected platforms (2-8)
    - day_number: schedule day (1-14, then cycles)
    - values: list of positions per platform slot (P1, P2, ... Pn)
      where each position is "A", "B", or "C"
"""

THREE_SONG_GRIDS = {
    8: {
        1:  ["A", "B", "B", "C", "B", "B", "C", "A"],
        2:  ["B", "A", "C", "B", "A", "B", "C", "B"],
        3:  ["C", "B", "A", "B", "B", "C", "A", "B"],
        4:  ["B", "C", "B", "A", "C", "B", "B", "C"],
        5:  ["A", "B", "C", "B", "B", "A", "C", "C"],
        6:  ["B", "A", "B", "C", "B", "B", "B", "C"],
        7:  ["C", "C", "B", "B", "C", "C", "B", "A"],
        8:  ["B", "B", "A", "A", "B", "C", "B", "C"],
        9:  ["C", "B", "B", "A", "A", "B", "C", "B"],
        10: ["B", "C", "A", "B", "B", "A", "B", "C"],
        11: ["A", "B", "B", "C", "B", "B", "C", "B"],
        12: ["B", "A", "C", "B", "C", "B", "B", "C"],
        13: ["C", "B", "B", "B", "B", "C", "C", "A"],
        14: ["B", "C", "C", "B", "C", "B", "A", "B"],
    },
    7: {
        1:  ["A", "B", "B", "C", "B", "B", "C"],
        2:  ["B", "A", "C", "B", "A", "B", "C"],
        3:  ["C", "B", "A", "B", "B", "C", "B"],
        4:  ["B", "C", "B", "A", "C", "B", "B"],
        5:  ["A", "B", "C", "B", "B", "A", "C"],
        6:  ["B", "A", "B", "C", "B", "B", "C"],
        7:  ["C", "C", "B", "B", "C", "C", "A"],
        8:  ["B", "B", "A", "A", "B", "C", "B"],
        9:  ["C", "B", "B", "A", "A", "B", "C"],
        10: ["B", "C", "A", "B", "B", "A", "B"],
        11: ["A", "B", "B", "C", "B", "B", "C"],
        12: ["B", "A", "C", "B", "C", "B", "B"],
        13: ["C", "B", "B", "B", "B", "C", "C"],
        14: ["B", "C", "C", "B", "C", "B", "A"],
    },
    6: {
        1:  ["A", "B", "B", "C", "B", "C"],
        2:  ["B", "A", "C", "B", "A", "B"],
        3:  ["C", "B", "A", "B", "B", "C"],
        4:  ["B", "C", "B", "A", "C", "B"],
        5:  ["A", "B", "C", "B", "B", "C"],
        6:  ["B", "A", "B", "C", "B", "B"],
        7:  ["C", "C", "B", "B", "C", "A"],
        8:  ["B", "B", "A", "A", "B", "C"],
        9:  ["C", "B", "B", "A", "A", "B"],
        10: ["B", "C", "A", "B", "B", "C"],
        11: ["A", "B", "B", "C", "B", "B"],
        12: ["B", "A", "C", "B", "C", "C"],
        13: ["C", "B", "B", "B", "B", "C"],
        14: ["B", "C", "C", "B", "C", "A"],
    },
    5: {
        1:  ["A", "B", "B", "C", "B"],
        2:  ["B", "A", "B", "B", "C"],
        3:  ["B", "B", "A", "B", "C"],
        4:  ["C", "B", "B", "A", "B"],
        5:  ["B", "C", "B", "B", "A"],
        6:  ["C", "B", "C", "B", "B"],
        7:  ["B", "C", "A", "C", "B"],
        8:  ["A", "B", "B", "B", "C"],
        9:  ["B", "A", "C", "B", "B"],
        10: ["B", "B", "B", "C", "C"],
        11: ["C", "B", "A", "B", "B"],
        12: ["A", "A", "B", "B", "C"],
        13: ["A", "B", "C", "B", "B"],
        14: ["C", "B", "B", "C", "A"],
    },
    4: {
        1:  ["A", "B", "C", "B"],
        2:  ["B", "A", "B", "C"],
        3:  ["B", "B", "A", "C"],
        4:  ["C", "B", "B", "B"],
        5:  ["B", "C", "B", "A"],
        6:  ["C", "B", "B", "B"],
        7:  ["B", "C", "A", "C"],
        8:  ["A", "B", "B", "C"],
        9:  ["B", "A", "C", "B"],
        10: ["B", "B", "B", "C"],
        11: ["C", "B", "A", "B"],
        12: ["B", "C", "B", "B"],
        13: ["A", "B", "C", "C"],
        14: ["C", "B", "B", "A"],
    },
    3: {
        1:  ["A", "B", "C"],
        2:  ["B", "A", "B"],
        3:  ["B", "B", "C"],
        4:  ["C", "B", "B"],
        5:  ["B", "C", "A"],
        6:  ["C", "B", "B"],
        7:  ["B", "C", "C"],
        8:  ["A", "B", "B"],
        9:  ["B", "A", "C"],
        10: ["B", "B", "C"],
        11: ["C", "B", "B"],
        12: ["B", "C", "B"],
        13: ["A", "B", "C"],
        14: ["C", "B", "A"],
    },
    2: {
        1:  ["A", "C"],
        2:  ["B", "C"],
        3:  ["B", "B"],
        4:  ["B", "B"],
        5:  ["C", "B"],
        6:  ["C", "B"],
        7:  ["C", "A"],
        8:  ["A", "A"],
        9:  ["C", "B"],
        10: ["C", "B"],
        11: ["B", "B"],
        12: ["B", "C"],
        13: ["B", "C"],
        14: ["B", "A"],
    },
}
