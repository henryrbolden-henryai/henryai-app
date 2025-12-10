"""
Henry Job Search Engine - Backend API
FastAPI application with resume parsing, JD analysis, and document generation
"""

import os
import sys
import json
import io
import uuid
import random
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import anthropic

# Add parent directory to path for document_generator import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from document_generator import ResumeFormatter, CoverLetterFormatter

# Initialize FastAPI app
app = FastAPI(
    title="Henry Job Search Engine API",
    description="Backend for resume parsing, JD analysis, and application generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add validation error handler for better debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"🔥 VALIDATION ERROR: {exc.errors()}")
    print(f"🔥 REQUEST BODY: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)[:500]}
    )

# Initialize Anthropic client
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

client = anthropic.Anthropic(api_key=API_KEY, timeout=120.0)  # 2 min timeout for long transcripts

# OpenAI API key for TTS (optional - for natural AI voice)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# In-memory storage for outcomes (Feature 2: Learning/Feedback Loop)
# In production, replace with proper database
outcomes_store: List[Dict[str, Any]] = []

# In-memory storage for mock interview sessions
# In production, replace with proper database
mock_interview_sessions: Dict[str, Dict[str, Any]] = {}
mock_interview_questions: Dict[str, Dict[str, Any]] = {}
mock_interview_responses: Dict[str, List[Dict[str, Any]]] = {}
mock_interview_analyses: Dict[str, Dict[str, Any]] = {}

# Load question bank
QUESTION_BANK_PATH = os.path.join(os.path.dirname(__file__), "data", "question_bank.json")
QUESTION_BANK: Dict[str, Any] = {}

def load_question_bank():
    """Load the structured question bank from JSON file."""
    global QUESTION_BANK
    try:
        if os.path.exists(QUESTION_BANK_PATH):
            with open(QUESTION_BANK_PATH, "r") as f:
                QUESTION_BANK = json.load(f)
            print(f"✅ Loaded question bank with {len(QUESTION_BANK.get('role_specific_questions', {}))} role types")
        else:
            print(f"⚠️ Question bank not found at {QUESTION_BANK_PATH}")
            QUESTION_BANK = {}
    except Exception as e:
        print(f"🔥 Error loading question bank: {e}")
        QUESTION_BANK = {}

# Load question bank on startup
load_question_bank()


def get_question_from_bank(role_type: str, category: str, asked_questions: List[str], target_level: str = "mid") -> Optional[Dict]:
    """
    Select an appropriate question from the bank based on role, category, and level.
    Returns None if no suitable question is found (fallback to Claude generation).
    """
    if not QUESTION_BANK:
        return None

    # Map role_type to question bank keys
    role_mapping = {
        "product_manager": "product_manager",
        "software_engineer": "software_engineer",
        "ux_designer": "ux_designer",
        "ui_designer": "ui_designer",
        "talent_acquisition": "talent_acquisition",
        "general_leadership": "general_leadership"
    }

    role_key = role_mapping.get(role_type, "general_leadership")
    role_questions = QUESTION_BANK.get("role_specific_questions", {}).get(role_key, {})

    # Determine which question pool to use based on category/stage
    question_pool = []

    if category in ["warm_start", "recruiter_screen"]:
        # Use generic category questions
        category_questions = QUESTION_BANK.get("question_categories", {}).get(category, {}).get("questions", [])
        question_pool.extend(category_questions)
    elif category == "behavioral":
        # Use both generic and role-specific behavioral
        generic_behavioral = QUESTION_BANK.get("question_categories", {}).get("behavioral", {}).get("questions", [])
        role_behavioral = role_questions.get("behavioral", [])
        question_pool.extend(generic_behavioral)
        question_pool.extend(role_behavioral)
    elif category in ["hiring_manager", "hiring_manager_deep_dive"]:
        # Use role-specific hiring manager questions
        question_pool.extend(role_questions.get("hiring_manager_deep_dive", []))
    elif category == "strategy":
        # Use role-specific strategy questions
        question_pool.extend(role_questions.get("strategy", []))
    else:
        # Default: use hiring_manager_deep_dive + behavioral
        question_pool.extend(role_questions.get("hiring_manager_deep_dive", []))
        question_pool.extend(role_questions.get("behavioral", []))

    # Filter by target level and exclude already asked questions
    filtered_questions = []
    for q in question_pool:
        # Check if question hasn't been asked
        if q.get("text") in asked_questions or q.get("id") in asked_questions:
            continue
        # Check if question is appropriate for target level
        target_levels = q.get("target_levels", ["mid", "senior", "director", "executive"])
        if target_level in target_levels:
            filtered_questions.append(q)

    if not filtered_questions:
        return None

    # Return a random question from filtered pool
    return random.choice(filtered_questions)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

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

class JDAnalyzeRequest(BaseModel):
    company: str
    role_title: str
    job_description: str
    resume: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

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

class SupplementAnswer(BaseModel):
    """A user-provided answer to a clarifying question about a gap"""
    gap_area: str
    question: str
    answer: str

class DocumentsGenerateRequest(BaseModel):
    resume: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    preferences: Optional[Dict[str, Any]] = None
    supplements: Optional[List[SupplementAnswer]] = None  # User-provided answers from Strengthen page

class ResumeContent(BaseModel):
    summary: str
    skills: List[str]
    experience: List[Experience]

class CoverLetterContent(BaseModel):
    greeting: str
    opening: str
    body: str
    closing: str
    full_text: str

class GeneratedDocuments(BaseModel):
    resume: ResumeContent
    cover_letter: CoverLetterContent

# ============================================================================
# TAILORED DOCUMENT GENERATION MODELS
# ============================================================================

class ResumeCustomizeRequest(BaseModel):
    resume_text: Optional[str] = None
    resume_json: Optional[Dict[str, Any]] = None
    job_description: str
    target_role: str
    target_company: str
    jd_analysis: Optional[Dict[str, Any]] = None
    situation: Optional[Dict[str, Any]] = None  # Candidate emotional/situational state
    supplements: Optional[List[SupplementAnswer]] = None  # User-provided gap-filling info

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

# ============================================================================
# MVP+1 FEATURE MODELS
# ============================================================================

# Feature 1: Daily Command Center
class Application(BaseModel):
    id: str
    company: str
    role_title: str
    fit_score: int = Field(ge=0, le=100)
    stage: str  # applied|screen|onsite|offer|rejected
    last_activity_date: str  # ISO date
    has_outreach: bool = False

class TasksPrioritizeRequest(BaseModel):
    applications: List[Application]
    today: str  # ISO date

class Task(BaseModel):
    type: str  # apply|follow_up|outreach
    application_id: str
    priority: int = Field(ge=1, le=3)
    reason: str
    suggested_message_stub: Optional[str] = None

class TasksPrioritizeResponse(BaseModel):
    tasks: List[Task]

# Feature 2: Learning/Feedback Loop
class OutcomeLogRequest(BaseModel):
    application_id: str
    stage: str  # applied|viewed|replied|interview|offer|rejected
    outcome: str
    date: str  # ISO date

class StrategyReviewRequest(BaseModel):
    applications: List[Dict[str, Any]]
    outcomes: List[Dict[str, Any]]

class StrategyReviewResponse(BaseModel):
    insights: List[str]
    recommendations: List[str]

# Feature 3: Network Engine (Lite)
class Contact(BaseModel):
    name: str
    company: str
    title: str
    relationship: str

class NetworkRecommendRequest(BaseModel):
    company: str
    role_title: str
    contacts: List[Contact]

class ContactRecommendation(BaseModel):
    name: str
    company: str
    title: str
    relationship: str
    priority: int = Field(ge=1, le=3)
    reason: str
    suggested_message_stub: str

class NetworkRecommendResponse(BaseModel):
    recommendations: List[ContactRecommendation]

# Feature 4: Interview Intelligence
class InterviewQuestion(BaseModel):
    question: str
    type: str  # behavioral|technical|leadership|competency|wildcard
    competency_tag: str
    difficulty: int = Field(ge=1, le=5)

class InterviewParseRequest(BaseModel):
    transcript_text: str
    role_title: str
    company: str
    jd_analysis: Optional[Dict[str, Any]] = None

class InterviewParseResponse(BaseModel):
    questions: List[InterviewQuestion]
    themes: List[str]
    warnings: List[str]

class InterviewFeedbackRequest(BaseModel):
    transcript_text: str
    role_title: str
    company: str
    questions: List[InterviewQuestion]

class DeliveryFeedback(BaseModel):
    tone: str
    pacing: str
    clarity: str
    structure: str

class InterviewFeedbackResponse(BaseModel):
    overall_score: int = Field(ge=1, le=100)
    strengths: List[str]
    areas_for_improvement: List[str]
    delivery_feedback: DeliveryFeedback
    recommendations: List[str]

class ThankYouRequest(BaseModel):
    transcript_text: str
    role_title: str
    company: str
    interviewer_name: Optional[str] = None
    jd_analysis: Optional[Dict[str, Any]] = None

class ThankYouResponse(BaseModel):
    subject: str
    body: str
    key_points_used: List[str]

# ============================================================================
# INTERVIEW INTELLIGENCE MODELS
# ============================================================================

class InterviewPrepRequest(BaseModel):
    """Request for generating interview prep materials"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    jd_analysis: Optional[Dict[str, Any]] = None

class RedFlagMitigation(BaseModel):
    flag: str
    mitigation: str

class QuestionToAsk(BaseModel):
    question: str
    why: str

class STARExample(BaseModel):
    competency: str
    situation: str
    task: str
    action: str
    result: str

class LikelyQuestion(BaseModel):
    question: str
    suggested_answer: str

class RecruiterScreenPrepContent(BaseModel):
    interview_overview: str
    key_talking_points: List[str]
    red_flag_mitigation: List[RedFlagMitigation]
    likely_questions: List[LikelyQuestion]
    questions_to_ask: List[QuestionToAsk]
    compensation_expectations: str
    timeline_strategy: str

class HiringManagerPrepContent(BaseModel):
    interview_overview: str
    strengths_to_emphasize: List[str]
    gaps_to_mitigate: List[str]
    star_examples: List[STARExample]
    likely_questions: List[LikelyQuestion]
    questions_to_ask: List[QuestionToAsk]
    closing_strategy: str

class InterviewPrepResponse(BaseModel):
    interview_stage: str
    prep_content: Dict[str, Any]

class IntroSellTemplateRequest(BaseModel):
    """Request for generating intro sell template"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str

class IntroSellTemplateResponse(BaseModel):
    template: str
    word_count: int
    coaching_note: str

class IntroSellFeedbackRequest(BaseModel):
    """Request for analyzing intro sell attempt"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    candidate_version: str

class IntroSellFeedbackResponse(BaseModel):
    overall_score: float
    content_score: int
    structure_score: int
    tone_score: int
    word_count: int
    estimated_time_seconds: int
    strengths: List[str]
    opportunities: List[str]
    revised_version: str
    coaching_note: str

class TypedDebriefResponses(BaseModel):
    overall_feeling: str
    questions_asked: List[str]
    strong_answers: List[str]
    weak_answers: List[str]
    learnings: str

class InterviewDebriefRequest(BaseModel):
    """Request for post-interview debrief analysis"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    interview_date: str
    interviewer_name: Optional[str] = None
    transcript_text: Optional[str] = None
    typed_responses: Optional[TypedDebriefResponses] = None

class DimensionScores(BaseModel):
    content: int = Field(..., ge=1, le=10)
    clarity: int = Field(..., ge=1, le=10)
    delivery: int = Field(..., ge=1, le=10)
    tone: int = Field(..., ge=1, le=10)
    structure: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=10)

class WhatTheyShouldHaveSaid(BaseModel):
    question: str
    weak_answer: str
    strong_answer: str

class InterviewDebriefResponse(BaseModel):
    overall_score: int = Field(..., ge=1, le=10)
    dimension_scores: DimensionScores
    strengths: List[str]
    opportunities: List[str]
    what_they_should_have_said: List[WhatTheyShouldHaveSaid]
    coaching_points: List[str]
    action_items: List[str]
    thank_you_email: str
    next_stage_adjustments: List[str]

# ============================================================================
# SCREENING QUESTIONS MODELS
# ============================================================================

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

# ============================================================================
# EXPERIENCE SUPPLEMENTATION MODELS
# ============================================================================

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

# ============================================================================
# PREP GUIDE MODELS
# ============================================================================

class PrepGuideLikelyQuestion(BaseModel):
    """A likely interview question with guidance"""
    question: str
    guidance: str  # Suggested answer approach based on candidate's experience

class PrepGuideStory(BaseModel):
    """A STAR story for the candidate"""
    title: str
    competency: str  # e.g., "Leadership", "Problem-solving"
    situation: str
    task: str
    action: str
    result: str

class PrepGuideStrategyScenario(BaseModel):
    """A strategy/case scenario for HM/Technical interviews"""
    scenario: str
    approach: str

class PrepGuideRequest(BaseModel):
    """Request to generate an interview prep guide"""
    company: str
    role_title: str
    interview_type: str  # recruiter_screen, hiring_manager, technical, panel, executive
    job_description: str = ""
    interviewer_name: str = ""
    interviewer_title: str = ""
    resume_json: Dict[str, Any] = {}

class PrepGuideResponse(BaseModel):
    """Response containing the full prep guide"""
    what_they_evaluate: List[str]
    intro_pitch: str
    likely_questions: List[PrepGuideLikelyQuestion]
    stories: List[PrepGuideStory]
    red_flags: List[str]
    strategy_scenarios: Optional[List[PrepGuideStrategyScenario]] = None

class RegenerateIntroRequest(BaseModel):
    """Request to regenerate just the intro pitch"""
    company: str
    role_title: str
    interview_type: str
    resume_json: Dict[str, Any] = {}

class RegenerateIntroResponse(BaseModel):
    """Response with new intro pitch"""
    intro_pitch: str

# ============================================================================
# MOCK INTERVIEW MODELS
# ============================================================================

class StartMockInterviewRequest(BaseModel):
    """Request to start a mock interview session"""
    resume_json: Dict[str, Any]
    job_description: str
    company: str
    role_title: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")

class FirstQuestionResponse(BaseModel):
    """First question returned when starting a session"""
    question_id: str
    question_text: str
    competency_tested: str
    question_number: int

class StartMockInterviewResponse(BaseModel):
    """Response after starting a mock interview"""
    session_id: str
    interview_stage: str
    difficulty_level: str
    first_question: FirstQuestionResponse

class SubmitMockResponseRequest(BaseModel):
    """Request to submit a response to a mock interview question"""
    session_id: str
    question_id: str
    response_text: str
    response_number: int = Field(..., ge=1, le=4)

class SubmitMockResponseResponse(BaseModel):
    """Response after submitting an answer"""
    response_recorded: bool
    follow_up_question: Optional[str] = None
    should_continue: bool
    brief_feedback: str

class QuestionFeedbackResponse(BaseModel):
    """Comprehensive feedback for a completed question"""
    question_text: str
    all_responses: List[str]
    score: int = Field(..., ge=1, le=10)
    level_demonstrated: str
    what_landed: List[str]
    what_didnt_land: List[str]
    coaching: str
    revised_answer: str

class NextQuestionRequest(BaseModel):
    """Request to move to the next question"""
    session_id: str
    current_question_number: int

class MockSessionProgress(BaseModel):
    """Progress within a mock interview session"""
    questions_completed: int
    average_score: float

class NextQuestionResponse(BaseModel):
    """Response with the next question"""
    question_id: str
    question_text: str
    competency_tested: str
    question_number: int
    total_questions: int
    session_progress: MockSessionProgress

class EndMockInterviewRequest(BaseModel):
    """Request to end a mock interview session"""
    session_id: str

class MockQuestionSummary(BaseModel):
    """Summary of a single question's performance"""
    question_number: int
    question_text: str
    score: int
    brief_feedback: str

class MockSessionFeedback(BaseModel):
    """Session-level feedback after completing mock interview"""
    overall_assessment: str
    key_strengths: List[str]
    areas_to_improve: List[str]
    coaching_priorities: List[str]
    recommended_drills: List[str] = []  # Signal-based drill recommendations
    readiness_score: str  # "Ready" | "Almost Ready" | "Needs Practice"
    level_estimate: str = "mid"  # "mid" | "senior" | "director" | "executive"
    next_steps: str

class EndMockInterviewResponse(BaseModel):
    """Response after ending a mock interview"""
    session_id: str
    overall_score: float
    questions_completed: int
    session_feedback: MockSessionFeedback
    question_summaries: List[MockQuestionSummary]

class MockInterviewSessionSummary(BaseModel):
    """Summary of a past mock interview session"""
    session_id: str
    interview_stage: str
    started_at: str
    completed_at: Optional[str]
    overall_score: Optional[float]
    questions_completed: int

class ImprovementTrend(BaseModel):
    """Improvement trend across multiple sessions"""
    first_session_score: float
    latest_session_score: float
    improvement: str

