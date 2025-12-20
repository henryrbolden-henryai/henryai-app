"""
Reality Check Data Models

Defines the core data structures for the Reality Check system.
These models enforce the strict boundaries defined in REALITY_CHECK_SPEC.md.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


class SignalClass(str, Enum):
    """
    Six distinct signal classes for Reality Checks.
    Each has strict boundaries and allowed outputs.
    """
    ELIGIBILITY = "eligibility"      # Hard requirements - Blocker only
    FIT = "fit"                       # Experience matching - Warning, Coaching
    CREDIBILITY = "credibility"       # Claim believability - Warning, Coaching
    RISK = "risk"                     # Pattern recognition - Warning, Coaching
    MARKET_BIAS = "market_bias"       # Hiring preferences - Coaching only, NEVER modifies score
    MARKET_CLIMATE = "market_climate" # External conditions - Informational only, NEVER modifies score


class Severity(str, Enum):
    """
    Reality Check severity levels.
    """
    BLOCKER = "blocker"           # Prevents action - Red, clear stop signal
    WARNING = "warning"           # Strong discouragement - Orange/amber
    COACHING = "coaching"         # Strategic guidance - Blue/informational
    INFORMATIONAL = "informational"  # Context only - Neutral gray


# Forbidden interactions - hard guardrails that must NEVER be violated
FORBIDDEN_INTERACTIONS = [
    "fit_score_modification",
    "cec_threshold_alteration",
    "leadership_credit_inflation",
    "internship_experience_counting",
    "hidden_score_boost",
    "hidden_score_penalty",
    "candidate_identity_rewrite",
    "work_experience_suppression",
    "ats_keyword_modification",
    "experience_penalty_adjustment",
    "backend_safety_net_override",
]

# Allowed outputs by signal class
ALLOWED_OUTPUTS = {
    SignalClass.ELIGIBILITY: [Severity.BLOCKER],
    SignalClass.FIT: [Severity.WARNING, Severity.COACHING],
    SignalClass.CREDIBILITY: [Severity.WARNING, Severity.COACHING],
    SignalClass.RISK: [Severity.WARNING, Severity.COACHING],
    SignalClass.MARKET_BIAS: [Severity.COACHING],  # NEVER modifies score
    SignalClass.MARKET_CLIMATE: [Severity.INFORMATIONAL, Severity.COACHING],  # NEVER modifies score
}

# Priority order for multiple signals (1 = highest priority)
SIGNAL_PRIORITY = {
    SignalClass.ELIGIBILITY: 1,
    SignalClass.FIT: 2,
    SignalClass.CREDIBILITY: 3,
    SignalClass.RISK: 4,
    SignalClass.MARKET_BIAS: 5,
    SignalClass.MARKET_CLIMATE: 6,
}


@dataclass
class RealityCheck:
    """
    A single Reality Check result.

    Per REALITY_CHECK_SPEC.md:
    - Must declare signal class
    - Must declare severity
    - Must declare allowed outputs
    - Must declare forbidden outputs
    - Must provide evidence
    - Must offer alternatives (when blocking or warning)
    """
    signal_class: SignalClass
    severity: Severity
    trigger: str  # What triggered this check
    message: str  # User-facing message
    strategic_alternatives: List[str] = field(default_factory=list)
    evidence: Optional[str] = None  # Specific evidence cited
    allowed_outputs: List[str] = field(default_factory=list)
    forbidden_outputs: List[str] = field(default_factory=lambda: FORBIDDEN_INTERACTIONS.copy())
    user_override_allowed: bool = True  # Can user proceed anyway?

    def __post_init__(self):
        """Validate the Reality Check against spec requirements."""
        # Validate signal class and severity combination
        allowed_severities = ALLOWED_OUTPUTS.get(self.signal_class, [])
        if self.severity not in allowed_severities:
            raise ValueError(
                f"Severity '{self.severity}' not allowed for signal class '{self.signal_class}'. "
                f"Allowed: {allowed_severities}"
            )

        # Eligibility blockers cannot be overridden
        if self.signal_class == SignalClass.ELIGIBILITY and self.severity == Severity.BLOCKER:
            self.user_override_allowed = False

        # Market Bias and Market Climate NEVER modify scores
        if self.signal_class in [SignalClass.MARKET_BIAS, SignalClass.MARKET_CLIMATE]:
            # Ensure score modification is in forbidden outputs
            if "fit_score_modification" not in self.forbidden_outputs:
                self.forbidden_outputs.append("fit_score_modification")
            if "eligibility_change" not in self.forbidden_outputs:
                self.forbidden_outputs.append("eligibility_change")

        # Warnings and Blockers must have strategic alternatives
        if self.severity in [Severity.BLOCKER, Severity.WARNING]:
            if not self.strategic_alternatives:
                raise ValueError(
                    f"Reality Checks with severity '{self.severity}' must provide strategic_alternatives"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "signal_class": self.signal_class.value,
            "severity": self.severity.value,
            "trigger": self.trigger,
            "message": self.message,
            "strategic_alternatives": self.strategic_alternatives,
            "evidence": self.evidence,
            "allowed_outputs": self.allowed_outputs,
            "forbidden_outputs": self.forbidden_outputs,
            "user_override_allowed": self.user_override_allowed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealityCheck':
        """Create from dictionary."""
        return cls(
            signal_class=SignalClass(data["signal_class"]),
            severity=Severity(data["severity"]),
            trigger=data["trigger"],
            message=data["message"],
            strategic_alternatives=data.get("strategic_alternatives", []),
            evidence=data.get("evidence"),
            allowed_outputs=data.get("allowed_outputs", []),
            forbidden_outputs=data.get("forbidden_outputs", FORBIDDEN_INTERACTIONS.copy()),
            user_override_allowed=data.get("user_override_allowed", True),
        )


@dataclass
class RealityCheckResult:
    """
    Complete Reality Check analysis result.

    Contains all detected signals, prioritized and limited per spec.
    """
    checks: List[RealityCheck] = field(default_factory=list)
    has_blocker: bool = False
    has_warning: bool = False
    primary_check: Optional[RealityCheck] = None
    secondary_check: Optional[RealityCheck] = None

    def add_check(self, check: RealityCheck):
        """Add a Reality Check to the result."""
        self.checks.append(check)

        if check.severity == Severity.BLOCKER:
            self.has_blocker = True
        elif check.severity == Severity.WARNING:
            self.has_warning = True

    def prioritize(self):
        """
        Prioritize checks per spec:
        - Sort by severity (Blocker > Warning > Coaching > Informational)
        - Then by signal class priority
        - Limit to 2 displayed checks
        - Market Bias/Climate must be paired with Fit/Eligibility/Credibility/Risk
        """
        if not self.checks:
            return

        # Sort by severity first, then by signal class priority
        severity_order = {
            Severity.BLOCKER: 0,
            Severity.WARNING: 1,
            Severity.COACHING: 2,
            Severity.INFORMATIONAL: 3,
        }

        sorted_checks = sorted(
            self.checks,
            key=lambda c: (severity_order[c.severity], SIGNAL_PRIORITY[c.signal_class])
        )

        # Get primary and secondary checks
        displayed = []
        has_capability_signal = False  # Fit, Eligibility, Credibility, or Risk

        for check in sorted_checks:
            if len(displayed) >= 2:
                break

            # Market Bias/Climate must be paired with capability signals
            if check.signal_class in [SignalClass.MARKET_BIAS, SignalClass.MARKET_CLIMATE]:
                if not has_capability_signal and len(displayed) == 0:
                    # Skip for now, we need a capability signal first
                    continue
            else:
                has_capability_signal = True

            displayed.append(check)

        # If we only have Market Bias/Climate signals, still show them but log warning
        if not displayed and sorted_checks:
            displayed = sorted_checks[:2]

        self.primary_check = displayed[0] if len(displayed) > 0 else None
        self.secondary_check = displayed[1] if len(displayed) > 1 else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        self.prioritize()

        return {
            "checks": [c.to_dict() for c in self.checks],
            "has_blocker": self.has_blocker,
            "has_warning": self.has_warning,
            "primary_check": self.primary_check.to_dict() if self.primary_check else None,
            "secondary_check": self.secondary_check.to_dict() if self.secondary_check else None,
            "display_checks": [
                c.to_dict() for c in [self.primary_check, self.secondary_check] if c
            ],
        }
