# Leadership Evaluation & Positioning Engine (LEPE) — Implementation Specification

**Version:** 1.0  
**Last Updated:** December 18, 2025  
**Status:** Production-Ready  
**Scope:** Manager+ Roles Only  
**Owner:** HenryHQ Core Intelligence Layer

---

## Executive Summary

The Leadership Evaluation & Positioning Engine (LEPE) is a truth layer that evaluates people-leadership readiness for Manager+ roles with recruiter-grade realism. It separates eligibility from advisability, detects title inflation, and provides honest coaching when gaps are addressable.

**Core Principle:** Reality beats reassurance. LEPE exists to answer one question honestly:

> "Are you ready for this level of leadership in today's hiring market — and if not, what's the smartest move forward?"

**What LEPE Does:**
- Extracts leadership signals from resume (not just titles)
- Calculates accurate people leadership tenure
- Identifies leadership gaps vs role requirements
- Determines positioning strategy or hard lock
- Maintains accountability record

**What LEPE Does NOT Do:**
- Boost confidence with false optimism
- Accept title inflation at face value
- Apply to IC roles (hard bypass)
- Soften feedback based on user sentiment

---

## Table of Contents

1. [Applicability Rules](#applicability-rules)
2. [Leadership Competency Schema](#leadership-competency-schema)
3. [Leadership Tier Model](#leadership-tier-model)
4. [Signal Extraction Logic](#signal-extraction-logic)
5. [Tenure Calculation](#tenure-calculation)
6. [Requirement Inference](#requirement-inference)
7. [Positioning Decision Engine](#positioning-decision-engine)
8. [Output Contract](#output-contract)
9. [API Implementation](#api-implementation)
10. [Claude Prompt Templates](#claude-prompt-templates)
11. [Testing & Validation](#testing--validation)
12. [Integration Guidelines](#integration-guidelines)

---

## 1. Applicability Rules (Hard Guardrails)

### When LEPE Runs

LEPE applies **ONLY** to roles tagged as Manager+ levels:

```python
MANAGER_LEVELS = [
    "Manager",
    "Senior Manager",
    "Director",
    "Senior Director",
    "VP",
    "Head",
    "C-Suite"
]

def should_apply_lepe(role_level: str) -> bool:
    """
    Determines if LEPE should run for this role.
    
    Returns True only for Manager+ roles.
    """
    return role_level in MANAGER_LEVELS
```

### Explicit Bypass Rule

**If role_level < Manager:**
- Skip ALL LEPE logic
- Do NOT calculate leadership tenure
- Do NOT apply leadership credibility caps
- Do NOT run positioning engine
- Return None for all LEPE outputs

**This guardrail is non-negotiable.**

### Example Flow

```python
if not should_apply_lepe(role_level):
    return {
        "lepe_applicable": False,
        "reason": "Role is IC-level, LEPE does not apply"
    }

# Continue with LEPE logic
```

---

## 2. Leadership Competency Schema (Baseline, Role-Agnostic)

This schema overlays **every Manager+ job description**, regardless of JD quality.

### Core Competency Domains

**1. People Management**
- Hiring, performance management, coaching
- 1:1s, feedback, development plans
- Performance reviews, PIPs, exits
- Succession planning, talent pipeline

**Indicator Phrases:**
- "managed team of [N]", "hired", "fired", "coached"
- "performance reviews", "1:1s", "mentored"
- "built team from X to Y", "succession planning"

---

**2. Decision Authority**
- Hiring approvals, headcount decisions
- Budget ownership, spend authority
- Escalation responsibility, final say
- Trade-off decisions, resource allocation

**Indicator Phrases:**
- "owned budget of $X", "hiring authority"
- "final approval for", "escalation point"
- "prioritized", "allocated resources"

---

**3. Org Design & Scale**
- Team growth, restructures
- Span of control expansion
- Organizational architecture
- Reporting structure changes

**Indicator Phrases:**
- "grew team from X to Y", "restructured"
- "managed [N] direct reports, [M] indirect"
- "org design", "team topology"

---

**4. Strategic Leadership**
- Direction setting, vision creation
- Multi-quarter planning, roadmaps
- Strategic prioritization, north star
- Long-term vs short-term trade-offs

**Indicator Phrases:**
- "set strategy", "defined vision", "roadmap"
- "multi-year plan", "strategic priorities"
- "direction setting", "north star"

---

**5. Cross-Functional Influence**
- Executive partnership, stakeholder management
- Conflict resolution at senior levels
- Alignment across orgs
- Influencing without authority

**Indicator Phrases:**
- "collaborated with execs", "aligned cross-functionally"
- "resolved conflicts", "stakeholder management"
- "influenced [function]", "executive partner"

---

**6. Accountability & Ownership**
- Owning outcomes (not just activities)
- Risk management, failure ownership
- Corrective action, course correction
- Ultimately responsible for results

**Indicator Phrases:**
- "accountable for", "owned outcome"
- "responsible for $X revenue/P&L"
- "turned around", "corrected course"

---

### Signal Metadata Structure

Every detected leadership signal MUST include:

```python
class LeadershipSignal(BaseModel):
    competency_domain: str  # One of 6 domains above
    evidence_text: str      # Exact quote from resume
    evidence_type: str      # "explicit" | "implied" | "inferred"
    strength: str           # "strong" | "medium" | "weak"
    leadership_tier: str    # "Tier 1" | "Tier 2" | "Tier 3"
    role_title: str         # Job title where signal detected
    company: str            # Company name
    role_start_date: str    # ISO date or "YYYY-MM"
    role_end_date: str      # ISO date or "YYYY-MM" or "Present"
    scope_quantified: bool  # Has numbers (team size, budget, etc.)
```

**Example:**

```json
{
  "competency_domain": "People Management",
  "evidence_text": "Managed team of 8 engineers, conducted performance reviews, and hired 3 senior engineers",
  "evidence_type": "explicit",
  "strength": "strong",
  "leadership_tier": "Tier 2",
  "role_title": "Engineering Manager",
  "company": "Stripe",
  "role_start_date": "2020-03",
  "role_end_date": "2023-06",
  "scope_quantified": true
}
```

---

## 3. Leadership Tier Model (Canonical)

### Tier Definitions

**Tier 1 — Strategic / Functional Leadership**
- Cross-functional initiatives, project leadership
- Technical/functional expertise leadership
- **NO direct reports**
- **Does NOT count toward people leadership tenure**

**Examples:**
- "Led cross-functional product launch"
- "Owned technical strategy for platform"
- "Drove adoption of new framework across 50+ engineers"

---

**Tier 2 — People Leadership**
- Direct reports, performance management
- Hiring authority, firing responsibility
- Team accountability, people development
- **Counts fully toward people leadership tenure**

**Examples:**
- "Managed team of 5 product managers"
- "Hired and onboarded 3 engineers"
- "Conducted quarterly performance reviews"

---

**Tier 3 — Org-Level Leadership**
- Executive leadership, C-suite
- P&L ownership, revenue/cost accountability
- Board exposure, investor relations
- Multi-org scope (managing managers)
- **Counts as senior people leadership**

**Examples:**
- "VP Engineering, managed 45 engineers across 5 teams"
- "Owned $20M P&L, reported to CEO"
- "Built engineering org from 10 to 60 people"

---

### Tier Assignment Logic

```python
def determine_leadership_tier(signal: LeadershipSignal, role_data: dict) -> str:
    """
    Assigns leadership tier based on signal characteristics.
    
    Tier 3: P&L ownership, board exposure, VP+, managing managers
    Tier 2: Direct reports, hiring/firing authority, performance mgmt
    Tier 1: Everything else (strategic/functional leadership)
    """
    # Tier 3 indicators
    tier_3_indicators = [
        "P&L", "board", "VP", "managing managers",
        "executive team", "C-suite", "investor relations"
    ]
    
    # Tier 2 indicators
    tier_2_indicators = [
        "direct reports", "managed team", "hired", "fired",
        "performance reviews", "1:1s", "coaching"
    ]
    
    evidence_lower = signal.evidence_text.lower()
    
    if any(indicator.lower() in evidence_lower for indicator in tier_3_indicators):
        return "Tier 3"
    elif any(indicator.lower() in evidence_lower for indicator in tier_2_indicators):
        return "Tier 2"
    else:
        return "Tier 1"
```

---

## 4. Signal Extraction Logic

### Extraction Principles

1. **Parse every role, not just job titles**
   - A "Senior IC" can have leadership bullets
   - A "Manager" title can lack leadership evidence

2. **Extract from bullets, verbs, metrics, scope language**
   - Look for ownership verbs: "managed", "owned", "led"
   - Look for scope indicators: team size, budget, outcomes
   - Look for decision authority: "approved", "authorized", "prioritized"

3. **Detect mixed-scope roles**
   - Many roles blend IC + leadership work
   - Apply proportional credit (see below)

---

### Extraction Algorithm

```python
def extract_leadership_signals(resume: dict) -> List[LeadershipSignal]:
    """
    Extracts all leadership signals from resume.
    
    Returns list of LeadershipSignal objects with metadata.
    """
    signals = []
    
    for experience in resume.get("experience", []):
        role_title = experience.get("title", "")
        company = experience.get("company", "")
        dates = experience.get("dates", "")
        bullets = experience.get("bullets", [])
        
        # Parse dates
        start_date, end_date = parse_date_range(dates)
        
        # Extract from bullets
        for bullet in bullets:
            # Check each competency domain
            for domain, indicators in COMPETENCY_INDICATORS.items():
                for indicator in indicators:
                    if indicator.lower() in bullet.lower():
                        signal = LeadershipSignal(
                            competency_domain=domain,
                            evidence_text=bullet,
                            evidence_type=classify_evidence_type(bullet),
                            strength=assess_signal_strength(bullet),
                            leadership_tier=determine_leadership_tier(bullet, experience),
                            role_title=role_title,
                            company=company,
                            role_start_date=start_date,
                            role_end_date=end_date,
                            scope_quantified=has_numbers(bullet)
                        )
                        signals.append(signal)
    
    return deduplicate_signals(signals)
```

---

### Competency Indicator Mapping

```python
COMPETENCY_INDICATORS = {
    "People Management": [
        "managed team", "direct reports", "hired", "fired",
        "performance reviews", "1:1s", "coached", "mentored",
        "onboarded", "offboarded", "succession planning"
    ],
    "Decision Authority": [
        "owned budget", "hiring authority", "final approval",
        "escalation point", "prioritized", "allocated",
        "trade-off decisions", "resource allocation"
    ],
    "Org Design & Scale": [
        "grew team", "restructured", "org design",
        "team topology", "reporting structure",
        "managed [N] direct", "span of control"
    ],
    "Strategic Leadership": [
        "set strategy", "defined vision", "roadmap",
        "multi-year plan", "strategic priorities",
        "direction setting", "north star"
    ],
    "Cross-Functional Influence": [
        "collaborated with execs", "aligned cross-functionally",
        "stakeholder management", "executive partner",
        "influenced", "conflict resolution"
    ],
    "Accountability & Ownership": [
        "accountable for", "owned outcome", "responsible for",
        "P&L", "revenue", "turned around", "corrected course"
    ]
}
```

---

### Evidence Type Classification

```python
def classify_evidence_type(bullet: str) -> str:
    """
    Determines if evidence is explicit, implied, or inferred.
    
    Explicit: Clear statement with specifics
    Implied: Reasonable inference from context
    Inferred: Weak signal, needs confirmation
    """
    # Explicit: Has numbers, clear ownership verbs, specific outcomes
    if has_numbers(bullet) and has_ownership_verbs(bullet):
        return "explicit"
    
    # Implied: Has ownership verbs but less specific
    elif has_ownership_verbs(bullet):
        return "implied"
    
    # Inferred: Weak signals
    else:
        return "inferred"

def has_ownership_verbs(text: str) -> bool:
    ownership_verbs = ["managed", "owned", "led", "directed", "oversaw", "accountable"]
    return any(verb in text.lower() for verb in ownership_verbs)

def has_numbers(text: str) -> bool:
    return bool(re.search(r'\d+', text))
```

---

### Signal Strength Assessment

```python
def assess_signal_strength(bullet: str) -> str:
    """
    Rates signal strength based on evidence quality.
    
    Strong: Quantified + specific + outcome
    Medium: Clear statement, may lack quantification
    Weak: Vague or generic
    """
    has_qty = has_numbers(bullet)
    has_outcome = any(word in bullet.lower() for word in ["increased", "reduced", "improved", "generated"])
    has_scope = any(word in bullet.lower() for word in ["team", "budget", "org", "cross-functional"])
    
    if has_qty and has_outcome and has_scope:
        return "strong"
    elif has_qty or (has_outcome and has_scope):
        return "medium"
    else:
        return "weak"
```

---

## 5. Tenure Calculation

### Critical Rules

**Leadership tenure is NEVER derived from total career years.**

**People leadership years = cumulative duration of Tier 2+ signals only**

**Tier 1 signals alone → 0 people leadership years** (but show strategic leadership years separately)

---

### Mixed-Scope Credit Rule

If a role includes both IC and leadership responsibilities, apply proportional credit.

**Example:**

```
Role: "Senior Engineer & Tech Lead"
Duration: 2 years
Bullets:
- "Led team of 3 engineers" (Tier 2)
- "Implemented new architecture" (IC work)
- "Mentored junior engineers" (Tier 2)

Assessment: ~50% leadership, 50% IC
Credit: 1 year people leadership (2 years * 0.5)
```

---

### Calculation Algorithm

```python
def calculate_leadership_tenure(signals: List[LeadershipSignal]) -> dict:
    """
    Calculates leadership tenure across all tiers.
    
    Returns breakdown by tier and total people leadership years.
    """
    tier_1_years = 0
    tier_2_years = 0
    tier_3_years = 0
    
    # Group signals by role
    roles = group_signals_by_role(signals)
    
    for role_id, role_signals in roles.items():
        start_date = role_signals[0].role_start_date
        end_date = role_signals[0].role_end_date
        duration_years = calculate_duration(start_date, end_date)
        
        # Determine dominant tier for this role
        tier_2_signals = [s for s in role_signals if s.leadership_tier == "Tier 2"]
        tier_3_signals = [s for s in role_signals if s.leadership_tier == "Tier 3"]
        tier_1_signals = [s for s in role_signals if s.leadership_tier == "Tier 1"]
        
        # Proportional credit for mixed roles
        total_signals = len(role_signals)
        tier_2_proportion = len(tier_2_signals) / total_signals if total_signals > 0 else 0
        tier_3_proportion = len(tier_3_signals) / total_signals if total_signals > 0 else 0
        tier_1_proportion = len(tier_1_signals) / total_signals if total_signals > 0 else 0
        
        if tier_3_proportion > 0:
            tier_3_years += duration_years * tier_3_proportion
        if tier_2_proportion > 0:
            tier_2_years += duration_years * tier_2_proportion
        if tier_1_proportion > 0:
            tier_1_years += duration_years * tier_1_proportion
    
    # People leadership = Tier 2 + Tier 3
    people_leadership_years = tier_2_years + tier_3_years
    
    return {
        "people_leadership_years": round(people_leadership_years, 1),
        "tier_1_strategic_years": round(tier_1_years, 1),
        "tier_2_people_mgmt_years": round(tier_2_years, 1),
        "tier_3_org_level_years": round(tier_3_years, 1),
        "total_leadership_signals": len(signals)
    }
```

---

### Messaging Rule

**Never say "0 years" unless NO leadership signals exist at any tier.**

**Correct messaging:**

```python
def format_leadership_tenure_message(tenure: dict) -> str:
    """
    Formats tenure message for user-facing output.
    """
    people_years = tenure["people_leadership_years"]
    tier_1_years = tenure["tier_1_strategic_years"]
    
    if people_years == 0 and tier_1_years == 0:
        return "Your resume does not show people leadership experience."
    elif people_years == 0 and tier_1_years > 0:
        return f"You show approximately {tier_1_years} years of strategic/functional leadership, but no direct people management experience."
    else:
        return f"You show approximately {people_years} years of people leadership experience."
```

**Example outputs:**

✅ "You show approximately 3.5 years of people leadership. This role typically screens for 7+."

✅ "You show approximately 2 years of strategic leadership, but no direct people management experience. This Manager role requires people management."

❌ "You have 0 years of leadership experience." (Too harsh, misses Tier 1)

---

## 6. Requirement Inference (JD Normalization)

### Purpose

When job descriptions are vague or incomplete, LEPE infers leadership expectations based on role level.

---

### Inference Rules by Level

```python
INFERRED_REQUIREMENTS = {
    "Manager": {
        "people_leadership_years": 2,
        "required_competencies": ["People Management", "Decision Authority"],
        "typical_team_size": "3-8 direct reports"
    },
    "Senior Manager": {
        "people_leadership_years": 5,
        "required_competencies": ["People Management", "Strategic Leadership", "Cross-Functional Influence"],
        "typical_team_size": "8-15 direct reports"
    },
    "Director": {
        "people_leadership_years": 7,
        "required_competencies": ["People Management", "Org Design & Scale", "Strategic Leadership", "Accountability & Ownership"],
        "typical_team_size": "15-30 people (managing managers)"
    },
    "Senior Director": {
        "people_leadership_years": 10,
        "required_competencies": ["All 6 domains"],
        "typical_team_size": "30-60 people"
    },
    "VP": {
        "people_leadership_years": 12,
        "required_competencies": ["All 6 domains"],
        "typical_team_size": "60-150 people"
    }
}
```

---

### Inference Algorithm

```python
def infer_leadership_requirements(jd_analysis: dict, role_level: str) -> dict:
    """
    Infers leadership requirements when JD is vague.
    
    Additive, not fabricated: adds baseline expectations to JD analysis.
    """
    explicit_requirements = jd_analysis.get("leadership_requirements", {})
    inferred = INFERRED_REQUIREMENTS.get(role_level, {})
    
    # Merge: explicit requirements take precedence
    merged_requirements = {
        "people_leadership_years": explicit_requirements.get("years") or inferred["people_leadership_years"],
        "required_competencies": list(set(
            explicit_requirements.get("competencies", []) + inferred["required_competencies"]
        )),
        "typical_team_size": explicit_requirements.get("team_size") or inferred["typical_team_size"],
        "inference_applied": not bool(explicit_requirements)
    }
    
    return merged_requirements
```

---

### Example Usage

**Vague JD:**
> "We're looking for a Director of Engineering to lead our product development team."

**Inferred requirements:**
- 7+ years people leadership
- Required competencies: People Management, Org Design, Strategic Leadership, Accountability
- Typical scope: 15-30 people, managing managers

---

## 7. Positioning Decision Engine (Coaching vs Stop Sign)

### Purpose

Determines how the system responds once gaps are identified.

---

### Decision Logic

```python
def determine_positioning_strategy(
    candidate_tenure: float,
    required_tenure: float,
    missing_competencies: List[str],
    role_level: str
) -> dict:
    """
    Decides between positioning mode, caution mode, or hard lock.
    
    Returns positioning strategy with messaging.
    """
    gap = required_tenure - candidate_tenure
    
    # Hard lock conditions
    if gap > 4 or len(missing_competencies) >= 3:
        return {
            "mode": "HARD_LOCK",
            "recommendation": "Do Not Apply",
            "reasoning": generate_hard_lock_reasoning(gap, missing_competencies),
            "allow_proceed": False
        }
    
    # Caution mode
    elif gap >= 3 or len(missing_competencies) == 2:
        return {
            "mode": "APPLY_WITH_CAUTION",
            "recommendation": "Apply with Caution",
            "reasoning": generate_caution_reasoning(gap, missing_competencies),
            "positioning_strategy": generate_positioning_advice(candidate_tenure, missing_competencies),
            "allow_proceed": True,
            "risk_level": "high"
        }
    
    # Positioning mode
    elif gap <= 2:
        return {
            "mode": "POSITIONING",
            "recommendation": "Apply with Strategic Positioning",
            "reasoning": generate_positioning_reasoning(gap, missing_competencies),
            "positioning_strategy": generate_positioning_advice(candidate_tenure, missing_competencies),
            "allow_proceed": True,
            "risk_level": "medium"
        }
    
    # No gap
    else:
        return {
            "mode": "CLEARED",
            "recommendation": "Strong Candidate for Leadership Level",
            "allow_proceed": True,
            "risk_level": "low"
        }
```

---

### Mode Definitions

**POSITIONING Mode (Gap ≤ 2 years):**
- Surface implied leadership signals
- Generate transition narrative
- Name hiring manager skepticism explicitly
- Recommend resume + outreach adjustments

**Example messaging:**
> "You have 5 years of people leadership for a role requiring 7+. Here's how to position yourself:
> 
> 1. Lead your resume with team scaling accomplishments
> 2. Emphasize cross-functional influence in your summary
> 3. In your cover letter, acknowledge the stretch and explain how your Stripe experience prepared you for larger scope
> 
> Hiring manager skepticism: They may question whether you can manage a 20-person org. Address this proactively in interviews by discussing your experience growing teams and managing managers indirectly."

---

**APPLY_WITH_CAUTION Mode (Gap 3-4 years or 2 missing competencies):**
- Explicit skepticism about candidacy
- Positioning advice still provided
- Strong warning about low success probability

**Example messaging:**
> "You have 4 years of people leadership for a role requiring 8+. This is a significant gap.
> 
> Reality check: Most hiring managers will screen you out before interviews. This is a long shot.
> 
> If you proceed:
> - Emphasize Stripe brand and growth environment
> - Highlight any indirect management or org-level projects
> - Be prepared to explain why you're ready for this jump
> 
> Recommendation: Target Senior Manager roles instead, then move to Director after 2-3 years."

---

**HARD_LOCK Mode (Gap > 4 years or 3+ missing competencies):**
- Do not apply
- No positioning advice
- Clear explanation of why this is not advisable
- Redirect to appropriate level

**Example messaging:**
> "You have 2 years of people leadership for a role requiring 8+. This gap is too large to bridge with positioning.
> 
> Missing competencies:
> - Org Design & Scale (no evidence of managing managers)
> - Strategic Leadership (no evidence of multi-quarter planning)
> - P&L Accountability (no budget ownership signals)
> 
> This application will not succeed. Focus on Manager or Senior Manager roles where your experience is competitive."

---

## 8. Output Contract

### Required LEPE Outputs

Every LEPE evaluation must produce:

```python
class LEPEOutput(BaseModel):
    # Applicability
    lepe_applicable: bool
    role_level: str
    
    # Leadership analysis
    leadership_signals: List[LeadershipSignal]
    leadership_tenure: dict  # From calculate_leadership_tenure()
    leadership_gap_vs_role: float  # Years gap
    
    # Competency assessment
    detected_competencies: List[str]
    missing_competencies: List[str]
    competency_coverage: float  # Percentage of required competencies
    
    # Positioning decision
    positioning_mode: str  # CLEARED | POSITIONING | APPLY_WITH_CAUTION | HARD_LOCK
    recommendation: str
    reasoning: str
    positioning_strategy: Optional[str]
    allow_proceed: bool
    risk_level: str  # low | medium | high
    
    # Accountability
    accountability_record: dict
```

---

### Accountability Record Structure

```json
{
  "timestamp": "2025-12-18T10:30:00Z",
  "role_title": "Director of Engineering",
  "company": "Stripe",
  "candidate_tenure": 5.5,
  "required_tenure": 8.0,
  "gap": 2.5,
  "missing_competencies": ["Org Design & Scale"],
  "positioning_mode": "APPLY_WITH_CAUTION",
  "advice_given": "Target Senior Manager roles instead",
  "risk_communicated": "Most hiring managers will screen you out",
  "user_proceeded": null  // Updated if user applies anyway
}
```

---

## 9. API Implementation

### Endpoint: POST /api/lepe/evaluate

**Request:**
```json
{
  "resume": {
    "experience": [...],
    "skills": [...]
  },
  "jd_analysis": {
    "role_title": "Director of Engineering",
    "role_level": "Director",
    "leadership_requirements": {
      "years": 8,
      "competencies": ["People Management", "Org Design", "Strategic Leadership"]
    }
  }
}
```

**Response:**
```json
{
  "lepe_applicable": true,
  "role_level": "Director",
  "leadership_tenure": {
    "people_leadership_years": 5.5,
    "tier_1_strategic_years": 2.0,
    "tier_2_people_mgmt_years": 4.5,
    "tier_3_org_level_years": 1.0,
    "total_leadership_signals": 12
  },
  "leadership_gap_vs_role": 2.5,
  "detected_competencies": [
    "People Management",
    "Strategic Leadership",
    "Cross-Functional Influence",
    "Accountability & Ownership"
  ],
  "missing_competencies": [
    "Org Design & Scale"
  ],
  "competency_coverage": 0.83,
  "positioning_mode": "APPLY_WITH_CAUTION",
  "recommendation": "Apply with Caution",
  "reasoning": "You have 5.5 years of people leadership for a role requiring 8+. This is a stretch. Most hiring managers will screen you out before interviews.",
  "positioning_strategy": "Emphasize Stripe brand and growth environment. Highlight any indirect management or org-level projects. Be prepared to explain why you're ready for this jump.",
  "allow_proceed": true,
  "risk_level": "high",
  "accountability_record": {...}
}
```

---

### Error Responses

```json
{
  "error": "Role level not provided",
  "status": 400
}

{
  "error": "LEPE not applicable for IC roles",
  "status": 200,
  "lepe_applicable": false
}
```

---

## 10. Claude Prompt Templates

### System Prompt for LEPE Extraction

```
You are a leadership evaluation specialist analyzing resumes for Manager+ roles.

Your job:
1. Extract ALL leadership signals from the resume
2. Classify signals by competency domain
3. Assign leadership tier (1, 2, or 3)
4. Assess signal strength (strong, medium, weak)
5. Calculate accurate people leadership tenure

CRITICAL RULES:
1. Tier 1 leadership (strategic/functional) does NOT count as people leadership
2. Tier 2+ (direct reports, hiring/firing authority) counts fully
3. Mixed-scope roles get proportional credit
4. Never default to 0 years if any leadership signals exist
5. Extract from bullets, not just titles

COMPETENCY DOMAINS:
1. People Management - hiring, firing, performance reviews, coaching
2. Decision Authority - budget, hiring approvals, escalations
3. Org Design & Scale - team growth, restructures, span of control
4. Strategic Leadership - vision, roadmap, multi-quarter planning
5. Cross-Functional Influence - exec partnerships, stakeholder mgmt
6. Accountability & Ownership - P&L, outcomes, risk, failure

TIER DEFINITIONS:
- Tier 1: Project leadership, no direct reports
- Tier 2: Direct reports, people management
- Tier 3: Managing managers, P&L, executive leadership

Return JSON with this structure:
{
  "leadership_signals": [
    {
      "competency_domain": "People Management",
      "evidence_text": "exact quote from resume",
      "evidence_type": "explicit | implied | inferred",
      "strength": "strong | medium | weak",
      "leadership_tier": "Tier 1 | Tier 2 | Tier 3",
      "role_title": "title",
      "company": "company",
      "role_start_date": "YYYY-MM",
      "role_end_date": "YYYY-MM or Present",
      "scope_quantified": true/false
    }
  ],
  "leadership_tenure": {
    "people_leadership_years": 5.5,
    "tier_1_strategic_years": 2.0,
    "tier_2_people_mgmt_years": 4.5,
    "tier_3_org_level_years": 1.0
  },
  "detected_competencies": ["list of 6 domains found"],
  "tenure_explanation": "Brief explanation of how tenure was calculated"
}
```

---

### User Message Template

```
Extract leadership signals from this resume and calculate accurate people leadership tenure.

RESUME:
{json.dumps(resume, indent=2)}

ROLE CONTEXT:
Title: {role_title}
Level: {role_level}
Required Leadership: {required_years} years people leadership

Remember:
- Tier 1 leadership alone = 0 people leadership years
- Extract from bullets, not just titles
- Mixed-scope roles get proportional credit
- Be precise: 3.5 years, not "approximately 3-4 years"
```

---

### Positioning Strategy Prompt

```
You are a career strategist helping a candidate position themselves for a stretch leadership role.

SITUATION:
- Candidate has {candidate_years} years people leadership
- Role requires {required_years} years
- Gap: {gap} years
- Missing competencies: {missing_competencies}

Your job:
1. Generate a positioning narrative that addresses the gap honestly
2. Recommend resume/outreach adjustments
3. Name hiring manager skepticism explicitly
4. Provide interview prep guidance

TONE RULES:
- Direct, not apologetic
- Realistic, not optimistic
- Strategic, not desperate
- Acknowledges gap, doesn't minimize it

Return JSON:
{
  "positioning_narrative": "2-3 sentence framing for cover letter",
  "resume_adjustments": ["specific changes to make"],
  "outreach_strategy": "How to approach hiring manager/recruiter",
  "interview_prep": "Key skepticism to address proactively",
  "success_probability": "honest assessment (e.g., '20-30% chance of landing interview')"
}
```

---

## 11. Testing & Validation

### Test Cases

**Test Case 1: Clear Tier 2 Leadership**

**Input:**
```json
{
  "experience": [
    {
      "title": "Engineering Manager",
      "company": "Stripe",
      "dates": "2020-2023",
      "bullets": [
        "Managed team of 8 engineers",
        "Hired 5 senior engineers, conducted performance reviews",
        "Owned $2M engineering budget"
      ]
    }
  ]
}
```

**Expected Output:**
- `people_leadership_years`: 3.0
- `detected_competencies`: ["People Management", "Decision Authority"]
- `leadership_tier`: "Tier 2"

---

**Test Case 2: Mixed IC + Leadership**

**Input:**
```json
{
  "experience": [
    {
      "title": "Senior Engineer & Tech Lead",
      "company": "Google",
      "dates": "2019-2023",
      "bullets": [
        "Led team of 3 engineers on platform rewrite",
        "Implemented new caching architecture (IC work)",
        "Mentored 2 junior engineers"
      ]
    }
  ]
}
```

**Expected Output:**
- `people_leadership_years`: 2.0 (4 years * 50% proportional credit)
- `tier_1_strategic_years`: 2.0
- `detected_competencies`: ["People Management"]

---

**Test Case 3: Tier 1 Only (No People Leadership)**

**Input:**
```json
{
  "experience": [
    {
      "title": "Staff Engineer",
      "company": "Meta",
      "dates": "2018-2023",
      "bullets": [
        "Led cross-functional initiative for data privacy",
        "Drove adoption of new framework across 50+ engineers",
        "Owned technical strategy for platform"
      ]
    }
  ]
}
```

**Expected Output:**
- `people_leadership_years`: 0
- `tier_1_strategic_years`: 5.0
- `detected_competencies`: ["Strategic Leadership", "Cross-Functional Influence"]
- Message: "You show approximately 5 years of strategic/functional leadership, but no direct people management experience."

---

**Test Case 4: Gap > 4 Years (Hard Lock)**

**Candidate:** 2 years people leadership  
**Role Required:** 8 years (Director)

**Expected Output:**
- `positioning_mode`: "HARD_LOCK"
- `recommendation`: "Do Not Apply"
- `allow_proceed`: false
- `reasoning`: "This gap is too large to bridge with positioning."

---

### Validation Checklist

- [ ] LEPE bypasses IC roles correctly
- [ ] Tier 1 signals do NOT count as people leadership
- [ ] Mixed-scope roles get proportional credit
- [ ] Never says "0 years" when Tier 1 signals exist
- [ ] Hard lock triggers at gap > 4 years
- [ ] Positioning mode provides actionable advice
- [ ] Accountability record logs all decisions
- [ ] Missing competencies identified correctly
- [ ] Tenure calculation matches manual review

---

## 12. Integration Guidelines

### Integration with Job Fit Scoring

```python
def integrate_lepe_with_fit_scoring(
    base_fit_score: int,
    lepe_output: LEPEOutput
) -> int:
    """
    LEPE constrains fit score for Manager+ roles.
    
    Cannot be overridden by optimism elsewhere.
    """
    if not lepe_output.lepe_applicable:
        return base_fit_score
    
    # Hard cap based on positioning mode
    if lepe_output.positioning_mode == "HARD_LOCK":
        return min(base_fit_score, 30)  # Force "Do Not Apply"
    elif lepe_output.positioning_mode == "APPLY_WITH_CAUTION":
        return min(base_fit_score, 55)  # Force "Conditional Apply"
    elif lepe_output.positioning_mode == "POSITIONING":
        return min(base_fit_score, 70)  # Force "Apply"
    else:
        return base_fit_score  # No constraint if cleared
```

---

### Integration with Resume Leveling

Resume Leveling must reference LEPE outputs:

```python
# In resume-leveling.html or backend
if lepe_output and lepe_output.lepe_applicable:
    display_leadership_readiness_section(
        tenure=lepe_output.leadership_tenure,
        gaps=lepe_output.missing_competencies,
        positioning=lepe_output.positioning_mode
    )
```

---

### Integration with LinkedIn Scoring

LinkedIn Scoring should validate leadership claims:

```python
# Cross-reference LinkedIn profile with LEPE analysis
if linkedin_profile.claims_leadership and lepe_output.people_leadership_years == 0:
    flag_discrepancy("LinkedIn claims leadership but resume shows none")
```

---

## Tone & Language Rules

### Second-Person Voice Only

✅ "You have 5 years of people leadership."  
❌ "The candidate has 5 years of people leadership."

---

### No Shaming

✅ "This role requires 8+ years. You have 5. Here's how to position yourself."  
❌ "You're clearly not qualified for this role."

---

### No Euphemisms

✅ "This is a long shot. Most hiring managers will screen you out."  
❌ "This might be a bit of a stretch."

---

### No "Stretch Role" Language

✅ "This role requires 8+ years. You have 5. That's a 3-year gap."  
❌ "This is a stretch role that could be a great growth opportunity."

---

### Reality Beats Reassurance

✅ "You're not ready for Director yet. Target Senior Manager roles instead."  
❌ "You're almost there! Just need a bit more experience."

---

## North Star

LEPE exists to answer one question honestly:

> **"Are you ready for this level of leadership in today's hiring market — and if not, what's the smartest move forward?"**

This specification defines the **truth layer** for leadership evaluation in HenryHQ.

---

## Appendix

### Glossary

- **Tier 1 Leadership:** Strategic/functional leadership without direct reports
- **Tier 2 Leadership:** People management with direct reports
- **Tier 3 Leadership:** Org-level leadership, managing managers, P&L
- **People Leadership Tenure:** Cumulative years of Tier 2+ leadership
- **Positioning Mode:** Strategic advice to bridge small gaps (≤2 years)
- **Hard Lock:** Do not apply recommendation for gaps >4 years

---

### Related Specifications

- [Resume Leveling Spec](./RESUME_LEVELING_SPEC.md)
- [Job Fit Scoring](./JOB_FIT_SCORING_SPEC.md)
- [Credibility Alignment Engine](./CAE_SPEC.md)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 18, 2025 | Initial production-ready specification | Product |

---

**Status:** Production-Ready  
**Next Review:** January 2026  
**Owner:** HenryHQ Core Intelligence Layer
