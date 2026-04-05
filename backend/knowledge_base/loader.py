"""
Knowledge base loader — unified access to character data, frame data, and matchups.

Usage:
    from backend.knowledge_base.loader import (
        load_character,
        load_matchup,
        get_all_characters,
        search_moves,
    )
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_FRAME_DATA_DIR = _DATA_DIR / "frame_data"
_MATCHUP_DIR = _DATA_DIR / "matchup_data"
_CHARACTERS_FILE = _DATA_DIR / "characters.json"
_MATCHUP_CHART_FILE = _MATCHUP_DIR / "matchup_chart.json"
_PRO_KNOWLEDGE_DIR = _DATA_DIR / "pro_knowledge"
_PRO_CHARACTERS_DIR = _PRO_KNOWLEDGE_DIR / "characters"
_PRO_MATCHUPS_DIR = _PRO_KNOWLEDGE_DIR / "matchups"
_PRO_THEORY_FILE = _PRO_KNOWLEDGE_DIR / "competitive_theory.json"
_YOUTUBE_TRANSCRIPTS_DIR = _DATA_DIR / "youtube_transcripts"


# -------------------------------------------------------------------
# Data classes (frozen for immutability)
# -------------------------------------------------------------------


@dataclass(frozen=True)
class CharacterProfile:
    """Character profile from characters.json."""

    id: str
    name_en: str
    name_ja: str
    weight_class: str
    archetype: str
    tier: str
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]


@dataclass(frozen=True)
class MatchupResult:
    """Matchup data between two characters."""

    char_a: str
    char_b: str
    rating: int
    notes: str
    char_a_profile: CharacterProfile | None = None
    char_b_profile: CharacterProfile | None = None


# -------------------------------------------------------------------
# Internal loaders with caching
# -------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_characters_json() -> dict[str, Any]:
    """Load and cache the characters.json file."""
    if not _CHARACTERS_FILE.exists():
        raise FileNotFoundError(f"Characters file not found: {_CHARACTERS_FILE}")
    return json.loads(_CHARACTERS_FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_matchup_chart() -> dict[str, Any]:
    """Load and cache the matchup chart."""
    if not _MATCHUP_CHART_FILE.exists():
        raise FileNotFoundError(f"Matchup chart not found: {_MATCHUP_CHART_FILE}")
    return json.loads(_MATCHUP_CHART_FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _build_character_index() -> dict[str, CharacterProfile]:
    """Build an index of character ID -> CharacterProfile."""
    data = _load_characters_json()
    index: dict[str, CharacterProfile] = {}
    for char in data.get("characters", []):
        profile = CharacterProfile(
            id=char["id"],
            name_en=char["name_en"],
            name_ja=char["name_ja"],
            weight_class=char["weight_class"],
            archetype=char["archetype"],
            tier=char["tier"],
            strengths=tuple(char.get("strengths", [])),
            weaknesses=tuple(char.get("weaknesses", [])),
        )
        index[char["id"]] = profile
    return index


@lru_cache(maxsize=128)
def _load_frame_data_file(slug: str) -> dict[str, Any] | None:
    """Load a single character's frame data JSON."""
    path = _FRAME_DATA_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_character_name(name: str) -> str:
    """
    Normalize a character name to a slug.

    Handles common variations:
        "Mario" -> "mario"
        "Captain Falcon" -> "captain_falcon"
        "Mr. Game & Watch" -> "mr_game_and_watch"
        "R.O.B." -> "rob"
        "Pac-Man" -> "pac_man"
    """
    slug = name.strip().lower()
    slug = slug.replace("&", "and")
    slug = slug.replace("-", "_")
    slug = slug.replace(".", "")
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"[^a-z0-9_]", "", slug)

    # Handle common aliases
    aliases: dict[str, str] = {
        "pokemon_trainer": "pt_squirtle",
        "pt": "pt_squirtle",
        "squirtle": "pt_squirtle",
        "ivysaur": "pt_ivysaur",
        "charizard": "pt_charizard",
        "game_and_watch": "mr_game_and_watch",
        "gandw": "mr_game_and_watch",
        "gnw": "mr_game_and_watch",
        "zss": "zero_suit_samus",
        "dk": "donkey_kong",
        "dedede": "king_dedede",
        "k_rool": "king_k_rool",
        "krool": "king_k_rool",
        "pacman": "pac_man",
        "min_min": "minmin",
        "nair": "neutral_air",
        "fair": "forward_air",
        "bair": "back_air",
        "dair": "down_air",
        "uair": "up_air",
    }

    return aliases.get(slug, slug)


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------


