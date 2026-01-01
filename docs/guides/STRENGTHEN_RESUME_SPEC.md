# Strengthen Your Resume - Product Specification

## Overview

The Strengthen Your Resume flow provides guided, constrained remediation for resume weaknesses identified during analysis. It enables candidates to provide missing context that strengthens their positioning while preventing fabrication or inflation.

## Flow Position

```
Job Fit Score → Resume Level Analysis → Strengthen My Resume → LinkedIn Profile Analysis → Strategy Overview
```

**Trust Layer Model:**

| Layer | Step | Purpose |
|-------|------|---------|
| 1. Ground Truth | Job Fit Score | High-level reality check. Sets expectations. |
| 1. Ground Truth | Resume Level Analysis | Pure diagnosis. Resume-only. "This is how the market reads what you uploaded." |
| 2. Repair & Agency | Strengthen My Resume | Clarify, de-risk, remove, reframe. Candidate feels in control. |
| 3. Augmentation | LinkedIn Profile Analysis | Optional enrichment. "Want us to cross-check against how recruiters see you online?" |
| 4. Payoff | Strategy Overview | Tailored resume, cover letter, positioning notes. The deliverable. |

**Rationale:** LinkedIn comes before Strategy Overview because:
- Resume analysis earns credibility first (pure diagnosis from what user provided)
- Strengthen step gives user agency before any external data enters
- LinkedIn feels like a bonus/validator, not surveillance
- User explicitly opts into cross-checking, not silent input
- Strategy Overview is the payoff - all inputs are gathered before generating final documents

---

## Part 1: Resume Leveling Page Revisions

### New Section: Credibility & Verifiability

Add to the Resume Leveling page, positioned after the main leveling analysis:

#### Section Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ CREDIBILITY & VERIFIABILITY                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Company Credibility                                             │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Company Name] - [Status: Strong/Weak/Unverifiable]         │ │
│ │ [Explanation of assessment]                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Title Alignment                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Title] at [Company]                                        │ │
│ │ Evidence Level: [Aligned/Inflated/Undersold]                │ │
│ │ [Supporting analysis]                                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Experience Relevance (for career switchers)                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Role/Experience]                                           │ │
│ │ Type: [Direct/Adjacent/Exposure]                            │ │
│ │ [Explanation of transferability]                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Data Sources

Pulls from existing detection systems in `/backend/resume_detection.py`:
- `assess_company_credibility()` → Company Credibility
- `detect_title_inflation()` → Title Alignment
- `recognize_career_switcher()` → Experience Relevance

---

## Part 2: Strengthen Your Resume Flow

### Entry Points

1. **From Resume Leveling Page** - "Strengthen Your Resume" button
2. **From Red Flag Detection** - "Address This Issue" links
3. **From Navigation** - Direct access after leveling is complete

### Core Principle

**Constrained Input, Guided Output**

Users can only provide:
- Missing context that was true but not included
- Clarification of ambiguous statements
- Metrics/numbers they forgot to include

Users cannot:
- Invent new accomplishments
- Inflate titles or responsibilities
- Add skills they don't have
- Fabricate metrics

---

## Strengthen Flow Screens

### Screen 1: Issue Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ STRENGTHEN YOUR RESUME                                          │
│                                                                 │
│ We found [N] areas where your resume could be stronger.         │
│ Let's work through them together.                               │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Priority Issues                                              │ │
│ │                                                              │ │
│ │ 🔴 High Priority (3)                                         │ │
│ │    • Missing impact metrics on 2 key bullets                 │ │
│ │    • Scope unclear for leadership experience                 │ │
│ │                                                              │ │
│ │ 🟡 Medium Priority (2)                                       │ │
│ │    • Vague ownership language                                │ │
│ │    • Technical depth not demonstrated                        │ │
│ │                                                              │ │
│ │ 🟢 Low Priority (1)                                          │ │
│ │    • Minor formatting suggestions                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│                              [Begin Strengthening →]            │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 2: Guided Remediation (Per Issue)

