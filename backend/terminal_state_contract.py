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


# =============================================================================
# CANONICAL CANDIDATE PROFILE (Round 3 Fix)
# Single source of truth - runs ONCE, consumed by ALL downstream modules
# =============================================================================

class FunctionType(str, Enum):
    """P1-NEW-1: Unified PM taxonomy - these are DISTINCT functions."""
    PRODUCT_MANAGEMENT = "PRODUCT_MANAGEMENT"      # Product ownership, roadmap, strategy
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"      # Delivery, timelines, coordination
    PROGRAM_MANAGEMENT = "PROGRAM_MANAGEMENT"      # Cross-functional programs, PMO
    PM_ADJACENT = "PM_ADJACENT"                    # TPM, Scrum Master, BA with PM overlap
    ENGINEERING = "ENGINEERING"
    DESIGN = "DESIGN"
    DATA_SCIENCE = "DATA_SCIENCE"
    MARKETING = "MARKETING"
    SALES = "SALES"
    OPERATIONS = "OPERATIONS"
    RECRUITING = "RECRUITING"                      # Recruiting, talent acquisition, TA
    FINANCE = "FINANCE"                            # Finance, accounting, FP&A
    HR = "HR"                                      # HR (non-recruiting), people ops
    LEGAL = "LEGAL"                                # Legal, compliance
    CUSTOMER_SUCCESS = "CUSTOMER_SUCCESS"          # CS, account management
    OTHER = "OTHER"


class CandidateLevel(str, Enum):
    """Canonical seniority levels."""
    ENTRY = "ENTRY"           # 0-2 years
    ASSOCIATE = "ASSOCIATE"   # 2-4 years
    MID = "MID"               # 4-6 years
    SENIOR = "SENIOR"         # 6-10 years
    STAFF = "STAFF"           # 8-12 years (IC track)
    PRINCIPAL = "PRINCIPAL"   # 10+ years (IC track)
    DIRECTOR = "DIRECTOR"     # 8+ years (management track)
    VP = "VP"                 # 12+ years
    EXECUTIVE = "EXECUTIVE"   # C-level


class SignalStrength(str, Enum):
    """How strong the evidence is for detected function/level."""
    STRONG = "STRONG"       # Multiple clear signals with quantified evidence
    MODERATE = "MODERATE"   # Some signals present, partial evidence
    WEAK = "WEAK"           # Indirect signals, inferred
    NONE = "NONE"           # No signals detected


@dataclass
class CanonicalCandidateProfile:
    """
    P1-NEW-2: Single canonical output consumed by ALL modules.

    This is the ONLY place candidate function and level are determined.
    All downstream modules (Resume Leveling, Fit Analysis, Quick View, etc.)
    MUST consume this - no independent re-evaluation allowed.
    """
    detected_function: FunctionType
    detected_level: CandidateLevel
    signal_strength: SignalStrength

    # Canonical statement - THE source of truth for all copy
    canonical_statement: str

    # Evidence supporting the determination
    function_evidence: List[str] = field(default_factory=list)
    level_evidence: List[str] = field(default_factory=list)

    # Target role comparison
    target_function: Optional[FunctionType] = None
    target_level: Optional[CandidateLevel] = None
    function_match: bool = True
    level_gap: int = 0  # Positive = target higher, negative = candidate higher

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected_function": self.detected_function.value,
            "detected_level": self.detected_level.value,
            "signal_strength": self.signal_strength.value,
            "canonical_statement": self.canonical_statement,
            "function_evidence": self.function_evidence,
            "level_evidence": self.level_evidence,
            "target_function": self.target_function.value if self.target_function else None,
            "target_level": self.target_level.value if self.target_level else None,
            "function_match": self.function_match,
            "level_gap": self.level_gap,
        }


# Product Management signal patterns (DISTINCT from Project Management)
PRODUCT_MANAGEMENT_SIGNALS = [
    r'\b(?:product\s+)?roadmap\b',
    r'\bproduct\s+strategy\b',
    r'\bproduct\s+vision\b',
    r'\bproduct\s+discovery\b',
    r'\bproduct\s+requirements?\b',
    r'\bprd\b',
    r'\buser\s+research\b',
    r'\bcustomer\s+discovery\b',
    r'\bfeature\s+prioritization\b',
    r'\bbacklog\s+(?:management|prioritization|grooming)\b',
    r'\bproduct\s+metrics\b',
    r'\bproduct\s+analytics\b',
    r'\ba/b\s+test(?:ing)?\b',
    r'\bexperimentation\b',
    r'\bproduct[\-\s]led\b',
    r'\bproduct\s+owner\b',
    r'\bproduct\s+manager\b',
    r'\bpm\s+(?:at|for|on)\b',  # "PM at Stripe" pattern
]

# Project Management signal patterns (delivery-focused, NOT product ownership)
PROJECT_MANAGEMENT_SIGNALS = [
    r'\bproject\s+plan(?:ning)?\b',
    r'\bproject\s+timeline\b',
    r'\bgantt\b',
    r'\bproject\s+schedule\b',
    r'\bmilestone\s+tracking\b',
    r'\bdelivery\s+management\b',
    r'\bproject\s+coordination\b',
    r'\bresource\s+allocation\b',
    r'\bpmp\b',
    r'\bprince2\b',
    r'\bwaterfall\b',
    r'\bproject\s+manager\b',
    r'\bproject\s+management\s+(?:office|professional)\b',
]

# PM-Adjacent patterns (has overlap but not core PM)
PM_ADJACENT_SIGNALS = [
    r'\btechnical\s+program\s+manager\b',
    r'\btpm\b',
    r'\bscrum\s+master\b',
    r'\bagile\s+coach\b',
    r'\bbusiness\s+analyst\b',
    r'\brequirements\s+analyst\b',
    r'\bsolutions?\s+architect\b',
]

# Recruiting/Talent Acquisition signal patterns
RECRUITING_SIGNALS = [
    r'\brecruit(?:er|ing|ment)?\b',
    r'\btalent\s+acquis(?:ition|er)\b',
    r'\bta\s+(?:lead|manager|director|head|partner)\b',
    r'\bsourc(?:er|ing)\b',
    r'\bcandidate\s+(?:pipeline|experience|sourcing)\b',
    r'\bhiring\s+(?:manager|partner|team)\b',
    r'\bemployer\s+brand(?:ing)?\b',
    r'\bats\b',  # Applicant tracking system
    r'\bheadcount\s+planning\b',
    r'\brecruiting\s+(?:team|org|strategy|operations)\b',
    r'\btalent\s+(?:pipeline|strategy|operations|partner)\b',
    r'\buniversity\s+recruiting\b',
    r'\bcampus\s+recruiting\b',
    r'\bexecutive\s+search\b',
    r'\bworkday\b',
    r'\bgreenhouse\b',
    r'\blever\b',
    r'\bicims\b',
    r'\blinkedin\s+recruiter\b',
]

