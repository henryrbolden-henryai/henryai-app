# Resume Builder Test Assertion Matrix

**Version:** 1.0  
**Date:** January 2026  
**Purpose:** Pass/fail verification contracts for synthetic test resumes  
**Status:** Ready for QA Implementation

---

## Overview

This document defines explicit, objective assertions the Resume Builder must satisfy when processing each synthetic test resume. These are binary pass/fail contracts with no subjective interpretation.

**Test Context:** Assume each resume is evaluated against a Senior Product Manager role at a Series B SaaS company requiring 7+ years experience, team leadership, and P&L ownership.

---

## TEST RESUME #1: Missing Scope

**Candidate:** Rachel M. Patterson  
**Design Intent:** Mid-senior titles present but zero scope signals (no team size, budget, revenue, users, geography, or decision authority)

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | PM II (Mid-level) |
| Target level | Senior PM / PM III |
| Level gap | 1-2 levels |
| Confidence | <65 |
| Fit score | Capped at 50% maximum |

**Rationale:** Title says "Senior PM" but evidence shows only collaboration and participation, not ownership or scale.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `missing_scope_signal` | blocker | user-visible | YES |
| `missing_ownership_signal` | warning | analysis only | YES |
| `weak_impact_signal` | warning | user-visible | YES |
| `title_inflation_detected` | N/A | N/A | NO |
| `keyword_stuffing_detected` | N/A | N/A | NO |
| `mid_market_language_detected` | warning | analysis only | OPTIONAL |

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| No team size mentioned across 3 roles | presentation | Candidate likely managed scope but failed to quantify it |
| No budget or P&L responsibility stated | presentation | Senior PM roles typically have budget; omission is presentation failure |
| No user/customer count provided | presentation | Product impact exists but is not articulated |
| No decision authority language | experience OR presentation | Requires follow-up; "collaborated" and "contributed" suggest IC work |

**Hard Rule Compliance:** Not all gaps classified as experience. Majority are presentation gaps.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | NO - Block generation pending user action |
| Blocking reason | Missing scope signal is a blocker |
| Required user action | Add scope signals: team size, budget, user count, or geography |
| If override allowed | Generate with downgraded positioning only |
| Max bullets per role | 3 (if generated) |
| Bullets dropped | YES - All "collaborated/contributed/participated" bullets deprioritized |
| Summary replaced | YES - Role Snapshot format required |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | Zero scope signals; cannot verify senior-level work |
| Apply | NO | Insufficient evidence of target-level performance |
| Conditional Apply | YES | IF user adds scope signals in follow-up |
| Long Shot | YES | Acceptable with explicit market positioning warning |
| Do Not Apply | YES | Defensible given evidence gap |

**Forbidden:** "Apply" or higher without scope signals present.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES, but only in context |
| Keyword density reduced | N/A (not a stuffing issue) |
| Keyword lists suppressed | N/A |
| Override rule | ATS optimization must NOT override credibility gates |

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | NO | |
| Ownership signal detected | NO | |
| Title inflation flagged | NO | |
| `missing_scope_signal` fired | YES (blocker) | |
| Bullet quality gate enforced | YES | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Conditional or lower) | |
| Fit score capped | YES (≤50%) | |
| Generation blocked | YES | |

---

## TEST RESUME #2: Missing Ownership

**Candidate:** James T. Whitfield  
**Design Intent:** Projects and initiatives mentioned but passive voice throughout; never states who owned decisions

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | Operations Manager (Mid-level) |
| Target level | Director of Operations |
| Level gap | 1 level |
| Confidence | <60 |
| Fit score | Capped at 45% maximum |

**Rationale:** Title says "Director" but all bullets use passive voice ("was implemented," "were maintained"), suggesting contributor not owner.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `missing_ownership_signal` | blocker | user-visible | YES |
| `missing_scope_signal` | warning | user-visible | YES |
| `weak_impact_signal` | warning | analysis only | YES |
| `title_inflation_detected` | warning | analysis only | OPTIONAL |
| `keyword_stuffing_detected` | N/A | N/A | NO |
| `mid_market_language_detected` | warning | analysis only | OPTIONAL |

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| 100% passive voice in bullets | presentation | Active ownership exists but is obscured by writing style |
| No "led/owned/decided/accountable" language | presentation | Director-level work likely happened but not articulated |
| No stated decision authority | experience OR presentation | Passive framing suggests possible IC disguised as Director |
| WMS implementation not attributed | presentation | System implementation happened; who decided is unclear |

