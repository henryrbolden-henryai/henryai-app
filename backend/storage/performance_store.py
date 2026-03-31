"""Performance persistence — interview responses, story performance, user summary."""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("henryhq")

_supabase_client = None


def set_performance_supabase_client(client):
    """Set the Supabase client for performance storage."""
    global _supabase_client
    _supabase_client = client


# ── Save Interview Response ──────────────────────────────────────────────────

def save_interview_response(data: Dict[str, Any]) -> bool:
    """
    Persist a single evaluated interview response.
    Called after mock interview answer evaluation or voice drill evaluation.
    Fails silently — never blocks UX.
    """
    if not _supabase_client:
        logger.warning("Performance store: no Supabase client, skipping save")
        return False

    user_id = data.get("user_id")
    if not user_id:
        logger.warning("Performance store: no user_id, skipping save")
        return False

    row = {
        "user_id": user_id,
        "interview_id": data.get("interview_id"),
        "question": data.get("question"),
        "transcript": data.get("transcript"),
        "content_score": data.get("content_score"),
        "delivery_score": data.get("delivery_score"),
        "final_score": data.get("final_score"),
        "verdict": data.get("verdict"),
        "rejection_reason": data.get("rejection_reason"),
        "filler_word_count": data.get("filler_word_count"),
        "confidence_score": data.get("confidence_score"),
        "pace_score": data.get("pace_score"),
        "clarity_score": data.get("clarity_score"),
        "energy_score": data.get("energy_score"),
    }

    try:
        _supabase_client.table("interview_responses").insert(row).execute()
        logger.info(f"Saved interview response for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save interview response: {e}")
        # Retry once
        try:
            _supabase_client.table("interview_responses").insert(row).execute()
            return True
        except Exception as retry_err:
            logger.error(f"Retry failed for interview response: {retry_err}")
            return False


# ── Save Story Performance ───────────────────────────────────────────────────

def save_story_performance(data: Dict[str, Any]) -> bool:
    """
    Persist story usage performance — when a story is used in an interview
    or explicitly logged.
    """
    if not _supabase_client:
        logger.warning("Performance store: no Supabase client, skipping story save")
        return False

    user_id = data.get("user_id")
    if not user_id or not data.get("story_id"):
        logger.warning("Performance store: missing user_id or story_id")
        return False

    row = {
        "user_id": user_id,
        "story_id": data.get("story_id"),
        "interview_id": data.get("interview_id"),
        "effectiveness": data.get("effectiveness"),
        "delivery_score": data.get("delivery_score"),
        "final_score": data.get("final_score"),
        "context": data.get("context", {}),
    }

    try:
        _supabase_client.table("story_performance").insert(row).execute()
        logger.info(f"Saved story performance for user {user_id}, story {data.get('story_id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to save story performance: {e}")
        try:
            _supabase_client.table("story_performance").insert(row).execute()
            return True
        except Exception as retry_err:
            logger.error(f"Retry failed for story performance: {retry_err}")
            return False


# ── Update User Performance Summary ─────────────────────────────────────────

def update_user_performance_summary(user_id: str) -> bool:
    """
    Recompute and upsert the user's aggregate performance summary.
    Called after every interview response save.
    """
    if not _supabase_client or not user_id:
        return False

    try:
        # Fetch all responses for this user
        result = _supabase_client.table("interview_responses") \
            .select("confidence_score, clarity_score, delivery_score, final_score, verdict") \
            .eq("user_id", user_id) \
            .execute()

        rows = result.data or []
        if not rows:
            return False

        total = len(rows)

        # Compute averages (skip nulls)
        def avg_field(field: str) -> Optional[float]:
            vals = [r[field] for r in rows if r.get(field) is not None]
            return round(sum(vals) / len(vals), 1) if vals else None

        avg_confidence = avg_field("confidence_score")
        avg_clarity = avg_field("clarity_score")
        avg_delivery = avg_field("delivery_score")

        # Pass rate = advance / total
        advance_count = sum(1 for r in rows if r.get("verdict") == "advance")
        pass_rate = round(advance_count / total * 100, 1) if total > 0 else 0

        # Top issues: count verdicts
        reject_count = sum(1 for r in rows if r.get("verdict") == "reject")
        hold_count = sum(1 for r in rows if r.get("verdict") == "hold")

        top_issues = []
        if avg_confidence is not None and avg_confidence < 65:
            top_issues.append("Low confidence scores")
        if avg_clarity is not None and avg_clarity < 65:
            top_issues.append("Clarity needs work")
        if avg_delivery is not None and avg_delivery < 65:
            top_issues.append("Delivery below threshold")
        if reject_count > total * 0.3:
            top_issues.append("High rejection rate")
        if hold_count > total * 0.4:
            top_issues.append("Too many borderline answers")

        summary_row = {
            "user_id": user_id,
            "avg_confidence": avg_confidence,
            "avg_clarity": avg_clarity,
            "avg_delivery_score": avg_delivery,
            "pass_rate": pass_rate,
            "top_issues": top_issues,
            "updated_at": "now()",
        }

        _supabase_client.table("user_performance_summary") \
            .upsert(summary_row, on_conflict="user_id") \
            .execute()

        logger.info(f"Updated performance summary for user {user_id}: pass_rate={pass_rate}%")
        return True

    except Exception as e:
        logger.error(f"Failed to update performance summary for {user_id}: {e}")
        return False


# ── Get User Performance Summary ─────────────────────────────────────────────

def get_user_performance_summary(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve the user's cached performance summary."""
    if not _supabase_client or not user_id:
        return None

    try:
        result = _supabase_client.table("user_performance_summary") \
            .select("*") \
            .eq("user_id", user_id) \
            .single() \
            .execute()
        return result.data
    except Exception as e:
        logger.warning(f"Failed to get performance summary for {user_id}: {e}")
        return None
