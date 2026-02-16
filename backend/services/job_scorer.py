"""
Job Relevance Scorer
Scores job listings 0-100 against a candidate profile for alignment quality.
Rules-based (no LLM call) for speed and cost efficiency.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("henryhq.job_scorer")

# Seniority levels ordered from junior to executive
SENIORITY_LEVELS = ["entry", "junior", "mid", "senior", "staff", "director", "vp", "executive"]

# Industry keyword mappings for matching job descriptions against target industries
INDUSTRY_KEYWORDS = {
    "technology": ["software", "saas", "tech", "platform", "api", "cloud", "devops"],
    "healthcare": ["health", "medical", "clinical", "patient", "hospital", "pharma", "biotech"],
    "fintech": ["fintech", "payments", "banking", "financial", "lending", "insurance", "crypto"],
    "ecommerce": ["ecommerce", "e-commerce", "retail", "marketplace", "shopping", "commerce"],
    "media": ["media", "entertainment", "content", "publishing", "streaming", "news"],
    "manufacturing": ["manufacturing", "industrial", "production", "supply chain", "factory"],
    "energy": ["energy", "oil", "gas", "renewable", "solar", "utility"],
    "real_estate": ["real estate", "property", "housing", "mortgage", "construction"],
    "education": ["education", "edtech", "learning", "university", "school", "training"],
    "government": ["government", "public sector", "federal", "state", "municipal", "defense"],
    "consulting": ["consulting", "advisory", "strategy", "management consulting"],
    "telecom": ["telecom", "telecommunications", "wireless", "network", "5g"],
    "transportation": ["transportation", "logistics", "shipping", "delivery", "fleet"],
    "hospitality": ["hospitality", "hotel", "restaurant", "travel", "tourism"],
    "nonprofit": ["nonprofit", "non-profit", "ngo", "foundation", "charity"],
}

# Function-mismatch differentiators: words that signal a DIFFERENT function area.
# If a target role implies function X, and the job title contains differentiator words
# for function X, the job is likely in a different domain despite keyword overlap.
# Example: target "Product Manager" + job "Product Marketing Manager" → "marketing" is
# a differentiator for product_management, signaling a mismatch.
FUNCTION_DIFFERENTIATORS = {
    "engineering": {"sales", "marketing", "recruiter", "recruiting", "accounting", "legal", "nurse", "nursing", "teacher", "support", "customer", "hr", "human resources"},
    "product_management": {"marketing", "sales", "support", "operations", "accounting", "design", "content", "community", "customer"},
    "marketing": {"software", "mechanical", "electrical", "civil", "chemical", "data", "devops", "infrastructure", "backend", "frontend"},
    "sales": {"software", "mechanical", "electrical", "civil", "chemical", "nursing", "devops", "infrastructure", "backend", "frontend"},
    "design": {"sales", "accounting", "legal", "mechanical", "civil", "chemical", "nursing"},
    "data_analytics": {"sales", "marketing", "nursing", "legal", "mechanical", "civil", "customer"},
    "customer_success": {"software", "mechanical", "electrical", "chemical", "devops", "backend", "frontend"},
    "operations": {"software", "mechanical", "electrical", "nursing", "devops", "backend", "frontend"},
    "finance": {"software", "mechanical", "electrical", "nursing", "devops", "marketing", "design"},
    "hr_people": {"software", "mechanical", "electrical", "nursing", "devops", "marketing", "chemical"},
}

# Map common title keywords to their function area for mismatch detection
TITLE_FUNCTION_MAP = {
    "engineer": "engineering", "developer": "engineering", "architect": "engineering",
    "swe": "engineering", "devops": "engineering", "sre": "engineering",
    "product manager": "product_management", "program manager": "product_management",
    "product owner": "product_management",
    "designer": "design", "ux": "design", "ui": "design",
    "data scientist": "data_analytics", "data analyst": "data_analytics",
    "analyst": "data_analytics", "analytics": "data_analytics",
    "sales": "sales", "account executive": "sales", "bdr": "sales", "sdr": "sales",
    "marketing": "marketing", "growth": "marketing", "brand": "marketing",
    "customer success": "customer_success", "csm": "customer_success",
    "recruiter": "hr_people", "talent": "hr_people", "people": "hr_people",
    "finance": "finance", "accountant": "finance", "controller": "finance",
    "operations": "operations", "ops": "operations",
}


def infer_seniority_from_title(title: str) -> str:
    """Infer seniority level from a job title string."""
    title_lower = title.lower()

    if any(term in title_lower for term in ["chief", "cto", "cfo", "ceo", "coo", "cmo", "cpo", "ciso"]):
        return "executive"
    if any(term in title_lower for term in ["vp ", "vice president", "v.p."]):
        return "vp"
    if any(term in title_lower for term in ["director", "head of"]):
        return "director"
    if any(term in title_lower for term in ["staff", "principal"]):
        return "staff"
    if any(term in title_lower for term in ["senior", "sr.", "sr ", "lead"]):
        return "senior"
    if any(term in title_lower for term in ["junior", "jr.", "jr ", "associate", "entry", "intern"]):
        return "entry"
    return "mid"


def _seniority_distance(level_a: str, level_b: str) -> int:
    """Calculate distance between two seniority levels. 0 = exact match."""
    try:
        idx_a = SENIORITY_LEVELS.index(level_a)
        idx_b = SENIORITY_LEVELS.index(level_b)
        return abs(idx_a - idx_b)
    except ValueError:
        return 2  # Default moderate distance for unknown levels


def _title_keyword_overlap(title: str, target_roles: List[str]) -> float:
    """Calculate keyword overlap between job title and target roles. Returns 0.0-1.0."""
    if not target_roles or not title:
        return 0.0

    title_words = set(re.findall(r'\b\w+\b', title.lower()))
    # Remove common filler words
    filler = {"the", "a", "an", "of", "in", "at", "for", "and", "or", "to", "with", "is"}
    title_words -= filler

    best_overlap = 0.0
    for role in target_roles:
        role_words = set(re.findall(r'\b\w+\b', role.lower())) - filler
        if not role_words:
            continue
        overlap = len(title_words & role_words) / len(role_words)
        best_overlap = max(best_overlap, overlap)

    return best_overlap


def _infer_function_from_title(title: str) -> Optional[str]:
    """Infer the function area from a title string using TITLE_FUNCTION_MAP."""
    title_lower = title.lower()
    # Check multi-word keys first (longer = more specific)
    for keyword, function in sorted(TITLE_FUNCTION_MAP.items(), key=lambda x: -len(x[0])):
        if keyword in title_lower:
            return function
    return None


def _has_function_mismatch(job_title: str, target_roles: List[str]) -> int:
    """
    Detect if a job title indicates a different function area than the target roles.
    Returns a penalty: -15 if mismatch detected, 0 otherwise.

    Example: target "Product Manager" (product_management) vs job "Product Marketing Manager"
    → job title contains "marketing" which is a differentiator for product_management → penalty.
    """
    if not target_roles or not job_title:
        return 0

    # Determine function area implied by target roles
    target_functions = set()
    for role in target_roles:
        fn = _infer_function_from_title(role)
        if fn:
            target_functions.add(fn)

    if not target_functions:
        return 0

    # Check if job title contains differentiator words for any target function
    job_title_lower = job_title.lower()
    job_words = set(re.findall(r'\b\w+\b', job_title_lower))

    for target_fn in target_functions:
        differentiators = FUNCTION_DIFFERENTIATORS.get(target_fn, set())
        mismatch_words = job_words & differentiators
        if mismatch_words:
            logger.debug(
                f"Function mismatch: target function '{target_fn}', "
                f"job '{job_title}' contains differentiators: {mismatch_words}"
            )
            return -15

    return 0


def _should_disqualify(
    job: Dict[str, Any],
    target_roles: List[str],
    candidate_seniority: str,
    comp_min: Optional[int],
) -> bool:
    """
    Hard disqualification check — rejects jobs that are fundamentally misaligned
    BEFORE scoring. Returns True if job should be rejected outright.

    Disqualification rules:
    1. Seniority gap >= 3 levels (e.g., candidate "senior" but job is "entry")
    2. Salary ceiling < 70% of comp_min (e.g., comp_min=$150K but job max=$95K)
    3. Zero title keyword overlap when target_roles are provided
    """
    job_title = job.get("title", "")

    # Rule 1: Seniority too far apart
    if candidate_seniority and job_title:
        job_seniority = infer_seniority_from_title(job_title)
        dist = _seniority_distance(candidate_seniority, job_seniority)
        if dist >= 3:
            logger.debug(
                f"DISQUALIFIED (seniority): '{job_title}' is '{job_seniority}', "
                f"candidate is '{candidate_seniority}' (distance={dist})"
            )
            return True

    # Rule 2: Salary ceiling way below comp_min
    if comp_min:
        job_salary_max = job.get("salary_max")
        job_salary_min = job.get("salary_min")
        # Use job_salary_max if available, otherwise job_salary_min as a proxy
        salary_ceiling = job_salary_max or job_salary_min
        if salary_ceiling and salary_ceiling < comp_min * 0.70:
            logger.debug(
                f"DISQUALIFIED (salary): '{job_title}' ceiling ${salary_ceiling:,.0f} "
                f"< 70% of comp_min ${comp_min:,.0f}"
            )
            return True

    # Rule 3: Zero title keyword overlap
    if target_roles and job_title:
        overlap = _title_keyword_overlap(job_title, target_roles)
        if overlap == 0.0:
            logger.debug(
                f"DISQUALIFIED (title): '{job_title}' has zero keyword overlap "
                f"with target roles {target_roles}"
            )
            return True

    return False


def score_job(
    job: Dict[str, Any],
    target_roles: List[str],
    candidate_seniority: str = "mid",
    candidate_location: Optional[str] = None,
    candidate_remote_preferred: bool = False,
    comp_min: Optional[int] = None,
    comp_max: Optional[int] = None,
    target_industry: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Score a single job listing against candidate profile.

    Returns the job dict with added fields:
    - relevance_score (0-100)
    - relevance_reasons (list of strings explaining the score)
    """
    score = 0
    reasons = []

    job_title = job.get("title", "")
    job_location = job.get("location", "")
    job_salary_min = job.get("salary_min")
    job_salary_max = job.get("salary_max")
    job_description = job.get("description_snippet", "")
    job_is_remote = job.get("is_remote", False)
    days_since_posted = job.get("days_since_posted")

    # =================================================================
    # FACTOR 1: Title Match (0-30 points, with function mismatch penalty)
    # =================================================================
    title_overlap = _title_keyword_overlap(job_title, target_roles)
    function_penalty = _has_function_mismatch(job_title, target_roles)

    if title_overlap >= 0.8 and function_penalty == 0:
        score += 30
        reasons.append("Strong title match")
    elif title_overlap >= 0.8 and function_penalty < 0:
        # High keyword overlap BUT function mismatch — reduce credit
        score += 15
        reasons.append("Title overlap but different function")
    elif title_overlap >= 0.5 and function_penalty == 0:
        score += 20
        reasons.append("Good title match")
    elif title_overlap >= 0.5 and function_penalty < 0:
        # Moderate overlap with function mismatch — minimal credit
        score += 10
        reasons.append("Partial title, different function")
    elif title_overlap >= 0.25:
        score += 10
        reasons.append("Partial title match")
    # else: 0 points

    # Apply function mismatch penalty to overall score
    score += function_penalty

    # =================================================================
    # FACTOR 2: Seniority Match (0-20 points)
    # =================================================================
    job_seniority = infer_seniority_from_title(job_title)
    seniority_dist = _seniority_distance(candidate_seniority, job_seniority)

    if seniority_dist == 0:
        score += 20
        reasons.append("Seniority match")
    elif seniority_dist == 1:
        score += 12
        reasons.append("Close seniority")
    elif seniority_dist == 2:
        # 2 levels off — no points (was +5 before, too lenient)
        pass
    # else: 0 points (too far apart — should have been disqualified)

    # =================================================================
    # FACTOR 3: Location Match (0-15 points)
    # =================================================================
    if candidate_remote_preferred and job_is_remote:
        score += 15
        reasons.append("Remote")
    elif candidate_location and job_location:
        loc_lower = job_location.lower()
        cand_loc_lower = candidate_location.lower()
        # Check city match
        cand_parts = [p.strip() for p in cand_loc_lower.split(",")]
        if cand_parts[0] in loc_lower:
            score += 15
            reasons.append("Location match")
        elif len(cand_parts) > 1 and cand_parts[1].strip() in loc_lower:
            score += 10
            reasons.append("Same state")
        elif job_is_remote:
            score += 12
            reasons.append("Remote option")
    elif job_is_remote:
        score += 10
        reasons.append("Remote")

    # =================================================================
    # FACTOR 4: Salary Match (0-15 points)
    # =================================================================
    if comp_min and (job_salary_min or job_salary_max):
        job_min = job_salary_min or 0
        job_max = job_salary_max or job_min * 1.3
        comp_max_val = comp_max or comp_min * 1.3

        # Check for overlap between [comp_min, comp_max] and [job_min, job_max]
        if job_min <= comp_max_val and job_max >= comp_min:
            score += 15
            reasons.append("Salary in range")
        elif job_max >= comp_min * 0.85:
            score += 8
            reasons.append("Salary close")
        # else: 0 points (should have been disqualified if < 70%)
    # else: No salary data — 0 points (no more "benefit of the doubt")

    # =================================================================
    # FACTOR 5: Industry Match (0-10 points)
    # =================================================================
    if target_industry and job_description:
        industry_kws = INDUSTRY_KEYWORDS.get(target_industry, [])
        desc_lower = job_description.lower()
        company_lower = job.get("company", "").lower()
        combined = f"{desc_lower} {company_lower} {job_title.lower()}"

        matches = sum(1 for kw in industry_kws if kw in combined)
        if matches >= 2:
            score += 10
            reasons.append("Industry match")
        elif matches >= 1:
            score += 5
            reasons.append("Possible industry match")

    # =================================================================
    # FACTOR 6: Recency (0-10 points)
    # =================================================================
    if days_since_posted is not None:
        if days_since_posted <= 3:
            score += 10
            reasons.append("Just posted")
        elif days_since_posted <= 7:
            score += 7
            reasons.append("Recent")
        elif days_since_posted <= 14:
            score += 4
        elif days_since_posted <= 30:
            score += 2

    # Floor score at 0 (function penalty could push negative)
    job["relevance_score"] = max(min(score, 100), 0)
    job["relevance_reasons"] = reasons

    return job


