"""
Red Flag Language Lint for Resume Generation

Senior candidates get quietly downgraded by mid-market language that sounds fine
but signals junior positioning. This lint runs before resume output and flags
phrases that weaken senior signal.

Core Test: If a sentence can apply to 1,000 LinkedIn profiles, it fails.
If it doesn't answer "what broke if you weren't there?", it fails.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class LintResult:
    """Result of linting a single bullet point."""
    bullet: str
    bullet_index: int
    role: str
    failures: List[str]
    severity: str  # "high" | "medium" | "low"
    rewrite_suggestion: str


# =============================================================================
# TIER 1: KILL ON SIGHT
# These phrases add zero signal. Remove or rewrite every time.
# =============================================================================
TIER_1_PATTERNS = [
    (r"\bresults-driven\b", "Says nothing, universal filler", "Delete entirely, lead with actual result"),
    (r"\bpassionate about\b", "Emotion, not evidence", "Delete, show passion through outcomes"),
    (r"\bmotivated professional\b", "Generic self-description", "Delete, let work speak"),
    (r"\bteam player\b", "Table stakes, not differentiator", "Delete or specify collaboration outcome"),
    (r"\bdetail-oriented\b", "Claim without proof", "Delete or show detail in the work itself"),
    (r"\bexcellent communication skills?\b", "Everyone claims this", "Delete, demonstrate through stakeholder outcomes"),
    (r"\bproven track record\b", "Assertion without evidence", "Delete, show the track record instead"),
    (r"\bdynamic\b", "Meaningless adjective", "Delete"),
    (r"\bsynerg(?:y|ies)\b", "Consultant bingo", "Delete, specify what was actually combined"),
    (r"\bleveraged synergies\b", "Consultant bingo", "Delete, specify what was actually combined"),
    (r"\bvalue-add\b", "Corporate jargon", "Delete, state the value directly"),
]

# =============================================================================
# TIER 2: PASSIVE/JUNIOR-CODED
# These phrases signal contribution without ownership. Rewrite to show decision authority.
# =============================================================================
TIER_2_PATTERNS = [
    (r"\bresponsible for\b", "Passive, job description language", "'Owned [X]' or 'Led [X]'"),
    (r"\bhelped? (?:drive|build|create|develop|launch)\b", "Who owned the decision?", "'Drove [X]' or 'Led [X], resulting in...'"),
    (r"\bworked on\b", "Contribution without ownership", "'Built [X]' or 'Shipped [X]'"),
    (r"\bsupported\b", "Adjacent, not accountable", "'Enabled [X] by [specific action]' or reframe to owned outcome"),
    (r"\bassisted with\b", "Junior positioning", "'Co-led [X]' or specify owned component"),
    (r"\bwas involved in\b", "Observer language", "State specific role and decision authority"),
    (r"\bcontributed to\b", "Hides level of ownership", "Specify what you owned within the contribution"),
    (r"\bparticipated in\b", "Passive observer", "State what you decided or delivered"),
]

# =============================================================================
# TIER 3: VAGUE SCOPE HIDERS
# These phrases obscure seniority signals. Replace with specifics.
# =============================================================================
TIER_3_PATTERNS = [
    (r"\bvarious stakeholders\b", "Hides level, could be anyone", "Name the levels: 'VPs across Product, Eng, and Design'"),
    (r"\bcross-functional collaboration\b", "Table stakes, not signal", "Specify who, what decision, what outcome"),
    (r"\bmultiple teams\b", "How many? What scope?", "'4 engineering teams (35 engineers)'"),
    (r"\blarge-scale\b", "Relative, unverifiable", "Quantify: '$50M budget' or '2M users'"),
    (r"\bfast-paced environment\b", "Meaningless without stakes", "'Shipped 12 features in 6 months under Series B pressure'"),
    (r"\bend-to-end\b(?!.*(?:from|through|including))", "Must specify what end-to-end means", "'End-to-end ownership from discovery through launch and post-launch optimization'"),
    (r"\bkey initiatives?\b", "Which ones? What made them key?", "Name the initiative and its business impact"),
    (r"\bstrategic projects?\b", "Vague importance claim", "Specify the strategy and your decision authority"),
]

# =============================================================================
# TIER 4: EXPOSURE WITHOUT OWNERSHIP
# These phrases read as observer, not operator. Flag for career switcher detection.
# =============================================================================
TIER_4_PATTERNS = [
    (r"\bexposure to\b", "Observer, not operator", "If you operated, say what you did; if not, remove"),
    (r"\bfamiliar with\b", "Learning, not doing", "Remove or upgrade to demonstrated usage"),
    (r"\bknowledge of\b", "Passive awareness", "Show application, not awareness"),
    (r"\bunderstanding of\b", "Academic, not applied", "Demonstrate through outcomes"),
    (r"\bexperience with\b(?!\s+(?:building|leading|shipping|launching|driving|managing|owning))", "Weak without specifics", "Add what you built, shipped, or decided"),
]


def fails_linkedin_test(sentence: str) -> Tuple[bool, List[str]]:
    """
    If this sentence could appear on 1,000+ LinkedIn profiles unchanged,
    it provides no differentiation signal.

    Returns tuple of (failed, list of matched patterns)
    """
    matched = []
    sentence_lower = sentence.lower()

    for pattern, reason, _ in TIER_1_PATTERNS:
        if re.search(pattern, sentence_lower):
            matched.append(reason)

    # Also check some tier 3 patterns that are generic
    generic_tier_3 = [
        r"\bcross-functional collaboration\b",
        r"\bfast-paced environment\b",
    ]
    for pattern in generic_tier_3:
        if re.search(pattern, sentence_lower):
            if "Table stakes" not in matched:
                matched.append("Table stakes, not differentiator")

    return len(matched) > 0, matched


def fails_ownership_test(sentence: str) -> Tuple[bool, List[str]]:
    """
    If the sentence doesn't answer "what broke if you weren't there?",
    it lacks ownership signal.

    Returns tuple of (failed, list of matched patterns)
    """
    matched = []
    sentence_lower = sentence.lower()

    for pattern, reason, _ in TIER_2_PATTERNS:
        if re.search(pattern, sentence_lower):
            matched.append(reason)

    return len(matched) > 0, matched


def fails_scope_test(sentence: str) -> Tuple[bool, List[str]]:
    """
    If scope is described with adjectives instead of numbers,
    it hides seniority signals.

    Returns tuple of (failed, list of matched patterns)
    """
    matched = []
    sentence_lower = sentence.lower()

    for pattern, reason, _ in TIER_3_PATTERNS:
        if re.search(pattern, sentence_lower):
            matched.append(reason)

    return len(matched) > 0, matched


def fails_observer_test(sentence: str) -> Tuple[bool, List[str]]:
    """
    If the sentence positions the candidate as observer rather than operator,
    it signals adjacent experience, not ownership.

    Returns tuple of (failed, list of matched patterns)
    """
    matched = []
    sentence_lower = sentence.lower()

    for pattern, reason, _ in TIER_4_PATTERNS:
        if re.search(pattern, sentence_lower):
            matched.append(reason)

    return len(matched) > 0, matched


def classify_severity(failures: List[str]) -> str:
    """
    Classify severity based on failure types.
    """
    if "linkedin_test" in failures:
        return "high"  # Generic filler is worst
    if "ownership_test" in failures:
        return "high"  # Passive language is critical for senior roles
    if "observer_test" in failures:
        return "medium"  # May indicate career switcher
    return "low"  # Vague scope is fixable


def generate_rewrite_suggestion(bullet: str, failures: List[str]) -> str:
    """
    Generate specific rewrite guidance based on failure type.
    """
    suggestions = []

    if "linkedin_test" in failures:
        suggestions.append("Remove generic filler. Lead with the outcome.")

    if "ownership_test" in failures:
        suggestions.append("Replace passive language with ownership verbs (Owned, Led, Built, Shipped).")

    if "scope_test" in failures:
        suggestions.append("Replace adjectives with numbers (team size, budget, users, revenue).")

    if "observer_test" in failures:
        suggestions.append("If you operated, state what you decided or delivered. If you only observed, consider removing.")

    return " ".join(suggestions)


def get_specific_issues(bullet: str) -> List[Dict[str, str]]:
    """
    Get specific issues with rewrite guidance for a bullet.
    """
    issues = []
    bullet_lower = bullet.lower()

    # Check all tiers
    all_patterns = [
        ("tier_1", TIER_1_PATTERNS),
        ("tier_2", TIER_2_PATTERNS),
        ("tier_3", TIER_3_PATTERNS),
        ("tier_4", TIER_4_PATTERNS),
    ]

    for tier, patterns in all_patterns:
        for pattern, reason, rewrite in patterns:
            match = re.search(pattern, bullet_lower)
            if match:
                issues.append({
                    "tier": tier,
                    "matched_text": match.group(0),
                    "reason": reason,
                    "rewrite_pattern": rewrite,
                })

    return issues


def lint_resume_bullets(resume: Dict[str, Any]) -> Tuple[List[LintResult], Optional[str]]:
    """
    Run all lint rules against resume bullets.
    Returns list of flagged bullets and summary warning.
    """
    results = []

    for role in resume.get("experience", []):
        role_title = role.get("title", "Unknown Role")
        for i, bullet in enumerate(role.get("bullets", [])):
            failures = []

            linkedin_failed, linkedin_issues = fails_linkedin_test(bullet)
            ownership_failed, ownership_issues = fails_ownership_test(bullet)
            scope_failed, scope_issues = fails_scope_test(bullet)
            observer_failed, observer_issues = fails_observer_test(bullet)

            if linkedin_failed:
                failures.append("linkedin_test")
            if ownership_failed:
                failures.append("ownership_test")
            if scope_failed:
                failures.append("scope_test")
            if observer_failed:
                failures.append("observer_test")

            if failures:
                severity = classify_severity(failures)
                suggestion = generate_rewrite_suggestion(bullet, failures)
                results.append(LintResult(
                    bullet=bullet,
                    bullet_index=i,
                    role=role_title,
                    failures=failures,
                    severity=severity,
                    rewrite_suggestion=suggestion
                ))

    # Generate summary warning
    if not results:
        warning = None
    elif len(results) == 1:
        warning = "1 bullet reads mid-market and weakens senior signal. Recommend rewrite."
    else:
        warning = f"{len(results)} bullets read mid-market and weaken senior signal. Recommend rewrite."

    return results, warning


def lint_summary(summary: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Run lint rules against resume summary.
    Returns list of issues and summary warning.
    """
    issues = get_specific_issues(summary)

    if not issues:
        return [], None

    warning = f"Summary contains {len(issues)} phrase(s) that weaken senior signal."
    return issues, warning


