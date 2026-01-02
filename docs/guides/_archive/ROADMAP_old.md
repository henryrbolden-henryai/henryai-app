# HenryAI Product Roadmap

**Last Updated:** January 1, 2026

---

## Vision

HenryAI is a strategic job search intelligence platform that provides honest, actionable guidance to job seekers navigating a broken market. We differentiate from generic resume generators and high-volume application tools by offering recruiter-level strategic insight with a strict "no fabrication" policy.

**Core Principle:** Quality over quantity. Strategy over spam.

**Product Goal:** Users should think "What would Henry say?" before every job search decision. Henry is their strategist, not just their document generator.

---

## Phase 0: Conversational Resume Builder ✅

**Status:** Complete (Wave 1) - In Beta Testing

Transform the profile creation experience from form-filling into an AI-guided conversation that extracts skills and builds a professional resume from any background.

**Strategic Goal:** Make HenryAI accessible to job seekers who don't have a polished resume yet, including career changers, gig workers, recent graduates, and underemployed professionals.

### Core Concept

A streamlined text chat interface that:
1. Guides users through telling their work story naturally in 3-5 minutes
2. Extracts transferable skills from any experience (retail, gig work, volunteering, school projects)
3. Maps those skills to professional competencies
4. Suggests adjacent roles the user may not have considered
5. Generates a professional resume formatted for ATS systems

### Features

1. **Conversational Onboarding** ✅
   - Quick text chat with Henry (3-5 minutes, 10-15 questions total)
   - Direct, efficient questioning style ("Got it." "Nice." "Love it.")
   - No over-probing - accepts short answers and moves on
   - Name collection upfront (first, last, nickname)
   - Personalized greeting using preferred name
   - Infers details from job titles/companies rather than asking obvious questions

2. **Skills Extraction Engine** ✅
   - 12 skill categories: Leadership, Operations, Customer, Financial, Communication, Technical, Sales, Marketing, Administrative, Self-Management, Training, Industry-Specific
   - Indicator phrases mapped to skills (e.g., "handled complaints" → Customer Service, Conflict Resolution)
   - Confidence scoring for extracted skills
   - Responsibility-to-skill mapping for common job titles

3. **Adjacent Role Mapping** (Planned - Wave 2)
   - 35+ role definitions with required and preferred skills
   - Salary ranges and transition difficulty ratings
   - "Why It Fits" explanations based on extracted skills
   - Seniority level matching (entry, mid, senior, director)

4. **Skills Analysis Presentation** ✅
   - Visual skill breakdown by category with proficiency levels
   - Strength identification with evidence from conversation
   - Growth area identification for professional development
   - Matched roles with fit percentages

5. **Resume Generation** ✅
   - Professional formatting from conversational input
   - ATS-optimized structure
   - Experience bullets using extracted skills and real examples
   - Skills section organized by category

### Conversation Design Principles

The conversation follows a strict flow to respect user time:

1. **Current Role** - "What's your current job title and company?"
2. **Tenure/Location** - "How long have you been there, and where are you based?"
3. **Day-to-Day** - "What does a typical day look like?"
4. **Achievement** - "What's something you're proud of from your time there?"
5. **Previous Jobs** - "Any previous jobs worth mentioning?"
6. **Target Role** - "What kind of role are you looking for next?"

**Key Rules:**
- ONE question per turn
- Accept short answers without probing for more
- Use short acknowledgments: "Got it." "Nice." "Love it."
- Infer details from context (job title tells you the function)
- Never ask "Can you tell me more about..." or "What specifically..."

### User Segments

| Segment | Pain Point | How Phase 0 Helps |
|---------|-----------|-------------------|
| Career Changers | Don't know how to translate experience | Skill mapping to new industries |
| Gig Workers | Non-traditional work history | Extracts skills from diverse experiences |
| Recent Grads | Limited work experience | Values internships, projects, volunteering |
| Underemployed | Skills exceed current role | Surfaces hidden capabilities |
| Re-entering Workforce | Employment gaps | Focuses on skills over timeline |

### Integration with Existing Flow ✅

```
Phase 0: Conversational Onboarding (resume-chat.html)
        ↓
    Skills Analysis Review (skills-analysis.html)
        ↓
    Profile Setup (profile-edit.html)
        ↓
EXISTING: Analyze Job → Fit Scoring → Application Strategy
```

- Conversation data flows to skills analysis page
- Skills analysis flows to profile-edit for final touches
- Generated resume becomes default for role analysis
- Extracted skills enhance fit scoring accuracy

### Implementation Waves

**Wave 1: Text-Only MVP** ✅ Complete
- ✅ Chat interface for conversational onboarding
- ✅ Core skill extraction from conversation
- ✅ Basic resume generation
- ✅ Skills visualization (skills-analysis.html)
- ✅ Session persistence for conversation continuity
- ✅ Claude Haiku for fast conversational responses
- ✅ Name collection on start screen
- ✅ Streamlined conversation flow (3-5 minutes)

**Wave 2: Adjacent Role Engine** (Planned)
- Complete role database integration
- Personalized role recommendations
- Transition difficulty and salary insights

**Wave 3: Voice Integration** (Future Enhancement)
- OpenAI Whisper for speech-to-text
- OpenAI TTS for Henry's responses
- Voice/text hybrid mode
- Auto-listen with silence detection
- Visual feedback during speech

### Reference Documents

- [Resume Builder Specification](./henryai-resume-builder-spec.md) - Full implementation details
- [Skill Taxonomy](./henryai-skill-taxonomy.json) - Complete skill categories and indicators
- [Adjacent Roles Database](./henryai-adjacent-roles.json) - Role definitions and requirements
- [Sample Conversations](./henryai-resume-builder-sample-conversations.md) - Example conversation flows

---

## Phase 1: Core Application Engine ✅

**Status:** Complete (MVP) - In Beta Testing

The foundational workflow that takes a candidate from resume to application-ready materials.

### Features

1. **Resume Parsing** ✅ - Extract structured candidate data
2. **Job Description Analysis** ✅ - 50/30/20 fit scoring (Skills/Experience/Scope)
3. **Fit Assessment** ✅ - Honest evaluation with strengths, gaps, and recommendation
4. **Tailored Resume Generation** ✅ - ATS-optimized, no fabrication
5. **Tailored Cover Letter Generation** ✅ - Strategic positioning, real experience only
6. **Outreach Templates** ✅ - Hiring manager and recruiter messages
7. **Basic Interview Prep** ✅ - Talking points and gap mitigation
8. **Application Tracker** ✅ - Status tracking with actionable next steps
9. **Reality Check** ✅ - Honest market context and networking strategies
10. **Download Package** ✅ - ZIP with resume, cover letter, and outreach templates
11. **6-Tier Recommendation System** ✅ - Graduated guidance from "Strong Apply" to "Do Not Apply"
12. **Experience Penalty Hard Caps** ✅ - Backend safety net enforces maximum scores based on experience gaps
13. **Company Credibility Scoring** ✅ - Adjusts experience credit based on company scale/stage

