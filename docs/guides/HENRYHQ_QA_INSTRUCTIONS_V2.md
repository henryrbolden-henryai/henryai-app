# HenryHQ Systems QA Testing Instructions v2.0
## Single Source of Truth Architecture

**Core Principle:** Job Fit Scoring is the single source of truth. No other page may reinterpret, soften, or recompute fit decisions.

**Authority Statement:** HenryHQ is not here to encourage applications. It is here to tell the truth early, with evidence, and coach only when the gap is realistically bridgeable.

---

## RULE 1: DECISION OWNER (NON-NEGOTIABLE)

### Single Authority
**Job Fit Scoring** is the ONLY system allowed to decide:
- Apply / Apply with Caution / Do Not Apply recommendation
- Leadership sufficiency determination
- Experience sufficiency determination
- LEPE (Leadership Experience Penalty Enforcement) caps
- CAE (Credible Actual Experience) adjustments

### Downstream Consumption
All other pages (Resume Leveling, LinkedIn Analysis, Skills Analysis) must:
- **CONSUME** the Job Fit decision
- **NEVER** reinterpret, soften, or override
- **MIRROR** the locked recommendation

### Claude Code Hard Rule
```
IF Job Fit says "Do Not Apply" 
THEN downstream pages may explain WHY
BUT may NOT reframe it as viable

Violation example: Job Fit = "Do Not Apply" → LinkedIn says "Here's how to optimize for this role"
Correct behavior: Job Fit = "Do Not Apply" → LinkedIn says "Your profile is optimized for [other roles], not this one"
```

---

## RULE 2: ORDER OF OPERATIONS (FROZEN SEQUENCE)

### Execution Flow
This sequence is hardcoded. No deviations. No parallelization.

```
Step 1: Role Parsing
  ↓
Step 2: Experience + Leadership Eligibility Gates
  ↓
Step 3: CAE (Credibility Risk Assessment)
  ↓
Step 4: LEPE (Leadership Gap + Positioning Mode)
  ↓
Step 5: Final Recommendation Lock
  ↓
Step 6: Coaching Output Generation
```

### Claude Code Hard Rule
```
NO downstream logic may execute before Step 5 completes.

Example violation:
- LinkedIn optimization starting before recommendation is locked
- Resume Leveling running in parallel with Job Fit

Enforcement:
- Job Fit must write `recommendation_locked = true` before any other analysis runs
- Downstream pages must check for lock before proceeding
```

---

## RULE 3: MATH VS MESSAGING (STRICT SEPARATION)

### Scoring Logic Output
The scoring engine produces ONLY these fields:
```json
{
  "score": 45,
  "recommendation": "Do Not Apply",
  "locked_reason": "Critical experience gap: No direct safety product experience",
  "leadership_years_actual": 0,
  "leadership_years_required": 5,
  "experience_years_actual": 7,
  "experience_years_required": 7,
  "hard_requirement_failures": ["safety product experience"],
  "caps_applied": {
    "cae_multiplier": 1.0,
    "lepe_cap": null
  }
}
```

### Messaging Logic
Messaging functions render based ONLY on the above outputs. They:
- Format the score for display
- Generate explanatory text
- Create "Your Move" coaching

### Claude Code Hard Rule
```
Messaging functions CANNOT:
- Change scores
- Recompute caps
- Alter recommendations
- Remove locked_reason
- Soften hard_requirement_failures

Violation example:
```python
# WRONG - messaging changes logic
if score < 50:
    score = 50  # "give them a chance"
    
# CORRECT - messaging only formats
if score < 50:
    display_message = f"Your fit score is {score}%. This is below the threshold."
```
```

---

## RULE 4: LEADERSHIP YEARS (NON-NEGOTIABLE DEFINITION)

### Hard Definition
**Total experience ≠ Leadership experience**

