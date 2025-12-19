# HenryHQ Command Center — Implementation Spec

**Version:** 2.0  
**Date:** December 18, 2025  
**Audience:** Claude Code  
**Scope:** Behavioral logic, decision intelligence, data model changes

---

## **1. Core Constraint**

Every tracker action must answer:
- **What should I do next?** (≤5 words)
- **Why does it matter?** (≤10 words, contextual to timeline/stage/momentum)

If a feature can't answer both clearly, it doesn't ship.

---

## **2. Data Model Changes**

### **Supabase Schema Updates**

```sql
-- Add to applications table
ALTER TABLE applications ADD COLUMN IF NOT EXISTS jd_source VARCHAR(50);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS provisional_profile JSONB;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS confidence_label VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS decision_confidence INTEGER;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS substatus VARCHAR(50);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS days_since_last_activity INTEGER;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_activity_date DATE;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS next_action VARCHAR(100);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS next_action_reason VARCHAR(200);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS priority_level VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS user_override BOOLEAN DEFAULT FALSE;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS user_override_reason TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS manual_lock BOOLEAN DEFAULT FALSE;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_applications_jd_source ON applications(jd_source);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_substatus ON applications(substatus);
CREATE INDEX IF NOT EXISTS idx_applications_decision_confidence ON applications(decision_confidence);
CREATE INDEX IF NOT EXISTS idx_applications_next_action ON applications(next_action);
```

### **Field Definitions**

| Field | Type | Purpose | Example Values |
|-------|------|---------|----------------|
| `jd_source` | VARCHAR(50) | Track JD provenance | `user_provided`, `url_fetched`, `inferred`, `missing`, `link_failed` |
| `provisional_profile` | JSONB | Store reconstructed role profile | `{"typical_responsibilities": [...], "common_competencies": [...]}` |
| `confidence_label` | VARCHAR(20) | Trust preservation | `directional`, `refined` |
| `decision_confidence` | INTEGER | Strategic guidance score (0-100) | `85`, `45`, `20` |
| `substatus` | VARCHAR(50) | Granular state tracking | `waiting`, `follow_up_sent`, `prep_needed`, `ghosted_14d` |
| `days_since_last_activity` | INTEGER | Momentum tracking | `7`, `14`, `21` |
| `last_activity_date` | DATE | For calculating staleness | `2025-12-18` |
| `next_action` | VARCHAR(100) | Explicit instruction | `Send follow-up email`, `Archive this application`, `None—wait` |
| `next_action_reason` | VARCHAR(200) | Contextual "why" | `70% respond by now. Silence = ghosting.` |
| `priority_level` | VARCHAR(20) | Focus guidance | `high`, `medium`, `low`, `archive` |
| `user_override` | BOOLEAN | User manually set priority/action | `true`, `false` |
| `user_override_reason` | TEXT | Why user overrode system | `Strategic relationship. Worth staying on radar.` |
| `manual_lock` | BOOLEAN | Prevent system from changing action | `true`, `false` |

---

## **3. New Backend Endpoints**

### **3.1 Reconstruct JD from Role Signal**

```
POST /api/jd/reconstruct

Purpose: Generate Provisional Role Profile when JD is missing

Input:
{
  "role_title": "Senior Product Manager",
  "company_name": "Stripe",
  "industry": "fintech",  // optional, inferred if missing
  "seniority": "senior"   // optional, inferred from title
}

Output:
{
  "provisional_profile": {
    "role_title": "Senior Product Manager",
    "typical_responsibilities": [
      "Own product roadmap for payments platform",
      "Partner with engineering on technical scoping",
      "Drive cross-functional execution"
    ],
    "common_competencies": [
      "Stakeholder management",
      "Technical fluency",
      "Strategic thinking"
    ],
    "interview_focus_areas": [
      "Product sense (hypothetical design)",
      "Execution (cross-functional collaboration)",
      "Technical depth (API/platform knowledge)"
    ],
    "evaluation_criteria": [
      "Can they scope ambiguous problems?",
      "Do they understand technical constraints?",
      "Can they influence without authority?"
    ]
  },
  "confidence": "directional",
  "jd_source": "inferred"
}

Claude System Prompt:
You are a recruiter reconstructing typical role expectations.

Given:
- Role title: {role_title}
- Company: {company_name}
- Industry: {industry}
- Seniority: {seniority}

Generate a Provisional Role Profile with:
1. Typical responsibilities (3-5 bullets)
2. Common competencies assessed (3-5 items)
3. Likely interview focus areas (3-4 areas)
4. Typical evaluation criteria (2-3 questions)

Base this on:
- Standard expectations for this role at this level
- Industry norms (e.g., fintech PM vs. enterprise SaaS PM)
- Company type (startup vs. public company)

Be specific but acknowledge uncertainty. This is directional, not exact.
```

---

### **3.2 Tracker Intelligence Engine**

