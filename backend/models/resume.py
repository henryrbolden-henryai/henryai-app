"""Resume-related Pydantic models"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ResumeParseRequest(BaseModel):
    resume_text: Optional[str] = None
    linkedin_url: Optional[str] = None


class Experience(BaseModel):
    company: str
    title: str
    dates: str
    industry: Optional[str] = None
    bullets: List[str] = []


class ResumeProfile(BaseModel):
    full_name: str
    current_title: Optional[str] = None
    target_roles: List[str] = []
    industries: List[str] = []
    years_experience: Optional[str] = None
    summary: str
    experience: List[Experience]
    key_achievements: List[str] = []
    core_competencies: List[str] = []
    skills: List[str] = []
    education: Optional[str] = None


class ResumeCustomizeRequest(BaseModel):
    resume_text: Optional[str] = None
    resume_json: Optional[Dict[str, Any]] = None
    job_description: str
    target_role: str
    target_company: str
    jd_analysis: Optional[Dict[str, Any]] = None
    situation: Optional[Dict[str, Any]] = None  # Candidate emotional/situational state
    supplements: Optional[List[Dict[str, Any]]] = None  # User-provided gap-filling info (SupplementAnswer format)


class ResumeContent(BaseModel):
    summary: str
    skills: List[str]
    experience: List[Experience]


# Resume CRUD models
class SaveResumeRequest(BaseModel):
    resume_json: Dict[str, Any]
    name: Optional[str] = None
    is_primary: bool = False


class UpdateResumeRequest(BaseModel):
    resume_json: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    is_primary: Optional[bool] = None


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    name: str
    resume_json: Dict[str, Any]
    is_primary: bool
    created_at: str
    updated_at: str


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    count: int


# Resume Leveling models
class LevelCompetency(BaseModel):
    """Assessment of a specific competency area"""
    area: str  # e.g., "Technical Depth", "Leadership", "Strategic Thinking"
    current_level: str  # e.g., "Strong at Senior level"
    evidence: List[str]  # Quotes/signals from resume
    gap_to_target: Optional[str] = None  # What's missing for target level


class LevelingGap(BaseModel):
    """A specific gap between current and target level"""
    category: str  # "scope", "impact", "competency", "language"
    description: str
    recommendation: str  # How to address in resume
    priority: str  # "high", "medium", "low"
    gap_type: str = "presentation"  # "experience" or "presentation" - CRITICAL distinction
    # experience = candidate genuinely needs more time/roles
    # presentation = candidate likely has this but resume doesn't show it


class LevelingRecommendation(BaseModel):
    """A specific recommendation to strengthen resume for target level"""
    type: str  # "content", "language", "quantification", "scope"
    priority: str  # "high", "medium", "low"
    current: str  # Current state
    suggested: str  # Recommended change
    rationale: str  # Why this matters
    gap_type: str = "presentation"  # "experience" or "presentation"


class QuickWin(BaseModel):
    """Single highest-impact action for the candidate"""
    action: str  # What to do
    rationale: str  # Why this matters most
    expected_impact: str  # What improvement to expect
    gap_type: str  # "experience" or "presentation"


class SignalItem(BaseModel):
    """A signal with severity for sorting"""
    text: str  # The signal text
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    source: Optional[str] = None  # Where it came from (e.g., "Uber - Senior PM")
    gap_type: Optional[str] = None  # "experience" or "presentation" if this is a gap


class RedFlag(BaseModel):
    """Enhanced red flag with cause, consequence, and fix"""
    type: str  # Category of flag
    instance: str  # Specific instance from resume
    why_it_matters: str  # Market perception consequence
    gap_type: str  # "experience" or "presentation"
    how_to_fix: List[str]  # Actionable fixes
    source_bullets: Optional[List[str]] = None  # For context-specific replacements


class ResumeLevelingRequest(BaseModel):
    """Request for resume level assessment"""
    resume_json: Any  # Can be dict or string (will be parsed in endpoint)
    job_description: Optional[str] = None
    target_title: Optional[str] = None  # If provided, do gap analysis against this
    company: Optional[str] = None
    role_title: Optional[str] = None


class LevelMismatchWarning(BaseModel):
    """Warning when target level doesn't match assessed level"""
    target_level: str
    assessed_level: str
    gap_explanation: str
    alternative_recommendation: Optional[str] = None


class RoleTypeBreakdown(BaseModel):
    """Breakdown of years by role type"""
    pm_years: int = 0
    engineering_years: int = 0
    operations_years: int = 0
    other_years: int = 0


