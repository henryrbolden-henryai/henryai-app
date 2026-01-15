# HenryHQ Feature Roadmap & Technical Specification

## Document Purpose

This document outlines proposed feature additions and enhancements for HenryHQ. The goal is to evaluate technical feasibility, identify architectural implications, and prioritize implementation based on effort-to-impact ratio.

**Key question for each feature:** Can this be implemented without bloating the codebase or blocking other features?

---

## Product Context

### What HenryHQ Is

HenryHQ is a strategic job search intelligence platform. Unlike resume builders and mass-application tools, HenryHQ helps candidates:

1. **Assess fit before applying** - Proprietary 50/30/20 scoring (skills/experience/scope)
2. **Get honest recommendations** - Including "don't apply" when appropriate
3. **Generate zero-fabrication content** - Every word traces to actual resume data
4. **Receive complete application packages** - Resume, cover letter, interview prep, outreach templates

### What Makes It Different

- **Anti-mass-application philosophy** - Quality over quantity
- **Recruiter-built methodology** - 15+ years of executive and technical recruiting experience
- **Emotional state awareness** - Adapts guidance based on user's job search state (zen/stressed/desperate)
- **Truth over encouragement** - Honest market feedback, not cheerleading

### Current Architecture (High-Level)

- **Frontend:** Vanilla JavaScript, deployed on Vercel
- **Backend:** FastAPI with Claude API integration, deployed on Railway
- **Database:** Supabase
- **Email:** Resend with proper DNS configuration
- **Core Flow:** Resume parsing → Fit analysis → Document generation → Application tracking

---

## Feature Specifications

### Category 1: Emotional Intelligence & Adaptation

#### Feature 1: Emotional State Deepening

**Current State:** Users select their emotional state (zen/stressed/desperate) during onboarding. This data is captured but minimally utilized.

**Proposed Enhancement:** Emotional state should ripple through ALL user interactions:

| State | Behavior Modifications |
|-------|----------------------|
| **Zen** | Full data, thorough analysis, explore options, standard pacing |
| **Stressed** | Tighter guidance, prioritized actions, "focus on this one thing today," reduced cognitive load |
| **Desperate** | Survival mode, small visible wins, reframe rejections, guardrails against counterproductive behavior (e.g., mass-applying), gentler tone |

**Technical Considerations:**
- Could be implemented as prompt modifiers injected based on user state
- State stored in user profile, passed to all generation endpoints
- No new data models required
- Primarily prompt engineering + conditional logic

**Value:** High differentiation. No competitor adapts to emotional context. Job searching is emotionally brutal; acknowledging that builds trust and improves outcomes.

**Estimated Effort:** Low

---

#### Feature 2: Mid-Conversation State Detection

**Description:** Detect language patterns indicating stress/desperation shifts without requiring manual state updates.

**Trigger Patterns:**
- "nothing is working"
- "I can't do this anymore"
- "running out of money/savings"
- "been searching for X months"
- Increased use of negative language, hopelessness indicators

**Behavior:** When detected, Hey Henry adapts tone and recommendations. Could also prompt: "It sounds like things have gotten harder. Want me to adjust my approach?"

**Technical Considerations:**
- Sentiment analysis on user inputs
- Could use Claude's native understanding (prompt-based) or lightweight classifier
- Needs threshold tuning to avoid false positives
- State change could be temporary (session) or persistent (update profile)

**Value:** Proactive empathy without being performative. Catches users who wouldn't self-report state changes.

**Estimated Effort:** Medium

---

### Category 2: Job Search Intelligence

#### Feature 3: Saved Positioning Profiles

**Description:** Allow users to save multiple "versions" of themselves for different target roles.

**Example Profiles:**
- "Growth PM" - Emphasize 0-to-1, product discovery, startup experience
- "Enterprise PM" - Emphasize scale, stakeholder management, process
- "Chief of Staff" - Emphasize cross-functional leadership, exec communication

**Each Profile Contains:**
- Profile name
- Target role type
- Skills/experience to emphasize
- Skills/experience to de-emphasize
- Narrative tone (builder, operator, strategist, etc.)
- Target company characteristics (stage, size, industry)
- Saved keyword preferences

**User Flow:**
1. User creates profile(s) during setup or ad-hoc
2. When analyzing a job, user selects which profile to apply
3. All outputs (fit analysis, resume tailoring, cover letter, interview prep) inherit profile settings

**Technical Considerations:**
- New data model: `positioning_profiles` table (user_id, profile_name, settings JSON)
- Profile settings passed as context to generation prompts
- UI: Profile selector in job analysis flow
- Could start with 1-3 profile limit, expand later

**Value:** Reduces friction for users targeting multiple role types. Improves consistency. Particularly valuable for career pivoters.

