# Resume Quality Gates Specification

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Ready for Implementation  
**Owner:** Product Team  
**Depends On:** RESUME_COVER_LETTER_CUSTOMIZATION_SPEC.md

---

## Purpose

This addendum hardens the Resume Customization spec. The goal: **no weak output possible.**

At the 0.01% level, tight does not mean more features. Tight means the system cannot produce a mid-market resume even if it tries.

---

## 1. Resume Signal Contract

**Every generated resume must satisfy this contract before export.**

### Required Signals

| Signal Type | Definition | Example |
|-------------|------------|---------|
| **Scope** | Team size, budget, users, revenue, geography, or authority | "Led 12-person team" / "$50M P&L" / "20M MAU" |
| **Impact** | Outcome + consequence | "Reduced churn 18%, saving $2.4M ARR" |
| **Ownership** | Decision-maker vs. contributor | "Owned" / "Led" / "Defined" (not "Supported" / "Helped") |
| **Level** | Language matches detected seniority | Senior = strategy language; Mid = execution language |

### Validation Logic

```python
@dataclass
class SignalContract:
    scope_present: bool
    impact_present: bool
    ownership_present: bool
    level_aligned: bool
    
    def is_valid(self) -> bool:
        return all([
            self.scope_present,
            self.impact_present,
            self.ownership_present,
            self.level_aligned
        ])

def validate_signal_contract(resume: dict, detected_level: str) -> SignalContract:
    """
    Check if resume satisfies the signal contract.
    Run after customization, before export.
    """
    bullets = extract_all_bullets(resume)
    
    return SignalContract(
        scope_present=any(has_scope_signal(b) for b in bullets),
        impact_present=any(has_impact_signal(b) for b in bullets),
        ownership_present=any(has_ownership_signal(b) for b in bullets),
        level_aligned=check_level_alignment(resume, detected_level)
    )

def has_scope_signal(bullet: str) -> bool:
    """Detect team size, budget, users, revenue, geography, or authority."""
    scope_patterns = [
        r'\d+[\-\s]*(person|people|engineer|team|report)',  # team size
        r'\$[\d\.]+[MBK]',  # budget/revenue
        r'\d+[MKB]?\+?\s*(users|customers|MAU|DAU)',  # user scale
        r'(global|regional|national|EMEA|APAC|NA)',  # geography
        r'(P&L|budget|revenue|ARR|GMV)',  # financial authority
    ]
    return any(re.search(p, bullet, re.IGNORECASE) for p in scope_patterns)

def has_impact_signal(bullet: str) -> bool:
    """Detect outcome + consequence (not just activity)."""
    # Must have both a metric AND a business consequence
    has_metric = bool(re.search(r'\d+%|\$[\d\.]+|[\d\.]+x', bullet))
    has_consequence = any(word in bullet.lower() for word in [
        'resulting', 'saving', 'driving', 'enabling', 'reducing',
        'increasing', 'generating', 'delivering', 'achieving'
    ])
    return has_metric and has_consequence

def has_ownership_signal(bullet: str) -> bool:
    """Detect decision-maker language, not contributor language."""
    ownership_verbs = [
        'owned', 'led', 'defined', 'built', 'shipped', 'launched',
        'architected', 'designed', 'established', 'created', 'drove'
    ]
    contributor_verbs = [
        'supported', 'helped', 'assisted', 'contributed', 'participated',
        'involved', 'worked on', 'responsible for'
    ]
    
    bullet_lower = bullet.lower()
    has_ownership = any(v in bullet_lower for v in ownership_verbs)
    has_contributor = any(v in bullet_lower for v in contributor_verbs)
    
    return has_ownership and not has_contributor
```

### Contract Failure Behavior

**If any signal is missing:**
1. Do NOT auto-fill
2. Do NOT hallucinate
3. Surface a blocker notice:

```
┌─────────────────────────────────────────────────────────────────┐
│  🚫 Resume Signal Gap                                           │
│  ───────────────────────────────────────────────────────────    │
│                                                                 │
│  This resume cannot signal seniority yet.                       │
│                                                                 │
│  Missing: Scope indicator                                       │
│                                                                 │
│  Your resume doesn't show team size, budget, user scale, or     │
│  decision authority. Senior roles require at least one.         │
│                                                                 │
│  Quick fix: Add one of these to your most recent role:          │
│  • Team size you led or influenced                              │
│  • Budget you owned or managed                                  │
│  • User/customer scale you impacted                             │
│  • Geographic scope of your work                                │
│                                                                 │
│  [Add scope signal] [Download anyway (not recommended)]         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Bullet Quality Gate

**Before a bullet enters the final resume, it must pass at least one test.**

### Passing Criteria (One Required)

| Criterion | Definition | Example |
|-----------|------------|---------|
| **Quantified outcome** | Has a number tied to business result | "Increased conversion 23%" |
| **Explicit decision ownership** | Shows what candidate decided | "Defined pricing strategy that..." |
| **Irreversible business consequence** | Something changed permanently | "Launched product that became..." |
| **Org-level leverage** | Influence, scale, or systems | "Established framework adopted by..." |

### Quality Gate Logic

```python
def bullet_passes_quality_gate(bullet: str) -> Tuple[bool, str]:
    """
    Returns (passes, reason).
    Bullet must pass at least one criterion.
    """
    if has_quantified_outcome(bullet):
        return True, "quantified_outcome"
    if has_decision_ownership(bullet):
        return True, "decision_ownership"
    if has_irreversible_consequence(bullet):
        return True, "irreversible_consequence"
    if has_org_leverage(bullet):
        return True, "org_leverage"
    
    return False, "no_qualifying_signal"

def has_quantified_outcome(bullet: str) -> bool:
    """Number tied to business result."""
    return bool(re.search(r'(\d+%|\$[\d\.]+[MBK]?|[\d\.]+x|\d+\s*(users|customers|deals|launches))', bullet))

def has_decision_ownership(bullet: str) -> bool:
    """Shows what candidate decided, not just did."""
    decision_verbs = ['defined', 'decided', 'chose', 'prioritized', 'approved', 'vetoed', 'set']
    return any(v in bullet.lower() for v in decision_verbs)

def has_irreversible_consequence(bullet: str) -> bool:
    """Something changed permanently."""
    consequence_markers = ['launched', 'shipped', 'established', 'created', 'built', 'founded', 'introduced']
    return any(m in bullet.lower() for m in consequence_markers)

def has_org_leverage(bullet: str) -> bool:
    """Influence beyond immediate scope."""
    leverage_markers = [
        'adopted by', 'scaled across', 'influenced', 'framework',
        'standard', 'company-wide', 'org-wide', 'cross-functional'
    ]
    return any(m in bullet.lower() for m in leverage_markers)
```

### Gate Behavior

```python
def apply_bullet_quality_gate(bullets: List[str], max_bullets: int = 5) -> dict:
    """
    Rank bullets, keep top N, archive the rest.
    """
    passing = []
    failing = []
    
    for bullet in bullets:
        passes, reason = bullet_passes_quality_gate(bullet)
        if passes:
            passing.append({"bullet": bullet, "reason": reason})
        else:
            failing.append(bullet)
    
    # Sort passing bullets by signal strength
    passing_sorted = sort_by_signal_strength(passing)
    
    return {
        "kept": [b["bullet"] for b in passing_sorted[:max_bullets]],
        "deprioritized": [b["bullet"] for b in passing_sorted[max_bullets:]],
        "dropped": failing,
        "drop_count": len(failing)
    }