```
┌─────────────────────────────────────────────────────────────────┐
│ ISSUE 1 OF 6                                                    │
│                                                                 │
│ Current Bullet:                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ "Led team to improve customer satisfaction"                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ What's Missing: Quantified outcome                              │
│                                                                 │
│ Help us understand the impact:                                  │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ How large was the team you led?                              │ │
│ │ [___________] people                                         │ │
│ │                                                              │ │
│ │ What was the measurable improvement?                         │ │
│ │ ○ Percentage increase (e.g., 25% improvement)                │ │
│ │ ○ Absolute number (e.g., NPS went from 32 to 67)            │ │
│ │ ○ I don't have specific metrics                              │ │
│ │                                                              │ │
│ │ If you have metrics, enter them:                             │ │
│ │ [___________________________________________]                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Skip This Issue]                    [Generate Stronger Bullet] │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 3: Regeneration Preview

```
┌─────────────────────────────────────────────────────────────────┐
│ STRENGTHENED BULLET                                             │
│                                                                 │
│ Original:                                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ "Led team to improve customer satisfaction"                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Strengthened:                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ "Led 8-person support team that increased NPS from 32 to    │ │
│ │  67, representing a 109% improvement in customer            │ │
│ │  satisfaction scores"                                        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ What changed:                                                   │
│ • Added team size (8 people)                                    │
│ • Added specific metrics (NPS 32→67)                           │
│ • Quantified the improvement (109%)                            │
│                                                                 │
│ [← Try Different Wording]  [Accept & Continue →]                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Allowed vs Forbidden Inputs

### Allowed User Inputs

| Input Type | Example | Validation |
|------------|---------|------------|
| Team/org size | "8 people", "50-person department" | Numeric or range |
| Metrics you have | "25% increase", "$2M revenue" | Numeric with context |
| Time periods | "over 6 months", "Q3 2023" | Temporal reference |
| Scope clarification | "across 3 regions" | Bounded description |
| Tool/technology used | "using Salesforce" | From known tech list or freeform |
| Stakeholder level | "reported to VP" | Title/level reference |

### Forbidden Inputs (with enforcement)

| Forbidden | Why | Enforcement |
|-----------|-----|-------------|
| New accomplishments | Can't verify | Detect "I also..." patterns |
| Title changes | Verifiable on LinkedIn | Compare to uploaded resume |
| Skill additions | Outside remediation scope | Reject new skill claims |
| Company additions | Can't fabricate experience | Block new employer mentions |
| Inflated metrics | Credibility risk | Flag implausible numbers |

### Enforcement Rules

```python
FORBIDDEN_PATTERNS = [
    r"I also (did|led|managed|created)",  # New accomplishments
    r"promoted to|became|was made",        # Title changes
    r"learned|picked up|started using",    # New skills
    r"worked at|joined|started at",        # New companies
]

IMPLAUSIBLE_THRESHOLDS = {
    "revenue_impact_entry_level": 1_000_000,      # $1M+ for entry suspicious
    "team_size_ic": 50,                           # 50+ direct reports for IC suspicious
    "percentage_improvement": 500,                 # 500%+ improvement suspicious
}
```

---

## Regeneration Constraints

### Regeneration Rules

1. **Maximum 3 regenerations per bullet** - Prevents infinite iteration
2. **Each regeneration must use new user input** - Can't just re-roll
3. **Audit trail required** - All versions tracked with inputs

### Audit Trail Schema

```python
@dataclass
class BulletRegeneration:
    original_bullet: str
    issue_type: str              # "missing_metrics", "vague_ownership", etc.
    user_inputs: Dict[str, str]  # What user provided
    generated_bullet: str
    generation_number: int       # 1, 2, or 3
    accepted: bool
    timestamp: datetime

@dataclass
class StrengthenSession:
    session_id: str
    resume_id: str
    issues_found: List[str]
    issues_addressed: List[str]
    issues_skipped: List[str]
    regenerations: List[BulletRegeneration]
    started_at: datetime
    completed_at: Optional[datetime]
```

