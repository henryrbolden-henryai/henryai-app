# Interview Intelligence — Implementation Spec

**Version:** 1.0  
**Date:** December 2024  
**Target:** Claude Code / Backend Developer  
**Purpose:** Technical implementation guide for Interview Intelligence endpoints

---

## **Overview**

Implement Interview Intelligence endpoints for HenryAI. This includes:
1. Pre-interview prep generation (recruiter screen, hiring manager)
2. 60-90 second intro sell practice (template generation + feedback)
3. Conversational practice mode
4. Post-interview debrief analysis
5. Thank-you email generation

**Critical Rules**:
- NEVER fabricate experience, companies, achievements, or metrics
- ALL content must be grounded in candidate's actual resume
- Maintain all existing functionality—this is additive only
- Use structured JSON responses for all endpoints
- Include comprehensive error handling

---

## **Database Schema Changes**

### **New Tables**

```sql
-- Interview prep storage (one per stage per application)
CREATE TABLE interview_prep (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
    interview_stage VARCHAR(50) NOT NULL, -- 'recruiter_screen' or 'hiring_manager'
    prep_content JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(job_application_id, interview_stage)
);

-- Practice session tracking
CREATE TABLE practice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
    interview_stage VARCHAR(50) NOT NULL,
    session_started_at TIMESTAMP DEFAULT NOW(),
    questions_practiced JSONB DEFAULT '[]'::jsonb,
    total_time_minutes INTEGER DEFAULT 0
);

-- Intro sell practice attempts
CREATE TABLE intro_sell_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    candidate_version TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    feedback JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Interview debriefs
CREATE TABLE interview_debriefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_application_id UUID REFERENCES job_applications(id) ON DELETE CASCADE,
    interview_stage VARCHAR(50) NOT NULL,
    interview_date DATE NOT NULL,
    debrief_submitted_at TIMESTAMP DEFAULT NOW(),
    transcript_provided BOOLEAN DEFAULT FALSE,
    transcript_text TEXT,
    overall_score INTEGER CHECK (overall_score BETWEEN 1 AND 10),
    dimension_scores JSONB NOT NULL,
    feedback JSONB NOT NULL,
    thank_you_email TEXT,
    next_stage_adjustments JSONB DEFAULT '[]'::jsonb
);

-- Indexes for performance
CREATE INDEX idx_interview_prep_job_app ON interview_prep(job_application_id);
CREATE INDEX idx_practice_sessions_job_app ON practice_sessions(job_application_id);
CREATE INDEX idx_intro_sell_job_app ON intro_sell_attempts(job_application_id);
CREATE INDEX idx_interview_debriefs_job_app ON interview_debriefs(job_application_id);
```

---

## **API Endpoints**

### **1. Generate Interview Prep**

```python
@router.post("/api/interview-prep/generate")
async def generate_interview_prep(request: InterviewPrepRequest):
    """
    Generate stage-specific interview prep (recruiter screen or hiring manager).
    
    Request:
    {
        "job_application_id": "uuid",
        "interview_stage": "recruiter_screen" | "hiring_manager"
    }
    
    Response:
    {
        "interview_stage": "recruiter_screen",
        "prep_content": {
            "interview_overview": "string (2-3 sentences)",
            "key_talking_points": ["string", "string", ...],
            "red_flag_mitigation": [
                {"flag": "string", "mitigation": "string"},
                ...
            ],
            "likely_questions": ["string", ...],
            "questions_to_ask": [
                {"question": "string", "why": "string"},
                ...
            ],
            "compensation_strategy": "string",
            "timeline_strategy": "string"
        }
    }
    
    Logic:
    1. Fetch job_application by ID
    2. Fetch candidate resume
    3. Fetch fit_analysis (if exists)
    4. Select appropriate prompt based on interview_stage
    5. Call Claude API with structured prompt
    6. Parse response into prep_content structure
    7. Store in interview_prep table
    8. Return prep_content
    
    Error Handling:
    - 404 if job_application not found
    - 400 if interview_stage invalid
    - 500 if Claude API fails
    """
```

