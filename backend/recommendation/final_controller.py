# ============================================================================
# FINAL RECOMMENDATION CONTROLLER
# Single Source of Truth for all recommendation decisions
#
# PURPOSE: One controller to rule them all. Everything else is advisory.
#
# CORE INVARIANT (SYSTEM_CONTRACT.md §0):
# "If it doesn't make the candidate better, no one wins."
#
# Outputs must improve candidate decision quality.
# Do not soften, inflate, or redirect unless it materially makes the candidate better.
#
# HARD RULES:
# 1. Recommendation is set ONCE and locked
# 2. Score is set ONCE and locked
# 3. No downstream layer may mutate these values
# 4. Any override attempt is logged and ignored
# 5. Score and Decision MUST be logically consistent (INVARIANT ENFORCED)
#
# SIX-TIER RECOMMENDATION SYSTEM (Dec 21, 2025):
# Score Range | Decision           | Meaning
# 85-100      | Strong Apply       | Top-tier match. Prioritize this application.
# 70-84       | Apply              | Solid fit. Worth your time and energy.
# 55-69       | Consider           | Moderate fit. Apply if genuinely interested.
# 40-54       | Apply with Caution | Stretch role. Need positioning and referral.
# 25-39       | Long Shot          | Significant gaps. Only with inside connection.
# 0-24        | Do Not Apply       | Not your role. Invest energy elsewhere.
#
# INPUTS:
# - Eligibility Gate result (pass/fail)
# - Fit Score (0-100)
# - Role metadata (manager-level, VP+)
#
# OUTPUTS:
# - final_recommendation (immutable)
# - final_score (immutable)
# - advisory_signals (for coaching/UI, non-blocking)
#
# ============================================================================

from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class Recommendation(str, Enum):
    """
    Six-Tier Recommendation System.

    Per HenryHQ Scoring Spec v2.0 (Dec 21, 2025)
    These boundaries are hardcoded and may NOT be overridden.
    """
    STRONG_APPLY = "Strong Apply"
    APPLY = "Apply"
    CONSIDER = "Consider"
    APPLY_WITH_CAUTION = "Apply with Caution"
    LONG_SHOT = "Long Shot"
    DO_NOT_APPLY = "Do Not Apply"


# ============================================================================
# SCORE-TO-RECOMMENDATION MAPPING - IMMUTABLE BOUNDARIES
# ============================================================================

# Score -> Decision mapping (inclusive lower bound, exclusive upper bound)
SCORE_TO_RECOMMENDATION = {
    (85, 101): Recommendation.STRONG_APPLY,
    (70, 85): Recommendation.APPLY,
    (55, 70): Recommendation.CONSIDER,
    (40, 55): Recommendation.APPLY_WITH_CAUTION,
    (25, 40): Recommendation.LONG_SHOT,
    (0, 25): Recommendation.DO_NOT_APPLY,
}

# Decision -> Score constraints (for invariant enforcement)
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
INVALID_SCORE_DECISION_PAIRS: List[Tuple[Callable[[int], bool], Recommendation, str]] = [
    # High score + low decision = INVALID
    (lambda s: s >= 70, Recommendation.DO_NOT_APPLY, "High score (>=70) cannot pair with Do Not Apply"),
    (lambda s: s >= 70, Recommendation.LONG_SHOT, "High score (>=70) cannot pair with Long Shot"),
    (lambda s: s >= 85, Recommendation.APPLY_WITH_CAUTION, "Top score (>=85) cannot pair with Apply with Caution"),
    (lambda s: s >= 85, Recommendation.CONSIDER, "Top score (>=85) cannot pair with Consider"),

    # Low score + high decision = INVALID
    (lambda s: s < 40, Recommendation.APPLY, "Low score (<40) cannot pair with Apply"),
    (lambda s: s < 55, Recommendation.STRONG_APPLY, "Score below 55 cannot pair with Strong Apply"),
    (lambda s: s < 25, Recommendation.APPLY_WITH_CAUTION, "Very low score (<25) cannot pair with Apply with Caution"),
]


# ============================================================================
# SCORE-DECISION LOCK FUNCTIONS
# ============================================================================

