# ============================================================================
# QA SANITIZATION MODULE
# Per HenryHQ Implementation Guide (Dec 21, 2025)
#
# PURPOSE: Clean generated text and validate output quality before response.
#
# REMOVES:
# - Em dashes (AI detection pattern)
# - Double spaces
# - Orphaned punctuation
# - Inconsistent capitalization
#
# DETECTS:
# - Cross-candidate leakage (output too similar to recent analyses)
# - Generic filler language
# - Missing required fields
#
# ============================================================================

import re
from typing import Dict, Any, List, Set, Optional
from difflib import SequenceMatcher


# ============================================================================
# TEXT SANITIZATION
# ============================================================================

def sanitize_output(text: str) -> str:
    """
    Clean generated text before response.

    Removes:
    - Em dashes and en dashes (AI detection pattern)
    - Double spaces
    - Orphaned punctuation
    - Inconsistent capitalization after periods

    Args:
        text: Raw text to sanitize

    Returns:
        Cleaned text
    """
    if not text:
        return text

    # Remove em dashes and en dashes (AI detection pattern)
    # Replace with hyphen surrounded by spaces for readability
    text = text.replace("—", " - ").replace("–", " - ")

    # Fix orphaned punctuation (space before punctuation)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)

    # Fix double spaces (including after em dash replacement)
    text = re.sub(r'\s{2,}', ' ', text)

    # Ensure sentences start with capital after period
    text = re.sub(
        r'\.(\s+)([a-z])',
        lambda m: '.' + m.group(1) + m.group(2).upper(),
        text
    )

    # Remove trailing/leading whitespace
    text = text.strip()

    # Fix common AI-generated patterns
    # "with We" -> "with we" (lowercase after preposition)
    text = re.sub(r'\bwith We\b', 'with we', text)

    # Remove incomplete sentences (ending with orphaned words)
    # Pattern: sentence ending with single short word followed by nothing
    text = re.sub(r'\s+\w{1,3}\.?$', '.', text)

    return text


