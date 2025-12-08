# Mock Interview — Implementation Spec (Phase 1 MVP)

**Version:** 1.0  
**Date:** December 2024  
**Target:** Backend Developer / Product Team  
**Purpose:** Technical specification for conversational mock interview feature

---

## **Overview**

Build a conversational mock interview feature that allows candidates to practice behavioral and technical questions with real-time adaptation and feedback. This is Phase 1 (MVP) focused on core functionality.

**What This Enables:**
- Candidates practice interview questions in a dynamic conversation
- Claude asks follow-up questions based on their responses
- Real-time analysis and feedback after each question
- Session storage for later review
- Text-based only (voice comes in Phase 2)

**Critical Rules:**
- All questions must be realistic for the interview stage
- All feedback must be grounded in actual competency frameworks
- Never fabricate or suggest false experience
- Provide specific, actionable coaching
- Track session state for multi-turn conversations

---

## **Database Schema**

### **New Tables**

```sql
-- Mock interview sessions
CREATE TABLE mock_interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
    interview_stage VARCHAR(50) NOT NULL, -- 'recruiter_screen' or 'hiring_manager'
    difficulty_level VARCHAR(20) DEFAULT 'medium', -- 'easy', 'medium', 'hard'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    overall_score FLOAT, -- Average score across all questions
    session_feedback TEXT,
    CONSTRAINT valid_stage CHECK (interview_stage IN ('recruiter_screen', 'hiring_manager')),
    CONSTRAINT valid_difficulty CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Individual questions within a session
CREATE TABLE mock_interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES mock_interview_sessions(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL, -- 1, 2, 3, 4, 5
    question_text TEXT NOT NULL,
    competency_tested VARCHAR(100), -- e.g., 'leadership', 'ambiguity_tolerance'
    difficulty VARCHAR(20) NOT NULL,
    asked_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_difficulty CHECK (difficulty IN ('easy', 'medium', 'hard'))
);

-- Candidate responses to questions (includes follow-ups)
CREATE TABLE mock_interview_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES mock_interview_questions(id) ON DELETE CASCADE,
    response_number INTEGER NOT NULL, -- 1 = initial, 2-4 = follow-ups
    response_text TEXT NOT NULL,
    response_type VARCHAR(20) DEFAULT 'text', -- 'text' or 'audio' (Phase 2)
    responded_at TIMESTAMP DEFAULT NOW()
);

-- Analysis and feedback per question
CREATE TABLE mock_interview_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID REFERENCES mock_interview_questions(id) ON DELETE CASCADE,
    score INTEGER CHECK (score BETWEEN 1 AND 10),
    level_demonstrated VARCHAR(10), -- 'L4', 'L5A', 'L5B'
    gaps JSONB DEFAULT '[]'::jsonb, -- ["gap1", "gap2"]
    strengths JSONB DEFAULT '[]'::jsonb, -- ["strength1", "strength2"]
    follow_up_questions JSONB DEFAULT '[]'::jsonb, -- ["q1", "q2", "q3"]
    feedback_text TEXT,
    revised_answer TEXT, -- Better version of their answer
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_mock_sessions_job_app ON mock_interview_sessions(job_application_id);
CREATE INDEX idx_mock_questions_session ON mock_interview_questions(session_id);
CREATE INDEX idx_mock_responses_question ON mock_interview_responses(question_id);
CREATE INDEX idx_mock_analysis_question ON mock_interview_analysis(question_id);
```

---

## **API Endpoints**

### **1. Start Mock Interview Session**

```python
@router.post("/api/mock-interview/start")
async def start_mock_interview(request: StartMockInterviewRequest):
    """
    Initialize a new mock interview session.
    
    Request:
    {
        "job_application_id": "uuid",
        "interview_stage": "recruiter_screen" | "hiring_manager",
        "difficulty_level": "medium" (default)
    }
    
    Response:
    {
        "session_id": "uuid",
        "interview_stage": "hiring_manager",
        "difficulty_level": "medium",
        "first_question": {
            "question_id": "uuid",
            "question_text": "Tell me about a time you led a cross-functional project...",
            "competency_tested": "leadership",
            "question_number": 1
        }
    }
    
    Logic:
    1. Create new mock_interview_session record
    2. Fetch job_application and resume
    3. Generate first question using GENERATE_QUESTION_PROMPT
    4. Store question in mock_interview_questions
    5. Return session_id + first question
    
    Error Handling:
    - 404 if job_application not found
    - 400 if invalid interview_stage or difficulty_level
    - 500 if question generation fails
    """
```

