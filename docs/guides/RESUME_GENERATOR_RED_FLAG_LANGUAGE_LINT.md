# Red Flag Language Lint Specification

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Ready for Implementation  
**Owner:** Product Team

---

## Purpose

Senior candidates get quietly downgraded by mid-market language that sounds fine but signals junior positioning. This lint runs before resume output and flags phrases that weaken senior signal.

**Core Test:** If a sentence can apply to 1,000 LinkedIn profiles, it fails. If it doesn't answer "what broke if you weren't there?", it fails.

---

## Red Flag Phrases

### Tier 1: Kill on Sight

These phrases add zero signal. Remove or rewrite every time.

| Phrase | Why It Fails | Rewrite Direction |
|--------|--------------|-------------------|
| "Results-driven" | Says nothing, universal filler | Delete entirely, lead with actual result |
| "Passionate about" | Emotion, not evidence | Delete, show passion through outcomes |
| "Motivated professional" | Generic self-description | Delete, let work speak |
| "Team player" | Table stakes, not differentiator | Delete or specify collaboration outcome |
| "Detail-oriented" | Claim without proof | Delete or show detail in the work itself |
| "Excellent communication skills" | Everyone claims this | Delete, demonstrate through stakeholder outcomes |
| "Proven track record" | Assertion without evidence | Delete, show the track record instead |
| "Dynamic" | Meaningless adjective | Delete |
| "Synergies" / "Leveraged synergies" | Consultant bingo | Delete, specify what was actually combined |
| "Value-add" | Corporate jargon | Delete, state the value directly |

### Tier 2: Passive/Junior-Coded

These phrases signal contribution without ownership. Rewrite to show decision authority.

| Phrase | Why It Fails | Rewrite Pattern |
|--------|--------------|-----------------|
| "Responsible for" | Passive, job description language | "Owned [X]" or "Led [X]" |
| "Helped drive" | Who owned the decision? | "Drove [X]" or "Led [X], resulting in..." |
| "Worked on" | Contribution without ownership | "Built [X]" or "Shipped [X]" |
| "Supported" | Adjacent, not accountable | "Enabled [X] by [specific action]" or reframe to owned outcome |
| "Assisted with" | Junior positioning | "Co-led [X]" or specify owned component |
| "Was involved in" | Observer language | State specific role and decision authority |
| "Contributed to" | Hides level of ownership | Specify what you owned within the contribution |
| "Participated in" | Passive observer | State what you decided or delivered |

### Tier 3: Vague Scope Hiders

These phrases obscure seniority signals. Replace with specifics.

| Phrase | Why It Fails | Rewrite Pattern |
|--------|--------------|-----------------|
| "Various stakeholders" | Hides level, could be anyone | Name the levels: "VPs across Product, Eng, and Design" |
| "Cross-functional collaboration" | Table stakes, not signal | Specify who, what decision, what outcome |
| "Multiple teams" | How many? What scope? | "4 engineering teams (35 engineers)" |
| "Large-scale" | Relative, unverifiable | Quantify: "$50M budget" or "2M users" |
| "Fast-paced environment" | Meaningless without stakes | "Shipped 12 features in 6 months under Series B pressure" |
| "End-to-end" (alone) | Must specify what end-to-end means | "End-to-end ownership from discovery through launch and post-launch optimization" |
| "Key initiatives" | Which ones? What made them key? | Name the initiative and its business impact |
| "Strategic projects" | Vague importance claim | Specify the strategy and your decision authority |

### Tier 4: Exposure Without Ownership

These phrases read as observer, not operator. Flag for career switcher detection.

| Phrase | Why It Fails | Rewrite Pattern |
|--------|--------------|-----------------|
| "Exposure to" | Observer, not operator | If you operated, say what you did; if not, remove |
| "Familiar with" | Learning, not doing | Remove or upgrade to demonstrated usage |
| "Knowledge of" | Passive awareness | Show application, not awareness |
| "Understanding of" | Academic, not applied | Demonstrate through outcomes |
| "Experience with" (alone) | Weak without specifics | Add what you built, shipped, or decided |

---

## Lint Rules

### Rule 1: LinkedIn Test

```python
def fails_linkedin_test(sentence: str) -> bool:
    """
    If this sentence could appear on 1,000+ LinkedIn profiles unchanged,
    it provides no differentiation signal.
    """
    generic_patterns = [
        r"results-driven",
        r"passionate about",
        r"team player",
        r"excellent communication",
        r"proven track record",
        r"detail-oriented",
        r"motivated professional",
        r"dynamic",
        r"fast-paced environment",
        r"cross-functional collaboration",
    ]
    return any(re.search(pattern, sentence.lower()) for pattern in generic_patterns)
```

