"""
Master Scoring Model for Interview Evaluation.

Content gets you in the door. Delivery gets you the offer.

final_score = (content_weight * content_score) + (delivery_weight * delivery_score)

Weights adjust by role level:
  - IC/Senior: content 0.7, delivery 0.3
  - Manager: content 0.6, delivery 0.4 (default)
  - Director/Head: content 0.5, delivery 0.5
  - VP/Executive: content 0.5, delivery 0.5
"""

from typing import Optional


def compute_content_score(
    clarity: int,
    structure: int,
    impact: int,
    credibility: int,
) -> int:
    """
    Weighted content score.
    Impact highest (0.30) — outcomes matter most.
    """
    raw = (
        (0.25 * clarity)
        + (0.25 * structure)
        + (0.30 * impact)
        + (0.20 * credibility)
    )
    return max(0, min(100, round(raw)))


def compute_delivery_score(
    confidence: int,
    clarity_speaking: int,
    pace: int,
    energy: int,
    conciseness: int,
    filler_word_count: int = 0,
) -> int:
    """
    Weighted delivery score with filler word penalty.

    Filler threshold:
      0-3: no penalty
      4-8: -5%
      9+:  -10%
    """
    raw = (
        (0.30 * confidence)
        + (0.20 * clarity_speaking)
        + (0.20 * pace)
        + (0.15 * energy)
        + (0.15 * conciseness)
    )

    # Filler word penalty
    if filler_word_count >= 9:
        raw -= 10
    elif filler_word_count >= 4:
        raw -= 5

    return max(0, min(100, round(raw)))


def get_weights_for_role(role_level: str) -> tuple:
    """Returns (content_weight, delivery_weight) based on role level."""
    level = (role_level or "").lower().strip()

    if level in ("ic", "junior", "mid", "senior"):
        return (0.7, 0.3)
    elif level in ("manager",):
        return (0.6, 0.4)
    elif level in ("director", "head", "vp", "executive", "c-level"):
        return (0.5, 0.5)
    else:
        # Default to manager-level weighting
        return (0.6, 0.4)


def compute_final_score(
    content_score: int,
    delivery_score: int,
    role_level: str = "senior",
) -> int:
    """Weighted final score adjusted by role level."""
    cw, dw = get_weights_for_role(role_level)
    raw = (cw * content_score) + (dw * delivery_score)
    return max(0, min(100, round(raw)))


def compute_verdict(
    content_score: int,
    delivery_score: int,
    red_flags: list = None,
) -> dict:
    """
    Deterministic verdict mapping.

    ADVANCE: content >= 75 AND delivery >= 70 AND no major red flags
    HOLD:    content >= 65 AND delivery >= 60 OR mixed signals
    REJECT:  content < 65 OR delivery < 55 OR major red flag

    Returns: { verdict, recruiter_screen }
    """
    red_flags = red_flags or []
    has_major_flag = len(red_flags) > 0

    # Recruiter screen (lower bar)
    recruiter_screen = "pass" if content_score >= 55 and delivery_score >= 45 else "fail"

    # Hiring manager verdict
    if has_major_flag:
        # Red flags force hold or reject
        if content_score < 60 or delivery_score < 50:
            verdict = "reject"
        else:
            verdict = "hold"
    elif content_score >= 75 and delivery_score >= 70:
        verdict = "advance"
    elif content_score >= 65 and delivery_score >= 60:
        verdict = "hold"
    elif content_score < 65 or delivery_score < 55:
        verdict = "reject"
    else:
        verdict = "hold"

    return {
        "verdict": verdict,
        "recruiter_screen": recruiter_screen,
    }


def compute_intro_score(
    content_score: int,
    delivery_score: int,
    weak_opening: bool = False,
    unclear_positioning: bool = False,
) -> int:
    """
    Intro scoring — first impression matters more.
    50/50 content/delivery (higher delivery weight than normal).
    Extra penalties for weak opening or unclear positioning.
    """
    raw = (0.5 * content_score) + (0.5 * delivery_score)

    if weak_opening:
        raw -= 10
    if unclear_positioning:
        raw -= 15

    return max(0, min(100, round(raw)))


def build_combined_score(
    content_scores: Optional[dict] = None,
    delivery_scores: Optional[dict] = None,
    role_level: str = "senior",
    red_flags: list = None,
) -> dict:
    """
    Build the full CombinedScore object from raw scores.

    This is the main entry point — call this from endpoints.
    """
    red_flags = red_flags or []

    # Compute content score
    cs = content_scores or {}
    content = compute_content_score(
        clarity=cs.get("clarity", 50),
        structure=cs.get("structure", 50),
        impact=cs.get("impact", 50),
        credibility=cs.get("credibility", 50),
    )

    # Compute delivery score
    ds = delivery_scores or {}
    delivery = compute_delivery_score(
        confidence=ds.get("confidence", 50),
        clarity_speaking=ds.get("clarity", 50),
        pace=ds.get("pace", 50),
        energy=ds.get("energy", 50),
        conciseness=ds.get("conciseness", 70),
        filler_word_count=ds.get("filler_word_count", 0),
    )

    # Final score
    final = compute_final_score(content, delivery, role_level)

    # Verdict
    verdict_result = compute_verdict(content, delivery, red_flags)

    # Top issues (derive from lowest scores)
    top_issues = []
    if ds.get("filler_word_count", 0) >= 4:
        count = ds["filler_word_count"]
        top_issues.append(f"Filler words: {count} detected — this undermines credibility")
    if ds.get("confidence", 100) < 55:
        top_issues.append("Low confidence — hedging language or trailing sentences detected")
    if cs.get("impact", 100) < 55:
        top_issues.append("Weak impact — no clear outcome or metric in the answer")
    if ds.get("conciseness", 100) < 50:
        top_issues.append("Rambling — answer went past the point, needs tighter delivery")
    if cs.get("structure", 100) < 55:
        top_issues.append("Weak structure — answer lacked clear STAR format or logical flow")
    if ds.get("pace", 100) < 40 or ds.get("pace", 0) > 85:
        top_issues.append("Pacing issues — too fast or too slow for conversational interview")
    for flag in red_flags:
        top_issues.append(f"Red flag: {flag}")

    # Next actions (top 3, derived from top issues)
    next_actions = []
    if ds.get("filler_word_count", 0) >= 4:
        next_actions.append("Record yourself answering one question with zero filler words. Repeat until clean.")
    if ds.get("confidence", 100) < 55:
        next_actions.append("Rewrite your answer starting every key sentence with 'I decided' or 'I built'. Practice saying it out loud.")
    if cs.get("impact", 100) < 55:
        next_actions.append("Add a specific metric to your result. Revenue, percentage, timeline — pick one and land on it.")
    if ds.get("conciseness", 100) < 50:
        next_actions.append("Practice the 90-second rule: answer, then stop. Set a timer.")

    return {
        "final_score": final,
        "content_score": content,
        "delivery_score": delivery,
        "content_breakdown": content_scores,
        "delivery_breakdown": delivery_scores,
        "verdict": verdict_result["verdict"],
        "recruiter_screen": verdict_result["recruiter_screen"],
        "red_flags": red_flags,
        "top_issues": top_issues[:3],
        "next_actions": next_actions[:3],
    }