---

### **2. Submit Response & Get Follow-Up**

```python
@router.post("/api/mock-interview/respond")
async def submit_response(request: SubmitResponseRequest):
    """
    Submit candidate's response, get analysis + follow-up question.
    
    Request:
    {
        "session_id": "uuid",
        "question_id": "uuid",
        "response_text": "string (candidate's answer)",
        "response_number": integer (1 = initial, 2-4 = follow-ups)
    }
    
    Response:
    {
        "response_recorded": true,
        "follow_up_question": "string (next question)" | null,
        "should_continue": true | false,
        "brief_feedback": "string (quick coaching note)"
    }
    
    Logic:
    1. Store response in mock_interview_responses
    2. If response_number < 4:
        - Analyze response using ANALYZE_RESPONSE_PROMPT
        - Store analysis in mock_interview_analysis
        - Generate follow-up question
        - Return follow-up + brief feedback
    3. If response_number == 4 (max follow-ups reached):
        - Analyze final response
        - Generate comprehensive feedback
        - Return should_continue = false
    
    Error Handling:
    - 404 if session_id or question_id not found
    - 400 if response_number invalid
    - 500 if analysis fails
    """
```

---

### **3. Get Question Feedback**

```python
@router.get("/api/mock-interview/question-feedback/{question_id}")
async def get_question_feedback(question_id: str):
    """
    Get comprehensive feedback for a completed question.
    
    Response:
    {
        "question_text": "string",
        "all_responses": ["response1", "response2", "response3"],
        "score": integer (1-10),
        "level_demonstrated": "L4" | "L5A" | "L5B",
        "what_landed": ["bullet1", "bullet2"],
        "what_didnt_land": ["bullet1", "bullet2"],
        "coaching": "string (specific improvement advice)",
        "revised_answer": "string (better version at target level)"
    }
    
    Logic:
    1. Fetch question and all responses
    2. Fetch analysis from mock_interview_analysis
    3. If analysis doesn't exist, generate it now
    4. Format and return
    
    Error Handling:
    - 404 if question_id not found
    - 500 if feedback generation fails
    """
```

---

### **4. Move to Next Question**

```python
@router.post("/api/mock-interview/next-question")
async def next_question(request: NextQuestionRequest):
    """
    Generate and move to the next question in the session.
    
    Request:
    {
        "session_id": "uuid",
        "current_question_number": integer
    }
    
    Response:
    {
        "question_id": "uuid",
        "question_text": "string",
        "competency_tested": "string",
        "question_number": integer,
        "total_questions": 5,
        "session_progress": {
            "questions_completed": 2,
            "average_score": 7.5
        }
    }
    
    Logic:
    1. Verify session exists
    2. Check if max questions (5) reached
    3. Calculate current average score
    4. Generate next question using GENERATE_QUESTION_PROMPT
    5. Store question in mock_interview_questions
    6. Return question + progress
    
    Error Handling:
    - 404 if session_id not found
    - 400 if max questions already reached
    - 500 if question generation fails
    """
```

---

### **5. End Mock Interview Session**

```python
@router.post("/api/mock-interview/end")
async def end_mock_interview(request: EndMockInterviewRequest):
    """
    Complete the mock interview session and generate final feedback.
    
    Request:
    {
        "session_id": "uuid"
    }
    
    Response:
    {
        "session_id": "uuid",
        "overall_score": 7.2,
        "questions_completed": 5,
        "session_feedback": {
            "overall_assessment": "string (2-3 sentences)",
            "key_strengths": ["bullet1", "bullet2", "bullet3"],
            "areas_to_improve": ["bullet1", "bullet2", "bullet3"],
            "coaching_priorities": ["priority1", "priority2", "priority3"],
            "readiness_score": "Ready | Almost Ready | Needs Practice"
        },
        "question_summaries": [
            {
                "question_number": 1,
                "question_text": "string",
                "score": 7,
                "brief_feedback": "string"
            },
            ...
        ]
    }
    
    Logic:
    1. Fetch all questions and analyses for session
    2. Calculate overall_score (average of all question scores)
    3. Generate session-level feedback using SESSION_FEEDBACK_PROMPT
    4. Update mock_interview_sessions with completed_at, overall_score, session_feedback
    5. Return comprehensive summary
    
    Error Handling:
    - 404 if session_id not found
    - 500 if feedback generation fails
    """
```

---

### **6. Get Session History**

