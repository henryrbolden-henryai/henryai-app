# HenryAI Implementation Guide

**Date**: December 19, 2025
**Version**: 1.9
**Audience**: Development Team
**Last Updated**: January 5, 2026
**Total Features**: 56 implemented, 85 API endpoints

---

## Table of Contents

1. [Recently Implemented Features](#recently-implemented-features)
2. [Code Architecture Overview](#code-architecture-overview)
3. [Implementation Details: Completed Features](#implementation-details-completed-features)
4. [Next Steps: Streaming & UI Enhancements](#next-steps-streaming--ui-enhancements)
5. [API Reference](#api-reference)
6. [Testing & Quality Assurance](#testing--quality-assurance)
7. [Deployment Guide](#deployment-guide)

---

## Recently Implemented Features

### Summary of December 2025 Improvements

All features below have been implemented and deployed to production:

1. ✅ **Post-Generation Validation Layer** (Dec 11)
2. ✅ **ATS Keyword Coverage Verification** (Dec 11)
3. ✅ **Conversational Wrappers for Structured Outputs** (Dec 11)
4. ✅ **Enhanced System Prompts with Grounding Rules** (Dec 11)
5. ✅ **Streaming Support Infrastructure** (backend function added)
6. ✅ **Resume Level Analysis Feature** (Dec 11)
7. ✅ **UI/UX Improvements** (Dec 11)
8. ✅ **Beta Access Gate** (Dec 12)
9. ✅ **Dashboard & Tracker Improvements** (Dec 12)
10. ✅ **Ask Henry Chatbot Enhancements** (Dec 12)
11. ✅ **HenryHQ.ai Landing Page** (Dec 12)
12. ✅ **New User Signup Flow** (Dec 13)
13. ✅ **API Error Resilience** (Dec 14)
14. ✅ **Status Banner Component** (Dec 14)
15. ✅ **Dashboard UI Refinements** (Dec 14)
16. ✅ **Profile Management Enhancements** (Dec 14)
17. ✅ **Supabase Database Integration** (Dec 14)
18. ✅ **QA Validation Updates** (Dec 14) - blocking disabled
19. ✅ **Async/Await Syntax Fix** (Dec 14) - documents.html
20. ✅ **LinkedIn Profile Integration** (Dec 15) - upload, parse, align, optimize
21. ✅ **4-Tier Recommendation System** (Dec 16) - Strongly Apply, Apply, Conditional Apply, Do Not Apply
22. ✅ **Experience Penalty Hard Caps** (Dec 16) - backend safety net
23. ✅ **Company Credibility Scoring** (Dec 16) - multipliers for experience calculation
24. ✅ **Reality Check Improvements** (Dec 16) - candidate name personalization
25. ✅ **Candidate Identity Bug Fix** (Dec 16) - fixed "Henry" appearing in outputs
26. ✅ **JSON Repair & Error Handling** (Dec 16) - enhanced robustness
27. ✅ **Streaming Analysis Endpoint** (Dec 16) - experimental, reverted
28. ✅ **LEPE Integration** (Dec 17-18) - leadership experience pattern extraction
29. ✅ **Capability Evidence Check (CEC) System** (Dec 18-19) - recruiter-grade diagnostics
30. ✅ **Final Recommendation Controller** (Dec 19) - Single Source of Truth for decisions
31. ✅ **SYSTEM CONTRACT Block** (Dec 19) - 10-section non-negotiable constraints
32. ✅ **JD-Scoped Signal Extraction** (Dec 19) - prevents cross-candidate contamination
33. ✅ **Candidate Evidence Validation** (Dec 19) - resume-first grounding
34. ✅ **Your Move Coaching Overhaul** (Dec 19) - context-aware, decisive guidance
35. ✅ **UI Contract Enforcement** (Dec 19) - gaps/Your Move consistency
36. ✅ **Strengths Extraction Recovery** (Dec 19) - contract-compliant failure handling
37. ✅ **Proceed Anyway Navigation Fix** (Dec 23) - fixed freeze on Do Not Apply acknowledgment
38. ✅ **Domain Gap Priority Fix** (Dec 23) - domain mismatch now takes priority over years checks
39. ✅ **Ask Henry UI Improvements** (Dec 23) - larger input box, smaller send button, timestamps
40. ✅ **Ask Henry Auto-Expand** (Dec 23) - drawer expands for long responses (>400 chars)
41. ✅ **Hey Henry Crash Fix** (Dec 23) - handle dict format for gaps/strengths
42. ✅ **Your Move Redirect Fix** (Dec 23) - gaps now include redirect field for coaching controller
43. ✅ **Interview Debrief Intelligence** (Dec 25) - structured extraction, pattern analysis
44. ✅ **Story Bank UI** (Dec 25) - behavioral example management with effectiveness tracking
45. ✅ **Hey Henry Strategic Intelligence Engine** (Dec 25) - Phase 2.1-2.8 complete
46. ✅ **Canonical Document System** (Jan 1) - single source of truth for preview/download
47. ✅ **Strengthen Your Resume Flow** (Jan 1) - constrained remediation with forbidden input validation
48. ✅ **Fit Score Delta Display** (Jan 1) - before/after comparison locked at download
49. ✅ **Credibility & Verifiability Section** (Jan 1) - company, title, experience relevance cards
50. ✅ **Resume Language Lint** (Jan 1) - 4-tier pattern detection for weak language
51. ✅ **Resume Quality Gates** (Jan 1) - pre-download validation
52. ✅ **Non-Accusatory Red Flags** (Jan 1) - neutral, constructive messaging
53. ✅ **Name Mismatch Detection** (Jan 5) - signup vs resume name comparison
54. ✅ **Hey Henry Name Mismatch Alerts** (Jan 5) - proactive fraud/error messaging

---

### Name Mismatch Detection (Jan 5, 2026)

**Overview:** Detects discrepancies between the name provided at signup and the name on the uploaded resume to identify potential fraud or data entry errors.

**Components:**

1. **`checkNameMismatch()` in supabase-client.js**
   - Compares signup first/last name against resume name
   - Normalizes names (removes punctuation, extra spaces)
   - Classifies as 'major' (first name different) or 'minor' (last name different)
   - Stores mismatch data in localStorage for Hey Henry
   - Updates `name_match_status` column in candidate_profiles

2. **Hey Henry Greeting Integration**
   - Checks `henryai_name_mismatch` in localStorage
   - Major mismatch: "I noticed your resume shows [X] but you signed up as [Y]..."
   - Minor mismatch: "Quick heads up—your resume shows [X] but your account has [Y]..."
   - Acknowledgment tracking prevents repeated alerts (`henryai_name_mismatch_ack`)

3. **Database Schema**
   - `name_match_status` column: 'matched' | 'minor_mismatch' | 'major_mismatch'
   - Stored in `candidate_profiles` table for admin review

**Files Modified:**
- `frontend/js/supabase-client.js` - Added `checkNameMismatch()` function
- `frontend/components/hey-henry.js` - Added mismatch detection in greeting + acknowledgment handling
- `backend/migrations/add_candidate_profile_fields_v2.sql` - Added `name_match_status` column

**Future Enhancements (Phase 3):**
- Admin dashboard for reviewing flagged accounts
- Fuzzy matching for common name variations (Bob/Robert, etc.)
- Pattern detection across multiple resume uploads
- Third-party identity verification integration (Persona, Jumio)

---

### Phase 2.5: Document Quality & Trust Layer (Jan 1, 2026)

**New Backend Modules Created:**

| Module | Lines | Purpose |
|--------|-------|---------|
| `backend/canonical_document.py` | ~770 | Single source of truth for preview/download |
| `backend/strengthen_session.py` | ~470 | Strengthen flow session management |
| `backend/resume_detection.py` | ~760 | Credibility, title inflation, career switcher detection |
| `backend/resume_language_lint.py` | ~440 | Mid-market language detection and auto-rewrite |
| `backend/resume_quality_gates.py` | ~790 | Pre-download validation gates |
| `backend/document_versioning.py` | ~600 | Document version tracking |

**New API Endpoints:**

```
POST /api/strengthen/session     - Create strengthen session
GET  /api/strengthen/session/{id} - Get session state
POST /api/strengthen/regenerate  - Generate strengthened bullet
POST /api/strengthen/accept      - Accept regeneration
POST /api/strengthen/skip        - Skip issue
POST /api/strengthen/complete    - Mark session complete
GET  /api/download/canonical     - Download with integrity checks
```

**Key Classes:**

```python
# canonical_document.py
@dataclass
class CanonicalDocument:
    resume: CanonicalResume
    cover_letter: CanonicalCoverLetter
    metadata: DocumentMetadata  # includes FitScoreDelta

@dataclass
class FitScoreDelta:
    original_score: int
    final_score: int
    improvement_summary: str
    score_locked: bool  # True after download

# strengthen_session.py
@dataclass
class StrengthenSession:
    session_id: str
    issues_found: List[str]
    regenerations: List[BulletRegeneration]  # Max 3 per bullet

FORBIDDEN_PATTERNS = [
    r"I also (did|led|managed|created)",  # New accomplishments
    r"promoted to|became|was made",        # Title changes
    r"learned|picked up|started using",    # New skills
]
```

**Frontend Changes:**
- `documents.html`: Canonical preview/download + fit score delta display
- `resume-leveling.html`: Credibility & Verifiability section with `renderCredibility()`

---

### Pre-Launch QA Fixes (Dec 23, 2025)

**Files Modified**:
- `frontend/results.html` - Proceed Anyway navigation, Apply button disable
- `backend/backend.py` - Domain gap priority, CORS fix, redirect field for gaps
- `frontend/components/hey-henry.js` - UI improvements, auto-expand, timestamps

**Fixes Implemented**:

1. **Proceed Anyway Navigation**
   - Fixed screen freeze after clicking "Acknowledged - Proceeding"
   - Now navigates to resume-leveling.html and auto-adds to tracker

2. **Domain Gap Priority**
   - Reordered priority so domain mismatch is Priority 1 when eligibility fails
   - Added specific redirects for Product Designers

3. **Your Move Redirect Field**
   - Added `redirect` field to eligibility, people leadership, and generic gaps
   - Coaching controller now generates specific redirect messaging
   - "Redirect to Product Designer roles at companies..." instead of generic

4. **Ask Henry UI**
   - Input box: min-height 80px (was 56px)
   - Send button: 28px (was 32px)
   - Timestamps on messages (e.g., "2:30 PM")
   - Auto-expand for responses >400 chars

---

### LinkedIn Profile Integration (Dec 15, 2025)

**Files Created/Modified**:
- `backend/backend.py` - New endpoints: `/api/linkedin/upload`, `/api/linkedin/align`, `/api/linkedin/optimize`
- `frontend/documents.html` - LinkedIn tab with optimized sections
- `frontend/profile-edit.html` - LinkedIn upload section
- `frontend/js/linkedin-upload.js` - LinkedIn parsing and rendering

**Features Implemented**:

1. **LinkedIn PDF Upload & Parsing**
   - Upload LinkedIn PDF export
   - Claude AI extracts profile data
   - Stores in sessionStorage alongside resume

2. **LinkedIn Score (0-100)**
   - Section-by-section analysis
   - Severity-based scoring (Critical, Important, Nice-to-Have)
   - Specific improvement suggestions

3. **LinkedIn Alignment Check**
   - Compare LinkedIn profile to job requirements
   - Identify gaps between resume and LinkedIn
   - Alignment score calculation

4. **LinkedIn Optimization**
   - Generate optimized headline (220 char limit)
   - Generate optimized About section (600-800 words)
   - Optimized experience bullets
   - Role-appropriate skill recommendations
   - Role-agnostic (PM, engineer, recruiter, sales, marketing)

---

### 4-Tier Recommendation System (Dec 16, 2025)

> **Versioning Note:** This document reflects the currently deployed 4-tier recommendation system. A 6-tier expansion is planned but not yet implemented.

**Files Modified**:
- `backend/backend.py` - `force_apply_experience_penalties()` function

**Features Implemented**:

Replaced binary Apply/Skip with nuanced 4-tier guidance:

```python
# CURRENT (DEPLOYED) - 4-Tier System
def get_recommendation_from_score(capped_score: int) -> str:
    if capped_score >= 75:
        return "Strongly Apply"    # Strong match - prioritize
    elif capped_score >= 60:
        return "Apply"             # Good fit - worth pursuing
    elif capped_score >= 40:
        return "Conditional Apply" # Stretch role - strategic positioning needed
    else:
        return "Do Not Apply"      # Not recommended
```

---

### Planned: 6-Tier Recommendation System (Not Yet Deployed)

The following 6-tier expansion is planned for a future release:

```python
# PLANNED (NOT YET DEPLOYED) - 6-Tier System
def get_recommendation_from_score_v2(capped_score: int) -> str:
    if capped_score >= 85:
        return "Strongly Apply"    # Strong match - prioritize
    elif capped_score >= 70:
        return "Apply"             # Good fit - worth pursuing
    elif capped_score >= 55:
        return "Consider"          # Moderate fit - if interested
    elif capped_score >= 40:
        return "Conditional Apply" # Stretch role - strategic positioning
    elif capped_score >= 25:
        return "Long Shot"         # Significant gaps
    else:
        return "Do Not Apply"      # Not recommended
```

**Migration Notes:**
- "Consider" and "Long Shot" tiers are not yet deployed
- Current system uses 4 tiers with different thresholds
- 6-tier system will require UI updates for new tier styling

---

### 4-Tier → 6-Tier Migration Plan

This migration plan ensures a painless transition when ready to expand to 6 tiers.

**Phase 0: Lock Today (Current)** ✅
- 4-tier system = canonical
- Reality Check + Strategic Redirects depend only on:
  - `fit_score` thresholds
  - High-level recommendation categories
- Docs clearly separate Current vs Planned

**Phase 1: Shadow the 6-Tier System (No UI)** ⏳
- Internally compute a secondary `recommendation_v2`
- Not shown to users, logged only for analysis
- Mapping:
  - Strongly Apply → Strongly Apply
  - Apply → Apply
  - Conditional Apply → Consider OR Conditional Apply (based on gaps)
  - Do Not Apply → Long Shot OR Do Not Apply (based on severity)
- Purpose: Validate distributions without user impact

**Phase 2: Dual-Read, Single-Write** ⏳
- Keep 4-tier as the UI and API output
- Test Strategic Redirects sensitivity under 6-tier
- Test Reality Check severity mapping
- Add analytics: "Would 6-tier have changed guidance?"
- No migrations yet

**Phase 3: Opt-in UI (Feature Flag)** ⏳
- Enable 6-tier display for internal testing and beta users
- Keep 4-tier as fallback
- Ensure no change to eligibility logic, CEC math, or blockers

**Phase 4: Cutover** ⏳
- Rename enums cleanly
- Migrate stored recommendations
- Remove shadow logic
- Update specs from "Planned" → "Current"
- One release. No ambiguity.

---

### Experience Penalty Hard Caps (Dec 16, 2025)

**Files Modified**:
- `backend/backend.py` - Post-processing safety net

**Features Implemented**:

Backend enforces hard caps on fit scores based on experience gaps:

```python
def force_apply_experience_penalties(analysis_data, resume_data, jd_analysis):
    required_years = jd_analysis.get("required_years", 0)
    candidate_years = calculate_pm_years_from_resume(resume_data)

    if required_years > 0:
        years_percentage = (candidate_years / required_years) * 100

        if years_percentage < 50:
            hard_cap = 45
        elif years_percentage < 70:
            hard_cap = 60
        elif years_percentage < 90:
            hard_cap = 75
        else:
            hard_cap = 100  # No cap

        original_score = analysis_data.get("fit_score", 0)
        capped_score = min(original_score, hard_cap)

        if capped_score != original_score:
            analysis_data["fit_score"] = capped_score
            analysis_data["recommendation"] = get_recommendation_from_score(capped_score)
            analysis_data["_experience_cap_applied"] = True

    return analysis_data
```

---

### Company Credibility Scoring (Dec 16, 2025)

**Features Implemented**:

Multiplier system for experience calculation:

```python
CREDIBILITY_MULTIPLIERS = {
    "HIGH": 1.0,    # Public companies, Series B+, established brands
    "MEDIUM": 0.7,  # Series A startups, 10-50 employees
    "LOW": 0.3,     # Seed-stage startups, <10 employees
    "ZERO": 0.0     # Operations roles with PM title, volunteer/side projects
}
```

Applied BEFORE experience penalty calculations.

---

### Candidate Identity Bug Fix (Dec 16, 2025)

**Files Modified**:
- `backend/backend.py` - Lines 3162-3166 (`/api/jd/analyze`)
- `backend/backend.py` - Lines 4317-4321 (`/api/jd/analyze/stream`)

**Issue**: Analysis was addressing all users as "Henry" (template contamination)

**Fix**: Added explicit identity instruction to Claude prompts:

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

### Streaming Analysis Endpoint (Dec 16, 2025) - EXPERIMENTAL

**Files Created**:
- `backend/backend.py` - `/api/jd/analyze/stream` endpoint
- `frontend/streaming_test.html` - Development test page
- `frontend/analyzing_streaming.html` - Production-ready page

**Features**:
- Server-Sent Events (SSE) for real-time analysis
- Progressive UI updates as Claude generates
- Fields stream in order: fit_score → recommendation → strengths → applicants

**Status**: REVERTED from production
- Experience penalties weren't reflecting correctly in partial data
- Files preserved for future re-integration

---

### API Error Resilience (Dec 13-14, 2025)

**Files Modified**:
- `backend/backend.py` - Added retry logic to `call_claude` and `call_claude_streaming`
- `frontend/analyzing.html` - Added user-friendly error messages

**Features Implemented**:

1. **Exponential Backoff Retry Logic**
   - Handles Anthropic 529 (overload) errors gracefully
   - Retries up to 3 times with exponential backoff (2s, 4s, 8s)
   - User-friendly error messages when retries exhausted

   ```python
   def call_claude(system_prompt: str, user_message: str, max_tokens: int = 4096, max_retries: int = 3) -> str:
       import time
       for attempt in range(max_retries):
           try:
               message = client.messages.create(...)
               return response_text
           except anthropic.APIStatusError as e:
               if e.status_code == 529:
                   if attempt < max_retries - 1:
                       wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                       time.sleep(wait_time)
                       continue
                   else:
                       raise HTTPException(status_code=503, detail="Our AI is temporarily busy. Please try again in a moment.")
   ```

2. **Frontend Error Handling**
   - Detects Claude API errors and displays friendly messages
   - Avoids exposing technical error details to users

---

### Status Banner Component (Dec 13-14, 2025)

**Files Created**:
- `frontend/components/status-banner.js` - New toggleable status banner component

**Files Modified**:
- 17+ HTML files - Added status-banner.js include

**Features Implemented**:

1. **Toggleable Service Outage Banner**
   - Simple flag to enable/disable: `SHOW_STATUS_BANNER = true/false`
   - Customizable message
   - Personalized greeting with user's name
   - Fun, friendly tone ("Ahh damn, [Name]!")

   ```javascript
   const SHOW_STATUS_BANNER = false;  // Toggle on/off
   const STATUS_MESSAGE = "Our AI provider is experiencing some hiccups...";

   function createAlert() {
       const firstName = getUserFirstName();
       const nameGreeting = firstName ? `, ${firstName}` : "";
       const fullMessage = `Ahh damn${nameGreeting}! ${STATUS_MESSAGE}`;
       // Creates inline alert box with 😅 icon
   }
   ```

2. **Inline Alert Positioning**
   - Inserted above Today's Focus section (not fixed position)
   - Does not disrupt page layout or navigation
   - Dismissible with sessionStorage persistence

---

### Dashboard UI Refinements (Dec 13-14, 2025)

**Files Modified**:
- `frontend/dashboard.html` - Layout changes
- `frontend/components/strategy-nav.js` - Logo positioning

**Features Implemented**:

1. **HenryHQ Logo Repositioning**
   - Moved from header to fixed position above sidebar navigation
   - Centered over the nav panel (268px width)
   - Sized to match greeting text (2rem)

   ```javascript
   const logo = document.createElement('div');
   logo.className = 'strategy-nav-logo';
   logo.innerHTML = '<a href="dashboard.html"><em>Henry</em>HQ</a>';
   document.body.appendChild(logo);
   ```

2. **Removed Redundant Banner**
   - Removed "You have 1 active application" daily pulse banner
   - Streamlined dashboard layout

3. **Section Reordering**
   - Moved Reality Check section below Today's Focus
   - Improved visual hierarchy

---

### Profile Management Enhancements (Dec 13-14, 2025)

**Files Modified**:
- `frontend/profile-edit.html` - Danger zone redesign

**Features Implemented**:

1. **Subtle Account Actions**
   - Replaced alarming "Danger Zone" red box with subtle text links
   - Positioned in bottom-left corner, stacked vertically
   - 50% opacity, small font (0.75rem)
   - Actions still accessible but not prominent

   ```html
   <div id="dangerZone" style="display: none; position: fixed; bottom: 24px; left: 24px; opacity: 0.5;">
       <div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-start;">
           <button id="resetProfileBtn" style="background: transparent; border: none; color: var(--color-text-muted); font-size: 0.75rem;">Reset Profile</button>
           <button id="deleteAccountBtn" style="background: transparent; border: none; color: var(--color-text-muted); font-size: 0.75rem;">Delete Account</button>
       </div>
   </div>
   ```

---

### Beta Access Gate (Dec 12, 2025)

**Files Created**:
- `frontend/beta-access.html` - Clean passcode entry UI

**Features Implemented**:

1. **Controlled Beta Testing**
   - Hardcoded passcode "BETA2025" (case-insensitive)
   - localStorage-based verification persistence
   - Protected pages: index, login, dashboard, analyze, tracker, profile-edit, interview-intelligence
   - Meta tags for noindex/nofollow

---

### Ask Henry Chatbot Enhancements (Dec 12, 2025)

**Files Modified**:
- `frontend/components/ask-henry.js` - Full-featured contextual AI assistant (1,058 lines)

**What's Implemented** (Informational Chat):

1. **Random Tooltip Messages**
   - 14+ fun prompts appearing every 20-40 seconds
   - Examples: "Peek-a-boo!", "Knock knock, it's Henry!", "Got questions?"
   - Timer pauses when chat is open

2. **Breathing Animation**
   - Logo pulses with scale animation (2.5s cycle)
   - Active pulse when chat is open

3. **Conversation History Persistence**
   - Last 20 messages saved in sessionStorage
   - Persists across page navigation

4. **Pipeline Data Integration**
   - Tracks total, active, interviewing applications
   - Calculates interview rates and fit scores
   - Identifies ghosted applications (14+ days no response)
   - Provides top 5 apps context to AI

5. **13+ Contextual Suggestion Sets**
   - Page-specific quick prompts (documents, tracker, interview-prep, etc.)

6. **Personalized Greetings**
   - Uses user's first name from profile/resume data

7. **Page Context Awareness**
   - 12 different page contexts with descriptions
   - Sent to backend for context-aware responses

8. **Message Formatting**
   - Supports bold (**text**), italic (*text*)
   - Bulleted and numbered lists
   - Paragraph formatting

9. **Global Functions**
   - `openAskHenry()` - Opens chat drawer
   - `openAskHenryWithPrompt(prompt)` - Opens and sends a message

**Also Implemented** (Transactional Features - Phase 1.5):

- ✅ **Document regeneration from chat commands**
  - Endpoint: `POST /api/documents/refine`
  - Natural language refinement ("make this more senior", "add more keywords")
  - Version tracking with before/after diffs

- ✅ **Screening questions analysis**
  - Endpoint: `POST /api/screening-questions/analyze`
  - Frontend: `frontend/screening-questions.html`
  - Risk assessment, knockout detection, honesty flags

---

### HenryHQ.ai Landing Page (Dec 12, 2025)

**Files Created**:
- `frontend/henryhq-landing.html` - Branded landing page

**Features Implemented**:
- Animated H logo with fade transition (2-second display)
- Clean black background, Instrument Serif font
- Ready for Cloudflare Pages deployment
- Domain HenryHQ.ai locked-in

---

### New User Signup Flow (Dec 13, 2025)

**Features Implemented**:

1. **Profile Check on Dashboard Load**
   - Redirects new users to onboarding flow
   - Delete Account with Supabase data clearing
   - Reset Profile (clears data, keeps account)
   - Confirmation modals with type-to-confirm safety

---

### Supabase Database Integration (Dec 14, 2025)

**Files Modified**:
- `frontend/supabase-client.js` - Full CRUD operations (20,306 lines)

**Database Tables**:
- `candidate_profiles` - User profiles
- `applications` - Job tracking
- `resume_conversations` - Chat history
- `interviews` - Interview management
- Row Level Security (RLS) policies on all tables

**Features**:
- Full authentication (signup, signin, signout, password reset)
- Data migration from localStorage to Supabase
- User data isolation by user_id

---

### QA Validation System Updates (Dec 14, 2025)

**Files Modified**:
- `backend/qa_validation.py` - Blocking disabled

**Changes**:
- Fixed schema mismatch in validation field names
- Disabled aggressive blocking (false positives on "improved pipeline" etc.)
- All blocking flags set to `False`:
  - `BLOCK_ON_FABRICATED_COMPANY = False`
  - `BLOCK_ON_FABRICATED_SKILL = False`
  - `BLOCK_ON_FABRICATED_METRIC = False`
- TODO: Re-enable after fixing regex detection logic

---

### Async/Await Syntax Fix (Dec 14, 2025)

**Files Modified**:
- `frontend/documents.html` - Fixed syntax error

**Commit**: `97edb3e` - Fix async/await syntax error in documents.html

---

### Resume Level Analysis Feature (Dec 11, 2025)

**Files Modified**:
- `frontend/resume-leveling.html` - Complete UI overhaul
- `frontend/components/strategy-nav.js` - Navigation updates
- `frontend/overview.html` - Removed leveling card

**Features Implemented**:

1. **Confidence-Based Visual Indicators**
   - Green checkmark (✓) for confidence ≥85%
   - Orange exclamation (!) for confidence 70-84%
   - Red X (✗) for confidence <70%

   ```javascript
   if (confidence >= 85) {
       levelBadge.className = 'level-badge high-confidence';
       levelBadgeIcon.textContent = '✓';
   } else if (confidence >= 70) {
       levelBadge.className = 'level-badge medium-confidence';
       levelBadgeIcon.textContent = '!';
   } else {
       levelBadge.className = 'level-badge low-confidence';
       levelBadgeIcon.textContent = '✗';
   }
   ```

2. **Signal Category Explanations**
   - Scope: "The scale of your work—team sizes, budgets, global reach, and organizational breadth."
   - Impact: "Measurable business outcomes—revenue growth, cost savings, efficiency gains, and KPI improvements."
   - Leadership: "How you influence others—managing teams, mentoring, driving initiatives, and cross-functional collaboration."
   - Technical: "Domain expertise and specialized skills—tools, methodologies, certifications, and technical depth."

3. **Collapsible Sections**
   - Reduces information overload on results page
   - Default collapsed: Signals, Red Flags, Language Analysis
   - Default expanded: Target Analysis, Recommendations
   - Level Card always visible

   ```css
   .collapsible-section {
       background: var(--color-surface);
       border: 1px solid var(--color-border);
       border-radius: 16px;
       margin-bottom: 24px;
       overflow: hidden;
   }
   .collapsible-section.collapsed .collapsible-content {
       max-height: 0 !important;
       padding-top: 0;
       padding-bottom: 0;
       opacity: 0;
   }
   ```

4. **Updated Navigation Flow**
   - Job Fit Score → Resume Level Analysis → Strategy Overview
   - Replaced "Skills Analysis" with "Resume Level Analysis" in nav
   - Sidebar now appears on Resume Level Analysis page

---

### UI/UX Improvements (Dec 11, 2025)

**Files Modified**:
- `frontend/components/strategy-nav.js` - Fixed toggle, updated nav structure
- `frontend/overview.html` - Removed leveling card and associated JS

**Fixes Implemented**:

1. **Sidebar Navigator Toggle Fix**
   - Issue: Toggle button wasn't expanding the sidebar panel
   - Root cause: Missing event listener on toggle button
   - Fix: Added click event listener in `init()` function

   ```javascript
   // Add toggle event listener
   const toggle = nav.querySelector('.strategy-nav-toggle');
   if (toggle) {
       toggle.addEventListener('click', () => toggleNav(nav, toggle));
   }
   ```

2. **Overview Page Cleanup**
   - Removed Resume Level Analysis card (it's a pre-generation step, not post-generation)
   - Removed associated JavaScript that referenced `levelingInsight`

3. **Navigation Structure Update**
   ```javascript
   const NAV_STRUCTURE = {
       topLevel: [
           { id: 'results', label: 'Job Fit Score', href: 'results.html' },
           { id: 'resume-leveling', label: 'Resume Level Analysis', href: 'resume-leveling.html' }
       ],
       parent: { id: 'overview', label: 'Strategy Overview', href: 'overview.html' },
       children: [
           { id: 'positioning', label: 'Positioning Strategy', href: 'positioning.html' },
           { id: 'documents', label: 'Tailored Documents', href: 'documents.html' },
           { id: 'outreach', label: 'Network & Outreach', href: 'outreach.html' },
           { id: 'interview-intelligence', label: 'Interview Intelligence', href: 'interview-intelligence.html' },
           { id: 'tracker', label: 'Command Center', href: 'tracker.html' }
       ],
       bottomLevel: [
           { id: 'analyze', label: 'Analyze New Role', href: 'analyze.html' }
       ]
   };
   ```

---

## Code Architecture Overview

### Backend Structure

```
backend/
├── backend.py                  # Main FastAPI application (7200+ lines)
├── document_generator/
│   ├── resume_formatter.py    # DOCX resume generation
│   └── cover_letter_formatter.py  # DOCX cover letter generation
```

### Frontend Structure

```
frontend/
├── index.html                 # Landing page
├── analyze.html               # JD analysis entry point
├── analyzing.html             # JD analysis in progress
├── results.html               # Fit score results
├── resume-leveling.html       # Resume level analysis (NEW - career leveling)
├── strengthen.html            # Gap-filling supplements
├── generating.html            # Document generation (auto-triggers)
├── overview.html              # Application strategy overview
├── documents.html             # Resume & cover letter preview
├── positioning.html           # Positioning strategy
├── outreach.html              # Network intelligence & outreach
├── interview-intelligence.html # Interview prep
├── tracker.html               # Pipeline command center
├── resume-chat.html           # Resume upload & conversation
├── ask-henry.html             # General chat interface
└── components/
    ├── ask-henry.js           # Shared chat widget
    └── strategy-nav.js        # Sidebar navigation component
```

### Key Files Modified

| File | Lines Changed | Purpose |
|------|---------------|---------|
| `backend/backend.py` | +168 | Added validation, keyword coverage, streaming support |
| System prompts | +6 | Added conversational wrapper instructions |
| `frontend/resume-leveling.html` | +200 | Collapsible sections, confidence icons, signal explanations |
| `frontend/components/strategy-nav.js` | +10 | Fixed toggle, updated nav structure |
| `frontend/overview.html` | -30 | Removed leveling card and associated JS |

---

## Implementation Details: Completed Features

### 1. Post-Generation Validation Layer

**Location**: `backend/backend.py` lines 856-928

**Function**: `validate_document_quality(generated_data, source_resume, jd_analysis)`

**What it does**:
- Validates generated documents for quality issues
- Checks grounding (no fabrication)
- Verifies ATS keyword coverage
- Detects generic language
- Validates company names match source resume
- Calculates overall quality score (0-100)

**Validation Checks**:

```python
def validate_document_quality(generated_data: Dict[str, Any], source_resume: Dict[str, Any], jd_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates:
    1. ATS Keyword Coverage (0-100%)
    2. Generic Language Detection (10 common phrases)
    3. Company Name Grounding (source vs generated)
    4. Minimum Length Check (>200 chars)

    Returns:
    {
        "quality_score": 0-100,
        "issues": ["list of critical issues"],
        "warnings": ["list of minor warnings"],
        "keyword_coverage": {
            "coverage_percentage": 0-100,
            "total_keywords": int,
            "found_keywords": [list],
            "missing_keywords": [list],
            "status": "complete" | "incomplete"
        },
        "approval_status": "PASS" | "NEEDS_REVIEW"
    }
    ```

**Quality Scoring Algorithm**:
```python
quality_score = 100
quality_score -= len(issues) * 15      # -15 per critical issue
quality_score -= len(warnings) * 5     # -5 per warning
quality_score = max(0, quality_score)

approval_status = "PASS" if quality_score >= 70 and len(issues) == 0 else "NEEDS_REVIEW"
```

**Integration Point**:
- Called in `/api/documents/generate` endpoint (line 3397)
- Results added to response as `validation` field
- Logged to console for debugging

**Example Output**:
```json
{
  "validation": {
    "quality_score": 92,
    "issues": [],
    "warnings": ["Generic phrases detected: team player, results-driven"],
    "keyword_coverage": {
      "coverage_percentage": 100.0,
      "total_keywords": 12,
      "found_keywords": ["stakeholder management", "agile", "cross-functional", ...],
      "missing_keywords": [],
      "status": "complete"
    },
    "approval_status": "PASS"
  }
}
```

---

### 2. ATS Keyword Coverage Verification

**Location**: `backend/backend.py` lines 821-854

**Function**: `verify_ats_keyword_coverage(generated_text, ats_keywords)`

**What it does**:
- Takes generated resume text and ATS keywords list
- Checks if each keyword appears in the resume (case-insensitive)
- Calculates coverage percentage
- Returns detailed report

**Algorithm**:
```python
def verify_ats_keyword_coverage(generated_text: str, ats_keywords: List[str]) -> Dict[str, Any]:
    generated_lower = generated_text.lower()
    found_keywords = []
    missing_keywords = []

    for keyword in ats_keywords:
        if keyword.lower() in generated_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    coverage_percentage = (len(found_keywords) / len(ats_keywords)) * 100

    return {
        "coverage_percentage": round(coverage_percentage, 1),
        "total_keywords": len(ats_keywords),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "status": "complete" if coverage_percentage == 100 else "incomplete"
    }
```

**Use Cases**:
1. Verify resume includes all ATS keywords from JD analysis
2. Flag missing keywords for user review
3. Ensure ATS systems will properly score the resume

**Example**:
```python
# Input
generated_text = "Experienced in stakeholder management and agile development..."
ats_keywords = ["stakeholder management", "agile development", "cross-functional leadership"]

# Output
{
  "coverage_percentage": 66.7,
  "total_keywords": 3,
  "found_keywords": ["stakeholder management", "agile development"],
  "missing_keywords": ["cross-functional leadership"],
  "status": "incomplete"
}
```

---

### 3. Conversational Wrappers

**Location**: `backend/backend.py` lines 2949-2955 (system prompt)

**What it does**:
- Adds a conversational context **before the required JSON output**
- JSON output is **always required** - this wrapper enhances it with explanation
- Explains strategic positioning decisions
- Highlights what was changed and why
- Notes key ATS keywords incorporated
- Flags gaps and mitigation strategies

**Important**: The JSON output is mandatory. The conversational wrapper provides additional context but does not replace the structured JSON response.

**System Prompt Addition**:
```python
CONVERSATIONAL CONTEXT:
Before the JSON output, provide a 3-4 sentence conversational summary that:
- Explains your strategic positioning decisions
- Highlights what you changed and why
- Notes key ATS keywords you incorporated
- Flags any gaps and how you mitigated them
Format: Start with "Here's what I created for you:\n\n" followed by your analysis, then add "\n\n---JSON_START---\n" before the JSON.

# NOTE: The JSON output after ---JSON_START--- is REQUIRED. The conversational
# summary is an enhancement that precedes the mandatory JSON response.
```

**Response Parsing** (lines 3282-3305):
```python
# Extract conversational context (appears before the required JSON)
conversational_summary = ""
json_text = response.strip()

if "---JSON_START---" in json_text:
    parts = json_text.split("---JSON_START---")
    conversational_summary = parts[0].strip()
    json_text = parts[1].strip()

# Parse the required JSON output
parsed_data = json.loads(json_text)

# Add conversational summary to response (if wrapper was included)
if conversational_summary:
    parsed_data["conversational_summary"] = conversational_summary
```

**Example Conversational Summary**:
```
Here's what I created for you:

I positioned you as a cross-functional product leader with a focus on data-driven decision making, which aligns perfectly with the JD's emphasis on analytics and stakeholder management. I led with your Spotify experience since it's most relevant to their B2B SaaS context, and de-emphasized your earlier IC work to emphasize leadership. I incorporated all 12 ATS keywords naturally throughout the resume, with particular density in the summary and core competencies sections. The main gap—fintech experience—was mitigated by highlighting your payment infrastructure work at Uber.
```

---

### 4. Enhanced System Prompts

**Location**: `backend/backend.py` lines 2935-2955

**Changes**:
1. Added explicit conversational wrapper instructions (see above)
2. Strengthened grounding rules (10 explicit rules vs. previous implicit guidance)
3. Added ATS optimization emphasis
4. Clarified candidate identity rules

**Key Grounding Rules** (lines 2936-2947):
```
CRITICAL RULES - READ CAREFULLY:
1. Use ONLY information from the CANDIDATE RESUME DATA provided below
2. Do NOT fabricate any experience, metrics, achievements, companies, titles, or dates
3. Do NOT invent new roles, companies, or responsibilities that are not in the resume
4. Do NOT use any template data, sample data, or default placeholder content
5. Do NOT use Henry's background, or any pre-existing resume templates
6. If a field is missing from the candidate's resume (e.g., no education listed), use an empty array []
7. You MAY rewrite bullets and summaries to better match the JD language
8. The underlying FACTS must remain true to the candidate's actual uploaded resume
9. Tailor which roles and bullets you emphasize based on the JD
10. Optimize for ATS systems with keywords from the JD
```

**Impact**:
- Reduces hallucination risk significantly
- Makes grounding expectations crystal clear
- Emphasizes factual accuracy over creative writing

---

### 5. Streaming Support Infrastructure

**Location**: `backend/backend.py` lines 783-799

**Function**: `call_claude_streaming(system_prompt, user_message, max_tokens)`

**What it does**:
- Provides streaming interface to Claude API
- Yields text chunks as they're generated
- Enables real-time UI updates

**Implementation**:
```python
def call_claude_streaming(system_prompt: str, user_message: str, max_tokens: int = 4096):
    """Call Claude API with streaming support - yields chunks of text"""
    try:
        print(f"🤖 Calling Claude API (streaming)... (message length: {len(user_message)} chars)")
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        print(f"🔥 CLAUDE API ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
```

**Status**: Infrastructure ready, endpoint not yet created
**Next Step**: Create `/api/documents/generate/stream` endpoint

---

## Next Steps: Streaming & UI Enhancements

### 1. Create Streaming Document Generation Endpoint

**File**: `backend/backend.py`

**Add after line 3425** (after existing `/api/documents/generate`):

```python
@app.post("/api/documents/generate/stream")
async def generate_documents_streaming(request: DocumentsGenerateRequest):
    """
    Streaming version of document generation.
    Returns Server-Sent Events (SSE) stream with:
    1. Progressive text chunks (conversational summary)
    2. Complete JSON data when finished
    3. Validation results
    """

    # Build system prompt and user message (same as non-streaming version)
    system_prompt = """You are a senior career strategist..."""  # Use same prompt as line 2933

    user_message = f"""Generate complete tailored application materials for this candidate and role.

CANDIDATE RESUME DATA:
{json.dumps(request.resume, indent=2)}

JOB DESCRIPTION ANALYSIS:
{json.dumps(request.jd_analysis, indent=2)}
"""

    if request.preferences:
        user_message += f"\n\nCANDIDATE PREFERENCES:\n{json.dumps(request.preferences, indent=2)}"

    if request.supplements and len(request.supplements) > 0:
        user_message += "\n\n=== ADDITIONAL CANDIDATE CONTEXT (from Strengthen Your Candidacy) ===\n"
        for supp in request.supplements:
            user_message += f"**Gap Area: {supp.gap_area}**\n"
            user_message += f"Question: {supp.question}\n"
            user_message += f"Candidate's Answer: {supp.answer}\n\n"

    # Define streaming generator
    async def stream_generator():
        full_response = ""

        # Send initial event
        yield f"data: {json.dumps({'type': 'start', 'message': 'Generating documents...'})}\n\n"

        try:
            # Stream Claude response
            for chunk in call_claude_streaming(system_prompt, user_message, max_tokens=8000):
                full_response += chunk

                # Send chunk to frontend
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            # Parse and validate complete response
            conversational_summary = ""
            json_text = full_response.strip()

            if "---JSON_START---" in json_text:
                parts = json_text.split("---JSON_START---")
                conversational_summary = parts[0].strip()
                json_text = parts[1].strip()

            # Clean and parse JSON
            cleaned = json_text
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            parsed_data = json.loads(cleaned)

            # Add conversational summary
            if conversational_summary:
                parsed_data["conversational_summary"] = conversational_summary

            # Ensure all required fields (same logic as non-streaming)
            if "resume_output" not in parsed_data:
                parsed_data["resume_output"] = {}

            resume_output = parsed_data["resume_output"]
            # ... (add all the fallback logic from lines 3307-3394) ...

            # Validate document quality
            validation_results = validate_document_quality(parsed_data, request.resume, request.jd_analysis)
            parsed_data["validation"] = validation_results

            # Send complete data
            yield f"data: {json.dumps({'type': 'complete', 'data': parsed_data})}\n\n"

        except Exception as e:
            print(f"❌ Streaming error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
```

---

### 2. Update Frontend to Use Streaming

**File**: `frontend/generating.html`

**Replace lines 279-361** (the `generateDocuments` function) with:

```javascript
async function generateDocuments() {
    // Get analysis data
    const analysisDataStr = sessionStorage.getItem('analysisData');
    if (!analysisDataStr) {
        showError('No analysis data found. Please start over.');
        return;
    }

    const analysisData = JSON.parse(analysisDataStr);
    const supplementsStr = sessionStorage.getItem('supplements');
    const supplements = supplementsStr ? JSON.parse(supplementsStr) : [];

    startProgressAnimation();

    try {
        // Build request payload
        const requestPayload = {
            resume: analysisData._resume_json || {},
            jd_analysis: {
                role_title: analysisData.role_title || analysisData._role || '',
                company_name: analysisData._company_name || analysisData._company || '',
                job_description: analysisData._jd_text || '',
                fit_score: analysisData.fit_score || 50,
                strengths: analysisData.strengths || [],
                gaps: analysisData.gaps || [],
                intelligence_layer: analysisData.intelligence_layer || {},
                ats_keywords: analysisData.intelligence_layer?.ats_keywords || []
            },
            preferences: analysisData._profile || {},
            supplements: supplements.length > 0 ? supplements : undefined
        };

        console.log('Generating documents with payload:', requestPayload);

        // Use streaming endpoint
        const response = await fetch(`${API_BASE_URL}/api/documents/generate/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            throw new Error(`Document generation failed (${response.status})`);
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let documentsData = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process complete lines
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));

                    if (data.type === 'start') {
                        console.log('Generation started');
                    } else if (data.type === 'chunk') {
                        // Show streaming text (optional: display in UI)
                        console.log('Chunk:', data.content);
                        // Could add a preview div to show conversational summary as it streams
                    } else if (data.type === 'complete') {
                        documentsData = data.data;
                        console.log('Documents generated:', documentsData);
                    } else if (data.type === 'error') {
                        throw new Error(data.message);
                    }
                }
            }
        }

        if (!documentsData) {
            throw new Error('No data received from server');
        }

        // Store documents data
        sessionStorage.setItem('documentsData', JSON.stringify(documentsData));

        const companyName = analysisData._company_name || analysisData._company || 'Unknown';
        const roleTitle = analysisData.role_title || analysisData._role || 'Unknown';
        const documentsKey = `documents_${companyName}_${roleTitle}`.toLowerCase().replace(/[^a-z0-9_]/g, '_');
        localStorage.setItem(documentsKey, JSON.stringify({
            ...documentsData,
            _company: companyName,
            _role: roleTitle,
            _generatedAt: new Date().toISOString()
        }));

        // Clear supplements
        sessionStorage.removeItem('supplements');
        sessionStorage.removeItem('originalGaps');

        // Go to overview
        window.location.href = 'overview.html';

    } catch (error) {
        console.error('Error generating documents:', error);

        let errorMsg = 'Something went wrong. Please try again.';
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            errorMsg = 'Unable to connect to the server. Please check your connection and try again.';
        } else if (error.message) {
            errorMsg = error.message;
        }

        showError(errorMsg);
    }
}

