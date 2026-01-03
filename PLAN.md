# Strengthen Your Resume - Implementation Plan

## Overview

This plan implements the new "Strengthen Your Resume" module that:
1. Audits resume bullets flagged in Resume Leveling Analysis
2. Asks targeted clarification questions to unlock real experience
3. Produces verified enhancements for document generation
4. Enforces zero-fabrication before any documents are generated

## Corrected Flow

```
JD Submission + Job Fit Score
→ Resume Leveling Analysis
→ Strengthen Your Resume (NEW)
→ LinkedIn Analysis (conditional: if profile uploaded, analyze; if not, prompt upload)
→ Application Strategy Overview
→ Document Generation
```

---

## Phase 1: Extend Leveling Prompt for Bullet Audit

### Task 1.1: Update `backend/prompts/leveling.py`

**File:** `backend/prompts/leveling.py`

Add `bullet_audit` to the output schema. This array contains every resume bullet with a verification tag.

**New output fields to add:**

```python
"bullet_audit": [
  {
    "id": "exp-{job_index}-bullet-{bullet_index}",
    "text": "The actual bullet text",
    "section": "Experience - Company Name, Role Title",
    "tag": "VERIFIED | VAGUE | RISKY | IMPLAUSIBLE",
    "issues": ["List of specific issues if not VERIFIED"],
    "clarifies": "ownership | scope | outcome" // What type of clarification needed
  }
]
```

**Tag mapping logic (add to prompt instructions):**

| Condition | Tag |
|-----------|-----|
| Bullet has quantified outcomes, clear ownership, no flags | VERIFIED |
| Bullet lacks metrics, ownership unclear, or generic language | VAGUE |
| Scope seems inflated for role/tenure, title/evidence mismatch | RISKY |
| IC claiming executive scope, implausible metrics, credibility contradiction | IMPLAUSIBLE |

**Location in prompt:** After the existing `red_flags_enhanced` section, add instructions for `bullet_audit` generation.

---

### Task 1.2: Update Leveling API Response

**File:** `backend/backend.py`

Ensure the `/api/resume/level` endpoint returns the new `bullet_audit` field in its response.

No new endpoint needed - just ensure the Claude response parsing includes this field.

---

## Phase 2: Create Strengthen Prompts

### Task 2.1: Create `backend/prompts/strengthen.py`

**New file with three prompts:**

#### `STRENGTHEN_QUESTIONS_PROMPT`

```python
STRENGTHEN_QUESTIONS_PROMPT = """
Generate ONE clarifying question for each flagged resume bullet.

RULES:
1. ONE question per bullet - no sub-questions
2. Question must clarify OWNERSHIP, SCOPE, or OUTCOME
3. Do NOT suggest answers or provide examples
4. Do NOT assume they have more experience than stated
5. Frame as genuine inquiry, not interrogation
6. Accept "I didn't own that" as a valid answer
7. Keep questions under 25 words

FLAGGED BULLETS:
{flagged_bullets}

CANDIDATE CONTEXT:
{resume_context}

Return JSON:
{
  "questions": [
    {
      "bullet_id": "<id>",
      "original_bullet": "<text>",
      "tag": "<VAGUE|RISKY|IMPLAUSIBLE>",
      "question": "<single clarifying question>",
      "clarifies": "ownership | scope | outcome"
    }
  ]
}
"""
```

#### `STRENGTHEN_APPLY_PROMPT`

```python
STRENGTHEN_APPLY_PROMPT = """
Update resume bullets based on candidate's clarifying answers.

CRITICAL RULES:
1. ONLY use information the candidate explicitly provided
2. If they narrowed scope, reflect the ACTUAL scope (not inflated)
3. If they provided metrics, use their EXACT numbers
4. If they said "I didn't own that" → downgrade or remove claim
5. Do NOT invent details they didn't mention
6. Do NOT add qualifiers like "approximately" unless they said it
7. Enhanced bullet should be MORE credible, not more impressive

ORIGINAL BULLETS AND ANSWERS:
{answers}

Return JSON:
{
  "enhancements": [
    {
      "bullet_id": "<id>",
      "original_bullet": "<text>",
      "enhanced_bullet": "<rewritten bullet using only provided info>",
      "confidence": "HIGH | MEDIUM",
      "changes_made": "<brief explanation of what changed>"
    }
  ],
  "declined": [
    {
      "bullet_id": "<id>",
      "reason": "Candidate confirmed they did not own this"
    }
  ]
}
"""
```

---

## Phase 3: Refactor Backend Infrastructure

### Task 3.1: Update `backend/strengthen_session.py`

**Changes:**
1. Replace `IssueType` enum with new tag system
2. Update `StrengthenIssue` dataclass to use tags
3. Keep session management, validation, audit trail logic
4. Keep forbidden pattern detection (valuable for catching fabrication)

**New tag enum:**