**Hard Rule Compliance:** Majority presentation gaps; one potential experience gap flagged for review.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | NO - Block generation pending user action |
| Blocking reason | Missing ownership signal is a blocker |
| Required user action | Rewrite bullets in active voice with decision ownership |
| If override allowed | Generate with hard seniority cap (Manager level max) |
| Max bullets per role | 3 (if generated) |
| Bullets dropped | YES - All passive bullets flagged for rewrite |
| Summary replaced | YES - Role Snapshot format required |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | Cannot verify decision-making authority |
| Apply | NO | Ownership is table stakes for Director roles |
| Conditional Apply | YES | IF user rewrites with ownership language |
| Long Shot | YES | With explicit positioning as operations contributor |
| Do Not Apply | YES | Defensible; resume does not support Director claim |

**Forbidden:** "Apply" or higher without ownership signals present.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES, but only in context |
| Keyword density reduced | N/A |
| Keyword lists suppressed | N/A |
| Override rule | ATS optimization must NOT override credibility gates |

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | PARTIAL (4 facilities mentioned) | |
| Ownership signal detected | NO | |
| Title inflation flagged | OPTIONAL | |
| `missing_ownership_signal` fired | YES (blocker) | |
| Passive voice detected | YES (100%) | |
| Bullet quality gate enforced | YES | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Conditional or lower) | |
| Fit score capped | YES (≤45%) | |
| Generation blocked | YES | |

---

## TEST RESUME #3: Inflated Title, Junior Evidence

**Candidate:** Marcus D. Chen  
**Design Intent:** Title says "Head of Engineering" but evidence shows IC work (writing code, fixing bugs, reviewing PRs)

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | Software Engineer II / Senior Engineer |
| Target level | Engineering Manager / Director |
| Level gap | 2-3 levels |
| Confidence | <50 |
| Fit score | Hard cap at 35% maximum |

**Rationale:** "Head of Engineering" title with zero evidence of team leadership, architecture decisions, or org-level impact. Evidence suggests senior IC at best.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `title_inflation_detected` | blocker | user-visible | YES |
| `missing_scope_signal` | warning | user-visible | YES |
| `missing_ownership_signal` | warning | user-visible | YES |
| `weak_impact_signal` | warning | analysis only | YES |
| `keyword_stuffing_detected` | N/A | N/A | NO |
| `mid_market_language_detected` | N/A | N/A | NO |

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| No team size or direct reports mentioned | experience | "Head of" without team is a title inflation signal |
| No architecture or technical strategy | experience | Heads of Engineering own technical direction; none shown |
| No hiring/performance management evidence | experience | Leadership role without people management evidence |
| All bullets are IC tasks (coding, debugging, PRs) | experience | Evidence directly contradicts title claim |
| No org-level impact or cross-team coordination | experience | Head-level should show department or company impact |

**Hard Rule Compliance:** All gaps classified as experience gaps. This is correct because title is inflated, not poorly presented.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | YES - With hard cap and warnings |
| Positioning | Downgraded to "Senior Software Engineer" maximum |
| Warning text | "Title inflation detected. Resume repositioned to match evidence." |
| Max bullets per role | 3 |
| Bullets dropped | NO - Bullets are accurate for IC level |
| Summary replaced | YES - Must reflect actual level (Senior Engineer) |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | Evidence does not support management-level roles |
| Apply | NO | Title claim is not credible |
| Conditional Apply | NO | No presentation fix can address experience gap |
| Long Shot | YES | For IC/Senior IC roles only |
| Do Not Apply | YES | For any management or Director-level role |

**Forbidden:** Any recommendation above "Long Shot" for leadership roles.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES (technical skills valid) |
| Keyword density reduced | N/A |
| Keyword lists suppressed | N/A |
| Leadership keywords | SUPPRESS - Cannot claim leadership keywords |
| Override rule | ATS optimization must NOT override credibility gates |

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | NO | |
| Ownership signal detected | NO | |
| Title inflation flagged | YES (blocker) | |
| `title_inflation_detected` fired | YES | |
| Detected level matches evidence | YES (Senior IC) | |
| Bullet quality gate enforced | YES | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Long Shot or DNR for leadership) | |
| Fit score hard-capped | YES (≤35%) | |
| Positioning downgraded | YES (Senior Engineer max) | |

