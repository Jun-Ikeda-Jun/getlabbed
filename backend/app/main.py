"""FrameCoach API — FastAPI application.

Endpoints:
    POST /api/analyze        — Submit a YouTube URL for match analysis
    POST /api/analyze-upload — Upload a video file for match analysis
    GET  /api/characters     — List all supported characters
    GET  /api/matchup/{char_a}/{char_b} — Get matchup data
    GET  /api/health         — Health check
"""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import analyze_match
from app.config import WORK_DIR
from app.models import (
    AnalyzeRequest,
    CharacterInfo,
    ErrorResponse,
    HealthResponse,
    MatchAnalysis,
    MatchupInfo,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional imports from parallel-developed modules
# ---------------------------------------------------------------------------

try:
    from video_processing.pipeline import ProcessedMatch, process_match, process_match_from_file

    _HAS_VIDEO_PROCESSING = True
except ImportError:
    logger.info("video_processing module not available — using mock pipeline")
    _HAS_VIDEO_PROCESSING = False

    from app.analyzer import ProcessedMatch  # mock stub

    async def process_match(youtube_url: str, work_dir: str) -> ProcessedMatch:  # type: ignore[misc]
        """Mock process_match for development."""
        return ProcessedMatch(
            frames=[
                {
                    "path": "",
                    "timestamp": i * 10.0,
                    "player_pct": i * 12.0,
                    "opponent_pct": i * 8.0,
                    "player_stocks": max(1, 3 - i // 5),
                    "opponent_stocks": max(1, 3 - i // 7),
                }
                for i in range(30)
            ],
            metadata={"duration": 300, "fps": 60},
        )


try:
    from knowledge_base.loader import (
        get_all_characters,
        load_character,
        load_matchup,
        load_pro_knowledge,
        load_youtube_context,
    )

    _HAS_KNOWLEDGE_BASE = True
except ImportError:
    logger.info("knowledge_base module not available — using mock data")
    _HAS_KNOWLEDGE_BASE = False

    def get_all_characters() -> list[dict]:  # type: ignore[misc]
        """Mock character list for development."""
        return [
            {"name": "mario", "display_name": "Mario", "weight_class": "medium"},
            {"name": "donkey_kong", "display_name": "Donkey Kong", "weight_class": "heavy"},
            {"name": "link", "display_name": "Link", "weight_class": "medium"},
            {"name": "samus", "display_name": "Samus", "weight_class": "heavy"},
            {"name": "yoshi", "display_name": "Yoshi", "weight_class": "medium"},
            {"name": "kirby", "display_name": "Kirby", "weight_class": "light"},
            {"name": "fox", "display_name": "Fox", "weight_class": "light"},
            {"name": "pikachu", "display_name": "Pikachu", "weight_class": "light"},
            {"name": "captain_falcon", "display_name": "Captain Falcon", "weight_class": "medium"},
            {"name": "joker", "display_name": "Joker", "weight_class": "medium"},
        ]

    def load_character(name: str) -> dict | None:  # type: ignore[misc]
        """Mock character data."""
        characters = {c["name"]: c for c in get_all_characters()}
        return characters.get(name.lower().replace(" ", "_"))

    def load_matchup(char_a: str, char_b: str) -> dict | None:  # type: ignore[misc]
        """Mock matchup data."""
        return {
            "character_a": char_a,
            "character_b": char_b,
            "advantage": f"Even matchup between {char_a} and {char_b}",
            "summary": f"{char_a} and {char_b} is generally considered an even matchup.",
            "tips_for_a": [f"Watch out for {char_b}'s aerial approaches"],
            "tips_for_b": [f"Watch out for {char_a}'s ground game"],
        }

    def load_pro_knowledge(player: str, opponent: str | None = None) -> dict:  # type: ignore[misc]
        """Mock pro knowledge."""
        return {"player_guide": None, "opponent_guide": None, "matchup_guide": None, "theory": None}

    def load_youtube_context(character: str, max_transcripts: int = 3) -> list:  # type: ignore[misc]
        """Mock youtube context."""
        return []


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FrameCoach API",
    version="0.1.0",
    description="AI-powered Super Smash Bros. Ultimate coaching API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse()


@app.get("/api/characters", response_model=list[CharacterInfo])
async def list_characters() -> list[CharacterInfo]:
    """Return all supported characters."""
    raw = get_all_characters()
    return [
        CharacterInfo(
            name=c.get("id", c.get("name", "")),
            display_name=c.get("name_en", c.get("display_name", c.get("name", ""))),
            weight_class=c.get("weight_class"),
        )
        for c in raw
    ]


@app.get(
    "/api/matchup/{char_a}/{char_b}",
    response_model=MatchupInfo,
    responses={404: {"model": ErrorResponse}},
)
async def get_matchup(char_a: str, char_b: str) -> MatchupInfo:
    """Return matchup data for two characters."""
    data = load_matchup(char_a, char_b)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No matchup data found for {char_a} vs {char_b}",
        )
    return MatchupInfo(
        character_a=data.get("character_a", char_a),
        character_b=data.get("character_b", char_b),
        advantage=data.get("advantage", "Unknown"),
        tips_for_a=data.get("tips_for_a", []),
        tips_for_b=data.get("tips_for_b", []),
    )


@app.post(
    "/api/analyze",
    response_model=MatchAnalysis,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze(request: AnalyzeRequest) -> MatchAnalysis:
    """Analyze a Smash Bros match from a YouTube URL.

    Workflow:
    1. Download + process video (extract frames, OCR damage %)
    2. Load character frame data and matchup info
    3. Select key frames and send to Claude Vision API
    4. Return structured coaching analysis
    """
    logger.info(
        "Analyze request: url=%s, player=%s, opponent=%s, mode=%s, lang=%s",
        request.youtube_url,
        request.player_character,
        request.opponent_character,
        request.mode,
        request.language,
    )

    # 1. Process video
    job_id = uuid.uuid4().hex[:8]
    work_dir = str(Path(WORK_DIR) / job_id)
    os.makedirs(work_dir, exist_ok=True)

    try:
        processed = await process_match(request.youtube_url, work_dir)
    except Exception as exc:
        logger.error("Video processing failed: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process video: {exc}",
        ) from exc

    # 2. Load knowledge base data
    frame_data = load_character(request.player_character) or {}
    matchup_data = None
    if request.opponent_character:
        matchup_data = load_matchup(request.player_character, request.opponent_character)

    # 3. Load pro knowledge & YouTube context
    pro_knowledge = load_pro_knowledge(
        request.player_character,
        request.opponent_character,
    )
    youtube_excerpts = load_youtube_context(request.player_character)

    # 4. Run analysis
    try:
        analysis = await analyze_match(
            processed_match=processed,
            player_character=request.player_character,
            opponent_character=request.opponent_character,
            frame_data=frame_data,
            matchup_data=matchup_data,
            mode=request.mode,
            language=request.language,
            pro_knowledge=pro_knowledge,
            youtube_excerpts=youtube_excerpts,
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis engine error: {exc}",
        ) from exc

    logger.info("Analysis complete: score=%d, moments=%d", analysis.score, len(analysis.moments))
    return analysis


@app.post(
    "/api/analyze-upload",
    response_model=MatchAnalysis,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def analyze_upload(
    video: UploadFile = File(..., description="Video file (mp4, webm, mov)"),
    player_character: str = Form(..., description="Character the player is using"),
    opponent_character: str | None = Form(default=None, description="Opponent character"),
    mode: Literal["friendly", "detailed"] = Form(default="friendly"),
    language: Literal["ja", "en"] = Form(default="ja"),
) -> MatchAnalysis:
    """Analyze a Smash Bros match from an uploaded video file."""
    allowed_types = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}
    if video.content_type and video.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported video type: {video.content_type}")

    job_id = uuid.uuid4().hex[:8]
    work_dir = str(Path(WORK_DIR) / job_id)
    os.makedirs(work_dir, exist_ok=True)

    # Save uploaded file
    video_path = str(Path(work_dir) / f"upload.{video.filename.rsplit('.', 1)[-1] if video.filename else 'mp4'}")
    try:
        with open(video_path, "wb") as f:
            shutil.copyfileobj(video.file, f)
        logger.info("Saved uploaded video: %s (%.1f MB)", video_path, Path(video_path).stat().st_size / 1e6)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to save uploaded video: {exc}") from exc

    try:
        processed = await process_match_from_file(video_path, work_dir)
    except Exception as exc:
        logger.error("Video processing failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Failed to process video: {exc}") from exc

    # Load knowledge base
    frame_data = load_character(player_character) or {}
    matchup_data = None
    if opponent_character:
        matchup_data = load_matchup(player_character, opponent_character)

    pro_knowledge = load_pro_knowledge(player_character, opponent_character)
    youtube_excerpts = load_youtube_context(player_character)

    try:
        analysis = await analyze_match(
            processed_match=processed,
            player_character=player_character,
            opponent_character=opponent_character,
            frame_data=frame_data,
            matchup_data=matchup_data,
            mode=mode,
            language=language,
            pro_knowledge=pro_knowledge,
            youtube_excerpts=youtube_excerpts,
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {exc}") from exc

    logger.info("Analysis complete: score=%d, moments=%d", analysis.score, len(analysis.moments))
    return analysis