### Rule 2: Ownership Test

```python
def fails_ownership_test(sentence: str) -> bool:
    """
    If the sentence doesn't answer "what broke if you weren't there?",
    it lacks ownership signal.
    """
    passive_patterns = [
        r"\bresponsible for\b",
        r"\bhelped (drive|build|create|develop|launch)\b",
        r"\bworked on\b",
        r"\bsupported\b",
        r"\bassisted with\b",
        r"\bwas involved in\b",
        r"\bcontributed to\b",
        r"\bparticipated in\b",
    ]
    return any(re.search(pattern, sentence.lower()) for pattern in passive_patterns)
```

### Rule 3: Vague Scope Test

```python
def fails_scope_test(sentence: str) -> bool:
    """
    If scope is described with adjectives instead of numbers,
    it hides seniority signals.
    """
    vague_scope_patterns = [
        r"\bvarious stakeholders\b",
        r"\bmultiple teams\b",
        r"\blarge-scale\b",
        r"\bkey initiatives\b",
        r"\bstrategic projects\b",
        r"\bend-to-end\b(?!.*(?:from|through|including))",  # end-to-end without specifics
    ]
    return any(re.search(pattern, sentence.lower()) for pattern in vague_scope_patterns)
```

### Rule 4: Observer Test

```python
def fails_observer_test(sentence: str) -> bool:
    """
    If the sentence positions the candidate as observer rather than operator,
    it signals adjacent experience, not ownership.
    """
    observer_patterns = [
        r"\bexposure to\b",
        r"\bfamiliar with\b",
        r"\bknowledge of\b",
        r"\bunderstanding of\b",
    ]
    return any(re.search(pattern, sentence.lower()) for pattern in observer_patterns)
```

---

## Implementation

### Lint Function

```python
from dataclasses import dataclass
from typing import List, Tuple
import re

@dataclass
class LintResult:
    bullet: str
    bullet_index: int
    role: str
    failures: List[str]
    severity: str  # "high" | "medium" | "low"
    rewrite_suggestion: str

def lint_resume_bullets(resume: dict) -> Tuple[List[LintResult], str]:
    """
    Run all lint rules against resume bullets.
    Returns list of flagged bullets and summary warning.
    """
    results = []
    
    for role in resume.get("experience", []):
        role_title = role.get("title", "Unknown Role")
        for i, bullet in enumerate(role.get("bullets", [])):
            failures = []
            
            if fails_linkedin_test(bullet):
                failures.append("linkedin_test")
            if fails_ownership_test(bullet):
                failures.append("ownership_test")
            if fails_scope_test(bullet):
                failures.append("scope_test")
            if fails_observer_test(bullet):
                failures.append("observer_test")
            
            if failures:
                severity = classify_severity(failures)
                suggestion = generate_rewrite_suggestion(bullet, failures)
                results.append(LintResult(
                    bullet=bullet,
                    bullet_index=i,
                    role=role_title,
                    failures=failures,
                    severity=severity,
                    rewrite_suggestion=suggestion
                ))
    
    # Generate summary warning
    if not results:
        warning = None
    elif len(results) == 1:
        warning = "1 bullet reads mid-market and weakens senior signal. Recommend rewrite."
    else:
        warning = f"{len(results)} bullets read mid-market and weaken senior signal. Recommend rewrite."
    
    return results, warning

def classify_severity(failures: List[str]) -> str:
    """
    Classify severity based on failure types.
    """
    if "linkedin_test" in failures:
        return "high"  # Generic filler is worst
    if "ownership_test" in failures:
        return "high"  # Passive language is critical for senior roles
    if "observer_test" in failures:
        return "medium"  # May indicate career switcher
    return "low"  # Vague scope is fixable
```

### Rewrite Suggestion Generator

```python
def generate_rewrite_suggestion(bullet: str, failures: List[str]) -> str:
    """
    Generate specific rewrite guidance based on failure type.
    """
    suggestions = []
    
    if "linkedin_test" in failures:
        suggestions.append("Remove generic filler. Lead with the outcome.")
    
    if "ownership_test" in failures:
        suggestions.append("Replace passive language with ownership verbs (Owned, Led, Built, Shipped).")
    
    if "scope_test" in failures:
        suggestions.append("Replace adjectives with numbers (team size, budget, users, revenue).")
    
    if "observer_test" in failures:
        suggestions.append("If you operated, state what you decided or delivered. If you only observed, consider removing.")
    
    return " ".join(suggestions)
```

