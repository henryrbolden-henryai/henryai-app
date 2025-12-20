# ============================================================================
# CALIBRATION CONTROLLER
# Per Recruiter Calibration Spec v1.0 (REVISED)
#
# Purpose: Control layer that enforces gap classification and priority ranking.
# CEC detects capabilities. This controller decides which gaps matter.
#
# CORE INVARIANT (SYSTEM_CONTRACT.md §0):
# "If it doesn't make the candidate better, no one wins."
#
# Outputs must improve candidate decision quality.
# Do not soften, inflate, or redirect unless it materially makes the candidate better.
#
# HARD CONSTRAINTS:
# - Does NOT override Job Fit recommendation
# - Does NOT change fit scores
# - Calibration explains a "Do Not Apply," it does NOT create one
# - locked_reason comes from Job Fit only
# - Calibration provides redirect_reason for coaching, not for changing recommendation
#
# RECRUITER REALITY CHECK:
# - If candidate shows ≥3 strong signals, suppress coachable gaps for that capability
# - Explicit outcomes override missing keyword patterns
# - Think like a recruiter, not a rule engine
# ============================================================================

from typing import Dict, List, Any, Optional, Tuple
import re
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
            'suppressed_gaps': list (for internal logging),
            'strong_signals': dict (for coaching controller),
            'dominant_narrative': str or None (for Strong Apply)
        }

    CRITICAL: This function does NOT override Job Fit recommendation.
    It only interprets and prioritizes gaps for coaching output.
    """
    # Defensive: ensure inputs are dicts, not strings
    if not isinstance(cec_results, dict):
        cec_results = {}
    if not isinstance(candidate_resume, dict):
        candidate_resume = {}
    if not isinstance(job_requirements, dict):
        job_requirements = {}

    # === LOGGING: ENTRY ===
    print("\n" + "=" * 80)
    print("🎯 CALIBRATION CONTROLLER - ENTRY")
    print("=" * 80)
    print(f"   Job Fit Recommendation: {job_fit_recommendation}")
    print(f"   CEC Results Present: {bool(cec_results)}")

    # ==========================================================================
    # STEP 0: EVIDENCE SANITY CHECK (Recruiter Reality Assertion)
    # If candidate shows ≥3 strong signals, they're credible. Don't nitpick.
    # ==========================================================================
    strong_signals = count_strong_signals(candidate_resume, cec_results)
    explicit_capabilities = count_explicit_capabilities(cec_results)
    dominant_narrative = extract_dominant_narrative(candidate_resume, job_requirements)

    print(f"   Strong Signals Total: {strong_signals.get('total', 0)}")
    print(f"   Explicit Capabilities: {explicit_capabilities}")
    print(f"   Dominant Narrative: {dominant_narrative[:50] if dominant_narrative else 'None'}...")

    def _log_and_return(result: Dict[str, Any], exit_reason: str) -> Dict[str, Any]:
        """Helper to log calibration result before returning."""
        print("\n" + "-" * 80)
        print("🎯 CALIBRATION CONTROLLER - EXIT")
        print("-" * 80)
        print(f"   Exit Reason: {exit_reason}")
        primary = result.get('primary_gap')
        if primary:
            gap_name = primary.get('gap', {}).get('capability', 'Unknown')
            gap_class = primary.get('classification', 'Unknown')
            print(f"   Primary Gap: {gap_name} ({gap_class})")
        else:
            print(f"   Primary Gap: None")
        print(f"   Secondary Gaps: {len(result.get('secondary_gaps', []))}")
        print(f"   Redirect Reason: {result.get('redirect_reason', 'None')[:50] if result.get('redirect_reason') else 'None'}")
        print(f"   Suppress Gaps Section: {result.get('suppress_gaps_section')}")
        print(f"   Suppressed Gaps: {len(result.get('suppressed_gaps', []))}")
        print(f"   Recruiter Override: {result.get('recruiter_override', 'None')}")
        print("=" * 80 + "\n")
        return result

    # Recruiter Reality Assertion:
    # If Job Fit = "Strong Apply" AND ≥2 capabilities are explicit, suppress all gaps
    if job_fit_recommendation == "Strong Apply" and explicit_capabilities >= 2:
        return _log_and_return({
            'primary_gap': None,
            'secondary_gaps': [],
            'redirect_reason': None,
            'suppress_gaps_section': True,
            'suppressed_gaps': [],
            'strong_signals': strong_signals,
            'dominant_narrative': dominant_narrative,
            'recruiter_override': 'strong_explicit_evidence'
        }, "Strong Apply + ≥2 explicit capabilities")

    # Extract all gaps from CEC results
    all_gaps = extract_all_gaps_from_cec(cec_results)
    print(f"   Total Gaps Extracted from CEC: {len(all_gaps)}")

    # Step 1: Classify each gap, respecting strong signal overrides
    classified_gaps = []
    for gap in all_gaps:
        # Check if this capability has strong explicit evidence that overrides the gap
        if should_suppress_gap_due_to_strong_signals(gap, strong_signals, cec_results):
            classified_gaps.append({
                'gap': gap,
                'classification': 'suppressed',
                'reason': 'Overridden by strong explicit signals',
                'redirect': None,
                'mitigation': None
            })
            continue

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

    # Log classification counts
    terminal_count = sum(1 for g in classified_gaps if g['classification'] == 'terminal')
    coachable_count = sum(1 for g in classified_gaps if g['classification'] == 'coachable')
    suppressed_count = sum(1 for g in classified_gaps if g['classification'] == 'suppressed')
    print(f"   Gap Classification: {terminal_count} terminal, {coachable_count} coachable, {suppressed_count} suppressed")

    # Step 2: Filter by Job Fit decision
    # If "Strong Apply", suppress gaps section (but allow strategic guidance)
    if job_fit_recommendation == "Strong Apply":
        return _log_and_return({
            'primary_gap': None,
            'secondary_gaps': [],
            'redirect_reason': None,
            'suppress_gaps_section': True,
            'suppressed_gaps': classified_gaps,
            'strong_signals': strong_signals,
            'dominant_narrative': dominant_narrative
        }, "Strong Apply (standard path)")

    # If "Apply", check if strong signals warrant gap suppression
    if job_fit_recommendation == "Apply" and strong_signals.get('total', 0) >= 3:
        # =====================================================================
        # STAFF+ PM CALIBRATION MODIFIER
        # For Staff+ PM roles, require at least one system-level signal
        # to reach "Apply". Otherwise cap at "Conditional Apply".
        # =====================================================================
        role_title = (job_requirements.get('role_title', '') or '').lower()
        is_staff_plus_pm = (
            ('staff' in role_title or 'principal' in role_title or 'senior' in role_title) and
            ('product' in role_title or 'pm' in role_title)
        )

        if is_staff_plus_pm:
            # Check for system-level signals in JD
            jd_text = (job_requirements.get('job_description', '') or '').lower()
            system_level_patterns = [
                'attribution', 'governance', 'internal platform', 'org-wide',
                'company-wide', 'strategic initiative', 'executive', 'c-suite',
                'system design', 'architecture'
            ]
            jd_has_system_signals = any(p in jd_text for p in system_level_patterns)

            # Check for candidate system-level evidence
            resume_text = _build_resume_text(candidate_resume).lower()
            candidate_has_system_evidence = any(p in resume_text for p in system_level_patterns)

            if jd_has_system_signals and not candidate_has_system_evidence:
                print(f"   ⚠️ STAFF+ PM RULE: System-level signals required but not found in resume")
                print(f"      JD requires: {[p for p in system_level_patterns if p in jd_text][:3]}")
                print(f"      Capping at Conditional Apply (not blocking Apply recommendation)")
                # Don't suppress gaps - let them inform coaching
                # This affects coaching tone, not the recommendation itself
                return _log_and_return({
                    'primary_gap': None,
                    'secondary_gaps': [],
                    'redirect_reason': None,
                    'suppress_gaps_section': False,  # Show gaps for Staff+ PM
                    'suppressed_gaps': classified_gaps,
                    'strong_signals': strong_signals,
                    'dominant_narrative': dominant_narrative,
                    'recruiter_override': 'staff_pm_system_signals_missing',
                    'staff_pm_warning': 'System-level signals required but not found'
                }, "Apply + Staff+ PM without system signals")

        return _log_and_return({
            'primary_gap': None,
            'secondary_gaps': [],
            'redirect_reason': None,
            'suppress_gaps_section': True,
            'suppressed_gaps': classified_gaps,
            'strong_signals': strong_signals,
            'dominant_narrative': dominant_narrative,
            'recruiter_override': 'strong_signals_apply'
        }, "Apply + ≥3 strong signals")

    # If "Do Not Apply", only terminal gaps matter for coaching explanation
    if job_fit_recommendation == "Do Not Apply":
        relevant_gaps = [g for g in classified_gaps if g['classification'] == 'terminal']
    elif job_fit_recommendation in ["Apply with Caution", "Apply"]:
        relevant_gaps = [g for g in classified_gaps if g['classification'] in ['terminal', 'coachable']]
    else:
        relevant_gaps = classified_gaps

    # Step 3: Apply gap hierarchy (Priority order)
    terminal_gaps = [g for g in relevant_gaps if g['classification'] == 'terminal']
    coachable_gaps = [g for g in relevant_gaps if g['classification'] == 'coachable']
    suppressed_gaps = [g for g in classified_gaps if g['classification'] == 'suppressed']

    # Step 4: Rank gaps by priority
    prioritized_terminal = rank_gaps_by_priority(terminal_gaps)
    prioritized_coachable = rank_gaps_by_priority(coachable_gaps)

    # Step 5: Select primary gap and secondary gaps
    if prioritized_terminal:
        primary_gap = prioritized_terminal[0]
        secondary_gaps = []
        redirect_reason = primary_gap.get('redirect')
        suppress_gaps_section = False
    elif prioritized_coachable:
        primary_gap = prioritized_coachable[0]
        secondary_gaps = prioritized_coachable[1:3]
        assert len(secondary_gaps) <= 2, "Secondary gaps must not exceed 2"
        redirect_reason = None
        suppress_gaps_section = False
    else:
        primary_gap = None
        secondary_gaps = []
        redirect_reason = None
        suppress_gaps_section = True

    return _log_and_return({
        'primary_gap': primary_gap,
        'secondary_gaps': secondary_gaps,
        'redirect_reason': redirect_reason,
        'suppress_gaps_section': suppress_gaps_section,
        'suppressed_gaps': suppressed_gaps,
        'strong_signals': strong_signals,
        'dominant_narrative': dominant_narrative
    }, f"Standard path ({job_fit_recommendation})")


def count_strong_signals(candidate_resume: Dict[str, Any], cec_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Counts strong signals from resume that indicate credibility.

    Signal hierarchy (in order of strength):
    1. Decision authority (hiring, budget, P&L ownership)
    2. Scale (users, traffic, revenue, uptime)
    3. Business impact (cost savings, growth percentage, launch outcomes)
    4. Org scope (team size, platform ownership, multi-team influence)

    Returns dict with signal counts and specific proof points.
    """
    # Defensive: ensure inputs are dicts
    if not isinstance(candidate_resume, dict):
        candidate_resume = {}
    if not isinstance(cec_results, dict):
        cec_results = {}

    signals = {
        'decision_authority': [],
        'scale': [],
        'business_impact': [],
        'org_scope': [],
        'total': 0
    }

    # Build combined text from resume
    combined_text = _build_resume_text(candidate_resume)

    # 1. Decision Authority Signals
    authority_patterns = [
        (r'hired\s+\d+', 'hiring authority'),
        (r'built\s+(?:\w+\s+)*(?:a\s+)?team\s+(?:of\s+)?\d+', 'team building'),
        (r'\$[\d.]+[MBK]?\+?\s*(?:budget|p&l|revenue)', 'budget ownership'),
        (r'p&l\s*(?:ownership|responsibility)', 'P&L ownership'),
        (r'(?:own|owned|owning)\s+(?:the\s+)?(?:roadmap|strategy|vision)', 'strategic ownership'),
        (r'(?:led|leading|lead)\s+(?:the\s+)?(?:decision|initiative|transformation)', 'decision authority'),
        (r'(?:approved|approving)\s+(?:budget|headcount|spend)', 'approval authority'),
    ]
    for pattern, label in authority_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            signals['decision_authority'].append(label)

    # 2. Scale Signals
    scale_patterns = [
        (r'(\d+(?:\.\d+)?)\s*(?:million|M)\s*(?:users|customers|DAU|MAU)', 'user scale'),
        (r'(\d+(?:\.\d+)?)\s*(?:billion|B)\s*(?:requests|transactions)', 'traffic scale'),
        (r'\$(\d+(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:revenue|ARR|GMV)', 'revenue scale'),
        (r'(\d{2,})\s*%\s*(?:uptime|availability|SLA)', 'reliability scale'),
        (r'(?:scaled|grew|increased)\s+(?:from\s+)?\d+\s*(?:to|→)\s*\d+', 'growth trajectory'),
        (r'(\d+)k\+?\s*(?:users|customers|transactions)', 'K-scale users'),
    ]
    for pattern, label in scale_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            signals['scale'].append(label)

    # 3. Business Impact Signals
    impact_patterns = [
        (r'(?:saved|reduced)\s*\$?(\d+(?:\.\d+)?)\s*(?:million|M|K)', 'cost savings'),
        (r'(\d+)\s*%\s*(?:increase|growth|improvement)', 'percentage growth'),
        (r'launched\s+(?:\w+\s+)*(?:product|feature|platform)', 'product launch'),
        (r'(?:drove|achieved|delivered)\s+\$?(\d+)', 'revenue impact'),
        (r'(?:reduced|improved)\s+(?:\w+\s+)*by\s+(\d+)\s*%', 'efficiency gain'),
        (r'(?:0|zero)\s*(?:to|→)\s*(?:\$?\d+|launch)', 'zero-to-one'),
    ]
    for pattern, label in impact_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            signals['business_impact'].append(label)

    # 4. Org Scope Signals
    scope_patterns = [
        (r'(?:team|org)\s*(?:of\s+)?(\d{2,})\s*(?:people|engineers|members)?', 'large team'),
        (r'(?:managed|led|oversaw)\s+(\d+)\s*(?:direct|reports|engineers)', 'direct reports'),
        (r'(?:cross-functional|multi-team|org-wide)', 'org influence'),
        (r'(?:platform|infrastructure|core)\s*(?:team|org)', 'platform scope'),
        (r'(?:global|international|multi-region)', 'global scope'),
        (r'(?:VP|Director|Head\s+of)', 'executive level'),
    ]
    for pattern, label in scope_patterns:
        if re.search(pattern, combined_text, re.IGNORECASE):
            signals['org_scope'].append(label)

    # Calculate total unique signals
    signals['total'] = (
        min(len(signals['decision_authority']), 2) +  # Cap each category
        min(len(signals['scale']), 2) +
        min(len(signals['business_impact']), 2) +
        min(len(signals['org_scope']), 2)
    )

    return signals


