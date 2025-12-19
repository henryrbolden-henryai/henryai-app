# ============================================================================
# CALIBRATION CONTROLLER
# Per Recruiter Calibration Spec v1.0 (REVISED)
#
# Purpose: Control layer that enforces gap classification and priority ranking.
# CEC detects capabilities. This controller decides which gaps matter.
#
# HARD CONSTRAINTS:
# - Does NOT override Job Fit recommendation
# - Does NOT change fit scores
# - Calibration explains a "Do Not Apply," it does NOT create one
# - locked_reason comes from Job Fit only
# - Calibration provides redirect_reason for coaching, not for changing recommendation
# ============================================================================

from typing import Dict, List, Any, Optional
from .gap_classifier import (
    classify_gap,
    assess_domain_transferability,
    calculate_level_distance,
)
from .signal_detectors import has_upward_trajectory


def calibrate_gaps(
    cec_results: Dict[str, Any],
    job_fit_recommendation: str,
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Control layer that enforces Recruiter Calibration Spec v1.0.

    Input:
        - cec_results: dict with capability evaluations from CEC
        - job_fit_recommendation: str ("Do Not Apply", "Apply with Caution", "Apply", "Strong Apply")
        - candidate_resume: dict
        - job_requirements: dict

    Output:
        - calibrated_gaps: dict {
            'primary_gap': dict or None,
            'secondary_gaps': list (max 2, coachable only),
            'redirect_reason': str or None (if terminal exists),
            'suppress_gaps_section': bool (if silence appropriate),
            'suppressed_gaps': list (for internal logging)
        }

    CRITICAL: This function does NOT override Job Fit recommendation.
    It only interprets and prioritizes gaps for coaching output.
    """
    # Extract all gaps from CEC results
    all_gaps = extract_all_gaps_from_cec(cec_results)

    # Step 1: Classify each gap
    classified_gaps = []
    for gap in all_gaps:
        classification = classify_gap_terminal_vs_coachable(
            gap=gap,
            candidate_resume=candidate_resume,
            job_requirements=job_requirements
        )
        classified_gaps.append({
            'gap': gap,
            'classification': classification['type'],  # 'terminal', 'coachable', 'suppressed'
            'reason': classification['reason'],
            'redirect': classification.get('redirect'),
            'mitigation': classification.get('mitigation')
        })

    # Step 2: Filter by Job Fit decision
    # If "Strong Apply", suppress gaps section (but allow strategic guidance)
    if job_fit_recommendation == "Strong Apply":
        # CORRECTED: Silence suppresses gaps, not "Your Move"
        return {
            'primary_gap': None,
            'secondary_gaps': [],
            'redirect_reason': None,
            'suppress_gaps_section': True,  # Hide gaps section
            'suppressed_gaps': classified_gaps  # Log what we suppressed
        }

    # If "Do Not Apply", only terminal gaps matter for coaching explanation
    if job_fit_recommendation == "Do Not Apply":
        relevant_gaps = [g for g in classified_gaps if g['classification'] == 'terminal']
    elif job_fit_recommendation in ["Apply with Caution", "Apply"]:
        # Include coachable gaps only (terminal already handled by Job Fit)
        relevant_gaps = [g for g in classified_gaps if g['classification'] in ['terminal', 'coachable']]
    else:
        relevant_gaps = classified_gaps

    # Step 3: Apply gap hierarchy (Priority order)
    # Terminal > coachable
    terminal_gaps = [g for g in relevant_gaps if g['classification'] == 'terminal']
    coachable_gaps = [g for g in relevant_gaps if g['classification'] == 'coachable']
    suppressed_gaps = [g for g in classified_gaps if g['classification'] == 'suppressed']

    # Step 4: Rank gaps by priority
    prioritized_terminal = rank_gaps_by_priority(terminal_gaps)
    prioritized_coachable = rank_gaps_by_priority(coachable_gaps)

    # Step 5: Select primary gap and secondary gaps
    if prioritized_terminal:
        # Terminal gap exists - it's the only thing that matters
        primary_gap = prioritized_terminal[0]
        secondary_gaps = []  # Terminal overrides everything
        redirect_reason = primary_gap.get('redirect')
        suppress_gaps_section = False
    elif prioritized_coachable:
        # Multiple coachable gaps scenario
        primary_gap = prioritized_coachable[0]
        secondary_gaps = prioritized_coachable[1:3]  # Max 2 additional gaps

        # Assertion for safety
        assert len(secondary_gaps) <= 2, "Secondary gaps must not exceed 2"

        redirect_reason = None
        suppress_gaps_section = False
    else:
        # No significant gaps
        primary_gap = None
        secondary_gaps = []
        redirect_reason = None
        suppress_gaps_section = True

    return {
        'primary_gap': primary_gap,
        'secondary_gaps': secondary_gaps,
        'redirect_reason': redirect_reason,
        'suppress_gaps_section': suppress_gaps_section,
        'suppressed_gaps': suppressed_gaps  # For internal logging/QA
    }


def extract_all_gaps_from_cec(cec_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts all evaluated capabilities that have gaps (implicit or missing).

    Returns: list of gap dicts with capability info
    """
    gaps = []

    # Handle capability_evidence_report structure
    if 'capability_evidence_report' in cec_results:
        evaluated = cec_results['capability_evidence_report'].get('evaluated_capabilities', [])
    elif 'evaluated_capabilities' in cec_results:
        evaluated = cec_results.get('evaluated_capabilities', [])
    else:
        evaluated = []

    for cap in evaluated:
        evidence_status = cap.get('evidence_status', '')
        # Only include gaps (not explicit matches)
        if evidence_status in ['implicit', 'missing']:
            gaps.append({
                'capability': cap.get('capability_name', cap.get('capability_id', '')),
                'capability_id': cap.get('capability_id', ''),
                'evidence_status': evidence_status,
                'diagnosis': cap.get('diagnosis', ''),
                'distance': cap.get('distance', ''),
                'coachable': cap.get('coachable', False),
                'criticality': cap.get('criticality', 'preferred'),
                'jd_requirement': cap.get('jd_requirement', ''),
                'resume_evidence': cap.get('resume_evidence', '')
            })

    return gaps


def classify_gap_terminal_vs_coachable(
    gap: Dict[str, Any],
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Implements terminal vs coachable classification logic from Recruiter Calibration Spec.

    Terminal gaps (Do Not Apply):
    1. Wrong function (no bridge)
    2. Wrong domain (zero transferability)
    3. Wrong level (>2 levels)
    4. Hard requirement missing
    5. Red flag patterns

    Coachable gaps (Apply with Caution):
    1. Adjacent domain
    2. Career switcher with evidence
    3. Level stretch with foundation
    4. Soft requirement gap
    5. Context mismatch

    Suppressed (ignorable):
    1. Minor soft requirements
    2. Skills easily learned
    3. Nice-to-haves
    """
    capability_id = gap.get('capability_id', '').lower()
    capability_name = gap.get('capability', '').lower()
    evidence_status = gap.get('evidence_status', 'missing')
    criticality = gap.get('criticality', 'preferred')

    # Priority 1: Domain gaps
    if 'domain' in capability_id or 'domain' in capability_name:
        candidate_domain = candidate_resume.get('domain', '')
        required_domain = job_requirements.get('domain', '')

        transferability = assess_domain_transferability(candidate_domain, required_domain)

        if transferability == 'zero':
            return {
                'type': 'terminal',
                'reason': 'Domain expertise non-transferable',
                'redirect': suggest_aligned_domains(candidate_resume, candidate_domain)
            }
        elif transferability == 'adjacent':
            return {
                'type': 'coachable',
                'reason': 'Adjacent domain with transferable skills',
                'mitigation': generate_domain_mitigation(candidate_domain, required_domain)
            }
        else:
            return {
                'type': 'suppressed',
                'reason': 'Domain match sufficient'
            }

    # Priority 2: Leadership/level gaps
    if 'leadership' in capability_id or 'scope' in capability_id or 'level' in capability_name:
        candidate_level = candidate_resume.get('level', '')
        required_level = job_requirements.get('level', '')

        level_distance = calculate_level_distance(candidate_level, required_level)

        if level_distance > 2:
            return {
                'type': 'terminal',
                'reason': f'Level gap too large ({level_distance} levels)',
                'redirect': suggest_appropriate_level(candidate_resume)
            }
        elif level_distance >= 1:
            if has_upward_trajectory(candidate_resume):
                return {
                    'type': 'coachable',
                    'reason': 'Level stretch with strong foundation',
                    'mitigation': 'Position growing scope and upward trajectory'
                }
            elif level_distance == 1:
                return {
                    'type': 'coachable',
                    'reason': 'Level stretch (1 level)',
                    'mitigation': 'Position readiness for next level with specific evidence'
                }
            else:
                return {
                    'type': 'terminal',
                    'reason': 'Level gap without demonstrated growth',
                    'redirect': suggest_appropriate_level(candidate_resume)
                }
        else:
            return {
                'type': 'suppressed',
                'reason': 'Level match sufficient'
            }

    # Priority 3: Hard requirement missing
    if evidence_status == 'missing' and criticality == 'required':
        return {
            'type': 'terminal',
            'reason': gap.get('diagnosis', 'Missing required qualification'),
            'redirect': 'Build required experience before applying'
        }

    # Priority 4: Cross-functional gaps (typically coachable)
    if 'cross_functional' in capability_id or 'product' in capability_id:
        if evidence_status == 'missing':
            return {
                'type': 'coachable',
                'reason': 'Cross-functional collaboration not evidenced',
                'mitigation': 'Position any cross-team work or stakeholder management'
            }
        else:  # implicit
            return {
                'type': 'coachable',
                'reason': 'Cross-functional work implied but not explicit',
                'mitigation': 'Frame existing collaboration as explicit partnership'
            }

    # Priority 5: Scale gaps (typically coachable unless extreme)
    if 'scale' in capability_id:
        if evidence_status == 'missing':
            return {
                'type': 'coachable',
                'reason': 'Scale experience not evidenced',
                'mitigation': 'Position any growth metrics or impact at scale'
            }
        else:
            return {
                'type': 'coachable',
                'reason': 'Scale signals implicit',
                'mitigation': 'Quantify impact with specific numbers'
            }

    # Priority 6: Soft requirement gap (coachable)
    if evidence_status in ['implicit', 'missing'] and criticality != 'required':
        return {
            'type': 'coachable',
            'reason': 'Addressable gap with positioning',
            'mitigation': generate_positioning_advice(gap)
        }

    # Default: suppressed (nice-to-have, detected but intentionally hidden)
    return {
        'type': 'suppressed',
        'reason': 'Minor soft requirement or skill easily learned on job'
    }


def rank_gaps_by_priority(gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks gaps using hierarchy from Selective Coaching Spec:
    1. Domain beats level
    2. Level beats leadership
    3. Leadership beats cross-functional
    4. Cross-functional beats scale
    5. Scale beats tooling

    Returns: sorted list (highest priority first)
    """
    priority_map = {
        'domain': 1,
        'level': 2,
        'leadership': 3,
        'scope': 3,  # Same as leadership
        'cross_functional': 4,
        'product': 4,  # Same as cross-functional
        'scale': 5,
        'tooling': 6,
        'skill': 6
    }

    def get_priority(gap_entry: Dict[str, Any]) -> int:
        gap = gap_entry.get('gap', {})
        capability_id = gap.get('capability_id', '').lower()
        capability_name = gap.get('capability', '').lower()

        combined = f"{capability_id} {capability_name}"

        for key in priority_map:
            if key in combined:
                return priority_map[key]
        return 99  # Unknown, lowest priority

    return sorted(gaps, key=get_priority)


def suggest_aligned_domains(candidate_resume: Dict[str, Any], current_domain: str = '') -> str:
    """
    Suggest aligned domains for terminal domain mismatch.
    """
    domain = current_domain or candidate_resume.get('domain', '')

    adjacency_suggestions = {
        'healthcare': 'healthtech, medtech, insurance, or payer/provider tech',
        'fintech': 'payments, banking, insurance, or financial services',
        'consumer': 'B2C, social, ecommerce, or marketplace',
        'enterprise': 'B2B SaaS, enterprise software, or infrastructure',
        'ecommerce': 'retail, marketplace, or payments',
        'payments': 'fintech, banking, or ecommerce',
        'safety': 'trust & safety, content moderation, or security',
    }

    if domain:
        domain_lower = domain.lower()
        for key, suggestion in adjacency_suggestions.items():
            if key in domain_lower:
                return f"Redirect to {suggestion} roles where your {domain} background applies"

    return "Redirect to roles in adjacent domains where your experience transfers"


def suggest_appropriate_level(candidate_resume: Dict[str, Any]) -> str:
    """
    Suggest appropriate level for terminal level mismatch.
    """
    # Infer current level from resume
    level = candidate_resume.get('level', '').lower()

    level_suggestions = {
        'ic': 'Focus on Senior IC or Staff Engineer roles matching your current scope',
        'senior': 'Focus on Senior or Staff roles matching your experience level',
        'manager': 'Focus on Manager or Senior Manager roles matching your people management scope',
        'director': 'Focus on Director roles matching your team leadership experience',
    }

    for key, suggestion in level_suggestions.items():
        if key in level:
            return suggestion

    return "Focus on roles matching your current experience level and scope"


def generate_domain_mitigation(candidate_domain: str, required_domain: str) -> str:
    """
    Generate domain positioning advice.
    """
    if not candidate_domain or not required_domain:
        return "Position transferable skills from your domain"

    candidate_lower = candidate_domain.lower()
    required_lower = required_domain.lower()

    mitigations = {
        ('fintech', 'payments'): 'Position financial product experience as payments expertise',
        ('payments', 'fintech'): 'Position payment infrastructure knowledge as broader fintech skills',
        ('healthcare', 'healthtech'): 'Position clinical understanding as healthtech domain knowledge',
        ('consumer', 'enterprise'): 'Position user empathy as buyer understanding',
        ('enterprise', 'consumer'): 'Position stakeholder management as user research skills',
        ('ecommerce', 'fintech'): 'Position checkout and payments experience as fintech exposure',
        ('safety', 'trust_and_safety'): 'Position safety work as trust & safety expertise',
    }

    key = (candidate_lower, required_lower)
    if key in mitigations:
        return mitigations[key]

    return f"Position {candidate_domain} experience as transferable to {required_domain}"


def generate_positioning_advice(gap: Dict[str, Any]) -> str:
    """
    Generate generic positioning advice for a gap.
    """
    capability = gap.get('capability', '').lower()
    diagnosis = gap.get('diagnosis', '')

    if 'leadership' in capability:
        return 'Position any team influence or mentorship as leadership signals'
    elif 'cross' in capability or 'product' in capability:
        return 'Frame stakeholder collaboration as cross-functional partnership'
    elif 'scale' in capability:
        return 'Quantify impact with specific metrics and numbers'
    elif 'domain' in capability:
        return 'Position adjacent experience as transferable domain knowledge'
    else:
        return 'Position relevant experience as evidence of capability'