### 10-Step Workflow

1. Upload resume
2. Paste job description (or extract from URL)
3. Analyze fit (50/30/20 scoring)
4. Review strengths and gaps
5. Generate tailored resume
6. Generate cover letter
7. Generate outreach messages
8. Provide interview prep
9. Prompt: "Save to tracker?"
10. Done - move to next role

---

## Phase 1.5: Interview Intelligence ✅

**Status:** Complete - In Beta Testing

Advanced interview preparation and post-interview analysis, accelerated from Phase 3.

### Features

1. **Interview Transcript Analysis** ✅ - Upload or paste transcript for feedback
2. **Response Scoring** ✅ - Rate content, clarity, relevance, structure, impact
3. **Mock Interview Prep** ✅ - Practice questions tailored to role with real-time feedback
4. **Interview Debrief** ✅ - Post-interview analysis with coaching and next steps
5. **Interviewer Intelligence** ✅ - Analyze interviewer LinkedIn profiles for communication patterns
6. **Practice Drills** ✅ - Dedicated practice interface for specific question types
7. **Intro/Elevator Pitch Practice** ✅ - Practice and refine your introduction with feedback

### Additional Features Built

- **Ask Henry Chat** ✅ - AI assistant widget available on all pages for contextual help
- **Text-to-Speech** ✅ - Audio generation for interview prep materials
- **URL JD Extraction** ✅ - Extract job descriptions directly from job posting URLs
- **Screening Question Responses** ✅ - Generate responses to application screening questions
- **Thank You Email Generation** ✅ - Post-interview thank you messages

---

## Phase 1.75: Engagement & Coaching Layer

**Status:** In Development - Current Priority

Transform Henry from a tool into a coach. Drive engagement beyond document generation to make HenryAI the user's one-stop job search hub.

**Strategic Goal:** Users currently get resume/cover letter and leave. This phase makes the other sections (Positioning, Network Intelligence, Interview Intelligence) feel essential, not optional.

### Henry as Proactive Coach

Shift Henry from reactive (waits for questions) to proactive (initiates guidance).

- **Application Readiness Score** - Visual progress indicator showing preparation completeness
  - Resume tailored (20%)
  - Cover letter generated (15%)
  - Positioning reviewed (10%)
  - Outreach prepared (20%)
  - Interview prep started (15%)
  - Mock interview completed (20%)

- **Proactive Notifications** - Henry nudges users based on their pipeline
  - Follow-up reminders: "You applied to [Company] 5 days ago. Want me to draft a follow-up?"
  - Interview prep alerts: "Your interview is in 2 days. You haven't done mock practice yet."
  - Stale application warnings: "[Company] has been quiet for 2 weeks. Should we discuss next steps?"
  - Post-interview prompts: "How did your interview go? Let's debrief."

- **Daily Pulse** - Dashboard summary on tracker page
  - Active applications count
  - Follow-ups due today
  - Upcoming interviews
  - Highest priority action

- **Application Import** - Import existing job search tracking
  - CSV/Excel import for candidates already tracking via spreadsheets
  - Column mapping for company, role, status, dates
  - Reduces friction for users with existing systems

### Insight-Driven Navigation

Surface personalized insights that create curiosity and drive exploration.

- **Teaser Insights on Overview Cards** - Don't just list sections, show what's inside
  - Positioning: "Your biggest gap is [X]. I have 3 ways to address it."
  - Network Intelligence: "I found the likely hiring manager. Direct outreach could 2x your response rate."
  - Interview Intelligence: "[Company] asks behavioral questions 73% of the time. You have 2 strong stories."

- **Post-Download Guidance** - After downloading documents, guide to next high-impact action
  - Modal: "Your documents are ready! But 70% of jobs are filled through referrals. I found 2 people to reach out to."

### Enhanced Ask Henry

Position Ask Henry as the central strategic hub, not just a help widget.

- **Proactive Conversation Starters** - Context-aware opening messages
- **Action Suggestions in Responses** - Include clickable next steps in Henry's answers
- **"What Should I Do Next?" Intelligence** - Smart prioritization of user's next best action
- **Cross-Page Context** - Henry remembers conversation across page navigation

### Success Metrics

| Metric | Current (Est.) | Target |
|--------|----------------|--------|
| Pages visited per session | 2-3 | 5+ |
| Return visits per week | 1-2 | 4+ |
| Network Intelligence views | 10% | 50%+ |
| Interview Intelligence views | 15% | 60%+ |
| Mock interview completion | 5% | 30%+ |
| Time on platform per session | 3-5 min | 10+ min |

### Implementation Priority

**Wave 1: Quick Wins**
1. Teaser Insights on Overview Cards
2. Post-Download Modal for Network Intelligence
3. Daily Pulse Banner on Tracker

**Wave 2: Core Systems**
4. Application Readiness Score
5. Proactive Ask Henry enhancements

**Wave 3: Full Notification System**
6. Henry Notification Engine with triggers, UI, and actions

---

## Phase 2: Strategic Intelligence Layer

**Status:** Partially Complete (~75%)

Enhances decision-making with market intelligence and broader career positioning.

### Hey Henry Strategic Intelligence Engine ✅

**Status:** Complete (Phase 2.1-2.8)

Transforms Hey Henry from reactive Q&A into a proactive strategic coach.

**Completed Features:**
1. **Pipeline Pattern Analysis** ✅ - Analyzes application success/failure patterns
2. **Proactive Network Surfacing** ✅ - Surfaces LinkedIn connections at target companies
3. **Rejection Forensics** ✅ - Identifies patterns in rejected applications
4. **Outreach Tracking** ✅ - Tracks follow-ups and surfaces overdue contacts
5. **Interview Debrief Intelligence** ✅ - Structured extraction from debrief conversations
6. **Cross-Interview Pattern Detection** ✅ - Identifies weak areas and overused stories
7. **Conversation Persistence** ✅ - Saves Hey Henry conversations to Supabase
8. **Story Bank UI** ✅ - Manage behavioral examples with usage tracking and effectiveness ratings

**Intelligence Loop:**
- User completes interview → debriefs with Henry
- Debrief conversation → extraction → structured data stored
- Next interview prep → pulls past debriefs → personalized coaching
- After 3+ debriefs → pattern detection → "This keeps coming up"

**Reference Documents:**
- [Hey Henry Strategic Intelligence Spec](./HEY_HENRY_STRATEGIC_INTELLIGENCE_ENGINE_SPEC_v1.md)
- [Interview Debrief Intelligence Spec](./HEY_HENRY_INTERVIEW_DEBRIEF_INTELLIGENCE_SPEC_v1.md)
- [Conversation History Spec](./HENRY_HENRY_CONVERSATION_HISTORY_SPEC_v1.md)

### Multi-Resume Management (Future)

**Status:** Planned - Requires Authentication Infrastructure

Allow users to upload and manage multiple resumes (up to 5) for multi-track job searches.

