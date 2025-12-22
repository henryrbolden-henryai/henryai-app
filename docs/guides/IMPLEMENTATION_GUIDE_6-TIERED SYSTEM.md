# HenryHQ Implementation Guide for Claude Code

**Date**: December 21, 2025
**Priority**: P0 (Critical Path)
**Scope**: Six-Tier Scoring System, Score-Decision Lock, Reality Check Rebuild, Seniority-Aware Guidance

---

## Executive Summary

This document provides implementation instructions for Claude Code to fix six critical issues identified during Round 2 testing of the Job Fit Scoring system. The primary goal is to eliminate score-decision mismatches (e.g., 78% fit with "Do Not Apply") and implement honest, tiered guidance.

**Critical Rule**: After these changes, it should be **impossible** for a high score (70%+) to pair with "Do Not Apply" or for a low score (<40%) to pair with "Strong Apply."

---

## Part 1: Six-Tier Recommendation System

### Current State (Broken)

The current system uses inconsistent tiers that allow invalid score-decision combinations:
- 78% score → "Do Not Apply" (INVALID)
- 55% score → "Apply" (INVALID)

### Target State (Fixed)

Implement a strict six-tier system with hardcoded boundaries:

| Score Range | Decision | Meaning | Never Allow |
|-------------|----------|---------|-------------|
| 85-100 | **Strong Apply** | Top-tier match. Prioritize this application. | anything else |
| 70-84 | **Apply** | Solid fit. Worth your time and energy. | Do Not Apply, Long Shot |
| 55-69 | **Consider** | Moderate fit. Apply if genuinely interested. | Strong Apply, Do Not Apply |
| 40-54 | **Apply with Caution** | Stretch role. Need positioning and possibly referral. | Apply, Strong Apply |
| 25-39 | **Long Shot** | Significant gaps. Only with inside connection. | anything above Caution |
| 0-24 | **Do Not Apply** | Not your role. Invest energy elsewhere. | anything else |

### Implementation Instructions

#### Step 1: Update `backend/recommendation/final_controller.py`

Find the `SCORE_TO_RECOMMENDATION` mapping (around line 73-80) and replace with:

```python
# Six-Tier Recommendation System - IMMUTABLE BOUNDARIES
# Per HenryHQ Scoring Spec v2.0 (Dec 21, 2025)
# These boundaries are hardcoded and may NOT be overridden

from enum import Enum

class Recommendation(str, Enum):
    STRONG_APPLY = "Strong Apply"
    APPLY = "Apply"
    CONSIDER = "Consider"
    APPLY_WITH_CAUTION = "Apply with Caution"
    LONG_SHOT = "Long Shot"
    DO_NOT_APPLY = "Do Not Apply"

# Score → Decision mapping (inclusive ranges)
SCORE_TO_RECOMMENDATION = {
    (85, 101): Recommendation.STRONG_APPLY,
    (70, 85): Recommendation.APPLY,
    (55, 70): Recommendation.CONSIDER,
    (40, 55): Recommendation.APPLY_WITH_CAUTION,
    (25, 40): Recommendation.LONG_SHOT,
    (0, 25): Recommendation.DO_NOT_APPLY,
}

# Decision → Score constraints (for invariant enforcement)
DECISION_SCORE_FLOORS = {
    Recommendation.STRONG_APPLY: 85,
    Recommendation.APPLY: 70,
    Recommendation.CONSIDER: 55,
    Recommendation.APPLY_WITH_CAUTION: 40,
    Recommendation.LONG_SHOT: 25,
    Recommendation.DO_NOT_APPLY: 0,
}

DECISION_SCORE_CEILINGS = {
    Recommendation.STRONG_APPLY: 100,
    Recommendation.APPLY: 84,
    Recommendation.CONSIDER: 69,
    Recommendation.APPLY_WITH_CAUTION: 54,
    Recommendation.LONG_SHOT: 39,
    Recommendation.DO_NOT_APPLY: 24,
}

# Invalid combinations - if detected, system MUST autocorrect
INVALID_SCORE_DECISION_PAIRS = [
    # High score + low decision = INVALID
    (lambda s: s >= 70, Recommendation.DO_NOT_APPLY, "High score (>=70) cannot pair with Do Not Apply"),
    (lambda s: s >= 70, Recommendation.LONG_SHOT, "High score (>=70) cannot pair with Long Shot"),
    (lambda s: s >= 85, Recommendation.APPLY_WITH_CAUTION, "Top score (>=85) cannot pair with Apply with Caution"),
    
    # Low score + high decision = INVALID
    (lambda s: s < 40, Recommendation.APPLY, "Low score (<40) cannot pair with Apply"),
    (lambda s: s < 55, Recommendation.STRONG_APPLY, "Score below 55 cannot pair with Strong Apply"),
    (lambda s: s < 25, Recommendation.APPLY_WITH_CAUTION, "Very low score (<25) cannot pair with Apply with Caution"),
]
```

#### Step 2: Add Score-Decision Lock Function

Add this function to `backend/recommendation/final_controller.py`:

