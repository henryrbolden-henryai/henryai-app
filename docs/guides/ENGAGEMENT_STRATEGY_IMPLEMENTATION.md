# HenryAI Engagement Strategy Implementation Plan

**Goal:** Transform HenryAI from "a tool that helps you apply to jobs" into "your job search strategist who happens to also generate documents."

**Core Insight:** Users currently get documents and leave. We need to make the other sections feel essential, not optional.

---

## Initiative 1: Proactive Henry Notification System

### Concept
Henry actively nudges users based on their tracker status and application timeline, shifting from reactive tool to proactive coach.

### Notification Triggers

| Trigger | Timing | Message Example |
|---------|--------|-----------------|
| Follow-up due | 5-7 days after applying | "You applied to [Company] 5 days ago. Most companies respond within 7 days. Want me to draft a follow-up email?" |
| Interview prep reminder | 2 days before interview | "Your interview at [Company] is in 2 days. You haven't done any mock practice for this role yet. Want to run through some questions?" |
| Stale application | 14+ days no update | "[Company] has been quiet for 2 weeks. This might be ghosting. Should we discuss next steps or focus energy elsewhere?" |
| Post-interview follow-up | 1 day after interview | "How did your interview at [Company] go? Let's debrief so I can help you prepare for next steps." |
| Momentum check | Weekly | "You have 3 applications in interview stages. Here's what I'd prioritize this week..." |
| New pattern detected | After 5+ applications | "I noticed you're getting interviews at fintech companies but not enterprise SaaS. Want to analyze why?" |

### Technical Implementation

**Option A: In-App Notifications (Recommended for Beta)**

1. Create `frontend/components/henry-notifications.js`:
```javascript
// On page load, check for notification triggers
function checkNotificationTriggers() {
    const apps = JSON.parse(localStorage.getItem('trackedApplications') || '[]');
    const notifications = [];

    apps.forEach(app => {
        // Check follow-up timing
        if (app.status === 'Applied' && getDaysSince(app.dateApplied) >= 5) {
            notifications.push({
                type: 'follow_up',
                priority: 'high',
                app: app,
                message: `Time to follow up with ${app.company}?`
            });
        }

        // Check interview prep
        if (isInterviewScheduled(app) && getDaysUntil(app.interviewDate) <= 2) {
            if (!hasMockPractice(app)) {
                notifications.push({
                    type: 'interview_prep',
                    priority: 'urgent',
                    app: app,
                    message: `Interview at ${app.company} in ${getDaysUntil(app.interviewDate)} days`
                });
            }
        }

        // Check for ghosting risk
        if (app.status === 'Applied' && getDaysSince(app.dateApplied) >= 14) {
            notifications.push({
                type: 'ghost_risk',
                priority: 'medium',
                app: app,
                message: `${app.company} may have gone quiet`
            });
        }
    });

    return prioritizeNotifications(notifications);
}
```

2. Display as a notification banner on tracker/overview pages:
```html
<div class="henry-notification" data-type="follow_up">
    <div class="notification-avatar"><!-- Henry logo --></div>
    <div class="notification-content">
        <p><strong>Henry:</strong> You applied to Stripe 5 days ago. Companies typically respond within 7 days. Want me to draft a follow-up?</p>
    </div>
    <div class="notification-actions">
        <button class="btn-primary" onclick="draftFollowUp('stripe')">Draft Follow-up</button>
        <button class="btn-secondary" onclick="dismissNotification()">Not now</button>
    </div>
</div>
```

**Option B: Email Digest (Phase 2)**

- Daily/weekly email with personalized action items
- Requires email collection and SendGrid/similar integration
- Links back to specific pages in HenryAI

### Data Requirements

Add to tracked application schema:
```javascript
{
    // Existing fields...
    interviewDate: null,           // ISO date string
    interviewType: null,           // 'phone', 'video', 'onsite'
    mockPracticeCompleted: false,  // boolean
    lastFollowUpDate: null,        // ISO date string
    followUpCount: 0,              // number
    notificationsDismissed: []     // array of dismissed notification IDs
}
```