def score_and_rank_jobs(
    jobs: List[Dict[str, Any]],
    target_roles: List[str],
    candidate_seniority: str = "mid",
    candidate_location: Optional[str] = None,
    candidate_remote_preferred: bool = False,
    comp_min: Optional[int] = None,
    comp_max: Optional[int] = None,
    target_industry: Optional[str] = None,
    min_score: int = 40,
) -> List[Dict[str, Any]]:
    """
    Score all jobs and return sorted by relevance_score descending.
    Jobs that fail hard disqualification checks are rejected outright.
    Remaining jobs below min_score are filtered out.
    """
    scored = []
    disqualified_count = 0

    for job in jobs:
        # Hard disqualification check — reject fundamentally misaligned jobs
        if _should_disqualify(job, target_roles, candidate_seniority, comp_min):
            disqualified_count += 1
            continue

        scored_job = score_job(
            job=job,
            target_roles=target_roles,
            candidate_seniority=candidate_seniority,
            candidate_location=candidate_location,
            candidate_remote_preferred=candidate_remote_preferred,
            comp_min=comp_min,
            comp_max=comp_max,
            target_industry=target_industry,
        )
        if scored_job["relevance_score"] >= min_score:
            scored.append(scored_job)

    if disqualified_count > 0:
        logger.info(f"Hard-filtered {disqualified_count} jobs (seniority/salary/title mismatch)")

    # Sort by relevance_score descending, then by network connection, then recency
    scored.sort(
        key=lambda j: (
            -j.get("relevance_score", 0),
            not j.get("network_connection", False),
            j.get("days_since_posted") or 999,
        )
    )

    return scored
