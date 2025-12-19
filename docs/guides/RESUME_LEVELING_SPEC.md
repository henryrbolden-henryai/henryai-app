# Resume Leveling Feature Specification

**Version:** 2.0  
**Last Updated:** December 18, 2025  
**Status:** Production Enhancement Required  
**Owner:** Product Team

---

## Executive Summary

The Resume Leveling feature provides candidates with honest, recruiter-grade assessment of how their resume signals seniority in the market. It evaluates scope, credibility, and evidence to determine if a resume supports claims of senior-level positioning.

**Current State:** 80-85% complete. Strong UI/UX foundation, but missing critical narrative authority and trust-building framing.

**Required Enhancements:**
1. Add explicit "How to Read This" framing section
2. Enhance red flag messaging with cause + consequence structure
3. Add senior-level readiness checks for Director+ roles
4. Strengthen credibility assessment language

---

## Product Philosophy

### Core Principle: Market Perception, Not Personal Worth

This feature does NOT judge:
- Candidate's potential
- Intelligence or capability
- Work ethic or character
- Future trajectory

This feature DOES assess:
- How the resume will be interpreted by senior hiring managers
- Whether the evidence on paper supports the claimed level
- Market signals that affect credibility
- Gaps between self-perception and market perception

### Tone Guidelines

**What we are:**
- Direct and honest
- Coach-style, not drill-sergeant
- Evidence-based, not judgmental
- Supportive while realistic

**What we are NOT:**
- Sugar-coating or cheerleading
- Harsh or demoralizing
- Vague or evasive
- Making assumptions without evidence

### User Empathy Map

**Who uses this feature:**
- Mid-level professionals aiming for senior roles (largest segment)
- Senior professionals validating their positioning
- Career switchers assessing transferability
- Candidates who've been ghosted/rejected and want honest feedback

**What they're feeling:**
- Anxious about honest feedback
- Frustrated with black-box rejections
- Defensive about their experience
- Hopeful for concrete improvement steps

**What they need:**
- Clear explanation of why the assessment landed where it did
- Distinction between "you're not qualified" vs "your resume doesn't show it"
- Specific, actionable improvement recommendations
- Validation that this is market perception, not personal judgment

---

## Page Structure

### Information Architecture

```
1. Header
   - Page title: "Resume Level Analysis"
   - Subtitle: "How your experience signals in the market"

2. How to Read This Section (NEW - Critical Addition)
   - Collapsed by default, visible chevron
   - 2-3 paragraph explainer
   - Sets frame before delivering verdict

3. Level Card (Primary Result)
   - Current Level badge
   - Confidence meter
   - Brief explanation

4. What This Means (NEW - Immediate Context)
   - 2-3 sentences
   - What level you can credibly target
   - What needs to change to level up

5. Collapsible Sections (Existing, Enhanced)
   - Signals by Category (Scope, Impact, Leadership, Technical)
   - Red Flags (Enhanced with cause + consequence)
   - Language Analysis
   - Target Level Recommendations

6. Action Items (NEW - What to Do Next)
   - Prioritized list
   - Immediate fixes
   - Longer-term development

7. Senior Readiness Checks (NEW - Director+ Only)
   - Strategy ownership evidence
   - Org-level impact signals
   - Decision-making authority indicators
```

---

## Section 1: How to Read This (NEW)

### Purpose
Set the frame before delivering the assessment. Prevent defensive reactions by establishing that this is market perception, not personal judgment.

### Content Structure

**Collapsed by default with visible chevron icon.**

**Title:** "How to Read This Analysis"

**Content (2-3 paragraphs):**

> "This analysis evaluates how your resume will likely be interpreted by senior hiring managers and recruiters today. It looks at scope, credibility, and evidence—not your potential or capability.
>
> Your level assessment reflects what the market can verify from your resume, not what you're capable of. A gap here doesn't mean you can't do senior work. It means your resume doesn't show it yet.
>
> Think of this as a reality check from someone who's reviewed thousands of resumes. The feedback is direct because that's what helps. If something sounds harsh, remember: this is how the market sees it, not how we see you."

### Design Specifications

**Visual Treatment:**
- Light background (slightly darker than page background)
- Subtle border (not alarming)
- Chevron icon (collapsed state)
- Font size: 0.95rem (slightly smaller than body)
- Padding: 20px
- Border-radius: 8px
- Border-left: 3px solid var(--color-primary) (accent)

