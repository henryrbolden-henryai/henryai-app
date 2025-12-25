# STRATEGIC INTELLIGENCE ENGINE SPECIFICATION v1.0

**Date:** December 25, 2025
**Status:** DRAFT - Ready for Review
**Purpose:** Phase 2 implementation guide for longitudinal intelligence features
**Dependencies:** Phase 1.5 Conversation History Persistence

---

## EXECUTIVE SUMMARY

This document specifies the Strategic Intelligence Engine, a Phase 2 enhancement that transforms Hey Henry from a point-in-time advisor into a longitudinal strategic partner. These features enable Hey Henry to see patterns across the candidate's entire job search, remember history, compound insights over time, and proactively surface opportunities.

**Core Principle:** The top 0.01% of candidates don't need another tool. They need a strategic partner who knows their full history, sees patterns they miss, and gets smarter about them over time.

**Key Features:**
1. Proactive Network Surfacing
2. Pipeline Pattern Analysis
3. Interview Debrief Compounding
4. Rejection Forensics
5. Negotiation Intelligence
6. Second-Degree Path Suggestions
7. Outreach Tracking and Follow-Up

---

## DEPENDENCIES

Before implementing Phase 2, the following Phase 1.5 features must be complete:

| Dependency | Status | Why Required |
|------------|--------|--------------|
| Conversation History Persistence | Phase 1.5 | Foundation for all longitudinal features |
| LinkedIn CSV Upload | Complete | Required for network surfacing |
| Pipeline Tracking | Complete | Required for pattern analysis |
| Interview Debrief | Phase 1.5 | Required for compounding debriefs |

---

## 2.1 PROACTIVE NETWORK SURFACING

### Problem
LinkedIn connection data exists but is siloed on the Outreach page. Users must navigate there manually. Elite candidates expect their advisor to surface relevant connections automatically.

### Solution
Integrate network intelligence into the core analysis flow. When a candidate analyzes a role, Hey Henry automatically checks their uploaded connections and surfaces relevant paths.

### Trigger
- User analyzes a new role
- LinkedIn CSV has been uploaded to profile

### Behavior

**When direct connections exist:**

```
"You have 2 first-degree connections at [Company]:

* Sarah Chen, Senior PM (connected since March 2019)
* Mike Torres, Engineering Manager (connected since January 2022)

Sarah's the stronger path. She's in the same department as this role. Want me to draft outreach?"
```

**When no direct connections exist:**

```
"No direct connections at [Company], but your network has options:

* David Park at Uber used to work at [Company] (2019-2022). He might know the team.
* You have 3 connections in [Industry] who could provide intel on the company culture.

Want me to draft a message to David asking for an intro?"
```

### Data Requirements
- Store parsed LinkedIn CSV in Supabase per user
- Match company names (fuzzy matching for variations: "Google" = "Google LLC" = "Alphabet")
- Surface connection date to indicate relationship strength
- Cross-reference job titles to identify relevant connections (same department, similar role)

### Database Schema

```sql
-- Already exists, may need enhancement
CREATE TABLE linkedin_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    first_name TEXT,
    last_name TEXT,
    company TEXT,
    company_normalized TEXT, -- For fuzzy matching
    position TEXT,
    connected_on DATE,
    email TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast company lookups
CREATE INDEX idx_connections_company ON linkedin_connections(company_normalized);
CREATE INDEX idx_connections_user ON linkedin_connections(user_id);
```

### UI Integration
- Add "Network Intelligence" card to analysis results (after fit score, before documents)
- Include in Hey Henry's conversational response
- Link to full Outreach page for deeper exploration

### Success Criteria
- Connections surfaced within 2 seconds of analysis completion
- Fuzzy company matching catches 90%+ of variations
- Users can draft outreach directly from analysis flow

---

## 2.2 PIPELINE PATTERN ANALYSIS

### Problem
Hey Henry evaluates roles one at a time. A great career coach sees patterns across the entire search and provides strategic feedback.

