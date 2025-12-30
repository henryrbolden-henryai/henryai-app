"""Mock Interview Pydantic models"""

from typing import Optional, List
from pydantic import BaseModel, Field
from typing import Dict, Any


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