---

## TEST RESUME #4: Metrics Without Consequence

**Candidate:** Sarah L. Thompson  
**Design Intent:** Impressive-looking numbers (34%, 67%, 156%) but no connection to business decisions or risk

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | Marketing Manager (Mid-level) |
| Target level | Senior Marketing Manager |
| Level gap | 0-1 level |
| Confidence | 55-65 |
| Fit score | Capped at 55% maximum |

**Rationale:** Metrics present but "vanity metrics" without business context. Cannot determine actual impact.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `weak_impact_signal` | warning | user-visible | YES |
| `missing_scope_signal` | warning | analysis only | YES |
| `missing_ownership_signal` | warning | analysis only | OPTIONAL |
| `title_inflation_detected` | N/A | N/A | NO |
| `keyword_stuffing_detected` | N/A | N/A | NO |
| `mid_market_language_detected` | warning | analysis only | OPTIONAL |

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| Metrics lack business context | presentation | Numbers exist but "so what?" is missing |
| No revenue/pipeline impact stated | presentation | Marketing metrics should tie to business outcomes |
| No decision ownership on metric improvements | presentation | Who decided to pursue these improvements is unclear |
| "Improved X by Y%" without methodology | presentation | How improvements happened is not articulated |
| No budget or resource context | presentation | Scale of work is unknown |

**Hard Rule Compliance:** All gaps are presentation gaps. The work may be legitimate but is poorly framed.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | YES - With warnings and bullet rewrites |
| Positioning | Maintain level but flag weak evidence |
| Warning text | "Metrics require business context. Add revenue impact or strategic decisions." |
| Max bullets per role | 4 |
| Bullets dropped | YES - Deprioritize context-free metrics |
| Summary replaced | YES - Role Snapshot with context requirement |
| Required rewrites | All metric bullets need "which resulted in..." framing |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | Cannot verify business impact |
| Apply | NO | Vanity metrics insufficient for senior roles |
| Conditional Apply | YES | IF user adds business context to metrics |
| Long Shot | YES | Acceptable with metric context warning |
| Do Not Apply | NO | Not warranted; work may be legitimate |

**Forbidden:** "Apply" or higher without business context added to metrics.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES |
| Keyword density reduced | N/A |
| Keyword lists suppressed | N/A |
| Metric bullets | DEPRIORITIZE without context |
| Override rule | ATS optimization must NOT override credibility gates |

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | NO | |
| Ownership signal detected | NO | |
| Title inflation flagged | NO | |
| `weak_impact_signal` fired | YES | |
| Metrics detected | YES (multiple) | |
| Metrics have business context | NO | |
| Bullet quality gate enforced | YES (deprioritized) | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Conditional or lower) | |
| Fit score capped | YES (≤55%) | |
| Rewrite prompts generated | YES | |

---

## TEST RESUME #5: Keyword-Stuffed ATS Trap

**Candidate:** Kevin R. Martinez  
**Design Intent:** Heavy Tier-1 keyword repetition in disconnected lists with no contextual usage

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | Data Scientist (Mid-level) |
| Target level | Senior Data Scientist |
| Level gap | 0-1 level |
| Confidence | <55 |
| Fit score | Reduced by keyword penalty |

**Rationale:** Keywords present but used as decoration, not demonstration. Actual work is obscured by keyword noise.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `keyword_stuffing_detected` | warning | user-visible | YES |
| `weak_impact_signal` | warning | analysis only | YES |
| `missing_scope_signal` | warning | analysis only | YES |
| `missing_ownership_signal` | warning | analysis only | OPTIONAL |
| `title_inflation_detected` | N/A | N/A | NO |
| `mid_market_language_detected` | N/A | N/A | NO |

**Keyword Density Metrics (for validation):**
- "Machine Learning" appears: 5+ times
- "Deep Learning" appears: 4+ times
- "TensorFlow" appears: 4+ times
- "Python" appears: 4+ times
- Keyword-to-substance ratio: HIGH (flag trigger)

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| Keywords in list format without context | presentation | Skills exist but are listed, not demonstrated |
| Summary is keyword soup | presentation | Professional summary should tell a story, not list tools |
| Bullets repeat keywords without outcomes | presentation | "Applied ML using TensorFlow" says nothing about what was built |
| No project outcomes or business impact | presentation | Technical work happened but results are missing |
| Core Competencies section is pure keyword list | presentation | Legitimate skills presented in non-credible format |