class SessionHistoryResponse(BaseModel):
    """Response with session history"""
    sessions: List[MockInterviewSessionSummary]
    improvement_trend: Optional[ImprovementTrend] = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def call_claude(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    """Call Claude API with given prompts"""
    try:
        print(f"🤖 Calling Claude API... (message length: {len(user_message)} chars)")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        response_text = message.content[0].text
        print(f"🤖 Claude responded with {len(response_text)} chars")
        return response_text
    except Exception as e:
        print(f"🔥 CLAUDE API ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

def clean_claude_json(text: str) -> str:
    """Aggressively clean Claude's response to extract valid JSON"""
    # Remove code fences
    if text.strip().startswith("```"):
        parts = text.strip().split("```")
        text = parts[1] if len(parts) > 1 else text
    # Remove "json" prefix inside code blocks
    text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()
    # Remove leading non-json content
    first_brace = text.find("{")
    if first_brace != -1:
        text = text[first_brace:]
    # Remove trailing junk after last closing brace
    last_brace = text.rfind("}")
    if last_brace != -1:
        text = text[:last_brace + 1]
    return text


# ============================================================================
# MOCK INTERVIEW HELPER FUNCTIONS AND PROMPTS
# ============================================================================

def get_competency_for_stage(interview_stage: str, question_number: int) -> str:
    """
    Select competency to test based on stage and question number.
    Ensures variety across the session.
    """
    competencies = {
        "recruiter_screen": [
            "communication",
            "motivation",
            "culture_fit",
            "technical_basics",
            "availability"
        ],
        "hiring_manager": [
            "leadership",
            "problem_solving",
            "ambiguity_tolerance",
            "stakeholder_management",
            "technical_depth"
        ]
    }

    stage_competencies = competencies.get(interview_stage, competencies["hiring_manager"])
    return stage_competencies[(question_number - 1) % len(stage_competencies)]


def determine_target_level(job_description: str) -> str:
    """
    Infer target level from job description language.
    Returns: "L4", "L5A", or "L5B"
    """
    jd_lower = job_description.lower()

    # L5B indicators
    if any(phrase in jd_lower for phrase in [
        "lead strategic initiatives",
        "define organizational direction",
        "influence senior leadership",
        "drive company-wide",
        "principal", "staff"
    ]):
        return "L5B"

    # L5A indicators
    elif any(phrase in jd_lower for phrase in [
        "lead cross-functional",
        "coordinate across teams",
        "strategic input",
        "senior", "lead"
    ]):
        return "L5A"

    # Default to L4
    else:
        return "L4"


def detect_role_type(job_description: str, role_title: str) -> str:
    """
    Detect the role type for role-specific question routing and signal weighting.
    Returns: "product_manager", "software_engineer", "ux_designer", "ui_designer",
             "talent_acquisition", "general_leadership"
    """
    combined = f"{job_description} {role_title}".lower()

    # Product Manager
    if any(term in combined for term in [
        "product manager", "product management", "pm ", "product lead",
        "product owner", "roadmap", "product strategy"
    ]):
        return "product_manager"

    # Software Engineer
    elif any(term in combined for term in [
        "software engineer", "developer", "engineering", "swe",
        "backend", "frontend", "full stack", "architect", "devops"
    ]):
        return "software_engineer"

    # UX Designer
    elif any(term in combined for term in [
        "ux designer", "ux research", "user experience", "user research",
        "design research", "uxr"
    ]):
        return "ux_designer"

    # UI Designer
    elif any(term in combined for term in [
        "ui designer", "visual designer", "ui/ux", "product designer",
        "interaction designer", "design system"
    ]):
        return "ui_designer"

    # Talent Acquisition / Recruiting
    elif any(term in combined for term in [
        "talent acquisition", "recruiting", "recruiter", "ta ",
        "sourcer", "talent partner", "hiring", "recruitment"
    ]):
        return "talent_acquisition"

    # General Leadership
    else:
        return "general_leadership"


# Signal weights by role type (used for scoring)
SIGNAL_WEIGHTS_BY_ROLE = {
    "product_manager": {
        "functional_competency": 0.15,
        "leadership": 0.10,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.15,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.10,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.05
    },
    "software_engineer": {
        "functional_competency": 0.20,
        "leadership": 0.05,
        "collaboration": 0.10,
        "ownership": 0.15,
        "strategic_thinking": 0.10,
        "problem_solving": 0.15,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.05
    },
    "ux_designer": {
        "functional_competency": 0.15,
        "leadership": 0.05,
        "collaboration": 0.15,
        "ownership": 0.10,
        "strategic_thinking": 0.10,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.15
    },
    "ui_designer": {
        "functional_competency": 0.20,
        "leadership": 0.05,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.05,
        "problem_solving": 0.10,
        "communication_clarity": 0.15,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.00,
        "user_centricity": 0.15
    },
    "talent_acquisition": {
        "functional_competency": 0.15,
        "leadership": 0.10,
        "collaboration": 0.15,
        "ownership": 0.10,
        "strategic_thinking": 0.10,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.10,
        "stakeholder_management": 0.10,
        "executive_presence": 0.00,
        "user_centricity": 0.00
    },
    "general_leadership": {
        "functional_competency": 0.15,
        "leadership": 0.15,
        "collaboration": 0.10,
        "ownership": 0.10,
        "strategic_thinking": 0.15,
        "problem_solving": 0.10,
        "communication_clarity": 0.10,
        "metrics_orientation": 0.05,
        "stakeholder_management": 0.05,
        "executive_presence": 0.05,
        "user_centricity": 0.00
    }
}


def calculate_weighted_score(signals: dict, role_type: str) -> float:
    """
    Calculate weighted score based on signals and role-specific weights.
    """
    weights = SIGNAL_WEIGHTS_BY_ROLE.get(role_type, SIGNAL_WEIGHTS_BY_ROLE["general_leadership"])
    weighted_sum = 0.0

    for signal_name, signal_value in signals.items():
        weight = weights.get(signal_name, 0.0)
        weighted_sum += signal_value * weight

    # Convert to 1-10 scale
    return round(weighted_sum * 10, 1)


def calculate_mock_session_average(session_id: str) -> float:
    """
    Calculate average score across all completed questions in session.
    """
    session = mock_interview_sessions.get(session_id)
    if not session:
        return 0.0

    question_ids = session.get("question_ids", [])
    scores = []

    for qid in question_ids:
        analysis = mock_interview_analyses.get(qid)
        if analysis and analysis.get("score"):
            scores.append(analysis["score"])

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


def format_responses_for_analysis(question_id: str) -> str:
    """
    Format all responses to a question into text for analysis.
    """
    responses = mock_interview_responses.get(question_id, [])
    formatted = []

    for i, response in enumerate(responses, 1):
        label = "INITIAL RESPONSE" if i == 1 else f"FOLLOW-UP {i-1}"
        formatted.append(f"{label}:\n{response.get('response_text', '')}")

    return "\n\n".join(formatted)


# Mock Interview Prompt Templates

MOCK_GENERATE_QUESTION_PROMPT = """You are conducting a mock interview for a {interview_stage} stage.

CANDIDATE NAME: {candidate_name}

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
Company: {company}
Role: {role_title}

JOB DESCRIPTION:
{job_description}

INTERVIEW STAGE: {interview_stage}
DIFFICULTY LEVEL: {difficulty}
QUESTIONS ALREADY ASKED: {asked_questions}

Generate a behavioral or technical question that:
1. Tests competency in {competency_area}
2. Is realistic for this interview stage
3. Is answerable using candidate's actual work experience
4. Matches the difficulty level
5. Does not repeat previously asked questions
6. IMPORTANT: Start the question with a natural, conversational opener that uses the candidate's first name (e.g., "Okay {candidate_name},", "So {candidate_name},", "Alright {candidate_name},", "{candidate_name},")

DIFFICULTY GUIDELINES:
- Easy: Straightforward STAR questions, clear scenarios
- Medium: Multi-faceted situations, requires prioritization or tradeoffs
- Hard: Ambiguous scenarios, strategic thinking, handling conflict/failure

OUTPUT FORMAT:
Return JSON:
{{
    "question_text": "string (the actual question, starting with the candidate's name)",
    "competency_tested": "string (primary competency being evaluated)",
    "difficulty": "easy|medium|hard"
}}

No markdown, no preamble."""


MOCK_ANALYZE_RESPONSE_PROMPT = """Analyze this candidate's COMPLETE response to a mock interview question, including all their follow-up answers.

QUESTION: {question_text}
EXPECTED COMPETENCY: {competency}
TARGET LEVEL: {target_level}
ROLE TYPE: {role_type}

COMPLETE RESPONSE HISTORY:
{all_responses}

CANDIDATE BACKGROUND:
{resume_text}

IMPORTANT: Score based on the CUMULATIVE quality of ALL responses, not just the latest one. If the candidate's follow-up answers filled gaps or added valuable details, their score should improve significantly.

## SIGNAL TRACKING
For each response, evaluate these 11 signals (score 0.0 to 1.0):

1. **functional_competency** - Does the candidate demonstrate relevant functional knowledge for their role?
2. **leadership** - Team direction, influence, decision-making
3. **collaboration** - Cross-team work, partnership, relationship building
4. **ownership** - End-to-end accountability, "I" statements, taking responsibility
5. **strategic_thinking** - High-level planning, long-term vision, business context
6. **problem_solving** - Structured thinking, root cause analysis, creative solutions
7. **communication_clarity** - Concise, clear, well-structured responses
8. **metrics_orientation** - Uses numbers, percentages, measurable outcomes
9. **stakeholder_management** - Managing up/across, influencing without authority
10. **executive_presence** - Confidence, gravitas, ability to communicate to senior leaders (if applicable)
11. **user_centricity** - Customer/user focus (for PM/UX/UI roles)

## FOLLOW-UP TRIGGER RULES
Trigger a follow-up when you detect:
- **missing_metrics**: Answer lacks numbers or measurable outcomes
- **vague_answer**: Too broad, no specifics, missing "what YOU did"
- **no_conflict**: Too polished, no mention of challenges or obstacles
- **no_strategy**: Jumps to solution without explaining thinking process
- **no_user_focus**: (PM/UX) Missing user insight or customer perspective
- **no_technical_depth**: (SWE) Missing architectural or technical reasoning

## LEVEL GUIDELINES
- **Mid-level**: Strong functional competency + okay communication
- **Senior**: Strong functional + problem solving + some strategy
- **Director**: Solid strategy + cross-functional influence + leadership
- **Executive**: Vision + executive presence + organizational impact

OUTPUT FORMAT:
Return JSON:
{{
    "score": integer (1-10, reflecting cumulative quality),
    "level_demonstrated": "mid" | "senior" | "director" | "executive",
    "signals": {{
        "functional_competency": float (0.0-1.0),
        "leadership": float (0.0-1.0),
        "collaboration": float (0.0-1.0),
        "ownership": float (0.0-1.0),
        "strategic_thinking": float (0.0-1.0),
        "problem_solving": float (0.0-1.0),
        "communication_clarity": float (0.0-1.0),
        "metrics_orientation": float (0.0-1.0),
        "stakeholder_management": float (0.0-1.0),
        "executive_presence": float (0.0-1.0),
        "user_centricity": float (0.0-1.0)
    }},
    "signal_strengths": ["signals >= 0.7"],
    "signal_gaps": ["signals <= 0.4"],
    "follow_up_trigger": "missing_metrics" | "vague_answer" | "no_conflict" | "no_strategy" | "no_user_focus" | "no_technical_depth" | null,
    "follow_up_questions": ["question1", "question2"],
    "brief_feedback": "string (1-2 sentences of immediate coaching)",
    "resume_content": {{
        "metrics": ["specific metric or number mentioned"],
        "achievements": ["specific accomplishment they described"],
        "stories": ["brief summary of any STAR story they told"]
    }}
}}

RULES:
- Score should INCREASE if follow-up responses added valuable detail
- Be specific about gaps (not "needs more detail" but "didn't mention stakeholder alignment")
- Only generate follow-ups if there's a clear trigger; otherwise set follow_up_trigger to null
- Extract concrete numbers, percentages, or metrics for resume enhancement

No markdown, no preamble."""


MOCK_QUESTION_FEEDBACK_PROMPT = """Provide comprehensive coaching feedback after this mock interview question.

QUESTION: {question_text}
COMPETENCY TESTED: {competency}
TARGET LEVEL: {target_level}

ALL CANDIDATE RESPONSES:
{all_responses_text}

ANALYSIS:
{analysis_json}

CANDIDATE BACKGROUND:
{resume_text}

Generate detailed feedback covering:
1. Overall assessment (2-3 sentences)
2. What landed (2-3 specific things they did well)
3. What didn't land (2-3 specific gaps or weaknesses)
4. Coaching (actionable advice for improvement)
5. Revised answer (rewrite their response at the target level using their actual experience)

OUTPUT FORMAT:
Return JSON:
{{
    "overall_assessment": "string (2-3 sentences)",
    "what_landed": ["bullet1", "bullet2", "bullet3"],
    "what_didnt_land": ["bullet1", "bullet2", "bullet3"],
    "coaching": "string (2-3 paragraphs of specific advice)",
    "revised_answer": "string (their answer rewritten at target level)"
}}

RULES FOR REVISED ANSWER:
- Use only their actual work experience (no fabrication)
- Elevate to target level (L4 → L5A → L5B)
- Include specific metrics, outcomes, and scope
- Follow STAR structure (Situation, Task, Action, Result)
- Keep it realistic (what they COULD have said, not fantasy)

COACHING GUIDELINES:
- Be direct and specific
- Reference actual gaps from their responses
- Provide tactical fixes (not just "be more strategic")
- Connect to competency frameworks

No markdown, no preamble."""


MOCK_SESSION_FEEDBACK_PROMPT = """Generate comprehensive feedback for this completed mock interview session.

SESSION DETAILS:
- Interview Stage: {interview_stage}
- Role Type: {role_type}
- Questions Completed: {num_questions}
- Average Score: {average_score}
- Level Demonstrated: {level_demonstrated}

## AGGREGATED SIGNAL SCORES (0.0 - 1.0)
{signal_summary}

## SIGNAL STRENGTHS (≥ 0.7)
{signal_strengths}

## SIGNAL GAPS (≤ 0.4)
{signal_gaps}

QUESTION SUMMARIES:
{questions_summary}

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
Company: {company}
Role: {role_title}

JOB DESCRIPTION:
{job_description}

Generate session-level feedback covering:
1. Overall assessment (2-3 sentences on readiness)
2. Key strengths (3 specific things based on signal strengths)
3. Areas to improve (3 specific things based on signal gaps)
4. Coaching priorities (3 specific drills/exercises based on gaps)
5. Recommended drills (map to weak signals)
6. Readiness score: "Ready" | "Almost Ready" | "Needs Practice"
7. Level estimate: "mid" | "senior" | "director" | "executive"

READINESS CRITERIA:
- Ready: Average score ≥8, no signal gaps below 0.3, level-appropriate
- Almost Ready: Average score 6-7.9, 1-2 minor signal gaps, mostly level-appropriate
- Needs Practice: Average score <6, multiple signal gaps, below-level

DRILL MAPPING:
- Low metrics_orientation → "Practice adding specific numbers and outcomes to every story"
- Low ownership → "Rewrite stories using 'I' statements and personal accountability"
- Low strategic_thinking → "Practice framing answers with business context first"
- Low stakeholder_management → "Add examples of cross-functional influence to your stories"
- Low communication_clarity → "Practice STAR structure: Situation, Task, Action, Result"
- Low problem_solving → "Practice explaining your decision-making framework step by step"

OUTPUT FORMAT:
Return JSON:
{{
    "overall_assessment": "string (2-3 sentences)",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "areas_to_improve": ["area1", "area2", "area3"],
    "coaching_priorities": ["priority1", "priority2", "priority3"],
    "recommended_drills": ["drill1", "drill2", "drill3"],
    "readiness_score": "Ready" | "Almost Ready" | "Needs Practice",
    "level_estimate": "mid" | "senior" | "director" | "executive",
    "next_steps": "string (what to do next)"
}}

RULES:
- Strengths should be specific and tied to signals (not "good communication" but "strong ownership signals - consistently used 'I' statements")
- Improvements should be actionable and tied to signal gaps
- Drills should directly address the weakest signals
- Level estimate should match demonstrated signals across all questions

No markdown, no preamble."""


def validate_outreach_template(template_text: str, template_type: str = "generic") -> tuple[bool, list[str]]:
    """
    Validates outreach template for quality and positioning.
    Returns (is_valid, error_messages)
    
    Args:
        template_text: The outreach message text to validate
        template_type: "hiring_manager" or "recruiter" or "generic"
    """
    errors = []
    
    if not template_text or len(template_text.strip()) == 0:
        errors.append("Template is empty")
        return False, errors
    
    # Check for em dashes and en dashes
    if '—' in template_text:
        errors.append("Contains em dashes (—) - use colons or periods instead")
    if '–' in template_text:
        errors.append("Contains en dashes (–) - use colons or periods instead")
    
    # Check for exclamation points (signals desperation)
    if '!' in template_text:
        errors.append("Contains exclamation points - remove for professional tone")
    
    # Check for generic phrases
    generic_phrases = [
        "I'm excited about this opportunity",
        "I'd be a great fit",
        "I'd love to chat",
        "I came across your posting",
        "I'm reaching out to express my interest",
        "great fit for my background",
        "perfect match for",
        "thrilled about"
    ]
    for phrase in generic_phrases:
        if phrase.lower() in template_text.lower():
            errors.append(f"Contains generic phrase: '{phrase}' - be more specific")
    
    # Check sentence length (flag if any sentence > 35 words)
    sentences = [s.strip() for s in template_text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
    for i, sentence in enumerate(sentences):
        word_count = len(sentence.split())
        if word_count > 35:
            errors.append(f"Sentence {i+1} is too long ({word_count} words) - keep under 30 words")
    
    # Check for passive voice indicators
    passive_indicators = ['was led by', 'were managed by', 'is overseen by', 'has been done']
    for indicator in passive_indicators:
        if indicator in template_text.lower():
            errors.append(f"Contains passive voice: '{indicator}' - use active voice")
    
    # Check for clear ask at the end (should have call-to-action words)
    ask_keywords = ['discuss', 'conversation', 'call', 'meeting', 'chat', 'connect', 'talk', 'explore']
    has_ask = any(keyword in template_text.lower() for keyword in ask_keywords)
    if not has_ask:
        errors.append("Missing clear ask/call-to-action")
    
    # Check minimum length (should be at least 2 sentences)
    if len(sentences) < 2:
        errors.append("Template too short - should be 3-5 sentences")
    
    # Check maximum length (should not be more than 7 sentences)
    if len(sentences) > 7:
        errors.append("Template too long - should be 3-5 sentences")
    
    return len(errors) == 0, errors


def cleanup_outreach_template(template_text: str) -> str:
    """
    Cleans up common issues in generated outreach templates.
    This is a last-resort cleanup for minor formatting issues.
    """
    if not template_text:
        return template_text
    
    # Replace em dashes with colons
    template_text = template_text.replace('—', ':')
    template_text = template_text.replace('–', ':')
    
    # Remove exclamation points (replace with periods)
    template_text = template_text.replace('!', '.')
    
    # Fix double spaces
    template_text = ' '.join(template_text.split())
    
    # Fix double periods
    while '..' in template_text:
        template_text = template_text.replace('..', '.')
    
    return template_text.strip()



def build_candidate_calibration_prompt(situation: Optional[Dict[str, Any]]) -> str:
    """
    Build a calibration prompt based on candidate's emotional state and situation.
    This affects DELIVERY, not ACCURACY - never inflate scores or hide gaps.
    """
    if not situation:
        return ""
    
    holding_up = situation.get("holding_up", "")
    timeline = situation.get("timeline", "")
    confidence = situation.get("confidence", "")
    move_type = situation.get("move_type", "")
    
    # If no situation data, return empty
    if not any([holding_up, timeline, confidence, move_type]):
        return ""
    
    calibration = """
=== CANDIDATE STATE CALIBRATION ===

The candidate has shared their current emotional and situational context. 
Use this to calibrate your tone, prioritization, and framing—not to change the facts, but to change how you deliver them.

**Candidate State:**
"""
    
    if holding_up:
        calibration += f"- Emotional state: {holding_up}\n"
    if timeline:
        calibration += f"- Timeline/Urgency: {timeline}\n"
    if confidence:
        calibration += f"- Confidence level: {confidence}\n"
    if move_type:
        calibration += f"- Move type: {move_type}\n"
    
    calibration += """
**Calibration Rules:**

### Emotional State (holding_up)
- "doing_well" → They're browsing, not desperate. Be efficient, skip emotional framing. Focus on fit and strategy.
- "stressed_but_managing" → Acknowledge the pressure briefly, then get to work. Don't dwell.
- "struggling" → Validate first. Acknowledge the difficulty before diving into tactics. Avoid toxic positivity. Be warm but direct.
- "rather_not_say" → Neutral tone. Don't probe. Just do the job.

### Timeline (timeline)
- "no_rush" → Full strategic mode. Include long-game moves: networking, positioning for future roles, stretch applications. Quality over speed.
- "actively_looking" → Balance strategy with momentum. Mix high-probability with strategic stretch roles.
- "soon" → Prioritize high-probability roles. Lead with "Apply" and "Strongly Apply" recommendations. Flag stretch roles as secondary.
- "urgent" → Speed matters. Prioritize roles above 60% fit. Lead with quick wins. Be direct about what's realistic. Do not waste their time on long shots.

### Confidence (confidence)
- "strong" → Be direct. They can handle blunt feedback. Don't pad the analysis.
- "shaky" → Balanced delivery. State gaps plainly but constructively. Remind them that rejections reflect market noise, not just their value.
- "low" → Lead with strengths. Frame gaps as "areas to address" not weaknesses. Soften language in fit analysis without hiding reality. End sections on a forward-looking note.
- "need_validation" → They need to hear they're not crazy. Acknowledge the market is brutal. Be honest about their strengths. Don't fabricate, but don't be stingy with legitimate praise either.

### Move Type (move_type)
- "lateral" → Emphasize transferable wins, culture fit, and why this company over others. Positioning is about differentiation.
- "step_up" → Emphasize leadership signals, scope expansion, and readiness for the next level. Address the "stretch" concern head-on.
- "pivot" → Emphasize transferable skills, adjacent experience, and learning agility. Acknowledge the narrative gap and help bridge it.
- "returning" → Normalize the gap. Emphasize what they did during it (if anything) and how their prior experience still applies. Don't make them feel like they're starting over.

**CRITICAL:** These calibrations affect *delivery*, not *accuracy*. Never inflate fit scores, hide real gaps, or sugarcoat bad-fit roles. The candidate deserves honesty—just delivered in a way that meets them where they are.

"""
    return calibration

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF file using PyMuPDF (fitz)"""
    try:
        import fitz  # PyMuPDF
        
        # Open PDF from bytes
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Clean the text
        text = text.replace('\x00', '')  # Remove null bytes
        
        if not text.strip():
            raise ValueError("No text extracted from PDF")
            
        return text.strip()
    except ImportError:
        # Fallback to PyPDF2 if fitz not available
        try:
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")

def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX file using python-docx"""
    try:
        from docx import Document
        from io import BytesIO
        
        print("📄 Attempting to parse DOCX file...")
        doc = Document(BytesIO(file_bytes))
        
        # Extract text from paragraphs
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        print(f"📄 Found {len(paragraphs)} paragraphs")
        
        # Also extract text from tables (resumes often use tables for layout)
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    table_text.append(' | '.join(row_text))
        print(f"📄 Found {len(table_text)} table rows")
        
        # Combine all text
        all_text = paragraphs + table_text
        text = '\n'.join(all_text)
        
        # Clean the text
        text = text.replace('\x00', '')  # Remove null bytes
        
        if not text.strip():
            raise ValueError("No text extracted from DOCX")
        
        print(f"📄 Successfully extracted {len(text)} characters from DOCX")
        return text.strip()
    except Exception as e:
        print(f"🔥 DOCX EXTRACTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"DOCX extraction failed: {str(e)}")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Henry Job Search Engine API",
        "version": "1.4.0",
        "endpoints": [
            "/api/resume/parse",
            "/api/jd/analyze",
            "/api/documents/generate",
            "/api/screening-questions/generate",
            "/api/experience/clarifying-questions",
            "/api/experience/reanalyze",
            "/api/tasks/prioritize",
            "/api/outcomes/log",
            "/api/strategy/review",
            "/api/network/recommend",
            "/api/interview/parse",
            "/api/interview/feedback",
            "/api/interview/thank_you",
            "/api/prep-guide/generate",
            "/api/prep-guide/regenerate-intro"
        ]
    }

@app.post("/api/resume/parse")
async def parse_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Parse resume from file upload or text
    
    Two ways to call this endpoint:
    1. File upload: Send multipart/form-data with 'file' field containing PDF/DOCX
    2. JSON body: Send application/json with { "resume_text": "..." }
    
    Returns structured JSON profile
    """
    
    text_content = None
    
    try:
        # Method 1: File upload (multipart/form-data)
        if file:
            print(f"📁 Received file: {file.filename}")
            try:
                file_bytes = await file.read()
                print(f"📁 File size: {len(file_bytes)} bytes")
                filename = file.filename.lower() if file.filename else ""
                
                if filename.endswith('.pdf'):
                    print("📁 Detected PDF format")
                    text_content = extract_pdf_text(file_bytes)
                elif filename.endswith('.docx'):
                    print("📁 Detected DOCX format")
                    text_content = extract_docx_text(file_bytes)
                elif filename.endswith('.txt'):
                    print("📁 Detected TXT format")
                    text_content = file_bytes.decode('utf-8')
                else:
                    # Try to decode as text
                    print(f"📁 Unknown format: {filename}, trying as text")
                    try:
                        text_content = file_bytes.decode('utf-8')
                    except:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Unsupported file type: {filename}. Please upload PDF, DOCX, or TXT file."
                        )
                print(f"📁 Extracted text length: {len(text_content) if text_content else 0}")
            except HTTPException:
                raise
            except Exception as e:
                print(f"🔥 FILE READING ERROR: {e}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        # Method 2: Text from form data (for compatibility)
        elif resume_text:
            text_content = resume_text
        
        # Method 3: JSON body (handle via request body parsing)
        # This is handled by FastAPI's automatic JSON parsing when Content-Type is application/json
        # We need a separate endpoint or use Request object
        
        if not text_content:
            raise HTTPException(
                status_code=400, 
                detail="No resume provided. Please upload a file or provide resume text."
            )
        
        # System prompt for resume parsing
        system_prompt = """You are a resume parser. Extract structured information from resumes.

CRITICAL RULES:
- Extract ONLY information that is explicitly present
- Do NOT fabricate or infer data
- If a field is not found, use null or empty array
- Maintain exact titles, companies, and dates as written
- Preserve all bullet points exactly as written

Return valid JSON matching this structure:
{
  "full_name": "string",
  "contact": {
    "full_name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null"
  },
  "current_title": "string or null",
  "target_roles": ["array of strings"],
  "industries": ["array of strings"],
  "years_experience": "string or null",
  "summary": "string (extract or create brief 2-3 sentence summary)",
  "experience": [
    {
      "company": "string",
      "title": "string",
      "dates": "string (as written)",
      "industry": "string or null",
      "bullets": ["array of bullet points exactly as written"]
    }
  ],
  "key_achievements": ["array of strings"],
  "core_competencies": ["array of strings"],
  "skills": ["array of technical and soft skills"],
  "education": "string or null",
  "certifications": ["array of strings or empty"]
}

Your response must be ONLY valid JSON, no additional text."""

        user_message = f"Parse this resume into structured JSON:\n\n{text_content}"
        
        # Call Claude
        print(f"📤 Sending {len(text_content)} chars to Claude for parsing...")
        response = call_claude(system_prompt, user_message)
        print(f"📥 Received response from Claude: {len(response)} chars")
        print(f"📥 Response preview: {response[:500]}...")
        
        # Clean and parse JSON response
        cleaned = clean_claude_json(response)
        print(f"📥 Cleaned JSON preview: {cleaned[:500]}...")
        
        try:
            parsed_data = json.loads(cleaned)
        except Exception as e:
            print("🔥 FINAL JSON PARSE ERROR:", e)
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Claude returned invalid JSON. Cleaned output preview: {cleaned[:300]}"
            )
        
        print(f"✅ Successfully parsed resume for: {parsed_data.get('full_name', 'Unknown')}")
        return parsed_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except json.JSONDecodeError as e:
        print("🔥 JSON DECODE ERROR:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse Claude response as JSON: {str(e)}"
        )
    except Exception as e:
        print("🔥 ERROR WHILE PARSING RESUME:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error parsing resume: {str(e)}"
        )


# Separate endpoint for JSON body resume text
@app.post("/api/resume/parse/text")
async def parse_resume_text(request: ResumeParseRequest) -> Dict[str, Any]:
    """
    Alternative endpoint that accepts JSON body with resume_text field
    This allows frontend to send JSON instead of form-data
    """
    if not request.resume_text:
        raise HTTPException(status_code=400, detail="resume_text field is required")
    
    try:
        # System prompt for resume parsing (same as above)
        system_prompt = """You are a resume parser. Extract structured information from resumes.

CRITICAL RULES:
- Extract ONLY information that is explicitly present
- Do NOT fabricate or infer data
- If a field is not found, use null or empty array
- Maintain exact titles, companies, and dates as written
- Preserve all bullet points exactly as written

Return valid JSON matching this structure:
{
  "full_name": "string",
  "contact": {
    "full_name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null"
  },
  "current_title": "string or null",
  "target_roles": ["array of strings"],
  "industries": ["array of strings"],
  "years_experience": "string or null",
  "summary": "string (extract or create brief 2-3 sentence summary)",
  "experience": [
    {
      "company": "string",
      "title": "string",
      "dates": "string (as written)",
      "industry": "string or null",
      "bullets": ["array of bullet points exactly as written"]
    }
  ],
  "key_achievements": ["array of strings"],
  "core_competencies": ["array of strings"],
  "skills": ["array of technical and soft skills"],
  "education": "string or null",
  "certifications": ["array of strings or empty"]
}

Your response must be ONLY valid JSON, no additional text."""

        user_message = f"Parse this resume into structured JSON:\n\n{request.resume_text}"
        
        # Call Claude
        response = call_claude(system_prompt, user_message)
        
        # Parse JSON response
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return parsed_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse Claude response as JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error parsing resume text: {str(e)}"
        )


# ============================================================================
# URL JOB DESCRIPTION EXTRACTION
# ============================================================================

class URLExtractRequest(BaseModel):
    url: str

class URLExtractResponse(BaseModel):
    success: bool
    job_description: Optional[str] = None
    company: Optional[str] = None
    role_title: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/jd/extract-from-url", response_model=URLExtractResponse)
async def extract_jd_from_url(request: URLExtractRequest):
    """
    Extract job description content from a URL.

    Supported job boards:
    - LinkedIn, Indeed, Greenhouse, Lever, Workday, and generic job pages

    Note: Some sites may block scraping or require authentication.
    Results may vary in quality depending on the site structure.
    """
    import httpx
    import re

    url = request.url.strip()

    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print(f"🔗 Extracting JD from URL: {url}")

    try:
        # Set up headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as http_client:
            response = await http_client.get(url, headers=headers)

            if response.status_code != 200:
                return URLExtractResponse(
                    success=False,
                    error=f"Could not access the page (status {response.status_code}). The site may block automated access."
                )

            html_content = response.text

        # Check for common blocking patterns
        if "captcha" in html_content.lower() or "verify you are human" in html_content.lower():
            return URLExtractResponse(
                success=False,
                error="This site requires human verification. Please copy and paste the job description manually."
            )

        if len(html_content) < 500:
            return URLExtractResponse(
                success=False,
                error="Page content appears incomplete. The site may require login or block automated access."
            )

        # Use Claude to extract the job description from HTML
        extraction_prompt = f"""Extract the job description from this HTML page. Return a JSON object with these fields:

1. "job_description": The full job description text, including:
   - About the company (if present)
   - Role overview/summary
   - Responsibilities/duties
   - Requirements/qualifications
   - Nice-to-haves/preferred qualifications
   - Benefits (if present)

   Format this as clean, readable text with clear section breaks. Remove any navigation, footer, or unrelated content.

2. "company": The company name

3. "role_title": The job title

If you cannot find a job description on this page, set job_description to null and explain in the "error" field.

HTML CONTENT:
{html_content[:50000]}

Return ONLY valid JSON, no markdown code blocks."""

        extraction_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        result_text = extraction_response.content[0].text.strip()

        # Clean up potential markdown formatting
        if result_text.startswith("```"):
            result_text = re.sub(r'^```(?:json)?\n?', '', result_text)
            result_text = re.sub(r'\n?```$', '', result_text)

        try:
            extracted = json.loads(result_text)
        except json.JSONDecodeError:
            print(f"❌ Failed to parse extraction result: {result_text[:500]}")
            return URLExtractResponse(
                success=False,
                error="Could not parse the job description from this page. Please copy and paste manually."
            )

        job_description = extracted.get("job_description")

        if not job_description or len(job_description) < 100:
            return URLExtractResponse(
                success=False,
                error=extracted.get("error", "Could not find a job description on this page. Please copy and paste manually.")
            )

        print(f"✅ Extracted JD: {len(job_description)} chars, Company: {extracted.get('company')}, Role: {extracted.get('role_title')}")

        return URLExtractResponse(
            success=True,
            job_description=job_description,
            company=extracted.get("company"),
            role_title=extracted.get("role_title"),
            warning="Job descriptions extracted from URLs may be incomplete or contain formatting artifacts. For best results, review and edit the extracted text before analyzing."
        )

    except httpx.TimeoutException:
        return URLExtractResponse(
            success=False,
            error="Request timed out. The site may be slow or blocking automated access."
        )
    except httpx.RequestError as e:
        print(f"❌ HTTP error: {e}")
        return URLExtractResponse(
            success=False,
            error="Could not connect to the URL. Please check the URL and try again."
        )
    except Exception as e:
        print(f"❌ URL extraction error: {e}")
        return URLExtractResponse(
            success=False,
            error=f"An error occurred while extracting the job description. Please copy and paste manually."
        )


# ============================================================================
# TAILORED DOCUMENT GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/resume/customize")
async def customize_resume(request: ResumeCustomizeRequest) -> Dict[str, Any]:
    """
    Generate a tailored resume based on job description.
    Returns fully formatted resume text ready for display/download.
    """

    system_prompt = """You are HenryAI, an intelligent resume customization engine that generates ATS-optimized, strategically positioned resumes. Your goal is to maximize interview conversion by combining keyword optimization with strategic positioning.

=== 1. ABSOLUTE RULES (NON-NEGOTIABLE) ===

## 1.1 Zero Fabrication Rule
You may NOT invent: job titles, metrics, tools/technologies, achievements, degrees, certifications.
You may only rewrite, clarify, reorder, or strengthen content that already exists in the candidate's resume.

## 1.2 ATS-Safe Formatting
- No tables, no two-column layouts, no icons, no graphics
- Standard section headers only: SUMMARY, EXPERIENCE, SKILLS, EDUCATION
- Bullet points using • only
- Standard fonts assumed (Arial, Calibri)
- No special characters beyond • and standard punctuation

=== 2. KEYWORD TIERING SYSTEM (CRITICAL FOR ATS) ===

Before writing the resume, extract keywords from the JD into three tiers:

**Tier 1 (Critical - MUST appear 4-6 times each):**
- Keywords in the job title itself
- Keywords repeated 3+ times in the JD
- Keywords in "required qualifications" section
Examples: If JD title is "Director of Talent Acquisition" and mentions "executive search" 4 times, both are Tier 1.

**Tier 2 (Important - MUST appear 2-3 times each):**
- Keywords in "required qualifications" that appear 1-2 times
- Industry-specific terms and tools mentioned
- Action verbs the JD emphasizes (lead, build, scale, optimize)
Examples: "Workday ATS", "high-volume recruiting", "workforce planning"

**Tier 3 (Nice-to-have - appear 1-2 times):**
- Keywords in "preferred qualifications"
- Soft skills mentioned (collaborative, data-driven)
- Secondary tools or methodologies

**Keyword Placement Priority (ATS Weight):**
1. HIGHEST: Job title line in header, Summary section (first 3 sentences), Skills section
2. MEDIUM: First bullet of each experience section, Key Achievements
3. LOWER: Later bullets, company descriptions

**Exact Match Rule:** Use the JD's exact phrasing. If JD says "Workday ATS" use "Workday ATS" not just "Workday". If JD says "executive search" use "executive search" not "executive recruiting".

=== 3. COMPANY STAGE POSITIONING ===

Detect company stage from JD signals and adjust tone/emphasis:

**Startup/Scale-up Signals:** "fast-paced", "0-1", "Series A/B/C", "high-growth", "build from scratch", "wear multiple hats"
→ Lead with: startup/growth experience, scrappy execution, speed, building from scratch
→ Tone: Action-oriented, emphasize agility and impact
→ De-emphasize: Large enterprise process, bureaucratic language

**Enterprise/Fortune 500 Signals:** "global", "Fortune 500", "public company", "cross-regional", "compliance"
→ Lead with: Scale, process rigor, executive stakeholder management, global scope
→ Tone: Professional, strategic, emphasize governance
→ Keep all experience, show progression

**Mid-market/PE-backed Signals:** "growth-stage", "private equity", "scalable", "cost efficiency"
→ Balance: Startup agility + operational maturity
→ Lead with: Scalable systems, efficiency, rapid execution with structure

=== 4. FUNCTIONAL DEPTH MATCHING ===

Identify what the JD emphasizes most and lead with matching experience:

**If JD emphasizes executive search/C-suite hiring:**
→ Lead with executive search experience, retained search, leadership assessment
→ Add keywords: succession planning, Board-level, VP/SVP placement

**If JD emphasizes high-volume/operational hiring:**
→ Lead with high-volume metrics, pipeline scale, hiring velocity
→ Add keywords: pipeline generation, sourcing campaigns, funnel metrics

**If JD emphasizes technical recruiting:**
→ Lead with engineering/product hiring experience
→ Add keywords: technical pipelines, engineering hiring, product roles

**If JD emphasizes team leadership:**
→ Lead with team size, global scope, mentoring
→ Add keywords: team development, recruiter coaching, performance management

=== 5. LEVEL CALIBRATION ===

**If applying for role BELOW current level (overqualified risk):**
→ Reframe: "Seeking hands-on leadership role balancing strategy with execution"
→ Emphasize: Execution metrics, deliverables, processes built
→ De-emphasize: Pure strategy, C-suite language

**If applying for role ABOVE current level (stretch role):**
→ Emphasize: Scope of impact, budget managed, cross-functional influence
→ Frame: "Operating at [higher level] scope"

=== 6. RESUME STRUCTURE (MANDATORY FORMAT) ===

```
{FULL NAME IN ALL CAPS}
{TARGET ROLE FROM JD} | {Strength 1} | {Strength 2}
{Phone} • {Email} • {LinkedIn URL} • {City, State}

SUMMARY
[4-5 sentences, 80-100 words. Must include: role being pursued, 2-3 core strengths matching JD, 1 measurable impact. Load with Tier 1 keywords. First sentence must state professional identity + years + core function.]

SKILLS
[8-16 skills in format: Skill 1 | Skill 2 | Skill 3 | ... ]
[Order by: JD required skills first, then tools from resume, then domain knowledge]
[Only include skills the candidate actually has evidence of]

EXPERIENCE

{COMPANY NAME}
{Job Title} | {Location} | {Dates}
[Optional 1-line company context if adds credibility: "Fortune 500 healthcare company with 50,000+ employees"]
• [Most JD-relevant bullet first - front-load with Tier 1 keywords, include metric]
• [Second most relevant - include Tier 1 or 2 keyword]
• [Third bullet - achievement or responsibility aligned to JD]
• [Fourth bullet - skill/tool demonstration]
[Max 5-6 bullets per role, fewer for older roles]

[Repeat for each relevant role - typically 3-4 roles for 2-page resume]

EDUCATION
{Degree}, {Major} | {University}
[Optional: relevant concentration, honors]
```

=== 7. BULLET REORDERING RULE ===

For each role, reorder bullets by relevance to THIS specific job:
- Most JD-relevant bullet becomes first bullet (even if chronologically it came later)
- Front-load each bullet with keywords (first 8-10 words get highest ATS weight)
- Each bullet should contain 2-4 relevant keywords naturally integrated

**Bullet Formula:** [Strong Action Verb] + [What You Did with JD Keywords] + [Quantified Outcome]
Example: "Led 25-person global technical recruiting team across engineering, product, and data functions, reducing time-to-offer by 30% while achieving 95% offer acceptance rate."

=== 8. OUTPUT FORMAT ===

Return a JSON object with this EXACT structure:

{
  "tailored_resume_text": "FULL FORMATTED RESUME TEXT - use \\n for line breaks",
  "positioning_strategy": {
    "company_stage_detected": "startup|scale-up|enterprise|mid-market",
    "functional_emphasis": "executive_search|high_volume|technical|team_leadership|generalist",
    "level_calibration": "at_level|stretch_up|stepping_down",
    "lead_with": "1 sentence describing what experience we're leading with and why",
    "de_emphasize": "1 sentence describing what we're de-emphasizing and why"
  },
  "keyword_analysis": {
    "tier_1_keywords": ["keyword1", "keyword2", "keyword3"],
    "tier_1_placements": 15,
    "tier_2_keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
    "tier_2_placements": 10,
    "tier_3_keywords": ["keyword1", "keyword2"],
    "tier_3_placements": 4
  },
  "changes_summary": {
    "summary_rationale": "What we changed in the summary and why, referencing specific JD requirements",
    "experience_rationale": "Which roles/bullets we emphasized or reordered and why",
    "ats_optimization": "How we optimized for ATS with specific keyword placements",
    "positioning_statement": "This positions you as [specific strategic positioning for this role]"
  },
  "red_flags_addressed": [
    {"flag": "description of potential concern", "mitigation": "how we addressed it in the resume"}
  ]
}

Your response must be ONLY valid JSON. No markdown formatting."""

    # Inject candidate state calibration if available
    calibration_prompt = build_candidate_calibration_prompt(request.situation)
    if calibration_prompt:
        system_prompt += calibration_prompt

    # Build the resume content for Claude
    resume_content = ""
    if request.resume_json:
        resume_content = json.dumps(request.resume_json, indent=2)
    elif request.resume_text:
        resume_content = request.resume_text
    else:
        raise HTTPException(status_code=400, detail="Either resume_text or resume_json is required")

    user_message = f"""Generate a tailored resume for this candidate applying to this role.

TARGET ROLE: {request.target_role}
TARGET COMPANY: {request.target_company}

JOB DESCRIPTION:
{request.job_description}

CANDIDATE RESUME DATA:
{resume_content}
"""

    if request.jd_analysis:
        user_message += f"\n\nJD ANALYSIS (use for tailoring):\n{json.dumps(request.jd_analysis, indent=2)}"

    # Add supplemental information from candidate if provided
    if request.supplements and len(request.supplements) > 0:
        user_message += "\n\n=== ADDITIONAL CANDIDATE CONTEXT ===\n"
        user_message += "The candidate provided the following additional context to address gaps. INCORPORATE this information into the resume where appropriate (but do NOT fabricate beyond what they stated):\n\n"
        for supp in request.supplements:
            user_message += f"**Gap Area: {supp.gap_area}**\n"
            user_message += f"Question: {supp.question}\n"
            user_message += f"Candidate's Answer: {supp.answer}\n\n"

    user_message += """

Generate the tailored resume following the exact format in the system instructions.
Remember: NO fabrication - only use information from the candidate's actual resume AND the additional context provided above."""

    try:
        response = call_claude(system_prompt, user_message, max_tokens=4000)
        cleaned = clean_claude_json(response)
        result = json.loads(cleaned)
        
        # Validate required fields
        if "tailored_resume_text" not in result:
            raise ValueError("Missing tailored_resume_text in response")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"🔥 JSON parse error in /api/resume/customize: {e}")
        print(f"Response was: {response[:500]}...")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")
    except Exception as e:
        print(f"🔥 Error in /api/resume/customize: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cover-letter/generate")
async def generate_cover_letter(request: CoverLetterGenerateRequest) -> Dict[str, Any]:
    """
    Generate a tailored cover letter based on job description and candidate background.
    Returns fully formatted cover letter text ready for display/download.
    """
    
    system_prompt = """You are the document generation engine for HenryAI.
Your job is to generate high-quality, recruiter-grade cover letters tailored to each job description.

=== 1. GLOBAL RULES ===

## 1.1 Zero Fabrication Rule
You may NOT invent:
- job titles
- metrics
- tools/technologies
- achievements
You may only rewrite, clarify, or strengthen content that already exists.

## 1.2 Recruiter-Quality, No Fluff
Write like a senior recruiting leader building a candidate's narrative:
- direct
- concise
- metric-driven
- confident
- no filler language or vague claims
- NO "I believe," "I think," "I feel"
- NO "I am writing to express my interest..."
- NO "I would be honored..."

=== 2. HEADER FORMAT (MANDATORY) ===

Use this header exactly (same as resume):

{FULL NAME IN ALL CAPS}
{TARGET ROLE} | {STRENGTH 1} | {STRENGTH 2}
{PHONE} • {EMAIL} • {LINKEDIN} • {CITY, STATE}

=== 3. COVER LETTER STRUCTURE ===

4 paragraphs max:

## Paragraph 1: Opening
- State interest in role
- 1 sentence linking background to company's needs

## Paragraph 2: Key Experience
- Pull top 1-2 accomplishments
- Tie directly to responsibilities in JD

## Paragraph 3: Value Proposition
- Show strengths aligned with what company is solving for
- Highlight leadership, process rigor, or technical depth

## Paragraph 4: Close
- Confident, brief
- End with appreciation
- NO "I believe," "I think," "I feel"

=== 4. RULES ===
- Do NOT repeat lines from summary or resume
- No generic filler
- Include metrics where they exist in the resume
- Match the tone: senior professional who knows their worth

=== OUTPUT FORMAT ===

Return a JSON object with this EXACT structure:

{
  "cover_letter_text": "FULL FORMATTED COVER LETTER TEXT - use \\n for line breaks",
  "changes_summary": {
    "opening_rationale": "1 sentence explaining why you led with this angle",
    "body_rationale": "1-2 sentences on what themes you emphasized and avoided",
    "closing_rationale": "1 sentence on the tone of the close",
    "positioning_statement": "This frames you as [strategic insight]"
  }
}

Your response must be ONLY valid JSON."""

    # Inject candidate state calibration if available
    calibration_prompt = build_candidate_calibration_prompt(request.situation)
    if calibration_prompt:
        system_prompt += calibration_prompt

    # Build the resume content for Claude
    resume_content = ""
    if request.resume_json:
        resume_content = json.dumps(request.resume_json, indent=2)
    elif request.resume_text:
        resume_content = request.resume_text
    else:
        raise HTTPException(status_code=400, detail="Either resume_text or resume_json is required")

    user_message = f"""Generate a tailored cover letter for this candidate applying to this role.

TARGET ROLE: {request.target_role}
TARGET COMPANY: {request.target_company}

JOB DESCRIPTION:
{request.job_description}

CANDIDATE RESUME DATA:
{resume_content}
"""

    if request.strengths:
        user_message += f"\n\nCANDIDATE STRENGTHS TO EMPHASIZE:\n{json.dumps(request.strengths, indent=2)}"

    if request.jd_analysis:
        user_message += f"\n\nJD ANALYSIS (use for tailoring):\n{json.dumps(request.jd_analysis, indent=2)}"

    # Add supplemental information from candidate if provided
    if request.supplements and len(request.supplements) > 0:
        user_message += "\n\n=== ADDITIONAL CANDIDATE CONTEXT ===\n"
        user_message += "The candidate provided the following additional context to address gaps. WEAVE this into the cover letter naturally to strengthen their narrative:\n\n"
        for supp in request.supplements:
            user_message += f"**Gap Area: {supp.gap_area}**\n"
            user_message += f"Context: {supp.answer}\n\n"

    user_message += """

Generate the cover letter following the exact format in the system instructions.
Remember: NO fabrication, NO generic filler, NO clichés."""

    try:
        response = call_claude(system_prompt, user_message, max_tokens=2000)
        cleaned = clean_claude_json(response)
        result = json.loads(cleaned)
        
        # Validate required fields
        if "cover_letter_text" not in result:
            raise ValueError("Missing cover_letter_text in response")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"🔥 JSON parse error in /api/cover-letter/generate: {e}")
        print(f"Response was: {response[:500]}...")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")
    except Exception as e:
        print(f"🔥 Error in /api/cover-letter/generate: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jd/analyze")
async def analyze_jd(request: JDAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze job description with MANDATORY Intelligence Layer
    
    This endpoint performs comprehensive strategic analysis BEFORE any execution:
    1. Job Quality Score (apply/caution/skip)
    2. Strategic Positioning Recommendations
    3. Salary & Market Context
    4. Apply/Skip Decision
    5. Then traditional JD analysis
    
    Returns detailed analysis with intelligence layer and fit score
    """
    
    system_prompt = """You are a senior executive recruiter and career strategist.

=== ACCURACY & INFERENCE RULES (READ FIRST) ===

## Cardinal Rule: Optimize Language, Not Reality
You are reframing and emphasizing existing experience to match job description requirements.
You are NOT inventing new experience.

## Inference Framework

### HIGH CONFIDENCE → SAFE TO RECOMMEND
- Reframing existing experience with JD-aligned keywords
- Emphasizing accomplishments already in the resume
- Reordering bullets to highlight relevant work
- Using industry-standard terminology for work they clearly did

### MEDIUM CONFIDENCE → INFER CONSERVATIVELY
- Logical skill adjacencies (e.g., "worked with design team" → "collaborated with designers")
- Industry-standard responsibilities for their role
- Implicit competencies (e.g., "launched feature" → "managed timelines")

### LOW CONFIDENCE → FLAG AS GAP, DON'T FABRICATE
- Skills/tools never mentioned
- Experience outside their stated scope
- Metrics that don't exist in the resume

## What You Can Recommend
- Reframing bullets with JD-aligned language
- Pulling forward relevant experience that's buried
- Adding ATS keywords if the candidate demonstrably has the underlying skill
- Strengthening weak language ("worked with" → "collaborated with")

## What You CANNOT Do
- Invent metrics that don't exist
- Add skills the candidate never demonstrated
- Fabricate companies, roles, or outcomes
- Create accomplishments that aren't supported by the resume

CRITICAL: You MUST complete the Intelligence Layer analysis BEFORE any execution recommendations.

=== INTELLIGENCE LAYER (MANDATORY - MUST BE COMPLETE) ===

## 1. JOB QUALITY SCORE (REQUIRED)
Evaluate the job posting quality using these criteria:
• Posting age signals (if detectable from context)
• Salary range vs market benchmarks for role/level/location
• Company signals (stability, growth, recent news)
• JD clarity (clear role vs vague "Frankenstein" combining multiple functions)
• Level alignment with candidate background

You MUST provide one of these EXACT strings:
- "Apply" (strong opportunity, good fit, clear role)
- "Apply with caution" (red flags present but salvageable)
- "Skip — poor quality or low close rate" (multiple issues, waste of time)

Then explain in 3-5 substantive sentences why you gave this rating. DO NOT leave this empty.

## 2. STRATEGIC POSITIONING RECOMMENDATIONS (REQUIRED)
As an experienced executive recruiter, you MUST provide ALL of these:
• lead_with_strengths: Array of 2-3 specific strengths (NOT empty, NOT generic)
• gaps_and_mitigation: Array of 2-3 gaps with how to frame them (be specific)
• emphasis_points: Array of 2-3 things to emphasize (actionable advice)
• avoid_points: Array of 2-3 things to avoid or de-emphasize (specific guidance)
• positioning_strategy: 1-2 sentence overall strategy (substantive, not vague)
• positioning_rationale: Array of 2-3 strategic decisions explaining WHY you made these choices. Each should explain the reasoning, not just repeat the advice. Format: "We're [doing X] because [specific reason from JD or resume]." Examples:
  - "Leading with your Spotify experience because the JD mentions 'scale' 4 times and they need someone who's operated at high volume"
  - "De-emphasizing the consulting background because this is an in-house role and they may worry about your hands-on commitment"
  - "Positioning you as a builder rather than a maintainer because they're in growth mode (Series B, 50→200 headcount goal)"

Be direct and opinionated. This is strategic counsel, not generic advice.
If resume is not provided, base recommendations on the JD requirements alone.

## 3. SALARY & MARKET CONTEXT (REQUIRED)
You MUST provide ALL of these fields with real content:
• typical_range: Provide a realistic salary range (e.g., "$150K-$200K for Director level in SF")
  - Use your knowledge of market rates
  - If uncertain, provide a reasonable estimate with qualifier
  - DO NOT leave empty
• posted_comp_assessment: "not mentioned", "low", "fair", "strong", or "unclear"
• recommended_expectations: Specific guidance (e.g., "Target $180K-$200K base given experience")
  - Be actionable and specific
  - DO NOT just say "competitive" or "market rate"
• market_competitiveness: Assessment of supply/demand (2-3 sentences)
  - Reference market conditions
  - Be specific about this role/industry
• risk_indicators: Array of specific risks, or empty array [] if none

If salary data cannot be determined, explain WHY (e.g., "Insufficient location/level info in JD to estimate range accurately").

## 4. APPLY/SKIP DECISION (REQUIRED)
You MUST provide ALL of these:
• recommendation: "Apply", "Apply with caution", or "Skip" (EXACT strings only)
• reasoning: 1-2 substantive sentences explaining why (NOT vague)
• timing_guidance: Specific guidance (e.g., "Apply immediately", "Apply within 1 week", "Skip")

## 5. REALITY CHECK (REQUIRED - Data-Driven Market Context)

Calculate expected competition and provide market context using this data:

### Step 1: Identify Candidate's Primary Function
Match resume to one of: HR/Recruiting, Engineering, Product Management, Marketing, Sales, Customer Support, Design, Data Science, Finance, Operations/Admin

### Step 2: Apply Saturation Multipliers (base: 200 applicants)
SATURATION_MULTIPLIER by function:
- HR/Recruiting: 3.5 (50% workforce cut, highest saturation)
- Operations/Admin: 2.8 (34% of layoffs)
- Sales: 2.2 (20% of layoffs)
- Engineering: 2.0 (22% of layoffs but only 10% workforce cut)
- Product Management: 2.0 (7% of layoffs, specialized)
- Marketing: 1.9 (7-8% of layoffs)
- Finance: 1.8 (professional services hit hard)
- Design: 1.7 (2.3x more likely cut than engineers)
- Data Science: 1.6 (3% of layoffs)
- Customer Support: 1.5 (lower % but AI threat)

SENIORITY_MULTIPLIER:
- Entry/Junior: 0.7
- Mid-level: 1.0
- Senior: 1.5
- Staff/Principal: 1.8
- Director: 1.6
- VP/Executive: 1.3

GEOGRAPHY_MULTIPLIER:
- SF Bay Area: 1.3
- NYC: 1.3
- Seattle: 1.2
- Austin: 1.2
- Remote: 1.1
- Boston: 1.1
- LA: 1.1
- Denver/Boulder: 1.0
- Chicago: 1.0
- Secondary Markets: 0.8

INDUSTRY_MULTIPLIER:
- AI/ML: 1.3
- Fintech: 1.2
- Cybersecurity: 1.2
- Enterprise SaaS: 1.0
- Consumer Tech: 0.9
- Ad Tech: 0.8
- Crypto/Web3: 0.7

### Step 3: Calculate
expected_applicants = 200 * function_mult * seniority_mult * geography_mult * industry_mult
Round to range (e.g., 347 → "300-400+")

### Step 4: Response Rate by Function
- HR/Recruiting: 2-3%
- Operations/Admin: 3-4%
- Sales: 4-6%
- Engineering: 4-5%
- Product Management: 3-5%
- Marketing: 3-5%
- Finance: 3-4%
- Customer Support: 5-7%
- Design: 3-4%
- Data Science: 4-5%

### Step 5: Function Context (use these exact stats)
IMPORTANT: Use proper punctuation. NO em dashes (—). Use commas, periods, or colons instead.

- HR/Recruiting: "HR/Recruiting roles were hit hardest: 27.8% of all tech layoffs, with nearly 50% of the HR workforce eliminated (highest of any function)."
- Engineering: "Engineering roles represent 22% of tech layoffs, but only 10% of the engineering workforce was cut, far lower than most functions. However, AI automation is increasing pressure."
- Product Management: "Product Management roles represent 7% of tech layoffs (about 16,700 PMs cut in 2024-2025). Some companies eliminated entire PM layers."
- Marketing: "Marketing roles represent 7-8% of tech layoffs. Generative AI has enabled automation of content creation."
- Sales: "Sales roles were relatively protected: only 4% of salespeople in tech lost jobs. However, about 20% of total layoff victims worked in sales or customer-facing roles."
- Operations/Admin: "Operations and administrative roles represent 34% of all tech layoffs, the single largest category."
- Design: "Design roles represent 3% of tech layoffs, but designers were 2.3x more likely to be laid off than engineers."
- Data Science: "Data Science roles represent 3% of tech layoffs. Companies retained essential data infrastructure but downsized analytics teams."
- Finance: "Finance and accounting roles were hit across industries. Big Four firms cut thousands."
- Customer Support: "Customer support roles represent about 5% of tech layoffs, but AI automation is accelerating cuts (companies adopting AI reduced staffing by 24%)."

### Step 6: Industry Context
IMPORTANT: Use proper punctuation. NO em dashes (—). Use commas, periods, or colons instead.

- Tech: "Tech sector cut 95K+ U.S. jobs in 2024, with continued pressure in 2025."
- Healthcare: "Administrative roles heavily cut to preserve clinical staff. Hospitals eliminated non-clinical positions at 5:1 ratio."
- Finance: "Banking consolidation and rising interest rates drove support role elimination."
- Retail: "Store closures and HQ restructuring driven by e-commerce shift."
- Professional Services: "Big Four accounting firms cut thousands: PwC (1,800 jobs), KPMG (5% of staff)."
- Government: "Federal workforce reduction targeted 10K+ jobs at HHS alone."
- Manufacturing: "Production rebalancing and automation reduced operations and admin roles."
- Media/Entertainment: "Cord-cutting and mergers drove cuts. Disney and Paramount each eliminated approximately 7K roles."

### Step 7: Strategic Action (based on fit score)
Write this in FIRST PERSON, directly to the candidate. Be specific and actionable.
IMPORTANT: Use proper punctuation. NO em dashes (—). Use commas, periods, or colons instead.

- 70%+ fit: "Apply within 24 hours and immediately find the hiring manager or VP of [function] on LinkedIn. With [X] expected applicants, you cannot rely on the ATS alone. Your [specific strength from resume] gives you an edge. Use it in your outreach."
- 50-69% fit: "Apply, but do not just submit and hope. You are competing against candidates with more direct experience. Find someone at the company who can refer you internally. That is your only real path here."
- <50% fit: "I will be direct: this is a long shot. [X]+ better-matched candidates means your cold application probably will not get seen. Only pursue if you have an inside connection. Otherwise, focus on roles where you are 70%+ fit."

The strategic_action field should feel like a recruiter giving honest advice, not a form letter.

=== THEN TRADITIONAL JD ANALYSIS ===

After completing the Intelligence Layer and Reality Check, provide standard JD analysis:

FIT SCORING (when resume provided):
- 50% responsibilities alignment
- 30% required experience match
- 20% industry/domain alignment
Score range: 0-100
If no resume: provide fit score of 0 or null

REQUIRED RESPONSE FORMAT - Every field must be populated:
{
  "intelligence_layer": {
    "job_quality_score": "Apply|Apply with caution|Skip — poor quality or low close rate",
    "quality_explanation": "MUST be 3-5 substantive sentences",
    "strategic_positioning": {
      "lead_with_strengths": ["MUST have 2-3 items", "NOT empty"],
      "gaps_and_mitigation": ["MUST have 2-3 items", "Be specific"],
      "emphasis_points": ["MUST have 2-3 items", "Actionable"],
      "avoid_points": ["MUST have 2-3 items", "Specific"],
      "positioning_strategy": "MUST be 1-2 substantive sentences",
      "positioning_rationale": ["WHY decision 1 - explain reasoning", "WHY decision 2 - explain reasoning", "WHY decision 3 - explain reasoning"]
    },
    "salary_market_context": {
      "typical_range": "MUST provide estimate (e.g., $150K-$200K)",
      "posted_comp_assessment": "not mentioned|low|fair|strong",
      "recommended_expectations": "MUST be specific and actionable",
      "market_competitiveness": "MUST be 2-3 substantive sentences",
      "risk_indicators": ["list specific risks"] or []
    },
    "apply_decision": {
      "recommendation": "Apply|Apply with caution|Skip",
      "reasoning": "MUST be 1-2 substantive sentences",
      "timing_guidance": "MUST be specific guidance"
    }
  },
  "company": "string from JD",
  "role_title": "string from JD",
  "company_context": "MUST be 2-3 substantive sentences about company, industry, stage",
  "role_overview": "MUST be 2-3 substantive sentences about role purpose and impact",
  "key_responsibilities": ["MUST have 4-6 main responsibilities from JD"],
  "required_skills": ["MUST have array of required skills/experience"],
  "preferred_skills": ["array of nice-to-have skills"] or [],
  "ats_keywords": ["MUST have 10-15 important keywords for ATS"],
  "fit_score": 85,
  "strengths": ["3-4 candidate strengths matching this role"] or [],
  "gaps": ["2-3 potential gaps or concerns"] or [],
  "strategic_positioning": "2-3 sentences on how to position candidate",
  "salary_info": "string if mentioned in JD, otherwise null",
  "interview_prep": {
    "narrative": "3-4 sentence story tailored to this role for framing alignment",
    "talking_points": [
      "bullet 1 - key talking point for recruiter screen",
      "bullet 2 - key talking point for recruiter screen",
      "bullet 3 - key talking point for recruiter screen",
      "bullet 4 - key talking point for recruiter screen"
    ],
    "gap_mitigation": [
      "concern + mitigation strategy 1",
      "concern + mitigation strategy 2",
      "concern + mitigation strategy 3 (if applicable)"
    ]
  },
  "outreach_intelligence": {
    "hiring_manager_likely_title": "The likely title of the hiring manager (e.g., 'VP of Talent Acquisition', 'Director of Engineering'). Infer from role level and department.",
    "hiring_manager_why_matters": "1-2 sentences explaining why reaching out to the hiring manager is valuable for THIS specific role.",
    "hiring_manager_linkedin_query": "A specific LinkedIn search query to find the hiring manager. Format: 'COMPANY_NAME AND (title1 OR title2) AND (keyword1 OR keyword2)'. Use the ACTUAL company name from the JD.",
    "hiring_manager_filter_instructions": "Specific instructions for filtering LinkedIn results (e.g., 'Filter by: Current employees only, Director level or above, recent activity').",
    "hiring_manager_outreach_template": "3-5 sentence personalized message to the hiring manager. MUST reference the ACTUAL role title, ACTUAL company name, and candidate's SPECIFIC experience.",
    "recruiter_likely_title": "The likely title of the recruiter (e.g., 'Technical Recruiter', 'Senior Talent Partner'). Match to role type.",
    "recruiter_why_matters": "1-2 sentences explaining why building a recruiter relationship matters for THIS role.",
    "recruiter_linkedin_query": "A specific LinkedIn search query to find recruiters. Format: 'COMPANY_NAME AND (recruiter OR talent acquisition OR people operations)'. Use the ACTUAL company name.",
    "recruiter_filter_instructions": "Specific instructions for filtering recruiter search results.",
    "recruiter_outreach_template": "3-5 sentence professional message to the recruiter. MUST reference the ACTUAL role title, ACTUAL company name, and candidate's relevant qualifications."
  },

CRITICAL OUTREACH TEMPLATE RULES (MANDATORY - NON-NEGOTIABLE):
1. PUNCTUATION: Use ONLY professional punctuation (periods, commas, semicolons, colons)
2. NO EM DASHES (—) OR EN DASHES (–) - use colons or periods instead
3. NO EXCLAMATION POINTS - they signal desperation
4. GROUNDING: Every claim must be traceable to the candidate's actual resume
5. NO GENERIC PHRASES: Avoid "I'm excited about this opportunity", "I'd love to chat", "I'd be a great fit", "I came across your posting"
6. SPECIFICITY: Reference actual companies, roles, metrics from the candidate's resume
7. ACTIVE VOICE: No passive voice constructions like "was led by" or "were managed by"
8. CONCISENESS: Each sentence under 30 words
9. CLEAR ASK: End with specific request (e.g., "Would you be open to a 20-minute call next week?")
10. VALUE-FIRST: Lead with what candidate brings, not flattery or generic interest
11. METRICS: Use specific numbers from resume when available ("led team of 10", "drove $2M revenue")
12. PROFESSIONAL TONE: Confident, direct, not pushy or desperate

GOOD OUTREACH EXAMPLE:
"Hi [Name], I'm reaching out about the Senior PM role. I've spent 5 years building B2B products at Uber and Spotify, most recently launching a marketplace feature that drove $12M ARR. Your focus on payment infrastructure aligns with my fintech background. Would you be open to a 20-minute call next week?"

BAD OUTREACH EXAMPLE (DO NOT EMULATE):
"Hi [Name]! I'm super excited about this opportunity—it seems like a great fit for my background. I'd love to chat about how I could contribute to the team!"

Violations to avoid: exclamation points, em dashes, generic phrases, no specifics, vague ask.
  "changes_summary": {
    "resume": {
      "summary_rationale": "1-2 sentences explaining HOW the resume should be tailored. Be SPECIFIC: reference actual companies/roles from the candidate's background and specific JD requirements.",
      "qualifications_rationale": "1-2 sentences explaining which experience to pull forward vs de-emphasize. Reference ACTUAL companies and roles from the resume.",
      "ats_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
      "positioning_statement": "One strategic sentence starting with 'This positions you as...'"
    },
    "cover_letter": {
      "opening_rationale": "1 sentence explaining the recommended opening angle and WHY.",
      "body_rationale": "1-2 sentences on what themes to emphasize and what to avoid mentioning.",
      "close_rationale": "1 sentence on recommended tone for the close.",
      "positioning_statement": "One strategic sentence starting with 'This frames you as...'"
    }
  },
  "reality_check": {
    "expected_applicants": "300-500+",
    "applicant_calculation": {
      "base": 200,
      "function_multiplier": 2.0,
      "function_name": "Product Management",
      "seniority_multiplier": 1.5,
      "seniority_level": "Senior",
      "geography_multiplier": 1.1,
      "geography": "Remote",
      "industry_multiplier": 1.0,
      "industry": "Tech",
      "total": 330
    },
    "response_rate": "3-5%",
    "function_context": "Full paragraph about layoffs/market for candidate's function",
    "industry_context": "Full paragraph about the target industry",
    "strategic_action": "Your move: Apply within 24 hours..."
  }
}

FRONTEND WIRING - REQUIRED JSON FIELDS:
After you have generated all analysis, interview prep, and outreach content, you MUST also return the interview_prep and outreach objects with the exact structure shown above.

Rules for interview_prep and outreach:
- NEVER return undefined, null, empty strings, or placeholder text
- Populate every field with real, substantive content
- talking_points must have 4-6 bullets for recruiter screen preparation
- gap_mitigation must address 2-3 specific concerns with mitigation strategies
- hiring_manager message should be warm, concise, and value-focused
- recruiter message should be professional and highlight relevant experience
- linkedin_help_text should provide clear, actionable search instructions

ABSOLUTE REQUIREMENTS:
1. Intelligence Layer MUST be complete - NO empty strings, NO empty required arrays
2. If data truly cannot be determined, provide reasoning (e.g., "Insufficient information in JD")
3. Use your knowledge to make reasonable estimates for salary ranges
4. Be direct and opinionated - avoid vague or generic advice
5. Every array marked "MUST have" cannot be empty
6. Your response must be ONLY valid JSON with no markdown formatting
7. Double-check that intelligence_layer has ALL required fields before responding
8. MUST include complete interview_prep and outreach objects
9. MUST include changes_summary with specific rationale for resume and cover letter tailoring
10. changes_summary must reference ACTUAL companies/roles from the candidate's resume - no generic placeholders
11. MUST include reality_check with calculated applicant estimates, function context, and strategic action
12. reality_check.applicant_calculation must show your work (all multipliers used)
13. NEVER fabricate statistics in reality_check - use ONLY the data provided in these instructions"""

    # Inject candidate state calibration if available
    situation = None
    if request.preferences:
        situation = request.preferences.get("situation")
    calibration_prompt = build_candidate_calibration_prompt(situation)
    if calibration_prompt:
        system_prompt += calibration_prompt

    # Build user message
    user_message = f"""Job Description:
Company: {request.company}
Role: {request.role_title}

{request.job_description}
"""
    
    if request.resume:
        user_message += f"\n\nCandidate Resume Data:\n{json.dumps(request.resume, indent=2)}"
    
    if request.preferences:
        user_message += f"\n\nCandidate Preferences:\n{json.dumps(request.preferences, indent=2)}"
    
    # Call Claude with higher token limit for comprehensive analysis
    response = call_claude(system_prompt, user_message, max_tokens=4096)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)

        # Validate and cleanup outreach templates if present
        if "outreach_intelligence" in parsed_data:
            outreach = parsed_data["outreach_intelligence"]

            # Validate hiring manager template
            if "hiring_manager_outreach_template" in outreach:
                hm_template = outreach["hiring_manager_outreach_template"]
                is_valid, errors = validate_outreach_template(hm_template, "hiring_manager")
                if not is_valid:
                    print(f"\n⚠️  JD Analysis - Hiring manager outreach has quality issues: {errors}")
                    # Cleanup common issues
                    outreach["hiring_manager_outreach_template"] = cleanup_outreach_template(hm_template)

            # Validate recruiter template
            if "recruiter_outreach_template" in outreach:
                rec_template = outreach["recruiter_outreach_template"]
                is_valid, errors = validate_outreach_template(rec_template, "recruiter")
                if not is_valid:
                    print(f"\n⚠️  JD Analysis - Recruiter outreach has quality issues: {errors}")
                    # Cleanup common issues
                    outreach["recruiter_outreach_template"] = cleanup_outreach_template(rec_template)

        return parsed_data
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")

def generate_resume_full_text(resume_output: dict) -> str:
    """
    Generate formatted full resume text from resume_output structure.
    This is a fallback if Claude doesn't return full_text.

    NOTE: Header (name, tagline, contact) is handled separately by the DOCX formatter.
    This function only generates the body content (Summary, Competencies, Experience, etc.)
    to avoid duplicate tagline appearing in the preview.
    """
    lines = []

    # NOTE: Headline/tagline is NOT included here - it's already in the document header
    # The add_header() function handles: Name, Tagline, Contact Info, Border

    # Summary
    summary = resume_output.get("summary", "")
    if summary:
        lines.append("SUMMARY")
        lines.append(summary)
        lines.append("")
    
    # Core Competencies (not "Key Qualifications")
    core_competencies = resume_output.get("core_competencies", []) or resume_output.get("key_qualifications", [])
    if core_competencies and len(core_competencies) > 0:
        lines.append("CORE COMPETENCIES")
        for comp in core_competencies:
            if comp:  # Skip empty strings
                lines.append(f"✓ {comp}")
        lines.append("")
    
    # Experience
    experience_sections = resume_output.get("experience_sections", []) or resume_output.get("experience", [])
    if experience_sections and len(experience_sections) > 0:
        lines.append("EXPERIENCE")
        lines.append("")
        for exp in experience_sections:
            company = exp.get("company", "")
            title = exp.get("title", "")
            location = exp.get("location", "")
            dates = exp.get("dates", "")
            overview = exp.get("overview", "") or exp.get("company_overview", "")

            # Company name (bold in Word, plain text here)
            if company:
                lines.append(company)

            # Job title
            if title:
                lines.append(title)

            # Location and dates on same line (right-aligned in Word)
            if location or dates:
                meta_parts = [location, dates] if location and dates else [location or dates]
                lines.append("    ".join(filter(None, meta_parts)))

            # Company overview (italic in Word)
            if overview:
                lines.append(f"Company Overview: {overview}")

            # Bullets
            bullets = exp.get("bullets", [])
            for bullet in bullets:
                if bullet:  # Skip empty strings
                    lines.append(f"• {bullet}")
            lines.append("")
    
    # Skills
    skills = resume_output.get("skills", [])
    if skills and len(skills) > 0:
        lines.append("SKILLS")
        lines.append(", ".join([s for s in skills if s]))  # Filter empty strings
        lines.append("")
    
    # Tools & Technologies
    tools = resume_output.get("tools_technologies", [])
    if tools and len(tools) > 0:
        lines.append("TOOLS & TECHNOLOGIES")
        lines.append(", ".join([t for t in tools if t]))  # Filter empty strings
        lines.append("")
    
    # Education
    education = resume_output.get("education", [])
    if education and len(education) > 0:
        lines.append("EDUCATION")
        for edu in education:
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            details = edu.get("details", "")
            
            if institution or degree:
                edu_parts = []
                if institution:
                    edu_parts.append(institution)
                if degree:
                    edu_parts.append(degree)
                lines.append(" | ".join(edu_parts))
                
            if details:
                lines.append(details)
        lines.append("")
    
    # Additional sections
    additional_sections = resume_output.get("additional_sections", [])
    for section in additional_sections:
        label = section.get("label", "")
        items = section.get("items", [])
        if label and items and len(items) > 0:
            lines.append(label.upper())
            for item in items:
                if item:  # Skip empty strings
                    lines.append(f"• {item}")
            lines.append("")
    
    result = "\n".join(lines).strip()
    
    # If result is empty or very short, return a helpful message
    if not result or len(result) < 50:
        return "Resume generation failed. Please try again or contact support."
    
    return result

@app.post("/api/documents/generate")
async def generate_documents(request: DocumentsGenerateRequest) -> Dict[str, Any]:
    """
    Generate tailored resume, cover letter, interview prep, and outreach content.
    Returns complete JSON for frontend consumption including full resume preview.
    """
    
    system_prompt = """You are a senior career strategist and resume writer for an ATS-optimized job application engine.

CRITICAL RULES - READ CAREFULLY:
1. Use ONLY information from the CANDIDATE RESUME DATA provided below
2. Do NOT fabricate any experience, metrics, achievements, companies, titles, or dates
3. Do NOT invent new roles, companies, or responsibilities that are not in the resume
4. Do NOT use any template data, sample data, or default placeholder content
5. Do NOT use Henry's background, or any pre-existing resume templates
6. If a field is missing from the candidate's resume (e.g., no education listed), use an empty array []
7. You MAY rewrite bullets and summaries to better match the JD language
8. The underlying FACTS must remain true to the candidate's actual uploaded resume
9. Tailor which roles and bullets you emphasize based on the JD
10. Optimize for ATS systems with keywords from the JD

THE CANDIDATE IS THE PERSON WHOSE RESUME WAS UPLOADED - NOT the user, NOT Henry, NOT a template.

You MUST return valid JSON with this EXACT structure. ALL fields are REQUIRED:

{
  "resume": {
    "summary": "3-4 line professional summary tailored to the JD",
    "skills": ["array of 8-12 skills reordered by JD relevance"],
    "experience": [
      {
        "company": "exact company name from resume",
        "title": "exact title from resume",
        "dates": "exact dates from resume",
        "industry": "industry if known or null",
        "bullets": ["array of 3-5 rewritten bullets using JD keywords"]
      }
    ]
  },
  "resume_output": {
    "headline": "Optional 1-line headline for top of resume (e.g., 'Senior Product Manager | B2B SaaS | Cross-Functional Leadership'), or null if not needed",
    "summary": "2-4 sentence tailored professional summary for this specific role. Must incorporate JD keywords naturally.",
    "core_competencies": [
      "Competency 1: concise skill phrase aligned to JD (e.g., 'High-Volume Interview Coordination & Scheduling')",
      "Competency 2: concise skill phrase aligned to JD (e.g., 'ATS Administration & Data Integrity')",
      "Competency 3: concise skill phrase aligned to JD",
      "Competency 4: concise skill phrase aligned to JD",
      "Competency 5: concise skill phrase aligned to JD",
      "Competency 6: concise skill phrase aligned to JD"
    ],
    "experience_sections": [
      {
        "company": "Company name exactly as it appears on candidate's resume",
        "title": "Role title exactly as it appears on candidate's resume",
        "location": "City, State or City, Country if available from resume, or null",
        "dates": "Date range exactly as on resume (e.g., 'Jan 2020 – Present' or '2019 – 2023')",
        "overview": "Brief 1-line company description if available (e.g., 'Multinational electricity & gas utility with 30,000 employees'), or null",
        "bullets": [
          "Accomplishment bullet 1: rewritten to emphasize JD-relevant skills, but based ONLY on real experience",
          "Accomplishment bullet 2: rewritten with metrics if available in original",
          "Accomplishment bullet 3: rewritten to highlight transferable skills",
          "Accomplishment bullet 4: additional if relevant (3-5 bullets per role)"
        ]
      }
    ],
    "skills": [
      "High-level skill 1 that is true and relevant to the role",
      "High-level skill 2",
      "High-level skill 3",
      "etc. (8-12 skills prioritized by JD relevance)"
    ],
    "tools_technologies": [
      "Tool or technology 1 from candidate's actual resume",
      "Tool or technology 2",
      "etc. (only include what's actually on the resume and relevant to JD)"
    ],
    "education": [
      {
        "institution": "School/University name from resume",
        "degree": "Degree type and field (e.g., 'Bachelor of Science in Computer Science')",
        "details": "Any relevant details: graduation year, honors, location, GPA if notable, or null"
      }
    ],
    "additional_sections": [
      {
        "label": "Certifications",
        "items": ["Certification 1 from resume", "Certification 2"]
      },
      {
        "label": "Languages",
        "items": ["Language 1", "Language 2"]
      }
    ],
    "ats_keywords": [
      "keyword1 from JD",
      "keyword2 from JD",
      "keyword3 from JD",
      "keyword4 from JD",
      "keyword5 from JD",
      "keyword6 from JD",
      "keyword7 from JD"
    ],
    "full_text": "Complete formatted resume BODY text (NOT including header/tagline - that is handled separately). Start with SUMMARY. Format: SUMMARY\\n[summary text]\\n\\nCORE COMPETENCIES\\n✓ [comp 1]\\n✓ [comp 2]\\n...\\n\\nEXPERIENCE\\n[Company]\\n[Title]\\n[Location] [Dates]\\n• [bullet 1]\\n• [bullet 2]\\n...\\n\\nSKILLS\\n[Category]: [skills as bullet-separated list]\\n\\nEDUCATION\\n[School]\\n[Degree]\\n• [detail 1]\\n• [detail 2]"
  },
  "cover_letter": {
    "greeting": "Dear Hiring Manager,",
    "opening": "Strong opening paragraph (2-3 sentences) that hooks with relevant experience",
    "body": "2-3 paragraphs connecting specific experience to role requirements. Include metrics where available.",
    "closing": "Closing paragraph with confident call to action",
    "full_text": "Complete cover letter as one string with proper paragraph breaks"
  },
  "changes_summary": {
    "resume": {
      "summary_rationale": "1-2 sentences explaining WHY you rewrote the summary. Be SPECIFIC about what JD theme you emphasized.",
      "qualifications_rationale": "1-2 sentences explaining what experience you pulled forward vs buried. Reference ACTUAL companies and roles.",
      "ats_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
      "positioning_statement": "One strategic sentence starting with 'This positions you as...'"
    },
    "cover_letter": {
      "opening_rationale": "1 sentence explaining WHY you led with this angle.",
      "body_rationale": "1-2 sentences on what you emphasized and avoided.",
      "close_rationale": "1 sentence on tone.",
      "positioning_statement": "One strategic sentence starting with 'This frames you as...'"
    }
  },
  "interview_prep": {
    "narrative": "3-4 sentence career story answering 'Tell me about yourself' that leads naturally to why this role is the next step.",
    "talking_points": [
      "Key talking point 1: specific achievement aligned to JD",
      "Key talking point 2: specific achievement aligned to JD",
      "Key talking point 3: specific achievement aligned to JD",
      "Key talking point 4: specific achievement aligned to JD"
    ],
    "gap_mitigation": [
      "Gap 1 + mitigation: 'If asked about [gap], emphasize [strategy]'",
      "Gap 2 + mitigation: 'If asked about [gap], emphasize [strategy]'",
      "Gap 3 + mitigation: 'If asked about [gap], emphasize [strategy]'"
    ]
  },
  "outreach": {
    "hiring_manager": "3-5 sentence LinkedIn message to the hiring manager. Professional, concise, personalized.",
    "recruiter": "3-5 sentence LinkedIn message to the recruiter. Friendly, efficient, signals serious interest.",
    "linkedin_help_text": "Step-by-step instructions for finding the right people on LinkedIn."
  }
}

CRITICAL OUTREACH TEMPLATE RULES (MANDATORY - NON-NEGOTIABLE):
1. PUNCTUATION: Use ONLY professional punctuation (periods, commas, semicolons, colons)
2. NO EM DASHES (—) OR EN DASHES (–) - use colons or periods instead
3. NO EXCLAMATION POINTS - they signal desperation
4. GROUNDING: Every claim must be traceable to the candidate's actual resume
5. NO GENERIC PHRASES: Avoid "I'm excited about this opportunity", "I'd love to chat", "I'd be a great fit", "I came across your posting", "I'm reaching out to express my interest"
6. SPECIFICITY: Reference actual companies, roles, metrics from the candidate's resume
7. ACTIVE VOICE: No passive voice constructions like "was led by" or "were managed by"
8. CONCISENESS: Each sentence under 30 words
9. CLEAR ASK: End with specific request (e.g., "Would you be open to a 20-minute call next week?")
10. VALUE-FIRST: Lead with what candidate brings, not flattery or generic interest
11. METRICS: Use specific numbers from resume when available ("led team of 10", "drove $2M revenue")
12. PROFESSIONAL TONE: Confident, direct, not pushy or desperate

GOOD OUTREACH EXAMPLE (Hiring Manager):
"Hi [Name], I'm reaching out about the Senior PM role. I've spent 5 years building B2B products at Uber and Spotify, most recently launching a marketplace feature that drove $12M ARR. Your focus on payment infrastructure aligns with my fintech background. Would you be open to a 20-minute call next week?"

BAD OUTREACH EXAMPLE (DO NOT EMULATE):
"Hi [Name]! I'm super excited about this opportunity—it seems like a great fit for my background. I'd love to chat about how I could contribute to the team!"

Violations to avoid: exclamation points, em dashes, generic phrases, no specifics, vague ask.

CRITICAL REQUIREMENTS FOR resume_output:
1. experience_sections MUST include ALL relevant roles from the candidate's resume
2. Each role MUST have 3-5 bullets rewritten to emphasize JD-relevant accomplishments
3. skills and tools_technologies MUST be subsets of what appears in the actual resume
4. education MUST reflect the candidate's actual education (use empty array [] if none provided)
5. additional_sections should include certifications, languages, or other relevant sections from resume (use empty array [] if none)
6. **full_text is MANDATORY** - MUST contain the complete formatted resume BODY with ALL sections (summary, qualifications, experience, skills, education) formatted exactly as specified above with proper line breaks (\\n). DO NOT include headline/tagline in full_text - start directly with SUMMARY
7. NEVER fabricate companies, titles, dates, metrics, or achievements
8. You MAY reword and emphasize, but underlying facts must be true

CRITICAL REQUIREMENTS FOR ALL FIELDS:
1. ALL fields must be populated - no empty strings, no null values (except where explicitly allowed like headline)
2. Use SPECIFIC examples from the candidate's actual resume
3. ats_keywords must be 5-7 keywords extracted DIRECTLY from the job description
4. cover_letter.full_text must be the complete letter with proper formatting
5. **resume_output.full_text is REQUIRED** - do not skip this field
5. If a section has no content (e.g., no certifications), use an empty array []

Your response must be ONLY valid JSON. No markdown code blocks. No explanatory text."""

    # Build comprehensive user message
    user_message = f"""Generate complete tailored application materials for this candidate and role.

CANDIDATE RESUME DATA:
{json.dumps(request.resume, indent=2)}

JOB DESCRIPTION ANALYSIS:
{json.dumps(request.jd_analysis, indent=2)}
"""
    
    if request.preferences:
        user_message += f"\n\nCANDIDATE PREFERENCES:\n{json.dumps(request.preferences, indent=2)}"

    # Add supplemental information from Strengthen Your Candidacy page
    if request.supplements and len(request.supplements) > 0:
        user_message += "\n\n=== ADDITIONAL CANDIDATE CONTEXT (from Strengthen Your Candidacy) ===\n"
        user_message += "The candidate provided the following additional context to address gaps in their application.\n"
        user_message += "INCORPORATE this information into the resume and cover letter where appropriate:\n\n"
        for supp in request.supplements:
            user_message += f"**Gap Area: {supp.gap_area}**\n"
            user_message += f"Question: {supp.question}\n"
            user_message += f"Candidate's Answer: {supp.answer}\n\n"
        user_message += "Use this information to strengthen the resume summary, relevant experience bullets, and cover letter body.\n"
        user_message += "Do NOT fabricate beyond what the candidate stated, but DO weave in this context naturally.\n"

    user_message += """

REQUIREMENTS:
1. resume_output.experience_sections must include all relevant roles with rewritten bullets
2. resume_output.skills and tools_technologies must come from the actual resume
3. resume_output.education must reflect actual education from the resume
4. Maintain all factual accuracy - NO fabrication
5. Cover letter should be professional, concise, and ready to send
6. Interview prep should give actionable guidance
7. Outreach messages should be ready to copy/paste
8. If supplements were provided, incorporate that context into the resume and cover letter

Generate the complete JSON response with ALL required fields populated."""
    
    # Call Claude with longer token limit for comprehensive response
    response = call_claude(system_prompt, user_message, max_tokens=8000)
    
    # DEBUG: Print raw Claude response to console
    print("\n" + "="*60)
    print("DEBUG: Raw Claude response from /api/documents/generate:")
    print("="*60)
    print(response)
    print("="*60 + "\n")
    
    # Parse JSON response
    try:
        cleaned = response.strip()
        # Remove markdown code blocks if present
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        
        parsed_data = json.loads(cleaned)
        
        # Ensure resume_output has all required fields with fallbacks
        if "resume_output" not in parsed_data:
            parsed_data["resume_output"] = {}
        
        resume_output = parsed_data["resume_output"]
        resume_data = parsed_data.get("resume", {})
        
        # Ensure all resume_output fields exist
        if "headline" not in resume_output:
            resume_output["headline"] = None
        if "summary" not in resume_output:
            resume_output["summary"] = resume_data.get("summary", "")
        if "core_competencies" not in resume_output:
            # Fall back to key_qualifications if present, otherwise skills
            resume_output["core_competencies"] = resume_output.get("key_qualifications", resume_data.get("skills", [])[:6])
        if "experience_sections" not in resume_output:
            # Convert from resume.experience if available
            resume_output["experience_sections"] = []
            for exp in resume_data.get("experience", []):
                resume_output["experience_sections"].append({
                    "company": exp.get("company", ""),
                    "title": exp.get("title", ""),
                    "location": exp.get("location", ""),
                    "dates": exp.get("dates", ""),
                    "overview": exp.get("overview", "") or exp.get("company_overview", ""),
                    "bullets": exp.get("bullets", [])
                })
        if "skills" not in resume_output:
            resume_output["skills"] = resume_data.get("skills", [])
        if "tools_technologies" not in resume_output:
            resume_output["tools_technologies"] = []
        if "education" not in resume_output:
            resume_output["education"] = []
        if "additional_sections" not in resume_output:
            resume_output["additional_sections"] = []
        if "ats_keywords" not in resume_output:
            resume_output["ats_keywords"] = parsed_data.get("changes_summary", {}).get("resume", {}).get("ats_keywords", [])
        
        # Generate full_text if missing
        if "full_text" not in resume_output or not resume_output["full_text"]:
            print("\n⚠️  WARNING: full_text missing from Claude response, generating fallback...")
            print(f"resume_output keys: {list(resume_output.keys())}")
            print(f"experience_sections count: {len(resume_output.get('experience_sections', []))}")
            print(f"summary exists: {bool(resume_output.get('summary'))}")
            resume_output["full_text"] = generate_resume_full_text(resume_output)
            print(f"Generated full_text length: {len(resume_output['full_text'])} characters")
            print(f"Generated full_text preview: {resume_output['full_text'][:200]}...")
        
        # Ensure other required top-level keys exist
        if "interview_prep" not in parsed_data:
            parsed_data["interview_prep"] = {
                "narrative": "Review the job description and prepare to discuss how your experience aligns with their requirements.",
                "talking_points": ["Highlight relevant experience", "Discuss key achievements", "Show enthusiasm for the role"],
                "gap_mitigation": ["Address any gaps by emphasizing transferable skills and willingness to learn"]
            }
        
        if "outreach" not in parsed_data:
            company = request.jd_analysis.get("company", "the company")
            role = request.jd_analysis.get("role_title", "this role")
            parsed_data["outreach"] = {
                "hiring_manager": f"Hi, I recently applied for the {role} position at {company} and wanted to introduce myself. My background aligns well with what you're building. I'd welcome the chance to discuss how I can contribute to your team.",
                "recruiter": f"Hi, I just submitted my application for the {role} role at {company}. I believe I'd be a strong fit. Happy to provide any additional information that would be helpful.",
                "linkedin_help_text": f"1) Search LinkedIn for '{company}' employees, 2) Filter by title keywords like 'Hiring Manager', 'Director', or 'Recruiter', 3) Send a personalized connection request with the message above."
            }
        
        # Validate and cleanup outreach templates
        outreach = parsed_data.get("outreach", {})
        
        # Validate hiring manager template
        if "hiring_manager" in outreach:
            hm_template = outreach["hiring_manager"]
            is_valid, errors = validate_outreach_template(hm_template, "hiring_manager")
            if not is_valid:
                print(f"\n⚠️  WARNING: Hiring manager outreach has quality issues: {errors}")
                # Cleanup common issues
                outreach["hiring_manager"] = cleanup_outreach_template(hm_template)
        
        # Validate recruiter template
        if "recruiter" in outreach:
            rec_template = outreach["recruiter"]
            is_valid, errors = validate_outreach_template(rec_template, "recruiter")
            if not is_valid:
                print(f"\n⚠️  WARNING: Recruiter outreach has quality issues: {errors}")
                # Cleanup common issues
                outreach["recruiter"] = cleanup_outreach_template(rec_template)
        
        if "changes_summary" not in parsed_data:
            parsed_data["changes_summary"] = {
                "resume": {
                    "summary_rationale": "Tailored summary to emphasize skills most relevant to the job requirements.",
                    "qualifications_rationale": "Prioritized experience that best matches the role's key requirements.",
                    "ats_keywords": request.jd_analysis.get("ats_keywords", [])[:5] if request.jd_analysis.get("ats_keywords") else [],
                    "positioning_statement": "This positions you as a strong candidate for the role."
                },
                "cover_letter": {
                    "opening_rationale": "Led with your most relevant experience to capture attention.",
                    "body_rationale": "Emphasized achievements that directly address the job requirements.",
                    "close_rationale": "Confident closing that invites next steps.",
                    "positioning_statement": "This frames you as a qualified candidate ready to contribute."
                }
            }
        
        # DEBUG: Print final parsed data
        print("\n" + "="*60)
        print("DEBUG: Final parsed_data being returned:")
        print("="*60)
        print(json.dumps(parsed_data, indent=2))
        print("="*60 + "\n")
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON PARSE ERROR: {str(e)}")
        print(f"Raw response was: {response[:1000]}...")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")

# ============================================================================
# MVP+1 FEATURE ENDPOINTS
# ============================================================================

@app.post("/api/tasks/prioritize")
async def prioritize_tasks(request: TasksPrioritizeRequest) -> TasksPrioritizeResponse:
    """
    FEATURE 1: Daily Command Center
    
    Analyzes applications and creates prioritized task list for the day.
    Uses Claude to determine highest-leverage actions based on:
    - Fit score
    - Recency of activity
    - Current stage
    - Whether follow-up is needed
    
    Returns 3-7 actionable tasks with priority, reason, and message stubs.
    """
    
    system_prompt = """You are a job search strategist helping prioritize daily activities.

Analyze the provided applications and create a focused task list for today.

TASK TYPES:
- "apply": Apply to this role (for high-fit roles not yet applied)
- "follow_up": Send a follow-up message (for pending applications)
- "outreach": Reach out to network contacts about this role

PRIORITIZATION LOGIC:
1. High fit score (70+) + recent activity = high priority
2. Applied but no follow-up in 5-7+ days = follow-up task
3. Screen/onsite stage without recent contact = follow-up task
4. High fit without outreach = outreach task

CONSTRAINTS:
- Return 3-7 tasks maximum (focus on highest leverage)
- Priority 1 = critical, 2 = important, 3 = nice-to-have
- Provide specific, actionable reasons
- Include brief message stubs (1-2 sentences) where helpful

Return valid JSON:
{
  "tasks": [
    {
      "type": "apply|follow_up|outreach",
      "application_id": "string",
      "priority": 1-3,
      "reason": "string explaining why this is important",
      "suggested_message_stub": "string or null (brief message template)"
    }
  ]
}

Your response must be ONLY valid JSON."""

    # Build user message with application data
    user_message = f"""Today's date: {request.today}

Applications to analyze:
{json.dumps([app.model_dump() for app in request.applications], indent=2)}

Create a prioritized task list focusing on the highest-leverage activities."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=3000)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return TasksPrioritizeResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


@app.post("/api/outcomes/log")
async def log_outcome(request: OutcomeLogRequest) -> Dict[str, str]:
    """
    FEATURE 2: Learning/Feedback Loop (Part 1)
    
    Logs outcome data for an application.
    Stores in simple in-memory store for pattern analysis.
    
    In production, replace with proper database persistence.
    """
    
    # Add to in-memory store
    outcome_entry = {
        "application_id": request.application_id,
        "stage": request.stage,
        "outcome": request.outcome,
        "date": request.date,
        "logged_at": datetime.utcnow().isoformat()
    }
    
    outcomes_store.append(outcome_entry)
    
    return {
        "status": "success",
        "message": f"Outcome logged for application {request.application_id}",
        "total_outcomes": len(outcomes_store)
    }


@app.post("/api/strategy/review")
async def review_strategy(request: StrategyReviewRequest) -> StrategyReviewResponse:
    """
    FEATURE 2: Learning/Feedback Loop (Part 2)
    
    Analyzes patterns in applications and outcomes to identify:
    - What's working (successful patterns)
    - What's not working (unsuccessful patterns)
    - Concrete strategy shifts to improve results
    
    Returns 3-5 insights and actionable recommendations.
    """
    
    system_prompt = """You are a job search analyst providing strategic feedback.

Analyze application data and outcomes to identify patterns and provide actionable recommendations.

ANALYSIS FRAMEWORK:
1. Success patterns: What's working? (roles, companies, approaches that advance)
2. Challenge patterns: What's not working? (rejections, no responses, common gaps)
3. Fit score correlation: Do higher fit scores lead to better outcomes?
4. Stage progression: Where do applications typically stall?
5. Timing patterns: Response rates based on follow-up timing

INSIGHTS (3-5 observations):
- Data-driven patterns you observe
- Be specific and evidence-based
- Focus on actionable insights

RECOMMENDATIONS (3-5 actions):
- Concrete strategy shifts
- Specific next steps
- Prioritized by impact

Return valid JSON:
{
  "insights": [
    "Insight 1: Specific pattern observed",
    "Insight 2: Another pattern",
    ...
  ],
  "recommendations": [
    "Recommendation 1: Specific action to take",
    "Recommendation 2: Another action",
    ...
  ]
}

Your response must be ONLY valid JSON."""

    # Build comprehensive user message
    user_message = f"""Analyze this job search data:

APPLICATIONS:
{json.dumps(request.applications, indent=2)}

OUTCOMES:
{json.dumps(request.outcomes, indent=2)}

Provide strategic insights and recommendations to improve results."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=3000)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return StrategyReviewResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


@app.post("/api/network/recommend")
async def recommend_contacts(request: NetworkRecommendRequest) -> NetworkRecommendResponse:
    """
    FEATURE 3: Network Engine (Lite)
    
    Analyzes candidate's network contacts and recommends 3-10 best people
    to reach out to for a specific role/company.
    
    Considers:
    - Relationship strength and type
    - Current company/role relevance
    - Potential to provide referral, intro, or intel
    
    Returns prioritized list with outreach reasoning and message stubs.
    """
    
    system_prompt = """You are a networking strategist for job searches.

Analyze the candidate's network contacts and recommend the best people to reach out to
for this specific target role and company.

RANKING CRITERIA:
1. Current company match: Works at target company = highest priority
2. Role relevance: Similar function or has hiring influence
3. Relationship strength: Former colleague > friend > weak connection
4. Potential help type:
   - Direct referral (works there now)
   - Warm introduction (knows someone there)
   - Industry intel (similar company/role)
   - General advice (mentorship)

PRIORITIES:
- Priority 1: Direct connection to target company or hiring manager
- Priority 2: Strong relationship + relevant role/industry
- Priority 3: Weak connection but potentially helpful

MESSAGE STUBS:
- Personalized based on relationship
- Clear ask (referral, intro, advice, intel)
- Brief and respectful of their time
- 1-2 sentences only

Return 3-10 recommendations, ranked by potential impact.

Return valid JSON:
{
  "recommendations": [
    {
      "name": "string",
      "company": "string",
      "title": "string",
      "relationship": "string",
      "priority": 1-3,
      "reason": "Why this person is valuable to contact",
      "suggested_message_stub": "Brief personalized message template"
    }
  ]
}

Your response must be ONLY valid JSON."""

    # Build user message
    user_message = f"""Target Role: {request.role_title}
Target Company: {request.company}

Network Contacts:
{json.dumps([contact.model_dump() for contact in request.contacts], indent=2)}

Recommend the best contacts to reach out to and provide personalized outreach stubs."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=3000)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return NetworkRecommendResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")

# ============================================================================
# INTERVIEW INTELLIGENCE ENDPOINTS
# ============================================================================

@app.post("/api/interview/parse")
async def parse_interview(request: InterviewParseRequest) -> InterviewParseResponse:
    """
    FEATURE 4A: Interview Intelligence - Parse & Classify Questions
    
    Extracts interview questions from transcript and classifies them by:
    - Type (behavioral, technical, leadership, competency, wildcard)
    - Competency tag (e.g., product sense, stakeholder management)
    - Difficulty level (1-5)
    
    Also identifies themes and potential issues in the interview.
    """
    
    system_prompt = """You are an interview analysis expert specializing in talent acquisition.

Analyze the interview transcript and extract all questions that were asked.
Classify each question using modern hiring competency frameworks.

QUESTION TYPES:
- behavioral: Past behavior questions (Tell me about a time...)
- technical: Skills assessment, problem-solving, domain knowledge
- leadership: People management, influence, decision-making
- competency: Role-specific skills (e.g., data analysis, stakeholder mgmt)
- wildcard: Unusual, creative, or off-script questions

COMPETENCY TAGS (use standard hiring framework terms):
- Product Sense, Strategic Thinking, Data Fluency
- Stakeholder Management, Cross-Functional Collaboration
- Team Leadership, Coaching & Development, Conflict Resolution
- Process Design, Operational Excellence, Metrics & Analytics
- Communication, Presentation Skills, Executive Presence
- Adaptability, Learning Agility, Problem Solving
- Influence, Negotiation, Change Management
- Technical Expertise, Domain Knowledge

DIFFICULTY SCORING (1-5):
1 = Entry level, straightforward
2 = Mid-level, requires some depth
3 = Senior level, multi-faceted
4 = Executive level, strategic thinking required
5 = Extremely challenging, tests edge cases

THEMES:
Identify 3-5 overarching themes across all questions (e.g., "focus on scaling experience", 
"heavy emphasis on metrics", "testing cultural fit for autonomous environment")

WARNINGS:
Flag issues like:
- Vague or poorly structured questions
- Leading questions
- Potential bias indicators
- Missing critical competencies for the role
- Overemphasis on one area

CRITICAL RULES:
- Extract ONLY questions that were actually asked
- Do NOT fabricate questions
- If a question is unclear in transcript, note it in warnings
- Be precise with competency tagging

Return valid JSON:
{
  "questions": [
    {
      "question": "exact question as asked",
      "type": "behavioral|technical|leadership|competency|wildcard",
      "competency_tag": "specific competency from framework",
      "difficulty": 1-5
    }
  ],
  "themes": ["theme 1", "theme 2", ...],
  "warnings": ["warning 1 if any", ...]
}

Your response must be ONLY valid JSON."""

    # Build user message
    user_message = f"""Role: {request.role_title}
Company: {request.company}

Interview Transcript:
{request.transcript_text}
"""

    if request.jd_analysis:
        user_message += f"\n\nJob Description Analysis (for context):\n{json.dumps(request.jd_analysis, indent=2)}"

    user_message += "\n\nExtract and classify all interview questions."

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=3000)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return InterviewParseResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