# Finance signal patterns
FINANCE_SIGNALS = [
    r'\bfp&a\b',
    r'\bfinancial\s+(?:planning|analysis|analyst|controller)\b',
    r'\baccounting\b',
    r'\bcfo\b',
    r'\bcontroller\b',
    r'\baudit(?:or|ing)?\b',
    r'\bbudget(?:ing)?\b',
    r'\bforecast(?:ing)?\b',
    r'\btreasury\b',
    r'\btax\s+(?:planning|compliance)\b',
    r'\bfinance\s+(?:manager|director|lead)\b',
]

# Customer Success signal patterns
CUSTOMER_SUCCESS_SIGNALS = [
    r'\bcustomer\s+success\b',
    r'\bcsm\b',
    r'\baccount\s+manag(?:er|ement)\b',
    r'\bclient\s+(?:success|management|relations)\b',
    r'\brelationship\s+manag(?:er|ement)\b',
    r'\brenewal(?:s)?\b',
    r'\bretention\b',
    r'\bnrr\b',  # Net revenue retention
    r'\bchurn\b',
    r'\bonboarding\b',
    r'\bcustomer\s+health\b',
]


def detect_function_type(resume_text: str, titles: List[str]) -> Tuple[FunctionType, SignalStrength, List[str]]:
    """
    P1-NEW-1: Detect candidate's PRIMARY function with proper taxonomy.

    Project Manager ≠ Product Manager ≠ PM-Adjacent
    Recruiting ≠ HR ≠ Operations

    Returns: (function_type, signal_strength, evidence_list)
    """
    if not resume_text:
        return FunctionType.OTHER, SignalStrength.NONE, []

    text_lower = resume_text.lower()
    titles_lower = " ".join(titles).lower() if titles else ""
    evidence = []

    # Count signals for each function type
    product_count = sum(1 for p in PRODUCT_MANAGEMENT_SIGNALS if re.search(p, text_lower))
    project_count = sum(1 for p in PROJECT_MANAGEMENT_SIGNALS if re.search(p, text_lower))
    pm_adjacent_count = sum(1 for p in PM_ADJACENT_SIGNALS if re.search(p, text_lower))
    recruiting_count = sum(1 for p in RECRUITING_SIGNALS if re.search(p, text_lower))
    finance_count = sum(1 for p in FINANCE_SIGNALS if re.search(p, text_lower))
    cs_count = sum(1 for p in CUSTOMER_SUCCESS_SIGNALS if re.search(p, text_lower))

    # Check titles for explicit function
    has_product_title = bool(re.search(r'\bproduct\s+(?:manager|management|owner)\b', titles_lower))
    has_project_title = bool(re.search(r'\bproject\s+manager\b', titles_lower))
    has_tpm_title = bool(re.search(r'\b(?:technical\s+program|tpm)\b', titles_lower))
    has_recruiting_title = bool(re.search(r'\b(?:recruit(?:er|ing)|talent\s+acquis(?:ition|er)|ta\s+(?:lead|manager|director|head))\b', titles_lower))
    has_finance_title = bool(re.search(r'\b(?:finance|fp&a|controller|accounting)\b', titles_lower))
    has_cs_title = bool(re.search(r'\b(?:customer\s+success|csm|account\s+manag)\b', titles_lower))

    # Check for recruiting FIRST (before PM checks, since TA roles may have some PM-like language)
    if has_recruiting_title and recruiting_count >= 2:
        evidence.append(f"Recruiting title + {recruiting_count} recruiting signals")
        return FunctionType.RECRUITING, SignalStrength.STRONG, evidence

    if has_recruiting_title or recruiting_count >= 5:
        evidence.append(f"Recruiting signals: {recruiting_count}")
        strength = SignalStrength.STRONG if recruiting_count >= 5 else SignalStrength.MODERATE
        return FunctionType.RECRUITING, strength, evidence

    # Determine primary function - PM types
    if has_product_title and product_count >= 3:
        evidence.append(f"Product Manager title + {product_count} product signals")
        return FunctionType.PRODUCT_MANAGEMENT, SignalStrength.STRONG, evidence

    if has_product_title or product_count >= 5:
        evidence.append(f"Product signals: {product_count}")
        strength = SignalStrength.STRONG if product_count >= 5 else SignalStrength.MODERATE
        return FunctionType.PRODUCT_MANAGEMENT, strength, evidence

    if has_project_title or project_count >= 3:
        evidence.append(f"Project Manager signals: {project_count}")
        strength = SignalStrength.STRONG if project_count >= 5 else SignalStrength.MODERATE
        return FunctionType.PROJECT_MANAGEMENT, strength, evidence

    if has_tpm_title or pm_adjacent_count >= 2:
        evidence.append(f"PM-Adjacent signals: {pm_adjacent_count}")
        return FunctionType.PM_ADJACENT, SignalStrength.MODERATE, evidence

    # Check for product signals without title (weaker)
    if product_count >= 2:
        evidence.append(f"Product signals without PM title: {product_count}")
        return FunctionType.PRODUCT_MANAGEMENT, SignalStrength.WEAK, evidence

    # Check for engineering
    if re.search(r'\b(?:software|backend|frontend|fullstack|engineer|developer|swe)\b', titles_lower):
        return FunctionType.ENGINEERING, SignalStrength.STRONG, ["Engineering title detected"]

    # Check for design
    if re.search(r'\b(?:product\s+)?design(?:er)?\b', titles_lower):
        return FunctionType.DESIGN, SignalStrength.STRONG, ["Design title detected"]

    # Check for finance
    if has_finance_title or finance_count >= 3:
        evidence.append(f"Finance signals: {finance_count}")
        strength = SignalStrength.STRONG if finance_count >= 5 else SignalStrength.MODERATE
        return FunctionType.FINANCE, strength, evidence

    # Check for customer success
    if has_cs_title or cs_count >= 3:
        evidence.append(f"Customer Success signals: {cs_count}")
        strength = SignalStrength.STRONG if cs_count >= 5 else SignalStrength.MODERATE
        return FunctionType.CUSTOMER_SUCCESS, strength, evidence

    # Check for recruiting signals without explicit title (weaker)
    if recruiting_count >= 3:
        evidence.append(f"Recruiting signals without title: {recruiting_count}")
        return FunctionType.RECRUITING, SignalStrength.WEAK, evidence

    return FunctionType.OTHER, SignalStrength.WEAK, ["No clear function signals"]