class ResumeLevelingResponse(BaseModel):
    """Response containing full resume leveling analysis"""
    # Function detection
    detected_function: str  # "Engineering", "Product Management", "Marketing", etc.
    function_confidence: float  # 0-1 confidence score

    # Current level assessment
    current_level: str  # e.g., "Associate PM", "Mid-Level PM" (NOT inflated titles)
    current_level_id: str  # e.g., "associate_pm", "mid_pm"
    level_confidence: float  # 0-1 confidence score
    years_experience: int

    # Strict role-type experience tracking
    years_in_role_type: Optional[int] = None  # Only years in actual PM/Eng/etc roles
    role_type_breakdown: Optional[RoleTypeBreakdown] = None

    # What This Means - contextual summary
    what_this_means: Optional[str] = None  # 2-3 sentence contextual explanation

    # Quick Win - single highest-impact action (v3.0)
    quick_win: Optional[QuickWin] = None

    # Evidence for current level - now with severity (v3.0)
    scope_signals: List[str]  # Legacy format for backward compat
    impact_signals: List[str]
    leadership_signals: List[str]
    technical_signals: List[str]

    # Enhanced signals with severity (v3.0)
    scope_signals_enhanced: Optional[List[SignalItem]] = None
    impact_signals_enhanced: Optional[List[SignalItem]] = None
    leadership_signals_enhanced: Optional[List[SignalItem]] = None
    technical_signals_enhanced: Optional[List[SignalItem]] = None

    # Competency breakdown
    competencies: List[LevelCompetency]

    # Language analysis
    language_level: str  # "Entry", "Mid", "Senior", "Principal"
    action_verb_distribution: Dict[str, float]  # {"entry": 0.1, "mid": 0.3, "senior": 0.5, "principal": 0.1}
    quantification_rate: float  # % of bullets with numbers

    # Generic phrase replacements with context (v3.0)
    generic_phrase_replacements: Optional[List[Dict[str, str]]] = None
    # Each: {"phrase": "team player", "suggested_replacement": "led cross-functional squad of 8", "source_bullet": "..."}

    # Red flags - legacy format for backward compat
    red_flags: List[str]  # Issues found (generic claims, inconsistencies, etc.)

    # Enhanced red flags with cause + consequence + fix (v3.0)
    red_flags_enhanced: Optional[List[RedFlag]] = None

    # Title inflation detection
    title_inflation_detected: Optional[bool] = None
    title_inflation_explanation: Optional[str] = None

    # Target analysis (if target_title provided)
    target_level: Optional[str] = None
    target_level_id: Optional[str] = None
    levels_apart: Optional[int] = None  # 0 = matches, positive = target is higher
    is_qualified: Optional[bool] = None
    qualification_confidence: Optional[float] = None

    # Level mismatch warnings
    level_mismatch_warnings: Optional[List[LevelMismatchWarning]] = None

    # Gap analysis (if target provided) - now includes gap_type (v3.0)
    gaps: Optional[List[LevelingGap]] = None

    # Recommendations - now includes gap_type (v3.0)
    recommendations: List[LevelingRecommendation]

    # Summary
    summary: str  # Brief narrative assessment

    # LEPE Integration (for Manager+ roles)
    lepe_applicable: Optional[bool] = None  # True if target is Manager+
    lepe_decision: Optional[str] = None  # apply | position | caution | locked
    lepe_coaching: Optional[str] = None  # Coaching advice if positioning mode
    lepe_skepticism_warning: Optional[str] = None  # Warning if caution/locked
    leadership_tenure: Optional[Dict[str, Any]] = None  # From LEPE analysis
    accountability_record: Optional[Dict[str, Any]] = None  # LEPE accountability


# Resume Chat models
class ResumeChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ExtractedSkill(BaseModel):
    skill: str
    years: Optional[int] = None
    level: Optional[str] = None  # "beginner", "intermediate", "advanced", "expert"
    context: Optional[str] = None


class ResumeChatRequest(BaseModel):
    messages: List[ResumeChatMessage]
    current_resume_json: Optional[Dict[str, Any]] = None
    extracted_skills: Optional[List[ExtractedSkill]] = None


class ResumeChatResponse(BaseModel):
    message: str
    updated_resume_json: Optional[Dict[str, Any]] = None
    new_extracted_skills: Optional[List[ExtractedSkill]] = None
    is_complete: bool = False
    next_section: Optional[str] = None


class GenerateResumeFromChatRequest(BaseModel):
    messages: List[ResumeChatMessage]
    extracted_skills: List[ExtractedSkill]
    target_role: Optional[str] = None


class GenerateResumeFromChatResponse(BaseModel):
    resume_json: Dict[str, Any]
    summary: str


