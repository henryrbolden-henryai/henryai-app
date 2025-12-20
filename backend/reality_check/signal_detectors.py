"""
Reality Check Signal Detectors

Implements the 6 signal class detectors as specified in REALITY_CHECK_SPEC.md.
Each detector returns a list of RealityCheck objects for its signal class.

CRITICAL: Market Bias and Market Climate signals NEVER modify fit_score.
"""

import re
from typing import Dict, Any, List, Optional
from .models import RealityCheck, SignalClass, Severity


def detect_eligibility_signals(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    eligibility_result: Optional[Dict[str, Any]] = None
) -> List[RealityCheck]:
    """
    Detect Eligibility Signals - hard requirements that block application.

    Examples:
    - Missing required domain expertise
    - Seniority mismatch
    - Non-transferable ownership gaps
    - Work authorization requirements
    - Education/certification mandates

    Returns: List of RealityCheck objects (Blocker severity only)
    """
    checks = []

    # Use pre-computed eligibility result if available
    if eligibility_result and not eligibility_result.get("eligible", True):
        reason = eligibility_result.get("reason", "Eligibility requirements not met")
        failed_check = eligibility_result.get("failed_check", "unknown")

        checks.append(RealityCheck(
            signal_class=SignalClass.ELIGIBILITY,
            severity=Severity.BLOCKER,
            trigger=failed_check,
            message=reason,
            strategic_alternatives=[
                "Focus on roles that match your current qualifications",
                "Build the required experience or credentials before applying",
                "Look for related roles with fewer hard requirements",
            ],
            evidence=f"Failed eligibility check: {failed_check}",
            allowed_outputs=["blocker"],
        ))

    # Check for certification requirements
    jd_text = (jd_data.get("job_description", "") or "").lower()
    role_title = (jd_data.get("role_title", "") or "").lower()

    # Required certifications
    cert_patterns = [
        (r'\b(pmp|project management professional)\s+(required|certification required)', "PMP Certification"),
        (r'\bactive\s+security\s+clearance\s+required', "Security Clearance"),
        (r'\b(cpa|certified public accountant)\s+required', "CPA Certification"),
        (r'\b(cissp|cism)\s+required', "Security Certification"),
        (r'\bbar\s+admission\s+required', "Bar Admission"),
        (r'\b(rn|registered nurse)\s+license\s+required', "RN License"),
        (r'\bpe\s+license\s+required', "PE License"),
    ]

    resume_text = _extract_resume_text(resume_data).lower()

    for pattern, cert_name in cert_patterns:
        if re.search(pattern, jd_text):
            # Check if candidate has this certification
            cert_keywords = cert_name.lower().split()
            has_cert = any(kw in resume_text for kw in cert_keywords)

            if not has_cert:
                checks.append(RealityCheck(
                    signal_class=SignalClass.ELIGIBILITY,
                    severity=Severity.BLOCKER,
                    trigger=f"missing_certification:{cert_name}",
                    message=f"This role requires {cert_name}. This is typically an automatic filter. Do Not Apply unless you have this certification or can obtain it quickly.",
                    strategic_alternatives=[
                        f"Obtain {cert_name} before applying",
                        "Look for similar roles that don't require this certification",
                        "Consider roles at companies willing to wait for certification",
                    ],
                    evidence=f"JD requires '{cert_name}', not found in resume",
                    allowed_outputs=["blocker"],
                ))

    return checks


