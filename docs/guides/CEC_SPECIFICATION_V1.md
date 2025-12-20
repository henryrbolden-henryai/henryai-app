# Capability Evidence Check (CEC) — Implementation Specification v1.0

**Status:** Ready for Implementation
**Last Updated:** December 20, 2025
**Authority:** This layer is diagnostic only. It does not alter scoring, recommendations, or eligibility.

> **Versioning Note:** This document reflects the currently deployed 4-tier recommendation system (Strongly Apply, Apply, Conditional Apply, Do Not Apply). A 6-tier expansion is planned but not yet implemented.

---

## PURPOSE

The Capability Evidence Check diagnoses **how** a candidate's resume diverges from a job's real requirements. It improves coaching quality without altering eligibility, scoring, or recommendations.

**This layer explains the mismatch. It does not decide outcomes.**

---

## ARCHITECTURAL PLACEMENT

### Execution Order (Non-Negotiable)

```
Step 1: Role Parsing
Step 2: Eligibility + Leadership Gates → (may set recommendation_locked = true)
Step 2.5: CAPABILITY EVIDENCE CHECK ← NEW LAYER (annotation only)
Step 3: CAE (Credibility Adjustment)
Step 4: LEPE (Leadership Experience Penalty Enforcement)
Step 5: Final Recommendation Lock
Step 6: Coaching Output Generation (uses capability_evidence_report)
```

### Execution Conditions

**CEC runs if and only if:**
- Job description parsing succeeded
- Resume parsing succeeded
- Eligibility gates completed (Step 2)
- **Note:** CEC runs even when recommendation is not yet locked, as long as eligibility check passed. CEC runs before the lock is set.

**CEC does NOT run if:**
- Job Fit parsing failed
- Resume data missing
- Already locked due to terminal eligibility failure (eligibility check failed)

### Hard Constraints (What CEC CANNOT Do)

```
✗ Change fit score
✗ Change recommendation (Strongly Apply / Apply / Conditional Apply / Do Not Apply)
✗ Trigger LEPE caps
✗ Trigger CAE multipliers
✗ Override hard_requirement_failures
✗ Change locked_reason
✗ Alter leadership_years calculation
✗ Make eligibility determinations
```

### What CEC DOES

```
✓ Annotates each JD requirement with evidence strength
✓ Classifies evidence as: explicit, implicit, or missing
✓ Provides coaching-grade diagnosis of gaps
✓ Explains distance between resume and requirements
✓ Feeds "Gaps to Address", "Your Move", downstream banners
```

---

## INPUT CONTRACT

### CEC Consumes

```python
{
  # From Job Description Analysis
  "jd_requirements": [
    {
      "category": "leadership",  # leadership | technical | domain | scale
      "requirement": "Lead global engineering teams",
      "criticality": "required"  # required | preferred
    }
  ],
  
  # From Resume Parsing
  "resume_data": {
    "experience": [...],
    "skills": [...],
    "education": [...]
  },
  
  # From Leadership Extraction (already computed)
  "leadership_extraction": {
    "tier_2_years": 4.75,
    "tier_3_years": 0,
    "global_scope": false,
    "distributed_teams": false,
    "manager_of_managers": false
  },
  
  # From Job Fit Interim State (pre-lock)
  "interim_context": {
    "current_score": 45,
    "current_recommendation": "Do Not Apply",
    "locked": false,
    "hard_requirement_failures": ["software engineering experience"]
  }
}
```

### CEC Does NOT Read

- Downstream page state
- User session data
- Previous CEC runs
- External APIs

---

## OUTPUT CONTRACT

### Structure

```python
{
  "capability_evidence_report": {
    "evaluated_capabilities": [
      {
        "capability_id": "leadership_global_scope",
        "capability_name": "People Leadership – Global Scope",
        "jd_requirement": "Lead a global engineering team across 3+ regions",
        "evidence_status": "missing",  # explicit | implicit | missing
        "resume_evidence": null,
        "diagnosis": "Resume shows people management (12 engineers) but no evidence of globally distributed teams or multi-region ownership.",
        "distance": "Local → Global leadership gap",
        "coachable": true,
        "criticality": "required"
      },
      {
        "capability_id": "cross_functional_product",
        "capability_name": "Cross-Functional Partnership – Product",
        "jd_requirement": "Collaborate closely with Product Management on roadmap",
        "evidence_status": "implicit",
        "resume_evidence": "Worked with DevOps, SRE, Infrastructure teams",
        "diagnosis": "Cross-functional work is present, but direct Product partnership is not demonstrated.",
        "distance": "Adjacent functions ≠ Product co-ownership",
        "coachable": true,
        "criticality": "preferred"
      },
      {
        "capability_id": "scale_distributed_systems",
        "capability_name": "Scale Signals – Distributed Systems",
        "jd_requirement": "Experience with distributed systems at 100M+ requests/day",
        "evidence_status": "explicit",
        "resume_evidence": "Scaled platform to handle 150M API requests/day maintaining 99.99% uptime",
        "diagnosis": "Strong evidence of scale.",
        "distance": null,
        "coachable": null,
        "criticality": "required"
      }
    ],
    "summary": {
      "total_capabilities_evaluated": 3,
      "explicit_count": 1,
      "implicit_count": 1,
      "missing_count": 1,
      "critical_gaps": ["leadership_global_scope"]
    }
  }
}
```

