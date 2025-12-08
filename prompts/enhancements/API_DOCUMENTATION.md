# Henry Job Search Engine - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add API key auth in production).

---

## Core Endpoints

### 1. Resume Parsing

**Endpoint:** `POST /api/resume/parse`

**Description:** Parses resume from file upload, text, or LinkedIn URL and returns structured JSON profile.

**Request:**
```bash
# File upload
curl -X POST "http://localhost:8000/api/resume/parse" \
  -F "file=@resume.pdf"

# Text input
curl -X POST "http://localhost:8000/api/resume/parse" \
  -F "resume_text=<paste resume text here>"

# LinkedIn URL
curl -X POST "http://localhost:8000/api/resume/parse" \
  -F "linkedin_url=https://linkedin.com/in/yourprofile"
```

**Response:**
```json
{
  "full_name": "Henry Smith",
  "current_title": "Director & Global Head of Recruitment",
  "target_roles": ["VP Talent Acquisition", "Head of Recruiting"],
  "industries": ["Technology", "Finance"],
  "years_experience": "10+",
  "summary": "Results-driven recruiting leader with 10+ years experience...",
  "experience": [
    {
      "company": "National Grid",
      "title": "Director & Global Head of Recruitment",
      "dates": "2022 – 2024",
      "industry": "Energy",
      "bullets": [
        "Led global recruitment strategy across 15+ countries",
        "Managed team of 12 recruiters"
      ]
    }
  ],
  "key_achievements": [
    "95% hiring plan attainment",
    "22% reduction in time-to-fill"
  ],
  "core_competencies": [
    "Strategic Talent Acquisition",
    "Executive Search"
  ],
  "skills": [
    "ATS Systems",
    "Data-Driven Decision Making",
    "DEI Recruiting"
  ],
  "education": "B.A. in Social Sciences, NYU"
}
```

---

### 2. Job Description Analysis

**Endpoint:** `POST /api/jd/analyze`

**Description:** Analyzes job description and computes fit score with candidate profile.

**Request:**
```json
{
  "company": "Stripe",
  "role_title": "Director of Talent Acquisition",
  "job_description": "We are seeking an experienced...",
  "resume": { /* resume JSON from parse endpoint */ },
  "preferences": {
    "fullName": "Henry Smith",
    "industry": "Technology",
    "comp": "$190K+"
  }
}
```

**Response:**
```json
{
  "company": "Stripe",
  "role_title": "Director of Talent Acquisition",
  "company_context": "Stripe is a leading fintech company...",
  "role_overview": "This role will lead recruiting strategy...",
  "key_responsibilities": [
    "Build and scale global recruiting team",
    "Partner with executive leadership",
    "Implement data-driven hiring processes"
  ],
  "required_skills": [
    "10+ years recruiting experience",
    "Leadership of recruiting teams",
    "Tech industry experience"
  ],
  "preferred_skills": [
    "Fintech experience",
    "Greenhouse ATS proficiency"
  ],
  "ats_keywords": [
    "talent acquisition",
    "recruiting strategy",
    "team leadership",
    "ATS",
    "data-driven"
  ],
  "fit_score": 92,
  "strengths": [
    "10+ years recruiting leadership experience",
    "Proven track record scaling teams",
    "Strong metrics and data orientation"
  ],
  "gaps": [
    "Limited fintech-specific experience",
    "No Greenhouse ATS mentioned"
  ],
  "strategic_positioning": "Emphasize scaling experience from Spotify and leadership at National Grid...",
  "salary_info": "$180K - $220K + equity"
}
```

**Fit Score Calculation:**
- 50% responsibilities alignment
- 30% required experience match
- 20% industry/domain alignment
- Range: 0-100

---

### 3. Document Generation

**Endpoint:** `POST /api/documents/generate`

**Description:** Generates tailored resume and cover letter content optimized for ATS.

**Request:**
```json
{
  "resume": { /* resume JSON from parse endpoint */ },
  "jd_analysis": { /* JD analysis JSON */ },
  "preferences": {
    "fullName": "Henry Smith",
    "tone": "professional"
  }
}
```