```

### UI: "What We Deprioritized"

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 Bullet Prioritization                                       │
│  ───────────────────────────────────────────────────────────    │
│                                                                 │
│  Kept (5 bullets with strongest signals):                       │
│  ✓ Owned product roadmap for payments, serving 20M users        │
│  ✓ Led 12-person team through SOC2 compliance                   │
│  ✓ Drove 34% reduction in checkout abandonment                  │
│  ✓ Defined pricing strategy generating $8M incremental ARR      │
│  ✓ Launched fraud detection system reducing chargebacks 62%     │
│                                                                 │
│  Deprioritized (moved to archive):                              │
│  • Collaborated with engineering on technical requirements      │
│  • Managed stakeholder communications                           │
│  • Participated in quarterly planning sessions                  │
│                                                                 │
│  These bullets lack quantified outcomes or decision ownership.  │
│  [Restore a bullet] [Keep as optimized]                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Role Framing Requirement

**Every position must have an inferred role frame, even if not shown in output.**

### Role Frame Structure

```
Hired to [problem], accountable for [scope], measured on [outcome].
```

### Examples

| Role | Role Frame |
|------|------------|
| Senior PM at Stripe | Hired to scale payments infrastructure, accountable for checkout conversion, measured on revenue per transaction |
| Engineering Manager at Uber | Hired to build reliability at scale, accountable for 12-person platform team, measured on uptime and deployment velocity |
| Director of Marketing at Series B | Hired to establish demand gen function, accountable for pipeline generation, measured on qualified leads and CAC |

### Implementation

```python
def infer_role_frame(role: dict, company_context: dict) -> dict:
    """
    Infer the role frame from resume content.
    Used to guide bullet generation and prioritization.
    """
    title = role.get("title", "")
    company = role.get("company", "")
    bullets = role.get("bullets", [])
    
    # Attempt to infer each component
    problem = infer_problem(title, company, company_context)
    scope = infer_scope(bullets)
    outcome = infer_outcome(bullets)
    
    return {
        "problem": problem,
        "scope": scope,
        "outcome": outcome,
        "confidence": calculate_frame_confidence(problem, scope, outcome),
        "missing": identify_missing_frame_components(problem, scope, outcome)
    }

def identify_missing_frame_components(problem, scope, outcome) -> List[str]:
    """Identify what's missing from the role frame."""
    missing = []
    if not problem or problem == "unknown":
        missing.append("problem")
    if not scope or scope == "unknown":
        missing.append("scope")
    if not outcome or outcome == "unknown":
        missing.append("outcome")
    return missing
```

### Frame Gap Behavior

If Claude cannot infer the role frame:
1. Flag as **presentation gap**
2. Trigger quick win suggestion:

```
Quick Win: Your [Role] at [Company] doesn't show why you were hired.

Add context like: "Brought in to [problem]. Owned [scope]."

This signals strategic hire, not backfill.
```

---

## 4. Contextual Keyword Integration

**Tier 1 keywords must appear inside a decision, outcome, or system description. Never standalone.**

### Keyword Placement Rules

| Placement | Allowed | Example |
|-----------|---------|---------|
| Inside decision | ✅ | "Owned **roadmap prioritization** decisions that cut cycle time 18%" |
| Inside outcome | ✅ | "**Product strategy** that drove $8M ARR" |
| Inside system description | ✅ | "Built **agile** delivery framework adopted by 4 teams" |
| Standalone claim | ❌ | "Experienced with roadmap prioritization" |
| Skills list | ❌ | "Skills: roadmap prioritization, product strategy" |

### Validation Logic

```python
def validate_keyword_placement(bullet: str, keyword: str) -> bool:
    """
    Keyword must be embedded in decision, outcome, or system context.
    Not allowed as standalone claim.
    """
    if keyword.lower() not in bullet.lower():
        return True  # Keyword not present, no violation
    
    # Check if keyword is embedded in qualifying context
    decision_context = re.search(
        rf'(owned|led|defined|decided|set).*{re.escape(keyword)}',
        bullet, re.IGNORECASE
    )
    outcome_context = re.search(
        rf'{re.escape(keyword)}.*(\d+%|\$[\d\.]+|resulting|driving|enabling)',
        bullet, re.IGNORECASE
    )
    system_context = re.search(
        rf'(built|established|created|designed).*{re.escape(keyword)}.*(framework|system|process|standard)',
        bullet, re.IGNORECASE
    )
    
    return bool(decision_context or outcome_context or system_context)

