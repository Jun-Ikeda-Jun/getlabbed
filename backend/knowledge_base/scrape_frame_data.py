"""
Scraper for ultimateframedata.com — extracts frame data for all 89 SSBU characters.

Saves each character as data/frame_data/{slug}.json and creates data/frame_data/_index.json.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://ultimateframedata.com"

# Complete roster: slug -> display name
CHARACTERS: dict[str, str] = {
    "banjo_and_kazooie": "Banjo & Kazooie",
    "bayonetta": "Bayonetta",
    "bowser": "Bowser",
    "bowser_jr": "Bowser Jr.",
    "byleth": "Byleth",
    "captain_falcon": "Captain Falcon",
    "chrom": "Chrom",
    "cloud": "Cloud",
    "corrin": "Corrin",
    "daisy": "Daisy",
    "dark_pit": "Dark Pit",
    "dark_samus": "Dark Samus",
    "diddy_kong": "Diddy Kong",
    "donkey_kong": "Donkey Kong",
    "dr_mario": "Dr. Mario",
    "duck_hunt": "Duck Hunt",
    "falco": "Falco",
    "fox": "Fox",
    "ganondorf": "Ganondorf",
    "greninja": "Greninja",
    "hero": "Hero",
    "ice_climbers": "Ice Climbers",
    "ike": "Ike",
    "incineroar": "Incineroar",
    "inkling": "Inkling",
    "isabelle": "Isabelle",
    "jigglypuff": "Jigglypuff",
    "joker": "Joker",
    "kazuya": "Kazuya",
    "ken": "Ken",
    "king_dedede": "King Dedede",
    "king_k_rool": "King K. Rool",
    "kirby": "Kirby",
    "link": "Link",
    "little_mac": "Little Mac",
    "lucario": "Lucario",
    "lucas": "Lucas",
    "lucina": "Lucina",
    "luigi": "Luigi",
    "mario": "Mario",
    "marth": "Marth",
    "mega_man": "Mega Man",
    "meta_knight": "Meta Knight",
    "mewtwo": "Mewtwo",
    "mii_brawler": "Mii Brawler",
    "mii_gunner": "Mii Gunner",
    "mii_swordfighter": "Mii Swordfighter",
    "minmin": "Min Min",
    "mr_game_and_watch": "Mr. Game & Watch",
    "mythra": "Mythra",
    "ness": "Ness",
    "olimar": "Olimar",
    "pac_man": "Pac-Man",
    "palutena": "Palutena",
    "peach": "Peach",
    "pichu": "Pichu",
    "pikachu": "Pikachu",
    "piranha_plant": "Piranha Plant",
    "pit": "Pit",
    "pt_squirtle": "Squirtle",
    "pt_ivysaur": "Ivysaur",
    "pt_charizard": "Charizard",
    "pyra": "Pyra",
    "richter": "Richter",
    "ridley": "Ridley",
    "rob": "R.O.B.",
    "robin": "Robin",
    "rosalina_and_luma": "Rosalina & Luma",
    "roy": "Roy",
    "ryu": "Ryu",
    "samus": "Samus",
    "sephiroth": "Sephiroth",
    "sheik": "Sheik",
    "shulk": "Shulk",
    "simon": "Simon",
    "snake": "Snake",
    "sonic": "Sonic",
    "sora": "Sora",
    "steve": "Steve",
    "terry": "Terry",
    "toon_link": "Toon Link",
    "villager": "Villager",
    "wario": "Wario",
    "wii_fit_trainer": "Wii Fit Trainer",
    "wolf": "Wolf",
    "yoshi": "Yoshi",
    "young_link": "Young Link",
    "zelda": "Zelda",
    "zero_suit_samus": "Zero Suit Samus",
}

# -------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------


@dataclass(frozen=True)
class MoveData:
    """Single move's frame data."""

    name: str
    category: str  # ground_attacks, aerial_attacks, special_attacks, grabs_throws, dodges_rolls
    startup: str = ""
    active_frames: str = ""
    total_frames: str = ""
    landing_lag: str = ""
    on_shield: str = ""
    damage: str = ""
    base_knockback: str = ""
    knockback_growth: str = ""
    notes: str = ""