---

## Initiative 2: Application Readiness Score

### Concept
Visual indicator showing how prepared they are for each application, using gamification through completeness.

### Score Breakdown

| Component | Weight | Criteria |
|-----------|--------|----------|
| Resume tailored | 20% | Has customized resume for this role |
| Cover letter | 15% | Has generated cover letter |
| Positioning reviewed | 10% | Has viewed positioning strategy page |
| Outreach prepared | 20% | Has viewed outreach templates OR sent outreach |
| Interview prep started | 15% | Has viewed prep guide OR done mock practice |
| Mock interview completed | 20% | Has completed at least one mock session |

### Visual Design

```
┌─────────────────────────────────────────────────┐
│  Application Readiness                    45%   │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                 │
│  ✅ Resume tailored                             │
│  ✅ Cover letter generated                      │
│  ⚠️ No outreach sent (+30% response rate)       │
│  ❌ Interview prep not started                  │
│  ❌ No mock practice completed                  │
│                                                 │
│  [Complete Next Step →]                         │
└─────────────────────────────────────────────────┘
```

### Implementation

1. Add to `overview.html` above the cards grid:
```html
<div class="readiness-score-card">
    <div class="readiness-header">
        <h3>Application Readiness</h3>
        <span class="readiness-percentage" id="readinessScore">45%</span>
    </div>
    <div class="readiness-bar">
        <div class="readiness-fill" id="readinessBar" style="width: 45%"></div>
    </div>
    <div class="readiness-checklist" id="readinessChecklist">
        <!-- Dynamically populated -->
    </div>
    <button class="readiness-cta" id="readinessCta">Complete Next Step</button>
</div>
```

2. Track completion in sessionStorage per analysis:
```javascript
const readinessState = {
    resumeTailored: true,
    coverLetterGenerated: true,
    positioningReviewed: false,
    outreachPrepared: false,
    interviewPrepStarted: false,
    mockCompleted: false
};
sessionStorage.setItem('readinessState', JSON.stringify(readinessState));
```

3. Update state when user visits each section:
```javascript
// In positioning.html
window.addEventListener('DOMContentLoaded', () => {
    updateReadinessState('positioningReviewed', true);
});
```

### Psychology

- People hate incomplete progress bars
- "45%" feels like leaving value on the table
- "+30% response rate" creates FOMO
- "Complete Next Step" removes decision paralysis

---

## Initiative 3: Teaser Insights on Overview Cards

### Concept
Don't just list sections—show what's waiting inside. Create curiosity.

### Current State
```html
<h2 class="card-title">Your Positioning Strategy</h2>
<p class="card-description">
    How to position yourself for this role. Includes what to emphasize,
    what to avoid, key positioning decisions, and how to handle concerns.
</p>
```

### Enhanced State
```html
<h2 class="card-title">Your Positioning Strategy</h2>
<p class="card-insight">
    <span class="insight-highlight">Your biggest gap:</span> Enterprise SaaS experience.
    I have 3 ways to reframe this in interviews.
</p>
<p class="card-description">
    How to position yourself for this role...
</p>
```

### Insight Generation Per Card

**Positioning Strategy:**
- Pull from `analysis_data.gaps` or `analysis_data.concerns`
- Example: "Your biggest gap for this role is [first gap]. I have strategies to address it."

**Network Intelligence:**
- Pull from `analysis_data.outreach_intelligence`
- Example: "The likely hiring manager is a [title]. Direct outreach could 2x your response rate."

**Interview Intelligence:**
- Pull from `analysis_data.interview_prep` or company patterns
- Example: "[Company] heavily emphasizes [focus area]. Your resume has [N] relevant stories."

### Implementation