@app.post("/api/interview/feedback")
async def interview_feedback(request: InterviewFeedbackRequest) -> InterviewFeedbackResponse:
    """
    FEATURE 4B: Interview Intelligence - Performance Feedback
    
    Analyzes candidate's interview performance across multiple dimensions:
    - Overall scoring (1-100)
    - Strengths and improvement areas
    - Delivery feedback (tone, pacing, clarity, structure)
    - Specific, actionable recommendations
    
    Uses STAR framework for behavioral questions and provides concrete examples.
    """
    
    system_prompt = """You are a senior executive coach specializing in interview preparation.

Analyze the candidate's interview performance and provide constructive, actionable feedback.

SCORING FRAMEWORK (1-100):
90-100: Exceptional - compelling answers with strong examples and metrics
80-89: Strong - good structure, clear communication, solid examples
70-79: Good - adequate answers but missing some depth or polish
60-69: Fair - needs improvement in structure, examples, or clarity
50-59: Weak - significant gaps in content or delivery
Below 50: Poor - major issues requiring substantial work

STRENGTHS (identify 3-5):
What the candidate did well. Be specific:
- "Used clear STAR structure in behavioral questions"
- "Demonstrated quantitative impact with specific metrics"
- "Showed authentic passion for the company mission"

AREAS FOR IMPROVEMENT (identify 3-5):
What needs work. Be constructive and specific:
- "Behavioral answers lacked concrete metrics or outcomes"
- "Tended to ramble - answers could be 30% shorter"
- "Missed opportunities to connect experience to role requirements"

DELIVERY FEEDBACK:
Tone: Professional, conversational, enthusiastic? Any concerns?
Pacing: Too fast, too slow, or well-modulated? Pauses for emphasis?
Clarity: Easy to follow? Jargon-heavy? Clear structure?
Structure: Organized responses? Answered the actual question? Stayed on topic?

RECOMMENDATIONS (3-6 specific actions):
Highly actionable, prioritized advice:
- "Practice the 'SBO' framework: Situation-Behavior-Outcome in 90 seconds"
- "Prepare 3 metrics-driven stories that demonstrate [specific competency]"
- "Work on ending answers with 'So that's why I'm excited about this opportunity'"

CRITICAL RULES:
- Base feedback ONLY on what's in the transcript
- Do NOT fabricate answers that weren't given
- Be supportive but direct - candidates need honest feedback
- Provide phrasing examples for improvements
- Consider the role requirements when evaluating fit
- Use STAR framework (Situation-Task-Action-Result) as evaluation lens

Return valid JSON:
{
  "overall_score": 75,
  "strengths": ["strength 1", "strength 2", ...],
  "areas_for_improvement": ["area 1", "area 2", ...],
  "delivery_feedback": {
    "tone": "analysis and assessment",
    "pacing": "analysis and assessment",
    "clarity": "analysis and assessment",
    "structure": "analysis and assessment"
  },
  "recommendations": ["action 1", "action 2", ...]
}

Your response must be ONLY valid JSON."""

    # Build user message with questions for context
    user_message = f"""Role: {request.role_title}
Company: {request.company}

Questions Asked:
{json.dumps([q.model_dump() for q in request.questions], indent=2)}

Interview Transcript:
{request.transcript_text}

Provide comprehensive performance feedback focusing on what was actually said."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=4096)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return InterviewFeedbackResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


@app.post("/api/interview/thank_you")
async def generate_thank_you(request: ThankYouRequest) -> ThankYouResponse:
    """
    FEATURE 4C: Interview Intelligence - Thank You Email
    
    Generates a professional, personalized thank-you email based on:
    - Actual conversation topics from interview
    - Role requirements and company context
    - Candidate's specific examples and experiences discussed
    
    Email is concise (3-4 paragraphs) with modern professional tone.
    """
    
    system_prompt = """You are a professional communication coach specializing in post-interview follow-ups.

