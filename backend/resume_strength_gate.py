"""
Resume Strength Gate

Moves from "technically correct" to "clearly strong." A resume that passes all
existing quality gates but still reads like a B+ candidate should get caught
and elevated.

This runs after existing quality gates. It's not pass/fail—it's a score that
triggers the amplification pass if too low.
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta


# =============================================================================
# SCORING WEIGHTS (Revised per spec review)
# =============================================================================
SCOPE_CLARITY = 25
OUTCOME_SPECIFICITY = 30  # Increased from 25 - outcome is king signal
VERB_STRENGTH = 20
COMPARATIVE_CONTEXT = 10  # Reduced from 15
BUSINESS_IMPACT = 15


# =============================================================================
# LEVEL-AWARE VERB TIERS
# =============================================================================
POWER_VERBS = {
    'entry': ['built', 'created', 'delivered', 'executed', 'launched', 'completed',
              'developed', 'produced', 'achieved', 'generated'],
    'mid': ['led', 'managed', 'drove', 'owned', 'designed', 'implemented',
            'directed', 'coordinated', 'oversaw', 'supervised'],
    'senior': ['defined', 'architected', 'established', 'transformed', 'scaled',
               'pioneered', 'shaped', 'elevated', 'modernized', 'revamped'],
    'director': ['orchestrated', 'spearheaded', 'championed', 'instituted',
                 'overhauled', 'revolutionized', 'reimagined', 'unified']
}

WEAK_VERBS = [
    'helped', 'assisted', 'supported', 'worked on', 'was responsible for',
    'participated', 'contributed', 'involved in', 'handled', 'dealt with',
    'took part in', 'was part of', 'aided'
]


# =============================================================================
# SENIORITY LEVEL INFERENCE
# =============================================================================
SENIORITY_LEVELS = {
    'intern': 0, 'associate': 1, 'junior': 1,
    'analyst': 2, 'specialist': 2, 'coordinator': 2,
    'senior': 3, 'lead': 3, 'sr': 3,
    'staff': 4, 'principal': 4,
    'manager': 5,
    'senior manager': 6,
    'director': 7,
    'senior director': 8,
    'vp': 9, 'vice president': 9,
    'svp': 10, 'senior vice president': 10,
    'evp': 11, 'executive vice president': 11,
    'c-suite': 12, 'cto': 12, 'cfo': 12, 'coo': 12, 'ceo': 12, 'chief': 12
}


def infer_seniority(title: str) -> int:
    """Infer seniority level from title (0-12 scale)."""
    title_lower = title.lower()

    # Check longest matches first to avoid partial matches
    for key, level in sorted(SENIORITY_LEVELS.items(), key=lambda x: -len(x[0])):
        if key in title_lower:
            return level

    return 3  # Default to mid-level if unknown


def title_to_level_category(title: str) -> str:
    """Convert title to level category for verb matching."""
    seniority = infer_seniority(title)

    if seniority <= 1:
        return 'entry'
    elif seniority <= 4:
        return 'mid'
    elif seniority <= 6:
        return 'senior'
    else:
        return 'director'


# =============================================================================
# BULLET STRENGTH SCORING
# =============================================================================
@dataclass
class BulletStrengthResult:
    """Result of scoring a single bullet's strength."""
    bullet: str
    score: int
    missing: List[str]
    level_appropriate: bool
    breakdown: Dict[str, int] = field(default_factory=dict)