```python
class BulletTag(str, Enum):
    VERIFIED = "verified"
    VAGUE = "vague"
    RISKY = "risky"
    IMPLAUSIBLE = "implausible"

class ClarificationType(str, Enum):
    OWNERSHIP = "ownership"
    SCOPE = "scope"
    OUTCOME = "outcome"
```

**Update `StrengthenIssue`:**

```python
@dataclass
class StrengthenIssue:
    issue_id: str
    bullet_id: str
    tag: BulletTag
    original_bullet: str
    section: str  # e.g., "Experience - Acme Corp, PM"
    issues: List[str]
    clarifies: ClarificationType
    question: Optional[str] = None
    answer: Optional[str] = None
    enhanced_bullet: Optional[str] = None
    confidence: Optional[str] = None
    addressed: bool = False
    skipped: bool = False
    declined: bool = False
```

---

### Task 3.2: Add New API Endpoints

**File:** `backend/backend.py`

#### `POST /api/strengthen/questions`

**Request:**
```json
{
  "flagged_bullets": [...],
  "resume_context": {...}
}
```

**Response:**
```json
{
  "questions": [...]
}
```

#### `POST /api/strengthen/apply`

**Request:**
```json
{
  "answers": [
    {
      "bullet_id": "exp-1-bullet-2",
      "original_bullet": "...",
      "answer": "...",
      "tag": "RISKY"
    }
  ],
  "resume_data": {...}
}
```

**Response:**
```json
{
  "enhancements": [...],
  "declined": [],
  "unresolved": []
}
```

---

### Task 3.3: Create Pydantic Models

**File:** `backend/models/strengthen.py` (new file)

```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class BulletTag(str, Enum):
    VERIFIED = "verified"
    VAGUE = "vague"
    RISKY = "risky"
    IMPLAUSIBLE = "implausible"

class ClarificationType(str, Enum):
    OWNERSHIP = "ownership"
    SCOPE = "scope"
    OUTCOME = "outcome"

class FlaggedBullet(BaseModel):
    id: str
    text: str
    tag: BulletTag
    issues: List[str]
    section: str

class StrengthenQuestionsRequest(BaseModel):
    flagged_bullets: List[FlaggedBullet]
    resume_context: dict

class StrengthenQuestion(BaseModel):
    bullet_id: str
    original_bullet: str
    tag: BulletTag
    question: str
    clarifies: ClarificationType

class StrengthenQuestionsResponse(BaseModel):
    questions: List[StrengthenQuestion]

class BulletAnswer(BaseModel):
    bullet_id: str
    original_bullet: str
    answer: str
    tag: BulletTag

class StrengthenApplyRequest(BaseModel):
    answers: List[BulletAnswer]
    resume_data: dict

class Enhancement(BaseModel):
    bullet_id: str
    original_bullet: str
    enhanced_bullet: str
    confidence: str
    changes_made: str

class DeclinedBullet(BaseModel):
    bullet_id: str
    reason: str

class StrengthenApplyResponse(BaseModel):
    enhancements: List[Enhancement]
    declined: List[DeclinedBullet]
    unresolved: List[dict]
```

---

## Phase 4: Replace Frontend

### Task 4.1: Archive Old `strengthen.html`

Move current `frontend/strengthen.html` to `frontend/_archive/strengthen.html.old`

---

### Task 4.2: Create New `frontend/strengthen.html`

Complete replacement with new UI per spec:

**Key sections:**
1. Progress indicator (Question X of Y)
2. Question card showing:
   - Tag badge (RISKY, VAGUE, IMPLAUSIBLE)
   - Original bullet text
   - Bullet source (role/company)
   - Clarifying question
   - Answer textarea
   - Skip button
3. Results summary (after all questions)
4. Skip all option

**SessionStorage:**
- Reads from: `analysisData`, `levelingData`
- Writes to: `strengthenedData`

**Navigation:**
- Back: `resume-leveling.html`
- Next: `linkedin-upload.html` OR `linkedin-analysis.html` (conditional)

---

### Task 4.3: Create `frontend/components/strengthen-flow.js`

JavaScript module handling:
- Loading flagged bullets from levelingData
- Fetching questions from `/api/strengthen/questions`
- Collecting answers
- Submitting to `/api/strengthen/apply`
- Storing results to sessionStorage
- Navigation logic

---

## Phase 5: LinkedIn Placeholder Pages

### Task 5.1: Create `frontend/linkedin-upload.html`

Simple upload prompt:
- "Want to optimize your LinkedIn profile for this role?"
- Upload button for LinkedIn PDF export
- "Skip - Continue to Strategy Overview" option
- On upload success: navigate to `linkedin-analysis.html`
- On skip: navigate to `overview.html` (strategy)

---

### Task 5.2: Create `frontend/linkedin-analysis.html`

Placeholder page:
- If `linkedinData` exists in sessionStorage: show basic display or "Analysis coming soon"
- Continue button to `overview.html`