def detect_fit_signals(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    fit_score: float,
    fit_details: Optional[Dict[str, Any]] = None
) -> List[RealityCheck]:
    """
    Detect Fit Signals - experience quality and quantity matching.

    Examples:
    - Fit score below threshold
    - Skill alignment gaps
    - Experience level mismatch
    - Scope disconnect

    CRITICAL: Internships never count toward years of experience.

    Returns: List of RealityCheck objects (Warning, Coaching)
    """
    checks = []

    # Fit score threshold check
    if fit_score < 40:
        checks.append(RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.WARNING,
            trigger=f"fit_score_below_threshold:{fit_score}",
            message=f"Your fit score is {fit_score}% (below our 40% threshold). This indicates significant gaps between your experience and role requirements.",
            strategic_alternatives=[
                "Only proceed if you have exceptional referrals or inside connections",
                "Focus on roles where you are 60%+ fit",
                "Consider adjacent roles that leverage your existing strengths",
            ],
            evidence=f"Fit score: {fit_score}%",
            allowed_outputs=["warning", "coaching"],
        ))
    elif fit_score < 60:
        checks.append(RealityCheck(
            signal_class=SignalClass.FIT,
            severity=Severity.COACHING,
            trigger=f"fit_score_stretch:{fit_score}",
            message=f"Your fit score is {fit_score}%. This is a stretch role. Focus on demonstrating transferable skills and relevant outcomes.",
            strategic_alternatives=[
                "Lead with your most relevant experience in cover letter",
                "Prioritize employee referrals to bypass initial screening",
                "Apply within first 24-48 hours for best results",
            ],
            evidence=f"Fit score: {fit_score}%",
            allowed_outputs=["coaching"],
        ))

    # Experience level mismatch
    if fit_details:
        years_gap = fit_details.get("years_gap", 0)
        if years_gap >= 3:
            checks.append(RealityCheck(
                signal_class=SignalClass.FIT,
                severity=Severity.WARNING,
                trigger=f"experience_gap:{years_gap}_years",
                message=f"You're missing {years_gap}+ years of required experience. Recruiters will likely screen you out early.",
                strategic_alternatives=[
                    "Focus on roles requiring fewer years of experience",
                    "Emphasize impact density over tenure in your application",
                    "Pursue internal referrals to bypass initial screening",
                ],
                evidence=f"Experience gap: {years_gap} years",
                allowed_outputs=["warning", "coaching"],
            ))

    return checks


def detect_credibility_signals(
    resume_data: Dict[str, Any],
    credibility_result: Optional[Dict[str, Any]] = None
) -> List[RealityCheck]:
    """
    Detect Credibility Signals - believability of scope and achievement claims.

    Examples:
    - Title inflation
    - Implausible metrics
    - Press-release resume language
    - Scope mismatches

    Returns: List of RealityCheck objects (Warning, Coaching)
    """
    checks = []

    # Use pre-computed credibility analysis if available
    if credibility_result:
        title_inflation = credibility_result.get("title_inflation", {})
        if title_inflation.get("detected"):
            actual_level = title_inflation.get("actual_level", "a lower level")
            reason = title_inflation.get("reason", "Title appears inflated")

            checks.append(RealityCheck(
                signal_class=SignalClass.CREDIBILITY,
                severity=Severity.COACHING,
                trigger="title_inflation",
                message=f"Your title may trigger credibility questions. {reason}. This doesn't mean your work wasn't real - just that recruiters will scrutinize it.",
                strategic_alternatives=[
                    "Lead with scope and outcomes rather than titles",
                    "Quantify team size, budget, and business impact",
                    "Prepare to explain your actual responsibilities in interviews",
                ],
                evidence=reason,
                allowed_outputs=["coaching"],
            ))

        # Fabrication risk
        if credibility_result.get("fabrication_risk"):
            checks.append(RealityCheck(
                signal_class=SignalClass.CREDIBILITY,
                severity=Severity.WARNING,
                trigger="fabrication_risk",
                message="Some metrics on your resume appear inconsistent with the company size or stage. This may trigger verification scrutiny.",
                strategic_alternatives=[
                    "Review and adjust any metrics that seem disproportionate",
                    "Provide context for exceptional numbers (e.g., market conditions)",
                    "Be prepared to explain methodology in interviews",
                ],
                evidence="Metrics appear inconsistent with company context",
                allowed_outputs=["warning", "coaching"],
            ))

        # Press release pattern
        if credibility_result.get("press_release_pattern"):
            checks.append(RealityCheck(
                signal_class=SignalClass.CREDIBILITY,
                severity=Severity.COACHING,
                trigger="press_release_pattern",
                message="Your resume reads like a press release - all wins, no challenges. Add evidence of navigating complexity and tradeoffs.",
                strategic_alternatives=[
                    "Include examples of difficult decisions and tradeoffs",
                    "Show how you handled setbacks or pivots",
                    "Demonstrate learning and growth, not just success",
                ],
                evidence="Resume lacks tension, failures, or tradeoffs",
                allowed_outputs=["coaching"],
            ))

    return checks