```
POST /api/tracker/intelligence

Purpose: Calculate next actions for all applications

Input:
{
  "user_id": "abc123",
  "applications": [
    {
      "id": "app1",
      "status": "Applied",
      "company": "Stripe",
      "role": "Senior PM",
      "date_applied": "2025-12-11",
      "decision_confidence": 75,
      "jd_source": "user_provided"
    },
    // ... more applications
  ]
}

Output:
{
  "priority_actions": [
    {
      "application_id": "app1",
      "action": "Send follow-up email",
      "reason": "70% respond by now. Silence = ghosting.",
      "priority": "high",
      "one_click_action": {
        "type": "draft_email",
        "template": "follow_up_day_7"
      }
    },
    {
      "application_id": "app2",
      "action": "Archive this application",
      "reason": "21+ days. You're wasting mental energy.",
      "priority": "high",
      "one_click_action": {
        "type": "archive",
        "confirm": true
      }
    },
    {
      "application_id": "app3",
      "action": "None—wait for next steps",
      "reason": "Typical response: 3-5 days. Don't follow up.",
      "priority": "low",
      "one_click_action": null
    }
  ],
  "pipeline_health": {
    "active_count": 5,
    "status": "healthy",
    "recommendation": "None—maintain pace, focus on interviews",
    "reason": "Good volume. Shift energy to conversion."
  },
  "focus_mode": {
    "top_actions": [
      {
        "application_id": "app1",
        "company": "Stripe",
        "action": "Send follow-up email"
      },
      {
        "application_id": "app4",
        "company": "Plaid",
        "action": "Review prep guide now"
      }
    ],
    "dim_others": true
  }
}

Logic Rules:

1. Calculate days_since_last_activity for each application
2. Determine substatus based on:
   - Days since applied/last contact
   - Interview scheduled/completed
   - Follow-up sent
3. Calculate next_action based on status + substatus + days
4. Prioritize actions (max 2-3 "high" priority)
5. Recommend pipeline-level actions (apply more, pause, focus)

Strategic Stop Logic:
If interview_rate < 5% AND total_applications >= 10:
  pipeline_action = "Stop applying. Fix your positioning."
  pipeline_reason = "Something's broken. Diagnose before continuing."
  pipeline_tone = "urgent"
  cooldown_until = now + 7 days  // Block new applications for 7 days
  
This is a circuit breaker. The system refuses to let them keep doing what's not working.

Manual Override Handling:
If application.manual_lock = true:
  Skip intelligence recalculation for this application
  Display user_override_reason in UI
  Log: "User override active - [reason]"
  
This lets users say "I know this is low confidence, but it's strategic" without the system fighting them.

Action Decision Tree:

Status: Applied
- Days 0-6: action = "None—wait", reason = "Most responses Days 3-7. Wait."
- Day 7: action = "Send follow-up email", reason = "70% respond by now. Silence = ghosting."
- Day 14: action = "Mark ghosted or final check-in", reason = "Dead deal. Stop tracking. Move on."
- Day 21: action = "Archive this application", reason = "You're wasting mental energy. It's over."

Status: Recruiter Screen Scheduled
- action = "Review prep guide now", reason = "Recruiters screen out 60%. Be ready."

Status: Recruiter Screen Complete
- Days 0-5: action = "None—wait for next steps", reason = "Typical response: 3-5 days. Don't follow up."
- Days 5+: action = "Send status check-in", reason = "They're deciding or ghosting. Force clarity."

Status: Hiring Manager Scheduled
- action = "Prepare 3 scope-alignment stories", reason = "This stage kills 40%. Prove you fit."

Status: Final Round Scheduled
- action = "Practice executive presence now", reason = "They're testing culture fit. Be confident."

Status: Final Round Complete
- Days 0-3: action = "Send thank-you + reiterate interest", reason = "Decisions happen Days 3-7. Stay visible."
- Days 7+: action = "Request feedback or close mentally", reason = "7+ days = probably rejection. Get clarity."

Decision Confidence:
- <40: action = "Deprioritize or withdraw", reason = "This is low-leverage. Focus better bets."
- 40-70: action = "Continue but don't overinvest", reason = "Decent fit. Watch for stalls."
- 70+: action = "Prioritize—stay aggressive here", reason = "Strong alignment. This is worth energy."
```

---

### **3.3 Calculate Decision Confidence**

```
POST /api/tracker/calculate-confidence

Purpose: Calculate decision_confidence score for an application

Input:
{
  "application_id": "app1",
  "fit_score": 75,
  "jd_source": "user_provided",
  "days_since_applied": 7,
  "status": "Applied",
  "interview_count": 0,
  "response_time_days": null
}

Output:
{
  "decision_confidence": 68,
  "label": "medium",
  "factors": {
    "alignment_score": 75,
    "momentum_score": 40,  // No response yet
    "jd_confidence": 100   // Real JD provided
  },
  "guidance": "Decent fit. Watch for stalls."
}

Calculation Logic:

decision_confidence = (
  (alignment_score * 0.5) +
  (momentum_score * 0.3) +
  (jd_confidence * 0.2)
)

alignment_score = fit_score (from initial analysis)

momentum_score = calculated from:
- Has there been any response? (+20 if yes)
- Response time (faster = higher)
- Interview progression (each stage +10)
- Days since last activity (staleness penalty)
- Confidence decay: -5 points per 10 days of no new signal

Confidence Decay Rule:
If days_since_last_activity >= 10:
  decay_penalty = floor(days_since_last_activity / 10) * 5
  momentum_score = max(0, momentum_score - decay_penalty)

This prevents zombie optimism. Silence degrades confidence.

jd_confidence:
- user_provided: 100
- url_fetched: 100
- inferred: 70
- missing: 50
- link_failed: 50
```

---

### **3.4 Update Interview Prep (Handle Missing JDs)**