**Hard Rule Compliance:** All gaps are presentation gaps. Candidate may be skilled but resume is gaming ATS.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | YES - With keyword reduction and warnings |
| Positioning | Maintain level but reduce keyword density |
| Warning text | "Keyword density exceeds credibility threshold. Contextual usage required." |
| Max bullets per role | 3 |
| Bullets dropped | YES - Keyword-heavy bullets deprioritized |
| Summary replaced | YES - Role Snapshot format, max 2 keywords |
| Core Competencies | SUPPRESS or reduce to top 8 |
| Keyword insertion | BLOCKED - No additional keywords |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | Cannot verify actual technical depth |
| Apply | NO | Keyword stuffing undermines credibility |
| Conditional Apply | YES | IF user rewrites with contextual keyword usage |
| Long Shot | YES | With explicit resume revision requirement |
| Do Not Apply | NO | Not warranted; skills may be real |

**Forbidden:** "Apply" or higher without keyword density reduction.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES, but limited to contextual usage only |
| Keyword density reduced | YES - Mandatory |
| Keyword lists suppressed | YES - Core Competencies section suppressed or reduced |
| Keyword repetition | FLAG and reduce |
| Override rule | ATS optimization must NOT override credibility gates |

**Critical Rule:** Keyword stuffing must REDUCE fit score, not improve it.

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | NO | |
| Ownership signal detected | NO | |
| Title inflation flagged | NO | |
| `keyword_stuffing_detected` fired | YES | |
| Keyword density calculated | YES (HIGH) | |
| Keyword repetition flagged | YES | |
| Keyword lists suppressed | YES | |
| Bullet quality gate enforced | YES | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Conditional or lower) | |
| Fit score NOT inflated by keywords | YES | |
| ATS weighting reduced | YES | |

---

## TEST RESUME #6: Generic Mid-Market Resume

**Candidate:** Amanda J. Brooks  
**Design Intent:** Safe corporate language, no unique decisions, no irreversible outcomes, could apply to 10+ roles

### 1. Expected System Classification

| Field | Required Value |
|-------|----------------|
| Detected level | Project Manager (Mid-level) |
| Target level | Senior Project Manager |
| Level gap | 0-1 level |
| Confidence | 50-60 |
| Fit score | Capped at 50% maximum |

**Rationale:** Resume is competent but undifferentiated. No signal that distinguishes this candidate from 100 others.

### 2. Required Flags & Warnings

| Flag Name | Severity | Visibility | Required |
|-----------|----------|------------|----------|
| `mid_market_language_detected` | warning | user-visible | YES |
| `weak_impact_signal` | warning | user-visible | YES |
| `missing_scope_signal` | warning | analysis only | YES |
| `missing_ownership_signal` | warning | analysis only | YES |
| `title_inflation_detected` | N/A | N/A | NO |
| `keyword_stuffing_detected` | N/A | N/A | NO |

**Red Flag Language Detected (from lint):**
- "Results-oriented professional"
- "Proven track record of success"
- "Strong communicator"
- "Self-motivated team player"
- "Fast-paced environments"
- "Exceeding expectations"
- "Strong attention to detail"
- "Demonstrated flexibility and adaptability"
- "Took initiative"
- "Willingness to learn and grow"

### 3. Gap Classification Assertions

| Gap Description | Gap Type | Justification |
|-----------------|----------|---------------|
| Summary uses cliche language | presentation | Real accomplishments may exist but are hidden behind buzzwords |
| No specific project outcomes | presentation | "Delivered projects on time" says nothing unique |
| No industry or domain expertise shown | presentation | Could be any PM in any industry |
| No decision authority or ownership | presentation OR experience | "Facilitated meetings" is not ownership |
| No irreversible consequences mentioned | presentation | No evidence of high-stakes work |
| Generic skills section | presentation | "Problem Solving" and "Communication" are not differentiators |

**Hard Rule Compliance:** Majority presentation gaps with one potential experience gap.

### 4. Resume Output Behavior

