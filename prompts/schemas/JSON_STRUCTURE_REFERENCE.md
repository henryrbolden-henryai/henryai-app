# JSON Structure Reference - Backend Response Formats

## Document Generation Response (`/api/documents/generate`)

```json
{
  "resume": {
    "summary": "3-4 line professional summary tailored to JD",
    "skills": ["array", "of", "skills", "reordered", "by", "relevance"],
    "experience": [
      {
        "company": "Exact Company Name",
        "title": "Exact Job Title",
        "dates": "Jan 2020 - Present",
        "bullets": [
          "Rewritten bullet using JD keywords",
          "Another tailored accomplishment"
        ]
      }
    ]
  },
  "cover_letter": {
    "greeting": "Dear Hiring Manager,",
    "opening": "Strong opening paragraph connecting to role",
    "body": "2-3 paragraphs demonstrating fit",
    "closing": "Confident closing with call to action",
    "full_text": "Complete cover letter as single string"
  },
  "changes_summary": {
    "resume": {
      "summary_rationale": "Rewrote to emphasize cross-functional leadership and growth-stage execution because that's what they're prioritizing in this role",
      "qualifications_rationale": "Pulled forward your Spotify roadmap work and Uber metrics execution. Buried the National Grid utility background since it doesn't map to what they need",
      "ats_keywords": [
        "product market fit",
        "stakeholder alignment",
        "agile development",
        "data driven decision making",
        "user centric design"
      ],
      "positioning_statement": "This positions you as someone who can scale consumer products in high-growth environments, not just manage features"
    },
    "cover_letter": {
      "opening_rationale": "Led with your track record scaling consumer products at Spotify and Uber because that's the competency gap they're trying to fill",
      "body_rationale": "Emphasized cross-functional execution, data-driven decision making, and launching under tight timelines. Avoided utility sector work since it dilutes the narrative",
      "close_rationale": "Confident but not pushy. Signals interest without desperation",
      "positioning_statement": "This frames you as the senior PM who can step in and own product strategy from day one"
    }
  }
}
```

---

## JD Analysis Response (`/api/jd/analyze`)

```json
{
  "intelligence_layer": {
    "job_quality_score": "Apply|Apply with caution|Skip — poor quality or low close rate",
    "quality_explanation": "3-5 substantive sentences explaining the rating",
    "strategic_positioning": {
      "lead_with_strengths": [
        "Specific strength 1",
        "Specific strength 2",
        "Specific strength 3"
      ],
      "gaps_and_mitigation": [
        "Gap 1 with mitigation strategy",
        "Gap 2 with mitigation strategy"
      ],
      "emphasis_points": [
        "What to emphasize 1",
        "What to emphasize 2"
      ],
      "avoid_points": [
        "What to avoid or de-emphasize 1",
        "What to avoid or de-emphasize 2"
      ],
      "positioning_strategy": "1-2 sentence overall strategy"
    },
    "salary_market_context": {
      "typical_range": "$150K-$200K for Director level in SF",
      "posted_comp_assessment": "not mentioned|low|fair|strong",
      "recommended_expectations": "Target $180K-$200K base given experience",
      "market_competitiveness": "2-3 sentences on supply/demand",
      "risk_indicators": ["specific risk 1", "specific risk 2"] or []
    },
    "apply_decision": {
      "recommendation": "Apply|Apply with caution|Skip",
      "reasoning": "1-2 substantive sentences",
      "timing_guidance": "Specific guidance on when to apply"
    }
  },
  "company": "Company Name",
  "role_title": "Job Title",
  "company_context": "2-3 sentences about company, industry, stage",
  "role_overview": "2-3 sentences about role purpose and impact",
  "key_responsibilities": [
    "Responsibility 1",
    "Responsibility 2",
    "Responsibility 3",
    "Responsibility 4"
  ],
  "required_skills": [
    "Required skill 1",
    "Required skill 2",
    "Required skill 3"
  ],
  "preferred_skills": ["Nice-to-have 1", "Nice-to-have 2"] or [],
  "ats_keywords": [
    "keyword1",
    "keyword2",
    "keyword3",
    "... 10-15 total"
  ],
  "fit_score": 85,
  "strengths": [
    "Candidate strength 1",
    "Candidate strength 2",
    "Candidate strength 3"
  ],
  "gaps": [
    "Gap or concern 1",
    "Gap or concern 2"
  ],
  "strategic_positioning": "2-3 sentences on positioning strategy",
  "salary_info": "Exact text from JD or null",
  "interview_prep": {
    "narrative": "3-4 sentence story tailored to this role for framing alignment. Explains how candidate's background connects to role requirements and addresses any gaps proactively.",
    "talking_points": [
      "Key talking point 1 for recruiter screen",
      "Key talking point 2 highlighting relevant experience",
      "Key talking point 3 demonstrating impact",
      "Key talking point 4 showing cultural fit"
    ],
    "gap_mitigation": [
      "Concern 1 + specific mitigation strategy to address it",
      "Concern 2 + how to reframe it positively",
      "Concern 3 + pivot strategy if asked about it"
    ]
  },
  "outreach": {
    "hiring_manager": "Hi [Name], I just applied for the [Role] role on your team. Based on my experience in [X], I'd love to briefly connect and share how I can help you hit [team/company goal]. Would you be open to a 15-minute call this week?",
    "recruiter": "Hi [Name], I've just submitted my application for the [Role] role. I lead [type of teams/work], and I'd appreciate any insight into the process and what you're prioritizing in candidates. Are you available for a quick call?",
    "linkedin_help_text": "Start by searching LinkedIn for: [Company] + 'talent acquisition' OR 'recruiting' + 'director' OR 'head'. For the hiring manager, search: [Company] + [department] + 'director' OR 'VP'. Look for profiles mentioning this team or function. Check recent company posts to identify who's involved in this hire."
  }
}
```

