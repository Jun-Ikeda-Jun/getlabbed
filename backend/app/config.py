"""FrameCoach configuration."""

import os

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
MAX_FRAMES_PER_ANALYSIS: int = 600
ANALYSIS_MODEL: str = "claude-opus-4-6"
WORK_DIR: str = "/tmp/framecoach"
