# Mock Interview — Claude Code Implementation Instructions

**Version:** 1.0  
**Date:** December 2024  
**Target:** Claude Code  
**Purpose:** Step-by-step instructions for implementing mock interview endpoints

---

## **Overview**

Implement a conversational mock interview feature with the following capabilities:
1. Start mock interview session (generates first question)
2. Submit responses and get follow-up questions (up to 3 follow-ups per question)
3. Get comprehensive feedback after each question
4. Move to next question (total 5 questions per session)
5. End session with overall feedback
6. View session history

**Critical Requirements:**
- All questions must be realistic for interview stage
- All feedback must be specific and actionable
- Never fabricate experience
- Maintain conversation state across multiple turns
- Generate JSON responses only (no markdown)

---

## **Step 1: Database Setup**

Create a new migration file for mock interview tables.

```bash
alembic revision -m "add_mock_interview_tables"
```

In the migration file, add these table definitions:

```python
def upgrade():
    # Mock interview sessions
    op.create_table(
        'mock_interview_sessions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('job_application_id', sa.UUID(), nullable=False),
        sa.Column('interview_stage', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('session_feedback', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_application_id'], ['job_applications.id'], ondelete='CASCADE'),
        sa.CheckConstraint("interview_stage IN ('recruiter_screen', 'hiring_manager')", name='valid_stage'),
        sa.CheckConstraint("difficulty_level IN ('easy', 'medium', 'hard')", name='valid_difficulty')
    )
    
    # Individual questions within a session
    op.create_table(
        'mock_interview_questions',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('competency_tested', sa.String(100), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('asked_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['mock_interview_sessions.id'], ondelete='CASCADE'),
        sa.CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name='valid_difficulty_q')
    )
    
    # Candidate responses to questions (includes follow-ups)
    op.create_table(
        'mock_interview_responses',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_id', sa.UUID(), nullable=False),
        sa.Column('response_number', sa.Integer(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('response_type', sa.String(20), nullable=False, server_default='text'),
        sa.Column('responded_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['question_id'], ['mock_interview_questions.id'], ondelete='CASCADE')
    )
    
    # Analysis and feedback per question
    op.create_table(
        'mock_interview_analysis',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_id', sa.UUID(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('level_demonstrated', sa.String(10), nullable=True),
        sa.Column('gaps', sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('strengths', sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('follow_up_questions', sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('revised_answer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['question_id'], ['mock_interview_questions.id'], ondelete='CASCADE'),
        sa.CheckConstraint("score IS NULL OR (score >= 1 AND score <= 10)", name='valid_score')
    )
    
    # Indexes
    op.create_index('idx_mock_sessions_job_app', 'mock_interview_sessions', ['job_application_id'])
    op.create_index('idx_mock_questions_session', 'mock_interview_questions', ['session_id'])
    op.create_index('idx_mock_responses_question', 'mock_interview_responses', ['question_id'])
    op.create_index('idx_mock_analysis_question', 'mock_interview_analysis', ['question_id'])

def downgrade():
    op.drop_index('idx_mock_analysis_question')
    op.drop_index('idx_mock_responses_question')
    op.drop_index('idx_mock_questions_session')
    op.drop_index('idx_mock_sessions_job_app')
    op.drop_table('mock_interview_analysis')
    op.drop_table('mock_interview_responses')
    op.drop_table('mock_interview_questions')
    op.drop_table('mock_interview_sessions')
```

Run the migration:
```bash
alembic upgrade head
```

---

## **Step 2: Create SQLAlchemy Models**

Add these models to your models file (e.g., `app/models.py`):

