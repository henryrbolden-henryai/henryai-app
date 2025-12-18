# Backend Audit Results

**Date**: December 18, 2025
**File**: backend/backend.py
**Total Lines**: 11,578

---

## Executive Summary

- ✅ `calculate_role_specific_years()` - Exists with full role support (PM, engineering, recruiting, sales, marketing, design, ops, general)
- ✅ `detect_role_type_from_jd()` - Exists and routes to correct calculator
- ✅ `force_apply_experience_penalties()` - Exists and uses role detection
- ✅ `apply_credibility_adjustment()` - Exists for startup/short-tenure detection
- ✅ `validate_recommendation_consistency()` - Exists for contradiction fixing
- ✅ **Strategic Action Coaching Framework** - FULLY IMPLEMENTED with score-band-specific guidance
- ✅ **Second-Person Voice Enforcement** - FULLY IMPLEMENTED throughout system prompt
- ❌ `calculate_pm_years_from_resume()` - NOT FOUND (replaced by `calculate_role_specific_years`)
- ❌ `calculate_recruiting_years()` - NOT FOUND (merged into `calculate_role_specific_years`)
- ❌ `calculate_domain_years_from_resume()` - NOT FOUND (replaced by `detect_role_type_from_jd` + `calculate_role_specific_years`)
- ❌ `get_recommendation_from_score()` - NOT FOUND (logic embedded in `force_apply_experience_penalties`)

---

## Detailed Findings

### 1. Experience Calculation Functions

#### Function: `calculate_role_specific_years()`

**Location**: Lines 3167-3259 in backend.py

**Patterns Matched**:
```python
role_patterns = {
    "pm": [
        "product manager", "product lead", "product owner", "pm",
        "product director", "head of product", "vp product", "cpo",
        "associate product manager", "senior product manager", "staff product",
        "principal product", "group product manager", "technical pm"
    ],
    "engineering": [
        "engineer", "developer", "swe", "software", "programmer",
        "cto", "tech lead", "architect", "devops"
    ],
    "design": [
        "designer", "ux", "ui", "product design", "design lead",
        "head of design", "creative director"
    ],
    "ops": [
        "operations", "ops manager", "chief operating", "coo",
        "business operations", "strategy & ops"
    ],
    "recruiting": [
        "recruit", "talent acquisition", "ta director", "ta manager",
        "sourcer", "sourcing", "headhunter", "talent partner",
        "talent coordinator", "recruiting operations", "recruiting manager",
        "technical recruiter", "executive recruiter", "hr generalist",
        "talent lead", "head of talent", "vp talent", "people operations"
    ],
    "sales": [
        "sales", "account executive", "account manager", "business development",
        "bd", "revenue", "sales engineer", "sales operations", "sales manager",
        "enterprise sales", "smb sales", "strategic accounts", "ae", "sdr",
        "bdr", "sales director", "vp sales", "chief revenue"
    ],
    "marketing": [
        "marketing", "growth", "brand", "content", "digital marketing",
        "product marketing", "demand gen", "campaigns", "seo", "sem",
        "social media", "community", "communications", "pr", "cmo",
        "marketing manager", "head of marketing", "vp marketing"
    ],
    "general": []  # Empty list means match ALL roles (fallback)
}
```

**Logic**:
- Iterates through resume experience entries
- Checks if job title contains any pattern for the target role type
- Parses date ranges to calculate years using `parse_experience_duration()`
- For "general" type, counts ALL professional experience
- Returns total years as float

**Called By**:
- `force_apply_experience_penalties()` at line 2865

---

#### Function: `detect_role_type_from_jd()`

**Location**: Lines 3262-3340 in backend.py

