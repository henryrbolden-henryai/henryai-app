# HenryHQ Quality Gates: Bug Report & Fix Specifications

**Date:** January 2, 2026  
**Testing Phase:** Pre-Launch QA  
**Test Suite:** 6 Synthetic Resumes vs. Braze Senior PM, Core Messaging  
**Status:** Critical fixes required before launch

---

## Executive Summary

Testing revealed that the Resume Level Analysis layer correctly detects signals, gaps, and blockers, but the Fit Analysis decision layer ignores these findings. The system has two disconnected components that need to be wired together.

**Pass Rate:** 1 of 6 (17%)

| Resume | Assertion | Result | Severity |
|--------|-----------|--------|----------|
| Rachel Patterson | Missing Scope | ❌ FAIL | Critical |
| James Whitfield | Function Mismatch (Operations → PM) | ⚠️ PARTIAL | Medium |
| Marcus Chen | Inflated Title | ❌ FAIL | Critical |
| Sarah Thompson | Metrics Without Consequence | ✅ PASS | - |
| Kevin Martinez | Keyword Stuffed | ❌ FAIL | High |
| Amanda Brooks | Generic Mid-Market | ⚠️ PARTIAL | Low |

**Note on James Whitfield:** Originally designed to test "Missing Ownership," but function mismatch (Operations → PM) was the dominant terminal state. Ownership gap was moot once mismatch fired. Decisioning was correct; messaging contradiction was the bug.

---

## Critical Architecture Bugs

### ARCH-001: Blocker Signals Not Propagating to Fit Analysis
**Severity:** Critical  
**Affected Tests:** Rachel Patterson

**Current Behavior:**
- Resume Level Analysis correctly detects missing scope, impact, ownership
- Fit Analysis ignores these blockers and scores on keywords/experience only
- No wiring between the two systems

**Expected Behavior:**
- When `missing_scope_signal`, `missing_impact_signal`, or `missing_ownership_signal` = TRUE
- Fit score capped at ≤50%
- Recommendation downgraded to "Conditional Apply" or lower
- Apply button disabled or demoted

**Fix Required:**
```
BEFORE Fit Analysis runs:
  IF scope_present = FALSE OR impact_present = FALSE OR ownership_present = FALSE:
    fit_score_cap = 50
    recommendation_cap = "Conditional Apply"
    apply_button = "disabled" OR "demoted"
    surface_blocker_notice = TRUE
```

---

### ARCH-002: Resume Level Analysis Output Not Consumed by Fit Analysis
**Severity:** Critical  
**Affected Tests:** Rachel Patterson, James Whitfield, Kevin Martinez

**Current Behavior:**
- Resume Level Analysis outputs: detected_level, gap_classification, red_flags, signal_counts
- Fit Analysis does not consume any of these outputs
- Two systems operate independently

**Expected Behavior:**
- Fit Analysis must consume Resume Level Analysis outputs
- Detected level caps fit score if 2+ levels below target
- Gap classification (presentation vs experience) drives recommendation
- Red flags downgrade recommendation if high severity

**Fix Required:**
```
Fit Analysis Input:
  - detected_level (from Resume Level)
  - gap_classification (from Resume Level)
  - red_flag_count (from Resume Level)
  - red_flag_severity (from Resume Level)
  - signal_counts (from Resume Level)

Decision Logic (caps are HARD, penalties are TUNABLE):

  // HARD CAPS (non-negotiable)
  IF detected_level < target_level - 2:
    recommendation_cap = "Long Shot"  // HARD
  
  // TUNABLE PENALTIES (parameterize these)
  IF gap_classification = "EXPERIENCE_GAP":
    fit_score_penalty = CONFIG.experience_gap_penalty  // default: -20
  
  IF red_flag_severity = "HIGH" AND red_flag_count >= CONFIG.red_flag_threshold:
    recommendation_downgrade = TRUE

// The recommendation state matters more than exact score.
// A 47% and 52% should behave identically if both map to "Conditional Apply."
```

