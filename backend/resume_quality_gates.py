"""
Resume Quality Gates

This module hardens resume customization output. The goal: no weak output possible.

At the 0.01% level, tight does not mean more features. Tight means the system
cannot produce a mid-market resume even if it tries.
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# 1. SIGNAL CONTRACT
# =============================================================================

@dataclass
class SignalContract:
    """Every generated resume must satisfy this contract before export."""
    scope_present: bool
    impact_present: bool
    ownership_present: bool
    level_aligned: bool

    missing_signals: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        return all([
            self.scope_present,
            self.impact_present,
            self.ownership_present,
            self.level_aligned
        ])

    def to_dict(self) -> dict:
        return {
            "valid": self.is_valid(),
            "scope_present": self.scope_present,
            "impact_present": self.impact_present,
            "ownership_present": self.ownership_present,
            "level_aligned": self.level_aligned,
            "missing_signals": self.missing_signals,
            "blocker_message": self._get_blocker_message() if not self.is_valid() else None
        }

    def _get_blocker_message(self) -> str:
        if not self.scope_present:
            return "This resume cannot signal seniority yet. No scope indicator (team size, budget, users, or authority) is present."
        if not self.impact_present:
            return "This resume lacks quantified business impact. Add at least one outcome with metrics."
        if not self.ownership_present:
            return "This resume uses contributor language, not ownership language. Use 'Owned', 'Led', 'Defined' instead of 'Helped', 'Supported'."
        if not self.level_aligned:
            return "Resume language doesn't match target seniority level. Senior roles need strategy language."
        return ""


def has_scope_signal(bullet: str) -> bool:
    """Detect team size, budget, users, revenue, geography, or authority."""
    scope_patterns = [
        r'\d+[\-\s]*(person|people|engineer|member|report|team)',  # team size
        r'\$[\d,\.]+\s*[MBK]?',  # budget/revenue
        r'\d+[MKB]?\+?\s*(users|customers|MAU|DAU|accounts)',  # user scale
        r'(global|regional|national|EMEA|APAC|NA|worldwide)',  # geography
        r'(P&L|budget|revenue|ARR|GMV|pipeline)',  # financial authority
        r'\d+\s*(countries|markets|regions)',  # geographic scale
    ]
    return any(re.search(p, bullet, re.IGNORECASE) for p in scope_patterns)


def has_impact_signal(bullet: str) -> bool:
    """Detect outcome + consequence (not just activity)."""
    # Must have both a metric AND a business consequence
    has_metric = bool(re.search(r'\d+%|\$[\d,\.]+|[\d\.]+x', bullet))
    consequence_words = [
        'resulting', 'saving', 'driving', 'enabling', 'reducing',
        'increasing', 'generating', 'delivering', 'achieving',
        'grew', 'reduced', 'increased', 'improved', 'accelerated'
    ]
    has_consequence = any(word in bullet.lower() for word in consequence_words)
    return has_metric and has_consequence


def has_ownership_signal(bullet: str) -> bool:
    """Detect decision-maker language, not contributor language."""
    ownership_verbs = [
        'owned', 'led', 'defined', 'built', 'shipped', 'launched',
        'architected', 'designed', 'established', 'created', 'drove',
        'spearheaded', 'pioneered', 'founded', 'orchestrated'
    ]
    contributor_verbs = [
        'supported', 'helped', 'assisted', 'contributed', 'participated',
        'involved in', 'worked on', 'responsible for'
    ]

    bullet_lower = bullet.lower()
    has_ownership = any(v in bullet_lower for v in ownership_verbs)
    has_contributor = any(v in bullet_lower for v in contributor_verbs)

    # Ownership signal is present if we have ownership language without contributor language
    return has_ownership and not has_contributor


def check_level_alignment(resume: dict, detected_level: str) -> bool:
    """Check if resume language matches detected seniority level."""
    bullets = extract_all_bullets(resume)
    summary = resume.get("summary", "")
    all_text = summary + " " + " ".join(bullets)
    all_text_lower = all_text.lower()

    senior_language = [
        'strategy', 'strategic', 'vision', 'roadmap', 'cross-functional',
        'stakeholder', 'executive', 'c-suite', 'board', 'org-wide',
        'company-wide', 'scaled', 'transformed', 'established'
    ]

    mid_language = [
        'implemented', 'executed', 'delivered', 'completed', 'managed',
        'coordinated', 'organized', 'tracked', 'reported'
    ]

    senior_count = sum(1 for word in senior_language if word in all_text_lower)
    mid_count = sum(1 for word in mid_language if word in all_text_lower)

    senior_levels = ['senior', 'staff', 'principal', 'lead', 'director', 'vp', 'head', 'chief']
    is_senior_target = any(level in detected_level.lower() for level in senior_levels)

    if is_senior_target:
        # Senior roles should have more senior language than mid language
        return senior_count >= mid_count
    else:
        # Non-senior roles are always aligned
        return True


def extract_all_bullets(resume: dict) -> List[str]:
    """Extract all bullet points from resume experience."""
    bullets = []
    for role in resume.get("experience", []):
        bullets.extend(role.get("bullets", []))
    return bullets


def validate_signal_contract(resume: dict, detected_level: str = "Senior") -> SignalContract:
    """
    Check if resume satisfies the signal contract.
    Run after customization, before export.
    """
    bullets = extract_all_bullets(resume)
    summary = resume.get("summary", "")
    all_content = [summary] + bullets

    scope = any(has_scope_signal(b) for b in all_content)
    impact = any(has_impact_signal(b) for b in all_content)
    ownership = any(has_ownership_signal(b) for b in all_content)
    level = check_level_alignment(resume, detected_level)

    missing = []
    if not scope:
        missing.append("scope")
    if not impact:
        missing.append("impact")
    if not ownership:
        missing.append("ownership")
    if not level:
        missing.append("level_alignment")

    return SignalContract(
        scope_present=scope,
        impact_present=impact,
        ownership_present=ownership,
        level_aligned=level,
        missing_signals=missing
    )


# =============================================================================
# 2. BULLET QUALITY GATE
# =============================================================================

@dataclass
class BulletQualityResult:
    """Result of bullet quality gate."""
    kept: List[dict]
    deprioritized: List[str]
    dropped: List[str]

    def to_dict(self) -> dict:
        return {
            "kept_count": len(self.kept),
            "deprioritized_count": len(self.deprioritized),
            "dropped_count": len(self.dropped),
            "kept_bullets": [b["bullet"] for b in self.kept],
            "deprioritized_bullets": self.deprioritized,
            "dropped_bullets": self.dropped
        }


def has_quantified_outcome(bullet: str) -> bool:
    """Number tied to business result."""
    return bool(re.search(
        r'(\d+%|\$[\d,\.]+[MBK]?|[\d\.]+x|\d+\s*(users|customers|deals|launches|products|features))',
        bullet
    ))


def has_decision_ownership(bullet: str) -> bool:
    """Shows what candidate decided, not just did."""
    decision_verbs = ['defined', 'decided', 'chose', 'prioritized', 'approved', 'vetoed', 'set', 'determined']
    return any(v in bullet.lower() for v in decision_verbs)


def has_irreversible_consequence(bullet: str) -> bool:
    """Something changed permanently."""
    consequence_markers = ['launched', 'shipped', 'established', 'created', 'built', 'founded', 'introduced', 'pioneered']
    return any(m in bullet.lower() for m in consequence_markers)


def has_org_leverage(bullet: str) -> bool:
    """Influence beyond immediate scope."""
    leverage_markers = [
        'adopted by', 'scaled across', 'influenced', 'framework',
        'standard', 'company-wide', 'org-wide', 'cross-functional',
        'enterprise-wide', 'organization'
    ]
    return any(m in bullet.lower() for m in leverage_markers)


def bullet_passes_quality_gate(bullet: str) -> Tuple[bool, str, int]:
    """
    Returns (passes, reason, strength_score).
    Bullet must pass at least one criterion.
    Strength score is used for ranking (higher = stronger signal).
    """
    score = 0
    reasons = []

    if has_quantified_outcome(bullet):
        score += 3
        reasons.append("quantified_outcome")
    if has_decision_ownership(bullet):
        score += 3
        reasons.append("decision_ownership")
    if has_irreversible_consequence(bullet):
        score += 2
        reasons.append("irreversible_consequence")
    if has_org_leverage(bullet):
        score += 2
        reasons.append("org_leverage")

    passes = score > 0
    reason = ",".join(reasons) if reasons else "no_qualifying_signal"

    return passes, reason, score


def apply_bullet_quality_gate(bullets: List[str], max_bullets: int = 5) -> BulletQualityResult:
    """
    Rank bullets, keep top N, archive the rest.
    """
    passing = []
    failing = []

    for bullet in bullets:
        passes, reason, score = bullet_passes_quality_gate(bullet)
        if passes:
            passing.append({"bullet": bullet, "reason": reason, "score": score})
        else:
            failing.append(bullet)

    # Sort passing bullets by signal strength (highest first)
    passing_sorted = sorted(passing, key=lambda x: -x["score"])

    return BulletQualityResult(
        kept=passing_sorted[:max_bullets],
        deprioritized=[b["bullet"] for b in passing_sorted[max_bullets:]],
        dropped=failing
    )


# =============================================================================
# 3. ROLE FRAME INFERENCE
# =============================================================================

@dataclass
class RoleFrame:
    """Role frame: Hired to [problem], accountable for [scope], measured on [outcome]."""
    role_title: str
    company: str
    problem: Optional[str]
    scope: Optional[str]
    outcome: Optional[str]
    confidence: float
    missing: List[str]

    def to_dict(self) -> dict:
        return {
            "role": f"{self.role_title} at {self.company}",
            "problem": self.problem,
            "scope": self.scope,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "missing": self.missing
        }


def infer_problem(title: str, company: str, bullets: List[str]) -> Tuple[Optional[str], float]:
    """Infer what problem the candidate was hired to solve."""
    # Look for hiring context clues
    hiring_patterns = [
        r'brought in to (.+?)(?:\.|,|$)',
        r'hired to (.+?)(?:\.|,|$)',
        r'tasked with (.+?)(?:\.|,|$)',
        r'charged with (.+?)(?:\.|,|$)',
    ]

    for bullet in bullets:
        for pattern in hiring_patterns:
            match = re.search(pattern, bullet, re.IGNORECASE)
            if match:
                return match.group(1).strip(), 0.9

    # Infer from title and company
    title_lower = title.lower()
    if 'product' in title_lower:
        return "drive product strategy and execution", 0.6
    if 'engineer' in title_lower:
        return "build and scale technical systems", 0.6
    if 'marketing' in title_lower:
        return "grow brand awareness and demand", 0.6
    if 'sales' in title_lower:
        return "drive revenue growth", 0.6

    return None, 0.0


def infer_scope(bullets: List[str]) -> Tuple[Optional[str], float]:
    """Infer accountability scope from bullets."""
    for bullet in bullets:
        # Look for explicit scope
        if has_scope_signal(bullet):
            # Extract the scope indicator
            scope_match = re.search(
                r'(\d+[\-\s]*(person|people|engineer|member|team)|\$[\d,\.]+\s*[MBK]?|\d+[MKB]?\+?\s*(users|customers))',
                bullet, re.IGNORECASE
            )
            if scope_match:
                return scope_match.group(0).strip(), 0.85

    return None, 0.0


def infer_outcome(bullets: List[str]) -> Tuple[Optional[str], float]:
    """Infer what the candidate was measured on."""
    for bullet in bullets:
        if has_impact_signal(bullet):
            # Extract the outcome
            outcome_match = re.search(
                r'(increasing|reducing|driving|achieving|improving)\s+(.+?)\s+(\d+%|\$[\d,\.]+)',
                bullet, re.IGNORECASE
            )
            if outcome_match:
                return f"{outcome_match.group(2)} ({outcome_match.group(3)})", 0.8

    return None, 0.0


def infer_role_frame(role: dict) -> RoleFrame:
    """
    Infer the role frame from resume content.
    Used to guide bullet generation and prioritization.
    """
    title = role.get("title", "Unknown")
    company = role.get("company", "Unknown")
    bullets = role.get("bullets", [])

    problem, problem_conf = infer_problem(title, company, bullets)
    scope, scope_conf = infer_scope(bullets)
    outcome, outcome_conf = infer_outcome(bullets)

    # Calculate overall confidence
    confidence = (problem_conf + scope_conf + outcome_conf) / 3

    # Identify missing components
    missing = []
    if not problem:
        missing.append("problem")
    if not scope:
        missing.append("scope")
    if not outcome:
        missing.append("outcome")

    return RoleFrame(
        role_title=title,
        company=company,
        problem=problem,
        scope=scope,
        outcome=outcome,
        confidence=round(confidence, 2),
        missing=missing
    )


# =============================================================================
# 4. KEYWORD PLACEMENT VALIDATION
# =============================================================================

def validate_keyword_placement(bullet: str, keyword: str) -> bool:
    """
    Keyword must be embedded in decision, outcome, or system context.
    Not allowed as standalone claim.
    """
    keyword_lower = keyword.lower()
    bullet_lower = bullet.lower()

    if keyword_lower not in bullet_lower:
        return True  # Keyword not present, no violation

    # Check if keyword is embedded in qualifying context
    keyword_escaped = re.escape(keyword_lower)

    decision_context = re.search(
        rf'(owned|led|defined|decided|set|drove|built)\s+.*{keyword_escaped}',
        bullet_lower
    )
    outcome_context = re.search(
        rf'{keyword_escaped}.*(\d+%|\$[\d,\.]+|resulting|driving|enabling)',
        bullet_lower
    )
    system_context = re.search(
        rf'(built|established|created|designed)\s+.*{keyword_escaped}.*(framework|system|process|standard|platform)',
        bullet_lower
    )

    return bool(decision_context or outcome_context or system_context)


def filter_embeddable_keywords(keywords: List[str], bullets: List[str]) -> Tuple[List[str], List[str]]:
    """
    If a keyword can't be embedded cleanly, skip it.
    Returns (embeddable, skipped).
    """
    embeddable = []
    skipped = []

    for keyword in keywords:
        can_embed = any(
            validate_keyword_placement(bullet, keyword)
            for bullet in bullets
        )
        if can_embed:
            embeddable.append(keyword)
        else:
            skipped.append(keyword)

    return embeddable, skipped


# =============================================================================
# 5. SUMMARY KILL SWITCH
# =============================================================================

def is_generic_summary(summary: str) -> bool:
    """
    Detect if summary could fit 5 different roles.
    """
    generic_markers = [
        r'results-driven',
        r'passionate',
        r'motivated professional',
        r'proven track record',
        r'excellent communication',
        r'team player',
        r'detail-oriented',
        r'dynamic',
        r'self-starter',
        r'strong work ethic',
    ]

    has_generic_language = any(
        re.search(m, summary, re.IGNORECASE)
        for m in generic_markers
    )

    lacks_scale = not bool(re.search(
        r'(\d+[MBK]?\+?\s*(users|customers|ARR|revenue|budget|team|engineers|reports)|\$[\d,\.]+[MBK])',
        summary
    ))

    lacks_specificity = not bool(re.search(
        r'(at|for|serving)\s+[A-Z][a-z]+',  # Company or product name
        summary
    ))

    return has_generic_language or (lacks_scale and lacks_specificity)


def generate_role_snapshot(resume: dict, detected_level: str, detected_function: str) -> str:
    """
    Generate a Role Snapshot to replace generic summary.
    Format: [Level] [Function] operating at [stage/scale]. [Ownership statement]. [Trust signal].
    """
    # Extract best scope signal from resume
    bullets = extract_all_bullets(resume)
    summary = resume.get("summary", "")
    all_content = [summary] + bullets

    scale_indicator = None
    ownership_statement = None

    for content in all_content:
        if has_scope_signal(content) and not scale_indicator:
            # Extract scale
            scale_match = re.search(
                r'(\d+[MBK]?\+?\s*(users|customers|MAU)|\$[\d,\.]+[MBK]?\s*(ARR|revenue|budget)|\d+[\-\s]*(person|people|engineer|member)\s*team)',
                content, re.IGNORECASE
            )
            if scale_match:
                scale_indicator = scale_match.group(0).strip()

        if has_ownership_signal(content) and not ownership_statement:
            # Extract ownership
            ownership_match = re.search(
                r'(owned|led|built|drove|defined)\s+([^,\.]+)',
                content, re.IGNORECASE
            )
            if ownership_match:
                ownership_statement = ownership_match.group(0).strip()

    # Build role snapshot
    parts = []

    # Level + Function
    parts.append(f"{detected_level} {detected_function}")

    # Scale indicator
    if scale_indicator:
        parts[0] += f" operating at scale ({scale_indicator})"

    # Ownership statement
    if ownership_statement:
        parts.append(ownership_statement.capitalize())

    # Trust signal
    parts.append("Trusted decision-maker across cross-functional stakeholders.")

    return ". ".join(parts)


# =============================================================================
# 6. CHANGE LOG
# =============================================================================

@dataclass
class ChangeLogEntry:
    """A single change made to the resume."""
    change_type: str  # "moved_up" | "moved_down" | "removed" | "rewritten" | "added_keyword"
    location: str  # "summary" | "role:Company Name" | "skills"
    original: str
    modified: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "change_type": self.change_type,
            "location": self.location,
            "original": self.original[:100] + "..." if len(self.original) > 100 else self.original,
            "modified": self.modified[:100] + "..." if len(self.modified) > 100 else self.modified,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ResumeChangeLog:
    """Log of all changes made to a resume."""
    session_id: str
    original_hash: str
    modified_hash: str
    entries: List[ChangeLogEntry] = field(default_factory=list)

    def add_entry(self, change_type: str, location: str, original: str, modified: str, reason: str):
        self.entries.append(ChangeLogEntry(
            change_type=change_type,
            location=location,
            original=original,
            modified=modified,
            reason=reason
        ))

    def summary(self) -> dict:
        return {
            "moved_up": len([e for e in self.entries if e.change_type == "moved_up"]),
            "moved_down": len([e for e in self.entries if e.change_type == "moved_down"]),
            "removed": len([e for e in self.entries if e.change_type == "removed"]),
            "rewritten": len([e for e in self.entries if e.change_type == "rewritten"]),
            "keywords_added": len([e for e in self.entries if e.change_type == "added_keyword"]),
            "total_changes": len(self.entries)
        }

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "summary": self.summary(),
            "entries": [e.to_dict() for e in self.entries[:20]]  # Limit to 20 for response size
        }


# =============================================================================
# 7. CREDIBILITY ASSESSMENT (HARD TRUTH RULE)
# =============================================================================

def assess_credibility(
    fit_score: int,
    signal_contract: SignalContract,
    lint_high_severity_count: int = 0,
    level_gap: int = 0
) -> dict:
    """
    Determine if resume can credibly compete for target role.
    """
    credibility_score = fit_score
    deductions = []

    # Deductions
    if not signal_contract.is_valid():
        credibility_score -= 15
        deductions.append("Signal contract not satisfied (-15)")

    if lint_high_severity_count > 0:
        lint_penalty = lint_high_severity_count * 5
        credibility_score -= lint_penalty
        deductions.append(f"{lint_high_severity_count} high-severity lint issues (-{lint_penalty})")

    if level_gap > 1:
        credibility_score -= 20
        deductions.append(f"Level gap of {level_gap} is significant (-20)")
    elif level_gap == 1:
        credibility_score -= 10
        deductions.append(f"Level gap of {level_gap} is notable (-10)")

    # Determine credibility level
    if credibility_score >= 70:
        credibility = "competitive"
        honest_assessment = "Your resume positions you competitively for this role."
    elif credibility_score >= 50:
        credibility = "marginal"
        honest_assessment = "You can apply, but address the gaps noted above to improve your odds."
    else:
        credibility = "not_credible"
        honest_assessment = "This resume cannot credibly compete for this role yet. The signal gaps are significant. Consider targeting roles closer to your current level or addressing the gaps identified."

    return {
        "credibility": credibility,
        "credibility_score": max(0, credibility_score),
        "can_generate": True,  # Always allow generation
        "recommendation_downgrade": credibility == "not_credible",
        "honest_assessment": honest_assessment,
        "deductions": deductions
    }


# =============================================================================
# MAIN QUALITY GATES FUNCTION
# =============================================================================

def run_quality_gates(
    resume: dict,
    detected_level: str = "Senior",
    detected_function: str = "Product Manager",
    fit_score: int = 70,
    lint_high_severity_count: int = 0,
    level_gap: int = 0,
    session_id: str = ""
) -> dict:
    """
    Run all quality gates on a resume.
    Returns comprehensive quality assessment.
    """
    import hashlib
    import json

    # 1. Signal Contract
    signal_contract = validate_signal_contract(resume, detected_level)

    # 2. Bullet Quality Gate (for each role)
    bullet_gate_results = {}
    for role in resume.get("experience", []):
        company = role.get("company", "Unknown")
        bullets = role.get("bullets", [])
        if bullets:
            result = apply_bullet_quality_gate(bullets)
            bullet_gate_results[company] = result.to_dict()

    # Aggregate bullet gate stats
    total_kept = sum(r.get("kept_count", 0) for r in bullet_gate_results.values())
    total_deprioritized = sum(r.get("deprioritized_count", 0) for r in bullet_gate_results.values())
    total_dropped = sum(r.get("dropped_count", 0) for r in bullet_gate_results.values())

    # 3. Role Frames
    role_frames = []
    for role in resume.get("experience", []):
        frame = infer_role_frame(role)
        role_frames.append(frame.to_dict())

    # 4. Summary Status
    summary = resume.get("summary", "")
    summary_is_generic = is_generic_summary(summary)
    summary_status = "generic_detected" if summary_is_generic else "acceptable"

    suggested_snapshot = None
    if summary_is_generic:
        suggested_snapshot = generate_role_snapshot(resume, detected_level, detected_function)

    # 5. Credibility Assessment
    credibility = assess_credibility(
        fit_score=fit_score,
        signal_contract=signal_contract,
        lint_high_severity_count=lint_high_severity_count,
        level_gap=level_gap
    )

    # 6. Change Log (placeholder - would be populated during actual generation)
    original_hash = hashlib.md5(json.dumps(resume, sort_keys=True).encode()).hexdigest()[:8]
    change_log = ResumeChangeLog(
        session_id=session_id or "unknown",
        original_hash=original_hash,
        modified_hash=original_hash  # Same if no changes yet
    )

    return {
        "signal_contract": signal_contract.to_dict(),
        "bullet_gate": {
            "kept_count": total_kept,
            "deprioritized_count": total_deprioritized,
            "dropped_count": total_dropped,
            "by_role": bullet_gate_results
        },
        "role_frames": role_frames,
        "summary_status": summary_status,
        "suggested_snapshot": suggested_snapshot,
        "credibility": credibility,
        "change_log": change_log.summary(),
        "quality_score": calculate_overall_quality_score(
            signal_contract, total_kept, total_dropped, summary_is_generic, credibility
        )
    }


def calculate_overall_quality_score(
    signal_contract: SignalContract,
    kept_bullets: int,
    dropped_bullets: int,
    summary_generic: bool,
    credibility: dict
) -> int:
    """Calculate overall quality score 0-100."""
    score = 100

    # Signal contract (up to -30)
    if not signal_contract.scope_present:
        score -= 10
    if not signal_contract.impact_present:
        score -= 10
    if not signal_contract.ownership_present:
        score -= 10

    # Bullet quality (up to -20)
    if kept_bullets == 0:
        score -= 20
    elif dropped_bullets > kept_bullets:
        score -= 10

    # Summary (up to -15)
    if summary_generic:
        score -= 15

    # Credibility alignment (up to -20)
    if credibility.get("credibility") == "not_credible":
        score -= 20
    elif credibility.get("credibility") == "marginal":
        score -= 10

    return max(0, score)
