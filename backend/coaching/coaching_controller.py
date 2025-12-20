# ============================================================================
# COACHING CONTROLLER
# Per Selective Coaching Moments Spec v1.0 (REVISED)
#
# Purpose: Consumes calibrated_gaps and governs what gets said to users.
#
# CORE INVARIANT (SYSTEM_CONTRACT.md §0):
# "If it doesn't make the candidate better, no one wins."
#
# Outputs must improve candidate decision quality.
# Do not soften, inflate, or redirect unless it materially makes the candidate better.
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
    user_proceeded_anyway: bool = False,
    strengths: Optional[List[str]] = None,
    role_title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enforces Selective Coaching Moments Spec v1.0.

    Input:
        - calibrated_gaps: output from calibration_controller
        - job_fit_recommendation: str
        - candidate_resume: dict
        - job_requirements: dict
        - user_proceeded_anyway: bool
        - strengths: list of strength strings from response (for role-specific binding)
        - role_title: job title (for role context)

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

    # =========================================================================
    # UI CONTRACT: Single Source of Truth for Presentation State
    #
    # This flag determines what Your Move MAY reference.
    # Computed ONCE, used everywhere. No downstream guessing.
    #
    # RULES:
    # - gaps_visible = False → Your Move may NOT reference gaps
    # - strengths_available = False → Use positioning fallback, not generic gap copy
    # =========================================================================

    # Step 1: Compute gaps_to_render FIRST (before any Your Move logic)
    suppress_gaps_section = calibrated_gaps.get('suppress_gaps_section', False)
    has_gaps = bool(calibrated_gaps.get('primary_gap') or calibrated_gaps.get('secondary_gaps'))

    gaps_to_render = []
    if not suppress_gaps_section and has_gaps:
        show_gaps = should_show_gaps_section(
            job_fit_recommendation=job_fit_recommendation,
            primary_gap=calibrated_gaps.get('primary_gap')
        )
        if show_gaps:
            gaps_to_render = format_gaps_for_display(
                primary_gap=calibrated_gaps.get('primary_gap'),
                secondary_gaps=calibrated_gaps.get('secondary_gaps', [])
            )

    # Step 2: Build UI Contract (THE ONLY AUTHORITY)
    ui_contract = {
        "gaps_visible": not suppress_gaps_section and len(gaps_to_render) > 0,
        "strengths_available": strengths is not None and len(strengths) > 0,
        "recommendation": job_fit_recommendation
    }

    print(f"   📋 UI Contract: gaps_visible={ui_contract['gaps_visible']}, strengths_available={ui_contract['strengths_available']}")

    # =========================================================================
    # STRENGTHS EXTRACTION RECOVERY (uses UI contract)
    #
    # If strengths extraction fails:
    # - Check UI contract for gaps visibility
    # - If gaps visible → gap-focused move
    # - If gaps NOT visible → positioning move (no gap language!)
    # =========================================================================

    if not ui_contract['strengths_available']:
        print("   🚨 CONTRACT BREACH: Strengths extraction returned 0 items")
        print("   📋 Recovery: Using UI contract to determine Your Move copy")

        # Use UI contract to determine the right fallback
        if ui_contract['gaps_visible']:
            # Gaps ARE visible - can reference them
            informational_your_move = _generate_gap_focused_move(
                job_fit_recommendation=job_fit_recommendation,
                calibrated_gaps=calibrated_gaps,
                job_requirements=job_requirements
            )
            print("   ✅ Recovery path: gap-focused move (gaps visible)")
        else:
            # Gaps NOT visible - positioning move only
            informational_your_move = _generate_positioning_move(
                job_fit_recommendation=job_fit_recommendation,
                job_requirements=job_requirements
            )
            print("   ✅ Recovery path: positioning move (gaps suppressed)")

        return {
            'your_move': informational_your_move,
            'gaps_to_address': gaps_to_render if ui_contract['gaps_visible'] else None,
            'show_accountability_banner': False,
            'accountability_message': None,
            '_contract_state': 'strengths_extraction_recovery',
            '_strengths_count': 0,
            '_ui_contract': ui_contract
        }

    # Generate "Your Move" (ALWAYS generate, even with silence)
    # Gaps influence the tone even when suppressed from display
    your_move_raw = generate_your_move(
        primary_gap=calibrated_gaps.get('primary_gap'),
        job_fit_recommendation=job_fit_recommendation,
        redirect_reason=calibrated_gaps.get('redirect_reason'),
        candidate_resume=candidate_resume,
        job_requirements=job_requirements,
        calibrated_gaps=calibrated_gaps,  # Gaps still influence coaching tone
        strengths=strengths,
        role_title=role_title
    )

    # Sanitize: Remove em dashes and enforce clean sentence structure
    your_move = _sanitize_your_move(your_move_raw)

    # =========================================================================
    # UI CONTRACT ASSERTION: Your Move must not reference gaps when none visible
    # =========================================================================
    if not ui_contract['gaps_visible']:
        gap_language = ['gaps below', 'address gaps', 'missing experience', 'close the gap', 'gaps identified', 'highlighted gaps']
        your_move_lower = your_move.lower()
        for phrase in gap_language:
            if phrase in your_move_lower:
                print(f"   🚨 UI CONTRACT VIOLATION: Your Move contains '{phrase}' but gaps_visible=False")
                # Do NOT block - just log. This should never happen with proper generation.
                break

    # Use pre-computed gaps_to_render (from UI contract computation above)
    gaps_to_address = gaps_to_render if ui_contract['gaps_visible'] else None
    if not ui_contract['gaps_visible'] and has_gaps:
        print("   🔇 Gaps suppressed from UI (but still influenced coaching tone)")

    result = {
        'your_move': your_move,
        'gaps_to_address': gaps_to_address,
        'show_accountability_banner': False,
        'accountability_message': None,
        '_ui_contract': ui_contract
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
    calibrated_gaps: Optional[Dict[str, Any]] = None,
    strengths: Optional[List[str]] = None,
    role_title: Optional[str] = None
) -> str:
    """
    Generates "Your Move" section per Selective Coaching Spec.

    HARD REQUIREMENTS:
    - Max 3 sentences
    - Must reference role-specific capabilities (not generic leadership)
    - Structure: Positioning + Action + Timing/Channel

    BINDING RULES by recommendation tier:
    - Apply/Strong Apply: Reference role-specific strengths, immediate action, concrete tactic
    - Conditional Apply: Emphasize positioning + gap mitigation
    - Do Not Apply: Redirect or upskilling

    BANNED (unless tied to role evidence):
    - "Position as a proven leader"
    - "Lead with outcomes"
    - "Apply soon"
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
        # CONDITIONAL APPLY: Strict Action Contract (max 80 words)
        #
        # Structure:
        # 1. POSITIONING (1 sentence): How to frame yourself
        # 2. RESUME FOCUS (1-2 bullets inline): What to emphasize/downplay
        # 3. EXECUTION (1 sentence): Apply timing + outreach action
        #
        # No fluff. No repetition of strengths. Answer: "What do I literally do next?"
        # ==========================================================================

        # If no primary gap visible (e.g., domain gap suppressed for managers),
        # provide generic positioning guidance without gap-specific reframing
        if not primary_gap:
            # Check for dominant_narrative from calibration
            dominant_narrative = calibrated_gaps.get('dominant_narrative') if calibrated_gaps else None
            if dominant_narrative:
                return (f"Position yourself as a proven leader. You {dominant_narrative}. "
                       f"Lead with outcomes, not credentials. "
                       f"Apply within 24 hours with a targeted note positioning yourself as a platform-first leader.")
            else:
                return (f"Position your leadership experience around this role's core needs. "
                       f"Lead with outcomes and team impact; cut tangential experience. "
                       f"Apply within 24 hours and reach out to the hiring manager directly.")

        gap = primary_gap.get('gap', {}) if primary_gap else {}
        gap_capability = (gap.get('capability', '') or gap.get('capability_id', '') or '').lower()
        target_domain = job_requirements.get('domain', '')

        # Extract specific gap context for reframing instruction
        # Mobile, ads, healthcare, etc. - weaponize the gap
        gap_surface = _extract_gap_surface(gap_capability, target_domain)

        # Determine gap type and build tight action contract
        if 'domain' in gap_capability or 'healthcare' in gap_capability or 'ads' in gap_capability:
            # Domain/surface gap - translate experience into target language
            if gap_surface:
                return (f"Position as platform-scale leadership with {gap_surface}-adjacent impact. "
                       f"Lead with customer-facing delivery and cross-functional wins; de-emphasize pure infra. "
                       f"Apply within 24 hours with a targeted note to the hiring manager.")
            else:
                return (f"Position as cross-domain leadership with transferable platform scale. "
                       f"Lead with customer impact and team scaling; downplay domain-specific depth. "
                       f"Apply within 24 hours and reach out directly on LinkedIn.")

        elif 'leadership' in gap_capability or 'scope' in gap_capability or 'level' in gap_capability:
            # Leadership/scope gap - show trajectory
            return (f"Position as high-trajectory leader with expanding scope. "
                   f"Stack team growth and increased ownership at the top; cut flat-looking tenures. "
                   f"Apply fast and address trajectory directly in your outreach.")

        elif 'experience' in gap_capability or 'years' in gap_capability:
            # Experience years gap - lead with impact density
            return (f"Position on impact density, not tenure. "
                   f"Lead with your biggest outcomes; remove date-heavy formatting. "
                   f"Apply within 24 hours. Speed matters when competing on results.")

        elif 'mobile' in gap_capability or 'web' in gap_capability or 'surface' in gap_capability:
            # Surface/platform gap (mobile, web, ads)
            return (f"Position as platform-agnostic leader who scales across surfaces. "
                   f"Emphasize any mobile/web-adjacent work; frame platform experience as transferable. "
                   f"Apply within 24 hours with a note highlighting cross-surface delivery.")

        else:
            # Generic coachable gap - still tight and actionable
            return (f"Position your experience around this role's core needs. "
                   f"Lead with directly relevant outcomes; cut tangential experience. "
                   f"Apply within 24 hours and reach out to the hiring manager directly.")

    elif job_fit_recommendation in ["Strong Apply", "Apply"]:
        # ======================================================================
        # APPLY / STRONG APPLY: Role-Specific, Actionable, Grounded
        #
        # Structure (HARD REQUIREMENT):
        # 1. POSITIONING: Why you fit THIS role (not leadership in general)
        # 2. ACTION: What to emphasize in resume/outreach
        # 3. TIMING/CHANNEL: Apply now, reach out directly, or both
        #
        # MUST reference role-specific capabilities from strengths
        # ======================================================================

        # Extract role-specific signals from strengths (with candidate evidence validation)
        role_signals = _extract_role_signals(
            strengths or [],
            role_title or '',
            job_requirements,
            candidate_resume=candidate_resume
        )

        # Get dominant narrative for proof point
        dominant_narrative = calibrated_gaps.get('dominant_narrative') if calibrated_gaps else None

        # Build role-specific "Your Move"
        if role_signals:
            # We have role-specific signals - use them
            signal_text = role_signals[0]  # Top signal
            additional_signal = role_signals[1] if len(role_signals) > 1 else None

            if additional_signal:
                positioning = f"Your {signal_text} and {additional_signal} directly match this role's core requirements."
            else:
                positioning = f"Your {signal_text} directly matches this role's core requirements."

            action = f"Emphasize this experience prominently in your resume and outreach."
            timing = "Apply now and prioritize a direct message to the hiring manager. ATS volume is high."

            return f"{positioning} {action} {timing}"

        elif dominant_narrative:
            # Fall back to dominant narrative but tie to role
            role_context = _get_role_context(role_title or '', job_requirements)
            if role_context:
                return (f"You {dominant_narrative}. This aligns with {role_context}. "
                       f"Lead with this proof point in your application. "
                       f"Apply now and reach out directly to bypass ATS filtering.")
            else:
                return (f"You {dominant_narrative}. "
                       f"Lead with this accomplishment in your application and outreach. "
                       f"Apply now. Strong matches move fast.")

        else:
            # Last resort - extract from resume text
            key_strength = extract_primary_strength(candidate_resume, job_requirements, calibrated_gaps)
            if key_strength:
                return (f"Your {key_strength} positions you competitively. "
                       f"Emphasize this directly in your resume header and outreach. "
                       f"Apply now and message the hiring manager on LinkedIn.")
            else:
                # Absolute fallback - still role-aware
                role_context = _get_role_context(role_title or '', job_requirements)
                if role_context:
                    return (f"You're a competitive match for {role_context}. "
                           f"Lead with your most relevant accomplishments. "
                           f"Apply now and reach out directly to the hiring manager.")
                else:
                    return (f"You're a competitive match. "
                           f"Lead with your highest-impact, most relevant accomplishment. "
                           f"Apply now and message the hiring manager directly.")

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


def _extract_gap_surface(gap_capability: str, target_domain: str) -> str:
    """
    Extract specific surface/domain from gap for reframing instruction.
    Returns: 'ads', 'mobile', 'healthcare', 'web', etc. or empty string
    """
    gap_lower = gap_capability.lower()
    domain_lower = (target_domain or '').lower()

    # Check gap capability for specific surfaces
    surfaces = ['ads', 'advertising', 'mobile', 'web', 'healthcare', 'fintech', 'ecommerce', 'logistics']
    for surface in surfaces:
        if surface in gap_lower or surface in domain_lower:
            # Normalize
            if surface == 'advertising':
                return 'ads'
            return surface

    # Check for compound terms
    if 'consumer' in gap_lower or 'consumer' in domain_lower:
        return 'consumer'
    if 'enterprise' in gap_lower or 'enterprise' in domain_lower:
        return 'enterprise'
    if 'platform' in gap_lower:
        return 'platform'

    return ''


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


def _build_candidate_evidence_text(candidate_resume: Optional[Dict[str, Any]]) -> str:
    """
    Build combined text from candidate resume for cross-validation.

    Used by _extract_role_signals to ensure keywords are grounded in candidate evidence,
    not just JD keywords that the model hallucinated as strengths.

    Returns: lowercase combined text from resume
    """
    if not candidate_resume:
        return ""

    parts = []

    # Summary
    summary = candidate_resume.get('summary', '')
    if summary:
        parts.append(summary)

    # Skills (explicit skill list)
    skills = candidate_resume.get('skills', []) or []
    for skill in skills:
        if isinstance(skill, str):
            parts.append(skill)
        elif isinstance(skill, dict):
            parts.append(skill.get('name', ''))
            parts.append(skill.get('skill', ''))

    # Experience
    experience = candidate_resume.get('experience', []) or []
    for exp in experience:
        if isinstance(exp, dict):
            parts.append(exp.get('title', ''))
            parts.append(exp.get('company', ''))
            parts.append(exp.get('description', ''))
            # Bullets/achievements
            bullets = exp.get('bullets', []) or exp.get('achievements', []) or []
            for bullet in bullets:
                if isinstance(bullet, str):
                    parts.append(bullet)
                elif isinstance(bullet, dict):
                    parts.append(bullet.get('text', ''))

    # Education
    education = candidate_resume.get('education', []) or []
    for edu in education:
        if isinstance(edu, dict):
            parts.append(edu.get('degree', ''))
            parts.append(edu.get('field', ''))
            parts.append(edu.get('institution', ''))

    # Projects
    projects = candidate_resume.get('projects', []) or []
    for proj in projects:
        if isinstance(proj, dict):
            parts.append(proj.get('name', ''))
            parts.append(proj.get('description', ''))

    return ' '.join(filter(None, parts))


def _compute_candidate_signal_profile(candidate_resume: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute a per-candidate signal profile before prioritization.

    This prevents overfitting to a single candidate by ensuring we only
    elevate signals that exist in the candidate's actual background.

    Returns:
        {
            'primary_domains': ['infra', 'sre', ...],
            'secondary_domains': ['product', ...],
            'scale_context': ['150m requests', ...],
            'leadership_context': ['team of 12', ...],
            'evidence_keywords': set of all lowercase keywords found
        }
    """
    if not candidate_resume:
        return {
            'primary_domains': [],
            'secondary_domains': [],
            'scale_context': [],
            'leadership_context': [],
            'evidence_keywords': set()
        }

    evidence_text = _build_candidate_evidence_text(candidate_resume).lower()

    # Domain detection patterns
    domain_patterns = {
        'infra': ['infrastructure', 'platform', 'sre', 'devops', 'cloud', 'kubernetes', 'k8s', 'docker', 'container'],
        'backend': ['backend', 'api', 'server', 'microservice', 'distributed'],
        'frontend': ['frontend', 'react', 'vue', 'angular', 'javascript', 'typescript', 'ui', 'ux'],
        'data': ['data', 'analytics', 'ml', 'machine learning', 'ai', 'pipeline', 'etl'],
        'product': ['product', 'roadmap', 'strategy', 'discovery', 'user research'],
        'mobile': ['mobile', 'ios', 'android', 'swift', 'kotlin'],
    }

    # Scale detection patterns
    scale_patterns = ['million', '100m', '150m', 'requests/day', 'requests per day', 'users', 'traffic',
                     '99.9', 'uptime', 'latency', 'throughput', 'scale']

    # Leadership detection patterns
    leadership_patterns = ['team of', 'engineers', 'reports', 'hired', 'built team', 'grew team',
                          'managed', 'led', 'directed', 'head of', 'director', 'vp']

    # Detect domains
    primary_domains = []
    secondary_domains = []
    for domain, patterns in domain_patterns.items():
        matches = sum(1 for p in patterns if p in evidence_text)
        if matches >= 3:
            primary_domains.append(domain)
        elif matches >= 1:
            secondary_domains.append(domain)

    # Detect scale context
    scale_context = [p for p in scale_patterns if p in evidence_text]

    # Detect leadership context
    leadership_context = [p for p in leadership_patterns if p in evidence_text]

    # Build evidence keyword set (all words for fast lookup)
    evidence_keywords = set(evidence_text.split())

    profile = {
        'primary_domains': primary_domains,
        'secondary_domains': secondary_domains,
        'scale_context': scale_context,
        'leadership_context': leadership_context,
        'evidence_keywords': evidence_keywords
    }

    print(f"   👤 Candidate Signal Profile:")
    print(f"      Primary domains: {primary_domains}")
    print(f"      Secondary domains: {secondary_domains}")
    print(f"      Scale context: {scale_context[:3]}..." if len(scale_context) > 3 else f"      Scale context: {scale_context}")

    return profile