**Prompt Templates**:

```python
RECRUITER_SCREEN_PREP_PROMPT = """
You are generating pre-interview intelligence for a recruiter screen.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

FIT ANALYSIS:
{fit_analysis}

Generate structured prep covering:
1. interview_overview (2-3 sentences explaining recruiter's goals)
2. key_talking_points (4-6 bullets, must reference actual achievements from resume)
3. red_flag_mitigation (2-3 bullets addressing gaps, job hopping, overqualification)
4. likely_questions (5-7 questions recruiter will ask)
5. questions_to_ask (3-4 strategic questions with rationale)
6. compensation_strategy (1-2 sentences on handling salary discussion)
7. timeline_strategy (1 sentence on availability)

CRITICAL RULES:
- Use ONLY information from the candidate's actual resume
- Include specific metrics and achievements from resume
- Be direct about red flags—provide mitigation strategies
- No generic advice—everything must be tailored to this candidate and role

Return ONLY a valid JSON object with the structure above. No markdown, no preamble.
"""

HIRING_MANAGER_PREP_PROMPT = """
You are generating pre-interview intelligence for a hiring manager interview.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

FIT ANALYSIS:
{fit_analysis}

Generate structured prep covering:
1. interview_overview (2-3 sentences explaining hiring manager's goals)
2. strengths_to_emphasize (3-4 bullets tied to job requirements, must reference resume)
3. gaps_to_mitigate (2-3 bullets with credible workarounds)
4. star_examples (3-4 behavioral stories using STAR format, must be from actual resume)
   Format: {"competency": "string", "situation": "string", "task": "string", "action": "string", "result": "string"}
5. likely_questions (5-7 technical/functional questions)
6. questions_to_ask (4-5 strategic questions with rationale)
7. closing_strategy (1-2 sentences on how to close strong)

STAR EXAMPLES RULES:
- Every example must come from candidate's actual work history
- Include specific metrics, timeframes, and outcomes from resume
- Map each example to a key competency from the job description
- Use concrete details, not generic scenarios

Return ONLY a valid JSON object with the structure above. No markdown, no preamble.
"""
```

---

### **2. Generate Intro Sell Template**

```python
@router.post("/api/interview-prep/intro-sell/generate")
async def generate_intro_sell_template(request: IntroSellTemplateRequest):
    """
    Generate customized 60-90 second intro sell template.
    
    Request:
    {
        "job_application_id": "uuid"
    }
    
    Response:
    {
        "template": "string (full template with structure)",
        "word_count": integer (100-150 target),
        "coaching_note": "string (2-3 sentences)"
    }
    
    Logic:
    1. Fetch job_application and resume
    2. Call Claude API with INTRO_SELL_TEMPLATE_PROMPT
    3. Return template + coaching note
    """
```

**Prompt Template**:

```python
INTRO_SELL_TEMPLATE_PROMPT = """
Generate a customized 60-90 second intro sell template for this candidate.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

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

No markdown, no preamble.
"""
```

---

### **3. Analyze Intro Sell Attempt**

```python
@router.post("/api/interview-prep/intro-sell/feedback")
async def analyze_intro_sell(request: IntroSellFeedbackRequest):
    """
    Analyze candidate's intro sell attempt and provide structured feedback.
    
    Request:
    {
        "job_application_id": "uuid",
        "candidate_version": "string (their typed intro)",
        "audio_url": "string (optional, for Phase 2)"
    }
    
    Response:
    {
        "overall_score": float (1-10),
        "content_score": integer (1-10),
        "structure_score": integer (1-10),
        "tone_score": integer (1-10),
        "word_count": integer,
        "estimated_time_seconds": integer,
        "strengths": ["string", ...],
        "opportunities": ["string", ...],
        "revised_version": "string (tightened version)",
        "coaching_note": "string"
    }
    
    Logic:
    1. Count words in candidate_version
    2. Calculate estimated time (assume 140 WPM)
    3. Call Claude API with INTRO_SELL_FEEDBACK_PROMPT
    4. Parse response into structured feedback
    5. Store in intro_sell_attempts table
    6. Return feedback
    """
```

