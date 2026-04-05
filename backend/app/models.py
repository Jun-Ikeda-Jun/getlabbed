"""Pydantic models for FrameCoach API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    youtube_url: str = Field(
        ...,
        description="YouTube video URL to analyze",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    player_character: str = Field(
        ...,
        description="Character the player is using",
        examples=["Mario"],
    )
    opponent_character: str | None = Field(
        default=None,
        description="Character the opponent is using (auto-detected if omitted)",
    )
    mode: Literal["friendly", "detailed"] = Field(
        default="friendly",
        description="Output style: friendly (middle-school readable) or detailed (frame data included)",
    )
    language: Literal["ja", "en"] = Field(
        default="ja",
        description="Output language",
    )


class MatchMoment(BaseModel):
    """A key moment identified in the match."""

    timestamp: float = Field(..., description="Timestamp in seconds from the start of the video")
    description: str = Field(..., description="What happened at this moment")
    rating: Literal[
        "great",
        "good",
        "okay",
        "missed_opportunity",
        "mistake",
        "critical_error",
    ] = Field(..., description="How well the player performed at this moment")
    suggestion: str | None = Field(default=None, description="What the player could do differently")
    practice_tip: str | None = Field(default=None, description="How to practice the improvement")


class MatchAnalysis(BaseModel):
    """Full analysis result returned to the client."""

    summary: str = Field(..., description="Overall match summary")
    score: int = Field(..., ge=0, le=100, description="Performance score 0-100")
    moments: list[MatchMoment] = Field(default_factory=list, description="Key moments with ratings")
    strengths: list[str] = Field(default_factory=list, description="Things the player did well")
    weaknesses: list[str] = Field(default_factory=list, description="Areas to improve")
    practice_plan: list[str] = Field(default_factory=list, description="Specific practice recommendations")
    matchup_tips: list[str] = Field(default_factory=list, description="Character-specific advice")


class CharacterInfo(BaseModel):
    """Basic character information."""

    name: str
    display_name: str
    weight_class: str | None = None


class MatchupInfo(BaseModel):
    """Matchup data between two characters."""

    character_a: str
    character_b: str
    advantage: str = Field(..., description="Who has the advantage and why")
    tips_for_a: list[str] = Field(default_factory=list)
    tips_for_b: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
