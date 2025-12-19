# ============================================================================
# SIGNAL DETECTORS
# Per Calibration Spec v1.0: Core helper functions for evidence detection
#
# These functions extract structured signals from resume/experience text
# to enable recruiter-grade gap classification.
# ============================================================================

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


def extract_team_size(experience: Dict[str, Any]) -> int:
    """
    Extracts team size from resume text.

    Patterns:
    - "managed 12 engineers"
    - "led team of 20"
    - "15-person org"
    - "team of 8 direct reports"

    Returns: int (0 if not found)
    """
    if not experience:
        return 0

    # Build combined text from experience
    combined_text = _build_experience_text(experience).lower()

    # Team size patterns (ordered by specificity)
    patterns = [
        r'(?:managed|led|oversaw|supervised)\s+(?:a\s+)?(?:team\s+of\s+)?(\d+)\s*(?:\+)?\s*(?:engineers?|developers?|people|reports?|members?|ics?)',
        r'team\s+of\s+(\d+)\s*(?:\+)?\s*(?:engineers?|developers?|people|reports?|members?)?',
        r'(\d+)\s*(?:\+)?\s*(?:direct\s+)?reports?',
        r'(\d+)\s*-?\s*person\s+(?:team|org|organization)',
        r'managed\s+(\d+)\s*(?:\+)?\s*(?:engineers?|developers?|people)?',
        r'led\s+(\d+)\s*(?:\+)?\s*(?:engineers?|developers?|people)?',
        r'org\s+of\s+(\d+)',
        r'organization\s+of\s+(\d+)',
    ]

    max_size = 0
    for pattern in patterns:
        matches = re.findall(pattern, combined_text)
        for match in matches:
            try:
                size = int(match)
                if size > max_size and size < 10000:  # Sanity check
                    max_size = size
            except (ValueError, TypeError):
                continue

    return max_size


def extract_scope_signals(experience: Dict[str, Any]) -> Dict[str, str]:
    """
    Detects scope indicators across multiple dimensions.

    Dimensions:
    - Geographic: local, regional, national, global
    - Organizational: team, department, company-wide, multi-company
    - Product: feature, product, platform, ecosystem

    Returns: dict with scope level for each dimension
    """
    combined_text = _build_experience_text(experience).lower()

    # Geographic scope
    geographic_levels = {
        'global': ['global', 'worldwide', 'international', 'multi-region', 'across regions',
                   'emea', 'apac', 'americas', 'multiple countries'],
        'national': ['national', 'country-wide', 'us-wide', 'nationwide'],
        'regional': ['regional', 'multi-office', 'multiple offices', 'cross-office'],
        'local': ['local', 'single office', 'on-site', 'co-located']
    }

    # Organizational scope
    org_levels = {
        'company-wide': ['company-wide', 'org-wide', 'enterprise', 'across the company',
                         'all teams', 'entire organization', 'company strategy'],
        'multi-department': ['multi-department', 'cross-org', 'multiple departments',
                             'across departments', 'cross-functional org'],
        'department': ['department', 'division', 'business unit', 'org'],
        'team': ['team', 'squad', 'pod', 'group']
    }

    # Product scope
    product_levels = {
        'ecosystem': ['ecosystem', 'suite', 'platform of platforms', 'portfolio'],
        'platform': ['platform', 'infrastructure', 'foundational', 'core system'],
        'product': ['product', 'application', 'service', 'offering'],
        'feature': ['feature', 'component', 'module', 'improvement']
    }

    def detect_level(levels_dict: Dict[str, List[str]]) -> str:
        for level, keywords in levels_dict.items():
            if any(kw in combined_text for kw in keywords):
                return level
        return 'unknown'

    return {
        'geographic': detect_level(geographic_levels),
        'organizational': detect_level(org_levels),
        'product': detect_level(product_levels)
    }