Generate a thank-you email that is:
- Professional but warm and genuine
- 3-4 paragraphs maximum
- References specific topics discussed in interview
- Reiterates genuine interest and fit
- Modern tone (not overly formal, no corporate jargon)

STRUCTURE:
Paragraph 1: Thank them and reference something specific from conversation
Paragraph 2: Brief reinforcement of 1-2 key qualifications discussed
Paragraph 3: Express enthusiasm and next steps

DO NOT:
- Fabricate topics that weren't discussed
- Be overly effusive or desperate
- Use corporate buzzwords excessively
- Make it longer than 4 paragraphs
- Repeat the entire conversation

DO:
- Reference actual conversation points
- Show you were listening and engaged
- Reinforce fit naturally
- Keep it concise and respectful of their time
- End with clear next step or openness to questions

TONE EXAMPLES:
Good: "I really enjoyed our conversation about scaling recruiting operations during hypergrowth."
Bad: "It was an absolute pleasure to have the distinct honor of speaking with you..."

Good: "The challenge you mentioned around competing for technical talent in SF resonates with my experience at Spotify."
Bad: "I am extremely passionate about leveraging synergies to optimize talent acquisition pipelines."

Return valid JSON:
{
  "subject": "Thank you - [Role Title] conversation",
  "body": "Full email text, 3-4 paragraphs",
  "key_points_used": ["point 1", "point 2", "point 3"]
}

