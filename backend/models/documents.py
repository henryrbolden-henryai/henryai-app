"""Document generation Pydantic models"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel

class SupplementAnswer(BaseModel):
    """A user-provided answer to a clarifying question about a gap"""
    gap_area: str
    question: str
    answer: str


class LevelingContext(BaseModel):
    """Career level assessment data from resume-leveling page"""
    current_level: str
    current_level_id: str
    target_level: Optional[str] = None
    target_level_id: Optional[str] = None
    levels_apart: Optional[int] = None
    detected_function: str
    language_level: str
    recommendations: Optional[List[Dict[str, Any]]] = None
    gaps: Optional[List[Dict[str, Any]]] = None


class DocumentsGenerateRequest(BaseModel):
    resume: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    preferences: Optional[Dict[str, Any]] = None
    supplements: Optional[List[SupplementAnswer]] = None  # User-provided answers from Strengthen page
    leveling: Optional[LevelingContext] = None  # Career level assessment data


class CoverLetterContent(BaseModel):
    greeting: str
    opening: str
    body: str
    closing: str
    full_text: str


class GeneratedDocuments(BaseModel):
    resume: "ResumeContent"
    cover_letter: CoverLetterContent


class CoverLetterGenerateRequest(BaseModel):
    resume_text: Optional[str] = None
    resume_json: Optional[Dict[str, Any]] = None
    job_description: str
    target_role: str
    target_company: str
    strengths: Optional[List[str]] = None
    jd_analysis: Optional[Dict[str, Any]] = None
    situation: Optional[Dict[str, Any]] = None  # Candidate emotional/situational state
    supplements: Optional[List[SupplementAnswer]] = None  # User-provided gap-filling info


# Download models
class PackageDownloadRequest(BaseModel):
    resume: Dict[str, Any]
    cover_letter: Dict[str, Any]
    company: str


class ResumeDownloadRequest(BaseModel):
    resume_output: Dict[str, Any]
    company: str
    role_title: str
    # Contact info for header
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None


class CoverLetterDownloadRequest(BaseModel):
    cover_letter: Dict[str, Any]
    company: str
    role_title: str
    # Contact info for header
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


# Document refinement models
class DocumentTypeForRefine(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"


class DocumentRefineRequest(BaseModel):
    document_type: DocumentTypeForRefine
    current_document: Dict[str, Any]
    user_instruction: str
    job_description: Optional[str] = None
    jd_analysis: Optional[Dict[str, Any]] = None
    resume_json: Optional[Dict[str, Any]] = None  # Original resume for reference


class DocumentChangeDetail(BaseModel):
    section: str
    change_type: str  # "added", "modified", "removed"
    before: Optional[str] = None
    after: Optional[str] = None


class DocumentChangesSummary(BaseModel):
    total_changes: int
    changes: List[DocumentChangeDetail]
    summary: str


class DocumentRefineResponse(BaseModel):
    refined_document: Dict[str, Any]
    changes_summary: DocumentChangesSummary
    coaching_note: str