```python
@router.get("/api/mock-interview/sessions/{job_application_id}")
async def get_session_history(job_application_id: str):
    """
    Get all past mock interview sessions for a job application.
    
    Response:
    {
        "sessions": [
            {
                "session_id": "uuid",
                "interview_stage": "hiring_manager",
                "started_at": "timestamp",
                "completed_at": "timestamp",
                "overall_score": 7.2,
                "questions_completed": 5
            },
            ...
        ],
        "improvement_trend": {
            "first_session_score": 5.8,
            "latest_session_score": 7.2,
            "improvement": "+1.4"
        }
    }
    
    Logic:
    1. Fetch all sessions for job_application_id
    2. Sort by started_at DESC
    3. Calculate improvement trend if multiple sessions exist
    4. Return list + trend
    
    Error Handling:
    - 404 if job_application_id not found
    - 200 with empty list if no sessions
    """
```

---

## **Prompt Templates**

### **1. Generate Question**

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
```

---

### **2. Analyze Response**

```python
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
```

---

### **3. Generate Question Feedback**

```python
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
```

---

### **4. Generate Session Feedback**

```python
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

## **Pydantic Models**

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

class MockInterviewSession(BaseModel):
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
    sessions: List[MockInterviewSession]
    improvement_trend: Optional[ImprovementTrend] = None
```

---

## **Helper Functions**

```python
# app/services/mock_interview_service.py

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

def format_responses_for_analysis(responses: List[MockInterviewResponse]) -> str:
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
    import json
    
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

## **Implementation Steps**

### **Step 1: Database Setup**
```bash
# Create migration
alembic revision -m "add_mock_interview_tables"

# Add CREATE TABLE statements
# Run migration
alembic upgrade head
```

### **Step 2: Create Router**
```python
# app/routers/mock_interview.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    MockInterviewSession,
    MockInterviewQuestion,
    MockInterviewResponse,
    MockInterviewAnalysis
)
from app.schemas.mock_interview import *
from app.services.claude_service import call_claude_api
from app.services.mock_interview_service import *

router = APIRouter(prefix="/api/mock-interview", tags=["mock-interview"])

# Implement endpoints here
```

### **Step 3: Implement Endpoints**
- Start with `/start` endpoint
- Then `/respond` endpoint
- Then `/question-feedback` endpoint
- Then `/next-question` endpoint
- Then `/end` endpoint
- Finally `/sessions/{job_application_id}` endpoint

### **Step 4: Testing**
```python
# tests/test_mock_interview.py

def test_start_mock_interview():
    """Test starting a new mock interview session."""
    # Create test job application
    # Call /start endpoint
    # Assert session created
    # Assert first question returned
    pass

def test_submit_response_initial():
    """Test submitting initial response."""
    # Start session
    # Submit initial response
    # Assert response recorded
    # Assert follow-up question returned
    pass

def test_submit_response_follow_ups():
    """Test submitting follow-up responses."""
    # Start session
    # Submit initial + 3 follow-ups
    # Assert all responses recorded
    # Assert should_continue = false after 4th response
    pass

def test_get_question_feedback():
    """Test getting comprehensive feedback."""
    # Complete a question
    # Call /question-feedback
    # Assert feedback structure
    # Assert revised answer provided
    pass

def test_next_question():
    """Test moving to next question."""
    # Complete first question
    # Call /next-question
    # Assert new question generated
    # Assert progress tracking correct
    pass

def test_end_session():
    """Test ending mock interview."""
    # Complete 5 questions
    # Call /end
    # Assert session completed
    # Assert comprehensive feedback
    pass

def test_session_history():
    """Test retrieving session history."""
    # Create multiple sessions
    # Call /sessions/{job_app_id}
    # Assert all sessions returned
    # Assert improvement trend calculated
    pass
```

---

## **Frontend Requirements**

### **UI Components Needed**

1. **Mock Interview Start Screen**
   - Button: "Start Mock Interview"
   - Dropdown: Select interview stage (Recruiter Screen / Hiring Manager)
   - Dropdown: Select difficulty (Easy / Medium / Hard)
   - Displays: "This will take approximately 30-45 minutes. You'll answer 5 questions with follow-ups."

2. **Question Display**
   - Shows question text
   - Shows progress: "Question 3/5"
   - Text area for response (multi-line)
   - Button: "Submit Response"
   - Shows loading state while analyzing

3. **Follow-Up Display**
   - Shows previous question + candidate's answer (collapsed)
   - Shows follow-up question
   - Text area for response
   - Shows: "Follow-up 2/3"
   - Button: "Submit Response"