### Solution
Analyze the candidate's full pipeline to identify patterns, tendencies, and strategic gaps.

### Triggers
- User has 5+ applications in pipeline
- User asks "How's my search going?" or similar
- Weekly proactive check-in (if enabled)

### Analysis Dimensions

| Dimension | What to Track | Insight Example |
|-----------|---------------|-----------------|
| Fit distribution | % of apps that were Strong/Moderate/Reach/Long Shot | "8 of your 12 applications were reaches. You're consistently overreaching on scope." |
| Stage conversion | % that advance past each stage | "You're getting to final rounds but not converting. Something's happening in those late-stage conversations." |
| Company patterns | Types of companies applied to (stage, size, industry) | "Every role you've marked 'excited about' is at a Series B company. That's your sweet spot." |
| Role patterns | Seniority, function, scope | "You're applying to both IC and management roles. Pick a lane or your narrative gets muddy." |
| Timeline | Velocity of applications, response times | "You applied to 8 roles last week but only 2 this week. Momentum stalling?" |
| Red flags | Repeated patterns in rejections or ghosting | "Three rejections at the same stage. Either the market's saturated or your story isn't landing." |

### Output Format

```
"Here's what I'm seeing across your search:

Pipeline Health: 12 applications, 3 active, 2 interviews scheduled, 4 rejected, 3 ghosted

Patterns:
* You're overreaching on scope. 8 of 12 were stretch roles.
* Strong conversion to first round (67%), but dropping off at hiring manager stage (25%).
* All your ghosted applications were at companies with 50+ open roles. They're probably overwhelmed.

Recommendation: Tighten your targeting to roles where you're a 75%+ fit. Your hit rate will improve."
```

### Data Requirements
- Aggregate pipeline data per user
- Track stage progression timestamps
- Calculate conversion rates by stage
- Identify company and role clustering

### Database Schema

```sql
-- Enhancement to existing applications table
ALTER TABLE applications ADD COLUMN IF NOT EXISTS
    fit_score_at_application INTEGER,
    company_size TEXT,
    company_stage TEXT,
    role_seniority TEXT,
    role_function TEXT;

-- Analytics view for pattern analysis
CREATE VIEW pipeline_analytics AS
SELECT 
    user_id,
    COUNT(*) as total_applications,
    AVG(fit_score_at_application) as avg_fit_score,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejections,
    COUNT(*) FILTER (WHERE status = 'ghosted') as ghosted,
    COUNT(*) FILTER (WHERE status = 'interviewing') as active_interviews,
    COUNT(*) FILTER (WHERE fit_score_at_application >= 80) as strong_fits,
    COUNT(*) FILTER (WHERE fit_score_at_application < 60) as reaches
FROM applications
GROUP BY user_id;
```

### Success Criteria
- Pattern analysis available after 5+ applications
- Insights are specific and actionable (not generic)
- Users report "I didn't notice that" reaction

---

## 2.3 INTERVIEW DEBRIEF COMPOUNDING

### Problem
Current interview debrief spec evaluates single interviews in isolation. Elite candidates need coaching that builds on previous sessions and identifies recurring patterns.

### Solution
Track interview performance across multiple debriefs and surface compounding insights.

### Triggers
- User submits second or subsequent interview transcript
- User asks "What patterns do you see in my interviews?"

### Compounding Analysis

| Pattern Type | Detection Method | Coaching Example |
|--------------|------------------|------------------|
| Answer length | Average word count per response | "Your STAR answers are too long. Across 4 interviews, you averaged 3 minutes per answer. Cut to 90 seconds." |
| Weak question types | Track ratings by question category | "This is the third time you've stumbled on 'why this company' questions. Let's fix that permanently." |
| Filler words | Count "um," "like," "you know" | "Your filler word usage is up 40% from your first interview. Nerves or fatigue?" |
| Story repetition | Track which examples are used | "You've used the 'Uber launch' story in 3 interviews. Time to expand your repertoire." |
| Confidence trajectory | Track confidence ratings over time | "Your confidence has improved from 2.5 to 4.0 over 6 interviews. The prep is working." |

