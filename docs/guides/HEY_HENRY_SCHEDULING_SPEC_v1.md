# HEY HENRY SCHEDULING & PRE-CALL BRIEFING SPECIFICATION v1.0

**Date:** December 25, 2025
**Status:** DRAFT - Phase 2 Feature
**Purpose:** Native scheduling for coaching calls with automated pre-call intelligence
**Dependencies:** Conversation History Persistence (Complete), Pipeline Tracking (Complete)

---

## EXECUTIVE SUMMARY

This document specifies Hey Henry's native scheduling capability, enabling candidates to book coaching calls directly within the chat interface. The key differentiator is automated pre-call briefing generation: when someone books time, the coach receives a comprehensive intelligence package before the call.

**User Problem:**
Candidates want to speak with a human coach for complex situations (negotiation strategy, career pivots, repeated final-round failures). Currently, this requires:
1. Leaving HenryHQ to book via Calendly
2. Manually filling out intake forms
3. Coach has no context on the candidate's history

**Solution:**
Hey Henry handles scheduling natively. The candidate never leaves the interface, and the coach gets full context automatically.

**Core Value Proposition:**
- For candidates: Frictionless booking without context loss
- For coaches: Pre-call briefing with complete candidate intelligence
- For HenryHQ: Keeps users in-product, proves Hey Henry's value

---

## USER STORIES

### Candidate Perspective

**Story 1: Booking a Call**
> "I've been stuck at the final round for 3 companies. I want to talk to someone about what's going wrong."

Hey Henry response:
```
"That pattern is worth digging into. I can help with prep, but talking through it with a coach might surface something I'm missing.

Want to schedule 30 minutes? I'll brief them on your interview history so you don't have to repeat yourself."

[View Available Times]
```

**Story 2: Pre-Call Confirmation**
> User selects Thursday at 2pm

Hey Henry response:
```
"Done. You're booked for Thursday, December 28 at 2:00 PM EST with [Coach Name].

I'll send them your application history, interview debriefs, and the patterns I've spotted. They'll come prepared.

You'll get a calendar invite and a reminder 1 hour before. Anything specific you want me to flag for them?"
```

**Story 3: Adding Context**
> "Yeah, I want to talk about whether I should even be targeting these roles or if I need to adjust my search."

Hey Henry response:
```
"Got it. I'll flag that you're questioning role targeting, not just interview technique. That changes the conversation.

See you Thursday. In the meantime, want to review your pipeline together?"
```

---

### Coach Perspective

**Story 4: Receiving Pre-Call Briefing**
> Coach opens HenryHQ admin 15 minutes before call

**Pre-Call Briefing (Auto-Generated):**

```
PRE-CALL BRIEFING
Candidate: [Name]
Call: Thursday, December 28 at 2:00 PM EST (30 min)
Coach: [Coach Name]

─────────────────────────────────────────

CANDIDATE SNAPSHOT
- Current role: Senior PM at [Company] (3 years)
- Target: Director-level PM roles at Series B-D startups
- Search duration: 4 months active
- Profile strength: 85/100

─────────────────────────────────────────

PIPELINE SUMMARY (Last 30 Days)
- Applications: 12
- Average fit score: 78%
- Interviews: 8
- Final rounds: 3
- Offers: 0

Companies in pipeline:
• Stripe (Final Round - No decision yet)
• Notion (HM Round - Scheduled next week)
• Figma (Rejected after final)
• Linear (Rejected after HM)

─────────────────────────────────────────

PATTERN ANALYSIS

Concerning patterns:
• Final round conversion: 0/3 (0%) - significantly below average
• Consistent feedback gap: "Great skills, not sure about culture fit"
• Story repetition: Uber launch story used in 6/8 interviews

Positive patterns:
• Strong recruiter screen pass rate: 100%
• Technical rounds: 4/4 passed
• Fit scores improving over time (started at 65%, now averaging 82%)

─────────────────────────────────────────

INTERVIEW DEBRIEF HIGHLIGHTS

Figma Final Round (Dec 18):
- Self-rating: 3/5
- Stumbled on: "Why Figma specifically" and leadership style questions
- Hey Henry note: "Answer felt generic. Didn't connect personal motivation to company mission."

Linear HM Round (Dec 12):
- Self-rating: 4/5
- Felt good but rejected
- Interviewer seemed engaged but asked repeated clarifying questions about team size managed

─────────────────────────────────────────

CANDIDATE'S STATED GOAL FOR THIS CALL
"Questioning whether I should even be targeting these roles or if I need to adjust my search."

─────────────────────────────────────────

HEY HENRY'S HYPOTHESIS
The candidate has the skills (passing technical rounds) but is losing on "fit" signals in final rounds. Possible causes:
1. Story selection not tailored to company values
2. "Why this company" answers feel transactional
3. Leadership narrative may not match Director-level expectations

Suggested focus: Help candidate articulate a compelling "why" narrative and assess whether Director targeting is premature or just poorly positioned.

─────────────────────────────────────────

QUICK LINKS
• Full application history: [Link]
• Interview debriefs: [Link]
• Hey Henry conversation history: [Link]
• Resume: [Link]
```