def get_recommendation_from_score(score: int) -> Recommendation:
    """
    Get the correct recommendation for a given score.
    This is the ONLY function that should determine recommendation from score.

    Args:
        score: Fit score (0-100)

    Returns:
        Recommendation enum value
    """
    for (low, high), rec in SCORE_TO_RECOMMENDATION.items():
        if low <= score < high:
            return rec

    # Edge case: exactly 100
    if score >= 100:
        return Recommendation.STRONG_APPLY

    # Fallback for invalid scores
    if score < 0:
        return Recommendation.DO_NOT_APPLY
    return Recommendation.STRONG_APPLY


def enforce_score_decision_lock(score: int, decision: str) -> Tuple[int, str]:
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
            print(f"   ⚠️ Unknown decision '{decision}' - defaulting to {decision_enum.value}")
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


def validate_score_decision_pair(score: int, decision: str) -> Dict[str, Any]:
    """
    Validate a score-decision pair and return diagnostics.

    Args:
        score: Fit score (0-100)
        decision: Recommendation string

    Returns:
        dict with keys:
        - valid: bool
        - expected_decision: str
        - actual_decision: str
        - violation_type: str or None
        - correction_needed: bool
        - corrected_score: int
        - corrected_decision: str
    """
    expected = get_recommendation_from_score(score)

    try:
        decision_enum = Recommendation(decision) if isinstance(decision, str) else decision
    except ValueError:
        return {
            "valid": False,
            "expected_decision": expected.value,
            "actual_decision": decision,
            "violation_type": "unknown_decision",
            "correction_needed": True,
            "corrected_score": score,
            "corrected_decision": expected.value,
        }

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


