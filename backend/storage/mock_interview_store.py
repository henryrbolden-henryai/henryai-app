"""Mock interview storage helpers - Supabase with in-memory fallback"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("henryhq")

# Session TTL in seconds (24 hours)
SESSION_TTL_SECONDS = 24 * 60 * 60

# In-memory storage fallback (used when Supabase is not available)
# WARNING: Data is lost on server restart when using fallback
outcomes_store: List[Dict[str, Any]] = []
mock_interview_sessions: Dict[str, Dict[str, Any]] = {}
mock_interview_questions: Dict[str, Dict[str, Any]] = {}
mock_interview_responses: Dict[str, List[Dict[str, Any]]] = {}
mock_interview_analyses: Dict[str, Dict[str, Any]] = {}

# Supabase client reference - will be set by main app
_supabase_client = None


def set_supabase_client(client):
    """Set the Supabase client for storage operations."""
    global _supabase_client
    _supabase_client = client


def save_mock_session(session_id: str, session_data: Dict[str, Any], user_id: str = None) -> bool:
    """Save mock interview session to Supabase or fallback to in-memory."""
    if _supabase_client and user_id:
        try:
            data = {
                "id": session_id,
                "user_id": user_id,
                "resume_json": session_data.get("resume_json", {}),
                "job_description": session_data.get("job_description"),
                "company": session_data.get("company"),
                "role_title": session_data.get("role_title"),
                "interview_stage": session_data.get("interview_stage"),
                "difficulty_level": session_data.get("difficulty_level", "medium"),
                "current_question_number": session_data.get("current_question_number", 1),
            }
            _supabase_client.table("mock_interview_sessions").upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save session to Supabase: {e}")
    # Fallback to in-memory
    mock_interview_sessions[session_id] = session_data
    return True


def get_mock_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get mock interview session from Supabase or fallback."""
    if _supabase_client:
        try:
            result = _supabase_client.table("mock_interview_sessions").select("*").eq("id", session_id).single().execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"Failed to get session from Supabase: {e}")
    # Fallback to in-memory
    return mock_interview_sessions.get(session_id)


def save_mock_question(question_id: str, question_data: Dict[str, Any]) -> bool:
    """Save mock interview question to Supabase or fallback."""
    if _supabase_client:
        try:
            data = {
                "id": question_id,
                "session_id": question_data.get("session_id"),
                "question_number": question_data.get("question_number"),
                "question_text": question_data.get("question_text"),
                "competency_tested": question_data.get("competency_tested"),
                "difficulty": question_data.get("difficulty", "medium"),
            }
            _supabase_client.table("mock_interview_questions").upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save question to Supabase: {e}")
    # Fallback to in-memory
    mock_interview_questions[question_id] = question_data
    return True


def get_mock_question(question_id: str) -> Optional[Dict[str, Any]]:
    """Get mock interview question from Supabase or fallback."""
    if _supabase_client:
        try:
            result = _supabase_client.table("mock_interview_questions").select("*").eq("id", question_id).single().execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"Failed to get question from Supabase: {e}")
    # Fallback to in-memory
    return mock_interview_questions.get(question_id)


def save_mock_response(question_id: str, response_data: Dict[str, Any]) -> bool:
    """Save mock interview response to Supabase or fallback."""
    if _supabase_client:
        try:
            data = {
                "question_id": question_id,
                "session_id": response_data.get("session_id"),
                "response_text": response_data.get("response_text"),
                "score": response_data.get("score"),
                "feedback": response_data.get("feedback"),
                "strengths": response_data.get("strengths", []),
                "improvements": response_data.get("improvements", []),
            }
            _supabase_client.table("mock_interview_responses").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save response to Supabase: {e}")
    # Fallback to in-memory
    if question_id not in mock_interview_responses:
        mock_interview_responses[question_id] = []
    mock_interview_responses[question_id].append(response_data)
    return True


def get_mock_responses(question_id: str) -> List[Dict[str, Any]]:
    """Get mock interview responses from Supabase or fallback."""
    if _supabase_client:
        try:
            result = _supabase_client.table("mock_interview_responses").select("*").eq("question_id", question_id).execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"Failed to get responses from Supabase: {e}")
    # Fallback to in-memory
    return mock_interview_responses.get(question_id, [])


def save_mock_analysis(session_id: str, analysis_data: Dict[str, Any]) -> bool:
    """Save mock interview analysis to Supabase or fallback."""
    if _supabase_client:
        try:
            data = {
                "session_id": session_id,
                "overall_score": analysis_data.get("overall_score"),
                "competency_scores": analysis_data.get("competency_scores"),
                "key_strengths": analysis_data.get("key_strengths", []),
                "areas_for_improvement": analysis_data.get("areas_for_improvement", []),
                "recommendations": analysis_data.get("recommendations", []),
                "detailed_feedback": analysis_data.get("detailed_feedback"),
            }
            _supabase_client.table("mock_interview_analyses").upsert(data, on_conflict="session_id").execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis to Supabase: {e}")
    # Fallback to in-memory
    mock_interview_analyses[session_id] = analysis_data
    return True


def get_mock_analysis(session_id: str) -> Optional[Dict[str, Any]]:
    """Get mock interview analysis from Supabase or fallback."""
    if _supabase_client:
        try:
            result = _supabase_client.table("mock_interview_analyses").select("*").eq("session_id", session_id).single().execute()
            if result.data:
                return result.data
        except Exception as e:
            logger.warning(f"Failed to get analysis from Supabase: {e}")
    # Fallback to in-memory
    return mock_interview_analyses.get(session_id)


def update_mock_session(session_id: str, updates: Dict[str, Any]) -> bool:
    """Update mock interview session in Supabase or fallback."""
    if _supabase_client:
        try:
            _supabase_client.table("mock_interview_sessions").update(updates).eq("id", session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update session in Supabase: {e}")
    # Fallback to in-memory
    if session_id in mock_interview_sessions:
        mock_interview_sessions[session_id].update(updates)
        return True
    return False


def cleanup_expired_sessions() -> int:
    """
    Clean up expired mock interview sessions to prevent memory leaks
    and cross-session contamination.

    Returns:
        Number of sessions cleaned up
    """
    import time
    from datetime import datetime

    current_time = time.time()
    expired_sessions = []

    # Find expired sessions
    for session_id, session in mock_interview_sessions.items():
        created_at = session.get("created_at", 0)
        if isinstance(created_at, str):
            # Parse ISO format timestamp
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.timestamp()
            except (ValueError, TypeError):
                created_at = 0

        if current_time - created_at > SESSION_TTL_SECONDS:
            expired_sessions.append(session_id)

    # Clean up expired sessions and their associated data
    for session_id in expired_sessions:
        # Find and remove questions for this session
        questions_to_remove = [
            qid for qid, q in mock_interview_questions.items()
            if q.get("session_id") == session_id
        ]
        for qid in questions_to_remove:
            mock_interview_questions.pop(qid, None)
            mock_interview_responses.pop(qid, None)

        # Remove session
        mock_interview_sessions.pop(session_id, None)
        mock_interview_analyses.pop(session_id, None)

    if expired_sessions:
        print(f"🧹 Cleaned up {len(expired_sessions)} expired mock interview sessions")

    return len(expired_sessions)