```
POST /api/interview-prep/generate

Purpose: Generate prep regardless of JD availability

Input:
{
  "application_id": "abc123",
  "interview_type": "hiring_manager",
  "jd_source": "inferred",
  "provisional_profile": { ... },  // if jd_source = inferred/missing
  "real_jd": "...",  // if jd_source = user_provided/url_fetched
  "resume": { ... }
}

Output:
{
  "prep_guide": {
    "likely_questions": [
      "Tell me about a time you led a cross-functional initiative",
      "How do you prioritize when everything is urgent?",
      "Walk me through how you'd approach [product problem]"
    ],
    "signal_areas": [
      "Stakeholder management",
      "Execution under ambiguity",
      "Technical fluency"
    ],
    "common_failure_points": [
      "Weak execution stories (too high-level)",
      "Can't articulate technical trade-offs",
      "No examples of influencing laterally"
    ],
    "intro_framing": "Lead with your cross-functional PM experience at Uber. Emphasize technical fluency and execution in ambiguous environments.",
    "stage_specific_guidance": "Hiring managers assess scope alignment. Be ready to discuss specific project types and decision-making frameworks."
  },
  "confidence": "directional",  // or "refined"
  "ui_note": "This prep is based on typical expectations for this role. Add recruiter context anytime to refine it."
}

Logic:

if jd_source in ['inferred', 'missing']:
  Use provisional_profile for prep generation
  Set confidence = "directional"
  Include ui_note about typical expectations
else:
  Use real_jd for prep generation
  Set confidence = "refined"
  ui_note = null

Always generate prep. Never block on missing JD.

Prep Regeneration Triggers:
- Prep guide doesn't exist
- JD source upgraded (inferred → user_provided/url_fetched)
- Interview type changed (recruiter_screen → hiring_manager)
- User uploads recruiter context/email
- User explicitly clicks "Regenerate Prep"

When regenerating, include change note:
"Prep updated based on [new JD / interview type change / recruiter context]"
```

---

### **3.5 Fit Analysis (Handle Missing JDs)**

```
POST /api/jd/analyze

Purpose: Analyze fit even without real JD

Input:
{
  "resume": { ... },
  "jd_source": "inferred",
  "provisional_profile": { ... },  // if jd_source = inferred/missing
  "job_description": "...",  // if jd_source = user_provided
  "role_title": "Senior Product Manager",
  "company_name": "Stripe"
}

Output:
{
  "fit_score": 68,
  "confidence_label": "directional",
  "strengths": [
    "Cross-functional PM experience at Uber",
    "Technical fluency with APIs and platforms",
    "Track record in fintech (payments at Stripe)"
  ],
  "gaps": [
    "Limited experience with 0-1 products",
    "No direct B2B SaaS background"
  ],
  "recommendation": "Apply",
  "ui_note": "This is based on typical expectations for Senior PMs at fintech companies. Your actual fit may vary—add JD text anytime to refine.",
  "decision_confidence": 65
}

Logic:

if jd_source in ['inferred', 'missing']:
  Use provisional_profile as baseline for fit assessment
  Cap fit_score at 75 max (uncertainty penalty)
  Set confidence_label = "directional"
  Include ui_note about typical expectations
else:
  Use real job_description for fit assessment
  No cap on fit_score
  Set confidence_label = "refined"
  ui_note = null

Always return fit analysis. Never block on missing JD.
```

---

## **4. Frontend Integration Points**

### **4.1 Tracker Page Load**

```javascript
// On tracker.html load:

async function initializeTracker() {
  // 1. Load applications from Supabase
  const applications = await HenryData.getApplications();
  
  // 2. Call intelligence engine
  const intelligence = await fetch('/api/tracker/intelligence', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      user_id: currentUser.id, 
      applications: applications 
    })
  }).then(r => r.json());
  
  // 3. Update each application with next_action and priority
  applications.forEach(app => {
    const action = intelligence.priority_actions.find(a => a.application_id === app.id);
    if (action) {
      app.next_action = action.action;
      app.next_action_reason = action.reason;
      app.priority_level = action.priority;
      app.one_click_action = action.one_click_action;
    }
  });
  
  // 4. Render tracker with actions
  renderTracker(applications, intelligence);
  
  // 5. If Focus Mode enabled, dim non-priority items
  if (focusModeEnabled) {
    applyFocusMode(intelligence.focus_mode);
  }
}
```

---

### **4.2 Application Card Rendering**

```javascript
// In renderApplicationCard():

function renderApplicationCard(app) {
  const card = document.createElement('div');
  card.className = `application-card priority-${app.priority_level}`;
  
  // Confidence color-coding
  if (app.decision_confidence >= 70) {
    card.classList.add('confidence-high');  // Green border
  } else if (app.decision_confidence >= 40) {
    card.classList.add('confidence-medium');  // Yellow border
  } else {
    card.classList.add('confidence-low');  // Red border
  }
  
  card.innerHTML = `
    <div class="card-header">
      <h3>${app.company} - ${app.role}</h3>
      ${app.confidence_label === 'directional' ? '<span class="badge-directional">Directional</span>' : ''}
    </div>
    
    <div class="card-stats">
      <span>Fit: ${app.fit_score}%</span>
      <span>Confidence: ${app.decision_confidence}</span>
      <span>${app.days_since_last_activity} days since activity</span>
    </div>
    
    <div class="next-action">
      <strong>Next:</strong> ${app.next_action}
      <p class="action-reason">${app.next_action_reason}</p>
    </div>
    
    ${app.one_click_action ? renderOneClickButton(app.one_click_action) : ''}
  `;
  
  return card;
}

function renderOneClickButton(action) {
  if (action.type === 'draft_email') {
    return `<button class="btn-primary" onclick="draftEmail('${action.template}')">Draft Email</button>`;
  } else if (action.type === 'archive') {
    return `<button class="btn-secondary" onclick="archiveApplication('${action.application_id}')">Archive</button>`;
  }
  // ... other action types
}
```