def detect_candidate_level(resume_text: str, titles: List[str], years_experience: Optional[int] = None) -> Tuple[CandidateLevel, SignalStrength, List[str]]:
    """
    Detect candidate's seniority level based on evidence.

    Returns: (level, signal_strength, evidence_list)
    """
    if not resume_text and not titles:
        return CandidateLevel.MID, SignalStrength.NONE, ["No data to assess"]

    titles_lower = " ".join(titles).lower() if titles else ""
    text_lower = (resume_text or "").lower()
    evidence = []

    # Check for explicit level in titles
    if re.search(r'\b(?:chief|cto|cpo|ceo|coo)\b', titles_lower):
        evidence.append("C-level title")
        return CandidateLevel.EXECUTIVE, SignalStrength.STRONG, evidence

    if re.search(r'\b(?:vp|vice\s+president)\b', titles_lower):
        evidence.append("VP title")
        return CandidateLevel.VP, SignalStrength.STRONG, evidence

    if re.search(r'\b(?:senior\s+)?director\b', titles_lower):
        evidence.append("Director title")
        return CandidateLevel.DIRECTOR, SignalStrength.STRONG, evidence

    if re.search(r'\bprincipal\b', titles_lower):
        evidence.append("Principal title")
        return CandidateLevel.PRINCIPAL, SignalStrength.STRONG, evidence

    if re.search(r'\bstaff\b', titles_lower):
        evidence.append("Staff title")
        return CandidateLevel.STAFF, SignalStrength.STRONG, evidence

    if re.search(r'\bsenior\b', titles_lower):
        evidence.append("Senior title")
        return CandidateLevel.SENIOR, SignalStrength.STRONG, evidence

    if re.search(r'\b(?:associate|junior|jr\.?)\b', titles_lower):
        evidence.append("Associate/Junior title")
        return CandidateLevel.ASSOCIATE, SignalStrength.STRONG, evidence

    # Infer from years if available
    if years_experience is not None:
        if years_experience >= 12:
            evidence.append(f"{years_experience} years experience")
            return CandidateLevel.DIRECTOR, SignalStrength.MODERATE, evidence
        elif years_experience >= 8:
            evidence.append(f"{years_experience} years experience")
            return CandidateLevel.SENIOR, SignalStrength.MODERATE, evidence
        elif years_experience >= 4:
            evidence.append(f"{years_experience} years experience")
            return CandidateLevel.MID, SignalStrength.MODERATE, evidence
        elif years_experience >= 2:
            evidence.append(f"{years_experience} years experience")
            return CandidateLevel.ASSOCIATE, SignalStrength.MODERATE, evidence
        else:
            evidence.append(f"{years_experience} years experience")
            return CandidateLevel.ENTRY, SignalStrength.MODERATE, evidence

    # Default to mid if no signals
    evidence.append("No explicit level signals, defaulting to mid")
    return CandidateLevel.MID, SignalStrength.WEAK, evidence


def generate_canonical_statement(
    function: FunctionType,
    level: CandidateLevel,
    signal_strength: SignalStrength,
    target_function: Optional[FunctionType] = None,
    function_match: bool = True
) -> str:
    """
    P1-NEW-3: Generate the canonical statement that ALL modules must use.

    Replaces harsh "zero PM" language with accurate, professional copy.
    """
    level_name = level.value.replace("_", " ").title()
    function_name = function.value.replace("_", " ").title()

    # Function mismatch cases
    if not function_match and target_function:
        target_name = target_function.value.replace("_", " ").title()

        if function == FunctionType.PROJECT_MANAGEMENT and target_function == FunctionType.PRODUCT_MANAGEMENT:
            return f"Your resume shows {level_name} Project Management experience. This role requires Product Management - a different function focused on product ownership, strategy, and customer discovery rather than delivery coordination."

        if function == FunctionType.PM_ADJACENT and target_function == FunctionType.PRODUCT_MANAGEMENT:
            return f"Your resume shows PM-adjacent experience ({function_name}). While there's overlap with Product Management, this role requires explicit product ownership signals - roadmap authority, customer discovery, and feature prioritization."

        if function == FunctionType.ENGINEERING and target_function == FunctionType.PRODUCT_MANAGEMENT:
            return f"Your resume shows {level_name} Engineering experience. This role requires Product Management experience - product ownership, roadmap authority, and customer-facing discovery work."

        return f"Your resume shows {level_name} {function_name} experience. This role requires {target_name} experience."

    # No product ownership signals detected (replaces "zero PM")
    if function == FunctionType.OTHER and target_function == FunctionType.PRODUCT_MANAGEMENT:
        if signal_strength == SignalStrength.NONE:
            return "No explicit product ownership signals detected in your resume. This role requires demonstrated product management experience - roadmap authority, customer discovery, and feature prioritization."
        else:
            return "Your resume shows project delivery but not product ownership. This role requires demonstrated product ownership - defining what to build and why, not just delivering what others define."

    # No recruiting signals detected
    if function == FunctionType.OTHER and target_function == FunctionType.RECRUITING:
        return "No recruiting or talent acquisition signals detected in your resume. This role requires demonstrated recruiting experience - candidate sourcing, pipeline management, hiring partnerships, and talent strategy."

    # Matched function - specific messages for different functions
    if function == FunctionType.RECRUITING and function_match:
        if signal_strength == SignalStrength.STRONG:
            return f"Your resume demonstrates {level_name} Recruiting/Talent Acquisition experience with strong supporting evidence."
        elif signal_strength == SignalStrength.MODERATE:
            return f"Your resume shows {level_name} Recruiting experience. Some signals could be strengthened with more quantified evidence (hires made, time-to-fill, pipeline metrics)."
        else:
            return f"Your resume suggests {level_name} Recruiting experience, though the signals are indirect. Consider adding explicit recruiting metrics and outcomes."

    # Matched function - general case
    if signal_strength == SignalStrength.STRONG:
        return f"Your resume demonstrates {level_name} {function_name} experience with strong supporting evidence."
    elif signal_strength == SignalStrength.MODERATE:
        return f"Your resume shows {level_name} {function_name} experience. Some signals could be strengthened with more quantified evidence."
    else:
        return f"Your resume suggests {level_name} {function_name} experience, though the signals are indirect. Consider adding explicit examples of {function_name.lower()} work."


