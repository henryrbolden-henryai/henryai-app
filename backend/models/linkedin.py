"""LinkedIn Pydantic models"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class LinkedInExperience(BaseModel):
    """A single experience entry from LinkedIn"""
    title: str
    company: str
    dates: Optional[str] = None
    location: Optional[str] = None
    bullets: List[str] = []


class LinkedInEducation(BaseModel):
    """A single education entry from LinkedIn"""
    school: str
    degree: Optional[str] = None
    dates: Optional[str] = None


class LinkedInParsedData(BaseModel):
    """Structured data parsed from LinkedIn PDF"""
    headline: Optional[str] = None
    summary: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    experience: List[LinkedInExperience] = []
    skills: List[str] = []
    education: List[LinkedInEducation] = []


class LinkedInUploadResponse(BaseModel):
    """Response from LinkedIn upload"""
    success: bool
    parsed_data: LinkedInParsedData
    message: str


class LinkedInAlignmentIssue(BaseModel):
    """A single alignment issue between resume and LinkedIn"""
    type: str  # title_mismatch, company_mismatch, date_mismatch, skills_mismatch
    severity: str  # high, medium, low
    resume_value: Optional[str] = None
    linkedin_value: Optional[str] = None
    message: str


class LinkedInAlignmentResponse(BaseModel):
    """Response from alignment check"""
    aligned: bool
    discrepancies: List[LinkedInAlignmentIssue]
    severity: str  # overall severity: high, medium, low
    discrepancy_count: int


class LinkedInOptimizeRequest(BaseModel):
    """Request for optimizing LinkedIn sections"""
    job_id: Optional[str] = None
    resume_json: Optional[Dict[str, Any]] = None
    job_description: Optional[str] = None
    target_role: Optional[str] = None
    linkedin_data: Optional[Dict[str, Any]] = None  # Current LinkedIn profile data
    # Single Source of Truth: Job Fit decision fields
    job_fit_recommendation: Optional[str] = None  # "Do Not Apply", "Apply with Caution", etc.
    recommendation_locked: Optional[bool] = False
    locked_reason: Optional[str] = None
    proceeded_despite_guidance: Optional[bool] = False  # User clicked "Pass Anyway"


class LinkedInExperienceOptimization(BaseModel):
    """Optimized content for a single experience entry"""
    title: str
    company: str
    dates: str
    company_context: str  # E.g., "Fortune 500 tech company with 50K+ employees"
    bullets: List[str]
    why_these_work: List[str]


class LinkedInOptimizeResponse(BaseModel):
    """Response with optimized LinkedIn sections"""
    # Severity and summary
    severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    summary_message: str = ""
    benefits: List[str] = []

    # Headline
    headline: str
    current_headline: Optional[str] = None
    headline_why: List[str] = []
    headline_update_reason: str = ""

    # About section
    summary: str
    current_summary: Optional[str] = None
    summary_why: List[str] = []
    summary_update_reason: str = ""

    # Experience
    experience_optimizations: List[LinkedInExperienceOptimization] = []

    # Skills
    top_skills: List[str]
    skills_to_add: List[str] = []
    skills_to_remove: List[str] = []
    skills_why: List[str] = []

    # Optional sections
    featured_recommendation: str = ""
    featured_suggestions: List[str] = []
    recommendations_advice: str = ""
    who_to_ask: List[Dict[str, str]] = []
    activity_recommendation: str = ""

    # Legacy fields for backwards compatibility
    experience_highlights: Optional[List[str]] = None
    has_issues: bool = False
    issue_count: int = 0
    generated_at: str

    # LEPE Integration (for Manager+ target roles)
    lepe_applicable: Optional[bool] = None  # True if target is Manager+
    lepe_decision: Optional[str] = None  # apply | position | caution | locked
    lepe_coaching: Optional[str] = None  # Coaching advice if positioning mode
    lepe_skepticism_warning: Optional[str] = None  # Warning if caution/locked
    leadership_tenure: Optional[Dict[str, Any]] = None  # From LEPE analysis
    accountability_record: Optional[Dict[str, Any]] = None  # LEPE accountability
