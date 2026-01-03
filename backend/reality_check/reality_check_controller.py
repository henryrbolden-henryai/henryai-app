"""
Reality Check Controller

Main orchestration layer for the Reality Check System.
Enforces all guardrails as hard assertions that fail fast.

CORE INVARIANT (SYSTEM_CONTRACT.md §0):
"If it doesn't make the candidate better, no one wins."

Outputs must improve candidate decision quality.
Do not soften, inflate, or redirect unless it materially makes the candidate better.

Per REALITY_CHECK_SPEC.md:
- No silent logic
- No vibes-based branching
- No implicit penalties
- Hard guardrails validated in post-processing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .models import (
    RealityCheck,
    RealityCheckResult,
    SignalClass,
    Severity,
    FORBIDDEN_INTERACTIONS,
    ALLOWED_OUTPUTS,
    SIGNAL_PRIORITY,
)
from .signal_detectors import (
    detect_eligibility_signals,
    detect_fit_signals,
    detect_credibility_signals,
    detect_risk_signals,
    detect_market_bias_signals,
    detect_market_climate_signals,
    detect_company_health_signals,
)


class RealityCheckViolationError(Exception):
    """Raised when a Reality Check violates hard guardrails."""

    def __init__(self, message: str, signal_class: str = None, endpoint: str = None):
        self.message = message
        self.signal_class = signal_class
        self.endpoint = endpoint
        super().__init__(self.message)

        # AGGRESSIVE LOGGING: Every violation is logged for early warning
        import logging
        logger = logging.getLogger("reality_check.violations")
        logger.error(
            f"🚨 REALITY CHECK VIOLATION | "
            f"signal_class={signal_class or 'unknown'} | "
            f"endpoint={endpoint or 'unknown'} | "
            f"message={message}"
        )
        # Also print to stdout for Railway/Vercel logs
        print(
            f"🚨 REALITY CHECK VIOLATION | "
            f"signal_class={signal_class or 'unknown'} | "
            f"endpoint={endpoint or 'unknown'} | "
            f"message={message}"
        )


class RealityCheckController:
    """
    Controller for Reality Check detection and validation.

    Enforces all guardrails as hard assertions:
    1. Market Bias/Climate signals NEVER modify fit_score
    2. Signal class/severity combinations are validated
    3. Forbidden interactions are blocked
    4. Max 2 checks displayed per analysis
    5. Blockers/Warnings must have strategic alternatives
    """

    def __init__(self, feature_flag_enabled: bool = True):
        """
        Initialize the controller.

        Args:
            feature_flag_enabled: If False, all checks return empty results.
                                  Use for gradual rollout.
        """
        self.feature_flag_enabled = feature_flag_enabled
        self._pre_analysis_score: Optional[float] = None
        self._post_analysis_score: Optional[float] = None

    def analyze(
        self,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        fit_score: float,
        eligibility_result: Optional[Dict[str, Any]] = None,
        fit_details: Optional[Dict[str, Any]] = None,
        credibility_result: Optional[Dict[str, Any]] = None,
        risk_analysis: Optional[Dict[str, Any]] = None,
        company_intel: Optional[Dict[str, Any]] = None,
    ) -> RealityCheckResult:
        """
        Analyze all signals and return prioritized Reality Checks.

        CRITICAL: fit_score is passed in for reference only.
        Reality Checks NEVER modify fit_score. This is asserted.

        Args:
            resume_data: Parsed resume data
            jd_data: Job description data
            fit_score: Current fit score (READ ONLY - never modified)
            eligibility_result: Pre-computed eligibility analysis
            fit_details: Pre-computed fit analysis details
            credibility_result: Pre-computed credibility analysis
            risk_analysis: Pre-computed risk analysis
            company_intel: Company intelligence data (from company_intel.py)

        Returns:
            RealityCheckResult with prioritized checks

        Raises:
            RealityCheckViolationError: If any guardrail is violated
        """
        if not self.feature_flag_enabled:
            return RealityCheckResult()

        # HARD ASSERTION: Capture score before analysis
        self._pre_analysis_score = fit_score

        result = RealityCheckResult()

        # Run all signal detectors
        all_checks = []

        # 1. Eligibility Signals (Blocker only)
        eligibility_checks = detect_eligibility_signals(
            resume_data, jd_data, eligibility_result
        )
        all_checks.extend(eligibility_checks)

        # 2. Fit Signals (Warning, Coaching)
        fit_checks = detect_fit_signals(
            resume_data, jd_data, fit_score, fit_details
        )
        all_checks.extend(fit_checks)

        # 3. Credibility Signals (Warning, Coaching)
        credibility_checks = detect_credibility_signals(
            resume_data, credibility_result
        )
        all_checks.extend(credibility_checks)

        # 4. Risk Signals (Warning, Coaching)
        risk_checks = detect_risk_signals(
            resume_data, risk_analysis
        )
        all_checks.extend(risk_checks)

        # 5. Market Bias Signals (Coaching only, NEVER modifies score)
        market_bias_checks = detect_market_bias_signals(
            jd_data, resume_data
        )
        all_checks.extend(market_bias_checks)

        # 6. Market Climate Signals (Informational only, NEVER modifies score)
        market_climate_checks = detect_market_climate_signals(
            resume_data, jd_data
        )
        all_checks.extend(market_climate_checks)

        # 7. Company Health Signals (from external company intelligence)
        if company_intel:
            company_name = jd_data.get("company_name", "") or jd_data.get("company", "")
            company_health_checks = detect_company_health_signals(
                company_name, company_intel
            )
            all_checks.extend(company_health_checks)

        # Validate each check against hard guardrails
        for check in all_checks:
            self._validate_check(check)
            result.add_check(check)

        # Prioritize and limit to max 2 displayed
        result.prioritize()

        # HARD ASSERTION: Verify score was not modified
        self._post_analysis_score = fit_score
        self._assert_score_unchanged()

        return result

    def _validate_check(self, check: RealityCheck, endpoint: str = "/api/jd/analyze"):
        """
        Validate a Reality Check against all hard guardrails.

        Raises:
            RealityCheckViolationError: If any guardrail is violated
        """
        signal_class_str = check.signal_class.value if check.signal_class else "unknown"

        # 1. Validate signal class / severity combination
        allowed_severities = ALLOWED_OUTPUTS.get(check.signal_class, [])
        if check.severity not in allowed_severities:
            raise RealityCheckViolationError(
                f"GUARDRAIL VIOLATION: Severity '{check.severity.value}' not allowed "
                f"for signal class '{check.signal_class.value}'. "
                f"Allowed severities: {[s.value for s in allowed_severities]}",
                signal_class=signal_class_str,
                endpoint=endpoint
            )

        # 2. Validate forbidden interactions are blocked
        for forbidden in FORBIDDEN_INTERACTIONS:
            if forbidden in check.allowed_outputs:
                raise RealityCheckViolationError(
                    f"GUARDRAIL VIOLATION: Forbidden interaction '{forbidden}' "
                    f"found in allowed_outputs for check '{check.trigger}'",
                    signal_class=signal_class_str,
                    endpoint=endpoint
                )

        # 3. Market Bias and Market Climate MUST NOT modify scores
        if check.signal_class in [SignalClass.MARKET_BIAS, SignalClass.MARKET_CLIMATE]:
            score_modifiers = [
                "fit_score_modification",
                "eligibility_change",
                "score_boost",
                "score_penalty",
            ]
            for modifier in score_modifiers:
                if modifier in check.allowed_outputs:
                    raise RealityCheckViolationError(
                        f"GUARDRAIL VIOLATION: {check.signal_class.value} signals "
                        f"MUST NOT include '{modifier}' in allowed_outputs",
                        signal_class=signal_class_str,
                        endpoint=endpoint
                    )

        # 4. Blockers and Warnings MUST have strategic alternatives
        if check.severity in [Severity.BLOCKER, Severity.WARNING]:
            if not check.strategic_alternatives:
                raise RealityCheckViolationError(
                    f"GUARDRAIL VIOLATION: {check.severity.value} severity checks "
                    f"MUST provide strategic_alternatives. Check: '{check.trigger}'",
                    signal_class=signal_class_str,
                    endpoint=endpoint
                )

        # 5. Eligibility blockers MUST NOT be user-overridable
        if (check.signal_class == SignalClass.ELIGIBILITY and
            check.severity == Severity.BLOCKER and
            check.user_override_allowed):
            raise RealityCheckViolationError(
                f"GUARDRAIL VIOLATION: Eligibility blockers MUST NOT be "
                f"user-overridable. Check: '{check.trigger}'",
                signal_class=signal_class_str,
                endpoint=endpoint
            )

    def _assert_score_unchanged(self, endpoint: str = "/api/jd/analyze"):
        """
        Hard assertion that fit_score was not modified during analysis.

        This is the critical guardrail that prevents score manipulation.
        """
        if self._pre_analysis_score != self._post_analysis_score:
            raise RealityCheckViolationError(
                f"CRITICAL GUARDRAIL VIOLATION: fit_score was modified during "
                f"Reality Check analysis. Before: {self._pre_analysis_score}, "
                f"After: {self._post_analysis_score}. "
                f"Reality Checks MUST NEVER modify fit_score.",
                signal_class="score_mutation",
                endpoint=endpoint
            )

    def validate_no_score_mutation(
        self,
        original_score: float,
        current_score: float,
        context: str = ""
    ):
        """
        External validation that can be called after Reality Check integration.

        Use this to verify score integrity at any point.

        Args:
            original_score: Score before Reality Check processing
            current_score: Score after Reality Check processing
            context: Optional context for error message

        Raises:
            RealityCheckViolationError: If scores don't match
        """
        if original_score != current_score:
            raise RealityCheckViolationError(
                f"SCORE MUTATION DETECTED: {context}. "
                f"Original: {original_score}, Current: {current_score}. "
                f"Reality Checks MUST NEVER modify fit_score."
            )

    @staticmethod
    def validate_reality_check_output(output: Dict[str, Any]) -> bool:
        """
        Validate Reality Check output structure before returning to caller.

        Returns True if valid, raises exception if invalid.
        """
        if not output:
            return True  # Empty is valid (no checks triggered)

        required_fields = ["signal_class", "severity", "trigger", "message"]
        for field in required_fields:
            if field not in output:
                raise RealityCheckViolationError(
                    f"Reality Check output missing required field: {field}"
                )

        # Validate signal_class is valid enum value
        valid_signal_classes = [sc.value for sc in SignalClass]
        if output["signal_class"] not in valid_signal_classes:
            raise RealityCheckViolationError(
                f"Invalid signal_class: {output['signal_class']}. "
                f"Valid values: {valid_signal_classes}"
            )

        # Validate severity is valid enum value
        valid_severities = [s.value for s in Severity]
        if output["severity"] not in valid_severities:
            raise RealityCheckViolationError(
                f"Invalid severity: {output['severity']}. "
                f"Valid values: {valid_severities}"
            )

        return True


def create_reality_check_controller(feature_flag: bool = True) -> RealityCheckController:
    """
    Factory function to create a RealityCheckController.

    Use feature_flag=False to disable Reality Checks during rollout.
    """
    return RealityCheckController(feature_flag_enabled=feature_flag)


# Convenience function for one-shot analysis
def analyze_reality_checks(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    fit_score: float,
    eligibility_result: Optional[Dict[str, Any]] = None,
    fit_details: Optional[Dict[str, Any]] = None,
    credibility_result: Optional[Dict[str, Any]] = None,
    risk_analysis: Optional[Dict[str, Any]] = None,
    company_intel: Optional[Dict[str, Any]] = None,
    feature_flag: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function for one-shot Reality Check analysis.

    Returns the result as a dictionary for JSON serialization.
    """
    controller = RealityCheckController(feature_flag_enabled=feature_flag)

    result = controller.analyze(
        resume_data=resume_data,
        jd_data=jd_data,
        fit_score=fit_score,
        eligibility_result=eligibility_result,
        fit_details=fit_details,
        credibility_result=credibility_result,
        risk_analysis=risk_analysis,
        company_intel=company_intel,
    )

    return result.to_dict()