def build_canonical_profile(
    resume_data: dict,
    target_role_title: str = "",
    target_role_function: Optional[str] = None
) -> CanonicalCandidateProfile:
    """
    P1-NEW-2: Build the canonical candidate profile - THE single source of truth.

    This function runs ONCE. All downstream modules consume its output.
    No module is allowed to independently re-evaluate function or level.
    """
    # Extract resume text and titles
    titles = []
    bullets_text = ""

    for role in resume_data.get("experience", []):
        if role.get("title"):
            titles.append(role["title"])
        bullets_text += " ".join(role.get("bullets", []))

    summary = resume_data.get("summary", "")
    full_text = f"{summary} {bullets_text}"

    # Calculate years of experience (EXCLUDING internships)
    # CRITICAL: Internships do NOT count toward professional experience
    years_exp = None
    experience_list = resume_data.get("experience", [])
    if experience_list:
        # Count only non-internship roles
        internship_patterns = [r'\bintern\b', r'\binternship\b', r'\bco-?op\b', r'\bfellow\b', r'\btrainee\b', r'\bstudent\b']
        full_time_roles = 0
        for role in experience_list:
            title = (role.get("title", "") or "").lower()
            is_intern = any(re.search(p, title) for p in internship_patterns)
            if not is_intern:
                full_time_roles += 1
        # Estimate years based on full-time roles only
        years_exp = full_time_roles * 2.5 if full_time_roles > 0 else 0

    # Detect function and level
    detected_function, func_strength, func_evidence = detect_function_type(full_text, titles)
    detected_level, level_strength, level_evidence = detect_candidate_level(full_text, titles, years_exp)

    # Overall signal strength is the weaker of the two
    if func_strength == SignalStrength.NONE or level_strength == SignalStrength.NONE:
        overall_strength = SignalStrength.NONE
    elif func_strength == SignalStrength.WEAK or level_strength == SignalStrength.WEAK:
        overall_strength = SignalStrength.WEAK
    elif func_strength == SignalStrength.MODERATE or level_strength == SignalStrength.MODERATE:
        overall_strength = SignalStrength.MODERATE
    else:
        overall_strength = SignalStrength.STRONG

    # Determine target function from role title
    target_function = None
    if target_role_function:
        try:
            target_function = FunctionType(target_role_function)
        except ValueError:
            pass

    if not target_function and target_role_title:
        target_lower = target_role_title.lower()
        # Check recruiting first (before PM checks)
        if re.search(r'\b(?:recruit(?:er|ing)|talent\s+acquis|ta\s+(?:lead|manager|director|head)|sourcer)\b', target_lower):
            target_function = FunctionType.RECRUITING
        elif "product" in target_lower and "manager" in target_lower:
            target_function = FunctionType.PRODUCT_MANAGEMENT
        elif "project" in target_lower and "manager" in target_lower:
            target_function = FunctionType.PROJECT_MANAGEMENT
        elif "engineer" in target_lower or "developer" in target_lower:
            target_function = FunctionType.ENGINEERING
        elif "design" in target_lower:
            target_function = FunctionType.DESIGN
        elif re.search(r'\b(?:customer\s+success|csm|account\s+manag)\b', target_lower):
            target_function = FunctionType.CUSTOMER_SUCCESS
        elif re.search(r'\b(?:finance|fp&a|controller|accounting)\b', target_lower):
            target_function = FunctionType.FINANCE

    # Determine function match
    function_match = True
    if target_function:
        if target_function == FunctionType.PRODUCT_MANAGEMENT:
            # Only PRODUCT_MANAGEMENT matches PRODUCT_MANAGEMENT
            function_match = detected_function == FunctionType.PRODUCT_MANAGEMENT
        elif target_function == FunctionType.RECRUITING:
            # Only RECRUITING matches RECRUITING
            function_match = detected_function == FunctionType.RECRUITING
        else:
            function_match = detected_function == target_function

    # Generate canonical statement
    canonical = generate_canonical_statement(
        detected_function,
        detected_level,
        overall_strength,
        target_function,
        function_match
    )

    return CanonicalCandidateProfile(
        detected_function=detected_function,
        detected_level=detected_level,
        signal_strength=overall_strength,
        canonical_statement=canonical,
        function_evidence=func_evidence,
        level_evidence=level_evidence,
        target_function=target_function,
        function_match=function_match,
        level_gap=0  # TODO: Calculate based on target level
    )


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
            "years of experience",  # P1-4: Say "function experience" not "years"
        ],
        required_messaging=[
            "function mismatch",
            "different function",
            "requires [function] experience",  # P1-4: Specify function, not years
        ],
        reason="This role requires experience in a different function than your background"
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
    ARCH-003: Detect REAL scope signals - quantified scale metrics only.

    Activity nouns alone do NOT count as scope.
    Titles alone do NOT count as scope.

    Must have at least ONE of:
    - Quantified scale metric (team size, budget, user volume, revenue, geography)
    - Clear ownership of a bounded system with complexity markers (for senior ICs)
    """
    if not text:
        return False

    text_lower = text.lower()

    # Option 1: Quantified scale patterns
    quantified_scale_patterns = [
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

    for pattern in quantified_scale_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # Option 2: Bounded system ownership + complexity marker (ARCH-003)
    # For senior ICs at early-stage who own bounded systems
    # e.g., "Owned the recommendation engine" + "serving 10M requests/day"
    # e.g., "Built the payments infrastructure" + "processing $X"

    # System ownership patterns - must show clear ownership
    system_ownership_patterns = [
        r'\b(?:owned|built|architected|designed|created)\s+(?:the\s+)?(?:\w+\s+){0,2}(?:engine|infrastructure|platform|system|pipeline|service|api|framework)',
        r'\b(?:owned|led)\s+(?:the\s+)?(?:entire|full|end-to-end)\s+\w+',
        r'\bsole\s+(?:owner|architect|engineer)',
        r'\bfrom\s+(?:scratch|zero|ground\s+up)',
    ]

    # Complexity markers - must show scale or difficulty
    complexity_markers = [
        r'\bserving\s+\d+',
        r'\bprocessing\s+[\$\d]',
        r'\bhandling\s+\d+',
        r'\bscaling\s+(?:to|from)',
        r'\b\d+\s*(?:ms|millisecond|latency)',
        r'\b(?:99|99\.9|99\.99)%?\s*(?:uptime|availability|SLA)',
        r'\bhigh[\-\s]?(?:availability|throughput|performance)',
        r'\bdistributed\b',
        r'\bmicroservices?\b',
        r'\breal[\-\s]?time\b',
        r'\bproduction\s+(?:system|traffic|load)',
    ]

    has_ownership = any(re.search(p, text_lower) for p in system_ownership_patterns)
    has_complexity = any(re.search(p, text_lower) for p in complexity_markers)

    if has_ownership and has_complexity:
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


def has_ownership_signal(text: str, require_quantified: bool = False) -> bool:
    """
    Detect ownership signals - decision-maker language, not contributor language.

    P1-3 Enhancement: Can require quantified evidence alongside ownership words.
    For senior roles, ownership claims need proof (team size, scope, etc.)

    Args:
        text: The bullet or text to check
        require_quantified: If True, ownership words alone are not enough - must have numbers
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

    if not has_ownership or has_contributor:
        return False

    # P1-3: If quantified evidence is required, check for numbers
    if require_quantified:
        # Must have some quantification - numbers, percentages, dollar amounts
        has_numbers = bool(re.search(r'\d+', text))
        if not has_numbers:
            return False

    return True