---

### ARCH-003: Scope Signal Detector Over-Counting Activity Nouns
**Severity:** Medium  
**Affected Tests:** Rachel Patterson, Marcus Chen, Amanda Brooks

**Current Behavior:**
- "Core platform," "quarterly roadmap planning," "cross-functional teams" counted as scope signals
- Titles like "Head of Engineering," "Director" counted as scope
- Any activity noun parsed as scope evidence

**Expected Behavior:**
- Scope requires at least ONE of:
  - Quantified scale metric (team size, budget, user volume, revenue, geography)
  - Clear ownership of a bounded system with complexity markers
- Activity nouns alone do NOT count as scope
- Titles alone do NOT count as scope

**Fix Required:**
```
scope_signal_valid = FALSE

FOR each scope_candidate:
  // Option 1: Quantified scale
  IF contains(team_size_pattern) OR
     contains(budget_pattern) OR
     contains(user_volume_pattern) OR
     contains(revenue_pattern) OR
     contains(geography_pattern):
    scope_signal_valid = TRUE
  
  // Option 2: Bounded system ownership (for senior ICs, early-stage)
  IF contains(system_ownership_pattern) AND contains(complexity_marker):
    // e.g., "Owned the recommendation engine" + "serving 10M requests/day"
    // e.g., "Built the payments infrastructure" + "processing $X"
    scope_signal_valid = TRUE

IF scope_signal_valid = FALSE:
  scope_signals = 0
  missing_scope_blocker = TRUE
```

**Note:** This allows senior ICs at early-stage companies who own bounded systems but may not have traditional scale metrics. The key is ownership + complexity, not just activity.

---

### ARCH-005: Terminal Decision State Not Collapsing Downstream Components
**Severity:** High  
**Affected Tests:** James Whitfield, Kevin Martinez

**Current Behavior:**
- Fit Analysis says "Do Not Apply" (correct)
- Resume Level Analysis still says "Your resume supports Senior PM roles" (contradicts)
- Coaching modules still render in "improvement mode"

**Expected Behavior:**
- Once `FUNCTION_MISMATCH = TRUE` or `PM_EXPERIENCE = 0`:
  - Resume Level switches to diagnostic-only mode
  - "Supports [target role]" language forbidden
  - No "quick wins" framed as near-term fixes
  - Coaching shifts to redirection, not optimization

**Fix Required:**
```
IF fit_recommendation = "Do Not Apply" OR function_mismatch = TRUE:
  resume_level_mode = "DIAGNOSTIC"
  forbidden_phrases = [
    "supports [target role]",
    "you have the foundation",
    "you're close",
    "stretch role with addressable gaps"
  ]
  coaching_mode = "REDIRECTION"
  quick_win_mode = "DISABLED"
```

---

### ARCH-007: Title Inflation Treated as Presentation Gap
**Severity:** Critical  
**Affected Tests:** Marcus Chen

**Current Behavior:**
- Head of Engineering doing IC tasks → treated as "presentation gap"
- System assumes "senior but wrote poorly"
- Coaching says "you're probably operating at Senior+ level"
- Apply button enabled

**Expected Behavior:**
- Title inflation = credibility violation, not presentation gap
- Blocker status, not coaching opportunity
- Harsher treatment than honest function mismatch

**Fix Required:**
```
IF title_inflation_detected = TRUE:
  recommendation = "Do Not Apply"
  apply_button = "DISABLED"
  coaching_mode = "CREDIBILITY_REPAIR"
  
  forbidden_phrases = [
    "you're actually senior",
    "you likely have this",
    "presentation gap",
    "make it visible on your resume"
  ]
  
  required_phrases = [
    "title not supported by evidence",
    "credibility risk",
    "content does not match claimed level"
  ]
```

---

### ARCH-008: Signals Engine Rewards Inflated Titles
**Severity:** Critical  
**Affected Tests:** Marcus Chen