---

## CAPABILITY DIMENSIONS (v1 Required Set)

### 1. Leadership Scope

**Evaluates:**
- Local vs regional vs global teams
- Distributed vs co-located
- Time zone ownership
- Manager of managers vs IC managers

**Evidence Classification:**

| Evidence Status | Examples |
|----------------|----------|
| Explicit | "Managed distributed team across 3 regions", "Led global engineering org" |
| Implicit | "Managed team of 12" (local assumed), "Cross-functional leadership" (not people mgmt) |
| Missing | No mention of managing people, or only project/technical leadership |

**Diagnosis Templates:**
```
- "Resume shows people management but no evidence of globally distributed teams."
- "Leadership experience is local only (Boston office). No multi-region ownership demonstrated."
- "Managed team of 12, but no evidence of managing managers (Tier 3 leadership)."
```

### 2. Cross-Functional Depth

**Evaluates:**
- Explicit Product partnership
- Joint roadmap ownership
- Tradeoff and prioritization language
- Stakeholder influence vs co-decision making

**Evidence Classification:**

| Evidence Status | Examples |
|----------------|----------|
| Explicit | "Partnered with Product team on roadmap prioritization", "Co-owned product strategy with PM" |
| Implicit | "Collaborated with engineering team", "Worked with DevOps" (adjacent but not Product) |
| Missing | No mention of cross-functional work, or only single-function context |

**Diagnosis Templates:**
```
- "Cross-functional work is present, but direct Product partnership is not demonstrated."
- "Resume shows collaboration with engineering teams but no evidence of Product/Design partnership."
- "Stakeholder management mentioned, but no evidence of joint decision-making or roadmap ownership."
```

### 3. Scale Signals

**Evaluates:**
- Team size (5, 12, 50, 200+)
- Org size (division, multi-team, enterprise-wide)
- Platform complexity (monolith, microservices, distributed)
- Revenue, ARR, users, transactions

**Evidence Classification:**

| Evidence Status | Examples |
|----------------|----------|
| Explicit | "$200M ARR", "50M+ users", "150M requests/day", "Team of 35 across 4 orgs" |
| Implicit | "High-growth startup" (scale unclear), "Large enterprise" (no numbers) |
| Missing | No scale indicators, or only small-scale context ("team of 3") |

**Diagnosis Templates:**
```
- "Resume shows team management (12 engineers) but JD requires org-level leadership (50+ people)."
- "Experience is at Series A scale ($10M ARR). JD requires post-Series C scale ($200M ARR)."
- "Platform complexity demonstrated (microservices, Kubernetes) matches JD requirements."
```

### 4. Domain Adjacency

**Evaluates:**
- Direct domain experience (exact match)
- Closely adjacent experience (transferable)
- Unrelated experience (different domain)

**Evidence Classification:**

| Evidence Status | Examples |
|----------------|----------|
| Explicit | JD: "Fintech product experience" → Resume: "Built payment processing at Stripe" |
| Implicit | JD: "Healthcare product" → Resume: "Built regulated B2B SaaS products" |
| Missing | JD: "Safety & trust product" → Resume: "Billing and payments products" |

**Diagnosis Templates:**
```
- "No direct safety or trust & safety product experience. Domain gap is significant."
- "B2B SaaS experience is adjacent to this fintech role, but no direct financial services background."
- "Experience in e-commerce payments is closely related to this fintech role."
```

---

## EVIDENCE CLASSIFICATION RULES

### Hard Rules

Each capability must be tagged as **exactly one**:

1. **`explicit`**
   - Resume directly demonstrates requirement with clear evidence
   - No inference required
   - Keywords match, or quantified metrics present

2. **`implicit`**
   - Adjacent or inferred experience, but not explicit
   - Related but not direct match
   - Transferable but not proven in target domain

3. **`missing`**
   - No credible evidence present
   - Experience is in unrelated domain/function
   - Requirement not addressed in resume

