# ============================================================================
# INTERNAL RECRUITER CALIBRATION SYSTEM
# Per Calibration Spec v1.0: Recruiter-grade judgment framework
#
# Purpose: Interpret CEC evidence and classify gaps as terminal vs coachable
# Ensures HenryHQ reasons like three senior recruiters reviewing together
# ============================================================================

from .signal_detectors import (
    extract_team_size,
    extract_scope_signals,
    detect_org_level_influence,
    has_upward_trajectory,
    calculate_career_span,
    extract_revenue_impact,
    detect_ownership_level,
    analyze_scope_trajectory,
    detect_tool_obsession,
    detect_sales_motion,
    extract_metrics,
    has_metric_context,
    detect_passive_voice_dominance,
    detect_manager_of_managers,
    is_ic_to_leadership_transition,
    detect_press_release_pattern,
    detect_scale_inconsistency,
)

from .executive_calibration import calibrate_executive_role
from .technical_calibration import calibrate_technical_role
from .gtm_calibration import calibrate_gtm_role
from .gap_classifier import classify_gap, assess_domain_transferability, calculate_level_distance
from .red_flag_detector import detect_red_flags
from .calibration_controller import calibrate_gaps

__all__ = [
    # Signal detectors
    'extract_team_size',
    'extract_scope_signals',
    'detect_org_level_influence',
    'has_upward_trajectory',
    'calculate_career_span',
    'extract_revenue_impact',
    'detect_ownership_level',
    'analyze_scope_trajectory',
    'detect_tool_obsession',
    'detect_sales_motion',
    'extract_metrics',
    'has_metric_context',
    'detect_passive_voice_dominance',
    'detect_manager_of_managers',
    'is_ic_to_leadership_transition',
    'detect_press_release_pattern',
    'detect_scale_inconsistency',
    # Calibrators
    'calibrate_executive_role',
    'calibrate_technical_role',
    'calibrate_gtm_role',
    # Gap classification
    'classify_gap',
    'assess_domain_transferability',
    # Red flags
    'detect_red_flags',
    # Control layer
    'calibrate_gaps',
    'calculate_level_distance',
]