**Dependencies:**
- User authentication system (Supabase Auth)
- Backend database persistence for user data
- File storage (Supabase Storage)

**Features:**
- Upload up to 5 resumes with custom labels (e.g., "Technical Recruiting", "Executive Search")
- Set primary/default resume for new analyses
- Select which resume to use when analyzing each job
- Edit labels, delete resumes, manage library

**Why Deferred:**
- Current localStorage approach works for single-track users
- Requires foundational auth infrastructure not yet implemented
- Better to validate need with real user feedback first

**Implementation Guide:** Available in `docs/guides/MULTI_RESUME_IMPLEMENTATION.md`

---

### Job Quality and Market Intelligence

- **Job Quality Scoring** ✅ - Apply/Apply with caution/Skip assessment of role legitimacy
- **Industry Translation Engine** - Help career switchers reframe experience
- **Adjacent Role Mapping** - Surface related roles candidate may not have considered
- **Level Mismatch Detection** - Flag when candidate is over/under qualified

### LinkedIn Optimization ✅ (Complete)

- **LinkedIn Profile Score** ✅ - 0-100 rating with severity-based scoring and specific fixes
- **LinkedIn Profile Upload** ✅ - Upload LinkedIn PDF for automated parsing and analysis
- **LinkedIn Optimization Module** ✅ - Comprehensive rewrite of:
  - Headline (220 char limit enforced, role-appropriate format)
  - About Section (4 paragraphs, 600-800 words, role-specific content)
  - Experience Bullets (with severity prioritization)
  - Skills (role-appropriate keyword recommendations)
  - Optional Sections (Featured, Recommendations, Activity guidance)
- **LinkedIn Network Intelligence** ✅ - Search queries for hiring managers/recruiters
- **LinkedIn Alignment Check** ✅ - Compare LinkedIn profile to job requirements
- **Role-Agnostic Output** ✅ - Detects role type (recruiter, engineer, PM, marketing, sales) and generates appropriate content

### Tracker Enhancements

- **Calendar Sync** ✅ (Backend) - ICS file generation for Google/Apple Calendar (needs frontend triggers)
- **Action Item Reminders** - Email or push alerts for follow-ups (moved to Phase 1.75)
- **Follow-up Timing Alerts** ✅ (Phase 1.75) - "It has been 7 days, time to follow up"
- **Similar Roles Feed** - Auto-surface matching roles from job boards (Indeed API)

---

## Phase 3: Performance Intelligence Layer

**Status:** Partially Complete (Interview features moved to Phase 1.5)

Post-application coaching and interview performance optimization.

### Interview Intelligence (Moved to Phase 1.5)

- ~~Interview Transcript Analysis~~ ✅ Implemented
- ~~Response Scoring~~ ✅ Implemented
- **Behavioral Example Library** - Build STAR stories from past experience
- ~~Mock Interview Prep~~ ✅ Implemented

### Negotiation and Offers

- **Compensation Strategy** - Market rate research and negotiation scripts
- **Offer Review** - Evaluate total comp, not just base salary
- **Counter-offer Templates** - Professional negotiation language
- **Overqualified Coaching** - How to position when you exceed requirements

---

## Phase 4: Distribution and Ecosystem

**Status:** Long-term Vision

Expand reach and integrate with job search ecosystem.

### Integrations

- **Chrome Extension** - Analyze jobs directly on LinkedIn, Indeed, Greenhouse
- **Email Integration** - Track responses and auto-update tracker
- **ATS Direct Apply** - Submit applications without leaving HenryAI

### Community

- **Peer Review Network** - Get feedback from other job seekers
- **Industry-Specific Communities** - TA professionals, engineers, etc.
- **Success Stories** - Share wins and strategies

### External Engagement

- **Weekly Email Digest** - Personalized summary driving users back to platform
  - Pipeline health metrics
  - What's working analysis
  - Priority actions for the week

---

## Phase 5: Monetization and Scale

**Status:** Long-term Vision

Sustainable business model and enterprise expansion.

### Subscription Tiers

- **Free Tier** - Limited analyses per month
- **Pro Tier** - Unlimited analyses, full tracker, calendar sync
- **Career Switcher Pro** - Industry translation + adjacent role mapping
- **Interview Intelligence Pro** - Transcript analysis + mock interviews

### Enterprise

- **Internal Mobility Platform** - Help companies redeploy talent
- **Workforce Intelligence** - Aggregate insights for HR teams
- **Outplacement Partnership** - White-label for career transition firms

### Growth

- **Referral Program** - Rewards for successful referrals
- **Affiliate Partnerships** - Career coaches, resume writers
- **Content Marketing** - Job search strategy content

---

## Out of Scope (Intentionally)

These features conflict with HenryAI's philosophy:

- **Mass Application Tools** - We do not help spam 500 applications
- **Fake Experience Generation** - No fabrication, ever
- **ATS Gaming** - No keyword stuffing or dishonest optimization
- **Pay-to-Apply Services** - We help you apply smarter, not pay to cut lines

---

## Development Principles

1. **No fabrication** - Every word must trace to real experience
2. **Honest guidance** - Tell candidates when a role is not worth pursuing
3. **Recruiter perspective** - Build what actually moves the needle in hiring
4. **Phase discipline** - Complete each phase before starting the next
5. **User testing first** - Validate with real users before expanding features
6. **Engagement over features** - A used feature beats an unused feature

---

## Current Priority

**Phase 0: Conversational Resume Builder** ✅ Complete (Wave 1)

Streamlined text-based conversational onboarding is now live and in beta testing.

**Completed:**
1. ✅ Text chat interface for conversational onboarding
2. ✅ Skills extraction engine with Claude Haiku
3. ✅ Skills analysis visualization page
4. ✅ Name collection on start screen (first, last, nickname)
5. ✅ Session persistence for conversation continuity
6. ✅ Flow to profile-edit for final setup
7. ✅ Streamlined conversation (3-5 minutes, 10-15 questions)
8. ✅ Efficient questioning style (no over-probing)

**Next (Wave 2):**
- Adjacent role mapping engine
- Personalized role recommendations
- Transition difficulty and salary insights

**Future (Wave 3):**
- Voice integration (OpenAI Whisper STT + TTS)
- Auto-listen with silence detection
- Voice/text hybrid mode

---

**Phase 1.75: Engagement & Coaching Layer** (Ongoing)

The best features mean nothing if users don't engage with them. Before adding more capabilities, ensure users are getting full value from what's already built.

**Completed (Wave 1):**
1. ✅ Teaser Insights on Overview Cards
2. ✅ Post-Download Modal guiding to Network Intelligence
3. ✅ Daily Pulse Banner on Tracker
4. ✅ Command Center card on Overview
5. ✅ Standardized "Command Center" naming across nav
6. ✅ Application Import (CSV/Excel with job URL, JD, interview date)
7. ✅ "Ask Henry" button on application cards (context-aware help)
8. ✅ Separate Resume Discussion flow (resume-discuss.html)
9. ✅ HenryAI branding consistency across all pages