**Estimated Effort:** Low-Medium

---

#### Feature 4: Rejection Intelligence Enhancement

**Current State:** Conversational debrief module exists.

**Proposed Enhancements:**

1. **Structured Hypothesis Generation**
   - After user describes rejection, generate 3 most likely reasons
   - "Based on what you told me, the most likely reasons are: [A], [B], [C]. Which feels closest?"
   - Helps users move from emotion to analysis

2. **Pattern Detection Across Rejections**
   - Track rejection data over time
   - After 3+ rejections, surface trends: "You've reached final rounds at three companies and lost each time. The common thread seems to be [X]."
   - Requires storing structured rejection data

3. **Positioning Adjustment Recommendations**
   - Based on rejection patterns, suggest specific changes
   - "For your next application in this space, here's how I'd adjust your narrative..."

4. **Feedback Request Templates**
   - Provide email templates to request feedback from recruiters
   - Optimize for actually getting responses (brief, specific, easy to answer)

**Technical Considerations:**
- New data model: `rejections` table (user_id, company, role, stage_reached, rejection_reason, date, notes)
- Pattern detection could be rule-based initially, ML later
- Mostly prompt engineering + structured data capture
- UI: Rejection logging flow, pattern visualization

**Value:** Turns painful experiences into actionable intelligence. Nobody else does this well.

**Estimated Effort:** Low-Medium

---

#### Feature 5: Job Quality Scoring / Ghost Job Detection

**Description:** Analyze job postings to warn users about potentially dead or low-quality listings.

**Signals to Analyze:**
- Posting age (>30 days = yellow flag, >60 days = red flag)
- Reposting patterns (same job reposted multiple times)
- Company hiring velocity (are they actually hiring or just collecting resumes?)
- Salary range vs. market data (lowball = red flag)
- Job description quality (vague requirements, buzzword soup)
- Glassdoor/review sentiment for the company
- Recruiter responsiveness patterns (if data available)

**Output:** Job Quality Score (Strong / Medium / Weak) with explanation

**Technical Considerations:**
- Some signals available from job description text analysis
- Other signals require external data (posting date, company data)
- Could integrate with LinkedIn API, job board APIs, or scraping (legal considerations)
- MVP: Focus on text-based signals only (description quality, salary analysis)
- Advanced: External data integration

**Value:** Saves users from wasting time on ghost jobs. Addresses real market frustration. Differentiator.

**Estimated Effort:** Medium (MVP) / High (full implementation)

---

### Category 3: Career Pivot & Translation

#### Feature 6: Industry Translation Engine (MVP)

**Description:** Help career changers translate their experience from one context to another.

**MVP Scope:** Single corridor - Government to Private Sector OR Military to Corporate

**What It Does:**
- Maps government/military titles to private sector equivalents
- Translates responsibilities into business language
- Identifies transferable skills that candidates undersell
- Provides industry-specific keyword mappings
- Suggests narrative framing for the pivot

**Example:**
- Input: "GS-14 Program Manager, Department of Defense"
- Output: "Equivalent to Senior Program Manager / Director level. Key translations: 'Stakeholder management across agencies' → 'Cross-functional leadership across business units.' 'Budget authority $50M' → 'P&L responsibility $50M.'"

**Technical Considerations:**
- Translation mappings could be stored as structured data (JSON/database)
- Prompt engineering to apply translations contextually
- Would need research to build accurate mapping tables
- Could be modular: add new corridors over time (agency→in-house, big tech→startup, etc.)

**Value:** Massively underserved market. Government and military professionals struggle to translate their experience. High willingness to pay for solutions that work.

**Estimated Effort:** High (requires domain research + implementation)

**Recommendation:** Post-launch. One corridor done well > multiple corridors done poorly.

---

### Category 4: Network & Outreach

#### Feature 7: Network Strategy Guidance

**Description:** Help users activate their network, especially those with weak networks.

**For Users WITH Networks:**
- Second-degree mapping prompts: "List 5-10 people who might know someone at your target companies"
- Warm intro request templates
- Follow-up sequences

**For Users WITHOUT Networks:**
- Alumni network activation (college, bootcamps, previous employers)
- Professional community identification (Slack groups, Discord, LinkedIn groups, associations)
- Cold outreach optimization (templates, timing, follow-up cadence)
- Networking roadmap: "Here's how to build relationships in your target industry over the next 90 days"

**Technical Considerations:**
- Mostly content/guidance (low technical lift)
- Could store user's network data if they provide it, but not required
- LinkedIn CSV import limitation: only 1st connections available
- Focus on strategy over automation for V1

**Value:** "Network is everything" but nobody operationalizes it. Even guidance-only version adds value.

