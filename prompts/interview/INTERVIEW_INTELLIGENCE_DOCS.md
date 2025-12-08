# Interview Intelligence - API Documentation

## Overview

Interview Intelligence is an AI-powered system that helps candidates:
- Extract and classify interview questions from transcripts
- Receive detailed performance feedback on their answers
- Generate personalized thank-you emails
- Build a growing question bank for preparation

---

## Endpoints

### 1. Parse Interview Transcript

**Endpoint:** `POST /api/interview/parse`

**Description:** Extracts interview questions from transcript and classifies them by type, competency, and difficulty level. Identifies themes and potential issues.

**Use Case:** After an interview, upload or paste the transcript to understand what was asked and how questions mapped to competencies.

**Request:**
```json
{
  "transcript_text": "Full interview transcript with questions and answers",
  "role_title": "Director of Talent Acquisition",
  "company": "Stripe",
  "jd_analysis": {
    "key_responsibilities": ["..."],
    "required_skills": ["..."]
  }
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "Can you tell me about your experience scaling recruiting teams?",
      "type": "behavioral",
      "competency_tag": "Team Leadership",
      "difficulty": 3
    },
    {
      "question": "How do you think about building diverse and inclusive recruiting pipelines?",
      "type": "competency",
      "competency_tag": "DEI Recruiting",
      "difficulty": 3
    },
    {
      "question": "Tell me about your experience with metrics and data in recruiting.",
      "type": "technical",
      "competency_tag": "Data Fluency",
      "difficulty": 2
    }
  ],
  "themes": [
    "Heavy focus on scaling and growth experience",
    "Strong emphasis on metrics and data-driven decision making",
    "Cultural fit and DEI commitment assessment",
    "Strategic thinking and planning capabilities"
  ],
  "warnings": [
    "No questions about specific ATS tools mentioned in JD",
    "Limited probing on fintech-specific experience"
  ]
}
```

**Question Types:**
- `behavioral`: Past behavior questions (Tell me about a time...)
- `technical`: Skills assessment, domain knowledge
- `leadership`: People management, influence, decision-making
- `competency`: Role-specific skills (stakeholder management, etc.)
- `wildcard`: Unusual, creative, or off-script questions

**Competency Tags** (Modern Hiring Framework):
- Product Sense, Strategic Thinking, Data Fluency
- Stakeholder Management, Cross-Functional Collaboration
- Team Leadership, Coaching & Development, Conflict Resolution
- Process Design, Operational Excellence, Metrics & Analytics
- Communication, Presentation Skills, Executive Presence
- Adaptability, Learning Agility, Problem Solving
- Influence, Negotiation, Change Management
- Technical Expertise, Domain Knowledge

**Difficulty Levels:**
- `1`: Entry level, straightforward
- `2`: Mid-level, requires some depth
- `3`: Senior level, multi-faceted
- `4`: Executive level, strategic thinking required
- `5`: Extremely challenging, tests edge cases

---

### 2. Interview Performance Feedback

**Endpoint:** `POST /api/interview/feedback`

**Description:** Analyzes candidate's interview performance and provides detailed feedback on content, delivery, and areas for improvement. Uses STAR framework for behavioral questions.

**Use Case:** Get AI-powered coaching on your interview performance to improve for next rounds or future interviews.

**Request:**
```json
{
  "transcript_text": "Full interview transcript",
  "role_title": "Director of Talent Acquisition",
  "company": "Stripe",
  "questions": [
    {
      "question": "...",
      "type": "behavioral",
      "competency_tag": "Team Leadership",
      "difficulty": 3
    }
  ]
}
```

