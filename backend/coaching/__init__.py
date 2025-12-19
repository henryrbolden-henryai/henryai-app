# ============================================================================
# COACHING MODULE
# Per Selective Coaching Moments Spec v1.0 (REVISED)
#
# Purpose: Control what gets said to users based on calibrated gaps.
# Silence suppresses "Gaps to Address," not "Your Move."
# ============================================================================

from .coaching_controller import (
    generate_coaching_output,
    generate_your_move,
    should_show_gaps_section,
    format_gaps_for_display,
    generate_accountability_banner,
    extract_primary_strength,
)

__all__ = [
    'generate_coaching_output',
    'generate_your_move',
    'should_show_gaps_section',
    'format_gaps_for_display',
    'generate_accountability_banner',
    'extract_primary_strength',
]