**Current Behavior:**
- "Head of Engineering" counted as leadership signal
- "Director of Software Development" counted as scope signal
- No penalty for mismatch between title and evidence

**Expected Behavior:**
- Titles alone do not count as signals
- Signal must be backed by evidence (actions, outcomes, scale)
- Mismatch between title and content triggers `title_inflation_detected`

**Fix Required:**
```
FOR each title_signal:
  evidence_found = search_bullets_for_supporting_evidence(title_signal)
  
  IF evidence_found = FALSE:
    signal_count -= 1
    title_inflation_flag = TRUE

IF title_inflation_flag = TRUE AND title_level >= "Director":
  title_inflation_detected = TRUE
  blocker = TRUE
```

---

### ARCH-009: Inflated Resumes Get Softer Treatment Than Honest Mismatches
**Severity:** Critical  
**Affected Tests:** Marcus Chen vs James Whitfield

**Current Behavior:**
- James (honest mismatch): 15%, Do Not Apply, disabled button
- Marcus (inflated): 25%, Long Shot, enabled button
- System punishes honesty, rewards inflation

**Expected Behavior:**
- Inflated resumes treated MORE harshly than honest mismatches
- Credibility violation > function mismatch in severity

**Fix Required:**
```
severity_ranking = {
  "title_inflation": 1,      // Most severe
  "experience_fabrication": 1,
  "function_mismatch": 2,
  "experience_gap": 3,
  "presentation_gap": 4      // Least severe
}

IF title_inflation_detected:
  fit_score_cap = 20
  recommendation = "Do Not Apply"
```

---

### ARCH-012: Keyword Stuffing Not Detected
**Severity:** High  
**Affected Tests:** Kevin Martinez

**Current Behavior:**
- Buzzword lists counted as "Technical Signals"
- "Technical depth (5 found)" = positive framing
- No `keyword_stuffing_detected` warning

**Expected Behavior:**
- Keywords without applied context flagged as stuffing
- Density threshold triggers warning
- "Skills checklist" pattern identified and penalized

**Fix Required:**
```
keyword_density = count(technical_keywords) / total_bullet_count

IF keyword_density > 0.4:
  keyword_stuffing_detected = TRUE
  
FOR each keyword:
  context_found = search_for_applied_context(keyword)
  // Applied context = project, outcome, or scenario
  
  IF context_found = FALSE:
    uncontextualized_keywords += 1

IF uncontextualized_keywords > 5:
  keyword_stuffing_detected = TRUE
  technical_signal_penalty = -50%
```

---

### ARCH-013: Mid-Market Phrase Detection is Shallow
**Severity:** High  
**Affected Tests:** Amanda Brooks

**Current Behavior:**
- Only 4 red flags caught when resume contains 10+
- Generic pattern detected but specific phrases not itemized

**Expected Behavior:**
- Red Flag Language Lint catches specific mid-market phrases
- Each flagged phrase displayed to user
- Lint runs before any generation

**Fix Required:**
Implement Red Flag Language Lint per `RED_FLAG_LANGUAGE_LINT.md` spec:

```
mid_market_phrases = [
  "managed multiple projects",
  "cross-functional teams",
  "stakeholders at all levels",
  "proven track record",
  "results-driven",
  "self-starter",
  "team player",
  "excellent communication skills",
  "detail-oriented",
  "fast-paced environment"
]

FOR each phrase in mid_market_phrases:
  IF resume_contains(phrase):
    red_flags.append({
      "phrase": phrase,
      "severity": "MEDIUM",
      "suggestion": get_replacement_guidance(phrase)
    })
```

---

### ARCH-014: Leadership Signals Counting Generic Words
**Severity:** Medium  
**Affected Tests:** Amanda Brooks

**Current Behavior:**
- "Leadership" (word alone) counted as leadership signal
- "Team Collaboration" counted as leadership signal
- No evidence validation