```python
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class MockInterviewSession(Base):
    __tablename__ = 'mock_interview_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_application_id = Column(UUID(as_uuid=True), ForeignKey('job_applications.id', ondelete='CASCADE'), nullable=False)
    interview_stage = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False, default='medium')
    started_at = Column(TIMESTAMP, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    overall_score = Column(Float, nullable=True)
    session_feedback = Column(Text, nullable=True)
    
    # Relationships
    questions = relationship("MockInterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    job_application = relationship("JobApplication", back_populates="mock_interview_sessions")
    
    __table_args__ = (
        CheckConstraint("interview_stage IN ('recruiter_screen', 'hiring_manager')", name='valid_stage'),
        CheckConstraint("difficulty_level IN ('easy', 'medium', 'hard')", name='valid_difficulty'),
    )

class MockInterviewQuestion(Base):
    __tablename__ = 'mock_interview_questions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('mock_interview_sessions.id', ondelete='CASCADE'), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    competency_tested = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False)
    asked_at = Column(TIMESTAMP, nullable=False)
    
    # Relationships
    session = relationship("MockInterviewSession", back_populates="questions")
    responses = relationship("MockInterviewResponse", back_populates="question", cascade="all, delete-orphan")
    analysis = relationship("MockInterviewAnalysis", back_populates="question", uselist=False, cascade="all, delete-orphan")

class MockInterviewResponse(Base):
    __tablename__ = 'mock_interview_responses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('mock_interview_questions.id', ondelete='CASCADE'), nullable=False)
    response_number = Column(Integer, nullable=False)
    response_text = Column(Text, nullable=False)
    response_type = Column(String(20), nullable=False, default='text')
    responded_at = Column(TIMESTAMP, nullable=False)
    
    # Relationships
    question = relationship("MockInterviewQuestion", back_populates="responses")

class MockInterviewAnalysis(Base):
    __tablename__ = 'mock_interview_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('mock_interview_questions.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=True)
    level_demonstrated = Column(String(10), nullable=True)
    gaps = Column(JSON, nullable=False, default=[])
    strengths = Column(JSON, nullable=False, default=[])
    follow_up_questions = Column(JSON, nullable=False, default=[])
    feedback_text = Column(Text, nullable=True)
    revised_answer = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    
    # Relationships
    question = relationship("MockInterviewQuestion", back_populates="analysis")
    
    __table_args__ = (
        CheckConstraint("score IS NULL OR (score >= 1 AND score <= 10)", name='valid_score'),
    )
```

---

## **Step 3: Create Pydantic Schemas**

Create a new schema file (e.g., `app/schemas/mock_interview.py`):

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StartMockInterviewRequest(BaseModel):
    job_application_id: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")

class FirstQuestionResponse(BaseModel):
    question_id: str
    question_text: str
    competency_tested: str
    question_number: int

class StartMockInterviewResponse(BaseModel):
    session_id: str
    interview_stage: str
    difficulty_level: str
    first_question: FirstQuestionResponse

class SubmitResponseRequest(BaseModel):
    session_id: str
    question_id: str
    response_text: str
    response_number: int = Field(..., ge=1, le=4)

class SubmitResponseResponse(BaseModel):
    response_recorded: bool
    follow_up_question: Optional[str] = None
    should_continue: bool
    brief_feedback: str

class QuestionFeedbackResponse(BaseModel):
    question_text: str
    all_responses: List[str]
    score: int = Field(..., ge=1, le=10)
    level_demonstrated: str
    what_landed: List[str]
    what_didnt_land: List[str]
    coaching: str
    revised_answer: str

class NextQuestionRequest(BaseModel):
    session_id: str
    current_question_number: int

class SessionProgress(BaseModel):
    questions_completed: int
    average_score: float

class NextQuestionResponse(BaseModel):
    question_id: str
    question_text: str
    competency_tested: str
    question_number: int
    total_questions: int
    session_progress: SessionProgress

class EndMockInterviewRequest(BaseModel):
    session_id: str

class QuestionSummary(BaseModel):
    question_number: int
    question_text: str
    score: int
    brief_feedback: str

class SessionFeedback(BaseModel):
    overall_assessment: str
    key_strengths: List[str]
    areas_to_improve: List[str]
    coaching_priorities: List[str]
    readiness_score: str

class EndMockInterviewResponse(BaseModel):
    session_id: str
    overall_score: float
    questions_completed: int
    session_feedback: SessionFeedback
    question_summaries: List[QuestionSummary]