def bullet_strength_score(bullet: str, level: str) -> BulletStrengthResult:
    """
    Score bullet strength 0-100.
    Returns score + what's missing for amplification pass.

    Args:
        bullet: The bullet text to score
        level: Candidate level ('entry', 'mid', 'senior', 'director')
    """
    score = 0
    missing = []
    breakdown = {}

    # Normalize level
    if level not in POWER_VERBS:
        level = 'mid'

    # 1. SCOPE CLARITY (25 pts)
    scope_patterns = [
        r'\d+[\-\s]*(person|people|member|report|engineer|team|employee)',
        r'\$[\d,\.]+\s*[MBK]?',
        r'\d+[MKB]?\+?\s*(users|customers|MAU|DAU|accounts|clients)',
        r'(global|regional|national|EMEA|APAC|NA|LATAM|cross-functional|enterprise-wide)',
        r'(P&L|budget|revenue|ARR|GMV|portfolio|pipeline)',
        r'\d+\s*(countries|markets|regions|locations|offices)',
        r'\d+\s*(products?|platforms?|applications?|systems?)',
    ]
    if any(re.search(p, bullet, re.IGNORECASE) for p in scope_patterns):
        score += SCOPE_CLARITY
        breakdown['scope'] = SCOPE_CLARITY
    else:
        missing.append('scope')
        breakdown['scope'] = 0

    # 2. OUTCOME SPECIFICITY (30 pts)
    has_metric = bool(re.search(
        r'\d+%|\$[\d,\.]+[MBK]?|[\d\.]+x|\d+\s*(point|pts|basis)',
        bullet
    ))
    consequence_words = [
        'resulting', 'saving', 'driving', 'enabling', 'reducing',
        'increasing', 'generating', 'delivering', 'achieving',
        'improving', 'accelerating', 'eliminating', 'cutting',
        'boosting', 'growing', 'expanding', 'lowering'
    ]
    has_consequence = any(w in bullet.lower() for w in consequence_words)

    if has_metric and has_consequence:
        score += OUTCOME_SPECIFICITY
        breakdown['outcome'] = OUTCOME_SPECIFICITY
    elif has_metric:
        score += 20  # Partial credit for metric without consequence
        breakdown['outcome'] = 20
        missing.append('consequence')
    else:
        missing.append('outcome')
        breakdown['outcome'] = 0

    # 3. VERB STRENGTH (20 pts)
    bullet_lower = bullet.lower()
    has_weak = any(v in bullet_lower for v in WEAK_VERBS)

    # Check level-appropriate power verbs
    level_verbs = POWER_VERBS.get(level, POWER_VERBS['mid'])
    # Also accept verbs from adjacent levels
    all_acceptable_verbs = set(level_verbs)
    if level == 'entry':
        all_acceptable_verbs.update(POWER_VERBS['mid'])
    elif level == 'mid':
        all_acceptable_verbs.update(POWER_VERBS['entry'])
        all_acceptable_verbs.update(POWER_VERBS['senior'])
    elif level == 'senior':
        all_acceptable_verbs.update(POWER_VERBS['mid'])
        all_acceptable_verbs.update(POWER_VERBS['director'])
    elif level == 'director':
        all_acceptable_verbs.update(POWER_VERBS['senior'])

    has_power = any(
        bullet_lower.startswith(v) or f' {v} ' in bullet_lower
        for v in all_acceptable_verbs
    )

    if has_power and not has_weak:
        score += VERB_STRENGTH
        breakdown['verb'] = VERB_STRENGTH
    elif not has_weak:
        score += 10  # Neutral verb, not weak
        breakdown['verb'] = 10
        missing.append('verb_strength')
    else:
        missing.append('weak_verb')
        breakdown['verb'] = 0

    # 4. COMPARATIVE CONTEXT (10 pts)
    comparative_patterns = [
        r'(vs|versus|compared to|from|to)\s+\d',
        r'(#\d|top\s+\d|first|only|highest|lowest)',
        r'(\d+%\s+(above|below|over|under|more|less))',
        r'(industry|company|team|district|department)\s+(average|benchmark|standard|record)',
        r'(exceeded|surpassed|outperformed|beat|topped)',
        r'(\d+)\s*(to|→|->)\s*(\d+)',  # Before/after pattern
    ]
    if any(re.search(p, bullet, re.IGNORECASE) for p in comparative_patterns):
        score += COMPARATIVE_CONTEXT
        breakdown['comparative'] = COMPARATIVE_CONTEXT
    else:
        missing.append('comparative')
        breakdown['comparative'] = 0

    # 5. BUSINESS IMPACT LANGUAGE (15 pts)
    impact_terms = [
        'revenue', 'cost', 'efficiency', 'risk', 'retention', 'churn',
        'conversion', 'margin', 'growth', 'profit', 'savings', 'roi',
        'throughput', 'velocity', 'capacity', 'compliance', 'nps',
        'satisfaction', 'engagement', 'productivity', 'quality',
        'uptime', 'latency', 'performance', 'adoption', 'utilization'
    ]
    if any(t in bullet.lower() for t in impact_terms):
        score += BUSINESS_IMPACT
        breakdown['business_impact'] = BUSINESS_IMPACT
    else:
        missing.append('business_impact')
        breakdown['business_impact'] = 0

    # Level appropriateness check
    level_appropriate = check_level_alignment(bullet, level)

    return BulletStrengthResult(
        bullet=bullet,
        score=score,
        missing=missing,
        level_appropriate=level_appropriate,
        breakdown=breakdown
    )