// Start generation when page loads
generateDocuments();
```

---

### 3. Display Conversational Summary & Validation

**File**: `frontend/overview.html`

**Add after line 60** (after subtitle):

```html
<!-- Conversational Summary Section -->
<div id="conversationalSummary" class="conversational-summary" style="display: none;">
    <h2>What I Created for You</h2>
    <p id="conversationalText"></p>
</div>

<!-- Validation Results Section -->
<div id="validationResults" class="validation-results" style="display: none;">
    <h3>Quality Report</h3>
    <div class="quality-badge">
        <div class="score" id="qualityScore">--</div>
        <div class="score-label">Overall Score</div>
    </div>
    <div class="validation-details">
        <div class="validation-item">
            <span class="validation-label">ATS Keyword Coverage:</span>
            <span class="validation-value" id="keywordCoverage">--</span>
        </div>
        <div id="validationIssues"></div>
        <div id="validationWarnings"></div>
    </div>
</div>
```

**Add CSS** (after existing styles):

```css
.conversational-summary {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-left: 4px solid #60a5fa;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 40px;
}

.conversational-summary h2 {
    font-size: 1.5rem;
    margin-bottom: 15px;
    color: #60a5fa;
}

.conversational-summary p {
    font-size: 1.05rem;
    line-height: 1.8;
    color: #d1d5db;
}

