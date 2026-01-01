"""
Resume Detection Systems - Phase 2

This module implements detection systems for:
1. Company credibility assessment
2. Title inflation detection
3. Career switcher recognition

These systems feed into the credibility scoring and provide honest assessment
to elite candidates about their positioning.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


# =============================================================================
# 1. COMPANY CREDIBILITY ASSESSMENT
# =============================================================================

class CompanyCredibility(Enum):
    """Company credibility levels."""
    STRONG = "strong"      # Public data available (press, funding, reviews)
    WEAK = "weak"          # Limited presence (website, LinkedIn)
    UNVERIFIABLE = "unverifiable"  # Cannot validate claims


@dataclass
class CompanyCredibilityResult:
    """Result of company credibility assessment."""
    company_name: str
    credibility: CompanyCredibility
    confidence: float
    signals: List[str]
    discount: int  # Percentage discount applied to fit score

    def to_dict(self) -> dict:
        return {
            "company": self.company_name,
            "credibility": self.credibility.value,
            "confidence": self.confidence,
            "signals": self.signals,
            "score_discount": self.discount
        }


# Well-known companies that automatically get STRONG credibility
KNOWN_COMPANIES = {
    # FAANG/MAANG
    "google", "alphabet", "meta", "facebook", "amazon", "aws", "apple",
    "microsoft", "netflix",
    # Major tech
    "stripe", "plaid", "square", "block", "paypal", "shopify", "salesforce",
    "adobe", "oracle", "ibm", "intel", "nvidia", "amd", "cisco", "vmware",
    "snowflake", "databricks", "datadog", "mongodb", "elastic", "splunk",
    "twilio", "zendesk", "hubspot", "slack", "zoom", "dropbox", "box",
    "pinterest", "twitter", "x", "linkedin", "snap", "tiktok", "bytedance",
    "uber", "lyft", "doordash", "instacart", "airbnb", "booking",
    "coinbase", "robinhood", "affirm", "klarna", "chime", "nubank",
    "figma", "canva", "notion", "asana", "monday", "atlassian", "jira",
    "github", "gitlab", "hashicorp", "docker", "kubernetes",
    # Major consulting/finance
    "mckinsey", "bain", "bcg", "deloitte", "accenture", "pwc", "ey", "kpmg",
    "goldman sachs", "morgan stanley", "jpmorgan", "jp morgan", "chase",
    "bank of america", "citibank", "citi", "wells fargo", "blackrock",
    "blackstone", "kkr", "carlyle", "tpg", "sequoia", "andreessen",
    "a16z", "benchmark", "greylock", "kleiner", "bessemer",
    # Fortune 500 / Major corps
    "walmart", "target", "costco", "home depot", "cvs", "walgreens",
    "johnson & johnson", "pfizer", "merck", "abbvie", "bristol-myers",
    "united health", "kaiser", "anthem", "cigna", "humana",
    "exxon", "chevron", "conocophillips", "bp", "shell",
    "boeing", "lockheed", "raytheon", "northrop", "general dynamics",
    "general electric", "ge", "honeywell", "3m", "caterpillar", "deere",
    "ford", "gm", "general motors", "toyota", "honda", "tesla",
    "disney", "warner", "paramount", "comcast", "nbc", "fox", "viacom",
    "at&t", "verizon", "t-mobile", "sprint",
    # Hot startups (Series C+)
    "openai", "anthropic", "cohere", "stability", "midjourney",
    "vercel", "supabase", "railway", "render", "fly.io",
    "retool", "airtable", "coda", "webflow", "framer",
    "rippling", "gusto", "deel", "remote", "oyster",
    "loom", "calendly", "typeform", "survey monkey",
    "postman", "insomnia", "kong", "mulesoft",
}

# Patterns that indicate consulting/agency work
CONSULTING_PATTERNS = [
    r"consulting",
    r"consultancy",
    r"solutions",
    r"services",
    r"partners",
    r"advisors",
    r"group llc",
    r"group inc",
    r"associates",
    r"freelance",
    r"self-employed",
    r"independent",
    r"contractor",
]


def assess_company_credibility(
    company_name: str,
    title: str = "",
    bullets: List[str] = None
) -> CompanyCredibilityResult:
    """
    Assess credibility of a company based on name and context.

    Returns credibility level and score discount.
    """
    if bullets is None:
        bullets = []

    company_lower = company_name.lower().strip()
    signals = []

    # Check if known company
    for known in KNOWN_COMPANIES:
        if known in company_lower or company_lower in known:
            signals.append(f"Recognized company: {company_name}")
            return CompanyCredibilityResult(
                company_name=company_name,
                credibility=CompanyCredibility.STRONG,
                confidence=0.95,
                signals=signals,
                discount=0
            )

    # Check for consulting/agency patterns
    for pattern in CONSULTING_PATTERNS:
        if re.search(pattern, company_lower):
            signals.append(f"Consulting/agency pattern detected: {pattern}")
            # Consulting is not bad, but requires more scrutiny
            return CompanyCredibilityResult(
                company_name=company_name,
                credibility=CompanyCredibility.WEAK,
                confidence=0.7,
                signals=signals,
                discount=10
            )

    # Check for scope signals in bullets that validate credibility
    scope_signals = []
    for bullet in bullets:
        # Look for specific numbers that suggest real scale
        if re.search(r'\$\d+[MBK]', bullet):
            scope_signals.append("Revenue/budget mentioned")
        if re.search(r'\d+[MK]?\+?\s*(users|customers)', bullet, re.IGNORECASE):
            scope_signals.append("User/customer scale mentioned")
        if re.search(r'\d+[\-\s]*(person|people|engineer|report)', bullet, re.IGNORECASE):
            scope_signals.append("Team size mentioned")

    if scope_signals:
        signals.extend(scope_signals)
        # Scope signals increase credibility
        return CompanyCredibilityResult(
            company_name=company_name,
            credibility=CompanyCredibility.WEAK,
            confidence=0.6,
            signals=signals,
            discount=10
        )

    # Default: Unverifiable
    signals.append("Company not recognized, no scope signals found")
    return CompanyCredibilityResult(
        company_name=company_name,
        credibility=CompanyCredibility.UNVERIFIABLE,
        confidence=0.4,
        signals=signals,
        discount=20
    )


def assess_all_companies(resume: dict) -> Dict[str, Any]:
    """
    Assess credibility of all companies in resume.
    Returns aggregate assessment and per-company details.
    """
    results = []
    total_discount = 0

    for role in resume.get("experience", []):
        company = role.get("company", "Unknown")
        title = role.get("title", "")
        bullets = role.get("bullets", [])

        result = assess_company_credibility(company, title, bullets)
        results.append(result.to_dict())

        # Most recent role has highest weight on discount
        if len(results) == 1:
            total_discount = result.discount
        else:
            # Later roles have diminishing weight
            total_discount = max(total_discount, result.discount * 0.5)

    # Determine overall credibility
    credibilities = [r["credibility"] for r in results]
    if all(c == "strong" for c in credibilities):
        overall = "strong"
    elif any(c == "unverifiable" for c in credibilities):
        overall = "mixed"
    else:
        overall = "weak"

    return {
        "overall_credibility": overall,
        "score_discount": int(total_discount),
        "companies": results
    }


# =============================================================================
# 2. TITLE INFLATION DETECTION
# =============================================================================

class TitleInflation(Enum):
    """Title inflation levels."""
    NONE = "none"          # Title matches evidence
    MINOR = "minor"        # Slight mismatch
    SIGNIFICANT = "significant"  # Major mismatch


@dataclass
class TitleInflationResult:
    """Result of title inflation detection."""
    title: str
    company: str
    inflation_level: TitleInflation
    expected_level: str
    evidence: List[str]
    confidence: float

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "inflation_level": self.inflation_level.value,
            "expected_level": self.expected_level,
            "evidence": self.evidence,
            "confidence": self.confidence
        }


# Title level hierarchy
TITLE_LEVELS = {
    # Individual Contributors
    "associate": 1,
    "junior": 1,
    "entry": 1,
    "analyst": 2,
    "specialist": 2,
    "coordinator": 2,
    "": 3,  # Default/no prefix
    "senior": 4,
    "lead": 5,
    "staff": 5,
    "principal": 6,
    "distinguished": 7,
    "fellow": 8,
    # Managers
    "manager": 4,
    "senior manager": 5,
    "director": 6,
    "senior director": 7,
    "vp": 8,
    "vice president": 8,
    "svp": 9,
    "senior vice president": 9,
    "evp": 10,
    "executive vice president": 10,
    "chief": 11,
    "c-suite": 11,
    "ceo": 11,
    "cto": 11,
    "cfo": 11,
    "coo": 11,
    "cpo": 11,
    "cmo": 11,
}

# Evidence patterns for different levels
LEVEL_EVIDENCE = {
    1: {
        "team_size": 0,
        "budget": 0,
        "reports": 0,
        "ownership_verbs": ["supported", "assisted", "helped", "contributed"],
    },
    2: {
        "team_size": 0,
        "budget": 0,
        "reports": 0,
        "ownership_verbs": ["executed", "implemented", "completed", "managed"],
    },
    3: {
        "team_size": 0,
        "budget": 0,
        "reports": (0, 3),
        "ownership_verbs": ["owned", "led", "built", "drove"],
    },
    4: {
        "team_size": (3, 10),
        "budget": (0, 1000000),
        "reports": (1, 5),
        "ownership_verbs": ["led", "owned", "defined", "established"],
    },
    5: {
        "team_size": (5, 20),
        "budget": (500000, 5000000),
        "reports": (3, 10),
        "ownership_verbs": ["led", "drove", "architected", "established", "scaled"],
    },
    6: {
        "team_size": (10, 50),
        "budget": (1000000, 20000000),
        "reports": (5, 20),
        "ownership_verbs": ["led", "drove", "defined strategy", "transformed"],
    },
    7: {
        "team_size": (20, 100),
        "budget": (5000000, 50000000),
        "reports": (10, 50),
        "ownership_verbs": ["led org", "defined vision", "transformed", "built organization"],
    },
    8: {
        "team_size": (50, 500),
        "budget": (10000000, 200000000),
        "reports": (20, 100),
        "ownership_verbs": ["led function", "drove company strategy", "p&l ownership"],
    },
}


def extract_title_level(title: str) -> Tuple[int, str]:
    """Extract level from title string."""
    title_lower = title.lower()

    # Check for explicit level markers
    for marker, level in sorted(TITLE_LEVELS.items(), key=lambda x: -len(x[0])):
        if marker and marker in title_lower:
            return level, marker

    return 3, ""  # Default mid-level


def extract_evidence_level(bullets: List[str]) -> Tuple[int, List[str]]:
    """
    Extract implied level from bullet point evidence.
    Returns (level, evidence_list).
    """
    evidence = []
    max_team_size = 0
    max_budget = 0
    ownership_signals = []

    for bullet in bullets:
        bullet_lower = bullet.lower()

        # Extract team size
        team_match = re.search(r'(\d+)[\-\s]*(person|people|engineer|member|report|team)', bullet, re.IGNORECASE)
        if team_match:
            size = int(team_match.group(1))
            max_team_size = max(max_team_size, size)
            evidence.append(f"Team size: {size}")

        # Extract budget
        budget_match = re.search(r'\$(\d+(?:\.\d+)?)\s*([MBK])?', bullet)
        if budget_match:
            amount = float(budget_match.group(1))
            multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(budget_match.group(2), 1)
            budget = amount * multiplier
            max_budget = max(max_budget, budget)
            evidence.append(f"Budget: ${budget_match.group(0)}")

        # Check ownership verbs
        for level, level_data in LEVEL_EVIDENCE.items():
            for verb in level_data.get("ownership_verbs", []):
                if verb in bullet_lower:
                    ownership_signals.append((level, verb))

    # Determine level from evidence
    implied_level = 3  # Default

    if max_team_size >= 50:
        implied_level = max(implied_level, 8)
    elif max_team_size >= 20:
        implied_level = max(implied_level, 7)
    elif max_team_size >= 10:
        implied_level = max(implied_level, 6)
    elif max_team_size >= 5:
        implied_level = max(implied_level, 5)
    elif max_team_size >= 3:
        implied_level = max(implied_level, 4)

    if max_budget >= 10000000:
        implied_level = max(implied_level, 8)
    elif max_budget >= 5000000:
        implied_level = max(implied_level, 7)
    elif max_budget >= 1000000:
        implied_level = max(implied_level, 6)

    if ownership_signals:
        highest_ownership = max(o[0] for o in ownership_signals)
        implied_level = max(implied_level, highest_ownership)

    return implied_level, evidence


def detect_title_inflation(
    title: str,
    company: str,
    bullets: List[str]
) -> TitleInflationResult:
    """
    Detect if title is inflated relative to evidence in bullets.
    """
    claimed_level, level_marker = extract_title_level(title)
    evidence_level, evidence = extract_evidence_level(bullets)

    gap = claimed_level - evidence_level

    if gap <= 0:
        inflation = TitleInflation.NONE
        expected = title
        confidence = 0.9
    elif gap == 1:
        inflation = TitleInflation.MINOR
        expected = f"Evidence suggests {level_marker} level or slightly below"
        confidence = 0.7
    else:
        inflation = TitleInflation.SIGNIFICANT
        expected = f"Evidence suggests level {evidence_level}, but title claims level {claimed_level}"
        confidence = 0.8

    if not bullets:
        # Can't assess without evidence
        inflation = TitleInflation.NONE
        expected = "Insufficient evidence to assess"
        confidence = 0.3
        evidence = ["No bullet points provided"]

    return TitleInflationResult(
        title=title,
        company=company,
        inflation_level=inflation,
        expected_level=expected,
        evidence=evidence,
        confidence=confidence
    )


def detect_all_title_inflation(resume: dict) -> Dict[str, Any]:
    """
    Detect title inflation across all roles in resume.
    """
    results = []
    inflation_count = 0

    for role in resume.get("experience", []):
        title = role.get("title", "")
        company = role.get("company", "Unknown")
        bullets = role.get("bullets", [])

        result = detect_title_inflation(title, company, bullets)
        results.append(result.to_dict())

        if result.inflation_level != TitleInflation.NONE:
            inflation_count += 1

    return {
        "inflation_detected": inflation_count > 0,
        "inflated_role_count": inflation_count,
        "total_roles": len(results),
        "roles": results
    }


# =============================================================================
# 3. CAREER SWITCHER RECOGNITION
# =============================================================================

class ExperienceType(Enum):
    """Type of experience evidence."""
    DIRECT = "direct"      # Full ownership: "Owned roadmap", "Defined strategy"
    ADJACENT = "adjacent"  # Supporting role: "Supported PM team", "Contributed to"
    EXPOSURE = "exposure"  # Observer only: "Participated in", "Familiar with"


@dataclass
class CareerSwitcherResult:
    """Result of career switcher detection."""
    is_switcher: bool
    source_function: str
    target_function: str
    experience_breakdown: Dict[str, float]  # DIRECT/ADJACENT/EXPOSURE percentages
    confidence: float
    recommendation: str

    def to_dict(self) -> dict:
        return {
            "is_career_switcher": self.is_switcher,
            "source_function": self.source_function,
            "target_function": self.target_function,
            "experience_breakdown": self.experience_breakdown,
            "confidence": self.confidence,
            "recommendation": self.recommendation
        }


# Function keywords
FUNCTION_KEYWORDS = {
    "product_management": [
        "product manager", "product lead", "product owner", "pm",
        "roadmap", "product strategy", "product vision", "user stories",
        "product requirements", "prd", "backlog", "sprint planning",
        "product discovery", "product analytics", "product metrics",
    ],
    "engineering": [
        "software engineer", "developer", "sde", "swe", "programmer",
        "architecture", "code review", "technical design", "api",
        "database", "backend", "frontend", "full stack", "devops",
        "ci/cd", "testing", "debugging", "performance optimization",
    ],
    "design": [
        "designer", "ux", "ui", "user experience", "user interface",
        "design system", "prototyping", "wireframe", "figma", "sketch",
        "user research", "usability testing", "visual design",
    ],
    "marketing": [
        "marketing manager", "marketing lead", "brand", "campaign",
        "content marketing", "demand generation", "growth marketing",
        "seo", "sem", "paid media", "social media", "email marketing",
        "marketing analytics", "conversion", "funnel",
    ],
    "sales": [
        "sales", "account executive", "ae", "sdr", "bdr",
        "quota", "pipeline", "deals", "revenue", "bookings",
        "sales cycle", "closing", "prospecting", "negotiation",
    ],
    "operations": [
        "operations", "ops", "process", "efficiency", "workflow",
        "supply chain", "logistics", "vendor management",
        "business operations", "operational excellence",
    ],
    "data": [
        "data scientist", "data analyst", "data engineer", "ml engineer",
        "machine learning", "analytics", "statistical analysis",
        "data pipeline", "etl", "data modeling", "visualization",
    ],
}

# Direct ownership patterns
DIRECT_PATTERNS = [
    r"\b(owned|led|defined|built|shipped|launched|drove|architected)\b",
    r"\b(p&l|profit.?loss|revenue.?owner|budget.?owner)\b",
    r"\b(decision.?maker|final.?say|approved|vetoed)\b",
]

# Adjacent/supporting patterns
ADJACENT_PATTERNS = [
    r"\b(supported|contributed|collaborated|partnered|worked with)\b",
    r"\b(assisted|helped|facilitated|coordinated)\b",
    r"\b(part of|member of|joined)\b",
]

# Exposure/observer patterns
EXPOSURE_PATTERNS = [
    r"\b(participated|attended|observed|shadowed)\b",
    r"\b(exposure to|familiar with|knowledge of|understanding of)\b",
    r"\b(learned|trained|certified)\b",
]


def detect_function_from_text(text: str) -> str:
    """Detect primary function from text."""
    text_lower = text.lower()

    function_scores = {}
    for function, keywords in FUNCTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            function_scores[function] = score

    if function_scores:
        return max(function_scores, key=function_scores.get)
    return "unknown"


def classify_experience_type(bullet: str) -> ExperienceType:
    """Classify a bullet point as DIRECT, ADJACENT, or EXPOSURE."""
    bullet_lower = bullet.lower()

    # Check patterns in order of strength
    for pattern in DIRECT_PATTERNS:
        if re.search(pattern, bullet_lower):
            return ExperienceType.DIRECT

    for pattern in ADJACENT_PATTERNS:
        if re.search(pattern, bullet_lower):
            return ExperienceType.ADJACENT

    for pattern in EXPOSURE_PATTERNS:
        if re.search(pattern, bullet_lower):
            return ExperienceType.EXPOSURE

    # Default to ADJACENT if no clear pattern
    return ExperienceType.ADJACENT


def detect_career_switcher(
    resume: dict,
    target_function: str
) -> CareerSwitcherResult:
    """
    Detect if candidate is a career switcher trying to enter target_function.

    Returns breakdown of DIRECT/ADJACENT/EXPOSURE experience in target function.
    """
    target_lower = target_function.lower()
    target_keywords = FUNCTION_KEYWORDS.get(target_lower, [])

    # If no keywords for target, try to match partial
    if not target_keywords:
        for func, keywords in FUNCTION_KEYWORDS.items():
            if target_lower in func or func in target_lower:
                target_keywords = keywords
                break

    # Analyze each bullet for target function experience
    direct_count = 0
    adjacent_count = 0
    exposure_count = 0
    total_target_bullets = 0

    all_bullets = []
    for role in resume.get("experience", []):
        bullets = role.get("bullets", [])
        all_bullets.extend(bullets)

    for bullet in all_bullets:
        bullet_lower = bullet.lower()

        # Check if bullet relates to target function
        is_target_related = any(kw in bullet_lower for kw in target_keywords)

        if is_target_related:
            total_target_bullets += 1
            exp_type = classify_experience_type(bullet)

            if exp_type == ExperienceType.DIRECT:
                direct_count += 1
            elif exp_type == ExperienceType.ADJACENT:
                adjacent_count += 1
            else:
                exposure_count += 1

    # Detect source function from most common signals
    all_text = " ".join(all_bullets)
    source_function = detect_function_from_text(all_text)

    # Calculate percentages
    total = max(total_target_bullets, 1)
    breakdown = {
        "direct": round(direct_count / total * 100, 1),
        "adjacent": round(adjacent_count / total * 100, 1),
        "exposure": round(exposure_count / total * 100, 1),
    }

    # Determine if career switcher
    is_switcher = False
    recommendation = ""
    confidence = 0.5

    if source_function != target_lower and source_function != "unknown":
        if breakdown["direct"] < 30:
            is_switcher = True
            if breakdown["direct"] < 10:
                recommendation = f"Career switch from {source_function} to {target_function} detected. Direct {target_function} experience is minimal. Consider highlighting transferable skills and seeking stepping stone roles."
                confidence = 0.85
            else:
                recommendation = f"Transitioning from {source_function} to {target_function}. Some direct experience exists. Emphasize direct ownership bullets and de-emphasize observer language."
                confidence = 0.7
        else:
            recommendation = f"Has meaningful {target_function} experience despite {source_function} background. Position as hybrid/cross-functional strength."
            confidence = 0.75
    else:
        recommendation = f"Primary experience aligns with {target_function}. Not a career switcher."
        confidence = 0.9

    return CareerSwitcherResult(
        is_switcher=is_switcher,
        source_function=source_function,
        target_function=target_function,
        experience_breakdown=breakdown,
        confidence=confidence,
        recommendation=recommendation
    )


# =============================================================================
# MAIN DETECTION FUNCTION
# =============================================================================

def run_all_detections(
    resume: dict,
    target_function: str = "product_management"
) -> Dict[str, Any]:
    """
    Run all detection systems on a resume.
    Returns comprehensive detection results.
    """
    # 1. Company credibility
    company_assessment = assess_all_companies(resume)

    # 2. Title inflation
    title_assessment = detect_all_title_inflation(resume)

    # 3. Career switcher
    switcher_assessment = detect_career_switcher(resume, target_function)

    # Calculate combined credibility impact
    total_discount = company_assessment["score_discount"]

    if title_assessment["inflation_detected"]:
        # Significant inflation adds 10-15% discount
        inflated_roles = title_assessment["inflated_role_count"]
        total_roles = max(title_assessment["total_roles"], 1)
        inflation_ratio = inflated_roles / total_roles
        inflation_discount = int(inflation_ratio * 15)
        total_discount += inflation_discount

    if switcher_assessment.is_switcher:
        # Career switcher with low direct experience adds discount
        direct_pct = switcher_assessment.experience_breakdown.get("direct", 0)
        if direct_pct < 20:
            total_discount += 15
        elif direct_pct < 40:
            total_discount += 10

    # Cap total discount at 40%
    total_discount = min(total_discount, 40)

    return {
        "company_credibility": company_assessment,
        "title_inflation": title_assessment,
        "career_switcher": switcher_assessment.to_dict(),
        "combined_score_discount": total_discount,
        "detection_summary": {
            "has_credibility_concerns": company_assessment["overall_credibility"] != "strong",
            "has_title_inflation": title_assessment["inflation_detected"],
            "is_career_switcher": switcher_assessment.is_switcher,
        }
    }
