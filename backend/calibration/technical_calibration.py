# ============================================================================
# TECHNICAL CALIBRATION
# Per Calibration Spec v1.0: Calibrates IC3 (Mid) → IC4 (Senior) → IC5 (Staff+)
#
# Leveling criteria:
# - IC3: Executes projects, needs direction on "what"
# - IC4: Owns outcomes, figures out "what" and "how"
# - IC5: Sets direction, defines "why", org-level impact
# ============================================================================

from typing import Dict, List, Any
from .signal_detectors import (
    detect_ownership_level,
    analyze_scope_trajectory,
    detect_tool_obsession,
    detect_org_level_influence,
    extract_team_size,
    has_upward_trajectory,
)


def calibrate_technical_role(
    candidate_experience: Dict[str, Any],
    role_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calibrates IC3 (Mid) → IC4 (Senior) → IC5 (Staff+) levels.

    Args:
        candidate_experience: Parsed resume data with roles/experience
        role_requirements: Job requirements including level, etc.

    Returns:
        dict: {
            'actual_level': str,
            'terminal_gaps': list,
            'coachable_gaps': list,
            'confidence': float
        }
    """
    terminal_gaps = []
    coachable_gaps = []

    # Extract candidate signals
    ownership_level = detect_ownership_level(candidate_experience)
    trajectory = analyze_scope_trajectory(candidate_experience)
    org_influence = detect_org_level_influence(candidate_experience)
    has_trajectory = has_upward_trajectory(candidate_experience)

    # Role requirements
    required_level = role_requirements.get('level', 'IC4').upper()

    # =========================================================================
    # Check 1: Ownership Signals
    # =========================================================================
    if ownership_level == 'missing' and required_level in ['IC4', 'IC5', 'IC6', 'SENIOR', 'STAFF', 'PRINCIPAL']:
        terminal_gaps.append({
            'type': 'ownership',
            'reason': 'No ownership signals (all "contributed to", "worked on")',
            'distance': 'Participant → Owner',
            'coachable': False
        })
    elif ownership_level == 'implicit' and required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        coachable_gaps.append({
            'type': 'ownership',
            'reason': 'Contributor language, role requires ownership language',
            'distance': 'Contributor → Owner',
            'coachable': True,
            'mitigation': 'Reframe contributions as owned outcomes with measurable impact'
        })

    # =========================================================================
    # Check 2: Scope Trajectory
    # =========================================================================
    if trajectory == 'flat' and required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        terminal_gaps.append({
            'type': 'scope_stagnation',
            'reason': '5+ years at same level with no scope growth',
            'distance': 'Feature-level → Org-level impact',
            'coachable': False
        })
    elif trajectory == 'shrinking':
        terminal_gaps.append({
            'type': 'scope_regression',
            'reason': 'Scope has decreased over time (step-down pattern)',
            'distance': 'Regression → Growth trajectory',
            'coachable': False
        })
    elif trajectory == 'flat' and required_level in ['IC4', 'SENIOR']:
        coachable_gaps.append({
            'type': 'scope_trajectory',
            'reason': 'Flat scope trajectory, role expects growth pattern',
            'distance': 'Flat → Growing scope',
            'coachable': True,
            'mitigation': 'Highlight any scope expansion, even if modest'
        })

    # =========================================================================
    # Check 3: Tool Obsession Without Problem-Solving
    # =========================================================================
    if detect_tool_obsession(candidate_experience):
        terminal_gaps.append({
            'type': 'depth_vs_breadth',
            'reason': 'Resume optimized for ATS (tool lists, no problem-solving context)',
            'distance': 'Tool proficiency → Problem-solving capability',
            'coachable': False
        })

    # =========================================================================
    # Check 4: Level Stretch Assessment (IC4 → IC5)
    # =========================================================================
    if required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        if org_influence == 'missing':
            terminal_gaps.append({
                'type': 'org_influence',
                'reason': 'No evidence of org-level technical influence',
                'distance': 'Team scope → Org scope',
                'coachable': False
            })
        elif org_influence == 'implicit':
            coachable_gaps.append({
                'type': 'org_influence',
                'reason': 'Team-level impact, not org-level (IC4 → IC5 stretch)',
                'distance': 'Team scope → Org scope',
                'coachable': True,
                'mitigation': 'Position platform work with downstream impact metrics'
            })

    # =========================================================================
    # Check 5: Technical Depth vs Breadth
    # =========================================================================
    depth_signals = detect_technical_depth(candidate_experience)

    if required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        if depth_signals['level'] == 'shallow':
            coachable_gaps.append({
                'type': 'technical_depth',
                'reason': 'Broad experience without demonstrated deep expertise',
                'distance': 'Generalist → Deep specialist or technical leader',
                'coachable': True,
                'mitigation': 'Position deepest technical contributions with specific architecture decisions'
            })
    elif required_level in ['IC4', 'SENIOR']:
        if depth_signals['level'] == 'missing':
            terminal_gaps.append({
                'type': 'technical_depth',
                'reason': 'No demonstrated technical depth or system design',
                'distance': 'No depth → Technical depth required',
                'coachable': False
            })

    # =========================================================================
    # Check 6: Architecture/Design Signals for Staff+
    # =========================================================================
    if required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        arch_signals = detect_architecture_signals(candidate_experience)

        if arch_signals['level'] == 'missing':
            terminal_gaps.append({
                'type': 'architecture',
                'reason': 'No evidence of system design or architecture ownership',
                'distance': 'Implementer → Architect',
                'coachable': False
            })
        elif arch_signals['level'] == 'implicit':
            coachable_gaps.append({
                'type': 'architecture',
                'reason': 'Implementation experience but no explicit architecture ownership',
                'distance': 'Implementer → Architect',
                'coachable': True,
                'mitigation': 'Position technical decisions as architecture choices with rationale'
            })

    # =========================================================================
    # Check 7: Mentorship/Technical Leadership for Staff+
    # =========================================================================
    if required_level in ['IC5', 'IC6', 'STAFF', 'PRINCIPAL']:
        mentorship_signals = detect_mentorship_signals(candidate_experience)

        if mentorship_signals['level'] == 'missing':
            coachable_gaps.append({
                'type': 'mentorship',
                'reason': 'No evidence of mentoring or technical leadership of others',
                'distance': 'Individual contributor → Technical multiplier',
                'coachable': True,
                'mitigation': 'Position any code review, onboarding, or knowledge sharing as mentorship'
            })

    # Determine actual level
    actual_level = infer_ic_level(
        ownership_level=ownership_level,
        trajectory=trajectory,
        org_influence=org_influence,
        has_trajectory=has_trajectory
    )

    return {
        'actual_level': actual_level,
        'terminal_gaps': terminal_gaps,
        'coachable_gaps': coachable_gaps,
        'confidence': calculate_confidence(terminal_gaps, coachable_gaps)
    }


def detect_technical_depth(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects technical depth signals.

    Returns: {'level': 'deep'|'moderate'|'shallow'|'missing', 'areas': list}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    # Deep expertise signals
    deep_keywords = [
        'designed', 'architected', 'led the design', 'technical decision',
        'system design', 'data model', 'api design', 'protocol',
        'performance optimization', 'scaling', 'distributed system',
        'concurrency', 'cache strategy', 'database optimization',
        'technical specification', 'rfc', 'design doc'
    ]

    # Moderate depth signals
    moderate_keywords = [
        'implemented', 'built', 'developed', 'created',
        'integrated', 'debugged', 'refactored', 'optimized'
    ]

    # Shallow/missing signals
    shallow_keywords = [
        'used', 'worked with', 'familiar with', 'experience in',
        'exposure to', 'basic knowledge', 'some experience'
    ]

    deep_count = sum(1 for kw in deep_keywords if kw in combined_text)
    moderate_count = sum(1 for kw in moderate_keywords if kw in combined_text)
    shallow_count = sum(1 for kw in shallow_keywords if kw in combined_text)

    if deep_count >= 3:
        return {'level': 'deep', 'areas': []}
    elif deep_count >= 1 or moderate_count >= 3:
        return {'level': 'moderate', 'areas': []}
    elif moderate_count >= 1:
        return {'level': 'shallow', 'areas': []}
    else:
        return {'level': 'missing', 'areas': []}


def detect_architecture_signals(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects architecture/system design signals.

    Returns: {'level': 'explicit'|'implicit'|'missing', 'evidence': list}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()
    evidence = []

    # Explicit architecture signals
    explicit_keywords = [
        'architected', 'designed the system', 'system architecture',
        'technical architecture', 'led the design', 'design decision',
        'architectural decision', 'technical specification',
        'api design', 'data architecture', 'microservices design',
        'distributed architecture', 'scalability design'
    ]

    import re
    explicit_patterns = [
        r'designed\s+(?:the\s+)?(?:system|architecture|api|service)',
        r'architected\s+(?:a\s+)?(?:platform|system|service)',
        r'technical\s+lead\s+(?:for|on)\s+(?:the\s+)?(?:design|architecture)',
    ]

    for kw in explicit_keywords:
        if kw in combined_text:
            evidence.append(f"Explicit: '{kw}'")

    for pattern in explicit_patterns:
        if re.search(pattern, combined_text):
            evidence.append(f"Explicit pattern matched")

    if len(evidence) >= 2:
        return {'level': 'explicit', 'evidence': evidence}

    # Implicit signals
    implicit_keywords = [
        'technical design', 'system design', 'design review',
        'code review', 'technical decision', 'tradeoff',
        'scalability', 'reliability', 'performance'
    ]

    for kw in implicit_keywords:
        if kw in combined_text:
            evidence.append(f"Implicit: '{kw}'")

    if evidence:
        return {'level': 'implicit', 'evidence': evidence}

    return {'level': 'missing', 'evidence': []}


def detect_mentorship_signals(experience: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects mentorship and technical leadership signals.

    Returns: {'level': 'explicit'|'implicit'|'missing', 'evidence': list}
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()
    evidence = []

    # Explicit mentorship signals
    explicit_keywords = [
        'mentored', 'coached', 'onboarded', 'trained',
        'developed engineers', 'grew the team', 'leveled up',
        'promoted engineers', 'career development', 'tech lead'
    ]

    for kw in explicit_keywords:
        if kw in combined_text:
            evidence.append(f"Explicit: '{kw}'")

    if len(evidence) >= 2:
        return {'level': 'explicit', 'evidence': evidence}

    # Implicit signals
    implicit_keywords = [
        'code review', 'pair programming', 'knowledge sharing',
        'documentation', 'tech talk', 'brown bag', 'workshop'
    ]

    for kw in implicit_keywords:
        if kw in combined_text:
            evidence.append(f"Implicit: '{kw}'")

    if evidence:
        return {'level': 'implicit', 'evidence': evidence}

    return {'level': 'missing', 'evidence': []}


def infer_ic_level(
    ownership_level: str,
    trajectory: str,
    org_influence: str,
    has_trajectory: bool
) -> str:
    """
    Infers actual IC level based on signals.

    Returns: 'IC2' | 'IC3' | 'IC4' | 'IC5' | 'IC6'
    """
    # IC6 (Distinguished/Fellow): org influence + explicit ownership + growth
    if org_influence == 'explicit' and ownership_level == 'explicit' and trajectory == 'growing':
        return 'IC6'

    # IC5 (Staff/Principal): org influence + ownership
    if org_influence in ['explicit', 'implicit'] and ownership_level == 'explicit':
        return 'IC5'

    # IC4 (Senior): ownership + trajectory
    if ownership_level == 'explicit' or (ownership_level == 'implicit' and has_trajectory):
        return 'IC4'

    # IC3 (Mid): some ownership or implicit
    if ownership_level == 'implicit':
        return 'IC3'

    # IC2 (Junior): missing ownership
    return 'IC2'


def calculate_confidence(terminal_gaps: List, coachable_gaps: List) -> float:
    """
    Calculate confidence in calibration assessment.
    """
    confidence = 1.0
    confidence -= len(terminal_gaps) * 0.2
    confidence -= len(coachable_gaps) * 0.05
    return max(0.0, min(1.0, confidence))