.validation-results {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 40px;
}

.validation-results h3 {
    font-size: 1.3rem;
    margin-bottom: 20px;
    color: #ffffff;
}

.quality-badge {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: rgba(96, 165, 250, 0.1);
    border: 2px solid #60a5fa;
    border-radius: 12px;
    padding: 20px 30px;
    margin-bottom: 20px;
}

.quality-badge .score {
    font-size: 2.5rem;
    font-weight: bold;
    color: #60a5fa;
}

.quality-badge .score-label {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-top: 5px;
}

.validation-details {
    margin-top: 20px;
}

.validation-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #374151;
}

.validation-label {
    color: #9ca3af;
}

.validation-value {
    color: #ffffff;
    font-weight: 600;
}

.validation-issue {
    background: rgba(239, 68, 68, 0.1);
    border-left: 3px solid #ef4444;
    padding: 12px;
    margin-top: 10px;
    border-radius: 4px;
    color: #fca5a5;
}

.validation-warning {
    background: rgba(251, 191, 36, 0.1);
    border-left: 3px solid #fbbf24;
    padding: 12px;
    margin-top: 10px;
    border-radius: 4px;
    color: #fcd34d;
}
```

**Add JavaScript** (at end of file, before `</body>`):

```javascript
<script>
// Load and display conversational summary and validation
function loadDocumentsMetadata() {
    const documentsDataStr = sessionStorage.getItem('documentsData');
    if (!documentsDataStr) return;

    const documentsData = JSON.parse(documentsDataStr);

    // Display conversational summary
    if (documentsData.conversational_summary) {
        document.getElementById('conversationalSummary').style.display = 'block';
        document.getElementById('conversationalText').textContent = documentsData.conversational_summary;
    }

    // Display validation results
    if (documentsData.validation) {
        const validation = documentsData.validation;
        document.getElementById('validationResults').style.display = 'block';

        // Quality score
        const score = validation.quality_score;
        const scoreElement = document.getElementById('qualityScore');
        scoreElement.textContent = score;
        scoreElement.style.color = score >= 90 ? '#10b981' : score >= 70 ? '#60a5fa' : '#ef4444';

        // Keyword coverage
        const coverage = validation.keyword_coverage;
        const coverageText = `${coverage.coverage_percentage}% (${coverage.found_keywords.length}/${coverage.total_keywords} keywords)`;
        document.getElementById('keywordCoverage').textContent = coverageText;

        // Issues
        const issuesDiv = document.getElementById('validationIssues');
        if (validation.issues && validation.issues.length > 0) {
            validation.issues.forEach(issue => {
                const issueDiv = document.createElement('div');
                issueDiv.className = 'validation-issue';
                issueDiv.textContent = `⚠️ ${issue}`;
                issuesDiv.appendChild(issueDiv);
            });
        }

        // Warnings
        const warningsDiv = document.getElementById('validationWarnings');
        if (validation.warnings && validation.warnings.length > 0) {
            validation.warnings.forEach(warning => {
                const warningDiv = document.createElement('div');
                warningDiv.className = 'validation-warning';
                warningDiv.textContent = `⚡ ${warning}`;
                warningsDiv.appendChild(warningDiv);
            });
        }
    }
}