---

## USER FLOWS

### Flow 1: Candidate-Initiated Booking

```
┌─────────────────────────────────────────────────────────┐
│ 1. Candidate asks Hey Henry about booking              │
│    "Can I talk to someone about my search?"            │
│    "I want to schedule time with a coach"              │
│    "Is there a human I can speak with?"                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Hey Henry confirms intent and explains value        │
│    - Acknowledges the request                          │
│    - Explains what the call can cover                  │
│    - Notes that briefing will be auto-generated        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Hey Henry shows available slots                     │
│    - Inline calendar picker (next 7 days)              │
│    - 30-minute slots by default                        │
│    - Timezone auto-detected                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Candidate selects time                              │
│    - Click to select                                   │
│    - Confirmation prompt                               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Hey Henry asks for context (optional)               │
│    "Anything specific you want me to flag for them?"   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Booking confirmed                                   │
│    - Calendar event created                            │
│    - Confirmation email sent                           │
│    - Pre-call briefing generation queued               │
└─────────────────────────────────────────────────────────┘
```

### Flow 2: Hey Henry-Initiated Suggestion

```
┌─────────────────────────────────────────────────────────┐
│ TRIGGERS (Hey Henry suggests a call)                   │
│                                                        │
│ • 3+ final round rejections without clear cause        │
│ • Negotiation situation (offer received)               │
│ • Career pivot consideration                           │
│ • Emotional state: crushed or desperate (sustained)    │
│ • User explicitly expresses need for human support     │
│ • Complex situation beyond Hey Henry's scope           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Hey Henry offers scheduling naturally                  │
│                                                        │
│ "This might be worth talking through with a coach.     │
│ I can prep them on your history so you don't have to   │
│ start from scratch. Want to book 30 minutes?"          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                   [Same flow as above]
```

### Flow 3: Pre-Call Briefing Generation

```
┌─────────────────────────────────────────────────────────┐
│ TRIGGER: Booking confirmed                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Gather candidate data                               │
│    - Profile snapshot                                  │
│    - Application history (last 30 days)                │
│    - Interview debriefs                                │
│    - Hey Henry conversation history                    │
│    - Pattern analysis from Strategic Intelligence      │
│    - Candidate's stated goal for call                  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Generate briefing via Claude                        │
│    - Structured summary                                │
│    - Pattern highlights                                │
│    - Hypothesis for call focus                         │
│    - Quick links to detailed data                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Store and notify                                    │
│    - Save briefing to database                         │
│    - Notify coach (email or in-app)                    │
│    - Make available in admin view                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Pre-call reminder (1 hour before)                   │
│    - Email to candidate with prep suggestions          │
│    - Email to coach with briefing link                 │
└─────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA

### Bookings Table

```sql
CREATE TABLE coaching_bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    
    -- Scheduling
    coach_id UUID REFERENCES coaches(id),
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    timezone TEXT NOT NULL,
    
    -- Status
    status TEXT DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no_show'
    
    -- Context
    candidate_goal TEXT, -- What they want to discuss
    hey_henry_context TEXT, -- Auto-captured context from conversation
    
    -- Meeting details
    meeting_link TEXT,
    calendar_event_id TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_bookings_user ON coaching_bookings(user_id);
CREATE INDEX idx_bookings_coach ON coaching_bookings(coach_id);
CREATE INDEX idx_bookings_scheduled ON coaching_bookings(scheduled_at);
CREATE INDEX idx_bookings_status ON coaching_bookings(status);
```

### Pre-Call Briefings Table

```sql
CREATE TABLE precall_briefings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES coaching_bookings(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    
    -- Briefing content
    briefing_content JSONB NOT NULL, -- Structured briefing data
    briefing_markdown TEXT NOT NULL, -- Rendered markdown for display
    
    -- Generation metadata
    generated_at TIMESTAMP DEFAULT NOW(),
    data_snapshot JSONB, -- Snapshot of data used to generate
    
    -- Access tracking
    viewed_at TIMESTAMP,
    viewed_by UUID REFERENCES coaches(id),
    
    CONSTRAINT fk_booking FOREIGN KEY (booking_id) 
        REFERENCES coaching_bookings(id) ON DELETE CASCADE
);

