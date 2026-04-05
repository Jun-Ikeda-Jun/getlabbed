"""Core analysis engine — sends frames + context to Claude Vision API.

This module selects key frames from a processed match, builds a prompt
with character/matchup context, and parses Claude's response into a
structured MatchAnalysis.
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Literal

import anthropic

from app.config import ANALYSIS_MODEL, ANTHROPIC_API_KEY
from app.models import MatchAnalysis, MatchMoment
from app.prompts import build_user_prompt, get_system_prompt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock types — used when video_processing is not yet available
# ---------------------------------------------------------------------------

try:
    from video_processing.pipeline import ProcessedMatch
except ImportError:

    class ProcessedMatch:  # type: ignore[no-redef]
        """Stub for development — mirrors the real ProcessedMatch interface."""

        def __init__(
            self,
            frames: list[dict] | None = None,
            metadata: dict | None = None,
        ) -> None:
            self.frames: list[dict] = frames or []
            self.metadata: dict = metadata or {}


# ---------------------------------------------------------------------------
# Image encoding
# ---------------------------------------------------------------------------


def _encode_frame_image(frame_path: str) -> str | None:
    """Read an image file and return its base64 encoding."""
    path = Path(frame_path)
    if not path.exists():
        logger.warning("Frame image not found: %s", frame_path)
        return None
    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except OSError as exc:
        logger.error("Failed to read frame image %s: %s", frame_path, exc)
        return None


def _detect_media_type(frame_path: str) -> str:
    """Detect the media type from file extension."""
    ext = Path(frame_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/png")


# ---------------------------------------------------------------------------
# Frame data formatting
# ---------------------------------------------------------------------------


def _format_frame_data_summary(frame_data: dict, language: Literal["ja", "en"]) -> str:
    """Convert raw frame data dict into a readable summary for the prompt."""
    if not frame_data:
        if language == "ja":
            return "（キャラクターデータなし）"
        return "(No character data available)"

    lines: list[str] = []
    for key, value in frame_data.items():
        if isinstance(value, dict):
            lines.append(f"### {key}")
            for sub_key, sub_value in value.items():
                lines.append(f"- {sub_key}: {sub_value}")
        else:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Message construction
# ---------------------------------------------------------------------------


def _build_frame_metadata_text(
    frame: dict,
    index: int,
    language: Literal["ja", "en"],
) -> str:
    """Build a text label for a frame image."""
    timestamp = frame.get("timestamp", 0)
    player_pct = frame.get("player_pct", "?")
    opponent_pct = frame.get("opponent_pct", "?")
    player_stocks = frame.get("player_stocks", "?")
    opponent_stocks = frame.get("opponent_stocks", "?")

    if language == "ja":
        return (
            f"フレーム {index + 1} — "
            f"時間: {timestamp:.1f}秒 | "
            f"自分: {player_pct}% (残機{player_stocks}) | "
            f"相手: {opponent_pct}% (残機{opponent_stocks})"
        )
    return (
        f"Frame {index + 1} — "
        f"Time: {timestamp:.1f}s | "
        f"Player: {player_pct}% ({player_stocks} stocks) | "
        f"Opponent: {opponent_pct}% ({opponent_stocks} stocks)"
    )


def _build_claude_messages(
    selected_frames: list[dict],
    user_prompt_text: str,
    language: Literal["ja", "en"],
) -> list[dict[str, Any]]:
    """Build the messages array for the Claude API call.

    Interleaves text metadata and base64 images so Claude can see each
    frame in context.
    """
    content_blocks: list[dict[str, Any]] = []

    # Leading text with match context
    content_blocks.append({"type": "text", "text": user_prompt_text})

    # Frame images with metadata
    for i, frame in enumerate(selected_frames):
        frame_path = frame.get("path", "")
        metadata_text = _build_frame_metadata_text(frame, i, language)
        content_blocks.append({"type": "text", "text": metadata_text})

        encoded = _encode_frame_image(frame_path)
        if encoded:
            media_type = _detect_media_type(frame_path)
            content_blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": encoded,
                    },
                }
            )
        else:
            if language == "ja":
                content_blocks.append(
                    {"type": "text", "text": f"（フレーム {i + 1} の画像を読み込めませんでした）"}
                )
            else:
                content_blocks.append(
                    {"type": "text", "text": f"(Could not load image for frame {i + 1})"}
                )

    return [{"role": "user", "content": content_blocks}]


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def _parse_analysis_response(raw_text: str) -> MatchAnalysis:
    """Extract structured JSON from Claude's response text.

    Claude may wrap JSON in a markdown code block, so we try multiple
    extraction strategies.
    """
    # Try to find JSON in code blocks first
    json_str = raw_text
    if "```json" in raw_text:
        start = raw_text.index("```json") + len("```json")
        end = raw_text.index("```", start)
        json_str = raw_text[start:end].strip()
    elif "```" in raw_text:
        start = raw_text.index("```") + len("```")
        end = raw_text.index("```", start)
        json_str = raw_text[start:end].strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        logger.error("Failed to parse analysis JSON. Raw response:\n%s", raw_text[:500])
        return MatchAnalysis(
            summary=raw_text[:500],
            score=0,
            moments=[],
            strengths=[],
            weaknesses=["Analysis parsing failed — raw response returned as summary"],
            practice_plan=[],
            matchup_tips=[],
        )

    moments = [
        MatchMoment(
            timestamp=m.get("timestamp", 0),
            description=m.get("description", ""),
            rating=m.get("rating", "okay"),
            suggestion=m.get("suggestion"),
            practice_tip=m.get("practice_tip"),
        )
        for m in data.get("moments", [])
    ]

    return MatchAnalysis(
        summary=data.get("summary", ""),
        score=max(0, min(100, int(data.get("score", 0)))),
        moments=moments,
        strengths=data.get("strengths", []),
        weaknesses=data.get("weaknesses", []),
        practice_plan=data.get("practice_plan", []),
        matchup_tips=data.get("matchup_tips", []),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def analyze_match(
    processed_match: ProcessedMatch,
    player_character: str,
    opponent_character: str | None,
    frame_data: dict,
    matchup_data: dict | None,
    mode: Literal["friendly", "detailed"] = "friendly",
    language: Literal["ja", "en"] = "ja",
    pro_knowledge: dict[str, Any] | None = None,
    youtube_excerpts: list[dict[str, Any]] | None = None,
) -> MatchAnalysis:
    """Run a full match analysis using Claude Vision API.

    Args:
        processed_match: Processed video data containing extracted frames.
        player_character: Name of the player's character.
        opponent_character: Name of the opponent's character (may be None).
        frame_data: Character frame data from the knowledge base.
        matchup_data: Optional matchup-specific data.
        mode: Output style — "friendly" or "detailed".
        language: Output language — "ja" or "en".

    Returns:
        Structured MatchAnalysis with moments, ratings, and coaching advice.
    """
    opponent = opponent_character or "Unknown"

    # Merge frames + game_states into unified dicts for frame selection
    unified_frames: list[dict] = []
    game_states = getattr(processed_match, "game_states", [])
    frame_paths = getattr(processed_match, "frames", [])

    if game_states:
        # Real ProcessedMatch: frames are paths, game_states have HUD data
        for i, gs in enumerate(game_states):
            path = frame_paths[i] if i < len(frame_paths) else ""
            unified_frames.append({
                "path": path,
                "timestamp": gs.timestamp,
                "player_pct": gs.p1_damage,
                "opponent_pct": gs.p2_damage,
                "player_stocks": gs.p1_stocks,
                "opponent_stocks": gs.p2_stocks,
            })
    elif frame_paths and isinstance(frame_paths[0], dict):
        # Mock/stub: frames are already dicts
        unified_frames = list(frame_paths)
    else:
        # Fallback: just paths with no metadata
        for i, path in enumerate(frame_paths):
            unified_frames.append({
                "path": path if isinstance(path, str) else "",
                "timestamp": i * 1.0,
                "player_pct": None,
                "opponent_pct": None,
                "player_stocks": None,
                "opponent_stocks": None,
            })

    # Send all frames — Opus 4.6 handles up to 600 and finds key moments itself
    logger.info(
        "Sending %d frames for analysis (%s vs %s)",
        len(unified_frames),
        player_character,
        opponent,
    )

    # Build prompt
    frame_data_summary = _format_frame_data_summary(frame_data, language)
    user_prompt_text = build_user_prompt(
        language=language,
        player_character=player_character,
        opponent_character=opponent,
        total_frames=len(unified_frames),
        selected_frames=len(unified_frames),
        frame_data_summary=frame_data_summary,
        matchup_data=matchup_data,
        pro_knowledge=pro_knowledge,
        youtube_excerpts=youtube_excerpts,
    )

    system_prompt = get_system_prompt(language, mode)
    messages = _build_claude_messages(unified_frames, user_prompt_text, language)

    # Call Claude API
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — returning mock analysis")
        return _mock_analysis(player_character, opponent, language)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        logger.info("Sending analysis request to Claude (%s, %s mode)", ANALYSIS_MODEL, mode)
        # Use streaming — Opus + 600 frames can take 10+ minutes
        raw_text = ""
        with client.messages.stream(
            model=ANALYSIS_MODEL,
            max_tokens=16384,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                raw_text += text
    except anthropic.RateLimitError:
        logger.error("Claude API rate limit hit")
        raise
    except anthropic.APIError as exc:
        logger.error("Claude API error: %s", exc)
        raise

    logger.info("Received analysis response (%d chars)", len(raw_text))
    return _parse_analysis_response(raw_text)


# ---------------------------------------------------------------------------
# Mock data for development (when API key is not set)
# ---------------------------------------------------------------------------


def _mock_analysis(
    player_character: str,
    opponent_character: str,
    language: Literal["ja", "en"],
) -> MatchAnalysis:
    """Return a mock analysis for development without an API key."""
    if language == "ja":
        return MatchAnalysis(
            summary=(
                f"{player_character}での試合、全体的にいい動きだったよ！"
                f"特に{opponent_character}に対する立ち回りで光る場面がいくつかあった。"
                "もう少し着地狩りを意識できると、さらにワンランク上に行けるはず。"
            ),
            score=65,
            moments=[
                MatchMoment(
                    timestamp=15.0,
                    description=(
                        "相手の着地に合わせてダッシュ掴みを通した。"
                        "ここから下投げ→空上のコンボで30%近く稼げたのはナイス！"
                    ),
                    rating="great",
                    suggestion=None,
                    practice_tip=None,
                ),
                MatchMoment(
                    timestamp=42.5,
                    description=(
                        "ガード解除後にダッシュ攻撃を選んでしまった場面。"
                        "相手の技はガードで-8Fだったから、掴みで確定反撃が取れたはず。"
                    ),
                    rating="missed_opportunity",
                    suggestion="ガードからの反撃は掴みが安定。リスクが低くてリターンが高いよ。",
                    practice_tip=(
                        "トレモでCPUをランダム行動に設定して、"
                        "ガード→掴み→コンボを10回連続で成功させよう。"
                    ),
                ),
                MatchMoment(
                    timestamp=78.0,
                    description="崖際で相手の復帰に対して空後で撃墜！完璧なタイミングだった。",
                    rating="great",
                    suggestion=None,
                    practice_tip=None,
                ),
            ],
            strengths=[
                "掴みからのコンボが安定している",
                "崖攻めのタイミングが良い",
                "相手の着地を待てる忍耐力がある",
            ],
            weaknesses=[
                "ガードからの反撃が遅い場面がある",
                "復帰ルートがワンパターンになりがち",
                "不利状況での暴れが多い",
            ],
            practice_plan=[
                "トレモでガード→掴み→コンボを毎日10分練習",
                "復帰ルートを3パターン使い分ける練習",
                "不利状況では回避を多めに使ってリセットする意識を持つ",
            ],
            matchup_tips=[
                f"{opponent_character}の空中攻撃はガード後に掴みで反撃できるものが多い",
                f"{opponent_character}の復帰は下から来ることが多いので、崖下への攻撃が有効",
            ],
        )
    return MatchAnalysis(
        summary=(
            f"Solid game with {player_character}! "
            f"You had some great moments against {opponent_character}, "
            "especially your punish game. Work on your edgeguarding "
            "and you'll see a big improvement."
        ),
        score=65,
        moments=[
            MatchMoment(
                timestamp=15.0,
                description=(
                    "Caught the opponent's landing with a dash grab. "
                    "Down-throw to up-air combo dealt ~30% — nice!"
                ),
                rating="great",
                suggestion=None,
                practice_tip=None,
            ),
            MatchMoment(
                timestamp=42.5,
                description=(
                    "After blocking, you went for dash attack. "
                    "The opponent's move was -8 on shield, so grab was a guaranteed punish."
                ),
                rating="missed_opportunity",
                suggestion="Grab out of shield is safer and deals more damage.",
                practice_tip=(
                    "In training mode, set CPU to random action. "
                    "Practice shield → grab → combo 10 times in a row."
                ),
            ),
            MatchMoment(
                timestamp=78.0,
                description="Perfect back-air edgeguard for the KO! Great timing and spacing.",
                rating="great",
                suggestion=None,
                practice_tip=None,
            ),
        ],
        strengths=[
            "Consistent grab combos",
            "Good ledge-trapping timing",
            "Patient in neutral — willing to wait for openings",
        ],
        weaknesses=[
            "Slow out-of-shield punishes in some situations",
            "Predictable recovery routes",
            "Mashing in disadvantage instead of resetting",
        ],
        practice_plan=[
            "Practice shield → grab → combo for 10 minutes daily in training mode",
            "Use 3 different recovery routes and vary them each stock",
            "In disadvantage, focus on airdodge/drift to reset to neutral",
        ],
        matchup_tips=[
            f"Many of {opponent_character}'s aerials are punishable on shield with grab",
            f"{opponent_character} usually recovers low — edgeguard below the ledge",
        ],
    )