| Decision | Value |
|----------|-------|
| Generation allowed | YES - With warnings and heavy rewrites |
| Positioning | Flag as "replaceable candidate" signal |
| Warning text | "Resume contains mid-market language. Differentiation required for competitive roles." |
| Max bullets per role | 3 |
| Bullets dropped | YES - All cliche bullets flagged for rewrite |
| Summary replaced | YES - Mandatory Role Snapshot replacement |
| Red flag language | STRIP all instances |

### 5. Recommendation Logic

| Recommendation | Allowed | Justification |
|----------------|---------|---------------|
| Strongly Apply | NO | No differentiation from candidate pool |
| Apply | NO | Cannot position as competitive without unique evidence |
| Conditional Apply | YES | IF user provides specific, unique accomplishments |
| Long Shot | YES | With explicit "generic resume" warning |
| Do Not Apply | NO | Not warranted; candidate may have real experience |

**Forbidden:** "Apply" or higher without differentiation signals.

### 6. ATS Handling Assertions

| Rule | Value |
|------|-------|
| Tier 1 keywords allowed to surface | YES, but only in context |
| Keyword density reduced | N/A |
| Keyword lists suppressed | N/A |
| Generic language | STRIP from output |
| Override rule | ATS optimization must NOT override credibility gates |

### Assertion Matrix

| Rule | Expected Result | Pass/Fail |
|------|-----------------|-----------|
| Scope signal present | NO | |
| Ownership signal detected | NO | |
| Title inflation flagged | NO | |
| `mid_market_language_detected` fired | YES | |
| Red flag phrases detected | YES (10+) | |
| Cliche summary detected | YES | |
| Bullet quality gate enforced | YES | |
| Fabrication check | PASS (no fabrication) | |
| Recommendation downgraded | YES (Conditional or lower) | |
| Fit score capped | YES (≤50%) | |
| Summary replaced | YES | |
| Red flag language stripped | YES | |

---

## Global Pass Criteria

The Resume Builder is working correctly only if:

1. **All 6 resumes fail their intended quality gates**
2. **No senior-positioned resume is generated without scope + ownership + impact signals**
3. **Title inflation triggers hard cap on positioning and fit score**
4. **Keyword stuffing reduces (not improves) fit score**
5. **Passive voice triggers ownership flag**
6. **Generic/mid-market language triggers differentiation warning**
7. **All blockers prevent generation until user action**
8. **No fabrication occurs in any output**
9. **Recommendations are capped at Conditional Apply or lower for all 6 resumes**
10. **ATS optimization never overrides credibility gates**

---

## Global Failure Conditions

The system is broken if ANY of the following occur:

| Failure | Severity | Indicates |
|---------|----------|-----------|
| Senior resume generated without scope signals | CRITICAL | Signal contract not enforced |
| Inflated title not capped in positioning | CRITICAL | Title validation bypassed |
| Keyword stuffing improves fit score | CRITICAL | ATS gaming vulnerability |
| No refusal/blocker behavior observed | CRITICAL | Quality gates not functional |
| "Apply" recommendation issued for any test resume | HIGH | Recommendation logic broken |
| Passive voice not detected as ownership gap | HIGH | Ownership detection failing |
| Generic language passes without warning | MEDIUM | Lint rules not firing |
| Metrics without context scored as strong impact | MEDIUM | Impact validation broken |
| Fabrication detected in any output | CRITICAL | Zero-fabrication policy violated |
| All gaps classified as "experience" when presentation fixes exist | HIGH | Gap classification broken |

---

## Implementation Notes

### For QA Team

1. Run each resume through the Resume Builder with the same target JD (Senior PM at Series B SaaS)
2. Document actual values in Pass/Fail column
3. Any deviation from Expected Result is a defect
4. Blockers must block; warnings must warn
5. Do not fix resumes during testing

### For Development Team

1. Use this matrix to validate each quality gate independently
2. Flag names must match exactly
3. Severity levels (blocker vs warning) must be enforced
4. Fit score caps are hard limits, not suggestions
5. Generation blocking is binary; no soft blocks

### For Product Team

1. This matrix defines minimum quality standards
2. Passing all assertions = ready for beta
3. Any CRITICAL failure = launch blocker
4. Any HIGH failure = requires remediation before launch

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2026 | Initial assertion matrix | Product |

---

**Status:** Ready for QA Implementation  
**Next Review:** After first QA pass  
**Owner:** Product Team
