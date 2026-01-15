# HENRYHQ COMPREHENSIVE TEST SCRIPT v1.0

**Date:** December 25, 2025
**Purpose:** Complete testing checklist combining new Phase 2 features + outstanding pre-launch tests
**Estimated Time:** 90-120 minutes total

---

## SECTION A: NEW HEY HENRY FEATURES (December 25, 2025)

These features were shipped today and need validation before beta rollout.

---

### TEST A1: CONVERSATION HISTORY PERSISTENCE

**What we're testing:** Chats persist across browser sessions

**Why it matters:** Alex validated this need. 45-minute conversations were being lost. This is the foundation for longitudinal intelligence.

#### Steps:

1. Open Hey Henry
2. Have a brief conversation:
   > "Hey Henry, I'm thinking about applying to Stripe. What do you think?"
3. Wait for response
4. **Close browser completely** (not just tab)
5. Reopen browser, go to HenryHQ
6. Open Hey Henry

#### Expected Results:
- [ ] "Continue Conversation" vs "Start Fresh" prompt appears
- [ ] Click "Continue" → Previous conversation loads
- [ ] Click "History" → See list of past conversations
- [ ] Previous messages display with correct timestamps
- [ ] Can scroll through full conversation history

#### Edge Cases:
- [ ] Multiple conversations in history list display correctly
- [ ] Starting fresh actually clears and begins new conversation
- [ ] Works on mobile (Alex's primary use case)

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A2: PIPELINE PATTERN ANALYSIS

**What we're testing:** Hey Henry analyzes search patterns when asked

**Why it matters:** This is the "strategic intelligence" differentiator. Users need to see patterns across their search, not just individual role analysis.

#### Prerequisites:
- 5+ applications in pipeline (various stages and fit scores)

#### Steps:

1. Open Hey Henry
2. Ask: "How's my job search going?"
3. Wait for response

#### Expected Results:
- [ ] Response includes "Pipeline Health" summary (total apps, active, interviewing, rejected)
- [ ] Response includes "Patterns I'm Seeing" with specific insights
- [ ] If overreaching: mentions fit score distribution (e.g., "8 of 12 were reaches")
- [ ] If stalled: mentions days since activity
- [ ] Conversion rates mentioned (application → interview → offer)
- [ ] Ends with specific, actionable recommendation

#### Trigger Phrases to Test:
| Phrase | Expected Behavior |
|--------|-------------------|
| "How's my search going?" | Full pattern analysis |
| "Review my applications" | Full pattern analysis |
| "What patterns do you see?" | Full pattern analysis |
| "Am I doing something wrong?" | Pattern analysis + diagnostic |
| "Why am I not getting interviews?" | Pattern analysis focused on conversion |

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A3: PROACTIVE NETWORK SURFACING

**What we're testing:** LinkedIn connections surface during role analysis

**Why it matters:** Warm intros get 3x response rate. Users shouldn't have to navigate to a separate page to discover they know someone at the target company.

#### Prerequisites:
- LinkedIn CSV uploaded to profile
- Target company has at least one connection in your network

#### Steps:

1. Go to Analyze page
2. Paste a job description from a company where you have connections
3. Complete the analysis
4. Open Hey Henry
5. Ask: "What do you think about this role?"

#### Expected Results:
- [ ] Response mentions LinkedIn connections at the company
- [ ] Shows connection name and title
- [ ] Shows when you connected (relationship strength signal)
- [ ] Offers to draft outreach message

#### No Connections Scenario:
1. Analyze a role at a company where you have NO connections
2. Ask Hey Henry about the role

- [ ] Suggests alternative paths (industry connections, alumni network)
- [ ] Offers cold outreach strategy
- [ ] Links to Outreach page for templates

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A4: REJECTION FORENSICS

**What we're testing:** Hey Henry diagnoses rejection patterns

**Why it matters:** Candidates don't know why they're getting rejected. Stage-specific diagnosis helps them fix the actual problem.

#### Prerequisites:
- 3+ applications marked as "Rejected" in pipeline
- Ideally with rejection stage noted (resume screen, recruiter, HM, final)

#### Steps:

1. Open Hey Henry
2. Ask: "Why do I keep getting rejected?"
3. Wait for response

#### Expected Results:
- [ ] Response acknowledges rejection count
- [ ] Breaks down rejections by stage (resume screen, recruiter, HM, final)
- [ ] Provides stage-specific diagnosis:
  - Resume screen: "Materials might be missing key terms"
  - Recruiter: "Could be salary mismatch or communication red flags"
  - HM: "Usually culture fit or scope concerns"
  - Final: "Often competition or factors outside your control"
- [ ] Identifies systemic patterns (same stage, same company type)
- [ ] Offers specific recommendation to address pattern

#### Trigger Phrases to Test:
| Phrase | Expected Behavior |
|--------|-------------------|
| "Why do I keep getting rejected?" | Full rejection forensics |
| "Analyze my rejections" | Full rejection forensics |
| "I'm not landing interviews" | Focus on resume screen rejections |
| "What's wrong with my approach?" | Diagnostic analysis |

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A5: OUTREACH TRACKING

**What we're testing:** Outreach logging and follow-up prompts

**Why it matters:** Users reach out but forget to follow up. Opportunities slip through cracks.

#### Part A: Log Outreach

1. Open Hey Henry
2. Ask: "Can you draft an outreach message to a hiring manager at [Company]?"
3. After Hey Henry provides the message, observe follow-up

#### Expected Results (Part A):
- [ ] Hey Henry drafts outreach message
- [ ] Asks "Did you send this? I'll track it for follow-up"
- [ ] If confirmed, outreach logged

#### Part B: Verify Logging

1. Open dev tools → Console
2. Run: `localStorage.getItem('outreachLog')`

#### Expected Results (Part B):
- [ ] JSON array contains logged outreach with:
  - contactName
  - company
  - channel
  - sentAt timestamp
  - status: 'pending'

#### Part C: Follow-up Reminder (Simulated)

1. Manually adjust outreach date in localStorage to 6 days ago
2. Refresh page, open Hey Henry

#### Expected Results (Part C):
- [ ] Hey Henry mentions pending follow-ups in greeting or tooltip
- [ ] "You reached out to [Name] at [Company] X days ago. No response. Want to follow up?"
- [ ] Offers to draft follow-up message

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A6: INTERVIEW DEBRIEF INTELLIGENCE

**What we're testing:** Structured extraction from debrief conversations

**Why it matters:** This is how the intelligence compounds. Raw debrief chat → structured data → informs future prep.

#### Steps:

1. Open Hey Henry
2. Start a debrief conversation:
   > "I just finished an interview at [Company]. Can we debrief?"
3. Answer Hey Henry's questions about:
   - How it went overall (rating)
   - What questions they asked
   - What went well (wins)
   - What you struggled with (stumbles)
   - Any stories you told
4. Complete the debrief conversation naturally
5. Check Supabase → `interview_debriefs` table

#### Expected Results:
- [ ] Debrief conversation flows naturally (not robotic questionnaire)
- [ ] Hey Henry asks follow-up questions based on responses
- [ ] After conversation ends, extraction triggers
- [ ] Supabase shows new row with structured data:

| Field | Expected |
|-------|----------|
| `interview_type` | Populated (recruiter/HM/technical/panel/final) |
| `rating_overall` | 1-5 rating |
| `questions_asked` | Array of questions mentioned |
| `stumbles` | Array of struggles mentioned |
| `wins` | Array of successes mentioned |
| `stories_used` | Array of examples/stories told |
| `key_insights` | AI-generated insights |

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A7: INTERVIEW PROGRESSION PROMPTS

**What we're testing:** Proactive prompts for users with upcoming interviews but missing debriefs

**Why it matters:** Users shouldn't go into panel interviews without processing what happened in earlier rounds.

#### Prerequisites:
- Application with "Panel Interview" or later stage scheduled
- No debrief exists for earlier rounds at that company

#### Steps:

1. Ensure you have an application at Panel/Final stage without prior debriefs
2. Open Hey Henry
3. Check tooltip or greeting message

#### Expected Results:
- [ ] Hey Henry mentions upcoming interview
- [ ] Prompts to debrief earlier rounds first
- [ ] Message like: "Before your panel interview at [Company], let's debrief your HM round. Those insights could help."

#### Variations:
| Stage | Expected Prompt |
|-------|-----------------|
| Panel scheduled, no HM debrief | Prompt to debrief HM round |
| Final scheduled, no prior debriefs | Prompt to debrief earlier rounds |
| Interview completed, no debrief | "How did your interview at [Company] go? Want to debrief?" |

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A8: DEBRIEF-INFORMED INTERVIEW PREP

**What we're testing:** Interview prep pulls from past debriefs

**Why it matters:** This closes the intelligence loop. Past struggles should inform future prep.

#### Prerequisites:
- At least one completed debrief for a company (from Test A6)
- Upcoming interview at the SAME company

#### Steps:

1. Complete a debrief for Company X (if not already done)
2. Go to Interview Prep page
3. Start prep for another interview at Company X (different round)
4. Review the prep output

#### Expected Results:
- [ ] Prep references past debrief: "In your recruiter screen, you mentioned..."
- [ ] Addresses stumbles from past rounds: "You struggled with X last time. Here's how to handle it..."
- [ ] Recommends stories that worked: "Your [Story Name] resonated. Use it again if relevant."
- [ ] Does NOT give generic prep that ignores debrief data

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A9: STORY BANK UI

**What we're testing:** Story Bank displays and functions correctly

**Why it matters:** Users need to see their story inventory, identify overused stories, and develop new ones.

#### Part A: View Stories

1. Navigate to Story Bank (Interview Intelligence → Practice → Story Bank)
2. Review the page

#### Expected Results (Part A):
- [ ] Stats bar shows correct counts (Total, High Impact, Overused, Needs Work)
- [ ] Stories display as cards (if any exist from debriefs)
- [ ] Status badges show correctly:
  - ✅ High Impact (effectiveness >= 4.0)
  - ⚠️ Overused (times_used >= 3)
  - 🆕 New (times_used = 0)
  - 📝 Needs Work (no summary)
- [ ] Empty state shows if no stories (with guidance)

#### Part B: Add Story

1. Click "+ Add New Story"
2. Fill in:
   - Story Name: "Test Story - Launch Under Pressure"
   - Demonstrates: Add tags (Leadership, Deadline Management)
   - Best for questions: "Tell me about a time you delivered under pressure"
   - Story summary: Write brief STAR narrative
3. Save

#### Expected Results (Part B):
- [ ] Modal opens correctly
- [ ] Tags can be added and removed
- [ ] Save creates story in Supabase
- [ ] Story appears in list without page refresh
- [ ] Stats bar updates

#### Part C: Edit Story

1. Click Edit on an existing story
2. Change the name or add content
3. Save

#### Expected Results (Part C):
- [ ] Modal pre-fills with existing data
- [ ] Changes save correctly to Supabase
- [ ] List updates without refresh

#### Part D: Delete Story

1. Click overflow menu (⋮) on a story
2. Click Delete
3. Confirm

#### Expected Results (Part D):
- [ ] Confirmation modal appears
- [ ] Story removed from Supabase
- [ ] List updates without refresh
- [ ] Stats bar updates

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A10: CROSS-INTERVIEW PATTERN DETECTION

**What we're testing:** Patterns surface after 3+ debriefs

**Why it matters:** "This is the third time you stumbled on X" is the compound intelligence users expect.

#### Prerequisites:
- 3+ debriefs completed in Supabase
- At least one recurring pattern (e.g., struggled with same question type multiple times)

#### Steps:

1. Ensure 3+ debriefs exist with overlapping weak areas (e.g., "why this company" struggles)
2. Open Hey Henry
3. Ask: "What patterns do you see in my interviews?"

#### Expected Results:
- [ ] Response identifies recurring weak categories
- [ ] Specific: "You've struggled with [category] in X of Y interviews"
- [ ] Shows confidence trend (improving/declining/stable)
- [ ] Flags overused stories if applicable
- [ ] Offers to work on weak areas

#### Automatic Pattern Surfacing:

After completing a debrief (when patterns exist):
- [ ] Hey Henry proactively mentions pattern: "I noticed this is the Nth time you've struggled with X"
- [ ] Offers to address it: "Want to work on a stronger approach?"

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST A11: CONTEXT-AWARE TOOLTIPS

**What we're testing:** Tooltips adapt to user state (not random rotation)

**Why it matters:** Tooltips should feel like a proactive coach, not random tips.

#### Steps:

Set up different states and observe tooltip behavior:

| State | How to Create | Expected Tooltip |
|-------|---------------|------------------|
| Pipeline stalled | No activity for 3+ days | "X apps, no movement. Want to review strategy?" |
| Interview tomorrow | Schedule interview for tomorrow | "Interview at [Company] tomorrow. Prepped?" |
| Recent rejection | Mark application as rejected | "That [Company] rejection sucked. Want to talk through it?" |
| Outreach pending | Log outreach 5+ days ago | "You have pending follow-ups. Check in?" |
| No urgent state | Active pipeline, no issues | Generic: "Got questions?" or "Need strategy help?" |

#### Steps:
1. Create the state (e.g., don't use app for 3 days, or schedule interview for tomorrow)
2. Open HenryHQ
3. Wait for tooltip to appear on FAB (20-40 seconds)
4. Observe tooltip text

#### Expected Results:
- [ ] Tooltip changes based on context
- [ ] Not random rotation
- [ ] Relevant to current user state
- [ ] Clicking tooltip opens Hey Henry with relevant context

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

## SECTION B: OUTSTANDING PRE-LAUNCH TESTS

These tests were identified in previous sessions but not yet completed.

---

### TEST B1: HEY HENRY CONTEXT AWARENESS

**What we're testing:** Hey Henry knows what page user is on and references actual data

**Why it matters:** If Henry gives generic ChatGPT-style answers, users won't see the value. Henry should feel like a recruiter who knows their situation.

#### Test Scenarios:

| # | Page | Prompt | Pass Criteria |
|---|------|--------|---------------|
| 1 | documents.html | "Why did you change my summary?" | References specific changes made, mentions JD alignment |
| 2 | tracker.html | "What should I focus on today?" | References actual applications by company name |
| 3 | results.html | "Is this role worth applying to?" | References fit score, specific strengths/gaps for THIS role |
| 4 | interview-intelligence.html | "What questions should I expect?" | References company/role, not generic questions |
| 5 | positioning.html | "What's my biggest weakness for this role?" | Names specific gap from analysis |

#### Steps:

1. Navigate to each page listed above
2. Open Hey Henry
3. Ask the prompt
4. Evaluate response

#### Expected Results:
- [ ] Documents: References specific positioning decisions made
- [ ] Tracker: References actual applications by company name
- [ ] Results: References fit score and specific strengths/gaps
- [ ] Interview Intelligence: Company/role-specific questions
- [ ] Positioning: Names actual gaps from analysis

#### Conversation Persistence Across Pages:
1. Ask something on results.html
2. Navigate to documents.html with chat open
3. Check if conversation history persists

- [ ] Previous messages still visible
- [ ] Context maintained

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST B2: MOCK INTERVIEW FEEDBACK QUALITY

**What we're testing:** Mock interview questions are relevant, feedback is specific

**Why it matters:** This is the highest-touch feature. If it feels robotic or generic, top candidates won't use it.

#### Prerequisites:
- A role with analysis complete
- Access to Interview Intelligence → Practice tab

#### Steps:

1. Go to Interview Intelligence for an analyzed role
2. Navigate to Practice tab
3. Start a Mock Interview session
4. Select interview type (Recruiter Screen recommended for speed)
5. Answer 3-4 questions
6. Review feedback

#### Expected Results:

**Questions:**
- [ ] Questions are relevant to the specific role/company
- [ ] Mix of behavioral and role-specific questions
- [ ] Not generic "tell me about yourself" only
- [ ] Appropriate difficulty for interview type

**Feedback:**
- [ ] References your actual answer (not generic)
- [ ] Mentions specific strengths
- [ ] Identifies specific improvements
- [ ] References resume/background where relevant
- [ ] Suggests better framing or examples

**Voice Input (if testing):**
- [ ] Microphone prompt appears
- [ ] Speech-to-text works accurately
- [ ] Can also type if preferred

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST B3: SCREENING QUESTIONS ANALYSIS

**What we're testing:** Screening questions get strategic analysis and honest answers

**Why it matters:** Bad screening answers cause auto-rejection. Users need strategic but honest responses.

#### Steps:

1. Go to Screening Questions page (or Ask Henry)
2. Paste 3-4 real screening questions, e.g.:
   - "Do you have experience with [specific technology]?"
   - "What are your salary expectations?"
   - "Are you authorized to work in the US?"
   - "Why are you interested in this role?"
3. Request analysis

#### Expected Results:

**Analysis:**
- [ ] Identifies auto-rejection risk for each question
- [ ] Flags questions that need careful handling (salary, authorization)
- [ ] Provides strategic framing

**Recommended Answers:**
- [ ] Grounded in actual resume data
- [ ] Honest (doesn't fabricate experience)
- [ ] Strategically framed (emphasizes relevant experience)
- [ ] Appropriate length for screening context

**Honesty Flags:**
- [ ] If experience doesn't match, suggests honest positioning
- [ ] Doesn't recommend lying about qualifications
- [ ] Suggests how to address gaps honestly

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST B4: CALENDAR INTEGRATION

**What we're testing:** Calendar invites have correct date/time/timezone and include prep context

**Why it matters:** Wrong timezone = missed interview. Missing context = unprepared candidate.

#### Prerequisites:
- Interview scheduled in the system

#### Steps:

1. Go to Interview Intelligence or Command Center
2. Find a scheduled interview
3. Download calendar invite (ICS file)
4. Open in Google Calendar
5. Open in Apple Calendar (or Outlook)

#### Expected Results:

**Basic Functionality:**
- [ ] ICS file downloads without error
- [ ] File opens in Google Calendar
- [ ] File opens in Apple Calendar

**Date/Time Accuracy:**
- [ ] Correct date (not off by one day)
- [ ] Correct time in your timezone
- [ ] Same time in both Google and Apple Cal (no timezone drift)

**Event Details:**
- [ ] Event title includes company name
- [ ] Event title includes interview type
- [ ] Description includes role title
- [ ] Description includes prep link or summary
- [ ] Location/video link if provided

#### Edge Cases:
| Scenario | Test | Pass Criteria |
|----------|------|---------------|
| Evening interview | 11:00 PM tonight | Shows today, not tomorrow |
| Morning interview | 8:00 AM day after tomorrow | Correct day and time |
| Different timezone | Set interview in different TZ | Converts correctly |

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

## SECTION C: KNOWN ISSUES TO VERIFY FIXED

These issues were identified in previous testing and should be verified as fixed.

---

### TEST C1: DOCUMENT REFINEMENT

**Previous Issue:** 500 errors when asking Hey Henry to refine documents

#### Steps:
1. Go to Documents page with generated documents
2. Open Hey Henry
3. Ask: "Can you make my resume summary more senior?"
4. Wait for response

#### Expected Results:
- [ ] No 500 error
- [ ] Hey Henry provides refined version
- [ ] Changes reflected in document preview
- [ ] Changes persist after page refresh (bug fix from today)

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST C2: COMMAND CENTER DRAG-AND-DROP

**Previous Issue:** Cards required page refresh to show movement

#### Steps:
1. Go to Command Center
2. Drag an application card from one column to another
3. Observe update

#### Expected Results:
- [ ] Card moves visually without refresh
- [ ] Status updates in database
- [ ] Metrics recalculate correctly

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST C3: INTERVIEW SCHEDULING FLOW

**Previous Issue:** "Continue to Schedule" freeze, interview not syncing

#### Steps:
1. Go to Command Center
2. Click "Got an Interview"
3. Select an application
4. Click "Continue to Schedule"
5. Complete scheduling
6. Verify interview appears in Interview Intelligence

#### Expected Results:
- [ ] No freeze on "Continue to Schedule"
- [ ] Scheduling form loads correctly
- [ ] Interview syncs to Interview Intelligence
- [ ] Application status updates in Command Center

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

### TEST C4: PREP GUIDE CONTENT

**Previous Issue:** Prep Guide showing blank or fabricated content on first load

#### Steps:
1. Schedule an interview (if not already done)
2. Go to Interview Intelligence
3. Click "Prep Guide" for the scheduled interview
4. Review content

#### Expected Results:
- [ ] Content loads on first click (no blank screen)
- [ ] Content is grounded in actual resume/JD (not fabricated)
- [ ] Company name correct
- [ ] Role-specific questions included
- [ ] "Questions to ask them" section populated

#### Result:
```
Pass / Fail / Partial

Notes:
```

---

## SUMMARY SCORECARD

### Section A: New Features (December 25)

| # | Test | Result | Notes |
|---|------|--------|-------|
| A1 | Conversation History Persistence | | |
| A2 | Pipeline Pattern Analysis | | |
| A3 | Proactive Network Surfacing | | |
| A4 | Rejection Forensics | | |
| A5 | Outreach Tracking | | |
| A6 | Interview Debrief Intelligence | | |
| A7 | Interview Progression Prompts | | |
| A8 | Debrief-Informed Interview Prep | | |
| A9 | Story Bank UI | | |
| A10 | Cross-Interview Pattern Detection | | |
| A11 | Context-Aware Tooltips | | |

**Section A Score:** _____ / 11

### Section B: Outstanding Pre-Launch Tests

| # | Test | Result | Notes |
|---|------|--------|-------|
| B1 | Hey Henry Context Awareness | | |
| B2 | Mock Interview Feedback Quality | | |
| B3 | Screening Questions Analysis | | |
| B4 | Calendar Integration | | |

**Section B Score:** _____ / 4

### Section C: Bug Fix Verification

| # | Test | Result | Notes |
|---|------|--------|-------|
| C1 | Document Refinement | | |
| C2 | Command Center Drag-and-Drop | | |
| C3 | Interview Scheduling Flow | | |
| C4 | Prep Guide Content | | |

**Section C Score:** _____ / 4

---

## OVERALL STATUS

**Total Tests:** 19
**Passing:** _____
**Failing:** _____
**Partial:** _____

**Launch Readiness:** Ready / Not Ready / Conditional

---

## BUGS FOUND

| Test | Issue | Severity | Page | Notes |
|------|-------|----------|------|-------|
| | | | | |
| | | | | |
| | | | | |

**Severity Definitions:**
- **Critical:** Blocks core functionality, launch blocker
- **High:** Major feature broken, should fix before launch
- **Medium:** Feature works but UX issue, can launch with known issue
- **Low:** Minor issue, post-launch fix acceptable

---

## TESTER NOTES

```
Additional observations, edge cases discovered, UX feedback:


```

---

**END OF TEST SCRIPT**