```python
def enforce_score_decision_lock(score: int, decision: str) -> tuple[int, str]:
    """
    Enforces invariant: score and decision MUST be logically consistent.
    
    If a mismatch is detected:
    1. Log the violation
    2. Adjust score to match the decision tier ceiling
    3. Return corrected values
    
    This is the FINAL AUTHORITY on score-decision pairing.
    No downstream code may override this function's output.
    
    Args:
        score: The fit score (0-100)
        decision: The recommendation string
        
    Returns:
        tuple[int, str]: (adjusted_score, decision)
    """
    # Normalize decision to enum if string
    if isinstance(decision, str):
        try:
            decision_enum = Recommendation(decision)
        except ValueError:
            # Unknown decision - default to score-based
            decision_enum = get_recommendation_from_score(score)
            print(f"⚠️ Unknown decision '{decision}' - defaulting to {decision_enum.value}")
            return score, decision_enum.value
    else:
        decision_enum = decision
    
    # Get valid score range for this decision
    floor = DECISION_SCORE_FLOORS[decision_enum]
    ceiling = DECISION_SCORE_CEILINGS[decision_enum]
    
    # Check for invariant violation
    if score < floor or score > ceiling:
        original_score = score
        
        # Determine correction strategy:
        # - If score is TOO HIGH for decision, cap to ceiling
        # - If score is TOO LOW for decision, bump to floor
        if score > ceiling:
            adjusted_score = ceiling
            correction_type = "capped"
        else:
            adjusted_score = floor
            correction_type = "bumped"
        
        # Log the violation
        print(f"\n{'🚨' * 10}")
        print(f"SCORE-DECISION INVARIANT VIOLATION DETECTED")
        print(f"{'🚨' * 10}")
        print(f"   Original: {original_score}% with '{decision_enum.value}'")
        print(f"   Valid range for '{decision_enum.value}': {floor}-{ceiling}%")
        print(f"   Correction: Score {correction_type} to {adjusted_score}%")
        print(f"{'🚨' * 10}\n")
        
        return adjusted_score, decision_enum.value
    
    return score, decision_enum.value


def get_recommendation_from_score(score: int) -> Recommendation:
    """
    Get the correct recommendation for a given score.
    This is the ONLY function that should determine recommendation from score.
    """
    for (low, high), rec in SCORE_TO_RECOMMENDATION.items():
        if low <= score < high:
            return rec
    
    # Edge case: exactly 100
    if score == 100:
        return Recommendation.STRONG_APPLY
    
    # Fallback for invalid scores
    if score < 0:
        return Recommendation.DO_NOT_APPLY
    return Recommendation.STRONG_APPLY


def validate_score_decision_pair(score: int, decision: str) -> dict:
    """
    Validate a score-decision pair and return diagnostics.
    
    Returns:
        dict with keys:
        - valid: bool
        - expected_decision: str
        - violation_type: str or None
        - correction_needed: bool
        - corrected_score: int
        - corrected_decision: str
    """
    expected = get_recommendation_from_score(score)
    decision_enum = Recommendation(decision) if isinstance(decision, str) else decision
    
    if expected != decision_enum:
        corrected_score, corrected_decision = enforce_score_decision_lock(score, decision)
        return {
            "valid": False,
            "expected_decision": expected.value,
            "actual_decision": decision_enum.value,
            "violation_type": "score_decision_mismatch",
            "correction_needed": True,
            "corrected_score": corrected_score,
            "corrected_decision": corrected_decision,
        }
    
    return {
        "valid": True,
        "expected_decision": expected.value,
        "actual_decision": decision_enum.value,
        "violation_type": None,
        "correction_needed": False,
        "corrected_score": score,
        "corrected_decision": decision,
    }
```

#### Step 3: Update `backend/backend.py` - `force_apply_experience_penalties()`

Find the function `force_apply_experience_penalties` (around line 5246) and update the recommendation logic.

**Replace the legacy recommendation mapping (around lines 5657-5680) with:**

```python
    # ========================================================================
    # FINAL RECOMMENDATION - SIX-TIER SYSTEM WITH INVARIANT ENFORCEMENT
    # Per HenryHQ Scoring Spec v2.0 (Dec 21, 2025)
    # ========================================================================
    
    if FINAL_CONTROLLER_AVAILABLE:
        from recommendation.final_controller import (
            get_recommendation_from_score,
            enforce_score_decision_lock,
            Recommendation,
        )
        
        # Get recommendation from score (single source of truth)
        if recommendation_locked and locked_recommendation:
            # Eligibility failure - use locked recommendation but enforce score cap
            raw_recommendation = Recommendation(locked_recommendation)
            capped_score, final_recommendation = enforce_score_decision_lock(
                capped_score, locked_recommendation
            )
        else:
            # Normal path - derive recommendation from score
            raw_recommendation = get_recommendation_from_score(capped_score)
            capped_score, final_recommendation = enforce_score_decision_lock(
                capped_score, raw_recommendation.value
            )
        
        correct_recommendation = final_recommendation
        
        print("\n" + "=" * 80)
        print("🔒 SIX-TIER RECOMMENDATION SYSTEM - INVARIANT ENFORCED")
        print("=" * 80)
        print(f"   Score: {capped_score}%")
        print(f"   Recommendation: {correct_recommendation}")
        print(f"   Eligibility: {'PASSED' if not recommendation_locked else 'FAILED'}")
        print("=" * 80 + "\n")
        
    else:
        # Fallback six-tier mapping (if controller not available)
        if capped_score >= 85:
            correct_recommendation = "Strong Apply"
        elif capped_score >= 70:
            correct_recommendation = "Apply"
        elif capped_score >= 55:
            correct_recommendation = "Consider"
        elif capped_score >= 40:
            correct_recommendation = "Apply with Caution"
        elif capped_score >= 25:
            correct_recommendation = "Long Shot"
        else:
            correct_recommendation = "Do Not Apply"
        
        # Override for eligibility failure
        if recommendation_locked:
            # Cap score to match locked decision
            if locked_recommendation == "Do Not Apply":
                capped_score = min(capped_score, 24)
                correct_recommendation = "Do Not Apply"
            elif locked_recommendation == "Long Shot":
                capped_score = min(capped_score, 39)
                correct_recommendation = "Long Shot"
```

