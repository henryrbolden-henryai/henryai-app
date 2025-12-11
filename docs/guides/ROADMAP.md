# HenryAI Product Roadmap

**Last Updated:** December 11, 2025

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

**Status:** Partially Complete

Enhances decision-making with market intelligence and broader career positioning.

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

### LinkedIn Optimization

- **LinkedIn Profile Score** - 0-100 rating with specific fixes
- **LinkedIn Optimization Module** - Rewrite headline, About, bullets, skills for visibility
- **LinkedIn Network Intelligence** ✅ (Partial) - Search queries for hiring managers/recruiters

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
| Phase 1.75: Engagement & Coaching | In Progress | ~50% |
| Phase 2: Strategic Intelligence | Partial | ~30% |
| Phase 3: Performance Intelligence | Partial | ~20% |
| Phase 4: Distribution & Ecosystem | Not Started | 0% |
| Phase 5: Monetization & Scale | Not Started | 0% |

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
