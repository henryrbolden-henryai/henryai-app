# LinkedIn Profile Score Feature Specification

**Version:** 1.0  
**Last Updated:** December 18, 2025  
**Status:** Production Ready with Enhancement Opportunities  
**Owner:** Product Team

---

## Executive Summary

The LinkedIn Profile Score feature provides candidates with a quantified assessment (0-100) of how well their LinkedIn profile is optimized for recruiter discovery and engagement. It combines automated analysis with recruiter-grade best practices to surface high-impact improvements.

**Current State:** Production-ready with strong foundation. Visual design is polished, scoring logic is comprehensive, and fix prioritization works well.

**Enhancement Opportunities:**
1. Add explicit framing about recruiter search behavior
2. Clarify that this measures "findability + first impression," not qualifications
3. Strengthen connection between score and job search outcomes
4. Add role-specific optimization guidance

---

## Product Philosophy

### Core Principle: Recruiter Search Optimization

This feature does NOT measure:
- Professional capability or competence
- Career success or trajectory
- Network quality or influence
- Content quality or thought leadership

This feature DOES measure:
- How easily recruiters can find you in search
- Whether your profile passes the "3-second test" when recruiters land on it
- Completeness of sections recruiters actually look at
- Recency signals that affect search ranking

### The "3-Second Test"

When a recruiter lands on your profile, they decide in 3 seconds whether to keep reading. Your score reflects how well you pass that test.

**What recruiters look for in 3 seconds:**
1. Headline: Does this person do what I'm hiring for?
2. Photo: Professional or casual?
3. Experience: Do I recognize these companies?
4. Recency: Is this profile active or stale?

### User Empathy Map

**Who uses this feature:**
- Job seekers preparing for active search (largest segment)
- Passive candidates optimizing for inbound
- Career switchers unsure how to position themselves
- Senior professionals who haven't updated LinkedIn in years

**What they're feeling:**
- Overwhelmed by LinkedIn's complexity
- Unsure what actually matters to recruiters
- Anxious about being "found"
- Frustrated by lack of inbound interest

**What they need:**
- Clear prioritization (what to fix first)
- Recruiter perspective (why it matters)
- Quick wins (high-impact, low-effort changes)
- Role-specific guidance (PM vs engineer vs recruiter)

---

## Scoring Methodology

### Overall Score Calculation (0-100)

```
Overall Score = 
  (Headline Score / 15) × 15 +
  (About Score / 20) × 20 +
  (Experience Score / 20) × 20 +
  (Skills Score / 15) × 15 +
  (Freshness Score / 10) × 10 +
  (Resume Alignment Score / 10) × 10 +
  (Credibility Score / 5) × 5 +
  Education, Recommendations, Activity (5 points combined)
```

**Weighting Rationale:**
- **Headline (15%):** Most important for search + first impression
- **About (20%):** Second thing recruiters read, shows strategic thinking
- **Experience (20%):** Core credibility signal, must be detailed
- **Skills (15%):** Drives search discovery, but less important than content
- **Freshness (10%):** Affects LinkedIn's ranking algorithm
- **Resume Alignment (10%):** Consistency matters for credibility
- **Credibility (5%):** Red flags like missing company URLs
- **Other (10%):** Education, recommendations, activity—nice-to-haves

---

### Section 1: Headline (15 points max)

**What recruiters see:** Your headline appears in every search result, every connection request, every comment you make. It's the #1 thing that drives clicks.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Not default template | 3 | "Student at X University" or "Looking for opportunities" = 0 points |
| Includes function/role | 4 | "Product Manager" or "Software Engineer" (searchable keywords) |
| Includes specialization | 3 | "B2B SaaS" or "Healthcare Tech" or "Fintech" (niche) |
| Uses full 220 characters | 2 | Longer = more keywords = more discoverable |
| Includes company/credentials | 3 | "Ex-Google" or "MBA" or "CSPO" (credibility signals) |

**Total: 15 points**

**Red Flags (Auto-deduct):**
- Generic template (e.g., "Passionate about making a difference") → -5 points
- All lowercase or all caps → -2 points
- Emojis (reduces professional credibility) → -1 point
- Missing entirely → 0 points

**Example Scoring:**

**Bad Headline (4/15 points):**
> "Product Manager | Passionate about technology"
- ✓ Includes function (4 points)
- ✗ Generic "passionate about" phrase (-5 penalty)
- ✗ No specialization (0 points)
- ✗ Only 48 characters (0 points)
- ✗ No credentials (0 points)
- **Final: -1 → floor at 0**

**Good Headline (14/15 points):**
> "Senior Product Manager, B2B SaaS | Growth & Monetization | Ex-Stripe, Spotify | Stanford MBA"
- ✓ Not default (3 points)
- ✓ Includes function "Product Manager" (4 points)
- ✓ Includes specialization "B2B SaaS, Growth & Monetization" (3 points)
- ✓ Uses 95 characters (2 points)
- ✓ Includes company + credentials "Ex-Stripe, Spotify, Stanford MBA" (3 points)
- **Final: 15/15**

---

### Section 2: About (20 points max)

**What recruiters see:** The About section is the #2 thing recruiters read after your headline. It's where they assess strategic thinking, communication skills, and cultural fit.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Exists and >100 words | 5 | Minimum substance threshold |
| 300-800 words (ideal length) | 3 | Longer = more context; too long = wall of text |
| First-person voice | 2 | "I lead..." vs "John leads..." (personal connection) |
| Quantified achievements | 5 | Numbers, metrics, outcomes (credibility) |
| Clear specialization | 3 | What you're known for, what problems you solve |
| No generic buzzwords | 2 | "Passionate," "results-driven," "team player" (red flags) |

**Total: 20 points**

