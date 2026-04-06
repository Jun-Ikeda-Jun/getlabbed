"""YouTube video downloader using yt-dlp."""

import logging
import os
import re
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)

_YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.)?"
    r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
    r"[\w-]{11}"
)


class DownloadError(Exception):
    """Raised when video download fails."""


def _validate_url(url: str) -> None:
    """Validate that the URL looks like a YouTube link."""
    if not _YOUTUBE_URL_PATTERN.match(url):
        raise DownloadError(
            f"Invalid YouTube URL: {url}. "
            "Expected format: https://youtube.com/watch?v=XXXXXXXXXXX"
        )


async def download_video(youtube_url: str, output_dir: str) -> str:
    """Download a YouTube video at 720p.

    Args:
        youtube_url: Full YouTube URL.
        output_dir: Directory to save the downloaded video.

    Returns:
        Absolute path to the downloaded video file.

    Raises:
        DownloadError: If download fails for any reason.
    """
    _validate_url(youtube_url)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    outtmpl = str(output_path / "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/bestvideo+bestaudio/best",
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 3,
        "extractor_args": {"youtube": {"player_client": ["ios"]}},
    }

    logger.info("Downloading video: %s", youtube_url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            if info is None:
                raise DownloadError("yt-dlp returned no info for the video.")

            video_id = info.get("id", "unknown")
            ext = info.get("ext", "mp4")
            filepath = output_path / f"{video_id}.{ext}"

            if not filepath.exists():
                # yt-dlp may have merged into mp4
                filepath = output_path / f"{video_id}.mp4"

            if not filepath.exists():
                # Fallback: find any file that was just created
                candidates = sorted(output_path.glob(f"{video_id}.*"), key=os.path.getmtime)
                if candidates:
                    filepath = candidates[-1]
                else:
                    raise DownloadError(
                        f"Download appeared to succeed but no file found for video {video_id}"
                    )

            logger.info("Downloaded video to: %s (%.1f MB)", filepath, filepath.stat().st_size / 1e6)
            return str(filepath.resolve())

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if "private" in error_msg:
            raise DownloadError(f"Video is private or unavailable: {youtube_url}") from e
        if "not found" in error_msg or "404" in error_msg:
            raise DownloadError(f"Video not found: {youtube_url}") from e
        if "age" in error_msg:
            raise DownloadError(f"Video is age-restricted: {youtube_url}") from e
        raise DownloadError(f"Failed to download video: {e}") from e
    except Exception as e:
        if isinstance(e, DownloadError):
            raise
        raise DownloadError(f"Unexpected error during download: {e}") from e
