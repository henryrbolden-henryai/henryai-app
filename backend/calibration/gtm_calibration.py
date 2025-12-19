# ============================================================================
# GTM CALIBRATION
# Per Calibration Spec v1.0: Calibrates Sales, CS, BizDev roles
#
# Sales motions:
# - Transactional: <$25K ACV, <3 month cycle
# - Mid-Market: $25K-$100K ACV, 3-6 month cycle
# - Enterprise: $100K+ ACV, 6-12+ month cycle
# ============================================================================

from typing import Dict, List, Any
from .signal_detectors import (
    detect_sales_motion,
    extract_metrics,
    has_metric_context,
    detect_ownership_level,
    has_upward_trajectory,
)


def calibrate_gtm_role(
    candidate_experience: Dict[str, Any],
    role_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calibrates Sales, CS, BizDev roles with motion understanding.

    Args:
        candidate_experience: Parsed resume data with roles/experience
        role_requirements: Job requirements including sales_motion, etc.

    Returns:
        dict: {
            'actual_motion': str,
            'terminal_gaps': list,
            'coachable_gaps': list,
            'confidence': float
        }
    """
    terminal_gaps = []
    coachable_gaps = []

    # Extract candidate signals
    candidate_motion = detect_sales_motion(candidate_experience)
    metrics = extract_metrics(candidate_experience)
    has_context = has_metric_context(metrics)
    ownership = detect_ownership_level(candidate_experience)

    # Role requirements
    required_motion = role_requirements.get('sales_motion', 'Unknown')
    required_role_type = role_requirements.get('role_type', 'Unknown')  # AE, CS, BizDev

    # =========================================================================
    # Check 1: Sales Motion Alignment
    # =========================================================================
    if candidate_motion != 'Unknown' and required_motion != 'Unknown':
        motion_distance = calculate_motion_distance(candidate_motion, required_motion)

        if motion_distance > 1:
            # More than 1 step apart = terminal
            terminal_gaps.append({
                'type': 'sales_motion',
                'reason': f'{candidate_motion} background, role requires {required_motion}',
                'distance': f'{candidate_motion} → {required_motion}',
                'coachable': False
            })
        elif motion_distance == 1:
            # Adjacent motion = coachable
            coachable_gaps.append({
                'type': 'sales_motion',
                'reason': f'{candidate_motion} → {required_motion} shift',
                'distance': 'Adjacent motion',
                'coachable': True,
                'mitigation': generate_motion_mitigation(candidate_motion, required_motion)
            })

    # =========================================================================
    # Check 2: Metrics Without Context
    # =========================================================================
    if metrics and not has_context:
        terminal_gaps.append({
            'type': 'metric_context',
            'reason': 'Quota attainment without context (quota size, territory, market)',
            'distance': 'Raw numbers → Contextualized performance',
            'coachable': False
        })

    # =========================================================================
    # Check 3: Role Type Transition
    # =========================================================================
    candidate_role_type = detect_gtm_role_type(candidate_experience)

    if required_role_type != 'Unknown' and candidate_role_type != 'Unknown':
        if not is_compatible_role_transition(candidate_role_type, required_role_type):
            # Check if there's a bridge
            bridge = find_role_bridge(candidate_role_type, required_role_type)
            if bridge:
                coachable_gaps.append({
                    'type': 'role_type',
                    'reason': f'{candidate_role_type} background, role is {required_role_type}',
                    'distance': f'{candidate_role_type} → {required_role_type}',
                    'coachable': True,
                    'mitigation': bridge
                })
            else:
                terminal_gaps.append({
                    'type': 'role_type',
                    'reason': f'{candidate_role_type} background, role is {required_role_type}',
                    'distance': f'{candidate_role_type} → {required_role_type} (no bridge)',
                    'coachable': False
                })

    # =========================================================================
    # Check 4: Quota Carrying Experience
    # =========================================================================
    if role_requirements.get('quota_carrying', False):
        quota_signals = detect_quota_signals(candidate_experience)

        if quota_signals['level'] == 'missing':
            terminal_gaps.append({
                'type': 'quota_carrying',
                'reason': 'No evidence of carrying individual quota',
                'distance': 'Non-quota → Quota-carrying role',
                'coachable': False
            })
        elif quota_signals['level'] == 'implicit':
            coachable_gaps.append({
                'type': 'quota_carrying',
                'reason': 'Team quota experience but no individual quota evidence',
                'distance': 'Team quota → Individual quota',
                'coachable': True,
                'mitigation': 'Position contribution to team quota with personal metrics'
            })

    # =========================================================================
    # Check 5: Deal Complexity
    # =========================================================================
    if required_motion == 'Enterprise':
        complexity_signals = detect_deal_complexity(candidate_experience)

        if complexity_signals['level'] == 'missing':
            terminal_gaps.append({
                'type': 'deal_complexity',
                'reason': 'No evidence of complex, multi-stakeholder deal management',
                'distance': 'Simple deals → Complex enterprise deals',
                'coachable': False
            })
        elif complexity_signals['level'] == 'implicit':
            coachable_gaps.append({
                'type': 'deal_complexity',
                'reason': 'Some complexity signals but not enterprise-grade',
                'distance': 'Moderate → Complex deal management',
                'coachable': True,
                'mitigation': 'Position multi-stakeholder projects as deal complexity experience'
            })

    # =========================================================================
    # Check 6: Customer Success Specific
    # =========================================================================
    if required_role_type == 'CS':
        cs_signals = detect_cs_signals(candidate_experience)

        if cs_signals['level'] == 'missing' and candidate_role_type != 'CS':
            coachable_gaps.append({
                'type': 'cs_experience',
                'reason': 'No direct Customer Success experience',
                'distance': f'{candidate_role_type} → Customer Success',
                'coachable': True,
                'mitigation': 'Position any post-sale customer work, renewals, or account growth'
            })

    # =========================================================================
    # Check 7: Territory/Account Management
    # =========================================================================
    if role_requirements.get('named_accounts', False):
        territory_signals = detect_territory_signals(candidate_experience)

        if territory_signals['level'] == 'missing':
            coachable_gaps.append({
                'type': 'territory_management',
                'reason': 'No evidence of named account or territory management',
                'distance': 'Inbound/assigned → Named territory',
                'coachable': True,
                'mitigation': 'Position any account ownership or growth responsibility'
            })

    return {
        'actual_motion': candidate_motion,
        'terminal_gaps': terminal_gaps,
        'coachable_gaps': coachable_gaps,
        'confidence': calculate_confidence(terminal_gaps, coachable_gaps)
    }


def calculate_motion_distance(motion1: str, motion2: str) -> int:
    """
    Calculate distance between sales motions.

    Transactional <-> Mid-Market <-> Enterprise

    Returns: 0 (same), 1 (adjacent), 2 (far)
    """
    motion_order = ['Transactional', 'Mid-Market', 'Enterprise']

    try:
        idx1 = motion_order.index(motion1)
        idx2 = motion_order.index(motion2)
        return abs(idx1 - idx2)
    except ValueError:
        return 0  # Unknown motion = no distance penalty


def generate_motion_mitigation(from_motion: str, to_motion: str) -> str:
    """
    Generate positioning advice for motion transition.
    """
    mitigations = {
        ('Transactional', 'Mid-Market'): 'Frame relationship-building skills and consultative approach from volume experience',
        ('Mid-Market', 'Transactional'): 'Position speed and efficiency, highlight any high-velocity wins',
        ('Mid-Market', 'Enterprise'): 'Emphasize complex deal navigation, multi-stakeholder relationships',
        ('Enterprise', 'Mid-Market'): 'Position adaptability and ability to close faster with lighter process',
    }

    return mitigations.get((from_motion, to_motion), 'Frame transferable sales skills')


def detect_gtm_role_type(experience: Dict[str, Any]) -> str:
    """
    Detect GTM role type: AE, SDR/BDR, CS, BizDev, Sales Ops, etc.

    Returns: role type string
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    role_signals = {
        'AE': ['account executive', 'ae', 'closing', 'quota', 'pipeline', 'deals'],
        'SDR/BDR': ['sdr', 'bdr', 'sales development', 'business development rep', 'outbound', 'prospecting'],
        'CS': ['customer success', 'csm', 'account manager', 'retention', 'renewal', 'churn'],
        'BizDev': ['business development', 'partnerships', 'strategic partnerships', 'alliances'],
        'Sales Ops': ['sales operations', 'rev ops', 'revenue operations', 'sales analytics'],
        'SE': ['sales engineer', 'solutions engineer', 'pre-sales', 'technical sales']
    }

    scores = {}
    for role_type, keywords in role_signals.items():
        score = sum(1 for kw in keywords if kw in combined_text)
        scores[role_type] = score

    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return 'Unknown'

    return max(scores, key=scores.get)


def is_compatible_role_transition(from_role: str, to_role: str) -> bool:
    """
    Check if role transition is compatible (direct or adjacent).
    """
    compatible_transitions = {
        'AE': ['AE', 'BizDev', 'CS'],
        'SDR/BDR': ['SDR/BDR', 'AE'],
        'CS': ['CS', 'AE', 'BizDev'],
        'BizDev': ['BizDev', 'AE', 'CS'],
        'Sales Ops': ['Sales Ops'],
        'SE': ['SE', 'AE', 'BizDev']
    }

    return to_role in compatible_transitions.get(from_role, [])


def find_role_bridge(from_role: str, to_role: str) -> str:
    """
    Find positioning bridge for role transition.
    """
    bridges = {
        ('SDR/BDR', 'CS'): 'Position customer-facing communication and relationship skills',
        ('CS', 'SDR/BDR'): 'Position customer understanding and prospecting from existing accounts',
        ('SE', 'CS'): 'Position technical account ownership and customer outcomes',
        ('Sales Ops', 'AE'): None,  # Hard transition
        ('AE', 'SE'): 'Position technical knowledge and consultative selling',
    }

    return bridges.get((from_role, to_role))


def detect_quota_signals(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect quota-carrying signals.

    Returns: {'level': 'explicit'|'implicit'|'missing'}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    explicit_keywords = [
        'individual quota', 'my quota', 'personal quota',
        'carried quota', 'quota attainment', '% of quota',
        'exceeded quota', 'hit quota', 'quota carrying'
    ]

    implicit_keywords = [
        'team quota', 'contributed to quota', 'revenue target',
        'sales target', 'pipeline target', 'booking target'
    ]

    if any(kw in combined_text for kw in explicit_keywords):
        return {'level': 'explicit'}
    elif any(kw in combined_text for kw in implicit_keywords):
        return {'level': 'implicit'}
    else:
        return {'level': 'missing'}


def detect_deal_complexity(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect enterprise deal complexity signals.

    Returns: {'level': 'explicit'|'implicit'|'missing'}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    explicit_keywords = [
        'multi-stakeholder', 'c-suite', 'executive sponsor',
        'complex deal', 'enterprise deal', 'long sales cycle',
        '6-12 month', 'procurement', 'legal negotiation',
        'security review', 'enterprise agreement', 'msa'
    ]

    implicit_keywords = [
        'multiple stakeholders', 'buying committee', 'decision-makers',
        'cross-functional', 'vp-level', 'department head'
    ]

    if sum(1 for kw in explicit_keywords if kw in combined_text) >= 2:
        return {'level': 'explicit'}
    elif any(kw in combined_text for kw in implicit_keywords):
        return {'level': 'implicit'}
    else:
        return {'level': 'missing'}


def detect_cs_signals(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect Customer Success specific signals.

    Returns: {'level': 'explicit'|'implicit'|'missing'}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    explicit_keywords = [
        'customer success', 'csm', 'retention', 'churn reduction',
        'nrr', 'net revenue retention', 'renewal', 'expansion',
        'customer health', 'qbr', 'business review', 'upsell'
    ]

    implicit_keywords = [
        'account management', 'customer relationship', 'post-sale',
        'customer satisfaction', 'nps', 'customer outcomes'
    ]

    if sum(1 for kw in explicit_keywords if kw in combined_text) >= 2:
        return {'level': 'explicit'}
    elif any(kw in combined_text for kw in implicit_keywords):
        return {'level': 'implicit'}
    else:
        return {'level': 'missing'}


def detect_territory_signals(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect territory/named account management signals.

    Returns: {'level': 'explicit'|'implicit'|'missing'}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    explicit_keywords = [
        'named accounts', 'territory', 'strategic accounts',
        'owned accounts', 'account portfolio', 'book of business'
    ]

    implicit_keywords = [
        'assigned accounts', 'account list', 'geographic territory'
    ]

    if any(kw in combined_text for kw in explicit_keywords):
        return {'level': 'explicit'}
    elif any(kw in combined_text for kw in implicit_keywords):
        return {'level': 'implicit'}
    else:
        return {'level': 'missing'}


def calculate_confidence(terminal_gaps: List, coachable_gaps: List) -> float:
    """
    Calculate confidence in calibration assessment.
    """
    confidence = 1.0
    confidence -= len(terminal_gaps) * 0.2
    confidence -= len(coachable_gaps) * 0.05
    return max(0.0, min(1.0, confidence))
