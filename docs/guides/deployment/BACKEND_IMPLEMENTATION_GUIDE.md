# BACKEND IMPLEMENTATION GUIDE
## Phase 1: Strategic Intelligence Features

**Last Updated**: December 16, 2025
**Status**: Phase 1 COMPLETE, Phase 2 In Progress

This guide covers all backend changes needed to support the new strategic intelligence sections in package.html.

---

## **OVERVIEW**

We're adding 4 new sections to the application package:
1. **Strategic Positioning** (emphasize/de-emphasize)
2. **Action Plan** (TODAY/TOMORROW/THIS WEEK tasks)
3. **Salary Strategy** (ranges, approach, talking points)
4. **Hiring Manager/Recruiter Intel** (lightweight, no CSV required)

---

## **STEP 1: UPDATE CLAUDE PROMPT**

Location: `/api/jd/analyze` endpoint

Add these sections to your Claude prompt:

```python
ANALYSIS_PROMPT = f"""
You are analyzing a job description and providing strategic guidance for a job application.

CANDIDATE RESUME:
{resume_data}

JOB DESCRIPTION:
{job_description}

USER LOCATION: {user_location}  # e.g., "New York, NY"
CANDIDATE EXPERIENCE LEVEL: {experience_level}  # e.g., "Senior" (10+ years)

Generate a complete strategic analysis with the following sections.

Return your response as JSON with this EXACT structure:

{{
  "fit_score": 87,
  "fit_explanation": "2-3 sentences explaining fit",
  "strengths": ["bullet 1", "bullet 2", "bullet 3"],
  "gaps": ["bullet 1", "bullet 2"],
  "recommendation": "Strongly Apply / Apply / Conditional Apply / Do Not Apply + rationale",
  
  "positioning_strategy": {{
    "emphasize": [
      "Your fintech experience at Uber Payments and Venmo - directly relevant to this role",
      "Track record building recruiting teams from scratch (3x)",
      "Hands-on execution combined with strategic thinking"
    ],
    "de_emphasize": [
      "National Grid utility context - doesn't map to startup environment",
      "Managing large teams - this role wants 75% execution, not pure leadership"
    ],
    "framing": "This positions you as someone who can step into a Series B environment and own recruiting strategy from day one, not just manage a team."
  }},
  
  "action_plan": {{
    "today": [
      "Apply via company ATS before end of day",
      "Research hiring manager on LinkedIn (search '[Company Name] talent acquisition')",
      "Check Glassdoor for company reviews (filter by 'recruiting' or 'talent acquisition')"
    ],
    "tomorrow": [
      "Send hiring manager outreach using template below",
      "Reach out to any network connections at [Company Name]"
    ],
    "this_week": [
      "Follow up if no response by Day 5",
      "Review phone screen prep daily",
      "Monitor LinkedIn for recruiter outreach"
    ]
  }},
  
  "salary_strategy": {{
    "their_range": "$180K-$220K (as posted)" OR "Not disclosed in job description",
    "your_target": "$190K-$220K base (based on {experience_level} experience level and {user_location} market)",
    "market_data": "Glassdoor shows $195K median for Director of Talent Acquisition in New York, NY. Levels.fyi shows $185K-$230K for Series B startups.",
    "approach": "Don't bring up salary first. If they ask early, say 'I'm targeting $190K-$220K base but flexible on the mix if equity is meaningful.' If they offer $180K, negotiate to $200K+ using your experience level and fintech background as leverage.",
    "talking_points": [
      "You've managed 25-person global teams at Spotify - this justifies higher end of range",
      "Fintech background (Uber Payments, Venmo) is directly relevant - you're not learning on the job",
      "You're taking a hands-on role despite strategic experience - could command more for pure strategy role"
    ]
  }},
  
  "hiring_intel": {{
    "hiring_manager": {{
      "likely_title": "VP of Talent Acquisition" OR "Director of People" OR "Head of Recruiting" (based on company size and role level),
      "search_instructions": "LinkedIn search: \"[Company Name] talent acquisition\" OR \"[Company Name] recruiting\"",
      "filters": "Filter by: Current employees, Director+ level, posted about hiring recently"
    }},
    "recruiter": {{
      "likely_title": "Technical Recruiter" OR "Talent Acquisition Partner" (based on role focus),
      "search_instructions": "LinkedIn search: \"[Company Name] technical recruiter\" OR \"[Company Name] talent acquisition partner\"",
      "filters": "Filter by: Current employees, recent activity, profile mentions engineering/product recruiting"
    }}
  }},
  
  "interview_prep": {{
    "narrative": "3-4 sentence story for framing alignment",
    "talking_points": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"],
    "gap_mitigation": ["concern + mitigation 1", "concern + mitigation 2"]
  }},
  
  "outreach": {{
    "hiring_manager": "3-5 sentence message",
    "recruiter": "3-5 sentence message",
    "linkedin_help_text": "Step-by-step instructions"
  }}
}}

RULES FOR POSITIONING STRATEGY:
- Use specific examples from candidate's resume (not generic: "your fintech experience" not "your relevant experience")
- Emphasize section: 3-5 bullets highlighting what makes them competitive
- De-emphasize section: 2-3 bullets on what to downplay (doesn't mean hide, just don't lead with)
- Framing: 1-2 sentences that synthesize the strategic narrative

RULES FOR ACTION PLAN:
- Reference actual company name in tasks
- TODAY: 3-4 tasks focused on application + research
- TOMORROW: 2-3 tasks focused on outreach
- THIS WEEK: 3-4 tasks focused on follow-up and preparation
- Be specific (not "apply" but "apply via company ATS before end of day")

RULES FOR SALARY STRATEGY:
- Extract their range from JD if present, otherwise say "Not disclosed"
- Your target should be based on candidate's experience level and location
- Market data should reference specific sources (Glassdoor, Levels.fyi, Payscale)
- Approach should be 2-3 sentences on negotiation timing and strategy
- Talking points should justify higher compensation based on candidate's background

RULES FOR HIRING INTEL:
- Titles should be based on company size (startup = fewer roles, enterprise = more specialized)
- Search instructions should be actual LinkedIn queries they can copy/paste
- Filters should explain how to narrow results
- If company is very small (<50 employees), hiring manager might be CEO or COO

CRITICAL: NEVER return null, undefined, or empty strings for ANY field.
"""
```

