# HenryAI — 3-Screen MVP (Frontend Only)

A radically simplified job search frontend that works with your existing backend. Upload resume + paste JD → get fit analysis → download tailored application package.

## Changes from Previous Version

1. **Restored full "Meet Henry" marketing content** - About, How we work, What makes this different, Core capabilities
2. **Fixed endpoint calls** - Now uses your existing `/api/jd/analyze` and `/api/documents/generate`
3. **Kept the clean 3-screen flow** - Analyzer card lives below the marketing sections

## The Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  LANDING PAGE (index.html)                                      │
│                                                                 │
│  "Meet Henry" hero + marketing sections                         │
│  - About Henry                                                  │
│  - How we work together                                         │
│  - What makes this different                                    │
│  - Core capabilities                                            │
│                                                                 │
│  ↓ Scroll to "Let's get started" ↓                              │
│                                                                 │
│  ANALYZER CARD: "Should you apply to this role?"                │
│  [Resume]  [Company]  [Role]  [Job Description]                 │
│  [Analyze This Role] ──────────────────────────────────────────>│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCREEN 2: THE ANSWER (results.html)                            │
│                                                                 │
│  72% fit for this role                                          │
│  ✓ Strengths   ✗ Gaps                                           │
│  [Apply / Apply with Caution / Skip]                            │
│                                                                 │
│  [Get My Application Package]  [Skip]                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCREEN 3: THE PACKAGE (package.html)                           │
│                                                                 │
│  ✓ Resume  ✓ Cover Letter  ✓ Talking Points                     │
│  What I Changed & Why                                           │
│  Interview Talking Points                                       │
│                                                                 │
│  [Download All]  [Email This to Me]                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Your Backend (No Changes Needed)

This frontend uses your existing endpoints:
- `POST /api/jd/analyze`
- `POST /api/documents/generate`

### 2. Run the Backend

```bash
export ANTHROPIC_API_KEY="your-key-here"
uvicorn backend:app --reload --port 8000
```

### 3. Serve the Frontend

```bash
python -m http.server 8080
```

### 4. Open in Browser

http://localhost:8080

## API Integration Details

### Screen 1 → Screen 2

Calls `POST /api/jd/analyze` with:
```json
{
  "company": "Acme Corp",
  "role_title": "Senior PM",
  "job_description": "...",
  "resume": { "resume_text": "...", "full_name": "Candidate" }
}
```

Uses response fields:
- `fit_score` for the big percentage
- `strengths` and `gaps` arrays
- `intelligence_layer.apply_decision.recommendation` for Apply/Caution/Skip
- `intelligence_layer.quality_explanation` for reasoning

### Screen 3 Download

Calls `POST /api/documents/generate` with:
```json
{
  "resume": { "resume_text": "..." },
  "jd_analysis": { ...from previous step... }
}
```

Uses response fields:
- `resume_output.full_text` for resume
- `cover_letter.full_text` for cover letter
- `interview_prep.talking_points` for interview prep
- `changes_summary` for "What I Changed & Why"

## Files

```
├── index.html      # Full landing + analyzer card
├── results.html    # Fit score & recommendation
├── package.html    # Download package
└── README.md       # This file
```

## What's Preserved

- Full "About Henry" section
- "How we work together" steps
- "What makes working with Henry different" differentiators
- "Core capabilities" features
- All existing backend logic

## What's New

- Clean analyzer card at bottom of landing page
- 3-screen linear flow
- Uses existing backend endpoints (not custom MVP endpoints)
- Graceful handling of `intelligence_layer` response shape

---

Built by Henry