**Red Flags (Auto-deduct):**
- Empty About section → 0 points
- <50 words → -3 points
- >1,200 words → -2 points (too long, recruiters won't read)
- Generic buzzwords (3+) → -2 points each

**Example Scoring:**

**Bad About (7/20 points):**
> "I'm a passionate product manager who loves solving problems and working with teams. I'm results-driven and always looking to make an impact."
- ✓ Exists and >100 words? No, only 28 words (0 points)
- ✗ <50 words penalty (-3 points)
- ✓ First-person (2 points)
- ✗ No quantified achievements (0 points)
- ✗ No clear specialization (0 points)
- ✗ Generic buzzwords: "passionate," "results-driven," "impact" (-6 points)
- **Final: 2 - 9 = -7 → floor at 0**

**Good About (19/20 points):**
> "I'm a Senior Product Manager specializing in B2B SaaS growth. Over the past 8 years, I've launched products that generated $50M+ in ARR across companies like Stripe and Spotify.
>
> At Stripe, I led the pricing strategy overhaul that increased margins by 25%. At Spotify, I owned the B2B podcast product, growing subscribers from 10K to 150K in 18 months.
>
> I focus on the intersection of product-market fit, pricing strategy, and go-to-market execution. I thrive in 0-1 environments where ambiguity is high and the roadmap is unwritten."

- ✓ Exists and >100 words (5 points)
- ✓ 300-800 words? Yes, 110 words (3 points)
- ✓ First-person (2 points)
- ✓ Quantified: "$50M ARR," "25% margin increase," "10K → 150K" (5 points)
- ✓ Clear specialization: "B2B SaaS growth, pricing, GTM" (3 points)
- ✓ No buzzwords (2 points)
- **Final: 20/20** (but let's say 19 because word count is on lower end)

---

### Section 3: Experience (20 points max)

**What recruiters see:** Your experience bullets prove you can do what your headline claims. Recruiters scan for: scope, impact, and relevance.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| All roles have 3+ bullets | 5 | Detail shows substance, not just title |
| Bullets use PAR format | 5 | Problem/Action/Result (shows strategic thinking) |
| Quantified outcomes (50%+ bullets) | 5 | Metrics = credibility |
| Most recent role is detailed | 3 | Recruiters care most about current work |
| Company URLs included | 2 | Helps recruiters validate scope/scale |

**Total: 20 points**

**Red Flags (Auto-deduct):**
- Most recent role has <3 bullets → -5 points
- No quantification anywhere → -5 points
- Copy-pasted job descriptions → -3 points (generic language detector)

**Example Scoring:**

**Bad Experience (5/20 points):**
> **Product Manager, Acme Inc. (2020-2023)**
> - Managed product roadmap
> - Worked with cross-functional teams
> - Launched new features

- ✗ Only 3 bullets (barely meets threshold) (2 points)
- ✗ No PAR format (0 points)
- ✗ No quantification (0 points)
- ✗ Detailed? No, very generic (0 points)
- ✓ Company URL? Let's assume yes (2 points)
- ✗ Generic language penalty (-3 points)
- **Final: 4 - 3 = 1 → let's say 5 for generosity**

**Good Experience (19/20 points):**
> **Senior Product Manager, Stripe (2020-2023)**
> - Led pricing strategy overhaul for 50K+ merchant accounts, increasing average revenue per user (ARPU) by 25% ($12M incremental ARR)
> - Owned product roadmap for payment infrastructure, shipping 15 features with 95% on-time delivery and <2% rollback rate
> - Built and managed cross-functional team of 12 (3 engineers, 2 designers, 4 data analysts, 3 PMs) across SF and Dublin offices
> - Partnered with Sales and Marketing to launch new pricing tier, converting 1,200 customers in 6 months (20% of target segment)

- ✓ 4 bullets (5 points)
- ✓ PAR format: problem implied, action clear, result quantified (5 points)
- ✓ Quantified: ARPU, $12M ARR, 15 features, 95% on-time, 12-person team, 1,200 customers (5 points)
- ✓ Most recent and detailed (3 points)
- ✓ Company URL (2 points)
- **Final: 20/20** (but let's say 19 because there's always room for polish)

---

### Section 4: Skills (15 points max)

**What recruiters see:** Skills drive search discovery. If a recruiter searches "product management," LinkedIn surfaces profiles with "Product Management" in their skills.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Has 10+ skills listed | 3 | LinkedIn recommends 10-50 |
| Includes function-specific skills | 4 | "Product Management" for PMs, "Software Development" for engineers |
| Includes tool-specific skills | 3 | "SQL," "Figma," "Python" (concrete, searchable) |
| Top 3 skills are relevant | 3 | Top 3 get priority in search |
| Skills match resume | 2 | Consistency = credibility |

**Total: 15 points**

**Red Flags (Auto-deduct):**
- <5 skills → -3 points
- Generic skills dominate top 3 (e.g., "Communication," "Leadership") → -2 points
- Skills include buzzwords ("Rockstar," "Ninja") → -2 points

**Example Scoring:**

**Bad Skills (5/15 points):**
- Communication, Leadership, Microsoft Office, Team Player, Problem Solving
- ✗ Only 5 skills (-3 penalty)
- ✗ All generic, no function-specific (0 points)
- ✗ No tool-specific (0 points)
- ✗ Top 3 are "Communication," "Leadership," "Microsoft Office" (-2 penalty)
- ✗ Don't match resume context (0 points)
- **Final: 0 - 5 = -5 → floor at 0**

**Good Skills (15/15 points):**
- Product Management, Product Strategy, Agile Development, SQL, Tableau, A/B Testing, Pricing Strategy, User Research, Data Analysis, Go-to-Market Strategy, Stakeholder Management, Roadmap Planning, Feature Prioritization, API Integration, Python
- ✓ 15 skills (3 points)
- ✓ Function-specific: "Product Management," "Product Strategy" (4 points)
- ✓ Tool-specific: "SQL," "Tableau," "Python" (3 points)
- ✓ Top 3 are relevant (3 points)
- ✓ Match resume (2 points)
- **Final: 15/15**

---

### Section 5: Freshness (10 points max)

**What recruiters see:** LinkedIn's algorithm prioritizes active profiles. Stale profiles rank lower in search and appear less engaged.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Profile updated in last 30 days | 3 | Recent activity boosts search ranking |
| Activity (posts/comments) in last 30 days | 3 | Shows engagement |
| Most recent role end date is current | 2 | "Present" signals you're active in your career |
| Profile photo updated in last 2 years | 2 | Shows you care about your presence |

**Total: 10 points**

**Red Flags (Auto-deduct):**
- Profile not updated in 6+ months → -3 points
- No activity in 6+ months → -3 points
- Most recent role ended >1 year ago with no "current" role → -2 points

**Example Scoring:**

**Stale Profile (2/10 points):**
- Last update: 8 months ago (-3 penalty)
- No posts/comments in 6+ months (-3 penalty)
- Most recent role: "2020-2023" (ended, no current role) (-2 penalty)
- Photo: 3 years old (0 points)
- **Final: 0 - 8 = -8 → floor at 0, but let's say 2 to acknowledge they have something**

**Fresh Profile (10/10 points):**
- Last update: 2 weeks ago (3 points)
- Posted article 3 days ago (3 points)
- Current role: "2023-Present" (2 points)
- Photo: 6 months old (2 points)
- **Final: 10/10**

---

### Section 6: Resume Alignment (10 points max)

**What recruiters see:** When your LinkedIn doesn't match your resume, it raises red flags. Consistency = credibility.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Job titles match resume | 3 | "Senior PM" on both, not "PM" on one and "Lead PM" on other |
| Company names match resume | 3 | Exact match, not abbreviations |
| Date ranges match resume | 2 | ±1 month tolerance |
| Skills on LinkedIn appear on resume | 2 | Avoid claiming skills you can't demonstrate |

**Total: 10 points**

**Red Flags (Auto-deduct):**
- Title inflation on LinkedIn → -3 points (e.g., "VP" on LinkedIn, "Senior PM" on resume)
- Company name mismatch → -2 points
- Date discrepancies >3 months → -2 points

---

### Section 7: Credibility (5 points max)

**What recruiters see:** Small details signal professionalism and authenticity.

**Scoring Criteria:**

| Criterion | Points | Explanation |
|-----------|--------|-------------|
| Company URLs exist for all roles | 2 | Helps recruiters validate scope |
| Profile photo is professional | 2 | Headshot vs vacation photo |
| No broken links | 1 | Portfolio, personal site, etc. |

**Total: 5 points**

**Red Flags (Auto-deduct):**
- Missing company URLs for 2+ roles → -2 points
- Unprofessional photo (group photo, dark/blurry) → -2 points
- Broken links → -1 point

---

### Section 8: Other Signals (10 points combined)

**Education (3 points):**
- Has education listed (2 points)
- Includes degree + field (1 point)

**Recommendations (3 points):**
- Has 3+ recommendations (2 points)
- Recommendations are recent (<2 years) (1 point)

**Activity (2 points):**
- Has Featured section (1 point)
- Has Activity visible (1 point)

**Volunteer/Certifications (2 points):**
- Has certifications (1 point)
- Has volunteer work (1 point)

---

## Score Interpretation & Messaging

### Score Ranges

| Score | Label | Recruiter Perception | User Message |
|-------|-------|---------------------|--------------|
| 80-100 | Strong Profile | "This person is searchable, credible, and active" | Your profile is well-optimized. Focus on the minor improvements below to maximize visibility. |
| 60-79 | Needs Improvement | "I can find them, but the profile doesn't wow me" | Recruiters will find you but may not click. Address the high-priority items below. |
| 40-59 | Needs Work | "Profile exists but lacks substance" | Your profile is missing key elements. Fix the critical issues to start getting noticed. |
| 0-39 | Critical Attention Needed | "This profile won't show up in my searches" | Your profile isn't optimized for recruiter search. Start with the critical items immediately. |

### Color Coding

**Score Circle:**
- 80-100: Green (#4ade80)
- 60-79: Yellow/Warning (#fbbf24)
- 40-59: Orange (blend)
- 0-39: Red (#f87171)

**Section Cards:**
- ≥80% of max: Green border
- 50-79% of max: Yellow border
- <50% of max: Red border

---

## Profile Gaps Detection & Explanation

### Purpose

Explicitly identify and name gaps in the candidate's LinkedIn profile that reduce recruiter confidence or senior-level competitiveness. This mirrors Resume Leveling's gap logic, but applied to LinkedIn as a discovery and credibility surface.

**Why This Matters:**
Fixing formatting issues (headline length, bullet count) won't help if the fundamental gap is "no evidence of senior scope." Users need to understand what's **missing**, not just what's **wrong**.

### Gap Categories (Non-Negotiable)

The system MUST evaluate and surface gaps across these categories:

---

#### 1. Scope Gaps

**What we're detecting:**
- Senior titles without evidence of scale, ownership, or decision authority
- Experience bullets that describe activity but not responsibility
- No quantification of team size, budget, or organizational breadth

**Example Detection Logic:**
```javascript
// If title contains "Senior", "Lead", "Staff", "Principal", "Director", "VP"
// AND experience bullets lack scope indicators:
// - No team size mentioned
// - No budget mentioned
// - No "led", "owned", "drove" language
// - No cross-functional responsibility
// → FLAG: Scope Gap
```

**Example Output:**
```json
{
  "gap_type": "Scope",
  "description": "Your profile does not show evidence of senior-level ownership (strategy setting, roadmap accountability, or org-level decision making).",
  "why_it_matters": "Recruiters use LinkedIn to quickly assess scope. Without clear signals of scale and authority, senior roles are less likely to convert to outreach.",
  "how_to_address": "Add bullets that quantify team size, budget, or geographic scope. Use ownership language: 'Led 12-person team', 'Owned $5M budget', 'Drove company-wide initiative across 200+ employees'."
}
```

**User-Facing Message:**
> "Your profile does not demonstrate senior-level ownership or decision-making authority, which limits competitiveness for Director+ roles."

---

#### 2. Evidence Gaps

**What we're detecting:**
- Lack of quantified outcomes in experience bullets
- Vague or generic descriptions ("worked on", "helped with", "contributed to")
- No proof of impact (no metrics, no results, no business outcomes)

**Example Detection Logic:**
```javascript
// If 70%+ of experience bullets lack:
// - Numbers (%, $, X→Y, time savings)
// - Outcome language ("increased", "reduced", "generated", "saved")
// - Business metrics (revenue, ARR, MAU, efficiency, cost)
// → FLAG: Evidence Gap
```

**Example Output:**
```json
{
  "gap_type": "Evidence",
  "description": "Your experience describes what you worked on, but not the outcomes you drove.",
  "why_it_matters": "Recruiters rely on quantified results to validate impact. Without metrics, they assume your work had limited business effect.",
  "how_to_address": "Rewrite bullets to follow PAR format (Problem, Action, Result). Add specific metrics: revenue impact, cost savings, efficiency gains, user growth. Example: 'Increased user engagement by 40% (500K→700K MAU) through product roadmap prioritization'."
}
```

**User-Facing Message:**
> "Your profile lacks quantified outcomes, making it difficult for recruiters to assess the business impact of your work."

---

#### 3. Credibility Gaps

**What we're detecting:**
- Missing company URLs for 2+ roles
- Unverifiable companies (no LinkedIn Company Page, no website, no Crunchbase)
- Significant mismatches between resume and LinkedIn (titles, dates, companies)

**Example Detection Logic:**
```javascript
// If any of:
// - 2+ companies have no URL
// - 1+ companies cannot be verified online
// - Title or date mismatches between resume and LinkedIn
// → FLAG: Credibility Gap
```

**Example Output:**
```json
{
  "gap_type": "Credibility",
  "description": "Some roles on your profile are difficult to validate, which weakens recruiter confidence in scope and scale.",
  "why_it_matters": "Recruiters verify company legitimacy to assess the quality of your experience. Unverifiable companies raise questions about title inflation or exaggeration.",
  "how_to_address": "Add company URLs to all roles. If the company is defunct or very small, add context in your bullet: 'Series A fintech startup, $3M funding, 15 employees' or 'Acquired by [Company] in 2022'."
}
```

**User-Facing Message:**
> "Multiple roles on your profile cannot be easily verified by recruiters, creating credibility questions about scope and scale."

---

#### 4. Positioning Gaps

**What we're detecting:**
- Headline and About do not clearly answer "what you do"
- No specialization or market focus (too generic)
- Conflicting signals across headline, About, and experience (e.g., headline says "Product Manager" but experience is mostly engineering)

**Example Detection Logic:**
```javascript
// If any of:
// - Headline lacks function AND specialization
// - About section lacks clear focus area
// - Skills list is generic (no role-specific depth)
// - Headline function doesn't match majority of experience
// → FLAG: Positioning Gap
```

**Example Output:**
```json
{
  "gap_type": "Positioning",
  "description": "Your profile does not clearly position you for a specific role or niche, making it harder for recruiters to match you to open roles.",
  "why_it_matters": "Recruiters search for specific terms like 'product manager fintech' or 'backend engineer python'. Generic positioning makes you invisible in search and unclear in fit.",
  "how_to_address": "Choose a primary function (Product Manager, not 'PM/Engineer/Consultant') and specialize it (B2B SaaS, Healthcare Tech, Fintech). Update your headline, About, and skills to consistently reinforce this positioning."
}
```

**User-Facing Message:**
> "Your profile tries to appeal to multiple roles, which makes it unclear what you actually do. Recruiters need a clear, focused positioning."

---

#### 5. Recency & Engagement Gaps

**What we're detecting:**
- Profile not updated in 6+ months
- No activity (posts, comments, shares) in 6+ months
- Most recent role ended >1 year ago with no "current" role
- Profile photo appears outdated (low resolution, old style)

**Example Detection Logic:**
```javascript
// If any of:
// - Last profile update >180 days ago
// - No activity in last 180 days
// - Most recent experience end date is >1 year ago AND no current role
// - Photo quality flags (low resolution, group photo)
// → FLAG: Recency Gap
```

**Example Output:**
```json
{
  "gap_type": "Recency",
  "description": "Your profile appears inactive, which reduces how often it is surfaced in recruiter searches.",
  "why_it_matters": "LinkedIn's algorithm prioritizes active profiles in search results. Stale profiles rank lower and signal to recruiters that you may not be actively looking or engaged.",
  "how_to_address": "Update your profile monthly (even small changes like adding a skill or tweaking a bullet). Engage with content (like, comment, share) at least once per week. If you're between roles, add a 'current' entry like 'Open to Product Management Opportunities'."
}
```

**User-Facing Message:**
> "Your profile hasn't been updated in 8+ months, which signals inactivity to both LinkedIn's algorithm and recruiters."

---

### Required Output Structure

Add a new top-level field to the API response:

```json
{
  "overall_score": 72,
  "score_label": "Needs Improvement",
  "score_summary": "...",
  "section_scores": {...},
  "section_details": {...},
  "profile_gaps": [
    {
      "gap_type": "Scope",
      "description": "Your profile does not demonstrate senior-level ownership or decision-making authority.",
      "why_it_matters": "Recruiters use LinkedIn to quickly assess scope. Without clear signals of scale and authority, senior roles are less likely to convert to outreach.",
      "how_to_address": "Add bullets that quantify team size, budget, or geographic scope. Use ownership language: 'Led 12-person team', 'Owned $5M budget', 'Drove company-wide initiative'."
    },
    {
      "gap_type": "Evidence",
      "description": "Your experience describes what you worked on, but not the outcomes you drove.",
      "why_it_matters": "Recruiters rely on quantified results to validate impact. Without metrics, they assume your work had limited business effect.",
      "how_to_address": "Rewrite bullets to follow PAR format (Problem, Action, Result). Add specific metrics: revenue impact, cost savings, efficiency gains, user growth."
    }
  ],
  "fixes": [...]
}
```

**Rules for Gap Output:**
- Max 5 gaps to avoid overwhelm
- Written in second person ("Your profile...")
- Calm, factual, market-based language
- No moral judgment, no "you should have"
- Each gap includes: description, why it matters, how to address

---

### Gap Priority Logic

Not all gaps are equal. Prioritize based on:

1. **Target seniority level:**
   - Junior/Mid: Evidence gaps and Positioning gaps matter most
   - Senior/Staff: Scope gaps and Evidence gaps are critical
   - Director+: Scope gaps, Credibility gaps, and Positioning gaps are dealbreakers

2. **Severity of absence:**
   - Complete absence (e.g., zero quantified bullets) > Partial absence (e.g., some bullets quantified)
   - Conflicting signals (e.g., senior title, junior scope) > Missing signals (e.g., no scope mentioned)

3. **Market context:**
   - Competitive roles (PM, Engineer, Marketing) require sharper positioning
   - Less competitive roles (niche specializations) can be more generic

**Example Priority Order for Senior PM:**
1. Scope Gap (CRITICAL)
2. Evidence Gap (HIGH)
3. Positioning Gap (HIGH)
4. Credibility Gap (MEDIUM)
5. Recency Gap (MEDIUM)

---

### UI Placement & Design

**Where to place:**
- Below Score Card (overall score + label)
- Above Section Breakdown cards
- Above Fix List

**Why this order:**
1. Score Card: "Here's your score"
2. Profile Gaps: "Here's what's fundamentally missing"
3. Section Breakdown: "Here's how each section scored"
4. Fix List: "Here's how to fix the tactical issues"

**Visual Treatment:**

```
┌─────────────────────────────────────────────┐
│  What's Missing From Your Profile          │
│  ───────────────────────────────────────    │
│                                             │
│  Your profile has 2 significant gaps that   │
│  are limiting recruiter engagement:         │
│                                             │
│  🔴 Scope Gap                               │
│     Your profile does not demonstrate       │
│     senior-level ownership...               │
│                                             │
│     Why it matters: [Recruiter perspective] │
│     How to fix: [Specific actions]          │
│                                             │
│  🟡 Evidence Gap                            │
│     Your experience lacks quantified...     │
│                                             │
│     Why it matters: [Recruiter perspective] │
│     How to fix: [Specific actions]          │
│                                             │
└─────────────────────────────────────────────┘
```

**CSS Styling:**
```css
.profile-gaps-section {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-left: 4px solid var(--color-warning);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 32px;
}

.profile-gaps-header {
    font-family: var(--font-display);
    font-size: 1.4rem;
    margin-bottom: 12px;
}

.profile-gaps-intro {
    color: var(--color-text-secondary);
    margin-bottom: 24px;
    line-height: 1.6;
}

.gap-item {
    background: var(--color-surface-elevated);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

.gap-item:last-child {
    margin-bottom: 0;
}

.gap-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.gap-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

.gap-icon.scope { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.gap-icon.evidence { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.gap-icon.credibility { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.gap-icon.positioning { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.gap-icon.recency { background: rgba(34, 211, 238, 0.2); color: #22d3ee; }

.gap-title {
    font-weight: 600;
    font-size: 1.05rem;
}

.gap-description {
    color: var(--color-text);
    margin-bottom: 12px;
    line-height: 1.6;
}

.gap-why {
    color: var(--color-text-secondary);
    font-size: 0.95rem;
    margin-bottom: 12px;
    padding-left: 16px;
    border-left: 2px solid var(--color-border);
}

.gap-fix {
    color: var(--color-text);
    font-size: 0.95rem;
    padding: 12px;
    background: rgba(34, 211, 238, 0.1);
    border-radius: 8px;
    line-height: 1.6;
}
```

**Collapsible Behavior:**
- Collapsed by default on mobile
- Expanded by default on desktop
- Persist state in sessionStorage

---

### Integration with Fix List

**Gap vs Fix - What's the Difference?**

| Profile Gaps | Fix List |
|--------------|----------|
| Conceptual/strategic | Tactical/mechanical |
| "What's fundamentally missing" | "What's technically wrong" |
| Requires reframing or rewriting | Can be fixed with edits |
| Example: "No evidence of scope" | Example: "Headline only 48 characters" |

**Example:**
- **Gap:** Scope Gap (strategic issue)
- **Fix:** Add team size to bullets (tactical action)

Both should exist, but serve different purposes:
- Gaps help users understand the big picture
- Fixes help users take immediate action

**UI Flow:**
1. User sees score: 58/100
2. User reads gaps: "You're missing scope and evidence"
3. User expands section cards: "Here's where the gaps show up"
4. User reviews fix list: "Here are 8 specific things to change"

This creates a **learning journey** from strategic understanding to tactical execution.

---

## Fix Prioritization System

### Severity Levels

**CRITICAL (Red):**
- Absence will prevent recruiters from finding or engaging with your profile
- Examples: No headline, missing About section, no skills, stale profile (6+ months)

**HIGH (Orange):**
- Noticeable gap that significantly weakens your positioning
- Examples: Generic headline, thin experience bullets, skills don't match role

**MEDIUM (Yellow):**
- Improvement that strengthens your profile but not dealbreaker
- Examples: Could add more skills, About section could be longer

**LOW (Gray):**
- Nice-to-have polish opportunity
- Examples: Add Featured section, get more recommendations

### Fix Structure

Every fix follows this pattern:

```
[Severity Badge] [Problem Statement]

Why it matters: [Consequence from recruiter's perspective]

How to fix: [Specific, actionable steps]
```

**Example:**

```
🔴 CRITICAL: Your headline is the LinkedIn default

Why it matters: Recruiters see your headline in every search result. The default template ("Looking for opportunities") doesn't tell them what you do, so they skip your profile.

How to fix:
1. Click "Edit intro" at the top of your profile
2. Use this formula: [Seniority] [Function] | [Specialization] | [Credentials/Companies]
   Example: "Senior Product Manager | B2B SaaS Growth | Ex-Stripe, Spotify"
3. Use all 220 characters to maximize keywords
```

---

## UI/UX Specifications

### Page Layout

```
┌───────────────────────────────────────────┐
│  Header                                   │
│  - Back link to profile settings          │
│  - Title: "LinkedIn Profile Score"       │
│  - Subtitle: "Fix what's costing you..."  │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│  Score Card                               │
│  - Circle with score (0-100)              │
│  - Label (Strong / Needs Work / etc.)     │
│  - Summary message                         │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│  Section Breakdown (Desktop)              │
│  - Expandable cards for each section      │
│  - Score per section (e.g., 12/15)        │
│  - Criteria breakdown when expanded       │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│  Section Breakdown (Mobile)               │
│  - Compact grid showing section scores    │
│  - No expansion, just score summary       │
└───────────────────────────────────────────┘

┌───────────────────────────────────────────┐
│  Priority Fix List (Collapsible)         │
│  - Header: "X items" + severity summary   │
│  - Collapsible list of fixes              │
│  - Each fix: Problem + Why + How to Fix   │
└───────────────────────────────────────────┘
```

---

### Visual Design

**Color Palette:**
```css
--color-bg: #0a0a0b (page background)
--color-surface: #141416 (card background)
--color-surface-elevated: #1c1c1f (hover states)
--color-border: rgba(255, 255, 255, 0.08) (dividers)
--color-text: #fafafa (primary text)
--color-text-secondary: #a1a1aa (muted text)
--color-accent: #22d3ee (links, highlights)
--color-success: #4ade80 (green for good)
--color-warning: #fbbf24 (yellow for caution)
--color-error: #f87171 (red for critical)
--color-linkedin: #0077b5 (LinkedIn brand)
```

**Typography:**
```css
--font-display: 'Instrument Serif' (headings)
--font-body: 'DM Sans' (body text)
--size-heading: 2.2rem
--size-subheading: 1.4rem
--size-body: 1rem
--size-caption: 0.9rem
```

**Score Circle:**
- Size: 90px diameter
- Inner circle: 72px diameter (creates ring effect)
- Background: conic-gradient based on score percentage
- Text: Score value in center (1.6rem, bold)

**Section Cards (Desktop):**
- Background: var(--color-surface)
- Border: 1px solid var(--color-border)
- Border-radius: 16px
- Padding: 20px 24px
- Hover: background shifts to var(--color-surface-elevated)
- Expandable: click to reveal criteria breakdown

**Section Cards (Mobile):**
- Grid layout (2 columns)
- Compact: just score + label
- No expansion on mobile

**Fix Items:**
- Background: var(--color-surface-elevated)
- Border-left: 3px solid [severity color]
- Padding: 20px
- Margin-bottom: 12px
- Border-radius: 12px

---

### Responsive Behavior

**Desktop (≥1024px):**
- Max-width: 900px centered
- Section cards in single column (full detail)
- Fix list expanded by default

**Tablet (768px-1023px):**
- Max-width: 100% (padding: 0 20px)
- Section cards still single column
- Fix list collapsed by default

**Mobile (<768px):**
- Full-width layout
- Section breakdown switches to compact grid (2 columns)
- Fix list collapsed by default
- Larger touch targets (44px minimum)

---

### Interaction Patterns

**Section Card Expansion:**
- Click anywhere on card header to expand/collapse
- Chevron icon rotates 180deg when expanded
- Smooth height transition (300ms ease)
- Body slides in with opacity fade

**Fix List Toggle:**
- Click header to expand/collapse
- Chevron rotates 180deg
- Summary shows severity count (e.g., "2 critical, 3 high priority")
- Max 8 fixes shown to avoid overwhelm

**Scoring Animation:**
- Score circle animates from 0 to final score on page load
- Duration: 1.5 seconds
- Easing: ease-out
- Color transitions based on final score

---

## Backend Logic

### Input Data Structure

```json
{
  "linkedin_data": {
    "headline": "string",
    "about": "string",
    "experience": [
      {
        "company": "string",
        "title": "string",
        "dates": "string",
        "bullets": ["string"],
        "company_url": "string"
      }
    ],
    "skills": ["string"],
    "education": [...],
    "recommendations": [...],
    "activity_recent": boolean,
    "profile_updated_at": "ISO date",
    "photo_professional": boolean
  },
  "resume_data": {
    "experience": [...],
    "skills": [...]
  }
}
```

### Output Data Structure

```json
{
  "overall_score": 72,
  "score_label": "Needs Improvement",
  "score_summary": "Recruiters will find you but may not click. Address the high-priority items below.",
  "section_scores": {
    "headline": 8,
    "about": 15,
    "experience": 12,
    "skills": 11,
    "freshness": 5,
    "resumeAlignment": 7,
    "credibility": 3,
    "education": 2,
    "recommendations": 1,
    "activity": 1
  },
  "section_details": {
    "headline": {
      "notDefault": 3,
      "includesFunction": 4,
      "includesSpecialization": 0,
      "usesFullLength": 0,
      "includesCredentials": 1
    },
    "about": {...},
    "experience": {...},
    "skills": {...},
    "freshness": {...},
    "resumeAlignment": {...},
    "credibility": {...}
  },
  "profile_gaps": [
    {
      "gap_type": "Scope",
      "description": "Your profile does not demonstrate senior-level ownership or decision-making authority.",
      "why_it_matters": "Recruiters use LinkedIn to quickly assess scope. Without clear signals of scale and authority, senior roles are less likely to convert to outreach.",
      "how_to_address": "Add bullets that quantify team size, budget, or geographic scope. Use ownership language: 'Led 12-person team', 'Owned $5M budget', 'Drove company-wide initiative'."
    },
    {
      "gap_type": "Evidence",
      "description": "Your experience describes what you worked on, but not the outcomes you drove.",
      "why_it_matters": "Recruiters rely on quantified results to validate impact. Without metrics, they assume your work had limited business effect.",
      "how_to_address": "Rewrite bullets to follow PAR format (Problem, Action, Result). Add specific metrics: revenue impact, cost savings, efficiency gains, user growth."
    }
  ],
  "fixes": [
    {
      "severity": "CRITICAL",
      "problem": "Your headline doesn't use the full 220 characters",
      "why": "Longer headlines = more keywords = higher search ranking. You're leaving 172 characters unused.",
      "fix": "Add your specialization, key skills, or notable companies. Example: 'Product Manager | B2B SaaS | Growth & Monetization | Ex-Stripe'"
    },
    {
      "severity": "HIGH",
      "problem": "Your About section is only 85 words",
      "why": "Recruiters need context to assess fit. Short About sections signal lack of strategic thinking.",
      "fix": "Expand to 300-500 words. Include: your focus area, 2-3 quantified achievements, and what makes you different."
    }
  ]
}
```

---

## API Endpoint

### Endpoint: `/api/linkedin/score`

**Method:** POST

**Request Body:**
```json
{
  "linkedin_data": {...},
  "resume_data": {...}  // Optional, for alignment check
}
```

**Response:**
```json
{
  "overall_score": 72,
  "score_label": "Needs Improvement",
  "score_summary": "...",
  "section_scores": {...},
  "section_details": {...},
  "fixes": [...]
}
```

**Error Responses:**
```json
{
  "error": "Missing required field: linkedin_data",
  "status": 400
}
```

---

## Prompt Engineering

### System Prompt Template

```
You are a senior recruiter who specializes in LinkedIn optimization. Your job is to score a candidate's LinkedIn profile (0-100), identify strategic gaps, and provide specific, actionable fixes.

CRITICAL RULES:
1. Base scoring ONLY on the criteria defined in the scoring rubric
2. Identify strategic gaps BEFORE listing tactical fixes
3. Be direct and specific—no generic advice
4. Every fix must follow: Problem → Why it matters → How to fix
5. Prioritize fixes by severity (CRITICAL > HIGH > MEDIUM > LOW)
6. Max 8 fixes total to avoid overwhelming the user
7. Use recruiter language ("This signals X to recruiters")

SCORING RUBRIC:
[Include full rubric from above]

GAP DETECTION (MANDATORY):
Evaluate the profile for these 5 gap categories:

1. SCOPE GAPS
   - Senior titles without evidence of scale, ownership, or decision authority
   - No quantification of team size, budget, or organizational breadth
   - Experience bullets describe activity, not responsibility

2. EVIDENCE GAPS
   - Lack of quantified outcomes (no %, no $, no metrics)
   - Vague descriptions ("worked on", "helped with")
   - No proof of business impact

3. CREDIBILITY GAPS
   - Missing company URLs for 2+ roles
   - Unverifiable companies
   - Mismatches between resume and LinkedIn

4. POSITIONING GAPS
   - Headline/About don't clearly answer "what you do"
   - No specialization or market focus
   - Conflicting signals across sections

5. RECENCY GAPS
   - Profile not updated in 6+ months
   - No activity in 6+ months
   - Most recent role ended >1 year ago with no current role

For each gap detected, provide:
- Gap type
- Description (what's missing)
- Why it matters (recruiter perspective)
- How to address (specific actions)

Max 5 gaps. Focus on the most impactful ones for the candidate's target level.

TONE GUIDELINES:
- Direct: "Your headline is missing your specialization"
- NOT judgmental: "Your profile is terrible"
- Coach-style: "Add 3-4 bullet points to your current role"
- NOT preachy: "You should really take LinkedIn more seriously"

FIX STRUCTURE (MANDATORY):
Problem: [What's wrong]
Why it matters: [Consequence from recruiter perspective]
How to fix: [Specific steps, not vague advice]

Example:
Problem: Your About section is only 85 words
Why it matters: Recruiters need context to assess fit. Short About sections signal lack of strategic thinking or career focus.
How to fix:
1. Aim for 300-500 words (2-3 short paragraphs)
2. Paragraph 1: Your focus area and what you're known for
3. Paragraph 2: 2-3 quantified achievements (numbers, metrics, outcomes)
4. Paragraph 3: What makes your approach different or what you're looking for next
```

### User Message Template

```
Score this LinkedIn profile and identify strategic gaps:

LINKEDIN DATA:
{
  "headline": "Product Manager at Acme Inc.",
  "about": "I'm a product manager with 5 years of experience...",
  "experience": [
    {
      "company": "Acme Inc.",
      "title": "Product Manager",
      "dates": "2020-Present",
      "bullets": [
        "Managed product roadmap",
        "Worked with cross-functional teams"
      ]
    }
  ],
  "skills": ["Product Management", "Agile", "SQL"],
  "profile_updated_at": "2024-06-15",
  "photo_professional": true
}

RESUME DATA (optional):
{
  "experience": [...],
  "skills": [...]
}

TARGET LEVEL (if known): "Senior Product Manager"

Provide:
1. Overall score (0-100)
2. Score label and summary message
3. Section scores with criteria breakdown
4. Profile gaps (max 5, prioritized by impact)
5. Top 8 fixes prioritized by severity

Remember: 
- Identify strategic gaps FIRST (what's fundamentally missing)
- Then provide tactical fixes (what to change)
- Be specific, be direct, and explain why each gap/fix matters to recruiters.
```

---

## Enhancement Opportunities

### 1. Add Recruiter Behavior Framing (NEW)

**Problem:** Users don't understand how recruiters actually use LinkedIn.

**Solution:** Add collapsible "How Recruiters Search" section at top of page.

**Content:**
> "Recruiters use LinkedIn like a search engine. They type keywords (e.g., 'product manager fintech') and scan the first 20 results. Your score reflects how likely you are to (1) show up in that search and (2) get clicked.
>
> **What recruiters do in 3 seconds:**
> 1. Read your headline: Does this person do what I'm hiring for?
> 2. Glance at experience: Do I recognize these companies?
> 3. Check recency: Is this profile active or stale?
>
> If you pass the 3-second test, they read your About section and skim your bullets. This is where they decide whether to message you."

**Design:**
- Collapsed by default
- Light blue background (recruiter perspective color)
- Small info icon next to page title

---

### 2. Add "What This Score Means" Context (NEW)

**Problem:** Score without context doesn't drive behavior change.

**Solution:** Add outcome-based messaging below score circle.

**Content by Score Range:**

**80-100:**
> "You're in the top 20% of profiles. Recruiters will find you, click your profile, and likely reach out. Focus on staying fresh (update every 30 days)."

**60-79:**
> "You're findable but not compelling. Recruiters will see you in search results but may skip to the next person. Fix the high-priority items to stand out."

**40-59:**
> "You're barely visible. Most recruiters won't find you in search, and if they do, they won't click. Fix the critical issues to start getting inbound interest."

**0-39:**
> "Your profile is essentially invisible. LinkedIn's algorithm won't surface you in recruiter searches. Start with the critical items immediately."

---

### 3. Add Role-Specific Optimization (Future)

**Problem:** Generic advice doesn't account for role differences.

**Solution:** Detect role from headline/experience and customize fix recommendations.

**Role Detection:**
- Product Manager: Emphasize quantified impact, stakeholder management
- Software Engineer: Emphasize technical skills, GitHub/portfolio links
- Recruiter: Emphasize hiring metrics, candidate experience
- Sales: Emphasize quota attainment, deal sizes
- Marketing: Emphasize campaign metrics, brand work

**Example:**
- Product Manager headline should include "Product Manager" + specialization (B2B SaaS, consumer, fintech)
- Engineer headline should include tech stack (e.g., "Senior Backend Engineer | Python, AWS, Kubernetes")

---

### 4. Add Comparison to Benchmarks (Future)

**Problem:** Users don't know if 72/100 is good or bad relative to peers.

**Solution:** Show percentile ranking within role/seniority.

**Example:**
> "Your score of 72 puts you in the 55th percentile for Senior Product Managers. The top 25% score 85+."

**Data Requirements:**
- Need benchmark data per role + seniority
- Could crowdsource from HenryHQ user base over time

---

### 5. Add "Quick Wins" Section (Future)

**Problem:** Users overwhelmed by long fix list.

**Solution:** Surface 2-3 high-impact, low-effort fixes.

**Criteria for "Quick Win":**
- HIGH or CRITICAL severity
- Takes <5 minutes to fix
- Immediate score boost

**Example:**
> "🚀 Quick Wins (10 minutes, +15 points)
> 1. Expand your headline to 220 characters (+5 points)
> 2. Add 2 quantified achievements to your About section (+8 points)
> 3. Pin your top 3 skills (+2 points)"

---

## Testing Checklist

### Functional Testing

- [ ] Score calculation matches rubric for all test profiles
- [ ] Section scores sum correctly to overall score
- [ ] Profile gaps are detected correctly for each category
- [ ] Gap detection prioritizes by target seniority level
- [ ] Gap messages are distinct from fix messages
- [ ] Max 5 gaps shown per profile
- [ ] Fix list prioritizes by severity correctly
- [ ] Max 8 fixes shown (no overwhelming lists)
- [ ] Score circle animates smoothly on page load
- [ ] Collapsible sections expand/collapse correctly
- [ ] Mobile grid layout works on small screens
- [ ] All severity badges display correct colors

### Content Testing

- [ ] Gap descriptions are clear and specific (not vague)
- [ ] Gap "why it matters" explains recruiter perspective
- [ ] Gap "how to address" includes strategic guidance
- [ ] Gaps are distinct from tactical fixes
- [ ] Fix messages are specific (not generic advice)
- [ ] Fix "why it matters" explains recruiter perspective
- [ ] Fix "how to fix" includes actionable steps
- [ ] Score labels match score ranges
- [ ] Summary messages are appropriate for each range

### Gap Detection Validation

Test with these sample profiles:

**Profile 1: Scope Gap**
- Title: "Senior Product Manager"
- Bullets: "Worked on features", "Helped with roadmap", "Collaborated with team"
- Expected: Scope Gap detected (no evidence of ownership or scale)

**Profile 2: Evidence Gap**
- Title: "Product Manager"
- Bullets: "Led product roadmap", "Managed stakeholders", "Launched features"
- Expected: Evidence Gap detected (no quantification)

**Profile 3: Credibility Gap**
- Companies: "Acme Startup Inc." (no URL), "XYZ Consulting" (no LinkedIn page)
- Expected: Credibility Gap detected (unverifiable companies)

**Profile 4: Positioning Gap**
- Headline: "Product Manager | Engineer | Consultant"
- About: Discusses product management and engineering equally
- Expected: Positioning Gap detected (conflicting signals)

**Profile 5: Recency Gap**
- Last update: 18 months ago
- Most recent role: "2020-2023" (ended, no current role)
- Expected: Recency Gap detected (stale profile)

### Edge Cases

- [ ] Empty LinkedIn profile (all sections missing) → 0 score
- [ ] Minimal profile (just name + headline) → low score
- [ ] Perfect profile (all criteria met) → 100 score
- [ ] Resume data missing (optional field) → alignment checks skipped
- [ ] Profile updated today → full freshness points
- [ ] Profile not updated in 2 years → 0 freshness points

### UX Testing

- [ ] First-time users understand what the score means
- [ ] Users can identify top priority fixes quickly
- [ ] Mobile layout is usable on small screens
- [ ] Collapsible sections reduce information overload
- [ ] Color coding is intuitive (green = good, red = bad)

---

## Success Metrics

### Quantitative

| Metric | Current | Target |
|--------|---------|--------|
| Page bounce rate | Unknown | <15% |
| Time on page | Unknown | 4+ minutes |
| Users who take action after viewing | Unknown | 70%+ |
| Average score improvement (7 days post-view) | Unknown | +10 points |

### Qualitative (User Feedback)

**Questions to ask beta testers:**
1. "Did you understand what your score measures?" (Yes/No)
2. "Which fix did you tackle first?" (Open-ended)
3. "Did the fixes feel actionable?" (1-5 scale)
4. "Did anything feel overwhelming or unclear?" (Open-ended)

**Success criteria:**
- 85%+ answer "Yes" to understanding
- 80%+ can identify their #1 priority fix
- 4.2+ average on actionability scale
- <15% report feeling overwhelmed

---

## Implementation Plan

### Phase 1: Add Framing (1 day)

**Tasks:**
1. Add "How Recruiters Search" collapsible section
2. Add "What This Score Means" context below score circle
3. Test with 5 beta users for clarity

**Success Metric:**
- 90%+ of users understand what the score measures

---

### Phase 2: Enhance Fix Messaging (1 day)

**Tasks:**
1. Audit all fix templates for specificity
2. Ensure every fix has "Why it matters" + "How to fix"
3. Add severity badges to all fixes
4. Test fix prioritization with 10+ sample profiles

**Success Metric:**
- Every fix includes recruiter perspective
- Users can act on fixes without external research

---

### Phase 3: Mobile Optimization (1 day)

**Tasks:**
1. Test mobile grid layout on 5+ devices
2. Ensure touch targets are 44px+ minimum
3. Optimize collapsible animations for mobile
4. Test on slow connections

**Success Metric:**
- Mobile usable on iPhone SE and similar small screens
- No layout breaks on any common device

---

### Phase 4: Add Role-Specific Guidance (2-3 days)

**Tasks:**
1. Build role detection logic (PM, engineer, recruiter, etc.)
2. Create role-specific fix templates
3. Update scoring to weight criteria by role
4. Test with 5+ profiles per role

**Success Metric:**
- Role-specific fixes feel more relevant than generic advice
- Users report "this feels tailored to my situation"

---

## Open Questions & Decisions Needed

1. **Should we integrate this with resume leveling?**
   - Pro: One comprehensive assessment
   - Con: May overwhelm users with too much feedback

2. **Should we show before/after examples?**
   - Pro: Visual examples help users understand fixes
   - Con: May reveal other users' profiles (privacy concern)

3. **Should we add a "Share Results" feature?**
   - Pro: Users can get second opinions
   - Con: Privacy concerns

4. **Should we track score improvements over time?**
   - Pro: Shows progress, encourages action
   - Con: Requires user accounts and database

---

## Appendix

### Sample Profiles for Testing

**Profile A: Strong (Score: 92/100)**
- Headline: "Senior Product Manager, B2B SaaS | Growth & Monetization | Ex-Stripe, Spotify | CSPO"
- About: 450 words, quantified, clear specialization
- Experience: 4-5 bullets per role, all quantified
- Skills: 18 relevant skills
- Freshness: Updated 1 week ago
- Alignment: Perfect match with resume

**Profile B: Needs Work (Score: 58/100)**
- Headline: "Product Manager | Passionate about technology"
- About: 95 words, generic
- Experience: 2-3 bullets per role, no quantification
- Skills: 7 skills, mostly generic
- Freshness: Updated 9 months ago
- Alignment: Some discrepancies

**Profile C: Critical (Score: 23/100)**
- Headline: Default template "Looking for opportunities"
- About: Empty
- Experience: Just job titles, no bullets
- Skills: 3 skills
- Freshness: Updated 2+ years ago
- Alignment: Cannot check (no resume)

---

### References

- [HenryHQ Core Philosophy](./PHILOSOPHY.md)
- [Resume Leveling Spec](./RESUME_LEVELING_SPEC.md)
- [Product Roadmap](./PRODUCT_STRATEGY_ROADMAP.md)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 18, 2025 | Initial spec with scoring rubric, UI/UX, enhancements | Product |

---

**Next Review:** January 2026 (after beta user feedback)  
**Owner:** Product Team  
**Status:** Production with Enhancement Opportunities