---

### **4.3 CSV Import (Handle Missing JDs)**

```javascript
// In importCSV():

async function importCSV(file) {
  const data = await parseCSV(file);
  
  // Detect columns
  const columnMapping = await fetch('/api/import/detect-columns', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ headers: data.headers, sample_rows: data.rows.slice(0, 5) })
  }).then(r => r.json());
  
  // Preview import
  const preview = data.rows.map(row => ({
    company: row[columnMapping.company],
    role: row[columnMapping.role],
    status: row[columnMapping.status],
    date_applied: row[columnMapping.date_applied],
    jd_source: row[columnMapping.job_description] ? 'user_provided' : 'missing'
  }));
  
  showImportPreview(preview);
  
  // On confirm:
  for (const row of preview) {
    if (row.jd_source === 'missing') {
      // Generate Provisional Role Profile in background
      const profile = await fetch('/api/jd/reconstruct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role_title: row.role,
          company_name: row.company
        })
      }).then(r => r.json());
      
      row.provisional_profile = profile.provisional_profile;
      row.confidence_label = 'directional';
    }
    
    await HenryData.saveApplication(row);
  }
  
  showSuccess(`Imported ${preview.length} applications`);
  reloadTracker();
}
```

---

### **4.4 Daily Pulse Banner**

```javascript
// Replace existing daily pulse with intelligence-driven banner:

function renderDailyPulse(intelligence) {
  const pulseDiv = document.getElementById('dailyPulse');
  
  const topActions = intelligence.focus_mode.top_actions.slice(0, 3);
  
  pulseDiv.innerHTML = `
    <div class="pulse-greeting">
      Good ${getTimeOfDay()}, ${getUserFirstName()}! Here's what matters today:
    </div>
    
    <div class="pulse-actions">
      ${topActions.map(action => `
        <div class="pulse-action-card">
          <strong>${action.company}</strong>
          <p>${action.action}</p>
          <button onclick="focusApplication('${action.application_id}')">Take Action</button>
        </div>
      `).join('')}
    </div>
    
    <div class="pulse-pipeline">
      ${intelligence.pipeline_health.recommendation}
      <span class="pipeline-reason">${intelligence.pipeline_health.reason}</span>
    </div>
  `;
}
```

---

### **4.5 Interview Intelligence Sync**

```javascript
// When interview is added in tracker:

async function addInterview(applicationId, interviewData) {
  // 1. Create interview record
  const interview = await HenryData.saveInterview({
    application_id: applicationId,
    date: interviewData.date,
    type: interviewData.type,
    company: interviewData.company,
    role: interviewData.role
  });
  
  // 2. Update application status
  await HenryData.updateApplication(applicationId, {
    status: `${interviewData.type} Scheduled`,
    substatus: 'prep_needed',
    last_activity_date: new Date().toISOString().split('T')[0]
  });
  
  // 3. Trigger intelligence recalculation
  await recalculateIntelligence();
  
  // 4. Refresh tracker
  reloadTracker();
}

// Interview intelligence page loads interviews:

async function loadInterviews() {
  const interviews = await HenryData.getInterviews();
  
  interviews.forEach(async interview => {
    // Check if prep guide exists
    const hasPrepGuide = interview.prep_guide_generated;
    
    if (!hasPrepGuide) {
      // Generate prep guide (works with or without real JD)
      const application = await HenryData.getApplication(interview.application_id);
      
      const prepGuide = await fetch('/api/interview-prep/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          application_id: interview.application_id,
          interview_type: interview.type,
          jd_source: application.jd_source,
          provisional_profile: application.provisional_profile,
          real_jd: application.job_description,
          resume: getUserResume()
        })
      }).then(r => r.json());
      
      // Store prep guide
      interview.prep_guide = prepGuide;
    }
  });
  
  renderInterviews(interviews);
}
```

---

## **5. Cron Jobs / Background Tasks**

### **5.1 Daily Intelligence Recalculation**

```javascript
// Run every 24 hours:

async function dailyIntelligenceUpdate() {
  const allUsers = await getAllUsers();
  
  for (const user of allUsers) {
    const applications = await HenryData.getApplications(user.id);
    
    // Update days_since_last_activity for each application
    applications.forEach(app => {
      app.days_since_last_activity = calculateDaysSince(app.last_activity_date);
    });
    
    // Recalculate intelligence
    const intelligence = await fetch('/api/tracker/intelligence', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: user.id, applications })
    }).then(r => r.json());
    
    // Update applications with new next_actions
    for (const action of intelligence.priority_actions) {
      await HenryData.updateApplication(action.application_id, {
        next_action: action.action,
        next_action_reason: action.reason,
        priority_level: action.priority,
        days_since_last_activity: applications.find(a => a.id === action.application_id).days_since_last_activity
      });
    }
  }
}
```