CREATE INDEX idx_briefings_booking ON precall_briefings(booking_id);
```

### Coaches Table (if not exists)

```sql
CREATE TABLE coaches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identity
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    
    -- Availability
    calendar_id TEXT, -- Google Calendar ID
    timezone TEXT DEFAULT 'America/New_York',
    availability_rules JSONB, -- Working hours, blocked times
    
    -- Settings
    default_duration INTEGER DEFAULT 30,
    buffer_minutes INTEGER DEFAULT 15, -- Between calls
    max_daily_calls INTEGER DEFAULT 8,
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Availability Slots Table

```sql
CREATE TABLE coach_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coach_id UUID REFERENCES coaches(id) NOT NULL,
    
    -- Time slot
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    
    -- Status
    status TEXT DEFAULT 'available', -- 'available', 'booked', 'blocked'
    booking_id UUID REFERENCES coaching_bookings(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_coach FOREIGN KEY (coach_id) 
        REFERENCES coaches(id) ON DELETE CASCADE
);

CREATE INDEX idx_availability_coach ON coach_availability(coach_id);
CREATE INDEX idx_availability_time ON coach_availability(start_time);
CREATE INDEX idx_availability_status ON coach_availability(status);
```

---

## API ENDPOINTS

### Get Available Slots

```
GET /api/scheduling/availability
```

**Query Parameters:**
- `start_date` (required): ISO date string
- `end_date` (optional): defaults to start_date + 7 days
- `duration` (optional): defaults to 30 minutes
- `timezone` (optional): defaults to user's timezone

**Response:**
```json
{
    "slots": [
        {
            "date": "2025-12-26",
            "times": [
                {"start": "09:00", "end": "09:30", "available": true},
                {"start": "09:30", "end": "10:00", "available": false},
                {"start": "10:00", "end": "10:30", "available": true}
            ]
        },
        {
            "date": "2025-12-27",
            "times": [...]
        }
    ],
    "timezone": "America/New_York"
}
```

### Create Booking

```
POST /api/scheduling/book
```

**Request:**
```json
{
    "slot_start": "2025-12-26T14:00:00Z",
    "duration_minutes": 30,
    "candidate_goal": "Discuss final round conversion issues",
    "hey_henry_context": "User has 0/3 final round conversion rate..."
}
```

**Response:**
```json
{
    "booking": {
        "id": "uuid",
        "scheduled_at": "2025-12-26T14:00:00Z",
        "duration_minutes": 30,
        "coach_name": "Henry",
        "meeting_link": "https://meet.google.com/xxx",
        "status": "scheduled"
    },
    "calendar_event_created": true,
    "confirmation_email_sent": true
}
```

### Cancel Booking

```
POST /api/scheduling/cancel/:booking_id
```

**Request:**
```json
{
    "reason": "Schedule conflict"
}
```

**Response:**
```json
{
    "cancelled": true,
    "slot_released": true
}
```

### Get Pre-Call Briefing (Coach Only)

```
GET /api/scheduling/briefing/:booking_id
```

**Response:**
```json
{
    "booking_id": "uuid",
    "candidate_name": "Alex Smith",
    "scheduled_at": "2025-12-26T14:00:00Z",
    "briefing": {
        "snapshot": {...},
        "pipeline_summary": {...},
        "pattern_analysis": {...},
        "debrief_highlights": [...],
        "candidate_goal": "...",
        "hey_henry_hypothesis": "...",
        "quick_links": {...}
    },
    "briefing_markdown": "..."
}
```

### Get Upcoming Bookings (Admin)

```
GET /api/scheduling/upcoming
```

**Response:**
```json
{
    "bookings": [
        {
            "id": "uuid",
            "candidate_name": "Alex Smith",
            "scheduled_at": "2025-12-26T14:00:00Z",
            "duration_minutes": 30,
            "candidate_goal": "Final round conversion issues",
            "briefing_ready": true,
            "briefing_viewed": false
        }
    ]
}
```

---

## HEY HENRY INTEGRATION

### Trigger Phrases (Candidate-Initiated)

Hey Henry should recognize scheduling intent from:

```
- "Can I talk to someone?"
- "I want to schedule time with a coach"
- "Is there a human I can speak with?"
- "Can I book a call?"
- "I need to talk to a real person"
- "Schedule coaching"
- "Book time with Henry"
```

### Trigger Conditions (Hey Henry-Initiated)

Hey Henry should suggest scheduling when:

| Condition | Trigger Logic |
|-----------|---------------|
| Final round failures | 3+ final rounds with 0 conversions |
| Negotiation needed | Offer received, user asking about comp |
| Career pivot | User discussing major direction change |
| Emotional distress | Crushed/desperate state sustained 2+ sessions |
| Explicit request | User says they need human help |
| Complex situation | Multi-offer decision, counter-offer strategy |
| Repeated loops | Same question/concern 3+ times without resolution |

### Context Capture

When booking is initiated, Hey Henry should capture:

1. **Conversation summary**: Last 5-10 exchanges
2. **Stated goal**: What user said they want to discuss
3. **Emotional state**: Current detected state
4. **Relevant patterns**: Any patterns surfaced in conversation
5. **Unresolved questions**: Open loops from conversation

This context feeds directly into the pre-call briefing.

### Sample Dialogues

**Candidate-Initiated:**

```
User: "Can I talk to someone about my job search? I feel stuck."

Hey Henry: "Of course. Sounds like you're hitting a wall.

I can book you 30 minutes with a coach. I'll prep them on your application history, interview debriefs, and the patterns I've spotted so you don't have to start from scratch.

What days work best this week?"

[Show Calendar Picker]
```

**Hey Henry-Initiated:**

```
Hey Henry: "You've reached the final round at 3 companies and haven't converted any. That's not bad luck, that's a pattern.

I can help with prep, but this might be worth talking through with a coach. They can dig into things I might miss, like how you're coming across in person.

Want to schedule 30 minutes? I'll brief them on everything."

[Book a Call] [Not Right Now]
```

**Post-Booking:**

```
Hey Henry: "You're booked for Thursday at 2pm EST.

I'll send them:
- Your application history (12 roles, 78% average fit)
- Interview debriefs from Stripe, Figma, and Linear
- The final round conversion pattern I flagged

You mentioned wanting to discuss whether you should adjust your targeting. I'll make sure they know that's the focus.

Anything else you want me to flag?"
```

---

## PRE-CALL BRIEFING GENERATION

### Data Sources

| Source | What We Pull |
|--------|--------------|
| User Profile | Name, current role, target roles, search duration |
| Applications | Last 30 days of applications with fit scores |
| Pipeline | Current stage for active applications |
| Interview Debriefs | All debriefs with extracted patterns |
| Hey Henry Conversations | Recent conversations, especially around this booking |
| Pattern Analysis | Output from Strategic Intelligence Engine |
| Story Bank | Stories used, usage frequency |

### Briefing Structure

```markdown
# PRE-CALL BRIEFING

**Candidate:** [Name]
**Call:** [Date/Time] ([Duration])
**Coach:** [Name]

---

## CANDIDATE SNAPSHOT
- Current role and tenure
- Target role level and company stage
- Search duration
- Profile strength score

---

## PIPELINE SUMMARY (Last 30 Days)
- Application count and average fit score
- Interview stages reached
- Conversion rates by stage
- Active companies with current stage

---

## PATTERN ANALYSIS

### Concerning Patterns
- [Pattern 1 with data]
- [Pattern 2 with data]

### Positive Patterns
- [Pattern 1 with data]
- [Pattern 2 with data]

---

## INTERVIEW DEBRIEF HIGHLIGHTS

### [Company 1] - [Stage] ([Date])
- Self-rating: X/5
- Key stumble: [Description]
- Hey Henry note: [Insight]

### [Company 2] - [Stage] ([Date])
- ...

---

## CANDIDATE'S STATED GOAL
"[Verbatim from booking]"

---

## HEY HENRY'S HYPOTHESIS
[2-3 sentences on what Hey Henry thinks is going on and suggested focus for the call]

---

## QUICK LINKS
- Full application history: [Link]
- Interview debriefs: [Link]
- Conversation history: [Link]
- Resume: [Link]
```

### Generation Logic