**Response:**
```json
{
  "overall_score": 82,
  "strengths": [
    "Strong use of specific metrics (95% attainment, 22% reduction in time-to-fill)",
    "Excellent STAR structure in behavioral responses with clear situation, action, and results",
    "Demonstrated strategic thinking by connecting tactical work to business outcomes",
    "Authentic enthusiasm for company mission came through naturally"
  ],
  "areas_for_improvement": [
    "Some answers ran long (2-3 minutes) - aim for 90-120 seconds with offer to elaborate",
    "Could strengthen connection to Stripe's specific challenges mentioned in JD",
    "Missed opportunity to ask clarifying questions before diving into answers",
    "Limited discussion of failures or lessons learned - shows growth mindset"
  ],
  "delivery_feedback": {
    "tone": "Professional and confident throughout. Good energy level that conveys enthusiasm without being over-the-top. Authentic and genuine in responses.",
    "pacing": "Generally good pacing, but tended to speed up slightly when discussing metrics and data. Practice pausing after key points for emphasis. Comfortable with silence.",
    "clarity": "Very clear communication. Complex ideas about recruiting frameworks explained in accessible terms. No unnecessary jargon. Strong narrative flow.",
    "structure": "Excellent structure on behavioral questions using STAR framework. Technical answers well-organized with clear setup and conclusion. Could improve transitions between topics."
  },
  "recommendations": [
    "Practice the '90-second rule': Answer core question in 90 seconds, then pause and ask 'Would you like me to elaborate on any aspect?'",
    "Prepare 2-3 specific questions about Stripe's recruiting challenges to demonstrate deeper preparation and genuine interest",
    "Work on incorporating one 'lesson learned' story that shows adaptability and growth mindset",
    "For next round, practice transitioning from answer to question: 'That's my experience with X. I'm curious - how does your team currently approach this?'",
    "Prepare concrete examples of fintech-specific recruiting challenges to address any perceived gap in direct industry experience"
  ]
}
```

**Scoring Framework (1-100):**
- **90-100**: Exceptional - compelling answers with strong examples and metrics
- **80-89**: Strong - good structure, clear communication, solid examples
- **70-79**: Good - adequate answers but missing some depth or polish
- **60-69**: Fair - needs improvement in structure, examples, or clarity
- **50-59**: Weak - significant gaps in content or delivery
- **Below 50**: Poor - major issues requiring substantial work

**Delivery Aspects:**
- **Tone**: Professional, conversational, enthusiastic? Any concerns?
- **Pacing**: Too fast, too slow, or well-modulated? Pauses for emphasis?
- **Clarity**: Easy to follow? Jargon-heavy? Clear structure?
- **Structure**: Organized responses? Answered actual question? Stayed on topic?

---

### 3. Generate Thank-You Email

**Endpoint:** `POST /api/interview/thank_you`

**Description:** Generates a professional, personalized thank-you email based on actual conversation topics from the interview. Concise (3-4 paragraphs) with modern professional tone.

**Use Case:** Quickly create a thoughtful thank-you email that references specific discussion points and reinforces your fit for the role.

**Request:**
```json
{
  "transcript_text": "Full interview transcript",
  "role_title": "Director of Talent Acquisition",
  "company": "Stripe",
  "interviewer_name": "Sarah Chen",
  "jd_analysis": {
    "company_context": "Leading fintech company...",
    "role_overview": "..."
  }
}
```

**Response:**
```json
{
  "subject": "Thank you - Director of Talent Acquisition conversation",
  "body": "Hi Sarah,\n\nThank you for taking the time to speak with me today about the Director of Talent Acquisition role at Stripe. I really enjoyed our conversation about scaling recruiting operations during hypergrowth phases and the unique challenges of competing for technical talent in today's market.\n\nOur discussion about implementing data-driven hiring frameworks particularly resonated with my experience at Spotify, where we took a similar approach to optimize for both speed and quality of hire. The challenge you mentioned around maintaining culture fit while scaling quickly is something I've navigated before and am excited to tackle at Stripe's stage.\n\nI'm very enthusiastic about the opportunity to bring my experience in building high-performing recruiting teams to Stripe. The mission to increase the GDP of the internet is compelling, and I'm excited about contributing to that goal through strategic talent acquisition.\n\nPlease let me know if there's any additional information I can provide as you move forward in the process.\n\nBest regards,\nHenry",
  "key_points_used": [
    "Scaling recruiting operations during hypergrowth",
    "Data-driven hiring frameworks from Spotify experience",
    "Competing for technical talent in tight market",
    "Maintaining culture fit while scaling quickly",
    "Stripe's mission to increase GDP of internet"
  ]
}
```

