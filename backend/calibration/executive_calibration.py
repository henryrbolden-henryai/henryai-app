# ============================================================================
# EXECUTIVE CALIBRATION
# Per Calibration Spec v1.0: Calibrates Senior Director, VP, C-Suite roles
#
# Leadership years at exec level means:
# - Building orgs (20+ people), not just managing
# - Strategic influence at board/exec level
# - P&L or budget ownership with actual dollars
# ============================================================================

from typing import Dict, List, Any, Optional
from .signal_detectors import (
    extract_team_size,
    extract_scope_signals,
    detect_org_level_influence,
    extract_revenue_impact,
    detect_press_release_pattern,
    detect_scale_inconsistency,
    detect_manager_of_managers,
    is_ic_to_leadership_transition,
)


def calibrate_executive_role(
    candidate_experience: Dict[str, Any],
    role_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calibrates executive-level roles (Senior Director, VP, C-Suite).

    Args:
        candidate_experience: Parsed resume data with roles/experience
        role_requirements: Job requirements including level, team_size, etc.

    Returns:
        dict: {
            'actual_level': str,  # e.g., "Director" vs "VP"
            'terminal_gaps': list,
            'coachable_gaps': list,
            'confidence': float  # 0.0-1.0
        }
    """
    terminal_gaps = []
    coachable_gaps = []

    # Extract candidate signals
    team_size = extract_team_size(candidate_experience)
    scope_signals = extract_scope_signals(candidate_experience)
    decision_signals = detect_decision_authority(candidate_experience)
    has_mom = detect_manager_of_managers(candidate_experience)

    # Role requirements
    required_team_size = role_requirements.get('team_size_min', 20)
    required_level = role_requirements.get('level', 'VP').lower()

    # =========================================================================
    # Check 1: Scope Level
    # =========================================================================
    if team_size > 0 and team_size < required_team_size / 3:
        # If managing <7 people for role requiring 20+
        terminal_gaps.append({
            'type': 'scope_level',
            'reason': f'Manages {team_size} people, role requires {required_team_size}+',
            'distance': 'IC/Small team → Org leader',
            'coachable': False
        })
    elif team_size > 0 and team_size < required_team_size / 2:
        # Close but not quite
        coachable_gaps.append({
            'type': 'scope_level',
            'reason': f'Manages {team_size} people, role requires {required_team_size}+',
            'distance': 'Manager → Senior leader scope gap',
            'coachable': True,
            'mitigation': 'Position org-building experience and influence beyond direct reports'
        })

    # =========================================================================
    # Check 2: Decision Authority Language
    # =========================================================================
    if decision_signals['level'] == 'missing':
        terminal_gaps.append({
            'type': 'decision_authority',
            'reason': 'No evidence of final decision-making authority',
            'distance': 'Influencer → Decision-maker',
            'coachable': False
        })
    elif decision_signals['level'] == 'implicit':
        coachable_gaps.append({
            'type': 'decision_authority',
            'reason': 'Influencer language only (no explicit decision ownership)',
            'distance': 'Implicit → Explicit authority',
            'coachable': True,
            'mitigation': 'Position stakeholder influence as strategic leadership'
        })

    # =========================================================================
    # Check 3: Press Release Detection
    # =========================================================================
    if detect_press_release_pattern(candidate_experience):
        terminal_gaps.append({
            'type': 'credibility',
            'reason': 'Resume lacks specificity (no tension, no tradeoffs, no failures)',
            'distance': 'Marketing copy → Evidence-based resume',
            'coachable': False
        })

    # =========================================================================
    # Check 4: Internal Scale Consistency
    # =========================================================================
    if detect_scale_inconsistency(candidate_experience):
        terminal_gaps.append({
            'type': 'fabrication_risk',
            'reason': 'Claims of scale inconsistent with company size/stage',
            'distance': 'Implausible → Verifiable',
            'coachable': False
        })

    # =========================================================================
    # Check 5: Manager-of-Managers Threshold for IC→Leadership
    # =========================================================================
    if is_ic_to_leadership_transition(candidate_experience):
        if not has_mom and required_team_size >= 50:
            terminal_gaps.append({
                'type': 'leadership_readiness',
                'reason': 'IC → Senior Director without manager-of-managers experience',
                'distance': 'IC → First-level manager → Senior leader',
                'coachable': False
            })
        elif not has_mom and required_team_size >= 20:
            coachable_gaps.append({
                'type': 'leadership_readiness',
                'reason': 'Limited manager-of-managers experience for org leadership role',
                'distance': 'First-level manager → Manager of managers',
                'coachable': True,
                'mitigation': 'Position mentorship and skip-level influence as proto-MoM experience'
            })

    # =========================================================================
    # Check 6: Geographic Scope for Global Roles
    # =========================================================================
    if role_requirements.get('global_scope', False):
        if scope_signals.get('geographic') == 'local':
            if detect_org_level_influence(candidate_experience) == 'explicit':
                # Has org influence but not geographic
                coachable_gaps.append({
                    'type': 'geographic_scope',
                    'reason': 'Local team experience, role requires global scope',
                    'distance': 'Local → Global leadership',
                    'coachable': True,
                    'mitigation': 'Position cross-timezone stakeholder work and remote leadership'
                })
            else:
                terminal_gaps.append({
                    'type': 'geographic_scope',
                    'reason': 'No evidence of global or distributed team leadership',
                    'distance': 'Local only → Global/distributed leadership',
                    'coachable': False
                })

    # =========================================================================
    # Check 7: P&L/Budget Ownership
    # =========================================================================
    if role_requirements.get('requires_pnl', False):
        budget_signals = detect_budget_ownership(candidate_experience)
        if budget_signals['level'] == 'missing':
            terminal_gaps.append({
                'type': 'financial_ownership',
                'reason': 'No evidence of P&L or budget ownership',
                'distance': 'Cost center owner → P&L owner',
                'coachable': False
            })
        elif budget_signals['level'] == 'implicit':
            coachable_gaps.append({
                'type': 'financial_ownership',
                'reason': 'Cost management experience but no P&L ownership',
                'distance': 'Cost awareness → P&L responsibility',
                'coachable': True,
                'mitigation': 'Position budget ownership and business impact metrics'
            })

    # Determine actual level
    actual_level = infer_actual_level(
        team_size=team_size,
        decision_authority=decision_signals['level'],
        scope_signals=scope_signals,
        has_mom=has_mom
    )

    return {
        'actual_level': actual_level,
        'terminal_gaps': terminal_gaps,
        'coachable_gaps': coachable_gaps,
        'confidence': calculate_confidence(terminal_gaps, coachable_gaps)
    }


def detect_decision_authority(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects decision-making authority level.

    Returns: {'level': 'explicit'|'implicit'|'missing', 'evidence': list}

    Explicit signals:
    - "decided", "owned", "set direction", "final call"
    - P&L ownership with dollars
    - Budget authority with amounts

    Implicit signals:
    - "partnered with", "supported", "collaborated", "advised"
    - Stakeholder influence without decision ownership
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()
    evidence = []

    # Explicit decision authority
    explicit_keywords = [
        'decided', 'owned the decision', 'set direction', 'final call',
        'made the call', 'determined', 'chose', 'selected',
        'approved', 'signed off', 'authorized', 'greenlit',
        'my decision', 'i decided', 'ultimate authority',
        'p&l owner', 'p&l ownership', 'budget owner', 'budget authority'
    ]

    explicit_patterns = [
        r'owned\s+(?:the\s+)?(?:strategy|direction|roadmap|vision)',
        r'set\s+(?:the\s+)?(?:technical|product|business)\s+direction',
        r'final\s+(?:decision|authority|call)\s+on',
        r'\$\d+\s*(?:m|million|k|thousand)\s*budget',
    ]

    import re
    for kw in explicit_keywords:
        if kw in combined_text:
            evidence.append(f"Explicit: '{kw}'")

    for pattern in explicit_patterns:
        if re.search(pattern, combined_text):
            evidence.append(f"Explicit pattern: {pattern}")

    if len(evidence) >= 2:
        return {'level': 'explicit', 'evidence': evidence}

    # Implicit (influencer) signals
    implicit_keywords = [
        'partnered with', 'collaborated with', 'advised', 'supported',
        'influenced', 'recommended', 'suggested', 'proposed',
        'stakeholder', 'worked with leadership', 'reported to'
    ]

    implicit_evidence = []
    for kw in implicit_keywords:
        if kw in combined_text:
            implicit_evidence.append(f"Implicit: '{kw}'")

    if implicit_evidence and evidence:
        # Some explicit + some implicit = implicit overall
        return {'level': 'implicit', 'evidence': evidence + implicit_evidence}
    elif implicit_evidence:
        return {'level': 'implicit', 'evidence': implicit_evidence}

    return {'level': 'missing', 'evidence': []}


def detect_budget_ownership(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects budget/P&L ownership signals.

    Returns: {'level': 'explicit'|'implicit'|'missing', 'amount': int|None}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    import re

    # P&L ownership signals
    pnl_patterns = [
        r'p&l\s*(?:owner|ownership|responsibility)',
        r'profit\s*(?:and|&)\s*loss',
        r'owned\s+(?:the\s+)?budget',
        r'budget\s+(?:owner|ownership|authority)',
        r'\$(\d+(?:\.\d+)?)\s*(?:m|million)\s*(?:budget|p&l)',
    ]

    for pattern in pnl_patterns:
        match = re.search(pattern, combined_text)
        if match:
            # Try to extract amount
            amount_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(?:m|million)', combined_text)
            amount = None
            if amount_match:
                try:
                    amount = int(float(amount_match.group(1)) * 1_000_000)
                except:
                    pass
            return {'level': 'explicit', 'amount': amount}

    # Implicit budget signals
    implicit_keywords = [
        'managed budget', 'cost reduction', 'cost savings',
        'budget planning', 'resource allocation', 'headcount planning'
    ]

    if any(kw in combined_text for kw in implicit_keywords):
        return {'level': 'implicit', 'amount': None}

    return {'level': 'missing', 'amount': None}


def infer_actual_level(
    team_size: int,
    decision_authority: str,
    scope_signals: Dict[str, str],
    has_mom: bool
) -> str:
    """
    Infers actual leadership level based on signals.

    Returns: 'IC' | 'Manager' | 'Senior Manager' | 'Director' | 'Senior Director' | 'VP' | 'C-Suite'
    """
    # C-Suite: massive scope, explicit authority, global
    if (team_size >= 100 and
        decision_authority == 'explicit' and
        scope_signals.get('geographic') == 'global' and
        scope_signals.get('organizational') == 'company-wide'):
        return 'C-Suite'

    # VP: large scope, explicit authority, manager of managers
    if (team_size >= 50 and
        decision_authority == 'explicit' and
        has_mom):
        return 'VP'

    # Senior Director: significant scope, some authority, usually MoM
    if (team_size >= 30 and
        decision_authority in ['explicit', 'implicit'] and
        has_mom):
        return 'Senior Director'

    # Director: medium scope, manager of managers or large team
    if (team_size >= 15 and
        (has_mom or team_size >= 20)):
        return 'Director'

    # Senior Manager: manages team, no MoM
    if team_size >= 5:
        return 'Senior Manager'

    # Manager: small team
    if team_size >= 2:
        return 'Manager'

    return 'IC'


def calculate_confidence(terminal_gaps: List, coachable_gaps: List) -> float:
    """
    Calculate confidence in calibration assessment.

    Lower confidence when more gaps detected (less certainty about overall fit).
    """
    # Start with high confidence
    confidence = 1.0

    # Terminal gaps reduce confidence significantly
    confidence -= len(terminal_gaps) * 0.2

    # Coachable gaps reduce confidence slightly
    confidence -= len(coachable_gaps) * 0.05

    # Ensure bounds
    return max(0.0, min(1.0, confidence))
