"""
HenryHQ Post-Processors

Unified post-processing pipeline for JD analysis responses.
Applies Reality Check, Strategic Redirects, and Voice Guide in sequence.

This module orchestrates all post-processing without bloating the system prompt.
Each processor is rule-based and deterministic (no additional LLM calls).

Pipeline Order:
1. Reality Check - Market truth signals (never modifies score)
2. Strategic Redirects - Alternative role suggestions (for low-fit)
3. Voice Guide - Tone and messaging corrections

All processors are ADDITIVE or CORRECTIVE, never destructive.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PostProcessorConfig:
    """Configuration for the post-processing pipeline."""
    reality_check_enabled: bool = True
    strategic_redirects_enabled: bool = True
    voice_guide_enabled: bool = True
    voice_guide_strict: bool = False
    debug_mode: bool = False


def apply_all_postprocessors(
    response: Dict[str, Any],
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    fit_score: int,
    recommendation: str,
    config: Optional[PostProcessorConfig] = None,
    eligibility_result: Optional[Dict[str, Any]] = None,
    fit_details: Optional[Dict[str, Any]] = None,
    credibility_result: Optional[Dict[str, Any]] = None,
    risk_analysis: Optional[Dict[str, Any]] = None,
    gap_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Apply all post-processors to an API response.

    This is the main entry point for the post-processing pipeline.
    Call this after Claude returns the initial response.

    Args:
        response: The raw API response from Claude
        resume_data: Parsed resume data
        jd_data: Job description data {role_title, company, job_description}
        fit_score: Calculated fit score
        recommendation: Final recommendation
        config: Optional configuration
        eligibility_result: Pre-computed eligibility analysis
        fit_details: Pre-computed fit analysis details
        credibility_result: Pre-computed credibility analysis
        risk_analysis: Pre-computed risk analysis
        gap_analysis: Pre-computed gap analysis

    Returns:
        Processed response with all post-processors applied
    """
    if config is None:
        config = PostProcessorConfig()

    processed = response.copy()

    # CRITICAL: Capture fit_score before any processing
    original_fit_score = processed.get("fit_score", fit_score)

    # =========================================================================
    # STEP 1: Reality Check (Market truth signals)
    # Per REALITY_CHECK_SPEC.md: NEVER modifies fit_score
    # =========================================================================
    if config.reality_check_enabled:
        try:
            from ..reality_check import analyze_reality_checks

            reality_result = analyze_reality_checks(
                resume_data=resume_data,
                jd_data=jd_data,
                fit_score=fit_score,
                eligibility_result=eligibility_result,
                fit_details=fit_details,
                credibility_result=credibility_result,
                risk_analysis=risk_analysis,
                feature_flag=True,
            )

            processed["reality_check"] = reality_result

            # CRITICAL ASSERTION: Verify fit_score was NOT modified
            if processed.get("fit_score") != original_fit_score:
                print(f"🚨 POST-PROCESSOR GUARDRAIL: Reality Check modified fit_score! Restoring.")
                processed["fit_score"] = original_fit_score

            if config.debug_mode:
                print(f"✅ Reality Check applied: {len(reality_result.get('display_checks', []))} signals")

        except Exception as e:
            print(f"⚠️ Reality Check failed (non-blocking): {str(e)}")
            processed["reality_check"] = {"error": str(e), "checks": []}

    # =========================================================================
    # STEP 2: Strategic Redirects (Alternative role suggestions)
    # Per STRATEGIC_REDIRECTS_IMPLEMENTATION.md: Triggers for low-fit only
    # =========================================================================
    if config.strategic_redirects_enabled:
        try:
            from ..strategic_redirects import generate_strategic_redirects

            # Build inputs for redirect generator
            target_role = {
                "title": jd_data.get("role_title", processed.get("role_title", "")),
                "level": processed.get("candidate_level", "mid"),
                "company_type": jd_data.get("company", processed.get("company", "")),
            }

            candidate_profile = {
                "current_level": processed.get("candidate_level", "mid"),
                "cec_strengths": processed.get("cec_strengths", []),
                "recent_titles": _extract_recent_titles(resume_data),
                "company_types": _extract_company_types(resume_data),
            }

            gap_analysis_input = gap_analysis or {
                "primary_gap": processed.get("primary_gap", ""),
                "secondary_gap": processed.get("secondary_gap", ""),
                "specific_gaps": processed.get("gaps", []),
            }

            redirect_result = generate_strategic_redirects(
                target_role=target_role,
                candidate_profile=candidate_profile,
                gap_analysis=gap_analysis_input,
                fit_score=fit_score,
                recommendation=recommendation,
            )

            # Only include if triggered
            if redirect_result.get("triggered", False):
                processed["strategic_redirects"] = redirect_result

                if config.debug_mode:
                    print(f"✅ Strategic Redirects applied: {redirect_result.get('total_suggestions', 0)} suggestions")

        except Exception as e:
            print(f"⚠️ Strategic Redirects failed (non-blocking): {str(e)}")

    # =========================================================================
    # STEP 3: Voice Guide (Tone and messaging corrections)
    # Per HenryHQ_voice_guide.md: Light-touch corrections only
    # =========================================================================
    if config.voice_guide_enabled:
        try:
            from ..voice_guide import apply_voice_guide

            processed = apply_voice_guide(
                processed,
                strict_mode=config.voice_guide_strict
            )

            if config.debug_mode:
                if processed.get("_voice_guide_applied"):
                    summary = processed.get("_voice_guide_summary", {})
                    print(f"✅ Voice Guide applied: {summary.get('total_corrections_applied', 0)} corrections")

        except Exception as e:
            print(f"⚠️ Voice Guide failed (non-blocking): {str(e)}")

    # =========================================================================
    # FINAL ASSERTION: Verify fit_score integrity
    # =========================================================================
    final_fit_score = processed.get("fit_score")
    if final_fit_score != original_fit_score:
        print(f"🚨 POST-PROCESSOR FINAL CHECK: fit_score changed from {original_fit_score} to {final_fit_score}!")
        print(f"   Restoring original score. This is a bug that needs investigation.")
        processed["fit_score"] = original_fit_score
        processed["_fit_score_restored"] = True

    return processed


def _extract_recent_titles(resume_data: Dict[str, Any]) -> list:
    """Extract recent job titles from resume data."""
    titles = []
    for exp in resume_data.get("experience", [])[:3]:
        if isinstance(exp, dict) and exp.get("title"):
            titles.append(exp["title"])
    return titles


def _extract_company_types(resume_data: Dict[str, Any]) -> list:
    """Extract company types from resume data."""
    types = []
    for exp in resume_data.get("experience", [])[:3]:
        if isinstance(exp, dict):
            company = exp.get("company", "").lower()
            # Simple heuristic
            if any(kw in company for kw in ["startup", "ventures", "labs"]):
                types.append("Startup")
            elif any(kw in company for kw in ["google", "meta", "amazon", "apple", "microsoft"]):
                types.append("FAANG")
            elif any(kw in company for kw in ["consulting", "deloitte", "mckinsey", "bcg"]):
                types.append("Consulting")
            else:
                types.append("Tech company")
    return list(set(types))


__all__ = [
    'apply_all_postprocessors',
    'PostProcessorConfig',
]