**Next (Wave 2):**
- Application Readiness Score
- Proactive Ask Henry enhancements
- Expandable skills view in profile
- Target role field for skills gap analysis

---

**Beta Testing Continues:**
- Phase 0 conversational resume builder
- Core 10-step application workflow
- Mock interview experience
- Interview debrief accuracy
- Ask Henry contextual helpfulness
- Engagement metrics tracking

---

## Implementation Summary

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 0: Conversational Resume Builder | **Complete (Wave 1)** | ~70% |
| Phase 1: Core Application Engine | Complete | 100% |
| Phase 1.5: Interview Intelligence | Complete | 100% |
| Phase 1.75: Engagement & Coaching | In Progress | ~65% |
| Phase 2: Strategic Intelligence | **Major Progress** | ~80% |
| Phase 2.5: Document Quality & Trust | **NEW - Complete** | 100% |
| Phase 3: Performance Intelligence | Partial | ~20% |
| Phase 4: Distribution & Ecosystem | Not Started | 0% |
| Phase 5: Monetization & Scale | Not Started | 0% |

### Phase 2.5: Document Quality & Trust Layer (Jan 2026)

| Feature | Status | Notes |
|---------|--------|-------|
| Canonical Document System | ✅ Complete | Single source of truth for preview/download |
| Strengthen Your Resume Flow | ✅ Complete | Constrained remediation with forbidden input validation |
| Fit Score Delta Display | ✅ Complete | Before/after comparison, locked at download |
| Credibility & Verifiability | ✅ Complete | Company, title, experience relevance cards |
| Resume Language Lint | ✅ Complete | 4-tier pattern detection |
| Resume Quality Gates | ✅ Complete | Pre-download validation |
| Non-Accusatory Red Flags | ✅ Complete | Neutral, constructive messaging |

### Pre-Launch QA (Dec 22, 2025)

| Test Area | Status | Notes |
|-----------|--------|-------|
| Resume Parsing | ✅ Complete | 10/10 edge cases passed |
| URL Extraction | ✅ Complete | Captcha detection fixed |
| Document Generation | ✅ Complete | Education + skills bugs fixed |
| Tracker API | ✅ Complete | CRUD + status transitions |
| Error Handling | ✅ Complete | All endpoints validated |
| LinkedIn Upload | ✅ Complete | 3/3 profiles parsed correctly |
| Ask Henry Context | 🔲 Pending | Manual browser testing required |
| Mock Interview | 🔲 Pending | Manual browser testing required |
| Screening Questions | 🔲 Pending | Manual browser testing required |
| Calendar Integration | 🔲 Pending | Manual browser testing required |

### Recent Feature Additions (Dec 15-16, 2025)

| Feature | Phase | Status |
|---------|-------|--------|
| LinkedIn Profile Score (0-100) | 2 | Complete |
| LinkedIn Optimization Strategy | 2 | Complete |
| LinkedIn Profile Upload | 2 | Complete |
| 6-Tier Recommendation System | 1 | Complete |
| Experience Penalty Hard Caps | 1 | Complete |
| Company Credibility Scoring | 1 | Complete |
| Backend Safety Net for Scoring | 1 | Complete |
| Candidate Identity Fix | 1 | Complete |
| Streaming Analysis Endpoint | Future | Experimental (Reverted) |

---

## Reference Documents

- [Engagement Strategy Implementation Plan](./ENGAGEMENT_STRATEGY_IMPLEMENTATION.md) - Detailed technical specs for Phase 1.75

---

## Session Log: December 10, 2025 (Session 2)

### Completed Today

**1. Application Import Feature (tracker.html)**
- CSV/Excel import with SheetJS library
- Smart column mapping: company, role, status, applied date
- New fields: job URL, job description, interview date
- Supports existing tracker workflows

**2. "Ask Henry" Button on Application Cards**
- Added H-mark logo button to every application card
- Context-aware help based on job description availability
- Links to Ask Henry chat with application context

**3. Resume Discussion Flow (resume-discuss.html)**
- NEW separate page for discussing existing resumes
- Always prompts for resume upload (not localStorage)
- HenryAI logo avatar in chat interface
- Offers: skills gap analysis, resume improvements, articulation help
- Distinct from resume-chat.html (which is for BUILDING new resumes)

**4. Profile Edit Updates (profile-edit.html)**
- Replaced "Edit Resume" button with "Chat with Henry about your resume" link
- Links to resume-discuss.html for existing resume discussion

**5. HenryAI Branding Consistency**
- Removed HenryAI logo from landing page (index.html) - hero "Meet Henry!" is sufficient
- Added HenryAI top nav header to all other pages:
  - strengthen.html
  - practice-intro.html
  - resume-chat.html
  - resume-discuss.html
- Consistent navigation: HenryAI logo (left), Command Center + Edit Profile links (right)

**6. Login Page Design (previous session)**
- Larger HenryAI text (2rem)
- Bigger H-mark logo (54px)
- Smaller tagline (1.1rem)
- Logo inline with tagline with pulse animation

### Database Updates Required

The following Supabase schema changes were made (user ran SQL):
```sql
ALTER TABLE applications ADD COLUMN IF NOT EXISTS job_url TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS job_description TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS interview_date DATE;
```

### Key User Decisions

1. **One Master Resume** - No multiple resumes. System generates tailored versions per job.
2. **Separate Resume Flows**:
   - "Conversation with Henry" (resume-chat.html) = BUILD new resume
   - "Chat with Henry about your resume" (resume-discuss.html) = DISCUSS existing resume
3. **Skills Gap Analysis** - Currently only available via resume discussion; profile-edit just shows counts

### Files Modified

- `frontend/tracker.html` - Import feature, Ask Henry button
- `frontend/profile-edit.html` - Resume chat link
- `frontend/resume-discuss.html` - NEW file
- `frontend/resume-chat.html` - Cleaned up (build-only mode)
- `frontend/index.html` - Removed HenryAI from nav
- `frontend/strengthen.html` - Added HenryAI nav
- `frontend/practice-intro.html` - Added HenryAI nav
- `frontend/login.html` - Sizing adjustments (previous session)
- `frontend/js/supabase-client.js` - New fields for applications

---

## Session Log: December 11, 2025

### Completed Today

**1. Bug Fix: Ask Henry "there" Issue**
- Fixed bug where Ask Henry was using "there" as if it were a user's name
- When no user name available, AI now uses warm generic greetings ("Hey, that's a great question...")
- Updated system prompt to explicitly prevent "there, ..." as a greeting

**2. Bug Fix: Mock Interview Responses Failing**
- Fixed bug where all mock interview responses showed "I didn't catch that"
- Root cause: `/api/mock-interview/respond` endpoint required `session_id` but frontend wasn't sending it
- Added `session_id` to the request body in `frontend/mock-interview.html`

