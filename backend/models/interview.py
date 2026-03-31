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
    rationale: Optional[str] = None  # Alias for compatibility
    why_this_works: Optional[str] = None  # New field for interviewer intel


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


class RiskToAddress(BaseModel):
    """Single risk the candidate should proactively address"""
    concern: str
    how_to_address: str


class InterviewerIntelResponse(BaseModel):
    """
    Interviewer intelligence report per spec: Interviewer LinkedIn Analysis & Personalized Prep.
    Goal: Help candidate answer "How do I earn trust with this interviewer?"
    """
    # Interviewer Info
    interviewer_name: str
    interviewer_title: str
    current_company: str
    tenure: str

    # Core Analysis (new spec format)
    how_they_screen: str  # What they optimize for, what makes them lean in vs tune out
    what_to_emphasize: List[str]  # 3 themes to lean into
    what_to_deemphasize: List[str]  # Things less relevant for this interviewer
    risk_to_address: RiskToAddress  # One potential concern and how to address it
    story_framing: str  # Specific framing guidance, not a script
    questions_to_ask: List[QuestionToAsk]  # Interviewer-specific questions
    summary: str  # 2-3 sentence coaching summary

    # Legacy fields for backwards compatibility (optional)
    likely_evaluation_focus: Optional[List[str]] = None
    predicted_question_themes: Optional[List[str]] = None
    communication_style: Optional[str] = None
    risks: Optional[List[InterviewerRisk]] = None
    strengths_to_highlight: Optional[List[InterviewerStrength]] = None
    tailored_stories: Optional[List[TailoredStory]] = None

    # Debrief insights (if available)
    debrief_insights: Optional[str] = None


# ============================================
# EVALUATION CRITERIA ENGINE
# ============================================

class EvaluationCriterion(BaseModel):
    """A single capability the interviewer is assessing"""
    capability: str = Field(description="What they're evaluating, e.g. 'Scales hiring without quality loss'")
    description: str = Field(description="Why this matters for the role")
    priority: str = Field(description="must-have | differentiator | nice-to-have")
    evidence_required: str = Field(description="What proof looks like for this capability")
    interview_type_weight: float = Field(default=1.0, ge=0, le=2.0, description="How much this matters for the interview type")


class ProofRequirement(BaseModel):
    """Maps a capability to available proof in the story bank"""
    capability: str
    required_story_count: int = Field(default=1, ge=1, le=3)
    current_story_ids: List[str] = Field(default_factory=list)
    gap_severity: str = Field(default="moderate", description="critical | moderate | minor")
    suggestion: str = Field(default="", description="How to fill the gap")


class EvaluationCriteriaRequest(BaseModel):
    """Request to generate evaluation criteria and proof requirements"""
    job_description: str
    interview_type: str = "hiring_manager"
    company: str = ""
    role_title: str = ""
    role_level: str = ""
    resume_json: Dict[str, Any] = {}
    story_summaries: Optional[List[Dict[str, Any]]] = Field(None, description="Story bank summaries for proof mapping")


class Recommendations(BaseModel):
    """Actionable recommendations: what to use, avoid, and fix"""
    use: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    fix: List[str] = Field(default_factory=list)


class EvaluationCriteriaResponse(BaseModel):
    """Response with evaluation criteria and proof requirements"""
    criteria: List[EvaluationCriterion]
    proof_requirements: List[ProofRequirement]
    coverage_score: int = Field(ge=0, le=100, description="How well the candidate's stories cover the criteria")
    critical_gaps: List[str] = Field(default_factory=list, description="Capabilities with no proof")
    interview_strategy: Optional[str] = Field(None, description="1-2 sentence positioning strategy")
    recommendations: Optional[Recommendations] = None
    next_actions: List[str] = Field(default_factory=list, description="Max 3 specific, time-bound actions")


# ============================================
# STORY SELECTION ENGINE
# ============================================

class RecommendedStorySelection(BaseModel):
    """A story recommended for a specific interview"""
    story_id: str
    story_name: str
    reason: str
    proof_strength: int = 0
    relevance_score: int = 0
    past_performance: str = "unknown"
    final_score: int = 0


class StoryToAvoid(BaseModel):
    """A story the candidate should NOT use"""
    story_id: str
    story_name: str = ""
    reason: str


class StorySelectionRequest(BaseModel):
    """Request for interview-specific story selection"""
    job_description: str = ""
    evaluation_criteria: Optional[List[Dict[str, Any]]] = None
    story_bank: List[Dict[str, Any]] = []
    role_level: str = ""


class StorySelectionResponse(BaseModel):
    """Response with ranked story recommendations"""
    recommended_stories: List[RecommendedStorySelection]
    stories_to_avoid: List[StoryToAvoid] = []
    gaps: List[str] = []
    next_actions: List[str] = []


# ============================================
# PUSHBACK SIMULATION
# ============================================

class PushbackRequest(BaseModel):
    """Request for interview pushback simulation"""
    question: str
    user_answer: str
    role_level: str = "senior"