4. **Brief Feedback Display**
   - After each response, show brief coaching note
   - Example: "Good start, but you missed the cross-functional coordination aspect. Let's dig into that."
   - Button: "Continue" (if more follow-ups) or "Next Question" (if question complete)

5. **Question Feedback Screen**
   - Shows comprehensive feedback after question complete
   - Score: 7/10
   - Level Demonstrated: L5A
   - What Landed: [bullets]
   - What Didn't Land: [bullets]
   - Coaching: [paragraphs]
   - Revised Answer: [text]
   - Button: "Next Question" or "End Session" (if 5 questions complete)

6. **Session Summary Screen**
   - Overall Score: 7.2/10
   - Questions Completed: 5/5
   - Readiness Score: "Almost Ready"
   - Key Strengths: [bullets]
   - Areas to Improve: [bullets]
   - Coaching Priorities: [bullets]
   - Next Steps: [text]
   - Button: "Review Questions" (goes to session history)
   - Button: "Start New Session"

7. **Session History**
   - List of past sessions
   - For each session:
     - Date, Stage, Score, Readiness
     - Click to view full session details
   - Improvement trend chart (if multiple sessions)

---

## **Error Handling**

```python
# Common error scenarios

# 1. Session not found
if not session:
    raise HTTPException(status_code=404, detail="Mock interview session not found")

# 2. Question not found
if not question:
    raise HTTPException(status_code=404, detail="Question not found")

# 3. Max questions reached
if current_question_number >= 5:
    raise HTTPException(status_code=400, detail="Maximum questions reached. End session to see results.")

# 4. Claude API failure
try:
    response = await call_claude_api(prompt)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

# 5. Invalid JSON from Claude
try:
    parsed = parse_claude_json_response(response)
except ValueError as e:
    raise HTTPException(status_code=500, detail=f"Failed to parse response: {str(e)}")

# 6. Session already completed
if session.completed_at:
    raise HTTPException(status_code=400, detail="Session already completed. Start a new session.")
```

---

## **Performance Considerations**

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_job_description(job_app_id: str) -> str:
    """Cache job description to avoid repeated DB queries."""
    pass

# Async Claude API calls
async def generate_question_and_analyze_parallel(question_prompt: str, analysis_prompt: str):
    """Generate next question while analyzing current response."""
    import asyncio
    
    question_task = call_claude_api(question_prompt)
    analysis_task = call_claude_api(analysis_prompt)
    
    question_response, analysis_response = await asyncio.gather(question_task, analysis_task)
    return question_response, analysis_response
```

---

## **Success Metrics**

### **Engagement Metrics**
- % of users who start mock interviews
- Average questions completed per session
- Session completion rate (5/5 questions)
- Repeat usage (multiple sessions per user)

### **Quality Metrics**
- Average score improvement between first and third session
- Readiness score distribution (Ready vs Almost Ready vs Needs Practice)
- User satisfaction ratings
- Time spent in mock interviews

### **Technical Metrics**
- Response time for question generation (<3 seconds)
- Response time for analysis (<3 seconds)
- Claude API token usage per session
- Database query performance

---

## **Phase 2 Enhancements (Future)**

Not part of MVP, but planned for Phase 2:

1. **Voice Input**
   - Accept audio recordings
   - Transcribe with Whisper API
   - Analyze transcription + delivery
   - Provide feedback on pace, filler words, confidence

2. **Difficulty Escalation**
   - Start medium, adjust based on performance
   - If score ≥8 consistently, escalate to hard
   - If score <5 consistently, drop to easy

3. **Multi-Session Comparison**
   - Show improvement trends
   - "Your first session: 5.8, your third session: 8.2"
   - Track specific competency improvement

4. **Custom Question Sets**
   - Allow users to upload their own questions
   - Practice questions from Glassdoor interview reviews
   - Company-specific question banks

5. **Adversarial Mode**
   - Simulate hostile interviewer
   - Challenge assumptions
   - Interrupt mid-answer
   - Ask "why?" repeatedly

---

## **Deployment Checklist**

- [ ] Database migrations run successfully
- [ ] All endpoints return expected JSON structure
- [ ] Error handling covers common failure scenarios
- [ ] No fabricated content in questions or feedback
- [ ] Response times <3 seconds for generation/analysis
- [ ] Frontend can consume responses without modification
- [ ] All tests passing
- [ ] Logging added for debugging
- [ ] Session state properly managed
- [ ] Claude API costs monitored

---

**End of Implementation Spec**