---

## Frontend Display Mapping

### Changes Summary Section

| Frontend Element ID | Backend Path | Display Format |
|---------------------|--------------|----------------|
| `summary-rationale` | `changes_summary.resume.summary_rationale` | Text paragraph |
| `qualifications-rationale` | `changes_summary.resume.qualifications_rationale` | Text paragraph |
| `ats-keywords-list` | `changes_summary.resume.ats_keywords` | Comma-separated list |
| `resume-positioning-statement` | `changes_summary.resume.positioning_statement` | Highlighted text |
| `opening-rationale` | `changes_summary.cover_letter.opening_rationale` | Text paragraph |
| `body-rationale` | `changes_summary.cover_letter.body_rationale` | Text paragraph |
| `close-rationale` | `changes_summary.cover_letter.close_rationale` | Text paragraph |
| `cover-letter-positioning-statement` | `changes_summary.cover_letter.positioning_statement` | Highlighted text |

### Interview Prep Section

| Frontend Element ID | Backend Path | Display Format |
|---------------------|--------------|----------------|
| `interview-narrative` | `interview_prep.narrative` | Text paragraph |
| `interview-talking-points` | `interview_prep.talking_points` | Bulleted list |
| `interview-gap-mitigation` | `interview_prep.gap_mitigation` | Bulleted list |

### Outreach Section

| Frontend Element ID | Backend Path | Display Format |
|---------------------|--------------|----------------|
| `hiring-manager-message` | `outreach.hiring_manager` | Textarea (readonly) |
| `recruiter-message` | `outreach.recruiter` | Textarea (readonly) |
| `linkedin-help-message` | `outreach.linkedin_help_text` | Text paragraph |

---

## Validation Rules

### All Rationale Fields:
- ✅ Must be 1-2 sentences minimum
- ✅ Must reference specific content from candidate's actual resume
- ✅ Must be concrete, not generic
- ❌ Cannot be undefined, null, or empty string
- ❌ Cannot use placeholders like "TBD" or "N/A"

### ATS Keywords:
- ✅ Must have 5-7 keywords minimum
- ✅ Must come directly from job description
- ✅ Should be relevant to role requirements
- ❌ Cannot be generic terms like "teamwork" or "communication"

### Positioning Statements:
- ✅ Must be complete sentence
- ✅ Must start with "This positions you as..." or similar
- ✅ Must articulate strategic framing clearly
- ❌ Cannot be vague or generic

### Interview Prep:
- ✅ Narrative: 3-4 sentences minimum
- ✅ Talking points: 4-6 bullets
- ✅ Gap mitigation: 2-3 bullets with strategies
- ❌ No field can be empty

### Outreach:
- ✅ Hiring manager: 3-5 sentences, warm tone
- ✅ Recruiter: 3-5 sentences, professional tone
- ✅ LinkedIn help: Step-by-step instructions
- ❌ No placeholder names like [Name] without context

---

## Error Handling

### Backend:
```python
if not changes_summary.get('resume', {}).get('summary_rationale'):
    raise ValueError("Missing required field: changes_summary.resume.summary_rationale")
```

### Frontend:
```javascript
const summaryRationale = resumeChanges.summary_rationale || "No rationale provided.";
```

All frontend fields have fallback messages to prevent display issues even if backend returns incomplete data.
