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
    # === LOGGING: ENTRY ===
    print("\n" + "=" * 80)
    print("💬 COACHING CONTROLLER - ENTRY")
    print("=" * 80)
    print(f"   Job Fit Recommendation: {job_fit_recommendation}")
    print(f"   User Proceeded Anyway: {user_proceeded_anyway}")
    print(f"   Primary Gap Present: {bool(calibrated_gaps.get('primary_gap'))}")
    print(f"   Suppress Gaps Section: {calibrated_gaps.get('suppress_gaps_section')}")
    print(f"   Dominant Narrative: {calibrated_gaps.get('dominant_narrative', 'None')[:50] if calibrated_gaps.get('dominant_narrative') else 'None'}...")

    # Handle proceed-anyway scenario first
    if user_proceeded_anyway:
        result = {
            'your_move': None,
            'gaps_to_address': None,
            'show_accountability_banner': True,
            'accountability_message': generate_accountability_banner(
                job_fit_recommendation,
                calibrated_gaps.get('redirect_reason')
            )
        }
        print("\n" + "-" * 80)
        print("💬 COACHING CONTROLLER - EXIT (Proceed Anyway)")
        print("-" * 80)
        print(f"   Accountability Banner: {result['accountability_message'][:80]}...")
        print("=" * 80 + "\n")
        return result

    # Generate "Your Move" (ALWAYS generate, even with silence)
    # CORRECTED: Silence suppresses gaps, not "Your Move"
    # Pass full calibrated_gaps for dominant_narrative and strong_signals access
    your_move = generate_your_move(
        primary_gap=calibrated_gaps.get('primary_gap'),
        job_fit_recommendation=job_fit_recommendation,
        redirect_reason=calibrated_gaps.get('redirect_reason'),
        candidate_resume=candidate_resume,
        job_requirements=job_requirements,
        calibrated_gaps=calibrated_gaps  # For dominant_narrative
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

    result = {
        'your_move': your_move,
        'gaps_to_address': gaps_to_address,
        'show_accountability_banner': False,
        'accountability_message': None
    }

    # === LOGGING: EXIT ===
    print("\n" + "-" * 80)
    print("💬 COACHING CONTROLLER - EXIT")
    print("-" * 80)
    print(f"   Your Move: {result['your_move'][:100] if result['your_move'] else 'None'}...")
    print(f"   Gaps to Address: {len(result['gaps_to_address']) if result['gaps_to_address'] else 0}")
    print(f"   Show Accountability Banner: {result['show_accountability_banner']}")
    print("=" * 80 + "\n")

    return result


def generate_your_move(
    primary_gap: Optional[Dict[str, Any]],
    job_fit_recommendation: str,
    redirect_reason: Optional[str],
    candidate_resume: Dict[str, Any],
    job_requirements: Dict[str, Any],
    calibrated_gaps: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates "Your Move" section per Selective Coaching Spec.

    Rules:
    - Max 3 sentences
    - One action only: Apply, Redirect, or Position
    - No mixed signals
    - If terminal gap: no positioning advice, direct redirect only
    - NO vague language: "aligns well", "relevant experience", "some gaps"
    - Strong Apply REQUIRES concrete proof point from resume

    Structure:
    [Job Fit Recommendation]: [Specific proof point].
    [What to do]: [Specific action].
    [Expectation]: [Reality check].
    """
    if redirect_reason:
        # Terminal gap - redirect only, no positioning
        return f"{job_fit_recommendation}: {redirect_reason}"

    elif job_fit_recommendation == "Do Not Apply":
        # No terminal gap from calibration but fit is poor
        if primary_gap:
            gap_reason = primary_gap.get('reason', '')
            gap_diagnosis = primary_gap.get('gap', {}).get('diagnosis', gap_reason)
            return f"{job_fit_recommendation}: {gap_diagnosis} Focus on roles that match your domain expertise and experience level."
        else:
            return f"{job_fit_recommendation}: Your background does not align with this role's core requirements. Focus on roles that match your domain expertise and experience level."

    elif job_fit_recommendation in ["Apply with Caution", "Conditional Apply"]:
        # ==========================================================================
        # CONDITIONAL APPLY: Viable but requires strategic execution
        # This is NOT a weak candidate. It means positioning matters.
        #
        # Your Move must answer:
        # 1. What's the gating risk? (name it plainly)
        # 2. How to neutralize it in 24-48 hours? (specific action)
        # 3. Clear go/no-go? (no second-guessing)
        # ==========================================================================

        # Get the primary gap details
        gap = primary_gap.get('gap', {}) if primary_gap else {}
        gap_capability = gap.get('capability', '') or gap.get('capability_id', '')
        gap_diagnosis = gap.get('diagnosis', '')
        mitigation = primary_gap.get('mitigation', '') if primary_gap else ''

        # Get candidate's dominant narrative for positive framing
        dominant_narrative = None
        if calibrated_gaps:
            dominant_narrative = calibrated_gaps.get('dominant_narrative')

        # Get role context for specific guidance
        role_title = (job_requirements.get('role_title', '') or job_requirements.get('title', '') or '').lower()

        # Build decisive, specific "Your Move"
        # Format: [Viability] [Gating risk] [Specific neutralization action] [Urgency]

        # Determine the specific repositioning advice based on gap type
        if 'domain' in gap_capability.lower():
            # Domain gap - reframe around transferable skills
            domain = job_requirements.get('domain', 'this domain')
            if dominant_narrative:
                return (f"You're viable here if you control the narrative. "
                       f"Your strength is that you {dominant_narrative}. "
                       f"Update your resume to lead with customer-facing impact and cross-functional delivery—de-emphasize pure infrastructure unless it ties to product velocity. "
                       f"Apply within 24 hours with a targeted note positioning yourself as a platform-first leader who scales teams across surfaces.")
            else:
                return (f"You're viable here if you control the narrative. "
                       f"This team needs {domain} context—reframe your experience around adjacent domains and transferable leadership. "
                       f"Apply within 24 hours and lead with your cross-functional delivery track record, not domain expertise.")

        elif 'leadership' in gap_capability.lower() or 'scope' in gap_capability.lower():
            # Leadership/scope gap - emphasize trajectory
            if dominant_narrative:
                return (f"You're viable here, but only if you demonstrate trajectory. "
                       f"Lead with the fact that you {dominant_narrative}. "
                       f"Tighten your resume to emphasize growing scope and impact—this role will screen out flat career paths. "
                       f"Apply fast and reach out directly to the hiring manager.")
            else:
                return (f"You're viable here, but only if you demonstrate trajectory. "
                       f"Reframe your resume to show scope expansion over time—highlight team growth, increasing responsibility, or expanded ownership. "
                       f"Apply within 24 hours and address the trajectory question head-on in your outreach.")

        elif 'experience' in gap_capability.lower() or 'years' in gap_capability.lower():
            # Experience years gap - emphasize density of impact
            if dominant_narrative:
                return (f"You're viable here if you emphasize impact density over tenure. "
                       f"Your edge: you {dominant_narrative}. "
                       f"Lead with outcomes, not timeline. Stack your highest-impact work at the top of your resume. "
                       f"Apply within 24 hours—speed matters when you're competing on impact, not years.")
            else:
                return (f"You're viable here if you emphasize impact density over tenure. "
                       f"Don't let years be the story—lead with your highest-impact outcomes and results. "
                       f"Apply fast and reach out directly with a specific accomplishment that proves you punch above your weight class.")

        else:
            # Generic coachable gap - still be decisive
            if dominant_narrative:
                return (f"You're viable here, but positioning matters. "
                       f"Your edge: you {dominant_narrative}. "
                       f"Tighten your resume to lead with this and address the gap directly in your cover letter. "
                       f"Apply within 24 hours—if you apply without repositioning, this role becomes a coin flip.")
            elif gap_diagnosis and mitigation:
                return (f"You're viable here, but positioning matters. "
                       f"{mitigation} "
                       f"Apply within 24 hours and reach out directly to the hiring manager—speed and specificity beat perfection.")
            else:
                return (f"You're viable here, but positioning matters. "
                       f"Reframe your experience to lead with outcomes that map to this role's needs. "
                       f"Apply within 24 hours—if you apply without repositioning, this role becomes a coin flip.")

    elif job_fit_recommendation == "Strong Apply":
        # RECRUITER REALITY: Strong Apply MUST have a concrete proof point
        # No hedging allowed. Reference specific accomplishment.

        # First try dominant_narrative from calibration (most specific)
        dominant_narrative = None
        if calibrated_gaps:
            dominant_narrative = calibrated_gaps.get('dominant_narrative')

        if dominant_narrative:
            # Use the pre-computed dominant narrative
            return f"{job_fit_recommendation}: You {dominant_narrative}. Lead with this in your application and apply within 24 hours."

        # Fall back to extract_primary_strength with calibrated_gaps
        key_strength = extract_primary_strength(candidate_resume, job_requirements, calibrated_gaps)

        if key_strength:
            # BANNED: "aligns strongly", "aligns well", "relevant experience"
            # USE: Concrete statement about their accomplishment
            return f"{job_fit_recommendation}: Your {key_strength} is exactly what this role needs. Apply within 24 hours and reference this directly in your outreach."
        else:
            # Even without specific strength, don't use weak language
            return f"{job_fit_recommendation}: You're competitive for this role. Apply within 24 hours and lead with your highest-impact accomplishment."

    elif job_fit_recommendation == "Apply":
        # Good match - strategic guidance with proof points
        # First try dominant_narrative (verb phrase like "drove $8M revenue")
        dominant_narrative = None
        if calibrated_gaps:
            dominant_narrative = calibrated_gaps.get('dominant_narrative')

        if dominant_narrative:
            # Use "You" + verb phrase format
            return f"{job_fit_recommendation}: You {dominant_narrative}. Lead with this accomplishment and apply soon."

        # Fall back to key_strength (noun phrase like "track record of building teams")
        key_strength = extract_primary_strength(candidate_resume, job_requirements, calibrated_gaps)

        if key_strength:
            # Use "Your" + noun phrase format
            return f"{job_fit_recommendation}: Your {key_strength} positions you well. Lead with this accomplishment and apply soon."
        else:
            # Fallback without weak phrases
            return f"{job_fit_recommendation}: You're a solid match. Lead with your highest-impact accomplishment and apply soon."

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
    job_requirements: Dict[str, Any],
    calibrated_gaps: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Extracts the most relevant strength to lead with.

    UPGRADED: Uses ranked signal hierarchy, returns concrete proof points.

    Hierarchy (in order):
    1. Decision authority (hiring, budget, P&L ownership)
    2. Scale (users, traffic, revenue, uptime)
    3. Business impact (cost savings, growth)
    4. Org scope (team size, platform ownership)

    Returns: str with SPECIFIC accomplishment, NOT generic phrases.

    BANNED phrases (never return these):
    - "aligns well", "relevant experience", "strong background"
    - "cross-functional experience", "leadership experience" (without specifics)
    """
    import re

    # Check if calibrated_gaps has a dominant_narrative (pre-computed)
    if calibrated_gaps and calibrated_gaps.get('dominant_narrative'):
        return calibrated_gaps['dominant_narrative']

    # Build combined text from resume
    combined_text = _build_resume_text_for_strength(candidate_resume)

    # Priority 1: Decision Authority - Most impressive signal
    hire_match = re.search(r'(?:hired|built\s+(?:a\s+)?team\s+of)\s+(\d+)', combined_text, re.IGNORECASE)
    if hire_match:
        count = hire_match.group(1)
        return f"track record of building teams ({count}+ hires)"

    budget_match = re.search(r'\$(\d+(?:\.\d+)?)\s*([MBK])\s*(?:budget|p&l)', combined_text, re.IGNORECASE)
    if budget_match:
        amount, unit = budget_match.groups()
        return f"P&L ownership (${amount}{unit})"

    # Priority 2: Scale - Quantified impact
    user_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:million|M)\s*(?:users|customers|DAU|MAU)', combined_text, re.IGNORECASE)
    if user_match:
        count = user_match.group(1)
        return f"experience scaling to {count}M+ users"

    revenue_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:revenue|ARR|GMV)', combined_text, re.IGNORECASE)
    if revenue_match:
        amount = revenue_match.group(1)
        unit = 'B' if 'billion' in combined_text.lower() else 'M'
        return f"${amount}{unit} revenue impact"

    # Priority 3: Business Impact
    savings_match = re.search(r'(?:saved|reduced)\s*\$(\d+(?:\.\d+)?)\s*([MK])', combined_text, re.IGNORECASE)
    if savings_match:
        amount, unit = savings_match.groups()
        return f"${amount}{unit} cost reduction track record"

    growth_match = re.search(r'(\d+)\s*%\s*(?:increase|growth|improvement)\s+(?:in\s+)?(\w+)', combined_text, re.IGNORECASE)
    if growth_match:
        pct, metric = growth_match.groups()
        return f"{pct}% {metric} growth"

    launch_match = re.search(r'launched\s+(?:(\w+)\s+)?(?:product|platform|feature)', combined_text, re.IGNORECASE)
    if launch_match:
        product = launch_match.group(1)
        if product and product.lower() not in ['a', 'the', 'new', 'major']:
            return f"shipped {product} to market"
        return "zero-to-one product launch experience"

    # Priority 4: Org Scope
    team_match = re.search(r'(?:led|managed|oversaw)\s+(?:a\s+)?(?:team\s+of\s+)?(\d+)\s*(?:\+\s*)?(?:engineers|people|reports|members)', combined_text, re.IGNORECASE)
    if team_match:
        count = team_match.group(1)
        return f"leadership of {count}+ person team"

    # Priority 5: Platform/Product ownership (still specific)
    if re.search(r'(?:owned|own)\s+(?:the\s+)?(?:platform|product|roadmap)', combined_text, re.IGNORECASE):
        return "end-to-end product ownership"

    # Priority 6: Company-specific experience (use actual company names)
    experience = candidate_resume.get('experience', []) or []
    notable_companies = []
    faang_like = ['google', 'meta', 'facebook', 'amazon', 'apple', 'microsoft', 'netflix', 'stripe', 'airbnb', 'uber', 'lyft', 'doordash', 'coinbase', 'square', 'block']

    for exp in experience:
        if isinstance(exp, dict):
            company = (exp.get('company', '') or '').lower()
            for notable in faang_like:
                if notable in company:
                    return f"{exp.get('company', '')} experience"

    # Last resort: Use domain but make it specific
    domain = candidate_resume.get('domain', '')
    if domain:
        # Try to find years in domain
        years_match = re.search(r'(\d+)\+?\s*years?\s*(?:of\s+)?(?:experience|in)', combined_text, re.IGNORECASE)
        if years_match:
            years = years_match.group(1)
            return f"{years}+ years in {domain}"
        return f"deep {domain} expertise"

    # If nothing specific found, return None (don't return weak phrases)
    return None


def _build_resume_text_for_strength(candidate_resume: Dict[str, Any]) -> str:
    """Build combined text from resume for strength extraction."""
    parts = []

    summary = candidate_resume.get('summary', '')
    if summary:
        parts.append(summary)

    experience = candidate_resume.get('experience', []) or []
    for exp in experience:
        if isinstance(exp, dict):
            parts.append(exp.get('title', ''))
            parts.append(exp.get('company', ''))
            parts.append(exp.get('description', ''))
            # Also check bullets/achievements
            bullets = exp.get('bullets', []) or exp.get('achievements', []) or []
            for bullet in bullets:
                if isinstance(bullet, str):
                    parts.append(bullet)
                elif isinstance(bullet, dict):
                    parts.append(bullet.get('text', ''))

    return ' '.join(filter(None, parts))
