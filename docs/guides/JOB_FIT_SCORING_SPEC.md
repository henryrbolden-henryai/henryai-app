# Job Fit Scoring Implementation Specification

**Version**: 2.0  
**Date**: December 18, 2025  
**Status**: DRAFT - Pending Backend Audit Validation  
**Purpose**: Single source of truth for job fit analysis system

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Experience Calculation Functions](#experience-calculation-functions)
4. [Backend Safety Net](#backend-safety-net)
5. [Company Credibility Scoring](#company-credibility-scoring)
6. [6-Tier Recommendation System](#6-tier-recommendation-system)
7. [Strategic Action Coaching Framework](#strategic-action-coaching-framework)
8. [System Prompt Requirements](#system-prompt-requirements)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Test Cases](#test-cases)

---

## Executive Summary

### Current State (As of Dec 18, 2025)

**Known Issues:**
1. ❌ Experience calculator only recognizes PM patterns (CRITICAL)
2. ❌ Strategic action doesn't enforce coaching-first framework (HIGH)
3. ❌ Third-person tone in user-facing fields (HIGH)
4. ⚠️ Company credibility scoring not implemented (MEDIUM)

**What Works:**
- ✅ 6-tier recommendation thresholds correct
- ✅ Hard cap logic functioning
- ✅ Deterministic scoring (same input = same output)
- ✅ Backend safety net applies penalties

### Target State

**Goals:**
1. Support all job functions (recruiting, engineering, sales, marketing, PM)
2. Distinguish leadership vs IC experience
3. Apply company credibility multipliers
4. Enforce coaching-first strategic guidance
5. Use second-person tone for user-facing content

---

## System Architecture

### High-Level Flow

```
1. User uploads resume → parse_resume()
2. User provides JD → extract_jd_requirements()
3. Claude API call → generate base analysis
   ├── 50% Skills match
   ├── 30% Experience match
   └── 20% Scope/Seniority match
4. Backend post-processing → force_apply_experience_penalties()
   ├── Calculate role-specific years → calculate_domain_years_from_resume()
   ├── Apply company credibility → get_credibility_multiplier()
   ├── Calculate years percentage
   ├── Apply hard caps based on percentage
   └── Update recommendation tier
5. Return to frontend → display results
```

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `backend/backend.py` | Main API logic | ~7200 |
| `/api/jd/analyze` endpoint | Job analysis entry point | TBD |
| `force_apply_experience_penalties()` | Backend safety net | TBD |
| `calculate_domain_years_from_resume()` | Router function | NEW |
| `calculate_*_years()` functions | Role-specific calculators | NEW |

---

## Experience Calculation Functions

### Router Function (NEW)

**Purpose**: Detect job function and route to appropriate calculator

**Location**: `backend/backend.py` (to be added after line ~3000)

**Implementation**:

```python
def calculate_domain_years_from_resume(resume_data: Dict[str, Any], jd_analysis: Dict[str, Any]) -> float:
    """
    Routes to appropriate experience calculator based on role type.
    
    Priority order:
    1. Recruiting roles
    2. Product Management roles
    3. Engineering roles
    4. Sales roles
    5. Marketing roles
    6. Fallback (generic total years)
    
    Args:
        resume_data: Parsed resume dictionary
        jd_analysis: Job description analysis with role_title and job_description
    
    Returns:
        float: Total years of relevant experience (may be adjusted by credibility)
    """
    role_title = jd_analysis.get("role_title", "").lower()
    jd_text = jd_analysis.get("job_description", "").lower()
    combined = f"{role_title} {jd_text}"
    
    # Priority order detection (first match wins)
    if any(pattern in combined for pattern in [
        "recruit", "talent acquisition", "sourcer", "headhunter", 
        "talent partner", "executive search"
    ]):
        return calculate_recruiting_years(resume_data, jd_analysis)
    
    elif any(pattern in combined for pattern in [
        "product manager", "pm ", "product lead", "product owner",
        "head of product", "vp product", "cpo"
    ]):
        return calculate_pm_years_from_resume(resume_data)
    
    elif any(pattern in combined for pattern in [
        "engineer", "developer", "software", "backend", "frontend",
        "full stack", "devops", "sre", "architect", "tech lead"
    ]):
        return calculate_engineering_years(resume_data, jd_analysis)
    
    elif any(pattern in combined for pattern in [
        "account executive", "sales", "business development",
        "account manager", "sales rep", "enterprise sales"
    ]):
        return calculate_sales_years(resume_data, jd_analysis)
    
    elif any(pattern in combined for pattern in [
        "marketing", "growth", "brand", "content", "digital marketing",
        "demand generation", "product marketing"
    ]):
        return calculate_marketing_years(resume_data, jd_analysis)
    
    else:
        # Fallback: count all professional years
        return calculate_total_professional_years(resume_data)
```

---

### 1. Recruiting Experience Calculator (NEW)

**Purpose**: Calculate recruiting experience with leadership distinction

**Location**: `backend/backend.py` (to be added after router)

**Implementation**:

```python
def calculate_recruiting_years(resume_data: Dict[str, Any], jd_analysis: Dict[str, Any]) -> float:
    """
    Calculate recruiting experience with leadership vs IC distinction.
    
    Leadership roles get full credit.
    Senior IC roles get 70% credit.
    IC roles get 0% credit for leadership requirements.
    
    Args:
        resume_data: Parsed resume dictionary
        jd_analysis: Job description analysis (to check if leadership required)
    
    Returns:
        float: Total recruiting years (adjusted for leadership level)
    """
    # Check if JD requires leadership
    jd_text = jd_analysis.get("job_description", "").lower()
    requires_leadership = any(term in jd_text for term in [
        "director", "head of", "vp", "lead", "manager", "leadership"
    ])
    
    # Pattern definitions
    leadership_patterns = [
        "director", "head of", "vp", "vice president", 
        "manager", "lead", "principal"
    ]
    senior_ic_patterns = [
        "senior talent partner", "senior recruiter", 
        "staff recruiter", "principal recruiter"
    ]
    recruiting_patterns = [
        "recruit", "talent acquisition", "sourcer", "headhunter",
        "talent partner", "executive search"
    ]
    
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        title = experience.get("title", "").lower()
        dates = experience.get("dates", "")
        years = parse_duration_to_years(dates)
        
        # Skip if not a recruiting role
        if not any(pattern in title for pattern in recruiting_patterns):
            continue
        
        # Apply multipliers based on level
        if any(pattern in title for pattern in leadership_patterns):
            # Leadership roles: full credit
            total_years += years
        elif any(pattern in title for pattern in senior_ic_patterns):
            # Senior IC: 70% credit if leadership required
            if requires_leadership:
                total_years += (years * 0.7)
            else:
                total_years += years  # Full credit for IC roles
        else:
            # IC roles: no credit for leadership requirements
            if not requires_leadership:
                total_years += years
            # else: 0 credit for IC in leadership role
    
    return round(total_years, 1)
```

**Test Cases**:

| Resume | JD Requirement | Calculated Years | Logic |
|--------|----------------|------------------|-------|
| 4 years Director | Leadership (7+ years) | 4.0 | Full credit |
| 3 years Senior Partner | Leadership (7+ years) | 2.1 | 70% credit (3 * 0.7) |
| 5 years IC Recruiter | Leadership (7+ years) | 0.0 | No credit |
| 4 years Director + 3 years Senior | Leadership (7+ years) | 6.1 | 4.0 + 2.1 |
| 5 years IC Recruiter | IC role (3+ years) | 5.0 | Full credit |

---

### 2. Product Management Calculator (EXISTING - KEEP)

**Purpose**: Calculate PM experience

**Location**: `backend/backend.py` (existing, ~line 3000)

**Current Implementation** (verify via audit):

```python
def calculate_pm_years_from_resume(resume_data: Dict[str, Any]) -> float:
    """
    Calculate total PM experience from resume.
    
    Matches patterns: product manager, pm, product lead, product owner, etc.
    """
    pm_patterns = [
        "product manager", "pm", "product lead", "product owner",
        "head of product", "vp product", "cpo", "chief product"
    ]
    
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        title = experience.get("title", "").lower()
        dates = experience.get("dates", "")
        
        if any(pattern in title for pattern in pm_patterns):
            years = parse_duration_to_years(dates)
            total_years += years
    
    return round(total_years, 1)
```

**Status**: ✅ Keep as-is, just integrate with router

---

### 3. Engineering Calculator (NEW)

**Purpose**: Calculate engineering experience with IC vs leadership distinction

**Implementation**:

```python
def calculate_engineering_years(resume_data: Dict[str, Any], jd_analysis: Dict[str, Any]) -> float:
    """
    Calculate engineering experience with leadership distinction.
    
    Similar logic to recruiting calculator.
    """
    jd_text = jd_analysis.get("job_description", "").lower()
    requires_leadership = any(term in jd_text for term in [
        "tech lead", "engineering manager", "em", "director", 
        "head of engineering", "architect", "principal"
    ])
    
    leadership_patterns = [
        "tech lead", "engineering manager", "director", 
        "head of", "vp", "architect", "principal engineer", "staff engineer"
    ]
    senior_ic_patterns = [
        "senior engineer", "senior developer", "senior software"
    ]
    engineering_patterns = [
        "engineer", "developer", "software", "backend", "frontend",
        "full stack", "devops", "sre"
    ]
    
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        title = experience.get("title", "").lower()
        dates = experience.get("dates", "")
        years = parse_duration_to_years(dates)
        
        if not any(pattern in title for pattern in engineering_patterns):
            continue
        
        if any(pattern in title for pattern in leadership_patterns):
            total_years += years
        elif any(pattern in title for pattern in senior_ic_patterns):
            if requires_leadership:
                total_years += (years * 0.7)
            else:
                total_years += years
        else:
            if not requires_leadership:
                total_years += years
    
    return round(total_years, 1)
```

---

### 4. Sales Calculator (NEW)

**Purpose**: Calculate sales experience with AE vs leadership distinction

**Implementation**:

```python
def calculate_sales_years(resume_data: Dict[str, Any], jd_analysis: Dict[str, Any]) -> float:
    """
    Calculate sales experience.
    
    Sales leadership vs IC less critical than other functions.
    Most sales roles just count total sales years.
    """
    sales_patterns = [
        "account executive", "sales", "business development",
        "account manager", "sales rep", "enterprise sales",
        "commercial", "revenue"
    ]
    
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        title = experience.get("title", "").lower()
        dates = experience.get("dates", "")
        
        if any(pattern in title for pattern in sales_patterns):
            years = parse_duration_to_years(dates)
            total_years += years
    
    return round(total_years, 1)
```

---

### 5. Marketing Calculator (NEW)

**Purpose**: Calculate marketing experience

**Implementation**:

```python
def calculate_marketing_years(resume_data: Dict[str, Any], jd_analysis: Dict[str, Any]) -> float:
    """
    Calculate marketing experience.
    
    Similar to sales - less IC vs leadership distinction.
    """
    marketing_patterns = [
        "marketing", "growth", "brand", "content", "digital marketing",
        "demand generation", "product marketing", "field marketing"
    ]
    
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        title = experience.get("title", "").lower()
        dates = experience.get("dates", "")
        
        if any(pattern in title for pattern in marketing_patterns):
            years = parse_duration_to_years(dates)
            total_years += years
    
    return round(total_years, 1)
```

---

### 6. Fallback Calculator (NEW)

**Purpose**: Count all professional years when role type unclear

**Implementation**:

```python
def calculate_total_professional_years(resume_data: Dict[str, Any]) -> float:
    """
    Fallback calculator for roles that don't match standard patterns.
    
    Sums all professional experience regardless of title.
    """
    total_years = 0.0
    
    for experience in resume_data.get("experience", []):
        dates = experience.get("dates", "")
        years = parse_duration_to_years(dates)
        total_years += years
    
    return round(total_years, 1)
```

---

### Helper Function: Duration Parser

**Purpose**: Convert date strings to years (float)

**Location**: `backend/backend.py` (likely exists, verify via audit)

**Expected Implementation**:

```python
def parse_duration_to_years(date_string: str) -> float:
    """
    Parse experience dates and return duration in years.
    
    Handles formats like:
    - "Jan 2020 - Present"
    - "2018 - 2022"
    - "Mar 2019 - Dec 2021"
    
    Returns:
        float: Years of experience (e.g., 2.5)
    """
    # Implementation details
    # Should handle "Present", current date calculation
    # Should handle various date formats
    pass
```

**Status**: Verify via audit if this exists and works correctly

---

## Backend Safety Net

### Purpose

Apply experience-based hard caps **after** Claude generates the initial fit score. This ensures penalties are enforced even if Claude's response doesn't properly account for experience gaps.

### Function: `force_apply_experience_penalties()`

**Location**: `backend/backend.py` (existing, ~line 4100)

**Current Implementation** (verify via audit):

```python
def force_apply_experience_penalties(
    analysis_data: Dict[str, Any], 
    resume_data: Dict[str, Any], 
    jd_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Backend safety net that enforces experience-based hard caps.
    
    Called after Claude generates fit score to ensure penalties apply.
    
    Steps:
    1. Extract required years from JD
    2. Calculate candidate's relevant years (role-specific)
    3. Apply company credibility multipliers
    4. Calculate years percentage
    5. Apply hard caps based on percentage
    6. Update recommendation if score changed
    
    Args:
        analysis_data: Claude's raw analysis output
        resume_data: Parsed resume
        jd_analysis: Job description analysis
    
    Returns:
        Dict: Updated analysis_data with caps applied
    """
    # Extract required years from JD
    required_years = jd_analysis.get("required_years", 0)
    
    if required_years == 0:
        # No experience requirement specified, no penalties
        return analysis_data
    
    # Calculate candidate's relevant years (NEW: use router)
    candidate_years = calculate_domain_years_from_resume(resume_data, jd_analysis)
    
    # Apply company credibility multipliers (NEW)
    credibility_adjusted_years = apply_credibility_adjustments(
        candidate_years, 
        resume_data, 
        jd_analysis
    )
    
    # Calculate years percentage
    years_percentage = (credibility_adjusted_years / required_years) * 100
    
    # Determine hard cap based on percentage
    if years_percentage < 50:
        hard_cap = 45
    elif years_percentage < 70:
        hard_cap = 55
    elif years_percentage < 90:
        hard_cap = 70
    else:
        hard_cap = 100  # No cap
    
    # Apply cap
    original_score = analysis_data.get("fit_score", 0)
    capped_score = min(original_score, hard_cap)
    
    # Update if changed
    if capped_score != original_score:
        analysis_data["fit_score"] = capped_score
        analysis_data["recommendation"] = get_recommendation_from_score(capped_score)
        analysis_data["_experience_cap_applied"] = True
        analysis_data["_cap_reason"] = f"Capped from {original_score} to {capped_score} due to {round(years_percentage)}% of required years"
        
        # Log for debugging
        print(f"⚠️  EXPERIENCE CAP APPLIED: {original_score} → {capped_score}")
        print(f"   Candidate years: {credibility_adjusted_years}")
        print(f"   Required years: {required_years}")
        print(f"   Percentage: {round(years_percentage)}%")
    
    return analysis_data
```

**Changes Required**:
1. ✅ Line ~4110: Change `calculate_pm_years_from_resume()` to `calculate_domain_years_from_resume()`
2. ✅ Add company credibility logic (new function call)
3. ✅ Update hard cap thresholds if needed (verify current values)

---

## Company Credibility Scoring

### Purpose

Adjust experience credit based on company scale, stage, and legitimacy. A year at Google ≠ a year at a 3-person seed startup.

### Credibility Multipliers

| Tier | Multiplier | Examples |
|------|-----------|----------|
| HIGH | 1.0x | Public companies, Series B+ ($10M+), established brands (>50 employees), well-known names |
| MEDIUM | 0.7x | Series A startups, 10-50 employees, regional players, lesser-known but legitimate companies |
| LOW | 0.3x | Seed-stage (<10 employees), defunct companies, very limited online presence |
| ZERO | 0.0x | Operations roles with inflated PM/Eng titles, volunteer work, side projects, obvious title inflation |

### Implementation

**Location**: `backend/backend.py` (to be added)

```python
def apply_credibility_adjustments(
    total_years: float,
    resume_data: Dict[str, Any],
    jd_analysis: Dict[str, Any]
) -> float:
    """
    Apply company credibility multipliers to calculated years.
    
    Args:
        total_years: Raw years calculated by role-specific function
        resume_data: Parsed resume with company details
        jd_analysis: Job analysis (for context)
    
    Returns:
        float: Credibility-adjusted years
    """
    adjusted_years = 0.0
    
    for experience in resume_data.get("experience", []):
        company = experience.get("company", "")
        title = experience.get("title", "")
        dates = experience.get("dates", "")
        years = parse_duration_to_years(dates)
        
        # Get credibility tier
        credibility = get_credibility_tier(company, title, experience)
        
        # Apply multiplier
        multiplier = get_credibility_multiplier(credibility)
        adjusted_years += (years * multiplier)
    
    return round(adjusted_years, 1)


def get_credibility_tier(company: str, title: str, experience: Dict[str, Any]) -> str:
    """
    Determine company credibility tier.
    
    Returns: "HIGH", "MEDIUM", "LOW", or "ZERO"
    """
    company_lower = company.lower()
    title_lower = title.lower()
    
    # ZERO tier (title inflation red flags)
    operations_titles = ["operations", "ops", "coordinator", "assistant"]
    pm_eng_titles = ["product manager", "engineer", "developer"]
    
    if any(op in title_lower for op in operations_titles) and \
       any(pm in title_lower for pm in pm_eng_titles):
        return "ZERO"  # "Operations Product Manager" = title inflation
    
    if "volunteer" in title_lower or "side project" in company_lower:
        return "ZERO"
    
    # HIGH tier (well-known companies)
    high_credibility_keywords = [
        # FAANG
        "google", "facebook", "meta", "amazon", "apple", "microsoft",
        # Other big tech
        "netflix", "uber", "airbnb", "stripe", "spotify", "linkedin",
        "twitter", "dropbox", "salesforce", "oracle", "adobe",
        # Finance
        "goldman", "jp morgan", "morgan stanley", "blackrock", "citadel",
        # Consulting
        "mckinsey", "bain", "bcg", "deloitte", "accenture",
        # Public companies (general indicators)
        "inc.", "corp.", "plc", "limited"
    ]
    
    if any(keyword in company_lower for keyword in high_credibility_keywords):
        return "HIGH"
    
    # Check for Series B+ or funding indicators
    if "series b" in company_lower or "series c" in company_lower or \
       "series d" in company_lower or "publicly traded" in company_lower:
        return "HIGH"
    
    # LOW tier (seed stage, defunct, unclear)
    low_credibility_indicators = [
        "stealth", "seed", "pre-seed", "defunct", "acquired", 
        "shutdown", "closed", "bankrupt"
    ]
    
    if any(indicator in company_lower for indicator in low_credibility_indicators):
        return "LOW"
    
    # Default: MEDIUM (legitimate but not tier 1)
    return "MEDIUM"


def get_credibility_multiplier(tier: str) -> float:
    """
    Map credibility tier to multiplier.
    
    Returns: 1.0, 0.7, 0.3, or 0.0
    """
    multipliers = {
        "HIGH": 1.0,
        "MEDIUM": 0.7,
        "LOW": 0.3,
        "ZERO": 0.0
    }
    return multipliers.get(tier, 0.7)  # Default to MEDIUM
```

**Example Calculations**:

| Resume | Raw Years | Credibility Adjustments | Adjusted Years |
|--------|-----------|------------------------|----------------|
| 4 years @ Google Director | 4.0 | 4.0 × 1.0 = 4.0 | 4.0 |
| 2 years @ Series A startup | 2.0 | 2.0 × 0.7 = 1.4 | 1.4 |
| 3 years @ Seed startup | 3.0 | 3.0 × 0.3 = 0.9 | 0.9 |
| 1 year "PM" @ Operations | 1.0 | 1.0 × 0.0 = 0.0 | 0.0 |
| 4 years Google + 2 years Series A | 6.0 | (4.0 × 1.0) + (2.0 × 0.7) | 5.4 |

**Status**: ⚠️ Not yet implemented (verify via audit)

---

## 6-Tier Recommendation System

### Purpose

Replace binary "Apply/Skip" with graduated guidance that reflects reality.

### Tier Definitions

| Tier | Score Range | Label | Meaning |
|------|-------------|-------|---------|
| 1 | 85-100% | Strong Apply | Prioritize immediately |
| 2 | 70-84% | Apply | Good fit, worth pursuing |
| 3 | 55-69% | Consider | Moderate fit, apply if interested |
| 4 | 40-54% | Apply with Caution | Stretch role, strategic positioning needed |
| 5 | 25-39% | Long Shot | Significant gaps, unlikely |
| 6 | 0-24% | Do Not Apply | Not recommended, focus elsewhere |

### Implementation

**Location**: `backend/backend.py` (existing, verify line number via audit)

**Function**: `get_recommendation_from_score()`

```python
def get_recommendation_from_score(capped_score: int) -> str:
    """
    Map fit score to recommendation tier.
    
    Args:
        capped_score: Fit score after hard caps applied
    
    Returns:
        str: One of 6 recommendation labels
    """
    if capped_score >= 85:
        return "Strong Apply"
    elif capped_score >= 70:
        return "Apply"
    elif capped_score >= 55:
        return "Consider"
    elif capped_score >= 40:
        return "Apply with Caution"
    elif capped_score >= 25:
        return "Long Shot"
    else:
        return "Do Not Apply"
```

**Frontend Mapping** (verify via audit):

```javascript
// frontend/results.html or similar
const recommendationStyles = {
    "Strong Apply": { color: "#10b981", badge: "✓" },
    "Apply": { color: "#60a5fa", badge: "→" },
    "Consider": { color: "#f59e0b", badge: "?" },
    "Apply with Caution": { color: "#ef4444", badge: "⚠" },
    "Long Shot": { color: "#dc2626", badge: "✗" },
    "Do Not Apply": { color: "#991b1b", badge: "✗✗" }
};
```

**Status**: ✅ Thresholds confirmed correct via Darnel testing

---

## Strategic Action Coaching Framework

### Purpose

Provide score-band-specific guidance that prioritizes preparation over blind application. Different scores require different strategies.

### Framework by Score Band

#### Band 1: 85-100% (Strong Apply)

**Goal**: Convert strength into immediate action

**Format**:
```
"Apply immediately. [Specific strength]. [Differentiation]. [Outreach strategy]."
```

**Example**:
```
"Apply immediately. Your Ripple consumer wallet experience is exactly 
what they need for this fintech payments role. Reach out to the hiring 
manager on LinkedIn today and lead with your 2.3M user scale."
```

**Tone**: Confident, action-oriented, no hesitation

**Length**: 50-75 words

---

#### Band 2: 70-84% (Apply)

**Goal**: Tighten positioning BEFORE applying

**Format**:
```
"Before applying, tighten your resume to close the remaining gaps. 
[Specific improvements to make]. Once improved, apply quickly and 
[outreach strategy]. Don't rely on the ATS alone."
```

**Example**:
```
"Before applying, tighten your resume to close the remaining gaps. 
Focus on sharpening fintech impact metrics, emphasizing scale (2.3M+ users), 
and highlighting cross-functional leadership in payments infrastructure. 
Once improved, apply within 24 hours and reach out to the hiring manager 
with your Ripple Labs experience. Don't rely on the ATS to do the work."
```

**CRITICAL**: MUST start with "Before applying" for this band

**Tone**: Coaching-first, strategic, solution-focused

**Length**: 75-100 words

---

#### Band 3: 55-69% (Consider) or 40-54% (Apply with Caution)

**Goal**: Honest assessment + concrete weekly action plan

**Format**:
```
"You have [strength], but this role favors [what's missing]. The 
opportunity is viable if [conditions].

YOUR MOVE THIS WEEK:
1. Target these roles: [3 specific alternative titles]
2. Add this evidence: [1-2 specific resume improvements]
3. If still interested: [specific positioning requirement]

Before applying to THIS role, [specific preparation]. Once positioned 
correctly, [outreach guidance]."
```

**Example**:
```
"You have strong consumer product experience at scale, but this role 
favors candidates with direct customer support product ownership and 
chatbot experience. The opportunity is viable if you clearly position 
your consumer impact and experimentation depth.

YOUR MOVE THIS WEEK:
1. Target these roles: Consumer PM at Intercom, Growth PM at Zendesk, 
   Product Manager at Help Scout
2. Add this evidence: Quantify any customer-facing features you owned, 
   emphasize cross-functional work with support teams
3. If still interested in THIS role: Add self-service initiatives and 
   chatbot exposure to your resume

Before applying to this role, update your resume to emphasize customer 
problem-solving and support team partnerships. Once positioned correctly, 
apply and reach out to the hiring manager."
```

**Tone**: Honest about gaps, solution-focused, strategic

**Length**: 125-150 words

---

#### Band 4: 25-39% (Long Shot)

**Goal**: Reality check + concrete alternative path

**Format**:
```
"This is a significant stretch. [Gap explanation].

YOUR MOVE THIS WEEK:
1. Target these roles: [3 specific roles at appropriate level]
2. Build this evidence: [specific competency to develop]
3. Deprioritize: [what to stop applying to]

Timeline: [concrete readiness milestone]."
```

**Example**:
```
"This is a significant stretch for your current experience level. The 
role requires 10+ years at Staff/Principal scope with multi-product 
platform ownership. You're at 8 years Senior-level with single-product focus.

YOUR MOVE THIS WEEK:
1. Target these roles: Senior PM at Stripe, Atlassian, Datadog; Staff PM 
   at smaller Series B companies
2. Build this evidence: Lead a multi-quarter platform initiative, partner 
   with 3+ product teams, influence at VP level
3. Deprioritize: Stop applying to Principal/Staff roles at FAANG immediately

Timeline: You'll be competitive for Staff PM in 12-18 months with 
multi-product platform scope and proven organizational influence."
```

**Tone**: Direct, honest, helpful redirection with timeline

**Length**: 100-125 words

---

#### Band 5: 0-24% (Do Not Apply)

**Goal**: Clear "no" + immediate redirection

**Format**:
```
"Do not apply to this role. [Clear explanation why].

YOUR MOVE THIS WEEK:
1. Target these roles: [3 specific matching roles]
2. Focus on: [what actually matches background]
3. Deprioritize: [entire category to avoid]"
```

**Example**:
```
"Do not apply to this role. This is a Senior Backend Engineer position 
requiring 5+ years of hands-on backend development. Your background is 
Senior Product Management, not backend engineering.

YOUR MOVE THIS WEEK:
1. Target these roles: Senior PM at Uber, DoorDash, Instacart; Group PM 
   at Square, Stripe
2. Focus on: Delivery, logistics, or platform companies where your 8 years 
   of product leadership are directly relevant
3. Deprioritize: Engineering, data science, or technical IC roles entirely"
```

**Tone**: Direct, no ambiguity, helpful redirection

**Length**: 75-100 words

---

### Implementation in System Prompt

**Location**: `/api/jd/analyze` endpoint system prompt

**Add this section** (verify via audit if it exists):

```
STRATEGIC ACTION FRAMEWORK BY SCORE BAND:

For 85-100% (Strong Apply):
"Apply immediately. [Strength]. [Differentiation]. [Outreach]."
Example: "Apply immediately. Your Ripple consumer wallet experience is exactly what they need. Reach out to the hiring manager today."

For 70-84% (Apply):
"Before applying, tighten your resume to close the remaining gaps. [Specific improvements]. Once improved, [outreach]. Don't rely on the ATS alone."
CRITICAL: MUST start with "Before applying" for this band.

For 55-69% (Consider) OR 40-54% (Apply with Caution):
"You have [strength], but this role favors [what's missing]. Before applying, [specific preparation]."

For 25-39% (Long Shot):
"This is a significant stretch. [Gap]. Consider [alternative]."

For 0-24% (Do Not Apply):
"Do not apply to this role. [Explanation]. Focus on [better match]."

TONE REQUIREMENTS:
- Use SECOND PERSON for strategic_action: "your background" NOT "Maya's background"
- Use SECOND PERSON for gap mitigation: "you can" NOT "candidate can"
- Use THIRD PERSON for level analysis: "Maya is a legitimate Senior PM" (objective assessment)
```

**Status**: ⚠️ Verify via audit if this framework exists in deployed prompt

---

## System Prompt Requirements

### Full Prompt Structure

**Location**: `/api/jd/analyze` endpoint

**Required Sections** (verify via audit):

1. **Identity Rules** ✅ (confirmed exists from Dec 16 fix)
2. **Grounding Rules** ✅ (confirmed exists)
3. **Scoring Framework** ✅ (confirmed exists)
4. **Experience Penalties** ⚠️ (verify mentions backend safety net)
5. **Strategic Action Framework** ❌ (likely missing, verify via audit)
6. **Tone Requirements** ❌ (likely missing, verify via audit)
7. **Company Credibility** ❌ (not implemented, verify not in prompt)

### Sections to Add/Update

#### Section: Strategic Action Framework

**Add after scoring framework section:**

```
=== STRATEGIC ACTION FRAMEWORK ===

Your strategic_action field MUST follow these score-band-specific frameworks:

85-100% (Strong Apply):
Format: "Apply immediately. [Strength]. [Differentiation]. [Outreach]."
Length: 50-75 words
Tone: Confident, action-oriented

70-84% (Apply):
Format: "Before applying, tighten resume to close gaps. [Improvements]. Once improved, [outreach]."
Length: 75-100 words
CRITICAL: MUST start with "Before applying"
Tone: Coaching-first, strategic

55-69% (Consider) OR 40-54% (Apply with Caution):
Format: "You have [strength], but this role favors [missing]. Before applying, [preparation]."
Length: 100-125 words
Tone: Honest, solution-focused

25-39% (Long Shot):
Format: "This is a significant stretch. [Gap]. Consider [alternative]."
Length: 50-75 words
Tone: Direct, helpful redirection

0-24% (Do Not Apply):
Format: "Do not apply. [Explanation]. Focus on [better match]."
Length: 50-75 words
Tone: Clear, no ambiguity
```

#### Section: Tone Requirements

**Add after strategic action framework:**

```
=== TONE REQUIREMENTS ===

SECOND PERSON (coaching tone) for:
- strategic_action: "your background" NOT "Maya's background"
- recommendation rationale: "you should" NOT "candidate should"
- gap mitigation: "you can address" NOT "they can address"
- interview prep: "you'll want to" NOT "candidate will want to"

THIRD PERSON (objective assessment) for:
- level_analysis: "Maya is a legitimate Senior PM" (factual assessment)
- experience_summary: "The candidate has 8 years" (objective)
- strengths/gaps enumeration: "Strong consumer product experience" (factual)

When in doubt, use SECOND PERSON for any field the user will read directly.
```

#### Section: Backend Safety Net Note

**Add after experience scoring section:**

```
=== EXPERIENCE PENALTIES ===

Note: Your initial fit_score will be post-processed by a backend safety net.

The backend will:
1. Calculate the candidate's role-specific years of experience
2. Apply company credibility multipliers
3. Compare to JD required years
4. Apply hard caps if experience is insufficient:
   - <50% of required years → CAP at 45%
   - 50-69% of required years → CAP at 55%
   - 70-89% of required years → CAP at 70%
   - 90%+ of required years → NO CAP

Your job: Provide the most accurate initial assessment.
The backend will enforce penalties if you miss them.

Do NOT fabricate experience to boost the score.
Do NOT ignore significant experience gaps.
The backend will catch it.
```

---

## Implementation Roadmap

### Phase 1: Backend Calculator Fix (CRITICAL)

**Priority**: P0  
**Effort**: 2-3 hours  
**Impact**: Unblocks all non-PM roles

**Tasks**:
1. ✅ Create audit request for Claude Code
2. ⏳ Wait for audit results
3. ⏳ Review audit findings
4. ⏳ Implement router function (`calculate_domain_years_from_resume`)
5. ⏳ Implement role-specific calculators (recruiting, engineering, sales, marketing)
6. ⏳ Update `force_apply_experience_penalties()` to call router
7. ⏳ Test with Jordan's resume (recruiting)
8. ⏳ Test with engineer resume
9. ⏳ Test with sales resume
10. ⏳ Verify PM roles still work (regression test)

**Files to Modify**:
- `backend/backend.py`: Add 5 new functions (~150 lines)
- `backend/backend.py`: Update line ~4110 (1 line change)

**Success Criteria**:
- ✅ Jordan scores 55-70% (not 45%)
- ✅ Logs show "Calculated 4.2 years recruiting leadership"
- ✅ Recommendation is "Conditional Apply" or "Apply"
- ✅ PM roles still score correctly (no regression)

---

### Phase 2: Strategic Action Framework (HIGH)

**Priority**: P1  
**Effort**: 1-2 hours  
**Impact**: Improves user experience, better coaching

**Tasks**:
1. ⏳ Update system prompt with score-band frameworks
2. ⏳ Add tone requirements (second vs third person)
3. ⏳ Test with Maya's resume at 78% (Stripe)
4. ⏳ Verify "Before applying" appears for 70-84% band
5. ⏳ Verify second-person tone throughout
6. ⏳ Test other score bands (90%, 60%, 40%, 20%)

**Files to Modify**:
- `backend/backend.py`: Update system prompt (~50 lines added)

**Success Criteria**:
- ✅ 70-84% scores start with "Before applying"
- ✅ All user-facing text uses "your" not "Maya's"
- ✅ Different guidance for each score band

---

### Phase 3: Company Credibility (MEDIUM)

**Priority**: P2  
**Effort**: 2-3 hours  
**Impact**: More accurate experience assessment

**Tasks**:
1. ⏳ Implement `apply_credibility_adjustments()`
2. ⏳ Implement `get_credibility_tier()`
3. ⏳ Implement `get_credibility_multiplier()`
4. ⏳ Integrate with `force_apply_experience_penalties()`
5. ⏳ Test with mixed-credibility resume (Google + seed startup)
6. ⏳ Verify multipliers apply correctly
7. ⏳ Test title inflation detection ("Operations Product Manager" → 0x)

**Files to Modify**:
- `backend/backend.py`: Add 3 new functions (~100 lines)
- `backend/backend.py`: Update safety net to call credibility functions

**Success Criteria**:
- ✅ 4 years Google Director = 4.0 years
- ✅ 2 years Series A = 1.4 years (0.7x)
- ✅ 3 years seed startup = 0.9 years (0.3x)
- ✅ 1 year "Operations PM" = 0.0 years
- ✅ Logs show credibility adjustments

---

### Phase 4: Additional Improvements (LOW)

**Priority**: P3  
**Effort**: 1-2 hours each  
**Impact**: Nice to have

**Features**:
1. Career gap detection (3+ month gaps)
2. Staff/Principal scope gap detection
3. LinkedIn skip button fix
4. "Do Not Apply" label verification

**Status**: Lower priority, address after Phases 1-3 complete

---

## Test Cases

### Test Suite: Experience Calculators

#### Test 1: Jordan's Resume (Recruiting Director)

**Resume**:
- Director, Technical Recruiting @ Headway (Aug 2022 - Present) = 2.3 years
- Senior Talent Partner @ Heidrick (Dec 2019 - Aug 2022) = 2.7 years
- Talent Partner @ Heidrick (5 years prior) = 5.0 years
- Total: 10 years recruiting, 4.9 years leadership

**JD**: Headway Director, Technical Recruiting (7+ years recruiting leadership)

**Expected Calculation**:
```
Leadership years:
- Director (2.3 years × 1.0) = 2.3
- Senior Partner (2.7 years × 0.7) = 1.9
- IC Partner (5.0 years × 0.0) = 0.0
Total leadership: 4.2 years
```

**Expected Results**:
- Calculated years: 4.2
- Required years: 7.0
- Percentage: 60%
- Hard cap: 55%
- Fit score: 55% (capped from potential higher)
- Recommendation: "Consider" or "Apply with Caution"
- Strategic action: "You have [strength], but this role favors [7+ years leadership]. Before applying, position your 4 years of recruiting leadership prominently..."

**Current (Broken) Result**:
- Calculated years: 0.0
- Percentage: 0%
- Hard cap: 45%
- Recommendation: "Do Not Apply"

---

#### Test 2: Maya's Resume (Product Manager)

**Resume**:
- Senior PM @ Various companies = 8 years PM experience

**JD**: Stripe Senior PM (5+ years PM experience)

**Expected Calculation**:
```
PM years: 8.0
Required: 5.0
Percentage: 160%
Hard cap: None (>90%)
```

**Expected Results**:
- Calculated years: 8.0
- Required years: 5.0
- Percentage: 160%
- Hard cap: None
- Fit score: ~78% (based on skills/scope, no experience cap)
- Recommendation: "Apply"
- Strategic action: "Before applying, tighten your resume to close the remaining gaps..."

**Current Result**: ✅ Working correctly (regression test)

---

#### Test 3: Engineer Resume (Backend Engineer)

**Resume**:
- Senior Backend Engineer @ Google (3 years)
- Backend Engineer @ Startup (3 years)
- Total: 6 years engineering

**JD**: Staff Backend Engineer (8+ years backend engineering, leadership expected)

**Expected Calculation**:
```
Leadership years (staff role requires leadership):
- Senior Engineer (3 years × 0.7) = 2.1
- Engineer (3 years × 0.0) = 0.0
Total: 2.1 years leadership-level
```

**Expected Results**:
- Calculated years: 2.1
- Required years: 8.0
- Percentage: 26%
- Hard cap: 45%
- Recommendation: "Long Shot"
- Strategic action: "This is a significant stretch. You have 6 years engineering but only 3 at senior level. Consider targeting Senior Engineer roles first..."

---

#### Test 4: Sales Resume (Account Executive)

**Resume**:
- Enterprise AE @ Salesforce (4 years)

**JD**: Senior Enterprise AE (3+ years AE experience)

**Expected Calculation**:
```
Sales years: 4.0
Required: 3.0
Percentage: 133%
Hard cap: None (>90%)
```

**Expected Results**:
- Calculated years: 4.0
- Required years: 3.0
- Percentage: 133%
- Hard cap: None
- Fit score: ~85% (strong match)
- Recommendation: "Strong Apply"
- Strategic action: "Apply immediately. Your 4 years of enterprise sales at Salesforce is exactly what they need..."

---

#### Test 5: PM → Recruiting Career Switcher

**Resume**:
- Senior PM @ Uber (8 years)

**JD**: Technical Recruiter (3+ years recruiting)

**Expected Calculation**:
```
Recruiting years: 0.0 (PM experience doesn't count for recruiting)
Required: 3.0
Percentage: 0%
Hard cap: 45%
```

**Expected Results**:
- Calculated years: 0.0
- Required years: 3.0
- Percentage: 0%
- Hard cap: 45%
- Recommendation: "Do Not Apply"
- Strategic action: "Do not apply to this role. This is a recruiting position requiring 3+ years of recruiting experience. Your background is Product Management, not recruiting..."

---

### Test Suite: Company Credibility

#### Test 6: Mixed Credibility Resume

**Resume**:
- Director, PM @ Google (4 years) → HIGH (1.0x)
- PM @ Series A Startup (2 years) → MEDIUM (0.7x)
- PM @ Seed Startup (1 year) → LOW (0.3x)

**JD**: Senior PM (5+ years PM)

**Expected Calculation**:
```
Raw years: 7.0
Credibility-adjusted:
- Google: 4.0 × 1.0 = 4.0
- Series A: 2.0 × 0.7 = 1.4
- Seed: 1.0 × 0.3 = 0.3
Total: 5.7 years
```

**Expected Results**:
- Calculated years: 5.7
- Required years: 5.0
- Percentage: 114%
- Hard cap: None
- Fit score: ~75-80%
- Recommendation: "Apply"

---

#### Test 7: Title Inflation Detection

**Resume**:
- Operations Product Manager @ Startup (2 years)

**JD**: Product Manager (3+ years PM)

**Expected Calculation**:
```
Raw years: 2.0
Credibility adjustment: ZERO (operations title inflation)
Adjusted years: 0.0
```

**Expected Results**:
- Calculated years: 0.0
- Required years: 3.0
- Percentage: 0%
- Hard cap: 45%
- Recommendation: "Do Not Apply"
- Strategic action: "Do not apply. Your 'Operations Product Manager' title is not true product management experience..."

---

### Test Suite: Strategic Action Framework

#### Test 8: 78% Score (Apply Band)

**Expected strategic_action**:
- ✅ Starts with "Before applying, tighten your resume..."
- ✅ Includes specific improvement areas
- ✅ Includes "Once improved, apply quickly..."
- ✅ Uses second person ("your background" not "Maya's background")
- ✅ Length: 75-100 words

**Current (Broken)**:
- ❌ Starts with "Apply within 24 hours..."
- ❌ No preparation guidance

---

#### Test 9: 92% Score (Strong Apply Band)

**Expected strategic_action**:
- ✅ Starts with "Apply immediately"
- ✅ Highlights specific strength
- ✅ Includes outreach strategy
- ✅ Length: 50-75 words
- ✅ Confident tone

---

#### Test 10: 60% Score (Consider Band)

**Expected strategic_action**:
- ✅ Format: "You have [strength], but this role favors [missing]. Before applying, [preparation]."
- ✅ Honest about gaps
- ✅ Provides concrete preparation steps
- ✅ Length: 100-125 words

---

#### Test 11: 15% Score (Do Not Apply Band)

**Expected strategic_action**:
- ✅ Starts with "Do not apply to this role"
- ✅ Clear explanation why
- ✅ Redirects to better opportunities
- ✅ Length: 50-75 words
- ✅ Direct, helpful tone

---

## Appendix A: Open Questions

**Questions for Backend Audit**:

1. Does `calculate_pm_years_from_resume()` exist and what patterns does it match?
2. Are there any role-specific calculators already implemented?
3. What experience calculator does `force_apply_experience_penalties()` currently call?
4. What are the exact hard cap thresholds in production?
5. What are the exact recommendation thresholds in production?
6. Is company credibility implemented anywhere (prompt or code)?
7. Does the system prompt have strategic_action formatting rules?
8. Does the system prompt enforce second-person tone?
9. Are there any surprise functions we don't know about?

**Questions for Design Review**:

1. Should "Senior Talent Partner" get 0.7x credit for leadership roles? (Current spec: YES)
2. Should PM experience count for recruiting roles? (Current spec: NO, separate functions)
3. Should we display credibility tier to users? (Current spec: NO, internal only)
4. Should we log credibility adjustments for debugging? (Current spec: YES)
5. Should "Do Not Apply" be red or gray in UI? (Need designer input)

---

## Appendix B: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 18, 2025 | Henry + Claude | Initial draft based on audit findings |
| 2.0 | Dec 18, 2025 | Henry + Claude | Added Darnel feedback, strategic action framework |

---

## Appendix C: Related Documents

- `JOB_FIT_ANALYSIS_AUDIT.md` - Comprehensive bug analysis
- `BACKEND_AUDIT_REQUEST.md` - What to check in deployed code
- `BACKEND_AUDIT_RESULTS.md` - Audit findings (TBD from Claude Code)
- `PRODUCT_STRATEGY_ROADMAP.md` - Product roadmap context
- `IMPROVEMENTS_SUMMARY.md` - Recent improvements

---

**END OF SPECIFICATION**

**Next Steps**:
1. ✅ Send audit request to Claude Code
2. ⏳ Wait for `BACKEND_AUDIT_RESULTS.md`
3. ⏳ Review audit findings
4. ⏳ Update this spec based on actual deployed code
5. ⏳ Create implementation tickets
6. ⏳ Begin Phase 1 development

---