def detect_risk_signals(
    resume_data: Dict[str, Any],
    risk_analysis: Optional[Dict[str, Any]] = None
) -> List[RealityCheck]:
    """
    Detect Risk Signals - patterns that raise recruiter skepticism.

    Examples:
    - Job hopping (4+ jobs in 2 years)
    - Unexplained career gaps
    - Overqualification
    - Lateral moves after senior roles
    - Industry pivots

    Returns: List of RealityCheck objects (Warning, Coaching)
    """
    checks = []

    if risk_analysis:
        # Job hopping
        job_hopping = risk_analysis.get("job_hopping", {})
        if job_hopping.get("detected"):
            severity = job_hopping.get("severity", "proceed_with_caution")
            pattern = job_hopping.get("pattern", "frequent moves")

            if severity == "stop_search":
                checks.append(RealityCheck(
                    signal_class=SignalClass.RISK,
                    severity=Severity.WARNING,
                    trigger="severe_job_hopping",
                    message="You've had multiple short tenures. Recruiters will question stability and may screen you out.",
                    strategic_alternatives=[
                        "Create a cohesive narrative explaining the transitions",
                        "Address stability proactively in cover letter",
                        "Focus on contract or project-based roles initially",
                    ],
                    evidence=pattern,
                    allowed_outputs=["warning", "coaching"],
                ))
            else:
                checks.append(RealityCheck(
                    signal_class=SignalClass.RISK,
                    severity=Severity.COACHING,
                    trigger="job_hopping",
                    message="Your tenure pattern may raise stability questions. Frame transitions as strategic career building.",
                    strategic_alternatives=[
                        "Prepare a narrative arc explaining your moves",
                        "Emphasize skill progression across roles",
                        "Highlight what you learned at each stage",
                    ],
                    evidence=pattern,
                    allowed_outputs=["coaching"],
                ))

        # Career gaps
        career_gaps = risk_analysis.get("career_gaps", [])
        significant_gaps = [g for g in career_gaps if g.get("months", 0) >= 6]
        if significant_gaps:
            gap = significant_gaps[0]
            months = gap.get("months", 6)

            checks.append(RealityCheck(
                signal_class=SignalClass.RISK,
                severity=Severity.COACHING,
                trigger=f"career_gap:{months}_months",
                message=f"You have a {months}-month gap in your resume. Prepare to address this proactively.",
                strategic_alternatives=[
                    "Frame the gap positively (learning, caregiving, health, exploration)",
                    "Highlight any relevant activities during the gap",
                    "Address briefly in cover letter if gap is recent",
                ],
                evidence=f"{months}-month gap detected",
                allowed_outputs=["coaching"],
            ))

        # Overqualification
        overqualified = risk_analysis.get("overqualified", {})
        if overqualified.get("detected"):
            checks.append(RealityCheck(
                signal_class=SignalClass.RISK,
                severity=Severity.COACHING,
                trigger="overqualified_risk",
                message="Your recent experience suggests you may be perceived as overqualified. Address motivation directly.",
                strategic_alternatives=[
                    "Explain your genuine interest in the scope/stage",
                    "Address the 'flight risk' concern proactively",
                    "Emphasize what you want to learn or contribute",
                ],
                evidence="Recent senior-level scope may trigger overqualification concerns",
                allowed_outputs=["coaching"],
            ))

        # Company pattern mismatch
        company_pattern = risk_analysis.get("company_pattern", {})
        if company_pattern.get("extreme_mismatch"):
            reason = company_pattern.get("reason", "")
            detail = company_pattern.get("detail", "")

            checks.append(RealityCheck(
                signal_class=SignalClass.RISK,
                severity=Severity.COACHING,
                trigger="company_context_mismatch",
                message=f"{reason}. {detail}",
                strategic_alternatives=[
                    "Address context transition in your application",
                    "Emphasize adaptability and scrappy execution",
                    "Highlight any relevant experience at different scales",
                ],
                evidence=reason,
                allowed_outputs=["coaching"],
            ))

    return checks