Leadership tenure ONLY comes from:
- **Tier 2 People Leadership:** Directly managing individuals (1-on-1s, performance reviews, hiring/firing)
- **Tier 3 Org Leadership:** Managing managers, org-level strategy, budget ownership
- **Mixed-Scope Credit:** Already implemented (proportional counting)

### Exclusions (Never Count as Leadership)
```
EXCLUDED from leadership years:
- "Led cross-functional team" (project leadership, not people management)
- "Mentored junior engineers" (mentorship ≠ management)
- "Tech lead" (technical leadership, not people management)
- "Stakeholder management" (influencing, not managing)
- "Team collaboration" (working with peers, not managing reports)
```

### Claude Code Hard Rule
```
IF JD requires people leadership (e.g., "Engineering Manager", "Director of Product")
THEN only Tier 2+ leadership years count toward experience requirement

Example:
JD: "4+ years managing engineering teams"
Candidate: 9 years total, 5 years as tech lead, 3 years managing 12 engineers

Leadership years = 3 (only the people management period)
IC years MUST NEVER count toward this requirement
```

---

## RULE 5: FAIL LOUDLY (NO SOFT LANGUAGE)

### Required Transparency
When required experience or leadership is missing, the system MUST state:

1. **What's missing** (specific, not generic)
2. **How far off** (quantified gap)
3. **Terminal vs coachable** (honest assessment)

### Examples

**CORRECT - Fails loudly:**
```
"Sarah, do not apply. Critical experience gap identified.

Gap: You have 0 years of safety or trust & safety product experience. This role requires direct experience building products in this domain.

Distance: This is a 0→7 year gap. Not coachable in current job search timeline.

Your Move: Redirect to Product roles where your B2B SaaS experience directly applies (billing, payments, enterprise tools)."
```

**INCORRECT - Soft language:**
```
"While you have strong product management experience, this particular role might be challenging due to domain requirements. However, with some additional research into the safety space, you could potentially make a strong case."
```

### Claude Code Hard Rule
```
BANNED phrases in "Do Not Apply" messaging:
- "might be challenging"
- "potentially"
- "with some additional [X], you could..."
- "not a perfect fit, but..."
- "stretch opportunity"

REQUIRED components:
- Name the gap specifically
- Quantify the distance
- State terminal vs coachable
- Redirect clearly
```

---

## RULE 6: DOWNSTREAM PAGES = MIRRORS, NOT JUDGES

### Mandatory References
All downstream pages (Resume Leveling, LinkedIn Analysis, Skills Analysis) MUST:

1. **Reference `leadership_positioning_record`**
   - Show actual leadership years calculated
   - Show required leadership years from JD
   - Show gap if exists

2. **Reference `hard_requirement_failure`**
   - List any hard requirement failures verbatim
   - Do not soften or reinterpret

3. **Preserve `accountability_record`**
   - If candidate proceeds against "Do Not Apply" guidance
   - Log: `{"decision": "proceeded_despite_guidance", "timestamp": "...", "acknowledged": true}`

### Claude Code Hard Rule
```
Downstream pages display data. They do NOT recompute or reinterpret.

Example:
Job Fit output:
{
  "recommendation": "Do Not Apply",
  "locked_reason": "No safety product experience",
  "leadership_years_actual": 0,
  "leadership_years_required": 5
}

LinkedIn Analysis MUST display:
- "Your profile is optimized for B2B SaaS Product roles"
- "This role requires safety product experience, which you do not have"
- Reference to Job Fit decision

LinkedIn Analysis MUST NOT display:
- "Here's how to optimize your profile for this role"
- Suggestions to emphasize unrelated experience as if it bridges the gap
```

### Accountability Record
```
IF candidate clicks "Pass" on "Do Not Apply" screen
THEN downstream pages must show:
  "⚠️ Note: You chose to proceed despite HenryHQ's guidance. We recommend focusing energy on higher-fit roles."

This appears on:
- Resume Leveling page (top banner)
- LinkedIn Analysis page (top banner)  
- Document generation confirmation
```