### Output Format

```
"Across your last 4 interviews, here's what I'm seeing:

Strengths (consistent):
* Technical depth is strong. You scored 4+ on every technical question.
* You're great at building rapport in the first 5 minutes.

Patterns to fix:
* 'Why this company?' is still your weak spot. 3 of 4 interviewers noted a generic answer.
* You're rushing through your closing questions. Take more time there.

Improvement trajectory:
* Confidence: 2.5 -> 4.0 (significant improvement)
* Structure: 3.0 -> 3.5 (moderate improvement)
* Conciseness: 3.5 -> 3.0 (regression, answers getting longer)

Focus for next interview: Nail the 'why this company?' question. I can help you prep a specific answer for [Company]."
```

### Database Schema

```sql
CREATE TABLE interview_debriefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    application_id UUID REFERENCES applications(id),
    interview_date DATE,
    interview_type TEXT, -- 'recruiter', 'hiring_manager', 'technical', 'final'
    transcript TEXT,
    
    -- Ratings (1-5 scale)
    rating_content INTEGER,
    rating_clarity INTEGER,
    rating_delivery INTEGER,
    rating_tone INTEGER,
    rating_structure INTEGER,
    rating_confidence INTEGER,
    
    -- Analysis
    strengths JSONB,
    opportunities JSONB,
    stories_used TEXT[],
    question_categories_weak TEXT[],
    filler_word_count INTEGER,
    avg_answer_length_seconds INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for user lookups
CREATE INDEX idx_debriefs_user ON interview_debriefs(user_id);
```

### Success Criteria
- Compounding insights available after 2+ debriefs
- Identifies at least one recurring pattern per user
- Users can see improvement trajectory over time

---

## 2.4 REJECTION FORENSICS

### Problem
When candidates get rejected, they rarely know why. Hey Henry should help them learn from each rejection and identify systemic issues.

### Solution
Analyze rejection patterns to provide diagnostic insights and strategic adjustments.

### Triggers
- User marks application as "Rejected"
- User asks "Why do I keep getting rejected?"

### Forensic Analysis by Stage

| Rejection Stage | Likely Cause | Hey Henry Response |
|-----------------|--------------|-------------------|
| Resume screen | Keywords, experience match, ATS | "Rejected at resume screen. Your materials might be missing key terms, or the role was more senior than your background signals." |
| Recruiter screen | Communication, salary expectations, timeline | "Rejected after recruiter call. Common causes: salary mismatch, timeline issues, or red flags in how you presented. What did they ask about?" |
| Hiring manager | Culture fit, scope concerns, team dynamics | "Rejected after hiring manager round. This usually means culture fit or scope concerns, not skills. Did anything feel off in the conversation?" |
| Final round | Competition, internal candidate, budget | "Rejected at final round. You were qualified enough to get there. This is often about competition or factors outside your control. Did they give any feedback?" |
| Offer stage | Negotiation, references, background | "Rejected after offer? That's rare. Usually references or background check. Did anything surface there?" |

### Pattern Detection

```
"You've been rejected 4 times in the last month. Here's what I'm seeing:

* 2 rejections at resume screen -> Your materials might need refinement for these role types
* 1 rejection at recruiter screen -> Salary expectations were misaligned (you mentioned this)
* 1 rejection at final round -> Competition, not qualification

The resume screen rejections are the signal. Both were at enterprise SaaS companies where you don't have direct experience. Either sharpen your positioning for that sector or focus on companies where your background is a clearer fit."
```

### Systemic Issue Detection