def check_level_alignment(bullet: str, level: str) -> bool:
    """
    Check if bullet language matches expected seniority.
    """
    bullet_lower = bullet.lower()

    # Director+ should have strategy language
    if level == 'director':
        strategy_signals = [
            'strategy', 'vision', 'organization', 'portfolio',
            'executive', 'board', 'enterprise', 'transformation',
            'company-wide', 'org-wide', 'p&l', 'investment'
        ]
        return any(s in bullet_lower for s in strategy_signals)

    # Senior should have ownership language
    if level == 'senior':
        ownership_signals = [
            'owned', 'led', 'defined', 'architected', 'established',
            'drove', 'shaped', 'built', 'designed', 'created'
        ]
        return any(s in bullet_lower for s in ownership_signals)

    # Mid/entry: less strict
    return True


# =============================================================================
# RESUME-LEVEL STRENGTH ASSESSMENT
# =============================================================================
def assess_resume_strength(bullets: List[str], level: str) -> Dict[str, Any]:
    """
    Assess overall resume strength.
    Returns actionable data for amplification pass.

    Args:
        bullets: List of all bullet points from resume
        level: Candidate level ('entry', 'mid', 'senior', 'director')
    """
    if not bullets:
        return {
            "avg_strength": 0,
            "strong_count": 0,
            "weak_count": 0,
            "needs_amplification": True,
            "weak_bullets": [],
            "strong_bullets": [],
            "missing_patterns": {},
            "level_misalignment": [],
            "assessment": "No bullets to assess"
        }

    results = [bullet_strength_score(b, level) for b in bullets]

    weak_bullets = [r for r in results if r.score < 60]
    strong_bullets = [r for r in results if r.score >= 60]
    avg_score = sum(r.score for r in results) / len(results)

    # Aggregate what's missing across all bullets
    missing_summary = {}
    for r in results:
        for m in r.missing:
            missing_summary[m] = missing_summary.get(m, 0) + 1

    # Determine if amplification needed
    needs_amplification = avg_score < 65 or len(weak_bullets) > len(bullets) * 0.4

    # Generate assessment message
    if avg_score >= 75:
        assessment = "Strong resume. Bullets demonstrate clear impact and ownership."
    elif avg_score >= 65:
        assessment = "Solid resume. Some bullets could be strengthened with more specific outcomes."
    elif avg_score >= 50:
        assessment = "Resume needs work. Many bullets lack quantified outcomes or clear ownership."
    else:
        assessment = "Weak resume. Most bullets need significant strengthening before submission."

    return {
        "avg_strength": round(avg_score),
        "strong_count": len(strong_bullets),
        "weak_count": len(weak_bullets),
        "total_bullets": len(bullets),
        "needs_amplification": needs_amplification,
        "weak_bullets": [
            {
                "bullet": r.bullet,
                "score": r.score,
                "missing": r.missing,
                "breakdown": r.breakdown
            }
            for r in weak_bullets
        ],
        "strong_bullets": [
            {
                "bullet": r.bullet,
                "score": r.score,
                "breakdown": r.breakdown
            }
            for r in strong_bullets
        ],
        "missing_patterns": missing_summary,
        "level_misalignment": [r.bullet for r in results if not r.level_appropriate],
        "assessment": assessment
    }


# =============================================================================
# AMPLIFICATION APPLICATION
# =============================================================================
@dataclass
class AmplifiedBullet:
    """Result of applying amplification to a bullet."""
    original: str
    rewritten: str
    score_before: int
    score_after: int
    improvement: int
    changes_made: str
    confidence: str
    applied: bool
    action: str  # "apply", "queue_for_phase_2", "keep_original"
    user_prompt: Optional[str] = None