def has_leadership_signal(text: str) -> bool:
    """
    P1-3: Detect REAL leadership signals with quantified evidence.

    Leadership claims require proof:
    - "Led team" must include team size
    - "Managed" must include what/who
    - "Hired" must include count

    Words alone are not enough. Must have numbers or specific scope.
    """
    if not text:
        return False

    # Leadership patterns that REQUIRE numbers
    # These patterns allow words between the verb and the number
    leadership_with_numbers = [
        # "Managed 25-person team", "Led a team of 10"
        r'\b(?:led|managed|oversaw)\s+(?:a\s+)?(?:team\s+of\s+)?\d+',
        # "Managed 25-person global team", "Led 10-person engineering team"
        r'\b(?:led|managed)\s+\d+[\-\s]*(person|people|engineer|member|report)',
        # "Managed a 25-person team", "Led the 10-person team"
        r'\b(?:led|managed|oversaw)\s+(?:a|the)?\s*\d+[\-\s]*(person|people|member)',
        # "Managed global team of 25", "Led recruiting team of 10"
        r'\b(?:led|managed|oversaw)\s+(?:\w+\s+){0,3}team\s+of\s+\d+',
        # "Managed 25 recruiters", "Led 10 engineers"
        r'\b(?:led|managed|oversaw)\s+\d+\s+\w+',
        r'\bhired\s+\d+',
        r'\bbuilt\s+(?:a\s+)?team\s+(?:of\s+)?\d+',
        r'\b\d+\s*direct\s*reports?\b',
        r'\bmentored\s+\d+',
        r'\bgrew\s+(?:team|org)\s+(?:from\s+)?\d+',
        # "team of 25", "org of 100" anywhere in text with a number
        r'\bteam\s+of\s+\d+',
        r'\borg(?:anization)?\s+of\s+\d+',
        # "25-person team", "100-member organization"
        r'\b\d+[\-\s]*(?:person|people|member|head)\s+(?:team|org|department|group)',
    ]

    for pattern in leadership_with_numbers:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # Leadership patterns that require scope context (budget, P&L, etc.)
    leadership_with_scope = [
        r'\b(?:owned|managed)\s+(?:a\s+)?\$[\d,\.]+',
        r'\bp&l\s*(?:of|for)?\s*\$[\d,\.]+',
        r'\bbudget\s*(?:of|for)?\s*\$[\d,\.]+',
        r'\bresponsible\s+for\s+\$[\d,\.]+',
    ]

    for pattern in leadership_with_scope:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


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

    # P1-3: Check for leadership evidence using new rigorous validation
    # Leadership claims now require quantified evidence (team size, budget, etc.)
    has_leadership = False
    for bullet in bullets:
        if has_leadership_signal(bullet):
            has_leadership = True
            evidence_found.append(f"Leadership: {bullet[:50]}...")
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
# P1-CRITICAL: EXPERIENCE DETECTION HELPERS
# Internships do NOT count toward professional experience in ANY function
# =============================================================================

# Patterns that indicate a role is an internship/non-professional
INTERNSHIP_PATTERNS = [
    r'\bintern\b',
    r'\binternship\b',
    r'\bco-?op\b',
    r'\bfellow(?:ship)?\b',
    r'\bapprentice\b',
    r'\btrainee\b',
    r'\bstudent\b',
]


def _is_internship_role(title: str, company: str = "") -> bool:
    """
    Check if a role is an internship or non-professional position.

    Internships do NOT count toward professional experience regardless of function.
    """
    title_lower = (title or "").lower()
    company_lower = (company or "").lower()

    for pattern in INTERNSHIP_PATTERNS:
        if re.search(pattern, title_lower):
            return True
        if re.search(pattern, company_lower):
            return True

    return False


def _count_professional_experience(resume: dict) -> Tuple[int, int, int]:
    """
    Count PROFESSIONAL experience from resume, excluding internships.

    Returns: (total_roles, internship_count, full_time_months)

    CRITICAL: Internships do NOT count toward professional experience.
    A candidate with 5 years of internships has 0 years of professional experience.
    """
    total_roles = 0
    internship_count = 0
    full_time_months = 0

    for role in resume.get("experience", []):
        title = role.get("title", "") or ""
        company = role.get("company", "") or ""

        total_roles += 1

        if _is_internship_role(title, company):
            internship_count += 1
        else:
            # Only count full-time roles toward experience
            duration = role.get("duration_months", 24)  # Default 24 months if unknown
            full_time_months += duration

    return total_roles, internship_count, full_time_months


def _count_pm_experience(resume: dict) -> Tuple[int, int, int]:
    """
    Count PM-specific experience from resume.

    Returns: (pm_role_count, pm_internship_count, pm_full_time_months)

    This distinguishes between:
    - PM internships (short-term, learning roles)
    - Full-time PM roles (actual PM experience)

    Someone with only PM internships should not be treated as having PM experience
    for senior PM roles.
    """
    pm_role_count = 0
    pm_internship_count = 0
    pm_full_time_months = 0

    pm_title_patterns = [
        r'\bproduct\s+manager\b',
        r'\bproduct\s+owner\b',
        r'\bpm\b',
        r'\bapm\b',
        r'\bassociate\s+product\s+manager\b',
    ]

    for role in resume.get("experience", []):
        title = (role.get("title", "") or "").lower()
        company = role.get("company", "") or ""

        # Check if this is a PM role
        is_pm_role = any(re.search(p, title) for p in pm_title_patterns)

        if not is_pm_role:
            continue

        pm_role_count += 1

        # Check if it's an internship
        if _is_internship_role(title, company):
            pm_internship_count += 1
        else:
            # Only count full-time PM roles
            duration = role.get("duration_months", 24)
            pm_full_time_months += duration

    return pm_role_count, pm_internship_count, pm_full_time_months


def _calculate_professional_years(resume: dict) -> float:
    """
    Calculate years of PROFESSIONAL experience, excluding internships.

    CRITICAL: This is the correct way to calculate experience.
    Internships are learning experiences, not professional experience.
    """
    _, _, full_time_months = _count_professional_experience(resume)
    return full_time_months / 12.0


