# Prompts package - System prompts for Claude AI interactions

from .mock_interview import (
    MOCK_GENERATE_QUESTION_PROMPT,
    MOCK_ANALYZE_RESPONSE_PROMPT,
    MOCK_QUESTION_FEEDBACK_PROMPT,
    MOCK_SESSION_FEEDBACK_PROMPT,
)

from .debrief import (
    DEBRIEF_SYSTEM_PROMPT_WITH_TRANSCRIPT,
    DEBRIEF_SYSTEM_PROMPT_NO_TRANSCRIPT,
    DEBRIEF_EXTRACTION_PROMPT,
)

from .screening import (
    SCREENING_QUESTIONS_PROMPT,
    CLARIFYING_QUESTIONS_PROMPT,
    REANALYZE_PROMPT,
)

from .leveling import (
    RESUME_LEVELING_PROMPT,
)

from .hey_henry import (
    HEY_HENRY_SYSTEM_PROMPT,
    ASK_HENRY_SYSTEM_PROMPT,  # Backwards compatibility alias
)

from .resume_chat import (
    RESUME_CHAT_SYSTEM_PROMPT,
    RESUME_GENERATION_PROMPT,
)