**Estimated Effort:** Low-Medium

---

### Category 5: Negotiation

#### Feature 8: Negotiation Intelligence

**Description:** Help users negotiate offers effectively.

**Components:**

1. **Salary Benchmarking**
   - Compare offer to market data (Levels.fyi, Glassdoor, etc.)
   - Factor in location, company stage, years of experience

2. **Comp Structure Analysis**
   - Break down base vs. bonus vs. equity
   - Explain vesting schedules, cliff periods
   - Calculate total comp scenarios

3. **Counteroffer Scripting**
   - Generate negotiation language based on user's leverage points
   - Provide multiple options (aggressive, moderate, conservative)

4. **Competing Offer Leverage**
   - How to communicate competing offers
   - Timing strategies
   - What to reveal vs. withhold

**Technical Considerations:**
- Salary data: Could integrate external APIs or use static benchmarks
- Scripting: Prompt engineering based on offer details + user profile
- Calculator functionality for comp scenarios
- New UI flow triggered when user indicates they have an offer

**Value:** Where real money changes hands. Candidates leave thousands on the table. High-value, high-trust feature.

**Estimated Effort:** Medium

---

### Category 6: Longitudinal Career Tracking

#### Feature 9: Post-Offer Capture Flow

**Description:** When user accepts an offer, capture details for long-term tracking.

**Data to Capture:**
- Company name
- Title
- Start date
- Base salary
- Bonus structure (optional)
- Equity (optional)
- Manager name (optional)
- "What excited you most about this role?"
- "What's your 12-month goal in this position?"

**Technical Considerations:**
- New data model: `placements` table (user_id, company, title, start_date, comp_data JSON, goals, etc.)
- Trigger: User indicates offer accepted (new status in application tracker OR explicit flow)
- Simple form capture

**Value:** Foundation for all longitudinal features. Also valuable data for product analytics.

**Estimated Effort:** Low

---

#### Feature 10: Career Goal & Skills Gap Analysis

**Description:** Based on current title and stated future goal, identify skill gaps and development priorities.

**Example:**
- Current: Senior PM
- Goal: Director PM in 2 years
- Gap Analysis:
  - People management (0 reports → need 3-5)
  - Executive communication
  - P&L ownership
  - Portfolio-level thinking

**Technical Considerations:**
- Career ladder mappings (what skills differentiate each level)
- Could be stored as structured data or generated via prompts
- Personalized based on user's current experience
- Output: Skills to develop + suggested actions

**Value:** Turns HenryHQ from job search tool into career development partner.

**Estimated Effort:** Medium

---

#### Feature 11: Check-In Cadence System

**Description:** Automated check-ins at key milestones post-placement.

**Cadence:**
- 30 days: "Is the role matching expectations?"
- 90 days: "Are you learning and growing?"
- 180 days: "Career health check"
- 365 days: "One year assessment"
- 540 days (18 months): "You're in the window"

**Email Content:** Each check-in has:
- 2-3 pulse questions
- One-click response options
- Link back into HenryHQ for deeper engagement

**Technical Considerations:**
- **Requires job scheduler** (cron jobs, background workers, or external service like SendGrid automation)
- Email templates stored in system
- Track check-in responses in database
- Trigger logic based on start_date from placements table

**Value:** Maintains relationship between job searches. Dramatically increases retention and lifetime value.

**Estimated Effort:** Medium (requires scheduling infrastructure)

---

#### Feature 12: Career Health Score

**Description:** Dashboard metric showing career trajectory status.

**Score Components:**
- Skill development (self-reported + inferred)
- Role satisfaction (from check-ins)
- Comp trajectory (vs. market)
- Goal progress (vs. stated 12-month goal)
- Tenure risk (time in role vs. industry averages)

**Visualization:** Simple gauge or traffic light (Growing / Stable / At Risk)

**Technical Considerations:**
- Composite score calculated from multiple inputs
- Some inputs from check-in responses, some calculated
- Dashboard UI component
- Could trigger proactive outreach when score drops

**Value:** Makes invisible career health visible. Engagement driver.

**Estimated Effort:** Medium

---

#### Feature 13: Passive Job Market Monitoring

**Description:** Surface relevant opportunities even when user is employed and not actively searching.

**Functionality:**
- User sets "passive" status with target criteria
- System monitors job postings matching criteria
- Periodic digest: "3 Director PM roles opened at companies on your target list this month"
- No action required; awareness only

**Technical Considerations:**
- Requires job data ingestion (API integrations or scraping)
- Matching algorithm against user preferences
- Email digest system
- Storage for job postings data
- Legal/TOS considerations for job board data

**Value:** Keeps users engaged between active searches. Positions HenryHQ as always-on career radar.

**Estimated Effort:** High