---

### **5.2 Interview Reminders**

```javascript
// Run every 12 hours:

async function sendInterviewReminders() {
  const upcomingInterviews = await getInterviewsInNext48Hours();
  
  for (const interview of upcomingInterviews) {
    const hoursBefore = calculateHoursBefore(interview.date);
    
    if (hoursBefore <= 48 && !interview.prep_reminder_sent) {
      // Send 48-hour prep reminder
      await sendNotification(interview.user_id, {
        type: 'interview_prep',
        message: `Interview at ${interview.company} in 2 days. Review prep guide now.`,
        action_url: `/interview-intelligence.html?interview_id=${interview.id}`
      });
      
      await HenryData.updateInterview(interview.id, {
        prep_reminder_sent: true
      });
    }
    
    if (hoursBefore <= 1 && !interview.final_reminder_sent) {
      // Send 1-hour final reminder
      await sendNotification(interview.user_id, {
        type: 'interview_final',
        message: `Interview in 1 hour. Review your intro: [link]`,
        action_url: `/interview-intelligence.html?interview_id=${interview.id}#intro`
      });
      
      await HenryData.updateInterview(interview.id, {
        final_reminder_sent: true
      });
    }
  }
}
```

---

## **6. Testing Checklist**

### **Missing JD Handling**
- [ ] Import CSV with no JD column → applications create successfully
- [ ] Application without JD → generates Provisional Role Profile
- [ ] Fit analysis with inferred JD → returns "directional" label
- [ ] Interview prep with inferred JD → generates successfully
- [ ] UI shows "Directional" badge on inferred applications
- [ ] Adding real JD later → updates confidence_label to "refined"

### **Intelligence Engine**
- [ ] Day 7 post-apply → action = "Send follow-up email"
- [ ] Day 14 post-apply → action = "Mark ghosted or final check-in"
- [ ] Day 21 post-apply → action = "Archive this application"
- [ ] Recruiter screen scheduled → action = "Review prep guide now"
- [ ] Low decision confidence → action = "Deprioritize or withdraw"
- [ ] 3+ interviews next week → pipeline action = "Block prep time"
- [ ] No applications in 7 days → pipeline action = "Apply to 3 roles"

### **One-Click Actions**
- [ ] "Send follow-up email" → drafts email template
- [ ] "Archive this application" → archives with confirmation
- [ ] "Review prep guide" → opens interview intelligence
- [ ] "Block prep time" → exports calendar .ics

### **Interview Intelligence Sync**
- [ ] Add interview in tracker → creates interview record
- [ ] Interview added → updates application status
- [ ] Interview intelligence page → loads interviews from tracker
- [ ] Complete prep → updates substatus to "prep_complete"
- [ ] Complete debrief → updates status to "Awaiting Feedback"

### **Focus Mode**
- [ ] Focus mode enabled → dims non-priority applications
- [ ] Top 2-3 actions visible → rest hidden behind "View all"
- [ ] Priority applications highlighted

### **CSV Import**
- [ ] Drag CSV → AI detects columns
- [ ] Preview shows missing JDs → no warnings
- [ ] Import → creates applications with inferred profiles
- [ ] Import validation → flags missing status

---

## **7. Success Criteria**

The Command Center succeeds if:

1. **Every action answers "what/why" in ≤10 words**
2. **Candidates never blocked by missing JDs**
3. **System actively discourages low-leverage actions**
4. **Focus Mode reduces cognitive load**
5. **Intelligence engine guides decisions, not just tracks activity**

---

## **8. Out of Scope (For Now)**

These are future enhancements, not v2.0:

- Google Calendar OAuth sync
- SMS reminders
- Email digest
- Timeline graph view
- Benchmarking dashboard
- LinkedIn/Greenhouse inbox import

Focus: Get the decision intelligence layer working first.

---

## **9. Action Audit Reference**

Every tracker state must pass this test. Here's the complete action matrix:

### **Application Status: Applied**

| Days | Action | Why It Matters | Words |
|------|--------|----------------|-------|
| 0-6 | None—wait | Most responses Days 3-7. Wait. | 6 |
| 7 | Send follow-up email | 70% respond by now. Silence = ghosting. | 7 |
| 14 | Mark ghosted or final check-in | Dead deal. Stop tracking. Move on. | 6 |
| 21 | Archive this application | You're wasting mental energy. It's over. | 7 |

### **Application Status: Recruiter Screen**

| State | Action | Why It Matters | Words |
|-------|--------|----------------|-------|
| Scheduled | Review prep guide now | Recruiters screen out 60%. Be ready. | 6 |
| Complete (0-5 days) | None—wait for next steps | Typical response: 3-5 days. Don't follow up. | 7 |
| Complete (5+ days) | Send status check-in | They're deciding or ghosting. Force clarity. | 6 |

### **Application Status: Other Stages**

| Stage | Action | Why It Matters | Words |
|-------|--------|----------------|-------|
| Hiring Manager Scheduled | Prepare 3 scope-alignment stories | This stage kills 40%. Prove you fit. | 7 |
| Technical/Panel Scheduled | Practice technical depth questions | You're competing now. Differentiate or lose. | 6 |
| Final Round Scheduled | Practice executive presence now | They're testing culture fit. Be confident. | 7 |
| Final Round Complete (0-3 days) | Send thank-you + reiterate interest | Decisions happen Days 3-7. Stay visible. | 6 |
| Final Round Complete (7+ days) | Request feedback or close mentally | 7+ days = probably rejection. Get clarity. | 8 |
| Offer Received | None—negotiate or accept thoughtfully | Don't rush. This locks 2+ years. | 6 |

### **Decision Confidence Guidance**

| Confidence | Action | Why It Matters | Words |
|------------|--------|----------------|-------|
| Low (<40%) | Deprioritize or withdraw | This is low-leverage. Focus better bets. | 6 |
| Medium (40-70%) | Continue but don't overinvest | Decent fit. Watch for stalls. | 5 |
| High (70%+) | Prioritize—stay aggressive here | Strong alignment. This is worth energy. | 6 |

### **Pipeline Health Guidance**

| Condition | Action | Why It Matters | Words |
|-----------|--------|----------------|-------|
| Thin (<3 active) | Apply to 3 new roles now | Pipeline's too thin. You need momentum. | 6 |
| Healthy (5-8 active) | None—maintain pace, focus on interviews | Good volume. Shift energy to conversion. | 6 |
| Overloaded (10+ active) | Pause applications. Focus on interviews only. | You're spreading thin. Convert what you have. | 8 |
| Low interview rate (<10%) | Revise resume positioning immediately | Your applications aren't landing. Fix messaging. | 6 |
| **Strategic stop (interview rate <5% after 10+ apps)** | **Stop applying. Fix your positioning.** | **Something's broken. Diagnose before continuing.** | **6** |
| High interview rate (20%+) | Apply more—you're converting well | You're winning. Scale volume now. | 5 |
| High ghosting rate (>40%) | Analyze rejections. Something's breaking late. | You're advancing then failing. Diagnose why. | 6 |
| 3+ interviews next week | Block 6 hours prep time today | Unprepared interviews waste everyone's time. | 5 |
| No applications in 7+ days | Apply to 2 roles today | Momentum's gone. Restart or quit intentionally. | 6 |
| No interviews in 14+ days | Revise positioning or increase volume | You're not landing. Change strategy now. | 6 |

---

## **10. UI Signals Contract**

The backend must emit **UI-ready signals** so visual redesign can bind cleanly without refactoring logic.

### **Application-Level Signals**

Every application object returned by the API must include:

```javascript
{
  // Existing fields
  "id": "app123",
  "company": "Stripe",
  "role": "Senior Product Manager",
  "status": "Applied",
  "fit_score": 72,
  
  // NEW: UI-ready signals
  "ui_signals": {
    "priority": "high",           // "high" | "medium" | "low" | "archive"
    "confidence": "medium",        // "high" | "medium" | "low"
    "urgency": "immediate",        // "immediate" | "soon" | "routine" | "none"
    "color_code": "yellow",        // "green" | "yellow" | "red" | "gray"
    "icon": "⚠️",                  // emoji or icon identifier
    "badge": "directional",        // "directional" | "refined" | null
    "action_available": true,      // boolean (is there a one-click action?)
    "dimmed": false                // boolean (should be dimmed in focus mode?)
  },
  
  // Action guidance (already specified)
  "next_action": "Send follow-up email",
  "next_action_reason": "70% respond by now. Silence = ghosting.",
  "one_click_action": { ... }
}
```

### **Signal Calculation Rules**

#### **Priority**
```javascript
if (decision_confidence < 40) return "low";
if (days_since_last_activity >= 21) return "archive";
if (next_action !== "None—wait" && urgency === "immediate") return "high";
if (decision_confidence >= 70) return "high";
return "medium";
```

#### **Confidence**
```javascript
if (decision_confidence >= 70) return "high";
if (decision_confidence >= 40) return "medium";
return "low";
```

#### **Urgency**
```javascript
if (status === "Applied" && days_since_last_activity === 7) return "immediate";
if (status === "Applied" && days_since_last_activity === 14) return "immediate";
if (interview_tomorrow) return "immediate";
if (next_action.includes("Archive")) return "immediate";
if (next_action === "None—wait") return "none";
if (days_since_last_activity >= 5 && status.includes("Complete")) return "soon";
return "routine";
```

#### **Color Code**
```javascript
if (confidence === "high") return "green";
if (confidence === "medium") return "yellow";
if (confidence === "low") return "red";
if (priority === "archive") return "gray";
```

#### **Icon**
```javascript
if (urgency === "immediate") return "⚠️";
if (priority === "high" && confidence === "high") return "🔥";
if (priority === "low") return "❄️";
if (next_action === "None—wait") return "⏳";
if (priority === "archive") return "📦";
return "📋";
```

#### **Badge**
```javascript
if (jd_source === "inferred" || jd_source === "missing") return "directional";
if (jd_source === "user_provided" || jd_source === "url_fetched") return "refined";
return null;
```

#### **Dimmed**
```javascript
// Only relevant in focus mode
if (priority === "low" || priority === "archive") return true;
if (!focus_mode_enabled) return false;
if (priority === "high") return false;
return true;
```

---

### **Pipeline-Level Signals**

The intelligence endpoint must also return pipeline-level UI signals:

```javascript
{
  "pipeline_health": {
    "status": "healthy",           // "healthy" | "thin" | "overloaded" | "stalled"
    "color": "green",              // "green" | "yellow" | "red"
    "icon": "✅",                   // emoji
    "tone": "steady",              // "steady" | "caution" | "urgent"
    "recommendation": "None—maintain pace, focus on interviews",
    "reason": "Good volume. Shift energy to conversion.",
    "active_count": 5,
    "priority_count": 2            // number of high-priority actions
  },
  
  "focus_mode": {
    "enabled": true,
    "top_actions": [...],
    "dim_others": true
  }
}
```

#### **Pipeline Status**
```javascript
if (active_count < 3) return "thin";
if (active_count > 10) return "overloaded";
if (interview_rate < 5 && active_count >= 5) return "stalled";
return "healthy";
```

#### **Pipeline Color**
```javascript
if (status === "healthy") return "green";
if (status === "thin" || status === "overloaded") return "yellow";
if (status === "stalled") return "red";
```

#### **Pipeline Tone**
```javascript
if (status === "stalled") return "urgent";
if (status === "thin" && days_since_last_application > 7) return "urgent";
if (status === "overloaded" && interview_rate < 10) return "caution";
if (active_count >= 3 && interview_rate >= 15) return "steady";
return "caution";
```

---

### **Frontend Binding Examples**

With these signals, the UI can bind cleanly:

```javascript
// Color-code application card
card.classList.add(`confidence-${app.ui_signals.confidence}`);
card.style.borderColor = `var(--color-${app.ui_signals.color_code})`;