@dataclass
class CharacterFrameData:
    """All frame data for a single character."""

    slug: str
    display_name: str
    moves: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, str] = field(default_factory=dict)
    source_url: str = ""


# -------------------------------------------------------------------
# HTML parsing helpers
# -------------------------------------------------------------------

SECTION_NAMES = {
    "ground attacks": "ground_attacks",
    "aerial attacks": "aerial_attacks",
    "special attacks": "special_attacks",
    "grabs": "grabs_throws",
    "throws": "grabs_throws",
    "dodges": "dodges_rolls",
    "rolls": "dodges_rolls",
    "misc": "misc_info",
}


def _classify_section(header_text: str) -> str:
    """Map a section header to a category key."""
    lower = header_text.strip().lower()
    for keyword, category in SECTION_NAMES.items():
        if keyword in lower:
            return category
    return "other"


def _clean_text(text: str | None) -> str:
    """Normalize whitespace in extracted text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _extract_stat_value(row_text: str) -> tuple[str, str]:
    """Try to split a 'Label: Value' or 'Label Value' stat line."""
    if ":" in row_text:
        parts = row_text.split(":", 1)
        return parts[0].strip(), parts[1].strip()
    return row_text.strip(), ""


def parse_move_row(columns: list[str], category: str) -> MoveData | None:
    """
    Parse a row of text values into MoveData.

    The column layout on ultimateframedata.com varies by section, but
    the common pattern for attacks is:
      [move_name, startup, active, total, landing_lag/notes, on_shield, damage, ...]
    """
    if not columns or all(c.strip() == "" for c in columns):
        return None

    # Pad to at least 8 columns
    cols = [c.strip() for c in columns] + [""] * 8

    move_name = cols[0]
    if not move_name:
        return None

    return MoveData(
        name=move_name,
        category=category,
        startup=cols[1],
        active_frames=cols[2],
        total_frames=cols[3],
        landing_lag=cols[4],
        on_shield=cols[5],
        damage=cols[6],
        notes=cols[7],
    )


def parse_character_page(html: str, slug: str) -> CharacterFrameData:
    """Parse a full character page into structured frame data."""
    soup = BeautifulSoup(html, "html.parser")
    display_name = CHARACTERS.get(slug, slug)
    result = CharacterFrameData(
        slug=slug,
        display_name=display_name,
        source_url=f"{BASE_URL}/{slug}",
    )

    current_category = "ground_attacks"

    # Strategy 1: Look for <div class="moves"> or <div id="..."> sections
    # Strategy 2: Look for table rows
    # Strategy 3: Fallback — extract from text structure

    # Try to find move containers by common patterns
    # UFD uses divs with class "movecontainer" or similar
    move_containers = soup.find_all("div", class_=re.compile(r"move", re.I))

    if move_containers:
        result = _parse_div_based(soup, move_containers, slug, display_name)
    else:
        # Fallback: try table-based extraction
        tables = soup.find_all("table")
        if tables:
            result = _parse_table_based(soup, tables, slug, display_name)
        else:
            # Last resort: text-based extraction from the structured text
            result = _parse_text_based(soup, slug, display_name)

    # Extract character stats (weight, run speed, etc.)
    result.stats = _extract_stats(soup)
    result.source_url = f"{BASE_URL}/{slug}"

    return result


def _parse_div_based(
    soup: BeautifulSoup,
    move_divs: list[Tag],
    slug: str,
    display_name: str,
) -> CharacterFrameData:
    """Parse when moves are in div containers."""
    result = CharacterFrameData(slug=slug, display_name=display_name)
    current_category = "ground_attacks"

    for div in move_divs:
        # Check preceding headers for category
        prev = div.find_previous(["h2", "h3", "h4"])
        if prev:
            current_category = _classify_section(prev.get_text())

        # Extract all text lines from the div
        texts = [_clean_text(t) for t in div.stripped_strings]
        if not texts:
            continue

        move_name = texts[0]
        values = texts[1:] if len(texts) > 1 else []

        move = MoveData(
            name=move_name,
            category=current_category,
            startup=values[0] if len(values) > 0 else "",
            active_frames=values[1] if len(values) > 1 else "",
            total_frames=values[2] if len(values) > 2 else "",
            landing_lag=values[3] if len(values) > 3 else "",
            on_shield=values[4] if len(values) > 4 else "",
            damage=values[5] if len(values) > 5 else "",
            notes=" | ".join(values[6:]) if len(values) > 6 else "",
        )
        result.moves.append(asdict(move))

    return result


def _parse_table_based(
    soup: BeautifulSoup,
    tables: list[Tag],
    slug: str,
    display_name: str,
) -> CharacterFrameData:
    """Parse when moves are in HTML tables."""
    result = CharacterFrameData(slug=slug, display_name=display_name)
    current_category = "ground_attacks"

    for table in tables:
        prev_header = table.find_previous(["h2", "h3", "h4"])
        if prev_header:
            current_category = _classify_section(prev_header.get_text())

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            columns = [_clean_text(c.get_text()) for c in cells]
            move = parse_move_row(columns, current_category)
            if move:
                result.moves.append(asdict(move))

    return result


def _parse_text_based(
    soup: BeautifulSoup,
    slug: str,
    display_name: str,
) -> CharacterFrameData:
    """Fallback: extract from text content using pattern matching."""
    result = CharacterFrameData(slug=slug, display_name=display_name)
    current_category = "ground_attacks"

    # Get all text content, split by major sections
    body = soup.find("body")
    if not body:
        return result

    all_text = body.get_text(separator="\n")
    lines = [line.strip() for line in all_text.split("\n") if line.strip()]

    # Known move name patterns
    move_patterns = [
        r"^(Jab\s*\d*)",
        r"^(Forward Tilt|Up Tilt|Down Tilt|Dash Attack)",
        r"^(Forward Smash|Up Smash|Down Smash)",
        r"^(Neutral Air|Forward Air|Back Air|Up Air|Down Air)",
        r"^(Neutral (Special|B)|Side (Special|B)|Up (Special|B)|Down (Special|B))",
        r"^(Standing Grab|Dash Grab|Pivot Grab)",
        r"^(Forward Throw|Back Throw|Up Throw|Down Throw|Pummel)",
        r"^(Spot Dodge|Forward Roll|Back Roll|Air Dodge)",
        r"^(Nair|Fair|Bair|Uair|Dair)",
    ]
    combined_pattern = "|".join(f"(?:{p})" for p in move_patterns)

    section_markers = {
        "Ground Attacks": "ground_attacks",
        "Aerial Attacks": "aerial_attacks",
        "Special Attacks": "special_attacks",
        "Grabs": "grabs_throws",
        "Throws": "grabs_throws",
        "Dodges": "dodges_rolls",
        "Rolls": "dodges_rolls",
        "Misc": "misc_info",
    }

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for section headers
        for marker, cat in section_markers.items():
            if marker.lower() in line.lower():
                current_category = cat
                break

        # Check for move names
        if re.match(combined_pattern, line, re.IGNORECASE):
            move_name = line
            # Collect following numeric/data lines
            values: list[str] = []
            j = i + 1
            while j < len(lines) and j < i + 10:
                next_line = lines[j]
                # Stop if we hit another move name or section header
                if re.match(combined_pattern, next_line, re.IGNORECASE):
                    break
                if any(m.lower() in next_line.lower() for m in section_markers):
                    break
                values.append(next_line)
                j += 1

            move = MoveData(
                name=move_name,
                category=current_category,
                startup=values[0] if len(values) > 0 else "",
                active_frames=values[1] if len(values) > 1 else "",
                total_frames=values[2] if len(values) > 2 else "",
                landing_lag=values[3] if len(values) > 3 else "",
                on_shield=values[4] if len(values) > 4 else "",
                damage=values[5] if len(values) > 5 else "",
                notes=" | ".join(values[6:]) if len(values) > 6 else "",
            )
            result.moves.append(asdict(move))
            i = j
            continue

        i += 1

    return result


def _extract_stats(soup: BeautifulSoup) -> dict[str, str]:
    """Extract character stats like weight, run speed, etc."""
    stats: dict[str, str] = {}
    stat_keywords = [
        "weight", "gravity", "walk speed", "run speed", "initial dash",
        "air speed", "fall speed", "fast fall speed", "air acceleration",
        "sh / fh / shff / fhff",
    ]

    all_text = soup.get_text(separator="\n")
    for line in all_text.split("\n"):
        lower = line.strip().lower()
        for keyword in stat_keywords:
            if keyword in lower:
                key, val = _extract_stat_value(line.strip())
                if val:
                    stats[key] = val
                else:
                    stats[keyword] = line.strip()

    return stats


# -------------------------------------------------------------------
# Scraping orchestration
# -------------------------------------------------------------------

MAX_RETRIES = 3
RETRY_DELAY = 2.0  # seconds
REQUEST_DELAY = 0.5  # polite delay between requests


def scrape_character(client: httpx.Client, slug: str) -> CharacterFrameData | None:
    """Fetch and parse a single character's frame data with retries."""
    url = f"{BASE_URL}/{slug}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.get(url, timeout=30.0)
            resp.raise_for_status()
            data = parse_character_page(resp.text, slug)
            logger.info(
                "  %s: %d moves, %d stats",
                slug,
                len(data.moves),
                len(data.stats),
            )
            return data
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "  %s attempt %d/%d: HTTP %d",
                slug,
                attempt,
                MAX_RETRIES,
                exc.response.status_code,
            )
        except httpx.RequestError as exc:
            logger.warning(
                "  %s attempt %d/%d: %s",
                slug,
                attempt,
                MAX_RETRIES,
                exc,
            )

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY * attempt)

    logger.error("  SKIP %s after %d attempts", slug, MAX_RETRIES)
    return None


