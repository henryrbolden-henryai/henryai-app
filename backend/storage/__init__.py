# Storage package - Data persistence helpers for HenryAI backend

from .mock_interview_store import (
    save_mock_session,
    get_mock_session,
    save_mock_question,
    get_mock_question,
    save_mock_response,
    get_mock_responses,
    save_mock_analysis,
    get_mock_analysis,
    update_mock_session,
    cleanup_expired_sessions,
    # In-memory storage (fallback)
    mock_interview_sessions,
    mock_interview_questions,
    mock_interview_responses,
    mock_interview_analyses,
    outcomes_store,
    SESSION_TTL_SECONDS,
)