def apply_amplification(
    amplified: Dict[str, Any],
    original_bullet: str,
    level: str
) -> AmplifiedBullet:
    """
    Decide whether to apply an amplified rewrite.
    Only applies rewrites we're confident about.

    Args:
        amplified: The amplification result from Claude
        original_bullet: The original bullet text
        level: Candidate level for re-scoring
    """
    original_score = bullet_strength_score(original_bullet, level).score

    # Route low-confidence to Phase 2
    if amplified.get("confidence") == "low" or amplified.get("needs_user_input"):
        return AmplifiedBullet(
            original=original_bullet,
            rewritten=original_bullet,  # Keep original
            score_before=original_score,
            score_after=original_score,
            improvement=0,
            changes_made="Requires user confirmation",
            confidence=amplified.get("confidence", "low"),
            applied=False,
            action="queue_for_phase_2",
            user_prompt=amplified.get("user_prompt")
        )

    # Re-score the rewrite to verify improvement
    rewritten_text = amplified.get("rewritten", original_bullet)
    new_score = bullet_strength_score(rewritten_text, level).score

    # Don't apply if no improvement
    if new_score <= original_score:
        return AmplifiedBullet(
            original=original_bullet,
            rewritten=original_bullet,
            score_before=original_score,
            score_after=original_score,
            improvement=0,
            changes_made="Rewrite did not improve score",
            confidence=amplified.get("confidence", "medium"),
            applied=False,
            action="keep_original"
        )

    # Apply the improvement
    return AmplifiedBullet(
        original=original_bullet,
        rewritten=rewritten_text,
        score_before=original_score,
        score_after=new_score,
        improvement=new_score - original_score,
        changes_made=amplified.get("changes", "Strengthened bullet"),
        confidence=amplified.get("confidence", "high"),
        applied=True,
        action="apply"
    )


# =============================================================================
# FALLBACK HANDLING
# =============================================================================
def handle_weak_bullet_fallback(
    bullet: str,
    final_score: int,
    user_input_provided: bool,
    is_recent_role: bool
) -> Dict[str, Any]:
    """
    Decide what to do with bullets that couldn't be elevated.

    Args:
        bullet: The bullet text
        final_score: The final score after any amplification attempts
        user_input_provided: Whether user provided additional context
        is_recent_role: Whether this is from a recent role (last 5 years or top 2)
    """

    # Critical weakness, no user help
    if final_score < 30 and not user_input_provided:
        return {
            "action": "drop",
            "bullet": bullet,
            "reason": "No qualifying signal, could not elevate",
            "show_in_archive": True,  # User can restore if they want
            "severity": "critical"
        }

    # Weak but not critical
    if final_score < 40 and not user_input_provided:
        if is_recent_role:
            return {
                "action": "deprioritize",
                "bullet": bullet,
                "reason": "Moved to end of role - lacks impact signal",
                "new_position": "last",
                "severity": "high"
            }
        else:
            return {
                "action": "drop",
                "bullet": bullet,
                "reason": "Older role, weak signal - removed to save space",
                "show_in_archive": True,
                "severity": "medium"
            }

    # Marginal (40-59), keep but flag
    if final_score < 60:
        return {
            "action": "keep_with_warning",
            "bullet": bullet,
            "reason": "Kept but below strength threshold",
            "warning": "Consider adding metrics or outcomes to strengthen",
            "severity": "low"
        }

    # 60+ is acceptable
    return {
        "action": "keep",
        "bullet": bullet,
        "reason": "Meets strength threshold",
        "severity": "none"
    }


def is_recent_role(role_index: int, role_end_date: Optional[str] = None) -> bool:
    """
    Determine if a role is recent (should be preserved over older roles).

    Args:
        role_index: Position in experience list (0 = most recent)
        role_end_date: End date string (optional)
    """
    # Most recent 2 roles are always considered recent
    if role_index < 2:
        return True

    # Or within last 5 years
    if role_end_date:
        try:
            # Try common date formats
            for fmt in ['%Y-%m', '%Y', '%m/%Y', '%B %Y']:
                try:
                    end = datetime.strptime(role_end_date, fmt)
                    return end > datetime.now() - timedelta(days=5*365)
                except ValueError:
                    continue
        except Exception:
            pass

    # Default to not recent if we can't determine
    return False