**Detection Patterns** (in priority order):
```python
# 1. Recruiting (checked FIRST to catch "Technical Recruiter")
["recruit", "talent acquisition", "sourcer", "headhunter",
 "ta director", "ta manager", "talent partner", "head of talent"]

# 2. Product Management
["product manager", "product lead", "product owner", "head of product",
 "vp product", "cpo", "group pm", "technical pm"]

# 3. Engineering
["software engineer", "developer", "swe", "technical lead",
 "architect", "devops", "backend", "frontend", "full stack"]

# 4. Sales
["sales", "account executive", "business development", "revenue",
 "account manager", "enterprise", "sdr", "bdr"]

# 5. Marketing
["marketing", "growth", "brand manager", "demand gen",
 "product marketing", "content", "cmo"]

# 6. Design
["designer", "ux", "ui", "product design", "design lead"]

# 7. Operations
["operations", "ops manager", "coo", "chief operating"]

# 8. Fallback: "general" (counts all experience)
```

**Logic**:
- Combines role_title + job_description + intelligence_layer.role_summary
- Checks patterns in priority order (recruiting first to avoid misclassifying "Technical Recruiter" as engineering)
- Returns role type string

**Called By**:
- `force_apply_experience_penalties()` at line 2861

---

#### Function: `calculate_pm_years_from_resume()`
**Status**: ❌ NOT FOUND (functionality merged into `calculate_role_specific_years`)

#### Function: `calculate_recruiting_years()`
**Status**: ❌ NOT FOUND (functionality merged into `calculate_role_specific_years`)

#### Function: `calculate_engineering_years()`
**Status**: ❌ NOT FOUND (functionality merged into `calculate_role_specific_years`)

#### Function: `calculate_sales_years()`
**Status**: ❌ NOT FOUND (functionality merged into `calculate_role_specific_years`)

#### Function: `calculate_marketing_years()`
**Status**: ❌ NOT FOUND (functionality merged into `calculate_role_specific_years`)

#### Function: `calculate_domain_years_from_resume()`
**Status**: ❌ NOT FOUND (replaced by `detect_role_type_from_jd` + `calculate_role_specific_years`)

#### Function: `calculate_total_years()`
**Status**: ❌ NOT FOUND (functionality exists as "general" type in `calculate_role_specific_years`)

---

### 2. Backend Safety Net Function

#### Function: `force_apply_experience_penalties()`

**Location**: Lines 2822-3076 in backend.py

**Hard Cap Logic** (Lines 2893-2904):
```python
if years_percentage < 50:
    hard_cap = 45
    hard_cap_reason = f"Candidate has {years_percentage:.1f}% of required years..."
elif years_percentage < 70:
    hard_cap = 50
    hard_cap_reason = f"Candidate has {years_percentage:.1f}% of required years..."
elif years_percentage < 90:
    hard_cap = 55
    hard_cap_reason = f"Candidate has {years_percentage:.1f}% of required years..."
else:
    hard_cap = 100  # No cap for candidates with 90%+ of required years
    hard_cap_reason = None
```

**Hard Cap Summary Table**:
| Years % of Required | Hard Cap |
|---------------------|----------|
| < 50% | 45% |
| 50-69% | 50% |
| 70-89% | 55% |
| 90%+ | No cap (100%) |

**Which experience calculator does it call?**:
1. First calls `detect_role_type_from_jd(response_data)` at line 2861
2. Then calls `calculate_role_specific_years(resume_data, detected_role_type)` at line 2865

**Override Logic** (lines 2868-2879):
```python
# If Claude didn't count role-specific experience OR significantly overcounted, use ours
if candidate_years == 0 or (candidate_years > 3 and backend_role_years < candidate_years * 0.5):
    candidate_years = backend_role_years
    experience_analysis["backend_override"] = True
    experience_analysis["detected_role_type"] = detected_role_type
```

**Does it apply company credibility adjustments?**:
- Yes, at line 2852: `candidate_years = apply_credibility_adjustment(resume_data, raw_years)`
- Only applied if Claude didn't already do it

---

### 3. Credibility Adjustment Function

#### Function: `apply_credibility_adjustment()`

**Location**: Lines 3402-3447 in backend.py

**Red Flags Detected**:
```python
# 1. Short tenure signals
if "month" in dates.lower() or "1 year" in dates.lower():
    red_flags += 1

# 2. Startup signals in company name
startup_signals = ["seed", "stealth", "startup", "pre-seed", "founding"]
if any(signal in company.lower() for signal in startup_signals):
    red_flags += 1
```