```javascript
// In overview.html
function generateCardInsights(analysisData) {
    const insights = {};

    // Positioning insight
    if (analysisData.gaps && analysisData.gaps.length > 0) {
        const topGap = analysisData.gaps[0];
        insights.positioning = `Your biggest gap: ${topGap.area}. I have strategies to address this.`;
    }

    // Network insight
    if (analysisData.outreach_intelligence?.hiring_manager_likely_title) {
        insights.network = `The likely hiring manager is a ${analysisData.outreach_intelligence.hiring_manager_likely_title}. Direct outreach could 2x your response rate.`;
    }

    // Interview insight
    if (analysisData.interview_prep?.likely_questions) {
        const questionCount = analysisData.interview_prep.likely_questions.length;
        insights.interview = `I've identified ${questionCount} likely interview questions. Let's prepare your answers.`;
    }

    return insights;
}
```

---

## Initiative 4: Network Intelligence as Default Next Step

### Concept
After generating documents, don't end the flow—guide them to the next highest-impact action.

### Current Flow
```
Documents Page → "Download" → User leaves
```

### Enhanced Flow
```
Documents Page → "Download" →
    Modal: "Your documents are ready! But here's the reality:
           70% of jobs are filled through referrals.
           I found 2 people you should reach out to at [Company].
           [View Outreach Strategy →] [Maybe Later]"
```

### Implementation

1. Add post-download modal to `documents.html`:
```html
<div class="post-download-modal" id="postDownloadModal">
    <div class="modal-content">
        <div class="modal-icon">🤝</div>
        <h3>Great, your documents are ready!</h3>
        <p class="modal-stat">But here's the reality: <strong>70% of jobs are filled through referrals.</strong></p>
        <p class="modal-insight" id="networkInsight">
            I found the likely hiring manager at [Company].
            Direct outreach could significantly improve your chances.
        </p>
        <div class="modal-actions">
            <a href="outreach.html" class="btn-primary">View Outreach Strategy</a>
            <button class="btn-secondary" onclick="closeModal()">Maybe Later</button>
        </div>
    </div>
</div>
```

2. Trigger on download:
```javascript
function downloadPackage() {
    // ... existing download logic ...

    // Show modal after download starts
    setTimeout(() => {
        document.getElementById('postDownloadModal').classList.add('show');
    }, 1000);
}
```

### Psychology
- "Maybe Later" acknowledges their autonomy (reduces friction)
- Statistic creates urgency without being pushy
- Personalized insight ("I found the hiring manager") creates curiosity

---

## Initiative 5: Ask Henry as Central Hub

### Concept
Position Ask Henry not as a help widget, but as the primary interface for job search strategy.

### Current State
- Floating widget in bottom-right
- Contextual suggestions based on page
- Reactive—waits for user to ask

### Enhanced Capabilities

**1. Proactive Conversation Starters**

When chat opens, based on context:
```javascript
const proactiveOpeners = {
    'overview': [
        "I noticed you haven't reviewed your positioning strategy yet. Want me to explain the key points?",
        "Quick thought: your biggest differentiator for this role is [X]. Want to discuss how to emphasize it?"
    ],
    'tracker': [
        "You have 2 applications that need follow-ups. Want me to draft them?",
        "I see you're interviewing at 3 companies. Which one should we prep for first?"
    ],
    'documents': [
        "Before you download, want me to explain the key changes I made to your resume?",
        "I tailored 5 bullet points for this role. Want to understand why?"
    ]
};
```

**2. Action Suggestions in Responses**

Henry's responses should include actionable links:
```javascript
// Backend enhancement to /api/ask-henry
// Include suggested_actions in response:
{
    "response": "Your positioning for this role should emphasize...",
    "suggested_actions": [
        { "label": "Review full positioning strategy", "href": "positioning.html" },
        { "label": "Practice mock interview", "href": "mock-interview.html" }
    ]
}
```

**3. "What Should I Do Next?" Intelligence**

Dedicated logic for the most common question:
```javascript
function getNextBestAction(context) {
    const { analysisData, readinessState, trackerData } = context;

    // Priority order:
    // 1. Upcoming interview prep
    // 2. Follow-up due
    // 3. Incomplete readiness items
    // 4. New role to analyze

    if (hasUpcomingInterview(trackerData)) {
        return {
            action: "Prep for your interview",
            reason: "You have an interview in 2 days",
            href: "interview-intelligence.html"
        };
    }

    if (hasFollowUpDue(trackerData)) {
        return {
            action: "Send follow-up",
            reason: "It's been 7 days since you applied",
            href: "outreach.html"
        };
    }

    // ... etc
}
```