def filter_unembeddable_keywords(keywords: List[str], bullets: List[str]) -> List[str]:
    """
    If a keyword can't be embedded cleanly, skip it.
    ATS ≠ stuffing.
    """
    embeddable = []
    for keyword in keywords:
        can_embed = any(
            can_naturally_embed(keyword, bullet) 
            for bullet in bullets
        )
        if can_embed:
            embeddable.append(keyword)
    return embeddable
```

---

## 5. Summary Kill Switch

**If the summary sounds generic, replace with Role Snapshot.**

### Generic Summary Detection

```python
def is_generic_summary(summary: str) -> bool:
    """
    Detect if summary could fit 5 different roles.
    """
    generic_markers = [
        r'results-driven',
        r'passionate',
        r'motivated professional',
        r'proven track record',
        r'excellent communication',
        r'team player',
        r'detail-oriented',
    ]
    
    has_generic_language = any(
        re.search(m, summary, re.IGNORECASE) 
        for m in generic_markers
    )
    
    lacks_scale = not bool(re.search(
        r'(\d+[MBK]?\+?\s*(users|customers|ARR|revenue|budget|team)|\$[\d\.]+[MBK])',
        summary
    ))
    
    lacks_specificity = not bool(re.search(
        r'(at|for|serving)\s+[A-Z][a-z]+',  # Company or product name
        summary
    ))
    
    return has_generic_language or (lacks_scale and lacks_specificity)
```

### Role Snapshot Format

When summary fails, replace with:

```
[Level] [Function] operating at [stage/scale]. [Ownership statement]. [Trust signal].
```

**Example:**

❌ Generic:
> "Results-driven product manager with excellent communication skills and a proven track record of cross-functional collaboration."

✅ Role Snapshot:
> "Senior Product Manager operating at fintech scale. Owned payment systems serving 20M+ users. Trusted decision-maker across engineering, legal, and risk."

### Rules

- No adjectives (no "dynamic," "passionate," "driven")
- Must include scale indicator
- Must include ownership statement
- Must signal trust/authority level

---

## 6. Change Log (Mandatory)

**Every resume generation must internally record what changed and why.**

### Change Log Structure

```python
@dataclass
class ChangeLogEntry:
    change_type: str  # "moved_up" | "moved_down" | "removed" | "rewritten" | "added_keyword"
    location: str  # "summary" | "role:Company Name" | "skills"
    original: str
    modified: str
    reason: str
    timestamp: datetime

@dataclass
class ResumeChangeLog:
    session_id: str
    original_hash: str
    modified_hash: str
    entries: List[ChangeLogEntry]
    
    def summary(self) -> dict:
        return {
            "moved_up": len([e for e in self.entries if e.change_type == "moved_up"]),
            "moved_down": len([e for e in self.entries if e.change_type == "moved_down"]),
            "removed": len([e for e in self.entries if e.change_type == "removed"]),
            "rewritten": len([e for e in self.entries if e.change_type == "rewritten"]),
            "keywords_added": len([e for e in self.entries if e.change_type == "added_keyword"]),
        }
