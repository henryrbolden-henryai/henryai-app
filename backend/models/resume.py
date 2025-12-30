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


class LevelingRecommendation(BaseModel):
    """A specific recommendation to strengthen resume for target level"""
    type: str  # "content", "language", "quantification", "scope"
    priority: str  # "high", "medium", "low"
    current: str  # Current state
    suggested: str  # Recommended change
    rationale: str  # Why this matters


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

    # Evidence for current level
    scope_signals: List[str]  # Scope indicators found
    impact_signals: List[str]  # Impact statements found
    leadership_signals: List[str]  # Leadership evidence
    technical_signals: List[str]  # Technical depth evidence

    # Competency breakdown
    competencies: List[LevelCompetency]

    # Language analysis
    language_level: str  # "Entry", "Mid", "Senior", "Principal"
    action_verb_distribution: Dict[str, float]  # {"entry": 0.1, "mid": 0.3, "senior": 0.5, "principal": 0.1}
    quantification_rate: float  # % of bullets with numbers

    # Red flags
    red_flags: List[str]  # Issues found (generic claims, inconsistencies, etc.)

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

    # Gap analysis (if target provided)
    gaps: Optional[List[LevelingGap]] = None

    # Recommendations
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