// Show urgency indicator
if (app.ui_signals.urgency === "immediate") {
  card.classList.add('urgent');
}

// Show badge
if (app.ui_signals.badge === "directional") {
  badgeEl.textContent = "Directional";
  badgeEl.classList.add('badge-directional');
}

// Dim in focus mode
if (app.ui_signals.dimmed) {
  card.style.opacity = "0.3";
}

// Show icon
iconEl.textContent = app.ui_signals.icon;
```

---

### **Why This Matters**

**Without UI signals:**
Frontend has to replicate backend logic:
```javascript
// BAD: Frontend calculates color
const color = app.decision_confidence >= 70 ? 'green' : 
              app.decision_confidence >= 40 ? 'yellow' : 'red';
```

**With UI signals:**
Frontend just binds:
```javascript
// GOOD: Backend already calculated
const color = app.ui_signals.color_code;
```

**Benefits:**
1. Visual redesign doesn't touch logic
2. A/B testing different visual treatments is trivial
3. Backend owns all decision-making
4. Frontend is pure presentation layer

---

## **Section X: Data Migration & Backward Compatibility**

**Objective:** Deploy the new Command Center intelligence and UI signal framework without deleting, mutating, or invalidating any existing candidate data. This release must be strictly additive.

### **1. Additive Schema Changes Only**

All new fields introduced by this spec must:
- Be nullable
- Have no NOT NULL constraints
- Have no default values that overwrite existing records

**Additive Fields:**
```sql
ALTER TABLE applications ADD COLUMN IF NOT EXISTS priority VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS urgency VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS confidence VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS color_code VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS icon VARCHAR(10);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS badge VARCHAR(50);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS dimmed BOOLEAN;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS decision_confidence_score INTEGER;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS provisional_role_profile JSONB;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS ui_signal_version VARCHAR(10) DEFAULT 'v0';
```

**Existing columns must NOT be:**
- Renamed
- Re-typed
- Deleted
- Reinterpreted

All existing data is considered authoritative historical fact.

### **2. No Destructive Migrations**

Under no circumstances should this deployment:
- Delete application records
- Delete interview records
- Reset user-entered statuses or notes
- Modify historical timestamps (applied_date, interview_date, feedback_date)

### **3. Intelligence Is an Overlay, Not a Rewrite**

All intelligence outputs (signals, confidence, urgency, recommendations) must be:
- Computed at read-time or via background jobs
- Stored separately from user-entered fields
- Treated as derived interpretations, not ground truth

**If intelligence is unavailable or fails to compute:**
- Fall back to neutral defaults
- Do not block rendering

**Fallback Defaults:**
```javascript
const SAFE_DEFAULTS = {
  priority: 'medium',
  urgency: 'routine',
  confidence: 'medium',
  color_code: 'gray',
  icon: '📋',
  badge: null,
  dimmed: false,
  next_action: 'Review application',
  next_action_reason: 'Action pending analysis'
};
```

### **4. Lazy Backfill Strategy**

**No bulk backfill jobs at deploy time.**

Instead:
- Compute signals when an application is viewed
- Compute pipeline health when dashboard loads
- Cache results opportunistically

**Benefits:**
- Safe rollback
- Gradual rollout
- Reduced blast radius

**Implementation:**
```javascript
async function loadApplication(app_id) {
  const app = await supabase.from('applications').select('*').eq('id', app_id).single();
  
  // If signals missing or stale, compute
  if (!app.ui_signal_version || app.ui_signal_version === 'v0') {
    const signals = await computeSignals(app);
    await supabase.from('applications').update(signals).eq('id', app_id);
    return { ...app, ...signals };
  }
  
  return app;
}
```

### **5. Versioned Signal Framework**

Introduce `ui_signal_version` (e.g., v0, v1).

**Behavior:**
- Legacy records default to v0
- New logic emits v1 signals
- UI reads signals based on version

**Example:**
```javascript
function renderCard(app) {
  if (app.ui_signal_version === 'v1') {
    return renderIntelligentCard(app);  // New signals
  } else {
    return renderLegacyCard(app);       // Safe fallback
  }
}
```

This allows future iteration without corrupting legacy assumptions.

### **6. Feature Flag / Kill Switch**

All new intelligence logic must be gated behind a feature flag.

**Implementation:**
```javascript
const FEATURES = {
  INTELLIGENCE_ENGINE: false,  // Toggle without redeploy
  FOCUS_MODE: false,
  STRATEGIC_STOP: false
};