**Response:**
```json
{
  "resume": {
    "summary": "Results-driven recruiting leader with 10+ years of progressive experience building high-performing talent acquisition teams in fast-paced technology environments. Proven track record of implementing data-driven hiring strategies that drive business growth and improve quality of hire.",
    "skills": [
      "Strategic Talent Acquisition",
      "Executive Search",
      "ATS Systems (Greenhouse, Workday)",
      "Data-Driven Decision Making",
      "Team Leadership"
    ],
    "experience": [
      {
        "company": "National Grid",
        "title": "Director & Global Head of Recruitment",
        "dates": "2022 – 2024",
        "bullets": [
          "Led global recruitment strategy across 15+ countries, driving 95% hiring plan attainment while reducing time-to-fill by 22%",
          "Partnered with C-suite executives to build scalable talent acquisition roadmap aligned with organizational growth"
        ]
      }
    ]
  },
  "cover_letter": {
    "greeting": "Dear Hiring Manager,",
    "opening": "I am writing to express my strong interest in the Director of Talent Acquisition position at Stripe...",
    "body": "Throughout my career, I have consistently delivered measurable results...",
    "closing": "I would welcome the opportunity to discuss how my experience can contribute to Stripe's continued growth...",
    "full_text": "Dear Hiring Manager,\n\nI am writing to express my strong interest..."
  }
}
```

---

## MVP+1 Feature Endpoints

### 4. Daily Command Center - Task Prioritization

**Endpoint:** `POST /api/tasks/prioritize`

**Description:** Analyzes applications and creates prioritized daily task list focusing on highest-leverage activities.

**Use Case:** Generate a focused "what to do today" list based on application status, fit scores, and timing.

**Request:**
```json
{
  "applications": [
    {
      "id": "app-001",
      "company": "Stripe",
      "role_title": "Director of Talent Acquisition",
      "fit_score": 92,
      "stage": "applied",
      "last_activity_date": "2024-11-17T10:00:00Z",
      "has_outreach": false
    },
    {
      "id": "app-002",
      "company": "Airbnb",
      "role_title": "Head of Recruiting",
      "fit_score": 88,
      "stage": "screen",
      "last_activity_date": "2024-11-10T15:30:00Z",
      "has_outreach": true
    }
  ],
  "today": "2024-11-24T09:00:00Z"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "type": "follow_up",
      "application_id": "app-002",
      "priority": 1,
      "reason": "Phone screen was 2 weeks ago with no follow-up. High fit score (88) and already in conversation - critical to maintain momentum.",
      "suggested_message_stub": "Hi [Recruiter], I wanted to follow up on our phone conversation from two weeks ago. I remain very excited about the Head of Recruiting role and would love to discuss next steps."
    },
    {
      "type": "outreach",
      "application_id": "app-001",
      "priority": 1,
      "reason": "Highest fit score (92) but no network outreach yet. Applied last week - perfect timing to leverage connections.",
      "suggested_message_stub": "Hi [Contact], I recently applied for the Director of Talent Acquisition role at Stripe and would love to get your perspective on the team and role."
    },
    {
      "type": "apply",
      "application_id": "app-003",
      "priority": 2,
      "reason": "Strong fit (85) at growing company. Application should be straightforward with existing materials.",
      "suggested_message_stub": null
    }
  ]
}
```

**Task Types:**
- `apply`: Apply to this role
- `follow_up`: Send follow-up message to recruiter/company
- `outreach`: Reach out to network contact about role

**Priority Levels:**
- `1`: Critical - do today
- `2`: Important - do this week
- `3`: Nice to have - when you have time

**Prioritization Logic:**
- High fit (70+) + recent activity = high priority
- Applied but no follow-up in 5-7+ days = follow-up task
- Screen/onsite stage without contact = follow-up task
- High fit without network outreach = outreach task

---

### 5a. Learning/Feedback Loop - Log Outcome

**Endpoint:** `POST /api/outcomes/log`

**Description:** Logs outcome data for an application to enable pattern analysis.

**Use Case:** Track what happens with applications over time (viewed, replied, interviews, offers, rejections).

**Request:**
```json
{
  "application_id": "app-001",
  "stage": "viewed",
  "outcome": "Application viewed by recruiter on LinkedIn",
  "date": "2024-11-24T14:30:00Z"
}
```

**Stages:**
- `applied`: Initial application submitted
- `viewed`: Application viewed/opened
- `replied`: Received response
- `interview`: Interview scheduled/completed
- `offer`: Offer received
- `rejected`: Application rejected