// Call on page load
loadDocumentsMetadata();
</script>
```

---

## API Reference

### Core Endpoints

#### `POST /api/documents/generate`

**Status**: ✅ Enhanced with validation

**Request Body**:
```typescript
{
  resume: {
    name: string;
    contact: { email: string; phone?: string; location?: string; linkedin?: string };
    summary?: string;
    experience: Array<{
      company: string;
      title: string;
      dates: string;
      location?: string;
      bullets: string[];
    }>;
    education: Array<{
      institution: string;
      degree: string;
      graduation_year?: string;
    }>;
    skills: string[];
  };
  jd_analysis: {
    role_title: string;
    company_name: string;
    job_description: string;
    fit_score: number;
    strengths: string[];
    gaps: string[];
    intelligence_layer: {
      ats_keywords: string[];
      required_skills: string[];
      // ... other fields
    };
  };
  preferences?: {
    pronouns?: string;
    tone?: string;
    location?: string;
  };
  supplements?: Array<{
    gap_area: string;
    question: string;
    answer: string;
  }>;
}
```

**Response**:
```typescript
{
  resume_output: {
    headline?: string;
    summary: string;
    core_competencies: string[];
    experience_sections: Array<{
      company: string;
      title: string;
      location: string;
      dates: string;
      overview?: string;
      bullets: string[];
    }>;
    skills: string[];
    tools_technologies: string[];
    education: Array<{
      institution: string;
      degree: string;
      details?: string;
    }>;
    additional_sections: Array<{
      label: string;
      items: string[];
    }>;
    ats_keywords: string[];
    full_text: string;
  };
  cover_letter: {
    greeting: string;
    opening: string;
    body: string;
    closing: string;
    full_text: string;
  };
  interview_prep: {
    narrative: string;
    talking_points: string[];
    gap_mitigation: string[];
  };
  outreach: {
    hiring_manager: string;
    recruiter: string;
    linkedin_help_text: string;
  };
  changes_summary: {
    resume: {
      summary_rationale: string;
      qualifications_rationale: string;
      ats_keywords: string[];
      positioning_statement: string;
    };
    cover_letter: {
      opening_rationale: string;
      body_rationale: string;
      close_rationale: string;
      positioning_statement: string;
    };
  };
  conversational_summary?: string;  // NEW
  validation: {                      // NEW
    quality_score: number;           // 0-100
    issues: string[];
    warnings: string[];
    keyword_coverage: {
      coverage_percentage: number;
      total_keywords: number;
      found_keywords: string[];
      missing_keywords: string[];
      status: "complete" | "incomplete";
    };
    approval_status: "PASS" | "NEEDS_REVIEW";
  };
}
```

---

#### `POST /api/documents/generate/stream`

**Status**: 🚧 To be implemented

**Request Body**: Same as `/api/documents/generate`

**Response**: Server-Sent Events stream

**Event Types**:

```typescript
// Event 1: Start
{
  type: "start";
  message: string;
}