**3. Multi-Resume Feature - Deferred to Phase 2**
- Received detailed implementation guide for multi-resume management
- Decision: Defer until authentication infrastructure is in place
- Added to Phase 2 in roadmap with dependencies documented
- Created full implementation guide at `docs/guides/MULTI_RESUME_IMPLEMENTATION.md`

**Why Multi-Resume Deferred:**
- Requires backend database persistence (currently localStorage only)
- Requires user authentication (Supabase Auth)
- Requires file storage (Supabase Storage)
- Current single-resume flow works for beta users
- Better to validate need with real user feedback first

### Files Modified

- `backend/backend.py` - Ask Henry prompt fixes for name handling
- `frontend/mock-interview.html` - Added session_id to respond API call
- `docs/guides/ROADMAP.md` - Added Multi-Resume to Phase 2, session log
- `docs/guides/MULTI_RESUME_IMPLEMENTATION.md` - NEW: Full implementation guide for future

---

## Session Log: December 15, 2025

### Completed Today

**1. LinkedIn Profile Score Feature (Complete)**
- NEW: `linkedin-scoring.html` - Comprehensive LinkedIn audit page
- 0-100 scoring system with severity-based weighting (CRITICAL, HIGH, MEDIUM, LOW)
- Visual score display with clear fix prioritization
- Renamed from "LinkedIn Audit" to "LinkedIn Profile Score"
- Changed subtitle to "Fix what's costing you interviews"

**2. LinkedIn Optimization Strategy (Documents Page)**
- Complete LinkedIn optimization output in documents.html LinkedIn tab
- Optimized Headline: 220 character limit enforced, formula-based structure
- Optimized About Section: 4 paragraphs, 600-800 words, role-specific
- Experience Optimizations: Severity-based bullet improvements
- Skills Recommendations: Role-appropriate keyword libraries
- Optional Sections: Featured, Recommendations, Activity guidance

**3. Role-Agnostic Output Generation (Critical Bug Fix)**
- Fixed contamination bug where recruiter terminology bled into non-recruiter profiles
- All output functions now detect role type (recruiter, engineer, product, marketing, sales)
- Role-specific content for: Headlines, About sections, Skills recommendations
- Added skill libraries for: Engineering, Product, Marketing, Sales, Leadership