```javascript
async function generatePrecallBriefing(bookingId) {
    const booking = await getBooking(bookingId);
    const userId = booking.user_id;
    
    // Gather all data sources
    const [
        profile,
        applications,
        pipeline,
        debriefs,
        conversations,
        patterns,
        storyBank
    ] = await Promise.all([
        getUserProfile(userId),
        getRecentApplications(userId, 30), // Last 30 days
        getCurrentPipeline(userId),
        getInterviewDebriefs(userId),
        getRecentConversations(userId, 10), // Last 10 conversations
        getPatternAnalysis(userId),
        getStoryBank(userId)
    ]);
    
    // Build briefing data structure
    const briefingData = {
        snapshot: buildSnapshot(profile),
        pipeline_summary: buildPipelineSummary(applications, pipeline),
        pattern_analysis: buildPatternAnalysis(patterns),
        debrief_highlights: buildDebriefHighlights(debriefs),
        candidate_goal: booking.candidate_goal,
        hey_henry_context: booking.hey_henry_context,
        quick_links: buildQuickLinks(userId)
    };
    
    // Generate hypothesis via Claude
    const hypothesis = await generateHypothesis(briefingData);
    briefingData.hey_henry_hypothesis = hypothesis;
    
    // Render to markdown
    const briefingMarkdown = renderBriefingMarkdown(briefingData);
    
    // Store
    await storeBriefing(bookingId, briefingData, briefingMarkdown);
    
    return briefingMarkdown;
}
```

---

## CALENDAR INTEGRATION

### Google Calendar Setup

1. **OAuth Flow:**
   - Coach connects Google Calendar via OAuth
   - Store refresh token securely
   - Request calendar read/write permissions

2. **Availability Sync:**
   - Pull coach's calendar events daily
   - Block times that conflict with existing events
   - Respect working hours configuration

3. **Event Creation:**
   - Create calendar event on booking
   - Include meeting link (Google Meet)
   - Add candidate name and briefing link to description

### Event Details Template

```
Title: HenryHQ Coaching Call - [Candidate Name]

Description:
Coaching call with [Candidate Name]

PRE-CALL BRIEFING: [Link to briefing in HenryHQ admin]

Candidate's goal for this call:
"[Stated goal]"

---
This event was created by HenryHQ.
```

---

## NOTIFICATIONS

### Candidate Notifications

| Event | Channel | Timing |
|-------|---------|--------|
| Booking confirmed | Email + In-app | Immediate |
| Reminder | Email | 1 hour before |
| Post-call follow-up | In-app (Hey Henry) | 1 hour after |

### Coach Notifications

| Event | Channel | Timing |
|-------|---------|--------|
| New booking | Email | Immediate |
| Briefing ready | Email | When generated (usually immediate) |
| Reminder with briefing link | Email | 1 hour before |

### Email Templates

**Candidate Confirmation:**
```
Subject: Your coaching call is confirmed - [Date/Time]

Hi [Name],

Your call is booked:
- Date: [Date]
- Time: [Time] ([Timezone])
- Duration: 30 minutes
- Coach: [Coach Name]
- Meeting link: [Link]

I've already briefed [Coach Name] on your application history, interview debriefs, and the patterns I've spotted. You don't need to prep anything, but if you want to think about it beforehand, here's what you mentioned wanting to discuss:

"[Stated goal]"

Talk soon,
Henry

---
HenryHQ | Strategic Job Search Intelligence
```

**Coach Briefing Ready:**
```
Subject: Briefing ready for [Candidate Name] - [Date/Time]

Hi [Coach Name],

Your call with [Candidate Name] is coming up:
- Date: [Date]
- Time: [Time]
- Duration: 30 minutes

PRE-CALL BRIEFING: [Link]

Quick summary:
- [Candidate] has been searching for [X] months
- Applied to [X] roles, average fit score [X]%
- Key pattern: [Primary concern]
- Their goal for this call: "[Stated goal]"

See you then,
HenryHQ
```

---

## ADMIN INTERFACE

### Upcoming Calls View