// Event 2-N: Chunks (streaming text)
{
  type: "chunk";
  content: string;
}

// Event N+1: Complete
{
  type: "complete";
  data: {
    // Same structure as /api/documents/generate response
  };
}

// Error event
{
  type: "error";
  message: string;
}
```

**Frontend Usage**:
```javascript
const response = await fetch('/api/documents/generate/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  // Process SSE events
}
```

---

## Testing & Quality Assurance

### Validation Testing

**Test Cases**:

1. **ATS Keyword Coverage**
   ```python
   # Test Case 1: All keywords present
   generated_text = "Experience in stakeholder management, agile development, and cross-functional leadership..."
   ats_keywords = ["stakeholder management", "agile development", "cross-functional leadership"]
   result = verify_ats_keyword_coverage(generated_text, ats_keywords)
   assert result["coverage_percentage"] == 100.0
   assert result["status"] == "complete"

   # Test Case 2: Missing keywords
   generated_text = "Experience in stakeholder management..."
   ats_keywords = ["stakeholder management", "agile development"]
   result = verify_ats_keyword_coverage(generated_text, ats_keywords)
   assert result["coverage_percentage"] == 50.0
   assert result["missing_keywords"] == ["agile development"]
   assert result["status"] == "incomplete"
   ```

2. **Quality Validation**
   ```python
   # Test Case 1: Perfect score
   generated_data = {
       "resume_output": {
           "full_text": "Senior Product Manager with 8 years...",  # 500+ chars
           "experience_sections": [
               {"company": "Google", ...},  # Matches source resume
           ]
       }
   }
   source_resume = {
       "experience": [{"company": "Google", ...}]
   }
   jd_analysis = {
       "ats_keywords": ["product management", "agile"]
   }
   result = validate_document_quality(generated_data, source_resume, jd_analysis)
   assert result["quality_score"] >= 90
   assert result["approval_status"] == "PASS"

   # Test Case 2: Fabricated company
   generated_data = {
       "resume_output": {
           "full_text": "...",
           "experience_sections": [
               {"company": "FakeCompany Inc.", ...}  # Not in source resume
           ]
       }
   }
   source_resume = {
       "experience": [{"company": "Google", ...}]
   }
   result = validate_document_quality(generated_data, source_resume, jd_analysis)
   assert len(result["issues"]) > 0
   assert "Unrecognized company" in result["issues"][0]
   assert result["approval_status"] == "NEEDS_REVIEW"
   ```

3. **Conversational Summary Parsing**
   ```python
   # Test Case 1: Summary present
   response = """
   Here's what I created for you:

   I positioned you as a senior product leader...

   ---JSON_START---
   {"resume_output": {...}}
   """
   parsed_data = parse_response(response)
   assert "conversational_summary" in parsed_data
   assert "positioned you as" in parsed_data["conversational_summary"]

   # Test Case 2: No summary (backward compatibility)
   response = '{"resume_output": {...}}'
   parsed_data = parse_response(response)
   assert "conversational_summary" not in parsed_data or parsed_data["conversational_summary"] == ""
   ```

---

### Manual Testing Checklist

- [ ] Upload resume → Verify parsing
- [ ] Analyze JD → Check ATS keywords extracted
- [ ] Generate documents → Verify validation runs
- [ ] Check quality score is 70+
- [ ] Verify keyword coverage is 80%+
- [ ] Confirm no fabricated companies
- [ ] Check conversational summary displays
- [ ] Verify validation results show in UI
- [ ] Test error handling (bad JD, network failure)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

---

## Deployment Guide

### Pre-Deployment Checklist

- [ ] Run all validation tests
- [ ] Verify no regression in existing features
- [ ] Test on staging environment
- [ ] Review logs for errors
- [ ] Check API response times (<3s for document generation)
- [ ] Verify frontend displays validation results

### Deployment Steps

1. **Backend Deployment** (Railway/Heroku/AWS)
   ```bash
   git add backend/backend.py
   git commit -m "feat: add validation, keyword coverage, conversational wrappers"
   git push origin main
   ```

2. **Frontend Deployment**
   ```bash
   # If frontend and backend are separate repos
   git add frontend/overview.html frontend/generating.html
   git commit -m "feat: display validation results and conversational summary"
   git push origin main
   ```

3. **Monitor Deployment**
   - Check logs for errors
   - Test document generation endpoint
   - Verify validation results appear in response

### Rollback Plan

If issues arise:

1. Revert validation integration:
   ```python
   # Comment out validation in backend.py line 3397
   # validation_results = validate_document_quality(...)
   # parsed_data["validation"] = validation_results
   ```

2. Frontend will gracefully handle missing validation field:
   ```javascript
   if (documentsData.validation) {
       // Display validation - won't run if field missing
   }
   ```

---

## Monitoring & Metrics

### Key Metrics to Track

1. **Quality Metrics**
   - Average quality score: Target 85+
   - Keyword coverage: Target 95%+
   - Approval status: Target 90%+ PASS

2. **Performance Metrics**
   - Document generation time: Target <40s
   - Validation overhead: Target <500ms

3. **Error Rates**
   - JSON parsing errors: Target <1%
   - Validation failures: Track for quality improvements

### Logging

**Key log points**:
- Document generation start/complete
- Validation results (quality score, coverage %, issues)
- Errors and exceptions

**Example log output**:
```
🤖 Calling Claude API... (message length: 15234 chars)
🤖 Claude responded with 8976 chars
============================================================
VALIDATION RESULTS:
Quality Score: 92/100
Status: PASS
Keyword Coverage: 100.0%
Issues: []
Warnings: ['Generic phrases detected: team player']
============================================================
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Validation returns quality_score < 70

