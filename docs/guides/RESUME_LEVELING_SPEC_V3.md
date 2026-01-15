# Resume Leveling Feature Specification (Unified)

**Version:** 3.0  
**Last Updated:** December 30, 2025  
**Status:** Production Enhancement Required  
**Owner:** Product Team

---

## Executive Summary

The Resume Leveling feature provides candidates with honest, recruiter-grade assessment of how their resume signals seniority in the market. It evaluates scope, credibility, and evidence to determine if a resume supports claims of senior-level positioning.

**This unified specification consolidates:**
- Resume Leveling Spec v2.0
- Competency Diagnostics Integration Plan v1.0
- Code audit findings (December 2025)
- LEPE integration requirements
- CEC integration requirements

**Current State:** 80-85% complete. Strong UI/UX foundation with critical gaps in coaching quality, trust-building, and competency-level granularity.

### Version 3.0 Enhancements

**Trust-Building (Critical):**
1. Add experience vs. presentation gap distinction
2. Add signal severity to backend output with frontend sort/color-coding
3. Add `quick_win` field for single highest-impact action
4. Add "Strengthen This Resume" CTA

**Detection Layers (New):**
5. Title inflation detection with evidence
6. Company credibility assessment with scale validation
7. Career switcher recognition (adjacent vs. direct ownership)
8. Competency-level mapping by function

**Integration:**
9. LEPE output in Senior Readiness section for Manager+ targets
10. CEC diagnostic data for coaching enhancement
11. Function-specific competency frameworks

---

## Table of Contents

