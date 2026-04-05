"""
Scrape YouTube transcripts from Smash Ultimate educational channels.

Collects subtitles from top SSBU tutorial/guide channels and saves them
as JSON files for the GetLabbed AI knowledge base.

Usage:
    python scrape_youtube.py [--channel CHANNEL_NAME] [--max N]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "youtube_transcripts"

# ---------------------------------------------------------------------------
# Channel & video registry
# ---------------------------------------------------------------------------

# Known educational videos per channel.
# Format: (video_id, title, topics)
# Topics are lowercase tags for filtering later.

CHANNELS: dict[str, list[tuple[str, str, list[str]]]] = {
    "IzawSmash": [
        # Art of Series — character-specific deep-dives
        ("dndykqb1xVA", "Smash Ultimate: How to Sephiroth", ["sephiroth", "neutral", "combos", "edgeguard"]),
        ("xVbrtGvncd8", "Smash Ultimate: Art of Fox", ["fox", "neutral", "combos", "speed"]),
        ("6w7N3Pn8wNU", "Smash Ultimate: Art of Palutena", ["palutena", "neutral", "combos", "nair"]),
        ("dc3w_8r0seI", "Smash Ultimate: Art of Cloud", ["cloud", "neutral", "limit", "combos"]),
        ("xzE8m7gAs7E", "Smash Ultimate: Art of Falcon", ["captain_falcon", "neutral", "combos", "speed"]),
        ("E7e7fYu2pdM", "Smash Ultimate: Art of Luigi", ["luigi", "neutral", "combos", "grab"]),
        ("nW9AedeMeFw", "Smash Ultimate: Art of Samus", ["samus", "neutral", "projectiles", "zoning"]),
        ("8TEYez3_OFk", "Smash Ultimate: Art of Pikachu", ["pikachu", "neutral", "combos", "recovery"]),
        ("Ilb1Q_Cso8E", "Smash Ultimate: Art of Zelda", ["zelda", "neutral", "combos", "edgeguard"]),
        ("YsLJssA01b4", "Smash Ultimate: Art of Falco", ["falco", "neutral", "combos", "speed"]),
        ("DXUnfL77wng", "Smash Ultimate: Art of Mii Brawler", ["mii_brawler", "neutral", "combos"]),
        ("_9LR4LzdAgE", "Smash Ultimate: Art of Greninja", ["greninja", "neutral", "combos", "speed"]),
        ("xs9dqqKJXio", "Smash Ultimate: Art of Zero Suit Samus", ["zero_suit_samus", "neutral", "combos", "mobility"]),
        ("PzThnJQ_QsU", "Smash Ultimate: Art of Pokémon Trainer", ["pokemon_trainer", "neutral", "switching"]),
        ("mBSV7pragNc", "Smash Ultimate: Art of Charizard", ["charizard", "neutral", "combos", "heavyweight"]),
        ("ohYVPYbXP2E", "Smash Ultimate: Art of Ivysaur", ["ivysaur", "neutral", "combos", "range"]),
        ("mIsgi9uRa0Q", "Smash Ultimate: Art of Squirtle", ["squirtle", "neutral", "combos", "speed"]),
        ("M172F_U6DQk", "Smash Ultimate: Art of Corrin", ["corrin", "neutral", "combos", "range"]),
        ("ZLNX2uLYX7M", "Smash Ultimate: Art of Kirby", ["kirby", "neutral", "combos", "edgeguard"]),
        ("8msImwrdEnU", "Smash Ultimate: Art of Incineroar", ["incineroar", "neutral", "grappler", "revenge"]),
        ("F6m-jOY6nOw", "Smash Ultimate: Art of Ken", ["ken", "neutral", "combos", "inputs"]),
        ("P3LQJzwnf_c", "Smash Ultimate: Art of Ryu", ["ryu", "neutral", "combos", "inputs"]),
        ("81H83GAmi70", "Smash Ultimate: Art of Meta Knight", ["meta_knight", "neutral", "combos", "edgeguard"]),
        ("J7whNfvG5QE", "Smash Ultimate: Art of Bowser", ["bowser", "neutral", "heavyweight", "combos"]),
        ("Rl2UEKlIQ2k", "Smash Ultimate: Art of Donkey Kong", ["donkey_kong", "neutral", "heavyweight", "combos"]),
        ("q3_w0_7mLCw", "Smash Ultimate: Art of King K. Rool", ["king_k_rool", "neutral", "heavyweight", "projectiles"]),
        ("eL0knWidMgs", "Smash Ultimate: Art of Hero", ["hero", "neutral", "combos", "rng"]),
        ("MabiWH7VHuQ", "Smash Ultimate: Art of Dr. Mario", ["dr_mario", "neutral", "combos"]),
        ("yv2IqXu8fdI", "Smash Ultimate: Art of Duck Hunt", ["duck_hunt", "neutral", "projectiles", "zoning"]),
        ("vPn1AcdmCJg", "Smash Ultimate: Art of R.O.B.", ["rob", "neutral", "projectiles", "combos"]),
        ("KKdpNmT4v40", "Smash Ultimate: Art of Mr. Game & Watch", ["game_and_watch", "neutral", "combos", "bucket"]),
        ("MOSi3kG6H60", "Smash Ultimate: Art of Snake", ["snake", "neutral", "projectiles", "zoning"]),
        ("xrrfB-Sh9Y8", "Smash Ultimate: Art of Sonic", ["sonic", "neutral", "speed", "combos"]),
        ("WSep92_Z4CU", "Smash Ultimate: Art of Young Link", ["young_link", "neutral", "projectiles", "combos"]),
        ("YDYO5vVrsk8", "Smash Ultimate: Art of Toon Link", ["toon_link", "neutral", "projectiles", "combos"]),
        ("fn0v1UUpI18", "Smash Ultimate: Art of Chrom", ["chrom", "neutral", "combos", "spacing"]),
        ("AS9niTSzi6g", "Smash Ultimate: Art of Piranha Plant", ["piranha_plant", "neutral", "projectiles"]),
        # How to series — character guides
        ("z-USn9YQg7E", "Smash Ultimate: How to Pyra & Mythra", ["pyra", "mythra", "aegis", "guide"]),
        ("ImwcN7oXoAs", "Smash Ultimate: How to Kazuya", ["kazuya", "guide", "combos", "inputs"]),
        ("wdYABozlCyc", "Smash Ultimate: How to Steve", ["steve", "guide", "blocks", "combos"]),
        ("JL5qF6snEz8", "Smash Ultimate: How to Sora", ["sora", "guide", "combos", "recovery"]),
        ("x36t8ddVixI", "Smash Ultimate: How to Byleth", ["byleth", "guide", "combos", "range"]),
        ("px5dugK9Kc8", "Smash Ultimate: How to Terry", ["terry", "guide", "combos", "inputs"]),
        ("CKQqsXOkAgU", "Smash Ultimate: How to Banjo & Kazooie", ["banjo", "guide", "projectiles"]),
        ("IxeattPscpI", "Smash Ultimate: How to Min Min", ["min_min", "guide", "range", "zoning"]),
        # General improvement guides
        ("ta3L35wsE6o", "Smash Ultimate - The Improvement Guide", ["improvement", "fundamentals", "neutral", "guide"]),
        ("Q1kH6SkgXSA", "Smash Ultimate: FRAME DATA Guide", ["frame_data", "fundamentals", "guide"]),
        ("PAHTQ9T5ebY", "[SSBU] Top Level Movement & Positioning", ["movement", "positioning", "fundamentals"]),
    ],
    "Poppt1": [
        ("rAVZT_I-aZA", "Every Character's Most OP Move In Smash Bros. Ultimate", ["tier", "moves", "analysis"]),
        ("zO1lJjpHF1U", "1 Pro Tip for EVERY Smash Bros. Ultimate Character", ["tips", "all_characters", "guide"]),
    ],
    "ESAM": [
        ("OpXN3PdRFXc", "How to Hit Your Opponent (SSBU)", ["neutral", "fundamentals", "offense"]),
    ],
}

# All character names for topic extraction
SMASH_CHARACTERS = [
    "mario", "donkey kong", "link", "samus", "yoshi", "kirby", "fox", "pikachu",
    "luigi", "ness", "captain falcon", "jigglypuff", "peach", "daisy", "bowser",
    "ice climbers", "sheik", "zelda", "dr. mario", "pichu", "falco", "marth",
    "lucina", "young link", "ganondorf", "mewtwo", "roy", "chrom", "mr. game & watch",
    "meta knight", "pit", "dark pit", "zero suit samus", "wario", "snake", "ike",
    "pokemon trainer", "diddy kong", "lucas", "sonic", "king dedede", "olimar",
    "lucario", "r.o.b.", "toon link", "wolf", "villager", "mega man", "wii fit trainer",
    "rosalina", "little mac", "greninja", "palutena", "pac-man", "robin", "shulk",
    "bowser jr.", "duck hunt", "ryu", "ken", "cloud", "corrin", "bayonetta",
    "inkling", "ridley", "simon", "richter", "king k. rool", "isabelle", "incineroar",
    "piranha plant", "joker", "hero", "banjo", "terry", "byleth", "min min",
    "steve", "sephiroth", "pyra", "mythra", "kazuya", "sora",
]


@dataclass
class TranscriptResult:
    video_id: str
    title: str
    channel: str
    url: str
    language: str
    transcript: str
    topics: list[str]
    relevance: str = "high"


@dataclass
class ErrorRecord:
    video_id: str
    title: str
    channel: str
    error: str


def fetch_transcript(video_id: str) -> tuple[str, str]:
    """Fetch transcript for a video, preferring English, falling back to auto-generated."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=["en", "en-US", "en-GB", "ja"])
    formatter = TextFormatter()
    text = formatter.format_transcript(transcript)
    # Detect language from the fetched transcript
    lang = "en"
    if transcript and hasattr(transcript, "language"):
        lang = transcript.language or "en"
    return text, lang