---

## Red Flag Language Guidelines

### Current (Accusatory) → Revised (Neutral)

| Current | Revised |
|---------|---------|
| "This claim appears inflated" | "We couldn't find supporting evidence for this scope" |
| "Suspicious metric" | "This metric is unusually high - can you provide context?" |
| "Title doesn't match experience" | "The responsibilities described suggest a different level" |
| "Unverifiable company" | "We couldn't find information about this company" |
| "Fabricated accomplishment" | NEVER USE - redirect to clarifying questions |

### Tone Principles

1. **Assume good faith** - User may have forgotten details, not fabricated
2. **Offer opportunity to clarify** - "Can you help us understand..."
3. **Focus on evidence gaps** - "We're missing..." not "You're lying..."
4. **Suggest remediation** - Every flag should have a path forward

---

## API Endpoints

### New Endpoints Required

```
POST /api/strengthen/session
  - Creates a new strengthen session
  - Returns: session_id, issues_list, priority_order

GET /api/strengthen/session/{session_id}
  - Gets current session state
  - Returns: issues, progress, regenerations

POST /api/strengthen/regenerate
  - Generates strengthened bullet
  - Body: { session_id, issue_id, user_inputs }
  - Returns: { original, strengthened, changes, generation_number }

POST /api/strengthen/accept
  - Accepts a regenerated bullet
  - Body: { session_id, issue_id, regeneration_id }

POST /api/strengthen/skip
  - Skips an issue
  - Body: { session_id, issue_id, reason? }

POST /api/strengthen/complete
  - Marks session complete
  - Returns: { summary, before_after_comparison }
```

### Endpoint Validation

All `/api/strengthen/*` endpoints must:
1. Validate user inputs against forbidden patterns
2. Check regeneration count < 3
3. Verify session ownership
4. Log all actions for audit trail

---

## Frontend Components

### New Pages/Components

1. **StrengthenSummary** - Issue overview with priorities
2. **StrengthenIssue** - Single issue remediation flow
3. **StrengthenPreview** - Before/after comparison
4. **StrengthenComplete** - Session summary

### Integration Points

1. **Resume Leveling Page**
   - Add "Credibility & Verifiability" section
   - Add "Strengthen Your Resume" CTA button

2. **Navigation**
   - Add Strengthen to main nav after Leveling
   - Show progress indicator

3. **Strategy Overview**
   - Show strengthening summary
   - Display before/after improvements

---

## Success Metrics

1. **Completion Rate** - % of users who complete strengthen flow
2. **Issue Resolution Rate** - % of issues addressed (not skipped)
3. **Regeneration Quality** - User acceptance rate on first generation
4. **Level Improvement** - Score delta before/after strengthening

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Add Credibility & Verifiability section to Leveling page
- [ ] Create strengthen session API endpoints
- [ ] Build audit trail infrastructure

### Phase 2: Core Flow
- [ ] Implement issue summary screen
- [ ] Build guided remediation UI
- [ ] Create regeneration preview component

### Phase 3: Constraints & Validation
- [ ] Implement forbidden input detection
- [ ] Add implausible metric flagging
- [ ] Enforce 3-regeneration limit

### Phase 4: Polish
- [ ] Revise red flag language across codebase
- [ ] Add progress persistence
- [ ] Build completion summary

---

## Appendix: Detection Integration

The Credibility & Verifiability section pulls from:

```python
from resume_detection import (
    assess_company_credibility,  # → Company Credibility cards
    detect_title_inflation,      # → Title Alignment cards
    recognize_career_switcher,   # → Experience Relevance cards
)
```

These functions are already implemented in `/backend/resume_detection.py`.