def load_character(name: str) -> dict[str, Any]:
    """
    Load a character's complete data: profile + frame data.

    Args:
        name: Character name or slug (e.g., "Mario", "captain_falcon")

    Returns:
        dict with keys: profile, frame_data (may be None if not scraped yet)

    Raises:
        ValueError: If character is not found
    """
    slug = _normalize_character_name(name)
    index = _build_character_index()

    profile = index.get(slug)
    if profile is None:
        # Try fuzzy match
        for char_id, char_profile in index.items():
            if slug in char_id or char_id in slug:
                profile = char_profile
                slug = char_id
                break

    if profile is None:
        available = sorted(index.keys())
        raise ValueError(
            f"Character '{name}' (slug: '{slug}') not found. "
            f"Available: {', '.join(available[:10])}..."
        )

    frame_data = _load_frame_data_file(slug)

    return {
        "profile": {
            "id": profile.id,
            "name_en": profile.name_en,
            "name_ja": profile.name_ja,
            "weight_class": profile.weight_class,
            "archetype": profile.archetype,
            "tier": profile.tier,
            "strengths": list(profile.strengths),
            "weaknesses": list(profile.weaknesses),
        },
        "frame_data": frame_data,
    }


def load_matchup(char_a: str, char_b: str) -> dict[str, Any]:
    """
    Load matchup data between two characters.

    The rating is from char_a's perspective:
        positive = char_a has advantage
        negative = char_b has advantage
        0 = even

    Args:
        char_a: First character name/slug
        char_b: Second character name/slug

    Returns:
        dict with: char_a, char_b, rating, notes, profiles
    """
    slug_a = _normalize_character_name(char_a)
    slug_b = _normalize_character_name(char_b)

    chart = _load_matchup_chart()
    matchups = chart.get("matchups", {})

    rating = 0
    notes = ""

    # Try direct lookup: char_a -> char_b
    if slug_a in matchups:
        char_a_matchups = matchups[slug_a]
        if slug_b in char_a_matchups:
            entry = char_a_matchups[slug_b]
            rating = entry.get("rating", 0)
            notes = entry.get("notes", "")
        elif "default" in char_a_matchups:
            entry = char_a_matchups["default"]
            rating = entry.get("rating", 0)
            notes = entry.get("notes", "")

    # If no direct, try reverse lookup: char_b -> char_a (invert rating)
    elif slug_b in matchups:
        char_b_matchups = matchups[slug_b]
        if slug_a in char_b_matchups:
            entry = char_b_matchups[slug_a]
            rating = -entry.get("rating", 0)
            notes = entry.get("notes", "")
        elif "default" in char_b_matchups:
            entry = char_b_matchups["default"]
            rating = -entry.get("rating", 0)
            notes = entry.get("notes", "")

    # Load profiles
    index = _build_character_index()
    profile_a = index.get(slug_a)
    profile_b = index.get(slug_b)

    result: dict[str, Any] = {
        "char_a": slug_a,
        "char_b": slug_b,
        "rating": rating,
        "rating_description": _describe_rating(rating),
        "notes": notes,
    }

    if profile_a:
        result["char_a_profile"] = {
            "name_en": profile_a.name_en,
            "name_ja": profile_a.name_ja,
            "tier": profile_a.tier,
            "archetype": profile_a.archetype,
        }
    if profile_b:
        result["char_b_profile"] = {
            "name_en": profile_b.name_en,
            "name_ja": profile_b.name_ja,
            "tier": profile_b.tier,
            "archetype": profile_b.archetype,
        }

    return result


def _describe_rating(rating: int) -> str:
    """Convert a numeric rating to a human-readable description."""
    descriptions = {
        -2: "Very disadvantaged",
        -1: "Slightly disadvantaged",
        0: "Even",
        1: "Slightly advantaged",
        2: "Very advantaged",
    }
    return descriptions.get(rating, f"Rating: {rating}")


def get_all_characters() -> list[dict[str, Any]]:
    """
    Return all character profiles sorted by name.

    Returns:
        List of character profile dicts
    """
    index = _build_character_index()
    characters = []
    for profile in sorted(index.values(), key=lambda p: p.name_en):
        characters.append({
            "id": profile.id,
            "name_en": profile.name_en,
            "name_ja": profile.name_ja,
            "weight_class": profile.weight_class,
            "archetype": profile.archetype,
            "tier": profile.tier,
            "strengths": list(profile.strengths),
            "weaknesses": list(profile.weaknesses),
        })
    return characters


def search_moves(character: str, query: str) -> list[dict[str, Any]]:
    """
    Search a character's moves by name or category.

    Args:
        character: Character name/slug
        query: Search string (e.g., "jab", "aerial", "smash", "grab")

    Returns:
        List of matching move dicts
    """
    slug = _normalize_character_name(character)
    frame_data = _load_frame_data_file(slug)

    if frame_data is None:
        return []

    moves = frame_data.get("moves", [])
    if not moves:
        return []

    query_lower = query.strip().lower()

    # Map common abbreviations
    query_aliases: dict[str, list[str]] = {
        "nair": ["neutral air", "nair"],
        "fair": ["forward air", "fair"],
        "bair": ["back air", "bair"],
        "dair": ["down air", "dair"],
        "uair": ["up air", "uair"],
        "ftilt": ["forward tilt"],
        "dtilt": ["down tilt"],
        "utilt": ["up tilt"],
        "fsmash": ["forward smash"],
        "dsmash": ["down smash"],
        "usmash": ["up smash"],
        "nb": ["neutral b", "neutral special"],
        "side_b": ["side b", "side special"],
        "up_b": ["up b", "up special"],
        "down_b": ["down b", "down special"],
    }

    search_terms = [query_lower]
    if query_lower in query_aliases:
        search_terms.extend(query_aliases[query_lower])

    results = []
    for move in moves:
        move_name_lower = move.get("name", "").lower()
        move_category_lower = move.get("category", "").lower()

        for term in search_terms:
            if term in move_name_lower or term in move_category_lower:
                results.append(move)
                break

    return results


