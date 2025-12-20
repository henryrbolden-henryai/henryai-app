"""
Voice Guide Formatter

Applies HenryHQ voice standards to API responses.
Post-processing layer that ensures consistent, supportive-but-honest tone.

This is a VALIDATION and LIGHT TOUCH-UP layer, not a complete rewrite.
Heavy rewriting should happen in the prompts; this catches edge cases.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from .patterns import (
    FORBIDDEN_PATTERNS,
    APPROVED_CLOSINGS,
    APPROVED_SUPPORT_PHRASES,
    TONE_CORRECTIONS,
    has_next_step,
    has_forbidden_pattern,
    has_false_encouragement,
    has_shame_language,
)


@dataclass
class VoiceValidationResult:
    """Result of voice validation check."""
    is_valid: bool = True
    issues: List[str] = field(default_factory=list)
    corrections_applied: List[str] = field(default_factory=list)
    original_text: str = ""
    corrected_text: str = ""


class VoiceGuideFormatter:
    """
    Formats and validates text according to HenryHQ voice standards.

    This is a light-touch post-processor. It:
    1. Validates text against voice standards
    2. Applies minimal corrections for common issues
    3. Flags serious violations for logging
    4. Ensures actionable endings

    It does NOT:
    - Completely rewrite content
    - Add substantial new content
    - Remove important information
    """

    # Fields to process in the API response
    TEXT_FIELDS = [
        "your_move",
        "strategic_action",
        "company_context",
        "role_overview",
        "positioning_strategy",
    ]

    # Fields containing lists of strings to process
    LIST_FIELDS = [
        "gaps",
        "strengths",
        "key_responsibilities",
        "lead_with_strengths",
        "gaps_and_mitigation",
        "emphasis_points",
        "avoid_points",
        "positioning_rationale",
    ]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the formatter.

        Args:
            strict_mode: If True, raises exceptions on voice violations.
                         If False, logs warnings and applies corrections.
        """
        self.strict_mode = strict_mode
        self.validation_log: List[VoiceValidationResult] = []

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an entire API response, applying voice corrections.

        Args:
            response: The API response dictionary

        Returns:
            Processed response with voice corrections applied
        """
        processed = response.copy()

        # Process top-level text fields
        for field in self.TEXT_FIELDS:
            if field in processed and isinstance(processed[field], str):
                result = self.process_text(processed[field], field)
                processed[field] = result.corrected_text
                if result.corrections_applied:
                    self.validation_log.append(result)

        # Process list fields
        for field in self.LIST_FIELDS:
            if field in processed and isinstance(processed[field], list):
                processed[field] = [
                    self.process_text(item, f"{field}[{i}]").corrected_text
                    if isinstance(item, str) else item
                    for i, item in enumerate(processed[field])
                ]

        # Process nested structures
        if "intelligence_layer" in processed:
            processed["intelligence_layer"] = self._process_nested(
                processed["intelligence_layer"], "intelligence_layer"
            )

        if "strategic_positioning" in processed:
            processed["strategic_positioning"] = self._process_nested(
                processed["strategic_positioning"], "strategic_positioning"
            )

        # Ensure your_move has a next step
        if "your_move" in processed:
            processed["your_move"] = self._ensure_next_step(
                processed["your_move"], "your_move"
            )

        return processed

    def _process_nested(
        self, obj: Dict[str, Any], parent_key: str
    ) -> Dict[str, Any]:
        """Process nested dictionaries recursively."""
        if not isinstance(obj, dict):
            return obj

        processed = obj.copy()
        for key, value in processed.items():
            full_key = f"{parent_key}.{key}"
            if isinstance(value, str):
                result = self.process_text(value, full_key)
                processed[key] = result.corrected_text
            elif isinstance(value, list):
                processed[key] = [
                    self.process_text(item, f"{full_key}[{i}]").corrected_text
                    if isinstance(item, str) else item
                    for i, item in enumerate(value)
                ]
            elif isinstance(value, dict):
                processed[key] = self._process_nested(value, full_key)

        return processed

    def process_text(self, text: str, field_name: str = "") -> VoiceValidationResult:
        """
        Process a single text field.

        Args:
            text: The text to process
            field_name: Name of the field (for logging)

        Returns:
            VoiceValidationResult with validation status and corrected text
        """
        result = VoiceValidationResult(
            original_text=text,
            corrected_text=text
        )

        if not text or not isinstance(text, str):
            return result

        corrected = text

        # 1. Apply tone corrections
        for pattern, replacement, category in TONE_CORRECTIONS:
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                result.corrections_applied.append(f"Tone correction ({category}): {pattern}")

        # 2. Replace forbidden patterns
        for forbidden, replacement in FORBIDDEN_PATTERNS.items():
            if forbidden.lower() in corrected.lower():
                # Case-insensitive replacement
                pattern = re.compile(re.escape(forbidden), re.IGNORECASE)
                corrected = pattern.sub(replacement, corrected)
                result.corrections_applied.append(f"Removed: '{forbidden}'")

        # 3. Check for false encouragement
        if has_false_encouragement(corrected):
            result.issues.append("Contains false encouragement language")
            result.is_valid = False

        # 4. Check for shame language
        if has_shame_language(corrected):
            result.issues.append("Contains shame/blame language")
            result.is_valid = False

        # 5. Clean up multiple spaces
        corrected = re.sub(r'\s+', ' ', corrected).strip()

        # 6. Clean up sentence starts after removals
        corrected = re.sub(r'\.\s+\.', '.', corrected)
        corrected = re.sub(r'^\s*,\s*', '', corrected)

        result.corrected_text = corrected

        # Log serious issues
        if result.issues:
            print(f"⚠️ Voice Guide violation in '{field_name}': {result.issues}")

        return result

    def _ensure_next_step(self, text: str, field_name: str) -> str:
        """
        Ensure text contains a clear next step.

        If no next step is detected, append a generic one.
        """
        if not text:
            return text

        if has_next_step(text):
            return text

        # Only add next step indicator for your_move field
        if field_name == "your_move" and not text.strip().endswith('.'):
            text = text.strip() + '.'

        # Don't add generic next steps - the content should already have them
        # from the prompt. Just log a warning.
        if field_name == "your_move":
            print(f"⚠️ Voice Guide: '{field_name}' may lack clear next step")

        return text

    def validate_text(self, text: str) -> VoiceValidationResult:
        """
        Validate text without applying corrections.

        Use this for checking user-facing content before display.
        """
        result = VoiceValidationResult(
            original_text=text,
            corrected_text=text
        )

        if not text:
            return result

        # Check for forbidden patterns
        forbidden = has_forbidden_pattern(text)
        if forbidden:
            result.issues.append(f"Forbidden patterns: {forbidden}")
            result.is_valid = False

        # Check for false encouragement
        if has_false_encouragement(text):
            result.issues.append("False encouragement detected")
            result.is_valid = False

        # Check for shame language
        if has_shame_language(text):
            result.issues.append("Shame/blame language detected")
            result.is_valid = False

        # Check for next step
        if not has_next_step(text):
            result.issues.append("Missing clear next step")
            # Don't mark invalid - this is a soft requirement

        return result

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of all validation results."""
        total_processed = len(self.validation_log)
        total_corrections = sum(
            len(r.corrections_applied) for r in self.validation_log
        )
        total_issues = sum(len(r.issues) for r in self.validation_log)

        return {
            "total_fields_processed": total_processed,
            "total_corrections_applied": total_corrections,
            "total_issues_found": total_issues,
            "details": [
                {
                    "corrections": r.corrections_applied,
                    "issues": r.issues,
                }
                for r in self.validation_log if r.corrections_applied or r.issues
            ]
        }