---

## Initiative 6: Daily/Weekly Digest System

### Concept
Give users a reason to come back regularly with personalized summaries.

### Digest Content

**Daily Check-in (In-App Banner)**
```
Good morning, [Name]! Here's your job search pulse:
- 3 active applications
- 1 follow-up due today (Stripe - applied 7 days ago)
- Interview in 2 days (Google)

[See Full Dashboard]
```

**Weekly Summary (Email - Phase 2)**
```
Subject: Your week in job search: 2 interviews, 1 offer stage

Hi [Name],

Here's how your job search progressed this week:

📊 Pipeline Health
- 5 active applications (+2 from last week)
- 2 interviews completed
- 1 moved to offer stage!

🎯 What's Working
- Your interview rate is 40% (above average)
- Fintech companies are responding well

⚠️ Needs Attention
- 2 applications may be stalled (no response in 14+ days)
- You haven't prepped for your Thursday interview yet

📋 This Week's Priorities
1. Prep for Thursday interview at Stripe
2. Follow up with Plaid (applied 10 days ago)
3. Analyze 2 new roles to keep pipeline healthy

[Open HenryAI]
```

### Implementation (In-App First)

1. Add to tracker.html above the main content:
```html
<div class="daily-pulse" id="dailyPulse">
    <div class="pulse-greeting">
        Good morning, <span id="userName">there</span>! Here's your job search pulse:
    </div>
    <div class="pulse-stats">
        <div class="pulse-stat">
            <span class="stat-value" id="activeCount">3</span>
            <span class="stat-label">active apps</span>
        </div>
        <div class="pulse-stat highlight">
            <span class="stat-value" id="followUpCount">1</span>
            <span class="stat-label">follow-up due</span>
        </div>
        <div class="pulse-stat">
            <span class="stat-value" id="interviewCount">1</span>
            <span class="stat-label">upcoming interview</span>
        </div>
    </div>
    <div class="pulse-action" id="pulseAction">
        <!-- Dynamic based on highest priority -->
    </div>
</div>
```

---

## Implementation Priority

### Phase A: Quick Wins (1-2 days each)

1. **Teaser Insights on Overview Cards**
   - Low effort, high impact
   - Just JavaScript additions to overview.html
   - Uses existing analysis data

2. **Post-Download Modal for Network Intelligence**
   - Single modal addition to documents.html
   - Immediate behavior change

3. **Daily Pulse Banner on Tracker**
   - Uses existing tracker data
   - Reinforces daily engagement

### Phase B: Core Systems (3-5 days each)

4. **Application Readiness Score**
   - Requires tracking state across pages
   - Visual component + logic

5. **Proactive Ask Henry**
   - Backend changes to /api/ask-henry
   - Frontend changes to ask-henry.js
   - New proactive opener logic

### Phase C: Full Notification System (1-2 weeks)

6. **Henry Notification System**
   - Notification trigger engine
   - Notification UI components
   - Dismissal/snooze logic
   - Action handlers

### Phase D: External Engagement (Future)

7. **Email Digest System**
   - Email collection flow
   - SendGrid integration
   - Digest generation logic
   - Unsubscribe handling

---

## Success Metrics

| Metric | Current (Estimated) | Target |
|--------|---------------------|--------|
| Pages visited per session | 2-3 | 5+ |
| Return visits per week | 1-2 | 4+ |
| Network Intelligence page views | 10% of users | 50%+ |
| Interview Intelligence page views | 15% of users | 60%+ |
| Mock interview completion | 5% of users | 30%+ |
| Time on platform per session | 3-5 min | 10+ min |

---

## Next Steps

1. Review and prioritize with stakeholder
2. Create detailed tickets for Phase A items
3. Begin implementation with Teaser Insights (lowest effort, validates approach)
4. User test with beta group before Phase B