def _detect_self_declared_level(text: str) -> Optional[str]:
    """
    Detect if the candidate has self-declared their target level.

    Patterns like:
    - "Seeking APM role"
    - "Looking for entry-level PM position"
    - "Junior product manager seeking..."

    If found, this should cap the candidate's assessed level.
    """
    if not text:
        return None

    text_lower = text.lower()

    # Self-declaration patterns that indicate entry/junior level
    entry_patterns = [
        r'seeking\s+(?:an?\s+)?(?:entry[\-\s]?level|junior|apm|associate)',
        r'looking\s+for\s+(?:an?\s+)?(?:entry[\-\s]?level|junior|apm|associate)',
        r'aspiring\s+(?:product\s+manager|pm)',
        r'transitioning\s+(?:to|into)\s+(?:product|pm)',
        r'breaking\s+into\s+(?:product|pm)',
        r'career\s+change\s+(?:to|into)\s+(?:product|pm)',
        r'first\s+(?:product|pm)\s+role',
        r'entry[\-\s]?level\s+(?:product|pm)',
        r'junior\s+(?:product|pm)',
        r'apm\s+(?:role|position|opportunity)',
        r'associate\s+product\s+manager\s+(?:role|position)',
    ]

    for pattern in entry_patterns:
        if re.search(pattern, text_lower):
            return "entry"

    # Check for associate-level declarations
    associate_patterns = [
        r'seeking\s+(?:an?\s+)?associate',
        r'apm\s+or\s+junior',
        r'2[\-\s]?3\s+years?\s+(?:of\s+)?experience',
    ]

    for pattern in associate_patterns:
        if re.search(pattern, text_lower):
            return "associate"

    return None


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
    # P1-CRITICAL: Check professional experience (excluding ALL internships)
    total_roles, internship_count, full_time_months = _count_professional_experience(resume)
    pm_role_count, pm_internship_count, pm_full_time_months = _count_pm_experience(resume)
    self_declared_level = _detect_self_declared_level(all_text)
    professional_years = full_time_months / 12.0

    level_hierarchy = {
        "entry": 1, "junior": 1, "associate": 2, "apm": 2,
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

    # P1-CRITICAL: Override detected level based on ACTUAL professional experience
    # Internships do NOT count toward experience in ANY function
    if internship_count > 0 and full_time_months < 12:
        # Candidate has mostly/only internships - treat as entry level
        detected_num = 1  # Entry level
        detected_level = f"Entry ({internship_count} internship(s), <1 year professional experience)"

    # P1-CRITICAL: Override for internship-only PM experience specifically
    # If candidate only has PM internships (no full-time PM), they are ENTRY level for PM roles
    if pm_internship_count > 0 and pm_full_time_months < 12:
        detected_num = 1  # Entry level
        detected_level = "Entry (internship-only PM experience)"

    # P1-CRITICAL: Self-declared level caps the detected level
    # If resume says "seeking APM" or "entry-level position", respect that
    if self_declared_level:
        declared_num = level_hierarchy.get(self_declared_level, 3)
        if declared_num < detected_num:
            detected_num = declared_num
            detected_level = f"{self_declared_level.title()} (self-declared)"

    level_gap = target_num - detected_num

    # P1-CRITICAL: For severe gaps (3+ levels), use Do Not Apply
    if level_gap >= 3:
        # Create a more severe contract for severe experience gaps
        contract = TerminalStateContract(
            state_type=TerminalStateType.EXPERIENCE_GAP,
            fit_score_cap=25,  # Stricter cap for severe gaps
            recommendation="Do Not Apply",
            recommendation_cap="Do Not Apply",
            apply_button=ApplyButtonState.DISABLED,
            coaching_mode=CoachingMode.REDIRECTION,
            forbidden_messaging=[
                "strong fit", "ideal candidate", "competitive",
                "apply fast", "well-positioned", "good match"
            ],
            required_messaging=[
                "experience gap", "below target level", "redirect"
            ],
            reason=f"Experience level ({detected_level}) is {level_gap} levels below target ({target_level}). This is a severe gap."
        )
        return contract

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


# =============================================================================
# TERMINAL AUTHORITY COPY FILTER (P1-1)
# =============================================================================

# Universal forbidden phrases when ANY terminal state is active
UNIVERSAL_FORBIDDEN_PHRASES = [
    "you have the foundation",
    "supports senior pm roles",
    "supports senior product manager roles",
    "you likely have this",
    "make it visible on your resume",
    "gaps are meant to be closed",
    "let's build the foundation",
    "a few targeted improvements",
    "i've done the heavy lifting",
    "ready to apply",
    "ready to submit",
]

# Additional phrases forbidden for specific terminal states
TERMINAL_STATE_FORBIDDEN_PHRASES = {
    TerminalStateType.TITLE_INFLATION: [
        "presentation gap",
        "you're probably operating at senior",
        "you're close",
        "stretch role",
        "with some polish",
    ],
    TerminalStateType.CREDIBILITY_VIOLATION: [
        "presentation gap",
        "you're close",
        "strong foundation",
        "competitive",
    ],
    TerminalStateType.FUNCTION_MISMATCH: [
        "years of experience",  # Should say "function experience" not "years"
        "presentation gap",
        "you're close to",
    ],
    TerminalStateType.ELIGIBILITY_VIOLATION: [
        "presentation gap",
        "you're close",
    ],
}


def terminal_authority_copy_filter(
    response_data: dict,
    terminal_state: Optional[TerminalStateContract] = None
) -> dict:
    """
    FINAL PASS FILTER: Nukes forbidden phrases before render.

    This runs LAST, after all other processing, to ensure no optimistic
    language leaks through when a terminal state is active.

    Args:
        response_data: The complete response dict about to be returned
        terminal_state: The active terminal state contract (if any)

    Returns:
        response_data with forbidden phrases stripped from all text fields
    """
    # If no terminal state or NONE, skip filtering
    if terminal_state is None:
        terminal_state_dict = response_data.get("terminal_state", {})
        if not terminal_state_dict:
            return response_data
        state_type_str = terminal_state_dict.get("state_type", "NONE")
        if state_type_str == "NONE":
            return response_data
        try:
            state_type = TerminalStateType(state_type_str)
        except ValueError:
            return response_data
    else:
        if terminal_state.state_type == TerminalStateType.NONE:
            return response_data
        state_type = terminal_state.state_type

    # Build forbidden phrases list
    forbidden_phrases = UNIVERSAL_FORBIDDEN_PHRASES.copy()

    # Add state-specific forbidden phrases
    state_specific = TERMINAL_STATE_FORBIDDEN_PHRASES.get(state_type, [])
    forbidden_phrases.extend(state_specific)

    # Also add phrases from the contract's forbidden_messaging
    contract_forbidden = TERMINAL_STATES.get(state_type)
    if contract_forbidden:
        forbidden_phrases.extend(contract_forbidden.forbidden_messaging)

    # De-duplicate
    forbidden_phrases = list(set(phrase.lower() for phrase in forbidden_phrases))

    # Text fields to scan and filter
    text_fields_to_filter = [
        "recommendation_text",
        "rationale",
        "role_snapshot",
        "whats_working",
        "quick_win",
        "strategic_action",
        "brutal_truth",
        "why_still_viable",
        "helper_text",
        "cta_text",
    ]

    # Nested fields in reality_check
    reality_check_fields = [
        "strategic_action",
        "brutal_truth",
        "why_still_viable",
        "what_it_takes",
    ]

    filtered_count = 0

    def filter_text(text: str) -> Tuple[str, int]:
        """Filter forbidden phrases from text, return filtered text and count."""
        if not text:
            return text, 0

        count = 0
        filtered = text

        for phrase in forbidden_phrases:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            matches = pattern.findall(filtered)
            if matches:
                count += len(matches)
                # Replace with empty string (or could use placeholder)
                filtered = pattern.sub("", filtered)

        # Clean up double spaces and trailing punctuation issues
        filtered = re.sub(r'\s{2,}', ' ', filtered)
        filtered = re.sub(r'\s+([.,;:])', r'\1', filtered)
        filtered = filtered.strip()

        return filtered, count

    # Filter top-level fields
    for field in text_fields_to_filter:
        if field in response_data and response_data[field]:
            filtered, count = filter_text(response_data[field])
            if count > 0:
                response_data[field] = filtered
                filtered_count += count

    # Filter reality_check nested fields
    if "reality_check" in response_data and isinstance(response_data["reality_check"], dict):
        for field in reality_check_fields:
            if field in response_data["reality_check"] and response_data["reality_check"][field]:
                filtered, count = filter_text(response_data["reality_check"][field])
                if count > 0:
                    response_data["reality_check"][field] = filtered
                    filtered_count += count

    # Filter gap_analysis items
    if "gap_analysis" in response_data and isinstance(response_data["gap_analysis"], list):
        for i, gap in enumerate(response_data["gap_analysis"]):
            if isinstance(gap, dict):
                for key in ["description", "guidance", "action"]:
                    if key in gap and gap[key]:
                        filtered, count = filter_text(gap[key])
                        if count > 0:
                            response_data["gap_analysis"][i][key] = filtered
                            filtered_count += count

    # Filter coaching sections
    if "coaching" in response_data and isinstance(response_data["coaching"], dict):
        for section_key, section_value in response_data["coaching"].items():
            if isinstance(section_value, str):
                filtered, count = filter_text(section_value)
                if count > 0:
                    response_data["coaching"][section_key] = filtered
                    filtered_count += count
            elif isinstance(section_value, list):
                for i, item in enumerate(section_value):
                    if isinstance(item, str):
                        filtered, count = filter_text(item)
                        if count > 0:
                            response_data["coaching"][section_key][i] = filtered
                            filtered_count += count

    # Log filtering activity
    if filtered_count > 0:
        print(f"🔒 TERMINAL AUTHORITY FILTER: Removed {filtered_count} forbidden phrase(s) for {state_type.value}")
        response_data["_copy_filter_applied"] = True
        response_data["_copy_filter_count"] = filtered_count
        response_data["_copy_filter_state"] = state_type.value

    return response_data


# =============================================================================
# P2 - DOMAIN TRANSLATION GUARDRAIL (ARCH-004)
# =============================================================================

# Domain categories for matching
DOMAIN_CATEGORIES = {
    "b2b_saas": [
        "saas", "b2b", "enterprise software", "subscription", "recurring revenue",
        "enterprise sales", "sales cycle", "enterprise customer", "b2b sales",
    ],
    "messaging": [
        "messaging", "notifications", "push notifications", "email infrastructure",
        "sms", "communications platform", "messaging infrastructure", "in-app messaging",
        "twilio", "sendgrid", "braze", "iterable", "customer.io",
    ],
    "fintech": [
        "fintech", "payments", "banking", "financial services", "lending",
        "credit", "debit", "transactions", "payment processing", "stripe",
        "checkout", "billing", "invoicing", "financial infrastructure",
    ],
    "adtech": [
        "advertising", "adtech", "programmatic", "rtb", "dsp", "ssp",
        "ad exchange", "media buying", "ad serving", "attribution",
        "marketing technology", "martech",
    ],
    "ecommerce": [
        "ecommerce", "e-commerce", "retail", "marketplace", "shopping",
        "cart", "checkout", "product catalog", "inventory", "fulfillment",
        "shopify", "amazon", "ebay",
    ],
    "healthcare": [
        "healthcare", "health tech", "clinical", "ehr", "emr", "hipaa",
        "patient", "provider", "telemedicine", "telehealth", "medical",
    ],
    "developer_tools": [
        "developer tools", "devtools", "api", "sdk", "infrastructure",
        "platform", "developer platform", "developer experience", "dx",
        "ci/cd", "deployment", "cloud infrastructure",
    ],
    "data_analytics": [
        "analytics", "data platform", "data infrastructure", "bi",
        "business intelligence", "data warehouse", "etl", "data pipeline",
        "machine learning platform", "ml platform", "data science",
    ],
    "security": [
        "security", "cybersecurity", "infosec", "identity", "authentication",
        "authorization", "iam", "sso", "encryption", "compliance",
    ],
    "consumer": [
        "consumer", "b2c", "social", "content", "media", "entertainment",
        "gaming", "mobile app", "consumer app",
    ],
}

# Adjacent domains - reasonable translation claims
ADJACENT_DOMAINS = {
    "b2b_saas": ["developer_tools", "data_analytics"],
    "messaging": ["b2b_saas", "adtech", "ecommerce"],
    "fintech": ["ecommerce", "b2b_saas", "security"],
    "adtech": ["messaging", "data_analytics", "ecommerce"],
    "ecommerce": ["fintech", "consumer", "messaging"],
    "healthcare": ["b2b_saas", "security"],
    "developer_tools": ["b2b_saas", "data_analytics", "security"],
    "data_analytics": ["b2b_saas", "developer_tools", "adtech"],
    "security": ["developer_tools", "fintech", "healthcare"],
    "consumer": ["ecommerce", "adtech"],
}


def detect_candidate_domains(resume_text: str) -> List[str]:
    """
    Detect which domains a candidate has experience in based on resume text.

    Returns list of domain category keys.
    """
    if not resume_text:
        return []

    text_lower = resume_text.lower()
    detected_domains = []

    for domain, keywords in DOMAIN_CATEGORIES.items():
        # Require at least 2 keyword matches to claim domain experience
        match_count = sum(1 for kw in keywords if kw in text_lower)
        if match_count >= 2:
            detected_domains.append(domain)

    return detected_domains


def detect_target_domain(job_description: str) -> Optional[str]:
    """
    Detect the primary domain of a job description.

    Returns the domain category key with the most keyword matches.
    """
    if not job_description:
        return None

    text_lower = job_description.lower()
    domain_scores = {}

    for domain, keywords in DOMAIN_CATEGORIES.items():
        match_count = sum(1 for kw in keywords if kw in text_lower)
        if match_count > 0:
            domain_scores[domain] = match_count

    if not domain_scores:
        return None

    # Return domain with highest score
    return max(domain_scores, key=domain_scores.get)


def validate_domain_translation(
    candidate_domains: List[str],
    target_domain: Optional[str]
) -> Tuple[bool, str]:
    """
    P2/ARCH-004: Validate if "translates well to X" claim is supported.

    Returns: (is_valid, reason)

    Valid if:
    - Candidate has direct experience in target domain
    - Candidate has experience in adjacent domain
    - Target domain is unknown (can't invalidate)

    Invalid if:
    - Candidate has no experience in target or adjacent domains
    """
    if not target_domain:
        return True, "Target domain not identified - claim allowed"

    if not candidate_domains:
        return False, f"No domain experience detected, cannot claim translation to {target_domain}"

    # Direct match
    if target_domain in candidate_domains:
        return True, f"Direct experience in {target_domain}"

    # Adjacent domain match
    adjacent = ADJACENT_DOMAINS.get(target_domain, [])
    for domain in candidate_domains:
        if domain in adjacent:
            return True, f"{domain} is adjacent to {target_domain}"

    # Also check reverse - is target adjacent to candidate's domains?
    for domain in candidate_domains:
        candidate_adjacent = ADJACENT_DOMAINS.get(domain, [])
        if target_domain in candidate_adjacent:
            return True, f"{target_domain} is adjacent to candidate's {domain} experience"

    return False, f"No domain overlap: candidate has {candidate_domains}, target is {target_domain}"


def filter_unvalidated_translation_claims(
    text: str,
    candidate_domains: List[str],
    target_domain: Optional[str]
) -> str:
    """
    P2/ARCH-004: Filter out "translates well to X" claims without evidence.

    If domain translation is not validated, strip these phrases:
    - "translates well to"
    - "experience translates to"
    - "skills transfer to"
    - "background applies to"
    """
    is_valid, _ = validate_domain_translation(candidate_domains, target_domain)

    if is_valid:
        return text

    # Phrases to filter when translation is NOT valid
    translation_phrases = [
        r"your?\s+(?:experience|background|skills?)\s+translates?\s+(?:well\s+)?to",
        r"translates?\s+well\s+to",
        r"skills?\s+transfer\s+(?:well\s+)?to",
        r"background\s+applies?\s+(?:well\s+)?to",
        r"experience\s+is\s+transferable\s+to",
        r"directly\s+applicable\s+to",
    ]

    filtered = text
    for pattern in translation_phrases:
        filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE)

    # Clean up
    filtered = re.sub(r'\s{2,}', ' ', filtered)
    filtered = re.sub(r'\s+([.,;:])', r'\1', filtered)

    return filtered.strip()