```

### What Gets Logged

| Change Type | Example |
|-------------|---------|
| moved_up | Bullet about revenue impact moved from position 4 to position 1 |
| moved_down | Bullet about stakeholder communication moved to archive |
| removed | Generic bullet "Responsible for team management" dropped |
| rewritten | Summary rewritten from generic to role snapshot |
| added_keyword | "product strategy" embedded in existing bullet |

### Usage

1. **User trust:** Powers "Here's what I changed" UI
2. **Refinement:** Enables "Undo this change" functionality
3. **Debugging:** When user says "this feels off," log shows exactly what happened

---

## 7. Hard Truth Rule

**If the system believes the resume cannot credibly compete, it must say so.**

### Credibility Assessment

```python
def assess_credibility(
    fit_score: int,
    signal_contract: SignalContract,
    lint_results: List[LintResult],
    level_gap: int
) -> dict:
    """
    Determine if resume can credibly compete for target role.
    """
    credibility_score = fit_score
    
    # Deductions
    if not signal_contract.is_valid():
        credibility_score -= 15
    
    high_severity_lint = len([r for r in lint_results if r.severity == "high"])
    credibility_score -= (high_severity_lint * 5)
    
    if level_gap > 1:
        credibility_score -= 20
    
    # Determine credibility level
    if credibility_score >= 70:
        credibility = "competitive"
    elif credibility_score >= 50:
        credibility = "marginal"
    else:
        credibility = "not_credible"
    
    return {
        "credibility": credibility,
        "credibility_score": credibility_score,
        "can_generate": True,  # Always allow generation
        "recommendation_downgrade": credibility == "not_credible",
        "honest_assessment": generate_honest_assessment(credibility, fit_score, level_gap)
    }
```

### Honest Assessment Messages

| Credibility | Message |
|-------------|---------|
| competitive | "Your resume positions you competitively for this role." |
| marginal | "You can apply, but address the gaps noted above to improve your odds." |
| not_credible | "This resume cannot credibly compete for this role yet. The signal gaps are significant. Consider the stepping stone roles suggested below." |

### Behavior

- **Always generate** the resume if requested
- **Downgrade recommendation** if not credible
- **Explain why** with specific gaps
- **No AI optimism** - elite candidates respect honesty

---

## Integration Summary

### Validation Pipeline

```
[Resume Customization]
        ↓
[Signal Contract Check] → Block if missing, suggest fix
        ↓
[Bullet Quality Gate] → Rank, keep top N, archive rest
        ↓
[Role Frame Inference] → Flag presentation gaps
        ↓
[Keyword Placement Check] → Skip unembeddable keywords
        ↓
[Summary Kill Switch] → Replace generic with Role Snapshot
        ↓
[Red Flag Lint] → Flag mid-market language
        ↓
[Credibility Assessment] → Honest truth if not competitive
        ↓
[Change Log] → Record all modifications
        ↓
[Export]
```

### API Response Additions

```json
{
  "signal_contract": {
    "valid": false,
    "scope_present": false,
    "impact_present": true,
    "ownership_present": true,
    "level_aligned": true,
    "blocker_message": "This resume cannot signal seniority yet. One scope indicator is missing."
  },
  "bullet_gate": {
    "kept_count": 5,
    "deprioritized_count": 3,
    "dropped_count": 2
  },
  "role_frames": [
    {
      "role": "Senior PM at Stripe",
      "problem": "scale payments infrastructure",
      "scope": "checkout conversion",
      "outcome": "revenue per transaction",
      "confidence": 0.85,
      "missing": []
    }
  ],
  "summary_status": "replaced_with_snapshot",
  "credibility": {
    "level": "marginal",
    "score": 58,
    "honest_assessment": "You can apply, but address the gaps noted above to improve your odds."
  },
  "change_log": {
    "moved_up": 3,
    "moved_down": 2,
    "removed": 2,
    "rewritten": 1,
    "keywords_added": 4
  }
}
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Signal contract pass rate (first attempt) | <50% (forces improvement) |
| Signal contract pass rate (after quick win) | >85% |
| Bullets passing quality gate | 60-70% |
| Generic summaries caught | >90% |
| User trust score (post-implementation) | >4.5/5 |
| "This feels off" complaints | <5% |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2026 | Initial quality gates spec | Product |

---

**Status:** Ready for Implementation  
**Next Review:** February 2026  
**Owner:** Product Team
