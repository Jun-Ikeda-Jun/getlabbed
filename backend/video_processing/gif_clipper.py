"""Generate GIF clips for key moments from a match video.

Uses ffmpeg to extract short clips around each moment's timestamp,
then converts them to compact GIFs suitable for embedding in API responses.
"""

from __future__ import annotations

import base64
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# GIF settings — optimized for small file size while keeping readability
GIF_WIDTH = 240
GIF_FPS = 8
GIF_DURATION_BEFORE = 1.0  # seconds before the moment
GIF_DURATION_AFTER = 2.0  # seconds after the moment


@dataclass(frozen=True)
class MomentClip:
    """A GIF clip for a single moment."""

    timestamp: float
    gif_path: str
    gif_base64: str
    file_size_kb: float


def generate_moment_gif(
    video_path: str,
    timestamp: float,
    output_path: str,
    video_duration: float | None = None,
) -> MomentClip | None:
    """Generate a GIF clip for a single moment.

    Args:
        video_path: Path to the source video file.
        timestamp: The moment's timestamp in seconds.
        output_path: Where to save the GIF file.
        video_duration: Total video duration (for clamping end time).

    Returns:
        MomentClip with the GIF data, or None if generation fails.
    """
    start = max(0, timestamp - GIF_DURATION_BEFORE)
    duration = GIF_DURATION_BEFORE + GIF_DURATION_AFTER

    if video_duration and start + duration > video_duration:
        duration = max(1.0, video_duration - start)

    try:
        # Two-pass approach: palette generation → GIF encoding
        # This produces much better quality than single-pass
        palette_path = output_path.replace(".gif", "_palette.png")

        # Pass 1: Generate palette
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-t", str(duration),
                "-i", video_path,
                "-vf", f"fps={GIF_FPS},scale={GIF_WIDTH}:-1:flags=lanczos,palettegen=stats_mode=diff",
                palette_path,
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )

        # Pass 2: Generate GIF using palette
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-t", str(duration),
                "-i", video_path,
                "-i", palette_path,
                "-lavfi", f"fps={GIF_FPS},scale={GIF_WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                output_path,
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )

        # Clean up palette
        Path(palette_path).unlink(missing_ok=True)

        gif_path = Path(output_path)
        if not gif_path.exists() or gif_path.stat().st_size == 0:
            logger.warning("GIF generation produced empty file for timestamp %.1f", timestamp)
            return None

        gif_bytes = gif_path.read_bytes()
        file_size_kb = len(gif_bytes) / 1024

        return MomentClip(
            timestamp=timestamp,
            gif_path=output_path,
            gif_base64=base64.b64encode(gif_bytes).decode("utf-8"),
            file_size_kb=round(file_size_kb, 1),
        )

    except subprocess.TimeoutExpired:
        logger.error("GIF generation timed out for timestamp %.1f", timestamp)
        return None
    except subprocess.CalledProcessError as exc:
        logger.error("ffmpeg failed for timestamp %.1f: %s", timestamp, exc.stderr.decode()[:200])
        return None
    except Exception as exc:
        logger.error("Unexpected error generating GIF at %.1f: %s", timestamp, exc)
        return None


def generate_all_moment_gifs(
    video_path: str,
    timestamps: list[float],
    output_dir: str,
    video_duration: float | None = None,
) -> dict[float, MomentClip]:
    """Generate GIF clips for all moments.

    Args:
        video_path: Path to the source video.
        timestamps: List of moment timestamps in seconds.
        output_dir: Directory to save GIF files.
        video_duration: Total video duration for clamping.

    Returns:
        Dict mapping timestamp → MomentClip. Missing entries mean generation failed.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results: dict[float, MomentClip] = {}
    total = len(timestamps)

    for i, ts in enumerate(timestamps):
        gif_file = str(out_path / f"moment_{ts:.1f}s.gif")
        logger.info("Generating GIF %d/%d (%.1fs)...", i + 1, total, ts)

        clip = generate_moment_gif(video_path, ts, gif_file, video_duration)
        if clip:
            results[ts] = clip
            logger.info("  → %.1f KB", clip.file_size_kb)
        else:
            logger.warning("  → Failed")

    logger.info("GIF generation complete: %d/%d succeeded", len(results), total)
    return results