def count_explicit_capabilities(cec_results: Dict[str, Any]) -> int:
    """
    Counts capabilities with explicit evidence status.
    """
    # Defensive: ensure cec_results is a dict
    if not isinstance(cec_results, dict):
        return 0

    if 'capability_evidence_report' in cec_results:
        report = cec_results.get('capability_evidence_report')
        if isinstance(report, dict):
            evaluated = report.get('evaluated_capabilities', [])
        else:
            evaluated = []
    elif 'evaluated_capabilities' in cec_results:
        evaluated = cec_results.get('evaluated_capabilities', [])
    else:
        return 0

    # Defensive: ensure evaluated is a list
    if not isinstance(evaluated, list):
        return 0

    return sum(1 for cap in evaluated if isinstance(cap, dict) and cap.get('evidence_status') == 'explicit')


def extract_dominant_narrative(
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> Optional[str]:
    """
    Extracts ONE dominant narrative for Strong Apply coaching.

    Hierarchy:
    1. Decision authority (hiring, budget, ownership)
    2. Scale (users, traffic, revenue, uptime)
    3. Business impact (cost savings, growth)
    4. Org scope (team size, platform ownership)

    Returns a specific, concrete statement, NOT a generic phrase.
    """
    # Defensive: ensure inputs are dicts
    if not isinstance(candidate_resume, dict):
        candidate_resume = {}
    if not isinstance(job_requirements, dict):
        job_requirements = {}

    combined_text = _build_resume_text(candidate_resume)

    # Priority 1: Decision Authority
    # Find ALL matches and use the largest number (most impressive)
    # Patterns:
    # - "hired X" or "hired and onboarded X"
    # - "built a team of X" or "built and scaled a team of X"
    # - "lead/led team of X engineers"
    hire_patterns = [
        r'hired\s+(?:\w+\s+)*(\d+)',  # "hired 8", "hired and onboarded 8"
        r'built\s+(?:\w+\s+)*(?:a\s+)?team\s+(?:of\s+)?(\d+)',  # "built and scaled a team of 40"
        r'(?:lead|led)\s+(?:a\s+)?team\s+(?:of\s+)?(\d+)',  # "lead team of 12"
    ]
    hire_matches = []
    for pattern in hire_patterns:
        hire_matches.extend(re.findall(pattern, combined_text, re.IGNORECASE))
    if hire_matches:
        max_count = max(int(m) for m in hire_matches)
        return f"built and scaled a team of {max_count}"

    budget_match = re.search(r'\$(\d+(?:\.\d+)?)\s*([MBK])\s*(?:budget|p&l)', combined_text, re.IGNORECASE)
    if budget_match:
        amount, unit = budget_match.groups()
        return f"owned ${amount}{unit} P&L"

    # Priority 2: Scale
    user_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:million|M)\s*(?:users|customers|DAU|MAU)', combined_text, re.IGNORECASE)
    if user_match:
        count = user_match.group(1)
        return f"scaled product to {count}M users"

    revenue_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:revenue|ARR)', combined_text, re.IGNORECASE)
    if revenue_match:
        amount = revenue_match.group(1)
        unit = 'B' if 'billion' in combined_text.lower() else 'M'
        return f"drove ${amount}{unit} revenue"

    # Priority 3: Business Impact
    savings_match = re.search(r'(?:saved|reduced)\s*\$(\d+(?:\.\d+)?)\s*([MK])', combined_text, re.IGNORECASE)
    if savings_match:
        amount, unit = savings_match.groups()
        return f"delivered ${amount}{unit} in cost savings"

    growth_match = re.search(r'(\d+)\s*%\s*(?:increase|growth|improvement)\s+(?:in\s+)?(\w+)', combined_text, re.IGNORECASE)
    if growth_match:
        pct, metric = growth_match.groups()
        return f"drove {pct}% {metric} growth"

    # Priority 4: Org Scope
    team_match = re.search(r'(?:led|managed|oversaw)\s+(?:a\s+)?(?:team\s+of\s+)?(\d+)\s*(?:\+\s*)?(?:engineers|people|reports)', combined_text, re.IGNORECASE)
    if team_match:
        count = team_match.group(1)
        return f"led a team of {count}"

    # Fallback: Look for platform/product ownership
    if re.search(r'(?:owned|own)\s+(?:the\s+)?(?:platform|product|roadmap)', combined_text, re.IGNORECASE):
        return "owned the product roadmap end-to-end"

    return None