| Pattern | Insight |
|---------|---------|
| Same company, multiple rejections | "Two rejections at [Company], different roles. Might be a systemic issue with how you're presenting, or they've flagged your profile." |
| Same stage, multiple rejections | "Three rejections at hiring manager stage. Something's happening in those conversations that's not working." |
| Same role type, multiple rejections | "Rejected from 4 Senior PM roles. The market might be telling you that's not where you're competitive right now." |

### Database Schema

```sql
-- Enhancement to existing applications table
ALTER TABLE applications ADD COLUMN IF NOT EXISTS
    rejection_stage TEXT, -- 'resume', 'recruiter', 'hiring_manager', 'final', 'offer'
    rejection_reason TEXT,
    rejection_feedback TEXT,
    rejected_at TIMESTAMP;

-- View for rejection analysis
CREATE VIEW rejection_analytics AS
SELECT 
    user_id,
    rejection_stage,
    COUNT(*) as count,
    array_agg(company) as companies,
    array_agg(role_title) as roles
FROM applications
WHERE status = 'rejected'
GROUP BY user_id, rejection_stage;
```

### Success Criteria
- Forensic analysis provided within 24 hours of rejection logged
- Pattern detection after 3+ rejections
- Users report insights they hadn't considered

---

## 2.5 NEGOTIATION INTELLIGENCE

### Problem
Hey Henry stops at "here's the typical salary range." Elite candidates need company-specific negotiation intel and tactical guidance.

### Solution
Provide negotiation intelligence based on company patterns, role context, and market dynamics.

### Triggers
- User receives offer
- User asks about negotiation strategy
- User reaches final round (proactive prep)

### Intelligence Layers

**Layer 1: Company Patterns**

```
"[Company] negotiation intel:

* They typically lowball first offers by 15-20%. Counter expected.
* Sign-on bonuses are easier to negotiate than base salary.
* They move fast once you have an offer. Expect 48-72 hour pressure.
* Glassdoor reviews mention rigid leveling. If you're borderline, push for the higher level now."
```

**Layer 2: Role Context**

```
"This is a backfill role (the last person left). That gives you leverage:

* They need someone quickly
* The budget is already approved
* They've already invested in the interview process

Use this to negotiate timeline and comp."
```

**Layer 3: Market Dynamics**

```
"Market context for this role:

* [Function] hiring is down 23% YoY in [Industry]
* Average time-to-fill for this role type: 45 days
* Competing offers are your strongest leverage right now

If you have other offers, mention them early. If you don't, don't bluff."
```

### Tactical Guidance

```
"Negotiation playbook for [Company]:

1. Thank them, express enthusiasm, ask for 48 hours to review
2. Come back with a counter 15-20% above their offer
3. Focus on: base salary first, then sign-on, then equity
4. If they say 'final offer,' ask about sign-on or start date flexibility
5. Get everything in writing before giving notice

Want me to draft your counter-offer language?"
```

### Data Requirements
- Aggregate negotiation patterns by company (from user reports, Glassdoor, Levels.fyi)
- Track offer outcomes for HenryHQ users (anonymized)
- Identify role type (backfill vs. new headcount) from job posting signals
- Market data on hiring velocity by function and industry

### Database Schema

```sql
CREATE TABLE company_negotiation_intel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT,
    company_normalized TEXT,
    
    -- Patterns
    typical_lowball_percentage INTEGER,
    negotiation_flexibility TEXT, -- 'high', 'medium', 'low', 'rigid'
    easiest_to_negotiate TEXT[], -- ['sign_on', 'equity', 'title', 'start_date']
    decision_pressure_days INTEGER,
    
    -- Metadata
    data_points INTEGER, -- How many reports this is based on
    last_updated TIMESTAMP,
    source TEXT, -- 'user_reports', 'glassdoor', 'levels_fyi'
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE offer_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    application_id UUID REFERENCES applications(id),
    
    initial_offer_base INTEGER,
    initial_offer_equity INTEGER,
    initial_offer_sign_on INTEGER,
    
    final_offer_base INTEGER,
    final_offer_equity INTEGER,
    final_offer_sign_on INTEGER,
    
    negotiation_tactics_used TEXT[],
    outcome TEXT, -- 'accepted', 'declined', 'rescinded'
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Success Criteria
- Company-specific intel for Fortune 500 and major tech companies
- Tactical playbook customized to offer details
- Users report higher confidence in negotiation conversations

---

## 2.6 SECOND-DEGREE PATH SUGGESTIONS

### Problem
Users often don't have direct connections at target companies. Elite networkers leverage second-degree paths through mutual connections.

### Solution
Analyze LinkedIn connection work history to identify potential introduction paths.

### Triggers
- User analyzes role at company with no first-degree connections
- User asks "How can I get an intro to [Company]?"

### Path Analysis

```
"No direct connections at [Company], but I found potential paths:

Path 1 (Strongest):
* David Park (your connection at Uber) worked at [Company] 2019-2022
* He was in the same department as this role
* Approach: Ask David for intel on the team and a potential intro

Path 2 (Industry Intel):
* Sarah Chen (your connection at Stripe) is in the same function
* She might know people at [Company] or have insights on their culture
* Approach: Ask Sarah if she knows anyone there

Path 3 (Alumni Network):
* You and the hiring manager both went to [University]
* Approach: Lead with the shared background in your cold outreach

Want me to draft a message to David?"
```

### Data Requirements
- Parse LinkedIn CSV for work history (if available in export)
- Alternatively, prompt user to enrich key connections with past companies
- Match past companies to target company
- Identify shared backgrounds (schools, past employers, industries)

### Implementation Note

LinkedIn CSV exports don't include full work history. Options:

1. **Manual enrichment:** Prompt users to flag "key connections" and add their backgrounds
2. **Guided discovery:** Hey Henry asks "Do you know anyone who used to work at [Company]?"
3. **Future integration:** LinkedIn API partnership (long-term)

### Database Schema

```sql
-- Enhancement to linkedin_connections
ALTER TABLE linkedin_connections ADD COLUMN IF NOT EXISTS
    past_companies TEXT[],
    school TEXT,
    enriched_at TIMESTAMP;

-- Key connections table for manual enrichment
CREATE TABLE key_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    connection_id UUID REFERENCES linkedin_connections(id),
    
    past_companies TEXT[],
    school TEXT,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Success Criteria
- Surface at least one potential path for 60%+ of target companies
- Users report successful intros through suggested paths
- Path quality rated by users

---

## 2.7 OUTREACH TRACKING AND FOLLOW-UP

### Problem
Users reach out to connections but don't track responses or follow up systematically. Opportunities slip through the cracks.

### Solution
Track outreach attempts and prompt strategic follow-ups.

### Triggers
- User sends outreach (logged manually or via integration)
- 5 days pass with no logged response
- User asks "Did I follow up with [Person]?"

### Tracking Flow

1. User drafts outreach via Hey Henry
2. Hey Henry asks: "Did you send this? I'll track it for follow-up."
3. User confirms send
4. Hey Henry logs: Contact, Company, Date Sent, Channel (LinkedIn/Email)
5. After 5 days, Hey Henry prompts:

```
"You reached out to Sarah at Stripe 5 days ago. No response logged yet.

Options:
* Draft a gentle follow-up (recommended)
* Mark as 'No Response' and move on
* She responded (let me update the log)

Want me to draft the follow-up?"
```

### Follow-Up Templates

**Gentle bump (5 days):**
```
"Hi Sarah, wanted to bump this in case it got buried. I know things get busy. Still very interested in learning more about the [Role] opportunity at [Company]. Happy to work around your schedule."
```

**Final follow-up (10 days):**
```
"Hi Sarah, following up one more time. If now isn't a good time, no worries at all. I'll keep an eye on opportunities at [Company] and reach out if something else comes up. Thanks for considering!"
```

### Dashboard View