# -------------------------------------------------------------------
# Pro Knowledge Base loaders
# -------------------------------------------------------------------


@lru_cache(maxsize=128)
def _load_pro_character_file(slug: str) -> dict[str, Any] | None:
    """Load a character's pro knowledge JSON."""
    path = _PRO_CHARACTERS_DIR / f"{slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    # Follow alias references
    if "_alias" in data:
        alias_path = _PRO_CHARACTERS_DIR / f"{data['_alias']}.json"
        if alias_path.exists():
            return json.loads(alias_path.read_text(encoding="utf-8"))
    return data


@lru_cache(maxsize=64)
def _load_pro_matchup_file(slug_a: str, slug_b: str) -> dict[str, Any] | None:
    """Load a detailed matchup guide if available."""
    # Try both orderings
    for filename in (f"{slug_a}_vs_{slug_b}.json", f"{slug_b}_vs_{slug_a}.json"):
        path = _PRO_MATCHUPS_DIR / filename
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


@lru_cache(maxsize=1)
def _load_competitive_theory() -> dict[str, Any] | None:
    """Load the competitive theory knowledge base."""
    if not _PRO_THEORY_FILE.exists():
        return None
    return json.loads(_PRO_THEORY_FILE.read_text(encoding="utf-8"))


def load_pro_knowledge(
    player_character: str,
    opponent_character: str | None = None,
) -> dict[str, Any]:
    """Load all relevant pro knowledge for a match analysis.

    Returns a dict with keys:
        - player_guide: Character-specific tactics, combos, kill confirms
        - opponent_guide: Opponent's tactics (to identify their patterns)
        - matchup_guide: Detailed matchup-specific advice (if available)
        - theory: Relevant competitive theory sections

    Each value may be None if data is not available.
    """
    player_slug = _normalize_character_name(player_character)
    opponent_slug = _normalize_character_name(opponent_character) if opponent_character else None

    player_guide = _load_pro_character_file(player_slug)
    opponent_guide = _load_pro_character_file(opponent_slug) if opponent_slug else None
    matchup_guide = (
        _load_pro_matchup_file(player_slug, opponent_slug) if opponent_slug else None
    )
    theory = _load_competitive_theory()

    return {
        "player_guide": player_guide,
        "opponent_guide": opponent_guide,
        "matchup_guide": matchup_guide,
        "theory": theory,
    }


def load_youtube_context(
    character_slug: str,
    max_transcripts: int = 3,
) -> list[dict[str, Any]]:
    """Load relevant YouTube transcript excerpts for a character.

    Returns the most relevant transcripts (by topic match) trimmed to
    a reasonable size for prompt inclusion.
    """
    all_transcripts_file = _YOUTUBE_TRANSCRIPTS_DIR / "_all_transcripts.json"
    if not all_transcripts_file.exists():
        return []

    all_data: list[dict[str, Any]] = json.loads(
        all_transcripts_file.read_text(encoding="utf-8")
    )

    slug = _normalize_character_name(character_slug)

    # Score each transcript by topic relevance
    scored: list[tuple[float, dict[str, Any]]] = []
    for entry in all_data:
        topics = entry.get("topics", [])
        title_lower = entry.get("title", "").lower()

        score = 0.0
        # Direct character match in topics
        if slug in topics or slug.replace("_", " ") in title_lower:
            score += 10.0
        # Partial match (e.g. "pikachu" in "pokemon_trainer")
        for topic in topics:
            if slug in topic or topic in slug:
                score += 5.0
        # General guide topics are always somewhat useful
        if any(t in topics for t in ("fundamentals", "neutral", "improvement", "guide")):
            score += 1.0

        # Only include if there's a character-specific match (score >= 5)
        # or a strong general guide match
        if score >= 5.0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for _, entry in scored[:max_transcripts]:
        # Trim transcript to first ~2000 chars to control prompt size
        transcript = entry.get("transcript", "")
        trimmed = transcript[:2000] + ("..." if len(transcript) > 2000 else "")
        results.append({
            "title": entry.get("title", ""),
            "channel": entry.get("channel", ""),
            "url": entry.get("url", ""),
            "topics": entry.get("topics", []),
            "transcript_excerpt": trimmed,
        })

    return results