def should_suppress_gap_due_to_strong_signals(
    gap: Dict[str, Any],
    strong_signals: Dict[str, Any],
    cec_results: Dict[str, Any]
) -> bool:
    """
    Determines if a gap should be suppressed because candidate has strong
    explicit signals in that capability area.

    Rule: If candidate has ≥3 strong signals (scope + scale + authority),
    suppress all coachable gaps for that capability.
    """
    # Defensive: ensure inputs are dicts
    if not isinstance(gap, dict):
        return False
    if not isinstance(strong_signals, dict):
        strong_signals = {}
    if not isinstance(cec_results, dict):
        cec_results = {}

    capability_id = gap.get('capability_id', '').lower()

    # Check if this capability has explicit evidence
    if 'capability_evidence_report' in cec_results:
        report = cec_results.get('capability_evidence_report')
        if isinstance(report, dict):
            evaluated = report.get('evaluated_capabilities', [])
        else:
            evaluated = []
    elif 'evaluated_capabilities' in cec_results:
        evaluated = cec_results.get('evaluated_capabilities', [])
    else:
        evaluated = []

    # Defensive: ensure evaluated is a list
    if not isinstance(evaluated, list):
        evaluated = []

    for cap in evaluated:
        if not isinstance(cap, dict):
            continue
        if cap.get('capability_id', '').lower() == capability_id:
            if cap.get('evidence_status') == 'explicit':
                return True  # Explicit evidence overrides implicit/missing

    # Check if strong signals override this gap type
    total_signals = strong_signals.get('total', 0)

    if total_signals >= 3:
        # Leadership gaps suppressed if decision authority signals exist
        if 'leadership' in capability_id or 'scope' in capability_id:
            if strong_signals.get('decision_authority') or strong_signals.get('org_scope'):
                return True

        # Scale gaps suppressed if scale signals exist
        if 'scale' in capability_id:
            if strong_signals.get('scale'):
                return True

        # Cross-functional gaps suppressed if org scope signals exist
        if 'cross_functional' in capability_id:
            if strong_signals.get('org_scope'):
                return True

    return False