def sanitize_all_text_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize all text fields in a response dictionary.

    Args:
        data: Response dictionary with text fields

    Returns:
        Same dictionary with all text fields sanitized
    """
    if isinstance(data, str):
        return sanitize_output(data)
    elif isinstance(data, dict):
        return {k: sanitize_all_text_fields(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_all_text_fields(item) for item in data]
    else:
        return data


# ============================================================================
# CROSS-CANDIDATE LEAKAGE DETECTION
# ============================================================================

# Track recent outputs for duplicate detection
_recent_outputs: Set[str] = set()
_max_recent_outputs = 100


def reset_recent_outputs():
    """Reset the recent outputs cache. Call between test runs."""
    global _recent_outputs
    _recent_outputs = set()


def check_output_leakage(current_output: str, threshold: float = 0.8) -> bool:
    """
    Check if current output is too similar to recent outputs.

    This prevents cross-candidate leakage where the same generic
    text is reused across different analyses.

    Args:
        current_output: Text to check
        threshold: Similarity threshold (0.0-1.0, default 0.8)

    Returns:
        True if leakage detected (output should be regenerated).
    """
    if not current_output or len(current_output) < 50:
        return False

    # Normalize for comparison
    normalized = current_output.lower().strip()

    for recent in _recent_outputs:
        similarity = SequenceMatcher(None, normalized, recent).ratio()
        if similarity > threshold:
            print(f"   ⚠️ OUTPUT LEAKAGE DETECTED: {similarity:.1%} similarity to recent output")
            return True

    # Add to recent outputs (FIFO if over limit)
    _recent_outputs.add(normalized)
    if len(_recent_outputs) > _max_recent_outputs:
        # Remove oldest (first added)
        _recent_outputs.pop()

    return False


# ============================================================================
# OUTPUT QUALITY VALIDATION
# ============================================================================

# Generic phrases that reduce output quality
GENERIC_FILLER_PHRASES = [
    "I believe", "I think", "I feel",
    "results-driven", "team player", "hard worker",
    "detail-oriented", "self-starter",
    "passionate about", "dedicated to",
    "proven track record", "go-getter",
    "synergy", "leverage", "utilize",
    "circle back", "touch base"
]

# Banned patterns for AI detection
AI_DETECTION_PATTERNS = [
    "—",  # em dash
    "–",  # en dash
    "certainly",
    "absolutely",
    "It's important to note",
    "It's worth noting",
    "As an AI",
    "I cannot",
    "I'm unable to"
]


def validate_output_quality(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate output quality and return issues.

    Checks:
    - Em dashes present
    - Repeated phrases
    - Generic filler language
    - Cross-candidate leakage
    - AI detection patterns

    Args:
        output: Response dictionary to validate

    Returns:
        dict with keys:
        - valid: bool (True if no high-severity issues)
        - issues: List of issue dicts
        - issue_count: int
    """
    issues: List[Dict[str, Any]] = []

    # Flatten output to text for analysis
    text_fields = []

    def extract_text_fields(obj, prefix=""):
        if isinstance(obj, str):
            text_fields.append(obj)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                extract_text_fields(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                extract_text_fields(item, f"{prefix}[{i}]")

    extract_text_fields(output)
    full_text = " ".join(text_fields)

    # Check for em dashes and en dashes
    if "—" in full_text or "–" in full_text:
        issues.append({
            "type": "em_dash_detected",
            "severity": "medium",
            "message": "Em dashes detected - should be replaced with hyphens",
            "auto_fix": True
        })

    # Check for AI detection patterns
    for pattern in AI_DETECTION_PATTERNS:
        if pattern.lower() in full_text.lower():
            issues.append({
                "type": "ai_detection_pattern",
                "severity": "medium",
                "message": f"AI detection pattern found: '{pattern}'",
                "auto_fix": False
            })

    # Check for generic filler
    for phrase in GENERIC_FILLER_PHRASES:
        if phrase.lower() in full_text.lower():
            issues.append({
                "type": "generic_filler",
                "severity": "low",
                "message": f"Generic phrase detected: '{phrase}'",
                "auto_fix": False
            })

    # Check for leakage (only for Your Move and Reality Check)
    your_move = output.get("your_move", "") or output.get("intelligence_layer", {}).get("your_move", "")
    reality_check = output.get("reality_check", "") or output.get("the_opportunity", "")

    if your_move and check_output_leakage(str(your_move)):
        issues.append({
            "type": "potential_leakage_your_move",
            "severity": "high",
            "message": "Your Move output too similar to recent analysis - possible cross-candidate contamination",
            "auto_fix": False
        })

    if reality_check and check_output_leakage(str(reality_check)):
        issues.append({
            "type": "potential_leakage_reality_check",
            "severity": "high",
            "message": "Reality Check output too similar to recent analysis - possible cross-candidate contamination",
            "auto_fix": False
        })

    # Check for incomplete sentences
    incomplete_pattern = re.compile(r'(?<=[a-z])\s+(?:with|and|or|but|the|a|an)\s*$', re.IGNORECASE)
    if incomplete_pattern.search(full_text):
        issues.append({
            "type": "incomplete_sentence",
            "severity": "medium",
            "message": "Incomplete sentence detected (ends with dangling word)",
            "auto_fix": True
        })

    return {
        "valid": len([i for i in issues if i["severity"] == "high"]) == 0,
        "issues": issues,
        "issue_count": len(issues),
        "high_severity_count": len([i for i in issues if i["severity"] == "high"]),
        "auto_fixable_count": len([i for i in issues if i.get("auto_fix")])
    }


def apply_auto_fixes(output: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply automatic fixes for issues that can be auto-corrected.

    Args:
        output: Original output dictionary
        validation_result: Result from validate_output_quality()

    Returns:
        Fixed output dictionary
    """
    if validation_result.get("auto_fixable_count", 0) == 0:
        return output

    # Apply sanitization to fix em dashes, incomplete sentences, etc.
    return sanitize_all_text_fields(output)


# ============================================================================
# SENIORITY-BASED CONTENT FILTERING
# ============================================================================

# Phrases banned for executive candidates
EXECUTIVE_BANNED_PHRASES = [
    "polish your resume",
    "tailor your resume",
    "optimize for ATS",
    "include keywords",
    "update your LinkedIn",
    "practice your elevator pitch",
    "prepare for behavioral questions",
    "work on your skills",
    "build more experience"
]

# Phrases banned for IC/entry candidates
IC_BANNED_PHRASES = [
    "leverage your board connections",
    "reach out to the CEO directly",
    "executive presence",
    "C-suite network",
    "board-level visibility",
    "negotiate your package"
]


def filter_guidance_for_seniority(
    guidance_content: str,
    seniority: str
) -> str:
    """
    Filter out inappropriate guidance for the candidate's seniority level.

    For executives: Remove resume tips, ATS advice, basic interview prep
    For ICs: Remove executive networking strategies, board-level language

    Args:
        guidance_content: Raw guidance text
        seniority: 'executive', 'director', 'manager', or 'ic'

    Returns:
        Filtered guidance text
    """
    if not guidance_content:
        return guidance_content

    result = guidance_content

    if seniority == "executive":
        for phrase in EXECUTIVE_BANNED_PHRASES:
            # Case-insensitive replacement - replace phrase with empty string
            # but preserve sentence structure
            pattern = re.compile(
                r'(?:^|\.\s+)(?:[^.]*\b' + re.escape(phrase) + r'\b[^.]*\.)',
                re.IGNORECASE
            )
            # Only remove if it's a complete sentence about the banned topic
            if phrase.lower() in result.lower():
                # Simple approach: just remove the phrase, not the whole sentence
                simple_pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                result = simple_pattern.sub("", result)

    elif seniority == "ic":
        for phrase in IC_BANNED_PHRASES:
            if phrase.lower() in result.lower():
                simple_pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                result = simple_pattern.sub("", result)

    # Clean up double spaces and orphaned punctuation after removals
    # Fix any resulting broken sentences
    result = re.sub(r'\s+\.', '.', result)  # Remove space before period
    result = re.sub(r'\.\.+', '.', result)  # Fix multiple periods
    result = re.sub(r'\s+', ' ', result)  # Fix multiple spaces
    result = result.strip()

    # If result becomes too short after filtering, return original
    if len(result) < 20 and len(guidance_content) > 50:
        return guidance_content

    return result


# ============================================================================
# CONVENIENCE FUNCTION - Full validation and fix pipeline
# ============================================================================

def validate_and_fix_output(
    output: Dict[str, Any],
    candidate_seniority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run full validation and auto-fix pipeline on output.

    Args:
        output: Response dictionary
        candidate_seniority: Optional seniority for content filtering

    Returns:
        dict with keys:
        - fixed_output: Sanitized and fixed output
        - validation: Validation results
        - seniority_filtered: Whether seniority filtering was applied
    """
    # Step 1: Validate
    validation = validate_output_quality(output)

    # Step 2: Apply auto-fixes
    fixed_output = apply_auto_fixes(output, validation)

    # Step 3: Apply seniority filtering if specified
    seniority_filtered = False
    if candidate_seniority:
        # Filter your_move content
        if "your_move" in fixed_output:
            fixed_output["your_move"] = filter_guidance_for_seniority(
                fixed_output["your_move"],
                candidate_seniority
            )
            seniority_filtered = True

        if "intelligence_layer" in fixed_output and "your_move" in fixed_output["intelligence_layer"]:
            fixed_output["intelligence_layer"]["your_move"] = filter_guidance_for_seniority(
                fixed_output["intelligence_layer"]["your_move"],
                candidate_seniority
            )
            seniority_filtered = True

    return {
        "fixed_output": fixed_output,
        "validation": validation,
        "seniority_filtered": seniority_filtered
    }