**Multipliers Applied**:
```python
if red_flags >= 2:
    return raw_years * 0.3   # LOW credibility
elif red_flags == 1:
    return raw_years * 0.7   # MEDIUM credibility
else:
    return raw_years         # No adjustment
```

---

### 4. Recommendation Mapping

**Location**: Lines 2923-2961 in `force_apply_experience_penalties()`

**Note**: There is NO separate `get_recommendation_from_score()` function. The logic is embedded directly.

**6-Tier Recommendation Thresholds**:
```python
if capped_score < 50:
    correct_recommendation = "Do Not Apply"
elif capped_score < 60:
    correct_recommendation = "Do Not Apply"
elif capped_score < 70:
    correct_recommendation = "Apply with Caution"
elif capped_score < 80:
    correct_recommendation = "Conditional Apply"
elif capped_score < 90:
    correct_recommendation = "Apply"
else:
    correct_recommendation = "Strongly Apply"
```

**Summary Table**:
| Score Range | Recommendation |
|-------------|----------------|
| 0-49% | Do Not Apply |
| 50-59% | Do Not Apply |
| 60-69% | Apply with Caution |
| 70-79% | Conditional Apply |
| 80-89% | Apply |
| 90-100% | Strongly Apply |

---

### 5. Main Analysis Endpoint

#### Endpoint: POST `/api/jd/analyze`

**Location**: Lines 3450-4893 in backend.py

**Flow**:
1. ✅ Calls Claude API directly with system prompt (lines 3465-4800+)
2. ✅ Applies backend penalties after Claude at line 4830 and 4892
3. ✅ Uses `force_apply_experience_penalties(parsed_data, request.resume)`

**System Prompt Features**:
- ✅ Mentions experience penalties (lines 3495, 4952)
- ✅ Mentions credibility adjustments
- ✅ Contains "CRITICAL RULES" and "HARD CAPS" instructions
- ✅ Has strategic_action formatting rules (see Section 7 below)
- ✅ Enforces second-person tone (see Section 8 below)

**Call Sites for `force_apply_experience_penalties()`**:
- Line 4830: Main response processing
- Line 4892: Error recovery path
- Line 5136: Streaming endpoint

---

### 6. Consistency Validation Function

#### Function: `validate_recommendation_consistency()`

**Location**: Lines 3079-3164 in backend.py

**Purpose**: Fixes contradictions where Claude says "Do Not Apply" but uses language like "strong fit"

**Called By**: `force_apply_experience_penalties()` at line 3074

**Contradiction Detection**:
```python
skip_signals = ["skip", "do not apply", "not recommended", "pass on this"]
apply_signals = ["strong fit", "strong match", "excellent match", "good fit", "great fit",
                 "well-positioned", "competitive", "prioritize this", "apply immediately"]
```

**Second-Person Voice Enforcement** (Lines 3109, 3120):
- Comments explicitly state: `# CRITICAL: Do NOT use candidate names - use second-person voice only`
- Rewrites strategic_action to use "your background" not names

---

### 7. Strategic Action Coaching Framework

**Location**: Lines 4507-4677 in system prompt

**Status**: ✅ FULLY IMPLEMENTED

**Score Band Frameworks**:

#### BAND 1: 0-39% — DO NOT APPLY / LONG SHOT (Lines 4514-4551)
```
Structure: "[State what role requires]. [State candidate's background]. [Explain fundamental mismatch]."
YOUR MOVE: "Do not apply. [Direct decision]. [Redirect to appropriate roles]."
```

**Example** (Line 4534):
> "This role requires 5+ years of hands-on backend engineering experience. Your background is product management, not software engineering, making this a fundamental function mismatch."

#### BAND 2: 40-69% — CONDITIONAL APPLY / APPLY WITH CAUTION (Lines 4554-4608)
```
Structure: "Before applying, [specific positioning changes]. [Proof points to lead with]. Once positioned, [timing + outreach strategy]."
```

**Key Rule** (Line 4570):
> `DO start strategic_action with "Before applying" for this band`

**Example** (Line 4590):
> "Before applying, tighten your resume and outreach to address the gaps directly. Lead with your consumer product work at 2.3M user scale..."

