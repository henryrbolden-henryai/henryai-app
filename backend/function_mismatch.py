"""
Function Mismatch Detection Module

Detects when a candidate's primary function does not match the role's primary function.
This is distinct from transferable skills assessment - a PM applying to a TPM role is a
FUNCTION MISMATCH, not just a skills gap.

Severity Levels:
- none: Same function, no mismatch
- adjacent: Functions with significant overlap (e.g., PM → TPM)
- significant: Functions with some transferable skills (e.g., Marketing → PM)
- complete: Functions with minimal overlap (e.g., Recruiting → PM)

Score Caps by Severity:
- adjacent: 55%
- significant: 35-50%
- complete: 25-30%
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import re


class MismatchSeverity(str, Enum):
    """Severity levels for function mismatch."""
    NONE = "none"
    ADJACENT = "adjacent"
    SIGNIFICANT = "significant"
    COMPLETE = "complete"


# =============================================================================
# FUNCTION TAXONOMY
# =============================================================================

FUNCTION_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "product_management": {
        "titles": [
            "product manager", "pm", "senior product manager", "staff product manager",
            "principal product manager", "group product manager", "director of product",
            "vp product", "chief product officer", "associate product manager",
            "product lead", "product owner", "head of product"
        ],
        "signals": [
            "roadmap", "product strategy", "user research", "feature prioritization",
            "product requirements", "prd", "product vision", "customer discovery",
            "product-market fit", "backlog", "product analytics", "a/b testing",
            "experimentation", "product metrics", "product discovery"
        ],
        "core_responsibility": "Owns WHAT gets built and WHY"
    },

    "program_management": {
        "titles": [
            "program manager", "technical program manager", "tpm", "senior tpm",
            "staff tpm", "principal tpm", "program director", "portfolio manager",
            "delivery manager", "release manager", "launch manager", "head of programs"
        ],
        "signals": [
            "portfolio", "program delivery", "cross-functional coordination",
            "executive reporting", "milestone tracking", "dependency management",
            "risk management", "delivery cadence", "operating rhythm",
            "program governance", "workstream", "initiative tracking", "program metrics"
        ],
        "core_responsibility": "Owns HOW and WHEN things get delivered across workstreams"
    },

    "project_management": {
        "titles": [
            "project manager", "senior project manager", "it project manager",
            "technical project manager", "project coordinator", "pmo", "project lead"
        ],
        "signals": [
            "project plan", "gantt", "project timeline", "resource allocation",
            "project budget", "scope management", "project status", "deliverables",
            "project schedule", "milestone", "pmp", "prince2", "waterfall"
        ],
        "core_responsibility": "Owns delivery of a single project within defined scope"
    },

    "engineering": {
        "titles": [
            "software engineer", "senior engineer", "staff engineer", "principal engineer",
            "tech lead", "architect", "sre", "devops", "data engineer", "backend engineer",
            "frontend engineer", "fullstack engineer", "mobile engineer", "platform engineer"
        ],
        "signals": [
            "code", "architecture", "system design", "technical debt",
            "code review", "deployment", "infrastructure", "api design",
            "programming", "software development", "ci/cd", "microservices"
        ],
        "core_responsibility": "Owns technical implementation and system architecture"
    },

    "engineering_management": {
        "titles": [
            "engineering manager", "senior engineering manager", "director of engineering",
            "vp engineering", "head of engineering", "tech lead manager", "tlm",
            "chief technology officer", "cto"
        ],
        "signals": [
            "team leadership", "hiring engineers", "performance reviews",
            "technical roadmap", "engineering culture", "team scaling",
            "engineering organization", "tech strategy"
        ],
        "core_responsibility": "Owns engineering team performance and technical direction"
    },

    "data_analytics": {
        "titles": [
            "data analyst", "senior data analyst", "analytics manager",
            "business intelligence", "bi analyst", "data scientist",
            "analytics engineer", "head of analytics", "director of analytics"
        ],
        "signals": [
            "sql", "dashboards", "metrics", "data modeling", "tableau",
            "looker", "analytics", "reporting", "insights", "kpis",
            "data visualization", "statistical analysis"
        ],
        "core_responsibility": "Owns data analysis, reporting, and insights generation"
    },

    "strategy_operations": {
        "titles": [
            "strategy manager", "chief of staff", "business operations",
            "strategy and operations", "corporate strategy", "strategic planning",
            "director of strategy", "head of operations", "biz ops"
        ],
        "signals": [
            "strategic planning", "business cases", "market analysis",
            "competitive intelligence", "operating model", "org design",
            "executive enablement", "operating rhythm", "strategic initiatives"
        ],
        "core_responsibility": "Owns strategic analysis and operational planning"
    },

    "marketing": {
        "titles": [
            "marketing manager", "product marketing manager", "pmm",
            "growth marketing", "brand manager", "director of marketing",
            "vp marketing", "cmo", "content marketing", "demand generation"
        ],
        "signals": [
            "campaigns", "brand", "messaging", "positioning", "go-to-market",
            "demand generation", "content strategy", "marketing analytics",
            "lead generation", "marketing funnel"
        ],
        "core_responsibility": "Owns market positioning, messaging, and demand generation"
    },

    "sales": {
        "titles": [
            "account executive", "sales manager", "sales director",
            "business development", "bdm", "enterprise sales", "vp sales",
            "sales representative", "sdr", "bdr"
        ],
        "signals": [
            "quota", "pipeline", "deal closing", "sales cycle",
            "revenue target", "client acquisition", "account management",
            "sales process", "crm", "salesforce"
        ],
        "core_responsibility": "Owns revenue generation through direct sales"
    },

    "recruiting": {
        "titles": [
            "recruiter", "talent acquisition", "senior recruiter",
            "recruiting manager", "head of talent", "director of ta",
            "talent partner", "sourcer", "recruiting coordinator"
        ],
        "signals": [
            "hiring", "candidates", "interview process", "offer management",
            "talent pipeline", "employer brand", "recruiting metrics",
            "sourcing", "ats", "greenhouse", "lever", "linkedin recruiter"
        ],
        "core_responsibility": "Owns talent identification, attraction, and hiring"
    },

    "design": {
        "titles": [
            "product designer", "ux designer", "ui designer", "design lead",
            "head of design", "ux researcher", "design manager", "senior designer",
            "principal designer", "design director"
        ],
        "signals": [
            "user experience", "wireframes", "prototypes", "design systems",
            "user testing", "figma", "interaction design", "visual design",
            "usability", "design thinking"
        ],
        "core_responsibility": "Owns user experience and interface design"
    },

    "finance": {
        "titles": [
            "financial analyst", "fp&a", "controller", "cfo",
            "finance manager", "accounting manager", "finops",
            "finance director", "treasurer"
        ],
        "signals": [
            "financial modeling", "budgeting", "forecasting", "p&l",
            "cost analysis", "financial reporting", "variance analysis",
            "financial planning", "accounting"
        ],
        "core_responsibility": "Owns financial planning, analysis, and reporting"
    },

    "customer_success": {
        "titles": [
            "customer success manager", "csm", "account manager",
            "client success", "customer success director", "head of cs"
        ],
        "signals": [
            "customer health", "nrr", "churn", "renewal", "onboarding",
            "customer retention", "customer satisfaction", "nps"
        ],
        "core_responsibility": "Owns customer relationship health and retention"
    },

    "human_resources": {
        "titles": [
            "hr manager", "hr business partner", "hrbp", "people operations",
            "head of hr", "chief people officer", "hr director"
        ],
        "signals": [
            "employee relations", "compensation", "benefits", "performance management",
            "people strategy", "hr policy", "workforce planning"
        ],
        "core_responsibility": "Owns people strategy and employee experience"
    }
}


# =============================================================================
# ADJACENCY MAP - Defines relationships between functions
# =============================================================================

ADJACENCY_MAP: Dict[Tuple[str, str], Dict[str, Any]] = {
    # PM <-> Program/Project Management
    ("product_management", "program_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 55,
        "transferable": ["cross-functional leadership", "stakeholder management", "roadmap thinking"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. TPMs own delivery across workstreams; PMs own product strategy. Your cross-functional experience transfers, but you'll need to reframe around program delivery, executive reporting, and portfolio governance rather than product vision."
    },
    ("product_management", "project_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 50,
        "transferable": ["project execution", "stakeholder communication", "timeline management"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Project Managers own single-project delivery within defined scope. Your PM experience is broader, but you'll need to demonstrate comfort with structured delivery methodologies."
    },
    ("program_management", "project_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 60,
        "transferable": ["delivery management", "stakeholder reporting", "timeline management"],
        "coaching": "This is a {role_fn} role. Your program management background is strong, but this role has narrower scope. Consider whether the level matches your experience."
    },

    # PM <-> Strategy/Ops
    ("product_management", "strategy_operations"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 55,
        "transferable": ["strategic thinking", "cross-functional work", "data-driven decisions"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Strategy & Ops roles prioritize executive enablement, operating rhythm, and portfolio visibility over product ownership. Reframe your experience around strategic analysis and operational planning."
    },

    # Engineering Management <-> Program Management
    ("engineering_management", "program_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 55,
        "transferable": ["technical credibility", "delivery management", "team coordination"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Your engineering leadership experience gives you technical credibility, but TPM roles require portfolio-level thinking across multiple workstreams, not just your team's delivery."
    },

    # Data/Analytics <-> PM
    ("data_analytics", "product_management"): {
        "severity": MismatchSeverity.SIGNIFICANT,
        "score_cap": 45,
        "transferable": ["data-driven thinking", "metrics definition", "analytical rigor"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Analytics provides insights; PM owns product decisions. You'll need to demonstrate product ownership, customer empathy, and roadmap prioritization beyond data analysis."
    },

    # Marketing <-> PM
    ("marketing", "product_management"): {
        "severity": MismatchSeverity.SIGNIFICANT,
        "score_cap": 40,
        "transferable": ["customer understanding", "go-to-market", "messaging"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Marketing drives demand and positioning; PM owns what gets built. Consider Product Marketing Manager roles as a bridge, or target PM roles where go-to-market expertise is valued."
    },

    # Sales <-> PM
    ("sales", "product_management"): {
        "severity": MismatchSeverity.SIGNIFICANT,
        "score_cap": 35,
        "transferable": ["customer conversations", "market feedback", "business acumen"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Sales expertise gives you customer insight, but PM requires product ownership, technical collaboration, and roadmap prioritization. Consider roles where customer-facing experience is explicitly valued."
    },

    # Design <-> PM
    ("design", "product_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 50,
        "transferable": ["user empathy", "customer research", "collaboration with engineering"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Your design background gives you strong user empathy and research skills, but PM requires business prioritization, technical tradeoffs, and P&L thinking beyond UX."
    },

    # Finance <-> Strategy/Ops
    ("finance", "strategy_operations"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 60,
        "transferable": ["financial modeling", "business analysis", "executive reporting"],
        "coaching": "This is a {role_fn} role. Your finance background transfers well to strategy and ops roles that require financial acumen. Emphasize business case development and cross-functional influence."
    },

    # Customer Success <-> PM
    ("customer_success", "product_management"): {
        "severity": MismatchSeverity.SIGNIFICANT,
        "score_cap": 40,
        "transferable": ["customer empathy", "feedback loops", "product input"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Customer Success gives you deep customer empathy, but PM requires product ownership, technical collaboration, and strategic roadmap decisions."
    },

    # Recruiting <-> PM (Complete mismatch)
    ("recruiting", "product_management"): {
        "severity": MismatchSeverity.COMPLETE,
        "score_cap": 25,
        "transferable": ["stakeholder management"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Your recruiting experience doesn't transfer to product ownership. If you want to pivot to PM, consider internal mobility, bootcamps, or associate PM programs designed for career changers."
    },

    # HR <-> PM (Complete mismatch)
    ("human_resources", "product_management"): {
        "severity": MismatchSeverity.COMPLETE,
        "score_cap": 25,
        "transferable": ["stakeholder management", "process design"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. HR experience doesn't directly transfer to product ownership. Consider internal mobility programs or associate PM roles designed for career changers."
    },

    # Engineering <-> PM
    ("engineering", "product_management"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 55,
        "transferable": ["technical depth", "engineering collaboration", "system thinking"],
        "coaching": "This is a {role_fn} role, not an engineering role. Your technical background is valuable for PM roles, but you'll need to demonstrate product ownership, customer empathy, and business prioritization beyond technical implementation."
    },

    # Program Management <-> Engineering Management
    ("program_management", "engineering_management"): {
        "severity": MismatchSeverity.SIGNIFICANT,
        "score_cap": 45,
        "transferable": ["delivery management", "cross-functional coordination"],
        "coaching": "This is an {role_fn} role, not a {candidate_fn} role. Engineering management requires people leadership, technical mentorship, and architecture ownership - not just delivery coordination."
    },

    # Sales <-> Customer Success
    ("sales", "customer_success"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 60,
        "transferable": ["client relationships", "account management", "revenue focus"],
        "coaching": "This is a {role_fn} role. Your sales background transfers well - both require strong client relationships. Customer Success focuses on retention and expansion rather than new acquisition."
    },

    # Marketing <-> Sales
    ("marketing", "sales"): {
        "severity": MismatchSeverity.ADJACENT,
        "score_cap": 55,
        "transferable": ["market understanding", "customer messaging", "pipeline contribution"],
        "coaching": "This is a {role_fn} role, not a {candidate_fn} role. Sales requires direct revenue accountability and deal closing skills beyond demand generation."
    }
}


@dataclass
class FunctionClassification:
    """Result of classifying a function from text."""
    primary_function: str
    confidence: float  # 0.0 - 1.0
    secondary_functions: List[str] = field(default_factory=list)
    classification_signals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_function": self.primary_function,
            "confidence": round(self.confidence, 2),
            "secondary_functions": self.secondary_functions,
            "classification_signals": self.classification_signals[:5]
        }


@dataclass
class FunctionMismatchResult:
    """Result of function mismatch detection."""
    is_mismatch: bool
    severity: MismatchSeverity
    candidate_function: str
    role_function: str
    transferable_skills: List[str] = field(default_factory=list)
    score_cap: Optional[int] = None
    coaching_message: Optional[str] = None

    # Classification details
    candidate_classification: Optional[FunctionClassification] = None
    role_classification: Optional[FunctionClassification] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected": self.is_mismatch,
            "severity": self.severity.value,
            "candidate_function": _format_function_name(self.candidate_function),
            "role_function": _format_function_name(self.role_function),
            "transferable_skills": self.transferable_skills,
            "score_cap": self.score_cap,
            "message": self.coaching_message,
            "candidate_classification": self.candidate_classification.to_dict() if self.candidate_classification else None,
            "role_classification": self.role_classification.to_dict() if self.role_classification else None
        }


def _format_function_name(function_key: str) -> str:
    """Convert function key to display name."""
    return function_key.replace("_", " ").title()


def classify_candidate_function(resume_data: Dict[str, Any]) -> FunctionClassification:
    """
    Determine candidate's primary function based on resume.

    Args:
        resume_data: Resume dictionary with experience, skills, summary

    Returns:
        FunctionClassification with primary function and confidence
    """
    function_scores: Dict[str, Dict[str, Any]] = {}

    # Extract text from resume
    experience = resume_data.get("experience", [])
    skills = resume_data.get("skills", {})
    summary = resume_data.get("summary", "")

    # Get all titles
    titles = []
    for exp in experience:
        if isinstance(exp, dict):
            title = exp.get("title", "")
            if title:
                titles.append(title.lower())

    # Get all bullets
    all_bullets = []
    for exp in experience:
        if isinstance(exp, dict):
            bullets = exp.get("bullets", [])
            if isinstance(bullets, list):
                all_bullets.extend(bullets)

    combined_text = " ".join(titles + all_bullets).lower()
    if summary:
        combined_text += " " + summary.lower()

    # Score each function
    for function_name, function_def in FUNCTION_TAXONOMY.items():
        score = 0.0
        signals_found = []

        # Check titles (highest weight = 3 points per match)
        for title in titles:
            for pattern in function_def["titles"]:
                if pattern in title:
                    score += 3.0
                    signals_found.append(f"Title: {title}")
                    break

        # Check for function signals in text (1 point per match)
        for signal in function_def["signals"]:
            # Use word boundary matching
            if re.search(rf'\b{re.escape(signal)}\b', combined_text):
                score += 1.0
                if len(signals_found) < 10:  # Limit signal list
                    signals_found.append(f"Signal: {signal}")

        function_scores[function_name] = {
            "score": score,
            "signals": signals_found
        }

    # Rank functions by score
    sorted_functions = sorted(
        function_scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    if not sorted_functions or sorted_functions[0][1]["score"] == 0:
        return FunctionClassification(
            primary_function="other",
            confidence=0.0,
            secondary_functions=[],
            classification_signals=["No clear function signals detected"]
        )

    primary = sorted_functions[0]
    total_score = sum(f[1]["score"] for f in sorted_functions if f[1]["score"] > 0)

    # Get secondary functions (score > 0, not primary)
    secondary = [
        f[0] for f in sorted_functions[1:4]
        if f[1]["score"] > 0 and f[1]["score"] >= primary[1]["score"] * 0.3
    ]

    return FunctionClassification(
        primary_function=primary[0],
        confidence=primary[1]["score"] / total_score if total_score > 0 else 0,
        secondary_functions=secondary,
        classification_signals=primary[1]["signals"][:5]
    )


def classify_role_function(jd_data: Dict[str, Any]) -> FunctionClassification:
    """
    Determine role's primary function based on job description.

    Args:
        jd_data: JD dictionary with role_title, responsibilities, description

    Returns:
        FunctionClassification with primary function and confidence
    """
    function_scores: Dict[str, Dict[str, Any]] = {}

    # Build combined text
    role_title = jd_data.get("role_title", "") or jd_data.get("title", "")
    description = jd_data.get("job_description", "") or jd_data.get("description", "")
    responsibilities = jd_data.get("responsibilities", [])

    if isinstance(responsibilities, list):
        resp_text = " ".join(responsibilities)
    else:
        resp_text = str(responsibilities) if responsibilities else ""

    jd_text = f"{role_title} {description} {resp_text}".lower()
    job_title_lower = role_title.lower()

    # Score each function
    for function_name, function_def in FUNCTION_TAXONOMY.items():
        score = 0.0
        signals_found = []
        title_matched = False

        # Check job title (highest weight = 15 points for exact match, 10 for partial)
        # Job title is THE primary signal - should dominate over body text signals
        for pattern in function_def["titles"]:
            if pattern in job_title_lower:
                # Higher weight for more specific matches
                if job_title_lower.startswith(pattern) or f" {pattern}" in job_title_lower:
                    score += 15.0  # Strong title match
                    signals_found.append(f"Job title match: {pattern}")
                else:
                    score += 10.0  # Partial title match
                    signals_found.append(f"Job title contains: {pattern}")
                title_matched = True
                break

        # Check for explicit function declaration (4 points)
        for pattern in function_def["titles"]:
            declaration_patterns = [
                f"this is a {pattern}",
                f"this is an {pattern}",
                f"role is a {pattern}",
                f"position is a {pattern}",
                f"seeking a {pattern}",
                f"looking for a {pattern}"
            ]
            for decl in declaration_patterns:
                if decl in jd_text:
                    score += 4.0
                    signals_found.append(f"Explicit declaration: {decl}")
                    break

        # Check for function signals in text (1 point per match, capped at 8)
        # Cap signal points so they can't overwhelm a clear title match
        signal_points = 0.0
        for signal in function_def["signals"]:
            if re.search(rf'\b{re.escape(signal)}\b', jd_text):
                if signal_points < 8.0:  # Cap at 8 points from signals
                    signal_points += 1.0
                    if len(signals_found) < 10:
                        signals_found.append(f"Signal: {signal}")
        score += signal_points

        function_scores[function_name] = {
            "score": score,
            "signals": signals_found
        }

    # Rank functions by score
    sorted_functions = sorted(
        function_scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    if not sorted_functions or sorted_functions[0][1]["score"] == 0:
        return FunctionClassification(
            primary_function="other",
            confidence=0.0,
            secondary_functions=[],
            classification_signals=["No clear function signals in JD"]
        )

    primary = sorted_functions[0]
    total_score = sum(f[1]["score"] for f in sorted_functions if f[1]["score"] > 0)

    return FunctionClassification(
        primary_function=primary[0],
        confidence=primary[1]["score"] / total_score if total_score > 0 else 0,
        secondary_functions=[],
        classification_signals=primary[1]["signals"][:5]
    )


def detect_function_mismatch(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    candidate_function_override: Optional[str] = None,
    role_function_override: Optional[str] = None
) -> FunctionMismatchResult:
    """
    Compare candidate function to role function and determine mismatch severity.

    Args:
        resume_data: Resume dictionary
        jd_data: JD dictionary
        candidate_function_override: Optional override for candidate function
        role_function_override: Optional override for role function

    Returns:
        FunctionMismatchResult with severity, score cap, and coaching
    """
    # Classify functions
    candidate_classification = classify_candidate_function(resume_data)
    role_classification = classify_role_function(jd_data)

    candidate_fn = candidate_function_override or candidate_classification.primary_function
    role_fn = role_function_override or role_classification.primary_function

    # Same function = no mismatch
    if candidate_fn == role_fn:
        return FunctionMismatchResult(
            is_mismatch=False,
            severity=MismatchSeverity.NONE,
            candidate_function=candidate_fn,
            role_function=role_fn,
            transferable_skills=[],
            score_cap=None,
            coaching_message=None,
            candidate_classification=candidate_classification,
            role_classification=role_classification
        )

    # "other" function = can't determine mismatch
    if candidate_fn == "other" or role_fn == "other":
        return FunctionMismatchResult(
            is_mismatch=False,
            severity=MismatchSeverity.NONE,
            candidate_function=candidate_fn,
            role_function=role_fn,
            transferable_skills=[],
            score_cap=None,
            coaching_message=None,
            candidate_classification=candidate_classification,
            role_classification=role_classification
        )

    # Check for defined adjacency (both directions)
    pair = (candidate_fn, role_fn)
    reverse_pair = (role_fn, candidate_fn)

    adjacency = ADJACENCY_MAP.get(pair) or ADJACENCY_MAP.get(reverse_pair)

    if adjacency:
        coaching = adjacency["coaching"].format(
            role_fn=_format_function_name(role_fn),
            candidate_fn=_format_function_name(candidate_fn)
        )

        return FunctionMismatchResult(
            is_mismatch=True,
            severity=adjacency["severity"],
            candidate_function=candidate_fn,
            role_function=role_fn,
            transferable_skills=adjacency["transferable"],
            score_cap=adjacency["score_cap"],
            coaching_message=coaching,
            candidate_classification=candidate_classification,
            role_classification=role_classification
        )

    # No defined adjacency = complete mismatch
    coaching = (
        f"This is a {_format_function_name(role_fn)} role, not a "
        f"{_format_function_name(candidate_fn)} role. Your background doesn't align "
        f"with the core responsibilities. Consider targeting roles within your function "
        f"or exploring structured career transition paths."
    )

    return FunctionMismatchResult(
        is_mismatch=True,
        severity=MismatchSeverity.COMPLETE,
        candidate_function=candidate_fn,
        role_function=role_fn,
        transferable_skills=[],
        score_cap=30,
        coaching_message=coaching,
        candidate_classification=candidate_classification,
        role_classification=role_classification
    )


def get_recommendation_for_mismatch(severity: MismatchSeverity, base_score: int) -> str:
    """
    Get appropriate recommendation based on mismatch severity.

    Args:
        severity: The mismatch severity level
        base_score: The uncapped fit score

    Returns:
        Recommendation string
    """
    if severity == MismatchSeverity.COMPLETE:
        return "Do Not Apply"
    elif severity == MismatchSeverity.SIGNIFICANT:
        return "Long Shot"
    elif severity == MismatchSeverity.ADJACENT:
        return "Conditional Apply" if base_score >= 45 else "Long Shot"
    else:
        return "Apply"  # No mismatch


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

def apply_function_mismatch_cap(
    fit_score: int,
    mismatch_result: FunctionMismatchResult
) -> Tuple[int, bool]:
    """
    Apply score cap if function mismatch detected.

    Args:
        fit_score: Original calculated fit score
        mismatch_result: Result from detect_function_mismatch

    Returns:
        Tuple of (capped_score, was_capped)
    """
    if not mismatch_result.is_mismatch or mismatch_result.score_cap is None:
        return fit_score, False

    if fit_score > mismatch_result.score_cap:
        return mismatch_result.score_cap, True

    return fit_score, False


def format_mismatch_for_response(mismatch_result: FunctionMismatchResult) -> Dict[str, Any]:
    """
    Format mismatch result for API response.

    Returns a dict suitable for including in the API response.
    """
    if not mismatch_result.is_mismatch:
        return {
            "detected": False,
            "candidate_function": mismatch_result.candidate_function,
            "role_function": mismatch_result.role_function
        }

    return mismatch_result.to_dict()
