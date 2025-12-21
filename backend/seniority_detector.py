# ============================================================================
# SENIORITY DETECTION MODULE
# Per HenryHQ Implementation Guide (Dec 21, 2025)
#
# PURPOSE: Classify candidate seniority for appropriate coaching depth.
#
# TIERS:
# - executive: VP+, C-suite, President, Head of
# - director: Director-level titles
# - manager: Manager, Lead, Principal, Staff titles
# - ic: Individual contributor (default)
#
# GUIDANCE RULES BY TIER:
# - Executive: Leverage strategy, narrative framing, relationship guidance
# - Director: Positioning + gap mitigation, selective tactical advice
# - Manager: Resume focus, gap mitigation, networking strategy
# - IC: Full tactical guidance, resume/skills/outreach
#
# ============================================================================

from typing import Dict, Any, List, Optional


# ============================================================================
# SENIORITY DETECTION PATTERNS
# ============================================================================

# VP+ / Executive detection patterns
EXECUTIVE_PATTERNS = [
    "vp", "vice president", "svp", "evp", "avp",
    "ceo", "cfo", "cto", "cmo", "coo", "cpo", "cro", "ciso",
    "president", "chief", "head of",
    "general manager", "managing director", "gm",
    "partner", "principal" # In consulting/finance
]

# Director-level patterns
DIRECTOR_PATTERNS = [
    "director", "sr director", "senior director",
    "associate director"
]

# Manager-level patterns
MANAGER_PATTERNS = [
    "manager", "lead", "principal", "staff",
    "senior", "sr.", "team lead", "tech lead",
    "engineering manager", "product manager",
    "program manager", "project manager",
    "group manager"
]

# Patterns that indicate org-level scope (for executive detection refinement)
ORG_SCOPE_PATTERNS = [
    "p&l", "profit and loss", "budget authority",
    "board", "c-suite", "executive team",
    "org", "organization", "division",
    "region", "global", "enterprise"
]


# ============================================================================
# SENIORITY DETECTION FUNCTIONS
# ============================================================================

def detect_candidate_seniority(resume_data: Dict[str, Any]) -> str:
    """
    Classify candidate seniority for appropriate coaching depth.

    Detection hierarchy:
    1. Executive: VP+, C-suite, President, Head of
    2. Director: Director-level titles
    3. Manager: Manager, Lead, Principal, Staff titles
    4. IC: Individual contributor (default)

    Args:
        resume_data: Parsed resume data with experience list

    Returns:
        str: 'executive', 'director', 'manager', or 'ic'
    """
    titles: List[str] = []
    for exp in resume_data.get("experience", []):
        title = (exp.get("title") or "").lower()
        if title:
            titles.append(title)

    # Check for executive patterns first (highest tier)
    for title in titles:
        for pattern in EXECUTIVE_PATTERNS:
            if pattern in title:
                return "executive"

    # Check for director patterns
    for title in titles:
        for pattern in DIRECTOR_PATTERNS:
            if pattern in title:
                return "director"

    # Check for manager patterns
    for title in titles:
        for pattern in MANAGER_PATTERNS:
            if pattern in title:
                return "manager"

    return "ic"