#### BAND 3: 70-84% — APPLY (Lines 4611-4637)

**70-79% Sub-band** (Lines 4626-4632):
```
CRITICAL: ALWAYS lead with "Before applying..." (positioning requirements)
NEVER say "Apply immediately" without conditions
Structure: Fix → Position → Apply → Outreach
```

**Example** (Line 4626):
> "Before applying, adjust your resume and outreach to address your positioning gaps. Frame your Ripple work to emphasize consumer fintech payments..."

**80-84% Sub-band** (Line 4634-4635):
```
CAN say "Apply immediately"
```

**Example** (Line 4635):
> "Apply immediately. Your Ripple consumer wallet experience is exactly what they need..."

#### BAND 4: 85-100% — STRONGLY APPLY (Lines 4640-4660)
```
Structure: "[Decision: This is a priority target]. [Why this is near-ideal alignment]. [Exact achievements/metrics to lead with]. [Who to engage]. [Timeline: apply today]."
```

**Example** (Line 4655):
> "This is a priority target. Your Ripple consumer wallet background, mobile product expertise, and experimentation framework map 1:1 to what they're looking for..."

**One-Line Summary (North Star)** - Lines 4666-4669:
```
- 0-39% → "Don't apply. Here's where you win instead."
- 40-69% → "Viable if you fix [X]. Here's how."
- 70-84% → "Apply. Here's how you stand out."
- 85-100% → "This is a priority. Execute precisely."
```

---

### 8. Second-Person Voice Enforcement

**Location**: Lines 3472-3500 and 4929-4957 in system prompt (appears twice)

**Status**: ✅ FULLY IMPLEMENTED

**Mandatory Rules** (Lines 3472-3478):
```
MANDATORY SECOND-PERSON VOICE (APPLIES TO ALL SCORE BANDS):
- ALL explanations, recommendations, and strategic advice MUST use second-person voice
- Use "your background" NOT "Maya's background" or "the candidate's background"

🚫 NEVER USE CANDIDATE NAMES IN STRATEGIC_ACTION 🚫
- NEVER start strategic_action with the candidate's name ("Maya, this role...")
- NEVER use names anywhere in strategic_action field
- START strategic_action with the action/situation: "This role...", "Do not apply...", "Apply immediately...", "Before applying..."
```

**Correct Examples** (Lines 3483-3488):
```
✅ "This role requires 5+ years of backend development. Your background is product management, not engineering."
✅ "Before applying, tighten your resume to address the gaps directly."
```

**Incorrect Examples** (Lines 3489-3495):
```
❌ "Maya, this role requires..." (starts with name)
❌ "The candidate's background..." (third person)
```

**Fields Requiring Second Person** (Line 3500):
> This applies to ALL messaging fields: strategic_action, recommendation_rationale, gaps array descriptions, strengths array, positioning_strategy, mitigation_strategy, apply_decision.reasoning.

---

## Critical Issues Found

### ✅ No Critical Issues

The job fit scoring system is now properly implemented with:

1. **Role Detection**: `detect_role_type_from_jd()` correctly identifies role type
2. **Pattern Matching**: `calculate_role_specific_years()` has patterns for all major role types
3. **Fallback**: "general" type counts all experience when role type can't be detected
4. **Backend Override**: System uses backend calculation when Claude reports 0 years
5. **Strategic Action Framework**: Score-band-specific coaching guidance fully implemented
6. **Second-Person Voice**: Enforced throughout system prompt and validated by `validate_recommendation_consistency()`

---

## Key Questions Answered

### 1. Does `calculate_pm_years_from_resume()` exist?
**NO** - Replaced by `calculate_role_specific_years()` which handles PM and all other role types.

### 2. Are there role-specific calculators for recruiting, engineering, sales, marketing?
**YES** - All merged into `calculate_role_specific_years()` with patterns for each role type.

### 3. What experience calculator does `force_apply_experience_penalties()` call?
- First calls `detect_role_type_from_jd()` (line 2861)
- Then calls `calculate_role_specific_years(resume_data, detected_role_type)` (line 2865)