**Also update the alternative_actions mapping:**

```python
    # Generate tier-appropriate alternative actions
    if correct_recommendation == "Strong Apply":
        alternative_actions = [
            "Apply immediately - you're a top-tier match for this role",
            "Reach out directly to the hiring manager on LinkedIn",
            "This should be a priority application in your pipeline"
        ]
    elif correct_recommendation == "Apply":
        alternative_actions = [
            "Solid fit - apply within the next 24-48 hours",
            "Lead with your strongest, most relevant accomplishments",
            "Consider reaching out to someone at the company for an intro"
        ]
    elif correct_recommendation == "Consider":
        alternative_actions = [
            "Worth pursuing if you're genuinely interested in this company/role",
            "Address the experience gaps proactively in your cover letter",
            "Don't prioritize this over stronger fits in your pipeline"
        ]
    elif correct_recommendation == "Apply with Caution":
        alternative_actions = [
            "This is a stretch role - you'll need strong positioning",
            "Network with someone at the company before applying if possible",
            "Lead with your most transferable accomplishments"
        ]
    elif correct_recommendation == "Long Shot":
        alternative_actions = [
            "Only pursue if you have an inside connection or unique angle",
            "Consider targeting roles 1-2 levels below this one at the same company",
            f"Build 1-2 more years of experience before targeting {required_years}+ year roles"
        ]
    else:  # Do Not Apply
        alternative_actions = [
            f"Target roles requiring {max(1, int(candidate_years))}-{int(candidate_years) + 2} years of experience",
            "This role requires fundamentally different experience than you have",
            "Focus your energy on roles where you're a stronger match"
        ]
```

---

## Part 2: The Opportunity Section Schema

### Problem

Current "Reality Check" explains the market generically. It should answer strategic questions.

### Target Schema

The Opportunity section must answer these five questions:

1. **Why now?** - What makes this moment strategic for applying?
2. **Why this org?** - What's happening at this company that creates opportunity?
3. **Why this team?** - What does this team own and why does it matter?
4. **What it opens** - What does this role unlock in 18-24 months?
5. **Behind the scenes** - What's the internal context a candidate wouldn't see?

### Implementation Instructions

#### Step 1: Create New Signal Classes

Add to `backend/reality_check/signal_detectors.py`:

```python
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class OpportunitySignalType(str, Enum):
    WHY_NOW = "why_now"
    WHY_THIS_ORG = "why_this_org"
    WHY_THIS_TEAM = "why_this_team"
    WHAT_IT_OPENS = "what_it_opens"
    BEHIND_THE_SCENES = "behind_the_scenes"


@dataclass
class OpportunitySignal:
    signal_type: OpportunitySignalType
    headline: str
    explanation: str
    strategic_insight: str
    confidence: float  # 0.0 - 1.0


def detect_opportunity_signals(
    jd_data: Dict[str, Any],
    resume_data: Dict[str, Any],
    company_intel: Optional[Dict[str, Any]] = None
) -> Dict[str, OpportunitySignal]:
    """
    Detect opportunity signals for The Opportunity section.
    
    Returns a dict with keys: why_now, why_this_org, why_this_team, 
    what_it_opens, behind_the_scenes
    """
    signals = {}
    
    company = jd_data.get("company_name", "").lower()
    role_title = jd_data.get("role_title", "").lower()
    role_level = detect_role_level(role_title)
    jd_text = jd_data.get("job_description", "").lower()
    
    # =========================================================================
    # WHY NOW - Timing signals
    # =========================================================================
    why_now_signals = []
    
    # Hiring velocity signals
    if any(phrase in jd_text for phrase in ["growing team", "rapidly expanding", "new team"]):
        why_now_signals.append("Team is actively growing - hiring momentum is high")
    
    # Urgency signals
    if any(phrase in jd_text for phrase in ["immediate", "asap", "urgent", "start date"]):
        why_now_signals.append("Role has urgency - faster hiring process likely")
    
    # Budget cycle signals
    current_month = datetime.now().month
    if current_month in [1, 2, 7, 8]:  # Q1 or Q3 start
        why_now_signals.append("New budget cycle - fresh headcount approvals")
    
    # Backfill signals
    if any(phrase in jd_text for phrase in ["backfill", "replacement", "previous"]):
        why_now_signals.append("Backfill role - defined scope and expectations exist")
    
    signals["why_now"] = OpportunitySignal(
        signal_type=OpportunitySignalType.WHY_NOW,
        headline="Why now?",
        explanation=" | ".join(why_now_signals) if why_now_signals else "Standard hiring timeline - no special urgency signals detected",
        strategic_insight=_generate_timing_insight(why_now_signals),
        confidence=0.8 if why_now_signals else 0.5
    )
    
    # =========================================================================
    # WHY THIS ORG - Company trajectory signals
    # =========================================================================
    org_signals = []
    
    # Company stage detection
    if any(phrase in jd_text for phrase in ["series a", "series b", "series c", "startup"]):
        org_signals.append("Growth-stage company - high impact potential, equity upside")
    elif any(phrase in jd_text for phrase in ["fortune 500", "global", "enterprise"]):
        org_signals.append("Established enterprise - stability, brand credibility")
    elif any(phrase in jd_text for phrase in ["ipo", "pre-ipo", "public company"]):
        org_signals.append("IPO trajectory - potential liquidity event")
    
    # Brand leverage detection
    high_brand_companies = [
        "google", "meta", "amazon", "apple", "microsoft", "netflix",
        "warner bros", "disney", "nike", "goldman", "mckinsey", "stripe",
        "airbnb", "uber", "spotify", "salesforce"
    ]
    if any(b in company for b in high_brand_companies):
        org_signals.append(f"High-brand company - significant resume value")
    
    signals["why_this_org"] = OpportunitySignal(
        signal_type=OpportunitySignalType.WHY_THIS_ORG,
        headline="Why this org?",
        explanation=" | ".join(org_signals) if org_signals else "Standard company profile - evaluate based on role fit",
        strategic_insight=_generate_org_insight(org_signals, company),
        confidence=0.7 if org_signals else 0.4
    )
    
    # =========================================================================
    # WHY THIS TEAM - Team mandate signals
    # =========================================================================
    team_signals = []
    
    # Strategic priority signals
    if any(phrase in jd_text for phrase in ["strategic", "critical", "key initiative", "top priority"]):
        team_signals.append("Strategic priority team - high visibility to leadership")
    
    # Revenue signals
    if any(phrase in jd_text for phrase in ["revenue", "p&l", "profit", "growth"]):
        team_signals.append("Revenue-impacting team - clear success metrics")
    
    # New vs established
    if any(phrase in jd_text for phrase in ["new team", "building", "0 to 1", "greenfield"]):
        team_signals.append("New/building team - opportunity to shape direction")
    elif any(phrase in jd_text for phrase in ["established", "mature", "scaled"]):
        team_signals.append("Established team - existing playbook and support")
    
    signals["why_this_team"] = OpportunitySignal(
        signal_type=OpportunitySignalType.WHY_THIS_TEAM,
        headline="Why this team?",
        explanation=" | ".join(team_signals) if team_signals else "Team context not clear from JD - ask in interviews",
        strategic_insight=_generate_team_insight(team_signals),
        confidence=0.6 if team_signals else 0.3
    )
    
    # =========================================================================
    # WHAT IT OPENS - Career trajectory signals
    # =========================================================================
    trajectory_signals = []
    
    # Level signals
    if role_level == "entry":
        trajectory_signals.append("Entry point - focus on skill building and internal mobility")
    elif role_level == "mid":
        trajectory_signals.append("Mid-level - path to senior/lead within 2-3 years")
    elif role_level == "senior":
        trajectory_signals.append("Senior IC or Manager path - choose your trajectory")
    elif role_level == "director_plus":
        trajectory_signals.append("Executive trajectory - builds toward VP/C-suite")
    
    # Skill development signals
    if any(phrase in jd_text for phrase in ["mentorship", "coaching", "development"]):
        trajectory_signals.append("Development-focused culture - accelerated learning")
    
    # Internal mobility signals
    if any(phrase in jd_text for phrase in ["internal mobility", "growth opportunities", "career path"]):
        trajectory_signals.append("Strong internal mobility - multiple path options")
    
    signals["what_it_opens"] = OpportunitySignal(
        signal_type=OpportunitySignalType.WHAT_IT_OPENS,
        headline="What it opens",
        explanation=" | ".join(trajectory_signals) if trajectory_signals else "Standard career progression path",
        strategic_insight=_generate_trajectory_insight(trajectory_signals, role_level),
        confidence=0.7 if trajectory_signals else 0.5
    )
    
    # =========================================================================
    # BEHIND THE SCENES - Internal context signals
    # =========================================================================
    internal_signals = []
    
    # Reorg/restructure signals
    merger_companies = ["warner bros discovery", "wbd", "microsoft activision", "amazon mgm"]
    if any(m in company for m in merger_companies):
        internal_signals.append("Post-merger org - restructuring creates opportunity for adaptable performers")
    
    # Leadership change signals
    if any(phrase in jd_text for phrase in ["new leadership", "new ceo", "transformation"]):
        internal_signals.append("Leadership transition - new priorities being set")
    
    # Layoff recovery signals
    layoff_recovery_companies = ["meta", "amazon", "google", "microsoft", "salesforce", "stripe"]
    if any(c in company for c in layoff_recovery_companies):
        internal_signals.append("Post-layoff hiring - leaner org, higher expectations per role")
    
    signals["behind_the_scenes"] = OpportunitySignal(
        signal_type=OpportunitySignalType.BEHIND_THE_SCENES,
        headline="Behind the scenes",
        explanation=" | ".join(internal_signals) if internal_signals else "No unusual internal dynamics detected",
        strategic_insight=_generate_internal_insight(internal_signals),
        confidence=0.5 if internal_signals else 0.3
    )
    
    return signals


def detect_role_level(role_title: str) -> str:
    """Detect seniority level from role title."""
    role_lower = role_title.lower()
    
    if any(x in role_lower for x in ["vp", "vice president", "director", "head of", "chief", "c-suite"]):
        return "director_plus"
    elif any(x in role_lower for x in ["senior", "staff", "principal", "lead"]):
        return "senior"
    elif any(x in role_lower for x in ["associate", "junior", "entry", "i ", " i", "1"]):
        return "entry"
    else:
        return "mid"


def _generate_timing_insight(signals: List[str]) -> str:
    if not signals:
        return "Apply when ready - no special timing advantage detected."
    if len(signals) >= 2:
        return "Multiple timing signals suggest this is a good moment to apply. Move quickly."
    return "Timing appears favorable. Apply within the next week if interested."


def _generate_org_insight(signals: List[str], company: str) -> str:
    if "High-brand company" in str(signals):
        return f"Time at {company.title()} adds significant credibility to your resume for future opportunities."
    if "Growth-stage" in str(signals):
        return "Growth-stage company offers higher impact but less stability. Evaluate risk tolerance."
    return "Evaluate company culture and trajectory during interviews."


def _generate_team_insight(signals: List[str]) -> str:
    if "Strategic priority" in str(signals):
        return "Strategic teams get more resources and executive attention. High visibility, high expectations."
    if "New/building team" in str(signals):
        return "New teams offer more autonomy but less established process. Good for builders."
    return "Dig into team dynamics during interviews - ask about reporting structure and team tenure."


def _generate_trajectory_insight(signals: List[str], level: str) -> str:
    insights = {
        "entry": "Focus on learning velocity and internal mobility options. 18-24 months to next level.",
        "mid": "This role should position you for senior/lead within 2-3 years if you perform.",
        "senior": "At this level, you're choosing between IC depth or management path. Clarify in interviews.",
        "director_plus": "Executive roles are about building leverage. What scope does this role unlock?"
    }
    return insights.get(level, "Standard progression path - performance determines trajectory.")


def _generate_internal_insight(signals: List[str]) -> str:
    if "Post-merger" in str(signals):
        return "Post-merger orgs are politically complex but offer faster advancement for adaptable performers."
    if "Post-layoff" in str(signals):
        return "Leaner orgs post-layoff mean higher expectations per role. Prepare to demonstrate immediate impact."
    return "No unusual internal dynamics detected. Standard org context."
```