# =============================================================================
# RESUME TRAJECTORY ASSESSMENT
# =============================================================================
def extract_scope_signal(role: Dict[str, Any]) -> Optional[int]:
    """
    Extract numeric scope from role (team size, budget, users).
    Returns a normalized numeric value for comparison.
    """
    bullets = role.get("bullets", [])

    for bullet in bullets:
        # Team size (prioritize this as most common)
        match = re.search(
            r'(\d+)[\-\s]*(person|people|member|report|engineer|employee)',
            bullet, re.IGNORECASE
        )
        if match:
            return int(match.group(1))

        # User/customer count
        match = re.search(
            r'(\d+)([MKB])?\+?\s*(users|customers|accounts|clients)',
            bullet, re.IGNORECASE
        )
        if match:
            num = int(match.group(1))
            multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(match.group(2), 1)
            return num * multiplier

        # Budget/revenue
        match = re.search(
            r'\$(\d+(?:\.\d+)?)\s*([MBK])?',
            bullet, re.IGNORECASE
        )
        if match:
            num = float(match.group(1))
            multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}.get(match.group(2), 1)
            return int(num * multiplier)

    return None


def is_escalating(scopes: List[Optional[int]]) -> bool:
    """
    Check if scope generally increases over career (older → newer).
    Roles are ordered most recent first, so we check if index 0 has highest scope.
    """
    # Filter out None values but track positions
    valid = [(i, s) for i, s in enumerate(scopes) if s is not None]

    if len(valid) < 2:
        return True  # Can't assess with < 2 data points

    # Most recent (index 0) should have highest or comparable scope
    # Split into first half (recent) and second half (older)
    first_half = [s for i, s in valid if i < len(scopes) // 2]
    second_half = [s for i, s in valid if i >= len(scopes) // 2]

    if first_half and second_half:
        # Recent roles should have >= 80% of older role scope
        # (allows for some variance, lateral moves, etc.)
        return max(first_half) >= max(second_half) * 0.8

    return True


def assess_resume_trajectory(roles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check if resume shows progression, not just strong bullets.

    Args:
        roles: List of experience roles (most recent first)
    """
    issues = []

    if not roles:
        return {
            "trajectory_healthy": False,
            "issues": [{"type": "no_experience", "message": "No experience found", "severity": "critical"}]
        }

    # Check title progression (most recent should be highest)
    titles = [r.get("title", "") for r in roles]
    title_levels = [infer_seniority(t) for t in titles]

    # Check if titles are roughly descending (most senior first)
    if len(title_levels) >= 2:
        recent_max = max(title_levels[:2]) if len(title_levels) >= 2 else title_levels[0]
        older_max = max(title_levels[2:]) if len(title_levels) > 2 else 0

        if older_max > recent_max:
            issues.append({
                "type": "title_regression",
                "message": "Recent titles appear less senior than older roles",
                "severity": "warning",
                "details": f"Recent: {titles[0]} (level {title_levels[0]}), Older: {titles[-1]} (level {title_levels[-1]})"
            })

    # Check scope escalation
    scopes = [extract_scope_signal(r) for r in roles]
    if not is_escalating(scopes):
        issues.append({
            "type": "flat_scope",
            "message": "Team/budget scope doesn't clearly grow across roles",
            "severity": "info",
            "details": f"Scopes detected: {[s for s in scopes if s is not None]}"
        })

    # Check tenure pattern
    tenures = []
    for r in roles:
        # Try to calculate tenure from dates
        start = r.get("start_date", r.get("dates", "").split(" - ")[0] if " - " in r.get("dates", "") else "")
        end = r.get("end_date", r.get("dates", "").split(" - ")[-1] if " - " in r.get("dates", "") else "")

        # Simple heuristic: if dates look short
        if "month" in str(r.get("tenure", "")).lower():
            try:
                months = int(re.search(r'(\d+)', str(r.get("tenure", ""))).group(1))
                tenures.append(months)
            except:
                tenures.append(12)  # Default
        else:
            tenures.append(12)  # Default to 1 year if unknown

    # Check for job hopping in recent roles
    short_tenure_count = sum(1 for t in tenures[:3] if t < 12)
    if short_tenure_count >= 2:
        issues.append({
            "type": "short_tenure",
            "message": "Multiple recent roles under 12 months may raise questions",
            "severity": "warning",
            "details": f"Found {short_tenure_count} roles under 1 year in last 3 positions"
        })

    # Check for gaps (would need actual dates to implement fully)
    # Placeholder for now

    return {
        "trajectory_healthy": len([i for i in issues if i["severity"] == "warning"]) == 0,
        "issues": issues,
        "title_progression": list(zip(titles, title_levels)),
        "scope_signals": [s for s in scopes if s is not None]
    }


# =============================================================================
# PHASE 2 QUESTION GENERATION
# =============================================================================
PHASE_2_TEMPLATES = {
    "scope": [
        'You mentioned "{context}" How many people were on that team?',
        'You mentioned "{context}" What was the approximate budget or scope?',
        'Can you give me a sense of the scale for "{context}"? Team size, budget, or user count?',
    ],
    "outcome": [
        'You mentioned "{context}" What specifically changed because of this? Any metrics or before/after?',
        'For "{context}" - do you have a rough sense of the impact? Even a percentage improvement?',
        'What was the measurable result of "{context}"?',
    ],
    "consequence": [
        'You mentioned "{context}" What business outcome did this drive?',
        'How did "{context}" impact the business? Revenue, costs, efficiency?',
    ],
    "comparative": [
        'For "{context}" - how did that compare to before, or to others in your company?',
        'Was the result of "{context}" above or below average for your team/company?',
    ],
    "weak_verb": [
        'You mentioned "{context}" What specifically did you do? Did you lead any part of it?',
        'For "{context}" - were you the decision-maker, or supporting someone else?',
    ],
    "verb_strength": [
        'For "{context}" - can you describe your specific role and what you personally drove?',
    ],
    "business_impact": [
        'How did "{context}" affect the business bottom line?',
        'What business metric did "{context}" improve?',
    ],
}


def generate_phase_2_question(weak_bullet: Dict[str, Any]) -> Optional[str]:
    """
    Generate a targeted question from a specific weak bullet.

    Args:
        weak_bullet: Dict with 'bullet' and 'missing' keys
    """
    bullet_text = weak_bullet.get("bullet", "")
    missing = weak_bullet.get("missing", [])

    if not missing:
        return None

    # Truncate bullet for context
    context = bullet_text[:80] + "..." if len(bullet_text) > 80 else bullet_text

    # Prioritize by signal importance
    priority_order = ['outcome', 'scope', 'weak_verb', 'consequence', 'comparative', 'verb_strength', 'business_impact']

    for signal in priority_order:
        if signal in missing and signal in PHASE_2_TEMPLATES:
            templates = PHASE_2_TEMPLATES[signal]
            return templates[0].format(context=context)

    # Default question
    return f'Can you tell me more about: "{context}"'


def generate_phase_2_questions(
    strength_assessment: Dict[str, Any],
    max_questions: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate targeted follow-up questions based on what's missing.

    Args:
        strength_assessment: Result from assess_resume_strength
        max_questions: Maximum number of questions to generate
    """
    questions = []
    weak_bullets = strength_assessment.get("weak_bullets", [])

    # Prioritize weakest bullets
    sorted_weak = sorted(weak_bullets, key=lambda x: x.get("score", 0))

    for weak in sorted_weak[:max_questions]:
        question = generate_phase_2_question(weak)
        if question:
            questions.append({
                "bullet": weak.get("bullet"),
                "score": weak.get("score"),
                "missing": weak.get("missing"),
                "question": question
            })

    return questions


# =============================================================================
# AMPLIFICATION LOOP
# =============================================================================
MAX_AMPLIFICATION_ATTEMPTS = 2


async def amplification_loop(
    weak_bullets: List[Dict[str, Any]],
    level: str,
    run_amplification_fn
) -> List[AmplifiedBullet]:
    """
    Run amplification on weak bullets with retry limit.

    Args:
        weak_bullets: List of weak bullet dicts
        level: Candidate level
        run_amplification_fn: Async function to call Claude for amplification
    """
    results = []

    for bullet_data in weak_bullets:
        bullet = bullet_data.get("bullet", "")
        attempt = 0
        current_score = bullet_data.get("score", 0)

        while attempt < MAX_AMPLIFICATION_ATTEMPTS:
            try:
                amplified = await run_amplification_fn(bullet_data, level)
                result = apply_amplification(amplified, bullet, level)

                if result.action == "apply":
                    results.append(result)
                    break
                elif result.action == "queue_for_phase_2":
                    results.append(result)
                    break

                attempt += 1
            except Exception as e:
                print(f"Amplification attempt {attempt + 1} failed: {e}")
                attempt += 1

        if attempt >= MAX_AMPLIFICATION_ATTEMPTS:
            # Couldn't elevate after max attempts
            results.append(AmplifiedBullet(
                original=bullet,
                rewritten=bullet,
                score_before=current_score,
                score_after=current_score,
                improvement=0,
                changes_made=f"Could not elevate after {MAX_AMPLIFICATION_ATTEMPTS} attempts",
                confidence="low",
                applied=False,
                action="keep_with_warning"
            ))

    return results


# =============================================================================
# AUDIT LOGGING
# =============================================================================
@dataclass
class AmplificationAuditLog:
    """Audit log entry for amplification actions."""
    session_id: str
    timestamp: datetime
    original_bullet: str
    rewritten_bullet: str
    score_before: int
    score_after: int
    missing_signals: List[str]
    changes_made: str
    confidence: str
    action_taken: str  # "applied" | "queued" | "dropped" | "kept_original"
    user_input_used: bool
    attempt_number: int


def create_audit_log(
    session_id: str,
    result: AmplifiedBullet,
    missing_signals: List[str],
    attempt_number: int,
    user_input_used: bool = False
) -> AmplificationAuditLog:
    """Create an audit log entry from an amplification result."""
    return AmplificationAuditLog(
        session_id=session_id,
        timestamp=datetime.now(),
        original_bullet=result.original,
        rewritten_bullet=result.rewritten,
        score_before=result.score_before,
        score_after=result.score_after,
        missing_signals=missing_signals,
        changes_made=result.changes_made,
        confidence=result.confidence,
        action_taken=result.action,
        user_input_used=user_input_used,
        attempt_number=attempt_number
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def run_strength_gate(
    resume: Dict[str, Any],
    level: str = "mid",
    include_trajectory: bool = True
) -> Dict[str, Any]:
    """
    Run the complete strength gate assessment on a resume.

    Args:
        resume: Parsed resume dict with 'experience' key
        level: Candidate level ('entry', 'mid', 'senior', 'director')
        include_trajectory: Whether to include trajectory assessment

    Returns:
        Complete strength assessment with recommendations
    """
    # Extract all bullets
    all_bullets = []
    for role in resume.get("experience", []):
        all_bullets.extend(role.get("bullets", []))

    # Run strength assessment
    strength = assess_resume_strength(all_bullets, level)

    # Run trajectory assessment if requested
    trajectory = None
    if include_trajectory:
        trajectory = assess_resume_trajectory(resume.get("experience", []))

    # Generate Phase 2 questions for weak bullets
    phase_2_questions = generate_phase_2_questions(strength, max_questions=3)

    # Determine overall recommendation
    if strength["avg_strength"] < 50:
        recommendation = "block"
        recommendation_message = "Resume is too weak to submit. Significant strengthening required."
    elif strength["needs_amplification"]:
        recommendation = "amplify"
        recommendation_message = "Resume needs amplification pass before submission."
    else:
        recommendation = "proceed"
        recommendation_message = "Resume meets strength threshold. Ready for submission."

    return {
        "strength_assessment": strength,
        "trajectory_assessment": trajectory,
        "phase_2_questions": phase_2_questions,
        "recommendation": recommendation,
        "recommendation_message": recommendation_message,
        "thresholds": {
            "bullet_weak": 60,
            "bullet_critical": 40,
            "resume_weak": 50,
            "resume_amplify": 65
        }
    }