def apply_voice_guide(response: Dict[str, Any], strict_mode: bool = False) -> Dict[str, Any]:
    """
    Convenience function to apply voice guide to an API response.

    Args:
        response: The API response dictionary
        strict_mode: If True, raises on violations

    Returns:
        Processed response with voice corrections
    """
    formatter = VoiceGuideFormatter(strict_mode=strict_mode)
    processed = formatter.process_response(response)

    # Add voice validation metadata (for debugging)
    summary = formatter.get_validation_summary()
    if summary["total_corrections_applied"] > 0 or summary["total_issues_found"] > 0:
        processed["_voice_guide_applied"] = True
        processed["_voice_guide_summary"] = summary

    return processed


# Mini voice guide for embedding in prompts (kept small to avoid bloat)
MINI_VOICE_GUIDE = """
You are HenryHQ — a direct, honest, supportive career coach.
You tell candidates the truth without shame, and you always give them a clear next step.
Your tone is calm, confident, human, and never robotic or overly optimistic.
Your goal is simple: make the candidate better with every message.
If an output does not improve clarity, readiness, confidence, or strategy, rewrite it.

Core Rules:
1. Truth first, support second. Never sugar-coat. Never shame. Use: Truth → Why → Fix → Support.
2. Be direct and concise. Short sentences. No filler. No corporate jargon.
3. Every output must give the user a NEXT STEP.
4. No false encouragement. Praise must be earned and specific.
5. Emotional safety is mandatory. Deliver hard truths calmly and respectfully.

If it doesn't make the candidate better, no one wins.
"""