def lint_resume(resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run complete lint on resume and return structured results.

    This is the main entry point for linting a resume.
    Returns a dictionary suitable for API response.
    """
    # Lint bullets
    bullet_results, bullets_warning = lint_resume_bullets(resume)

    # Lint summary if present
    summary = resume.get("summary", "")
    summary_issues, summary_warning = lint_summary(summary) if summary else ([], None)

    # Convert LintResult objects to dicts for JSON serialization
    flagged_bullets = []
    for result in bullet_results:
        # Get specific issues for this bullet
        specific_issues = get_specific_issues(result.bullet)

        flagged_bullets.append({
            "role": result.role,
            "bullet_index": result.bullet_index,
            "bullet": result.bullet,
            "failures": result.failures,
            "severity": result.severity,
            "suggestion": result.rewrite_suggestion,
            "specific_issues": specific_issues,
        })

    # Count auto-fixable (Tier 1 deletions and simple Tier 2 replacements)
    auto_fixable_count = sum(
        1 for b in flagged_bullets
        if "linkedin_test" in b["failures"] or
           any(issue["tier"] == "tier_1" for issue in b.get("specific_issues", []))
    )

    # Build combined warning
    warnings = []
    if bullets_warning:
        warnings.append(bullets_warning)
    if summary_warning:
        warnings.append(summary_warning)

    combined_warning = " ".join(warnings) if warnings else None

    return {
        "warning": combined_warning,
        "flagged_count": len(flagged_bullets),
        "flagged_bullets": flagged_bullets,
        "summary_issues": summary_issues,
        "auto_fixable_count": auto_fixable_count,
        "severity_counts": {
            "high": sum(1 for b in flagged_bullets if b["severity"] == "high"),
            "medium": sum(1 for b in flagged_bullets if b["severity"] == "medium"),
            "low": sum(1 for b in flagged_bullets if b["severity"] == "low"),
        }
    }


# =============================================================================
# AUTO-REWRITE FUNCTIONALITY
# =============================================================================

AUTO_REWRITES = {
    # Tier 1: Delete entirely
    r"\bresults-driven\s*": "",
    r"\bpassionate about\s*": "",
    r"\bteam player\b": "",
    r"\bdetail-oriented\s*": "",
    r"\bdynamic\s*": "",
    r"\bmotivated professional\s*": "",

    # Tier 2: Upgrade passive to active
    r"\bresponsible for\b": "Owned",
    r"\bhelped drive\b": "Drove",
    r"\bhelped build\b": "Built",
    r"\bhelped create\b": "Created",
    r"\bhelped develop\b": "Developed",
    r"\bhelped launch\b": "Launched",
    r"\bworked on\b": "Built",
}


def auto_rewrite_bullet(bullet: str) -> Tuple[str, List[str]]:
    """
    Apply automatic rewrites to a bullet.
    Returns (rewritten_bullet, list_of_changes_made).
    """
    rewritten = bullet
    changes = []

    for pattern, replacement in AUTO_REWRITES.items():
        match = re.search(pattern, rewritten, re.IGNORECASE)
        if match:
            original_text = match.group(0)
            if replacement:
                changes.append(f"'{original_text}' -> '{replacement}'")
            else:
                changes.append(f"Removed '{original_text}'")
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)

    # Clean up any double spaces or leading/trailing whitespace
    rewritten = re.sub(r'\s+', ' ', rewritten).strip()

    # Ensure first letter is capitalized after rewrites
    if rewritten and rewritten[0].islower():
        rewritten = rewritten[0].upper() + rewritten[1:]

    return rewritten, changes


def auto_rewrite_resume(resume: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply automatic rewrites to entire resume.
    Returns (rewritten_resume, changes_log).
    """
    import copy
    rewritten = copy.deepcopy(resume)
    changes_log = {
        "summary_changes": [],
        "bullet_changes": [],
    }

    # Rewrite summary
    if rewritten.get("summary"):
        new_summary, summary_changes = auto_rewrite_bullet(rewritten["summary"])
        if summary_changes:
            rewritten["summary"] = new_summary
            changes_log["summary_changes"] = summary_changes

    # Rewrite bullets
    for role_idx, role in enumerate(rewritten.get("experience", [])):
        for bullet_idx, bullet in enumerate(role.get("bullets", [])):
            new_bullet, bullet_changes = auto_rewrite_bullet(bullet)
            if bullet_changes:
                role["bullets"][bullet_idx] = new_bullet
                changes_log["bullet_changes"].append({
                    "role": role.get("title", "Unknown"),
                    "bullet_index": bullet_idx,
                    "original": bullet,
                    "rewritten": new_bullet,
                    "changes": bullet_changes,
                })

    return rewritten, changes_log