---

## RULE 7: ONE TEST CASE = ONE EXPECTED OUTCOME

### Test Specification Format
For each test (candidate × job), define:

```yaml
test_id: sarah_chen_uber_senior_pm
candidate: Sarah Chen
job: Uber Senior PM, Safety Response & Intelligence

expected_outcome:
  score_range: [60, 75]
  recommendation: "Apply" OR "Apply with Caution"
  primary_gap: "No direct safety or trust & safety product experience"
  your_move_first_sentence: "Sarah, apply with strategic positioning."
  
validation:
  - score must fall within range
  - recommendation must exactly match
  - primary_gap must appear in gaps list
  - "Your Move" must start with expected sentence (verbatim)
```

### Failure Criteria
```
IF any field differs from expected:
  THEN test = FAIL
  AND log specific mismatch
  AND identify root cause (scoring logic, messaging, parsing)
```

### Claude Code Hard Rule
```
NO broad interpretation testing.
NO "close enough" evaluation.
NO manual overrides to force pass.

Example:
Expected: "Apply with Caution"
Actual: "Consider"

Result: FAIL (not "close enough")
Action: Fix recommendation logic in Job Fit scoring
```

---

## TEST EXECUTION PROTOCOL

### Phase 1: Setup
```bash
# Validate test environment
1. Confirm all 5 candidate resumes present
2. Confirm both JD files present
3. Load expected outcomes matrix (10 total: 5 candidates × 2 jobs)
```

### Phase 2: Run Tests
```python
for candidate in candidates:
    for job in jobs:
        # Execute Job Fit Scoring (single source of truth)
        result = run_job_fit_scoring(candidate, job)
        
        # Validate against expected outcome
        expected = get_expected_outcome(candidate, job)
        validation = validate_exact_match(result, expected)
        
        # Log result
        if validation.passed:
            log_pass(candidate, job, result)
        else:
            log_fail(candidate, job, result, validation.mismatches)
            
        # If passed, test downstream consistency
        if validation.passed:
            test_downstream_mirrors(candidate, job, result)
```

### Phase 3: Report
```markdown
## Test Results Summary
- Tests run: 10 (5 candidates × 2 jobs)
- Passed: X
- Failed: Y
- Pass rate: Z%

## Failed Tests
[For each failure]
- Candidate: [name]
- Job: [title]
- Expected: [outcome]
- Actual: [outcome]
- Mismatch: [specific field + values]
- Root cause: [scoring logic | messaging | parsing | downstream]
- Recommended fix: [specific code change]

## Critical Failures (Auto-Reject)
[Any of these = stop and fix immediately]
- Sarah Chen × Uber PM = "Do Not Apply" (should be Apply/Caution)
- Marcus Johnson leadership years = 0 or 9 (should be ~5)
- Jessica Martinez flagged for LEPE (should have no leadership requirements)
- David Park × APM = "Do Not Apply" without coaching (should be Caution with redirect)
- Aisha Williams score capped below 85% (should have no caps)

## Downstream Consistency Failures
[Tests where Job Fit passed but downstream pages contradicted]
- [Candidate × Job]: Job Fit = "Do Not Apply" but LinkedIn offered optimization
- [Candidate × Job]: Job Fit leadership years ≠ Resume Leveling leadership years
```

---

## EXPECTED OUTCOMES MATRIX

### Sarah Chen × Uber Senior PM
```yaml
score_range: [60, 75]
recommendation: "Apply" OR "Apply with Caution"
primary_gap: "No direct safety or trust & safety product experience"
secondary_gaps:
  - "Limited ML/AI product experience (preferred, not required)"
  - "No enterprise tooling for internal users (preferred, not required)"
your_move_first_sentence: "Sarah, apply with strategic positioning."
leadership_years_actual: 0
leadership_years_required: 0
hard_requirement_failures: []
rationale: "7 years PM at top companies, strong data skills, cross-functional leadership. Safety domain is gap but role doesn't hard-require it."
```