**4. Headline Character Limit Enforcement**
- Hard 220 character limit (LinkedIn's max)
- Skips consultancies, stealth startups, self-employed from brand signals
- Removes parenthetical explanations like "(Independent Consultancy)"
- Progressive part removal if over limit
- Role-appropriate domain expertise (not lowercase skill dumps)

**5. Skills Section Improvements**
- Short keywords only (2-5 words), not sentences
- "Pin to Top 3" and "Add These" show different skills (no duplicates)
- Role-based skill libraries: recruiting, engineering, product, marketing, sales, leadership
- Generic skills flagged for removal (Microsoft Office, Communication, etc.)

**6. Activity Section Overhaul**
- Removed hardcoded company names (was showing "Engage with Digital Realty")
- Role-specific topic recommendations
- Seniority-aware guidance
- How to engage well / What to avoid lists
- Role-specific positioning statements

**7. Grammar and Style Fixes**
- Removed all em dashes from LinkedIn About section content
- Replaced with proper punctuation (periods, colons, commas)
- Prevents AI detection patterns

**8. Profile Edit Enhancements**
- Added "Replace Resume" button for updating resumes
- Added "Delete" button for resume removal
- Proper button styling with hover states

### Key Technical Changes

**Headline Formula:**
```
[Seniority] [Function] | [Specialization] | Ex-[Company1, Company2, Company3] | [Domain Expertise]
```

**Role Detection Pattern:**
```javascript
const isRecruiter = /recruit|talent acquisition|sourcer|headhunter/i.test(role);
const isEngineer = /engineer|developer|software|technical|architect/i.test(role);
const isProduct = /product manager|product lead|pm\b/i.test(role);
const isMarketing = /marketing|growth|brand/i.test(role);
const isSales = /sales|account|business development|revenue/i.test(role);
```

**Skill Libraries by Role:**
- Recruiters: Talent Acquisition, Executive Search, Boolean Search, etc.
- Engineers: Software Development, System Design, API Development, etc.
- Product: Product Strategy, User Research, A/B Testing, etc.
- Marketing: Digital Marketing, Content Strategy, SEO, etc.
- Sales: Sales Strategy, Account Management, Pipeline Management, etc.

### Files Modified

- `frontend/linkedin-scoring.html` - New LinkedIn Profile Score page
- `frontend/documents.html` - LinkedIn optimization strategy generation
- `frontend/js/linkedin-upload.js` - Optimized sections rendering
- `frontend/profile-edit.html` - Resume replace/delete functionality
- `docs/guides/ROADMAP.md` - Updated with today's features

---

## Session Log: December 16, 2025

### Completed Today

**1. 6-Tier Graduated Recommendation System**
- Replaced binary Apply/Skip with nuanced 6-tier system:
  - **Strong Apply** (70%+ fit) - "This is a strong fit. Apply immediately."
  - **Apply** (60-69% fit) - "Worth applying with strategic positioning."
  - **Conditional Apply** (50-59% fit) - "Apply if you can address gaps."
  - **Cautious Apply** (40-49% fit) - "Only apply if you have inside connections."
  - **Long Shot** (30-39% fit) - "Focus on building relevant experience first."
  - **Do Not Apply** (<30% fit) - "This role requires fundamentally different experience."
- Removed "Strongly Apply" tier - was inflating expectations
- Updated hard caps: 70-89% of required years now caps at 55% (was 70%)

**2. Experience Penalties - Backend Safety Net**
- Added `force_apply_experience_penalties()` function as post-processing safety net
- Calculates PM-specific years from resume data
- Applies hard caps even if Claude's response missed them:
  - <50% of required years → cap at 45%
  - 50-69% → cap at 55%
  - 70-89% → cap at 55%
- Updates recommendation field based on capped score

**3. Company Credibility Scoring**
- Added credibility multipliers for experience calculation:
  - HIGH (1.0x): Public companies, Series B+, established brands
  - MEDIUM (0.7x): Series A startups, 10-50 employees
  - LOW (0.3x): Seed-stage startups, <10 employees, defunct companies
  - ZERO (0x): Operations roles with PM title, volunteer/side projects
- Credibility adjustments happen BEFORE experience penalty calculations
- Example: 1 year at seed-stage startup = 0.3 credible years

**4. Reality Check - Strategic Action Improvements**
- Fixed "there" contamination in strategic_action field
- Now uses candidate's first name from resume
- Removed em dashes (—) from all output - prevents AI detection patterns
- Made strategic_action FIRST PERSON and conversational
- Proper punctuation enforcement throughout

**5. Streaming Analysis Endpoint (Experimental)**
- Created `/api/jd/analyze/stream` endpoint for real-time UI updates
- Uses Server-Sent Events (SSE) for progressive data delivery
- Fields stream as they're generated: fit_score → recommendation → strengths → applicants
- Created `analyzing-stream.html` frontend page with skeleton loading
- **Status:** Reverted to regular flow - experience penalties weren't reflecting correctly in partial data
- Files preserved for future iteration: `analyzing-stream.html`, `streaming_test.html`

**6. Candidate Identity Bug Fix**
- Fixed critical bug where analysis was addressing user as "Henry"
- Added identity instruction to both `/api/jd/analyze` and `/api/jd/analyze/stream`:
  - "The candidate is NOT Henry, NOT any template, NOT a generic user"
  - Use actual candidate name from resume
  - If no name, use "you/your" (second person)
- Example: "Rawan, this role is a stretch..." NOT "Henry, this role..."

**7. JSON Repair and Error Handling**
- Added aggressive JSON repair for common Claude response issues
- Handles unescaped quotes in strings
- Handles truncated responses
- Better error logging for diagnosis
- Improved validation of required fields

### Key Technical Changes

**Recommendation Tiers (fit_score → recommendation):**
```python
if capped_score >= 70:
    return "Strong Apply"
elif capped_score >= 60:
    return "Apply"
elif capped_score >= 50:
    return "Conditional Apply"
elif capped_score >= 40:
    return "Cautious Apply"
elif capped_score >= 30:
    return "Long Shot"
else:
    return "Do Not Apply"
```

**Hard Cap Logic:**
```python
if years_percentage < 50:
    hard_cap = 45
elif years_percentage < 70:
    hard_cap = 55
elif years_percentage < 90:
    hard_cap = 55  # More aggressive than before
else:
    hard_cap = 100  # No cap
```

**PM-Specific Years Calculation:**
```python
def calculate_pm_years_from_resume(resume_data):
    pm_patterns = ["product manager", "pm", "product lead", ...]
    for experience in resume_data.get("experience", []):
        if any(pattern in title.lower() for pattern in pm_patterns):
            total_years += parse_duration(dates)
    return total_years
```

### Files Modified

**Backend:**
- `backend/backend.py` - Lines 3160-3175: Candidate identity instruction
- `backend/backend.py` - Lines 4315-4330: Streaming endpoint identity instruction
- `backend/backend.py` - ~Line 4090: 6-tier recommendation system
- `backend/backend.py` - ~Line 4100: force_apply_experience_penalties()
- `backend/backend.py` - ~Line 3000: calculate_pm_years_from_resume()

**Frontend:**
- `frontend/analyze.html` - Line 1044: Reverted to analyzing.html (was analyzing-stream.html)
- `frontend/analyzing-stream.html` - NEW: Streaming analysis page (unused)
- `frontend/streaming_test.html` - NEW: Development test page (unused)

**Documentation:**
- `docs/guides/STREAMING_INTEGRATION.md` - NEW: Streaming implementation guide
- `docs/guides/ROADMAP.md` - This session log

### Key Decisions

1. **Reverted Streaming** - Experience penalties only apply to complete data, causing partial fit_score to show uncapped values. Regular flow shows correct penalized scores.

2. **More Aggressive Caps** - 70-89% years now caps at 55% (was 70%). Prevents false hope for candidates with significant experience gaps.

3. **Removed Strongly Apply** - Was creating unrealistic expectations. Strong Apply (70%+) is now the highest tier.

4. **First-Person Strategic Action** - "Apply within 24 hours and find the hiring manager..." feels more like coaching than "The candidate should..."

### Bug Fixes Summary

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| "Henry" appearing in analysis | No identity instruction in prompt | Added explicit candidate identity rules |
| Strategic action says "there, ..." | Fallback name "there" used as greeting | Use warm generic greeting if no name |
| Fit score too high for junior candidates | Hard caps not enforced by Claude | Backend safety net applies caps post-hoc |
| Em dashes in output | Claude uses em dashes by default | Explicit punctuation rules in prompt |
| JSON parsing failures | Unescaped quotes in Claude response | Aggressive JSON repair function |

### What's Next

1. **Test 6-tier system with users** - Get feedback on new recommendation language
2. **Monitor cap enforcement** - Ensure backend safety net is catching misses
3. **Streaming (future)** - Revisit when experience penalties can be applied to partial data
4. **LinkedIn Profile Upload** - Complete integration with job analysis alignment check

---

## Session Log: December 22, 2025 (Pre-Launch QA)

### Completed Today

**1. Resume Parsing Test Suite (10/10 Passed)**
- Created 10 test resumes covering edge cases:
  - Multi-column creative layouts
  - Table-based finance resumes
  - Standard baseline (control)
  - International characters (é, ü, ñ, €)
  - Career gaps
  - Concurrent/overlapping roles
  - Long executive resumes (4 pages, 7 jobs)
  - Functional/career changer format
  - DOCX with tables
  - Minimal/sparse resumes
- All 10 test cases passed successfully via API

**2. Document Generation Bug Fixes**
- Fixed education details character-by-character iteration bug
  - Root cause: `document_generator/resume_formatter.py` iterated string as chars
  - Fix: Convert string to single-item list before iteration
- Fixed skills category capitalization ("technical" → "Technical")
  - Added `.title()` to category names in `backend/document_generator.py`
- Fixed frontend education details normalization
  - Ensures `details` field is always a string, not an array

**3. URL Extraction Improvements**
- Fixed false positive captcha detection
  - Changed broad "captcha" pattern to specific blocking patterns
  - Now checks for: "please verify you are human", "recaptcha-checkbox", etc.
- Updated warning message in frontend

**4. LinkedIn Upload Testing (3/3 Passed)**
- Tested LinkedIn profile PDF parsing with 3 sample profiles
- All profiles parsed correctly:
  - Sarah Chen (Senior PM at Stripe)
  - Priya Sharma (Healthcare career changer)
  - DeShawn Williams (Self-taught developer)
- Headlines, summaries, experience bullets, skills, and education all extracted accurately

**5. Error Handling Testing (All Passed)**
- Tested API error responses for:
  - Missing required fields → Proper "Field required" messages
  - Invalid JSON body → Graceful handling
  - Wrong content types → Proper validation
  - Null values → Type error messages
  - Invalid URL formats → User-friendly error messages

**6. Tracker API Testing (Passed)**
- CRUD operations verified
- Status transitions working

### Files Modified

**Backend:**
- `document_generator/resume_formatter.py` - Education details iteration fix
- `backend/document_generator.py` - Skills category capitalization
- `backend/backend.py` - URL extraction captcha detection

**Frontend:**
- `frontend/documents.html` - Education details normalization
- `frontend/analyze.html` - URL extraction warning message

**Documentation:**
- `docs/KNOWN_ISSUES.md` - Updated with QA results and fixes
- `docs/Tests/Test 1 - Resume_Parsing/` - Added test suite and tester
- `docs/Tests/Test 3 - Document_Generation/` - Added test documents

### Key Discovery: Railway Deployment

Critical finding: Railway uses `document_generator/` module directory, NOT `backend/document_generator.py` single file. The Dockerfile line `COPY document_generator/ ./document_generator/` confirms this. Fixes must go in the module directory to take effect in production.

### Remaining Tests (Tomorrow)

Manual browser testing required:
1. **Ask Henry Context Awareness** (#5) - Page context, conversation history
2. **Mock Interview Feedback Quality** (#7) - Role relevance, coaching quality
3. **Screening Questions Analysis** (#8) - Experience grounding, honesty flags
4. **Calendar Integration** (#9) - Timezone handling, ICS file generation

### Test Results Summary

| Test Area | Result | Notes |
|-----------|--------|-------|
| Resume Parsing | 10/10 ✅ | All edge cases passed |
| Document Generation | 7/7 ✅ | Bugs fixed, verified |
| URL Extraction | Working ✅ | Captcha fix applied |
| LinkedIn Upload | 3/3 ✅ | All profiles parsed correctly |
| Error Handling | All ✅ | Proper validation errors |
| Tracker API | ✅ | CRUD + status transitions working |

---

## Session Log: January 1, 2026

### Completed Today

**1. Canonical Document System (P0 Fix) - Complete**

Fixed critical preview/download mismatch bug where preview and download showed different content.

**Root Cause:**
- Two separate data assembly paths: preview assembled from component data, download re-fetched and re-assembled
- Missing contact info in downloads
- Keyword stuffing (one keyword appearing 18+ times)
- Users re-uploading because they couldn't tell if changes helped

**Solution - Single Source of Truth:**
- New `canonical_document.py` module with ~770 lines
- One JSON object powers BOTH preview AND download (no reassembly)
- Content hash verification ensures preview === download
- Document integrity gate validates contact info before download
- Keyword deduplication (max 3 occurrences per keyword)

**Backend Changes:**
- `CanonicalDocument`, `CanonicalResume`, `CanonicalCoverLetter`, `FitScoreDelta` dataclasses
- `check_document_integrity()` - validates before download
- `deduplicate_keywords()` - caps at 3 occurrences
- `assemble_canonical_document()` - single assembly point
- New endpoint: `/api/download/canonical` with integrity checks

**Frontend Changes:**
- Preview uses `canonical_full_text` (pre-rendered)
- Download calls `/api/download/canonical` (single source)
- Job Fit Impact module with CSS
- `showFitScoreDelta()` and `lockFitScoreAtDownload()` functions

**Files Created:**
- `backend/canonical_document.py` - Core schema and assembly
- `backend/document_versioning.py` - Version tracking (~600 lines)

**Files Modified:**
- `backend/backend.py` - Canonical document assembly in `/api/documents/generate`
- `frontend/documents.html` - Canonical preview/download + fit score delta

---

**2. Strengthen Your Resume Flow - Complete**

Implemented guided remediation for resume weaknesses with constrained user inputs.

**Trust Layer Model:**
| Layer | Step | Purpose |
|-------|------|---------|
| 1. Ground Truth | Job Fit Score | High-level reality check |
| 1. Ground Truth | Resume Level Analysis | Pure diagnosis from resume |
| 2. Repair & Agency | Strengthen My Resume | Clarify, de-risk, reframe |
| 3. Augmentation | LinkedIn Profile Analysis | Optional enrichment |
| 4. Payoff | Strategy Overview | Final deliverables |

**Core Principle: Constrained Input, Guided Output**

Users CAN provide:
- Missing context that was true but not included
- Clarification of ambiguous statements
- Metrics/numbers they forgot to include

Users CANNOT:
- Invent new accomplishments
- Inflate titles or responsibilities
- Add skills they don't have
- Fabricate metrics

**Backend Implementation:**
- New `strengthen_session.py` module (~470 lines)
- `StrengthenSession`, `BulletRegeneration` dataclasses
- `validate_user_input()` with FORBIDDEN_PATTERNS
- Max 3 regenerations per bullet with audit trail
- Implausible metric thresholds (e.g., $1M+ for entry-level suspicious)

**API Endpoints:**
- `POST /api/strengthen/session` - Create session
- `GET /api/strengthen/session/{id}` - Get state
- `POST /api/strengthen/regenerate` - Generate strengthened bullet
- `POST /api/strengthen/accept` - Accept regeneration
- `POST /api/strengthen/skip` - Skip issue
- `POST /api/strengthen/complete` - Mark complete

**Files Created:**
- `backend/strengthen_session.py` - Session management
- `docs/guides/STRENGTHEN_RESUME_SPEC.md` - Full specification

---

**3. Fit Score Delta Display - Complete**

Shows before/after comparison of fit score improvements (NOT re-analysis).

**Key Design Decisions:**
- Delta calculated using SAME scoring logic as initial analysis
- Score locked at download (no gamification)
- Honest when unchanged: "Your fit score didn't change, but your resume is clearer and safer for screening."
- Shows original score, final score, and improvement summary

**Implementation:**
- `FitScoreDelta` dataclass with `delta`, `improved` properties
- `calculate_fit_score_delta()` function
- Frontend display in documents.html with CSS styling
- Score locked on "Approve & Download" click

---

**4. Resume Leveling Page - Credibility & Verifiability Section - Complete**

Added new section to resume-leveling.html after main leveling analysis.

**Three Components:**
1. **Company Credibility** - Strong/Weak/Unverifiable assessment
2. **Title Alignment** - Aligned/Inflated/Undersold evidence level
3. **Experience Relevance** (career switchers) - Direct/Adjacent/Exposure

**Data Sources (from resume_detection.py):**
- `assess_company_credibility()` → Company cards
- `detect_title_inflation()` → Title alignment cards
- `recognize_career_switcher()` → Experience relevance cards

**Files Created:**
- `backend/resume_detection.py` - Detection systems (~760 lines)

**Files Modified:**
- `frontend/resume-leveling.html` - Added CSS and `renderCredibility()` function

---

**5. Red Flag Language - Non-Accusatory Tone - Complete**

Revised all red flag messaging to be neutral and constructive.

**Language Changes:**
| Before (Accusatory) | After (Neutral) |
|---------------------|-----------------|
| "This claim appears inflated" | "We couldn't find supporting evidence for this scope" |
| "Suspicious metric" | "This metric is unusually high - can you provide context?" |
| "fabrication" | "metrics_context" |
| "flight risk" | "recruiters may question this pattern" |

**Tone Principles:**
1. Assume good faith - user may have forgotten details, not fabricated
2. Offer opportunity to clarify - "Can you help us understand..."
3. Focus on evidence gaps - "We're missing..." not "You're lying..."
4. Suggest remediation - every flag has a path forward

**Files Modified:**
- `backend/calibration/red_flag_detector.py` - Updated messaging

---

**6. Resume Language Lint System - Complete**

New module for detecting mid-market language that weakens senior signal.

**Core Test:** If a sentence can apply to 1,000 LinkedIn profiles, it fails.

**4-Tier Pattern System:**

| Tier | Name | Example Patterns | Action |
|------|------|------------------|--------|
| 1 | Kill on Sight | "results-driven", "passionate about" | Delete entirely |
| 2 | Passive/Junior-Coded | "responsible for", "helped drive" | Rewrite with ownership |
| 3 | Vague Scope Hiders | "various stakeholders", "multiple teams" | Replace with specifics |
| 4 | Exposure Without Ownership | "exposure to", "familiar with" | Remove or upgrade |

**Functions:**
- `fails_linkedin_test()` - Generic filler detection
- `fails_ownership_test()` - Passive language detection
- `fails_scope_test()` - Vague scope detection
- `fails_observer_test()` - Observer vs operator detection
- `lint_resume()` - Complete lint with structured results
- `auto_rewrite_bullet()` - Automatic rewrites for Tier 1/2

**Files Created:**
- `backend/resume_language_lint.py` (~440 lines)

---

**7. Resume Quality Gates - Complete**

Pre-submission validation to catch issues before download.

**Gate System:**
- Contact info present (required)
- Keyword frequency (max 3 per keyword)
- Quantification rate check
- Bullet length validation
- Skills relevance check

**Files Created:**
- `backend/resume_quality_gates.py` (~790 lines)

---

**8. Documentation - Complete**

Created comprehensive specification documents.

**Files Created:**
- `docs/guides/STRENGTHEN_RESUME_SPEC.md` - Full strengthen flow spec
- `docs/guides/RESUME_COVER_LETTER_CUSTOMIZATION_SPEC.md` - Customization spec
- `docs/guides/RESUME_GENERATOR_RED_FLAG_LANGUAGE_LINT.md` - Lint rules spec
- `docs/guides/RESUME_QUALITY_GATES.md` - Quality gates spec

---

### Deployment

**Commit:** `7df24f2` - feat: Implement Canonical Document System and Strengthen Resume Flow
**Merged:** To main branch with `f680255`
**Pushed:** To origin/main, triggering Vercel/Railway deployment

### Files Summary

**New Backend Modules (6 files, ~3,800 lines):**
- `backend/canonical_document.py`
- `backend/strengthen_session.py`
- `backend/resume_detection.py`
- `backend/resume_language_lint.py`
- `backend/resume_quality_gates.py`
- `backend/document_versioning.py`

**Modified Backend:**
- `backend/backend.py` - Strengthen endpoints, canonical assembly
- `backend/calibration/red_flag_detector.py` - Non-accusatory language

**Modified Frontend:**
- `frontend/documents.html` - Canonical preview/download, fit score delta
- `frontend/resume-leveling.html` - Credibility & Verifiability section

**New Documentation (4 files):**
- `docs/guides/STRENGTHEN_RESUME_SPEC.md`
- `docs/guides/RESUME_COVER_LETTER_CUSTOMIZATION_SPEC.md`
- `docs/guides/RESUME_GENERATOR_RED_FLAG_LANGUAGE_LINT.md`
- `docs/guides/RESUME_QUALITY_GATES.md`

---

## Session Log: December 25, 2025

### Completed Today

**1. Interview Debrief Intelligence (Phase 2.3) - Complete**

Implemented the full debrief intelligence loop that compounds coaching across interviews.

**Database:**
- Created `interview_debriefs` table with structured fields (questions, stumbles, wins, stories, ratings)
- Created `user_story_bank` table for tracking stories across interviews
- Added RLS policies, indexes, and auto-update triggers
- Auto-mark stories as "overused" when used 3+ times

**Backend Endpoints:**
- `POST /api/debriefs/extract` - Uses Claude to extract structured data from debrief conversations
- `POST /api/debriefs/analyze-patterns` - Cross-interview pattern analysis (weak categories, overused stories, confidence trends)
- Updated `InterviewPrepRequest` to accept `past_debriefs` for debrief-informed prep
- Updated `HeyHenryRequest` to accept `debrief_pattern_analysis` for proactive coaching

**Frontend Integration:**
- `interview-debrief.html`: On "Debrief Completed", extracts structured data and stores in Supabase
- `interview-prep.html`: Fetches past debriefs and includes in prep request
- `hey-henry.js`: Fetches pattern analysis (cached 5 min) and sends to backend
- `supabase-client.js`: Full CRUD for debriefs and story bank

**Intelligence Loop Flow:**
1. User completes interview → debriefs with Henry
2. Conversation → extraction endpoint → structured data stored
3. User preps for next interview → prep pulls past debriefs → "Last time you stumbled on X"
4. After 3+ debriefs → pattern detection → "You've struggled with behavioral questions 3 times"

**Files Created:**
- `database/interview_debriefs.sql` - Database migration

**Files Modified:**
- `backend/backend.py` - Extraction/analysis endpoints, prep integration, Hey Henry context
- `frontend/interview-debrief.html` - Extraction trigger on completion
- `frontend/interview-prep.html` - Fetches past debriefs for prep
- `frontend/components/hey-henry.js` - Pattern analysis integration
- `frontend/js/supabase-client.js` - Debrief and story bank CRUD functions

### Key Technical Details

**Debrief Extraction Prompt:**
Claude extracts: interview_type, ratings (1-5), questions_asked with categories, stumbles, wins, stories_used with effectiveness, interviewer_signals, key_insights, improvement_areas.

**Pattern Analysis (requires 3+ debriefs):**
- Weak categories: Question types where user struggled 50%+ of the time
- Strong categories: Question types where user excelled 50%+ of the time
- Story usage: Tracks which stories are overused
- Confidence trend: Improving/declining/stable based on self-ratings

**Hey Henry Prompt Injection:**
When pattern analysis is available, Hey Henry receives:
- Recurring weak areas with struggle rates
- Strengths to leverage
- Overused stories needing alternatives
- Confidence trend direction
- Coaching insights to surface proactively

### Migration Required

Run `database/interview_debriefs.sql` in Supabase SQL Editor (completed).

---

**2. Story Bank UI (Behavioral Example Library) - Complete**

Implemented the user-facing Story Bank page to surface `user_story_bank` data.

**Frontend Pages:**
- `story-bank.html` - Full Story Bank management interface

**Features:**
- Stats bar showing Total Stories, High Impact, Overused, Needs Work counts
- Story cards grid with effectiveness badges (High Impact, Overused, New, Needs Work, Retired)
- Add/Edit modal with tag input for competencies (demonstrates) and question types (best_for_questions)
- Detail view modal with full story information
- Filter buttons: All, High Impact, Needs Work, Overused
- Empty state for new users

**Navigation Integration:**
- Added Story Bank card to Interview Intelligence → Practice tab
- Added toast notification on Interview Debrief page linking to Story Bank after stories are saved

**Supabase Functions Added:**
- `updateStory(storyId, updates)` - Update story details
- `deleteStory(storyId)` - Delete a story

**Files Created:**
- `frontend/story-bank.html` - Complete Story Bank UI

**Files Modified:**
- `frontend/interview-intelligence.html` - Added Story Bank card to Practice tab
- `frontend/interview-debrief.html` - Added toast notification with Story Bank link
- `frontend/js/supabase-client.js` - Added updateStory, deleteStory functions