def detect_org_level_influence(experience: Dict[str, Any]) -> str:
    """
    Detects evidence of org-level (vs team-level) influence.

    Returns: 'explicit'|'implicit'|'missing'

    Explicit: "Defined engineering strategy for org", "Set technical direction company-wide"
    Implicit: "Influenced architecture decisions across teams"
    Missing: No evidence of cross-team/org impact
    """
    combined_text = _build_experience_text(experience).lower()

    # Explicit org-level influence signals
    explicit_patterns = [
        r'defined\s+(?:engineering|technical|product)\s+strategy\s+(?:for|across)\s+(?:the\s+)?org',
        r'set\s+(?:technical|engineering|product)\s+direction\s+(?:company|org)',
        r'org-?wide\s+(?:impact|influence|initiative)',
        r'company-?wide\s+(?:strategy|direction|initiative)',
        r'led\s+(?:engineering|technical)\s+strategy',
        r'established\s+(?:engineering|technical)\s+standards\s+(?:for|across)',
        r'technical\s+vision\s+(?:for|across)\s+(?:the\s+)?(?:org|company)',
    ]

    for pattern in explicit_patterns:
        if re.search(pattern, combined_text):
            return 'explicit'

    # Explicit keywords
    explicit_keywords = [
        'org-wide impact', 'company-wide strategy', 'set technical direction',
        'engineering strategy', 'technical vision', 'org-level', 'company-level',
        'enterprise architecture', 'chief architect', 'principal architect'
    ]

    if any(kw in combined_text for kw in explicit_keywords):
        return 'explicit'

    # Implicit signals
    implicit_keywords = [
        'influenced architecture', 'cross-team', 'across teams', 'multiple teams',
        'platform', 'infrastructure', 'shared services', 'common framework',
        'technical standards', 'best practices', 'mentored across'
    ]

    if any(kw in combined_text for kw in implicit_keywords):
        return 'implicit'

    return 'missing'


def has_upward_trajectory(experience: Dict[str, Any]) -> bool:
    """
    Checks if scope is growing over time (promotion trajectory).

    Looks for:
    - Title progression (Engineer → Senior → Staff)
    - Scope expansion (team → org)
    - Increasing responsibility signals

    Returns: bool
    """
    # Defensive: handle non-dict experience
    if not experience or not isinstance(experience, dict):
        return False

    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if not isinstance(roles, list):
        return False

    if len(roles) < 2:
        return False

    # Level hierarchy (lower = more senior)
    level_ranks = {
        'intern': 10, 'junior': 9, 'associate': 8,
        'mid': 7, 'engineer': 7, 'ic3': 7,
        'senior': 5, 'ic4': 5,
        'staff': 4, 'principal': 4, 'ic5': 4,
        'lead': 3, 'architect': 3, 'ic6': 3,
        'manager': 3, 'engineering manager': 3,
        'senior manager': 2, 'director': 2,
        'senior director': 1, 'vp': 1, 'vice president': 1,
        'svp': 0, 'c-suite': 0, 'cto': 0, 'ceo': 0
    }

    def get_level_rank(title: str) -> int:
        title_lower = title.lower() if title else ''
        for level, rank in level_ranks.items():
            if level in title_lower:
                return rank
        return 7  # Default to mid-level

    # Check if titles show progression (decreasing rank = more senior)
    # Defensive: skip non-dict roles
    ranks = [get_level_rank(role.get('title', '')) for role in roles if isinstance(role, dict)]

    if len(ranks) < 2:
        return False

    # Roles are typically listed newest first, so we reverse
    ranks_chronological = list(reversed(ranks))

    # Check for overall upward trend
    improvements = 0
    for i in range(1, len(ranks_chronological)):
        if ranks_chronological[i] < ranks_chronological[i-1]:
            improvements += 1

    return improvements >= len(ranks_chronological) // 2