class MockInterviewSessionSchema(BaseModel):
    session_id: str
    interview_stage: str
    started_at: datetime
    completed_at: Optional[datetime]
    overall_score: Optional[float]
    questions_completed: int

class ImprovementTrend(BaseModel):
    first_session_score: float
    latest_session_score: float
    improvement: str

class SessionHistoryResponse(BaseModel):
    sessions: List[MockInterviewSessionSchema]
    improvement_trend: Optional[ImprovementTrend] = None
```

---

## **Step 4: Create Helper Functions**

Create a service file (e.g., `app/services/mock_interview_service.py`):

```python
from sqlalchemy.orm import Session
from app.models import MockInterviewAnalysis, MockInterviewQuestion, MockInterviewResponse
import json

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

def calculate_session_average(session_id: str, db: Session) -> float:
    """
    Calculate average score across all completed questions in session.
    """
    analyses = db.query(MockInterviewAnalysis).join(
        MockInterviewQuestion
    ).filter(
        MockInterviewQuestion.session_id == session_id,
        MockInterviewAnalysis.score.isnot(None)
    ).all()
    
    if not analyses:
        return 0.0
    
    scores = [analysis.score for analysis in analyses]
    return sum(scores) / len(scores)

def format_responses_for_analysis(responses: list) -> str:
    """
    Format all responses to a question into text for analysis.
    """
    formatted = []
    for i, response in enumerate(responses, 1):
        label = "INITIAL RESPONSE" if i == 1 else f"FOLLOW-UP {i-1}"
        formatted.append(f"{label}:\n{response.response_text}")
    
    return "\n\n".join(formatted)