---

## **STEP 2: UPDATE RESPONSE VALIDATION**

Add validation function to ensure all fields are present:

```python
def validate_analysis_response(analysis_data):
    """
    Validates that all required fields in the analysis response are present and non-empty.
    Raises ValueError if validation fails.
    """
    
    required_top_level = {
        "fit_score": int,
        "fit_explanation": str,
        "strengths": list,
        "gaps": list,
        "recommendation": str,
        "positioning_strategy": dict,
        "action_plan": dict,
        "salary_strategy": dict,
        "hiring_intel": dict,
        "interview_prep": dict,
        "outreach": dict
    }
    
    # Check top-level fields exist and are correct type
    for field, expected_type in required_top_level.items():
        if field not in analysis_data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(analysis_data[field], expected_type):
            raise ValueError(f"Field '{field}' should be {expected_type.__name__}, got {type(analysis_data[field]).__name__}")
    
    # Validate positioning_strategy
    ps = analysis_data["positioning_strategy"]
    if not ps.get("emphasize") or len(ps.get("emphasize", [])) == 0:
        raise ValueError("positioning_strategy.emphasize must have at least 1 item")
    if not ps.get("de_emphasize") or len(ps.get("de_emphasize", [])) == 0:
        raise ValueError("positioning_strategy.de_emphasize must have at least 1 item")
    if not ps.get("framing") or not isinstance(ps.get("framing"), str):
        raise ValueError("positioning_strategy.framing must be a non-empty string")
    
    # Validate action_plan
    ap = analysis_data["action_plan"]
    if not ap.get("today") or len(ap.get("today", [])) == 0:
        raise ValueError("action_plan.today must have at least 1 task")
    if not ap.get("tomorrow") or len(ap.get("tomorrow", [])) == 0:
        raise ValueError("action_plan.tomorrow must have at least 1 task")
    if not ap.get("this_week") or len(ap.get("this_week", [])) == 0:
        raise ValueError("action_plan.this_week must have at least 1 task")
    
    # Validate salary_strategy
    ss = analysis_data["salary_strategy"]
    required_salary_fields = ["their_range", "your_target", "market_data", "approach", "talking_points"]
    for field in required_salary_fields:
        if not ss.get(field):
            raise ValueError(f"salary_strategy.{field} cannot be empty")
    if not isinstance(ss.get("talking_points"), list) or len(ss["talking_points"]) == 0:
        raise ValueError("salary_strategy.talking_points must be a non-empty list")
    
    # Validate hiring_intel
    hi = analysis_data["hiring_intel"]
    if not hi.get("hiring_manager") or not isinstance(hi["hiring_manager"], dict):
        raise ValueError("hiring_intel.hiring_manager must be a non-empty dict")
    if not hi.get("recruiter") or not isinstance(hi["recruiter"], dict):
        raise ValueError("hiring_intel.recruiter must be a non-empty dict")
    
    # Validate hiring_manager and recruiter have required fields
    for role in ["hiring_manager", "recruiter"]:
        role_data = hi[role]
        if not role_data.get("likely_title"):
            raise ValueError(f"hiring_intel.{role}.likely_title cannot be empty")
        if not role_data.get("search_instructions"):
            raise ValueError(f"hiring_intel.{role}.search_instructions cannot be empty")
        if not role_data.get("filters"):
            raise ValueError(f"hiring_intel.{role}.filters cannot be empty")
    
    # Validate interview_prep (existing)
    interview = analysis_data["interview_prep"]
    if not interview.get("narrative"):
        raise ValueError("interview_prep.narrative cannot be empty")
    if not interview.get("talking_points") or len(interview["talking_points"]) == 0:
        raise ValueError("interview_prep.talking_points must be a non-empty list")
    
    # Validate outreach (existing)
    outreach = analysis_data["outreach"]
    if not outreach.get("hiring_manager"):
        raise ValueError("outreach.hiring_manager cannot be empty")
    if not outreach.get("recruiter"):
        raise ValueError("outreach.recruiter cannot be empty")
    
    return True
```