---

## UI Integration

### Warning Display

When lint flags bullets, surface in the "Here's what I changed" section:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  Senior Signal Check                                        │
│  ───────────────────────────────────────────────────────────    │
│                                                                 │
│  3 bullets read mid-market and weaken senior signal.            │
│                                                                 │
│  • "Responsible for managing cross-functional collaboration"    │
│    → Replace "Responsible for" with ownership verb              │
│    → Specify who you influenced and the outcome                 │
│                                                                 │
│  • "Helped drive strategic initiatives across various teams"    │
│    → "Helped drive" hides decision authority                    │
│    → "Various teams" hides scope                                │
│                                                                 │
│  • "Exposure to product strategy and roadmap planning"          │
│    → "Exposure to" reads as observer, not operator              │
│    → State what you decided or delivered                        │
│                                                                 │
│  [Auto-fix these] [Show me the rewrites] [Keep as-is]           │
└─────────────────────────────────────────────────────────────────┘
```

### Severity Indicators

| Severity | Color | Icon | Action |
|----------|-------|------|--------|
| High | Red | 🔴 | Block download until addressed or acknowledged |
| Medium | Orange | 🟠 | Warning, recommend fix |
| Low | Yellow | 🟡 | Suggestion only |

---

## Auto-Rewrite Rules

When user clicks "Auto-fix these", apply these transformations:

### Pattern Replacements

```python
AUTO_REWRITES = {
    # Tier 1: Delete entirely
    r"\bresults-driven\s*": "",
    r"\bpassionate about\s*": "",
    r"\bteam player\b": "",
    r"\bdetail-oriented\s*": "",
    r"\bdynamic\s*": "",
    
    # Tier 2: Upgrade passive to active
    r"\bresponsible for\b": "Owned",
    r"\bhelped drive\b": "Drove",
    r"\bhelped build\b": "Built",
    r"\bhelped create\b": "Created",
    r"\bworked on\b": "Built",
    r"\bassisted with\b": "Supported",  # Then flag for manual review
    
    # Tier 3: Flag for manual review (can't auto-fix without context)
    # "various stakeholders" -> needs human input on who
    # "multiple teams" -> needs human input on count
    # "large-scale" -> needs human input on numbers
}
```

### Post-Rewrite Validation

After auto-rewrite, re-run lint to catch:
1. Awkward phrasing from simple replacement
2. Remaining flags that need manual attention
3. New issues introduced by rewrite

---

## Integration with Resume Customization

### When to Run Lint

1. **After resume parse** - Flag issues in original resume
2. **After customization** - Ensure tailoring didn't introduce mid-market language
3. **Before download** - Final quality gate

### Lint in API Response

Add to `/api/resume/customize` response:

```json
{
  "lint_results": {
    "warning": "3 bullets read mid-market and weaken senior signal. Recommend rewrite.",
    "flagged_count": 3,
    "flagged_bullets": [
      {
        "role": "Senior Product Manager",
        "bullet_index": 2,
        "bullet": "Responsible for managing cross-functional collaboration",
        "failures": ["ownership_test", "scope_test"],
        "severity": "high",
        "suggestion": "Replace passive language with ownership verbs. Specify who you influenced and the outcome."
      }
    ],
    "auto_fixable_count": 1
  }
}
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Bullets flagged per resume (avg) | 2-5 |
| Auto-fix acceptance rate | >60% |
| Manual rewrite completion rate | >40% |
| Post-lint fit score improvement | +5-10% |
| User feedback on lint helpfulness | >4/5 |

---

## Testing

### Test Cases

```python
def test_linkedin_filler():
    assert fails_linkedin_test("Results-driven professional with proven track record")
    assert not fails_linkedin_test("Increased ARR from $2M to $8M in 18 months")

def test_passive_ownership():
    assert fails_ownership_test("Responsible for product roadmap")
    assert fails_ownership_test("Helped drive revenue growth")
    assert not fails_ownership_test("Owned product roadmap for payments platform")

def test_vague_scope():
    assert fails_scope_test("Collaborated with various stakeholders")
    assert fails_scope_test("Led multiple teams on key initiatives")
    assert not fails_scope_test("Led 4 teams (32 engineers) on payment processing migration")

def test_observer_language():
    assert fails_observer_test("Exposure to product strategy")
    assert fails_observer_test("Familiar with agile methodologies")
    assert not fails_observer_test("Defined product strategy for $50M revenue line")
```

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2026 | Initial spec | Product |

---

**Status:** Ready for Implementation  
**Next Review:** February 2026  
**Owner:** Product Team