class PushbackResponse(BaseModel):
    """Response with pushback questions and ideal responses"""
    pushbacks: List[str]
    ideal_responses: List[str]
    next_actions: List[str] = []


# ============================================
# CANDIDATE CONFIDENCE SCORE
# ============================================

class ConfidenceBreakdown(BaseModel):
    execution: int = Field(ge=0, le=100)
    leadership: int = Field(ge=0, le=100)
    strategy: int = Field(ge=0, le=100)


class ConfidenceScoreRequest(BaseModel):
    """Request for candidate confidence scoring"""
    evaluation_criteria: Optional[List[Dict[str, Any]]] = None
    story_bank: List[Dict[str, Any]] = []
    performance_history: List[Dict[str, Any]] = []
    job_description: str = ""
    role_level: str = ""


class ConfidenceScoreResponse(BaseModel):
    """Response with hiring committee confidence assessment"""
    score: int = Field(ge=0, le=100)
    breakdown: ConfidenceBreakdown
    risk_areas: List[str] = []
    likely_outcome: str = Field(description="strong_hire | mixed | no_hire")
    outcome_rationale: str = ""
    next_actions: List[str] = []


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


# ============================================
# VOICE DELIVERY ANALYSIS
# ============================================

class DeliveryScores(BaseModel):
    """Delivery analysis scores from voice input"""
    confidence: int = Field(ge=0, le=100, description="How confident the speaker sounds")
    pace: int = Field(ge=0, le=100, description="Pacing quality — 50 is ideal, 0 too slow, 100 too fast")
    clarity: int = Field(ge=0, le=100, description="How clear and articulate the speech is")
    energy: int = Field(ge=0, le=100, description="Energy and engagement level")
    conciseness: int = Field(default=70, ge=0, le=100, description="Time-to-value ratio — did they say it efficiently")
    filler_word_count: int = Field(ge=0, description="Number of filler words detected")
    monotone_risk: bool = Field(default=False, description="Whether delivery sounds monotone")


class ContentScores(BaseModel):
    """Content quality scores — what they said"""
    clarity: int = Field(ge=0, le=100, description="How clear and scannable the answer is")
    structure: int = Field(ge=0, le=100, description="STAR adherence, logical flow")
    impact: int = Field(ge=0, le=100, description="Does the answer prove business value")
    credibility: int = Field(ge=0, le=100, description="Does this sound real and earned")


class CombinedScore(BaseModel):
    """Master scoring model: content gets you in the door, delivery gets you the offer"""
    final_score: int = Field(ge=0, le=100, description="Weighted combination of content + delivery")
    content_score: int = Field(ge=0, le=100, description="What they said")
    delivery_score: int = Field(ge=0, le=100, description="How they said it")
    content_breakdown: Optional[ContentScores] = None
    delivery_breakdown: Optional[DeliveryScores] = None
    verdict: str = Field(description="advance | hold | reject")
    recruiter_screen: str = Field(default="pass", description="pass | fail — would this pass a recruiter screen")
    red_flags: List[str] = Field(default_factory=list, description="Issues that override scores")
    top_issues: List[str] = Field(default_factory=list, description="Top 3 things to fix")
    next_actions: List[str] = Field(default_factory=list, description="Max 3 specific actions")


class DeliveryAnalysisRequest(BaseModel):
    """Request for voice delivery analysis"""
    transcript: str
    question: Optional[str] = None
    role_level: str = "senior"
    duration_seconds: Optional[int] = None


class DeliveryAnalysisResponse(BaseModel):
    """Response from voice delivery analysis"""
    delivery_scores: DeliveryScores
    combined: Optional[CombinedScore] = None
    delivery_feedback: List[str]
    risks: List[str]
    next_actions: List[str]


class IntroDeliveryRequest(BaseModel):
    """Request for intro delivery evaluation"""
    transcript: str
    target_role: str = ""
    company: str = ""
    duration_seconds: Optional[int] = None


class IntroDeliveryResponse(BaseModel):
    """Response from intro delivery evaluation"""
    intro_score: int = Field(ge=0, le=100)
    first_impression: str = Field(description="strong | average | weak")
    combined: Optional[CombinedScore] = None
    delivery_issues: List[str]
    content_issues: List[str]
    improved_intro: str
    next_actions: List[str]


class PushbackVoiceRequest(BaseModel):
    """Request for pushback drill with voice input"""
    question: str
    transcript: str
    role_level: str = "senior"
    duration_seconds: Optional[int] = None


class PushbackVoiceResponse(BaseModel):
    """Response from pushback voice drill"""
    pushback_question: str
    previous_mistake: str
    improved_response_guidance: str
    delivery_scores: DeliveryScores
    next_actions: List[str]


class StoryDeliveryRequest(BaseModel):
    """Request to validate story delivery via voice"""
    story_id: str = ""
    title: str = ""
    transcript: str
    duration_seconds: Optional[int] = None


class StoryDeliveryResponse(BaseModel):
    """Response from story delivery validation"""
    delivery_strength: int = Field(ge=0, le=100)
    risk_flags: List[str]
    recommendation: str = Field(description="use | refine | avoid")
    next_actions: List[str]
