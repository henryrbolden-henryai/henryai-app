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

            # CRITICAL: Preserve coaching controller's strategic_action if already set
            # The coaching controller runs BEFORE post-processors and sets a carefully
            # crafted "Your Move" message. We must not overwrite it.
            existing_strategic_action = processed.get("reality_check", {}).get("strategic_action")

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

            # Restore coaching controller's strategic_action if it was set
            if existing_strategic_action:
                processed["reality_check"]["strategic_action"] = existing_strategic_action
                if config.debug_mode:
                    print(f"   ✅ Preserved coaching strategic_action: {existing_strategic_action[:50]}...")

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
    # STEP 4: Recommendation-Action Consistency
    # Ensure timing_guidance and action fields match the recommendation
    # =========================================================================
    processed = _enforce_action_recommendation_consistency(processed, recommendation)
    if config.debug_mode:
        print("✅ Action-Recommendation consistency enforced")

    # =========================================================================
    # STEP 5: Text Sanitization (Em dash removal, cleanup)
    # Applies globally to prevent AI-generated artifacts
    # =========================================================================
    processed = _sanitize_text_fields(processed)
    if config.debug_mode:
        print("✅ Text sanitization applied (em dashes, etc.)")

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


def _enforce_action_recommendation_consistency(data: Dict[str, Any], recommendation: str) -> Dict[str, Any]:
    """
    Ensure timing_guidance and action fields are consistent with the recommendation.

    Rules:
    - "Do Not Apply" / "Skip" → "Skip this one" or "Pass"
    - "Long Shot" → "Only if you have an inside connection"
    - "Apply with Caution" → Standard timing (no urgency language)
    - "Apply" / "Consider" → "Apply today" or "Apply this week"
    - "Strong Apply" → "Apply immediately"

    Contradictions (e.g., "Do Not Apply" + "Apply today") are fixed.
    """
    recommendation_lower = (recommendation or "").lower()

    # Map recommendation to valid timing_guidance values
    timing_map = {
        "strong apply": "Apply immediately",
        "strongly apply": "Apply immediately",
        "apply": "Apply today",
        "consider": "Apply if interested",
        "apply with caution": "Apply with caution - prepare positioning",
        "conditional apply": "Apply with caution - prepare positioning",
        "long shot": "Only pursue if you have an inside connection",
        "do not apply": "Skip this one",
        "skip": "Skip this one",
    }

    # Determine correct timing
    correct_timing = None
    for key, value in timing_map.items():
        if key in recommendation_lower:
            correct_timing = value
            break

    if not correct_timing:
        # Default based on recommendation tier
        if "not" in recommendation_lower or "skip" in recommendation_lower:
            correct_timing = "Skip this one"
        elif "caution" in recommendation_lower:
            correct_timing = "Apply with caution - prepare positioning"
        else:
            correct_timing = "Apply today"

    # Fix timing_guidance in intelligence_layer.apply_decision
    intelligence_layer = data.get("intelligence_layer", {})
    apply_decision = intelligence_layer.get("apply_decision", {})

    if apply_decision:
        current_timing = apply_decision.get("timing_guidance", "")

        # Detect contradictions
        is_skip_recommendation = "not" in recommendation_lower or "skip" in recommendation_lower
        has_apply_language = any(phrase in current_timing.lower() for phrase in [
            "apply today", "apply immediately", "apply now", "apply soon", "apply this week"
        ])

        if is_skip_recommendation and has_apply_language:
            print(f"   ⚠️ ACTION CONTRADICTION: '{recommendation}' with timing '{current_timing}'")
            print(f"   ✅ Fixed to: '{correct_timing}'")
            apply_decision["timing_guidance"] = correct_timing
            apply_decision["_timing_corrected"] = True

        # Also fix apply_decision.recommendation if mismatched
        decision_rec = apply_decision.get("recommendation", "")
        if is_skip_recommendation and "apply" in decision_rec.lower() and "not" not in decision_rec.lower():
            if "skip" not in decision_rec.lower():
                print(f"   ⚠️ DECISION CONTRADICTION: Main rec='{recommendation}', decision rec='{decision_rec}'")
                apply_decision["recommendation"] = "Skip"
                print(f"   ✅ Fixed apply_decision.recommendation to: 'Skip'")

        intelligence_layer["apply_decision"] = apply_decision
        data["intelligence_layer"] = intelligence_layer

    return data


def _sanitize_text_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize all text fields to remove AI-generated artifacts.

    Specifically targets:
    - Em dashes (—) → replaced with period + space for sentence break
    - En dashes (–) → replaced with period + space
    - Double spaces
    - Orphaned punctuation
    """
    import re

    def sanitize_text(text: str) -> str:
        if not text or not isinstance(text, str):
            return text

        # Replace em/en dashes with period + space for sentence breaks
        if '—' in text or '–' in text:
            text = text.replace('—', '. ')
            text = text.replace('–', '. ')
            # Clean up double periods and extra spaces
            text = text.replace('..', '.')
            text = text.replace('.  ', '. ')
            # Capitalize after new periods
            text = re.sub(r'\.\s+([a-z])', lambda m: '. ' + m.group(1).upper(), text)

        # Fix double spaces
        text = re.sub(r'\s{2,}', ' ', text)

        # Fix orphaned punctuation (space before punctuation)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)

        return text.strip()

    def recurse(obj):
        if isinstance(obj, dict):
            return {k: recurse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recurse(item) for item in obj]
        elif isinstance(obj, str):
            return sanitize_text(obj)
        else:
            return obj

    return recurse(data)


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
