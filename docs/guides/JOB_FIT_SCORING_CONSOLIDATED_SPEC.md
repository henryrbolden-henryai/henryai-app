# Job Fit Scoring Consolidated Specification

**Version**: 4.0
**Date**: December 30, 2025
**Status**: CANONICAL - Supersedes all previous specs
**Owner**: Henry / HenryHQ Product

---

## Purpose

This document is the single source of truth for Job Fit Scoring. It consolidates and supersedes:
- JOB_FIT_SCORING_SPEC.md (v3.0)
- REALITY_CHECK_SPEC.md (v1.0)
- CEC_SPECIFICATION_V1.md (v1.0)
- FRONTEND_CONTRACT.md (v1.0)

**Why this exists:** Previous specs defined WHAT each component should do but not WHO OWNS the output. This created three systems fighting over the same fields. This spec resolves ownership, eliminates redundancy, and enforces separation of concerns.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Ownership](#2-component-ownership)
3. [Score Summary Card](#3-score-summary-card)
4. [Your Move](#4-your-move)
5. [Reality Check](#5-reality-check)
6. [Gaps to Address](#6-gaps-to-address)
7. [The Opportunity](#7-the-opportunity)
8. [Outreach Templates](#8-outreach-templates)
9. [Information Flow Rules](#9-information-flow-rules)
10. [Tier Permissions](#10-tier-permissions)
11. [Tone and Voice](#11-tone-and-voice)
12. [Schema Definitions](#12-schema-definitions)
13. [Validation Rules](#13-validation-rules)
14. [Implementation Checklist](#14-implementation-checklist)
15. [Failure States](#15-failure-states)
16. [Auditing and Drift Control](#16-auditing-and-drift-control)
17. [Versioning and Backward Compatibility](#17-versioning-and-backward-compatibility)
18. [Human Override Policy](#18-human-override-policy)
19. [Performance Constraints](#19-performance-constraints)

---

## 1. Architecture Overview

### Execution Flow

```
1. Resume Parse → resume_data
2. JD Analysis → jd_requirements
3. Claude API Call → base analysis (50/30/20 scoring)
4. Eligibility Gate → hard requirement check
5. Experience Penalties → force_apply_experience_penalties()
6. Calibration Layer → CEC, red flags, role-specific adjustments
7. Final Recommendation Lock → IMMUTABLE
8. Output Generation → Score Summary, Your Move, Reality Check, Gaps
9. Frontend Render → tier-appropriate display
```

### Key Principle

**Scoring happens early. Decision locks late. Coaching uses the locked decision.**

Once the recommendation is locked, no downstream system can change it. All coaching, Reality Check, and Your Move content must align with the locked decision.

---

## 2. Component Ownership

This is the critical section that resolves the current conflicts.

### Ownership Matrix

| Component | Owner | Fallback | Can Modify Score? | Can Modify Recommendation? |
|-----------|-------|----------|-------------------|---------------------------|
| Score Summary | Claude | None (required output) | N/A (this IS the score) | N/A (this IS the recommendation) |
| Your Move | Claude | None (required output) | No | No |
| Reality Check | Backend calculation + Claude | Backend defaults | No | No |
| Gaps to Address | CEC Layer | Claude gaps[] array | No | No |
| The Opportunity | Claude | None (optional) | No | No |
| Outreach Templates | Claude | None (required for Principal+) | No | No |

### Ownership Rules

**Rule 1: Claude owns Your Move completely.**
- The coaching controller does NOT generate Your Move
- The coaching controller may ENRICH Your Move with CEC data
- If Claude's Your Move is missing/short, the response fails validation (not silently replaced)

**Rule 2: No fallback logic that restates fit.**
- If a component is missing, surface an error
- Never fill gaps by repeating information from another component

**Rule 3: Each field has exactly one writer.**
- `your_move` is written by Claude only
- `reality_check_market_data` is written by backend calculation only
- `reality_check_strategic_context` is written by Claude only
- No field is written by multiple systems

### Deprecated Patterns

The following patterns are explicitly deprecated and must be removed:

```python
# DEPRECATED - Remove this fallback
if not your_move_summary or len(your_move_summary) < 50:
    your_move_summary = coaching_controller.generate_your_move()

# DEPRECATED - Remove this overloaded field
strategic_action  # Split into your_move + reality_check_strategic_context

# DEPRECATED - Remove fit restating in coaching
"Your background in X gives you an edge..."  # This belongs in Score Summary, not Your Move
```

---

## 3. Score Summary Card

### Purpose

Assessment verdict. What's the fit and why. This is the ONLY place fit assessment lives.

### Appears For

All tiers (Sourcer through Coach)

### Required Fields

| Field | Type | Character Limit | Description |
|-------|------|-----------------|-------------|
| `fit_score` | Integer | N/A | 0-100 percentage |
| `recommendation` | Enum | N/A | One of six tiers |
| `recommendation_rationale` | String | 200 chars | Why this recommendation |
| `strengths` | Array[String] | 80 chars each | 3-4 bullets |
| `gaps` | Array[String] | 80 chars each | 2-3 bullets |

### Six-Tier Recommendation System

| Tier | Score Range | Label | Color |
|------|-------------|-------|-------|
| 1 | 85-100% | Strongly Apply | Green |
| 2 | 70-84% | Apply | Green |
| 3 | 55-69% | Consider | Yellow |
| 4 | 40-54% | Long Shot | Yellow |
| 5 | 25-39% | Do Not Apply | Red |
| 6 | 0-24% | Do Not Apply | Red |

### Override Conditions

These conditions lock the recommendation regardless of score:

| Condition | Locked Recommendation | Locked Reason |
|-----------|----------------------|---------------|
| Eligibility gate failure | Do Not Apply | Hard requirement not met |
| Non-transferable domain mismatch | Do Not Apply | Domain expertise required |
| Missing license/clearance/certification | Do Not Apply | Credential required |
| Experience < 25% of requirement | Do Not Apply | Insufficient experience |

### Example Output

```
78% FIT — APPLY

You match on skills and scope. The gap is industry: they want fintech, you have e-commerce. Bridgeable with positioning.

STRENGTHS
• 8 years product management, 5 at staff+ level
• Led cross-functional teams of 15-20
• Track record shipping 0-to-1 products

GAPS
• No fintech or payments experience
• Their tech stack (Kafka, Flink) not in background
```

### What Does NOT Belong Here

- Actions to take (belongs in Your Move)
- Market competition data (belongs in Reality Check)
- Detailed gap diagnosis (belongs in Gaps to Address)
- Networking advice (belongs in Your Move or Reality Check)

---

## 4. Your Move

### Purpose

Actions only. What to do next. Commands, not suggestions.

### Appears For

All tiers (varies by depth)

### Owner

**Claude only.** No fallback. No coaching controller generation.

### Required Fields

| Field | Type | Character Limit | Description |
|-------|------|-----------------|-------------|
| `positioning` | String | 75 chars | What to lead with |
| `contact_strategy` | String | 75 chars | Who to contact and how |
| `timing` | String | 75 chars | When to apply |
| `competition_level` | Enum | N/A | HIGH / MEDIUM / LOW |

### Total Section Limit

300 characters maximum. If you can't say it in 300 characters, you're explaining, not commanding.

### Format

```
YOUR MOVE

Lead with: Cross-functional product delivery at scale
Contact: Hiring manager first. Skip recruiter.
Timing: Apply within 48 hours. Role posted 3 days ago.
Competition: HIGH
```

### Tier Variations

| Tier | Your Move Content |
|------|-------------------|
| Sourcer | Basic: positioning + timing + competition level |
| Recruiter | Basic + contact strategy |
| Principal+ | Full Your Move + outreach templates |

### Forbidden Patterns

These phrases are BANNED from Your Move:

```
# BANNED - These restate fit (belongs in Score Summary)
"Your background in X gives you an edge"
"Your top-tier experience positions you well"
"Because you have Y, you should..."
"Your skills in Z align with..."

# BANNED - These are weak (use commands instead)
"Consider reaching out to..."
"You might want to..."
"It could help to..."
"Think about..."

# BANNED - These are explanations (just give the action)
"The reason you should contact the HM is..."
"Since the role requires X, you need to..."
```

### Good vs Bad Examples

**Bad (current state - fit restating, verbose):**
```
Lead with your cross-functional experience because that's what they're prioritizing, 
but your top-tier company experience gives you an edge in a competitive market where 
many candidates have similar backgrounds. Consider reaching out to the hiring manager 
since they often appreciate direct contact.
```

**Good (target state - actions only, punchy):**
```
Lead with: Cross-functional delivery, not company names
Contact: HM direct. Recruiter is gatekeeping.
Timing: Apply today. 200+ applicants by Friday.
Competition: HIGH
```

---

## 5. Reality Check

### Purpose

Market truth. What you're up against. Data, not encouragement.

### Appears For

Principal tier and above only (per tier permissions matrix)

### Owner

- **Market data fields**: Backend calculation (deterministic)
- **Strategic context**: Claude (grounded in market data)

### Required Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `applicant_estimate` | Object | Backend | Expected volume + methodology |
| `candidate_position` | String | Backend | Top 10%, 25%, 50%, etc. |
| `response_rate` | Object | Backend | Function-specific cold response rate |
| `layoff_context` | Object | Backend | Function-specific layoff data |
| `referral_required` | Enum | Backend | YES / HELPS / NO |
| `hard_truth` | String | Claude | One brutally honest line |

### Applicant Estimate Calculation

```python
def estimate_applicants(role_type, company_tier, location, days_posted):
    """
    Base estimates by role type (PM example):
    - FAANG/Top Tier: 400-600 applicants
    - Series C-D: 200-400 applicants
    - Series A-B: 100-200 applicants
    - Seed/Early: 50-100 applicants
    
    Multipliers:
    - Major metro (SF, NYC, Seattle): 1.5x
    - Remote: 2.0x
    - Days posted > 7: 1.3x
    - Days posted > 14: 1.5x
    """
```

### Response Rate by Function

| Function | Cold Response Rate | With Referral |
|----------|-------------------|---------------|
| Product Management | 2-4% | 15-25% |
| Engineering | 3-5% | 20-30% |
| Design | 2-4% | 15-25% |
| Sales | 5-8% | 25-35% |
| Marketing | 3-5% | 18-28% |
| Recruiting | 4-6% | 20-30% |
| Operations | 3-5% | 18-28% |

### Layoff Context Data (2024-2025)

| Function | % Roles Cut | Source |
|----------|-------------|--------|
| Product Management | 23% | Layoffs.fyi |
| Engineering | 18% | Layoffs.fyi |
| Recruiting | 45% | Layoffs.fyi |
| HR/People | 35% | Layoffs.fyi |
| Marketing | 28% | Layoffs.fyi |
| Sales | 15% | Layoffs.fyi |

### Referral Threshold Logic

```python
def requires_referral(applicant_estimate, competition_level, company_tier):
    """
    Returns: YES / HELPS / NO
    
    YES if:
    - Applicants > 300 AND company is top-tier
    - Competition is HIGH AND response rate < 3%
    - Role is at FAANG/equivalent
    
    HELPS if:
    - Applicants > 150
    - Competition is MEDIUM-HIGH
    - Company has strong employer brand
    
    NO if:
    - Applicants < 100
    - Competition is LOW-MEDIUM
    - Company is early stage / less known
    """
```

### Format

```
REALITY CHECK

Applicants: 300-400 (Series B, PM role, SF, 5 days posted)
Your position: Top 25% on paper
Cold response: 2-4% for PM roles at this stage
Layoffs: 23% of PM roles cut in 2024. Employers have leverage.
Referral: Required. Without one, you're noise.

Hard truth: This company gets 50+ referral applications. Cold applicants rarely advance past resume screen.
```

### What Does NOT Belong Here

- Actions to take (belongs in Your Move)
- Fit assessment (belongs in Score Summary)
- Encouragement or softening language
- Generic advice

---

## 6. Gaps to Address

### Purpose

Diagnostic detail on specific capability gaps. Feeds from CEC layer.

### Appears For

All tiers (depth varies)

### Owner

CEC Layer primary, Claude gaps[] array as fallback

### Required Fields Per Gap

| Field | Type | Description |
|-------|------|-------------|
| `capability_name` | String | Human-readable gap name |
| `evidence_status` | Enum | explicit / implicit / missing |
| `diagnosis` | String | Why this is a gap |
| `distance` | String | How far candidate is from requirement |
| `coachable` | Boolean | Can this be addressed in current search? |
| `criticality` | Enum | required / preferred |

### Severity Display

| Evidence Status | Criticality | Icon | Color |
|-----------------|-------------|------|-------|
| missing | required | 🔴 | Red |
| missing | preferred | 🟡 | Yellow |
| implicit | required | 🟡 | Yellow |
| implicit | preferred | ⚪ | Gray |
| explicit | any | ✓ | Green |

### Example Output

```
GAPS TO ADDRESS

🔴 Domain Expertise — Fintech (Required)
   No fintech or payments experience. Role requires direct domain knowledge.
   Distance: 0 years fintech → 3+ years required
   Coachable: No (domain expertise requires direct experience)

🟡 Technical Stack — Kafka/Flink (Preferred)
   Resume shows AWS/GCP but not streaming infrastructure.
   Distance: Adjacent tech → specific tools
   Coachable: Yes (can learn, but won't be day-one productive)

✓ Scale Signals — Team Size (Required)
   Strong evidence: "Led team of 15 across 3 workstreams"
```

---

## 7. The Opportunity

### Purpose

Strategic context about why this role might be worth pursuing (or not). Company and role signals.

### Appears For

Principal tier and above

### Owner

Claude (grounded in JD analysis)

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `company_context` | String | What's notable about this company |
| `role_context` | String | What's notable about this role |
| `strategic_signal` | String | Why this matters for candidate's career |

### Example Output

```
THE OPPORTUNITY

Company: Series C fintech, just raised $200M. Expanding product org.
Role: New headcount, not backfill. Reports to CPO.
Signal: This is a build role, not maintain. They want someone to own a new product line.
```

---

## 8. Outreach Templates

### Purpose

Ready-to-send messages for direct outreach.

### Appears For

Principal tier and above

### Owner

Claude (grounded in resume + JD)

### Required Fields

| Field | Type | Character Limit |
|-------|------|-----------------|
| `hiring_manager_message` | String | 500 chars |
| `recruiter_message` | String | 500 chars |
| `linkedin_instructions` | String | 300 chars |

### Rules

- No fabrication. Only reference real experience from resume.
- Confident but not desperate.
- Specific to this role, not generic.
- No "I'm passionate about..." or "I'm excited to..."

### Example Output

```
HIRING MANAGER MESSAGE

Hi [Name],

I saw the Senior PM role on your team. I've spent 8 years building B2B products at Stripe and Asana, most recently leading a team that shipped a $40M ARR feature. 

Your JD mentions needing someone who can work across eng and design to ship fast. That's exactly what I did at Stripe when we launched [specific feature] in 6 months.

Worth a conversation?

[Name]
```

---

## 9. Information Flow Rules

### No Redundancy Rule

Each piece of information lives in exactly one place.

| Information Type | Lives In | Does NOT Appear In |
|-----------------|----------|-------------------|
| Fit percentage | Score Summary | Your Move, Reality Check |
| Strengths/gaps summary | Score Summary | Your Move, Reality Check |
| Detailed gap diagnosis | Gaps to Address | Score Summary |
| What actions to take | Your Move | Score Summary, Reality Check |
| Who to contact | Your Move | Score Summary, Reality Check |
| Market competition | Reality Check | Score Summary, Your Move |
| Applicant volume | Reality Check | Score Summary, Your Move |
| Layoff data | Reality Check | Score Summary, Your Move |
| Referral requirement | Reality Check | Your Move (can reference, not explain) |
| Resume positioning | Your Move | Score Summary |

### Cross-Reference Rule

Components may REFERENCE each other but not DUPLICATE content.

**Allowed:**
```
Your Move: "Contact HM. Referral required per Reality Check."
```

**Not Allowed:**
```
Your Move: "You need a referral because there are 300+ applicants and cold response rate is 2-4%."
```

---

## 10. Tier Permissions

### Component Visibility by Tier

| Component | Sourcer | Recruiter | Principal | Partner | Coach |
|-----------|---------|-----------|-----------|---------|-------|
| Score Summary | ✓ | ✓ | ✓ | ✓ | ✓ |
| Your Move (basic) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Your Move (full) | — | — | ✓ | ✓ | ✓ |
| Reality Check | — | — | ✓ | ✓ | ✓ |
| Gaps to Address (summary) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gaps to Address (CEC detail) | — | — | ✓ | ✓ | ✓ |
| The Opportunity | — | — | ✓ | ✓ | ✓ |
| Outreach Templates | — | — | ✓ | ✓ | ✓ |

### Feature Limits by Tier

| Feature | Sourcer | Recruiter | Principal | Partner | Coach |
|---------|---------|-----------|-----------|---------|-------|
| Applications/month | 3 | 15 | 30 | Strategy | Strategy |
| Tailored resume | — | ✓ | ✓ | ✓ | ✓ |
| Tailored cover letter | — | ✓ | ✓ | ✓ | ✓ |
| ATS optimization | — | ✓ | ✓ | ✓ | ✓ |

---

## 11. Tone and Voice

### Core Identity

> **HenryHQ is a direct, honest, supportive career coach.**

Truth first. Support second. Always actionable.

### Message Structure

Every coaching message follows:

```
TRUTH — Direct statement of reality
WHY — One sentence explaining why it matters
FIX — Specific, doable action
SUPPORT — Brief, earned encouragement
```

### Tone Attributes

| Attribute | HenryHQ IS | HenryHQ IS NOT |
|-----------|------------|----------------|
| Direct | Gets to the point | Wordy, hedging |
| Honest | Tells the truth | Sugar-coating |
| Calm | Confident delivery | Alarmist |
| Human | Natural speech | Robotic AI tone |
| Supportive | Provides path forward | Cold or dismissive |
| Specific | Concrete actions | Vague suggestions |

### Forbidden Patterns

**Language:**
- Corporate jargon: "leverage," "synergize," "circle back"
- Filler words: "just," "maybe," "kind of," "a bit"
- Hedging: "You might want to consider perhaps..."
- Hype: "Amazing!" "Perfect!" "You'll crush it!"
- Shame: "You failed to..." "You should have known..."

**Punctuation:**
- Em dashes (use commas or periods instead)
- Excessive exclamation points
- Ellipses for trailing off...

### Support Lines

**Good (earned, specific):**
- "This is fixable in 15 minutes."
- "You're closer than the score suggests."
- "One referral changes this math."

**Bad (generic, unearned):**
- "You've got this!"
- "You're amazing!"
- "Everything will work out!"

---

## 12. Schema Definitions

### Complete Job Fit Response Schema

```json
{
  "score_summary": {
    "fit_score": 78,
    "recommendation": "Apply",
    "recommendation_rationale": "Strong skills match, bridgeable industry gap",
    "strengths": [
      "8 years PM experience, 5 at staff+ level",
      "Cross-functional team leadership (15-20 people)",
      "Track record shipping 0-to-1 products"
    ],
    "gaps": [
      "No fintech or payments domain experience",
      "Tech stack gap (Kafka, Flink not in background)"
    ]
  },
  
  "your_move": {
    "positioning": "Lead with cross-functional delivery at scale",
    "contact_strategy": "HM direct. Recruiter is gatekeeping.",
    "timing": "Apply within 48 hours. Role posted 3 days ago.",
    "competition_level": "HIGH"
  },
  
  "reality_check": {
    "applicant_estimate": {
      "range": "300-400",
      "methodology": "Series B, PM role, SF, 5 days posted"
    },
    "candidate_position": "Top 25%",
    "response_rate": {
      "cold": "2-4%",
      "with_referral": "15-25%"
    },
    "layoff_context": {
      "function": "Product Management",
      "percent_cut": 23,
      "implication": "Employers have leverage"
    },
    "referral_required": "YES",
    "hard_truth": "This company gets 50+ referral applications. Cold applicants rarely advance."
  },
  
  "gaps_to_address": [
    {
      "capability_name": "Domain Expertise — Fintech",
      "evidence_status": "missing",
      "diagnosis": "No fintech or payments experience in resume",
      "distance": "0 years → 3+ years required",
      "coachable": false,
      "criticality": "required"
    },
    {
      "capability_name": "Technical Stack — Kafka/Flink",
      "evidence_status": "implicit",
      "diagnosis": "AWS/GCP experience but not streaming infrastructure",
      "distance": "Adjacent tech → specific tools",
      "coachable": true,
      "criticality": "preferred"
    }
  ],
  
  "the_opportunity": {
    "company_context": "Series C fintech, raised $200M, expanding product org",
    "role_context": "New headcount, not backfill. Reports to CPO.",
    "strategic_signal": "Build role, not maintain. Ownership of new product line."
  },
  
  "outreach": {
    "hiring_manager_message": "Hi [Name], I saw the Senior PM role...",
    "recruiter_message": "Hi [Name], I applied for the Senior PM role...",
    "linkedin_instructions": "Search: [Company] + 'Head of Product' or 'VP Product'. Filter by 2nd connections."
  }
}
```

### Field Validation Rules

| Field | Required | Type | Validation |
|-------|----------|------|------------|
| fit_score | Yes | Integer | 0-100 |
| recommendation | Yes | Enum | One of 6 tiers |
| recommendation_rationale | Yes | String | 50-200 chars |
| strengths | Yes | Array | 3-4 items, each 20-80 chars |
| gaps | Yes | Array | 2-3 items, each 20-80 chars |
| your_move.positioning | Yes | String | 20-75 chars |
| your_move.contact_strategy | Yes | String | 20-75 chars |
| your_move.timing | Yes | String | 20-75 chars |
| your_move.competition_level | Yes | Enum | HIGH/MEDIUM/LOW |
| reality_check.* | Principal+ | Various | See schema |
| gaps_to_address | Yes | Array | 1-5 items |
| the_opportunity | Principal+ | Object | All fields required if present |
| outreach | Principal+ | Object | All fields required if present |

---

## 13. Validation Rules

### Pre-Output Validation

Before returning job fit analysis, validate:

```python
def validate_job_fit_response(response, tier):
    errors = []
    
    # 1. Score Summary completeness
    if not response.get("score_summary"):
        errors.append("Missing score_summary")
    if not response["score_summary"].get("fit_score"):
        errors.append("Missing fit_score")
    if len(response["score_summary"].get("strengths", [])) < 3:
        errors.append("Insufficient strengths (need 3+)")
    if len(response["score_summary"].get("gaps", [])) < 2:
        errors.append("Insufficient gaps (need 2+)")
    
    # 2. Your Move completeness (no fallback allowed)
    if not response.get("your_move"):
        errors.append("Missing your_move - REQUIRED, no fallback")
    if not response["your_move"].get("positioning"):
        errors.append("Missing your_move.positioning")
    if not response["your_move"].get("contact_strategy"):
        errors.append("Missing your_move.contact_strategy")
    
    # 3. Your Move does not restate fit
    your_move_text = " ".join(response["your_move"].values())
    fit_restate_patterns = [
        "your background",
        "your experience gives you",
        "your skills align",
        "you have an edge",
        "positions you well"
    ]
    for pattern in fit_restate_patterns:
        if pattern.lower() in your_move_text.lower():
            errors.append(f"Your Move restates fit: '{pattern}'")
    
    # 4. Character limits
    if len(response["your_move"].get("positioning", "")) > 75:
        errors.append("your_move.positioning exceeds 75 chars")
    if len(response["score_summary"].get("recommendation_rationale", "")) > 200:
        errors.append("recommendation_rationale exceeds 200 chars")
    
    # 5. Tier-appropriate content
    if tier in ["Sourcer", "Recruiter"]:
        if response.get("reality_check"):
            errors.append("Reality Check shown to non-Principal tier")
        if response.get("outreach"):
            errors.append("Outreach shown to non-Principal tier")
    
    # 6. No undefined/null/placeholder values
    def check_for_placeholders(obj, path=""):
        if obj is None:
            errors.append(f"Null value at {path}")
        elif isinstance(obj, str):
            if obj.strip() == "" or obj == "undefined" or "[" in obj and "]" in obj:
                errors.append(f"Placeholder/empty value at {path}: '{obj}'")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                check_for_placeholders(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                check_for_placeholders(v, f"{path}[{i}]")
    
    check_for_placeholders(response)
    
    return errors
```

### Validation Failure Handling

If validation fails:
1. Log the specific errors
2. Do NOT return partial/broken response to frontend
3. Return a structured error that frontend can handle gracefully
4. Never silently substitute with fallback content

---

## 14. Implementation Checklist

### Phase 1: Schema Alignment (Immediate)

- [ ] Split `strategic_action` into `your_move` and `reality_check_strategic_context`
- [ ] Remove coaching controller fallback for Your Move
- [ ] Update Claude prompt to require Your Move output
- [ ] Add validation for Your Move completeness
- [ ] Add validation for fit-restate patterns

### Phase 2: Reality Check Enhancement (Week 1)

- [ ] Implement `estimate_applicants()` function
- [ ] Add function-specific response rate lookup
- [ ] Add layoff context data by function
- [ ] Implement `requires_referral()` threshold logic
- [ ] Surface layoff data prominently in Reality Check

### Phase 3: CEC Integration (Week 2)

- [ ] Ensure CEC output feeds Gaps to Address
- [ ] Remove Claude gaps[] fallback when CEC data exists
- [ ] Add evidence_status to gap display
- [ ] Add coachable indicator to gap display

### Phase 4: Tier Gating (Week 2)

- [ ] Implement tier check for Reality Check visibility
- [ ] Implement tier check for Outreach visibility
- [ ] Implement tier check for CEC detail visibility
- [ ] Add tier parameter to validation function

### Phase 5: Testing (Week 3)

- [ ] Unit test: Your Move does not contain fit-restate patterns
- [ ] Unit test: Reality Check contains all required fields
- [ ] Unit test: Validation catches missing/placeholder values
- [ ] Integration test: Full response passes validation
- [ ] User test: Output matches spec examples

---

## 15. Failure States

### What Users See When Things Break

Every failure mode has a defined user-facing outcome. No silent failures. No blank screens.

#### Claude Output Failures

| Failure | Detection | User Sees | System Action |
|---------|-----------|-----------|---------------|
| Your Move missing | Validation check | "Analysis incomplete. Refresh to retry." | Log error, do not show partial results |
| Your Move too short (<50 chars total) | Validation check | "Analysis incomplete. Refresh to retry." | Log error, do not show partial results |
| Your Move restates fit | Pattern match | "Analysis incomplete. Refresh to retry." | Log violation, reject response, retry once |
| Score Summary missing | Validation check | "Analysis failed. Please try again." | Log error, return 500 |
| Strengths < 3 items | Validation check | Show what exists + "Limited analysis available" | Log warning, show partial |
| Gaps < 2 items | Validation check | Show what exists + "Limited analysis available" | Log warning, show partial |

#### Data Availability Failures

| Failure | Detection | User Sees | System Action |
|---------|-----------|-----------|---------------|
| Reality Check data unavailable | Backend check | Reality Check section hidden (not error) | Log warning, degrade gracefully |
| Layoff data stale (>90 days) | Timestamp check | Show data with "Last updated: [date]" | Log for refresh, show stale |
| Applicant estimate fails | Calculation error | "Market data unavailable" in Reality Check | Log error, show rest of Reality Check |
| CEC layer fails | Exception catch | Fall back to Claude gaps[] array | Log error, use fallback |

#### Tier Permission Failures

| Failure | Detection | User Sees | System Action |
|---------|-----------|-----------|---------------|
| Tier unknown/missing | Session check | Treat as Sourcer (most restrictive) | Log warning, default to lowest tier |
| Tier mismatch (content vs access) | Validation | Hide premium content, show upgrade prompt | Log mismatch, filter response |
| Tier upgrade mid-session | Session check | Refresh required to see new content | Log event, prompt refresh |

### Failure Response Template

When showing user-facing errors:

```
[Icon: Warning or Error]
[Headline: What happened - 5 words max]
[Explanation: Why - 1 sentence]
[Action: What to do - 1 sentence]
```

**Example:**
```
⚠️ Analysis Incomplete
We couldn't generate complete guidance for this role.
Refresh the page to try again, or contact support if this persists.
```

### Retry Policy

| Failure Type | Auto-Retry | Max Retries | Backoff |
|--------------|------------|-------------|---------|
| Claude output validation | Yes | 1 | None |
| Claude API timeout | Yes | 2 | Exponential (1s, 3s) |
| Backend calculation | No | 0 | N/A |
| Data fetch | Yes | 2 | Linear (2s, 4s) |

---

## 16. Auditing and Drift Control

### What Gets Logged Per Run

Every job fit analysis logs a structured audit record:

```json
{
  "audit_id": "uuid",
  "timestamp": "ISO8601",
  "version": "4.0.0",
  "user_tier": "Principal",
  
  "inputs": {
    "resume_hash": "sha256_first8",
    "jd_hash": "sha256_first8",
    "jd_url": "if_provided"
  },
  
  "scoring": {
    "raw_score": 82,
    "final_score": 78,
    "penalties_applied": ["experience_gap", "domain_mismatch"],
    "hard_caps_triggered": false,
    "recommendation_locked": true,
    "locked_reason": "score_based"
  },
  
  "validation": {
    "passed": true,
    "errors": [],
    "warnings": ["strengths_count_low"],
    "fit_restate_detected": false
  },
  
  "output": {
    "your_move_length": 287,
    "reality_check_present": true,
    "gaps_count": 3,
    "cec_used": true
  },
  
  "performance": {
    "total_latency_ms": 2340,
    "claude_latency_ms": 1890,
    "backend_latency_ms": 450
  }
}
```

### Drift Detection Signals

Monitor these metrics weekly. Alert if thresholds exceeded.

| Metric | Healthy Range | Alert Threshold | Indicates |
|--------|---------------|-----------------|-----------|
| Avg fit score | 45-65% | <40% or >70% | Scoring drift |
| "Do Not Apply" rate | 15-30% | <10% or >40% | Gate miscalibration |
| Your Move validation fail rate | <5% | >10% | Prompt drift |
| Fit-restate detection rate | <2% | >5% | Prompt regression |
| Reality Check missing rate | <3% | >8% | Data pipeline issue |
| Avg Your Move length | 200-280 chars | >350 chars | Bloat creep |
| Avg total latency | 2-4s | >6s | Performance degradation |

### Weekly Audit Report

Generate automatically every Monday:

```
JOB FIT SCORING - WEEKLY AUDIT
Period: [Date] to [Date]
Analyses run: [N]

SCORING DISTRIBUTION
- Strongly Apply: X%
- Apply: X%
- Consider: X%
- Long Shot: X%
- Do Not Apply: X%

VALIDATION HEALTH
- Pass rate: X%
- Most common error: [error]
- Fit-restate violations: [N]

DRIFT ALERTS
- [Any metrics outside healthy range]

ACTION REQUIRED
- [Specific fixes if any]
```

### Regression Testing

Before any prompt or logic change:

1. Run against 50-sample test set (stored resume+JD pairs)
2. Compare outputs to baseline
3. Flag if >10% of recommendations change
4. Flag if avg score shifts >5 points
5. Require manual review before deploy

---

## 17. Versioning and Backward Compatibility

### Version Numbering

Format: `MAJOR.MINOR.PATCH`

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking schema change | MAJOR | 4.0.0 to 5.0.0 |
| New field added (backward compatible) | MINOR | 4.0.0 to 4.1.0 |
| Bug fix, threshold tweak | PATCH | 4.0.0 to 4.0.1 |

### Version Pinning

Every stored analysis includes `spec_version`:

```json
{
  "analysis_id": "uuid",
  "spec_version": "4.0.0",
  "created_at": "ISO8601",
  "results": { ... }
}
```

### Historic Results Policy

**Stored analyses are immutable.** When a user views a past analysis:

1. Display results as originally calculated
2. Show version indicator if spec has changed: "Analyzed with v4.0 scoring"
3. Offer "Re-analyze with current scoring" button
4. Never silently update historic results

### Migration Policy

When MAJOR version changes:

1. New analyses use new version immediately
2. Historic analyses unchanged
3. User can opt-in to re-analyze
4. After 90 days, prompt users with old analyses to refresh
5. Never auto-migrate without user action

### Deprecation Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Announcement | 2 weeks | Notify users of upcoming changes |
| Soft deprecation | 4 weeks | Show "new version available" on old analyses |
| Hard deprecation | 8 weeks | Block new analyses on old version |
| Sunsetting | 12 weeks | Archive old version code |

---

## 18. Human Override Policy

### Scope

This policy governs internal overrides only. Users cannot override system decisions.

### Override Levels

| Level | Who Can Use | Use Cases | Logging |
|-------|-------------|-----------|---------|
| Debug | Engineers | Local testing, bug reproduction | Local only |
| Demo | Product, Sales | Controlled demos, screenshots | Logged, tagged "demo" |
| Support | Support team | User escalations, edge case investigation | Logged, requires ticket ID |
| Executive | Henry only | Strategic exceptions | Logged, requires written rationale |

### Override Mechanics

Overrides are applied via internal API flag, never by modifying production logic:

```python
# Internal override request
{
  "override_type": "support",
  "ticket_id": "SUP-1234",
  "override_fields": {
    "recommendation": "Apply",  # Force specific recommendation
    "skip_validation": false,   # Still validate, just override result
    "reason": "User has context not in resume (verbal confirmation of experience)"
  }
}
```

### Override Constraints

Even with override:

1. Fit score cannot be manually set (always calculated)
2. Hard caps cannot be bypassed (eligibility is eligibility)
3. Validation still runs (errors logged even if overridden)
4. All overrides expire after 24 hours
5. No override can be applied to another user's analysis

### Override Audit Trail

Every override logged permanently:

```json
{
  "override_id": "uuid",
  "analysis_id": "uuid",
  "override_level": "support",
  "overridden_by": "user_id",
  "ticket_id": "SUP-1234",
  "original_value": "Do Not Apply",
  "override_value": "Apply",
  "reason": "...",
  "timestamp": "ISO8601",
  "expires_at": "ISO8601"
}
```

### Prohibited Overrides

These overrides are never permitted, regardless of level:

- Changing another user's tier/permissions
- Bypassing eligibility gates for hard requirements
- Modifying historic analyses retroactively
- Bulk overrides (>5 per day requires VP approval)
- Overrides without documented reason

---

## 19. Performance Constraints

### Latency SLAs

| Operation | Target | Max Acceptable | Action if Exceeded |
|-----------|--------|----------------|-------------------|
| Full job fit analysis | 3s | 6s | Show loading state, log slow query |
| Score calculation only | 500ms | 1s | Optimize backend |
| Reality Check data fetch | 200ms | 500ms | Cache or degrade |
| Validation | 50ms | 100ms | Optimize regex |
| Frontend render | 100ms | 300ms | Optimize JS |

### Throughput Limits

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Analyses per user per hour | 20 | Rate limit, show "slow down" message |
| Analyses per user per day | 100 | Hard block, show upgrade prompt |
| Concurrent analyses per user | 3 | Queue additional requests |
| Claude API calls per analysis | 2 | Fail if exceeded (indicates retry loop) |

### Payload Size Limits

| Field | Max Size | Enforcement |
|-------|----------|-------------|
| Resume text | 50KB | Truncate with warning |
| JD text | 30KB | Truncate with warning |
| Total response | 100KB | Compress or split |
| Your Move total | 300 chars | Hard reject if exceeded |
| Single strength/gap | 80 chars | Truncate |

### Caching Policy

| Data | Cache Duration | Invalidation |
|------|----------------|--------------|
| Layoff data | 24 hours | Manual refresh |
| Response rates | 7 days | Manual refresh |
| Company credibility tiers | 30 days | Manual refresh |
| User's recent analyses | 1 hour | On new analysis |
| JD parse results | 24 hours | On JD change |

### Degradation Strategy

When system is under load, degrade in this order:

1. **First:** Disable The Opportunity section (lowest value)
2. **Second:** Simplify Reality Check to cached defaults
3. **Third:** Reduce CEC to top 3 gaps only
4. **Fourth:** Queue new requests (never drop)
5. **Never:** Skip Score Summary or Your Move

### Monitoring Alerts

| Metric | Warning | Critical |
|--------|---------|----------|
| P95 latency | >4s | >8s |
| Error rate | >2% | >5% |
| Claude timeout rate | >1% | >3% |
| Queue depth | >50 | >200 |
| Cache hit rate | <80% | <60% |

---

## Appendix A: Migration from Previous Specs

### Deprecated Fields

| Old Field | New Field(s) | Notes |
|-----------|--------------|-------|
| `strategic_action` | `your_move` + `reality_check.hard_truth` | Split by purpose |
| `your_move_summary` | `your_move` | Structured object, not string |
| `coaching_controller.generate_your_move()` | REMOVED | Claude owns Your Move |

### Deprecated Functions

| Function | Replacement | Notes |
|----------|-------------|-------|
| `coaching_controller.generate_your_move()` | Claude prompt | Remove fallback entirely |
| `coaching_controller.generate_gaps()` | CEC layer | CEC is source of truth |

### Deprecated Patterns

| Pattern | Replacement |
|---------|-------------|
| Fallback to coaching controller | Validation error |
| Fit restating in Your Move | Actions only |
| Overloaded `strategic_action` | Split fields |

---

## Appendix B: Prompt Updates Required

### Your Move Prompt Section

Add to Claude system prompt:

```
YOUR MOVE REQUIREMENTS:

You MUST output a your_move object with these exact fields:
- positioning: What to lead with (max 75 chars)
- contact_strategy: Who to contact and how (max 75 chars)  
- timing: When to apply (max 75 chars)
- competition_level: HIGH, MEDIUM, or LOW

RULES:
1. Actions only. No fit assessment.
2. Commands, not suggestions. Use "Contact HM" not "Consider contacting HM"
3. No phrases like "your background gives you" or "your experience positions you"
4. Total section must be under 300 characters
5. Every field is required. No empty strings.

GOOD EXAMPLE:
{
  "positioning": "Lead with cross-functional delivery at scale",
  "contact_strategy": "HM direct. Recruiter is gatekeeping.",
  "timing": "Apply within 48 hours. Role posted 3 days ago.",
  "competition_level": "HIGH"
}

BAD EXAMPLE (fit restating - FORBIDDEN):
{
  "positioning": "Your strong PM background positions you well for this role",
  "contact_strategy": "Consider reaching out to the hiring manager since your experience aligns",
  "timing": "Apply soon given your competitive profile",
  "competition_level": "MEDIUM"
}
```

---

## Appendix C: Frontend Display Rules

### Component Hierarchy

```
1. Score Summary Card (always visible, always first)
2. Your Move (always visible, below score)
3. Reality Check (Principal+ only, below Your Move)
4. Gaps to Address (always visible, collapsible detail)
5. The Opportunity (Principal+ only)
6. Outreach Templates (Principal+ only, bottom of page)
```

### Color Coding

| Element | Condition | Color |
|---------|-----------|-------|
| Score badge | 70%+ | Green |
| Score badge | 40-69% | Yellow |
| Score badge | <40% | Red |
| Strength bullet | Always | Green |
| Gap bullet | Required + missing | Red |
| Gap bullet | Preferred + missing | Yellow |
| Gap bullet | Implicit | Yellow |
| Competition level HIGH | Always | Red text |
| Competition level MEDIUM | Always | Yellow text |
| Competition level LOW | Always | Green text |

### Character Truncation

If content exceeds limits, truncate with "..." and show full content on hover/click. Never break mid-word.

---

## Appendix D: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 4.0 | Dec 30, 2025 | Henry + Claude | Consolidated spec, resolved ownership conflicts, added validation |
| 3.0 | Dec 21, 2025 | Henry + Claude | Six-tier system, invariant enforcement |
| 2.0 | Dec 18, 2025 | Henry + Claude | Strategic action framework |
| 1.0 | Dec 18, 2025 | Henry + Claude | Initial draft |

---

**END OF SPECIFICATION**

This document is the single source of truth. All previous specs are superseded.