def detect_market_bias_signals(
    jd_data: Dict[str, Any],
    resume_data: Dict[str, Any]
) -> List[RealityCheck]:
    """
    Detect Market Bias Signals - hiring preferences unrelated to capability.

    CRITICAL: This signal class NEVER modifies fit_score or eligibility.
    It only provides coaching overlays and strategic alternatives.

    Examples:
    - Selective school name-dropping
    - Employer brand clustering ("Ex-FAANG only")
    - Narrow leadership background homogeneity
    - "Culture fit" proxies

    Returns: List of RealityCheck objects (Coaching only)
    """
    checks = []

    jd_text = (jd_data.get("job_description", "") or "").lower()

    # School selectivity bias
    school_patterns = [
        r'\b(ivy league|top-tier|elite)\s+(school|university|institution)',
        r'\b(stanford|harvard|mit|yale|princeton|columbia|berkeley|wharton)\b',
        r'\bpreferred:\s*[^.]*\b(top|elite|prestigious)\s+university',
    ]

    for pattern in school_patterns:
        if re.search(pattern, jd_text):
            checks.append(RealityCheck(
                signal_class=SignalClass.MARKET_BIAS,
                severity=Severity.COACHING,
                trigger="school_selectivity_bias",
                message="Market Bias Signal: This role shows preference for selective school backgrounds. This affects resume screening speed, not your capability. Your experience speaks for itself.",
                strategic_alternatives=[
                    "Prioritize employee referrals to bypass initial screening",
                    "Lead with outcomes and impact over credentials",
                    "Apply within first 24-48 hours for best visibility",
                ],
                evidence="JD contains school selectivity language",
                allowed_outputs=["coaching", "outreach_emphasis"],
            ))
            break  # Only one school bias signal

    # FAANG/Brand bias
    brand_patterns = [
        r'\b(ex-|former\s+)(google|meta|facebook|amazon|apple|microsoft|netflix)\b',
        r'\bpreferred:\s*[^.]*\b(faang|big tech|top tech)\b',
        r'\bexperience\s+at\s+(google|meta|facebook|amazon|apple|microsoft)\s+preferred',
    ]

    for pattern in brand_patterns:
        if re.search(pattern, jd_text):
            checks.append(RealityCheck(
                signal_class=SignalClass.MARKET_BIAS,
                severity=Severity.COACHING,
                trigger="employer_brand_bias",
                message="Market Bias Signal: This role's language suggests preference for FAANG experience. Your background is equally valid. Lead with scale and impact metrics that translate across contexts.",
                strategic_alternatives=[
                    "Emphasize comparable scale and complexity from your experience",
                    "Use metrics that demonstrate similar scope of impact",
                    "Seek referrals from any big-tech connections in your network",
                ],
                evidence="JD contains employer brand preference language",
                allowed_outputs=["coaching", "outreach_emphasis"],
            ))
            break  # Only one brand bias signal

    # Consulting firm preference
    consulting_patterns = [
        r'\b(mckinsey|bain|bcg|deloitte|accenture|pwc)\s+(background|experience)\s+(preferred|required)',
        r'\bconsulting\s+background\s+strongly\s+preferred',
    ]

    for pattern in consulting_patterns:
        if re.search(pattern, jd_text):
            checks.append(RealityCheck(
                signal_class=SignalClass.MARKET_BIAS,
                severity=Severity.COACHING,
                trigger="consulting_background_bias",
                message="Market Bias Signal: This company values consulting backgrounds. Your industry experience provides equally valuable perspective. Emphasize strategic thinking and structured problem-solving.",
                strategic_alternatives=[
                    "Highlight strategic initiatives and cross-functional projects",
                    "Demonstrate structured problem-solving methodology",
                    "Show executive-level communication examples",
                ],
                evidence="JD contains consulting background preference",
                allowed_outputs=["coaching"],
            ))
            break

    return checks


