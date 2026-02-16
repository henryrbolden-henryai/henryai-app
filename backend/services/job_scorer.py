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
    # FACTOR 1: Title Match (0-30 points)
    # =================================================================
    title_overlap = _title_keyword_overlap(job_title, target_roles)

    if title_overlap >= 0.8:
        score += 30
        reasons.append("Strong title match")
    elif title_overlap >= 0.5:
        score += 20
        reasons.append("Good title match")
    elif title_overlap >= 0.25:
        score += 10
        reasons.append("Partial title match")
    # else: 0 points

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
        score += 5
    # else: 0 points (too far apart)

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
        # else: 0 points
    else:
        # No salary data — give benefit of the doubt
        score += 5

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

    # Add score data to job
    job["relevance_score"] = min(score, 100)
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
    min_score: int = 25,
) -> List[Dict[str, Any]]:
    """
    Score all jobs and return sorted by relevance_score descending.
    Jobs below min_score are filtered out.
    """
    scored = []
    for job in jobs:
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

    # Sort by relevance_score descending, then by network connection, then recency
    scored.sort(
        key=lambda j: (
            -j.get("relevance_score", 0),
            not j.get("network_connection", False),
            j.get("days_since_posted") or 999,
        )
    )

    return scored
