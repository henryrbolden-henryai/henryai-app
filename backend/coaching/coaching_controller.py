# ============================================================================
# COACHING CONTROLLER
# Per Selective Coaching Moments Spec v1.0 (REVISED)
#
# Purpose: Consumes calibrated_gaps and governs what gets said to users.
#
# HARD CONSTRAINTS:
# - Silence suppresses "Gaps to Address," NOT "Your Move"
# - NO vague language ("some gaps," "most requirements")
# - Max 3 sentences in "Your Move"
# - One action only: Apply, Redirect, or Position
# - Terminal gaps = redirect only, no positioning advice
# - Strong Apply still gets strategic guidance
# ============================================================================

from typing import Dict, List, Any, Optional


def generate_coaching_output(
    calibrated_gaps: Dict[str, Any],
    job_fit_recommendation: str,
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any],
    user_proceeded_anyway: bool = False
) -> Dict[str, Any]:
    """
    Enforces Selective Coaching Moments Spec v1.0.

    Input:
        - calibrated_gaps: output from calibration_controller
        - job_fit_recommendation: str
        - candidate_resume: dict
        - job_requirements: dict
        - user_proceeded_anyway: bool

    Output:
        - coaching_output: dict {
            'your_move': str (max 3 sentences),
            'gaps_to_address': list or None,
            'show_accountability_banner': bool,
            'accountability_message': str or None
        }
    """
    # Handle proceed-anyway scenario first
    if user_proceeded_anyway:
        return {
            'your_move': None,
            'gaps_to_address': None,
            'show_accountability_banner': True,
            'accountability_message': generate_accountability_banner(
                job_fit_recommendation,
                calibrated_gaps.get('redirect_reason')
            )
        }

    # Generate "Your Move" (ALWAYS generate, even with silence)
    # CORRECTED: Silence suppresses gaps, not "Your Move"
    your_move = generate_your_move(
        primary_gap=calibrated_gaps.get('primary_gap'),
        job_fit_recommendation=job_fit_recommendation,
        redirect_reason=calibrated_gaps.get('redirect_reason'),
        candidate_resume=candidate_resume,
        job_requirements=job_requirements
    )

    # Determine "Gaps to Address" visibility
    # CORRECTED: Use suppress_gaps_section flag
    if calibrated_gaps.get('suppress_gaps_section', False):
        gaps_to_address = None
    else:
        show_gaps = should_show_gaps_section(
            job_fit_recommendation=job_fit_recommendation,
            primary_gap=calibrated_gaps.get('primary_gap')
        )

        if show_gaps:
            gaps_to_address = format_gaps_for_display(
                primary_gap=calibrated_gaps.get('primary_gap'),
                secondary_gaps=calibrated_gaps.get('secondary_gaps', [])
            )
        else:
            gaps_to_address = None

    return {
        'your_move': your_move,
        'gaps_to_address': gaps_to_address,
        'show_accountability_banner': False,
        'accountability_message': None
    }