def detect_highest_seniority_held(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect the highest seniority level ever held by the candidate.

    Useful for understanding career trajectory and appropriate guidance.

    Args:
        resume_data: Parsed resume data

    Returns:
        dict with:
        - tier: 'executive', 'director', 'manager', or 'ic'
        - title: The actual title that triggered the classification
        - company: Company where this title was held
        - years_at_level: Approximate years at this level
    """
    highest_tier = "ic"
    highest_title = ""
    highest_company = ""
    tier_priority = {"executive": 4, "director": 3, "manager": 2, "ic": 1}

    for exp in resume_data.get("experience", []):
        title = (exp.get("title") or "").lower()
        company = exp.get("company", "")

        if not title:
            continue

        current_tier = "ic"

        # Check executive patterns
        for pattern in EXECUTIVE_PATTERNS:
            if pattern in title:
                current_tier = "executive"
                break

        # Check director patterns (only if not already executive)
        if current_tier == "ic":
            for pattern in DIRECTOR_PATTERNS:
                if pattern in title:
                    current_tier = "director"
                    break

        # Check manager patterns (only if not already higher)
        if current_tier == "ic":
            for pattern in MANAGER_PATTERNS:
                if pattern in title:
                    current_tier = "manager"
                    break

        # Update highest if this is higher
        if tier_priority.get(current_tier, 0) > tier_priority.get(highest_tier, 0):
            highest_tier = current_tier
            highest_title = exp.get("title", "")
            highest_company = company

    return {
        "tier": highest_tier,
        "title": highest_title,
        "company": highest_company,
        "tier_priority": tier_priority.get(highest_tier, 1)
    }


# ============================================================================
# SENIORITY-SPECIFIC GUIDANCE RULES
# ============================================================================

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
        ),
        "tone": "strategic",
        "detail_level": "high-level"
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
        ),
        "tone": "confident",
        "detail_level": "moderate"
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
        ),
        "tone": "practical",
        "detail_level": "detailed"
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
        ),
        "tone": "supportive",
        "detail_level": "step-by-step"
    }
}


def get_seniority_appropriate_guidance(
    seniority: str,
    role_title: str,
    primary_strength: str,
    top_gap: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate seniority-appropriate guidance that respects the candidate's level.

    Args:
        seniority: 'executive', 'director', 'manager', or 'ic'
        role_title: The role being applied for
        primary_strength: Candidate's strongest relevant attribute
        top_gap: Optional top gap to address

    Returns:
        dict with keys: your_move, allowed_content, banned_content, tone, detail_level
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
        "seniority_tier": seniority,
        "tone": rules["tone"],
        "detail_level": rules["detail_level"]
    }


def get_seniority_fallback_your_move(
    seniority: str,
    role_title: str,
    recommendation: str
) -> str:
    """
    Get a deterministic fallback Your Move message for a given seniority tier.

    This ensures Your Move is NEVER empty.

    Args:
        seniority: 'executive', 'director', 'manager', or 'ic'
        role_title: The role being applied for
        recommendation: The recommendation tier

    Returns:
        str: Fallback Your Move message (guaranteed non-empty)
    """
    fallbacks = {
        "executive": (
            f"Your executive experience positions you for {role_title}. "
            f"Lead with your most senior accomplishments and reach out directly to the hiring executive."
        ),
        "director": (
            f"Your leadership track record aligns with {role_title}. "
            f"Emphasize team-level outcomes and cross-functional wins in your outreach."
        ),
        "manager": (
            f"Position your management experience for {role_title}. "
            f"Lead with quantified team outcomes. Apply and reach out to the hiring manager."
        ),
        "ic": (
            f"Your technical background aligns with {role_title}. "
            f"Lead with your strongest project outcomes. Apply now and follow up on LinkedIn."
        )
    }

    return fallbacks.get(seniority, fallbacks["ic"])


def should_show_guidance_type(
    guidance_type: str,
    seniority: str
) -> bool:
    """
    Check if a specific guidance type should be shown to this seniority tier.

    Args:
        guidance_type: Type of guidance to check
        seniority: Candidate seniority tier

    Returns:
        bool: True if this guidance type is appropriate
    """
    rules = SENIORITY_GUIDANCE_RULES.get(seniority, SENIORITY_GUIDANCE_RULES["ic"])

    # If explicitly allowed, show
    if guidance_type in rules["allowed"]:
        return True

    # If explicitly banned, hide
    if guidance_type in rules["banned"]:
        return False

    # Default: show for manager and IC, hide for executive/director
    if seniority in ["executive", "director"]:
        return False
    return True


# ============================================================================
# TRANSITION CANDIDATE DETECTION
# ============================================================================

def detect_transition_candidate(
    resume_data: Dict[str, Any],
    target_role_type: str
) -> Dict[str, Any]:
    """
    Detect if this is a transition candidate (career changer).

    Transition candidates need different guidance:
    - More encouraging framing
    - Focus on transferable skills
    - Acknowledge the transition directly

    Args:
        resume_data: Parsed resume data
        target_role_type: The type of role being applied for

    Returns:
        dict with:
        - is_transition: bool
        - transition_type: 'career_change', 'function_change', 'industry_change', or None
        - source_domain: Previous domain/function
        - target_domain: Target domain/function
        - adjacency_score: 0.0-1.0 (how related are the domains)
    """
    # Extract current/most recent role
    experience = resume_data.get("experience", [])
    if not experience:
        return {
            "is_transition": False,
            "transition_type": None,
            "source_domain": None,
            "target_domain": target_role_type,
            "adjacency_score": 0.0
        }

    # Get most recent title and domain
    most_recent = experience[0] if experience else {}
    recent_title = (most_recent.get("title") or "").lower()

    # Detect source domain from title
    source_domain = _detect_domain_from_title(recent_title)

    # Check for career change patterns
    career_change_patterns = {
        # Clinical/Healthcare to Product
        ("clinical", "product"): {
            "type": "career_change",
            "adjacency": 0.35,
            "framing": "You're not unqualified. You're early. Healthcare → consumer PM is a pivot, not a stretch."
        },
        ("nursing", "product"): {
            "type": "career_change",
            "adjacency": 0.35,
            "framing": "You're not unqualified. You're early. Clinical → PM requires demonstrated product thinking."
        },
        # Operations to Product (common pivot)
        ("operations", "product"): {
            "type": "career_change",
            "adjacency": 0.45,
            "framing": "Operations to product is possible but requires demonstrated product thinking and user empathy."
        },
        # Government to Tech
        ("government", "engineering"): {
            "type": "industry_change",
            "adjacency": 0.3,
            "framing": "Government tech experience translates well to private sector."
        },
        ("government", "product"): {
            "type": "career_change",
            "adjacency": 0.5,
            "framing": "Program management skills are highly transferable to product management."
        },
        # Retail/Operations to Tech
        ("retail", "engineering"): {
            "type": "career_change",
            "adjacency": 0.2,
            "framing": "Non-traditional paths are valued at companies that prioritize grit and learning."
        },
        ("retail", "product"): {
            "type": "career_change",
            "adjacency": 0.3,
            "framing": "Retail operations experience needs strong product portfolio to bridge the gap."
        },
        # Program Management to Product
        ("program_management", "product"): {
            "type": "function_change",
            "adjacency": 0.6,
            "framing": "Program management to product is a common and viable transition."
        },
        # Marketing to Product
        ("marketing", "product"): {
            "type": "function_change",
            "adjacency": 0.55,
            "framing": "Marketing to product is achievable - lead with growth/analytics experience."
        },
        # Finance/Consulting to Product
        ("finance", "product"): {
            "type": "career_change",
            "adjacency": 0.4,
            "framing": "Finance to product requires demonstrated product sense and user research."
        },
        ("consulting", "product"): {
            "type": "function_change",
            "adjacency": 0.55,
            "framing": "Consulting to product is common - lead with client problem-solving experience."
        }
    }

    # Check for matches
    for (source, target), config in career_change_patterns.items():
        if source in source_domain and target in target_role_type.lower():
            return {
                "is_transition": True,
                "transition_type": config["type"],
                "source_domain": source_domain,
                "target_domain": target_role_type,
                "adjacency_score": config["adjacency"],
                "framing": config["framing"]
            }

    # Default: not a transition candidate
    return {
        "is_transition": False,
        "transition_type": None,
        "source_domain": source_domain,
        "target_domain": target_role_type,
        "adjacency_score": 1.0  # Assumed same domain
    }


def _detect_domain_from_title(title: str) -> str:
    """Detect the domain/function from a job title."""
    title_lower = title.lower()

    domain_patterns = {
        "engineering": ["engineer", "developer", "swe", "programmer", "architect", "software"],
        "product": ["product manager", "pm", "product owner", "product lead"],
        "program_management": ["program manager", "project manager", "tpm", "pmo"],
        "design": ["designer", "ux", "ui", "creative"],
        "clinical": ["nurse", "rn", "clinical", "physician", "doctor", "therapist", "healthcare", "medical"],
        "nursing": ["nurse", "rn", "lpn", "cna"],
        "government": ["gs-", "federal", "government", "gsa", "dhs", "dod"],
        "retail": ["retail", "store manager", "sales associate"],
        "operations": ["operations manager", "operations director", "ops manager", "logistics"],
        "consulting": ["consultant", "advisor", "strategy"],
        "finance": ["analyst", "finance", "accounting", "fp&a"],
        "marketing": ["marketing", "growth", "brand", "content"],
        "sales": ["sales", "account executive", "business development", "bd"]
    }

    for domain, patterns in domain_patterns.items():
        for pattern in patterns:
            if pattern in title_lower:
                return domain

    return "unknown"


# ============================================================================
# CAREER TRANSITION DECISION MODIFIER
# ============================================================================

def get_transition_adjusted_decision(
    base_decision: str,
    score: int,
    transition_info: Dict[str, Any],
    has_referral: bool = False
) -> Dict[str, Any]:
    """
    Adjust recommendation based on career transition type.

    For career pivot candidates with marginal scores:
    - Downgrade to more honest recommendation
    - A 45% fit for a career changer isn't "Apply with Caution"
    - It's "Long Shot" - be honest about the gap

    Args:
        base_decision: The initial recommendation
        score: Fit score (0-100)
        transition_info: Result from detect_transition_candidate()
        has_referral: Whether candidate has an inside connection

    Returns:
        dict with:
        - adjusted_decision: The (possibly) modified recommendation
        - was_adjusted: bool
        - adjustment_reason: str or None
    """
    # No adjustment needed if not a transition candidate
    if not transition_info.get("is_transition"):
        return {
            "adjusted_decision": base_decision,
            "was_adjusted": False,
            "adjustment_reason": None
        }

    transition_type = transition_info.get("transition_type")
    adjacency = transition_info.get("adjacency_score", 1.0)

    # Career changers with low adjacency (<0.5) and marginal scores need honest guidance
    if transition_type == "career_change" and adjacency < 0.5:
        # Score below 55 + career pivot = Long Shot or Do Not Apply
        if score < 55 and base_decision in ["Apply with Caution", "Consider"]:
            if has_referral:
                # Referral softens the penalty slightly
                return {
                    "adjusted_decision": "Apply with Caution",
                    "was_adjusted": base_decision != "Apply with Caution",
                    "adjustment_reason": "Career pivot with referral - proceed with strong positioning"
                }
            else:
                # No referral + career change + marginal score = Long Shot
                return {
                    "adjusted_decision": "Long Shot",
                    "was_adjusted": True,
                    "adjustment_reason": f"Career pivot ({transition_info.get('source_domain')} → {transition_info.get('target_domain')}) with {score}% fit requires inside connection"
                }

        # Score below 40 + career pivot = Do Not Apply
        if score < 40:
            return {
                "adjusted_decision": "Do Not Apply",
                "was_adjusted": base_decision != "Do Not Apply",
                "adjustment_reason": f"Fundamental domain mismatch - consider entry-level roles in target field"
            }

    # Function changes (adjacent moves) - less severe penalty
    if transition_type == "function_change" and adjacency >= 0.5:
        # These are stretch roles, not pivots - base decision is usually appropriate
        return {
            "adjusted_decision": base_decision,
            "was_adjusted": False,
            "adjustment_reason": None
        }

    # Industry change - moderate penalty for low scores
    if transition_type == "industry_change" and score < 50:
        if base_decision in ["Apply with Caution", "Consider"] and not has_referral:
            return {
                "adjusted_decision": "Long Shot",
                "was_adjusted": True,
                "adjustment_reason": "Industry transition with marginal fit - networking critical"
            }

    return {
        "adjusted_decision": base_decision,
        "was_adjusted": False,
        "adjustment_reason": None
    }