---

#### Feature 14: Return Triggers

**Description:** Detect signals that user may be ready to search again and prompt re-engagement.

**Triggers:**
- Check-in responses indicating dissatisfaction
- Career health score drops below threshold
- Tenure reaches 12+ months (soft prompt)
- Tenure reaches 18+ months (stronger prompt)
- User visits site after period of inactivity
- User updates resume/profile

**Response:** Contextual outreach or in-app prompt suggesting next steps.

**Technical Considerations:**
- Event tracking for user behaviors
- Trigger rules engine (if X then Y)
- Integration with email system for outreach
- Could be simple conditional logic initially

**Value:** Proactive re-engagement increases retention. Catches users before they go elsewhere.

**Estimated Effort:** Medium

---

### Category 7: Analytics & Insight

#### Feature 15: Retrospective Analytics

**Description:** After 30+ days of activity, show users insights about their job search patterns.

**Metrics:**
- Total applications submitted
- Average fit score
- Fit score distribution (how many <70%, 70-85%, 85%+)
- Response rate by fit score tier
- Response rate by role type
- Time from application to response (average)
- Interview conversion rate

**Insight Examples:**
- "You applied to 12 roles. Roles with fit scores above 80% had 3x the response rate."
- "Your average time-to-response is 8 days. Industry average is 14 days - you're doing something right."
- "You've had the most success with Series B-C companies. Consider focusing there."

**Technical Considerations:**
- Requires structured tracking of all applications and outcomes
- Analytics calculations (could be real-time or batch)
- Dashboard visualization
- Threshold logic (only show after minimum activity)

**Value:** Proves methodology works with user's own data. Builds trust. Encourages strategic behavior.

**Estimated Effort:** Medium

---

## Summary: Prioritization Framework

### Recommended Prioritization (Impact vs. Effort)

| Priority | Feature | Impact | Effort | Notes |
|----------|---------|--------|--------|-------|
| **P0 - Now** | #1 Emotional state deepening | High | Low | Prompt modifiers, high differentiation |
| **P0 - Now** | #3 Saved positioning profiles | Med-High | Low-Med | Data model + UI, high utility |
| **P0 - Now** | #4 Rejection intelligence (enhance) | High | Low-Med | Build on existing module |
| **P1 - Phase 1.5** | #9 Post-offer capture | High | Low | Foundation for longitudinal |
| **P1 - Phase 1.5** | #10 Skills gap analysis | Med-High | Med | Career development value |
| **P1 - Phase 1.5** | #7 Network strategy guidance | Med | Low-Med | Content-driven, low lift |
| **P2 - Phase 2** | #11 Check-in cadence | High | Med | Needs scheduler infrastructure |
| **P2 - Phase 2** | #8 Negotiation intelligence | High | Med | High-value moment |
| **P2 - Phase 2** | #12 Career health score | Med | Med | Engagement driver |
| **P2 - Phase 2** | #15 Retrospective analytics | Med | Med | Proves value with data |
| **P2 - Phase 2** | #2 Mid-conversation state detection | Med | Med | Nice-to-have enhancement |
| **P3 - Phase 3** | #14 Return triggers | Med | Med | Retention optimization |
| **P3 - Phase 3** | #5 Ghost job detection | Med-High | Med-High | External data complexity |
| **P3 - Phase 3** | #6 Industry translation (MVP) | High | High | High value but high lift |
| **P3 - Phase 3** | #13 Passive job monitoring | Med | High | External data + infrastructure |

---

## Questions for Technical Review

1. **Data Models:** Which features require new tables vs. extending existing ones?

2. **Prompt Engineering vs. Code:** Which features can be achieved primarily through prompt modifications vs. requiring new backend logic?

3. **Infrastructure Additions:** 
   - Do we have job scheduling capability for check-in cadences?
   - What's the lift to add background workers?

4. **External Integrations:** 
   - What's the feasibility of job board API integrations for passive monitoring?
   - Any existing salary data integrations we could leverage?

5. **Feature Flags:** Can we implement features behind flags for gradual rollout?

6. **Performance Implications:** Any features that could significantly impact response times or database load?

7. **Dependencies:** Are there features that should be built together or in a specific sequence?

---

## Success Metrics

For each feature, we should define success metrics before building:

- **Emotional state deepening:** User satisfaction scores, support ticket volume
- **Saved positioning profiles:** % of users with 2+ profiles, application completion rate
- **Rejection intelligence:** User return rate after rejection, time to next application
- **Longitudinal tracking:** 90-day retention, 180-day retention, return user rate
- **Negotiation intelligence:** Reported salary lift, user satisfaction

---

*Document Version: 1.0*
*Created: December 2024*
*For: Claude Code Technical Review*
