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

    # Generate "Your Move" (ALWAYS generate, even with silence)
    # CORRECTED: Silence suppresses gaps, not "Your Move"
    # Pass full calibrated_gaps for dominant_narrative and strong_signals access
    # NEW: Also pass strengths and role_title for role-specific binding
    your_move_raw = generate_your_move(
        primary_gap=calibrated_gaps.get('primary_gap'),
        job_fit_recommendation=job_fit_recommendation,
        redirect_reason=calibrated_gaps.get('redirect_reason'),
        candidate_resume=candidate_resume,
        job_requirements=job_requirements,
        calibrated_gaps=calibrated_gaps,
        strengths=strengths,
        role_title=role_title
    )

    # Sanitize: Remove em dashes and enforce clean sentence structure
    your_move = _sanitize_your_move(your_move_raw)

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

        # Extract role-specific signals from strengths
        role_signals = _extract_role_signals(strengths or [], role_title or '', job_requirements)

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


def _extract_role_signals(strengths: List[str], role_title: str, job_requirements: Dict[str, Any]) -> List[str]:
    """
    Extract role-specific signals from strengths list.

    Looks for concrete capabilities that match the role:
    - Technical: Kubernetes, SRE, distributed systems, platform, infrastructure
    - Domain: ads, consumer, enterprise, fintech, healthcare
    - Scale: API volume, user counts, team size

    Returns: List of role-specific signal phrases (max 2), or empty if none found.
    """
    if not strengths:
        return []

    role_lower = (role_title or '').lower()
    domain = (job_requirements.get('domain', '') or '').lower()

    # Define role-specific keywords to look for
    role_keywords = {
        'technical': ['kubernetes', 'k8s', 'sre', 'distributed', 'platform', 'infrastructure',
                     'reliability', 'scaling', 'api', 'backend', 'microservices', 'cloud',
                     'aws', 'gcp', 'azure', 'docker', 'container', 'openshift', 'rosa'],
        'product': ['product', 'roadmap', 'strategy', 'user research', 'metrics', 'okr',
                   'a/b test', 'experimentation', 'discovery', 'launch'],
        'data': ['data', 'analytics', 'ml', 'machine learning', 'ai', 'pipeline',
                'warehouse', 'etl', 'sql', 'python'],
        'leadership': ['team of', 'engineers', 'reports', 'hired', 'built team', 'grew team',
                      'managed', 'led', 'cross-functional'],
        'scale': ['million', 'M users', 'M requests', 'api requests', 'traffic',
                 'uptime', '99.', 'latency', 'throughput']
    }

    # Detect what type of role this is
    role_type = 'general'
    if any(k in role_lower for k in ['sre', 'reliability', 'platform', 'infrastructure', 'devops', 'cloud']):
        role_type = 'technical'
    elif any(k in role_lower for k in ['product', 'pm', 'growth']):
        role_type = 'product'
    elif any(k in role_lower for k in ['data', 'analytics', 'ml', 'machine learning']):
        role_type = 'data'

    signals = []

    for strength in strengths:
        if not isinstance(strength, str):
            continue

        strength_lower = strength.lower()

        # Check for role-type specific keywords
        keywords_to_check = role_keywords.get(role_type, []) + role_keywords.get('scale', []) + role_keywords.get('leadership', [])

        for keyword in keywords_to_check:
            if keyword in strength_lower:
                # Extract a clean signal phrase
                signal = _clean_signal_phrase(strength, keyword)
                if signal and signal not in signals:
                    signals.append(signal)
                    break  # Only one signal per strength

        if len(signals) >= 2:
            break

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