def detect_market_climate_signals(
    resume_data: Dict[str, Any],
    jd_data: Optional[Dict[str, Any]] = None
) -> List[RealityCheck]:
    """
    Detect Market Climate Signals - external conditions creating friction.

    CRITICAL: This signal class NEVER modifies fit_score or eligibility.
    It NEVER instructs identity suppression or work history omission.
    It ALWAYS validates the work's importance.

    Examples:
    - DEI-focused roles during political backlash
    - Climate/sustainability work during regulatory uncertainty
    - Political advocacy or campaign work
    - Industry sensitivity (crypto, cannabis, etc.)

    Returns: List of RealityCheck objects (Informational/Coaching)
    """
    checks = []

    resume_text = _extract_resume_text(resume_data).lower()
    experience = resume_data.get("experience", []) or resume_data.get("roles", [])

    # DEI-focused work detection
    dei_patterns = [
        r'\b(chief diversity officer|cdo|head of dei|dei director|inclusion lead)\b',
        r'\b(diversity|inclusion|equity|belonging)\s+(manager|director|lead|officer|head)\b',
    ]

    dei_company_patterns = [
        r'\bdiversity\s+tech\b',
        r'\binclusion\s+(platform|company|startup)\b',
    ]

    has_dei_role = any(re.search(p, resume_text) for p in dei_patterns)
    has_dei_company = any(re.search(p, resume_text) for p in dei_company_patterns)

    if has_dei_role or has_dei_company:
        checks.append(RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.COACHING,
            trigger="dei_focused_experience",
            message="Market Climate Signal: In the current political climate, some companies are scrutinizing DEI-focused roles more heavily. Your work driving inclusion and belonging is legitimate business impact.",
            strategic_alternatives=[
                "Lead with business outcomes: retention rates, engagement scores, team performance",
                "Frame as organizational effectiveness and talent strategy",
                "Emphasize measurable impact on hiring, development, and retention",
            ],
            evidence="Resume contains DEI-focused role titles or company focus",
            allowed_outputs=["coaching", "framing_guidance"],
        ))

    # Climate/Sustainability work detection
    climate_patterns = [
        r'\b(climate|sustainability)\s+(officer|director|manager|lead)\b',
        r'\b(esg|environmental social governance)\s+(lead|director|manager)\b',
        r'\bclimate\s+justice\b',
        r'\benvironmental\s+activism\b',
    ]

    has_climate_role = any(re.search(p, resume_text) for p in climate_patterns)

    if has_climate_role:
        checks.append(RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="climate_sustainability_experience",
            message="Market Climate Signal: Some companies are currently de-prioritizing climate-focused initiatives due to regulatory uncertainty. Your sustainability work demonstrates strategic thinking and stakeholder management.",
            strategic_alternatives=[
                "Emphasize cost savings, operational efficiency, and risk mitigation",
                "Frame as strategic business transformation",
                "Highlight cross-functional leadership and change management",
            ],
            evidence="Resume contains climate/sustainability role focus",
            allowed_outputs=["informational", "framing_guidance"],
        ))

    # Political campaign/advocacy work
    political_patterns = [
        r'\b(campaign manager|political organizer|advocacy director)\b',
        r'\bworked\s+for\s+[^.]*\b(campaign|pac|political)\b',
    ]

    has_political_work = any(re.search(p, resume_text) for p in political_patterns)

    if has_political_work:
        checks.append(RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="political_advocacy_experience",
            message="Market Climate Signal: Campaign and advocacy work can trigger political concerns in some hiring contexts. Your organizing and coalition-building skills are directly transferable.",
            strategic_alternatives=[
                "Lead with project management and stakeholder alignment",
                "Emphasize measurable outcomes and team leadership",
                "Frame as high-stakes execution and coalition building",
            ],
            evidence="Resume contains political/advocacy role history",
            allowed_outputs=["informational", "framing_guidance"],
        ))

    # Crypto/Web3 work (2022-2024 sensitivity)
    crypto_patterns = [
        r'\b(crypto|blockchain|web3|defi)\s+(manager|director|lead|engineer|pm)\b',
    ]

    has_crypto_work = any(re.search(p, resume_text) for p in crypto_patterns)

    # Check if crypto work is recent (2022-2024)
    if has_crypto_work:
        checks.append(RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="crypto_industry_experience",
            message="Market Climate Signal: Crypto/Web3 experience from 2022-2024 may face additional scrutiny given industry volatility. Your technical and product skills remain valuable.",
            strategic_alternatives=[
                "Emphasize transferable technical skills and system design",
                "Highlight product development and user growth metrics",
                "Frame as high-velocity startup experience",
            ],
            evidence="Resume contains crypto/Web3 role history",
            allowed_outputs=["informational", "framing_guidance"],
        ))

    # Cannabis industry
    cannabis_patterns = [
        r'\b(cannabis|marijuana|thc|cbd)\s+(industry|company|startup)\b',
    ]

    has_cannabis_work = any(re.search(p, resume_text) for p in cannabis_patterns)

    if has_cannabis_work:
        checks.append(RealityCheck(
            signal_class=SignalClass.MARKET_CLIMATE,
            severity=Severity.INFORMATIONAL,
            trigger="cannabis_industry_experience",
            message="Market Climate Signal: Cannabis industry experience may face regulatory and cultural scrutiny in some contexts. Your operational and compliance experience is directly relevant to regulated industries.",
            strategic_alternatives=[
                "Emphasize regulatory compliance and operational excellence",
                "Highlight experience navigating complex legal environments",
                "Frame as heavily regulated industry expertise",
            ],
            evidence="Resume contains cannabis industry role history",
            allowed_outputs=["informational", "framing_guidance"],
        ))

    return checks


def _extract_resume_text(resume_data: Dict[str, Any]) -> str:
    """Extract all text from resume data for pattern matching."""
    parts = []

    # Summary/About
    if resume_data.get("summary"):
        parts.append(resume_data["summary"])

    # Experience
    experience = resume_data.get("experience", []) or resume_data.get("roles", [])
    for exp in experience:
        if isinstance(exp, dict):
            parts.append(exp.get("title", ""))
            parts.append(exp.get("company", ""))
            parts.append(exp.get("description", ""))
            highlights = exp.get("highlights", [])
            if isinstance(highlights, list):
                parts.extend([h for h in highlights if isinstance(h, str)])

    # Skills
    skills = resume_data.get("skills", [])
    if isinstance(skills, list):
        parts.extend([s for s in skills if isinstance(s, str)])
    elif isinstance(skills, dict):
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                parts.extend([s for s in skill_list if isinstance(s, str)])

    # Education
    education = resume_data.get("education", [])
    for edu in education:
        if isinstance(edu, dict):
            parts.append(edu.get("institution", ""))
            parts.append(edu.get("degree", ""))
            parts.append(edu.get("field", ""))

    return " ".join(str(p) for p in parts if p)