def scrape_all(output_dir: Path) -> None:
    """Scrape all characters and save JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    index_entries: list[dict[str, str]] = []
    succeeded = 0
    failed = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        total = len(CHARACTERS)
        for i, (slug, display_name) in enumerate(CHARACTERS.items(), 1):
            logger.info("[%d/%d] Scraping %s ...", i, total, display_name)

            data = scrape_character(client, slug)
            if data is None:
                failed += 1
                continue

            # Save individual character JSON
            out_path = output_dir / f"{slug}.json"
            payload = {
                "slug": data.slug,
                "display_name": data.display_name,
                "source_url": data.source_url,
                "stats": data.stats,
                "moves": data.moves,
            }
            out_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            index_entries.append({
                "slug": slug,
                "display_name": display_name,
                "move_count": len(data.moves),
            })
            succeeded += 1

            # Be polite
            time.sleep(REQUEST_DELAY)

    # Save index
    index_path = output_dir / "_index.json"
    index_payload = {
        "total_characters": len(CHARACTERS),
        "scraped": succeeded,
        "failed": failed,
        "characters": sorted(index_entries, key=lambda x: x["slug"]),
    }
    index_path.write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("Done! %d succeeded, %d failed. Index at %s", succeeded, failed, index_path)


# -------------------------------------------------------------------
# CLI entry point
# -------------------------------------------------------------------

def main() -> None:
    """Run the scraper."""
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / "data" / "frame_data"

    # Allow overriding output dir via CLI arg
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])

    logger.info("Output directory: %s", output_dir)
    scrape_all(output_dir)


if __name__ == "__main__":
    main()