**Response:**
```json
{
  "status": "success",
  "message": "Outcome logged for application app-001",
  "total_outcomes": 15
}
```

**Notes:**
- Currently uses in-memory storage (resets on server restart)
- In production, replace with database persistence
- Used for pattern analysis in strategy review endpoint

---

### 5b. Learning/Feedback Loop - Strategy Review

**Endpoint:** `POST /api/strategy/review`

**Description:** Analyzes patterns in applications and outcomes to provide strategic insights and recommendations.

**Use Case:** Periodic review (weekly/monthly) to identify what's working and adjust strategy.

**Request:**
```json
{
  "applications": [
    {
      "id": "app-001",
      "company": "Stripe",
      "role_title": "Director of Talent Acquisition",
      "fit_score": 92,
      "stage": "viewed",
      "applied_date": "2024-11-10"
    },
    {
      "id": "app-002",
      "company": "Meta",
      "role_title": "Recruiting Manager",
      "fit_score": 72,
      "stage": "rejected",
      "applied_date": "2024-10-28"
    }
  ],
  "outcomes": [
    {
      "application_id": "app-001",
      "stage": "viewed",
      "outcome": "Application viewed by recruiter",
      "date": "2024-11-15"
    },
    {
      "application_id": "app-002",
      "stage": "rejected",
      "outcome": "Rejection - seeking more startup experience",
      "date": "2024-11-05"
    }
  ]
}
```

**Response:**
```json
{
  "insights": [
    "High fit scores (85+) are converting to phone screens at 75% rate, while lower fit (<75) convert at only 20%",
    "Applications to fintech companies are advancing more frequently than traditional tech, likely due to transferable financial services experience",
    "Roles with 'Director' or 'Head' titles are progressing further than 'VP' level roles, suggesting positioning at director level is stronger",
    "Follow-up messages sent within 5-7 days of application are getting responses 60% of the time",
    "Rejections cite 'startup experience' gap most frequently - this is a consistent pattern"
  ],
  "recommendations": [
    "Focus applications on high-fit roles (85+ fit score) - these have 3x better conversion rate",
    "Prioritize fintech and financial services companies where domain experience is valued",
    "Target Director-level roles rather than VP roles to maximize interview progression",
    "Systematically follow up on all applications within 5-7 days of submission",
    "Address startup experience gap proactively in cover letters by emphasizing scaling experience from Spotify hyper-growth phase"
  ]
}
```

**Analysis Framework:**
- Success patterns: What's advancing to interviews/offers?
- Challenge patterns: What's getting rejected and why?
- Fit score correlation: Do higher scores predict success?
- Stage progression: Where do applications typically stall?
- Timing patterns: Optimal follow-up timing?

---

### 6. Network Engine - Contact Recommendations

**Endpoint:** `POST /api/network/recommend`

**Description:** Analyzes network contacts and recommends best people to reach out to for a specific role.

**Use Case:** Identify who in your network can help with a target company/role (referrals, intros, intel).

**Request:**
```json
{
  "company": "Stripe",
  "role_title": "Director of Talent Acquisition",
  "contacts": [
    {
      "name": "Sarah Chen",
      "company": "Stripe",
      "title": "Engineering Manager",
      "relationship": "former colleague from Spotify"
    },
    {
      "name": "Jessica Lee",
      "company": "Square",
      "title": "VP Talent Acquisition",
      "relationship": "close friend and mentor"
    },
    {
      "name": "Michael Torres",
      "company": "Stripe",
      "title": "Head of People Operations",
      "relationship": "LinkedIn connection, met at conference"
    }
  ]
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "name": "Michael Torres",
      "company": "Stripe",
      "title": "Head of People Operations",
      "relationship": "LinkedIn connection, met at conference",
      "priority": 1,
      "reason": "Works directly at Stripe in People Ops leadership - likely involved in or aware of recruiting leadership hiring. Can provide internal referral and context on team/role.",
      "suggested_message_stub": "Hi Michael, I hope you're doing well! I recently applied for the Director of Talent Acquisition role at Stripe and would love to get your perspective on the team and what you're looking for in this hire."
    },
    {
      "name": "Sarah Chen",
      "company": "Stripe",
      "title": "Engineering Manager",
      "relationship": "former colleague from Spotify",
      "priority": 1,
      "reason": "Works at Stripe with strong prior relationship from Spotify. Can speak to your work firsthand and provide warm referral to hiring team.",
      "suggested_message_stub": "Hey Sarah! I saw Stripe is hiring a Director of TA and immediately thought of our work together at Spotify. Would you be open to a quick call to share your thoughts on Stripe's recruiting team and culture?"
    },
    {
      "name": "Jessica Lee",
      "company": "Square",
      "title": "VP Talent Acquisition",
      "relationship": "close friend and mentor",
      "priority": 2,
      "reason": "Similar fintech space (Square/Stripe) and exact functional expertise. May know Stripe's TA leadership personally and could make introduction or provide strategic advice.",
      "suggested_message_stub": "Hi Jessica, I'm exploring the Director of TA role at Stripe. Given your experience in fintech recruiting, I'd love your take on Stripe's recruiting organization and any insights you might have."
    }
  ]
}
```