### Classification Algorithm

```python
def classify_evidence(jd_requirement, resume_evidence):
    """
    Returns: "explicit" | "implicit" | "missing"
    """
    
    # Check for exact keyword matches or quantified evidence
    if exact_match(jd_requirement, resume_evidence):
        return "explicit"
    
    # Check for adjacent/transferable evidence
    if adjacent_match(jd_requirement, resume_evidence):
        return "implicit"
    
    # No evidence found
    return "missing"

def exact_match(requirement, evidence):
    """
    Examples:
    - Requirement: "global team leadership"
      Evidence: "managed distributed team across 3 regions" → True
    - Requirement: "100M+ requests/day"
      Evidence: "150M API requests/day" → True
    """
    # Extract key phrases and numbers
    # Match directly
    pass

def adjacent_match(requirement, evidence):
    """
    Examples:
    - Requirement: "Product partnership"
      Evidence: "collaborated with engineering" → True (adjacent)
    - Requirement: "fintech experience"
      Evidence: "payments at e-commerce company" → True (adjacent)
    
    Constraint: Maximum one degree of separation.
    - Product → Engineering = 1 degree (adjacent functions)
    - Product → HR = 2 degrees (not adjacent)
    - Fintech → Payments = 1 degree (adjacent domain)
    - Fintech → Healthcare = 2 degrees (not adjacent)
    """
    # Check for related domains/functions
    # Allow one degree of separation only
    pass
```

### No Soft Language Rule

```
BANNED in diagnosis:
- "Might have experience with..."
- "Potentially could demonstrate..."
- "May be able to..."
- "Likely has some background in..."

REQUIRED:
- "Resume shows X, but not Y."
- "No evidence of X."
- "X is demonstrated, but not at required scale."
```

---

## COACHING INTEGRATION

### Where CEC Output Appears

1. **"Gaps to Address" Section**
   - Lists all `missing` and `implicit` capabilities
   - Shows diagnosis and distance for each

2. **"Your Move" Coaching**
   - References critical gaps
   - Explains coachability
   - Provides strategic positioning guidance

3. **Downstream Banners**
   - Resume Leveling: Shows capability gaps context
   - LinkedIn Analysis: References positioning gaps

### Messaging Rules

**CEC messaging must:**
- Name the gap specifically
- Explain why it matters for this role
- State whether it's coachable (true/false)
- Never imply it fixes eligibility if Job Fit says "Do Not Apply"

**Example (Do Not Apply scenario):**
```
Gaps to Address:
- No direct safety product experience (0 → 7 year gap, not coachable in current search)
- Limited ML/AI product experience (preferred, not required)

Your Move:
Sarah, do not apply. The safety domain gap is terminal—this role requires 
direct experience building trust & safety products, which you do not have.

Redirect to: B2B SaaS Product roles (billing, payments, enterprise tools) 
where your Stripe and Asana experience directly applies.
```

**Example (Conditional Apply scenario):**
```
Gaps to Address:
- Leadership scope is local (team of 12 in Boston), not global (3+ regions required)
- No Product partnership evidenced (collaborated with engineering only)

Your Move:
Marcus, conditionally apply. You have strong people management (4.75 years,
12 engineers) but the global scale and Product partnership gaps will come up
in interviews.

Position it as: "I've built strong local teams and am ready to scale globally."
```

### Integration Points

```python
# In Step 6: Coaching Output Generation

def generate_gaps_section(capability_evidence_report):
    """
    Generate "Gaps to Address" from CEC output
    """
    critical_gaps = [
        cap for cap in capability_evidence_report["evaluated_capabilities"]
        if cap["evidence_status"] in ["missing", "implicit"] 
        and cap["criticality"] == "required"
    ]
    
    return format_gaps_for_display(critical_gaps)

def generate_your_move(job_fit_recommendation, capability_evidence_report):
    """
    Generate "Your Move" using:
    - Job Fit recommendation (primary authority)
    - CEC critical gaps (for specificity)
    """
    if job_fit_recommendation == "Do Not Apply":
        critical_gap = find_most_critical_gap(capability_evidence_report)
        return format_do_not_apply_coaching(critical_gap)
    
    elif job_fit_recommendation == "Conditional Apply":
        coachable_gaps = find_coachable_gaps(capability_evidence_report)
        return format_conditional_apply_coaching(coachable_gaps)
    
    # ... etc
```

---

## PROHIBITED BEHAVIORS

### CEC Must NOT

