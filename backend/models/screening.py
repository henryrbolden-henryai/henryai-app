"""Screening Questions Pydantic models"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel


# Basic screening models
class ScreeningQuestionsRequest(BaseModel):
    """Request for generating screening question responses"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    screening_questions: str  # Raw text of screening questions pasted by user
    jd_analysis: Optional[Dict[str, Any]] = None
    situation: Optional[Dict[str, Any]] = None  # Candidate emotional/situational state


class ScreeningQuestionResponse(BaseModel):
    """Individual screening question response"""
    question: str
    recommended_response: str
    strategic_note: str
    gap_detected: bool = False
    mitigation_strategy: Optional[str] = None


class ScreeningQuestionsResponse(BaseModel):
    """Response containing all screening question answers"""
    responses: List[ScreeningQuestionResponse]
    overall_strategy: str


# Experience supplementation models
class ClarifyingQuestion(BaseModel):
    """A targeted question to fill a specific gap"""
    gap_area: str  # The gap this question addresses
    question: str  # The question to ask the candidate
    why_it_matters: str  # Brief explanation of why this matters for the role
    example_answer: str  # Example of a strong response


class GenerateClarifyingQuestionsRequest(BaseModel):
    """Request to generate clarifying questions based on gaps"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    gaps: List[str]  # The gaps identified in JD analysis
    fit_score: int  # Current fit score


class GenerateClarifyingQuestionsResponse(BaseModel):
    """Response containing targeted clarifying questions"""
    questions: List[ClarifyingQuestion]
    intro_message: str  # Personalized message to the candidate


class SupplementedExperience(BaseModel):
    """A piece of supplemented experience from the candidate"""
    gap_area: str
    question: str
    answer: str


class ReanalyzeWithSupplementsRequest(BaseModel):
    """Request to re-analyze fit with supplemented experience"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    original_gaps: List[str]
    original_fit_score: int
    supplements: List[SupplementedExperience]


class ReanalyzeWithSupplementsResponse(BaseModel):
    """Response from re-analysis with supplemented experience"""
    new_fit_score: int
    score_change: int  # Positive = improved
    updated_strengths: List[str]
    remaining_gaps: List[str]
    addressed_gaps: List[str]
    updated_resume_json: Dict[str, Any]  # Resume with supplements incorporated
    summary: str  # Brief explanation of changes


# Advanced screening analysis models
class ScreeningQuestionType(str, Enum):
    """Types of screening questions encountered in job applications"""
    YES_NO = "yes_no"
    COMP_EXPECTATIONS = "comp_expectations"
    ESSAY = "essay"
    MULTIPLE_CHOICE = "multiple_choice"
    AVAILABILITY = "availability"


class ScreeningRiskLevel(str, Enum):
    """Risk level for auto-rejection from screening questions"""
    HIGH = "high"      # Honest answer likely triggers auto-rejection
    MEDIUM = "medium"  # Borderline/defensible answer needed
    LOW = "low"        # Meets requirements but could be stronger
    SAFE = "safe"      # Clearly meets requirements


class HonestyFlag(str, Enum):
    """Honesty assessment for recommended answers"""
    TRUTHFUL = "truthful"              # 100% accurate, no embellishment
    STRATEGIC_FRAMING = "strategic_framing"  # Defensible but generous interpretation
    BORDERLINE = "borderline"          # Requires judgment call


class ScreeningQuestionInput(BaseModel):
    """Individual screening question from user"""
    question_text: str
    question_type: ScreeningQuestionType
    required: bool = True
    user_draft_answer: Optional[str] = None


class ScreeningQuestionsAnalyzeRequest(BaseModel):
    """Request for analyzing screening questions for auto-rejection risk"""
    screening_questions: List[ScreeningQuestionInput]
    job_description_text: str
    candidate_resume_data: Dict[str, Any]
    job_analysis: Dict[str, Any]


class ScreeningQuestionAnalysis(BaseModel):
    """Analysis result for a single screening question"""
    question_text: str
    question_type: ScreeningQuestionType
    auto_rejection_risk: ScreeningRiskLevel
    risk_explanation: str
    recommended_answer: str
    recommended_answer_rationale: str
    honesty_flag: HonestyFlag
    honesty_explanation: str
    alternative_approach: str
    keywords_to_include: Optional[List[str]] = None


class ScreeningQuestionsAnalyzeResponse(BaseModel):
    """Response containing analysis of all screening questions"""
    screening_analysis: List[ScreeningQuestionAnalysis]
    overall_risk_score: ScreeningRiskLevel
    critical_dealbreakers: List[str]
    strategic_guidance: str
    conversational_summary: str
