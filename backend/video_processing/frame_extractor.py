"""Keyframe extraction from SSBU match videos."""

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when frame extraction fails."""


@dataclass(frozen=True)
class FrameInfo:
    """Metadata about an extracted frame."""

    path: str
    timestamp: float  # seconds from start
    is_key_moment: bool  # True if this frame is near a stock change / brightness spike


def _detect_brightness_spikes(
    video_path: str,
    *,
    sample_fps: float = 5.0,
    threshold_multiplier: float = 1.8,
) -> list[float]:
    """Scan video for brightness spikes that indicate stock losses.

    In SSBU, losing a stock causes a screen flash (bright white frame).
    We detect frames whose mean brightness is significantly above the running average.

    Returns:
        List of timestamps (seconds) where brightness spikes were detected.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ExtractionError(f"Cannot open video: {video_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        frame_interval = int(max(1, round(fps / sample_fps)))
        brightness_values: list[tuple[float, float]] = []  # (timestamp, brightness)
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mean_brightness = float(np.mean(gray))
                timestamp = frame_idx / fps
                brightness_values.append((timestamp, mean_brightness))
            frame_idx += 1

        if len(brightness_values) < 10:
            return []

        # Use rolling average to detect spikes
        window_size = 30  # ~6 seconds at 5fps sampling
        spike_timestamps: list[float] = []

        for i, (ts, brightness) in enumerate(brightness_values):
            window_start = max(0, i - window_size)
            window = [b for _, b in brightness_values[window_start:i]] if i > 0 else [brightness]
            avg = np.mean(window) if window else brightness

            if avg > 0 and brightness > avg * threshold_multiplier and brightness > 150:
                # Avoid duplicates within 2 seconds
                if not spike_timestamps or ts - spike_timestamps[-1] > 2.0:
                    spike_timestamps.append(ts)

        logger.info("Detected %d brightness spikes (potential stock changes)", len(spike_timestamps))
        return spike_timestamps

    finally:
        cap.release()


def extract_keyframes(
    video_path: str,
    output_dir: str,
    fps: float = 0.5,
    *,
    target_width: int = 640,
    target_height: int = 360,
    jpeg_quality: int = 25,
) -> list[FrameInfo]:
    """Extract frames from video at the specified FPS.

    Args:
        video_path: Path to the video file.
        output_dir: Directory to save extracted frame images.
        fps: Frames per second to extract (default 0.5 = every 2 seconds).
        target_width: Resize width for output frames (default 640).
        target_height: Resize height for output frames (default 360).
        jpeg_quality: JPEG compression quality 0-100 (default 25).

    Returns:
        Ordered list of FrameInfo with paths and timestamps.

    Raises:
        ExtractionError: If video cannot be opened or processed.
    """
    path = Path(video_path)
    if not path.exists():
        raise ExtractionError(f"Video file not found: {video_path}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ExtractionError(f"Cannot open video: {video_path}")

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30.0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / video_fps
        frame_interval = int(max(1, round(video_fps / fps)))

        logger.info(
            "Extracting frames: video=%.1fs, fps=%.1f, interval=%d frames, size=%dx%d Q%d",
            duration,
            fps,
            frame_interval,
            target_width,
            target_height,
            jpeg_quality,
        )

        frames: list[FrameInfo] = []
        frame_idx = 0
        extracted = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                timestamp = frame_idx / video_fps
                filename = f"frame_{extracted:06d}_{timestamp:.2f}s.jpg"
                filepath = out_path / filename

                resized = cv2.resize(frame, (target_width, target_height))
                cv2.imwrite(
                    str(filepath),
                    resized,
                    [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality],
                )
                frames.append(FrameInfo(
                    path=str(filepath.resolve()),
                    timestamp=timestamp,
                    is_key_moment=False,
                ))
                extracted += 1

            frame_idx += 1

        logger.info("Extracted %d frames from video", extracted)
        return frames

    finally:
        cap.release()


def extract_stock_change_frames(
    video_path: str,
    output_dir: str,
) -> list[FrameInfo]:
    """Detect stock changes via brightness spikes and extract high-density frames around them.

    Extracts at 5fps for 2 seconds before and after each detected spike.

    Args:
        video_path: Path to the video file.
        output_dir: Directory to save extracted frame images.

    Returns:
        Ordered list of FrameInfo for key moment frames.

    Raises:
        ExtractionError: If video cannot be opened or processed.
    """
    spike_timestamps = _detect_brightness_spikes(video_path)
    if not spike_timestamps:
        logger.info("No brightness spikes detected, no extra frames to extract")
        return []

    path = Path(video_path)
    if not path.exists():
        raise ExtractionError(f"Video file not found: {video_path}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ExtractionError(f"Cannot open video: {video_path}")

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30.0

        # Build set of target timestamps: 2s before to 2s after each spike, at 5fps
        target_timestamps: set[float] = set()
        for spike_ts in spike_timestamps:
            start = max(0.0, spike_ts - 2.0)
            end = spike_ts + 2.0
            t = start
            while t <= end:
                target_timestamps.add(round(t, 2))
                t += 0.2  # 5fps = 0.2s interval

        # Convert to frame numbers
        target_frame_numbers: set[int] = set()
        for ts in target_timestamps:
            frame_num = int(round(ts * video_fps))
            target_frame_numbers.add(frame_num)

        frames: list[FrameInfo] = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx in target_frame_numbers:
                timestamp = frame_idx / video_fps
                filename = f"key_{len(frames):06d}_{timestamp:.2f}s.jpg"
                filepath = out_path / filename

                cv2.imwrite(
                    str(filepath),
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 85],
                )
                frames.append(FrameInfo(
                    path=str(filepath.resolve()),
                    timestamp=timestamp,
                    is_key_moment=True,
                ))

            frame_idx += 1

        # Sort by timestamp
        frames.sort(key=lambda f: f.timestamp)

        logger.info(
            "Extracted %d key moment frames around %d stock changes",
            len(frames),
            len(spike_timestamps),
        )
        return frames

    finally:
        cap.release()