### Sarah Chen × Red Hat Engineering Manager
```yaml
score_range: [10, 20]
recommendation: "Do Not Apply"
primary_gap: "This role requires direct experience in core software engineering"
your_move_first_sentence: "Sarah, do not apply."
leadership_years_actual: 0
leadership_years_required: 4
hard_requirement_failures: ["software engineering experience", "people leadership"]
rationale: "Wrong function entirely. Product manager applying to engineering management role."
```

### Marcus Johnson × Red Hat Engineering Manager
```yaml
score_range: [40, 55]
recommendation: "Apply with Caution"
primary_gap: "Limited AWS-specific experience"
secondary_gaps:
  - "No direct OpenShift experience"
  - "No global team leadership (regional scope only)"
your_move_first_sentence: "Marcus, apply with caution."
leadership_years_actual: 5
leadership_years_required: 4
hard_requirement_failures: []
rationale: "Has manager experience (4.75 years, 12 reports) but tech stack gaps and scale gaps exist."
```

### Jessica Martinez × [Generic Senior Recruiter Role]
```yaml
score_range: [70, 85]
recommendation: "Apply"
primary_gap: "Targeting senior roles with 5 years experience (typically 7+ years preferred)"
your_move_first_sentence: "Jessica, apply."
leadership_years_actual: 0
leadership_years_required: 0
hard_requirement_failures: []
rationale: "Mid-level recruiter (5 years) applying to senior role. Experience is close enough. No leadership required."
```

### David Park × Uber Senior PM
```yaml
score_range: [35, 50]
recommendation: "Apply with Caution"
primary_gap: "Insufficient direct PM experience (3 months internship + consulting projects)"
secondary_gaps:
  - "No shipping product experience at scale"
  - "No direct PM reports or full product ownership"
your_move_first_sentence: "David, apply with caution."
leadership_years_actual: 0
leadership_years_required: 0
hard_requirement_failures: []
coaching_note: "Career switcher. Transferable skills exist (stakeholder mgmt, data analysis). Frame as growth opportunity."
rationale: "McKinsey consultant → APM pivot. Gap in direct PM years but transferable skills bridge some distance."
```

### Aisha Williams × [Generic VP Marketing Role]
```yaml
score_range: [85, 95]
recommendation: "Strong Apply"
primary_gap: null
your_move_first_sentence: "Aisha, strongly apply."
leadership_years_actual: 12
leadership_years_required: 10
hard_requirement_failures: []
caps_applied: null
rationale: "VP Marketing, 12+ years, teams of 35, $200M ARR scale. No caps, no skepticism."
```

---

## CRITICAL FAILURE CONDITIONS (AUTO-REJECT)

### Failure Mode 1: Strong Candidate False Negative
```
TEST: Sarah Chen × Uber Senior PM
EXPECTED: Apply OR Apply with Caution (60-75%)
CRITICAL FAILURE IF: "Do Not Apply"

WHY: Sarah has 7 years PM at Stripe/Asana/LinkedIn. She's qualified for senior PM roles. Safety domain is gap but not disqualifying.

FIX: Review experience penalty logic. Likely over-penalizing domain gap.
```

### Failure Mode 2: Leadership Years Miscalculation
```
TEST: Marcus Johnson × Red Hat Engineering Manager
EXPECTED: 4.75 years leadership (HubSpot role managing 12 engineers)
CRITICAL FAILURE IF: 0 years OR 9 years

WHY: 
- 0 years = misread as IC (parser failed)
- 9 years = counted total tenure not leadership tenure

FIX: Review leadership parsing logic. Must extract "managed team of X" not just "X years experience"
```