**Prompt Template**:

```python
INTRO_SELL_FEEDBACK_PROMPT = """
Analyze this candidate's 60-90 second intro sell attempt.

CANDIDATE'S VERSION:
{candidate_version}

CANDIDATE RESUME (for reference):
{resume_text}

JOB DESCRIPTION (for reference):
{job_description}

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
    "overall_score": float,
    "content_score": integer,
    "structure_score": integer,
    "tone_score": integer,
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

No markdown, no preamble.
"""
```

---

### **4. Post-Interview Debrief**

```python
@router.post("/api/interview-prep/debrief")
async def create_interview_debrief(request: InterviewDebriefRequest):
    """
    Analyze interview performance (transcript or typed debrief).
    
    Request:
    {
        "job_application_id": "uuid",
        "interview_stage": "recruiter_screen" | "hiring_manager",
        "interview_date": "YYYY-MM-DD",
        "transcript_text": "string (optional)",
        "typed_responses": {
            "overall_feeling": "1-10 scale",
            "questions_asked": ["string", ...],
            "strong_answers": ["string", ...],
            "weak_answers": ["string", ...],
            "learnings": "string"
        }
    }
    
    Response:
    {
        "overall_score": integer (1-10),
        "dimension_scores": {
            "content": integer,
            "clarity": integer,
            "delivery": integer,
            "tone": integer,
            "structure": integer,
            "confidence": integer
        },
        "strengths": ["string", ...],
        "opportunities": ["string", ...],
        "what_they_should_have_said": [
            {
                "question": "string",
                "weak_answer": "string",
                "strong_answer": "string"
            }
        ],
        "coaching_points": ["string", ...],
        "action_items": ["string", ...],
        "thank_you_email": "string",
        "next_stage_adjustments": ["string", ...]
    }
    
    Logic:
    1. Determine if transcript or typed debrief
    2. Call Claude API with DEBRIEF_ANALYSIS_PROMPT
    3. Parse response into structured feedback
    4. Generate thank-you email using THANK_YOU_EMAIL_PROMPT
    5. Store in interview_debriefs table
    6. Return feedback + email
    """
```

**Prompt Templates**:

```python
DEBRIEF_ANALYSIS_PROMPT = """
Analyze this interview performance and provide structured feedback.

INTERVIEW TYPE: {interview_stage}

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

INTERVIEW CONTENT:
{interview_content}

Provide structured feedback:

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
- coaching_points: 3 specific things to practice before next interview
- action_items: 3 concrete next steps
- next_stage_adjustments: 2-3 strategic changes for next interview round

OUTPUT FORMAT:
Return JSON with structure above.

RULES:
- Be specific—reference actual questions/answers when possible
- Provide rewritten answers that use candidate's real experience
- Coaching must be actionable, not generic
- Dimension scores must have brief rationale

No markdown, no preamble.
"""

THANK_YOU_EMAIL_PROMPT = """
Generate a thank-you email for this interview.

INTERVIEW TYPE: {interview_stage}
INTERVIEWER NAME: {interviewer_name}
COMPANY: {company_name}
ROLE: {role_title}

INTERVIEW HIGHLIGHTS:
{interview_highlights}

CANDIDATE BACKGROUND:
{resume_text}

STYLE:
- Professional but warm
- Reference 1-2 specific moments from the conversation
- Reinforce fit for the role with brief example
- Signal continued interest without desperation
- Keep to 3 short paragraphs

OUTPUT:
Return plain text email (no JSON, no markdown).
Include subject line.

STRUCTURE:
Subject: Thank you - [Role Title] Interview

Paragraph 1: Thank them, reference specific moment from interview
Paragraph 2: Reinforce your fit with brief relevant example
Paragraph 3: Express continued interest, offer to provide additional info

Signature:
[Candidate Name]
"""
```