**Expected Behavior:**
- Leadership signals require evidence of influence
- Generic words alone do not count

**Fix Required:**
```
leadership_evidence_patterns = [
  "led [team of X]",
  "managed [X] direct reports",
  "mentored",
  "drove initiative",
  "established process",
  "built team from"
]

FOR each leadership_candidate:
  IF NOT matches_any(leadership_evidence_patterns):
    leadership_signals -= 1
```

---

## UX Fixes Required

*All UX fixes are enforced by the Terminal State Contract. These are not independent tickets.*

### UX-001: Move Gaps Section Higher
**Severity:** Medium  
**Enforced By:** All terminal states

**Current:** Gaps buried below strengths, market context, coaching modules  
**Required:** Gaps appear immediately after recommendation, before any "How to Win" content

**Contract Reference:** Terminal states require gaps to be visible before any coaching content renders.

---

### UX-002: Remove "I've done the heavy lifting" on Rejections
**Severity:** Medium  
**Enforced By:** `FUNCTION_MISMATCH`, `TITLE_INFLATION`, `CREDIBILITY_VIOLATION`

**Current:** Coachy copy appears even on Do Not Apply / Long Shot  
**Required:** Copy adapts to recommendation tier

```
IF terminal_state IN ["CREDIBILITY_VIOLATION", "FUNCTION_MISMATCH", "TITLE_INFLATION"]:
  cta_copy = "This role is not the right fit. Here's why."
ELSE:
  cta_copy = "I've done the heavy lifting..."
```

**Contract Reference:** Terminal states with `coaching_mode = REDIRECTION` forbid optimization-framed copy.

---

### UX-003: Apply Button State Must Match Recommendation
**Severity:** Medium  
**Enforced By:** Terminal State Contract `apply_button` field

**Current:** Apply button enabled on Long Shot + function mismatch  
**Required:**

```
// Enforced by Terminal State Contract
IF terminal_state.apply_button = "DISABLED":
  button = DISABLED
  button_label = "Not eligible for this role"
  
IF terminal_state.apply_button = "DEMOTED":
  button = SECONDARY (gray)
  button_label = "Proceed Anyway"
  
IF terminal_state.apply_button = "ENABLED_WITH_WARNING":
  button = ENABLED
  warning_banner = VISIBLE
```

**Contract Reference:** Button state is not a UX decision. It is determined by terminal state.

---

## Domain Translation Guardrail

### ARCH-004: "Translates well to X" Generated Without Validation
**Severity:** Medium  
**Affected Tests:** Rachel Patterson

**Current Behavior:**
- "Your B2B product experience translates well to messaging infrastructure"
- Generated with zero domain overlap evidence

**Required Fix:**
```
BEFORE generating "translates well to X":
  domain_overlap = check_domain_overlap(candidate_domains, target_domain)
  adjacent_system = check_adjacent_system_ownership(candidate_experience)
  
  IF domain_overlap = FALSE AND adjacent_system = FALSE:
    translation_claim = FORBIDDEN
```

---

## Implementation Priority

### P0 (Block Launch)
1. ARCH-001: Wire blocker signals to Fit Analysis
2. ARCH-002: Wire Resume Level Analysis → Fit Analysis
3. ARCH-007: Title inflation as blocker, not presentation gap
4. ARCH-008: Evidence validation for title-based signals
5. ARCH-009: Severity hierarchy (inflation > honest mismatch)

### P1 (Launch Week)
6. ARCH-005: Terminal state collapses downstream messaging
7. ARCH-003: Scope signal redefinition
8. ARCH-012: Keyword stuffing detection
9. UX-001: Move gaps section up
10. UX-002: Remove coachy copy on rejections
11. UX-003: Apply button state consistency

### P2 (Post-Launch)
12. ARCH-004: Domain translation guardrail
13. ARCH-013: Deep mid-market phrase lint
14. ARCH-014: Leadership signal evidence validation