```
✗ Recommend applying (Job Fit owns recommendation)
✗ Suggest reframing to bypass hard requirements
✗ Invent experience not present in resume
✗ Re-score or re-cap after LEPE/CAE
✗ Contradict Job Fit outcomes
✗ Soften "Do Not Apply" to "maybe if you position well"
✗ Generate optimization advice for "Do Not Apply" roles
```

### Violation Examples

**WRONG:**
```
CEC Output:
"While you don't have safety product experience, you could emphasize your 
user empathy and data-driven approach to position yourself for this role."

Problem: Suggests reframing bypasses hard requirement failure.
```

**CORRECT:**
```
CEC Output:
"No direct safety or trust & safety product experience. This is a 0 → 7 year 
gap and is not coachable in current job search timeline. Job Fit recommendation: 
Do Not Apply."
```

---

## FAILURE CONDITIONS (Auto-Reject)

CEC implementation is **invalid** if:

1. **It changes score or recommendation**
   - Test: Run CEC, verify score/recommendation unchanged

2. **It fires before eligibility gates**
   - Test: Verify execution order via logs

3. **It suppresses hard requirement failures**
   - Test: Compare hard_requirement_failures before/after CEC

4. **It generates advice for "Do Not Apply" without referencing Job Fit**
   - Test: Check that "Do Not Apply" messaging includes locked_reason

5. **It contradicts Job Fit outcome**
   - Test: If Job Fit = "Do Not Apply", CEC cannot say "Apply with positioning"

---

## IMPLEMENTATION CHECKLIST

### Backend Changes

**File:** `backend.py`

- [ ] Create `evaluate_capability_evidence()` function
- [ ] Insert call after Step 2, before Step 3 (CAE)
- [ ] Function signature: `evaluate_capability_evidence(jd_requirements, resume_data, leadership_extraction, interim_context) -> Dict`
- [ ] Returns `capability_evidence_report` structure
- [ ] Does NOT modify: score, recommendation, locked_reason, hard_requirement_failures
- [ ] Add to final Job Fit response: `analysis_data["capability_evidence_report"] = cec_output`

### Capability Evaluators

- [ ] Implement `evaluate_leadership_scope()`
- [ ] Implement `evaluate_cross_functional_depth()`
- [ ] Implement `evaluate_scale_signals()`
- [ ] Implement `evaluate_domain_adjacency()`

### Coaching Integration

- [ ] Update `generate_gaps_section()` to use CEC output
- [ ] Update `generate_your_move()` to reference CEC critical gaps
- [ ] Add CEC context to Resume Leveling banner
- [ ] Add CEC context to LinkedIn Analysis banner

### Testing

- [ ] Unit test: CEC does not alter score
- [ ] Unit test: CEC does not alter recommendation
- [ ] Unit test: CEC output structure matches contract
- [ ] Integration test: "Gaps to Address" uses CEC data
- [ ] Integration test: "Your Move" references CEC critical gaps

---

## WHY THIS EXISTS (Claude Context)

CEC exists because:
- Candidates don't need encouragement
- They need clarity
- The difference between "not qualified" and "poorly evidenced" matters

**Before CEC:**
```
"Sarah, do not apply. Critical experience gap identified."
[Generic, not actionable]
```

**After CEC:**
```
"Sarah, do not apply. You have 0 years of safety or trust & safety product 
experience. This role requires direct experience building products in this 
domain—a 0 → 7 year gap that is not coachable in current search timeline.

Redirect to: B2B SaaS Product roles (billing, payments, enterprise tools) 
where your Stripe and Asana experience directly applies."
[Specific, diagnostic, actionable]
```

This layer turns HenryHQ from **accurate** into **coaching-grade**.

---

## APPENDIX A: EXAMPLE CEC OUTPUTS

### Example 1: Marcus Johnson × Red Hat Engineering Manager

**Input:**
- JD requirement: "Lead global engineering teams"
- Resume evidence: "Lead team of 12 engineers" (HubSpot, Cambridge MA)

**CEC Output:**
```json
{
  "capability_id": "leadership_global_scope",
  "capability_name": "People Leadership – Global Scope",
  "jd_requirement": "Lead global engineering teams across multiple regions",
  "evidence_status": "missing",
  "resume_evidence": "Lead team of 12 engineers (Cambridge, MA)",
  "diagnosis": "Resume shows people management but no evidence of globally distributed teams or multi-region ownership. Experience is local only.",
  "distance": "Local (single office) → Global (multi-region) leadership gap",
  "coachable": true,
  "criticality": "required"
}
```

### Example 2: Sarah Chen × Uber Senior PM (Safety)

**Input:**
- JD requirement: "Experience building safety or trust & safety products"
- Resume evidence: "Built B2B SaaS products at Stripe (billing), Asana (goals), LinkedIn (jobs)"