@dataclass
class FinalDecision:
    """Immutable final decision. Once set, cannot be changed."""
    recommendation: str
    fit_score: int
    confidence: str
    locked: bool = True
    locked_reason: str = ""

    # Advisory signals - for UI/coaching, do NOT affect decision
    advisory_signals: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate recommendation is canonical."""
        valid_recs = [r.value for r in Recommendation]
        if self.recommendation not in valid_recs:
            raise ValueError(f"Invalid recommendation: {self.recommendation}. Must be one of: {valid_recs}")


class FinalRecommendationController:
    """
    THE single source of truth for job fit recommendations.

    All other controllers (CEC, Calibration, Coaching) are advisory.
    They may add context but CANNOT change the decision.

    SIX-TIER RECOMMENDATION SYSTEM (Dec 21, 2025):
    Score Range | Decision           | Meaning
    85-100      | Strong Apply       | Top-tier match. Prioritize this application.
    70-84       | Apply              | Solid fit. Worth your time and energy.
    55-69       | Consider           | Moderate fit. Apply if genuinely interested.
    40-54       | Apply with Caution | Stretch role. Need positioning and referral.
    25-39       | Long Shot          | Significant gaps. Only with inside connection.
    0-24        | Do Not Apply       | Not your role. Invest energy elsewhere.
    """

    def __init__(self):
        self._decision: Optional[FinalDecision] = None
        self._override_attempts: List[Dict[str, Any]] = []

    @property
    def decision(self) -> Optional[FinalDecision]:
        return self._decision

    @property
    def is_locked(self) -> bool:
        return self._decision is not None

    def compute_recommendation(
        self,
        fit_score: int,
        eligibility_passed: bool = True,
        eligibility_reason: str = "",
        is_manager_role: bool = False,
        is_vp_plus_role: bool = False,
        domain_gap_detected: bool = False,
        transition_info: Optional[Dict[str, Any]] = None,
        has_referral: bool = False
    ) -> FinalDecision:
        """
        Compute final recommendation from score and eligibility.

        This is called ONCE. Any subsequent call is logged and ignored.

        SIX-TIER MAPPING (Dec 21, 2025):
        - fit_score >= 85 → Strong Apply
        - 70-84 → Apply
        - 55-69 → Consider
        - 40-54 → Apply with Caution
        - 25-39 → Long Shot
        - 0-24 → Do Not Apply

        INVARIANT ENFORCEMENT:
        - Score and decision MUST be logically consistent
        - If mismatch detected, score is adjusted to match decision tier

        CAREER TRANSITION MODIFIER:
        - Career pivots with low adjacency + marginal scores get honest guidance
        - A 45% fit for a career changer isn't "Apply with Caution" - it's "Long Shot"

        MANAGER RULE:
        - Domain gaps may NEVER downgrade recommendation for managers
        - They appear as advisory signals only

        VP+ RULE:
        - Domain gaps MAY block eligibility (not implemented here, handled upstream)
        """

        # If already locked, reject attempt
        if self._decision is not None:
            self._override_attempts.append({
                "attempted_score": fit_score,
                "attempted_eligibility": eligibility_passed,
                "blocked": True,
                "reason": "Decision already locked"
            })
            print(f"   ⚠️ Recommendation override attempt blocked (already locked)")
            return self._decision

        # ======================================================================
        # ELIGIBILITY GATE - FIRST
        # ======================================================================
        if not eligibility_passed:
            # Cap score to match Do Not Apply tier ceiling (24)
            capped_score = min(fit_score, DECISION_SCORE_CEILINGS[Recommendation.DO_NOT_APPLY])

            self._decision = FinalDecision(
                recommendation=Recommendation.DO_NOT_APPLY.value,
                fit_score=capped_score,
                confidence="high",
                locked=True,
                locked_reason=eligibility_reason or "Eligibility gate failed",
                advisory_signals={}
            )
            print(f"   🔒 ELIGIBILITY LOCKED: {Recommendation.DO_NOT_APPLY.value} (score capped to {capped_score}%)")
            return self._decision

        # ======================================================================
        # SCORE-BASED RECOMMENDATION - SIX-TIER SYSTEM
        # ======================================================================
        recommendation = get_recommendation_from_score(fit_score)

        # ======================================================================
        # CAREER TRANSITION MODIFIER
        # Career pivots with marginal scores need honest guidance
        # ======================================================================
        if transition_info and transition_info.get("is_transition"):
            from backend.seniority_detector import get_transition_adjusted_decision
            transition_adjustment = get_transition_adjusted_decision(
                base_decision=recommendation.value,
                score=fit_score,
                transition_info=transition_info,
                has_referral=has_referral
            )
            if transition_adjustment.get("was_adjusted"):
                recommendation = Recommendation(transition_adjustment["adjusted_decision"])
                print(f"   🔄 CAREER TRANSITION MODIFIER: {transition_adjustment['adjustment_reason']}")
                print(f"      Decision adjusted to: {recommendation.value}")

        # ======================================================================
        # INVARIANT ENFORCEMENT - Score must match decision tier
        # ======================================================================
        enforced_score, enforced_decision = enforce_score_decision_lock(
            fit_score, recommendation.value
        )

        # ======================================================================
        # MANAGER DOMAIN GAP RULE
        # Domain gaps are advisory only for managers - they CANNOT downgrade
        # ======================================================================
        advisory_signals = {}
        if is_manager_role and domain_gap_detected:
            advisory_signals["domain_gap"] = {
                "status": "suppressed",
                "reason": "Manager-level role - domain gaps are advisory only",
                "impacts_decision": False
            }

        # Add transition info to advisory signals for UI display
        if transition_info and transition_info.get("is_transition"):
            advisory_signals["career_transition"] = {
                "is_transition": True,
                "transition_type": transition_info.get("transition_type"),
                "source_domain": transition_info.get("source_domain"),
                "target_domain": transition_info.get("target_domain"),
                "adjacency_score": transition_info.get("adjacency_score"),
                "framing": transition_info.get("framing", "")
            }

        # ======================================================================
        # SET CONFIDENCE BASED ON SCORE (six-tier adjusted)
        # ======================================================================
        if enforced_score >= 85:
            confidence = "high"
        elif enforced_score >= 70:
            confidence = "high"
        elif enforced_score >= 55:
            confidence = "medium"
        elif enforced_score >= 40:
            confidence = "medium"
        else:
            confidence = "low"

        # ======================================================================
        # LOCK THE DECISION
        # ======================================================================
        self._decision = FinalDecision(
            recommendation=enforced_decision,
            fit_score=enforced_score,
            confidence=confidence,
            locked=True,
            locked_reason="Six-tier score-based mapping with invariant enforcement",
            advisory_signals=advisory_signals
        )

        print("\n" + "=" * 80)
        print("🔒 SIX-TIER RECOMMENDATION SYSTEM - DECISION LOCKED")
        print("=" * 80)
        print(f"   Score: {enforced_score}%")
        print(f"   Recommendation: {enforced_decision}")
        print(f"   Confidence: {confidence}")
        print("=" * 80 + "\n")

        return self._decision

    def _score_to_recommendation(self, score: int) -> Recommendation:
        """
        Apply six-tier score -> recommendation mapping.

        DEPRECATED: Use get_recommendation_from_score() instead.
        Kept for backwards compatibility.
        """
        return get_recommendation_from_score(score)

    def add_advisory_signal(self, signal_type: str, signal_data: Dict[str, Any]) -> bool:
        """
        Add advisory signal (coaching context, gaps, etc.)

        These signals are for UI/coaching display only.
        They CANNOT change the recommendation or score.

        Returns: True if added, False if decision not yet made
        """
        if self._decision is None:
            print(f"   ⚠️ Cannot add advisory signal before decision is locked")
            return False

        self._decision.advisory_signals[signal_type] = signal_data
        return True

    def attempt_override(
        self,
        new_recommendation: str,
        source: str,
        reason: str
    ) -> bool:
        """
        Attempt to override recommendation.

        This will ALWAYS fail and be logged.
        Downstream layers should NOT call this - they're advisory only.

        Returns: False always (override blocked)
        """
        self._override_attempts.append({
            "attempted_recommendation": new_recommendation,
            "source": source,
            "reason": reason,
            "blocked": True
        })
        print(f"   ⚠️ Recommendation override attempt blocked: {source} tried to set {new_recommendation}")
        return False

    def get_override_log(self) -> List[Dict[str, Any]]:
        """Return log of all blocked override attempts."""
        return self._override_attempts

    def to_dict(self) -> Dict[str, Any]:
        """Export decision for API response."""
        if self._decision is None:
            return {
                "recommendation": None,
                "fit_score": None,
                "locked": False,
                "error": "Decision not yet computed"
            }

        return {
            "recommendation": self._decision.recommendation,
            "fit_score": self._decision.fit_score,
            "confidence": self._decision.confidence,
            "locked": self._decision.locked,
            "locked_reason": self._decision.locked_reason,
            "advisory_signals": self._decision.advisory_signals,
            "override_attempts_blocked": len(self._override_attempts)
        }


# ============================================================================
# CONVENIENCE FUNCTION - For integration into existing flow
# ============================================================================

def compute_final_recommendation(
    fit_score: int,
    eligibility_passed: bool = True,
    eligibility_reason: str = "",
    is_manager_role: bool = False,
    is_vp_plus_role: bool = False,
    domain_gap_detected: bool = False,
    transition_info: Optional[Dict[str, Any]] = None,
    has_referral: bool = False
) -> Dict[str, Any]:
    """
    One-shot function to compute final recommendation.

    Use this for simple integration into existing code.
    For more control, instantiate FinalRecommendationController directly.

    Args:
        fit_score: Job fit score (0-100)
        eligibility_passed: Whether eligibility gate passed
        eligibility_reason: Reason for eligibility failure
        is_manager_role: Whether this is a manager-level role
        is_vp_plus_role: Whether this is a VP+ role
        domain_gap_detected: Whether a domain gap was detected
        transition_info: Career transition info from detect_transition_candidate()
        has_referral: Whether candidate has an inside connection
    """
    controller = FinalRecommendationController()
    controller.compute_recommendation(
        fit_score=fit_score,
        eligibility_passed=eligibility_passed,
        eligibility_reason=eligibility_reason,
        is_manager_role=is_manager_role,
        is_vp_plus_role=is_vp_plus_role,
        domain_gap_detected=domain_gap_detected,
        transition_info=transition_info,
        has_referral=has_referral
    )
    return controller.to_dict()