function loadTracker() {
  if (FEATURES.INTELLIGENCE_ENGINE) {
    return loadIntelligentTracker();
  } else {
    return loadBasicTracker();  // Classic mode
  }
}
```

**Kill Switch Behavior:**
- Ability to disable signals globally
- Tracker reverts to basic tracking mode if disabled
- No redeploy required

### **7. Pre-Deployment Safety Checks**

Before deploying:

- [ ] Full database snapshot / backup
- [ ] Staging test with real legacy data
- [ ] Verification that tracker renders correctly with:
  - Missing signals
  - Partially populated records
  - Legacy-only records
- [ ] Null-safety audit on all new code paths
- [ ] Rollback plan documented and tested

### **8. Post-Deployment Monitoring**

After deploy:

- Monitor error rates on tracker load
- Log signal computation failures
- Alert on unexpected null access
- Track feature flag toggle frequency (panic indicator)

**Alert Thresholds:**
- Tracker load error rate > 1%
- Signal computation failure > 5%
- Null access errors > 0

**Monitoring Dashboard:**
```javascript
{
  "tracker_loads": 1247,
  "signal_computations": 1198,
  "signal_failures": 23,       // 1.9% - within threshold
  "null_errors": 0,            // Good
  "fallback_renders": 49,      // 3.9% - acceptable
  "feature_flag_off_count": 2  // Low - not panic mode
}
```

Any anomaly defaults to non-intelligent fallback, not broken UI.

---

### **Guiding Principle**

**Candidate trust is the product. Intelligence augments data; it never rewrites history.**

---

## **QA Checklist**

Claude must pass before marking "done":

### **Data Safety**
- [ ] Existing applications render with zero data loss
- [ ] Existing interviews still linked correctly
- [ ] No user-entered fields overwritten
- [ ] Null-safe rendering everywhere (no crashes on missing signals)

### **Backward Compatibility**
- [ ] Legacy records (no new fields) load cleanly
- [ ] Mixed records (some signals present, some null) behave correctly
- [ ] Tracker still works with intelligence feature flag OFF

### **Signal Integrity**
- [ ] Each application emits: priority, urgency, confidence, color_code, badge, dimmed
- [ ] Signals change only when underlying facts change
- [ ] No UI recomputes logic client-side

### **Decision Guidance**
- [ ] At least one clear "next action" per active application
- [ ] System can recommend: follow up, wait, deprioritize, disengage
- [ ] "Do nothing" is a valid outcome

### **Missing JD Flow**
- [ ] Applications without JDs: still trackable, still analyzable (directional), can generate interview prep
- [ ] Prep clearly labeled as inferred when applicable

### **Interview Intelligence Sync**
- [ ] Adding interview in tracker → appears in Interview Intelligence
- [ ] Completing prep/debrief updates application state
- [ ] No duplicate interviews created

### **Calendar**
- [ ] .ics export works for single interview
- [ ] .ics export works for all upcoming interviews
- [ ] Calendar events include correct date/time/stage

### **Focus Mode**
- [ ] Dimmed logic respected
- [ ] Only top 2-3 actions remain visually emphasized
- [ ] No action disappears entirely

### **Error Handling**
- [ ] Signal computation failure → neutral fallback
- [ ] No broken cards
- [ ] No blocking errors

### **Performance**
- [ ] Tracker load < acceptable threshold with intelligence ON
- [ ] No runaway background jobs

---

## **Launch Checklist**

### **Beta Launch (Controlled Risk)**

**Before:**
- [ ] Feature flag ON for beta users only
- [ ] DB snapshot taken
- [ ] Logging enabled for: signal computation, decision_confidence, missing JD inference
- [ ] UI shows subtle "beta" indicator

**During:**
- [ ] Monitor: tracker load errors, signal null rates, prep generation failures
- [ ] Watch where users hesitate or override recommendations

**After:**
- [ ] Collect: "Was this helpful?" feedback on nudges, which actions users ignore
- [ ] Adjust signal thresholds, not UI

### **Prod Launch (Trust Protection Mode)**

**Before:**
- [ ] Feature flag default OFF
- [ ] Confirm rollback works in < 5 minutes
- [ ] Validate prod data against staging assumptions

**Rollout:**
- [ ] Gradual enablement: 10% → 25% → 50% → 100%
- [ ] Monitor: error rate, engagement drop, confusion signals (rapid toggling, overrides)

**If Anything Feels Off:**
- [ ] Flip flag OFF
- [ ] Tracker reverts to basic mode
- [ ] No data touched
- [ ] No user impact

---

### **Non-Negotiable Rule**

**Intelligence can fail. The tracker must never fail.**

---

**End of Spec**

This spec is ready for implementation. Backend emits UI-ready signals. Visual redesign can bind cleanly without refactoring.