**Ranking Criteria:**
1. Current company match (works at target = highest priority)
2. Role relevance (hiring influence or similar function)
3. Relationship strength (former colleague > friend > weak tie)
4. Help potential (referral > intro > intel > advice)

**Priority Levels:**
- `1`: Direct connection to company or strong relationship + relevance
- `2`: Strong relationship or relevant role but indirect
- `3`: Weak connection but potentially helpful

**Message Stub Guidelines:**
- Personalized based on relationship
- Clear ask (referral, intro, advice, intel)
- Respectful of their time
- 1-2 sentences max

---

## Frontend Integration Examples

### Task Prioritization Integration

```javascript
// Add to your JavaScript
async function getDailyTasks() {
  const applications = [
    // Your tracked applications
  ];
  
  const response = await fetch(`${API_BASE_URL}/api/tasks/prioritize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      applications: applications,
      today: new Date().toISOString()
    })
  });
  
  const result = await response.json();
  window.dailyTasks = result.tasks;
  
  // Display tasks in UI
  displayDailyTasks(result.tasks);
}
```

### Outcome Logging Integration

```javascript
async function logApplicationOutcome(appId, stage, outcome) {
  await fetch(`${API_BASE_URL}/api/outcomes/log`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      application_id: appId,
      stage: stage,
      outcome: outcome,
      date: new Date().toISOString()
    })
  });
}
```

### Network Recommendations Integration

```javascript
async function getNetworkRecommendations(company, role) {
  const contacts = [
    // User's network contacts
  ];
  
  const response = await fetch(`${API_BASE_URL}/api/network/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company: company,
      role_title: role,
      contacts: contacts
    })
  });
  
  const result = await response.json();
  return result.recommendations;
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid input)
- `422`: Validation error (Pydantic)
- `500`: Server error (Claude API error or parsing failure)

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limits

Currently no rate limits (add in production).

Recommended for production:
- 100 requests per hour per IP
- 10 requests per minute for Claude-heavy endpoints

---

## Development & Testing

### Start Server
```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run server
python backend.py
```

### Run Tests
```bash
# Test all endpoints
python test_mvp_plus_features.py

# Test individual features
curl -X POST "http://localhost:8000/api/tasks/prioritize" \
  -H "Content-Type: application/json" \
  -d @test_data/tasks_request.json
```

### Interactive API Docs
FastAPI provides automatic interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Production Considerations

### Required Changes for Production:

1. **Authentication:**
   - Add API key authentication
   - Implement user sessions
   - Rate limiting per user

2. **Database:**
   - Replace in-memory outcomes storage
   - Persist application tracking
   - Store user profiles

3. **CORS:**
   - Restrict `allow_origins` to your frontend domain
   - Remove wildcard `*`

4. **Error Handling:**
   - Add proper logging (Sentry, CloudWatch)
   - More detailed error messages in dev
   - Generic errors in production

5. **Caching:**
   - Cache Claude responses for identical requests
   - Redis for session management

6. **Monitoring:**
   - Track API usage
   - Monitor Claude API costs
   - Alert on failures

---

## Support

For issues or questions:
- Check interactive docs: http://localhost:8000/docs
- Review test script: `test_mvp_plus_features.py`
- Examine backend code: `backend.py`