def calculate_career_span(roles_or_experience) -> float:
    """
    Returns years between first and last role.

    BULLETPROOF: This function normalizes at the boundary.
    It will NEVER crash regardless of what caller passes in.

    Accepts either:
    - Dict with 'roles' or 'experience' key
    - List of role dicts directly
    - Anything else returns 0.0
    """
    # ==========================================================================
    # SELF-SEALING FUNCTION BOUNDARY - FIRST LINES, NO EXCEPTIONS
    # This function must handle ANY input without crashing.
    # ==========================================================================

    # Step 1: Extract roles list from whatever we received
    if isinstance(roles_or_experience, list):
        roles = roles_or_experience
    elif isinstance(roles_or_experience, dict):
        roles = roles_or_experience.get('roles', []) or roles_or_experience.get('experience', [])
    else:
        # Not a list or dict - bail immediately
        return 0.0

    # Step 2: Ensure roles is actually a list
    if not isinstance(roles, list):
        return 0.0

    # Step 3: Filter to ONLY dict items - this catches LinkedIn string roles
    roles = [r for r in roles if isinstance(r, dict)]
    if not roles:
        return 0.0

    # ==========================================================================
    # SAFE TO ITERATE - roles is guaranteed List[Dict] at this point
    # ==========================================================================

    dates = []
    for role in roles:
        # role is GUARANTEED to be a dict at this point
        start_date = role.get('start_date') or role.get('dates', {}).get('start')
        end_date = role.get('end_date') or role.get('dates', {}).get('end')

        if start_date:
            dates.append(_parse_date(start_date))
        if end_date and isinstance(end_date, str) and end_date.lower() != 'present':
            dates.append(_parse_date(end_date))

    # Filter out None dates
    dates = [d for d in dates if d is not None]

    if len(dates) < 2:
        return 0.0

    min_date = min(dates)
    max_date = max(dates)

    years = (max_date - min_date).days / 365.25
    return round(years, 1)


def extract_revenue_impact(role: Dict[str, Any]) -> Optional[float]:
    """
    Extracts claimed revenue impact from role.

    Patterns:
    - "$50M ARR"
    - "$10 million in revenue"
    - "drove $25M growth"

    Returns: float (dollars) or None
    """
    text = _build_role_text(role).lower()

    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(?:m|million)\s*(?:arr|revenue|growth|impact)?',
        r'\$(\d+(?:\.\d+)?)\s*(?:b|billion)',
        r'(\d+(?:\.\d+)?)\s*(?:m|million)\s*(?:\$|dollars?)',
        r'drove\s*\$?(\d+(?:\.\d+)?)\s*(?:m|million)',
        r'generated\s*\$?(\d+(?:\.\d+)?)\s*(?:m|million)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                value = float(match.group(1))
                # Convert to dollars
                if 'billion' in text or 'b' in pattern:
                    return value * 1_000_000_000
                else:
                    return value * 1_000_000
            except (ValueError, TypeError):
                continue

    return None


def detect_ownership_level(experience: Dict[str, Any]) -> str:
    """
    Detects ownership language level in resume.

    Returns: 'explicit'|'implicit'|'missing'

    Explicit: "Owned", "led", "built", "designed", "architected"
    Implicit: "Contributed to", "helped", "supported", "worked on"
    Missing: No ownership language at all
    """
    combined_text = _build_experience_text(experience).lower()

    # Explicit ownership signals
    explicit_keywords = [
        'owned', 'led', 'built', 'designed', 'architected', 'created',
        'launched', 'established', 'founded', 'drove', 'spearheaded',
        'delivered', 'shipped', 'implemented', 'developed', 'executed'
    ]

    # Implicit (contributor) signals
    implicit_keywords = [
        'contributed to', 'helped', 'supported', 'assisted', 'worked on',
        'participated in', 'was part of', 'collaborated on', 'involved in',
        'member of', 'joined'
    ]

    # Check for explicit first
    explicit_count = sum(1 for kw in explicit_keywords if kw in combined_text)
    implicit_count = sum(1 for kw in implicit_keywords if kw in combined_text)

    if explicit_count >= 3:
        return 'explicit'
    elif explicit_count >= 1:
        return 'implicit' if implicit_count > explicit_count else 'explicit'
    elif implicit_count >= 1:
        return 'implicit'
    else:
        return 'missing'