---

## **STEP 3: UPDATE ENDPOINT**

Update your `/api/jd/analyze` endpoint:

```python
from fastapi import HTTPException
import json

@app.post("/api/jd/analyze")
async def analyze_job_description(request: AnalyzeRequest):
    """
    Analyzes a job description and returns comprehensive strategic guidance.
    """
    
    try:
        # Extract data from request
        resume_data = request.resume_data
        job_description = request.job_description
        user_location = request.user_location or "United States"
        
        # Determine experience level from resume
        # This is a simplified example - you might have more sophisticated logic
        experience_level = "Senior"  # or extract from resume parsing
        
        # Build the prompt
        prompt = ANALYSIS_PROMPT.format(
            resume_data=resume_data,
            job_description=job_description,
            user_location=user_location,
            experience_level=experience_level
        )
        
        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Handle markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis_data = json.loads(response_text)
        
        # Validate response
        try:
            validate_analysis_response(analysis_data)
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            print(f"Response data: {json.dumps(analysis_data, indent=2)}")
            raise HTTPException(
                status_code=500,
                detail=f"Analysis validation failed: {str(e)}"
            )
        
        # Add metadata
        analysis_data["_company"] = extract_company_name(job_description)
        analysis_data["_role"] = extract_role_title(job_description)
        analysis_data["_candidate_name"] = extract_candidate_name(resume_data)
        
        return analysis_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Response text: {response_text}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse analysis response. Please try again."
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis."
        )
```

---

## **STEP 4: HELPER FUNCTIONS**

Add these helper functions if you don't already have them:

