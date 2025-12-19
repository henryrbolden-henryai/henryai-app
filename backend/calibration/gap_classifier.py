# ============================================================================
# GAP CLASSIFIER
# Per Calibration Spec v1.0: Terminal vs Coachable Classification
#
# Terminal gaps (Do Not Apply):
# 1. Wrong function (no bridge)
# 2. Wrong domain (zero transferability)
# 3. Wrong level (>2 levels)
# 4. Hard requirement missing
# 5. Red flag patterns
#
# Coachable gaps (Apply with Caution):
# 1. Adjacent domain
# 2. Career switcher with evidence
# 3. Level stretch with foundation
# 4. Soft requirement gap
# 5. Context mismatch
# ============================================================================

from typing import Dict, List, Any, Optional
from .signal_detectors import has_upward_trajectory


def classify_gap(
    gap_type: str,
    candidate_experience: Dict[str, Any],
    role_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determines if a gap is terminal or coachable.

    Args:
        gap_type: Type of gap ('function', 'domain', 'level', 'hard_requirement', 'red_flag', etc.)
        candidate_experience: Parsed resume data
        role_requirements: Job requirements

    Returns:
        dict: {
            'classification': 'terminal'|'coachable',
            'reason': str,
            'redirect': str (if terminal),
            'mitigation': str (if coachable)
        }
    """
    # Priority 1: Function mismatch
    if gap_type == 'function':
        has_bridge = detect_function_bridge(candidate_experience, role_requirements)
        if not has_bridge:
            return {
                'classification': 'terminal',
                'reason': 'Function mismatch with no transferable bridge',
                'redirect': suggest_aligned_functions(candidate_experience)
            }
        else:
            return {
                'classification': 'coachable',
                'reason': 'Function adjacent with transferable skills',
                'mitigation': has_bridge
            }

    # Priority 2: Domain transferability
    if gap_type == 'domain':
        candidate_domain = candidate_experience.get('domain')
        required_domain = role_requirements.get('domain')

        transferability = assess_domain_transferability(candidate_domain, required_domain)

        if transferability == 'zero':
            return {
                'classification': 'terminal',
                'reason': 'Domain expertise non-transferable',
                'redirect': suggest_aligned_domains(candidate_experience)
            }
        elif transferability == 'adjacent':
            return {
                'classification': 'coachable',
                'reason': 'Adjacent domain with transferable skills',
                'mitigation': generate_domain_mitigation(candidate_domain, required_domain)
            }
        else:  # direct
            return {
                'classification': 'coachable',
                'reason': 'Direct domain match',
                'mitigation': None
            }

    # Priority 3: Level gap
    if gap_type == 'level':
        candidate_level = candidate_experience.get('level')
        required_level = role_requirements.get('level')

        level_distance = calculate_level_distance(candidate_level, required_level)

        if level_distance > 2:
            return {
                'classification': 'terminal',
                'reason': f'Level gap too large ({level_distance} levels)',
                'redirect': suggest_appropriate_level(candidate_experience)
            }
        elif level_distance == 2:
            # 2 levels is borderline - check for strong trajectory
            if has_upward_trajectory(candidate_experience):
                return {
                    'classification': 'coachable',
                    'reason': 'Significant level stretch but strong growth trajectory',
                    'mitigation': 'Position rapid growth and increasing scope. This is a stretch.'
                }
            else:
                return {
                    'classification': 'terminal',
                    'reason': 'Level gap too large without demonstrated growth',
                    'redirect': suggest_appropriate_level(candidate_experience)
                }
        elif level_distance == 1 and has_upward_trajectory(candidate_experience):
            return {
                'classification': 'coachable',
                'reason': 'Level stretch with strong foundation',
                'mitigation': 'Position growing scope and upward trajectory'
            }
        elif level_distance == 1:
            return {
                'classification': 'coachable',
                'reason': 'Level stretch (1 level)',
                'mitigation': 'Position readiness for next level with specific evidence'
            }
        else:
            return {
                'classification': 'coachable',
                'reason': 'Level aligned',
                'mitigation': None
            }

    # Priority 4: Hard requirement
    if gap_type == 'hard_requirement':
        return {
            'classification': 'terminal',
            'reason': 'Missing required qualification',
            'redirect': 'Build required experience before applying'
        }

    # Priority 5: Red flag patterns
    if gap_type == 'red_flag':
        return {
            'classification': 'terminal',
            'reason': detect_red_flag_reason(candidate_experience, role_requirements),
            'redirect': 'Address red flags before applying'
        }

    # Priority 6: Soft requirement
    if gap_type == 'soft_requirement':
        return {
            'classification': 'coachable',
            'reason': 'Nice-to-have not met',
            'mitigation': 'Optional skill - may compensate with core strengths'
        }

    # Default: assess as coachable if not caught above
    return {
        'classification': 'coachable',
        'reason': 'Addressable gap with positioning',
        'mitigation': generate_generic_mitigation(gap_type)
    }


def assess_domain_transferability(
    candidate_domain: Optional[str],
    required_domain: Optional[str]
) -> str:
    """
    Assesses domain transferability.

    Returns: 'zero'|'adjacent'|'direct'

    Domain adjacency map:
    - Fintech → Payments: adjacent
    - Healthcare → Fintech: zero
    - B2B SaaS → Enterprise SaaS: direct
    - Consumer → Enterprise: adjacent
    """
    if not candidate_domain or not required_domain:
        return 'zero'

    candidate_domain = candidate_domain.lower().strip()
    required_domain = required_domain.lower().strip()

    if candidate_domain == required_domain:
        return 'direct'

    # Comprehensive adjacency map
    adjacency_map = {
        'fintech': ['payments', 'banking', 'insurance', 'financial services', 'lending', 'trading'],
        'payments': ['fintech', 'banking', 'ecommerce', 'financial services'],
        'banking': ['fintech', 'payments', 'financial services', 'insurance'],
        'insurance': ['fintech', 'banking', 'healthcare', 'financial services'],
        'healthcare': ['medtech', 'healthtech', 'pharma', 'biotech', 'insurance'],
        'medtech': ['healthcare', 'healthtech', 'biotech'],
        'healthtech': ['healthcare', 'medtech', 'enterprise_saas'],
        'pharma': ['healthcare', 'biotech'],
        'biotech': ['healthcare', 'pharma', 'medtech'],
        'enterprise_saas': ['b2b_saas', 'smb_saas', 'infrastructure'],
        'b2b_saas': ['enterprise_saas', 'smb_saas', 'enterprise'],
        'smb_saas': ['b2b_saas', 'consumer'],
        'consumer': ['b2c', 'social', 'ecommerce', 'smb_saas'],
        'b2c': ['consumer', 'social', 'ecommerce'],
        'social': ['consumer', 'b2c', 'advertising'],
        'ecommerce': ['retail', 'marketplace', 'consumer', 'payments'],
        'retail': ['ecommerce', 'marketplace', 'consumer'],
        'marketplace': ['ecommerce', 'retail', 'consumer'],
        'advertising': ['adtech', 'martech', 'social', 'consumer'],
        'adtech': ['advertising', 'martech'],
        'martech': ['advertising', 'adtech', 'enterprise_saas'],
        'enterprise': ['b2b_saas', 'enterprise_saas'],
        'infrastructure': ['cloud', 'devops', 'platform', 'enterprise_saas'],
        'cloud': ['infrastructure', 'devops', 'platform'],
        'devops': ['infrastructure', 'cloud', 'platform'],
        'platform': ['infrastructure', 'cloud', 'devops'],
        'security': ['cybersecurity', 'enterprise_saas', 'infrastructure'],
        'cybersecurity': ['security', 'enterprise_saas'],
        'safety': ['trust_and_safety', 'security', 'fintech'],
        'trust_and_safety': ['safety', 'content_moderation', 'security'],
        'content_moderation': ['trust_and_safety', 'social', 'consumer'],
        'ml_ai': ['data', 'infrastructure', 'enterprise_saas'],
        'data': ['ml_ai', 'analytics', 'infrastructure'],
        'analytics': ['data', 'enterprise_saas', 'ml_ai'],
    }

    # Normalize domain names
    candidate_normalized = candidate_domain.replace(' ', '_').replace('-', '_')
    required_normalized = required_domain.replace(' ', '_').replace('-', '_')

    # Check direct adjacency
    if required_normalized in adjacency_map.get(candidate_normalized, []):
        return 'adjacent'

    # Check reverse adjacency
    if candidate_normalized in adjacency_map.get(required_normalized, []):
        return 'adjacent'

    # No adjacency found
    return 'zero'


def detect_function_bridge(
    candidate_experience: Dict[str, Any],
    role_requirements: Dict[str, Any]
) -> Optional[str]:
    """
    Detect if there's a function bridge between candidate and role.

    Returns: Positioning advice if bridge exists, None otherwise
    """
    candidate_function = detect_candidate_function(candidate_experience)
    required_function = role_requirements.get('function', '').lower()

    if not candidate_function or not required_function:
        return None

    # Function bridge map
    bridges = {
        ('engineering', 'product'): 'Position technical depth as product judgment and customer understanding',
        ('product', 'engineering_management'): 'Position product ownership as team leadership preparation',
        ('sales', 'customer_success'): 'Position relationship skills and customer focus',
        ('customer_success', 'sales'): 'Position customer knowledge and expansion experience',
        ('marketing', 'product_marketing'): 'Position market understanding and positioning skills',
        ('product_marketing', 'product'): 'Position customer research and market insights',
        ('engineering', 'data'): 'Position analytical mindset and technical foundation',
        ('data', 'product'): 'Position data-driven decision making and user understanding',
        ('design', 'product'): 'Position user empathy and design thinking',
        ('sales_engineering', 'product'): 'Position technical knowledge and customer understanding',
        ('consulting', 'product'): 'Position problem-solving and stakeholder management',
        ('consulting', 'strategy'): 'Position analytical framework and executive communication',
    }

    bridge = bridges.get((candidate_function, required_function))
    if bridge:
        return bridge

    # Check reverse
    bridge = bridges.get((required_function, candidate_function))
    if bridge:
        return f"Reverse transition: {bridge}"

    return None


def detect_candidate_function(experience: Dict[str, Any]) -> Optional[str]:
    """
    Detect primary function from candidate experience.
    """
    from .signal_detectors import _build_experience_text

    combined_text = _build_experience_text(experience).lower()

    function_signals = {
        'engineering': ['engineer', 'developer', 'software', 'backend', 'frontend', 'full-stack'],
        'product': ['product manager', 'pm', 'product owner', 'product lead'],
        'design': ['designer', 'ux', 'ui', 'product design', 'visual design'],
        'data': ['data scientist', 'data analyst', 'analytics', 'machine learning'],
        'sales': ['account executive', 'ae', 'sales', 'business development'],
        'customer_success': ['customer success', 'csm', 'account manager'],
        'marketing': ['marketing', 'growth', 'demand gen', 'content'],
        'product_marketing': ['product marketing', 'pmm'],
        'engineering_management': ['engineering manager', 'eng manager', 'tech lead'],
        'consulting': ['consultant', 'consulting', 'advisory'],
        'sales_engineering': ['sales engineer', 'solutions engineer', 'se'],
    }

    scores = {}
    for function, keywords in function_signals.items():
        score = sum(1 for kw in keywords if kw in combined_text)
        scores[function] = score

    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return None

    return max(scores, key=scores.get)


def suggest_aligned_functions(experience: Dict[str, Any]) -> str:
    """
    Suggest aligned functions for terminal function mismatch.
    """
    current_function = detect_candidate_function(experience)

    suggestions = {
        'engineering': 'Focus on Engineering, Technical Lead, or Engineering Management roles',
        'product': 'Focus on Product Management, Product Strategy, or Technical PM roles',
        'design': 'Focus on Design, UX Research, or Design Leadership roles',
        'data': 'Focus on Data Science, Analytics, or ML Engineering roles',
        'sales': 'Focus on Sales, Business Development, or Sales Leadership roles',
        'customer_success': 'Focus on Customer Success, Account Management, or CS Leadership roles',
        'marketing': 'Focus on Marketing, Growth, or Marketing Leadership roles',
        'consulting': 'Focus on Strategy, Operations, or Business roles',
    }

    return suggestions.get(current_function, 'Focus on roles aligned with your background')


def suggest_aligned_domains(experience: Dict[str, Any]) -> str:
    """
    Suggest aligned domains for terminal domain mismatch.
    """
    # Extract domain from experience
    domain = experience.get('domain', '')

    adjacency_map = {
        'healthcare': 'healthtech, medtech, insurance, or payer/provider tech',
        'fintech': 'payments, banking, insurance, or financial services',
        'consumer': 'B2C, social, ecommerce, or marketplace',
        'enterprise': 'B2B SaaS, enterprise software, or infrastructure',
        'ecommerce': 'retail, marketplace, or payments',
    }

    if domain:
        suggestion = adjacency_map.get(domain.lower())
        if suggestion:
            return f"Redirect to {suggestion} roles where your {domain} background applies"

    return "Redirect to roles in adjacent domains where your experience transfers"


def suggest_appropriate_level(experience: Dict[str, Any]) -> str:
    """
    Suggest appropriate level for terminal level mismatch.
    """
    # Infer current level
    from .signal_detectors import extract_team_size, detect_org_level_influence

    team_size = extract_team_size(experience)
    org_influence = detect_org_level_influence(experience)

    if team_size >= 50 and org_influence == 'explicit':
        return "Focus on VP or Senior Director roles matching your org leadership experience"
    elif team_size >= 20:
        return "Focus on Director roles matching your team leadership scope"
    elif team_size >= 5:
        return "Focus on Senior Manager or Manager roles matching your people management experience"
    elif org_influence in ['explicit', 'implicit']:
        return "Focus on Staff or Principal IC roles matching your technical influence"
    else:
        return "Focus on Senior IC roles matching your current scope"


def calculate_level_distance(candidate_level: Optional[str], required_level: Optional[str]) -> int:
    """
    Calculate level distance between candidate and required.

    Returns: Number of levels apart (0 = same, 1 = adjacent, etc.)
    """
    if not candidate_level or not required_level:
        return 0

    level_order = [
        'intern', 'junior', 'associate',
        'mid', 'ic3',
        'senior', 'ic4',
        'staff', 'principal', 'ic5',
        'distinguished', 'ic6',
        'manager',
        'senior_manager',
        'director',
        'senior_director',
        'vp',
        'svp',
        'c_suite', 'cto', 'ceo'
    ]

    candidate_normalized = candidate_level.lower().replace(' ', '_').replace('-', '_')
    required_normalized = required_level.lower().replace(' ', '_').replace('-', '_')

    try:
        candidate_idx = None
        required_idx = None

        for i, level in enumerate(level_order):
            if level in candidate_normalized or candidate_normalized in level:
                candidate_idx = i
            if level in required_normalized or required_normalized in level:
                required_idx = i

        if candidate_idx is not None and required_idx is not None:
            return abs(required_idx - candidate_idx)
    except:
        pass

    return 0


def generate_domain_mitigation(candidate_domain: str, required_domain: str) -> str:
    """
    Generate domain positioning advice.
    """
    mitigations = {
        ('fintech', 'payments'): 'Position financial product experience as payments expertise',
        ('payments', 'fintech'): 'Position payment infrastructure knowledge as broader fintech skills',
        ('healthcare', 'healthtech'): 'Position clinical understanding as healthtech domain knowledge',
        ('consumer', 'enterprise'): 'Position user empathy as buyer understanding',
        ('enterprise', 'consumer'): 'Position stakeholder management as user research skills',
        ('ecommerce', 'fintech'): 'Position checkout and payments experience as fintech exposure',
    }

    if candidate_domain and required_domain:
        key = (candidate_domain.lower(), required_domain.lower())
        if key in mitigations:
            return mitigations[key]

    return f"Position {candidate_domain} experience as transferable to {required_domain}"


def detect_red_flag_reason(experience: Dict[str, Any], requirements: Dict[str, Any]) -> str:
    """
    Detect specific red flag reason.
    """
    from .signal_detectors import (
        detect_press_release_pattern,
        detect_scale_inconsistency
    )

    if detect_press_release_pattern(experience):
        return 'Resume lacks specificity (no tension, no tradeoffs, no failures)'

    if detect_scale_inconsistency(experience):
        return 'Claims inconsistent with company size/stage'

    return 'Red flag pattern detected'


def generate_generic_mitigation(gap_type: str) -> str:
    """
    Generate generic mitigation advice.
    """
    mitigations = {
        'skill': 'Position transferable skills and learning ability',
        'experience': 'Position adjacent experience with clear bridge',
        'context': 'Position adaptability and relevant parallel experience',
    }

    return mitigations.get(gap_type, 'Position relevant experience as transferable')