def analyze_scope_trajectory(experience: Dict[str, Any]) -> str:
    """
    Analyzes scope trajectory over career.

    Returns: 'growing'|'flat'|'shrinking'

    Growing: Scope increasing, complexity rising, impact expanding
    Flat: Repeating same level, no responsibility increase
    Shrinking: Step-downs, reduced responsibility
    """
    roles = experience.get('roles', []) or experience.get('experience', [])
    if not roles or len(roles) < 2:
        return 'flat'

    def estimate_scope(role: Dict[str, Any]) -> int:
        """Estimate scope level 1-10 based on signals."""
        text = _build_role_text(role).lower()
        score = 5  # Default

        # Team size signals
        team_size = extract_team_size({'roles': [role]})
        if team_size >= 50:
            score += 3
        elif team_size >= 20:
            score += 2
        elif team_size >= 5:
            score += 1

        # Scope keywords
        if any(kw in text for kw in ['global', 'company-wide', 'org-wide']):
            score += 2
        if any(kw in text for kw in ['platform', 'infrastructure', 'enterprise']):
            score += 1
        if any(kw in text for kw in ['feature', 'component', 'module']):
            score -= 1

        # Title signals
        title = role.get('title', '').lower()
        if any(kw in title for kw in ['vp', 'director', 'head']):
            score += 2
        elif any(kw in title for kw in ['staff', 'principal', 'senior manager']):
            score += 1
        elif any(kw in title for kw in ['junior', 'associate', 'intern']):
            score -= 2

        return max(1, min(10, score))

    # Calculate scope for each role (newest first typically)
    scopes = [estimate_scope(role) for role in roles]

    # Reverse to chronological order
    scopes_chronological = list(reversed(scopes))

    # Analyze trajectory
    growth_count = 0
    shrink_count = 0

    for i in range(1, len(scopes_chronological)):
        diff = scopes_chronological[i] - scopes_chronological[i-1]
        if diff > 0:
            growth_count += 1
        elif diff < 0:
            shrink_count += 1

    if growth_count > shrink_count and growth_count >= len(scopes_chronological) // 2:
        return 'growing'
    elif shrink_count > growth_count:
        return 'shrinking'
    else:
        return 'flat'


def detect_tool_obsession(experience: Dict[str, Any]) -> bool:
    """
    Detects if resume is optimized for ATS with tool lists but no problem-solving context.

    Red flags:
    - Long lists of technologies without context
    - Skills dump without application examples
    - No "why" or impact for technical choices

    Returns: bool
    """
    combined_text = _build_experience_text(experience)

    # Count technology/tool mentions vs problem-solving language
    tool_patterns = [
        r'(?:python|java|javascript|react|node|kubernetes|docker|aws|gcp|azure)',
        r'(?:sql|nosql|mongodb|postgresql|redis|elasticsearch)',
        r'(?:jenkins|terraform|ansible|github|gitlab|jira)',
    ]

    problem_solving_keywords = [
        'solved', 'improved', 'reduced', 'increased', 'optimized',
        'because', 'in order to', 'to achieve', 'resulting in',
        'led to', 'enabled', 'by implementing'
    ]

    tool_count = sum(len(re.findall(p, combined_text.lower())) for p in tool_patterns)
    problem_count = sum(1 for kw in problem_solving_keywords if kw in combined_text.lower())

    # Red flag: many tools, few problem-solving indicators
    if tool_count >= 15 and problem_count < 3:
        return True

    # Check for comma-separated tool dumps
    tool_dump_pattern = r'(?:\w+,\s*){5,}\w+'  # 5+ comma-separated items
    if re.search(tool_dump_pattern, combined_text):
        # Ensure it's not just a description
        if problem_count < 5:
            return True

    return False


