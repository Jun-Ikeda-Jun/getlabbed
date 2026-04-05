"""HUD element extraction from SSBU match frames using OCR and image analysis."""

import logging
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Raised when OCR processing fails."""


def _check_tesseract() -> None:
    """Verify that Tesseract is installed and accessible."""
    if shutil.which("tesseract") is None:
        raise OCRError(
            "Tesseract is not installed or not in PATH. "
            "Install via: brew install tesseract"
        )


# --- HUD region definitions for 1080p (1920x1080) SSBU ---
# These are approximate crop regions (x, y, w, h).
# We define primary regions and fallback (slightly expanded) regions.

@dataclass(frozen=True)
class CropRegion:
    """Rectangle defining a crop area."""

    x: int
    y: int
    w: int
    h: int

    def scale(self, scale_x: float, scale_y: float) -> "CropRegion":
        """Return a new region scaled to a different resolution."""
        return CropRegion(
            x=int(self.x * scale_x),
            y=int(self.y * scale_y),
            w=int(self.w * scale_x),
            h=int(self.h * scale_y),
        )

    def expand(self, px: int = 20) -> "CropRegion":
        """Return a new region expanded by px pixels in each direction."""
        return CropRegion(
            x=max(0, self.x - px),
            y=max(0, self.y - px),
            w=self.w + 2 * px,
            h=self.h + 2 * px,
        )


# Standard 1080p HUD positions
_HUD_1080P = {
    "p1_damage": CropRegion(x=150, y=880, w=200, h=80),
    "p2_damage": CropRegion(x=930, y=880, w=200, h=80),
    "p1_stocks": CropRegion(x=150, y=960, w=150, h=40),
    "p2_stocks": CropRegion(x=930, y=960, w=150, h=40),
    "timer": CropRegion(x=580, y=30, w=120, h=40),
}

_REF_WIDTH = 1920
_REF_HEIGHT = 1080


def _get_scaled_regions(frame_width: int, frame_height: int) -> dict[str, CropRegion]:
    """Scale HUD regions to match the actual frame resolution."""
    scale_x = frame_width / _REF_WIDTH
    scale_y = frame_height / _REF_HEIGHT
    return {name: region.scale(scale_x, scale_y) for name, region in _HUD_1080P.items()}


def _crop_region(image: np.ndarray, region: CropRegion) -> np.ndarray:
    """Crop a region from the image, clamping to image bounds."""
    h, w = image.shape[:2]
    x1 = max(0, region.x)
    y1 = max(0, region.y)
    x2 = min(w, region.x + region.w)
    y2 = min(h, region.y + region.h)
    return image[y1:y2, x1:x2]


def _preprocess_for_ocr(crop: np.ndarray) -> np.ndarray:
    """Preprocess a cropped HUD region for better OCR accuracy.

    Steps: grayscale -> resize (upscale 3x) -> threshold -> invert.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop

    # Upscale for better OCR accuracy
    scaled = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Adaptive threshold to handle varying background colors
    thresh = cv2.adaptiveThreshold(
        scaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Invert if the text is light on dark background (common in SSBU HUD)
    mean_val = np.mean(thresh)
    if mean_val > 127:
        thresh = cv2.bitwise_not(thresh)

    return thresh


def _ocr_text(preprocessed: np.ndarray, config: str = "--psm 7 -c tessedit_char_whitelist=0123456789%.:") -> str:
    """Run Tesseract OCR on a preprocessed image region.

    Args:
        preprocessed: Binary image ready for OCR.
        config: Tesseract configuration string.

    Returns:
        Raw OCR text output, stripped.
    """
    pil_image = Image.fromarray(preprocessed)
    text = pytesseract.image_to_string(pil_image, config=config)
    return text.strip()


def _parse_damage(raw_text: str) -> float | None:
    """Parse damage percentage from OCR text.

    Expected formats: "42%", "42", "142%", "0%"
    """
    cleaned = raw_text.replace(" ", "").replace("%", "").replace(".", "")
    # Extract digits
    match = re.search(r"(\d{1,3})", cleaned)
    if match:
        value = int(match.group(1))
        if 0 <= value <= 999:
            return float(value)
    return None


def _parse_timer(raw_text: str) -> str | None:
    """Parse timer from OCR text.

    Expected formats: "6:42", "642", "0:05"
    """
    cleaned = raw_text.replace(" ", "")

    # Try M:SS format
    match = re.search(r"(\d{1,2}):(\d{2})", cleaned)
    if match:
        return f"{match.group(1)}:{match.group(2)}"

    # Try bare digits (e.g., "642" -> "6:42")
    match = re.search(r"(\d)(\d{2})", cleaned)
    if match:
        return f"{match.group(1)}:{match.group(2)}"

    return None


def _count_stock_icons(crop: np.ndarray) -> int | None:
    """Count stock icons in a cropped region using contour detection.

    SSBU stock icons are small, roughly circular shapes in the stock area.
    We detect them by finding contours of appropriate size.
    """
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop

    # Threshold to isolate bright icons
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Filter contours by area (stock icons are small but not tiny)
    h, w = crop.shape[:2]
    min_area = (h * w) * 0.01  # At least 1% of crop area
    max_area = (h * w) * 0.4  # At most 40% of crop area

    valid_contours = [
        c for c in contours
        if min_area < cv2.contourArea(c) < max_area
    ]

    count = len(valid_contours)

    # SSBU has max 3 stocks in standard rules (can be up to 5 in custom)
    if 0 <= count <= 5:
        return count

    return None


@dataclass(frozen=True)
class GameState:
    """Game state extracted from a single frame."""

    timestamp: float
    p1_damage: float | None
    p2_damage: float | None
    p1_stocks: int | None
    p2_stocks: int | None
    timer: str | None


def extract_hud_data(frame_path: str, timestamp: float = 0.0) -> GameState:
    """Extract damage %, stocks, and timer from a single SSBU frame.

    Args:
        frame_path: Path to the frame image file.
        timestamp: Timestamp of this frame in the video (seconds).

    Returns:
        GameState with extracted values (None for fields that couldn't be read).
    """
    _check_tesseract()

    path = Path(frame_path)
    if not path.exists():
        logger.warning("Frame not found: %s", frame_path)
        return GameState(
            timestamp=timestamp,
            p1_damage=None,
            p2_damage=None,
            p1_stocks=None,
            p2_stocks=None,
            timer=None,
        )

    image = cv2.imread(str(path))
    if image is None:
        logger.warning("Failed to read frame: %s", frame_path)
        return GameState(
            timestamp=timestamp,
            p1_damage=None,
            p2_damage=None,
            p1_stocks=None,
            p2_stocks=None,
            timer=None,
        )

    h, w = image.shape[:2]
    regions = _get_scaled_regions(w, h)

    # Extract damage percentages
    p1_damage = _try_ocr_damage(image, regions["p1_damage"])
    p2_damage = _try_ocr_damage(image, regions["p2_damage"])

    # Extract stock counts
    p1_stocks = _count_stock_icons(_crop_region(image, regions["p1_stocks"]))
    p2_stocks = _count_stock_icons(_crop_region(image, regions["p2_stocks"]))

    # Extract timer
    timer = _try_ocr_timer(image, regions["timer"])

    return GameState(
        timestamp=timestamp,
        p1_damage=p1_damage,
        p2_damage=p2_damage,
        p1_stocks=p1_stocks,
        p2_stocks=p2_stocks,
        timer=timer,
    )


def _try_ocr_damage(image: np.ndarray, region: CropRegion) -> float | None:
    """Attempt OCR on a damage region, with fallback to expanded region."""
    crop = _crop_region(image, region)
    preprocessed = _preprocess_for_ocr(crop)
    raw = _ocr_text(preprocessed)
    result = _parse_damage(raw)

    if result is not None:
        return result

    # Fallback: try expanded region
    expanded = region.expand(px=30)
    crop = _crop_region(image, expanded)
    preprocessed = _preprocess_for_ocr(crop)
    raw = _ocr_text(preprocessed)
    return _parse_damage(raw)


def _try_ocr_timer(image: np.ndarray, region: CropRegion) -> str | None:
    """Attempt OCR on the timer region, with fallback to expanded region."""
    crop = _crop_region(image, region)
    preprocessed = _preprocess_for_ocr(crop)
    raw = _ocr_text(preprocessed)
    result = _parse_timer(raw)

    if result is not None:
        return result

    # Fallback: try expanded region
    expanded = region.expand(px=20)
    crop = _crop_region(image, expanded)
    preprocessed = _preprocess_for_ocr(crop)
    raw = _ocr_text(preprocessed)
    return _parse_timer(raw)


def process_all_frames(
    frame_infos: list[tuple[str, float]],
) -> list[GameState]:
    """Process all frames and return time-series game state data.

    Args:
        frame_infos: List of (frame_path, timestamp) tuples.

    Returns:
        Ordered list of GameState for each frame.
    """
    _check_tesseract()

    total = len(frame_infos)
    logger.info("Processing %d frames for HUD data", total)

    states: list[GameState] = []
    for i, (frame_path, timestamp) in enumerate(frame_infos):
        if (i + 1) % 50 == 0 or i == 0:
            logger.info("Processing frame %d/%d (%.1fs)", i + 1, total, timestamp)

        state = extract_hud_data(frame_path, timestamp)
        states.append(state)

    logger.info("Completed HUD extraction: %d frames processed", len(states))
    return states