Your response must be ONLY valid JSON."""

    # Build user message
    interviewer = request.interviewer_name or "the hiring team"
    
    user_message = f"""Role: {request.role_title}
Company: {request.company}
Interviewer: {interviewer}

Interview Transcript:
{request.transcript_text}
"""

    if request.jd_analysis:
        user_message += f"\n\nRole Context:\n{json.dumps(request.jd_analysis, indent=2)}"

    user_message += "\n\nGenerate a professional thank-you email that references actual conversation topics."

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=2000)
    
    # Parse JSON response
    try:
        if response.strip().startswith("```"):
            response = response.strip().split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        
        parsed_data = json.loads(response)
        return ThankYouResponse(**parsed_data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


# ============================================================================
# INTERVIEW INTELLIGENCE ENDPOINTS
# ============================================================================

def format_resume_for_prompt(resume_json: Dict[str, Any]) -> str:
    """Format resume JSON into readable text for prompts"""
    lines = []

    # Name and contact
    if resume_json.get('full_name'):
        lines.append(f"Name: {resume_json['full_name']}")
    if resume_json.get('current_title'):
        lines.append(f"Current Title: {resume_json['current_title']}")

    # Summary
    if resume_json.get('summary'):
        lines.append(f"\nSummary:\n{resume_json['summary']}")

    # Experience
    experience = resume_json.get('experience', [])
    if experience:
        lines.append("\nExperience:")
        for exp in experience:
            company = exp.get('company', '')
            title = exp.get('title', '')
            dates = exp.get('dates', '')
            lines.append(f"\n{company} - {title} ({dates})")
            for bullet in exp.get('bullets', []):
                lines.append(f"  • {bullet}")

    # Skills
    skills = resume_json.get('skills', [])
    if skills:
        if isinstance(skills, list):
            lines.append(f"\nSkills: {', '.join(skills)}")
        elif isinstance(skills, dict):
            lines.append("\nSkills:")
            for category, skill_list in skills.items():
                lines.append(f"  {category}: {', '.join(skill_list)}")

    # Core competencies
    competencies = resume_json.get('core_competencies', [])
    if competencies:
        lines.append(f"\nCore Competencies: {', '.join(competencies)}")

    # Education
    education = resume_json.get('education')
    if education:
        lines.append(f"\nEducation: {education}")

    return '\n'.join(lines)


@app.post("/api/interview-prep/generate", response_model=InterviewPrepResponse)
async def generate_interview_prep(request: InterviewPrepRequest):
    """
    INTERVIEW INTELLIGENCE: Generate stage-specific interview prep

    Generates comprehensive prep materials for either:
    - recruiter_screen: Focus on logistics, salary, timeline, red flags
    - hiring_manager: Focus on competencies, STAR stories, technical depth

    All content is grounded in the candidate's actual resume - NO fabrication.
    """

    resume_text = format_resume_for_prompt(request.resume_json)
    fit_analysis_text = json.dumps(request.jd_analysis, indent=2) if request.jd_analysis else "No fit analysis available"

    if request.interview_stage == "recruiter_screen":
        system_prompt = """You are generating pre-interview intelligence for a recruiter screen.