# =============================================================================
# P2 - EXPANDED MID-MARKET PHRASE DETECTION (ARCH-013)
# =============================================================================

# Comprehensive mid-market phrase list (90+ phrases)
EXPANDED_MID_MARKET_PHRASES = [
    # Original phrases
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

    # P2 Expansion - Common generic phrases
    "responsible for",
    "worked on",
    "involved in",
    "participated in",
    "helped with",
    "assisted with",
    "contributed to",
    "supported",
    "exposure to",
    "familiar with",
    "experience with",

    # P2 Expansion - Cliche accomplishment phrases
    "successfully delivered",
    "successfully completed",
    "successfully implemented",
    "key contributor",
    "major contributor",
    "significant contributor",
    "played a key role",
    "instrumental in",
    "critical to success",

    # P2 Expansion - Vague impact phrases
    "improved efficiency",
    "increased productivity",
    "streamlined processes",
    "optimized workflows",
    "enhanced performance",
    "drove results",
    "delivered value",
    "added value",
    "created value",

    # P2 Expansion - Generic leadership phrases
    "leadership experience",
    "leadership skills",
    "team leadership",
    "project leadership",
    "strong leader",
    "effective leader",
    "natural leader",

    # P2 Expansion - Overused soft skills
    "excellent organizational skills",
    "strong organizational skills",
    "time management skills",
    "multitasking abilities",
    "ability to prioritize",
    "ability to work independently",
    "works well under pressure",
    "performs well under pressure",
    "deadline-driven",
    "goal-oriented",

    # P2 Expansion - Generic technical phrases
    "technical skills",
    "technical expertise",
    "technical proficiency",
    "hands-on experience",
    "practical experience",
    "real-world experience",

    # P2 Expansion - Filler phrases
    "various projects",
    "numerous projects",
    "multiple projects",
    "many projects",
    "various initiatives",
    "numerous initiatives",
    "several teams",
    "various teams",
    "different departments",
    "various stakeholders",
]