def detect_sales_motion(experience: Dict[str, Any]) -> str:
    """
    Detects sales motion from experience.

    Returns: 'Transactional'|'Mid-Market'|'Enterprise'|'Unknown'

    Signals:
    - Deal size (ACV)
    - Sales cycle length
    - Stakeholder complexity (single buyer vs committee)
    """
    combined_text = _build_experience_text(experience).lower()

    # Enterprise signals
    enterprise_keywords = [
        'enterprise', 'fortune 500', 'f500', 'large accounts',
        'c-suite', 'cxo', 'executive sponsors', 'multi-stakeholder',
        'complex deals', '6-12 month', 'year-long', '$100k+', '$1m+',
        'strategic accounts', 'named accounts', 'territory'
    ]

    # Mid-market signals
    mid_market_keywords = [
        'mid-market', 'smb', 'small business', 'growing companies',
        '$25k', '$50k', '3-6 month', 'quick sales', 'department heads',
        'vp-level buyers'
    ]

    # Transactional signals
    transactional_keywords = [
        'transactional', 'high-velocity', 'volume', 'inbound',
        'self-serve', 'product-led', 'plg', 'short cycle',
        '$5k', '$10k', 'monthly', 'instant close'
    ]

    # Check for ACV mentions
    acv_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(?:k|K|thousand)?\s*(?:acv|deal|contract)', combined_text)
    if acv_match:
        acv = float(acv_match.group(1))
        if 'k' in combined_text[acv_match.start():acv_match.end()].lower():
            acv *= 1000

        if acv >= 100000:
            return 'Enterprise'
        elif acv >= 25000:
            return 'Mid-Market'
        else:
            return 'Transactional'

    # Keyword-based detection
    enterprise_score = sum(1 for kw in enterprise_keywords if kw in combined_text)
    mid_market_score = sum(1 for kw in mid_market_keywords if kw in combined_text)
    transactional_score = sum(1 for kw in transactional_keywords if kw in combined_text)

    max_score = max(enterprise_score, mid_market_score, transactional_score)

    if max_score == 0:
        return 'Unknown'
    elif enterprise_score == max_score:
        return 'Enterprise'
    elif mid_market_score == max_score:
        return 'Mid-Market'
    else:
        return 'Transactional'