def scrape_channel(
    channel_name: str,
    videos: list[tuple[str, str, list[str]]],
    max_videos: int | None = None,
) -> tuple[list[TranscriptResult], list[ErrorRecord]]:
    """Scrape transcripts for all videos in a channel."""
    results: list[TranscriptResult] = []
    errors: list[ErrorRecord] = []

    target = videos[:max_videos] if max_videos else videos

    for i, (vid_id, title, topics) in enumerate(target):
        logger.info(f"[{channel_name}] ({i+1}/{len(target)}) Fetching: {title}")
        try:
            text, lang = fetch_transcript(vid_id)
            result = TranscriptResult(
                video_id=vid_id,
                title=title,
                channel=channel_name,
                url=f"https://youtube.com/watch?v={vid_id}",
                language=lang,
                transcript=text,
                topics=topics,
            )
            results.append(result)
            logger.info(f"  -> OK ({len(text)} chars, lang={lang})")
        except Exception as e:
            err = ErrorRecord(
                video_id=vid_id,
                title=title,
                channel=channel_name,
                error=str(e),
            )
            errors.append(err)
            logger.warning(f"  -> FAILED: {e}")

        # Rate limiting
        if i < len(target) - 1:
            time.sleep(1.5)

    return results, errors


def save_results(
    results: list[TranscriptResult],
    errors: list[ErrorRecord],
    output_dir: Path,
) -> None:
    """Save transcript results and error log to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save individual channel files
    by_channel: dict[str, list[TranscriptResult]] = {}
    for r in results:
        by_channel.setdefault(r.channel, []).append(r)

    for channel, channel_results in by_channel.items():
        slug = channel.lower().replace(" ", "_")
        out_path = output_dir / f"{slug}.json"
        data = [asdict(r) for r in channel_results]
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"Saved {len(data)} transcripts to {out_path}")

    # Save combined file
    all_path = output_dir / "_all_transcripts.json"
    all_data = [asdict(r) for r in results]
    all_path.write_text(json.dumps(all_data, ensure_ascii=False, indent=2))
    logger.info(f"Saved combined {len(all_data)} transcripts to {all_path}")

    # Save error log
    if errors:
        err_path = output_dir / "_errors.json"
        err_data = [asdict(e) for e in errors]
        err_path.write_text(json.dumps(err_data, ensure_ascii=False, indent=2))
        logger.warning(f"Saved {len(err_data)} errors to {err_path}")

    # Save summary
    summary = {
        "total_videos_attempted": len(results) + len(errors),
        "total_success": len(results),
        "total_errors": len(errors),
        "total_chars": sum(len(r.transcript) for r in results),
        "by_channel": {
            ch: {
                "success": len(ch_results),
                "total_chars": sum(len(r.transcript) for r in ch_results),
            }
            for ch, ch_results in by_channel.items()
        },
    }
    summary_path = output_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    logger.info(f"Summary: {json.dumps(summary, indent=2)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape SSBU YouTube transcripts")
    parser.add_argument(
        "--channel",
        type=str,
        default=None,
        help="Scrape only this channel (e.g. IzawSmash)",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max videos per channel",
    )
    args = parser.parse_args()

    all_results: list[TranscriptResult] = []
    all_errors: list[ErrorRecord] = []

    channels = CHANNELS
    if args.channel:
        if args.channel not in CHANNELS:
            logger.error(f"Unknown channel: {args.channel}. Available: {list(CHANNELS.keys())}")
            sys.exit(1)
        channels = {args.channel: CHANNELS[args.channel]}

    for channel_name, videos in channels.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Channel: {channel_name} ({len(videos)} videos)")
        logger.info(f"{'='*60}")
        results, errors = scrape_channel(channel_name, videos, args.max)
        all_results.extend(results)
        all_errors.extend(errors)

    save_results(all_results, all_errors, OUTPUT_DIR)

    # Final report
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Success: {len(all_results)} / {len(all_results) + len(all_errors)}")
    print(f"Errors:  {len(all_errors)}")
    total_chars = sum(len(r.transcript) for r in all_results)
    print(f"Total transcript size: {total_chars:,} chars ({total_chars / 1024:.1f} KB)")
    print(f"Output dir: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
