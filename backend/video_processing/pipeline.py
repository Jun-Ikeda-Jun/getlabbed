"""Orchestrator for the full SSBU match processing pipeline."""

import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from video_processing.downloader import DownloadError, download_video
from video_processing.frame_extractor import (
    ExtractionError,
    FrameInfo,
    extract_keyframes,
    extract_stock_change_frames,
)
from video_processing.hud_ocr import GameState, OCRError, process_all_frames

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when the processing pipeline fails."""


@dataclass(frozen=True)
class ProcessedMatch:
    """Complete result of processing an SSBU match video."""

    video_path: str
    frames: list[str]  # paths to extracted frames
    game_states: list[GameState]  # time-series HUD data
    key_moments: list[int]  # indices of important frames (stock changes, etc.)
    metadata: dict[str, object]  # duration, resolution, etc.


def _merge_and_sort_frames(
    regular_frames: list[FrameInfo],
    key_frames: list[FrameInfo],
) -> list[FrameInfo]:
    """Merge regular and key moment frames, removing duplicates by timestamp proximity."""
    all_frames = list(regular_frames)
    existing_timestamps = {round(f.timestamp, 1) for f in regular_frames}

    for kf in key_frames:
        rounded = round(kf.timestamp, 1)
        if rounded not in existing_timestamps:
            all_frames.append(kf)
            existing_timestamps.add(rounded)

    all_frames.sort(key=lambda f: f.timestamp)
    return all_frames


def _extract_video_metadata(video_path: str) -> dict[str, object]:
    """Extract basic metadata from the video file."""
    import cv2

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video for metadata extraction"}

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0.0

        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_seconds": round(duration, 2),
            "resolution": f"{width}x{height}",
            "file_size_mb": round(Path(video_path).stat().st_size / 1e6, 2),
        }
    finally:
        cap.release()


async def process_match(youtube_url: str, work_dir: str) -> ProcessedMatch:
    """Full pipeline: download -> extract frames -> OCR -> return structured data.

    Args:
        youtube_url: YouTube URL of the SSBU match.
        work_dir: Directory to use for intermediate and output files.
            The caller is responsible for cleaning up this directory.

    Returns:
        ProcessedMatch with all extracted data.

    Raises:
        PipelineError: If any stage of the pipeline fails.
    """
    work_path = Path(work_dir)
    work_path.mkdir(parents=True, exist_ok=True)

    video_dir = work_path / "video"
    frames_dir = work_path / "frames"
    key_frames_dir = work_path / "key_frames"

    # Temp directory for download (cleaned up after we're done with raw video)
    temp_dir = None

    try:
        # --- Stage 1: Download ---
        logger.info("=== Stage 1/4: Downloading video ===")
        temp_dir = tempfile.mkdtemp(prefix="smash_dl_")
        video_path = await download_video(youtube_url, str(video_dir))
        logger.info("Video downloaded: %s", video_path)

        # --- Stage 2: Extract metadata ---
        logger.info("=== Stage 2/4: Extracting metadata ===")
        metadata = _extract_video_metadata(video_path)
        logger.info("Video metadata: %s", metadata)

        # --- Stage 3: Extract frames ---
        logger.info("=== Stage 3/4: Extracting frames ===")
        regular_frames = extract_keyframes(video_path, str(frames_dir))
        key_frames = extract_stock_change_frames(video_path, str(key_frames_dir))

        merged_frames = _merge_and_sort_frames(regular_frames, key_frames)
        logger.info(
            "Total frames: %d (regular=%d, key_moments=%d)",
            len(merged_frames),
            len(regular_frames),
            len(key_frames),
        )

        # --- Stage 4: OCR ---
        logger.info("=== Stage 4/4: Running HUD OCR ===")
        frame_infos = [(f.path, f.timestamp) for f in merged_frames]
        game_states = process_all_frames(frame_infos)

        # Identify key moment indices in the merged list
        key_moment_indices = [
            i for i, f in enumerate(merged_frames) if f.is_key_moment
        ]

        frame_paths = [f.path for f in merged_frames]

        result = ProcessedMatch(
            video_path=video_path,
            frames=frame_paths,
            game_states=game_states,
            key_moments=key_moment_indices,
            metadata=metadata,
        )

        logger.info(
            "Pipeline complete: %d frames, %d game states, %d key moments",
            len(result.frames),
            len(result.game_states),
            len(result.key_moments),
        )

        return result

    except DownloadError as e:
        raise PipelineError(f"Download failed: {e}") from e
    except ExtractionError as e:
        raise PipelineError(f"Frame extraction failed: {e}") from e
    except OCRError as e:
        raise PipelineError(f"OCR processing failed: {e}") from e
    except PipelineError:
        raise
    except Exception as e:
        raise PipelineError(f"Unexpected pipeline error: {e}") from e
    finally:
        # Clean up temp download directory
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