Generate structured prep covering:
1. interview_overview (2-3 sentences explaining recruiter's goals)
2. key_talking_points (4-6 bullets, must reference actual achievements from resume)
3. red_flag_mitigation (2-3 items addressing gaps, job hopping, overqualification - each with "flag" and "mitigation")
4. likely_questions (5-7 questions recruiter will ask about experience, motivation, and fit)
   DO NOT include salary/compensation questions - those are covered separately in compensation_expectations.
   IMPORTANT: Each must be an object with BOTH "question" AND "suggested_answer" fields.
   Format: {"question": "Why are you interested in this role?", "suggested_answer": "I'm drawn to this role because... [2-4 sentences using specific details from resume]"}
5. questions_to_ask (3-4 strategic questions with "question" and "why")
6. compensation_expectations (2-4 sentences providing a specific scripted response the candidate can use when asked "What are your salary expectations?" - include a realistic salary range based on the role level and their experience, with framing language like "Based on my research and experience level, I'm targeting..." or "I'm flexible but looking in the range of...")
7. timeline_strategy (1-2 sentences on how to respond about availability and start date)

CRITICAL RULES:
- Use ONLY information from the candidate's actual resume
- Include specific metrics and achievements from resume
- Be direct about red flags—provide mitigation strategies
- No generic advice—everything must be tailored to this candidate and role

Return ONLY a valid JSON object with the structure above. No markdown, no preamble."""
    else:  # hiring_manager
        system_prompt = """You are generating pre-interview intelligence for a hiring manager interview.

Generate structured prep covering:
1. interview_overview (2-3 sentences explaining hiring manager's goals)
2. strengths_to_emphasize (3-4 bullets tied to job requirements, must reference resume)
3. gaps_to_mitigate (2-3 bullets with credible workarounds)
4. star_examples (3-4 behavioral stories using STAR format, must be from actual resume)
   Format each as: {"competency": "string", "situation": "string", "task": "string", "action": "string", "result": "string"}
5. likely_questions (5-7 technical/functional questions)
   IMPORTANT: Each must be an object with BOTH "question" AND "suggested_answer" fields.
   Format: {"question": "Tell me about a time you led a cross-functional project", "suggested_answer": "At [Company], I led... [2-4 sentences using specific details from resume]"}
6. questions_to_ask (4-5 strategic questions with "question" and "why")
7. closing_strategy (1-2 sentences on how to close strong)

STAR EXAMPLES RULES:
- Every example must come from candidate's actual work history
- Include specific metrics, timeframes, and outcomes from resume
- Map each example to a key competency from the job description
- Use concrete details, not generic scenarios

Return ONLY a valid JSON object with the structure above. No markdown, no preamble."""

    user_message = f"""CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
Company: {request.company}
Role: {request.role_title}

{request.job_description}

FIT ANALYSIS:
{fit_analysis_text}

Generate the interview prep now."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=4000)

    # Parse JSON response
    try:
        cleaned = clean_claude_json(response)
        prep_content = json.loads(cleaned)

        return InterviewPrepResponse(
            interview_stage=request.interview_stage,
            prep_content=prep_content
        )
    except (json.JSONDecodeError, Exception) as e:
        print(f"🔥 Failed to parse interview prep response: {e}")
        print(f"Raw response: {response[:500]}")
        raise HTTPException(status_code=500, detail=f"Failed to parse interview prep: {str(e)}")


@app.post("/api/interview-prep/intro-sell/generate", response_model=IntroSellTemplateResponse)
async def generate_intro_sell_template(request: IntroSellTemplateRequest):
    """
    INTERVIEW INTELLIGENCE: Generate customized 60-90 second intro sell template

    Creates a structured template the candidate can practice:
    1. Current Role + Impact (quantified)
    2. Previous Role + Relevant Achievement
    3. Why You're Here (connection to target role)
    4. What You're Looking For (optional)

    Word count target: 100-150 words
    """

    resume_text = format_resume_for_prompt(request.resume_json)

    system_prompt = """Generate a customized 60-90 second intro sell template for this candidate.

STRUCTURE (MANDATORY):
1. Current Role + Impact (1-2 sentences, include quantified achievement)
2. Previous Role + Relevant Achievement (1-2 sentences)
3. Why You're Here (1 sentence connecting background to job)
4. What You're Looking For (1 sentence, optional)

RULES:
- Total word count: 100-150 words
- Use ONLY information from resume
- Include at least one quantified metric
- No college/education unless directly relevant
- No generic filler phrases
- End with confidence, not a question

OUTPUT FORMAT:
Return JSON:
{
    "template": "Full intro sell text",
    "word_count": integer,
    "coaching_note": "2-3 sentences on what to emphasize"
}

No markdown, no preamble."""

    user_message = f"""CANDIDATE RESUME:
{resume_text}

TARGET ROLE:
Company: {request.company}
Role: {request.role_title}

JOB DESCRIPTION:
{request.job_description}

Generate the intro sell template now."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=2000)

    # Parse JSON response
    try:
        cleaned = clean_claude_json(response)
        parsed = json.loads(cleaned)

        return IntroSellTemplateResponse(
            template=parsed.get("template", ""),
            word_count=parsed.get("word_count", len(parsed.get("template", "").split())),
            coaching_note=parsed.get("coaching_note", "")
        )
    except (json.JSONDecodeError, Exception) as e:
        print(f"🔥 Failed to parse intro sell template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse intro sell template: {str(e)}")


@app.post("/api/interview-prep/intro-sell/feedback", response_model=IntroSellFeedbackResponse)
async def analyze_intro_sell(request: IntroSellFeedbackRequest):
    """
    INTERVIEW INTELLIGENCE: Analyze candidate's intro sell attempt

    Provides structured feedback on:
    - Content (did they lead with impact, include metrics?)
    - Structure (word count, formula adherence)
    - Tone (confident vs tentative, specific vs vague)

    Returns scores, specific feedback, and a revised version.
    """

    resume_text = format_resume_for_prompt(request.resume_json)

    # Count words and estimate time
    word_count = len(request.candidate_version.split())
    estimated_time_seconds = int((word_count / 140) * 60)  # 140 WPM average

    system_prompt = """Analyze this candidate's 60-90 second intro sell attempt.

Provide structured feedback:

CONTENT (1-10):
- Did they lead with current role and impact?
- Did they include quantified achievement?
- Did they connect background to target role?
- Did they avoid irrelevant details?

STRUCTURE (1-10):
- Word count: 100-150 = 10 points, 151-200 = 7 points, 200+ = 5 points
- Did they follow formula (current → past → why here)?
- Did they end with statement, not question?

TONE (1-10):
- Confident language vs. tentative
- Specific vs. vague
- Active voice vs. passive

OUTPUT FORMAT:
Return JSON:
{
    "overall_score": float (average of three scores),
    "content_score": integer 1-10,
    "structure_score": integer 1-10,
    "tone_score": integer 1-10,
    "strengths": ["string", "string"],
    "opportunities": ["string", "string"],
    "revised_version": "string (tightened to 100-150 words)",
    "coaching_note": "string (what to practice next)"
}

REVISED VERSION RULES:
- Must be 100-150 words
- Must use only information from candidate's actual resume
- Tighten weak sections, cut irrelevant details
- End confidently

No markdown, no preamble."""

    user_message = f"""CANDIDATE'S VERSION:
{request.candidate_version}

CANDIDATE RESUME (for reference):
{resume_text}

TARGET ROLE:
Company: {request.company}
Role: {request.role_title}

JOB DESCRIPTION (for reference):
{request.job_description}

Analyze the intro sell attempt now."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=2000)

    # Parse JSON response
    try:
        cleaned = clean_claude_json(response)
        feedback = json.loads(cleaned)

        return IntroSellFeedbackResponse(
            overall_score=feedback.get("overall_score", 5.0),
            content_score=feedback.get("content_score", 5),
            structure_score=feedback.get("structure_score", 5),
            tone_score=feedback.get("tone_score", 5),
            word_count=word_count,
            estimated_time_seconds=estimated_time_seconds,
            strengths=feedback.get("strengths", []),
            opportunities=feedback.get("opportunities", []),
            revised_version=feedback.get("revised_version", ""),
            coaching_note=feedback.get("coaching_note", "")
        )
    except (json.JSONDecodeError, Exception) as e:
        print(f"🔥 Failed to parse intro sell feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse intro sell feedback: {str(e)}")


@app.post("/api/interview-prep/debrief", response_model=InterviewDebriefResponse)
async def create_interview_debrief(request: InterviewDebriefRequest):
    """
    INTERVIEW INTELLIGENCE: Post-interview debrief analysis

    Analyzes interview performance from either:
    - Transcript text (if candidate recorded/transcribed)
    - Typed responses (questions asked, strong/weak answers)

    Returns comprehensive feedback, coaching points, and a thank-you email.
    """

    resume_text = format_resume_for_prompt(request.resume_json)

    # Build interview content from available sources
    interview_content_parts = []

    # Include transcript if provided (primary source for detailed analysis)
    if request.transcript_text:
        interview_content_parts.append(f"INTERVIEW TRANSCRIPT:\n{request.transcript_text}")

    # Include typed responses if provided (candidate's self-assessment)
    if request.typed_responses:
        typed_content = f"""CANDIDATE SELF-ASSESSMENT:
Overall Feeling (1-10): {request.typed_responses.overall_feeling}

Questions Asked:
{chr(10).join('- ' + q for q in request.typed_responses.questions_asked) if request.typed_responses.questions_asked else '(not provided)'}

Strong Answers (self-identified):
{chr(10).join('- ' + a for a in request.typed_responses.strong_answers) if request.typed_responses.strong_answers else '(not provided)'}

Weak Answers (self-identified):
{chr(10).join('- ' + a for a in request.typed_responses.weak_answers) if request.typed_responses.weak_answers else '(not provided)'}

Key Learnings:
{request.typed_responses.learnings if request.typed_responses.learnings else '(not provided)'}"""
        interview_content_parts.append(typed_content)

    if not interview_content_parts:
        raise HTTPException(status_code=400, detail="Either transcript_text or typed_responses must be provided")

    interview_content = "\n\n".join(interview_content_parts)

    system_prompt = """Analyze this interview performance and provide structured feedback.

DIMENSION SCORES (1-10 each):
- content: Did they cover key competencies and provide strong examples?
- clarity: Were answers clear and well-structured?
- delivery: Confident tone, no excessive filler words?
- tone: Professional, enthusiastic, appropriate energy?
- structure: Did answers follow logical frameworks (STAR, etc.)?
- confidence: Did they sound assured without arrogance?

ANALYSIS:
- strengths: 2-3 specific things they did well
- opportunities: 2-3 specific areas for improvement
- what_they_should_have_said: 1-2 examples of weak answers rewritten stronger
  Format: {"question": "...", "weak_answer": "...", "strong_answer": "..."}
- coaching_points: 3 specific things to practice before next interview
- action_items: 3 concrete next steps
- next_stage_adjustments: 2-3 strategic changes for next interview round

THANK YOU EMAIL:
Generate a professional thank-you email (3 paragraphs):
- Reference specific conversation topics
- Reinforce fit naturally
- Keep it concise

OUTPUT FORMAT:
Return JSON:
{
    "overall_score": integer 1-10,
    "dimension_scores": {
        "content": int, "clarity": int, "delivery": int,
        "tone": int, "structure": int, "confidence": int
    },
    "strengths": ["string", ...],
    "opportunities": ["string", ...],
    "what_they_should_have_said": [{"question": "...", "weak_answer": "...", "strong_answer": "..."}, ...],
    "coaching_points": ["string", ...],
    "action_items": ["string", ...],
    "thank_you_email": "full email text",
    "next_stage_adjustments": ["string", ...]
}

RULES:
- Be specific—reference actual questions/answers when possible
- Provide rewritten answers that use candidate's real experience
- Coaching must be actionable, not generic

No markdown, no preamble."""

    user_message = f"""INTERVIEW TYPE: {request.interview_stage}
INTERVIEW DATE: {request.interview_date}
INTERVIEWER: {request.interviewer_name or 'Unknown'}

CANDIDATE RESUME:
{resume_text}

TARGET ROLE:
Company: {request.company}
Role: {request.role_title}

JOB DESCRIPTION:
{request.job_description}

{interview_content}

Analyze this interview and generate the debrief."""

    # Call Claude
    response = call_claude(system_prompt, user_message, max_tokens=4000)

    # Parse JSON response
    try:
        cleaned = clean_claude_json(response)
        debrief = json.loads(cleaned)

        # Build response with defaults for missing fields
        dimension_scores = debrief.get("dimension_scores", {})

        return InterviewDebriefResponse(
            overall_score=debrief.get("overall_score", 5),
            dimension_scores=DimensionScores(
                content=dimension_scores.get("content", 5),
                clarity=dimension_scores.get("clarity", 5),
                delivery=dimension_scores.get("delivery", 5),
                tone=dimension_scores.get("tone", 5),
                structure=dimension_scores.get("structure", 5),
                confidence=dimension_scores.get("confidence", 5)
            ),
            strengths=debrief.get("strengths", []),
            opportunities=debrief.get("opportunities", []),
            what_they_should_have_said=[
                WhatTheyShouldHaveSaid(**item) for item in debrief.get("what_they_should_have_said", [])
            ],
            coaching_points=debrief.get("coaching_points", []),
            action_items=debrief.get("action_items", []),
            thank_you_email=debrief.get("thank_you_email", ""),
            next_stage_adjustments=debrief.get("next_stage_adjustments", [])
        )
    except (json.JSONDecodeError, Exception) as e:
        print(f"🔥 Failed to parse debrief response: {e}")
        print(f"Raw response: {response[:500]}")
        raise HTTPException(status_code=500, detail=f"Failed to parse debrief: {str(e)}")


# ============================================================================
# INTERVIEW INTELLIGENCE: CONVERSATIONAL DEBRIEF CHAT
# ============================================================================

class DebriefContext(BaseModel):
    """Context for the debrief conversation."""
    interviewerName: str
    interviewerTitle: Optional[str] = None
    interviewDate: Optional[str] = None
    interviewStage: str
    feeling: Optional[str] = None
    company: str
    roleTitle: str
    candidateName: str


class ConversationMessage(BaseModel):
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class DebriefChatRequest(BaseModel):
    """Request for conversational debrief."""
    resume_json: Dict[str, Any]
    job_description: str
    context: DebriefContext
    transcript: Optional[str] = None  # Now optional - can have conversation without transcript
    conversation_history: List[ConversationMessage]
    user_message: Optional[str] = None  # None for initial analysis


class DebriefChatResponse(BaseModel):
    """Response from conversational debrief."""
    response: str


DEBRIEF_SYSTEM_PROMPT_WITH_TRANSCRIPT = """You are an expert interview coach having a warm, supportive conversation with a candidate who just completed an interview. You're like a trusted mentor who gives honest, actionable feedback while being encouraging.

INTERVIEW CONTEXT:
- Company: {company}
- Role: {role_title}
- Interview Stage: {interview_stage}
- Interviewer: {interviewer_name}{interviewer_title}
- Candidate's Self-Assessment (1-10): {feeling}

CANDIDATE BACKGROUND:
{resume_text}

JOB DESCRIPTION:
{job_description}

INTERVIEW TRANSCRIPT:
{transcript}

YOUR COACHING STYLE:
1. Be conversational and warm - like talking to a friend who happens to be a career expert
2. Be specific - reference exact quotes and moments from the transcript
3. Be balanced - celebrate wins AND identify growth areas
4. Be actionable - give concrete suggestions they can implement
5. Be strategic - help them think about next steps and future rounds
6. Use markdown formatting: ## for section headers, **bold** for emphasis, - for bullet points

WHEN GIVING INITIAL ANALYSIS:
- Start with a brief overall impression (1-2 sentences)
- Use ## headers to organize sections (e.g., "## What Landed Really Well", "## Areas to Refine", "## Key Intel Gathered")
- Highlight 2-3 specific things that landed well (with quotes from transcript)
- Identify 2-3 areas to refine (with specific suggestions)
- Note any key intel gathered about the company/role
- End with encouragement and offer to help with specific things (thank-you email, next round prep, etc.)

WHEN RESPONDING TO FOLLOW-UPS:
- Answer their specific question directly
- Provide relevant examples or templates when requested
- Be concise but thorough
- Always tie back to their specific interview when possible

Remember: This is a conversation, not a report. Be human, be helpful, be honest."""


DEBRIEF_SYSTEM_PROMPT_NO_TRANSCRIPT = """You are an expert interview coach having a warm, supportive conversation with a candidate who just completed an interview. You're like a trusted mentor who helps them reflect on how it went and prepare for next steps.

INTERVIEW CONTEXT:
- Company: {company}
- Role: {role_title}
- Interview Stage: {interview_stage}
- Interviewer: {interviewer_name}{interviewer_title}
- Candidate's Self-Assessment (1-10): {feeling}

CANDIDATE BACKGROUND:
{resume_text}

JOB DESCRIPTION:
{job_description}

NOTE: The candidate does not have a transcript to share. You'll need to ask questions to understand how the interview went.

YOUR COACHING STYLE:
1. Be conversational and warm - like talking to a friend who happens to be a career expert
2. Ask thoughtful questions to understand what happened in the interview
3. Be balanced - celebrate wins AND identify growth areas based on what they share
4. Be actionable - give concrete suggestions they can implement
5. Be strategic - help them think about next steps and future rounds
6. Use markdown formatting: ## for section headers, **bold** for emphasis, - for bullet points

INITIAL GREETING (when no transcript):
Start by warmly greeting them and asking open-ended questions to understand the interview:
- How did the conversation flow?
- What questions did they ask you?
- What moments felt strong? What felt shaky?
- Did they share any information about the role, team, or next steps?
- Any red flags or exciting things you learned?

As they share details, provide feedback, coaching, and strategic advice. Help them:
- Process what happened
- Identify what worked and what to improve
- Prepare for next rounds
- Draft thank-you emails
- Strategize on compensation if relevant

Remember: This is a conversation. Be curious, helpful, and supportive."""


@app.post("/api/debrief/chat", response_model=DebriefChatResponse)
async def debrief_chat(request: DebriefChatRequest):
    """
    INTERVIEW INTELLIGENCE: Conversational debrief coaching.

    Provides warm, actionable coaching in a conversational format.
    Supports multi-turn conversations for follow-up questions,
    thank-you email drafts, next round prep, etc.
    """
    print(f"💬 Debrief chat for {request.context.company} - {request.context.roleTitle}")

    # Format resume for prompt
    resume_text = format_resume_for_prompt(request.resume_json)

    # Build interviewer info string
    interviewer_title = f" ({request.context.interviewerTitle})" if request.context.interviewerTitle else ""

    # Map interview stage to readable name
    stage_labels = {
        'recruiter_screen': 'Recruiter Screen',
        'hiring_manager': 'Hiring Manager Interview',
        'technical': 'Technical Interview',
        'panel': 'Panel Interview',
        'executive': 'Executive/Final Round'
    }
    interview_stage = stage_labels.get(request.context.interviewStage, request.context.interviewStage)

    # Format feeling
    feeling = f"{request.context.feeling}/10" if request.context.feeling else "Not provided"

    # Choose prompt based on whether transcript is provided
    has_transcript = bool(request.transcript and request.transcript.strip())

    # Truncate extremely long transcripts to stay within Claude's context window
    # Claude Sonnet can handle ~200k tokens, so 400k chars is a safe limit (~100k tokens)
    transcript_text = request.transcript or ""
    MAX_TRANSCRIPT_CHARS = 400000
    if len(transcript_text) > MAX_TRANSCRIPT_CHARS:
        print(f"⚠️ Truncating very long transcript from {len(transcript_text)} to {MAX_TRANSCRIPT_CHARS} chars")
        transcript_text = transcript_text[:MAX_TRANSCRIPT_CHARS] + "\n\n[... transcript truncated for length ...]"

    if has_transcript:
        system_prompt = DEBRIEF_SYSTEM_PROMPT_WITH_TRANSCRIPT.format(
            company=request.context.company,
            role_title=request.context.roleTitle,
            interview_stage=interview_stage,
            interviewer_name=request.context.interviewerName,
            interviewer_title=interviewer_title,
            feeling=feeling,
            resume_text=resume_text,
            job_description=request.job_description,
            transcript=transcript_text
        )
    else:
        system_prompt = DEBRIEF_SYSTEM_PROMPT_NO_TRANSCRIPT.format(
            company=request.context.company,
            role_title=request.context.roleTitle,
            interview_stage=interview_stage,
            interviewer_name=request.context.interviewerName,
            interviewer_title=interviewer_title,
            feeling=feeling,
            resume_text=resume_text,
            job_description=request.job_description
        )

    # Build messages for Claude
    messages = []

    # Add conversation history
    for msg in request.conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add current user message or request initial greeting/analysis
    if request.user_message:
        messages.append({
            "role": "user",
            "content": request.user_message
        })
    else:
        # Initial message depends on whether we have a transcript
        if has_transcript:
            messages.append({
                "role": "user",
                "content": "I just finished this interview. Can you analyze how it went and give me your honest feedback? What did I do well and what should I work on?"
            })
        else:
            messages.append({
                "role": "user",
                "content": "I just finished an interview and I'd like to debrief with you. I don't have a transcript, but I can tell you about how it went."
            })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=messages
        )

        assistant_response = response.content[0].text
        print(f"✅ Debrief chat response generated ({len(assistant_response)} chars)")

        return DebriefChatResponse(response=assistant_response)

    except Exception as e:
        print(f"🔥 Debrief chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


# ============================================================================
# INTERVIEW INTELLIGENCE: MOCK INTERVIEW ENDPOINTS
# ============================================================================

@app.post("/api/mock-interview/start", response_model=StartMockInterviewResponse)
async def start_mock_interview(request: StartMockInterviewRequest):
    """
    INTERVIEW INTELLIGENCE: Start a new mock interview session

    Creates a session and generates the first question based on:
    - Interview stage (recruiter_screen or hiring_manager)
    - Difficulty level (easy, medium, hard)
    - Candidate's resume and job description

    Returns session_id and first question to begin the interview.
    """
    print(f"🎤 Starting mock interview for {request.company} - {request.role_title}")

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Format resume for prompt
    resume_text = format_resume_for_prompt(request.resume_json)

    # Extract candidate's first name from resume (check multiple possible field names)
    full_name = request.resume_json.get("name") or request.resume_json.get("full_name") or request.resume_json.get("candidate_name") or ""
    candidate_name = full_name.split()[0] if full_name else "there"

    # First question is always a warm "tell me about yourself" - the 60-90 second pitch
    # This mirrors how real interviews start
    question_data = {
        "question_text": f"Hi {candidate_name}, thank you for making time to speak with me today. I'm excited to learn more about you and your background. So, tell me about yourself.",
        "competency_tested": "intro_pitch",
        "difficulty": "medium"
    }

    # Generate question ID
    question_id = str(uuid.uuid4())

    # Store session
    mock_interview_sessions[session_id] = {
        "id": session_id,
        "resume_json": request.resume_json,
        "job_description": request.job_description,
        "company": request.company,
        "role_title": request.role_title,
        "interview_stage": request.interview_stage,
        "difficulty_level": request.difficulty_level,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "overall_score": None,
        "session_feedback": None,
        "question_ids": [question_id],
        "current_question_number": 1
    }

    # Store question
    mock_interview_questions[question_id] = {
        "id": question_id,
        "session_id": session_id,
        "question_number": 1,
        "question_text": question_data["question_text"],
        "competency_tested": question_data["competency_tested"],
        "difficulty": question_data["difficulty"],
        "asked_at": datetime.now().isoformat()
    }

    # Initialize empty responses for this question
    mock_interview_responses[question_id] = []

    print(f"✅ Mock interview session started: {session_id}")

    return StartMockInterviewResponse(
        session_id=session_id,
        interview_stage=request.interview_stage,
        difficulty_level=request.difficulty_level,
        first_question=FirstQuestionResponse(
            question_id=question_id,
            question_text=question_data["question_text"],
            competency_tested=question_data["competency_tested"],
            question_number=1
        )
    )


@app.post("/api/mock-interview/respond", response_model=SubmitMockResponseResponse)
async def submit_mock_response(request: SubmitMockResponseRequest):
    """
    INTERVIEW INTELLIGENCE: Submit response and get follow-up question

    Submits candidate's response, analyzes it, and returns:
    - Brief coaching feedback
    - Follow-up question (if not at max follow-ups)
    - Whether to continue with more follow-ups
    """
    print(f"📝 Submitting mock response for question {request.question_id}")

    # Verify session exists
    session = mock_interview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found")

    # Verify question exists
    question = mock_interview_questions.get(request.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Store the response
    response_entry = {
        "response_number": request.response_number,
        "response_text": request.response_text,
        "responded_at": datetime.now().isoformat()
    }

    if request.question_id not in mock_interview_responses:
        mock_interview_responses[request.question_id] = []
    mock_interview_responses[request.question_id].append(response_entry)

    # Format resume for prompt
    resume_text = format_resume_for_prompt(session["resume_json"])

    # Determine target level
    target_level = determine_target_level(session["job_description"])

    # Detect role type from job description for role-specific signal weighting
    role_type = detect_role_type(session["job_description"], session["role_title"])

    # Build ALL responses for cumulative analysis
    all_responses = mock_interview_responses.get(request.question_id, [])
    all_responses_text = ""
    for i, resp in enumerate(all_responses, 1):
        label = "Initial Response" if i == 1 else f"Follow-up Response #{i-1}"
        all_responses_text += f"\n{label}:\n{resp['response_text']}\n"

    # Build analysis prompt with ALL responses for cumulative scoring
    prompt = MOCK_ANALYZE_RESPONSE_PROMPT.format(
        question_text=question["question_text"],
        all_responses=all_responses_text,
        competency=question["competency_tested"],
        target_level=target_level,
        role_type=role_type,
        resume_text=resume_text
    )

    # Call Claude to analyze cumulative response
    try:
        response = call_claude(
            "You are analyzing a candidate's COMPLETE interview response including all follow-ups. Score based on CUMULATIVE quality. Return only valid JSON.",
            prompt,
            max_tokens=2000
        )
        cleaned = clean_claude_json(response)
        analysis_data = json.loads(cleaned)
    except Exception as e:
        print(f"🔥 Failed to analyze response: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze response: {str(e)}")

    # Store or update analysis with signals and resume content
    resume_content = analysis_data.get("resume_content", {})
    signals = analysis_data.get("signals", {})

    # Calculate weighted score based on signals if available
    if signals:
        weighted_score = calculate_weighted_score(signals, role_type)
    else:
        weighted_score = analysis_data.get("score", 5)

    mock_interview_analyses[request.question_id] = {
        "question_id": request.question_id,
        "score": analysis_data.get("score", 5),
        "weighted_score": weighted_score,
        "level_demonstrated": analysis_data.get("level_demonstrated", "mid"),
        "role_type": role_type,
        # New signal tracking
        "signals": {
            "functional_competency": signals.get("functional_competency", 0.5),
            "leadership": signals.get("leadership", 0.5),
            "collaboration": signals.get("collaboration", 0.5),
            "ownership": signals.get("ownership", 0.5),
            "strategic_thinking": signals.get("strategic_thinking", 0.5),
            "problem_solving": signals.get("problem_solving", 0.5),
            "communication_clarity": signals.get("communication_clarity", 0.5),
            "metrics_orientation": signals.get("metrics_orientation", 0.5),
            "stakeholder_management": signals.get("stakeholder_management", 0.5),
            "executive_presence": signals.get("executive_presence", 0.5),
            "user_centricity": signals.get("user_centricity", 0.5)
        },
        "signal_strengths": analysis_data.get("signal_strengths", []),
        "signal_gaps": analysis_data.get("signal_gaps", []),
        "follow_up_trigger": analysis_data.get("follow_up_trigger"),
        "follow_up_questions": analysis_data.get("follow_up_questions", []),
        "brief_feedback": analysis_data.get("brief_feedback", ""),
        "resume_content": {
            "metrics": resume_content.get("metrics", []),
            "achievements": resume_content.get("achievements", []),
            "stories": resume_content.get("stories", [])
        },
        "response_count": len(all_responses),
        "created_at": datetime.now().isoformat()
    }

    # Check if this is the last follow-up (response_number 4)
    if request.response_number >= 4:
        print(f"✅ Max follow-ups reached for question {request.question_id}")
        return SubmitMockResponseResponse(
            response_recorded=True,
            follow_up_question=None,
            should_continue=False,
            brief_feedback=analysis_data.get("brief_feedback", "Good effort on this question.")
        )

    # Return follow-up question
    follow_ups = analysis_data.get("follow_up_questions", [])
    follow_up = follow_ups[0] if follow_ups else None

    print(f"✅ Response analyzed, follow-up provided")

    return SubmitMockResponseResponse(
        response_recorded=True,
        follow_up_question=follow_up,
        should_continue=True,
        brief_feedback=analysis_data.get("brief_feedback", "")
    )


@app.get("/api/mock-interview/question-feedback/{question_id}", response_model=QuestionFeedbackResponse)
async def get_mock_question_feedback(question_id: str):
    """
    INTERVIEW INTELLIGENCE: Get comprehensive feedback for a completed question

    Returns detailed coaching feedback including:
    - Score and level demonstrated
    - What landed and what didn't
    - Specific coaching advice
    - Revised answer at target level
    """
    print(f"📊 Getting feedback for question {question_id}")

    # Verify question exists
    question = mock_interview_questions.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get session
    session = mock_interview_sessions.get(question["session_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get all responses
    responses = mock_interview_responses.get(question_id, [])
    all_responses = [r["response_text"] for r in responses]
    all_responses_text = format_responses_for_analysis(question_id)

    # Get existing analysis
    analysis = mock_interview_analyses.get(question_id, {})

    # Format resume for prompt
    resume_text = format_resume_for_prompt(session["resume_json"])

    # Determine target level
    target_level = determine_target_level(session["job_description"])

    # Build feedback prompt
    prompt = MOCK_QUESTION_FEEDBACK_PROMPT.format(
        question_text=question["question_text"],
        competency=question["competency_tested"],
        target_level=target_level,
        all_responses_text=all_responses_text if all_responses_text else "No responses recorded.",
        analysis_json=json.dumps(analysis, indent=2),
        resume_text=resume_text
    )

    # Call Claude for comprehensive feedback
    try:
        response = call_claude(
            "You are providing coaching feedback on interview responses. Return only valid JSON.",
            prompt,
            max_tokens=2000
        )
        cleaned = clean_claude_json(response)
        feedback_data = json.loads(cleaned)
    except Exception as e:
        print(f"🔥 Failed to generate feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")

    # Update analysis with comprehensive feedback
    if question_id in mock_interview_analyses:
        mock_interview_analyses[question_id]["feedback_text"] = feedback_data.get("coaching", "")
        mock_interview_analyses[question_id]["revised_answer"] = feedback_data.get("revised_answer", "")

    print(f"✅ Feedback generated for question {question_id}")

    return QuestionFeedbackResponse(
        question_text=question["question_text"],
        all_responses=all_responses,
        score=analysis.get("score", 5),
        level_demonstrated=analysis.get("level_demonstrated", "L4"),
        what_landed=feedback_data.get("what_landed", []),
        what_didnt_land=feedback_data.get("what_didnt_land", []),
        coaching=feedback_data.get("coaching", ""),
        revised_answer=feedback_data.get("revised_answer", "")
    )


@app.post("/api/mock-interview/next-question", response_model=NextQuestionResponse)
async def get_next_mock_question(request: NextQuestionRequest):
    """
    INTERVIEW INTELLIGENCE: Move to the next question

    Generates the next question based on:
    - Session progress
    - Previous questions asked (to avoid repeats)
    - Rotating competencies

    Returns new question and session progress.
    """
    print(f"➡️ Getting next question for session {request.session_id}")

    # Verify session exists
    session = mock_interview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found")

    # Check if max questions reached (5)
    if request.current_question_number >= 5:
        raise HTTPException(status_code=400, detail="Maximum questions reached. End session to see results.")

    # Check if session is already completed
    if session.get("completed_at"):
        raise HTTPException(status_code=400, detail="Session already completed. Start a new session.")

    # Calculate next question number
    next_question_number = request.current_question_number + 1

    # Get competency for next question
    competency = get_competency_for_stage(session["interview_stage"], next_question_number)

    # Get list of already asked questions
    asked_questions = []
    for qid in session.get("question_ids", []):
        q = mock_interview_questions.get(qid)
        if q:
            asked_questions.append(q["question_text"])

    asked_questions_text = "\n".join([f"- {q}" for q in asked_questions]) if asked_questions else "None"

    # Format resume for prompt
    resume_text = format_resume_for_prompt(session["resume_json"])

    # Extract candidate's first name from resume (check multiple possible field names)
    full_name = session["resume_json"].get("name") or session["resume_json"].get("full_name") or session["resume_json"].get("candidate_name") or ""
    candidate_name = full_name.split()[0] if full_name else "there"

    # Build prompt for next question
    prompt = MOCK_GENERATE_QUESTION_PROMPT.format(
        interview_stage=session["interview_stage"],
        candidate_name=candidate_name,
        resume_text=resume_text,
        company=session["company"],
        role_title=session["role_title"],
        job_description=session["job_description"],
        difficulty=session["difficulty_level"],
        asked_questions=asked_questions_text,
        competency_area=competency
    )

    # Call Claude to generate question
    try:
        response = call_claude(
            "You are generating interview questions for a mock interview practice session. Return only valid JSON.",
            prompt,
            max_tokens=1000
        )
        cleaned = clean_claude_json(response)
        question_data = json.loads(cleaned)
    except Exception as e:
        print(f"🔥 Failed to generate question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

    # Generate question ID
    question_id = str(uuid.uuid4())

    # Store question
    mock_interview_questions[question_id] = {
        "id": question_id,
        "session_id": request.session_id,
        "question_number": next_question_number,
        "question_text": question_data["question_text"],
        "competency_tested": question_data["competency_tested"],
        "difficulty": question_data["difficulty"],
        "asked_at": datetime.now().isoformat()
    }

    # Initialize empty responses for this question
    mock_interview_responses[question_id] = []

    # Update session with new question
    session["question_ids"].append(question_id)
    session["current_question_number"] = next_question_number

    # Calculate average score
    average_score = calculate_mock_session_average(request.session_id)

    print(f"✅ Next question generated: {question_id}")

    return NextQuestionResponse(
        question_id=question_id,
        question_text=question_data["question_text"],
        competency_tested=question_data["competency_tested"],
        question_number=next_question_number,
        total_questions=5,
        session_progress=MockSessionProgress(
            questions_completed=request.current_question_number,
            average_score=average_score
        )
    )


@app.post("/api/mock-interview/end", response_model=EndMockInterviewResponse)
async def end_mock_interview(request: EndMockInterviewRequest):
    """
    INTERVIEW INTELLIGENCE: End session and get comprehensive feedback

    Generates session-level feedback including:
    - Overall score and readiness assessment
    - Aggregated signal scores across all questions
    - Key strengths and areas to improve (based on signals)
    - Coaching priorities and recommended drills
    - Summary of each question's performance
    """
    print(f"🏁 Ending mock interview session {request.session_id}")

    # Verify session exists
    session = mock_interview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mock interview session not found")

    # Calculate overall score
    average_score = calculate_mock_session_average(request.session_id)

    # Detect role type for this session
    role_type = detect_role_type(session.get("job_description", ""), session.get("role_title", ""))

    # Build question summaries and aggregate signals
    question_summaries = []
    questions_summary_text = []

    # Initialize signal aggregation
    signal_names = [
        "functional_competency", "leadership", "collaboration", "ownership",
        "strategic_thinking", "problem_solving", "communication_clarity",
        "metrics_orientation", "stakeholder_management", "executive_presence",
        "user_centricity"
    ]
    aggregated_signals = {signal: [] for signal in signal_names}
    all_signal_strengths = []
    all_signal_gaps = []
    level_counts = {"mid": 0, "senior": 0, "director": 0, "executive": 0}

    for qid in session.get("question_ids", []):
        question = mock_interview_questions.get(qid)
        analysis = mock_interview_analyses.get(qid, {})

        if question:
            score = analysis.get("score", 5)
            brief_feedback = analysis.get("brief_feedback", "")

            question_summaries.append(MockQuestionSummary(
                question_number=question["question_number"],
                question_text=question["question_text"],
                score=score,
                brief_feedback=brief_feedback
            ))

            questions_summary_text.append(
                f"Q{question['question_number']}: {question['question_text']}\n"
                f"Score: {score}/10\n"
                f"Competency: {question['competency_tested']}\n"
                f"Feedback: {brief_feedback}"
            )

            # Aggregate signals from this question's analysis
            if "signals" in analysis:
                for signal_name in signal_names:
                    signal_value = analysis["signals"].get(signal_name)
                    if signal_value is not None:
                        aggregated_signals[signal_name].append(signal_value)

            # Collect strengths and gaps
            all_signal_strengths.extend(analysis.get("signal_strengths", []))
            all_signal_gaps.extend(analysis.get("signal_gaps", []))

            # Count levels demonstrated
            level = analysis.get("level_demonstrated", "mid")
            if level in level_counts:
                level_counts[level] += 1

    # Calculate average signal scores
    avg_signals = {}
    for signal_name, values in aggregated_signals.items():
        if values:
            avg_signals[signal_name] = round(sum(values) / len(values), 2)
        else:
            avg_signals[signal_name] = 0.5  # Default if no data

    # Identify session-level strengths and gaps
    session_strengths = [s for s, v in avg_signals.items() if v >= 0.7]
    session_gaps = [s for s, v in avg_signals.items() if v <= 0.4]

    # Determine predominant level
    predominant_level = max(level_counts, key=level_counts.get) if any(level_counts.values()) else "mid"

    # Format signal summary for prompt
    signal_summary_lines = [f"- {signal}: {avg_signals[signal]}" for signal in signal_names]
    signal_summary = "\n".join(signal_summary_lines)

    # Format strengths and gaps for prompt
    strengths_text = ", ".join(session_strengths) if session_strengths else "None identified"
    gaps_text = ", ".join(session_gaps) if session_gaps else "None identified"

    # Format resume for prompt
    resume_text = format_resume_for_prompt(session["resume_json"])

    # Build session feedback prompt with signal data
    prompt = MOCK_SESSION_FEEDBACK_PROMPT.format(
        interview_stage=session["interview_stage"],
        role_type=role_type,
        num_questions=len(session.get("question_ids", [])),
        average_score=round(average_score, 1),
        level_demonstrated=predominant_level,
        signal_summary=signal_summary,
        signal_strengths=strengths_text,
        signal_gaps=gaps_text,
        questions_summary="\n\n".join(questions_summary_text) if questions_summary_text else "No questions completed.",
        resume_text=resume_text,
        company=session["company"],
        role_title=session["role_title"],
        job_description=session["job_description"]
    )

    # Call Claude for session feedback
    try:
        response = call_claude(
            "You are providing comprehensive session feedback for a mock interview. Return only valid JSON.",
            prompt,
            max_tokens=2000
        )
        cleaned = clean_claude_json(response)
        feedback_data = json.loads(cleaned)
    except Exception as e:
        print(f"🔥 Failed to generate session feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate session feedback: {str(e)}")

    # Update session with completion info including signals
    session["completed_at"] = datetime.now().isoformat()
    session["overall_score"] = average_score
    session["session_feedback"] = feedback_data
    session["aggregated_signals"] = avg_signals
    session["signal_strengths"] = session_strengths
    session["signal_gaps"] = session_gaps
    session["level_estimate"] = feedback_data.get("level_estimate", predominant_level)

    print(f"✅ Mock interview session ended: {request.session_id}")
    print(f"   Signal strengths: {session_strengths}")
    print(f"   Signal gaps: {session_gaps}")
    print(f"   Level estimate: {session['level_estimate']}")

    return EndMockInterviewResponse(
        session_id=request.session_id,
        overall_score=round(average_score, 1),
        questions_completed=len(session.get("question_ids", [])),
        session_feedback=MockSessionFeedback(
            overall_assessment=feedback_data.get("overall_assessment", ""),
            key_strengths=feedback_data.get("key_strengths", []),
            areas_to_improve=feedback_data.get("areas_to_improve", []),
            coaching_priorities=feedback_data.get("coaching_priorities", []),
            recommended_drills=feedback_data.get("recommended_drills", []),
            readiness_score=feedback_data.get("readiness_score", "Needs Practice"),
            level_estimate=feedback_data.get("level_estimate", predominant_level),
            next_steps=feedback_data.get("next_steps", "")
        ),
        question_summaries=question_summaries
    )


@app.get("/api/mock-interview/sessions/{company}/{role_title}")
async def get_mock_session_history(company: str, role_title: str):
    """
    INTERVIEW INTELLIGENCE: Get session history for a company/role

    Returns all past mock interview sessions for the specified company and role,
    including improvement trends if multiple sessions exist.
    """
    print(f"📜 Getting mock interview history for {company} - {role_title}")

    # Find all sessions for this company/role
    matching_sessions = []

    for session_id, session in mock_interview_sessions.items():
        if session["company"] == company and session["role_title"] == role_title:
            questions_completed = len(session.get("question_ids", []))

            matching_sessions.append(MockInterviewSessionSummary(
                session_id=session_id,
                interview_stage=session["interview_stage"],
                started_at=session["started_at"],
                completed_at=session.get("completed_at"),
                overall_score=session.get("overall_score"),
                questions_completed=questions_completed
            ))

    # Sort by started_at (newest first)
    matching_sessions.sort(key=lambda s: s.started_at, reverse=True)

    # Calculate improvement trend if multiple completed sessions
    improvement_trend = None
    completed_sessions = [s for s in matching_sessions if s.overall_score is not None]

    if len(completed_sessions) >= 2:
        # Get first and latest completed sessions
        first_session = completed_sessions[-1]  # Oldest
        latest_session = completed_sessions[0]  # Newest

        improvement = latest_session.overall_score - first_session.overall_score
        improvement_str = f"+{improvement:.1f}" if improvement >= 0 else f"{improvement:.1f}"

        improvement_trend = ImprovementTrend(
            first_session_score=first_session.overall_score,
            latest_session_score=latest_session.overall_score,
            improvement=improvement_str
        )

    print(f"✅ Found {len(matching_sessions)} session(s)")

    return SessionHistoryResponse(
        sessions=matching_sessions,
        improvement_trend=improvement_trend
    )


# ============================================================================
# INTERVIEW INTELLIGENCE: TEXT-TO-SPEECH ENDPOINT
# ============================================================================

class TTSRequest(BaseModel):
    """Request for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=4096)
    voice: str = Field(default="onyx", pattern="^(alloy|echo|fable|onyx|nova|shimmer)$")


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    INTERVIEW INTELLIGENCE: Convert text to natural AI speech using OpenAI TTS.

    Available voices:
    - onyx: Deep male voice (recommended for interviewer)
    - echo: Male voice
    - fable: British male voice
    - alloy: Neutral voice
    - nova: Female voice
    - shimmer: Female voice
    """
    import httpx
    from fastapi.responses import Response

    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable for natural AI voice."
        )

    print(f"🎙️ TTS request: {len(request.text)} chars, voice={request.voice}")

    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": request.text,
                    "voice": request.voice,
                    "response_format": "mp3"
                },
                timeout=30.0
            )

            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ OpenAI TTS error: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=f"OpenAI TTS error: {error_detail}")

            print(f"✅ TTS audio generated: {len(response.content)} bytes")

            return Response(
                content=response.content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline"}
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="TTS request timed out")
    except Exception as e:
        print(f"❌ TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT DOWNLOAD ENDPOINTS
# ============================================================================

class PackageDownloadRequest(BaseModel):
    resume_text: str
    cover_letter_text: str
    candidate_name: str = "Candidate"

@app.post("/api/package/download")
async def download_package(request: PackageDownloadRequest):
    """
    Generate and download a ZIP file containing DOCX resume and cover letter
    """
    import io
    import zipfile
    from fastapi.responses import StreamingResponse
    
    try:
        print(f"📦 Generating download package for: {request.candidate_name}")
        
        # Create DOCX files
        resume_docx = create_docx_from_text(request.resume_text, f"{request.candidate_name} - Resume")
        cover_letter_docx = create_docx_from_text(request.cover_letter_text, f"{request.candidate_name} - Cover Letter")
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add resume
            resume_buffer = io.BytesIO()
            resume_docx.save(resume_buffer)
            resume_buffer.seek(0)
            zip_file.writestr(f"{request.candidate_name.replace(' ', '_')}_Resume.docx", resume_buffer.getvalue())
            
            # Add cover letter
            cl_buffer = io.BytesIO()
            cover_letter_docx.save(cl_buffer)
            cl_buffer.seek(0)
            zip_file.writestr(f"{request.candidate_name.replace(' ', '_')}_Cover_Letter.docx", cl_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        print(f"✅ Package generated successfully")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={request.candidate_name.replace(' ', '_')}_Application_Package.zip"
            }
        )
        
    except Exception as e:
        print(f"🔥 DOWNLOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate download: {str(e)}")


def create_docx_from_text(text: str, title: str):
    """
    Create an ATS-safe DOCX document from plain text.
    
    CRITICAL RULES:
    - Text-only, no templates, no restructuring
    - Exact line-by-line reproduction of preview text
    - No heading styles, no list styles, no formatting magic
    - ATS-safe: Calibri font, no tables, no textboxes, no images
    - Bullets (•) treated as plain text characters, NOT Word lists
    """
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    
    doc = Document()
    
    # Set ATS-safe margins (0.75 inches all around)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    
    # Process text line by line - EXACT reproduction
    lines = text.split('\n')
    
    for line in lines:
        # Preserve the line exactly (don't strip - preserve intentional spacing)
        # But do strip for empty line detection
        stripped = line.strip()
        
        if not stripped:
            # Empty line - add blank paragraph for spacing
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            continue
        
        # Add paragraph with the exact line content
        p = doc.add_paragraph()
        
        # CRITICAL: Use 'Normal' style only - no Heading, no ListParagraph
        p.style = doc.styles['Normal']
        
        # Reset all paragraph formatting
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Pt(0)
        p.paragraph_format.right_indent = Pt(0)
        p.paragraph_format.first_line_indent = Pt(0)
        
        # Add the text as a single run
        run = p.add_run(stripped)
        
        # ATS-safe font settings - consistent for ALL text
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.bold = False
        run.italic = False
        run.underline = False
        
        # Ensure Calibri is set for complex scripts too
        r = run._element
        rPr = r.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), 'Calibri')
        rFonts.set(qn('w:hAnsi'), 'Calibri')
        rFonts.set(qn('w:cs'), 'Calibri')
        rFonts.set(qn('w:eastAsia'), 'Calibri')
        rPr.insert(0, rFonts)
    
    return doc