---

## **Pydantic Models**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date

class InterviewPrepRequest(BaseModel):
    job_application_id: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")

class InterviewPrepResponse(BaseModel):
    interview_stage: str
    prep_content: Dict

class IntroSellTemplateRequest(BaseModel):
    job_application_id: str

class IntroSellTemplateResponse(BaseModel):
    template: str
    word_count: int
    coaching_note: str

class IntroSellFeedbackRequest(BaseModel):
    job_application_id: str
    candidate_version: str
    audio_url: Optional[str] = None

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
    job_application_id: str
    interview_stage: str = Field(..., pattern="^(recruiter_screen|hiring_manager)$")
    interview_date: date
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
```

---

## **Implementation Steps**

### **Step 1: Database Setup**
```bash
# Create migration file
alembic revision -m "add_interview_intelligence_tables"

# Add the CREATE TABLE statements from schema section above
# Run migration
alembic upgrade head
```

### **Step 2: Create Router**
```python
# app/routers/interview_prep.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import InterviewPrep, PracticeSession, IntroSellAttempt, InterviewDebrief
from app.schemas.interview_prep import *
from app.services.claude_service import call_claude_api
import json

router = APIRouter(prefix="/api/interview-prep", tags=["interview-prep"])

# Implement endpoints here
```

### **Step 3: Claude Service Integration**
```python
# app/services/claude_service.py
async def call_claude_api(prompt: str, max_tokens: int = 4000) -> str:
    """
    Call Claude API with given prompt.
    Returns response text.
    Raises exception if API call fails.
    """
    # Use existing Claude API integration
    # Add error handling
    # Return parsed response
```

### **Step 4: Helper Functions**
```python
# app/services/interview_prep_service.py

def get_resume_text(job_application_id: str, db: Session) -> str:
    """Fetch resume text for given application."""
    pass

def get_job_description(job_application_id: str, db: Session) -> str:
    """Fetch job description for given application."""
    pass

def get_fit_analysis(job_application_id: str, db: Session) -> Dict:
    """Fetch fit analysis if exists."""
    pass