```python
def extract_company_name(job_description: str) -> str:
    """
    Extracts company name from job description.
    Uses simple heuristics - can be improved.
    """
    # Look for patterns like "Company: XYZ" or "About XYZ:"
    # This is a placeholder - implement your own logic
    lines = job_description.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if 'company' in line.lower():
            # Extract company name
            # Placeholder logic
            pass
    return "the company"  # Fallback


def extract_role_title(job_description: str) -> str:
    """
    Extracts role title from job description.
    """
    # Look for patterns in first few lines
    # This is a placeholder - implement your own logic
    lines = job_description.split('\n')
    for line in lines[:5]:
        if any(keyword in line.lower() for keyword in ['director', 'manager', 'lead', 'head']):
            return line.strip()
    return "this role"  # Fallback


def extract_candidate_name(resume_data: str) -> str:
    """
    Extracts candidate name from resume.
    """
    # This should come from your resume parsing logic
    # Placeholder implementation
    lines = resume_data.split('\n')
    if lines:
        # Typically name is first line
        return lines[0].strip()
    return "You"  # Fallback
```

---

## **STEP 5: UPDATE REQUEST MODEL**

If you're using Pydantic models, update your request model:

```python
from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    resume_data: str
    job_description: str
    user_location: Optional[str] = "United States"
    candidate_name: Optional[str] = None
```

---

## **STEP 6: TESTING**

Test your endpoint with a sample request:

```python
# Test data
test_request = {
    "resume_data": "John Doe\nSenior Recruiter\n...",
    "job_description": "Company XYZ is hiring a Director of Talent Acquisition...",
    "user_location": "New York, NY"
}

# Make request
response = requests.post(
    "http://localhost:8000/api/jd/analyze",
    json=test_request
)

# Check response
assert response.status_code == 200
data = response.json()

# Validate all new fields exist
assert "positioning_strategy" in data
assert "emphasize" in data["positioning_strategy"]
assert "de_emphasize" in data["positioning_strategy"]
assert "framing" in data["positioning_strategy"]

assert "action_plan" in data
assert "today" in data["action_plan"]
assert "tomorrow" in data["action_plan"]
assert "this_week" in data["action_plan"]

assert "salary_strategy" in data
assert "their_range" in data["salary_strategy"]
assert "your_target" in data["salary_strategy"]
assert "market_data" in data["salary_strategy"]
assert "approach" in data["salary_strategy"]
assert "talking_points" in data["salary_strategy"]

assert "hiring_intel" in data
assert "hiring_manager" in data["hiring_intel"]
assert "recruiter" in data["hiring_intel"]

print("✓ All validation checks passed!")
```

---

## **ESTIMATED IMPLEMENTATION TIME**

- **Prompt updates:** 30 minutes
- **Validation function:** 20 minutes
- **Endpoint updates:** 30 minutes
- **Helper functions:** 20 minutes
- **Testing:** 30 minutes

**Total: ~2.5 hours**

---

## **COMMON ERRORS & FIXES**

### **Error: "Missing required field: positioning_strategy"**
**Cause:** Claude didn't return the field or returned null
**Fix:** Check your prompt includes clear examples and CRITICAL rules section

### **Error: "positioning_strategy.emphasize must have at least 1 item"**
**Cause:** Claude returned empty array
**Fix:** Add explicit instruction: "MUST include 3-5 items in emphasize array"

### **Error: JSON parsing failed**
**Cause:** Claude returned markdown code blocks
**Fix:** Add markdown stripping logic (already in code above)

### **Error: "salary_strategy.market_data cannot be empty"**
**Cause:** Claude didn't have enough context
**Fix:** Pass user location and experience level to Claude

---

## **NEXT STEPS AFTER BACKEND IS COMPLETE**

1. **Test with frontend:** Use the updated `package.html` (already provided)
2. **Verify all sections populate correctly**
3. **Test edge cases:** Missing data, very short JDs, unusual company names
4. **Get user feedback:** Does the strategic guidance feel valuable?

---

## **PHASE 1.5 PREPARATION (FUTURE)**

Once this is working, you'll be ready for Phase 1.5 (automation):
- Company research scraping (Glassdoor, LinkedIn)
- Automated salary data fetching
- LinkedIn OAuth integration (Phase 2)

But for now, focus on getting Phase 1 working perfectly with your beta testers.

---

## **QUESTIONS?**

