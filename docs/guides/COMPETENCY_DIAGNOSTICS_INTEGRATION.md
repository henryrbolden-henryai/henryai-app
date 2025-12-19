# Competency-Based Diagnostics Integration Plan

**Version**: 1.0  
**Date**: December 18, 2025  
**Status**: DESIGN - Phase 4 Feature  
**Purpose**: Integrate industry-standard competency frameworks with honest senior-level diagnostics

---

## Executive Summary

### Strategic Context

The current fit scoring system (50/30/20 - Skills/Experience/Scope) provides a numerical assessment but lacks **competency-level granularity** needed to:

1. Detect title inflation vs. demonstrated scope
2. Map resume evidence to specific competency levels (PM II vs Senior PM vs Staff PM)
3. Identify career switchers presenting adjacent exposure as direct ownership
4. Provide honest, coaching-focused guidance for misaligned candidates

### What This Adds

**Beyond basic fit scoring**:
- Competency-level readiness mapping (PM II, Senior PM, Staff PM, Principal PM)
- Title inflation detection (title vs. demonstrated scope mismatch)
- Company credibility at scale (unverifiable vs. verified companies)
- Career switcher recognition (advocacy work ≠ product ownership)
- Market reality coaching (honest guidance without shaming)

**Core Principle**: Truth + Direction, not encouragement theater.

---

## Competency Framework Reference

### Source Materials (Internal Use Only)

Industry-standard competency frameworks covering:

| Framework | Coverage | Key Content |
|-----------|----------|-------------|
| Product Management Leveling | PM I through Principal PM | Strategy, execution, scale, leadership competencies |
| Engineering Leveling | Engineer through Staff/Principal | Technical depth, architecture, execution at scale |
| Tech Lead Manager | TLM competencies | Technical leadership + people management |
| Technical Program Manager | TPM/PgM levels | Cross-functional execution, program management |
| Management Assessment | People leadership | Team building, performance management, org influence |

**Note**: These frameworks serve as internal reference for competency detection logic. They are NOT exposed to users or mentioned in any output.

### Competency Dimensions (Product Management Example)

Based on industry-standard PM frameworks:

1. **Product Strategy** - Vision, market positioning, competitive analysis
2. **Customer Insight** - User research, empathy, problem identification
3. **Roadmap Ownership** - Prioritization, tradeoffs, multi-quarter planning
4. **Metrics & Outcomes** - KPI definition, measurement, impact tracking
5. **Cross-functional Leadership** - Influence, alignment, stakeholder management
6. **Scale Complexity** - Team size, user base, revenue/budget, organizational scope
7. **Execution** - Delivery, launch management, operational excellence
8. **Technical Judgment** - Architecture understanding, tech tradeoff evaluation

### Level Definitions (Product Management Example)

Industry-standard PM levels:

| Level | Years | Scope | Key Distinction |
|-------|-------|-------|-----------------|
| PM I / Associate PM | 0-2 | Feature ownership | Executes on roadmap, learns process |
| PM II / Product Manager | 2-4 | Product area ownership | Defines roadmap for area, some strategy |
| Senior PM | 4-8 | Product/platform ownership | Sets strategy, influences org, proven scale |
| Staff PM | 8-12 | Multi-product/platform | Org-level impact, architectural decisions |
| Principal PM | 12+ | Company-level initiatives | Strategic direction, exec partnership |

---

## Detection Layers (Additive to Fit Scoring)

### 1. Title Inflation Detection

**Purpose**: Flag when resume title exceeds demonstrated scope

**Signals to Check**:

```python
def detect_title_inflation(resume_data: Dict, jd_analysis: Dict) -> Dict:
    """
    Detect title inflation by comparing claimed title to demonstrated scope.
    
    Red Flags:
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
    
    Returns:
        {
            "title_alignment": "accurate" | "inflated" | "unclear",
            "title_risk_reason": str,
            "demonstrated_level": str,
            "claimed_level": str,
            "scope_evidence": {
                "team_size": bool,
                "budget_ownership": bool,
                "roadmap_ownership": bool,
                "direct_reports": bool
            }
        }
    """
    pass
```

**Example Coaching Output**:

```
Title Alignment: INFLATED

Your current title is "Head of Product" but your resume shows:
- No team size or direct reports
- No budget/P&L ownership  
- No multi-product roadmap
- Company cannot be verified at scale

Hiring managers will discount the title and evaluate you as a Senior IC 
(PM II level) based on demonstrated scope. This role requires Staff PM 
competencies. You are not competitive as currently positioned.
```

---

### 2. Competency-Level Mapping

**Purpose**: Map resume evidence to competency framework levels

**PM Competency Detection**:

```python
def map_pm_competencies(resume_data: Dict, jd_analysis: Dict) -> Dict:
    """
    Map resume evidence against industry-standard PM competency framework.
    
    Competency Dimensions:
    1. Product Strategy (PM I: executes | Senior: owns | Staff: defines org)
    2. Customer Insight (PM I: contributes | Senior: leads | Staff: influences)
    3. Roadmap Ownership (PM I: feature | Senior: product | Staff: platform)
    4. Metrics & Outcomes (PM I: tracks | Senior: defines | Staff: business-level)
    5. Cross-functional Leadership (PM I: coordinates | Senior: influences | Staff: org-wide)
    6. Scale Complexity (PM I: small | Senior: significant | Staff: massive)
    7. Execution (PM I: ships features | Senior: ships products | Staff: ships platforms)
    8. Technical Judgment (PM I: understands | Senior: evaluates | Staff: architects)
    
    Evidence Signals:
    - Team size influenced
    - Budget managed
    - User scale
    - Revenue impact
    - Product launches
    - Strategic initiatives
    - Org-level changes
    
    Returns:
        {
            "required_level": "Senior PM",
            "demonstrated_level": "PM II",
            "competency_scores": {
                "product_strategy": {"level": "PM II", "evidence": [...]},
                "customer_insight": {"level": "Senior PM", "evidence": [...]},
                ...
            },
            "gaps": [
                "Product Strategy: Role requires org-level strategy. Resume shows product-level only.",
                "Scale Complexity: Role manages 50M+ users. Resume shows 2M max scale.",
                "Cross-functional Leadership: No evidence of exec-level stakeholder management."
            ]
        }
    """
    pass
```

**Example Output**:

```
Competency Alignment: MISALIGNED

Role Requirements: Senior PM (4-8 years, product-level ownership)
Demonstrated Level: PM II (2-4 years, feature-level ownership)

Competency Gaps:
1. Product Strategy: Role requires product-level strategy. Your resume shows 
   feature-level execution with limited strategic ownership.

2. Scale Complexity: Role manages 20M+ users and $50M+ revenue. Your resume 
   shows max 500K users and no revenue accountability.

3. Cross-functional Leadership: Role requires VP-level stakeholder management. 
   Your resume shows peer-level coordination.

4. Metrics & Outcomes: Role defines business KPIs. Your resume tracks feature 
   metrics with limited business impact evidence.
```

---

### 3. Company Credibility & Scale Check

**Purpose**: Go beyond "is it a startup" to assess verifiable scale

**Enhanced Credibility Detection**:

```python
def assess_company_credibility(company_name: str, experience: Dict) -> Dict:
    """
    Assess company credibility and scale beyond basic tier detection.
    
    Verification Levels:
    1. STRONG: Public data available
       - Press coverage
       - Product/app reviews
       - Funding announcements
       - Employee count verifiable
       - Active product
    
    2. WEAK: Limited but present
       - Company website exists
       - LinkedIn presence
       - Some employee profiles
       - Product exists but unclear scale
    
    3. UNVERIFIABLE: Cannot validate
       - No online presence
       - No product found
       - Personal branding entities
       - "Consulting" with no clients
       - "Founder" with no company
    
    Returns:
        {
            "credibility": "strong" | "weak" | "unverifiable",
            "verification_signals": {
                "press_coverage": bool,
                "product_active": bool,
                "funding_verified": bool,
                "employees_verifiable": bool
            },
            "market_discount": float,  # 0.0 to 1.0
            "scale_indicators": {
                "user_base": str | None,
                "revenue": str | None,
                "funding": str | None,
                "employees": int | None
            }
        }
    """
    pass
```

**Example Coaching**:

```
Company Credibility: UNVERIFIABLE

Your listed company "Acme Innovations" cannot be validated:
- No product or website found
- No press coverage or funding data
- No employee profiles on LinkedIn
- Presented as "Head of Product" at 2-person entity

Market Reality: Hiring managers will evaluate this as independent consulting 
or side project work, not senior product leadership at scale. Your experience 
will be discounted to IC level for competitive roles.

YOUR MOVE: Lead with verifiable scale companies in your positioning.
```

---

### 4. Career Switcher Recognition

**Purpose**: Detect adjacent exposure vs. direct ownership

**Switcher Patterns**:

```python
def detect_career_switcher(resume_data: Dict, jd_analysis: Dict) -> Dict:
    """
    Identify career switchers presenting adjacent work as direct experience.
    
    Red Flag Patterns:
    1. "Product Manager" with:
       - Program/project management background
       - Operations/advocacy work
       - Tool usage without decision ownership
    
    2. "Engineering Manager" with:
       - Tech support/operations background
       - Solutions engineering
       - No architecture/design ownership
    
    3. "Senior X" with:
       - Participation in X, not ownership of X
       - Supporting role presented as lead role
       - Exposure without accountability
    
    Evidence Types:
    - DIRECT: "Owned roadmap", "Defined strategy", "Shipped product"
    - ADJACENT: "Supported PM team", "Contributed to strategy", "Involved in launch"
    - EXPOSURE: "Participated in", "Familiar with", "Exposure to"
    
    Returns:
        {
            "is_switcher": bool,
            "switcher_type": "functional" | "seniority" | "none",
            "prior_function": str,
            "target_function": str,
            "ownership_level": "direct" | "adjacent" | "exposure",
            "coaching": str
        }
    """
    pass
```

**Example Coaching**:

```
Career Switcher Pattern: DETECTED

Your background is Program Management, not Product Management. Key differences:

Program Management (your experience):
- Coordinated cross-functional teams
- Managed timelines and deliverables
- Facilitated launches

Product Management (this role requires):
- Owned product strategy and roadmap
- Defined metrics and success criteria
- Made build/buy/partner decisions
- Managed product P&L

Your resume shows ADJACENT exposure, not DIRECT ownership. Senior PM roles 
require demonstrated product decision-making, not project coordination.

YOUR MOVE: Target "Associate PM" or "PM I" roles where you can build direct 
product ownership. Do not apply to Senior PM roles yet.
```

---

### 5. Market Reality Filter

**Purpose**: Acknowledge bias without validating avoidance

**Sensitive Topics Handling**:

```python
def apply_market_reality_filter(resume_data: Dict, gaps: List[str]) -> str:
    """
    Acknowledge market behavior without moral judgment.
    
    Topics to Handle:
    1. DEI/Advocacy work vs. delivery work
    2. Career gaps (parenting, caregiving)
    3. Non-traditional backgrounds
    4. International experience at US companies
    
    Rules:
    - NEVER label DEI work as "toxic"
    - DO acknowledge current market behavior
    - Frame as positioning strategy, not work value
    
    Example Output:
    "Some companies currently discount resumes heavily weighted toward 
    advocacy over delivery. To compete for senior product roles, your 
    positioning must lead with product outcomes first. DEI work can be 
    included but should not dominate the narrative for IC/senior roles."
    
    Returns:
        str: Coaching on market positioning
    """
    pass
```

---

## Scoring Impact Rules

### Hard Overrides

Regardless of raw fit score from Skills/Experience/Scope:

| Condition | Hard Cap | Recommendation |
|-----------|----------|----------------|
| Inflated title + missing competencies | 55% | "Consider" or "Apply with Caution" |
| Unverifiable company + senior role claim | 45% | "Apply with Caution" or "Long Shot" |
| Senior role requirement + PM II competencies | 40% | "Long Shot" or "Do Not Apply" |
| Career switcher + no direct ownership | 40% | "Long Shot" or "Do Not Apply" |

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
    1. Career switcher + no ownership → cap at 40%
    2. Title inflation + competency gap → cap at 55%
    3. Unverifiable company + senior claim → cap at 45%
    4. PM II demonstrated + Senior PM required → cap at 40%
    
    Returns:
        {
            "capped_score": int,
            "override_applied": bool,
            "override_reason": str,
            "recommendation": str
        }
    """
    capped_score = base_fit_score
    override_reason = None
    
    # Career switcher with no direct ownership
    if career_switcher["is_switcher"] and \
       career_switcher["ownership_level"] in ["adjacent", "exposure"]:
        capped_score = min(capped_score, 40)
        override_reason = "Career switcher with adjacent exposure, not direct ownership"
    
    # Title inflation with competency gap
    elif title_inflation["title_alignment"] == "inflated" and \
         competency_alignment["demonstrated_level"] < competency_alignment["required_level"]:
        capped_score = min(capped_score, 55)
        override_reason = "Title exceeds demonstrated competency level"
    
    # Unverifiable company with senior claim
    elif company_credibility["credibility"] == "unverifiable" and \
         "senior" in competency_alignment["required_level"].lower():
        capped_score = min(capped_score, 45)
        override_reason = "Cannot verify scale claimed in senior role"
    
    # Competency level mismatch
    elif competency_alignment["gaps_count"] >= 3:
        capped_score = min(capped_score, 40)
        override_reason = "Significant competency gaps for required level"
    
    return {
        "capped_score": capped_score,
        "override_applied": capped_score < base_fit_score,
        "override_reason": override_reason,
        "recommendation": get_recommendation_from_score(capped_score)
    }
```

---

## Canonical Messaging Patterns

**Purpose**: Single, repeatable voice for sensitive feedback. Use these exact phrasings to maintain consistency and calm tone.

### Pattern 1: Title Inflation

**Use when**: Resume title exceeds demonstrated scope

**Canonical phrasing**:
```
"Hiring managers will evaluate this experience at a different scope than 
the title suggests. That gap affects senior-level competitiveness."
```

**When to add context**:
- If unverifiable company: Add "because the company cannot be validated at scale"
- If missing scope signals: Add "because your resume doesn't show [team size/budget/roadmap]"

**Never say**: "Your title is inflated", "This looks suspicious", "Companies won't believe this"

---

### Pattern 2: Unverifiable Company

**Use when**: Cannot validate company at claimed scale

**Canonical phrasing**:
```
"This company cannot be validated at the scale your role implies. Hiring 
managers will evaluate your experience as individual contribution rather 
than senior leadership. Lead with verifiable scale companies in your 
positioning."
```

**Never say**: "This company doesn't exist", "This looks like a fake company", "This is a red flag"

---

### Pattern 3: Career Switcher (Adjacent vs Direct)

**Use when**: Resume shows adjacent exposure, not direct ownership

**Canonical phrasing**:
```
"Your background shows adjacent exposure to [function], not direct ownership. 
Senior roles require demonstrated decision-making in [specific area]."
```

**Never say**: "You're not a real [role]", "This isn't legitimate experience"

---

### Pattern 4: Competency Gap

**Use when**: Demonstrated level < Required level

**Canonical phrasing**:
```
"This role requires [required level] competencies. Your background shows 
[demonstrated level] evidence. The gap is in [specific dimensions]."
```

**Never say**: "You're not senior enough", "You're underqualified", "You don't have the skills"

---

## Strategic Action Output Template

### When Senior-Level Misalignment Detected

**Template**:

```
COMPETENCY ASSESSMENT: {demonstrated_level} → {required_level}

This role expects {required_level} competencies across {dimensions}.
Your background shows {demonstrated_level} evidence but not sustained 
ownership at {required_level}.

KEY GAPS:
1. {gap_1_dimension}: {specific_gap_description}
2. {gap_2_dimension}: {specific_gap_description}
3. {gap_3_dimension}: {specific_gap_description}

MARKET REALITY:
{title_inflation_coaching if applicable}
{company_credibility_coaching if applicable}
{career_switcher_coaching if applicable}

YOUR MOVE THIS WEEK:
1. Target these roles: {3 specific role titles at appropriate level}
2. Add this evidence: {1-2 specific improvements to resume/LinkedIn}
3. Deprioritize: {what to stop applying to immediately}

CLOSE THE GAP:
- Next 3 months: {specific competency to build + how}
- Next 6-12 months: {level advancement path}
- Ready when: {concrete readiness signal}
```

**Example (Senior PM Mismatch)**:

```
COMPETENCY ASSESSMENT: PM II → Senior PM

This role expects Senior PM competencies across product strategy, scale 
complexity, and cross-functional leadership. Your background shows PM II 
evidence (feature-level ownership, 500K users) but not sustained ownership 
at Senior PM level (product-level strategy, 10M+ users, VP stakeholder 
management).

KEY GAPS:
1. Product Strategy: Role requires product-level vision. Your resume shows 
   feature-level execution with limited strategic influence.

2. Scale Complexity: Role manages $50M+ revenue and 20M+ users. Your resume 
   shows 500K users max and no revenue accountability.

3. Cross-functional Leadership: Role requires VP-level influence. Your resume 
   shows peer-level coordination, not executive stakeholder management.

MARKET REALITY:
Hiring managers will evaluate this experience at a different scope than the 
title suggests. That gap affects senior-level competitiveness because your 
resume doesn't show team size, budget ownership, or multi-product roadmap 
evidence.

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

## Implementation Phases

### Phase 0: Foundation (CURRENT)

**Status**: ✅ Complete
- Basic fit scoring (50/30/20)
- Experience calculator
- Hard caps based on years
- 6-tier recommendations

---

### Phase 1: Experience Calculators (IN PROGRESS)

**Status**: 🔄 Specification complete, implementation pending
- Role-specific calculators (recruiting, engineering, sales, PM)
- Company credibility multipliers
- Leadership vs IC distinction
- Strategic action coaching framework

---

### Phase 2: Title & Company Detection (NEXT)

**Priority**: P2 - After Phase 1 complete  
**Effort**: 3-5 days  
**Impact**: Catches inflated titles and unverifiable companies

**Tasks**:
1. Implement title inflation detector
2. Implement enhanced company credibility checker
3. Add override logic to `force_apply_experience_penalties()`
4. Update strategic action templates
5. Test with inflated-title resumes
6. Test with unverifiable company resumes

**Deliverables**:
- `detect_title_inflation()` function
- `assess_company_credibility()` function (enhanced version)
- Override rules in backend safety net
- Coaching templates for title/company issues

---

### Phase 3: Competency Mapping Engine (FUTURE)

**Priority**: P3 - Strategic feature, not MVP  
**Effort**: 2-3 weeks  
**Impact**: High - but requires competency framework integration

**Tasks**:
1. Parse industry-standard competency frameworks (Excel → structured data)
2. Build competency evidence detector
3. Map resume signals to competency levels
4. Create PM competency mapping function
5. Create Engineering competency mapping function
6. Create TPM/TLM competency mapping function
7. Integrate with fit scoring system
8. Build competency gap reporting
9. Update strategic action with competency-specific coaching

**Challenges**:
- Competency frameworks are complex (8+ dimensions per role)
- Evidence detection is subjective (requires NLP + context)
- Multi-role support (PM, Eng, TPM, TLM, Sales, etc.)
- Maintaining accuracy without false positives

**Deliverables**:
- Structured competency framework data
- `map_pm_competencies()` function
- `map_engineering_competencies()` function
- Competency-based coaching templates
- Gap analysis reporting

---

### Phase 4: Career Switcher Detection (FUTURE)

**Priority**: P4 - Nice to have  
**Effort**: 1-2 weeks  
**Impact**: Medium - helps switchers understand positioning

**Tasks**:
1. Build career switcher pattern detector
2. Distinguish direct ownership vs adjacent exposure
3. Create switcher-specific coaching templates
4. Test with program → product switchers
5. Test with operations → engineering switchers

---

### Phase 5: Market Reality Filter (FUTURE)

**Priority**: P5 - Sensitive, needs careful design  
**Effort**: 1 week  
**Impact**: Medium - helps positioning without moral judgment

**Tasks**:
1. Build market positioning analyzer
2. Create sensitive topic handling rules
3. Write coaching templates for positioning strategy
4. Legal/ethical review
5. User testing with diverse candidates

---

## Data Requirements

### Competency Framework Data Structure

**Example: PM Competencies (Industry Standard)**

```json
{
  "PM_I": {
    "years_range": "0-2",
    "scope": "Feature ownership",
    "competencies": {
      "product_strategy": {
        "level": "Executes on product roadmap",
        "evidence_signals": [
          "Shipped features",
          "Followed PRD",
          "Supported roadmap execution"
        ]
      },
      "customer_insight": {
        "level": "Contributes to user research",
        "evidence_signals": [
          "Participated in user interviews",
          "Analyzed feedback",
          "Supported research"
        ]
      },
      "scale_complexity": {
        "level": "Small user base (<100K)",
        "evidence_signals": [
          "Managed features",
          "Small team coordination",
          "Limited organizational impact"
        ]
      }
    }
  },
  "Senior_PM": {
    "years_range": "4-8",
    "scope": "Product/platform ownership",
    "competencies": {
      "product_strategy": {
        "level": "Owns product strategy",
        "evidence_signals": [
          "Defined product vision",
          "Set multi-quarter roadmap",
          "Made build/buy/partner decisions",
          "Influenced org priorities"
        ]
      },
      "customer_insight": {
        "level": "Leads customer insight",
        "evidence_signals": [
          "Directed research strategy",
          "Defined user segments",
          "Established insight frameworks"
        ]
      },
      "scale_complexity": {
        "level": "Significant scale (10M+ users, $50M+ revenue)",
        "evidence_signals": [
          "Managed large user base",
          "Revenue accountability",
          "Multi-team influence",
          "VP-level stakeholders"
        ]
      }
    }
  }
}
```

---

## Testing Strategy

### Test Case 1: Title Inflation

**Resume**:
- Title: "Head of Product"
- Company: "InnovateTech Solutions" (unverifiable)
- Experience: 2 years, feature-level work
- No team size, budget, or roadmap mentioned

**Expected Detection**:
- `title_alignment`: "inflated"
- `demonstrated_level`: "PM II"
- `claimed_level`: "Head of Product"
- Override cap: 55%

**Expected Coaching**:
"Your title 'Head of Product' suggests senior leadership, but your resume shows feature-level work at an unverifiable company. Hiring managers will evaluate you as PM II, not Head of Product. This Senior PM role requires demonstrated product-level ownership. You are not competitive as currently positioned."

---

### Test Case 2: Competency Mismatch

**Resume**:
- Title: "Senior PM"
- 5 years experience
- Max scale: 500K users
- No budget/revenue accountability
- Peer-level coordination only

**JD**: Senior PM at Series C (20M users, $100M revenue)

**Expected Competency Gaps**:
1. Scale Complexity: 500K vs 20M users
2. Product Strategy: No evidence of product-level vision
3. Cross-functional Leadership: Peer coordination vs VP stakeholders

**Expected Override**: Cap at 40%

**Expected Recommendation**: "Long Shot" or "Do Not Apply"

---

### Test Case 3: Career Switcher

**Resume**:
- Current: "Product Manager"
- Prior: 8 years Program Management
- Language: "Supported PM team", "Contributed to roadmap"

**Expected Detection**:
- `is_switcher`: true
- `ownership_level`: "adjacent"
- Override cap: 40%

**Expected Coaching**:
"Your background is Program Management, not Product Management. Your resume shows adjacent exposure ('supported PM team', 'contributed to roadmap'), not direct product ownership. Senior PM roles require demonstrated product decision-making. Target Associate PM or PM I roles to build direct ownership."

---

## What We Never Do

**Forbidden Language**:
- ❌ "You're not good enough"
- ❌ "This is toxic to your career"
- ❌ "Companies won't hire you because..."
- ❌ "You should be more confident"
- ❌ Moral judgments about work choices
- ❌ Political framing
- ❌ Identity-based commentary

**What We Do Instead**:
- ✅ "This role requires X. Your background shows Y."
- ✅ "Market reality: Companies prioritize Z."
- ✅ "Your positioning should lead with A, not B."
- ✅ "Target these specific roles to close gaps."
- ✅ Assessment of market alignment, not personal worth
- ✅ Second-person coaching tone
- ✅ Receipts-based logic

---

## Frontend Implementation Notes

### Resume Leveling Page Framing

**Critical framing line** (must appear at top of `resume-leveling.html`):

```html
<div class="leveling-intro">
  <p class="framing-statement">
    This is how hiring managers level you, not how LinkedIn does.
  </p>
</div>
```

**Purpose**: Sets expectations and removes defensiveness immediately. Users understand they're getting recruiter perspective, not social validation.

**Placement**: Above the level badge, before any competency breakdown.

**Styling recommendation**:
```css
.framing-statement {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  font-style: italic;
  margin-bottom: 24px;
  text-align: center;
}
```

---

### Strategic Action Display

When displaying competency-based coaching, structure as:

```html
<div class="strategic-coaching">
  <section class="gaps">
    <h3>Key Gaps</h3>
    <!-- Bulleted list -->
  </section>
  
  <section class="market-reality">
    <h3>Market Reality</h3>
    <!-- Canonical inflation/credibility messaging -->
  </section>
  
  <section class="your-move">
    <h3>Your Move This Week</h3>
    <ol>
      <li><strong>Target these roles:</strong> [specific titles]</li>
      <li><strong>Add this evidence:</strong> [specific improvements]</li>
      <li><strong>Deprioritize:</strong> [what to stop]</li>
    </ol>
  </section>
  
  <section class="close-gap">
    <h3>Close the Gap</h3>
    <!-- Timeline with concrete milestones -->
  </section>
</div>
```

**Never display**: Internal competency framework names, raw competency scores, or diagnostic metadata.

---

## Integration with Existing System

### Current Flow

```
1. Upload resume
2. Analyze JD
3. Calculate fit score (50/30/20)
4. Apply experience penalties (hard caps)
5. Map to 6-tier recommendation
6. Generate strategic action
7. Return results
```

### Enhanced Flow (Phase 2+)

```
1. Upload resume
2. Analyze JD
3. Calculate fit score (50/30/20)
4. Apply experience penalties (hard caps)
5. [NEW] Detect title inflation
6. [NEW] Assess company credibility
7. [NEW] Detect career switcher patterns
8. [NEW] Apply competency-based overrides
9. Map to 6-tier recommendation
10. [NEW] Generate competency-aware strategic action
11. Return results + diagnostics
```

---

## Success Metrics

### Phase 2 (Title & Company Detection)

**Goals**:
- Detect 90%+ of inflated titles
- Identify 95%+ of unverifiable companies
- Reduce false "Strong Apply" for misaligned candidates by 30%

**Metrics**:
- Title inflation detection rate
- Company verification accuracy
- Override application rate (% of analyses)
- User feedback on coaching quality

### Phase 3 (Competency Mapping)

**Goals**:
- Map 80%+ of resume evidence to competency levels
- Provide competency-specific gaps for 90%+ of analyses
- Improve coaching specificity score by 50%

**Metrics**:
- Competency evidence detection accuracy
- Gap identification precision
- User satisfaction with coaching specificity
- Time to implement per role type

---

## Next Steps

1. ✅ **Complete Phase 1** (experience calculators, company credibility multipliers)
2. ⏳ **Design Phase 2** (title inflation, enhanced company checks)
3. ⏳ **Parse competency frameworks** (convert Excel to structured JSON)
4. ⏳ **Prototype competency mapping** (PM roles first)
5. ⏳ **User test with beta testers** (get feedback on honest coaching)
6. ⏳ **Iterate based on feedback**
7. ⏳ **Expand to other roles** (engineering, TPM, sales)

---

## Appendix: Why This Matters

### The Problem

**Current state**: Candidates apply to roles they're not ready for because:
1. Inflated job titles create false confidence
2. LinkedIn culture encourages "senior" self-labeling
3. No one tells them the truth about competency gaps
4. Resume feedback is either too harsh or too encouraging

### The Solution

**HenryHQ's approach**: Truth + Direction
- Honest assessment of readiness without shaming
- Clear competency gaps with specific evidence
- Actionable path to close gaps
- Market reality without moral judgment

### The Impact

**For candidates**:
- Stop wasting time on roles they won't get
- Understand specific gaps to close
- Target appropriate level roles
- Build plan to reach next level

**For HenryHQ**:
- Differentiation from generic resume tools
- Higher quality matches (better conversion)
- Builds trust through honesty
- Positions as strategic career advisor, not just document generator

---

**END OF INTEGRATION PLAN**