def generate_your_move(
    primary_gap: Optional[Dict[str, Any]],
    job_fit_recommendation: str,
    redirect_reason: Optional[str],
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> str:
    """
    Generates "Your Move" section per Selective Coaching Spec.

    Rules:
    - Max 3 sentences
    - One action only: Apply, Redirect, or Position
    - No mixed signals
    - If terminal gap: no positioning advice, direct redirect only
    - CORRECTED: No vague language like "some gaps"

    Structure:
    [Job Fit Recommendation]: [Reason from CEC if terminal].
    [What to do]: [Specific action].
    [Expectation]: [Reality check on competitiveness].
    """
    if redirect_reason:
        # Terminal gap - redirect only, no positioning
        return f"{job_fit_recommendation}: {redirect_reason}"

    elif job_fit_recommendation == "Do Not Apply":
        # No terminal gap from calibration but fit is poor
        # Must be specific, use primary gap if available
        if primary_gap:
            gap_reason = primary_gap.get('reason', '')
            gap_diagnosis = primary_gap.get('gap', {}).get('diagnosis', gap_reason)
            return f"{job_fit_recommendation}: {gap_diagnosis} Focus on roles that match your domain expertise and experience level."
        else:
            # No gap survived calibration - use general redirect
            return f"{job_fit_recommendation}: Your background does not align with this role's core requirements. Focus on roles that match your domain expertise and experience level."

    elif job_fit_recommendation == "Apply with Caution":
        # Coachable gaps scenario - must reference specific gap
        if primary_gap:
            gap = primary_gap.get('gap', {})
            gap_diagnosis = gap.get('diagnosis', '')
            mitigation = primary_gap.get('mitigation', '')

            if gap_diagnosis and mitigation:
                return f"{job_fit_recommendation}: {gap_diagnosis} {mitigation} This is a stretch—you'll compete with candidates who have direct experience."
            elif gap_diagnosis:
                return f"{job_fit_recommendation}: {gap_diagnosis} Position your relevant experience carefully. This is a stretch—you'll compete with candidates who have direct experience."
            else:
                # Fallback without vague language
                return f"{job_fit_recommendation}: Position your strengths carefully. This is a stretch—you'll compete with candidates who have direct experience."
        else:
            # CORRECTED: If no gap survived calibration, don't invent one
            # Still give actionable guidance without vague language
            return f"{job_fit_recommendation}: Position your strengths carefully and set realistic expectations about competitiveness."

    elif job_fit_recommendation == "Strong Apply":
        # CORRECTED: Strong match still gets strategic guidance
        # Extract specific strengths to lead with
        key_strength = extract_primary_strength(candidate_resume, job_requirements)
        if key_strength:
            return f"{job_fit_recommendation}: Your {key_strength} aligns strongly with this role's requirements. Lead with your most relevant accomplishments and apply within 24 hours."
        else:
            return f"{job_fit_recommendation}: Your background aligns strongly with this role. Lead with your most relevant accomplishments and apply within 24 hours."

    elif job_fit_recommendation == "Apply":
        # Good match - strategic guidance
        key_strength = extract_primary_strength(candidate_resume, job_requirements)
        if key_strength:
            return f"{job_fit_recommendation}: Your {key_strength} aligns well with this role. Emphasize your most relevant experience and apply soon."
        else:
            return f"{job_fit_recommendation}: Your background aligns well with this role. Emphasize your most relevant experience and apply soon."

    else:
        # Fallback - should rarely hit
        return f"{job_fit_recommendation}: Review your positioning strategy and apply if this role aligns with your career goals."


def should_show_gaps_section(
    job_fit_recommendation: str,
    primary_gap: Optional[Dict[str, Any]]
) -> bool:
    """
    Determines if "Gaps to Address" section should be visible.

    Hidden if:
    - Job Fit = "Do Not Apply" (gap already in "Your Move")
    - Job Fit = "Strong Apply" (no gaps worth mentioning)
    - suppress_gaps_section = True (from calibration)
    - User proceeded despite guidance (handled separately)

    Returns: bool
    """
    # Hide for Do Not Apply (gap already in "Your Move")
    if job_fit_recommendation == "Do Not Apply":
        return False

    # Hide for Strong Apply (silence on gaps)
    if job_fit_recommendation == "Strong Apply":
        return False

    # Show for Apply with Caution with coachable gaps
    if job_fit_recommendation in ["Apply with Caution", "Apply"]:
        if primary_gap and primary_gap.get('classification') == 'coachable':
            return True

    return False


def format_gaps_for_display(
    primary_gap: Optional[Dict[str, Any]],
    secondary_gaps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Formats gaps for "Gaps to Address" section.

    Rules:
    - Max 3 gaps total
    - Use CEC diagnosis verbatim
    - Never repeat what's in "Your Move"
    - Only include coachable gaps

    Returns: list of dicts
    """
    formatted_gaps = []

    # Add primary gap if coachable
    if primary_gap and primary_gap.get('classification') == 'coachable':
        gap = primary_gap.get('gap', {})
        formatted_gaps.append({
            'capability': gap.get('capability', gap.get('capability_id', '')),
            'diagnosis': gap.get('diagnosis', ''),
            'distance': gap.get('distance', ''),
            'coachable': True,
            'mitigation': primary_gap.get('mitigation', '')
        })

    # Add secondary gaps (max 2)
    for gap_entry in secondary_gaps[:2]:
        if gap_entry.get('classification') == 'coachable':
            gap = gap_entry.get('gap', {})
            formatted_gaps.append({
                'capability': gap.get('capability', gap.get('capability_id', '')),
                'diagnosis': gap.get('diagnosis', ''),
                'distance': gap.get('distance', ''),
                'coachable': True,
                'mitigation': gap_entry.get('mitigation', '')
            })

    # Ensure max 3 gaps
    return formatted_gaps[:3]


def generate_accountability_banner(
    job_fit_recommendation: str,
    redirect_reason: Optional[str]
) -> str:
    """
    Generates accountability banner for proceed-anyway scenario.

    Template:
    You chose to proceed with [Company] - [Role] despite HenryHQ's guidance
    ([Job Fit recommendation]: [redirect_reason]).

    Your materials are optimized within that constraint.
    """
    if redirect_reason:
        return f"You chose to proceed despite HenryHQ's guidance ({job_fit_recommendation}: {redirect_reason}). Your materials are optimized within that constraint."
    else:
        return f"You chose to proceed despite HenryHQ's guidance ({job_fit_recommendation}). Your materials are optimized within that constraint."


def extract_primary_strength(
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> Optional[str]:
    """
    Extracts the most relevant strength to lead with.

    Returns: str (e.g., "cross-functional leadership experience", "B2B SaaS background")
    """
    # Extract from resume summary or experience
    summary = candidate_resume.get('summary', '') or ''
    experience = candidate_resume.get('experience', []) or []

    # Build combined text
    combined = summary.lower()
    for exp in experience:
        if isinstance(exp, dict):
            combined += f" {exp.get('title', '')} {exp.get('description', '')}".lower()

    # Extract from job requirements
    role_title = job_requirements.get('role_title', '') or ''
    jd_text = job_requirements.get('job_description', '') or ''
    jd_combined = f"{role_title} {jd_text}".lower()

    # Strength categories in priority order
    strength_patterns = [
        ('cross-functional leadership', ['cross-functional', 'cross functional', 'stakeholder']),
        ('B2B SaaS experience', ['b2b', 'saas', 'enterprise software']),
        ('product management experience', ['product manager', 'product management', 'pm']),
        ('engineering leadership', ['engineering manager', 'tech lead', 'led engineers']),
        ('distributed systems expertise', ['distributed', 'microservices', 'at scale']),
        ('data-driven approach', ['data-driven', 'analytics', 'metrics']),
        ('customer-facing experience', ['customer', 'client', 'stakeholder']),
        ('technical depth', ['architect', 'designed', 'built']),
    ]

    # Find first matching strength that's relevant to role
    for strength_name, keywords in strength_patterns:
        # Check if candidate has this strength
        has_strength = any(kw in combined for kw in keywords)
        # Check if role wants this
        role_wants = any(kw in jd_combined for kw in keywords)

        if has_strength and role_wants:
            return strength_name

    # Fallback to generic domain match
    domain = candidate_resume.get('domain', '')
    if domain:
        return f"{domain} background"

    return None