**Note:** Can reuse/rename existing `linkedin-scoring.html` if appropriate.

---

## Phase 6: Update Navigation

### Task 6.1: Update `resume-leveling.html`

**Change CTA behavior:**
- Current: Goes to `strengthen.html` (old flow)
- New: Still goes to `strengthen.html` (new flow)
- No change needed here, but verify it passes correct data

**Ensure levelingData includes `bullet_audit`:**
- Store full leveling response in sessionStorage

---

### Task 6.2: Update Navigation Chain

| From | To | Condition |
|------|-----|-----------|
| `resume-leveling.html` | `strengthen.html` | Always |
| `strengthen.html` | `linkedin-upload.html` | No `linkedinData` |
| `strengthen.html` | `linkedin-analysis.html` | Has `linkedinData` |
| `linkedin-upload.html` | `linkedin-analysis.html` | After upload |
| `linkedin-upload.html` | `overview.html` | Skip |
| `linkedin-analysis.html` | `overview.html` | Continue |
| `overview.html` | `documents.html` | Generate |

---

## Phase 7: Auth & Error Handling

### Task 7.1: Add Auth Check to New Pages

All new pages should include:

```javascript
// Check auth on page load
const { data: { user } } = await supabase.auth.getUser();
if (!user) {
    window.location.href = 'login.html';
    return;
}
```

---

### Task 7.2: Add Error States

**API failures:**
- Show: "Something went wrong. Try again or skip."
- Allow retry or skip

**Empty state (no flags):**
- Auto-skip with message: "Your resume is already strong. Proceeding to LinkedIn analysis."

**Missing data:**
- Redirect to appropriate earlier step

---

## Phase 8: Testing

### Task 8.1: Manual Testing Checklist

- [ ] Leveling API returns `bullet_audit` array
- [ ] Flagged bullets load correctly from levelingData
- [ ] Questions generate without example answers
- [ ] Blank answers marked as UNVERIFIED
- [ ] "No" answers downgrade or remove claims
- [ ] Enhanced bullets use ONLY candidate-provided info
- [ ] Skip option works and logs reason
- [ ] `strengthenedData` persists to sessionStorage
- [ ] Navigation to LinkedIn conditional on profile upload
- [ ] Document generation respects declined_items

---

### Task 8.2: Integration Test

Full flow test:
1. Submit JD → Get fit score
2. View resume leveling → See bullet_audit
3. Enter strengthen flow → Answer questions
4. Skip/answer various combinations
5. Verify strengthenedData stored correctly
6. Navigate to LinkedIn → Upload or skip
7. View strategy overview → See strengthened data
8. Generate documents → Verify enhancements applied

---

## Implementation Order

```
1. [x] backend/prompts/leveling.py      - Add bullet_audit to output
2. [x] backend/prompts/strengthen.py    - Create new file with prompts
3. [x] backend/models/strengthen.py     - Create Pydantic models
4. [x] backend/strengthen_session.py    - Refactor to new tag system
5. [x] backend/backend.py               - Add new API endpoints
6. [x] frontend/strengthen.html         - Replace with new UI
7. [x] frontend/components/strengthen-flow.js - Create JS module
8. [x] frontend/linkedin-upload.html    - Create placeholder
9. [x] frontend/linkedin-analysis.html  - Create placeholder
10. [x] Update navigation in affected pages
11. [x] Auth checks (built into pages)
12. [x] Error handling (built into strengthen-flow.js)
13. [ ] Test full flow
14. [ ] Merge to main
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `backend/prompts/strengthen.py` | Question and apply prompts |
| `backend/models/strengthen.py` | Pydantic request/response models |
| `frontend/strengthen.html` | New strengthen UI (replaces old) |
| `frontend/components/strengthen-flow.js` | JS logic for strengthen flow |
| `frontend/linkedin-upload.html` | LinkedIn upload prompt |
| `frontend/linkedin-analysis.html` | LinkedIn analysis placeholder |

## Files to Modify

| File | Change |
|------|--------|
| `backend/prompts/leveling.py` | Add `bullet_audit` to output schema |
| `backend/strengthen_session.py` | Refactor to new tag system |
| `backend/backend.py` | Add new endpoints, update leveling response |
| `frontend/resume-leveling.html` | Ensure levelingData includes bullet_audit |

## Files to Archive

| File | Destination |
|------|-------------|
| `frontend/strengthen.html` | `frontend/_archive/strengthen.html.old` |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Completion rate (vs. skip) | 70%+ |
| Questions answered per session | 3-5 average |
| Enhancements accepted | 80%+ |
| User edits to enhancements | <20% |
| Time to complete | 2-4 minutes |

---

## Post-Implementation

After merging to main:
1. Monitor error rates on new endpoints
2. Track completion vs skip rates
3. Review enhancement quality samples
4. Gather user feedback on question clarity