| Contact | Company | Sent | Channel | Status | Next Action |
|---------|---------|------|---------|--------|-------------|
| Sarah Chen | Stripe | Dec 20 | LinkedIn | No response | Follow up due |
| Mike Torres | Uber | Dec 18 | Email | Responded | Schedule call |
| David Park | Google | Dec 22 | LinkedIn | Pending | Wait 3 more days |

### Database Schema

```sql
CREATE TABLE outreach_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    application_id UUID REFERENCES applications(id), -- Optional, if tied to specific app
    
    contact_name TEXT NOT NULL,
    contact_title TEXT,
    company TEXT NOT NULL,
    channel TEXT NOT NULL, -- 'linkedin', 'email', 'text', 'other'
    
    message_content TEXT,
    sent_at TIMESTAMP NOT NULL,
    
    status TEXT DEFAULT 'pending', -- 'pending', 'responded', 'no_response', 'meeting_scheduled'
    response_date TIMESTAMP,
    response_notes TEXT,
    
    follow_up_count INTEGER DEFAULT 0,
    last_follow_up_at TIMESTAMP,
    next_follow_up_due TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for follow-up queries
CREATE INDEX idx_outreach_followup ON outreach_log(user_id, status, next_follow_up_due);
```

### Hey Henry Integration

**After drafting outreach:**
```
"Here's your message to Sarah. Want me to track this for follow-up?

[Yes, I'll send it now] [No, just drafting]"
```

**Follow-up prompt (proactive):**
```
"Quick check-in: You have 2 outreach messages due for follow-up:

* Sarah Chen at Stripe (sent 5 days ago)
* Mike Torres at Uber (sent 7 days ago)

Want me to draft follow-ups for both?"
```

### Success Criteria
- Users log 80%+ of outreach attempts
- Follow-up prompts sent within 24 hours of due date
- Users report fewer "forgot to follow up" situations

---

## IMPLEMENTATION PRIORITY

| Feature | Complexity | Impact | Priority | Dependencies |
|---------|------------|--------|----------|--------------|
| 2.1 Proactive Network Surfacing | Medium | High | P1 | LinkedIn CSV (complete) |
| 2.2 Pipeline Pattern Analysis | Medium | High | P1 | Pipeline tracking (complete) |
| 2.4 Rejection Forensics | Low | Medium | P2 | Pipeline tracking (complete) |
| 2.7 Outreach Tracking | Low | Medium | P2 | None |
| 2.3 Interview Debrief Compounding | Medium | Medium | P2 | Interview debrief (Phase 1.5) |
| 2.5 Negotiation Intelligence | High | High | P3 | External data sources |
| 2.6 Second-Degree Path Suggestions | High | Medium | P3 | LinkedIn enrichment strategy |

### Recommended Sequence

1. **Foundation:** Ship Conversation History Persistence (Phase 1.5)
2. **Quick wins:** Build Pipeline Pattern Analysis (uses existing data)
3. **Integration:** Add Proactive Network Surfacing (uses existing LinkedIn CSV)
4. **Low lift, high value:** Add Rejection Forensics and Outreach Tracking
5. **Compound value:** Build Interview Debrief Compounding (requires multiple sessions)
6. **External data:** Scope Negotiation Intelligence (needs data sources)
7. **Long-term:** Explore Second-Degree Paths (needs LinkedIn enrichment strategy)

---

## TESTING CHECKLIST

### 2.1 Proactive Network Surfacing
- [ ] Connections surface automatically after role analysis
- [ ] Fuzzy company matching works (Google = Google LLC)
- [ ] "No connections" path shows alternative suggestions
- [ ] Outreach can be drafted from analysis flow
- [ ] Connection date displayed correctly
- [ ] Relevant connections prioritized (same department/function)

### 2.2 Pipeline Pattern Analysis
- [ ] Analysis available after 5+ applications
- [ ] Fit distribution calculated correctly
- [ ] Stage conversion rates accurate
- [ ] Company/role clustering identified
- [ ] Patterns are specific, not generic
- [ ] Recommendations are actionable