**Cause**: Missing keywords, fabricated companies, or generic language

**Solution**:
1. Check which validation check failed
2. If keyword coverage low, ensure JD analysis extracted correct keywords
3. If company mismatch, verify resume parsing accuracy
4. If generic language, prompt may need adjustment

#### Issue 2: No conversational_summary in response

**Cause**: Claude didn't follow format instructions

**Solution**:
1. Check if `---JSON_START---` appears in response
2. Verify system prompt includes conversational wrapper instructions
3. May need to adjust prompt phrasing for better compliance

#### Issue 3: Validation shows "Unrecognized company"

**Cause**: False positive (e.g., company name abbreviation)

**Solution**:
1. Improve company matching algorithm (fuzzy matching)
2. Add exception handling for common variations
3. Log false positives for manual review

---

## Future Enhancements

### Short-Term (Next Sprint)

1. **Streaming Endpoint** (Week 1-2)
   - Implement `/api/documents/generate/stream`
   - Update frontend to use SSE
   - Add progressive text rendering

2. **Validation UI** (Week 2)
   - Display quality badge in overview.html
   - Show keyword coverage details
   - Add "What Changed" section

3. **Optimistic UI** (Week 2)
   - Instant feedback on button clicks
   - Skeleton loaders
   - Pre-loaded state

---

## Phase 1.5: Application Support Features (Jan 2-17, 2026)

**Timeline**: Expedited 2.5 weeks (was Jan 9-22, now Jan 2-17)
**Purpose**: Prevent silent rejections and enable document refinement

### Sprint Overview

| Week | Focus | Deliverables |
|------|-------|--------------|
| Week 1 (Jan 2-8) | Core Development | Screening Questions endpoint, Document Refine endpoint, Frontend UI |
| Week 2 (Jan 9-15) | Beta Testing + Deploy | Internal testing, bug fixes, production deployment |
| Week 3 (Jan 16-17) | Buffer + Monitoring | Post-deploy monitoring, user feedback collection |

---

### 1.5.1 Screening Questions Analysis

**New Endpoint**: `POST /api/screening-questions/analyze`

**Purpose**: Analyze screening questions to prevent silent auto-rejections

**Pydantic Models**:

```python
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class QuestionType(str, Enum):
    YES_NO = "yes_no"
    EXPERIENCE_YEARS = "experience_years"
    SALARY = "salary"
    ESSAY = "essay"
    MULTIPLE_CHOICE = "multiple_choice"
    AVAILABILITY = "availability"

class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class HonestyFlag(str, Enum):
    TRUTHFUL = "truthful"
    STRATEGIC_FRAMING = "strategic_framing"
    BORDERLINE = "borderline"

class ScreeningQuestion(BaseModel):
    question: str
    type: QuestionType
    options: Optional[List[str]] = None

class ScreeningQuestionsRequest(BaseModel):
    questions: List[ScreeningQuestion]
    resume_data: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    job_description: Optional[str] = None

class QuestionAnalysis(BaseModel):
    question: str
    question_type: QuestionType
    risk_level: RiskLevel
    risk_reason: str
    recommended_answer: str
    justification: str
    honesty_flag: HonestyFlag
    knockout_question: bool
    confidence: float  # 0.0 - 1.0

class ScreeningQuestionsResponse(BaseModel):
    analysis: List[QuestionAnalysis]
    overall_risk: RiskLevel
    auto_reject_flags: int
    strategic_notes: str
    conversational_summary: str
```

**Endpoint Implementation**:

```python
@app.post("/api/screening-questions/analyze", response_model=ScreeningQuestionsResponse)
async def analyze_screening_questions(request: ScreeningQuestionsRequest):
    """
    Analyzes screening questions against resume to identify auto-rejection risks
    and provide strategic, honest answer recommendations.
    """

    system_prompt = """You are an expert career advisor helping job seekers navigate
    application screening questions. Your goal is to:

    1. Identify questions that could trigger automatic rejection
    2. Analyze the candidate's resume to find supporting evidence
    3. Recommend honest but strategically-framed answers
    4. Flag any questions where the candidate should be cautious

    CRITICAL RULES:
    - Never recommend lying or fabricating experience
    - Always base recommendations on actual resume content
    - Flag borderline cases honestly (e.g., "4.5 years" for "5+ years required")
    - Consider how recruiters typically interpret these questions
    - Prioritize the candidate's long-term reputation over short-term gains

    For each question, provide:
    - risk_level: "high" (likely auto-reject), "medium" (careful consideration needed), "low" (straightforward)
    - recommended_answer: The strategic but honest response
    - justification: Why this answer is appropriate
    - honesty_flag: "truthful" (100% accurate), "strategic_framing" (true but optimally presented), "borderline" (requires judgment call)
    - knockout_question: true if this could immediately disqualify the candidate

    Return as JSON matching the ScreeningQuestionsResponse schema.
    """

    user_message = f"""Analyze these screening questions for this candidate:

SCREENING QUESTIONS:
{json.dumps([q.dict() for q in request.questions], indent=2)}

CANDIDATE RESUME:
{json.dumps(request.resume_data, indent=2)}

JOB ANALYSIS:
{json.dumps(request.jd_analysis, indent=2)}

{f"JOB DESCRIPTION: {request.job_description}" if request.job_description else ""}

Provide analysis for each question with risk assessment and recommended answers.
Start with a brief conversational summary, then provide the structured analysis.
"""

    response = call_claude(system_prompt, user_message, max_tokens=4000)

    # Parse JSON from response
    json_text = response.strip()
    if "---JSON_START---" in json_text:
        parts = json_text.split("---JSON_START---")
        conversational_summary = parts[0].strip()
        json_text = parts[1].strip()
    else:
        conversational_summary = ""

    # Clean markdown code blocks if present
    if json_text.startswith("```"):
        json_text = json_text.split("```")[1]
        if json_text.startswith("json"):
            json_text = json_text[4:]
        json_text = json_text.strip()

    parsed = json.loads(json_text)
    parsed["conversational_summary"] = conversational_summary

    return ScreeningQuestionsResponse(**parsed)