**Email Structure:**
- **Paragraph 1**: Thank them and reference something specific from conversation
- **Paragraph 2**: Brief reinforcement of 1-2 key qualifications discussed
- **Paragraph 3**: Express enthusiasm and next steps

**Tone Guidelines:**
- Professional but warm and genuine
- Not overly formal or corporate
- References actual conversation points
- Shows you were listening and engaged
- Concise and respectful of their time

---

## Complete Workflow Example

### Scenario: Post-Interview Analysis

1. **Upload transcript** after phone screen with Stripe
2. **Parse questions** to understand what was tested
3. **Get feedback** on your performance
4. **Generate thank-you** email to send within 24 hours

**Code Example:**
```javascript
// After interview
const transcript = getUserTranscript();
const roleTitle = "Director of Talent Acquisition";
const company = "Stripe";

// Step 1: Parse questions
const parseResult = await parseInterviewTranscript(
  transcript, 
  roleTitle, 
  company,
  window.currentJDAnalysis
);

console.log(`Extracted ${parseResult.questions.length} questions`);
console.log('Themes:', parseResult.themes);

// Step 2: Get performance feedback
const feedback = await getInterviewFeedback(
  transcript,
  roleTitle,
  company,
  parseResult.questions
);

console.log(`Overall score: ${feedback.overall_score}/100`);
console.log('Top recommendation:', feedback.recommendations[0]);

// Step 3: Generate thank-you email
const thankYou = await generateThankYouEmail(
  transcript,
  roleTitle,
  company,
  "Sarah Chen",
  window.currentJDAnalysis
);

console.log('Email subject:', thankYou.subject);
// Copy email body to send
navigator.clipboard.writeText(thankYou.body);
```

---

## Question Bank Building

As you conduct more interviews, you're building a personal question bank:

**Categorization:**
- By role type (Director, VP, IC)
- By function (Recruiting, Engineering, Product)
- By competency (Leadership, Technical, Strategic)
- By difficulty level

**Use Cases:**
- Prepare for upcoming interviews by reviewing similar role questions
- Identify patterns in what companies are testing
- Practice answers to common questions for your function
- Understand difficulty progression across interview rounds

**Future Enhancement:**
Store questions with your performance data to track:
- Which question types you excel at
- Which competencies need more preparation
- Difficulty trends over time

---

## STAR Framework Guidance

For behavioral questions, the system evaluates using STAR:

**S**ituation: Set the context (2-3 sentences)
- Where were you? What was the challenge?

**T**ask: What needed to be done? (1-2 sentences)
- What was your specific responsibility?

**A**ction: What did YOU do? (4-5 sentences - bulk of answer)
- Focus on YOUR actions, not the team's
- Be specific about your approach
- Include any obstacles you overcame

**R**esult: What was the outcome? (2-3 sentences)
- Quantify when possible
- Connect to business impact
- Mention what you learned (optional)

**Total**: Aim for 90-120 seconds

---

## Best Practices

### Before Interview
1. Review question bank for similar roles
2. Prepare STAR stories for key competencies
3. Research company-specific challenges

### During Interview
1. Listen carefully to full question before answering
2. Ask clarifying questions if needed
3. Use STAR structure for behavioral questions
4. Include metrics and specific examples
5. Stay concise (90-120 seconds per answer)

### After Interview
1. Write down questions while fresh (or record with permission)
2. Upload transcript within 24 hours
3. Review feedback and note improvement areas
4. Send thank-you email within 24 hours
5. Log outcome in application tracking

---

## Data Privacy

**Important Notes:**
- Interview transcripts are processed by Claude AI
- No transcripts are stored permanently by default
- Transcripts are only in memory during processing
- Questions extracted can be stored for your question bank
- For production: implement proper data retention policies

