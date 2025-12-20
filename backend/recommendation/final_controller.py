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

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Recommendation(Enum):
    """Canonical recommendation values. No aliases."""
    DO_NOT_APPLY = "Do Not Apply"
    APPLY_WITH_CAUTION = "Apply with Caution"
    CONDITIONAL_APPLY = "Conditional Apply"
    APPLY = "Apply"
    STRONG_APPLY = "Strong Apply"


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
    """

    # Frozen mapping - DO NOT MODIFY
    SCORE_TO_RECOMMENDATION = {
        (0, 50): Recommendation.DO_NOT_APPLY,
        (50, 60): Recommendation.APPLY_WITH_CAUTION,
        (60, 70): Recommendation.APPLY_WITH_CAUTION,
        (70, 80): Recommendation.CONDITIONAL_APPLY,
        (80, 90): Recommendation.APPLY,
        (90, 101): Recommendation.STRONG_APPLY,
    }

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
        domain_gap_detected: bool = False
    ) -> FinalDecision:
        """
        Compute final recommendation from score and eligibility.

        This is called ONCE. Any subsequent call is logged and ignored.

        LOCKED MAPPING:
        - fit_score >= 85 → Apply
        - 70-84 → Conditional Apply
        - 60-69 → Apply with Caution
        - 50-59 → Apply with Caution
        - < 50 → Do Not Apply (if eligibility locked) OR Apply with Caution

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
            self._decision = FinalDecision(
                recommendation=Recommendation.DO_NOT_APPLY.value,
                fit_score=min(fit_score, 45),  # Cap at 45 if eligibility failed
                confidence="high",
                locked=True,
                locked_reason=eligibility_reason or "Eligibility gate failed",
                advisory_signals={}
            )
            print(f"   🔒 ELIGIBILITY LOCKED: {Recommendation.DO_NOT_APPLY.value}")
            return self._decision

        # ======================================================================
        # SCORE-BASED RECOMMENDATION - FROZEN MAPPING
        # ======================================================================
        recommendation = self._score_to_recommendation(fit_score)

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
            print(f"   🔄 MANAGER RULE: Domain gap suppressed (advisory only)")

        # ======================================================================
        # SET CONFIDENCE BASED ON SCORE
        # ======================================================================
        if fit_score >= 80:
            confidence = "high"
        elif fit_score >= 65:
            confidence = "medium"
        else:
            confidence = "low"

        # ======================================================================
        # LOCK THE DECISION
        # ======================================================================
        self._decision = FinalDecision(
            recommendation=recommendation.value,
            fit_score=fit_score,
            confidence=confidence,
            locked=True,
            locked_reason="Score-based mapping",
            advisory_signals=advisory_signals
        )

        print(f"   🔒 DECISION LOCKED: {recommendation.value} ({fit_score}%)")
        return self._decision

    def _score_to_recommendation(self, score: int) -> Recommendation:
        """Apply frozen score → recommendation mapping."""
        for (low, high), rec in self.SCORE_TO_RECOMMENDATION.items():
            if low <= score < high:
                return rec
        # Fallback for edge cases
        if score >= 90:
            return Recommendation.STRONG_APPLY
        return Recommendation.DO_NOT_APPLY

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
    domain_gap_detected: bool = False
) -> Dict[str, Any]:
    """
    One-shot function to compute final recommendation.

    Use this for simple integration into existing code.
    For more control, instantiate FinalRecommendationController directly.
    """
    controller = FinalRecommendationController()
    controller.compute_recommendation(
        fit_score=fit_score,
        eligibility_passed=eligibility_passed,
        eligibility_reason=eligibility_reason,
        is_manager_role=is_manager_role,
        is_vp_plus_role=is_vp_plus_role,
        domain_gap_detected=domain_gap_detected
    )
    return controller.to_dict()
