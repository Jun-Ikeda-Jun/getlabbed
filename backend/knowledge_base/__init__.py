"""
FrameCoach Knowledge Base — character data, frame data, and matchup information.

Public API:
    load_character(name)       - Load character profile + frame data
    load_matchup(a, b)         - Load matchup data between two characters
    get_all_characters()       - List all character profiles
    search_moves(char, query)  - Search moves by name/category
"""

from knowledge_base.loader import (
    get_all_characters,
    load_character,
    load_matchup,
    search_moves,
)

__all__ = [
    "get_all_characters",
    "load_character",
    "load_matchup",
    "search_moves",
]