**Recommendations:**
- Get permission before recording interviews
- Anonymize interviewer names if desired
- Store transcripts securely
- Delete sensitive data after analysis

---

## Frontend Integration

### Basic Integration
```javascript
// 1. Capture transcript
<textarea id="interview-transcript"></textarea>
<button onclick="analyzeInterview()">Analyze Interview</button>

// 2. Call API
async function analyzeInterview() {
  const transcript = document.getElementById('interview-transcript').value;
  
  const result = await completeInterviewReview(
    transcript,
    window.currentRole,
    window.currentCompany
  );
  
  // Display results
  showFeedback(result.feedback);
  showThankYou(result.thank_you);
}
```

### Advanced Integration
```javascript
// Link to application tracking
async function processPostInterview(applicationId) {
  const app = getApplication(applicationId);
  const transcript = getInterviewTranscript();
  
  const review = await completeInterviewReview(
    transcript,
    app.role_title,
    app.company,
    app.interviewer_name,
    app.jd_analysis
  );
  
  // Store with application
  app.interview_review = review;
  app.stage = 'post-interview';
  
  // Log outcome
  logOutcome(applicationId, 'interview', 
    `Score: ${review.feedback.overall_score}/100`);
  
  // Update UI
  displayInterviewFeedback(review);
}
```

---

## Error Handling

All endpoints return standard HTTP codes:
- `200`: Success
- `400`: Bad request (missing required fields)
- `422`: Validation error
- `500`: Server error (Claude API error)

**Common Issues:**
- Empty transcript → Validation error
- Transcript too short → Warning in parse response
- Claude API timeout → Retry with exponential backoff
- Invalid JSON in response → Server error with details

---

## Cost Considerations

Interview Intelligence uses Claude API:

**Token Usage Estimates:**
- Parse endpoint: ~1500-2500 tokens per interview
- Feedback endpoint: ~2000-3500 tokens per interview
- Thank-you endpoint: ~1000-1500 tokens per email

**At Claude Sonnet 4 pricing** (~$3/million input tokens):
- Parse: ~$0.005-0.008 per interview
- Feedback: ~$0.006-0.011 per interview
- Thank-you: ~$0.003-0.005 per email
- **Complete workflow: ~$0.014-0.024 per interview**

For active job seeker doing 10 interviews/month: ~$0.14-0.24/month

---

## Testing

### Run Test Suite
```bash
python test_interview_intelligence.py
```

### Manual Testing
```bash
# Parse interview
curl -X POST "http://localhost:8000/api/interview/parse" \
  -H "Content-Type: application/json" \
  -d @sample_interview.json

# Get feedback
curl -X POST "http://localhost:8000/api/interview/feedback" \
  -H "Content-Type: application/json" \
  -d @feedback_request.json

# Generate email
curl -X POST "http://localhost:8000/api/interview/thank_you" \
  -H "Content-Type: application/json" \
  -d @thankyou_request.json
```

---

## Future Enhancements

**Planned Features:**
1. **Question Bank Storage**
   - Persistent storage of all questions
   - Search by competency, difficulty, company
   - Practice mode with suggested answers

2. **Performance Tracking**
   - Track scores over time
   - Identify improving/declining areas
   - Competency heat map

3. **Mock Interview Mode**
   - Practice with AI interviewer
   - Real-time feedback
   - Adaptive difficulty

4. **Video Analysis**
   - Upload video interviews
   - Body language feedback
   - Eye contact and posture analysis

5. **Comparative Analytics**
   - Compare your performance to role benchmarks
   - Company-specific question patterns
   - Industry trends

---

## Support

**Documentation:**
- Full API reference: This document
- Frontend integration: `interview_intelligence_stubs.js`
- Test examples: `test_interview_intelligence.py`

**Interactive Testing:**
- Swagger UI: http://localhost:8000/docs
- Try endpoints with sample data
- See real-time request/response

**Questions?**
- Check test script for working examples
- Review frontend stubs for integration patterns
- Examine backend code for prompt details
