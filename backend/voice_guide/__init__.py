"""
HenryHQ Voice Guide Module

Post-processor that applies HenryHQ voice standards to API responses.
Rule-based text transformation - no LLM required.

Per HenryHQ_voice_guide.md:
- Direct, honest, supportive
- Truth first, support second
- Every output must give a clear next step
- No false encouragement or corporate jargon

Core Principle: If it doesn't make the candidate better, no one wins.
"""

from .voice_formatter import (
    VoiceGuideFormatter,
    apply_voice_guide,
)
from .patterns import (
    FORBIDDEN_PATTERNS,
    APPROVED_CLOSINGS,
    TONE_CORRECTIONS,
)

__all__ = [
    'VoiceGuideFormatter',
    'apply_voice_guide',
    'FORBIDDEN_PATTERNS',
    'APPROVED_CLOSINGS',
    'TONE_CORRECTIONS',
]