### 4. What are the EXACT hard cap thresholds?
| Years % | Hard Cap |
|---------|----------|
| <50% | 45% |
| 50-69% | 50% |
| 70-89% | 55% |
| 90%+ | 100% (no cap) |

### 5. What are the EXACT recommendation thresholds?
| Score | Recommendation |
|-------|----------------|
| 90-100% | Strongly Apply |
| 80-89% | Apply |
| 70-79% | Conditional Apply |
| 60-69% | Apply with Caution |
| 50-59% | Do Not Apply |
| 0-49% | Do Not Apply |

### 6. Is company credibility scoring implemented?
- **In Python function?** YES - `apply_credibility_adjustment()` at lines 3402-3447
- **In system prompt?** YES - Referenced in credibility adjustment sections

### 7. What are the strategic_action formatting rules?
**FULLY DOCUMENTED** - See Section 7 above. Key points:
- ✅ Score-band-specific frameworks exist (lines 4507-4677)
- ✅ "Before applying" required for 40-79% scores (lines 4570, 4629)
- ✅ Second-person voice enforced (lines 3472-3500, 4929-4957)
- ✅ Different guidance for 70-79% vs 80-84% (lines 4626-4635)

### 8. Are there any surprise functions?
**YES** - `validate_recommendation_consistency()` at lines 3079-3164 which fixes contradiction between "Do Not Apply" recommendation and "strong fit" language.

---

## Testing Notes

**For Jordan's Recruiting Case**:
- Resume with 12 years recruiting experience
- JD: Director of Technical Recruiting
- Expected detection: `🎯 Detected RECRUITING role from JD`
- Expected calculation: `Backend recruiting years calculation: 12.0 years`
- Expected hard cap: None (12/7 years = 171%, exceeds 90%)
- Expected recommendation: "Apply" or "Strongly Apply"

**Log Output to Expect**:
```
🎯 Detected RECRUITING role from JD
🔍 Detected role type: RECRUITING
🔍 Backend recruiting years calculation: 12.0 years
✅ Using backend calculation (Claude reported 0): 12.0 years
```

---

## Appendix: Mock Interview Scoring (Separate System)

**Note**: The following functions are for **mock interview behavioral scoring**, NOT job fit analysis:

### Function: `calculate_weighted_score()`

**Location**: Lines 1332-1344 in backend.py

**Purpose**: Calculates weighted behavioral signal scores during mock interview analysis

**Signal Weights by Role** (Lines 1250-1329):
| Role Type | Top Weighted Signals |
|-----------|---------------------|
| product_manager | functional_competency (15%), strategic_thinking (15%), metrics_orientation (10%) |
| software_engineer | functional_competency (20%), ownership (15%), problem_solving (15%) |
| ux_designer | collaboration (15%), user_centricity (15%), functional_competency (15%) |
| talent_acquisition | collaboration (15%), functional_competency (15%), metrics_orientation (10%) |
| general_leadership | leadership (15%), strategic_thinking (15%), functional_competency (15%) |

**All 11 Behavioral Signals Tracked**:
- functional_competency
- leadership
- collaboration
- ownership
- strategic_thinking
- problem_solving
- communication_clarity
- metrics_orientation
- stakeholder_management
- executive_presence
- user_centricity

**This is NOT part of job fit scoring** - it's used for mock interview debrief analysis.

---

## Code Verification Complete

The backend now correctly:
1. Detects role type from job descriptions
2. Calculates role-specific experience (not just PM)
3. Applies appropriate hard caps based on experience %
4. Maps scores to 6-tier recommendations
5. Overrides Claude when it miscounts experience
6. Enforces strategic_action coaching framework by score band
7. Enforces second-person voice throughout messaging

### Summary: Two Distinct Scoring Systems

| System | Purpose | Key Functions |
|--------|---------|---------------|
| **Job Fit Scoring** | Analyze resume vs JD compatibility | `force_apply_experience_penalties()`, `detect_role_type_from_jd()`, `calculate_role_specific_years()`, `apply_credibility_adjustment()`, `validate_recommendation_consistency()` |
| **Mock Interview Scoring** | Evaluate behavioral responses | `calculate_weighted_score()`, `calculate_mock_session_average()` |