#### Step 2: Integrate into Analysis Response

Update `backend/backend.py` to include The Opportunity in the analysis response. Find where `reality_check` is added to the response and add:

```python
    # =========================================================================
    # THE OPPORTUNITY - Strategic Context Section
    # Per HenryHQ Spec: Answers Why now? Why this org? Why this team? 
    # What it opens? Behind the scenes?
    # =========================================================================
    from reality_check.signal_detectors import detect_opportunity_signals
    
    opportunity_signals = detect_opportunity_signals(
        jd_data={
            "company_name": response_data.get("company_name", ""),
            "role_title": response_data.get("role_title", ""),
            "job_description": request.job_description or "",
        },
        resume_data=request.resume or {}
    )
    
    # Format for frontend
    the_opportunity = {
        "why_now": {
            "headline": opportunity_signals["why_now"].headline,
            "content": opportunity_signals["why_now"].explanation,
            "strategic_insight": opportunity_signals["why_now"].strategic_insight,
        },
        "why_this_org": {
            "headline": opportunity_signals["why_this_org"].headline,
            "content": opportunity_signals["why_this_org"].explanation,
            "strategic_insight": opportunity_signals["why_this_org"].strategic_insight,
        },
        "why_this_team": {
            "headline": opportunity_signals["why_this_team"].headline,
            "content": opportunity_signals["why_this_team"].explanation,
            "strategic_insight": opportunity_signals["why_this_team"].strategic_insight,
        },
        "what_it_opens": {
            "headline": opportunity_signals["what_it_opens"].headline,
            "content": opportunity_signals["what_it_opens"].explanation,
            "strategic_insight": opportunity_signals["what_it_opens"].strategic_insight,
        },
        "behind_the_scenes": {
            "headline": opportunity_signals["behind_the_scenes"].headline,
            "content": opportunity_signals["behind_the_scenes"].explanation,
            "strategic_insight": opportunity_signals["behind_the_scenes"].strategic_insight,
        },
    }
    
    response_data["the_opportunity"] = the_opportunity
```

---

## Part 3: Seniority-Aware Guidance

### Problem

Executive candidates (VP+) receive junior-level advice like "Polish your resume" - this is insulting and wastes their time.

### Implementation Instructions

#### Step 1: Add Seniority Detection

Add to `backend/backend.py` or create new file `backend/seniority_detector.py`:

```python
def detect_candidate_seniority(resume_data: dict) -> str:
    """
    Classify candidate seniority for appropriate coaching depth.
    
    Returns: 'executive', 'director', 'manager', 'ic'
    
    Detection hierarchy:
    1. Executive: VP+, C-suite, President, Head of
    2. Director: Director-level titles
    3. Manager: Manager, Lead, Principal, Staff titles
    4. IC: Individual contributor (default)
    """
    titles = []
    for exp in resume_data.get("experience", []):
        title = (exp.get("title") or "").lower()
        if title:
            titles.append(title)
    
    # VP+ / Executive detection
    exec_patterns = [
        "vp", "vice president", "svp", "evp", "ceo", "cfo", "cto", 
        "cmo", "coo", "cpo", "president", "chief", "head of", 
        "general manager", "managing director"
    ]
    if any(any(p in t for p in exec_patterns) for t in titles):
        return "executive"
    
    # Director detection
    director_patterns = ["director"]
    if any(any(p in t for p in director_patterns) for t in titles):
        return "director"
    
    # Manager detection
    manager_patterns = ["manager", "lead", "principal", "staff", "senior"]
    if any(any(p in t for p in manager_patterns) for t in titles):
        return "manager"
    
    return "ic"


# Seniority-specific guidance constraints
SENIORITY_GUIDANCE_RULES = {
    "executive": {
        "allowed": [
            "leverage_strategy",
            "relationship_guidance", 
            "narrative_framing",
            "negotiation_positioning",
            "executive_network_plays"
        ],
        "banned": [
            "resume_advice",
            "ats_tips",
            "generic_encouragement",
            "entry_level_tactics",
            "skills_gap_homework"
        ],
        "your_move_template": (
            "Your executive background positions you for {role}. "
            "Lead with {primary_strength}. "
            "Reach out directly to the hiring executive or a board connection."
        )
    },
    "director": {
        "allowed": [
            "positioning_strategy",
            "gap_mitigation",
            "selective_tactical_advice",
            "network_leverage"
        ],
        "banned": [
            "polish_your_resume",
            "entry_level_tactics",
            "basic_interview_tips"
        ],
        "your_move_template": (
            "Your director-level experience aligns with {role}. "
            "Emphasize {primary_strength} and address {top_gap} proactively. "
            "Apply and reach out to the hiring manager on LinkedIn."
        )
    },
    "manager": {
        "allowed": [
            "resume_focus",
            "gap_mitigation",
            "networking_strategy",
            "tactical_outreach"
        ],
        "banned": [
            "executive_framing",
            "board_level_language"
        ],
        "your_move_template": (
            "Your management background fits {role}. "
            "Lead with quantified team outcomes like {primary_strength}. "
            "Apply within 48 hours and follow up on LinkedIn."
        )
    },
    "ic": {
        "allowed": [
            "full_tactical_guidance",
            "resume_advice",
            "skills_development",
            "ats_optimization",
            "outreach_strategy"
        ],
        "banned": [
            "leverage_strategy",
            "executive_positioning"
        ],
        "your_move_template": (
            "Your technical background aligns with {role}. "
            "Lead with your strongest project outcomes like {primary_strength}. "
            "Apply now, tailor your resume, and follow up within a week."
        )
    }
}


def get_seniority_appropriate_guidance(
    seniority: str,
    role_title: str,
    primary_strength: str,
    top_gap: str = None
) -> dict:
    """
    Generate seniority-appropriate guidance that respects the candidate's level.
    
    Returns:
        dict with keys: your_move, allowed_content, banned_content
    """
    rules = SENIORITY_GUIDANCE_RULES.get(seniority, SENIORITY_GUIDANCE_RULES["ic"])
    
    # Format the your_move template
    your_move = rules["your_move_template"].format(
        role=role_title,
        primary_strength=primary_strength,
        top_gap=top_gap or "any experience gaps"
    )
    
    return {
        "your_move": your_move,
        "allowed_content": rules["allowed"],
        "banned_content": rules["banned"],
        "seniority_tier": seniority
    }


def filter_guidance_for_seniority(
    guidance_content: str,
    seniority: str
) -> str:
    """
    Filter out inappropriate guidance for the candidate's seniority level.
    
    For executives: Remove resume tips, ATS advice, basic interview prep
    For ICs: Remove executive networking strategies, board-level language
    """
    rules = SENIORITY_GUIDANCE_RULES.get(seniority, SENIORITY_GUIDANCE_RULES["ic"])
    banned = rules["banned"]
    
    # Phrases to remove for executives
    executive_banned_phrases = [
        "polish your resume",
        "tailor your resume",
        "optimize for ATS",
        "include keywords",
        "update your LinkedIn",
        "practice your elevator pitch",
        "prepare for behavioral questions"
    ]
    
    # Phrases to remove for ICs
    ic_banned_phrases = [
        "leverage your board connections",
        "reach out to the CEO directly",
        "executive presence",
        "C-suite network"
    ]
    
    if seniority == "executive":
        for phrase in executive_banned_phrases:
            guidance_content = guidance_content.replace(phrase, "")
    elif seniority == "ic":
        for phrase in ic_banned_phrases:
            guidance_content = guidance_content.replace(phrase, "")
    
    # Clean up double spaces
    guidance_content = " ".join(guidance_content.split())
    
    return guidance_content
```

#### Step 2: Integrate Seniority Detection into Analysis

Update `force_apply_experience_penalties()` to detect and use seniority:

```python
    # =========================================================================
    # SENIORITY DETECTION - Gate coaching content appropriately
    # =========================================================================
    candidate_seniority = "ic"  # default
    if resume_data:
        candidate_seniority = detect_candidate_seniority(resume_data)
        print(f"   👤 Candidate seniority detected: {candidate_seniority.upper()}")
        
        # Store for downstream use
        response_data["candidate_seniority"] = candidate_seniority
        response_data["seniority_guidance_rules"] = SENIORITY_GUIDANCE_RULES.get(
            candidate_seniority, 
            SENIORITY_GUIDANCE_RULES["ic"]
        )
```

---

## Part 4: QA Sanitization

### Implementation Instructions

Add to `backend/backend.py` or create `backend/qa_sanitization.py`:

```python
import re
from typing import Set


def sanitize_output(text: str) -> str:
    """
    Clean generated text before response.
    
    Removes:
    - Em dashes (AI detection pattern)
    - Double spaces
    - Orphaned punctuation
    - Inconsistent capitalization
    """
    if not text:
        return text
    
    # Remove em dashes and en dashes (AI detection pattern)
    text = text.replace("—", " - ").replace("–", " - ")
    
    # Fix orphaned punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Fix double spaces
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Ensure sentences start with capital after period
    text = re.sub(
        r'\.(\s+)([a-z])', 
        lambda m: '.' + m.group(1) + m.group(2).upper(), 
        text
    )
    
    # Remove trailing/leading whitespace
    text = text.strip()
    
    return text


# Track recent outputs for duplicate detection
_recent_outputs: Set[str] = set()
_max_recent_outputs = 100


def check_output_leakage(current_output: str, threshold: float = 0.8) -> bool:
    """
    Check if current output is too similar to recent outputs.
    
    This prevents cross-candidate leakage where the same generic
    text is reused across different analyses.
    
    Returns True if leakage detected (output should be regenerated).
    """
    from difflib import SequenceMatcher
    
    if not current_output or len(current_output) < 50:
        return False
    
    # Normalize for comparison
    normalized = current_output.lower().strip()
    
    for recent in _recent_outputs:
        similarity = SequenceMatcher(None, normalized, recent).ratio()
        if similarity > threshold:
            print(f"⚠️ OUTPUT LEAKAGE DETECTED: {similarity:.1%} similarity to recent output")
            return True
    
    # Add to recent outputs (FIFO if over limit)
    _recent_outputs.add(normalized)
    if len(_recent_outputs) > _max_recent_outputs:
        _recent_outputs.pop()
    
    return False


def validate_output_quality(output: dict) -> dict:
    """
    Validate output quality and return issues.
    
    Checks:
    - Em dashes present
    - Repeated phrases
    - Generic filler language
    - Cross-candidate leakage
    """
    issues = []
    
    # Flatten output to text for analysis
    text_fields = []
    for key, value in output.items():
        if isinstance(value, str):
            text_fields.append(value)
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, str):
                    text_fields.append(v)
    
    full_text = " ".join(text_fields)
    
    # Check for em dashes
    if "—" in full_text or "–" in full_text:
        issues.append({
            "type": "em_dash_detected",
            "severity": "medium",
            "message": "Em dashes detected - should be replaced with hyphens"
        })
    
    # Check for generic filler
    generic_phrases = [
        "I believe", "I think", "I feel",
        "results-driven", "team player", "hard worker",
        "detail-oriented", "self-starter"
    ]
    for phrase in generic_phrases:
        if phrase.lower() in full_text.lower():
            issues.append({
                "type": "generic_filler",
                "severity": "low",
                "message": f"Generic phrase detected: '{phrase}'"
            })
    
    # Check for leakage
    if check_output_leakage(full_text):
        issues.append({
            "type": "potential_leakage",
            "severity": "high",
            "message": "Output too similar to recent analysis - possible cross-candidate contamination"
        })
    
    return {
        "valid": len([i for i in issues if i["severity"] == "high"]) == 0,
        "issues": issues,
        "issue_count": len(issues)
    }
```

---

## Part 5: Documentation Updates

### Files to Update

Claude Code should update these documentation files to reflect the six-tier system:

#### 1. Update `PRODUCT_STRATEGY_ROADMAP.md`

Find the section on "6-Tier Recommendation System" and ensure it matches:

```markdown
### Six-Tier Recommendation System (Implemented Dec 21, 2025)

| Score Range | Decision | Meaning |
|-------------|----------|---------|
| 85-100 | **Strong Apply** | Top-tier match. Prioritize this application. |
| 70-84 | **Apply** | Solid fit. Worth your time and energy. |
| 55-69 | **Consider** | Moderate fit. Apply if genuinely interested. |
| 40-54 | **Apply with Caution** | Stretch role. Need positioning and referral. |
| 25-39 | **Long Shot** | Significant gaps. Only with inside connection. |
| 0-24 | **Do Not Apply** | Not your role. Invest energy elsewhere. |

**Invariant Rule**: Score and decision MUST be logically consistent. A score of 78% can NEVER pair with "Do Not Apply". The backend enforces this automatically.
```

#### 2. Update `IMPLEMENTATION_GUIDE.md`

Add a new section:

```markdown
## Six-Tier Scoring System (Dec 21, 2025)

### Score-Decision Lock

The system now enforces strict invariants between scores and decisions:

```python
# Valid combinations only
SCORE_TO_RECOMMENDATION = {
    (85, 101): "Strong Apply",
    (70, 85): "Apply",
    (55, 70): "Consider",
    (40, 55): "Apply with Caution",
    (25, 40): "Long Shot",
    (0, 25): "Do Not Apply",
}
```

If an invalid combination is detected (e.g., 78% with "Do Not Apply"), the system automatically corrects by capping the score to match the decision tier.

### The Opportunity Section

Reality Check has been enhanced to answer five strategic questions:

1. **Why now?** - Timing signals (budget cycles, urgency, hiring velocity)
2. **Why this org?** - Company trajectory (stage, brand value, growth)
3. **Why this team?** - Team mandate (strategic priority, revenue impact)
4. **What it opens** - Career trajectory (18-24 month outlook)
5. **Behind the scenes** - Internal context (reorgs, M&A, layoff recovery)
```

#### 3. Update `IMPROVEMENTS_SUMMARY.md`

Add to the December 2025 section:

```markdown
### Six-Tier Scoring System (Dec 21, 2025)

**Problem Solved**: Score-decision mismatches (78% fit with "Do Not Apply")

**Implementation**:
- Strict six-tier boundaries with invariant enforcement
- Automatic score correction if mismatch detected
- Seniority-aware guidance (executives don't get resume tips)
- The Opportunity section answers strategic questions

**Files Modified**:
- `backend/recommendation/final_controller.py` - Six-tier mapping
- `backend/backend.py` - `force_apply_experience_penalties()` updated
- `backend/reality_check/signal_detectors.py` - Opportunity signals added
- `backend/seniority_detector.py` - New file for seniority detection
- `backend/qa_sanitization.py` - New file for output quality

**Impact**:
- Zero score-decision mismatches possible
- Executives receive appropriate guidance
- Reality Check provides strategic context
- Output quality improved (no em dashes, no leakage)
```

---

## Part 6: Testing Checklist

After implementation, Claude Code should run these tests:

### Test 1: Score-Decision Invariant

```python
# These should all pass without correction
assert validate_score_decision_pair(88, "Strong Apply")["valid"] == True
assert validate_score_decision_pair(75, "Apply")["valid"] == True
assert validate_score_decision_pair(60, "Consider")["valid"] == True
assert validate_score_decision_pair(45, "Apply with Caution")["valid"] == True
assert validate_score_decision_pair(30, "Long Shot")["valid"] == True
assert validate_score_decision_pair(20, "Do Not Apply")["valid"] == True

# These should trigger correction
assert validate_score_decision_pair(78, "Do Not Apply")["valid"] == False
assert validate_score_decision_pair(85, "Apply with Caution")["valid"] == False
assert validate_score_decision_pair(30, "Apply")["valid"] == False
```

### Test 2: Seniority Detection

```python
# Executive detection
exec_resume = {"experience": [{"title": "VP of Product"}]}
assert detect_candidate_seniority(exec_resume) == "executive"

# Director detection
dir_resume = {"experience": [{"title": "Director of Engineering"}]}
assert detect_candidate_seniority(dir_resume) == "director"

# Manager detection
mgr_resume = {"experience": [{"title": "Senior Product Manager"}]}
assert detect_candidate_seniority(mgr_resume) == "manager"

# IC detection
ic_resume = {"experience": [{"title": "Software Engineer"}]}
assert detect_candidate_seniority(ic_resume) == "ic"
```

### Test 3: QA Sanitization

```python
# Em dash removal
assert "—" not in sanitize_output("This is a test — with em dash")
assert "–" not in sanitize_output("This is a test – with en dash")

# Double space removal
assert "  " not in sanitize_output("This has  double spaces")

# Capitalization fix
assert sanitize_output("first sentence. second sentence.") == "First sentence. Second sentence."
```

---

## Execution Order

1. **P0 (Day 1)**: Six-tier system + score-decision lock
2. **P0 (Day 1)**: QA sanitization
3. **P1 (Day 2)**: Seniority detection + guidance gating
4. **P1 (Day 2-3)**: The Opportunity section
5. **P2 (Day 3)**: Documentation updates
6. **P2 (Day 3)**: Testing + validation

---

## Success Criteria

After implementation:

- [ ] No score-decision mismatches possible (invariant enforced)
- [ ] Six-tier system consistently applied across all analyses
- [ ] Executives receive relationship/leverage guidance, not resume tips
- [ ] The Opportunity section answers all five strategic questions
- [ ] No em dashes in any output
- [ ] No cross-candidate leakage detected
- [ ] All documentation reflects six-tier system

---

**Document Version**: 1.1
**Created**: December 21, 2025
**Last Updated**: December 22, 2025
**Author**: HenryHQ Product Team

---

## Appendix: Pre-Launch QA Results (December 22, 2025)

### Bugs Fixed During QA

**1. Document Generation - Education Details Bug**
- **Issue**: Education details appeared character-by-character in DOCX output
- **Root Cause**: `document_generator/resume_formatter.py` line 332 iterated over string as chars
- **Fix**: Convert string to single-item list before iteration
- **File**: `document_generator/resume_formatter.py`

**2. Document Generation - Skills Capitalization**
- **Issue**: Skills categories showed "technical" instead of "Technical"
- **Fix**: Added `.title()` to category names
- **File**: `backend/document_generator.py`

**3. URL Extraction - False Positive Captcha Detection**
- **Issue**: Valid job posting URLs flagged as captcha-blocked
- **Fix**: Changed broad "captcha" detection to specific blocking patterns
- **File**: `backend/backend.py`

### Test Results

| Test | Result | Notes |
|------|--------|-------|
| Resume Parsing | 10/10 ✅ | All edge cases passed |
| Document Generation | 7/7 ✅ | Bugs fixed and verified |
| LinkedIn Upload | 3/3 ✅ | All profiles parsed correctly |
| Error Handling | All ✅ | Proper validation errors |
| Tracker API | ✅ | CRUD + status transitions |

### Critical Discovery

**Railway Deployment Architecture**: Railway uses the `document_generator/` module directory, NOT `backend/document_generator.py`. The Dockerfile confirms: `COPY document_generator/ ./document_generator/`. All production fixes must go in the module directory.

### Remaining Manual Tests

1. Ask Henry Context Awareness
2. Mock Interview Feedback Quality
3. Screening Questions Analysis
4. Calendar Integration