def _extract_jd_signal_profile(job_requirements: Dict[str, Any], role_title: str) -> Dict[str, Any]:
    """
    Extract role-specific signal profile FROM THE JD, not from a global list.

    This prevents candidate → candidate contamination by deriving keywords
    per-JD instead of using a shared global keyword list.

    Returns:
        {
            'jd_keywords': list of keywords extracted from JD,
            'role_type': 'technical' | 'product' | 'data' | 'general',
            'system_level_signals': list of Staff+ level signals if present
        }
    """
    jd_text = (job_requirements.get('job_description', '') or '').lower()
    role_lower = (role_title or '').lower()

    # =========================================================================
    # JD-SCOPED KEYWORD EXTRACTION
    # Keywords are derived from THIS JD, not a global list
    # =========================================================================

    # Technical signal patterns to look for in JD
    technical_patterns = [
        'kubernetes', 'k8s', 'openshift', 'rosa', 'sre', 'reliability',
        'distributed system', 'microservice', 'container', 'docker',
        'infrastructure', 'platform', 'devops', 'cloud', 'aws', 'gcp', 'azure',
        'incident response', 'on-call', 'backend', 'api'
    ]

    # Product signal patterns
    product_patterns = [
        'product', 'roadmap', 'strategy', 'user research', 'metrics', 'okr',
        'a/b test', 'experimentation', 'discovery', 'launch', 'growth',
        'attribution', 'conversion', 'funnel', 'retention'
    ]

    # Data signal patterns
    data_patterns = [
        'data', 'analytics', 'ml', 'machine learning', 'ai', 'pipeline',
        'warehouse', 'etl', 'sql', 'python', 'modeling', 'attribution model'
    ]

    # Scale patterns (apply to all roles)
    scale_patterns = [
        'million', '100m', '150m', 'requests/day', 'traffic', 'uptime',
        '99.9', 'latency', 'throughput', 'scale', 'high-volume'
    ]

    # Staff+ system-level signals (for PM calibration)
    staff_level_patterns = [
        'attribution', 'governance', 'internal platform', 'cross-functional',
        'system design', 'architecture', 'org-wide', 'company-wide',
        'strategic initiative', 'executive', 'c-suite'
    ]

    # Extract keywords that actually appear in the JD
    jd_keywords = []
    for pattern in technical_patterns + product_patterns + data_patterns + scale_patterns:
        if pattern in jd_text:
            jd_keywords.append(pattern)

    # Detect system-level signals for Staff+ roles
    system_level_signals = [p for p in staff_level_patterns if p in jd_text]

    # Detect role type from title AND JD content
    role_type = 'general'
    tech_count = sum(1 for p in technical_patterns if p in jd_text or p in role_lower)
    product_count = sum(1 for p in product_patterns if p in jd_text or p in role_lower)
    data_count = sum(1 for p in data_patterns if p in jd_text or p in role_lower)

    if tech_count >= product_count and tech_count >= data_count and tech_count > 0:
        role_type = 'technical'
    elif product_count >= tech_count and product_count >= data_count and product_count > 0:
        role_type = 'product'
    elif data_count > 0:
        role_type = 'data'

    profile = {
        'jd_keywords': jd_keywords,
        'role_type': role_type,
        'system_level_signals': system_level_signals
    }

    print(f"   📋 JD Signal Profile:")
    print(f"      Role type: {role_type}")
    print(f"      JD keywords: {jd_keywords[:5]}..." if len(jd_keywords) > 5 else f"      JD keywords: {jd_keywords}")
    print(f"      Staff+ signals: {system_level_signals}")

    return profile