### 2.3 Interview Debrief Compounding
- [ ] Second debrief references first
- [ ] Recurring patterns identified
- [ ] Improvement trajectory shown
- [ ] Story repetition tracked
- [ ] Question category weaknesses flagged
- [ ] Coaching recommendations compound

### 2.4 Rejection Forensics
- [ ] Stage-appropriate analysis provided
- [ ] Pattern detection after 3+ rejections
- [ ] Systemic issues flagged
- [ ] Company-specific patterns identified
- [ ] Actionable recommendations provided

### 2.5 Negotiation Intelligence
- [ ] Company-specific intel for major employers
- [ ] Role context (backfill vs. new headcount) detected
- [ ] Market dynamics incorporated
- [ ] Tactical playbook generated
- [ ] Counter-offer language drafted

### 2.6 Second-Degree Paths
- [ ] Alumni connections identified
- [ ] Past employer overlap detected
- [ ] Industry connections suggested
- [ ] Path strength ranked
- [ ] Outreach drafted for suggested path

### 2.7 Outreach Tracking
- [ ] Outreach logged on send confirmation
- [ ] Follow-up prompts at 5 days
- [ ] Status updates tracked correctly
- [ ] Dashboard view accurate
- [ ] Multiple channels supported
- [ ] Follow-up templates generated

---

## ANTI-PATTERNS

### Generic Insights (NEVER)

**BAD:**
```
"You have some applications in your pipeline. Keep applying!"
```

**GOOD:**
```
"8 of your 12 applications were reaches. You're overreaching on scope. Tighten targeting to 75%+ fit roles."
```

### Isolated Analysis (NEVER)

**BAD:**
```
"This interview went okay. Here are some tips."
```

**GOOD:**
```
"This is the third time you've stumbled on 'why this company?' Let's fix that permanently."
```

### Passive Tracking (NEVER)

**BAD:**
```
"You can log your outreach in the dashboard."
```

**GOOD:**
```
"Did you send this? I'll track it and remind you to follow up in 5 days if you don't hear back."
```

---

## SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Pattern insights surfaced | 100% of users with 5+ apps | Automated |
| Network connections surfaced | 80% of analyses (when CSV uploaded) | Automated |
| Outreach follow-up rate | 70% of logged outreach gets follow-up | Automated |
| User-reported "aha moments" | 4+ per active user per month | Survey |
| Interview improvement trajectory | Positive trend after 3+ debriefs | Calculated |
| Rejection pattern identification | 90% of users with 3+ rejections | Automated |

---

## NOTES FOR IMPLEMENTATION

### Critical Rules

1. **Always use correct grammar and punctuation**
2. **Never use em dashes** (use colons, commas, periods instead)
3. **Spec is source of truth** (code follows spec)
4. **Test before deploy** (use full checklist)
5. **Insights must be specific** (no generic advice)
6. **Patterns require data** (don't surface patterns without sufficient data points)

### When Stuck

1. Ask: "Would a great career coach say this?"
2. Check: "Is this insight specific to THIS candidate?"
3. Verify: "Do I have enough data to make this claim?"
4. Default: Show data, let candidate draw conclusions

### Data Privacy

- All pattern analysis is per-user only
- Aggregated company intel is anonymized
- Users can delete their data at any time
- No sharing of individual user data across accounts

---

## RELATED DOCUMENTS

- HEY_HENRY_IMPLEMENTATION_SPEC_v2.1.md (Phase 1 and 1.5)
- CONVERSATION_HISTORY_SPEC.md (Phase 1.5 dependency)
- outreach.html (existing networking intelligence UI)

---

**END OF STRATEGIC INTELLIGENCE ENGINE SPECIFICATION**

This document is ready for Claude Code review and implementation planning. All behavioral requirements, database schemas, testing procedures, and implementation priorities are included.
