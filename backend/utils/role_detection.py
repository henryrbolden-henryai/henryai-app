"""Role type detection and classification utilities"""


def detect_role_type(job_description: str, role_title: str) -> str:
    """
    Detect the role type for role-specific question routing and signal weighting.
    Returns: "product_manager", "software_engineer", "ux_designer", "ui_designer",
             "talent_acquisition", "general_leadership"
    """
    combined = f"{job_description} {role_title}".lower()

    # Product Manager
    if any(term in combined for term in [
        "product manager", "product management", "pm ", "product lead",
        "product owner", "roadmap", "product strategy"
    ]):
        return "product_manager"

    # Software Engineer
    elif any(term in combined for term in [
        "software engineer", "developer", "engineering", "swe",
        "backend", "frontend", "full stack", "architect", "devops"
    ]):
        return "software_engineer"

    # UX Designer
    elif any(term in combined for term in [
        "ux designer", "ux research", "user experience", "user research",
        "design research", "uxr"
    ]):
        return "ux_designer"

    # UI Designer
    elif any(term in combined for term in [
        "ui designer", "visual designer", "ui/ux", "product designer",
        "interaction designer", "design system"
    ]):
        return "ui_designer"

    # Talent Acquisition / Recruiting
    elif any(term in combined for term in [
        "talent acquisition", "recruiting", "recruiter", "ta ",
        "sourcer", "talent partner", "hiring", "recruitment"
    ]):
        return "talent_acquisition"

    # General Leadership
    else:
        return "general_leadership"


def determine_target_level(job_description: str) -> str:
    """
    Infer target level from job description language.
    Returns: "L4", "L5A", or "L5B"
    """
    jd_lower = job_description.lower()

    # L5B indicators
    if any(phrase in jd_lower for phrase in [
        "lead strategic initiatives",
        "define organizational direction",
        "influence senior leadership",
        "drive company-wide",
        "principal", "staff"
    ]):
        return "L5B"

    # L5A indicators
    elif any(phrase in jd_lower for phrase in [
        "lead cross-functional",
        "coordinate across teams",
        "strategic input",
        "senior", "lead"
    ]):
        return "L5A"

    # Default to L4
    else:
        return "L4"


def infer_seniority_from_title(role_title: str) -> str:
    """Infer seniority level from role title."""
    title_lower = role_title.lower()

    if any(term in title_lower for term in ["chief", "cto", "cfo", "ceo", "coo", "vp", "vice president", "head of"]):
        return "executive"
    elif any(term in title_lower for term in ["director", "principal", "staff"]):
        return "director"
    elif any(term in title_lower for term in ["senior", "sr.", "sr ", "lead"]):
        return "senior"
    elif any(term in title_lower for term in ["junior", "jr.", "jr ", "associate", "entry"]):
        return "junior"
    else:
        return "mid"


def infer_industry_from_company(company_name: str) -> str:
    """Infer industry from company name (basic heuristics)."""
    company_lower = company_name.lower()

    # Fintech
    if any(term in company_lower for term in ["stripe", "square", "plaid", "robinhood", "coinbase", "paypal", "venmo"]):
        return "fintech"
    # Big tech
    if any(term in company_lower for term in ["google", "meta", "amazon", "apple", "microsoft", "netflix"]):
        return "big_tech"
    # Enterprise
    if any(term in company_lower for term in ["salesforce", "oracle", "sap", "workday", "servicenow"]):
        return "enterprise_saas"
    # E-commerce
    if any(term in company_lower for term in ["shopify", "etsy", "ebay", "wayfair"]):
        return "ecommerce"
    # Healthcare
    if any(term in company_lower for term in ["health", "medical", "pharma", "biotech"]):
        return "healthcare"

    return "technology"


def get_competency_for_stage(interview_stage: str, question_number: int) -> str:
    """
    Select competency to test based on stage and question number.
    Ensures variety across the session.
    """
    competencies = {
        "recruiter_screen": [
            "communication",
            "motivation",
            "culture_fit",
            "technical_basics",
            "availability"
        ],
        "hiring_manager": [
            "leadership",
            "problem_solving",
            "ambiguity_tolerance",
            "stakeholder_management",
            "technical_depth"
        ]
    }

    stage_competencies = competencies.get(interview_stage, competencies["hiring_manager"])
    return stage_competencies[(question_number - 1) % len(stage_competencies)]


# Signal weights by role type (used for scoring)
SIGNAL_WEIGHTS_BY_ROLE = {
    "product_manager": {
        "functional_competency": 0.15,
        "leadership": 0.10,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.15,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.10,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.05
    },
    "software_engineer": {
        "functional_competency": 0.20,
        "leadership": 0.05,
        "collaboration": 0.10,
        "ownership": 0.15,
        "strategic_thinking": 0.10,
        "problem_solving": 0.15,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.05
    },
    "ux_designer": {
        "functional_competency": 0.15,
        "leadership": 0.05,
        "collaboration": 0.15,
        "ownership": 0.10,
        "strategic_thinking": 0.10,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.15
    },
    "ui_designer": {
        "functional_competency": 0.20,
        "leadership": 0.05,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.05,
        "problem_solving": 0.10,
        "communication_clarity": 0.15,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.15
    },
    "talent_acquisition": {
        "functional_competency": 0.15,
        "leadership": 0.10,
        "collaboration": 0.15,
        "ownership": 0.10,
        "strategic_thinking": 0.10,
        "problem_solving": 0.10,
        "communication_clarity": 0.15,
        "metrics_orientation": 0.10,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.00
    },
    "general_leadership": {
        "functional_competency": 0.10,
        "leadership": 0.15,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.15,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.10,
        "executive_presence": 0.05,
        "user_centricity": 0.00
    }
}