**Interaction:**
- Click anywhere on header to expand/collapse
- Smooth transition (300ms ease)
- Persist state in sessionStorage
- Auto-expand on first visit only

**Placement:**
- Immediately below page header
- Above level card
- Cannot be missed

---

## Section 2: Level Card (Enhanced)

### Current Structure (Keep)

```
┌─────────────────────────────────────┐
│  [LEVEL BADGE]                      │
│  Senior Product Manager             │
│                                     │
│  Confidence: ████████░░ 85%        │
│                                     │
│  Brief explanation text here        │
└─────────────────────────────────────┘
```

### Confidence Meter Visual Indicators

**High Confidence (≥85%):**
- Color: Green (#10b981)
- Icon: ✓ checkmark
- Message: "Strong evidence"

**Medium Confidence (70-84%):**
- Color: Orange (#f59e0b)
- Icon: ! exclamation
- Message: "Some gaps"

**Low Confidence (<70%):**
- Color: Red (#ef4444)
- Icon: ✗ x-mark
- Message: "Significant gaps"

### Enhancement: Add "What This Means" Section

Immediately below level card, add contextual explanation:

**Title:** "What This Means"

**Content (2-3 sentences):**
- What level you can credibly target
- Primary obstacle to next level
- What success looks like

**Example:**

> "Your resume currently supports Mid-Level Product Manager roles (IC4-IC5). To credibly target Senior PM roles, you need clearer evidence of org-level impact and strategic ownership. Focus on quantifying scope and demonstrating decision-making authority."

---

## Section 3: Signals by Category (Enhanced)

### Current Structure (Keep, Enhance Explanations)

Each signal category gets:
1. Category name
2. Category explanation (what it measures)
3. Severity-scored signals
4. Evidence quotes from resume

### Signal Categories

**1. Scope Signals**

**Definition:**
"The scale of your work—team sizes, budgets, global reach, and organizational breadth."

**What we look for:**
- Team size managed/influenced
- Budget responsibility
- Geographic scope (regional, national, global)
- Number of stakeholders
- Cross-functional breadth

**Examples of strong scope signals:**
- "Led 15-person engineering team across 3 offices"
- "Managed $5M annual budget"
- "Owned product roadmap for North America region"

**Examples of weak/missing scope signals:**
- "Worked on team projects"
- "Collaborated with stakeholders"
- No quantification of scale

---

**2. Impact Signals**

**Definition:**
"Measurable business outcomes—revenue growth, cost savings, efficiency gains, and KPI improvements."

**What we look for:**
- Revenue impact ($ or %)
- Cost savings ($ or %)
- Efficiency improvements (time/process)
- User/customer growth
- Market share gains

**Examples of strong impact signals:**
- "Drove 40% increase in user engagement (500K → 700K MAU)"
- "Reduced operational costs by $2M annually"
- "Shipped feature that generated $10M ARR"

**Examples of weak/missing impact signals:**
- "Improved user experience"
- "Contributed to company goals"
- No metrics or outcomes

---

**3. Leadership Signals**

**Definition:**
"How you influence others—managing teams, mentoring, driving initiatives, and cross-functional collaboration."

**What we look for:**
- Direct reports
- Indirect influence
- Mentorship/coaching
- Initiative ownership
- Stakeholder management at senior levels

**Examples of strong leadership signals:**
- "Managed 3 direct reports (2 PMs, 1 designer)"
- "Led cross-functional initiative with 20+ stakeholders"
- "Mentored 5 junior PMs on product strategy"

**Examples of weak/missing leadership signals:**
- "Team player"
- "Worked well with others"
- No evidence of leading people or initiatives

---

**4. Technical/Domain Signals**

**Definition:**
"Domain expertise and specialized skills—tools, methodologies, certifications, and technical depth."

**What we look for:**
- Technical proficiency (tools, platforms, languages)
- Domain expertise (industry-specific knowledge)
- Certifications/credentials
- Methodologies mastered (Agile, Six Sigma, etc.)

**Examples of strong technical signals:**
- "Expert in SQL, Python, Tableau for data analysis"
- "Certified Scrum Product Owner (CSPO)"
- "Deep expertise in healthcare compliance (HIPAA)"

**Examples of weak/missing technical signals:**
- "Proficient in Microsoft Office"
- "Good communication skills"
- Generic skills with no depth

---

### Signal Severity Levels

**CRITICAL (Red):**
- Absence will prevent you from getting interviews for target level
- Example: No evidence of team management for Senior PM role

**HIGH (Orange):**
- Noticeable gap that weakens positioning
- Example: Limited quantification of impact

**MEDIUM (Yellow):**
- Nice-to-have but not dealbreaker
- Example: No certifications

**LOW (Gray):**
- Minor polish opportunity
- Example: Could use more industry-specific terminology

---

## Section 4: Red Flags (Enhanced with Cause + Consequence)

### Purpose
Surface credibility risks that recruiters will notice, framed as market perception, not personal failure.

### Current Structure (Needs Enhancement)

**Before:**
```
❌ Company not found: "Acme Startup Inc."
❌ Title inflation detected
```

**After (Enhanced with cause + consequence):**
```
❌ Company not found: "Acme Startup Inc."
   → This creates a credibility gap because recruiters cannot validate scope or scale. 
   → Recommendation: Add company description (e.g., "Series A SaaS startup, $5M ARR, 20 employees") or link to Crunchbase/LinkedIn.

❌ Title inflation detected: "VP of Product" at 3-person startup
   → Inflated titles at small companies raise questions about real scope and authority.
   → Recommendation: Use functional title (e.g., "Product Lead") and emphasize scope in bullets.
```

### Red Flag Categories

**1. Credibility Gaps**
- Company not found/validated
- Non-existent company domains
- Defunct companies without context

**Why it matters:**
"Recruiters verify company legitimacy to assess scope. If they can't validate the company, they'll assume the scope is inflated or the experience is less credible."

**How to fix:**
- Add company description
- Link to Crunchbase, LinkedIn Company Page, or press coverage
- If defunct, note "acquired by [Company]" or "shut down [Year]"

---

**2. Title Inflation**
- Executive titles at tiny companies
- Title doesn't match described responsibilities
- Rapid title progression without scope increase

**Why it matters:**
"A VP title at a 3-person startup doesn't carry the same weight as a VP title at a 300-person company. Recruiters will discount inflated titles."

**How to fix:**
- Use functional titles that reflect actual scope (e.g., "Product Lead" instead of "VP of Product")
- Emphasize scope in bullets (team size, budget, stakeholders)
- Add company context (size, stage, funding)

---

**3. Generic Language**
- Buzzwords without evidence (e.g., "rockstar," "ninja")
- Vague responsibilities (e.g., "worked on projects")
- No quantification

**Why it matters:**
"Generic language makes it impossible to assess what you actually did. Senior roles require specificity."

**How to fix:**
- Replace buzzwords with specific skills
- Quantify responsibilities (how many? how much? how often?)
- Use PAR (Problem, Action, Result) framework

---

**4. Scope Mismatches**
- Title claims senior level, but bullets show IC work
- No evidence of leadership/influence
- Responsibilities don't match claimed seniority

**Why it matters:**
"If your title says 'Senior PM' but your bullets describe feature execution, recruiters will assume title inflation."

**How to fix:**
- Reframe bullets to show strategic ownership
- Add evidence of leadership and influence
- Remove or minimize IC-level tasks

---

### Design Treatment for Red Flags

**Visual Hierarchy:**
```
┌─────────────────────────────────────────┐
│  ❌ [RED FLAG NAME]                     │
│     [Specific instance from resume]     │
│                                         │
│  → Why this matters:                    │
│     [Consequence/market perception]     │
│                                         │
│  → How to fix:                          │
│     • [Recommendation 1]                │
│     • [Recommendation 2]                │
└─────────────────────────────────────────┘
```

**Color Scheme:**
- Red flag icon: #ef4444 (red)
- Background: rgba(239, 68, 68, 0.05) (light red tint)
- Border-left: 3px solid #ef4444

**Spacing:**
- 16px padding
- 12px gap between red flags
- 8px gap between sections within a red flag

---

## Section 5: Language Analysis (Keep, Minor Enhancements)

### Current Structure (Strong, Keep As-Is)

```
┌─────────────────────────────────────────┐
│  Language Analysis                      │
│  ─────────────────────────────────      │
│                                         │
│  Tone: Professional                     │
│  Clarity: Clear                         │
│  Specificity: Strong                    │
│                                         │
│  Generic phrases detected: 2            │
│  • "team player"                        │
│  • "results-driven"                     │
└─────────────────────────────────────────┘
```

### Minor Enhancement: Add Context

After listing generic phrases, add:

> "Generic phrases weaken your positioning because they don't differentiate you. Senior roles require evidence, not claims."

---

## Section 6: Senior Readiness Checks (NEW - Director+ Only)

### Purpose
For candidates targeting Director+ roles, provide explicit senior-level competency assessment.

### When to Show
Only display if:
- Target level is Director, VP, or C-suite
- Current level assessment is Senior Manager or above

### Competency Framework

**1. Strategy Ownership**

**What we're looking for:**
- Evidence of setting direction, not just executing
- Multi-quarter or multi-year planning
- Trade-off decisions with business impact

**Strong Evidence:**
- "Defined 3-year product roadmap aligned to company OKRs"
- "Led pricing strategy overhaul, resulting in 25% margin improvement"
- "Prioritized feature backlog based on market analysis and customer segmentation"

**Weak/Missing Evidence:**
- "Contributed to roadmap discussions"
- "Executed on strategic initiatives"
- No mention of strategy or planning

**Assessment:**
```
✓ Strong: [Quote from resume showing strategy ownership]
! Partial: [Quote showing some strategy work, but not ownership]
✗ Missing: No clear evidence of strategic decision-making
```

---

**2. Org-Level Impact**

**What we're looking for:**
- Influence beyond direct team
- Cross-functional initiatives
- Company-wide impact

**Strong Evidence:**
- "Led company-wide migration to microservices architecture (200+ engineers)"
- "Drove go-to-market strategy for new product line ($50M revenue)"
- "Established product operations function across 5 product teams"

**Weak/Missing Evidence:**
- "Worked with multiple teams"
- "Contributed to company goals"
- Impact limited to direct team

**Assessment:**
```
✓ Strong: [Quote from resume showing org-level impact]
! Partial: [Quote showing cross-team work, but not org-level]
✗ Missing: No evidence of influence beyond direct team
```

---

**3. Decision-Making Authority**

**What we're looking for:**
- Budget ownership
- Hiring decisions
- Go/no-go authority
- Trade-off decisions

**Strong Evidence:**
- "Owned $20M product budget with quarterly reallocation decisions"
- "Hired and built 12-person product team (3 direct reports, 9 indirect)"
- "Made final call on product launches and GTM timing"

**Weak/Missing Evidence:**
- "Provided input on decisions"
- "Recommended hiring candidates"
- No mention of ownership or authority

**Assessment:**
```
✓ Strong: [Quote from resume showing decision authority]
! Partial: [Quote showing some decision input, but not ownership]
✗ Missing: No clear evidence of decision-making authority
```

---

### Design Treatment for Senior Readiness Checks

**Visual Style:**
- Separate collapsible section (collapsed by default)
- Only appears for Director+ target levels
- Title: "Senior Readiness Assessment"
- Subtitle: "Evidence of Director+ competencies"

**Layout:**
```
┌────────────────────────────────────────────┐
│  [Competency Name]                         │
│  ─────────────────────────────────         │
│                                            │
│  ✓ Strong / ! Partial / ✗ Missing         │
│                                            │
│  Evidence from resume:                     │
│  "[Quote]"                                 │
│                                            │
│  What's needed:                            │
│  • [Recommendation]                        │
└────────────────────────────────────────────┘
```

---

## Section 7: Target Level Recommendations (Enhanced)

### Current Structure (Keep, Add Prioritization)

Currently shows:
- Target level suggestions
- Evidence needed for each level

### Enhancement: Add Priority Labels

**High Priority (Required for next level):**
```
🔴 Critical Gap: [What's missing]
   → Without this, you'll struggle to pass senior screens
```

**Medium Priority (Strengthens positioning):**
```
🟡 Important: [What would help]
   → This makes your case more competitive
```

**Low Priority (Nice-to-have):**
```
🟢 Enhancement: [Polish opportunity]
   → This rounds out your profile
```

---

## UI/UX Specifications

### Visual Design

**Color Palette:**
```css
--level-high: #10b981 (green)
--level-medium: #f59e0b (orange)
--level-low: #ef4444 (red)
--level-bg-high: rgba(16, 185, 129, 0.1)
--level-bg-medium: rgba(245, 158, 11, 0.1)
--level-bg-low: rgba(239, 68, 68, 0.1)
--level-border: #e5e7eb
--level-text: #1f2937
--level-text-muted: #6b7280
```

**Typography:**
```css
--font-heading: 'Inter', sans-serif
--font-body: 'Inter', sans-serif
--size-heading: 1.5rem (24px)
--size-subheading: 1.125rem (18px)
--size-body: 1rem (16px)
--size-caption: 0.875rem (14px)
--weight-bold: 600
--weight-regular: 400
```

**Spacing:**
```css
--spacing-section: 32px
--spacing-card: 24px
--spacing-item: 16px
--spacing-tight: 8px
```

**Borders & Shadows:**
```css
--border-radius: 12px
--border-width: 1px
--shadow-sm: 0 1px 3px rgba(0,0,0,0.1)
--shadow-md: 0 4px 6px rgba(0,0,0,0.1)
```

---

### Responsive Design

**Desktop (≥1024px):**
- Full-width layout
- Two-column grid for signals (if space allows)
- Expanded collapsibles by default

**Tablet (768px - 1023px):**
- Single-column layout
- Collapsed by default
- Touch-friendly hit areas (44px minimum)

**Mobile (<768px):**
- Single-column layout
- Collapsed by default
- Larger font sizes (1.125rem body)
- Bottom padding for thumb zones

---

### Accessibility

**Keyboard Navigation:**
- Tab order follows visual hierarchy
- Collapsibles toggle with Space/Enter
- Focus indicators visible (2px outline)

**Screen Readers:**
- All icons have aria-label attributes
- Collapsible sections have aria-expanded state
- Confidence meter includes text alternative

**Color Contrast:**
- Minimum 4.5:1 for body text
- Minimum 3:1 for large text
- Icons paired with text labels

---

## Backend Logic

### Input Data Structure

```json
{
  "resume_data": {
    "name": "string",
    "experience": [
      {
        "company": "string",
        "title": "string",
        "dates": "string",
        "bullets": ["string"]
      }
    ],
    "education": [...],
    "skills": ["string"]
  },
  "target_level": "string" // "Mid-Level", "Senior", "Staff", "Principal", "Director", "VP", "C-Suite"
}
```

### Output Data Structure

```json
{
  "level_assessment": {
    "current_level": "Senior Product Manager",
    "confidence": 85,
    "confidence_label": "High",
    "explanation": "Your resume shows strong evidence of senior-level scope and impact...",
    "what_this_means": "Your resume currently supports Senior PM roles. To target Staff PM, focus on..."
  },
  "signals": {
    "scope": [
      {
        "text": "Led 15-person engineering team",
        "severity": "CRITICAL",
        "source": "Uber - Senior PM"
      }
    ],
    "impact": [...],
    "leadership": [...],
    "technical": [...]
  },
  "red_flags": [
    {
      "type": "Company not found",
      "instance": "Acme Startup Inc.",
      "why_it_matters": "Recruiters cannot validate scope or scale",
      "how_to_fix": [
        "Add company description",
        "Link to Crunchbase/LinkedIn"
      ]
    }
  ],
  "language_analysis": {
    "tone": "Professional",
    "clarity": "Clear",
    "specificity": "Strong",
    "generic_phrases": ["team player", "results-driven"]
  },
  "senior_readiness": {
    "show": true, // Only if target_level is Director+
    "competencies": {
      "strategy_ownership": {
        "assessment": "Strong",
        "evidence": "[Quote from resume]",
        "recommendation": "Continue emphasizing strategic decision-making"
      },
      "org_level_impact": {...},
      "decision_authority": {...}
    }
  },
  "target_recommendations": [
    {
      "level": "Staff PM",
      "priority": "High",
      "gap": "Need clearer evidence of org-level impact",
      "evidence_needed": ["Cross-team initiatives", "Company-wide influence"]
    }
  ]
}
```

---

## API Endpoint

### Endpoint: `/api/resume/level-assessment`

**Method:** POST

**Request Body:**
```json
{
  "resume_data": {...},
  "target_level": "Senior Product Manager"
}
```

**Response:**
```json
{
  "level_assessment": {...},
  "signals": {...},
  "red_flags": [...],
  "language_analysis": {...},
  "senior_readiness": {...},
  "target_recommendations": [...]
}
```

**Error Responses:**
```json
{
  "error": "Missing required field: resume_data",
  "status": 400
}
```

---

## Prompt Engineering

### System Prompt Template

```
You are a senior recruiter with 15+ years of experience evaluating resumes. Your job is to assess how a candidate's resume signals seniority in the market.

CRITICAL RULES:
1. Evaluate based on market perception, not potential
2. Be direct and honest, but not harsh
3. Ground all assessments in specific evidence from the resume
4. If evidence is missing, say "No evidence found" - never make assumptions
5. For red flags, always explain why it matters AND how to fix it
6. Distinguish between "you're not qualified" and "your resume doesn't show it"

CONFIDENCE SCORING:
- High (85%+): Strong, consistent evidence across multiple roles
- Medium (70-84%): Some evidence, but gaps or inconsistencies
- Low (<70%): Limited or weak evidence

SIGNAL SEVERITY:
- CRITICAL: Absence prevents target-level interviews
- HIGH: Noticeable gap that weakens positioning
- MEDIUM: Nice-to-have but not dealbreaker
- LOW: Minor polish opportunity

TONE GUIDELINES:
- Direct: "Your resume doesn't show org-level impact"
- NOT judgmental: "You're not qualified for senior roles"
- Coach-style: "To credibly target Staff PM, you need..."
- NOT drill-sergeant: "You must do X or you'll fail"

RED FLAG STRUCTURE:
Always use: [Flag] → Why it matters → How to fix

Example:
"Company not found: 'Acme Startup Inc.'
→ This creates a credibility gap because recruiters cannot validate scope or scale.
→ Recommendation: Add company description (e.g., 'Series A SaaS startup, $5M ARR') or link to Crunchbase."
```

### User Message Template

```
Analyze this resume for level assessment:

TARGET LEVEL: [Senior Product Manager]

RESUME DATA:
[JSON resume data]

Provide:
1. Current level assessment with confidence score
2. Signals by category (Scope, Impact, Leadership, Technical)
3. Red flags with cause + consequence + fix
4. Language analysis
5. [If Director+ target] Senior readiness checks
6. Target level recommendations with priorities

Remember: This is market perception, not personal judgment. Be direct but supportive.
```

---

## Testing Checklist

### Functional Testing

- [ ] Level assessment generates correctly for all target levels
- [ ] Confidence meter displays correct color/icon for score
- [ ] Collapsibles expand/collapse smoothly
- [ ] Red flags show cause + consequence + fix structure
- [ ] Senior readiness checks only appear for Director+ targets
- [ ] "How to Read This" section displays on first visit
- [ ] sessionStorage persists collapsed/expanded states
- [ ] All data fields render without undefined/null errors

### Content Testing

- [ ] Level explanations are clear and non-judgmental
- [ ] Signal categories have proper definitions
- [ ] Red flags include specific fixes, not just problems
- [ ] Language analysis identifies generic phrases correctly
- [ ] Senior readiness checks use actual resume evidence
- [ ] Target recommendations are prioritized logically

### UX Testing

- [ ] First-time users understand what they're looking at
- [ ] Framing section reduces defensive reactions
- [ ] Users can navigate with keyboard only
- [ ] Mobile layout is usable on small screens
- [ ] Loading states prevent jarring content shifts
- [ ] Error states are helpful, not cryptic

### Tone Testing (Critical)

Test with real users who match these profiles:
- [ ] Mid-level aiming for senior (anxious about feedback)
- [ ] Senior validating positioning (defensive about experience)
- [ ] Career switcher (uncertain about transferability)

**Success criteria:**
- Users feel informed, not attacked
- Users understand why assessment landed where it did
- Users have clear next steps
- Users trust the assessment is fair

---

## Implementation Plan

### Phase 1: Add Framing & Context (1-2 days)

**Tasks:**
1. Add "How to Read This" collapsible section
2. Add "What This Means" context below level card
3. Update red flag structure to include cause + consequence + fix
4. Test with 3-5 beta users for tone validation

**Success Metric:**
- 80%+ of users understand why their assessment landed where it did
- <20% defensive reactions in feedback

---

### Phase 2: Enhance Red Flags (1-2 days)

**Tasks:**
1. Rewrite all red flag templates with cause + consequence structure
2. Add specific, actionable fix recommendations
3. Update backend prompt to enforce new structure
4. Test red flag output with 10+ sample resumes

**Success Metric:**
- Every red flag includes why + fix
- Users report clear understanding of credibility issues

---

### Phase 3: Add Senior Readiness Checks (2-3 days)

**Tasks:**
1. Build senior readiness UI components
2. Add competency framework logic (strategy, org-impact, authority)
3. Update backend to detect Director+ target levels
4. Test with 5+ Director-level resumes

**Success Metric:**
- Director+ candidates get explicit senior competency feedback
- Assessment distinguishes between "senior" and "principal/director" levels

---

### Phase 4: Polish & Testing (1-2 days)

**Tasks:**
1. Accessibility audit (keyboard nav, screen readers)
2. Mobile responsive testing
3. Edge case testing (missing data, malformed input)
4. Final tone validation with real users

**Success Metric:**
- No accessibility violations
- Mobile usable on devices as small as iPhone SE
- Zero crashes on edge cases

---

## Success Metrics

### Quantitative

| Metric | Current | Target |
|--------|---------|--------|
| Page bounce rate | Unknown | <20% |
| Time on page | Unknown | 3+ minutes |
| Feedback thumbs-up % | Unknown | 75%+ |
| Users who take action after viewing | Unknown | 60%+ |

### Qualitative (User Feedback)

**Questions to ask beta testers:**
1. "Did you understand why your level assessment landed where it did?" (Yes/No)
2. "Did the feedback feel fair?" (1-5 scale)
3. "What's the #1 thing you'll change based on this?" (Open-ended)
4. "Did anything feel harsh or judgmental?" (Open-ended)

**Success criteria:**
- 80%+ answer "Yes" to understanding
- 4.0+ average on fairness scale
- 90%+ have specific next step
- <10% report harsh/judgmental tone

---

## Open Questions & Decisions Needed

1. **Should we add a "Share Results" feature?**
   - Pro: Users can get second opinions
   - Con: Privacy concerns, potential for misuse

2. **Should we integrate level assessment into job analysis flow?**
   - Pro: One-stop assessment (resume + job fit)
   - Con: May overwhelm users with too much feedback at once

3. **Should we surface level assessment in tracker?**
   - Pro: Helps users prioritize applications
   - Con: May discourage applying to stretch roles

4. **Should we add a "Resume Rewrite" button after assessment?**
   - Pro: Direct path to improvement
   - Con: May set unrealistic expectations about time/effort

---

## Appendix

### Sample Level Descriptions

**Junior (IC2-IC3):**
"Early-career professional executing defined tasks with guidance. Scope limited to individual projects. Developing skills and building experience."

**Mid-Level (IC4-IC5):**
"Experienced professional owning projects end-to-end with minimal oversight. Scope includes cross-functional collaboration. Demonstrates consistent impact within team."

**Senior (IC6-IC7):**
"Expert professional leading initiatives with org-level visibility. Scope includes influencing beyond direct team. Demonstrates strategic thinking and measurable business impact."

**Staff (IC8-IC9):**
"Principal-level expert driving company-wide initiatives. Scope includes multi-quarter planning and cross-team influence. Demonstrates thought leadership and technical/strategic depth."

**Principal (IC10+):**
"Distinguished expert setting technical/strategic direction for organization. Scope includes multi-year vision and industry influence. Demonstrates authority in decision-making and talent development."

**Director:**
"Manager of managers with department-level scope. Owns functional strategy and resource allocation. Demonstrates org-level impact and people leadership."

**VP:**
"Senior leader with multi-department scope. Shapes company strategy and owns P&L. Demonstrates executive presence and business acumen."

**C-Suite:**
"Executive leader with company-wide or business unit scope. Sets strategic direction and represents organization externally. Demonstrates transformational leadership."

---

### References

- [HenryHQ Core Philosophy](./PHILOSOPHY.md)
- [Product Roadmap](./PRODUCT_STRATEGY_ROADMAP.md)
- [Implementation Guide](./IMPLEMENTATION_GUIDE.md)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial implementation | Engineering |
| 2.0 | Dec 18, 2025 | Added framing, red flag enhancements, senior readiness checks | Product |

---

**Next Review:** January 2026 (after beta user feedback)  
**Owner:** Product Team  
**Status:** Pending Phase 1 Implementation