```

**Frontend Page** (`screening-questions.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screening Questions Analysis | HenryAI</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="screening-container">
        <header>
            <h1>Screening Questions Analysis</h1>
            <p class="subtitle">Avoid silent rejections with strategic answer recommendations</p>
        </header>

        <!-- Question Input Section -->
        <section class="question-input-section">
            <h2>Add Your Screening Questions</h2>
            <p>Paste or type the screening questions from your job application</p>

            <div id="questionsList"></div>

            <button onclick="addQuestion()" class="add-btn">
                <span>+</span> Add Question
            </button>

            <button onclick="analyzeQuestions()" class="primary-btn" id="analyzeBtn">
                Analyze Questions
            </button>
        </section>

        <!-- Loading State -->
        <div id="loadingState" class="hidden">
            <div class="loading-spinner"></div>
            <p>Analyzing your screening questions...</p>
        </div>

        <!-- Analysis Results -->
        <section id="analysisResults" class="hidden">
            <div class="risk-summary">
                <div class="summary-card">
                    <h3>Overall Risk</h3>
                    <div class="overall-risk" id="overallRisk">--</div>
                </div>
                <div class="summary-card">
                    <h3>Knockout Questions</h3>
                    <div class="auto-reject-count" id="rejectFlags">0</div>
                </div>
            </div>

            <div class="conversational-summary" id="conversationalSummary"></div>

            <h2>Question-by-Question Analysis</h2>
            <div id="questionAnalysis"></div>
        </section>
    </div>

    <script>
        const API_BASE_URL = 'YOUR_API_URL';
        let questionCount = 0;

        function addQuestion() {
            questionCount++;
            const container = document.getElementById('questionsList');
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.id = `question-${questionCount}`;
            questionDiv.innerHTML = `
                <div class="question-header">
                    <span class="question-number">Q${questionCount}</span>
                    <button onclick="removeQuestion(${questionCount})" class="remove-btn">×</button>
                </div>
                <textarea placeholder="Enter the screening question..." class="question-text"></textarea>
                <select class="question-type">
                    <option value="yes_no">Yes/No</option>
                    <option value="experience_years">Years of Experience</option>
                    <option value="salary">Salary</option>
                    <option value="essay">Essay/Open-ended</option>
                    <option value="multiple_choice">Multiple Choice</option>
                    <option value="availability">Availability</option>
                </select>
            `;
            container.appendChild(questionDiv);
        }

        function removeQuestion(id) {
            document.getElementById(`question-${id}`).remove();
        }

        async function analyzeQuestions() {
            const questionItems = document.querySelectorAll('.question-item');
            if (questionItems.length === 0) {
                alert('Please add at least one screening question');
                return;
            }

            const questions = [];
            questionItems.forEach(item => {
                const text = item.querySelector('.question-text').value.trim();
                const type = item.querySelector('.question-type').value;
                if (text) {
                    questions.push({ question: text, type: type });
                }
            });

            if (questions.length === 0) {
                alert('Please enter at least one question');
                return;
            }

            // Get resume and analysis data from session
            const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
            const resumeData = analysisData._resume_json || {};

            // Show loading
            document.getElementById('loadingState').classList.remove('hidden');
            document.getElementById('analysisResults').classList.add('hidden');
            document.getElementById('analyzeBtn').disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/api/screening-questions/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        questions: questions,
                        resume_data: resumeData,
                        jd_analysis: analysisData
                    })
                });

                if (!response.ok) throw new Error('Analysis failed');

                const result = await response.json();
                displayResults(result);

            } catch (error) {
                console.error('Error:', error);
                alert('Failed to analyze questions. Please try again.');
            } finally {
                document.getElementById('loadingState').classList.add('hidden');
                document.getElementById('analyzeBtn').disabled = false;
            }
        }

        function displayResults(result) {
            // Overall risk
            const riskDiv = document.getElementById('overallRisk');
            riskDiv.textContent = result.overall_risk.toUpperCase();
            riskDiv.className = `overall-risk risk-${result.overall_risk}`;

            // Knockout count
            document.getElementById('rejectFlags').textContent = result.auto_reject_flags;

            // Conversational summary
            if (result.conversational_summary) {
                document.getElementById('conversationalSummary').innerHTML =
                    `<p>${result.conversational_summary}</p>`;
            }

            // Question analysis
            const analysisDiv = document.getElementById('questionAnalysis');
            analysisDiv.innerHTML = '';

            result.analysis.forEach((qa, index) => {
                const card = document.createElement('div');
                card.className = `analysis-card risk-${qa.risk_level}`;
                card.innerHTML = `
                    <div class="card-header">
                        <span class="question-label">Question ${index + 1}</span>
                        ${qa.knockout_question ? '<span class="knockout-badge">KNOCKOUT</span>' : ''}
                        <span class="risk-badge risk-${qa.risk_level}">${qa.risk_level.toUpperCase()}</span>
                    </div>
                    <p class="question-text">"${qa.question}"</p>
                    <div class="recommendation">
                        <h4>Recommended Answer</h4>
                        <p class="answer">${qa.recommended_answer}</p>
                    </div>
                    <div class="details">
                        <p><strong>Risk Reason:</strong> ${qa.risk_reason}</p>
                        <p><strong>Justification:</strong> ${qa.justification}</p>
                        <p class="honesty-flag">
                            <span class="flag-${qa.honesty_flag}">${qa.honesty_flag.replace('_', ' ')}</span>
                            <span class="confidence">${Math.round(qa.confidence * 100)}% confidence</span>
                        </p>
                    </div>
                `;
                analysisDiv.appendChild(card);
            });

            // Show results
            document.getElementById('analysisResults').classList.remove('hidden');
        }

        // Add first question on page load
        addQuestion();
    </script>

    <style>
        .screening-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .question-item {
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }

        .question-text {
            width: 100%;
            min-height: 80px;
            margin: 12px 0;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--color-border);
            background: var(--color-bg);
            color: var(--color-text);
        }

        .question-type {
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--color-border);
            background: var(--color-surface);
            color: var(--color-text);
        }

        .risk-high { border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.1); }
        .risk-medium { border-left: 4px solid #f59e0b; background: rgba(245, 158, 11, 0.1); }
        .risk-low { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.1); }

        .knockout-badge {
            background: #dc2626;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .risk-badge {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .risk-badge.risk-high { background: #fecaca; color: #991b1b; }
        .risk-badge.risk-medium { background: #fef3c7; color: #92400e; }
        .risk-badge.risk-low { background: #d1fae5; color: #065f46; }

        .analysis-card {
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        .recommendation {
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
        }

        .recommendation h4 {
            margin: 0 0 8px 0;
            color: #60a5fa;
        }

        .answer {
            font-size: 1.1rem;
            font-weight: 500;
        }
    </style>
</body>
</html>
```

---

### 1.5.2 Document Iteration via Chat

**New Endpoint**: `POST /api/documents/refine`

**Purpose**: Allow users to refine documents via Ask Henry chat without restarting the flow

**Pydantic Models**:

```python
class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    OUTREACH = "outreach"

class RefineDocumentRequest(BaseModel):
    document_type: DocumentType
    current_document: Dict[str, Any]
    refinement_prompt: str
    resume_data: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    version: int = 1

class DocumentChange(BaseModel):
    section: str
    before: str
    after: str
    change_type: str  # "added", "removed", "modified"

class RefineDocumentResponse(BaseModel):
    refined_document: Dict[str, Any]
    changes: List[DocumentChange]
    change_summary: str
    version: int
    validation: Dict[str, Any]
```

**Endpoint Implementation**:

```python
@app.post("/api/documents/refine", response_model=RefineDocumentResponse)
async def refine_document(request: RefineDocumentRequest):
    """
    Refines an existing document based on user feedback while maintaining
    grounding in the original resume data.
    """

    system_prompt = f"""You are refining a {request.document_type.value} based on user feedback.

CRITICAL RULES:
1. Maintain all factual accuracy from the original resume
2. Only modify based on the user's specific request
3. Do NOT fabricate new experience, metrics, or achievements
4. Track all changes for transparency
5. Ensure ATS optimization is maintained or improved

User's refinement request: "{request.refinement_prompt}"

Return a JSON object with:
1. "refined_document": The updated document in the same structure
2. "changes": Array of {{"section": "...", "before": "...", "after": "...", "change_type": "modified"}}
3. "change_summary": A 1-2 sentence summary of what you changed
"""

    user_message = f"""Refine this document based on the user's request.

CURRENT DOCUMENT (v{request.version}):
{json.dumps(request.current_document, indent=2)}

ORIGINAL RESUME DATA (source of truth):
{json.dumps(request.resume_data, indent=2)}

JOB ANALYSIS:
{json.dumps(request.jd_analysis, indent=2)}

USER REQUEST: {request.refinement_prompt}

Return the refined document with change tracking as JSON.
"""

    response = call_claude(system_prompt, user_message, max_tokens=6000)

    # Parse response
    json_text = response.strip()
    if json_text.startswith("```"):
        json_text = json_text.split("```")[1]
        if json_text.startswith("json"):
            json_text = json_text[4:]
        json_text = json_text.strip()

    parsed = json.loads(json_text)

    # Run validation on refined document
    validation = validate_document_quality(
        {"resume_output": parsed["refined_document"]} if request.document_type == DocumentType.RESUME else {"cover_letter": parsed["refined_document"]},
        request.resume_data,
        request.jd_analysis
    )

    return RefineDocumentResponse(
        refined_document=parsed["refined_document"],
        changes=parsed.get("changes", []),
        change_summary=parsed.get("change_summary", "Document refined successfully"),
        version=request.version + 1,
        validation=validation
    )
```

**Ask Henry Integration** (`ask-henry.js` additions):

```javascript
// Add to ask-henry.js - detect refinement requests
const REFINEMENT_TRIGGERS = [
    'make it more', 'make this more', 'can you make',
    'add more', 'remove the', 'change the',
    'too generic', 'more specific', 'more senior',
    'less formal', 'more formal', 'shorter', 'longer',
    'rewrite', 'update the', 'modify the'
];

function detectRefinementRequest(message) {
    const lowerMessage = message.toLowerCase();
    return REFINEMENT_TRIGGERS.some(trigger => lowerMessage.includes(trigger));
}

async function handleRefinementRequest(message) {
    const currentPage = window.location.pathname;

    // Only handle refinements on document pages
    if (!currentPage.includes('documents') && !currentPage.includes('overview')) {
        return null; // Let normal chat handle it
    }

    const documentsData = JSON.parse(sessionStorage.getItem('documentsData') || '{}');
    const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');

    if (!documentsData.resume_output) {
        return null; // No document to refine
    }

    // Determine document type from context or default to resume
    let documentType = 'resume';
    if (message.toLowerCase().includes('cover letter')) {
        documentType = 'cover_letter';
    }

    const currentDoc = documentType === 'resume'
        ? documentsData.resume_output
        : documentsData.cover_letter;

    try {
        const response = await fetch(`${API_BASE_URL}/api/documents/refine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_type: documentType,
                current_document: currentDoc,
                refinement_prompt: message,
                resume_data: analysisData._resume_json || {},
                jd_analysis: analysisData,
                version: documentsData._version || 1
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Refinement failed');
        }

        const result = await response.json();

        // Update stored documents
        if (documentType === 'resume') {
            documentsData.resume_output = result.refined_document;
        } else {
            documentsData.cover_letter = result.refined_document;
        }
        documentsData._version = result.version;
        documentsData._lastRefinement = {
            timestamp: new Date().toISOString(),
            changes: result.changes,
            summary: result.change_summary
        };
        sessionStorage.setItem('documentsData', JSON.stringify(documentsData));

        // Format response with changes
        let changesText = '';
        if (result.changes && result.changes.length > 0) {
            changesText = '\n\n**Changes made:**\n';
            result.changes.forEach(change => {
                changesText += `• ${change.section}: ${change.change_type}\n`;
            });
        }

        return {
            message: `✅ I've updated your ${documentType.replace('_', ' ')} (now v${result.version}).\n\n${result.change_summary}${changesText}\n\n*Refresh the page to see the updated document.*`,
            showRefreshButton: true,
            validation: result.validation
        };

    } catch (error) {
        console.error('Refinement error:', error);
        return {
            message: `I couldn't refine the document: ${error.message}. Try rephrasing your request or ask me a different question.`,
            showRefreshButton: false
        };
    }
}

// Add refresh button helper
function addRefreshButton() {
    const chatMessages = document.querySelector('.chat-messages');
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'refresh-btn';
    refreshBtn.textContent = '🔄 Refresh to see changes';
    refreshBtn.onclick = () => window.location.reload();
    chatMessages.appendChild(refreshBtn);
}

// Modify the existing sendMessage function to check for refinements first
// Add this at the beginning of sendMessage():
/*
if (detectRefinementRequest(message)) {
    showTypingIndicator();
    const result = await handleRefinementRequest(message);
    hideTypingIndicator();
    if (result) {
        displayAssistantMessage(result.message);
        if (result.showRefreshButton) {
            addRefreshButton();
        }
        return;
    }
}
// ... continue with normal chat handling
*/
```

---

### Phase 1.5 Testing Checklist

**Screening Questions Analysis**:
- [ ] Yes/No questions with exact match (have exactly 5 years, need 5 years)
- [ ] Yes/No questions with near-miss (have 4.5 years, need 5 years)
- [ ] Salary questions with range detection
- [ ] Essay questions with keyword coverage
- [ ] Multiple knockout questions in same application
- [ ] Resume with gaps vs questions about continuous employment
- [ ] Work authorization questions
- [ ] Availability/start date questions

**Document Refinement**:
- [ ] "Make it more senior" increases leadership language
- [ ] "Add more ATS keywords" improves keyword coverage
- [ ] "Make the summary shorter" reduces summary length
- [ ] "Make the cover letter more enthusiastic" adjusts tone
- [ ] Version tracking increments correctly
- [ ] Changes are tracked and displayed
- [ ] Validation runs on refined document
- [ ] Original resume facts remain unchanged
- [ ] Refresh button appears after successful refinement
- [ ] Error handling for failed refinements

---

### Phase 1.5 Deployment Timeline

| Day | Date | Milestone |
|-----|------|-----------|
| 1-3 | Jan 2-4 | Screening Questions backend + frontend |
| 4-5 | Jan 5-6 | Document Refine backend + ask-henry.js integration |
| 6-7 | Jan 7-8 | Integration testing, bug fixes |
| 8-10 | Jan 9-11 | Internal beta testing |
| 11-12 | Jan 12-13 | Bug fixes from beta feedback |
| 13 | Jan 14 | Production deployment |
| 14-15 | Jan 15-17 | Monitoring, user feedback collection |

---

### Medium-Term (Month 2-3)

4. **Iterative Refinement**
   - Auto-regenerate if validation fails
   - Include validation feedback in refinement prompt
   - Track improvement after refinement

5. **Extended JD Analysis**
   - Hard vs soft requirements
   - Red flags to avoid
   - Scope signals

### Long-Term (Month 4+)

6. **Database Integration**
   - PostgreSQL setup
   - User accounts
   - Persistent state

---

## Appendix

### File Locations Reference

| Feature | File | Lines |
|---------|------|-------|
| Validation function | `backend/backend.py` | 856-928 |
| Keyword coverage function | `backend/backend.py` | 821-854 |
| Streaming helper function | `backend/backend.py` | 783-799 |
| Conversational prompt | `backend/backend.py` | 2949-2955 |
| Validation integration | `backend/backend.py` | 3397-3412 |
| Response parsing | `backend/backend.py` | 3282-3305 |
| Document generation endpoint | `backend/backend.py` | 3036-3425 |

### Dependencies

**Backend** (`requirements.txt` or similar):
```
anthropic>=0.20.0
fastapi>=0.104.0
pydantic>=2.4.0
python-docx>=1.1.0
uvicorn>=0.24.0
```

**Frontend**:
- No new dependencies (vanilla JavaScript)
- Uses native `fetch` API for SSE streaming

---

## Questions & Support

For questions about this implementation:
1. Review this guide
2. Check code comments in `backend/backend.py`
3. Test in staging environment first
4. Document any issues for team review

---

---

## December 17-19 Architecture Changes

### SYSTEM CONTRACT Block (Dec 19)

**Files Created**:
- `backend/SYSTEM_CONTRACT.md` - Canonical reference for non-negotiable constraints

**10 Contract Sections**:
1. Stateless Candidate Isolation
2. Allowed Persistent State (Global Only)
3. JD-Scoped vs Candidate-Scoped Data
4. Explicit Ban on Candidate → Global Promotion
5. JD-First Narrative Ordering
6. Decision Authority Lock
7. Analysis ID Enforcement
8. Strength Extraction Failure Handling
9. No Cross-Candidate Memory
10. Trust Principle

**Implementation Reference** (from SYSTEM_CONTRACT.md):
- `backend/recommendation/final_controller.py` - Decision Authority Lock (§6)
- `backend/coaching/coaching_controller.py` - JD-First Narrative Ordering (§5), Strength Failure Handling (§8)
- `backend/calibration/calibration_controller.py` - Gap Classification, Staff+ PM Rules
- `backend/backend.py` - Analysis Flow, Controller Integration

---

### Final Recommendation Controller (Dec 19)

**File Created**: `backend/recommendation/final_controller.py`

**Purpose**: Single Source of Truth for all recommendation decisions

**Key Classes**:

```python
class Recommendation(Enum):
    DO_NOT_APPLY = "Do Not Apply"
    APPLY_WITH_CAUTION = "Apply with Caution"
    CONDITIONAL_APPLY = "Conditional Apply"
    APPLY = "Apply"
    STRONG_APPLY = "Strong Apply"

@dataclass
class FinalDecision:
    recommendation: str
    fit_score: int
    confidence: str
    locked: bool = True
    locked_reason: str = ""
    advisory_signals: Dict[str, Any] = field(default_factory=dict)
```

**Score-to-Recommendation Mapping** (FROZEN):

```python
SCORE_TO_RECOMMENDATION = {
    (0, 50): Recommendation.DO_NOT_APPLY,
    (50, 60): Recommendation.APPLY_WITH_CAUTION,
    (60, 70): Recommendation.APPLY_WITH_CAUTION,
    (70, 80): Recommendation.CONDITIONAL_APPLY,
    (80, 90): Recommendation.APPLY,
    (90, 101): Recommendation.STRONG_APPLY,
}
```

**Usage**:

```python
from recommendation.final_controller import FinalRecommendationController

controller = FinalRecommendationController()
decision = controller.compute_recommendation(
    fit_score=75,
    eligibility_passed=True,
    is_manager_role=True,
    domain_gap_detected=True
)
# Returns: FinalDecision with recommendation="Conditional Apply"
```

---

### Calibration Controller (Dec 18-19)

**File Created/Modified**: `backend/calibration/calibration_controller.py`

**Features**:
- Capability Evidence Check (CEC) v1.1 with recruiter-grade sub-signals
- Gap classification with severity levels
- Staff+ PM calibration modifier
- Manager-level domain gap suppression

**Staff+ PM Rule**:

```python
is_staff_plus_pm = (
    ('staff' in role_title or 'principal' in role_title or 'senior' in role_title) and
    ('product' in role_title or 'pm' in role_title)
)
if is_staff_plus_pm:
    system_level_patterns = ['attribution', 'governance', 'internal platform', ...]
    jd_has_system_signals = any(p in jd_text for p in system_level_patterns)
    candidate_has_system_evidence = any(p in resume_text for p in system_level_patterns)
    if jd_has_system_signals and not candidate_has_system_evidence:
        print(f"   ⚠️ STAFF+ PM RULE: System-level signals required but not found")
```

---

### Coaching Controller Updates (Dec 19)

**File Modified**: `backend/coaching/coaching_controller.py`

**New Functions**:

1. **`_extract_jd_signal_profile()`** - Extract keywords FROM the JD, not global lists
2. **`_build_candidate_evidence_text()`** - Combine resume text for validation
3. **`_compute_candidate_signal_profile()`** - Detect domains, scale, leadership from resume
4. **`_generate_gap_focused_move()`** - Your Move when gaps ARE visible
5. **`_generate_positioning_move()`** - Your Move when gaps NOT visible

**UI Contract**:

```python
ui_contract = {
    "gaps_visible": not suppress_gaps_section and len(gaps_to_render) > 0,
    "strengths_available": strengths is not None and len(strengths) > 0,
    "recommendation": job_fit_recommendation
}
```

**Contract Assertion**:

```python
if not ui_contract['gaps_visible']:
    gap_language = ['gaps below', 'address gaps', 'missing experience', 'close the gap']
    for phrase in gap_language:
        if phrase in your_move.lower():
            print(f"   🚨 UI CONTRACT VIOLATION: Your Move contains '{phrase}' but gaps_visible=False")
```

---

### Signal Extraction System (Dec 19)

**File Modified**: `backend/coaching/coaching_controller.py`

**JD-Scoped Extraction**:

```python
def _extract_jd_signal_profile(job_requirements: Dict[str, Any], role_title: str) -> Dict[str, Any]:
    """
    Extract role-specific signal profile FROM THE JD, not from a global list.
    Prevents candidate → candidate contamination.
    """
    jd_text = (job_requirements.get('job_description', '') or '').lower()

    # Technical signal patterns
    technical_patterns = ['kubernetes', 'k8s', 'sre', 'distributed system', ...]

    # Product signal patterns
    product_patterns = ['product', 'roadmap', 'strategy', 'user research', ...]

    # Staff+ system-level signals
    staff_level_patterns = ['attribution', 'governance', 'internal platform', ...]

    # Extract keywords that actually appear in THIS JD
    jd_keywords = [p for p in all_patterns if p in jd_text]

    return {
        'jd_keywords': jd_keywords,
        'role_type': detected_role_type,
        'system_level_signals': staff_signals
    }
```

**Candidate Evidence Validation**:

```python
def _extract_role_signals(strengths, role_title, job_requirements, candidate_resume=None):
    # CONTRACT: Log extraction attempt for audit trail
    import hashlib
    candidate_hash = hashlib.md5(str(candidate_resume).encode()).hexdigest()[:8]
    role_hash = hashlib.md5(f"{role_title}:{job_description[:100]}".encode()).hexdigest()[:8]
    print(f"   🔐 Signal extraction scope: candidate={candidate_hash}, role={role_hash}")

    # JD keyword must exist in BOTH strength AND candidate resume
    for keyword in jd_keywords:
        if keyword in strength_lower:
            if candidate_evidence_lower and keyword not in candidate_evidence_lower:
                print(f"   ⚠️ JD keyword '{keyword}' in strength but NOT in resume. Skipping.")
                continue
            # Valid signal - add to list
```

---

**Document Maintained By**: Engineering Team
**Last Updated**: December 19, 2025
**Next Review**: December 26, 2025