**CEC Output:**
```json
{
  "capability_id": "domain_safety_product",
  "capability_name": "Domain Expertise – Safety Products",
  "jd_requirement": "Experience building safety or trust & safety products",
  "evidence_status": "missing",
  "resume_evidence": null,
  "diagnosis": "No direct safety, trust & safety, or content moderation product experience. Experience is in billing, productivity, and jobs products—unrelated domains.",
  "distance": "0 → 7 year domain gap (not coachable)",
  "coachable": false,
  "criticality": "required"
}
```

### Example 3: David Park × Uber Senior PM (Career Switcher)

**Input:**
- JD requirement: "7+ years delivering successful products in tech companies"
- Resume evidence: "3 years McKinsey (digital transformation consulting) + 3 months Amazon PM intern"

**CEC Output:**
```json
{
  "capability_id": "experience_years_pm",
  "capability_name": "Product Management Experience Years",
  "jd_requirement": "7+ years delivering successful products in tech companies",
  "evidence_status": "implicit",
  "resume_evidence": "3 years McKinsey (digital transformation, product strategy projects) + 3 months Amazon PM intern",
  "diagnosis": "Consulting projects involved product strategy but no full product ownership or shipping. Direct PM experience is only 3 months (internship).",
  "distance": "3.25 years actual PM → 7 years required (52% of requirement)",
  "coachable": true,
  "criticality": "required"
}
```

---

## APPENDIX B: VISUAL RENDERING (Frontend)

### "Gaps to Address" Section (results.html or overview.html)

**Hierarchy Rule:** CEC cards never appear above the recommendation banner. Job Fit decision is always the visual anchor.

```html
<div class="gaps-section">
    <h3>Gaps to Address</h3>
    
    <!-- Critical Gap (missing, required) -->
    <div class="gap-item critical">
        <div class="gap-header">
            <span class="gap-icon">🔴</span>
            <span class="gap-title">People Leadership – Global Scope</span>
            <span class="gap-badge">Required</span>
        </div>
        <div class="gap-diagnosis">
            Resume shows people management but no evidence of globally distributed 
            teams or multi-region ownership. Experience is local only.
        </div>
        <div class="gap-distance">
            Distance: Local (single office) → Global (multi-region)
        </div>
    </div>
    
    <!-- Moderate Gap (implicit, preferred) -->
    <div class="gap-item moderate">
        <div class="gap-header">
            <span class="gap-icon">🟡</span>
            <span class="gap-title">Cross-Functional Partnership – Product</span>
            <span class="gap-badge">Preferred</span>
        </div>
        <div class="gap-diagnosis">
            Cross-functional work is present, but direct Product partnership 
            is not demonstrated.
        </div>
        <div class="gap-distance">
            Distance: Adjacent functions ≠ Product co-ownership
        </div>
    </div>
    
    <!-- No Gap (explicit) -->
    <div class="gap-item success">
        <div class="gap-header">
            <span class="gap-icon">✓</span>
            <span class="gap-title">Scale Signals – Distributed Systems</span>
        </div>
        <div class="gap-diagnosis">
            Strong evidence: "Scaled platform to 150M requests/day"
        </div>
    </div>
</div>
```

### Integration with "Your Move"

```html
<div class="your-move-section">
    <h2>Your Move</h2>
    <p class="move-recommendation">
        Marcus, apply with caution. You have strong people management 
        (4.75 years, 12 engineers) but the <strong>global scale gap</strong> 
        will surface in interviews.
    </p>
    <div class="move-positioning">
        <h4>How to position:</h4>
        <p>
            "I've built high-performing local teams and am ready to scale 
            globally. My distributed systems experience (Kubernetes, AWS) 
            translates directly to managing distributed teams."
        </p>
    </div>
</div>
```

---

## NEXT STEPS FOR IMPLEMENTATION

1. **Backend Implementation**
   - Implement `evaluate_capability_evidence()` function
   - Insert between Step 2 and Step 3
   - Add CEC output to Job Fit response

2. **Coaching Integration**
   - Update "Gaps to Address" to use CEC data
   - Update "Your Move" to reference critical gaps
   - Add CEC context to downstream pages

3. **Testing**
   - Unit tests for CEC functions
   - Integration tests for coaching quality
   - Validate CEC does not alter scoring

4. **Documentation**
   - Update IMPLEMENTATION_GUIDE.md
   - Add CEC examples to README
   - Document capability evaluation logic

---

**END OF SPECIFICATION**

This is the missing muscle that turns HenryHQ from accurate into coaching-grade.