def _build_resume_text(candidate_resume: Dict[str, Any]) -> str:
    """Build combined text from resume for pattern matching."""
    # Defensive: handle string or None input
    if not candidate_resume:
        return ''
    if isinstance(candidate_resume, str):
        return candidate_resume
    if not isinstance(candidate_resume, dict):
        return str(candidate_resume)

    parts = []

    summary = candidate_resume.get('summary', '')
    if summary and isinstance(summary, str):
        parts.append(summary)

    experience = candidate_resume.get('experience', []) or []
    # Handle case where experience is a string
    if isinstance(experience, str):
        parts.append(experience)
    elif isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                parts.append(exp.get('title', '') or '')
                parts.append(exp.get('company', '') or '')
                parts.append(exp.get('description', '') or '')
                # Also check bullets/achievements
                bullets = exp.get('bullets', []) or exp.get('achievements', []) or []
                if isinstance(bullets, str):
                    parts.append(bullets)
                elif isinstance(bullets, list):
                    for bullet in bullets:
                        if isinstance(bullet, str):
                            parts.append(bullet)
                        elif isinstance(bullet, dict):
                            parts.append(bullet.get('text', '') or '')
            elif isinstance(exp, str):
                parts.append(exp)

    return ' '.join(filter(None, parts))


def extract_all_gaps_from_cec(cec_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts all evaluated capabilities that have gaps (implicit or missing).

    Returns: list of gap dicts with capability info
    """
    # Defensive: ensure cec_results is a dict
    if not isinstance(cec_results, dict):
        return []

    gaps = []

    # Handle capability_evidence_report structure
    if 'capability_evidence_report' in cec_results:
        report = cec_results.get('capability_evidence_report')
        if isinstance(report, dict):
            evaluated = report.get('evaluated_capabilities', [])
        else:
            evaluated = []
    elif 'evaluated_capabilities' in cec_results:
        evaluated = cec_results.get('evaluated_capabilities', [])
    else:
        evaluated = []

    # Defensive: ensure evaluated is a list
    if not isinstance(evaluated, list):
        return []

    for cap in evaluated:
        # Defensive: ensure cap is a dict
        if not isinstance(cap, dict):
            continue
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
    2. Wrong domain (zero transferability) - EXCEPTION: Manager-level roles
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
    4. Domain gaps for Manager-level roles (managers can learn domains)

    CRITICAL RULE: Manager-level roles CANNOT have terminal domain gaps.
    Managers are hired for leadership ability, not domain expertise.
    Domain gaps for managers are ALWAYS coachable or suppressed.
    """
    capability_id = gap.get('capability_id', '').lower()
    capability_name = gap.get('capability', '').lower()
    evidence_status = gap.get('evidence_status', 'missing')
    criticality = gap.get('criticality', 'preferred')

    # ==========================================================================
    # CHECK: Is this a Manager-level role?
    # Manager-level roles have special handling for domain gaps.
    # ==========================================================================
    role_title = (job_requirements.get('role_title', '') or job_requirements.get('title', '') or '').lower()
    is_manager_role = any(x in role_title for x in [
        'manager', 'director', 'head of', 'vp ', 'vice president',
        'lead', 'chief', 'cto', 'ceo', 'coo', 'cfo', 'cmo'
    ])

    # Priority 1: Domain gaps
    if 'domain' in capability_id or 'domain' in capability_name:
        candidate_domain = candidate_resume.get('domain', '')
        required_domain = job_requirements.get('domain', '')

        transferability = assess_domain_transferability(candidate_domain, required_domain)

        # ==========================================================================
        # MANAGER EXCEPTION: Domain gaps are ALWAYS suppressed for manager-level roles
        # Managers are hired for leadership, not domain expertise.
        # Domain gaps should NOT appear in "Your Move" or "Gaps to Address" for managers.
        # ==========================================================================
        if is_manager_role:
            print(f"   🔄 MANAGER RULE: Suppressing domain gap entirely for manager role (transferability={transferability})")
            return {
                'type': 'suppressed',
                'reason': 'Domain gap suppressed for manager-level role (hired for leadership)'
            }

        # Non-manager roles: standard domain gap handling
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