def detect_mid_market_language_expanded(text: str) -> List[Dict[str, str]]:
    """
    P2/ARCH-013: Expanded mid-market phrase detection with itemized results.

    Returns list of dicts with phrase and suggestion for each match.
    """
    if not text:
        return []

    text_lower = text.lower()
    found = []

    # Phrase replacements/suggestions
    phrase_suggestions = {
        "responsible for": "Use action verbs: 'Owned', 'Led', 'Built'",
        "worked on": "Specify what you built or shipped",
        "involved in": "Describe your specific contribution",
        "results-driven": "Show results with numbers instead",
        "proven track record": "List specific accomplishments",
        "self-starter": "Give example of initiative you took",
        "team player": "Describe cross-functional collaboration with outcomes",
        "excellent communication skills": "Show communication impact (presentations, docs, alignment)",
        "detail-oriented": "Give example of catching critical issue",
        "fast-paced environment": "Quantify velocity (shipped X features in Y weeks)",
        "cross-functional teams": "Name the functions and what you achieved together",
        "stakeholders at all levels": "Name specific stakeholders (VP Eng, CEO, etc.)",
        "managed multiple projects": "Quantify: 'Managed 5 concurrent projects worth $Xm'",
        "improved efficiency": "Quantify: 'Reduced processing time by X%'",
        "streamlined processes": "Quantify: 'Cut approval time from X days to Y hours'",
        "leadership experience": "Specify: 'Led team of X' or 'Managed $X budget'",
        "various projects": "Be specific: 'Led checkout redesign, fraud detection system'",
    }

    for phrase in EXPANDED_MID_MARKET_PHRASES:
        if phrase in text_lower:
            suggestion = phrase_suggestions.get(phrase, f"Replace '{phrase}' with specific, quantified evidence")
            found.append({
                "phrase": phrase,
                "severity": "MEDIUM",
                "suggestion": suggestion,
            })

    return found


def get_mid_market_score(text: str) -> Tuple[int, str]:
    """
    Calculate a mid-market language score for text.

    Returns: (score 0-100, severity level)
    - 0-2 phrases: LOW (good)
    - 3-5 phrases: MEDIUM (needs work)
    - 6-10 phrases: HIGH (significant rewrite needed)
    - 11+: CRITICAL (complete rewrite needed)
    """
    phrases = detect_mid_market_language_expanded(text)
    count = len(phrases)

    if count <= 2:
        return count, "LOW"
    elif count <= 5:
        return count, "MEDIUM"
    elif count <= 10:
        return count, "HIGH"
    else:
        return count, "CRITICAL"