---

## Terminal State Contract (New Specification)

To prevent future failures of this class, implement a Terminal State Contract that enforces decision hierarchy:

```
TERMINAL_STATES = {
  "FUNCTION_MISMATCH": {
    "fit_score_cap": 25,
    "recommendation": "Do Not Apply" OR "Long Shot",
    "apply_button": "DISABLED" OR "DEMOTED",
    "coaching_mode": "REDIRECTION",
    "forbidden_messaging": ["supports [target role]", "you have the foundation"]
  },
  
  "TITLE_INFLATION": {
    "fit_score_cap": 20,
    "recommendation": "Do Not Apply",
    "apply_button": "DISABLED",
    "coaching_mode": "CREDIBILITY_REPAIR",
    "forbidden_messaging": ["you're actually senior", "presentation gap"]
  },
  
  "MISSING_CORE_SIGNAL": {
    "fit_score_cap": 50,
    "recommendation_cap": "Conditional Apply",
    "apply_button": "ENABLED_WITH_WARNING",
    "coaching_mode": "SIGNAL_BUILDING",
    "required_messaging": ["Missing [signal]. Address before applying."]
  }
}

ENFORCEMENT:
  1. Detect terminal state
  2. Apply all constraints from contract
  3. Collapse downstream components to match
  4. Validate no contradictory messaging
```

---

## Decision Authority Order

When multiple conditions apply, the highest-authority condition controls ALL downstream behavior. Lower conditions do not soften or override higher ones.

```
DECISION AUTHORITY ORDER (highest to lowest):

1. CREDIBILITY VIOLATIONS
   - Title inflation
   - Experience fabrication
   - Metrics fabrication
   → Result: Hard block. No Apply path. Credibility repair mode.

2. ELIGIBILITY VIOLATIONS  
   - Missing required credentials (license, clearance, certification)
   - Explicit disqualifiers in JD
   → Result: Hard block. No Apply path. Redirection mode.

3. FUNCTION MISMATCH
   - Engineering → PM
   - Marketing → PM
   - Operations → PM
   → Result: Do Not Apply or Long Shot. Disabled/demoted button. Redirection mode.

4. EXPERIENCE GAPS
   - Zero years in target function
   - 2+ levels below target
   → Result: Long Shot or Conditional Apply. Warning messaging.

5. PRESENTATION GAPS
   - Missing signals that likely exist
   - Weak language for actual level
   - Quantification missing
   → Result: Apply with coaching. Quick wins enabled.

6. OPTIMIZATION COACHING
   - Resume is competitive, can be stronger
   → Result: Apply. Full generation. Improvement suggestions.
```

**Rule:** Once a higher-authority condition fires, no lower-authority condition can upgrade the recommendation, enable the Apply button, or generate optimistic messaging.

---

## Validation Checklist (Post-Fix)

After implementing fixes, re-run all 6 test resumes and verify:

- [ ] Rachel Patterson: Fit ≤50%, Conditional Apply or lower, blocker surfaced
- [ ] James Whitfield: No "supports Senior PM" messaging after Do Not Apply
- [ ] Marcus Chen: Do Not Apply, disabled button, credibility language
- [ ] Sarah Thompson: No change (already passing)
- [ ] Kevin Martinez: Keyword stuffing flagged (even with function mismatch)
- [ ] Amanda Brooks: 10+ red flag phrases itemized

---

## Files Referenced

- `RESUME_COVER_LETTER_CUSTOMIZATION_SPEC.md` (in /mnt/user-data/outputs/)
- `RED_FLAG_LANGUAGE_LINT.md` (in /mnt/user-data/outputs/)
- `RESUME_QUALITY_GATES.md` (in /mnt/user-data/outputs/)

---

**Report Prepared By:** Claude (via HenryHQ QA Session)  
**Reviewed By:** Henry, ChatGPT  
**Next Step:** Claude Code implementation of P0 fixes
