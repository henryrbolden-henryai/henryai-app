# HENRY'S NETWORK FEATURE SPEC v1.0

**Date:** December 27, 2025
**Status:** DRAFT - Phase 2 Feature
**Purpose:** Leverage Henry's recruiting network to provide warm introductions for candidates without direct connections
**Dependencies:** LinkedIn Network Surfacing (A3), Conversation History Persistence (Complete)

---

## EXECUTIVE SUMMARY

HenryHQ candidates often lack direct connections at target companies. Henry has 15+ years of recruiting relationships at companies like Spotify, Uber, National Grid, and across executive search. This feature surfaces Henry's network when the candidate has no path, offering to broker introductions for qualified candidates.

**Core Value Proposition:**
- For candidates: Access to warm paths they couldn't get on their own
- For Henry: Differentiation no competitor can replicate (it's literally his Rolodex)
- For HenryHQ: Premium feature that justifies paid tiers

**The Promise:**
> "You don't know anyone at Stripe. But I do. Want me to introduce you?"

---

## USER STORIES

### Candidate Perspective

**Story 1: No connection, Henry has one**
> "I analyzed a role at Databricks. I don't know anyone there. Hey Henry tells me that Henry knows the Head of Talent Acquisition and offers to make an intro. I click 'Yes, please introduce me.' Two days later, I get an email from the recruiter asking for my resume."

**Story 2: Candidate has connection, Henry's network not needed**
> "I analyzed a role at Uber. I already know someone there from my LinkedIn. Hey Henry surfaces my connection first and offers to draft outreach. Henry's network doesn't come up because I don't need it."

**Story 3: Neither has a connection**
> "I analyzed a role at a small startup. Neither I nor Henry have connections there. Hey Henry acknowledges this and provides a cold outreach strategy instead."

### Henry's Perspective

**Story 4: Intro request comes in**
> "I get a Slack notification: 'Sarah Chen (78% fit) is requesting an intro to Mike Torres at Stripe for the Senior PM role.' I see Sarah's resume, fit analysis, and positioning strategy. I decide this is a good match, so I click 'Approve & Send Intro.' An email goes out to Mike with Sarah cc'd."

**Story 5: Declining a request**
> "I get a request for an intro, but the candidate is a 45% fit and the role is a reach. I click 'Decline' and select a reason: 'Fit too low for this role.' The candidate gets a message suggesting they strengthen their application before I make the intro."

---

## SYSTEM DESIGN

### Data Architecture

**Table: henrys_network**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| contact_name | String | Full name |
| contact_title | String | Current title |
| contact_company | String | Current company |
| contact_email | String | Email (encrypted) |
| contact_linkedin | String | LinkedIn URL |
| relationship_strength | Enum | strong / medium / weak |
| last_contact_date | Date | When Henry last spoke to them |
| notes | Text | Context about the relationship |
| intro_willingness | Enum | open / selective / rare |
| created_at | Timestamp | Record creation |
| updated_at | Timestamp | Last update |

**Table: intro_requests**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| candidate_id | UUID | FK to users |
| contact_id | UUID | FK to henrys_network |
| job_id | UUID | FK to analyzed jobs |
| fit_score | Integer | Candidate's fit for this role |
| status | Enum | pending / approved / declined / completed |
| decline_reason | String | If declined, why |
| requested_at | Timestamp | When candidate requested |
| resolved_at | Timestamp | When Henry acted |
| intro_sent_at | Timestamp | When intro email sent |
| outcome | Enum | responded / no_response / interview / hired |

---

### Query Logic

**When candidate asks about a role or views results:**

```
1. Query candidate's LinkedIn connections for [company]
2. IF candidate has connections:
     → Surface candidate's connections first
     → "You know [Name] at [Company]. Want me to draft outreach?"
3. ELSE query henrys_network for [company]:
     IF Henry has connections:
       → Surface Henry's network
       → "You don't have connections at [Company], but Henry knows [Name, Title]. Want him to introduce you?"
4. ELSE:
     → No warm paths available
     → "No direct paths to [Company]. Here's a cold outreach strategy..."
```

**Priority Order:**
1. Candidate's 1st-degree connections (always surface first)
2. Henry's strong relationships (intro_willingness = open)
3. Henry's medium relationships (intro_willingness = selective, only for 75%+ fit)
4. Cold outreach (fallback)

---

### Intro Request Flow

**Candidate Side:**

```
[Hey Henry]
"You don't have direct connections at Stripe, but Henry knows 
Mike Torres (Head of Recruiting). Want him to introduce you?"

[Request Introduction]  [No thanks, I'll go cold]
```

If candidate clicks "Request Introduction":

```
[Hey Henry]
"Got it. I'll send this to Henry for review. He typically 
responds within 24-48 hours. 

In the meantime, make sure your resume is tailored for this 
role. Want me to review it?"
```

**Henry Side (Admin Dashboard or Slack):**

```
NEW INTRO REQUEST

Candidate: Sarah Chen
Role: Senior PM, Identity Platform @ Stripe
Fit Score: 78%
Contact: Mike Torres (Head of Recruiting)

[View Full Analysis]

Sarah's positioning: "Platform experience at Affirm 
translates directly to Stripe's identity infrastructure..."

[Approve & Send Intro]  [Decline]  [Request More Info]
```

**Approval Flow:**

Henry clicks "Approve & Send Intro" → System generates intro email draft → Henry can edit or send as-is → Email sent to contact with candidate cc'd → Status updates to "completed"

**Decline Flow:**

Henry clicks "Decline" → Selects reason → Candidate notified with constructive feedback:

```
[Hey Henry]
"Henry reviewed your intro request for Stripe. He's holding 
off on this one because [reason]. 

His suggestion: [specific guidance based on decline reason]

Want to work on strengthening your application?"
```

---

## HEY HENRY CONVERSATION PATTERNS

### Pattern 1: Surfacing Henry's Network

**Trigger:** Candidate views role or asks about a company where they have no connections but Henry does.

```
User: "What do you think about this Stripe role?"

Hey Henry: "This is a solid fit at 78%. Your platform experience 
translates well.

You don't have direct connections at Stripe, but Henry knows 
Mike Torres, their Head of Recruiting. They worked together 
during Henry's time at Heidrick. Want him to introduce you?

[Request Introduction]  [No thanks]"
```

### Pattern 2: After Intro Request

```
User: [clicks Request Introduction]

Hey Henry: "Done. Henry will review and typically responds within 
24-48 hours. 

While you wait, let's make sure you're ready:
- Is your resume tailored for this role?
- Do you have your positioning story ready?

What do you want to work on?"
```

### Pattern 3: Intro Approved

```
[Proactive message when Henry approves]

Hey Henry: "Good news - Henry just sent an intro to Mike Torres 
at Stripe on your behalf. You're cc'd on the email.

A few tips for when Mike responds:
1. Reply within 24 hours
2. Keep it short - express interest, attach resume
3. Suggest 2-3 specific times for a call

Want me to draft your response template?"
```

### Pattern 4: Intro Declined

```
[Proactive message when Henry declines]

Hey Henry: "Henry reviewed your intro request for Stripe. He's 
holding off for now - your 52% fit score suggests this might 
be a reach, and he wants to preserve the relationship for 
stronger matches.

His advice: Focus on roles where you're 70%+ fit. You've got 
two of those in your pipeline right now. Want to prioritize 
those instead?"
```

---

## TIER GATING

| Tier | Network Access |
|------|----------------|
| Scout (Free) | Candidate's own LinkedIn only. Henry's Network not visible or mentioned. |
| Strategist ($49/mo) | Henry's Network visible. 2 intro requests per month. |
| Insider ($99/mo) | Henry's Network visible. 5 intro requests per month. |
| Command ($199/mo) | Henry's Network visible. Unlimited intro requests. Priority review. |

**Design Decision: Don't tease free users.**

Free users see only their own LinkedIn connections. If they have none, Hey Henry provides cold outreach strategies. Henry's Network is never mentioned.

Rationale: Telling free users "Henry knows someone, but you can't access this" is frustrating. It dangles value they can't have. Instead, keep the free tier clean and let Henry's Network be a genuine discovery moment when they upgrade.

**Upgrade Discovery (when user upgrades to Strategist+):**

```
Hey Henry: "You now have access to Henry's Network.

Henry has 15+ years of recruiting relationships across tech, 
finance, and executive search. When you don't have a direct 
connection at a company, I'll check if Henry does.

Want me to scan your current pipeline for warm paths?"

[Yes, check my pipeline]  [Not right now]
```

This creates a moment of delight, not relief from frustration.

---

## CAPACITY MANAGEMENT

### Henry's Time

**Assumption:** Henry can review ~20-30 intro requests per week without it becoming a second job.

**Safeguards:**

1. **Fit floor:** Only candidates with 70%+ fit can request intros (reduces low-quality requests)
2. **Monthly caps per tier:** Prevents any single user from flooding the queue
3. **Batch review:** Admin dashboard shows all pending requests in one view for efficient processing
4. **Auto-decline:** Requests pending >7 days get auto-declined with a message ("Henry's queue is full this week...")

### Contact Fatigue

**Assumption:** Henry's contacts are willing to receive occasional, high-quality intro requests. Not spam.

**Safeguards:**

1. **Per-contact limits:** Max 2 intros per contact per month
2. **Quality filter:** Only 70%+ fit candidates can be intro'd
3. **Relationship tracking:** If a contact stops responding, flag them as "cooling off"
4. **Outcome tracking:** If intros to a contact never convert, reduce their priority

---

## ADMIN DASHBOARD

### Intro Request Queue

| Candidate | Role | Company | Fit | Contact | Requested | Actions |
|-----------|------|---------|-----|---------|-----------|---------|
| Sarah Chen | Senior PM | Stripe | 78% | Mike Torres | 2h ago | [Approve] [Decline] |
| Marcus Johnson | EM | Datadog | 72% | Lisa Park | 1d ago | [Approve] [Decline] |
| ... | ... | ... | ... | ... | ... | ... |

### Network Management

- Add/edit/remove contacts
- Track intro outcomes
- See which contacts are most responsive
- Flag contacts for "cooling off" periods

### Analytics

- Intro requests per week
- Approval rate
- Conversion rate (intro → response → interview → hire)
- Top-performing contacts
- Candidate satisfaction with intro process

---

## INTRO EMAIL TEMPLATE

**Subject:** Introduction: [Candidate Name] - [Role Title]

**Body:**

```
Hi [Contact First Name],

Quick intro - [Candidate Name] is a [Candidate Title] exploring 
the [Role Title] role on your team. 

[1-2 sentences of positioning from fit analysis]

I've worked with [him/her/them] on their search strategy and 
think there's a genuine fit here. Worth a conversation if you 
have 15 minutes.

[Candidate Name] is cc'd - I'll let you two take it from here.

Best,
Henry
```

**Customization:** Henry can edit before sending. Template auto-populates from fit analysis.

---

## IMPLEMENTATION PHASES

### Phase 2A: Foundation (MVP)

- [ ] Create henrys_network table
- [ ] Populate with Henry's initial contacts (manual entry)
- [ ] Query logic: surface Henry's network when candidate has no connections
- [ ] Basic UI: "Request Introduction" button in Hey Henry
- [ ] Slack notification to Henry for new requests
- [ ] Manual email sending (Henry sends intros manually)

**Success Criteria:** 10 intro requests processed, 50%+ response rate from contacts

### Phase 2B: Automation

- [ ] Admin dashboard for batch review
- [ ] Auto-generated intro emails (Henry approves, system sends)
- [ ] Outcome tracking (did contact respond? interview? hire?)
- [ ] Candidate notifications (approved, declined, intro sent)

**Success Criteria:** Henry can process 20 requests in <30 minutes

### Phase 2C: Scale

- [ ] Tier gating enforced
- [ ] Per-contact and per-candidate limits
- [ ] Contact fatigue detection
- [ ] Analytics dashboard
- [ ] Auto-decline for stale requests

**Success Criteria:** System handles 100+ requests/month without Henry burnout

---

## RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Henry's contacts get annoyed | Medium | High | Quality filter (70%+ fit), per-contact limits, outcome tracking |
| Henry gets overwhelmed | Medium | High | Monthly caps, batch review UI, auto-decline for stale requests |
| Candidates abuse the feature | Low | Medium | Tier gating, fit floor, monthly limits per user |
| Low conversion rate | Medium | Medium | Track outcomes, refine candidate selection, improve intro copy |
| Privacy/consent issues | Low | High | Only use contacts who've agreed to receive intros |

---

## SUCCESS METRICS

| Metric | Target | Rationale |
|--------|--------|-----------|
| Intro request → response rate | >50% | Validates network quality |
| Intro → interview rate | >25% | Validates candidate quality |
| Candidate NPS on intro feature | >70 | Validates user experience |
| Henry time per request | <5 min | Validates efficiency |
| Contact opt-out rate | <5% | Validates relationship health |

---

## THE FLYWHEEL: PAY IT FORWARD

### The Model

This is the Heidrick model, productized. At executive search firms, placed candidates become future contacts. Those contacts help place more candidates. The network compounds over years.

HenryHQ can accelerate this cycle.

```
Candidate joins HenryHQ
        ↓
Gets intro via Henry's Network
        ↓
Lands the job
        ↓
Opts in to "Pay It Forward"
        ↓
Becomes a contact for future candidates
        ↓
Network grows
        ↓
More intros available
        ↓
More candidates join
        ↓
[repeat]
```

### Why It Works

1. **Gratitude is real.** Someone who landed a job through your intro genuinely wants to help others. They remember the struggle.

2. **Low friction ask.** You're not asking much. Just be open to occasional intro requests from qualified candidates.

3. **Quality control built in.** You only intro strong candidates (70%+ fit). So people joining your network are vetted by definition.

4. **Compounds over time.** Year 1: 50 placements = 50 new contacts. Year 3: 500 placements = 500 contacts across dozens of companies.

### The Prompt

When a candidate reports "I got the job" (via Command Center status update or Hey Henry conversation):

```
Hey Henry: "Congrats on landing the role at Stripe!

Quick ask: Would you be open to helping future candidates 
the way Henry helped you? If someone's a strong fit for 
Stripe, can we reach out for an intro?

[Yes, I'll pay it forward]  [Not right now]"
```

### If They Opt In

**Immediate response:**

```
Hey Henry: "That means a lot. Welcome to Henry's Network.

I'll only reach out when there's a genuinely strong candidate 
for your team. No spam, no weak fits. You have my word.

Congrats again on the new role. Go crush it."
```

**Database entry:**

Add to `henrys_network`:

| Field | Value |
|-------|-------|
| contact_name | [Candidate name] |
| contact_title | [New role title] |
| contact_company | [New company] |
| contact_email | [From profile] |
| contact_linkedin | [From profile] |
| relationship_strength | strong |
| intro_willingness | open |
| source | "HenryHQ placement" |
| placed_date | [Date they reported offer] |
| placed_via_intro | true/false |

### If They Decline

```
Hey Henry: "No problem at all. Focus on crushing the new role.

If you ever change your mind, just let me know. And congrats 
again - you earned this."
```

No guilt. No follow-up asks. Respect the boundary.

### Network Growth Projections

| Timeframe | Placements (est.) | Opt-in Rate (est.) | New Contacts | Total Network |
|-----------|-------------------|--------------------|--------------|--------------| 
| Launch | 0 | - | 0 | ~200 (Henry's existing) |
| Year 1 | 100 | 60% | 60 | ~260 |
| Year 2 | 300 | 65% | 195 | ~455 |
| Year 3 | 600 | 70% | 420 | ~875 |

**Conservative assumptions.** If HenryHQ scales faster, these numbers multiply.

### The Moat

In 3 years, this isn't just Henry's network. It's the HenryHQ Network.

- Hundreds of placed candidates across tech, finance, healthcare
- All pre-vetted (they were strong enough to get hired)
- All willing to help (they opted in out of gratitude)
- All trackable (intro success rates, response rates, outcomes)

**No competitor can replicate this.** Teal, Jobscan, Huntr have no network. LinkedIn has connections but no placement relationship. Career coaches have networks but can't scale.

This is a moat that deepens with every placement.

---

## OPEN QUESTIONS

1. **Contact consent:** Do we need explicit opt-in from Henry's contacts before including them? (Probably yes for GDPR/trust reasons)

2. **Intro copy ownership:** Does Henry write every intro, or can the system generate and Henry just approves?

3. **Failed intros:** If a contact doesn't respond, do we tell the candidate? How long do we wait?

4. **Network expansion:** Can Henry add contacts over time? Is there a workflow for "I just met someone at [Company]"?

5. **Candidate follow-through:** If candidate gets intro but ghosts the contact, how do we handle? Ban from future intros?

---

## APPENDIX: COMPETITOR ANALYSIS

| Competitor | Network Feature | Henry's Advantage |
|------------|-----------------|-------------------|
| LinkedIn Premium | "InMail" (cold outreach) | Warm intro > cold InMail |
| Teal | None | - |
| Jobscan | None | - |
| Huntr | None | - |
| Career coaches | Manual intros (expensive) | Scalable + integrated into platform |

**No direct competitor offers this.** Executive search firms do, but they charge $50K+ and work for companies, not candidates. Henry's Network democratizes access to recruiter relationships.

---

**END OF SPEC**