# ============================================================================
# NEW DOCUMENT DOWNLOAD ENDPOINTS (Using professional formatters)
# ============================================================================

class ResumeDownloadRequest(BaseModel):
    """Request body for resume download"""
    candidate_name: str
    tagline: str = ""
    contact: Dict[str, Any] = {}
    summary: str = ""
    competencies: List[str] = []
    experience: List[Dict[str, Any]] = []
    skills: Dict[str, Any] = {}
    education: Dict[str, Any] = {}

    class Config:
        extra = "allow"


class CoverLetterDownloadRequest(BaseModel):
    """Request body for cover letter download"""
    candidate_name: str
    tagline: str = ""
    contact: Dict[str, Any] = {}
    recipient_name: Optional[str] = None
    paragraphs: List[str] = []

    class Config:
        extra = "allow"


@app.post("/api/download/resume")
async def download_resume(request: ResumeDownloadRequest):
    """
    Generate and download a professionally formatted resume DOCX.
    """
    try:
        print(f"📄 Generating formatted resume for: {request.candidate_name}")

        # Initialize formatter
        formatter = ResumeFormatter()

        # Add header
        formatter.add_header(
            name=request.candidate_name,
            tagline=request.tagline,
            contact_info=request.contact
        )

        # Add summary if provided
        if request.summary:
            formatter.add_section_header("Summary")
            formatter.add_summary(request.summary)

        # Add core competencies if provided
        if request.competencies:
            formatter.add_section_header("Core Competencies")
            formatter.add_core_competencies(request.competencies)

        # Add experience if provided
        if request.experience:
            formatter.add_section_header("Experience")
            for job in request.experience:
                formatter.add_experience_entry(
                    company=job.get('company', ''),
                    title=job.get('title', ''),
                    location=job.get('location', ''),
                    dates=job.get('dates', ''),
                    overview=job.get('overview'),
                    bullets=job.get('bullets', [])
                )

        # Add skills if provided
        if request.skills:
            formatter.add_section_header("Skills")
            formatter.add_skills(request.skills)

        # Add education if provided
        if request.education and request.education.get('school'):
            formatter.add_section_header("Education")
            formatter.add_education(
                school=request.education.get('school', ''),
                degree=request.education.get('degree', ''),
                details=request.education.get('details')
            )

        # Save to buffer
        buffer = io.BytesIO()
        formatter.get_document().save(buffer)
        buffer.seek(0)

        filename = f"{request.candidate_name.replace(' ', '_')}_Resume.docx"

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        print(f"🔥 RESUME DOWNLOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")


@app.post("/api/download/cover-letter")
async def download_cover_letter(request: CoverLetterDownloadRequest):
    """
    Generate and download a professionally formatted cover letter DOCX.
    """
    try:
        print(f"📄 Generating formatted cover letter for: {request.candidate_name}")

        # Initialize formatter
        formatter = CoverLetterFormatter()

        # Add header
        formatter.add_header(
            name=request.candidate_name,
            tagline=request.tagline,
            contact_info=request.contact
        )

        # Add section label
        formatter.add_section_label()

        # Add salutation
        formatter.add_salutation(recipient_name=request.recipient_name)

        # Add body paragraphs
        for paragraph in request.paragraphs:
            formatter.add_body_paragraph(paragraph)

        # Add signature
        formatter.add_signature(request.candidate_name)

        # Save to buffer
        buffer = io.BytesIO()
        formatter.get_document().save(buffer)
        buffer.seek(0)

        filename = f"{request.candidate_name.replace(' ', '_')}_Cover_Letter.docx"

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        print(f"🔥 COVER LETTER DOWNLOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")


# ============================================================================
# SCREENING QUESTIONS ENDPOINT
# ============================================================================

SCREENING_QUESTIONS_PROMPT = """You are the screening question response engine for HenryAI.
Your job is to help candidates craft honest, strategically positioned responses to ATS screening questions.

=== CRITICAL RULES ===

## 1. Zero Fabrication Rule
You may NOT invent:
- Years of experience the candidate doesn't have
- Skills or tools they haven't used
- Achievements or metrics not in their background
- Degrees or certifications they don't hold

You may ONLY:
- Reframe and position existing experience
- Bridge adjacent experience to the question's context
- Highlight transferable skills from their actual background

## 2. Gap Detection
When the candidate lacks direct experience for a question:
- Flag it as a gap (gap_detected: true)
- Provide a mitigation strategy that honestly bridges their closest experience
- Never claim experience they don't have

## 3. Strategic Positioning
- Use strong action verbs
- Include specific metrics from their resume when relevant
- Position experience in the context the question is asking about
- Keep responses concise but substantive

=== CANDIDATE BACKGROUND ===

{resume_context}

=== JOB CONTEXT ===

Company: {company}
Role: {role_title}
Job Description: {job_description}

=== SCREENING QUESTIONS ===

{screening_questions}

=== OUTPUT FORMAT ===

Return a JSON object with this EXACT structure:

{{
  "responses": [
    {{
      "question": "The exact question text",
      "recommended_response": "The response to submit (can be multi-paragraph for essay questions, or brief for simple questions)",
      "strategic_note": "1-2 sentences explaining why this response works and what it emphasizes",
      "gap_detected": false,
      "mitigation_strategy": null
    }},
    {{
      "question": "Question where candidate has weak/no experience",
      "recommended_response": "Honest response that bridges their closest experience",
      "strategic_note": "Explains the positioning approach",
      "gap_detected": true,
      "mitigation_strategy": "Specific advice on how they reframed their experience to address this gap"
    }}
  ],
  "overall_strategy": "1-2 sentences summarizing the approach across all questions"
}}

IMPORTANT:
- Parse each question from the input (they may be numbered, bulleted, or separated by line breaks)
- For yes/no questions, provide the appropriate answer plus brief supporting context if helpful
- For years of experience questions, calculate accurately from their resume
- For essay/paragraph questions, provide substantive 2-4 sentence responses
- For multiple choice, indicate the best selection and why

Your response must be ONLY valid JSON, no additional text."""


@app.post("/api/screening-questions/generate")
async def generate_screening_responses(request: ScreeningQuestionsRequest) -> ScreeningQuestionsResponse:
    """
    Generate strategically positioned responses to ATS screening questions.
    Based on candidate's resume and job description, provides honest responses
    that emphasize relevant experience without fabrication.
    """
    try:
        print(f"📋 Generating screening question responses for {request.company} - {request.role_title}")

        # Build resume context
        resume_json = request.resume_json
        resume_context = f"""
Name: {resume_json.get('full_name', 'Unknown')}
Current Title: {resume_json.get('current_title', 'Unknown')}
Years of Experience: {resume_json.get('years_experience', 'Unknown')}
Summary: {resume_json.get('summary', '')}

Skills: {', '.join(resume_json.get('skills', []))}

Experience:
"""
        for exp in resume_json.get('experience', []):
            resume_context += f"\n- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('dates', '')})"
            for bullet in exp.get('bullets', [])[:3]:  # Limit bullets to keep context manageable
                resume_context += f"\n  • {bullet}"

        resume_context += f"\n\nEducation: {resume_json.get('education', 'Not specified')}"

        # Add JD analysis context if available
        jd_context = ""
        if request.jd_analysis:
            jd_context = f"""
Fit Score: {request.jd_analysis.get('fit_score', 'Unknown')}%
Strengths: {', '.join(request.jd_analysis.get('strengths', [])[:3])}
Gaps: {', '.join(request.jd_analysis.get('gaps', [])[:3])}
"""
            resume_context += f"\n\n=== FIT ANALYSIS ==={jd_context}"

        # Build the system prompt
        system_prompt = SCREENING_QUESTIONS_PROMPT.format(
            resume_context=resume_context,
            company=request.company,
            role_title=request.role_title,
            job_description=request.job_description[:3000],  # Limit JD length
            screening_questions=request.screening_questions
        )

        # Add candidate state calibration if available
        calibration_prompt = build_candidate_calibration_prompt(request.situation)
        if calibration_prompt:
            system_prompt += calibration_prompt

        # Call Claude
        user_message = f"Generate strategic responses for these screening questions:\n\n{request.screening_questions}"
        response = call_claude(system_prompt, user_message)

        # Parse the response
        cleaned = clean_claude_json(response)
        parsed_data = json.loads(cleaned)

        # Validate and return
        return ScreeningQuestionsResponse(
            responses=[
                ScreeningQuestionResponse(
                    question=r.get('question', ''),
                    recommended_response=r.get('recommended_response', ''),
                    strategic_note=r.get('strategic_note', ''),
                    gap_detected=r.get('gap_detected', False),
                    mitigation_strategy=r.get('mitigation_strategy')
                )
                for r in parsed_data.get('responses', [])
            ],
            overall_strategy=parsed_data.get('overall_strategy', '')
        )

    except json.JSONDecodeError as e:
        print(f"🔥 SCREENING QUESTIONS JSON ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse screening question responses: {str(e)}")
    except Exception as e:
        print(f"🔥 SCREENING QUESTIONS ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating screening responses: {str(e)}")


# ============================================================================
# EXPERIENCE SUPPLEMENTATION ENDPOINTS
# ============================================================================

CLARIFYING_QUESTIONS_PROMPT = """You are the experience supplementation engine for HenryAI.
Your job is to generate targeted clarifying questions when a candidate's resume shows gaps for a specific role.

=== CONTEXT ===
Candidates often tailor their resumes and may have omitted relevant experience. Before generating documents,
we ask clarifying questions to uncover hidden experience that could strengthen their fit.

=== CANDIDATE BACKGROUND ===

{resume_context}

=== JOB CONTEXT ===

Company: {company}
Role: {role_title}
Job Description: {job_description}

=== IDENTIFIED GAPS ===

{gaps}

Current Fit Score: {fit_score}%

=== YOUR TASK ===

Generate 1 targeted clarifying question for EACH gap (maximum 4 questions total, prioritize the most impactful gaps).

For each gap, create a question that:
1. Is specific and easy to answer
2. Helps uncover experience that may have been omitted from the resume
3. Could realistically improve their fit score if they have the experience

=== OUTPUT FORMAT ===

Return a JSON object with this EXACT structure:

{{
  "intro_message": "A brief, encouraging 1-2 sentence message to the candidate explaining why you're asking these questions. Use their first name if available. Example: 'Your background is strong, but I noticed a few areas where additional context could strengthen your fit. Quick questions:'",
  "questions": [
    {{
      "gap_area": "The specific gap this addresses (e.g., 'Enterprise sales experience')",
      "question": "A direct, specific question (e.g., 'Have you worked with enterprise clients ($100K+ deals) in any capacity, even if not in a pure sales role?')",
      "why_it_matters": "Brief explanation of why this matters for the role",
      "example_answer": "Example of what a strong response might look like"
    }}
  ]
}}

IMPORTANT:
- Questions should be conversational, not interrogative
- Focus on uncovering adjacent or transferable experience
- Don't ask about gaps that can't realistically be filled by hidden experience
- Maximum 4 questions, prioritize by impact on fit score

Your response must be ONLY valid JSON, no additional text."""


REANALYZE_PROMPT = """You are the experience re-analysis engine for HenryAI.
The candidate has provided additional context about their experience. Re-evaluate their fit for this role.

=== ORIGINAL RESUME ===

{resume_context}

=== SUPPLEMENTED EXPERIENCE ===

The candidate provided these additional details:

{supplements}

=== JOB CONTEXT ===

Company: {company}
Role: {role_title}
Job Description: {job_description}

=== ORIGINAL ANALYSIS ===

Original Fit Score: {original_fit_score}%
Original Gaps: {original_gaps}

=== YOUR TASK ===

1. Evaluate how the supplemented experience addresses each gap
2. Calculate a new fit score (be realistic - supplements can improve score but typically by 5-15 points max)
3. Identify which gaps were addressed vs. which remain
4. Update the resume JSON to incorporate the new experience appropriately

=== SCORING RULES ===

- If supplement FULLY addresses a gap: +5-8 points potential
- If supplement PARTIALLY addresses a gap: +2-4 points potential
- If supplement is weak/tangential: +0-1 points
- Maximum total improvement: 20 points (even with great supplements)
- Score cannot exceed 95 (even perfect candidates have room for growth)

=== OUTPUT FORMAT ===

Return a JSON object with this EXACT structure:

{{
  "new_fit_score": 72,
  "score_change": 8,
  "updated_strengths": ["List of strengths including any new ones from supplements"],
  "remaining_gaps": ["Gaps that weren't fully addressed"],
  "addressed_gaps": ["Gaps that were addressed by supplements"],
  "updated_resume_json": {{
    // The original resume_json with supplements incorporated
    // Add new experience entries or update existing ones
    // Add new skills if mentioned
  }},
  "summary": "Brief 1-2 sentence explanation of the score change and what improved"
}}

Your response must be ONLY valid JSON, no additional text."""


@app.post("/api/experience/clarifying-questions")
async def generate_clarifying_questions(request: GenerateClarifyingQuestionsRequest) -> GenerateClarifyingQuestionsResponse:
    """
    Generate targeted clarifying questions based on identified gaps.
    These questions help uncover experience the candidate may have omitted from their resume.
    """
    try:
        print(f"❓ Generating clarifying questions for {request.company} - {request.role_title}")
        print(f"   Gaps to address: {request.gaps}")

        # Build resume context
        resume_json = request.resume_json
        resume_context = f"""
Name: {resume_json.get('full_name', resume_json.get('contact', {}).get('full_name', 'Unknown'))}
Current Title: {resume_json.get('current_title', 'Unknown')}
Years of Experience: {resume_json.get('years_experience', 'Unknown')}
Summary: {resume_json.get('summary', resume_json.get('summary_text', ''))}

Skills: {', '.join(resume_json.get('skills', []))}

Experience:
"""
        for exp in resume_json.get('experience', []):
            resume_context += f"\n- {exp.get('title', exp.get('role', ''))} at {exp.get('company', '')} ({exp.get('dates', exp.get('start_date', ''))})"

        # Format gaps
        gaps_text = "\n".join([f"- {gap}" for gap in request.gaps])

        # Build the system prompt
        system_prompt = CLARIFYING_QUESTIONS_PROMPT.format(
            resume_context=resume_context,
            company=request.company,
            role_title=request.role_title,
            job_description=request.job_description[:3000],
            gaps=gaps_text,
            fit_score=request.fit_score
        )

        # Call Claude
        user_message = f"Generate clarifying questions for these gaps:\n\n{gaps_text}"
        response = call_claude(system_prompt, user_message)

        # Parse the response
        cleaned = clean_claude_json(response)
        parsed_data = json.loads(cleaned)

        # Validate and return
        return GenerateClarifyingQuestionsResponse(
            intro_message=parsed_data.get('intro_message', 'I have a few questions to better understand your background:'),
            questions=[
                ClarifyingQuestion(
                    gap_area=q.get('gap_area', ''),
                    question=q.get('question', ''),
                    why_it_matters=q.get('why_it_matters', ''),
                    example_answer=q.get('example_answer', '')
                )
                for q in parsed_data.get('questions', [])
            ]
        )

    except json.JSONDecodeError as e:
        print(f"🔥 CLARIFYING QUESTIONS JSON ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse clarifying questions: {str(e)}")
    except Exception as e:
        print(f"🔥 CLARIFYING QUESTIONS ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating clarifying questions: {str(e)}")


@app.post("/api/experience/reanalyze")
async def reanalyze_with_supplements(request: ReanalyzeWithSupplementsRequest) -> ReanalyzeWithSupplementsResponse:
    """
    Re-analyze candidate fit after they've provided supplemental experience information.
    Returns updated fit score, strengths, gaps, and an updated resume JSON.
    """
    try:
        print(f"🔄 Re-analyzing fit with {len(request.supplements)} supplements for {request.company} - {request.role_title}")

        # Build resume context
        resume_json = request.resume_json
        resume_context = f"""
Name: {resume_json.get('full_name', resume_json.get('contact', {}).get('full_name', 'Unknown'))}
Current Title: {resume_json.get('current_title', 'Unknown')}
Summary: {resume_json.get('summary', resume_json.get('summary_text', ''))}

Skills: {', '.join(resume_json.get('skills', []))}

Experience:
"""
        for exp in resume_json.get('experience', []):
            resume_context += f"\n- {exp.get('title', exp.get('role', ''))} at {exp.get('company', '')} ({exp.get('dates', exp.get('start_date', ''))})"
            for bullet in exp.get('bullets', [])[:2]:
                resume_context += f"\n  • {bullet}"

        # Format supplements
        supplements_text = ""
        for supp in request.supplements:
            supplements_text += f"\n**Gap: {supp.gap_area}**\n"
            supplements_text += f"Question: {supp.question}\n"
            supplements_text += f"Answer: {supp.answer}\n"

        # Format original gaps
        original_gaps_text = "\n".join([f"- {gap}" for gap in request.original_gaps])

        # Build the system prompt
        system_prompt = REANALYZE_PROMPT.format(
            resume_context=resume_context,
            supplements=supplements_text,
            company=request.company,
            role_title=request.role_title,
            job_description=request.job_description[:3000],
            original_fit_score=request.original_fit_score,
            original_gaps=original_gaps_text
        )

        # Include original resume JSON for the model to update
        user_message = f"""Re-analyze fit with the supplemented experience provided.

Original resume JSON to update:
```json
{json.dumps(resume_json, indent=2)}
```

Supplemented experience:
{supplements_text}"""

        response = call_claude(system_prompt, user_message)

        # Parse the response
        cleaned = clean_claude_json(response)
        parsed_data = json.loads(cleaned)

        # Calculate score change
        new_score = parsed_data.get('new_fit_score', request.original_fit_score)
        score_change = new_score - request.original_fit_score

        # Get updated resume JSON, fall back to original if not provided
        updated_resume = parsed_data.get('updated_resume_json', resume_json)

        return ReanalyzeWithSupplementsResponse(
            new_fit_score=new_score,
            score_change=score_change,
            updated_strengths=parsed_data.get('updated_strengths', []),
            remaining_gaps=parsed_data.get('remaining_gaps', []),
            addressed_gaps=parsed_data.get('addressed_gaps', []),
            updated_resume_json=updated_resume,
            summary=parsed_data.get('summary', f"Fit score updated from {request.original_fit_score}% to {new_score}%.")
        )

    except json.JSONDecodeError as e:
        print(f"🔥 REANALYZE JSON ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse re-analysis: {str(e)}")
    except Exception as e:
        print(f"🔥 REANALYZE ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error re-analyzing with supplements: {str(e)}")


# Legacy endpoint for backwards compatibility
@app.post("/api/documents/download")
async def download_documents_legacy(
    resume_data: str = Form(...),
    cover_letter_data: str = Form(...),
    candidate_name: str = Form("Candidate"),
    include_outreach: str = Form("false")
):
    """Legacy download endpoint using form data"""
    import io
    import zipfile
    from fastapi.responses import StreamingResponse
    
    try:
        print(f"📦 Legacy download for: {candidate_name}")
        
        # Parse JSON data
        resume_json = json.loads(resume_data)
        cover_letter_json = json.loads(cover_letter_data)
        
        resume_text = resume_json.get('full_text', '')
        cover_letter_text = cover_letter_json.get('full_text', '')
        
        # Create DOCX files
        resume_docx = create_docx_from_text(resume_text, f"{candidate_name} - Resume")
        cover_letter_docx = create_docx_from_text(cover_letter_text, f"{candidate_name} - Cover Letter")
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            resume_buffer = io.BytesIO()
            resume_docx.save(resume_buffer)
            resume_buffer.seek(0)
            zip_file.writestr(f"{candidate_name.replace(' ', '_')}_Resume.docx", resume_buffer.getvalue())
            
            cl_buffer = io.BytesIO()
            cover_letter_docx.save(cl_buffer)
            cl_buffer.seek(0)
            zip_file.writestr(f"{candidate_name.replace(' ', '_')}_Cover_Letter.docx", cl_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={candidate_name.replace(' ', '_')}_Application_Package.zip"
            }
        )
        
    except Exception as e:
        print(f"🔥 LEGACY DOWNLOAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate download: {str(e)}")


# ============================================================================
# PREP GUIDE ENDPOINTS
# ============================================================================

@app.post("/api/prep-guide/generate", response_model=PrepGuideResponse)
async def generate_prep_guide(request: PrepGuideRequest):
    """Generate a personalized interview prep guide"""
    try:
        print(f"📋 Generating prep guide for {request.company} - {request.role_title} ({request.interview_type})")

        # Build resume context
        resume_text = ""
        if request.resume_json:
            experiences = request.resume_json.get("experience", [])
            for exp in experiences:
                resume_text += f"- {exp.get('title', '')} at {exp.get('company', '')}\n"
                for bullet in exp.get("bullets", []):
                    resume_text += f"  • {bullet}\n"

            skills = request.resume_json.get("skills", [])
            if skills:
                resume_text += f"\nSkills: {', '.join(skills)}\n"

        # Interview type context
        interview_contexts = {
            "recruiter_screen": "initial phone screen focused on culture fit, basic qualifications, and motivation",
            "hiring_manager": "deep-dive on functional expertise, leadership style, and problem-solving approach",
            "technical": "technical depth, case studies, and hands-on problem solving",
            "panel": "multiple perspectives, cross-functional collaboration, and executive presence",
            "executive": "strategic vision, leadership philosophy, and cultural alignment at senior level"
        }

        interview_context = interview_contexts.get(request.interview_type, "general interview")

        prompt = f"""Generate a comprehensive interview prep guide for a candidate.

INTERVIEW DETAILS:
- Company: {request.company}
- Role: {request.role_title}
- Interview Type: {request.interview_type} ({interview_context})
- Interviewer: {request.interviewer_name or 'Unknown'} ({request.interviewer_title or 'Unknown title'})

JOB DESCRIPTION:
{request.job_description or 'Not provided'}

CANDIDATE BACKGROUND:
{resume_text or 'Not provided'}

Generate a prep guide with these sections:

1. WHAT THEY EVALUATE (5-7 bullet points of what interviewers assess in this type of interview)

2. INTRO PITCH (A 60-90 second "tell me about yourself" script that:
   - Opens with current role and key accomplishment
   - Bridges to relevant experience for this role
   - Closes with why this opportunity excites them
   - Is conversational, not robotic
   - Around 150-200 words)

3. LIKELY QUESTIONS (8-12 questions they'll probably ask, with personalized guidance on how to answer based on their specific experience. Each question should have a "guidance" field with 2-3 sentences of specific advice referencing their background.)

4. HIGH-IMPACT STORIES (3-4 STAR format stories from their experience that they should prepare. Pull from actual experience in their resume. Each story should have: title, competency it demonstrates, situation, task, action, result)

5. RED FLAGS TO AVOID (4-6 things that could hurt them in this interview)

{"6. STRATEGY SCENARIOS (3-4 case/scenario questions with suggested approaches - ONLY for hiring_manager or technical interviews)" if request.interview_type in ["hiring_manager", "technical"] else ""}

Return valid JSON matching this structure:
{{
    "what_they_evaluate": ["item1", "item2", ...],
    "intro_pitch": "The full 60-90 second intro script...",
    "likely_questions": [
        {{"question": "Question text", "guidance": "Personalized guidance on how to answer..."}},
        ...
    ],
    "stories": [
        {{
            "title": "Story title",
            "competency": "Leadership/Problem-solving/etc",
            "situation": "Context...",
            "task": "Challenge...",
            "action": "What they did...",
            "result": "Outcome with metrics..."
        }},
        ...
    ],
    "red_flags": ["Red flag 1", "Red flag 2", ...],
    {"'strategy_scenarios': [{'scenario': 'Scenario description', 'approach': 'How to approach it'}, ...]" if request.interview_type in ["hiring_manager", "technical"] else "'strategy_scenarios': null"}
}}"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            prep_data = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse JSON from response")

        print(f"✅ Prep guide generated successfully")
        return PrepGuideResponse(**prep_data)

    except json.JSONDecodeError as e:
        print(f"🔥 JSON parse error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse prep guide response")
    except Exception as e:
        print(f"🔥 Prep guide error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate prep guide: {str(e)}")


@app.post("/api/prep-guide/regenerate-intro", response_model=RegenerateIntroResponse)
async def regenerate_intro(request: RegenerateIntroRequest):
    """Regenerate just the intro pitch with a fresh take"""
    try:
        print(f"🔄 Regenerating intro for {request.company} - {request.role_title}")

        # Build resume context
        resume_text = ""
        if request.resume_json:
            experiences = request.resume_json.get("experience", [])
            for exp in experiences[:3]:  # Top 3 experiences
                resume_text += f"- {exp.get('title', '')} at {exp.get('company', '')}\n"

        prompt = f"""Generate a fresh 60-90 second "tell me about yourself" intro for an interview.

Company: {request.company}
Role: {request.role_title}
Interview Type: {request.interview_type}

Candidate's recent experience:
{resume_text or 'Not provided'}

Create a conversational, engaging intro (150-200 words) that:
- Opens with their current role and a key accomplishment
- Bridges to why their experience is relevant for this role
- Closes with genuine enthusiasm for this opportunity
- Sounds natural, not scripted
- Is different from typical generic intros

Return ONLY the intro text, no JSON or formatting."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        intro_pitch = response.content[0].text.strip()
        print(f"✅ Intro regenerated: {len(intro_pitch)} chars")

        return RegenerateIntroResponse(intro_pitch=intro_pitch)

    except Exception as e:
        print(f"🔥 Regenerate intro error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate intro: {str(e)}")


# ============================================================================
# INTERVIEWER INTELLIGENCE
# ============================================================================

class InterviewerRisk(BaseModel):
    """A risk area to prepare for"""
    risk: str
    defense: str

class InterviewerStrength(BaseModel):
    """A strength to highlight based on interviewer alignment"""
    strength: str
    why_relevant: str

class TailoredStory(BaseModel):
    """A story recommendation tailored to the interviewer"""
    story_title: str
    competency: str
    why_this_story: str

class QuestionToAsk(BaseModel):
    """A customized question for the candidate to ask the interviewer"""
    question: str
    rationale: str

class InterviewerIntelRequest(BaseModel):
    """Request to analyze an interviewer's profile"""
    linkedin_profile_text: str  # Can be from PDF extraction, pasted text, or OCR from image
    company: str
    role_title: str
    interview_type: str
    interviewer_name: str = ""
    interviewer_title: str = ""
    candidate_resume_json: Dict[str, Any] = {}
    job_description: str = ""

