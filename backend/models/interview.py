"""Interview-related Pydantic models"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


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


# Interview Prep models
class InterviewPrepRequest(BaseModel):
    """Request for generating interview prep materials"""
    resume_json: Dict[str, Any]
    job_description: Optional[str] = None  # Optional when using provisional_profile
    company: str
    role_title: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    jd_analysis: Optional[Dict[str, Any]] = None
    # Command Center v2.0 fields
    jd_source: Optional[str] = None  # user_provided, url_fetched, inferred, missing
    provisional_profile: Optional[Dict[str, Any]] = None  # When jd_source is inferred/missing
    application_id: Optional[str] = None  # For tracking
    # Debrief Intelligence (Phase 2.3)
    past_debriefs: Optional[List[Dict[str, Any]]] = None  # Past debriefs for this company or similar roles


class RedFlagMitigation(BaseModel):
    flag: str
    mitigation: str


class QuestionToAsk(BaseModel):
    question: str
    why: Optional[str] = None
    rationale: Optional[str] = None  # Alias for InterviewerIntelResponse compatibility


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
    # Command Center v2.0 fields
    confidence: Optional[str] = None  # "directional" or "refined"
    ui_note: Optional[str] = None  # Displayed to user when prep is directional


# Intro Sell models
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


# Interview Debrief models
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


# Debrief Chat models
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


# Prep Guide models
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


# Interviewer Intelligence models
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


# Debrief Extraction models
class DebriefExtractionRequest(BaseModel):
    """Request to extract structured data from debrief conversation."""
    conversation: str  # Raw conversation text
    company: str
    role: Optional[str] = None
    interview_type: Optional[str] = None  # If known from context
    application_id: Optional[str] = None


class DebriefExtractionResponse(BaseModel):
    """Response with structured debrief data and insights."""
    structured_data: Dict[str, Any]
    insights: List[str]
    stories_extracted: List[Dict[str, Any]]


class PatternAnalysisResponse(BaseModel):
    """Response with cross-interview pattern analysis."""
    weak_categories: List[Dict[str, Any]]
    strong_categories: List[Dict[str, Any]]
    story_usage: List[Dict[str, Any]]
    confidence_trend: Optional[Dict[str, Any]] = None
    total_debriefs: int
    insights: List[str]