### Failure Mode 3: Mid-Level LEPE False Trigger
```
TEST: Jessica Martinez × [Senior Recruiter]
EXPECTED: No LEPE penalties (she's IC applying to IC role)
CRITICAL FAILURE IF: Any Manager+ leadership requirements applied

WHY: Jessica is mid-level IC recruiter. No people management required or expected.

FIX: Review LEPE trigger conditions. Must only fire for JDs requiring people leadership.
```

### Failure Mode 4: Career Switcher Hard Stop
```
TEST: David Park × Uber Senior PM
EXPECTED: Apply with Caution + coaching on positioning
CRITICAL FAILURE IF: "Do Not Apply" without coaching

WHY: Career switcher with transferable skills. Gap is coachable with positioning.

FIX: Review hard requirement failure logic. Distinguish terminal gaps from coachable gaps.
```

### Failure Mode 5: Executive Score Caps
```
TEST: Aisha Williams × [VP Marketing]
EXPECTED: 85-95% with no caps
CRITICAL FAILURE IF: Score < 85% OR any LEPE/CAE caps applied

WHY: VP with 12 years, $200M ARR scale. No caps should apply.

FIX: Review credibility multipliers and LEPE logic. Executive scale must be recognized.
```

### Failure Mode 6: Blocking Button Prevents Analysis
```
TEST: Any "Do Not Apply" scenario
EXPECTED: User can still click "Pass" and access downstream pages
CRITICAL FAILURE IF: Button blocks access to Resume Leveling or LinkedIn Analysis

WHY: HenryHQ advises but doesn't control. User must have agency.

FIX: Update UI flow. "Do Not Apply" → show warning → allow proceed with accountability log.
```

---

## ACCEPTANCE CRITERIA

### Minimum Requirements
- **Pass rate:** 80% of 10 test cases (8/10 minimum)
- **Critical failures:** 0 (any critical failure = auto-reject entire test suite)
- **Downstream consistency:** 100% (all downstream pages must mirror Job Fit decision)

### Fix Priority
1. **Critical failures first** (blocks release)
2. **Scoring logic** (affects all candidates)
3. **Messaging** (user-facing but deterministic)
4. **Parsing** (affects specific candidates)

### Fix Methodology
```
IF test fails:
1. Identify root cause (scoring | messaging | parsing | downstream)
2. Fix the rule ONCE in the source system
3. Re-run ALL 10 tests
4. Verify fix doesn't break other cases

DO NOT:
- Patch individual outputs
- Add special case logic per candidate
- Override results manually to force pass
```

---

## OUTPUT DELIVERABLE

### QA Report Format
```markdown
# HenryHQ QA Test Results
**Date:** [timestamp]
**Test Suite:** 5 candidates × 2 jobs = 10 test cases
**Architecture:** Single Source of Truth (Job Fit Scoring)

## Summary
- Tests run: 10
- Passed: X (X%)
- Failed: Y (Y%)
- Critical failures: Z
- **Pass rate: [PASS/FAIL]** (minimum 80% required, 0 critical failures)

## Critical Failures
[If any exist, list here with root cause and recommended fix]

## Test Results

### Test 1: Sarah Chen × Uber Senior PM
- **Result:** PASS/FAIL
- Expected score: 60-75% | Actual: X%
- Expected rec: Apply/Caution | Actual: [rec]
- Mismatches: [if any]
- Root cause: [if failed]

[Repeat for all 10 tests]

## Downstream Consistency Check
- Job Fit → Resume Leveling alignment: PASS/FAIL
- Job Fit → LinkedIn alignment: PASS/FAIL
- Accountability records preserved: PASS/FAIL

## Recommended Fixes
[Prioritized list with specific code changes]

## Conclusion
[Overall assessment with next steps]
```

---

## FINAL ENFORCEMENT STATEMENT

**HenryHQ is not here to encourage applications. It is here to tell the truth early, with evidence, and coach only when the gap is realistically bridgeable.**

This principle governs all testing, all fixes, and all messaging decisions. Any ambiguity defaults to honesty, not optimism.