class InterviewerIntelResponse(BaseModel):
    """Complete interviewer intelligence report"""
    # Interviewer Summary
    interviewer_name: str
    interviewer_title: str
    current_company: str
    tenure: str
    summary: str  # Who they are and what they care about

    # Analysis
    likely_evaluation_focus: List[str]  # What they likely evaluate
    predicted_question_themes: List[str]  # Question themes based on background
    communication_style: str  # How to communicate with this person

    # Strategy
    risks: List[InterviewerRisk]  # Risk areas and defenses
    strengths_to_highlight: List[InterviewerStrength]  # Strengths to emphasize
    tailored_stories: List[TailoredStory]  # Story recommendations
    questions_to_ask: List[QuestionToAsk]  # Customized questions

    # Debrief insights (if available)
    debrief_insights: Optional[str] = None


@app.post("/api/interviewer-intelligence/analyze", response_model=InterviewerIntelResponse)
async def analyze_interviewer(request: InterviewerIntelRequest):
    """
    Analyze an interviewer's LinkedIn profile and generate strategic intelligence.
    This creates recruiter-grade coaching tailored to the specific interviewer.
    """
    try:
        print(f"🔍 Analyzing interviewer profile for {request.company} - {request.role_title}")
        print(f"   Profile text length: {len(request.linkedin_profile_text)} chars")

        # Build candidate context
        candidate_context = ""
        if request.candidate_resume_json:
            experiences = request.candidate_resume_json.get("experience", [])
            for exp in experiences[:4]:
                candidate_context += f"- {exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')[:200]}\n"
            skills = request.candidate_resume_json.get("skills", [])
            if skills:
                candidate_context += f"Skills: {', '.join(skills[:15])}\n"

        prompt = f"""You are an elite executive recruiter providing strategic interview coaching. Analyze this LinkedIn profile and create a comprehensive interviewer intelligence report.

INTERVIEWER'S LINKEDIN PROFILE:
{request.linkedin_profile_text}

INTERVIEW CONTEXT:
- Company: {request.company}
- Role the candidate is interviewing for: {request.role_title}
- Interview Type: {request.interview_type}
- Job Description: {request.job_description[:1000] if request.job_description else 'Not provided'}

CANDIDATE'S BACKGROUND:
{candidate_context if candidate_context else 'Not provided'}

Based on the interviewer's profile, generate a strategic intelligence report. Your analysis must be:
- Specific to THIS interviewer (not generic)
- Based on signals from their background, career path, and experience
- Actionable and practical for interview preparation

Return a JSON object with this exact structure:
{{
    "interviewer_name": "Their full name from profile",
    "interviewer_title": "Their current title",
    "current_company": "Their current company",
    "tenure": "How long they've been at current company (e.g., '3 years')",
    "summary": "2-3 sentence summary of who they are professionally and what they likely care about based on their career trajectory",

    "likely_evaluation_focus": [
        "What they'll likely probe based on their background (e.g., 'Execution rigor - they built teams at high-growth startups')",
        "Second focus area",
        "Third focus area",
        "Fourth focus area"
    ],

    "predicted_question_themes": [
        "Specific question theme they'll likely ask about based on their experience",
        "Second theme",
        "Third theme",
        "Fourth theme"
    ],

    "communication_style": "How to communicate with this person based on their background. Be specific about pace, level of detail, what to emphasize.",

    "risks": [
        {{
            "risk": "A specific risk area the candidate should prepare for",
            "defense": "How to address or mitigate this risk"
        }},
        {{
            "risk": "Second risk",
            "defense": "How to address it"
        }}
    ],

    "strengths_to_highlight": [
        {{
            "strength": "A strength the candidate should emphasize",
            "why_relevant": "Why this matters to this specific interviewer"
        }},
        {{
            "strength": "Second strength",
            "why_relevant": "Why it matters"
        }}
    ],

    "tailored_stories": [
        {{
            "story_title": "Title of a STAR story to prepare",
            "competency": "What competency it demonstrates",
            "why_this_story": "Why this story will resonate with this interviewer"
        }},
        {{
            "story_title": "Second story",
            "competency": "Competency",
            "why_this_story": "Why it resonates"
        }}
    ],

    "questions_to_ask": [
        {{
            "question": "A thoughtful question tailored to this interviewer's background",
            "rationale": "Why this question will resonate with them"
        }},
        {{
            "question": "Second question",
            "rationale": "Why it resonates"
        }},
        {{
            "question": "Third question",
            "rationale": "Why it resonates"
        }}
    ],

    "debrief_insights": null
}}

Return ONLY the JSON object, no additional text."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.content[0].text.strip()

        # Parse JSON response
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        intel_data = json.loads(result_text)

        print(f"✅ Interviewer intelligence generated for {intel_data.get('interviewer_name', 'Unknown')}")

        return InterviewerIntelResponse(**intel_data)

    except json.JSONDecodeError as e:
        print(f"🔥 JSON parse error: {e}")
        print(f"   Raw response: {result_text[:500]}")
        raise HTTPException(status_code=500, detail="Failed to parse interviewer analysis")
    except Exception as e:
        print(f"🔥 Interviewer analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze interviewer: {str(e)}")


@app.post("/api/interviewer-intelligence/extract-text")
async def extract_linkedin_text(file: UploadFile = File(...)):
    """
    Extract text from an uploaded LinkedIn PDF or image.
    For PDFs, uses PyMuPDF. For images, returns base64 for Claude vision.
    """
    try:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith('.pdf'):
            # Extract text from PDF using PyMuPDF
            import fitz  # PyMuPDF

            pdf_doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in pdf_doc:
                text += page.get_text()
            pdf_doc.close()

            print(f"✅ Extracted {len(text)} chars from PDF")
            return {"text": text, "type": "pdf"}

        elif any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
            # For images, we'll use Claude's vision capability
            import base64
            base64_image = base64.b64encode(content).decode('utf-8')

            # Determine media type
            if filename.endswith('.png'):
                media_type = "image/png"
            elif filename.endswith('.webp'):
                media_type = "image/webp"
            else:
                media_type = "image/jpeg"

            # Use Claude to extract text from image
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": """Extract ALL text from this LinkedIn profile screenshot. Include:
- Name and headline
- About section (full text)
- Experience section (all roles, companies, dates, descriptions)
- Education
- Skills
- Any other visible information

Format as plain text, preserving the structure. Be thorough - capture every piece of text visible."""
                        }
                    ]
                }]
            )

            extracted_text = response.content[0].text
            print(f"✅ Extracted {len(extracted_text)} chars from image via vision")
            return {"text": extracted_text, "type": "image"}

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or image.")

    except Exception as e:
        print(f"🔥 Text extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")


# ============================================================================
# ASK HENRY - FLOATING CHAT ASSISTANT
# ============================================================================

class AskHenryContext(BaseModel):
    """Context about where the user is in the app."""
    current_page: str
    page_description: str
    company: Optional[str] = None
    role: Optional[str] = None
    has_analysis: bool = False
    has_resume: bool = False
    has_pipeline: bool = False
    user_name: Optional[str] = None


class AskHenryMessage(BaseModel):
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class AskHenryRequest(BaseModel):
    """Request for Ask Henry chat."""
    message: str
    conversation_history: List[AskHenryMessage] = []
    context: AskHenryContext
    analysis_data: Optional[Dict[str, Any]] = None
    resume_data: Optional[Dict[str, Any]] = None
    user_profile: Optional[Dict[str, Any]] = None  # Includes emotional state/situation
    pipeline_data: Optional[Dict[str, Any]] = None  # Application pipeline metrics and apps


class AskHenryResponse(BaseModel):
    """Response from Ask Henry."""
    response: str


ASK_HENRY_SYSTEM_PROMPT = """You are Henry, an expert career coach built into HenryAI. You're warm, empathetic, direct, and strategic. You help job seekers with their applications, positioning, interview prep, and career strategy.

USER INFO:
- Name: {user_name}

CURRENT CONTEXT:
- User is on: {current_page} ({page_description})
- Target Company: {company}
- Target Role: {role}
- Has job analysis: {has_analysis}
- Has resume uploaded: {has_resume}
- Has pipeline data: {has_pipeline}

{analysis_context}

{pipeline_context}

{emotional_context}

YOUR PERSONALITY:
- Empathetic first - acknowledge emotions and difficult situations before jumping to solutions
- Warm but direct - no fluff, but always human
- Strategic thinker - tie advice to their specific situation
- Encouraging but honest - if something needs work, say so kindly
- PERSONALIZED - always use the user's name when starting responses. Begin with something like "[Name], that's a great question..." or "[Name], I can see your pipeline..." Don't just say "Hey" or start without acknowledging them.

RESPONSE GUIDELINES:
1. PERSONALIZE - Start responses with the user's name and acknowledge their specific question before answering.
2. USE THE DATA - If you have pipeline data, reference it specifically. Don't ask questions you already have answers to.
3. BE CONCISE - 2-3 short sentences max for simple questions. Even complex answers should be under 100 words.
4. Empathy before advice - If someone shares something difficult (job loss, long unemployment, rejection), acknowledge it genuinely first. Don't immediately launch into solutions.
5. One thing at a time - ask ONE follow-up question, not multiple
6. Skip the bullet lists unless truly needed - conversational tone is better
7. No sales pitches - don't list all your features. Help with what they're asking.
8. Reference their specific situation and data naturally

FORMATTING RULES (STRICT):
- Use proper grammar and punctuation. Write in complete sentences.
- DO NOT use asterisks or stars for emphasis. No **bold** or *italic* formatting.
- DO NOT use em dashes. Use periods or commas instead.
- DO NOT use bullet points or numbered lists unless absolutely necessary.
- Write like you're texting a friend, not formatting a document.

EXAMPLES OF GOOD RESPONSES:
"Sarah, that's a great question. Looking at your pipeline, you've got 4 active applications with 1 in interviews. Your Trade Desk role is the hottest right now. I'd focus your energy there while keeping the others warm."
"Mike, I can see why you're wondering. With a 0% interview rate so far, the focus should be on your outreach strategy. Have you tried reaching out directly to hiring managers?"
"Jen, your pipeline looks healthy. You've got good momentum with 2 in interview stages. The MongoDB one at 26 days without response might be ghosted, but The Trade Desk is moving. Keep that one priority."

You're available as a floating chat on every page. Be contextually aware, use the data you have, and be conversational like a smart friend who happens to be a career expert."""


@app.post("/api/ask-henry", response_model=AskHenryResponse)
async def ask_henry(request: AskHenryRequest):
    """
    ASK HENRY: Contextual AI assistant available from any page.

    Provides strategic career coaching based on:
    - Current page/section the user is viewing
    - Their job analysis data (if available)
    - Their resume data (if available)
    - Their pipeline data (if available)
    - Conversation history for continuity
    """
    print(f"💬 Ask Henry: {request.context.current_page} - {request.message[:50]}...")

    # Build analysis context string
    analysis_context = ""
    if request.analysis_data and request.context.has_analysis:
        analysis_context = f"""
ANALYSIS DATA AVAILABLE:
- Company: {request.analysis_data.get('_company_name', 'Unknown')}
- Role: {request.analysis_data.get('role_title', 'Unknown')}
- Fit Score: {request.analysis_data.get('fit_score', 'N/A')}
- Key Strengths: {', '.join(request.analysis_data.get('strengths', [])[:3])}
- Key Gaps: {', '.join(request.analysis_data.get('gaps', [])[:3])}
"""

    if request.resume_data and request.context.has_resume:
        analysis_context += f"""
RESUME DATA:
- Candidate Name: {request.resume_data.get('name', 'Unknown')}
- Current/Recent Role: {request.resume_data.get('experience', [{}])[0].get('title', 'Unknown') if request.resume_data.get('experience') else 'Unknown'}
"""

    # Build pipeline context from pipeline data
    pipeline_context = ""
    if request.pipeline_data and request.context.has_pipeline:
        pd = request.pipeline_data
        pipeline_context = f"""
PIPELINE DATA (USE THIS TO GIVE SPECIFIC, INFORMED ANSWERS):
- Total Applications: {pd.get('total', 0)}
- Active Applications: {pd.get('active', 0)}
- In Interview Stages: {pd.get('interviewing', 0)}
- Applied (waiting for response): {pd.get('applied', 0)}
- Rejected: {pd.get('rejected', 0)}
- Likely Ghosted: {pd.get('ghosted', 0)}
- Hot/Priority: {pd.get('hot', 0)}
- Average Fit Score: {pd.get('avgFitScore', 0)}%
- Interview Rate: {pd.get('interviewRate', 0)}%
- Summary: {pd.get('summary', 'No summary available')}

TOP APPLICATIONS IN PIPELINE:
"""
        top_apps = pd.get('topApps', [])
        for app in top_apps:
            pipeline_context += f"- {app.get('role', 'Unknown')} at {app.get('company', 'Unknown')}: {app.get('status', 'Unknown')} ({app.get('fitScore', 'N/A')}% fit, {app.get('daysSinceUpdate', 0)}d since update)\n"

    # Build emotional context from user profile
    emotional_context = ""
    if request.user_profile:
        situation = request.user_profile.get('situation', {})
        holding_up = situation.get('holding_up')
        timeline = situation.get('timeline')
        confidence = situation.get('confidence')

        if holding_up or timeline or confidence:
            emotional_context = "USER'S EMOTIONAL STATE (adjust your tone accordingly):\n"

            if holding_up == 'struggling':
                emotional_context += "- They're struggling emotionally. Be extra gentle and encouraging. Don't be pushy.\n"
            elif holding_up == 'hanging_in':
                emotional_context += "- They're hanging in there but it's hard. Be supportive but action-oriented.\n"
            elif holding_up == 'doing_okay':
                emotional_context += "- They're doing okay. You can be more direct and strategic.\n"

            if timeline == 'urgent':
                emotional_context += "- URGENT financial pressure. Prioritize speed but don't let them take bad roles out of desperation.\n"
            elif timeline == 'actively_looking':
                emotional_context += "- Actively looking with some runway. Balance speed with quality.\n"
            elif timeline == 'exploring':
                emotional_context += "- Just exploring, no rush. Can be more strategic and selective.\n"

            if confidence == 'low':
                emotional_context += "- Low confidence right now. Be encouraging. Remind them it's the market, not them. Build them up.\n"
            elif confidence == 'building':
                emotional_context += "- Confidence is building. Reinforce wins and progress.\n"
            elif confidence == 'confident':
                emotional_context += "- They're feeling confident. Match their energy, be direct and strategic.\n"

    # Format system prompt
    system_prompt = ASK_HENRY_SYSTEM_PROMPT.format(
        user_name=request.context.user_name or "there",
        current_page=request.context.current_page,
        page_description=request.context.page_description,
        company=request.context.company or "Not specified",
        role=request.context.role or "Not specified",
        has_analysis="Yes" if request.context.has_analysis else "No",
        has_resume="Yes" if request.context.has_resume else "No",
        has_pipeline="Yes" if request.context.has_pipeline else "No",
        analysis_context=analysis_context,
        pipeline_context=pipeline_context,
        emotional_context=emotional_context
    )

    # Build messages
    messages = []
    for msg in request.conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    messages.append({
        "role": "user",
        "content": request.message
    })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        assistant_response = response.content[0].text
        print(f"✅ Ask Henry response: {len(assistant_response)} chars")

        return AskHenryResponse(response=assistant_response)

    except Exception as e:
        print(f"🔥 Ask Henry error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response: {str(e)}")


# ============================================================================
# RESUME BUILDER - CONVERSATIONAL ONBOARDING
# ============================================================================

class ResumeChatMessage(BaseModel):
    """Single message in resume chat conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class ExtractedSkill(BaseModel):
    """A skill extracted from conversation."""
    skill_name: str
    category: str
    evidence: str
    confidence: str = "medium"  # high, medium, low


class ResumeChatRequest(BaseModel):
    """Request for resume builder conversation."""
    conversation_history: List[ResumeChatMessage]
    current_state: str = "START"
    extracted_data: Optional[Dict[str, Any]] = None


class ResumeChatResponse(BaseModel):
    """Response from resume builder conversation."""
    response: str
    next_state: str
    extracted_data: Dict[str, Any]
    skills_extracted: List[ExtractedSkill] = []
    suggested_responses: List[str] = []


# Skill taxonomy (simplified version - full version in frontend/docs)
SKILL_CATEGORIES = {
    "leadership": ["Team Coordination", "Training", "Delegation", "Mentoring", "Decision Making"],
    "operations": ["Process Improvement", "Inventory Management", "Quality Control", "Scheduling", "Logistics"],
    "customer": ["Customer Service", "Conflict Resolution", "Client Relations", "Upselling", "Account Management"],
    "communication": ["Written Communication", "Verbal Communication", "Presentation", "Negotiation", "Active Listening"],
    "technical": ["Data Analysis", "Software Skills", "Technical Writing", "Problem Solving", "Research"],
    "financial": ["Budgeting", "Financial Analysis", "Cash Handling", "Cost Reduction", "Forecasting"],
    "sales": ["Sales", "Lead Generation", "Account Growth", "Pipeline Management", "Closing"],
    "marketing": ["Marketing", "Social Media", "Content Creation", "Brand Management", "Campaign Management"],
    "administrative": ["Organization", "Documentation", "Scheduling", "Filing", "Compliance"],
    "self_management": ["Time Management", "Adaptability", "Reliability", "Initiative", "Stress Management"]
}

RESUME_CHAT_SYSTEM_PROMPT = """You are Henry, a warm and supportive career coach helping {candidate_name} build their resume through conversation. Your goal is to extract their skills and work experience through natural dialogue.

## CANDIDATE NAME: {candidate_name}
Use their name naturally throughout the conversation to make it personal and engaging. Don't overuse it, but include it every few responses to maintain connection.

## YOUR PERSONALITY
- Warm, encouraging, and direct
- Find the positive in any experience
- Never judge unconventional work history
- Celebrate transferable skills people don't realize they have
- Use casual, friendly language
- IMPORTANT: Never use em dashes (—) in your responses. Use commas, periods, or separate sentences instead.

## CONVERSATION STATES (Move quickly - don't linger)
The conversation progresses through these states:
1. CURRENT_ROLE: What is their current/most recent job? (1-2 exchanges max)
2. RESPONSIBILITIES: What did they do day-to-day? Get 2-3 key duties, then move on
3. ACHIEVEMENTS: One specific win or accomplishment, then move on
4. PREVIOUS_ROLES: Quick check on earlier experience (skip if entry-level)
5. EDUCATION: Brief education check (skip details if they have work experience)
6. SKILLS_SUMMARY: Summarize what you've learned about them
7. ROLE_GOALS: What kind of work do they want?
8. COMPLETE: Wrap up

IMPORTANT: Don't ask too many follow-up questions for each job. Get the essentials and move forward. The goal is a 5-7 minute conversation, not an interrogation.

## SKILL EXTRACTION
As the user shares experiences, identify transferable skills. Look for indicators like:
- "Managed" / "supervised" / "trained" → Leadership, Training
- "Handled complaints" / "dealt with customers" → Customer Service, Conflict Resolution
- "Organized" / "scheduled" / "coordinated" → Organization, Scheduling
- "Sold" / "upsold" / "recommended" → Sales, Upselling
- "Fixed problems" / "figured out" → Problem Solving
- "Made sure" / "ensured" / "quality" → Quality Control
- "Communicated" / "explained" / "presented" → Communication
- Working under pressure, multitasking → Stress Management, Time Management

## RESPONSE FORMAT
You must respond with valid JSON in this exact format:
{{
    "response": "Your conversational response to the user",
    "next_state": "CURRENT_STATE or next state in flow",
    "extracted_data": {{
        "contact": {{}},
        "experiences": [
            {{
                "title": "Job title if known",
                "company": "Company name if known",
                "industry": "Industry type",
                "duration": "Time period",
                "responsibilities": ["list of duties mentioned"],
                "achievements": ["specific accomplishments"]
            }}
        ],
        "skills": ["list of skill names extracted"],
        "education": []
    }},
    "skills_extracted": [
        {{
            "skill_name": "Name of skill",
            "category": "category from list",
            "evidence": "What they said that shows this skill",
            "confidence": "high/medium/low"
        }}
    ],
    "suggested_responses": ["Example answer the user might say", "Another possible user response"]
}}

## CURRENT CONVERSATION STATE: {current_state}

## PREVIOUSLY EXTRACTED DATA:
{extracted_data}

## IMPORTANT GUIDELINES
1. Keep responses concise (1-2 sentences max) - this is a spoken conversation
2. Use {candidate_name}'s name every 2-3 responses to stay personal
3. Ask ONE question at a time, never multiple questions
4. Move to the next state after 1-2 exchanges per topic - don't over-probe
5. Always be encouraging - find value in any work experience
6. If they give a short answer, that's fine - extract what you can and move on
7. For gig workers/non-traditional work, emphasize customer service, time management, self-direction
8. When transitioning to COMPLETE, give {candidate_name} a brief, warm summary of their strengths
9. CRITICAL - suggested_responses must be example ANSWERS the user might give, NOT questions. These are quick-reply buttons to help the user respond. Examples:
   - Good: "I managed a small team", "I worked in retail for 3 years", "I'm self-taught mostly"
   - Bad: "Tell me about your education", "What skills do you have?", "How long did you work there?"

Remember: This is a friendly 5-7 minute chat, not an interview. Help {candidate_name} see the professional value in their experiences without making them feel interrogated."""


@app.post("/api/resume-chat", response_model=ResumeChatResponse)
async def resume_chat(request: ResumeChatRequest):
    """
    RESUME CHAT: Conversational resume building through natural dialogue.

    Guides users through sharing their experience and extracts skills
    for resume generation.
    """
    print(f"📝 Resume Chat: State={request.current_state}, Messages={len(request.conversation_history)}")

    # Extract candidate name from contact info
    extracted_data = request.extracted_data or {}
    contact = extracted_data.get("contact", {})
    candidate_name = contact.get("nickname") or contact.get("firstName") or "there"

    # Format extracted data for prompt
    extracted_data_str = json.dumps(extracted_data, indent=2)

    system_prompt = RESUME_CHAT_SYSTEM_PROMPT.format(
        candidate_name=candidate_name,
        current_state=request.current_state,
        extracted_data=extracted_data_str
    )

    # Build messages for Claude
    messages = []
    for msg in request.conversation_history:
        messages.append({
            "role": msg.role if msg.role in ["user", "assistant"] else "user",
            "content": msg.content
        })

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )

        response_text = response.content[0].text
        print(f"✅ Resume Chat raw response: {response_text[:200]}...")

        # Parse JSON response
        try:
            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(response_text)

            # Validate and extract fields
            return ResumeChatResponse(
                response=parsed.get("response", "I'd love to hear more about your experience."),
                next_state=parsed.get("next_state", request.current_state),
                extracted_data=parsed.get("extracted_data", request.extracted_data or {}),
                skills_extracted=[
                    ExtractedSkill(**skill) for skill in parsed.get("skills_extracted", [])
                ],
                suggested_responses=parsed.get("suggested_responses", [])
            )

        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON response: {e}")
            # Return a graceful fallback
            return ResumeChatResponse(
                response=response_text if len(response_text) < 500 else "Tell me more about what you did in that role.",
                next_state=request.current_state,
                extracted_data=request.extracted_data or {},
                skills_extracted=[],
                suggested_responses=["I was responsible for...", "My main duties included...", "I mostly did..."]
            )

    except Exception as e:
        print(f"🔥 Resume Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process conversation: {str(e)}")


class GenerateResumeFromChatRequest(BaseModel):
    """Request to generate resume from chat-extracted data."""
    extracted_data: Dict[str, Any]
    target_role: Optional[str] = None


class GenerateResumeFromChatResponse(BaseModel):
    """Generated resume from conversation data."""
    resume_text: str
    resume_html: str
    sections: Dict[str, Any]


RESUME_GENERATION_PROMPT = """Based on the following extracted data from a conversation, generate a professional resume.

## EXTRACTED DATA:
{extracted_data}

## TARGET ROLE (if specified):
{target_role}

## GUIDELINES:
1. Create a professional resume with clear sections
2. Use the skills and experience shared in conversation
3. Write achievement-focused bullets using the STAR format where possible
4. Don't fabricate or embellish - only use what was actually shared
5. If target role is specified, emphasize relevant skills
6. Keep it concise - 1 page equivalent

## OUTPUT FORMAT:
Return JSON with this structure:
{{
    "resume_text": "Plain text version of the resume",
    "resume_html": "HTML formatted version with basic styling",
    "sections": {{
        "summary": "Professional summary paragraph",
        "experience": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "dates": "Date range",
                "bullets": ["Achievement 1", "Achievement 2"]
            }}
        ],
        "skills": ["Skill 1", "Skill 2"],
        "education": "Education details if any"
    }}
}}"""


@app.post("/api/generate-resume-from-chat", response_model=GenerateResumeFromChatResponse)
async def generate_resume_from_chat(request: GenerateResumeFromChatRequest):
    """
    Generate a professional resume from conversation-extracted data.
    """
    print(f"📄 Generating resume from chat data...")

    system_prompt = RESUME_GENERATION_PROMPT.format(
        extracted_data=json.dumps(request.extracted_data, indent=2),
        target_role=request.target_role or "Not specified - create general resume"
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": "Generate the resume based on the conversation data provided in the system prompt."
            }],
            system=system_prompt
        )

        response_text = response.content[0].text

        # Parse JSON response
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(response_text)

            return GenerateResumeFromChatResponse(
                resume_text=parsed.get("resume_text", ""),
                resume_html=parsed.get("resume_html", ""),
                sections=parsed.get("sections", {})
            )

        except json.JSONDecodeError:
            # Create basic resume from extracted data
            name = request.extracted_data.get("contact", {}).get("name", "Candidate")
            skills = request.extracted_data.get("skills", [])
            experiences = request.extracted_data.get("experiences", [])

            basic_text = f"{name}\n\n"
            if skills:
                basic_text += "SKILLS: " + ", ".join(skills) + "\n\n"
            if experiences:
                basic_text += "EXPERIENCE:\n"
                for exp in experiences:
                    basic_text += f"{exp.get('title', 'Role')} at {exp.get('company', 'Company')}\n"
                    for resp in exp.get("responsibilities", []):
                        basic_text += f"  - {resp}\n"

            return GenerateResumeFromChatResponse(
                resume_text=basic_text,
                resume_html=f"<pre>{basic_text}</pre>",
                sections={
                    "summary": "",
                    "experience": experiences,
                    "skills": skills,
                    "education": ""
                }
            )

    except Exception as e:
        print(f"🔥 Resume generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate resume: {str(e)}")


# ============================================================================
# VOICE ENDPOINTS (Whisper STT + OpenAI TTS)
# ============================================================================

# Import OpenAI for voice features
try:
    import openai
    OPENAI_CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    OPENAI_CLIENT = None
    print("⚠️ OpenAI library not installed - voice features disabled")


class SpeakRequest(BaseModel):
    """Request for text-to-speech."""
    text: str
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer


@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio using OpenAI Whisper.
    Accepts audio file uploads and returns transcribed text.
    """
    if not OPENAI_CLIENT:
        raise HTTPException(status_code=503, detail="Voice features not configured. Please set OPENAI_API_KEY.")

    print(f"🎙️ Transcribing audio: {audio.filename}, {audio.content_type}")

    try:
        # Read audio content
        audio_content = await audio.read()

        # Create a temporary file-like object for OpenAI
        audio_file = io.BytesIO(audio_content)
        audio_file.name = audio.filename or "recording.webm"

        # Call Whisper API
        transcription = OPENAI_CLIENT.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

        print(f"✅ Transcribed: {transcription[:100]}...")

        return {"text": transcription}

    except Exception as e:
        print(f"🔥 Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/api/speak")
async def text_to_speech(request: SpeakRequest):
    """
    Convert text to speech using OpenAI TTS.
    Returns audio stream.
    """
    if not OPENAI_CLIENT:
        raise HTTPException(status_code=503, detail="Voice features not configured. Please set OPENAI_API_KEY.")

    print(f"🔊 TTS request: {request.text[:50]}... (voice: {request.voice})")

    try:
        # Call OpenAI TTS API
        response = OPENAI_CLIENT.audio.speech.create(
            model="tts-1",
            voice=request.voice,
            input=request.text
        )

        # Stream the audio response
        audio_content = response.content

        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except Exception as e:
        print(f"🔥 TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Henry Job Search Engine API starting on http://localhost:{port}")
    print(f"📚 API docs available at http://localhost:{port}/docs")
    print(f"🔑 Using Anthropic API key: {API_KEY[:20]}...")
    if OPENAI_API_KEY:
        print(f"🎙️ Voice features enabled (OpenAI key: {OPENAI_API_KEY[:20]}...)")
    else:
        print("⚠️ Voice features disabled (no OPENAI_API_KEY)")
    uvicorn.run(app, host="0.0.0.0", port=port)