1. [Product Philosophy](#1-product-philosophy)
2. [Page Structure & UX](#2-page-structure--ux)
3. [Detection Layers](#3-detection-layers)
4. [Scoring & Override Rules](#4-scoring--override-rules)
5. [Canonical Messaging Patterns](#5-canonical-messaging-patterns)
6. [Strategic Action Templates](#6-strategic-action-templates)
7. [Backend API Specification](#7-backend-api-specification)
8. [Frontend Implementation](#8-frontend-implementation)
9. [Prompt Engineering](#9-prompt-engineering)
10. [Testing Checklist](#10-testing-checklist)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Appendix: Competency Frameworks Reference](#12-appendix-competency-frameworks-reference)

---

## 1. Product Philosophy

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

### Critical Distinction: Experience Gap vs. Presentation Gap

**This is the #1 trust-killer for elite candidates.**

Every gap identified must be classified as one of:

| Gap Type | Definition | User Message | Action |
|----------|------------|--------------|--------|
| `experience` | Candidate genuinely needs more time/roles | "This requires more time in role. Consider..." | Development path |
| `presentation` | Candidate has the experience but resume doesn't show it | "You likely have this. Make it visible by..." | Rewrite guidance |

**Why This Matters:**
A 12-year PM being told they "lack strategic experience" when their resume just buries it is insulting. Elite candidates immediately lose trust when we conflate "you can't do this" with "your resume doesn't show this."

**Implementation:**
- Backend must return `gap_type: "experience" | "presentation"` for every gap/flag
- Claude prompt must explicitly assess: "Is this a real experience gap or a framing gap?"
- UI messaging must adapt based on gap type

### Core Philosophy: Truth + Direction

**What we provide:**
- Honest assessment of readiness without shaming
- Clear competency gaps with specific evidence
- Actionable path to close gaps
- Market reality without moral judgment

**Core Principle:** Truth + Direction, not encouragement theater.

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

### What We Never Do

**Forbidden Language:**
- "You're not good enough"
- "This is toxic to your career"
- "Companies won't hire you because..."
- "You should be more confident"
- Moral judgments about work choices
- Political framing
- Identity-based commentary

**What We Do Instead:**
- "This role requires X. Your background shows Y."
- "Market reality: Companies prioritize Z."
- "Your positioning should lead with A, not B."
- "Target these specific roles to close gaps."
- Assessment of market alignment, not personal worth
- Second-person coaching tone
- Receipts-based logic

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
- Single highest-impact action (not a laundry list)

---

## 2. Page Structure & UX

### Information Architecture

```
1. Header
   - Page title: "Resume Level Analysis"
   - Subtitle: "How your experience signals in the market"
   - Framing line: "This is how hiring managers level you, not how LinkedIn does."

2. How to Read This Section
   - Collapsed by default, visible chevron
   - Auto-expand on first visit only
   - 2-3 paragraph explainer
   - Sets frame before delivering verdict

3. Level Card (Primary Result)
   - Current Level badge
   - Confidence meter (color-coded)
   - Brief explanation

4. What This Means (Immediate Context)
   - 2-3 sentences
   - What level you can credibly target
   - What needs to change to level up

5. Quick Win Section (NEW)
   - Single highest-impact action
   - Rationale for why this matters most
   - Expected impact
   - Gap type indicator

6. Detection Alerts (NEW - when triggered)
   - Title Inflation Warning
   - Company Credibility Alert
   - Career Switcher Recognition

7. Collapsible Sections (Enhanced)
   - Signals by Category (sorted by severity)
   - Red Flags (with cause + consequence + fix + gap_type)
   - Language Analysis (with context-specific replacements)
   - Competency Assessment (function-specific)
   - Target Level Recommendations

8. Senior Readiness Checks (Director+ Only)
   - Strategy ownership evidence
   - Org-level impact signals
   - Decision-making authority indicators
   - LEPE integration

9. Strategic Actions
   - Your Move This Week
   - Close the Gap (3-month, 6-12 month path)
   - Strengthen This Resume CTA
```

### Section 2.1: How to Read This

**Purpose:** Set the frame before delivering the assessment. Prevent defensive reactions by establishing that this is market perception, not personal judgment.

**Collapsed by default with visible chevron icon.**

**Title:** "How to Read This Analysis"

**Content:**

> "This analysis evaluates how your resume will likely be interpreted by senior hiring managers and recruiters today. It looks at scope, credibility, and evidence, not your potential or capability.
>
> Your level assessment reflects what the market can verify from your resume, not what you're capable of. A gap here doesn't mean you can't do senior work. It means your resume doesn't show it yet.
>
> Think of this as a reality check from someone who's reviewed thousands of resumes. The feedback is direct because that's what helps. If something sounds harsh, remember: this is how the market sees it, not how we see you."

**Design Specifications:**
- Light background (slightly darker than page background)
- Subtle border (not alarming)
- Chevron icon (collapsed state)
- Font size: 0.95rem
- Padding: 20px
- Border-radius: 8px
- Border-left: 3px solid var(--color-primary)
- Auto-expand on first visit only
- Persist state in sessionStorage

### Section 2.2: Level Card

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

**Confidence Meter Visual Indicators:**

| Confidence | Color | Icon | Message |
|------------|-------|------|---------|
| High (≥85%) | Green (#10b981) | ✓ | "Strong evidence" |
| Medium (70-84%) | Orange (#f59e0b) | ! | "Some gaps" |
| Low (<70%) | Red (#ef4444) | ✗ | "Significant gaps" |

### Section 2.3: What This Means

Immediately below level card:

**Title:** "What This Means"

**Content (2-3 sentences):**
- What level you can credibly target
- Primary obstacle to next level
- What success looks like

**Example:**
> "Your resume currently supports Mid-Level Product Manager roles (IC4-IC5). To credibly target Senior PM roles, you need clearer evidence of org-level impact and strategic ownership. Focus on quantifying scope and demonstrating decision-making authority."

### Section 2.4: Quick Win

**Purpose:** Elite candidates don't want a laundry list. They want the one thing that moves the needle most.

```
┌─────────────────────────────────────────────────────┐
│  🎯 Your Quick Win                                  │
│  ─────────────────────────────────────────          │
│                                                     │
│  [Single highest-impact action]                     │
│                                                     │
│  Why this matters most:                             │
│  [1-2 sentence rationale]                           │
│                                                     │
│  Expected impact:                                   │
│  [Concrete outcome if fixed]                        │
│                                                     │
│  [PRESENTATION GAP badge if applicable]             │
└─────────────────────────────────────────────────────┘
```

**Selection Logic:**
1. Criticality (CRITICAL > HIGH > MEDIUM > LOW)
2. Gap type (presentation gaps prioritized since they're immediately fixable)
3. Visibility (gaps in recent/prominent roles weighted higher)
4. Fix effort (quick fixes ranked above major rewrites)

---

## 3. Detection Layers

### 3.1 Level Assessment (Core)

**Purpose:** Determine the seniority level the resume credibly supports.

**Signal Categories:**

**1. Scope Signals**
- Team size managed/influenced
- Budget responsibility
- Geographic scope (regional, national, global)
- Number of stakeholders
- Cross-functional breadth

**2. Impact Signals**
- Revenue impact ($ or %)
- Cost savings ($ or %)
- Efficiency improvements
- User/customer growth
- Market share gains

**3. Leadership Signals**
- Direct reports
- Indirect influence
- Mentorship/coaching
- Initiative ownership
- Stakeholder management at senior levels

**4. Technical/Domain Signals**
- Technical proficiency
- Domain expertise
- Certifications/credentials
- Methodologies mastered

**Signal Severity Levels:**

| Severity | Color | Definition |
|----------|-------|------------|
| CRITICAL | Red (#ef4444) | Absence prevents target-level interviews |
| HIGH | Orange (#f59e0b) | Noticeable gap that weakens positioning |
| MEDIUM | Yellow (#eab308) | Nice-to-have but not dealbreaker |
| LOW | Gray (#9ca3af) | Minor polish opportunity |

### 3.2 Title Inflation Detection

**Purpose:** Flag when resume title exceeds demonstrated scope.

**Red Flags to Check:**
1. "Senior" / "Director" / "Head of" titles with:
   - No team size mentioned
   - No budget/P&L ownership
   - No multi-quarter roadmap evidence
   - No direct reports

2. Senior titles at:
   - Unverifiable companies
   - Personal branding entities
   - Companies with no product/users/revenue

3. Title progression that doesn't match tenure:
   - "Senior PM" with 2 years total experience
   - "Director" with no prior leadership roles

**Output Structure:**
```json
{
  "title_inflation": {
    "title_alignment": "accurate" | "inflated" | "unclear",
    "title_risk_reason": "string",
    "demonstrated_level": "PM II",
    "claimed_level": "Head of Product",
    "scope_evidence": {
      "team_size": false,
      "budget_ownership": false,
      "roadmap_ownership": false,
      "direct_reports": false
    }
  }
}
```

**Canonical Coaching (when inflated):**
> "Hiring managers will evaluate this experience at a different scope than the title suggests. That gap affects senior-level competitiveness because your resume doesn't show [team size/budget/roadmap]."

### 3.3 Company Credibility Assessment

**Purpose:** Go beyond "is it a startup" to assess verifiable scale.

**Verification Levels:**

| Level | Definition | Signals |
|-------|------------|---------|
| STRONG | Public data available | Press coverage, product reviews, funding announcements, employee count verifiable |
| WEAK | Limited but present | Website exists, LinkedIn presence, product exists but unclear scale |
| UNVERIFIABLE | Cannot validate | No online presence, no product found, personal branding entities |

**Output Structure:**
```json
{
  "company_credibility": {
    "credibility": "strong" | "weak" | "unverifiable",
    "verification_signals": {
      "press_coverage": true,
      "product_active": true,
      "funding_verified": true,
      "employees_verifiable": true
    },
    "market_discount": 0.0,
    "scale_indicators": {
      "user_base": "10M+",
      "revenue": "$50M ARR",
      "funding": "Series C",
      "employees": 500
    }
  }
}
```

**Canonical Coaching (when unverifiable):**
> "This company cannot be validated at the scale your role implies. Hiring managers will evaluate your experience as individual contribution rather than senior leadership. Lead with verifiable scale companies in your positioning."

### 3.4 Competency-Level Mapping

**Purpose:** Map resume evidence to industry-standard competency levels.

**Competency Dimensions (PM Example):**
1. Product Strategy - Vision, market positioning, competitive analysis
2. Customer Insight - User research, empathy, problem identification
3. Roadmap Ownership - Prioritization, tradeoffs, multi-quarter planning
4. Metrics & Outcomes - KPI definition, measurement, impact tracking
5. Cross-functional Leadership - Influence, alignment, stakeholder management
6. Scale Complexity - Team size, user base, revenue/budget, organizational scope
7. Execution - Delivery, launch management, operational excellence
8. Technical Judgment - Architecture understanding, tech tradeoff evaluation

**Level Definitions (PM):**

| Level | Years | Scope | Key Distinction |
|-------|-------|-------|-----------------|
| PM I / Associate PM | 0-2 | Feature ownership | Executes on roadmap, learns process |
| PM II / Product Manager | 2-4 | Product area ownership | Defines roadmap for area, some strategy |
| Senior PM | 4-8 | Product/platform ownership | Sets strategy, influences org, proven scale |
| Staff PM | 8-12 | Multi-product/platform | Org-level impact, architectural decisions |
| Principal PM | 12+ | Company-level initiatives | Strategic direction, exec partnership |

**Output Structure:**
```json
{
  "competency_mapping": {
    "required_level": "Senior PM",
    "demonstrated_level": "PM II",
    "competency_scores": {
      "product_strategy": {
        "level": "PM II",
        "evidence": ["Feature-level execution", "Limited strategic ownership"],
        "gap_type": "presentation"
      },
      "scale_complexity": {
        "level": "PM I",
        "evidence": ["500K users max", "No revenue accountability"],
        "gap_type": "experience"
      }
    },
    "gaps": [
      {
        "dimension": "Product Strategy",
        "description": "Role requires product-level strategy. Resume shows feature-level execution.",
        "gap_type": "presentation"
      }
    ]
  }
}
```

### 3.5 Career Switcher Recognition

**Purpose:** Detect adjacent exposure vs. direct ownership.

**Switcher Patterns:**

**1. "Product Manager" with:**
- Program/project management background
- Operations/advocacy work
- Tool usage without decision ownership

**2. "Engineering Manager" with:**
- Tech support/operations background
- Solutions engineering
- No architecture/design ownership

**3. "Senior X" with:**
- Participation in X, not ownership of X
- Supporting role presented as lead role
- Exposure without accountability

**Evidence Types:**
| Type | Examples |
|------|----------|
| DIRECT | "Owned roadmap", "Defined strategy", "Shipped product" |
| ADJACENT | "Supported PM team", "Contributed to strategy", "Involved in launch" |
| EXPOSURE | "Participated in", "Familiar with", "Exposure to" |

**Output Structure:**
```json
{
  "career_switcher": {
    "is_switcher": true,
    "switcher_type": "functional",
    "prior_function": "Program Management",
    "target_function": "Product Management",
    "ownership_level": "adjacent",
    "coaching": "Your background shows adjacent exposure to product management, not direct ownership. Senior roles require demonstrated decision-making in product strategy."
  }
}
```

**Canonical Coaching:**
> "Your background is Program Management, not Product Management. Your resume shows adjacent exposure ('supported PM team', 'contributed to roadmap'), not direct product ownership. Senior PM roles require demonstrated product decision-making. Target Associate PM or PM I roles to build direct ownership."

### 3.6 LEPE Integration (Manager+ Only)

When analyzing Manager+ target roles, integrate LEPE output:

**Display in Senior Readiness Section:**
```
┌────────────────────────────────────────────────────────────┐
│  People Leadership Assessment                              │
│  ─────────────────────────────────────────────────         │
│                                                            │
│  Leadership Tenure: 4.75 years (Tier 2)                    │
│  Target Requirement: 6+ years                              │
│  Gap: 1.25 years                                           │
│                                                            │
│  Detected Competencies:                                    │
│  ✓ People Management (strong evidence)                     │
│  ✓ Decision Authority (strong evidence)                    │
│  ! Cross-Functional Influence (partial evidence)           │
│  ✗ Org Design & Scale (missing)                            │
│                                                            │
│  Positioning Mode: POSITIONING                             │
│  "You can apply with strategic positioning. Address the    │
│  global scope gap proactively in your cover letter."       │
└────────────────────────────────────────────────────────────┘
```

### 3.7 CEC Integration

The Capability Evidence Check provides diagnostic detail that enhances coaching quality:

**How CEC Feeds Resume Leveling:**
1. `evidence_status` (explicit/implicit/missing) informs `gap_type` classification
2. `diagnosis` field provides recruiter-grade explanation
3. `distance` field quantifies the gap clearly
4. `coachable` boolean helps prioritize quick_win selection

---

## 4. Scoring & Override Rules

### Hard Overrides

Regardless of raw fit score:

| Condition | Hard Cap | Recommendation |
|-----------|----------|----------------|
| Career switcher + no direct ownership | 40% | Long Shot / Do Not Apply |
| Senior role required + PM II competencies | 40% | Long Shot / Do Not Apply |
| Unverifiable company + senior role claim | 45% | Conditional Apply / Long Shot |
| Inflated title + missing competencies | 55% | Apply / Conditional Apply |

### Override Logic

```python
def apply_competency_overrides(
    base_fit_score: int,
    title_inflation: Dict,
    competency_alignment: Dict,
    company_credibility: Dict,
    career_switcher: Dict
) -> Dict:
    """
    Apply competency-based hard caps after basic fit scoring.
    
    Priority order (first match wins):
    1. Career switcher + no ownership -> cap at 40%
    2. PM II demonstrated + Senior PM required -> cap at 40%
    3. Unverifiable company + senior claim -> cap at 45%
    4. Title inflation + competency gap -> cap at 55%
    """
    capped_score = base_fit_score
    override_reason = None
    
    # Career switcher with no direct ownership
    if career_switcher["is_switcher"] and \
       career_switcher["ownership_level"] in ["adjacent", "exposure"]:
        capped_score = min(capped_score, 40)
        override_reason = "Career switcher with adjacent exposure, not direct ownership"
    
    # Competency level mismatch (3+ gaps)
    elif competency_alignment.get("gaps_count", 0) >= 3:
        capped_score = min(capped_score, 40)
        override_reason = "Significant competency gaps for required level"
    
    # Unverifiable company with senior claim
    elif company_credibility["credibility"] == "unverifiable" and \
         "senior" in competency_alignment.get("required_level", "").lower():
        capped_score = min(capped_score, 45)
        override_reason = "Cannot verify scale claimed in senior role"
    
    # Title inflation with competency gap
    elif title_inflation["title_alignment"] == "inflated":
        capped_score = min(capped_score, 55)
        override_reason = "Title exceeds demonstrated competency level"
    
    return {
        "capped_score": capped_score,
        "override_applied": capped_score < base_fit_score,
        "override_reason": override_reason
    }
```

---

## 5. Canonical Messaging Patterns

**Purpose:** Single, repeatable voice for sensitive feedback. Use these exact phrasings to maintain consistency and calm tone.

### Pattern 1: Title Inflation

**Use when:** Resume title exceeds demonstrated scope

**Canonical phrasing:**
> "Hiring managers will evaluate this experience at a different scope than the title suggests. That gap affects senior-level competitiveness."

**Context additions:**
- If unverifiable company: Add "because the company cannot be validated at scale"
- If missing scope signals: Add "because your resume doesn't show [team size/budget/roadmap]"

**Never say:** "Your title is inflated", "This looks suspicious", "Companies won't believe this"

### Pattern 2: Unverifiable Company

**Use when:** Cannot validate company at claimed scale

**Canonical phrasing:**
> "This company cannot be validated at the scale your role implies. Hiring managers will evaluate your experience as individual contribution rather than senior leadership. Lead with verifiable scale companies in your positioning."

**Never say:** "This company doesn't exist", "This looks like a fake company", "This is a red flag"

### Pattern 3: Career Switcher

**Use when:** Resume shows adjacent exposure, not direct ownership

**Canonical phrasing:**
> "Your background shows adjacent exposure to [function], not direct ownership. Senior roles require demonstrated decision-making in [specific area]."

**Never say:** "You're not a real [role]", "This isn't legitimate experience"

### Pattern 4: Competency Gap

**Use when:** Demonstrated level < Required level

**Canonical phrasing:**
> "This role requires [required level] competencies. Your background shows [demonstrated level] evidence. The gap is in [specific dimensions]."

**Never say:** "You're not senior enough", "You're underqualified", "You don't have the skills"

### Pattern 5: Experience Gap vs Presentation Gap

**Experience Gap:**
> "This requires more time in role. Consider targeting [lower level] roles to build [specific competency]."

**Presentation Gap:**
> "You likely have this experience. Make it visible by [specific action]. Your [specific role] probably included [inferred activity] that isn't showing on your resume."

---

## 6. Strategic Action Templates

### Template: Senior-Level Misalignment

```
COMPETENCY ASSESSMENT: {demonstrated_level} → {required_level}

This role expects {required_level} competencies across {dimensions}.
Your background shows {demonstrated_level} evidence but not sustained 
ownership at {required_level}.

KEY GAPS:
1. {gap_1_dimension}: {specific_gap_description} [{gap_type}]
2. {gap_2_dimension}: {specific_gap_description} [{gap_type}]
3. {gap_3_dimension}: {specific_gap_description} [{gap_type}]

MARKET REALITY:
{title_inflation_coaching if applicable}
{company_credibility_coaching if applicable}
{career_switcher_coaching if applicable}

YOUR MOVE THIS WEEK:
1. Target these roles: {3 specific role titles at appropriate level}
2. Add this evidence: {1-2 specific improvements to resume}
3. Deprioritize: {what to stop applying to immediately}

CLOSE THE GAP:
- Next 3 months: {specific competency to build + how}
- Next 6-12 months: {level advancement path}
- Ready when: {concrete readiness signal}
```

### Example Output

```
COMPETENCY ASSESSMENT: PM II → Senior PM

This role expects Senior PM competencies across product strategy, scale 
complexity, and cross-functional leadership. Your background shows PM II 
evidence (feature-level ownership, 500K users) but not sustained ownership 
at Senior PM level.

KEY GAPS:
1. Product Strategy: Role requires product-level vision. Your resume shows 
   feature-level execution with limited strategic influence. [PRESENTATION]

2. Scale Complexity: Role manages $50M+ revenue and 20M+ users. Your resume 
   shows 500K users max and no revenue accountability. [EXPERIENCE]

3. Cross-functional Leadership: Role requires VP-level influence. Your resume 
   shows peer-level coordination, not executive stakeholder management. [PRESENTATION]

MARKET REALITY:
Hiring managers will evaluate this experience at a different scope than the 
title suggests. That gap affects senior-level competitiveness because your 
resume doesn't show team size, budget ownership, or multi-product roadmap.

YOUR MOVE THIS WEEK:
1. Target these roles: "Product Manager" (not Senior) at Stripe, Atlassian, 
   Shopify; "PM II" at Databricks, Figma
2. Add this evidence: Quantify your largest user base (use "500K users" 
   explicitly). Add one cross-functional project where you influenced 
   engineering + design + data.
3. Deprioritize: Stop applying to Senior PM, Staff PM, or Head of Product 
   roles immediately.

CLOSE THE GAP:
- Next 3 months: Own a product area (not feature) with measurable outcomes. 
  Add one exec stakeholder relationship to your resume.
- Next 6-12 months: Scale to 5M+ users. Lead cross-functional initiative 
  with 3+ teams.
- Ready when: You can point to product-level roadmap, 5M+ scale, and exec 
  partnership on your resume.
```

---

## 7. Backend API Specification

### Endpoint: `/api/resume/level-assessment`

**Method:** POST

**Request Body:**
```json
{
  "resume_data": {...},
  "target_level": "Senior Product Manager",
  "function": "product_management"
}
```

### Complete Response Schema (v3.0)

```json
{
  "level_assessment": {
    "current_level": "PM II",
    "confidence": 72,
    "confidence_label": "Medium",
    "explanation": "Your resume shows PM II competencies with some Senior PM evidence...",
    "what_this_means": "Your resume currently supports PM II roles. To target Senior PM, focus on..."
  },
  
  "quick_win": {
    "action": "Add quantified impact to your Spotify role bullets",
    "rationale": "Your Spotify experience is your strongest positioning asset, but zero bullets include metrics.",
    "expected_impact": "Closing this gap moves you from 'maybe interview' to 'definitely interview'",
    "gap_type": "presentation"
  },
  
  "detection_layers": {
    "title_inflation": {
      "title_alignment": "inflated",
      "title_risk_reason": "Head of Product title at unverifiable company with no team evidence",
      "demonstrated_level": "PM II",
      "claimed_level": "Head of Product",
      "scope_evidence": {
        "team_size": false,
        "budget_ownership": false,
        "roadmap_ownership": false,
        "direct_reports": false
      }
    },
    
    "company_credibility": {
      "company_name": "InnovateTech Solutions",
      "credibility": "unverifiable",
      "verification_signals": {
        "press_coverage": false,
        "product_active": false,
        "funding_verified": false,
        "employees_verifiable": false
      },
      "market_discount": 0.5
    },
    
    "career_switcher": {
      "is_switcher": false,
      "switcher_type": null,
      "prior_function": null,
      "target_function": null,
      "ownership_level": "direct"
    },
    
    "competency_mapping": {
      "function_detected": "product_management",
      "required_level": "Senior PM",
      "demonstrated_level": "PM II",
      "competency_scores": {
        "product_strategy": {
          "level": "PM II",
          "evidence": ["Feature roadmap ownership", "No product-level vision"],
          "gap_type": "presentation"
        },
        "customer_insight": {
          "level": "Senior PM",
          "evidence": ["User research leadership", "Segment definition"],
          "gap_type": null
        },
        "scale_complexity": {
          "level": "PM I",
          "evidence": ["500K users", "No revenue accountability"],
          "gap_type": "experience"
        },
        "cross_functional_leadership": {
          "level": "PM II",
          "evidence": ["Peer coordination", "No VP stakeholders"],
          "gap_type": "presentation"
        }
      },
      "gaps_count": 3
    }
  },
  
  "signals": {
    "scope": [
      {
        "text": "Led 15-person engineering team",
        "severity": "HIGH",
        "source": "Uber - Senior PM",
        "gap_type": null
      },
      {
        "text": "No evidence of budget ownership",
        "severity": "CRITICAL",
        "source": null,
        "gap_type": "presentation"
      }
    ],
    "impact": [...],
    "leadership": [...],
    "technical": [...]
  },
  
  "red_flags": [
    {
      "type": "Title Inflation",
      "instance": "'Head of Product' at InnovateTech Solutions",
      "why_it_matters": "Hiring managers will evaluate this experience at a different scope than the title suggests.",
      "gap_type": "presentation",
      "how_to_fix": [
        "Use functional title reflecting actual scope (e.g., 'Product Lead')",
        "Add company context (size, stage, funding)",
        "Emphasize scope in bullets (team size, budget)"
      ]
    },
    {
      "type": "Generic Language",
      "instance": "'team player' in summary",
      "why_it_matters": "Generic phrases don't differentiate you. Senior roles require evidence, not claims.",
      "gap_type": "presentation",
      "how_to_fix": [
        "Replace 'team player' with 'led cross-functional squad of 8 engineers and 3 designers to ship payment integration'"
      ],
      "source_bullets": ["Original: 'Team player with strong communication'", "Your Stripe role shows: Led cross-functional billing platform redesign"]
    }
  ],
  
  "language_analysis": {
    "tone": "Professional",
    "clarity": "Clear",
    "specificity": "Medium",
    "generic_phrases": ["team player", "results-driven"],
    "generic_phrase_replacements": [
      {
        "phrase": "team player",
        "suggested_replacement": "led cross-functional squad of 8 to ship payment integration",
        "source_bullet": "Stripe - Senior PM: 'Led cross-functional team on billing platform redesign'"
      }
    ],
    "quantification_rate": 0.45,
    "action_verb_distribution": {
      "strong": ["led", "owned"],
      "weak": ["helped", "assisted"]
    }
  },
  
  "senior_readiness": {
    "show": true,
    "competencies": {
      "strategy_ownership": {
        "assessment": "Partial",
        "evidence": "Feature-level roadmap, no product vision",
        "recommendation": "Add evidence of product-level strategy decisions",
        "gap_type": "presentation"
      },
      "org_level_impact": {
        "assessment": "Missing",
        "evidence": null,
        "recommendation": "This requires cross-team initiatives at scale",
        "gap_type": "experience"
      },
      "decision_authority": {
        "assessment": "Missing",
        "evidence": null,
        "recommendation": "Add budget/hiring ownership evidence",
        "gap_type": "presentation"
      }
    },
    "lepe_integration": {
      "tenure": 4.75,
      "tier": "Tier 2",
      "target_requirement": 6,
      "gap": 1.25,
      "detected_competencies": ["People Management", "Decision Authority"],
      "missing_competencies": ["Org Design & Scale"],
      "positioning_mode": "POSITIONING",
      "coaching_advice": "You can apply with strategic positioning. Address the leadership tenure gap proactively."
    }
  },
  
  "strategic_actions": {
    "your_move_this_week": [
      {
        "action": "Target these roles",
        "details": "Product Manager (not Senior) at Stripe, Atlassian, Shopify"
      },
      {
        "action": "Add this evidence",
        "details": "Quantify user base explicitly. Add cross-functional project."
      },
      {
        "action": "Deprioritize",
        "details": "Stop applying to Senior PM, Staff PM, Head of Product roles"
      }
    ],
    "close_the_gap": {
      "three_months": "Own a product area (not feature) with measurable outcomes",
      "six_to_twelve_months": "Scale to 5M+ users. Lead cross-functional initiative.",
      "ready_when": "Product-level roadmap, 5M+ scale, exec partnership on resume"
    }
  },
  
  "override_applied": {
    "original_score": 68,
    "capped_score": 55,
    "override_reason": "Title exceeds demonstrated competency level",
    "recommendation": "Conditional Apply"
  },
  
  "target_recommendations": [
    {
      "level": "PM II",
      "priority": "High",
      "gap": "Current demonstrated level - apply confidently",
      "gap_type": null
    },
    {
      "level": "Senior PM",
      "priority": "Medium",
      "gap": "Need product-level strategy and 5M+ scale evidence",
      "gap_type": "mixed"
    }
  ]
}
```

---

## 8. Frontend Implementation

### Critical Framing (Top of Page)

```html
<div class="leveling-intro">
  <p class="framing-statement">
    This is how hiring managers level you, not how LinkedIn does.
  </p>
</div>
```

### Detection Alert Display

When detection layers trigger warnings:

```html
<div class="detection-alerts">
  <!-- Title Inflation Alert -->
  <div class="alert alert-warning" v-if="titleInflation.title_alignment === 'inflated'">
    <span class="alert-icon">⚠️</span>
    <div class="alert-content">
      <strong>Title-Scope Mismatch Detected</strong>
      <p>{{ titleInflation.coaching }}</p>
    </div>
  </div>
  
  <!-- Company Credibility Alert -->
  <div class="alert alert-caution" v-if="companyCredibility.credibility === 'unverifiable'">
    <span class="alert-icon">🔍</span>
    <div class="alert-content">
      <strong>Company Verification Issue</strong>
      <p>{{ companyCredibility.coaching }}</p>
    </div>
  </div>
  
  <!-- Career Switcher Alert -->
  <div class="alert alert-info" v-if="careerSwitcher.is_switcher">
    <span class="alert-icon">🔄</span>
    <div class="alert-content">
      <strong>Career Transition Detected</strong>
      <p>{{ careerSwitcher.coaching }}</p>
    </div>
  </div>
</div>
```

### Strategic Action Display

```html
<div class="strategic-coaching">
  <section class="gaps">
    <h3>Key Gaps</h3>
    <ul>
      <li v-for="gap in competencyMapping.gaps">
        {{ gap.dimension }}: {{ gap.description }}
        <span class="gap-badge" :class="gap.gap_type">{{ gap.gap_type }}</span>
      </li>
    </ul>
  </section>
  
  <section class="market-reality" v-if="hasMarketRealityCoaching">
    <h3>Market Reality</h3>
    <p>{{ marketRealityCoaching }}</p>
  </section>
  
  <section class="your-move">
    <h3>Your Move This Week</h3>
    <ol>
      <li v-for="action in strategicActions.your_move_this_week">
        <strong>{{ action.action }}:</strong> {{ action.details }}
      </li>
    </ol>
  </section>
  
  <section class="close-gap">
    <h3>Close the Gap</h3>
    <div class="timeline">
      <div class="milestone">
        <span class="timeframe">Next 3 months</span>
        <p>{{ strategicActions.close_the_gap.three_months }}</p>
      </div>
      <div class="milestone">
        <span class="timeframe">6-12 months</span>
        <p>{{ strategicActions.close_the_gap.six_to_twelve_months }}</p>
      </div>
      <div class="milestone ready">
        <span class="timeframe">Ready when</span>
        <p>{{ strategicActions.close_the_gap.ready_when }}</p>
      </div>
    </div>
  </section>
  
  <section class="cta">
    <button id="strengthen-cta" class="btn-primary">
      Strengthen This Resume
    </button>
  </section>
</div>
```

### Strengthen CTA Behavior

```javascript
document.getElementById('strengthen-cta').addEventListener('click', function() {
    sessionStorage.setItem('levelingContext', JSON.stringify({
        assessment: levelingResults,
        quickWin: levelingResults.quick_win,
        gaps: levelingResults.red_flags,
        targetLevel: levelingResults.target_level,
        competencyMapping: levelingResults.detection_layers.competency_mapping
    }));
    window.location.href = 'strengthen.html';
});
```

### Visual Design

**Color Palette:**
```css
--level-high: #10b981;
--level-medium: #f59e0b;
--level-low: #ef4444;
--gap-experience: #6366f1;
--gap-presentation: #22c55e;
--alert-warning: #fef3cd;
--alert-caution: #fff3cd;
--alert-info: #cfe2ff;
```

**Gap Type Badges:**
```css
.gap-badge.experience {
  background: var(--gap-experience);
  color: white;
}
.gap-badge.presentation {
  background: var(--gap-presentation);
  color: white;
}
```

---

## 9. Prompt Engineering

### System Prompt (v3.0)

```
You are a senior recruiter with 15+ years of experience evaluating resumes. Your job is to assess how a candidate's resume signals seniority in the market.

CRITICAL RULES:
1. Evaluate based on market perception, not potential
2. Be direct and honest, but not harsh
3. Ground all assessments in specific evidence from the resume
4. If evidence is missing, say "No evidence found" - never make assumptions
5. For red flags, always explain why it matters AND how to fix it

GAP TYPE CLASSIFICATION (CRITICAL):
For EVERY gap you identify, you MUST classify it:
- "experience": Candidate genuinely needs more time/roles to close this gap
- "presentation": Candidate likely has this experience but resume doesn't show it

Example experience gap:
"Decision Authority - Missing. No evidence of budget ownership or hiring decisions. This requires more time in senior roles where you own headcount and spend."

Example presentation gap:
"Org-Level Impact - Partial. Your Spotify role likely had broader impact than shown. Your bullets focus on feature execution, not the org-level initiatives you influenced."

DETECTION LAYERS:
1. Title Inflation: Flag when title exceeds demonstrated scope
2. Company Credibility: Assess if company can be validated at claimed scale
3. Career Switcher: Detect adjacent exposure vs direct ownership
4. Competency Mapping: Map resume evidence to industry-standard levels

QUICK WIN SELECTION:
- Select the single highest-impact fix
- Prioritize: presentation gaps > experience gaps (presentation is immediately fixable)
- Provide specific guidance tied to their actual resume content

GENERIC PHRASE REPLACEMENTS:
- Do NOT give generic advice like "add quantification"
- Look at their actual roles and provide specific replacements
- Example: Replace "team player" with "led cross-functional squad of 8" (from their Stripe role)

CANONICAL MESSAGING:
- Title Inflation: "Hiring managers will evaluate this experience at a different scope than the title suggests."
- Unverifiable Company: "This company cannot be validated at the scale your role implies."
- Career Switcher: "Your background shows adjacent exposure to [function], not direct ownership."
- Competency Gap: "This role requires [X] competencies. Your background shows [Y] evidence."

FORBIDDEN LANGUAGE:
- "You're not good enough"
- "This is toxic to your career"
- "Companies won't hire you because..."
- "Your title is inflated" (use canonical phrasing instead)

TONE:
- Direct: "Your resume doesn't show org-level impact"
- NOT judgmental: "You're not qualified for senior roles"
- Coach-style: "To credibly target Staff PM, you need..."
- NOT drill-sergeant: "You must do X or you'll fail"

OUTPUT REQUIREMENTS:
1. Every gap must have gap_type
2. Quick win must be populated
3. Signals sorted by severity (CRITICAL first)
4. Generic phrase replacements must use actual resume content
5. Strategic actions must include specific role targets
```

---

## 10. Testing Checklist

### Functional Testing

- [ ] Level assessment generates correctly for all target levels
- [ ] Confidence meter displays correct color/icon for score
- [ ] Collapsibles expand/collapse smoothly
- [ ] Red flags show cause + consequence + gap_type + fix structure
- [ ] Senior readiness checks only appear for Director+ targets
- [ ] LEPE integration appears for Manager+ targets
- [ ] "How to Read This" section displays on first visit
- [ ] sessionStorage persists collapsed/expanded states
- [ ] All data fields render without undefined/null errors
- [ ] Quick win section always populated
- [ ] Signals sorted by severity within each category
- [ ] Strengthen CTA passes context correctly

### Detection Layer Testing

- [ ] Title inflation detected when title exceeds scope
- [ ] Company credibility assessed correctly (strong/weak/unverifiable)
- [ ] Career switcher patterns detected (adjacent vs direct)
- [ ] Competency mapping aligns with function (PM, Eng, etc.)
- [ ] Override rules apply correctly (caps enforced)

### Content Testing

- [ ] Level explanations are clear and non-judgmental
- [ ] Gap types correctly classified as experience vs presentation
- [ ] Generic phrase replacements use candidate's actual experience
- [ ] Strategic actions include specific role targets
- [ ] Canonical messaging patterns used consistently
- [ ] Forbidden language never appears

### Test Cases

**Test Case 1: Title Inflation**
- Resume: "Head of Product" at 2-person unverifiable company
- Expected: title_alignment = "inflated", cap at 55%

**Test Case 2: Competency Mismatch**
- Resume: 5 years PM, 500K users max, peer-level coordination
- JD: Senior PM at Series C (20M users, $100M revenue)
- Expected: demonstrated_level = "PM II", gaps in scale and leadership

**Test Case 3: Career Switcher**
- Resume: "Product Manager" with 8 years Program Management
- Language: "Supported PM team", "Contributed to roadmap"
- Expected: is_switcher = true, ownership_level = "adjacent", cap at 40%

**Test Case 4: Presentation Gap**
- Resume: Strong Spotify PM role with weak bullet language
- Expected: gap_type = "presentation" with specific rewrite guidance

---

## 11. Implementation Roadmap

### Phase 1: Trust-Building (Days 1-3)

**Tasks:**
1. Add `gap_type` field to backend output
2. Update Claude prompt to classify gap types
3. Add `quick_win` field to backend response
4. Add signal severity to backend output
5. Update frontend to sort signals by severity
6. Add gap_type indicator to UI messaging

**Success Metric:**
- Every gap classified as experience or presentation
- Quick win always populated
- Signals sorted by criticality

### Phase 2: Detection Layers (Days 4-7)

**Tasks:**
1. Implement `detect_title_inflation()` function
2. Implement `assess_company_credibility()` enhanced version
3. Add override logic to fit scoring
4. Update coaching templates for title/company issues
5. Add detection alerts to frontend

**Success Metric:**
- 90%+ inflated titles detected
- 95%+ unverifiable companies identified
- Override caps applied correctly

### Phase 3: Competency Mapping (Days 8-12)

**Tasks:**
1. Implement PM competency mapping
2. Implement Engineering competency mapping
3. Build competency evidence detector
4. Integrate with fit scoring
5. Add competency-specific coaching
6. Surface function-specific competencies in UI

**Success Metric:**
- 80%+ of resume evidence mapped to competency levels
- Competency-specific gaps identified
- Function detected correctly for 90%+ resumes

### Phase 4: Career Switcher & Strategic Actions (Days 13-15)

**Tasks:**
1. Implement `detect_career_switcher()` function
2. Build ownership level classifier
3. Create switcher-specific coaching templates
4. Implement strategic action templates
5. Add "Strengthen This Resume" CTA
6. Add "Close the Gap" timeline

**Success Metric:**
- Career switchers correctly identified
- Strategic actions include specific role targets
- Clear path from assessment to action

### Phase 5: Polish & Integration (Days 16-18)

**Tasks:**
1. Integrate LEPE output into Senior Readiness
2. Integrate CEC diagnostic data
3. Accessibility audit
4. Mobile responsive testing
5. Edge case testing
6. Final tone validation with real users

**Success Metric:**
- No accessibility violations
- Mobile usable on iPhone SE
- <10% of users report generic/unhelpful advice
- 90%+ understand gap type distinction

---

## 12. Appendix: Competency Frameworks Reference

### Product Management Competencies

**PM I / Associate PM (0-2 years)**
```json
{
  "scope": "Feature ownership",
  "product_strategy": "Executes on product roadmap",
  "customer_insight": "Contributes to user research",
  "scale_complexity": "Small user base (<100K)",
  "evidence_signals": ["Shipped features", "Followed PRD", "Supported roadmap execution"]
}
```

**PM II / Product Manager (2-4 years)**
```json
{
  "scope": "Product area ownership",
  "product_strategy": "Defines roadmap for area, some strategy",
  "customer_insight": "Leads user research for area",
  "scale_complexity": "Growing user base (100K-1M)",
  "evidence_signals": ["Owned feature roadmap", "Defined area priorities", "Some cross-functional influence"]
}
```

**Senior PM (4-8 years)**
```json
{
  "scope": "Product/platform ownership",
  "product_strategy": "Owns product strategy",
  "customer_insight": "Directs research strategy",
  "scale_complexity": "Significant scale (10M+ users, $50M+ revenue)",
  "evidence_signals": ["Defined product vision", "Set multi-quarter roadmap", "VP-level stakeholders", "Build/buy/partner decisions"]
}
```

**Staff PM (8-12 years)**
```json
{
  "scope": "Multi-product/platform",
  "product_strategy": "Defines org-level product direction",
  "customer_insight": "Influences company-wide customer strategy",
  "scale_complexity": "Massive scale (50M+ users, $200M+ revenue)",
  "evidence_signals": ["Company-wide initiatives", "Architectural decisions", "Executive partnership", "Multiple product ownership"]
}
```

**Principal PM (12+ years)**
```json
{
  "scope": "Company-level initiatives",
  "product_strategy": "Sets strategic direction for organization",
  "customer_insight": "Industry-level customer thought leadership",
  "scale_complexity": "Enterprise scale",
  "evidence_signals": ["Strategic direction setting", "Board-level influence", "Industry recognition", "Talent development"]
}
```

### Engineering Competencies (Summary)

| Level | Scope | Technical Depth | Leadership |
|-------|-------|-----------------|------------|
| Engineer | Individual tasks | Implements solutions | Self-directed |
| Senior Engineer | Project ownership | Designs systems | Mentors juniors |
| Staff Engineer | Multi-project | Architectural decisions | Influences org |
| Principal Engineer | Organization-wide | Technical strategy | Defines standards |

### Leadership Level Reference (LEPE)

| Tier | Definition | People Leadership |
|------|------------|-------------------|
| Tier 1 | Strategic/functional leadership | No direct reports |
| Tier 2 | People leadership | Direct reports, hiring/firing |
| Tier 3 | Org-level leadership | Managing managers, P&L |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial implementation | Engineering |
| 2.0 | Dec 18, 2025 | Added framing, red flag enhancements, senior readiness | Product |
| 3.0 | Dec 30, 2025 | Unified spec: merged Competency Diagnostics, audit fixes, LEPE/CEC integration | Product |

---

**Status:** Ready for Implementation  
**Next Review:** January 2026  
**Owner:** Product Team
