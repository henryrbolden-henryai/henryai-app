"""Application tracker helper functions for Command Center"""

from typing import Optional


def calculate_momentum_score(
    has_response: bool,
    response_time_days: Optional[int],
    interview_count: int,
    days_since_last_activity: int
) -> int:
    """
    Calculate momentum score (0-100) based on application progress.

    Factors:
    - Has there been any response? (+20 if yes)
    - Response time (faster = higher)
    - Interview progression (each stage +10)
    - Days since last activity (staleness penalty)
    - Confidence decay: -5 points per 10 days of no new signal
    """
    score = 50  # Base score

    # Response bonus
    if has_response:
        score += 20

    # Response time bonus (faster is better)
    if response_time_days is not None:
        if response_time_days <= 3:
            score += 15
        elif response_time_days <= 7:
            score += 10
        elif response_time_days <= 14:
            score += 5

    # Interview progression bonus
    score += min(interview_count * 10, 30)  # Cap at +30

    # Staleness penalty (confidence decay)
    if days_since_last_activity >= 10:
        decay_penalty = (days_since_last_activity // 10) * 5
        score = max(0, score - decay_penalty)

    return min(100, max(0, score))


def calculate_jd_confidence(jd_source: str) -> int:
    """Get confidence score based on JD source."""
    confidence_map = {
        "user_provided": 100,
        "url_fetched": 100,
        "inferred": 70,
        "missing": 50,
        "link_failed": 50
    }
    return confidence_map.get(jd_source, 50)


def calculate_decision_confidence(
    fit_score: int,
    momentum_score: int,
    jd_confidence: int
) -> int:
    """
    Calculate decision confidence score (0-100).

    Formula:
    decision_confidence = (alignment_score * 0.5) + (momentum_score * 0.3) + (jd_confidence * 0.2)
    """
    return int(
        (fit_score * 0.5) +
        (momentum_score * 0.3) +
        (jd_confidence * 0.2)
    )


def get_confidence_label(decision_confidence: int) -> str:
    """Get confidence label from score."""
    if decision_confidence >= 70:
        return "high"
    elif decision_confidence >= 40:
        return "medium"
    return "low"


def get_confidence_guidance(decision_confidence: int) -> str:
    """Get guidance text based on confidence."""
    if decision_confidence >= 70:
        return "Strong alignment. This is worth energy."
    elif decision_confidence >= 40:
        return "Decent fit. Watch for stalls."
    return "This is low-leverage. Focus better bets."


def determine_action_for_status(
    status: str,
    days_since_activity: int,
    decision_confidence: int,
    interview_scheduled: bool = False
) -> tuple:
    """
    Determine next action, reason, and one-click action type based on status and timing.

    Returns: (action, reason, action_type)

    Action Decision Tree from spec:
    - Applied: Days 0-6 wait, Day 7 follow-up, Day 14 ghosted check, Day 21 archive
    - Recruiter Screen Scheduled: Review prep
    - Recruiter Screen Complete: Days 0-5 wait, Days 5+ status check
    - Hiring Manager Scheduled: Prepare stories
    - Final Round Scheduled: Practice presence
    - Final Round Complete: Days 0-3 thank you, Days 7+ request feedback
    """
    status_lower = status.lower().replace("_", " ").replace("-", " ")

    # Applied status
    if "applied" in status_lower:
        if days_since_activity <= 6:
            return ("None—wait", "Most responses Days 3-7. Wait.", "none")
        elif days_since_activity == 7:
            return ("Send follow-up email", "70% respond by now. Silence = ghosting.", "draft_email")
        elif days_since_activity <= 14:
            return ("Mark ghosted or final check-in", "Dead deal. Stop tracking. Move on.", "draft_email")
        else:  # 21+
            return ("Archive this application", "You're wasting mental energy. It's over.", "archive")

    # Recruiter screen
    if "recruiter" in status_lower and "scheduled" in status_lower:
        return ("Review prep guide now", "Recruiters screen out 60%. Be ready.", "open_prep")

    if "recruiter" in status_lower and ("complete" in status_lower or "done" in status_lower):
        if days_since_activity <= 5:
            return ("None—wait for next steps", "Typical response: 3-5 days. Don't follow up.", "none")
        else:
            return ("Send status check-in", "They're deciding or ghosting. Force clarity.", "draft_email")

    # Hiring manager
    if "hiring" in status_lower and "manager" in status_lower and "scheduled" in status_lower:
        return ("Prepare 3 scope-alignment stories", "This stage kills 40%. Prove you fit.", "open_prep")

    # Technical/Panel
    if ("technical" in status_lower or "panel" in status_lower) and "scheduled" in status_lower:
        return ("Practice technical depth questions", "You're competing now. Differentiate or lose.", "open_prep")

    # Final round
    if "final" in status_lower and "scheduled" in status_lower:
        return ("Practice executive presence now", "They're testing culture fit. Be confident.", "open_prep")

    if "final" in status_lower and ("complete" in status_lower or "done" in status_lower):
        if days_since_activity <= 3:
            return ("Send thank-you + reiterate interest", "Decisions happen Days 3-7. Stay visible.", "draft_email")
        else:
            return ("Request feedback or close mentally", "7+ days = probably rejection. Get clarity.", "draft_email")

    # Offer
    if "offer" in status_lower:
        return ("None—negotiate or accept thoughtfully", "Don't rush. This locks 2+ years.", "none")

    # Decision confidence guidance
    if decision_confidence < 40:
        return ("Deprioritize or withdraw", "This is low-leverage. Focus better bets.", "archive")
    elif decision_confidence <= 70:
        return ("Continue but don't overinvest", "Decent fit. Watch for stalls.", "none")
    else:
        return ("Prioritize—stay aggressive here", "Strong alignment. This is worth energy.", "none")


def calculate_ui_signals(
    decision_confidence: int,
    days_since_activity: int,
    next_action: str,
    status: str,
    jd_source: str,
    interview_tomorrow: bool = False,
    focus_mode_enabled: bool = True
) -> dict:
    """
    Calculate UI-ready signals for frontend binding.

    Returns dict with: priority, confidence, urgency, color_code, icon, badge, action_available, dimmed
    """
    # Confidence
    if decision_confidence >= 70:
        confidence = "high"
    elif decision_confidence >= 40:
        confidence = "medium"
    else:
        confidence = "low"

    # Urgency
    status_lower = status.lower()
    if "applied" in status_lower and days_since_activity == 7:
        urgency = "immediate"
    elif "applied" in status_lower and days_since_activity == 14:
        urgency = "immediate"
    elif interview_tomorrow:
        urgency = "immediate"
    elif "archive" in next_action.lower():
        urgency = "immediate"
    elif next_action == "None—wait" or "wait" in next_action.lower():
        urgency = "none"
    elif days_since_activity >= 5 and "complete" in status_lower:
        urgency = "soon"
    else:
        urgency = "routine"

    # Priority
    if decision_confidence < 40:
        priority = "low"
    elif days_since_activity >= 21:
        priority = "archive"
    elif next_action != "None—wait" and urgency == "immediate":
        priority = "high"
    elif decision_confidence >= 70:
        priority = "high"
    else:
        priority = "medium"

    # Color code
    if confidence == "high":
        color_code = "green"
    elif confidence == "medium":
        color_code = "yellow"
    elif confidence == "low":
        color_code = "red"
    elif priority == "archive":
        color_code = "gray"
    else:
        color_code = "yellow"

    # Icon
    if urgency == "immediate":
        icon = "⚠️"
    elif priority == "high" and confidence == "high":
        icon = "🔥"
    elif priority == "low":
        icon = "❄️"
    elif "wait" in next_action.lower():
        icon = "⏳"
    elif priority == "archive":
        icon = "📦"
    else:
        icon = "📋"

    # Badge
    if jd_source in ["inferred", "missing"]:
        badge = "directional"
    elif jd_source in ["user_provided", "url_fetched"]:
        badge = "refined"
    else:
        badge = None

    # Action available
    action_available = next_action not in ["None—wait", "None—wait for next steps", "None—negotiate or accept thoughtfully"]

    # Dimmed (for focus mode)
    if priority in ["low", "archive"]:
        dimmed = True
    elif not focus_mode_enabled:
        dimmed = False
    elif priority == "high":
        dimmed = False
    else:
        dimmed = True

    return {
        "priority": priority,
        "confidence": confidence,
        "urgency": urgency,
        "color_code": color_code,
        "icon": icon,
        "badge": badge,
        "action_available": action_available,
        "dimmed": dimmed
    }


def calculate_pipeline_health(
    applications: list,
    interview_rate: float = 0.0,
    days_since_last_application: int = 0
) -> dict:
    """
    Calculate pipeline health metrics.

    Returns dict with: status, color, icon, tone, recommendation, reason, active_count, priority_count
    """
    active_count = len([a for a in applications if a.get("status", "").lower() not in ["rejected", "withdrawn", "archived"]])

    # Calculate priority count
    priority_count = len([a for a in applications if a.get("priority_level") == "high"])

    # Determine status
    if active_count < 3:
        status = "thin"
    elif active_count > 10:
        status = "overloaded"
    elif interview_rate < 5 and active_count >= 5:
        status = "stalled"
    else:
        status = "healthy"

    # Color
    if status == "healthy":
        color = "green"
    elif status in ["thin", "overloaded"]:
        color = "yellow"
    else:  # stalled
        color = "red"

    # Icon
    icon_map = {
        "healthy": "✅",
        "thin": "📉",
        "overloaded": "📈",
        "stalled": "🚨"
    }
    icon = icon_map.get(status, "📊")

    # Tone
    if status == "stalled":
        tone = "urgent"
    elif status == "thin" and days_since_last_application > 7:
        tone = "urgent"
    elif status == "overloaded" and interview_rate < 10:
        tone = "caution"
    elif active_count >= 3 and interview_rate >= 15:
        tone = "steady"
    else:
        tone = "caution"

    # Recommendation and reason
    if status == "thin":
        recommendation = "Apply to 3 new roles now"
        reason = "Pipeline's too thin. You need momentum."
    elif status == "healthy":
        recommendation = "None—maintain pace, focus on interviews"
        reason = "Good volume. Shift energy to conversion."
    elif status == "overloaded":
        recommendation = "Pause applications. Focus on interviews only."
        reason = "You're spreading thin. Convert what you have."
    else:  # stalled
        if interview_rate < 5:
            recommendation = "Stop applying. Fix your positioning."
            reason = "Something's broken. Diagnose before continuing."
        else:
            recommendation = "Revise resume positioning immediately"
            reason = "Your applications aren't landing. Fix messaging."

    return {
        "status": status,
        "color": color,
        "icon": icon,
        "tone": tone,
        "recommendation": recommendation,
        "reason": reason,
        "active_count": active_count,
        "priority_count": priority_count
    }
