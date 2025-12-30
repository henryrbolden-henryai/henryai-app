"""Job Description analysis Pydantic models"""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


class JDSource(str, Enum):
    """Track JD provenance"""
    USER_PROVIDED = "user_provided"
    URL_FETCHED = "url_fetched"
    INFERRED = "inferred"
    MISSING = "missing"
    LINK_FAILED = "link_failed"


class ConfidenceLabel(str, Enum):
    """Trust preservation labels"""
    DIRECTIONAL = "directional"
    REFINED = "refined"


class JDAnalyzeRequest(BaseModel):
    company: str
    role_title: str
    job_description: Optional[str] = None  # Optional when using provisional_profile
    resume: Optional[dict] = None
    preferences: Optional[dict] = None
    # Command Center v2.0 fields
    jd_source: Optional[str] = None  # user_provided, url_fetched, inferred, missing
    provisional_profile: Optional[dict] = None  # When jd_source is inferred/missing


class JDAnalysis(BaseModel):
    company: str
    role_title: str
    company_context: str
    role_overview: str
    key_responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    ats_keywords: List[str]
    fit_score: int
    strengths: List[str]
    gaps: List[str]
    strategic_positioning: str
    salary_info: Optional[str] = None


class URLExtractRequest(BaseModel):
    url: str


class URLExtractResponse(BaseModel):
    job_description: str
    role_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    extracted_at: str


# JD Reconstruct models (when JD is missing)
class JDReconstructRequest(BaseModel):
    """Request to generate Provisional Role Profile when JD is missing"""
    role_title: str
    company_name: str
    industry: Optional[str] = None  # Optional, inferred if missing
    seniority: Optional[str] = None  # Optional, inferred from title


class ProvisionalProfile(BaseModel):
    """Reconstructed role profile when JD is missing"""
    role_title: str
    typical_responsibilities: List[str]
    common_competencies: List[str]
    interview_focus_areas: List[str]
    evaluation_criteria: List[str]


class JDReconstructResponse(BaseModel):
    """Response from JD reconstruction"""
    provisional_profile: ProvisionalProfile
    confidence: ConfidenceLabel = ConfidenceLabel.DIRECTIONAL
    jd_source: JDSource = JDSource.INFERRED