def parse_claude_json_response(response_text: str) -> dict:
    """
    Parse Claude response as JSON.
    Handle markdown code blocks if present.
    """
    # Strip markdown code blocks
    if response_text.startswith("```json"):
        response_text = response_text.split("```json")[1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("```", 1)[0]
    
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from Claude: {e}")
```

---

## **Step 5: Create Prompt Templates**

Add these to your prompts file or as constants:

```python
GENERATE_QUESTION_PROMPT = """
You are conducting a mock interview for a {interview_stage} stage.

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
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

DIFFICULTY GUIDELINES:
- Easy: Straightforward STAR questions, clear scenarios
- Medium: Multi-faceted situations, requires prioritization or tradeoffs
- Hard: Ambiguous scenarios, strategic thinking, handling conflict/failure

OUTPUT FORMAT:
Return JSON:
{{
    "question_text": "string (the actual question)",
    "competency_tested": "string (primary competency being evaluated)",
    "difficulty": "easy|medium|hard"
}}

No markdown, no preamble.
"""

ANALYZE_RESPONSE_PROMPT = """
Analyze this candidate's response to a mock interview question.

QUESTION: {question_text}
CANDIDATE RESPONSE: {response_text}
RESPONSE NUMBER: {response_number} (1 = initial, 2-4 = follow-ups)
EXPECTED COMPETENCY: {competency}
TARGET LEVEL: {target_level}

CANDIDATE BACKGROUND:
{resume_text}

Evaluate:
1. Did they demonstrate the expected competency?
2. What level are they communicating at (L4/L5A/L5B)?
3. What gaps exist in their answer?
4. What strengths did they show?
5. Score the response 1-10

LEVEL GUIDELINES:
- L4: Execution-focused, task completion, individual contributor scope
- L5A: Cross-team coordination, strategic input, influence without authority
- L5B: Organizational impact, strategic decisions, ambiguity navigation

Generate 2-3 follow-up questions that:
- Probe gaps in their answer
- Test depth of experience
- Push them to elevate their response to target level
- Are realistic for this interview stage

OUTPUT FORMAT:
Return JSON:
{{
    "score": integer (1-10),
    "level_demonstrated": "L4" | "L5A" | "L5B",
    "gaps": ["gap1", "gap2"],
    "strengths": ["strength1", "strength2"],
    "follow_up_questions": ["question1", "question2", "question3"],
    "brief_feedback": "string (1-2 sentences of immediate coaching)"
}}

RULES:
- Be specific about gaps (not "needs more detail" but "didn't mention stakeholder alignment")
- Reference actual competencies (not generic advice)
- Follow-ups should build on their response
- Brief feedback should be actionable

No markdown, no preamble.
"""

GENERATE_QUESTION_FEEDBACK_PROMPT = """
Provide comprehensive coaching feedback after this mock interview question.

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

No markdown, no preamble.
"""

GENERATE_SESSION_FEEDBACK_PROMPT = """
Generate comprehensive feedback for this completed mock interview session.

SESSION DETAILS:
- Interview Stage: {interview_stage}
- Questions Completed: {num_questions}
- Average Score: {average_score}

QUESTION SUMMARIES:
{questions_summary}

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
{job_description}

Generate session-level feedback covering:
1. Overall assessment (2-3 sentences on readiness)
2. Key strengths (3 things they consistently did well)
3. Areas to improve (3 things that need work)
4. Coaching priorities (3 specific things to practice before real interview)
5. Readiness score: "Ready" | "Almost Ready" | "Needs Practice"

READINESS CRITERIA:
- Ready: Average score ≥8, no critical gaps, level-appropriate communication
- Almost Ready: Average score 6-7.9, minor gaps, mostly level-appropriate
- Needs Practice: Average score <6, significant gaps, below-level communication

OUTPUT FORMAT:
Return JSON:
{{
    "overall_assessment": "string (2-3 sentences)",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "areas_to_improve": ["area1", "area2", "area3"],
    "coaching_priorities": ["priority1", "priority2", "priority3"],
    "readiness_score": "Ready" | "Almost Ready" | "Needs Practice",
    "next_steps": "string (what to do next)"
}}

RULES:
- Strengths should be specific (not "good communication" but "demonstrated cross-team leadership with metrics")
- Improvements should be actionable (not "be more confident" but "practice leading with impact statements")
- Priorities should be ranked by importance
- Next steps should be tactical

No markdown, no preamble.
"""
```

---

## **Step 6: Implement Router Endpoints**

Create router file (e.g., `app/routers/mock_interview.py`):

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import (
    MockInterviewSession,
    MockInterviewQuestion,
    MockInterviewResponse,
    MockInterviewAnalysis,
    JobApplication,
    CandidateResume
)
from app.schemas.mock_interview import *
from app.services.claude_service import call_claude_api
from app.services.mock_interview_service import *

router = APIRouter(prefix="/api/mock-interview", tags=["mock-interview"])

@router.post("/start", response_model=StartMockInterviewResponse)
async def start_mock_interview(
    request: StartMockInterviewRequest,
    db: Session = Depends(get_db)
):
    """Start a new mock interview session."""
    
    # Fetch job application
    job_application = db.query(JobApplication).filter(
        JobApplication.id == request.job_application_id
    ).first()
    
    if not job_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    # Fetch resume
    resume = db.query(CandidateResume).filter(
        CandidateResume.candidate_id == job_application.candidate_id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=400, detail="Resume not found")
    
    # Create session
    session = MockInterviewSession(
        job_application_id=request.job_application_id,
        interview_stage=request.interview_stage,
        difficulty_level=request.difficulty_level,
        started_at=datetime.now()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Generate first question
    competency = get_competency_for_stage(request.interview_stage, 1)
    
    prompt = GENERATE_QUESTION_PROMPT.format(
        interview_stage=request.interview_stage,
        resume_text=resume.resume_text,
        job_description=job_application.job_description,
        difficulty=request.difficulty_level,
        asked_questions="None",
        competency_area=competency
    )
    
    try:
        response_text = await call_claude_api(prompt, max_tokens=1000)
        question_data = parse_claude_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")
    
    # Store question
    question = MockInterviewQuestion(
        session_id=session.id,
        question_number=1,
        question_text=question_data["question_text"],
        competency_tested=question_data["competency_tested"],
        difficulty=question_data["difficulty"],
        asked_at=datetime.now()
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return StartMockInterviewResponse(
        session_id=str(session.id),
        interview_stage=session.interview_stage,
        difficulty_level=session.difficulty_level,
        first_question=FirstQuestionResponse(
            question_id=str(question.id),
            question_text=question.question_text,
            competency_tested=question.competency_tested,
            question_number=1
        )
    )

@router.post("/respond", response_model=SubmitResponseResponse)
async def submit_response(
    request: SubmitResponseRequest,
    db: Session = Depends(get_db)
):
    """Submit response and get follow-up question or complete question."""
    
    # Verify question exists
    question = db.query(MockInterviewQuestion).filter(
        MockInterviewQuestion.id == request.question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Store response
    response = MockInterviewResponse(
        question_id=request.question_id,
        response_number=request.response_number,
        response_text=request.response_text,
        responded_at=datetime.now()
    )
    db.add(response)
    db.commit()
    
    # Fetch session and job application
    session = question.session
    job_application = session.job_application
    resume = db.query(CandidateResume).filter(
        CandidateResume.candidate_id == job_application.candidate_id
    ).first()
    
    target_level = determine_target_level(job_application.job_description)
    
    # Analyze response
    prompt = ANALYZE_RESPONSE_PROMPT.format(
        question_text=question.question_text,
        response_text=request.response_text,
        response_number=request.response_number,
        competency=question.competency_tested,
        target_level=target_level,
        resume_text=resume.resume_text
    )
    
    try:
        response_text = await call_claude_api(prompt, max_tokens=1500)
        analysis_data = parse_claude_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze response: {str(e)}")
    
    # Check if this is the last follow-up (response_number 4)
    if request.response_number >= 4:
        # Store final analysis
        analysis = MockInterviewAnalysis(
            question_id=request.question_id,
            score=analysis_data["score"],
            level_demonstrated=analysis_data["level_demonstrated"],
            gaps=analysis_data["gaps"],
            strengths=analysis_data["strengths"],
            follow_up_questions=[],
            feedback_text=analysis_data["brief_feedback"],
            created_at=datetime.now()
        )
        db.add(analysis)
        db.commit()
        
        return SubmitResponseResponse(
            response_recorded=True,
            follow_up_question=None,
            should_continue=False,
            brief_feedback=analysis_data["brief_feedback"]
        )
    
    # Store analysis with follow-ups
    analysis = MockInterviewAnalysis(
        question_id=request.question_id,
        score=analysis_data["score"],
        level_demonstrated=analysis_data["level_demonstrated"],
        gaps=analysis_data["gaps"],
        strengths=analysis_data["strengths"],
        follow_up_questions=analysis_data["follow_up_questions"],
        feedback_text=analysis_data["brief_feedback"],
        created_at=datetime.now()
    )
    db.add(analysis)
    db.commit()
    
    # Return first follow-up question
    follow_up = analysis_data["follow_up_questions"][0] if analysis_data["follow_up_questions"] else None
    
    return SubmitResponseResponse(
        response_recorded=True,
        follow_up_question=follow_up,
        should_continue=True,
        brief_feedback=analysis_data["brief_feedback"]
    )

@router.get("/question-feedback/{question_id}", response_model=QuestionFeedbackResponse)
async def get_question_feedback(
    question_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive feedback for a completed question."""
    
    # Fetch question and all responses
    question = db.query(MockInterviewQuestion).filter(
        MockInterviewQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    responses = db.query(MockInterviewResponse).filter(
        MockInterviewResponse.question_id == question_id
    ).order_by(MockInterviewResponse.response_number).all()
    
    # Fetch or generate analysis
    analysis = db.query(MockInterviewAnalysis).filter(
        MockInterviewAnalysis.question_id == question_id
    ).first()
    
    if not analysis or not analysis.revised_answer:
        # Generate comprehensive feedback
        session = question.session
        job_application = session.job_application
        resume = db.query(CandidateResume).filter(
            CandidateResume.candidate_id == job_application.candidate_id
        ).first()
        
        target_level = determine_target_level(job_application.job_description)
        all_responses_text = format_responses_for_analysis(responses)
        
        prompt = GENERATE_QUESTION_FEEDBACK_PROMPT.format(
            question_text=question.question_text,
            competency=question.competency_tested,
            target_level=target_level,
            all_responses_text=all_responses_text,
            analysis_json=json.dumps({
                "score": analysis.score if analysis else 5,
                "level_demonstrated": analysis.level_demonstrated if analysis else "L4",
                "gaps": analysis.gaps if analysis else [],
                "strengths": analysis.strengths if analysis else []
            }),
            resume_text=resume.resume_text
        )
        
        try:
            response_text = await call_claude_api(prompt, max_tokens=2000)
            feedback_data = parse_claude_json_response(response_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")
        
        # Update or create analysis with comprehensive feedback
        if analysis:
            analysis.feedback_text = feedback_data["coaching"]
            analysis.revised_answer = feedback_data["revised_answer"]
        else:
            analysis = MockInterviewAnalysis(
                question_id=question_id,
                score=5,
                level_demonstrated="L4",
                gaps=[],
                strengths=[],
                follow_up_questions=[],
                feedback_text=feedback_data["coaching"],
                revised_answer=feedback_data["revised_answer"],
                created_at=datetime.now()
            )
            db.add(analysis)
        
        db.commit()
        db.refresh(analysis)
        
        return QuestionFeedbackResponse(
            question_text=question.question_text,
            all_responses=[r.response_text for r in responses],
            score=analysis.score,
            level_demonstrated=analysis.level_demonstrated,
            what_landed=feedback_data["what_landed"],
            what_didnt_land=feedback_data["what_didnt_land"],
            coaching=feedback_data["coaching"],
            revised_answer=feedback_data["revised_answer"]
        )
    
    return QuestionFeedbackResponse(
        question_text=question.question_text,
        all_responses=[r.response_text for r in responses],
        score=analysis.score,
        level_demonstrated=analysis.level_demonstrated,
        what_landed=analysis.strengths,
        what_didnt_land=analysis.gaps,
        coaching=analysis.feedback_text,
        revised_answer=analysis.revised_answer
    )

# Continue in next message due to length...
```

**Note:** The router implementation is too long for one file. Continue implementing the remaining endpoints (`/next-question`, `/end`, `/sessions/{job_application_id}`) following the same pattern shown above. Each endpoint should:

1. Validate input
2. Fetch necessary data from database
3. Call Claude API with appropriate prompt
4. Parse and validate response
5. Store results in database
6. Return structured response

---

## **Step 7: Register Router**

In your main application file (e.g., `app/main.py`), register the router:

```python
from app.routers import mock_interview

app.include_router(mock_interview.router)
```

---

## **Step 8: Test Endpoints**

Create test file (e.g., `tests/test_mock_interview.py`) and run tests to verify:

1. Session creation works
2. Question generation uses candidate's actual experience
3. Response analysis provides specific feedback
4. Follow-up questions build on previous responses
5. Session completion generates comprehensive feedback
6. Session history tracks improvement

---

## **Critical Reminders**

1. **Never fabricate experience** — all questions and feedback must reference candidate's actual work history
2. **Parse JSON carefully** — Claude may return markdown code blocks, strip them before parsing
3. **Validate all inputs** — check request parameters before processing
4. **Handle errors gracefully** — provide clear error messages to frontend
5. **Track session state** — maintain conversation flow across multiple requests
6. **Test thoroughly** — verify questions are realistic and feedback is actionable

---

## **Success Criteria**

- [ ] All endpoints return expected JSON structure
- [ ] Questions are realistic for interview stage
- [ ] Feedback is specific and actionable
- [ ] Follow-up questions probe gaps effectively
- [ ] Session feedback provides clear coaching priorities
- [ ] No fabricated content in any outputs
- [ ] Response times <3 seconds per request
- [ ] Session state properly maintained

---

**End of Implementation Instructions**