If you hit any issues during implementation, check:
1. Is Claude returning valid JSON? (Check logs)
2. Are all fields populated? (Run validation function)
3. Does frontend receive data? (Check browser console)
4. Are fields displaying correctly? (Check element IDs match)

Good luck! 🚀

---

## **PHASE 2: RECENT ADDITIONS (Dec 15-16, 2025)**

The following features have been implemented and deployed:

### **6-Tier Graduated Recommendation System**

**Location**: `backend/backend.py` - `force_apply_experience_penalties()` function

The system now uses 6 recommendation tiers instead of binary Apply/Skip:

```python
def get_recommendation_from_score(capped_score: int) -> str:
    """Maps fit score to 6-tier recommendation."""
    if capped_score >= 85:
        return "Strong Apply"
    elif capped_score >= 70:
        return "Apply"
    elif capped_score >= 55:
        return "Consider"
    elif capped_score >= 40:
        return "Apply with Caution"
    elif capped_score >= 25:
        return "Long Shot"
    else:
        return "Do Not Apply"
```

---

### **Experience Penalty Hard Caps**

**Location**: `backend/backend.py` - Post-processing safety net

The backend now enforces hard caps on fit scores based on experience gaps:

```python
def force_apply_experience_penalties(analysis_data: dict, resume_data: dict, jd_analysis: dict) -> dict:
    """
    Backend safety net - applies experience penalties even if Claude missed them.
    """
    required_years = jd_analysis.get("required_years", 0)
    candidate_years = calculate_pm_years_from_resume(resume_data)

    if required_years > 0:
        years_percentage = (candidate_years / required_years) * 100

        # Hard cap logic
        if years_percentage < 50:
            hard_cap = 45
        elif years_percentage < 70:
            hard_cap = 60
        elif years_percentage < 90:
            hard_cap = 75
        else:
            hard_cap = 100  # No cap

        # Apply cap
        original_score = analysis_data.get("fit_score", 0)
        capped_score = min(original_score, hard_cap)

        if capped_score != original_score:
            analysis_data["fit_score"] = capped_score
            analysis_data["recommendation"] = get_recommendation_from_score(capped_score)
            analysis_data["_experience_cap_applied"] = True

    return analysis_data
```

---

### **Company Credibility Scoring**

Multiplier system for experience calculation based on company reputation:

```python
CREDIBILITY_MULTIPLIERS = {
    "HIGH": 1.0,    # Public companies, Series B+, established brands
    "MEDIUM": 0.7,  # Series A startups, 10-50 employees
    "LOW": 0.3,     # Seed-stage startups, <10 employees
    "ZERO": 0.0     # Operations roles with PM title, volunteer/side projects
}

def calculate_credible_years(experience: list) -> float:
    """
    Calculates experience years adjusted for company credibility.
    """
    total = 0.0
    for role in experience:
        years = parse_duration(role.get("dates", ""))
        credibility = assess_company_credibility(role.get("company", ""))
        total += years * CREDIBILITY_MULTIPLIERS.get(credibility, 0.7)
    return total
```

---

### **Candidate Identity Instruction**

**Location**: `backend/backend.py` - Lines 3162-3166 and 4317-4321

Added to both `/api/jd/analyze` and `/api/jd/analyze/stream`:

```python
IDENTITY_INSTRUCTION = """
🚨 CRITICAL: CANDIDATE IDENTITY 🚨
The candidate is the person whose resume was uploaded - NOT Henry, NOT any template, NOT a generic user.
When writing explanations, rationales, or strategic advice, use the candidate's actual name from their resume.
If no name is available, use "you/your" (second person) - NEVER use "Henry" as the candidate name.
Example: "Rawan, this role is a stretch..." or "This role is a stretch for your background..." - NOT "Henry, this role..."
"""
```

---

### **Streaming Endpoint (Experimental)**

**Location**: `backend/backend.py` - `/api/jd/analyze/stream`

New SSE streaming endpoint for real-time analysis:

```python
@app.post("/api/jd/analyze/stream")
async def analyze_job_description_stream(request: AnalyzeRequest):
    """
    Streaming version of JD analysis using Server-Sent Events.
    Returns partial results as they're generated.
    """
    async def event_generator():
        # Send start event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Analysis started'})}\n\n"

        # Stream partial results as Claude generates them
        for field, value in stream_analysis(request):
            yield f"data: {json.dumps({'type': 'partial', 'field': field, 'value': value})}\n\n"

        # Send complete event
        yield f"data: {json.dumps({'type': 'complete', 'data': full_analysis})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Status**: REVERTED from production (experience penalties not reflecting in partial data)
**Files preserved**: `streaming_test.html`, `analyzing_streaming.html`

---

### **LinkedIn Integration Endpoints**

**NEW Endpoints** (Dec 15, 2025):

```python
# Parse LinkedIn PDF
@app.post("/api/linkedin/upload")
async def upload_linkedin_pdf(file: UploadFile):
    """Parse LinkedIn PDF and extract profile data."""

# Compare LinkedIn to job requirements
@app.post("/api/linkedin/align")
async def check_linkedin_alignment(request: LinkedInAlignRequest):
    """Compare LinkedIn profile to job requirements."""

# Generate optimized LinkedIn sections
@app.post("/api/linkedin/optimize")
async def optimize_linkedin_profile(request: LinkedInOptimizeRequest):
    """Generate optimized headline, about, experience, skills."""
```

---

## **UPDATED API RESPONSE SCHEMA**

The `/api/jd/analyze` endpoint now returns additional fields:

```json
{
  "fit_score": 45,
  "recommendation": "Apply with Caution",
  "recommendation_details": {
    "tier": "Apply with Caution",
    "score_range": "40-54",
    "guidance": "Stretch role - be strategic about positioning"
  },
  "_experience_cap_applied": true,
  "_original_score": 72,
  "_candidate_years": 2.5,
  "_required_years": 5,
  "_years_percentage": 50,

  "reality_check": {
    "expected_applicants": 150,
    "company_credibility": "MEDIUM",
    "strategic_action": "Rawan, this is a competitive role..."
  },

  // ... existing fields ...
}
```

---

## **TESTING NEW FEATURES**

### Test Experience Caps

```python
# Test case: Junior candidate (2 years) applying for Senior role (5+ years)
test_request = {
    "resume_data": {"experience": [{"years": 2, "title": "Product Manager"}]},
    "jd_analysis": {"required_years": 5}
}

response = requests.post("/api/jd/analyze", json=test_request)
assert response.json()["fit_score"] <= 60  # Hard cap for 40% of required years
assert "Long Shot" in response.json()["recommendation"] or "Apply with Caution" in response.json()["recommendation"]
```

### Test Candidate Identity

```python
# Test case: Analysis should use candidate's name, not "Henry"
response = requests.post("/api/jd/analyze", json=test_request)
analysis = response.json()

assert "Henry" not in analysis.get("fit_explanation", "")
assert "Henry" not in analysis.get("recommendation", "")
assert "Henry" not in str(analysis.get("reality_check", {}))
```

### Test 6-Tier Recommendations

```python
# Test all tiers
test_scores = [90, 75, 60, 45, 30, 15]
expected_tiers = ["Strong Apply", "Apply", "Consider", "Apply with Caution", "Long Shot", "Do Not Apply"]

for score, expected_tier in zip(test_scores, expected_tiers):
    result = get_recommendation_from_score(score)
    assert result == expected_tier
```

---

## **DEPLOYMENT CHECKLIST (Dec 16)**

- [x] 6-tier recommendation system deployed
- [x] Experience penalty hard caps enforced
- [x] Company credibility scoring active
- [x] Candidate identity fix deployed
- [x] LinkedIn endpoints deployed
- [x] Streaming endpoint deployed (but reverted from frontend)
- [x] JSON repair function enhanced
- [x] Error handling improved with exponential backoff

---

## **NEXT STEPS**

1. **Re-enable streaming** - Fix experience penalty application in partial data
2. **Add credibility detection** - Auto-detect company stage from name/description
3. **Screening questions endpoint** - Phase 1.5 feature
4. **Document refinement endpoint** - Phase 1.5 feature
