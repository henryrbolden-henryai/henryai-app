# Utils package - Shared utility functions for HenryAI backend

from .text_processing import (
    clean_claude_json,
    extract_pdf_text,
    extract_docx_text,
)

from .date_helpers import (
    calculate_days_since,
)

from .role_detection import (
    detect_role_type,
    determine_target_level,
    infer_seniority_from_title,
    infer_industry_from_company,
    get_competency_for_stage,
    SIGNAL_WEIGHTS_BY_ROLE,
)

from .tracker_helpers import (
    calculate_momentum_score,
    calculate_jd_confidence,
    calculate_decision_confidence,
    get_confidence_label,
    get_confidence_guidance,
    determine_action_for_status,
    calculate_ui_signals,
    calculate_pipeline_health,
)

from .validation import (
    verify_ats_keyword_coverage,
    validate_document_quality,
)
