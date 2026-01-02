"""
Terminal State Contract

Single source of truth for decision authority. Once a terminal state fires,
all downstream behavior is determined by this contract.

DECISION AUTHORITY ORDER (highest to lowest):
1. CREDIBILITY VIOLATIONS - Title inflation, experience fabrication, metrics fabrication
2. ELIGIBILITY VIOLATIONS - Missing required credentials, explicit disqualifiers
3. FUNCTION MISMATCH - Wrong function for target role
4. EXPERIENCE GAPS - Zero years in target function, 2+ levels below target
5. PRESENTATION GAPS - Missing signals that likely exist
6. OPTIMIZATION COACHING - Resume is competitive, can be stronger

Rule: Once a higher-authority condition fires, no lower-authority condition
can upgrade the recommendation, enable the Apply button, or generate optimistic messaging.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re


class TerminalStateType(str, Enum):
    """Terminal state types in authority order (1 = highest)."""
    TITLE_INFLATION = "TITLE_INFLATION"
    CREDIBILITY_VIOLATION = "CREDIBILITY_VIOLATION"
    ELIGIBILITY_VIOLATION = "ELIGIBILITY_VIOLATION"
    FUNCTION_MISMATCH = "FUNCTION_MISMATCH"
    MISSING_CORE_SIGNAL = "MISSING_CORE_SIGNAL"
    EXPERIENCE_GAP = "EXPERIENCE_GAP"
    PRESENTATION_GAP = "PRESENTATION_GAP"
    NONE = "NONE"


class CoachingMode(str, Enum):
    """Coaching mode determines downstream messaging."""
    CREDIBILITY_REPAIR = "CREDIBILITY_REPAIR"
    REDIRECTION = "REDIRECTION"
    SIGNAL_BUILDING = "SIGNAL_BUILDING"
    OPTIMIZATION = "OPTIMIZATION"


class ApplyButtonState(str, Enum):
    """Apply button state."""
    DISABLED = "DISABLED"
    DEMOTED = "DEMOTED"
    ENABLED_WITH_WARNING = "ENABLED_WITH_WARNING"
    ENABLED = "ENABLED"


# Authority order - lower number = higher authority
AUTHORITY_ORDER = {
    TerminalStateType.TITLE_INFLATION: 1,
    TerminalStateType.CREDIBILITY_VIOLATION: 1,
    TerminalStateType.ELIGIBILITY_VIOLATION: 2,
    TerminalStateType.FUNCTION_MISMATCH: 3,
    TerminalStateType.MISSING_CORE_SIGNAL: 4,
    TerminalStateType.EXPERIENCE_GAP: 5,
    TerminalStateType.PRESENTATION_GAP: 6,
    TerminalStateType.NONE: 99,
}


@dataclass
class TerminalStateContract:
    """
    Contract that determines all downstream behavior once a terminal state fires.

    This is the SINGLE SOURCE OF TRUTH for:
    - Fit score caps
    - Recommendation locks
    - Apply button state
    - Coaching mode
    - Forbidden and required messaging
    """
    state_type: TerminalStateType
    fit_score_cap: int
    recommendation: str
    recommendation_cap: Optional[str]  # Maximum allowed recommendation
    apply_button: ApplyButtonState
    coaching_mode: CoachingMode
    forbidden_messaging: List[str]
    required_messaging: List[str]
    reason: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_type": self.state_type.value,
            "fit_score_cap": self.fit_score_cap,
            "recommendation": self.recommendation,
            "recommendation_cap": self.recommendation_cap,
            "apply_button": self.apply_button.value,
            "coaching_mode": self.coaching_mode.value,
            "forbidden_messaging": self.forbidden_messaging,
            "required_messaging": self.required_messaging,
            "reason": self.reason,
            "evidence": self.evidence,
        }


# =============================================================================
# TERMINAL STATE DEFINITIONS
# =============================================================================

TERMINAL_STATES = {
    TerminalStateType.TITLE_INFLATION: TerminalStateContract(
        state_type=TerminalStateType.TITLE_INFLATION,
        fit_score_cap=20,
        recommendation="Do Not Apply",
        recommendation_cap="Do Not Apply",
        apply_button=ApplyButtonState.DISABLED,
        coaching_mode=CoachingMode.CREDIBILITY_REPAIR,
        forbidden_messaging=[
            "you're actually senior",
            "you likely have this",
            "presentation gap",
            "make it visible on your resume",
            "supports senior",
            "supports director",
            "you have the foundation",
            "you're close",
            "stretch role with addressable gaps",
        ],
        required_messaging=[
            "title not supported by evidence",
            "credibility risk",
        ],
        reason="Title claims level not supported by evidence in resume"
    ),

    TerminalStateType.CREDIBILITY_VIOLATION: TerminalStateContract(
        state_type=TerminalStateType.CREDIBILITY_VIOLATION,
        fit_score_cap=15,
        recommendation="Do Not Apply",
        recommendation_cap="Do Not Apply",
        apply_button=ApplyButtonState.DISABLED,
        coaching_mode=CoachingMode.CREDIBILITY_REPAIR,
        forbidden_messaging=[
            "strong foundation",
            "competitive candidate",
            "well-positioned",
        ],
        required_messaging=[
            "credibility concerns",
        ],
        reason="Resume contains credibility violations"
    ),

    TerminalStateType.ELIGIBILITY_VIOLATION: TerminalStateContract(
        state_type=TerminalStateType.ELIGIBILITY_VIOLATION,
        fit_score_cap=20,
        recommendation="Do Not Apply",
        recommendation_cap="Do Not Apply",
        apply_button=ApplyButtonState.DISABLED,
        coaching_mode=CoachingMode.REDIRECTION,
        forbidden_messaging=[
            "apply fast",
            "strong candidate",
            "well-matched",
        ],
        required_messaging=[
            "does not meet eligibility requirements",
        ],
        reason="Does not meet eligibility requirements"
    ),

    TerminalStateType.FUNCTION_MISMATCH: TerminalStateContract(
        state_type=TerminalStateType.FUNCTION_MISMATCH,
        fit_score_cap=25,
        recommendation="Do Not Apply",
        recommendation_cap="Long Shot",
        apply_button=ApplyButtonState.DEMOTED,
        coaching_mode=CoachingMode.REDIRECTION,
        forbidden_messaging=[
            "supports [target role]",
            "you have the foundation",
            "strong match",
            "well-suited",
            "competitive for this role",
        ],
        required_messaging=[
            "function mismatch",
            "different career path",
        ],
        reason="Experience is in different function than target role"
    ),

    TerminalStateType.MISSING_CORE_SIGNAL: TerminalStateContract(
        state_type=TerminalStateType.MISSING_CORE_SIGNAL,
        fit_score_cap=50,
        recommendation="Apply with Caution",
        recommendation_cap="Apply with Caution",
        apply_button=ApplyButtonState.ENABLED_WITH_WARNING,
        coaching_mode=CoachingMode.SIGNAL_BUILDING,
        forbidden_messaging=[
            "strong candidate",
            "highly competitive",
        ],
        required_messaging=[
            "missing core signal",
            "address before applying",
        ],
        reason="Missing scope, impact, or ownership signals"
    ),

    TerminalStateType.EXPERIENCE_GAP: TerminalStateContract(
        state_type=TerminalStateType.EXPERIENCE_GAP,
        fit_score_cap=45,
        recommendation="Long Shot",
        recommendation_cap="Apply with Caution",
        apply_button=ApplyButtonState.DEMOTED,
        coaching_mode=CoachingMode.REDIRECTION,
        forbidden_messaging=[
            "strong fit",
            "ideal candidate",
        ],
        required_messaging=[
            "experience gap",
            "below target level",
        ],
        reason="Experience level significantly below target"
    ),

    TerminalStateType.PRESENTATION_GAP: TerminalStateContract(
        state_type=TerminalStateType.PRESENTATION_GAP,
        fit_score_cap=70,
        recommendation="Consider",
        recommendation_cap="Apply",
        apply_button=ApplyButtonState.ENABLED_WITH_WARNING,
        coaching_mode=CoachingMode.OPTIMIZATION,
        forbidden_messaging=[],
        required_messaging=[],
        reason="Resume presentation does not reflect actual experience level"
    ),
}


# =============================================================================
# SIGNAL DETECTION
# =============================================================================

def has_scope_signal(text: str) -> bool:
    """
    Detect REAL scope signals - quantified scale metrics only.

    Activity nouns alone do NOT count as scope.
    Titles alone do NOT count as scope.

    Must have at least ONE of:
    - Quantified scale metric (team size, budget, user volume, revenue, geography)
    - Clear ownership of a bounded system with complexity markers
    """
    if not text:
        return False

    scope_patterns = [
        # Team size - must be numeric
        r'\b(\d+)[\-\s]*(person|people|engineer|member|report|team|direct)',
        # Budget/revenue - must have dollar amount
        r'\$[\d,\.]+\s*[MBK]?(?:\s|$|\b)',
        r'\b[\d,\.]+\s*[MBK]\s*(budget|revenue|ARR|GMV|pipeline)',
        # User scale - must be numeric
        r'\b\d+[MKB]?\+?\s*(users|customers|MAU|DAU|accounts|subscribers)',
        # Geographic scale - quantified
        r'\b\d+\s*(countries|markets|regions|offices|locations)',
        # Requests/transactions scale
        r'\b\d+[MKB]?\+?\s*(requests|transactions|orders|calls)',
    ]

    for pattern in scope_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def has_impact_signal(text: str) -> bool:
    """
    Detect impact signals - metric + consequence, not just activity.

    Must have BOTH:
    - A quantifiable metric (%, $, x improvement)
    - A business consequence (what it meant)
    """
    if not text:
        return False

    # Check for metric
    has_metric = bool(re.search(r'\d+%|\$[\d,\.]+|[\d\.]+x|\d+[MKB]', text))

    # Check for consequence language
    consequence_patterns = [
        r'\bresulting\b', r'\bsaving\b', r'\bdriving\b', r'\benabling\b',
        r'\breducing\b', r'\bincreasing\b', r'\bgenerating\b', r'\bdelivering\b',
        r'\bachieving\b', r'\bgrew\b', r'\breduced\b', r'\bincreased\b',
        r'\bimproved\b', r'\baccelerated\b', r'\bwhich led to\b', r'\bleading to\b',
    ]
    has_consequence = any(re.search(p, text, re.IGNORECASE) for p in consequence_patterns)

    return has_metric and has_consequence


def has_ownership_signal(text: str) -> bool:
    """
    Detect ownership signals - decision-maker language, not contributor language.
    """
    if not text:
        return False

    text_lower = text.lower()

    ownership_patterns = [
        r'\bowned\b', r'\bled\b', r'\bdefined\b', r'\bbuilt\b', r'\bshipped\b',
        r'\blaunched\b', r'\barchitected\b', r'\bdesigned\b', r'\bestablished\b',
        r'\bcreated\b', r'\bdrove\b', r'\bspearheaded\b', r'\bpioneered\b',
        r'\bfounded\b', r'\borchestrated\b', r'\bdecided\b', r'\baccountable\b',
    ]

    contributor_patterns = [
        r'\bsupported\b', r'\bhelped\b', r'\bassisted\b', r'\bcontributed\b',
        r'\bparticipated\b', r'\binvolved in\b', r'\bworked on\b',
        r'\bresponsible for\b', r'\bexposed to\b',
    ]

    has_ownership = any(re.search(p, text_lower) for p in ownership_patterns)
    has_contributor = any(re.search(p, text_lower) for p in contributor_patterns)

    return has_ownership and not has_contributor


def detect_keyword_stuffing(resume: dict) -> Tuple[bool, int, List[str]]:
    """
    Detect keyword stuffing in resume.

    Returns: (is_stuffed, keyword_density_pct, uncontextualized_keywords)
    """
    bullets = []
    for role in resume.get("experience", []):
        bullets.extend(role.get("bullets", []))

    if not bullets:
        return False, 0, []

    # Common technical keywords to check
    tech_keywords = [
        "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
        "python", "java", "javascript", "typescript", "react", "node",
        "aws", "azure", "gcp", "cloud", "kubernetes", "docker",
        "agile", "scrum", "jira", "confluence",
        "sql", "nosql", "mongodb", "postgresql", "mysql",
        "tensorflow", "pytorch", "keras", "scikit-learn",
        "data analysis", "data science", "analytics",
    ]

    total_bullets = len(bullets)
    all_text = " ".join(bullets).lower()

    # Count keyword occurrences
    keyword_count = 0
    uncontextualized = []

    for kw in tech_keywords:
        occurrences = len(re.findall(rf'\b{re.escape(kw)}\b', all_text))
        if occurrences > 0:
            keyword_count += occurrences

            # Check if keyword has applied context (project/outcome)
            has_context = False
            for bullet in bullets:
                if kw in bullet.lower():
                    # Check for context patterns
                    context_patterns = [
                        r'\bto\b', r'\bfor\b', r'\bresulting\b', r'\bwhich\b',
                        r'\bthat\b', r'\busing\b', r'\bwith\b', r'\bbuilt\b',
                        r'\bcreated\b', r'\bdeveloped\b',
                    ]
                    if any(re.search(p, bullet.lower()) for p in context_patterns):
                        has_context = True
                        break

            if not has_context and occurrences > 2:
                uncontextualized.append(kw)

    # Calculate density
    density = (keyword_count / (total_bullets * 10)) * 100 if total_bullets > 0 else 0

    # Keyword stuffing detected if:
    # - Density > 40% OR
    # - More than 5 uncontextualized keywords
    is_stuffed = density > 40 or len(uncontextualized) > 5

    return is_stuffed, int(density), uncontextualized


def detect_title_inflation_from_evidence(
    title: str,
    bullets: List[str]
) -> Tuple[bool, str, List[str]]:
    """
    Detect if title is inflated relative to bullet evidence.

    Returns: (is_inflated, expected_level, evidence)
    """
    if not bullets:
        return False, "", ["No bullets to assess"]

    title_lower = title.lower()

    # Senior/leadership titles that require evidence
    senior_titles = [
        "head of", "director", "vp", "vice president", "chief",
        "principal", "staff", "senior director", "svp", "evp",
    ]

    is_senior_title = any(t in title_lower for t in senior_titles)

    if not is_senior_title:
        return False, title, []

    # Check for evidence of senior work in bullets
    evidence_found = []

    # Check for scope evidence
    has_scope = False
    for bullet in bullets:
        if has_scope_signal(bullet):
            has_scope = True
            evidence_found.append(f"Scope: {bullet[:50]}...")
            break

    # Check for leadership evidence
    leadership_patterns = [
        r'\bmanaged\s+\d+', r'\bled\s+(team|org)', r'\bhired\b',
        r'\bbuilt\s+team\b', r'\bdirect reports\b', r'\bmentored\b',
    ]
    has_leadership = False
    for bullet in bullets:
        for pattern in leadership_patterns:
            if re.search(pattern, bullet, re.IGNORECASE):
                has_leadership = True
                evidence_found.append(f"Leadership: {bullet[:50]}...")
                break
        if has_leadership:
            break

    # Check for strategic evidence (for Director+)
    strategic_patterns = [
        r'\bstrategy\b', r'\bstrategic\b', r'\broadmap\b', r'\bvision\b',
        r'\bp&l\b', r'\bbudget.*\$', r'\bcompany-wide\b', r'\borg-wide\b',
    ]
    has_strategic = False
    for bullet in bullets:
        for pattern in strategic_patterns:
            if re.search(pattern, bullet, re.IGNORECASE):
                has_strategic = True
                evidence_found.append(f"Strategic: {bullet[:50]}...")
                break
        if has_strategic:
            break

    # Determine inflation
    # Director+ needs scope + leadership + strategic
    is_director_plus = any(t in title_lower for t in ["director", "vp", "vice president", "chief", "head of"])

    if is_director_plus:
        signals_present = sum([has_scope, has_leadership, has_strategic])
        if signals_present < 2:
            return True, "Senior IC or Manager", evidence_found

    # Senior/Staff needs scope + ownership
    if not has_scope and not has_leadership:
        return True, "Mid-level IC", evidence_found

    return False, title, evidence_found


def detect_mid_market_language(text: str) -> List[str]:
    """
    Detect mid-market/generic phrases that weaken positioning.

    Returns list of detected phrases.
    """
    mid_market_phrases = [
        "results-driven",
        "results-oriented",
        "proven track record",
        "self-starter",
        "team player",
        "excellent communication skills",
        "strong communication skills",
        "detail-oriented",
        "attention to detail",
        "fast-paced environment",
        "dynamic environment",
        "passionate about",
        "excited to",
        "thrilled to",
        "synergies",
        "leverage",
        "best practices",
        "cross-functional teams",
        "stakeholders at all levels",
        "managed multiple projects",
        "exceeded expectations",
        "strong analytical skills",
        "problem-solving skills",
        "interpersonal skills",
        "demonstrated ability",
        "proven ability",
        "willingness to learn",
        "eager to learn",
        "quick learner",
        "go-getter",
        "think outside the box",
        "hit the ground running",
        "wear many hats",
        "strategic thinker",
        "thought leader",
        "industry expert",
        "seasoned professional",
        "accomplished professional",
    ]

    text_lower = text.lower()
    found = []

    for phrase in mid_market_phrases:
        if phrase in text_lower:
            found.append(phrase)

    return found


# =============================================================================
# TERMINAL STATE DETECTION
# =============================================================================

def detect_terminal_state(
    resume: dict,
    fit_score: int,
    detected_level: str,
    target_level: str,
    function_match: bool,
    eligibility_passed: bool,
    eligibility_reason: str = ""
) -> TerminalStateContract:
    """
    Detect the highest-authority terminal state that applies.

    Returns the contract that governs all downstream behavior.
    """
    bullets = []
    for role in resume.get("experience", []):
        bullets.extend(role.get("bullets", []))

    all_text = " ".join(bullets) + " " + resume.get("summary", "")

    # 1. Check title inflation (highest authority for credibility violations)
    for role in resume.get("experience", []):
        title = role.get("title", "")
        role_bullets = role.get("bullets", [])

        is_inflated, expected, evidence = detect_title_inflation_from_evidence(title, role_bullets)

        if is_inflated:
            contract = TERMINAL_STATES[TerminalStateType.TITLE_INFLATION]
            contract.evidence = evidence
            contract.reason = f"Title '{title}' not supported by evidence. Evidence suggests {expected}."
            return contract

    # 2. Check eligibility violations
    if not eligibility_passed:
        contract = TERMINAL_STATES[TerminalStateType.ELIGIBILITY_VIOLATION]
        contract.reason = eligibility_reason or "Does not meet eligibility requirements"
        return contract

    # 3. Check function mismatch
    if not function_match:
        contract = TERMINAL_STATES[TerminalStateType.FUNCTION_MISMATCH]
        return contract

    # 4. Check missing core signals (scope, impact, ownership)
    scope_present = any(has_scope_signal(b) for b in bullets)
    impact_present = any(has_impact_signal(b) for b in bullets)
    ownership_present = any(has_ownership_signal(b) for b in bullets)

    missing_signals = []
    if not scope_present:
        missing_signals.append("scope")
    if not impact_present:
        missing_signals.append("impact")
    if not ownership_present:
        missing_signals.append("ownership")

    # For senior roles, missing signals is a blocker
    senior_levels = ["senior", "staff", "principal", "director", "vp", "head", "chief"]
    is_senior_target = any(level in target_level.lower() for level in senior_levels)

    if is_senior_target and missing_signals:
        contract = TERMINAL_STATES[TerminalStateType.MISSING_CORE_SIGNAL]
        contract.reason = f"Missing core signals for senior role: {', '.join(missing_signals)}"
        contract.evidence = missing_signals
        return contract

    # 5. Check experience gap (2+ levels below target)
    level_hierarchy = {
        "entry": 1, "junior": 1, "associate": 2,
        "mid": 3, "": 3,
        "senior": 4, "lead": 5, "staff": 5,
        "principal": 6, "director": 6,
        "senior director": 7, "vp": 8, "svp": 9, "evp": 10, "chief": 11
    }

    detected_num = 3  # default mid
    target_num = 3

    for level, num in level_hierarchy.items():
        if level and level in detected_level.lower():
            detected_num = max(detected_num, num)
        if level and level in target_level.lower():
            target_num = max(target_num, num)

    level_gap = target_num - detected_num

    if level_gap >= 2:
        contract = TERMINAL_STATES[TerminalStateType.EXPERIENCE_GAP]
        contract.reason = f"Experience level ({detected_level}) is {level_gap} levels below target ({target_level})"
        return contract

    # 6. Check for presentation gaps (keyword stuffing, generic language)
    is_stuffed, density, uncontextualized = detect_keyword_stuffing(resume)
    mid_market = detect_mid_market_language(all_text)

    if is_stuffed or len(mid_market) > 5:
        contract = TERMINAL_STATES[TerminalStateType.PRESENTATION_GAP]
        issues = []
        if is_stuffed:
            issues.append(f"keyword stuffing ({density}% density)")
        if mid_market:
            issues.append(f"{len(mid_market)} generic phrases")
        contract.reason = f"Presentation issues: {', '.join(issues)}"
        contract.evidence = mid_market[:10] if mid_market else []
        return contract

    # No terminal state - normal flow
    return TerminalStateContract(
        state_type=TerminalStateType.NONE,
        fit_score_cap=100,
        recommendation="",
        recommendation_cap=None,
        apply_button=ApplyButtonState.ENABLED,
        coaching_mode=CoachingMode.OPTIMIZATION,
        forbidden_messaging=[],
        required_messaging=[],
        reason=""
    )


def apply_terminal_state_contract(
    response_data: dict,
    contract: TerminalStateContract
) -> dict:
    """
    Apply terminal state contract to response data.

    This enforces all constraints from the contract:
    - Caps fit score
    - Locks recommendation
    - Sets apply button state
    - Adds forbidden/required messaging validation
    """
    if contract.state_type == TerminalStateType.NONE:
        return response_data

    # 1. Apply fit score cap
    current_score = response_data.get("fit_score", 50)
    if current_score > contract.fit_score_cap:
        response_data["fit_score"] = contract.fit_score_cap
        response_data["fit_score_capped_by"] = contract.state_type.value
        response_data["fit_score_cap_reason"] = contract.reason

    # 2. Lock recommendation
    response_data["recommendation"] = contract.recommendation
    response_data["recommendation_locked"] = True
    response_data["recommendation_locked_by"] = contract.state_type.value

    # 3. Set apply button state
    response_data["apply_button_state"] = contract.apply_button.value

    # 4. Set coaching mode
    response_data["coaching_mode"] = contract.coaching_mode.value

    # 5. Add terminal state to response
    response_data["terminal_state"] = contract.to_dict()

    # 6. Add blocker notice
    if contract.apply_button in [ApplyButtonState.DISABLED, ApplyButtonState.DEMOTED]:
        response_data["blocker_notice"] = {
            "type": contract.state_type.value,
            "message": contract.reason,
            "coaching_mode": contract.coaching_mode.value,
        }

    return response_data


def validate_messaging(text: str, contract: TerminalStateContract) -> List[str]:
    """
    Validate messaging against terminal state contract.

    Returns list of violations found.
    """
    violations = []
    text_lower = text.lower()

    for forbidden in contract.forbidden_messaging:
        if forbidden.lower() in text_lower:
            violations.append(f"Forbidden phrase found: '{forbidden}'")

    # Check required messaging (at least one should be present)
    if contract.required_messaging:
        has_required = any(req.lower() in text_lower for req in contract.required_messaging)
        if not has_required:
            violations.append(f"Missing required messaging. Expected one of: {contract.required_messaging}")

    return violations


# =============================================================================
# COACHING MODE ENFORCEMENT - HARD ASSERTION
# =============================================================================

# Allowed copy patterns per coaching mode
COACHING_MODE_ALLOWED_COPY = {
    CoachingMode.CREDIBILITY_REPAIR: {
        "allowed": [
            "credibility", "evidence", "support", "verify", "address",
            "concern", "mismatch", "title", "claims", "demonstrates",
        ],
        "forbidden": [
            "strong fit", "competitive", "well-positioned", "apply now",
            "great match", "you have the foundation", "you're close",
            "i've done the heavy lifting", "ready to apply",
        ],
    },
    CoachingMode.REDIRECTION: {
        "allowed": [
            "not a fit", "different path", "consider", "alternative",
            "redirect", "mismatch", "gap", "experience", "function",
        ],
        "forbidden": [
            "apply", "strong candidate", "well-matched", "competitive",
            "you have the foundation", "supports senior", "supports director",
            "i've done the heavy lifting", "ready to submit",
        ],
    },
    CoachingMode.SIGNAL_BUILDING: {
        "allowed": [
            "gap", "signal", "strengthen", "add", "quantify", "scope",
            "impact", "ownership", "address", "before applying",
        ],
        "forbidden": [
            "strong fit", "highly competitive", "top candidate",
            "i've done the heavy lifting",
        ],
    },
    CoachingMode.OPTIMIZATION: {
        "allowed": [
            "apply", "submit", "ready", "competitive", "strong",
            "tailored", "personalize", "review",
        ],
        "forbidden": [],  # Optimization mode allows all positive framing
    },
}


class MessagingViolationError(Exception):
    """Raised when downstream copy violates coaching mode contract."""
    pass


def assert_coaching_mode_compliance(
    text: str,
    coaching_mode: CoachingMode,
    raise_on_violation: bool = True
) -> Tuple[bool, List[str]]:
    """
    HARD ASSERTION: No downstream copy renders outside allowed coaching_mode.

    This is not advisory. This is enforcement. Zero exceptions.

    Args:
        text: The copy/messaging text to validate
        coaching_mode: The active coaching mode from terminal state
        raise_on_violation: If True, raises MessagingViolationError on violation

    Returns:
        Tuple of (is_compliant, list of violations)

    Raises:
        MessagingViolationError: If raise_on_violation=True and violations found
    """
    if not text or coaching_mode == CoachingMode.OPTIMIZATION:
        return True, []

    mode_rules = COACHING_MODE_ALLOWED_COPY.get(coaching_mode, {})
    forbidden = mode_rules.get("forbidden", [])

    text_lower = text.lower()
    violations = []

    for phrase in forbidden:
        if phrase.lower() in text_lower:
            violations.append(f"[{coaching_mode.value}] Forbidden: '{phrase}'")

    is_compliant = len(violations) == 0

    if not is_compliant and raise_on_violation:
        raise MessagingViolationError(
            f"Coaching mode {coaching_mode.value} violated. "
            f"Found {len(violations)} forbidden phrases: {violations}"
        )

    return is_compliant, violations


def enforce_messaging_contract(response_data: dict) -> dict:
    """
    Enforce messaging contract on entire response.

    Scans all text fields and validates against coaching mode.
    Logs violations but does not block (for observability).

    Returns response_data with violations logged.
    """
    coaching_mode_str = response_data.get("coaching_mode", "OPTIMIZATION")
    try:
        coaching_mode = CoachingMode(coaching_mode_str)
    except ValueError:
        coaching_mode = CoachingMode.OPTIMIZATION

    if coaching_mode == CoachingMode.OPTIMIZATION:
        return response_data

    # Fields to scan for messaging compliance
    text_fields = [
        ("recommendation_text", response_data.get("recommendation_text", "")),
        ("rationale", response_data.get("rationale", "")),
        ("strategic_action", response_data.get("reality_check", {}).get("strategic_action", "")),
        ("brutal_truth", response_data.get("reality_check", {}).get("brutal_truth", "")),
        ("why_still_viable", response_data.get("reality_check", {}).get("why_still_viable", "")),
    ]

    all_violations = []

    for field_name, text in text_fields:
        if text:
            is_compliant, violations = assert_coaching_mode_compliance(
                text, coaching_mode, raise_on_violation=False
            )
            if violations:
                all_violations.extend([f"{field_name}: {v}" for v in violations])

    if all_violations:
        response_data["_messaging_violations"] = all_violations
        print(f"⚠️ MESSAGING CONTRACT VIOLATIONS ({len(all_violations)}):")
        for v in all_violations:
            print(f"   - {v}")

    return response_data


# =============================================================================
# DECISION AUTHORITY CHAIN LOGGING
# =============================================================================

@dataclass
class DecisionAuthorityEntry:
    """Single entry in the decision authority chain."""
    check_name: str
    triggered: bool
    authority_level: int
    result: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "check": self.check_name,
            "triggered": self.triggered,
            "authority": self.authority_level,
            "result": self.result,
            "evidence": self.evidence,
        }


def log_decision_authority_chain(
    resume: dict,
    fit_score: int,
    detected_level: str,
    target_level: str,
    function_match: bool,
    eligibility_passed: bool,
    eligibility_reason: str,
    final_state: TerminalStateContract,
    analysis_id: str = ""
) -> Dict[str, Any]:
    """
    Log the complete decision authority chain for audit.

    This produces a full trace of WHY a terminal state won,
    showing every check that was evaluated and its result.

    Returns dict with full authority chain for logging.
    """
    chain = []

    # 1. Title Inflation Check (Authority 1)
    title_inflation_triggered = False
    title_evidence = []
    for role in resume.get("experience", []):
        title = role.get("title", "")
        bullets = role.get("bullets", [])
        is_inflated, expected, evidence = detect_title_inflation_from_evidence(title, bullets)
        if is_inflated:
            title_inflation_triggered = True
            title_evidence = [f"Title: {title}", f"Expected: {expected}"] + evidence
            break

    chain.append(DecisionAuthorityEntry(
        check_name="TITLE_INFLATION",
        triggered=title_inflation_triggered,
        authority_level=1,
        result="BLOCKED" if title_inflation_triggered else "PASSED",
        evidence=title_evidence
    ))

    # 2. Eligibility Check (Authority 2)
    chain.append(DecisionAuthorityEntry(
        check_name="ELIGIBILITY",
        triggered=not eligibility_passed,
        authority_level=2,
        result="BLOCKED" if not eligibility_passed else "PASSED",
        evidence=[eligibility_reason] if eligibility_reason else []
    ))

    # 3. Function Mismatch Check (Authority 3)
    chain.append(DecisionAuthorityEntry(
        check_name="FUNCTION_MISMATCH",
        triggered=not function_match,
        authority_level=3,
        result="BLOCKED" if not function_match else "PASSED",
        evidence=["Function mismatch detected"] if not function_match else []
    ))

    # 4. Missing Core Signals Check (Authority 4)
    bullets = []
    for role in resume.get("experience", []):
        bullets.extend(role.get("bullets", []))

    scope_present = any(has_scope_signal(b) for b in bullets)
    impact_present = any(has_impact_signal(b) for b in bullets)
    ownership_present = any(has_ownership_signal(b) for b in bullets)

    missing_signals = []
    if not scope_present:
        missing_signals.append("scope")
    if not impact_present:
        missing_signals.append("impact")
    if not ownership_present:
        missing_signals.append("ownership")

    senior_levels = ["senior", "staff", "principal", "director", "vp", "head", "chief"]
    is_senior_target = any(level in target_level.lower() for level in senior_levels)
    signals_triggered = is_senior_target and len(missing_signals) > 0

    chain.append(DecisionAuthorityEntry(
        check_name="MISSING_CORE_SIGNAL",
        triggered=signals_triggered,
        authority_level=4,
        result="BLOCKED" if signals_triggered else "PASSED",
        evidence=[f"Missing: {', '.join(missing_signals)}"] if missing_signals else ["All signals present"]
    ))

    # 5. Experience Gap Check (Authority 5)
    level_hierarchy = {
        "entry": 1, "junior": 1, "associate": 2, "mid": 3, "": 3,
        "senior": 4, "lead": 5, "staff": 5, "principal": 6, "director": 6,
        "senior director": 7, "vp": 8, "svp": 9, "evp": 10, "chief": 11
    }

    detected_num = 3
    target_num = 3
    for level, num in level_hierarchy.items():
        if level and level in detected_level.lower():
            detected_num = max(detected_num, num)
        if level and level in target_level.lower():
            target_num = max(target_num, num)

    level_gap = target_num - detected_num
    gap_triggered = level_gap >= 2

    chain.append(DecisionAuthorityEntry(
        check_name="EXPERIENCE_GAP",
        triggered=gap_triggered,
        authority_level=5,
        result="BLOCKED" if gap_triggered else "PASSED",
        evidence=[f"Level gap: {level_gap} (detected: {detected_level}, target: {target_level})"]
    ))

    # 6. Presentation Gap Check (Authority 6)
    all_text = " ".join(bullets) + " " + resume.get("summary", "")
    is_stuffed, density, uncontextualized = detect_keyword_stuffing(resume)
    mid_market = detect_mid_market_language(all_text)
    presentation_triggered = is_stuffed or len(mid_market) > 5

    chain.append(DecisionAuthorityEntry(
        check_name="PRESENTATION_GAP",
        triggered=presentation_triggered,
        authority_level=6,
        result="WARNING" if presentation_triggered else "PASSED",
        evidence=[f"Keyword density: {density}%", f"Mid-market phrases: {len(mid_market)}"]
    ))

    # Determine winning state
    winning_check = None
    for entry in chain:
        if entry.triggered:
            winning_check = entry
            break

    # Build authority chain log
    authority_chain = {
        "analysis_id": analysis_id,
        "checks_evaluated": [e.to_dict() for e in chain],
        "winning_state": final_state.state_type.value,
        "winning_authority": AUTHORITY_ORDER.get(final_state.state_type, 99),
        "winning_check": winning_check.to_dict() if winning_check else None,
        "final_score_cap": final_state.fit_score_cap,
        "final_recommendation": final_state.recommendation,
        "coaching_mode": final_state.coaching_mode.value,
    }

    # Print full authority chain to Railway logs
    print("\n" + "=" * 80)
    print(f"📋 DECISION AUTHORITY CHAIN - Analysis: {analysis_id[:8] if analysis_id else 'N/A'}...")
    print("=" * 80)
    for entry in chain:
        status_icon = "🚫" if entry.triggered else "✅"
        print(f"   [{entry.authority_level}] {entry.check_name}: {status_icon} {entry.result}")
        if entry.evidence and entry.triggered:
            for ev in entry.evidence[:3]:
                print(f"       └─ {ev}")
    print("-" * 80)
    print(f"   🏆 WINNER: {final_state.state_type.value} (Authority {AUTHORITY_ORDER.get(final_state.state_type, 99)})")
    print(f"   📊 Score Cap: {final_state.fit_score_cap}% | Recommendation: {final_state.recommendation}")
    print(f"   🎯 Coaching Mode: {final_state.coaching_mode.value}")
    print("=" * 80 + "\n")

    return authority_chain