def extract_metrics(experience: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts quantified metrics from experience.

    Returns: List of {metric, value, context}
    """
    combined_text = _build_experience_text(experience)
    metrics = []

    # Revenue/ARR patterns
    revenue_patterns = [
        (r'\$(\d+(?:\.\d+)?)\s*(?:m|M|million)(?:\s*(?:arr|revenue|growth))?', 'revenue', 'millions'),
        (r'\$(\d+(?:\.\d+)?)\s*(?:b|B|billion)', 'revenue', 'billions'),
        (r'(\d+(?:\.\d+)?)\s*%\s*(?:growth|increase|improvement)', 'growth_rate', 'percentage'),
        (r'(\d+(?:\.\d+)?)\s*x\s*(?:growth|increase|improvement)', 'multiplier', 'times'),
    ]

    # Performance patterns
    perf_patterns = [
        (r'(\d+)\s*%\s*quota', 'quota_attainment', 'percentage'),
        (r'top\s*(\d+)\s*%', 'ranking', 'percentile'),
        (r'(\d+)\s*(?:deals?|accounts?)', 'deal_count', 'count'),
    ]

    for pattern, metric_type, unit in revenue_patterns + perf_patterns:
        matches = re.finditer(pattern, combined_text, re.IGNORECASE)
        for match in matches:
            try:
                value = float(match.group(1))
                context = combined_text[max(0, match.start()-50):match.end()+50]
                metrics.append({
                    'type': metric_type,
                    'value': value,
                    'unit': unit,
                    'context': context.strip()
                })
            except (ValueError, TypeError):
                continue

    return metrics


def has_metric_context(metrics: List[Dict[str, Any]]) -> bool:
    """
    Checks if metrics have proper context (quota size, territory, market).

    Metrics without context are red flags (unverifiable claims).

    Returns: bool
    """
    if not metrics:
        return True  # No metrics = no context issue

    context_keywords = [
        'territory', 'quota', 'market', 'segment', 'region',
        'team', 'company', 'industry', 'against', 'compared to',
        'of a', 'out of', 'baseline', 'benchmark'
    ]

    contextualized = 0
    for metric in metrics:
        context = metric.get('context', '').lower()
        if any(kw in context for kw in context_keywords):
            contextualized += 1

    # At least half of metrics should have context
    return contextualized >= len(metrics) / 2


def detect_passive_voice_dominance(experience: Dict[str, Any]) -> bool:
    """
    Detects if resume uses predominantly passive voice (vague ownership).

    Passive patterns suggest ambiguity about personal contribution.

    Returns: bool
    """
    combined_text = _build_experience_text(experience).lower()

    # Passive voice indicators
    passive_patterns = [
        r'was\s+(?:involved|responsible|tasked|assigned)',
        r'was\s+\w+ed\s+(?:by|to|for)',
        r'were\s+(?:developed|created|implemented)',
        r'has\s+been\s+\w+ed',
        r'it\s+was\s+decided',
        r'the\s+team\s+(?:developed|built|created)',
    ]

    # Active voice indicators
    active_keywords = [
        'i led', 'i built', 'i designed', 'i owned', 'i drove',
        'i implemented', 'i created', 'i developed', 'i managed'
    ]

    passive_count = sum(len(re.findall(p, combined_text)) for p in passive_patterns)
    active_count = sum(1 for kw in active_keywords if kw in combined_text)

    # Also count general passive signals
    passive_keywords = [
        'was responsible for', 'was involved in', 'was part of',
        'was tasked with', 'was assigned to'
    ]
    passive_count += sum(1 for kw in passive_keywords if kw in combined_text)

    # Red flag: passive >> active
    return passive_count > active_count * 2 and passive_count >= 3


def detect_manager_of_managers(experience: Dict[str, Any]) -> bool:
    """
    Detects evidence of managing other managers (Tier 3+ leadership).

    Returns: bool
    """
    combined_text = _build_experience_text(experience).lower()

    mom_keywords = [
        'manager of managers', 'managed managers', 'led managers',
        'managed directors', 'director reports', 'managed leads',
        'led leads', 'managers reporting', 'directors reporting',
        'org of', 'organization of', 'skip-level', 'second-line',
        'managed engineering managers', 'managed product managers'
    ]

    return any(kw in combined_text for kw in mom_keywords)


def is_ic_to_leadership_transition(experience: Dict[str, Any]) -> bool:
    """
    Detects if candidate is transitioning from IC to leadership role.

    Returns: bool
    """
    roles = experience.get('roles', []) or experience.get('experience', [])
    if not roles or len(roles) < 2:
        return False

    # Check most recent role for leadership signals
    recent_role = roles[0] if roles else {}
    recent_title = recent_role.get('title', '').lower()

    # Check previous roles for IC signals
    previous_titles = [r.get('title', '').lower() for r in roles[1:]]

    ic_keywords = ['engineer', 'developer', 'analyst', 'specialist', 'consultant']
    leadership_keywords = ['manager', 'director', 'head', 'lead', 'vp']

    recent_is_leadership = any(kw in recent_title for kw in leadership_keywords)
    previous_is_ic = any(
        any(kw in title for kw in ic_keywords) and
        not any(lk in title for lk in leadership_keywords)
        for title in previous_titles
    )

    return recent_is_leadership and previous_is_ic


def detect_press_release_pattern(experience: Dict[str, Any]) -> bool:
    """
    Detects "press release resume" pattern.

    Red flags:
    - No failures or setbacks mentioned
    - Every initiative succeeded
    - No tension or tradeoffs described
    - Vague ownership without specifics

    Returns: bool
    """
    combined_text = _build_experience_text(experience).lower()

    # Signs of real experience (failures, tradeoffs, specifics)
    reality_keywords = [
        'failed', 'learned', 'pivoted', 'tradeoff', 'trade-off',
        'challenge', 'difficult', 'obstacle', 'despite', 'although',
        'limitation', 'constraint', 'balanced', 'prioritized',
        'deprioritized', 'cut', 'reduced scope', 'phased'
    ]

    # Overly positive/vague language
    pr_keywords = [
        'spearheaded', 'revolutionized', 'transformed', 'pioneered',
        'world-class', 'best-in-class', 'cutting-edge', 'state-of-the-art',
        'innovative', 'groundbreaking', 'game-changing'
    ]

    reality_count = sum(1 for kw in reality_keywords if kw in combined_text)
    pr_count = sum(1 for kw in pr_keywords if kw in combined_text)

    # Also check for metric specificity
    metrics = extract_metrics(experience)
    has_specific_metrics = any(
        m.get('context') and len(m.get('context', '')) > 30
        for m in metrics
    )

    # Press release pattern: lots of PR language, no reality signals
    if pr_count >= 3 and reality_count == 0:
        return True

    # Or: many claims, no specifics
    if pr_count >= 2 and not has_specific_metrics and reality_count < 2:
        return True

    return False


def detect_scale_inconsistency(experience: Dict[str, Any]) -> bool:
    """
    Detects scale claims inconsistent with company size/stage.

    Examples of inconsistency:
    - "Global platform" at 10-person company
    - "$50M ARR impact" at early-stage startup
    - "Enterprise GTM" with $50K ACV

    Returns: bool
    """
    roles = experience.get('roles', []) or experience.get('experience', [])

    for role in roles:
        text = _build_role_text(role).lower()
        company_size = role.get('company_size', 0)

        # If company size is known, check for inconsistencies
        if company_size and company_size < 50:
            # Small company claiming enterprise scale
            if any(kw in text for kw in ['enterprise', 'global platform', 'worldwide']):
                return True

        if company_size and company_size < 20:
            # Tiny company claiming massive impact
            revenue_impact = extract_revenue_impact(role)
            if revenue_impact and revenue_impact > 10_000_000:  # $10M+
                return True

        # Check for stage inconsistencies
        if 'seed' in text or 'series a' in text or 'early-stage' in text:
            if any(kw in text for kw in ['$50m', '$100m', 'billion', 'enterprise-wide']):
                return True

    return False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _build_experience_text(experience: Dict[str, Any]) -> str:
    """Build combined text from experience dict."""
    if not experience:
        return ""

    # Defensive: handle string input
    if isinstance(experience, str):
        return experience

    # Defensive: handle non-dict input
    if not isinstance(experience, dict):
        return str(experience)

    parts = []

    # Handle roles/experience list
    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if isinstance(roles, str):
        parts.append(roles)
    elif isinstance(roles, list):
        for role in roles:
            # Defensive: skip non-dict roles
            if isinstance(role, dict):
                parts.append(_build_role_text(role))
            elif isinstance(role, str):
                parts.append(role)

    # Handle summary
    if experience.get('summary'):
        parts.append(str(experience.get('summary')))

    # Handle skills
    if experience.get('skills'):
        if isinstance(experience.get('skills'), list):
            parts.append(' '.join(str(s) for s in experience.get('skills')))
        else:
            parts.append(str(experience.get('skills')))

    return ' '.join(parts)


def _build_role_text(role: Dict[str, Any]) -> str:
    """Build text from a single role dict."""
    if not role:
        return ""

    # Defensive: handle string input
    if isinstance(role, str):
        return role

    # Defensive: handle non-dict input
    if not isinstance(role, dict):
        return str(role)

    parts = []

    if role.get('title'):
        parts.append(str(role.get('title')))
    if role.get('company'):
        parts.append(str(role.get('company')))
    if role.get('description'):
        parts.append(str(role.get('description')))

    # Handle bullets/highlights
    bullets = role.get('highlights', []) or role.get('bullets', [])
    if isinstance(bullets, str):
        parts.append(bullets)
    elif isinstance(bullets, list):
        parts.extend(str(b) for b in bullets if b)

    return ' '.join(parts)


def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None

    # Handle "present"
    if date_str.lower() in ['present', 'current', 'now']:
        return datetime.now()

    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m',
        '%m/%Y',
        '%Y',
        '%B %Y',
        '%b %Y',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Try extracting year
    year_match = re.search(r'(\d{4})', date_str)
    if year_match:
        return datetime(int(year_match.group(1)), 1, 1)

    return None