def _extract_role_signals(
    strengths: List[str],
    role_title: str,
    job_requirements: Dict[str, Any],
    candidate_resume: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Extract role-specific signals from strengths list.

    SYSTEM CONTRACT COMPLIANCE:
    - Keywords are JD-scoped, not global (prevents cross-candidate contamination)
    - Signals are (candidate, role) scoped - no persistence between runs
    - No reuse of prior candidate narratives, metrics, or examples
    - Leadership fallback only when JD-aligned evidence is insufficient

    ORDERING:
    1. Resume-verified signals that map to JD keywords (highest priority)
    2. Scale signals verified in both JD and resume
    3. Leadership fallback (only when JD-aligned evidence insufficient)

    Returns: List of role-specific signal phrases (max 2), or empty if none found.
    """
    # CONTRACT: Log extraction attempt for audit trail
    import hashlib
    candidate_hash = hashlib.md5(str(candidate_resume).encode()).hexdigest()[:8] if candidate_resume else "none"
    role_hash = hashlib.md5(f"{role_title}:{job_requirements.get('job_description', '')[:100]}".encode()).hexdigest()[:8]
    print(f"   🔐 Signal extraction scope: candidate={candidate_hash}, role={role_hash}")

    if not strengths:
        print("   🚨 CONTRACT BREACH: _extract_role_signals called with no strengths")
        print("   📋 Breach logged. Returning empty signals (no fallback permitted).")
        return []

    # =========================================================================
    # STEP 1: Extract JD signal profile (JD-scoped, not global)
    # =========================================================================
    jd_profile = _extract_jd_signal_profile(job_requirements, role_title)
    jd_keywords = jd_profile['jd_keywords']
    role_type = jd_profile['role_type']

    if not jd_keywords:
        print("   ⚠️ No JD keywords extracted - falling back to role-type detection")
        # Minimal fallback based on role title only
        role_lower = (role_title or '').lower()
        if 'sre' in role_lower or 'platform' in role_lower or 'infrastructure' in role_lower:
            jd_keywords = ['reliability', 'infrastructure', 'platform']
        elif 'product' in role_lower or 'pm' in role_lower:
            jd_keywords = ['product', 'roadmap', 'metrics']
        elif 'data' in role_lower:
            jd_keywords = ['data', 'analytics', 'pipeline']

    # =========================================================================
    # STEP 2: Build candidate evidence (resume-first)
    # =========================================================================
    candidate_profile = _compute_candidate_signal_profile(candidate_resume)
    candidate_evidence = _build_candidate_evidence_text(candidate_resume) if candidate_resume else ""
    candidate_evidence_lower = candidate_evidence.lower()

    print(f"   🔍 Extracting role signals from {len(strengths)} strengths")
    print(f"   📊 Role type: {role_type}")
    if candidate_evidence_lower:
        print(f"   📄 Candidate evidence: {len(candidate_evidence_lower)} chars")

    # Leadership keywords (for fallback only)
    leadership_keywords = ['team of', 'engineers', 'reports', 'hired', 'built team',
                          'grew team', 'managed', 'cross-functional']

    # =========================================================================
    # RESUME-FIRST EVIDENCE SELECTION
    #
    # Priority order:
    # 1. JD keywords that exist in BOTH strength AND candidate resume (weight 1.0)
    # 2. Scale keywords in both (weight 0.7)
    # 3. Leadership keywords (fallback only, weight 0.5)
    #
    # Dominant narrative is FALLBACK ONLY when JD-aligned evidence insufficient
    # =========================================================================

    scored_signals = []  # List of (signal, weight, keyword)

    # STEP 3: Score signals using JD-derived keywords (not global list)
    for strength in strengths:
        if not isinstance(strength, str) or not strength.strip():
            continue

        strength_lower = strength.lower()

        # Check JD keywords first (highest priority)
        for keyword in jd_keywords:
            if keyword in strength_lower:
                # CANDIDATE SCOPING: Must exist in resume too
                if candidate_evidence_lower and keyword not in candidate_evidence_lower:
                    print(f"   ⚠️ JD keyword '{keyword}' in strength but NOT in resume. Skipping.")
                    continue

                signal = _clean_signal_phrase(strength, keyword)
                if signal:
                    existing = [s[0] for s in scored_signals]
                    if signal not in existing:
                        scored_signals.append((signal, 1.0, keyword))
                        print(f"   ✅ JD-aligned signal: '{signal}' (keyword: '{keyword}')")
                        break

    # Sort by weight and take top 2
    scored_signals.sort(key=lambda x: x[1], reverse=True)
    signals = [s[0] for s in scored_signals[:2]]

    # =========================================================================
    # LEADERSHIP FALLBACK (only when JD-aligned evidence insufficient)
    # This is step 3 in the ordering rule - only used if JD-aligned signals
    # don't exist. If JD signals exist, leadership fallback is NOT allowed.
    # =========================================================================
    if not signals:
        print("   ⚠️ No JD-aligned signals found. Checking leadership fallback.")
        if candidate_profile.get('leadership_context'):
            for strength in strengths:
                if not isinstance(strength, str) or not strength.strip():
                    continue

                strength_lower = strength.lower()

                for keyword in leadership_keywords:
                    if keyword in strength_lower:
                        signal = _clean_signal_phrase(strength, keyword)
                        if signal and signal not in signals:
                            signals.append(signal)
                            print(f"   ✅ Leadership fallback signal: '{signal}'")
                            break

                if len(signals) >= 2:
                    break

    print(f"   📋 Extracted {len(signals)} signals: {signals}")
    return signals


def _clean_signal_phrase(strength: str, matched_keyword: str) -> str:
    """
    Clean up a strength string into a concise signal phrase.

    E.g., "Engineering management experience with distributed systems at scale (150M API requests/day)"
    → "distributed systems experience at scale"
    """
    strength_lower = strength.lower()

    # Try to extract the most relevant part
    # Look for patterns like "X experience with Y" or "Y expertise"
    patterns = [
        (r'(\w+(?:\s+\w+)?)\s+experience\s+(?:with\s+)?([^(]+)', r'\2 experience'),
        (r'(\w+)\s+expertise\s+(?:with\s+|in\s+)?([^(]+)', r'\2 expertise'),
        (r'strong\s+(\w+(?:\s+\w+)?)\s+background', r'\1 background'),
        (r'proven\s+(?:track record\s+)?(?:in\s+|of\s+)?([^(]+)', r'\1'),
    ]

    import re
    for pattern, replacement in patterns:
        match = re.search(pattern, strength_lower)
        if match:
            result = match.group(0)
            # Clean up parenthetical details but keep key metrics
            result = re.sub(r'\([^)]*\)', '', result).strip()
            # Capitalize first letter
            if result:
                return result[0].upper() + result[1:] if len(result) > 1 else result.upper()

    # If no pattern matched, use a simplified version
    # Remove parenthetical content and clean up
    cleaned = re.sub(r'\([^)]*\)', '', strength).strip()
    # Take first 60 chars max
    if len(cleaned) > 60:
        cleaned = cleaned[:57] + '...'

    return cleaned


def _get_role_context(role_title: str, job_requirements: Dict[str, Any]) -> str:
    """
    Get a concise role context string for use in "Your Move".

    E.g., "Red Hat's ROSA service requirements" or "this platform engineering role"
    """
    role_lower = (role_title or '').lower()
    domain = (job_requirements.get('domain', '') or '').lower()
    company = job_requirements.get('company', '')

    # Try to build a specific context
    if 'sre' in role_lower or 'reliability' in role_lower:
        if company:
            return f"{company}'s reliability engineering needs"
        return "this SRE role's requirements"

    if 'platform' in role_lower or 'infrastructure' in role_lower:
        if company:
            return f"{company}'s platform engineering needs"
        return "this platform role's requirements"

    if 'kubernetes' in domain or 'k8s' in domain or 'openshift' in domain:
        if company:
            return f"{company}'s Kubernetes/container infrastructure"
        return "the container orchestration requirements"

    if 'product' in role_lower:
        if company:
            return f"{company}'s product needs"
        return "this product role"

    if company:
        return f"{company}'s team needs"

    return None  # No specific context available


def _generate_gap_focused_move(
    job_fit_recommendation: str,
    calibrated_gaps: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> str:
    """
    Generate gap-focused "Your Move" when gaps ARE visible.

    Used when:
    - strengths extraction failed
    - gaps ARE rendered (ui_contract.gaps_visible = True)

    This is the ONLY path that may reference gaps in Your Move.
    """
    role_title = job_requirements.get('role_title', 'this role')

    # Get primary gap info
    primary_gap = calibrated_gaps.get('primary_gap')
    gap_summary = ""
    if primary_gap:
        gap_info = primary_gap.get('gap', {})
        gap_summary = gap_info.get('capability', gap_info.get('diagnosis', ''))

    # Generate gap-focused message based on recommendation tier
    if job_fit_recommendation == "Do Not Apply":
        if gap_summary:
            return f"Review the gaps identified below. {gap_summary} is a critical blocker for {role_title}."
        return f"Review the gaps identified below before considering {role_title}."

    elif job_fit_recommendation in ["Apply with Caution", "Conditional Apply"]:
        if gap_summary:
            return f"Address {gap_summary} in your application materials. Review gaps below for positioning guidance."
        return f"Review the highlighted gaps below and address them directly in your application for {role_title}."

    elif job_fit_recommendation in ["Apply", "Strong Apply"]:
        return f"Your background aligns with {role_title}. Review the analysis below and emphasize your most relevant experience."

    else:
        return f"Review the analysis below for {role_title} and focus on addressing any highlighted gaps."


def _generate_positioning_move(
    job_fit_recommendation: str,
    job_requirements: Dict[str, Any]
) -> str:
    """
    Generate positioning-only "Your Move" when gaps are NOT visible.

    Used when:
    - strengths extraction failed
    - gaps are SUPPRESSED or not rendered (ui_contract.gaps_visible = False)

    HARD RULE: This function may NEVER reference gaps.
    No "gaps below", "address gaps", "missing experience", etc.
    """
    role_title = job_requirements.get('role_title', 'this role')

    # Generate positioning-focused message (NO gap language)
    if job_fit_recommendation == "Do Not Apply":
        # Still no gap language - just be direct about fit
        return (
            f"Your background may not align with {role_title}'s core requirements. "
            "Consider roles that better match your domain expertise and experience level."
        )

    elif job_fit_recommendation in ["Apply with Caution", "Conditional Apply"]:
        # Positioning advice without gap references
        return (
            "Lead with your strongest transferable outcomes. "
            "Anchor your application in measurable impact and platform-level ownership. "
            "Be explicit about how your experience maps to this role's core responsibilities."
        )

    elif job_fit_recommendation in ["Apply", "Strong Apply"]:
        return (
            f"Your background aligns with {role_title}. "
            "Lead with your most relevant accomplishments and quantified impact. "
            "Apply now and reach out directly to the hiring manager."
        )

    else:
        # Absolute fallback - still no gap language
        return (
            "Lead with your strongest transferable outcomes. "
            "Anchor your application in measurable impact and platform-level ownership. "
            "Be explicit about how your experience maps to this role's core responsibilities."
        )


def _sanitize_your_move(text: str) -> str:
    """
    Sanitize "Your Move" text to enforce direct, tactical style.

    HARD RULES:
    - No em dashes (—)
    - No en dashes (–)
    - Replace with periods for clean sentence breaks

    This is a final safety net. Primary fix is in the generation code.
    """
    if not text:
        return text

    # Check for em/en dashes
    if '—' in text or '–' in text:
        print("   ⚠️ Em/en dash detected in Your Move. Sanitizing.")
        # Replace em dash with period + space (creates new sentence)
        text = text.replace('—', '. ')
        text = text.replace('–', '. ')
        # Clean up double periods and extra spaces
        text = text.replace('..', '.')
        text = text.replace('.  ', '. ')
        # Capitalize after new periods
        import re
        text = re.sub(r'\.\s+([a-z])', lambda m: '. ' + m.group(1).upper(), text)

    return text
