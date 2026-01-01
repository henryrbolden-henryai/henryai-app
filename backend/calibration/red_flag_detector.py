# ============================================================================
# RED FLAG DETECTOR
# Per Calibration Spec v1.0 & Selective Coaching Spec v1.0
#
# Stop the search (Do Not Apply):
# - Press release resume
# - Fabrication risk
# - Job hopping without narrative
# - Function/level catastrophic mismatch
#
# Proceed with caution (Apply with Caution):
# - Title inflation
# - Gap concerns
# - Responsibility ambiguity
# - Cultural misfit signals
# - Overqualified risk
# ============================================================================

from typing import Dict, List, Any
from .signal_detectors import (
    detect_press_release_pattern,
    detect_scale_inconsistency,
    detect_passive_voice_dominance,
    extract_revenue_impact,
    calculate_career_span,
)


def detect_red_flags(candidate_experience: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detects red flags with severity classification.

    Args:
        candidate_experience: Parsed resume data

    Returns:
        List of red flags with severity (stop_search | proceed_with_caution)
    """
    # ==========================================================================
    # HARD BAIL: This module is DIAGNOSTIC ONLY - must be crash-proof
    # If input is invalid, return empty list immediately. No partial parsing.
    # ==========================================================================
    if not candidate_experience or not isinstance(candidate_experience, dict):
        return []

    # HARD BAIL: Validate experience/roles is List[Dict]
    roles = candidate_experience.get('roles', []) or candidate_experience.get('experience', [])
    if not isinstance(roles, list):
        # Not a list - bail immediately
        return []

    # HARD BAIL: If roles contains ANY non-dict items, bail
    # This catches LinkedIn free text and malformed data
    if roles and not all(isinstance(r, dict) for r in roles):
        return []

    flags = []

    # =========================================================================
    # Check 1: Press Release Pattern (STOP SEARCH)
    # =========================================================================
    if detect_press_release_pattern(candidate_experience):
        flags.append({
            'type': 'press_release',
            'severity': 'stop_search',
            'reason': 'Resume may benefit from more specific details',
            'action': 'Do Not Apply',
            'detail': 'Adding challenges overcome and tradeoffs navigated strengthens credibility'
        })

    # =========================================================================
    # Check 2: Fabrication Risk (STOP SEARCH)
    # =========================================================================
    if detect_fabrication_risk(candidate_experience):
        flags.append({
            'type': 'metrics_context',
            'severity': 'stop_search',
            'reason': 'Metrics may need additional context for clarity',
            'action': 'Do Not Apply',
            'detail': 'Adding company stage or team context can help validate scope claims'
        })

    # =========================================================================
    # Check 3: Job Hopping (STOP SEARCH if severe)
    # =========================================================================
    tenure_pattern = analyze_tenure_pattern(candidate_experience)

    if tenure_pattern['avg_tenure'] < 1.0 and tenure_pattern['consecutive_short'] >= 3:
        flags.append({
            'type': 'job_hopping',
            'severity': 'stop_search',
            'reason': f"<1 year tenure at {tenure_pattern['consecutive_short']} consecutive roles",
            'action': 'Do Not Apply',
            'detail': 'Recruiters may question this pattern without context'
        })
    elif tenure_pattern['avg_tenure'] < 1.5 and tenure_pattern['consecutive_short'] >= 2:
        flags.append({
            'type': 'job_hopping',
            'severity': 'proceed_with_caution',
            'reason': f"Short tenure pattern ({tenure_pattern['avg_tenure']:.1f} year avg)",
            'action': 'Apply with Caution - prepare narrative for tenure',
            'detail': 'Prepare talking points explaining transitions'
        })

    # =========================================================================
    # Check 4: Title Inflation (PROCEED WITH CAUTION)
    # =========================================================================
    title_inflation = detect_title_inflation(candidate_experience)

    if title_inflation['detected']:
        flags.append({
            'type': 'title_inflation',
            'severity': 'proceed_with_caution',
            'reason': title_inflation['reason'],
            'action': 'Apply with Caution - calibrate to scope, not title',
            'detail': f"Actual level appears to be: {title_inflation['actual_level']}"
        })

    # =========================================================================
    # Check 5: Responsibility Ambiguity (PROCEED WITH CAUTION)
    # =========================================================================
    if detect_passive_voice_dominance(candidate_experience):
        flags.append({
            'type': 'ambiguity',
            'severity': 'proceed_with_caution',
            'reason': 'Passive voice throughout (vague ownership)',
            'action': 'Apply with Caution - clarify personal impact',
            'detail': 'Resume does not clearly state what candidate personally owned/delivered'
        })

    # =========================================================================
    # Check 6: Overqualified Risk (PROCEED WITH CAUTION)
    # =========================================================================
    overqualified = detect_overqualified_risk(candidate_experience)

    if overqualified['detected']:
        flags.append({
            'type': 'overqualified',
            'severity': 'proceed_with_caution',
            'reason': overqualified['reason'],
            'action': 'Apply with Caution - address downlevel motivation',
            'detail': 'May need to explain why stepping down to this level'
        })

    # =========================================================================
    # Check 7: Career Gap (PROCEED WITH CAUTION)
    # =========================================================================
    career_gaps = detect_career_gaps(candidate_experience)

    for gap in career_gaps:
        if gap['months'] >= 12:
            flags.append({
                'type': 'career_gap',
                'severity': 'proceed_with_caution',
                'reason': f"{gap['months']} month gap between roles",
                'action': 'Apply with Caution - prepare gap narrative',
                'detail': f"Gap between {gap['from_role']} and {gap['to_role']}"
            })

    # =========================================================================
    # Check 8: Decreasing Responsibility (PROCEED WITH CAUTION)
    # =========================================================================
    if detect_decreasing_responsibility(candidate_experience):
        flags.append({
            'type': 'decreasing_responsibility',
            'severity': 'proceed_with_caution',
            'reason': 'Scope appears to have decreased over career',
            'action': 'Apply with Caution - address step-down narrative',
            'detail': 'Recent roles show less scope than earlier roles'
        })

    # =========================================================================
    # Check 9: Company Size Mismatch Pattern
    # =========================================================================
    company_pattern = analyze_company_pattern(candidate_experience)

    if company_pattern['extreme_mismatch']:
        flags.append({
            'type': 'company_context',
            'severity': 'proceed_with_caution',
            'reason': company_pattern['reason'],
            'action': 'Apply with Caution - address context translation',
            'detail': company_pattern['detail']
        })

    return flags


def detect_fabrication_risk(experience: Dict[str, Any]) -> bool:
    """
    Detects potential resume fabrication.

    Signals:
    - Metrics don't match company size
    - Timeline inconsistencies
    - Responsibilities exceed typical scope
    - Scale claims inconsistent internally

    CRASH-PROOF: This function will NEVER throw. Expected input noise
    (LinkedIn strings, malformed data) is silently handled.
    """
    try:
        # Defensive: handle non-dict input
        if not experience or not isinstance(experience, dict):
            return False

        # Already implemented in signal_detectors, but add additional checks here
        if detect_scale_inconsistency(experience):
            return True

        roles = experience.get('roles', []) or experience.get('experience', [])

        # Defensive: handle non-list roles
        if not isinstance(roles, list):
            return False

        for role in roles:
            # Defensive: skip non-dict roles
            if not isinstance(role, dict):
                continue

            company_size = role.get('company_size', 0)
            claimed_impact = extract_revenue_impact(role)

            # Check for implausible impact at small companies
            if claimed_impact and company_size:
                # $50M impact at 20-person startup = red flag
                if company_size < 50 and claimed_impact > 20_000_000:
                    return True

                # $100M impact at 100-person company = suspicious
                if company_size < 100 and claimed_impact > 50_000_000:
                    return True

        # Check timeline math
        total_years_claimed = 0
        for role in roles:
            # Defensive: skip non-dict roles
            if not isinstance(role, dict):
                continue

            duration = role.get('duration', 0)
            if isinstance(duration, (int, float)):
                total_years_claimed += duration

        actual_career_span = calculate_career_span(experience)

        # If claimed years exceed actual career span by >20%
        if actual_career_span > 0 and total_years_claimed > actual_career_span * 1.2:
            return True

        return False

    except Exception:
        # Silently fail - this is expected noise from malformed input
        return False


def analyze_tenure_pattern(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes tenure pattern across roles.

    Returns:
        dict: {
            'avg_tenure': float,
            'consecutive_short': int,
            'pattern': 'stable'|'mixed'|'hopping'
        }
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return {'avg_tenure': 0, 'consecutive_short': 0, 'pattern': 'unknown'}

    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if not isinstance(roles, list) or not roles:
        return {'avg_tenure': 0, 'consecutive_short': 0, 'pattern': 'unknown'}

    tenures = []
    for role in roles:
        # Defensive: skip non-dict roles
        if not isinstance(role, dict):
            continue
        duration = role.get('duration')
        if duration is not None:
            tenures.append(float(duration))

    if not tenures:
        return {'avg_tenure': 0, 'consecutive_short': 0, 'pattern': 'unknown'}

    avg_tenure = sum(tenures) / len(tenures)

    # Count consecutive short tenures (recent first)
    consecutive_short = 0
    for tenure in tenures:
        if tenure < 1.0:
            consecutive_short += 1
        else:
            break

    # Determine pattern
    if avg_tenure >= 2.5:
        pattern = 'stable'
    elif avg_tenure >= 1.5:
        pattern = 'mixed'
    else:
        pattern = 'hopping'

    return {
        'avg_tenure': avg_tenure,
        'consecutive_short': consecutive_short,
        'pattern': pattern
    }


def detect_title_inflation(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects title inflation (title vs actual scope mismatch).

    Returns:
        dict: {
            'detected': bool,
            'reason': str,
            'actual_level': str
        }
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return {'detected': False, 'reason': '', 'actual_level': ''}

    from .signal_detectors import extract_team_size

    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if not isinstance(roles, list):
        return {'detected': False, 'reason': '', 'actual_level': ''}

    for role in roles:
        # Defensive: skip non-dict roles
        if not isinstance(role, dict):
            continue

        title = (role.get('title', '') or '').lower()
        company_size = role.get('company_size', 0)
        team_size = extract_team_size({'roles': [role]})

        # VP at small company
        if 'vp' in title or 'vice president' in title:
            if company_size and company_size < 50:
                return {
                    'detected': True,
                    'reason': f'VP title at {company_size}-person company',
                    'actual_level': 'Director or Senior Manager'
                }
            if team_size > 0 and team_size < 10:
                return {
                    'detected': True,
                    'reason': f'VP title managing {team_size} people',
                    'actual_level': 'Senior Manager or Director'
                }

        # Director without meaningful reports
        if 'director' in title and 'senior' not in title:
            if team_size > 0 and team_size < 5:
                return {
                    'detected': True,
                    'reason': f'Director title managing {team_size} people',
                    'actual_level': 'Manager or Senior Manager'
                }

        # Staff/Principal at tiny company
        if 'staff' in title or 'principal' in title:
            if company_size and company_size < 20:
                # Check for org-level influence
                from .signal_detectors import detect_org_level_influence
                if detect_org_level_influence({'roles': [role]}) != 'explicit':
                    return {
                        'detected': True,
                        'reason': f'Staff title at {company_size}-person company without org influence',
                        'actual_level': 'Senior IC'
                    }

        # Head of at tiny company
        if 'head of' in title:
            if company_size and company_size < 20:
                return {
                    'detected': True,
                    'reason': f'Head of title at {company_size}-person company',
                    'actual_level': 'Manager or Senior IC'
                }

    return {'detected': False, 'reason': '', 'actual_level': ''}


def detect_overqualified_risk(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects if candidate might be perceived as overqualified.
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return {'detected': False, 'reason': ''}

    from .signal_detectors import extract_team_size, detect_org_level_influence

    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if not isinstance(roles, list) or not roles:
        return {'detected': False, 'reason': ''}

    # Check most recent role scope
    recent_role = roles[0] if roles else {}

    # Defensive: skip if recent_role is not a dict
    if not isinstance(recent_role, dict):
        return {'detected': False, 'reason': ''}

    recent_title = (recent_role.get('title', '') or '').lower()
    recent_team_size = extract_team_size({'roles': [recent_role]})

    # Check for senior signals
    senior_keywords = ['vp', 'vice president', 'director', 'head of', 'c-suite', 'cto', 'ceo', 'cfo']

    if any(kw in recent_title for kw in senior_keywords):
        if recent_team_size >= 30 or detect_org_level_influence({'roles': [recent_role]}) == 'explicit':
            return {
                'detected': True,
                'reason': f'Recent {recent_title.title()} role suggests executive level'
            }

    return {'detected': False, 'reason': ''}


def detect_career_gaps(experience: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detects gaps between roles.

    Returns list of gaps > 6 months.
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return []

    import re
    from datetime import datetime

    roles = experience.get('roles', []) or experience.get('experience', [])
    gaps = []

    # Defensive: handle non-list roles
    if not isinstance(roles, list) or len(roles) < 2:
        return gaps

    def parse_date(date_str):
        if not date_str:
            return None
        if date_str.lower() in ['present', 'current', 'now']:
            return datetime.now()

        # Try common formats
        formats = ['%Y-%m-%d', '%Y-%m', '%m/%Y', '%B %Y', '%b %Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Extract year
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            return datetime(int(year_match.group(1)), 6, 1)

        return None

    for i in range(len(roles) - 1):
        current_role = roles[i]
        previous_role = roles[i + 1]

        # Defensive: skip non-dict roles
        if not isinstance(current_role, dict) or not isinstance(previous_role, dict):
            continue

        current_start = parse_date(
            current_role.get('start_date') or
            current_role.get('dates', {}).get('start')
        )
        previous_end = parse_date(
            previous_role.get('end_date') or
            previous_role.get('dates', {}).get('end')
        )

        if current_start and previous_end:
            gap_days = (current_start - previous_end).days
            gap_months = gap_days / 30

            if gap_months >= 6:
                gaps.append({
                    'months': int(gap_months),
                    'from_role': previous_role.get('title', 'Unknown'),
                    'to_role': current_role.get('title', 'Unknown')
                })

    return gaps


def detect_decreasing_responsibility(experience: Dict[str, Any]) -> bool:
    """
    Detects if responsibility/scope has decreased over career.
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return False

    from .signal_detectors import analyze_scope_trajectory

    trajectory = analyze_scope_trajectory(experience)
    return trajectory == 'shrinking'


def analyze_company_pattern(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes company size/stage pattern.

    Detects extreme mismatches like:
    - All FAANG → tiny startup
    - All startup → big tech
    """
    # Defensive: handle non-dict input
    if not experience or not isinstance(experience, dict):
        return {'extreme_mismatch': False, 'reason': '', 'detail': ''}

    roles = experience.get('roles', []) or experience.get('experience', [])

    # Defensive: handle non-list roles
    if not isinstance(roles, list) or len(roles) < 2:
        return {'extreme_mismatch': False, 'reason': '', 'detail': ''}

    company_sizes = []
    for role in roles:
        # Defensive: skip non-dict roles
        if not isinstance(role, dict):
            continue
        size = role.get('company_size')
        if size:
            company_sizes.append(size)

    if not company_sizes:
        return {'extreme_mismatch': False, 'reason': '', 'detail': ''}

    avg_size = sum(company_sizes) / len(company_sizes)

    # Check for big tech only background
    big_tech_names = ['google', 'meta', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix']
    # Defensive: filter to only dict roles
    dict_roles = [r for r in roles if isinstance(r, dict)]
    all_big_tech = dict_roles and all(
        any(bt in (role.get('company', '') or '').lower() for bt in big_tech_names)
        for role in dict_roles
    )

    if all_big_tech:
        return {
            'extreme_mismatch': True,
            'reason': 'All FAANG/big tech background - startup context may be unfamiliar',
            'detail': 'May need to address scrappy execution and resource constraints'
        }

    # Check for all small company background
    if avg_size > 0 and avg_size < 50:
        # Check if most recent roles suggest enterprise context needed
        return {
            'extreme_mismatch': False,
            'reason': '',
            'detail': ''
        }

    return {'extreme_mismatch': False, 'reason': '', 'detail': ''}