```
UPCOMING COACHING CALLS

┌─────────────────────────────────────────────────────────────────────┐
│ Thursday, December 26                                               │
├─────────────────────────────────────────────────────────────────────┤
│ 2:00 PM  Alex Smith (30 min)                                       │
│ Goal: "Final round conversion issues"                               │
│ [View Briefing] [Join Call] [Reschedule] [Cancel]                  │
├─────────────────────────────────────────────────────────────────────┤
│ 3:30 PM  Jordan Lee (30 min)                                       │
│ Goal: "Negotiation strategy for Stripe offer"                       │
│ [View Briefing] [Join Call] [Reschedule] [Cancel]                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Friday, December 27                                                 │
├─────────────────────────────────────────────────────────────────────┤
│ 10:00 AM  Sam Rivera (30 min)                                      │
│ Goal: "Career pivot from government to private sector"              │
│ [View Briefing] [Join Call] [Reschedule] [Cancel]                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Briefing View

Full markdown render of the pre-call briefing with:
- Collapsible sections
- Quick links that open in new tabs
- "Mark as Reviewed" button
- Notes field for coach to add pre-call thoughts

---

## INTERIM SOLUTION (Calendly Fallback)

Until native scheduling is implemented, use Calendly with manual briefing:

### Flow

1. Hey Henry provides Calendly link when scheduling requested
2. Candidate books via Calendly
3. Calendly webhook notifies HenryHQ of booking
4. Pre-call briefing generates automatically
5. Coach receives email with briefing link

### Calendly Webhook Integration

```javascript
// Webhook endpoint
POST /api/webhooks/calendly

// Payload processing
async function handleCalendlyWebhook(payload) {
    if (payload.event === 'invitee.created') {
        const email = payload.payload.email;
        const scheduledTime = payload.payload.scheduled_event.start_time;
        
        // Find user by email
        const user = await getUserByEmail(email);
        if (!user) return; // Not a HenryHQ user
        
        // Create booking record
        const booking = await createBooking({
            user_id: user.id,
            scheduled_at: scheduledTime,
            source: 'calendly',
            calendly_event_id: payload.payload.uri
        });
        
        // Generate briefing
        await generatePrecallBriefing(booking.id);
    }
}
```

### Hey Henry Dialogue (Interim)

```
User: "Can I talk to a coach?"

Hey Henry: "Absolutely. Here's the booking link:

[Book a Call with Henry](https://calendly.com/henryhq/coaching)

Once you book, I'll automatically prep a briefing with your application history, interview debriefs, and the patterns I've spotted. You won't need to repeat yourself."
```

---

## IMPLEMENTATION PHASES

### Phase 2.1: Calendly Integration (Interim)
- Calendly webhook integration
- Auto-briefing generation on booking
- Coach email notifications
- Admin view for upcoming calls
- Estimated effort: 4-6 hours

### Phase 2.2: Native Scheduling (Full)
- Calendar API integration (Google)
- Availability management
- In-chat booking UI
- Full notification system
- Estimated effort: 16-24 hours

### Phase 2.3: Post-Call Intelligence
- Call outcome tracking
- Follow-up action items
- Feedback loop to Hey Henry
- Estimated effort: 8-12 hours

---

## SUCCESS METRICS

| Metric | Target |
|--------|--------|
| Booking completion rate | >80% of started bookings complete |
| Briefing generation success | 100% of bookings have briefing |
| Coach briefing view rate | >90% viewed before call |
| Candidate satisfaction | >4.5/5 post-call rating |
| No-show rate | <10% |
| Time from booking to call | <72 hours average |

---

## ANTI-PATTERNS

### Forcing Scheduling (NEVER)

**BAD:**
```
Hey Henry: "You need to talk to a coach about this."
```

**GOOD:**
```
Hey Henry: "This might be worth talking through with a coach. Want me to set something up?"
```

### Generic Briefings (NEVER)

**BAD:**
```
Briefing: "User is looking for PM roles and has applied to several companies."
```

**GOOD:**
```
Briefing: "User has 0/3 final round conversion at Series B companies. Pattern suggests 'culture fit' concerns despite strong technical performance. Hypothesis: leadership narrative doesn't match Director expectations."
```

### Losing Context (NEVER)

**BAD:**
```
[After booking]
Hey Henry: "How can I help you?"
```

**GOOD:**
```
[After booking]
Hey Henry: "You're all set for Thursday. In the meantime, want to prep for your Notion interview next week?"
```

---

## RELATED DOCUMENTS

- HEY_HENRY_IMPLEMENTATION_SPEC_v2.2.md (Core Hey Henry spec)
- HEY_HENRY_STRATEGIC_INTELLIGENCE_ENGINE_SPEC_v1.md (Pattern analysis)
- HEY_HENRY_INTERVIEW_DEBRIEF_INTELLIGENCE_SPEC_v1.md (Debrief data)
- HEY_HENRY_CONVERSATION_HISTORY_SPEC_v1.md (Conversation persistence)

---

**END OF SCHEDULING & PRE-CALL BRIEFING SPECIFICATION v1.0**

This is a Phase 2 feature. The interim Calendly solution can be implemented quickly to validate demand before building native scheduling.