def parse_claude_json_response(response_text: str) -> Dict:
    """
    Parse Claude response as JSON.
    Handle markdown code blocks if present.
    Raise exception if invalid JSON.
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

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())

def estimate_speaking_time(word_count: int, wpm: int = 140) -> int:
    """Estimate speaking time in seconds given word count."""
    return int((word_count / wpm) * 60)
```

### **Step 5: Testing**
```python
# tests/test_interview_prep.py

def test_generate_recruiter_screen_prep():
    """Test recruiter screen prep generation."""
    # Create test job application
    # Call endpoint
    # Assert response structure
    # Assert no fabricated content
    pass

def test_generate_intro_sell_template():
    """Test intro sell template generation."""
    # Call endpoint
    # Assert word count in range
    # Assert uses real resume content
    pass

def test_intro_sell_feedback():
    """Test intro sell feedback analysis."""
    # Submit candidate version
    # Assert scores returned
    # Assert revised version provided
    pass

def test_interview_debrief_with_transcript():
    """Test debrief with transcript upload."""
    # Submit transcript
    # Assert structured feedback
    # Assert thank-you email generated
    pass

def test_interview_debrief_typed():
    """Test debrief with typed responses."""
    # Submit typed debrief
    # Assert feedback generated
    pass
```

---

## **Error Handling**

```python
# Common error scenarios

# 1. Job application not found
if not job_application:
    raise HTTPException(status_code=404, detail="Job application not found")

# 2. Invalid interview stage
if interview_stage not in ["recruiter_screen", "hiring_manager"]:
    raise HTTPException(status_code=400, detail="Invalid interview stage")

# 3. Claude API failure
try:
    response = await call_claude_api(prompt)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

# 4. Invalid JSON from Claude
try:
    parsed = parse_claude_json_response(response)
except ValueError as e:
    raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")

# 5. Missing required data (resume, JD)
if not resume_text:
    raise HTTPException(status_code=400, detail="Resume not found for this application")
```

---

## **Integration Points**

### **Existing Tables/Endpoints to Reference**

```python
# Reference existing job_applications table
job_application = db.query(JobApplication).filter(
    JobApplication.id == job_application_id
).first()

# Reference existing candidate_resumes table
resume = db.query(CandidateResume).filter(
    CandidateResume.candidate_id == job_application.candidate_id
).first()

# Reference existing fit_analysis table (if exists)
fit_analysis = db.query(FitAnalysis).filter(
    FitAnalysis.job_application_id == job_application_id
).first()
```

### **Frontend Expectations**

Frontend will call these endpoints and expect:
- Consistent JSON structure
- Clear error messages
- No undefined/null fields in critical response paths
- Fast response times (<5 seconds for generation, <2 seconds for feedback)

---

## **Validation Rules**

```python
def validate_interview_prep_content(content: Dict) -> bool:
    """
    Validate that prep content has all required fields.
    Raise ValueError if validation fails.
    """
    required_fields = [
        "interview_overview",
        "key_talking_points",
        "red_flag_mitigation",
        "likely_questions",
        "questions_to_ask"
    ]
    
    for field in required_fields:
        if field not in content:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate no empty arrays
    if not content["key_talking_points"]:
        raise ValueError("key_talking_points cannot be empty")
    
    return True

def validate_no_fabrication(content: str, resume_text: str) -> bool:
    """
    Basic check that content references resume information.
    This is not foolproof but catches obvious fabrications.
    """
    # Check for common fabrication patterns
    fabrication_phrases = [
        "for example", "such as", "including but not limited to",
        "hypothetically", "you could say"
    ]
    
    lower_content = content.lower()
    for phrase in fabrication_phrases:
        if phrase in lower_content:
            raise ValueError(f"Potential fabrication detected: '{phrase}'")
    
    return True
```

---

## **Performance Considerations**

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_resume(resume_id: str) -> str:
    """Cache resume text to avoid repeated DB queries."""
    pass

# Async Claude API calls
import asyncio

async def generate_prep_and_email_parallel(prep_prompt: str, email_prompt: str):
    """Generate prep and email in parallel to reduce latency."""
    prep_task = call_claude_api(prep_prompt)
    email_task = call_claude_api(email_prompt)
    
    prep_response, email_response = await asyncio.gather(prep_task, email_task)
    return prep_response, email_response
```

---

## **Deployment Checklist**

- [ ] Database migrations run successfully
- [ ] All endpoints return expected JSON structure
- [ ] Error handling covers common failure scenarios
- [ ] No fabricated content in generated outputs (spot check 10+ examples)
- [ ] Response times <5s for generation endpoints
- [ ] Frontend can consume responses without modification
- [ ] All tests passing
- [ ] Logging added for debugging (prompt used, response received, errors)
- [ ] API documentation updated (if using Swagger/OpenAPI)

---

## **Example Endpoint Implementations**

### **Generate Interview Prep Endpoint**

```python
@router.post("/api/interview-prep/generate", response_model=InterviewPrepResponse)
async def generate_interview_prep(
    request: InterviewPrepRequest,
    db: Session = Depends(get_db)
):
    """Generate stage-specific interview prep."""
    
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
    
    # Fetch job description
    job_description = job_application.job_description
    
    # Fetch fit analysis (optional)
    fit_analysis = db.query(FitAnalysis).filter(
        FitAnalysis.job_application_id == request.job_application_id
    ).first()
    
    fit_analysis_text = json.dumps(fit_analysis.analysis_content) if fit_analysis else "No fit analysis available"
    
    # Select prompt based on stage
    if request.interview_stage == "recruiter_screen":
        prompt = RECRUITER_SCREEN_PREP_PROMPT.format(
            resume_text=resume.resume_text,
            job_description=job_description,
            fit_analysis=fit_analysis_text
        )
    else:  # hiring_manager
        prompt = HIRING_MANAGER_PREP_PROMPT.format(
            resume_text=resume.resume_text,
            job_description=job_description,
            fit_analysis=fit_analysis_text
        )
    
    # Call Claude API
    try:
        response_text = await call_claude_api(prompt, max_tokens=4000)
        prep_content = parse_claude_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate prep: {str(e)}")
    
    # Validate content
    try:
        validate_interview_prep_content(prep_content)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Invalid prep content: {str(e)}")
    
    # Store in database
    interview_prep = InterviewPrep(
        job_application_id=request.job_application_id,
        interview_stage=request.interview_stage,
        prep_content=prep_content
    )
    
    # Check if prep already exists
    existing_prep = db.query(InterviewPrep).filter(
        InterviewPrep.job_application_id == request.job_application_id,
        InterviewPrep.interview_stage == request.interview_stage
    ).first()
    
    if existing_prep:
        existing_prep.prep_content = prep_content
        existing_prep.generated_at = datetime.now()
    else:
        db.add(interview_prep)
    
    db.commit()
    
    return InterviewPrepResponse(
        interview_stage=request.interview_stage,
        prep_content=prep_content
    )
```

### **Intro Sell Feedback Endpoint**

```python
@router.post("/api/interview-prep/intro-sell/feedback", response_model=IntroSellFeedbackResponse)
async def analyze_intro_sell(
    request: IntroSellFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Analyze candidate's intro sell attempt."""
    
    # Fetch job application and resume
    job_application = db.query(JobApplication).filter(
        JobApplication.id == request.job_application_id
    ).first()
    
    if not job_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    resume = db.query(CandidateResume).filter(
        CandidateResume.candidate_id == job_application.candidate_id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=400, detail="Resume not found")
    
    # Count words and estimate time
    word_count = count_words(request.candidate_version)
    estimated_time = estimate_speaking_time(word_count)
    
    # Generate feedback prompt
    prompt = INTRO_SELL_FEEDBACK_PROMPT.format(
        candidate_version=request.candidate_version,
        resume_text=resume.resume_text,
        job_description=job_application.job_description
    )
    
    # Call Claude API
    try:
        response_text = await call_claude_api(prompt, max_tokens=2000)
        feedback = parse_claude_json_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze intro sell: {str(e)}")
    
    # Get attempt number
    attempt_count = db.query(IntroSellAttempt).filter(
        IntroSellAttempt.job_application_id == request.job_application_id
    ).count()
    
    # Store attempt
    attempt = IntroSellAttempt(
        job_application_id=request.job_application_id,
        attempt_number=attempt_count + 1,
        candidate_version=request.candidate_version,
        word_count=word_count,
        feedback=feedback
    )
    db.add(attempt)
    db.commit()
    
    return IntroSellFeedbackResponse(
        overall_score=feedback["overall_score"],
        content_score=feedback["content_score"],
        structure_score=feedback["structure_score"],
        tone_score=feedback["tone_score"],
        word_count=word_count,
        estimated_time_seconds=estimated_time,
        strengths=feedback["strengths"],
        opportunities=feedback["opportunities"],
        revised_version=feedback["revised_version"],
        coaching_note=feedback["coaching_note"]
    )
```

---

## **Next Steps After Implementation**

1. **Test with real resumes and job descriptions**
   - Verify no fabrication
   - Check quality of STAR examples
   - Validate prep is actionable

2. **Gather user feedback**
   - Is prep helpful?
   - Are practice sessions improving performance?
   - Are debriefs actionable?

3. **Monitor API costs**
   - Claude API token usage per endpoint
   - Optimize prompts if costs too high

4. **Phase 2 Features**
   - Audio upload for intro sell
   - Conversational practice mode (full chat)
   - Panel interview prep
   - Salary negotiation prep

---

**End of Implementation Spec**
