# HenryHQ Job Fit Analysis — Deployment-Ready Summary

**Status**: ✅ GREENLIT FOR DEPLOYMENT  
**Date**: December 18, 2025  
**Reviewer**: Henry (Product Owner)

---

## What Was Fixed

Two critical guardrails have been tightened based on feedback:

### Guardrail 1: "Your Move" Now Answers "What Do I Do This Week?"

**Problem**: Strategic guidance was honest but sometimes abstract. Users felt exposed but not redirected.

**Solution**: Every score band below 70% now includes concrete weekly action plan:

```
YOUR MOVE THIS WEEK:
1. Target these roles: [3 specific role titles at appropriate level]
2. Add this evidence: [1-2 specific improvements to resume/LinkedIn]
3. Deprioritize: [what to stop applying to immediately]

CLOSE THE GAP:
- Next 3 months: [specific competency to build + how]
- Next 6-12 months: [level advancement path]
- Ready when: [concrete readiness signal]
```

**Impact**: Users know exactly what to do Monday morning.

---

### Guardrail 2: Single Canonical Messaging for Inflation/Credibility

**Problem**: Different flavors of sensitive feedback. Needed one calm, repeatable HenryHQ voice.

**Solution**: Four canonical messaging patterns standardized:

#### Pattern 1: Title Inflation
```
"Hiring managers will evaluate this experience at a different scope than 
the title suggests. That gap affects senior-level competitiveness."
```

#### Pattern 2: Unverifiable Company
```
"This company cannot be validated at the scale your role implies. Hiring 
managers will evaluate your experience as individual contribution rather 
than senior leadership. Lead with verifiable scale companies in your 
positioning."
```

#### Pattern 3: Career Switcher
```
"Your background shows adjacent exposure to [function], not direct ownership. 
Senior roles require demonstrated decision-making in [specific area]."
```

#### Pattern 4: Competency Gap
```
"This role requires [required level] competencies. Your background shows 
[demonstrated level] evidence. The gap is in [specific dimensions]."
```

**Impact**: Consistent, calm tone across all sensitive feedback. No shaming, no ambiguity.

---

## Bonus Addition: Resume Leveling Page Framing

**Added**: Critical framing line for `resume-leveling.html`:

```html
<p class="framing-statement">
  This is how hiring managers level you, not how LinkedIn does.
</p>
```

**Placement**: Top of page, above level badge, before competency breakdown

**Purpose**: Sets expectations immediately. Removes defensiveness. Users understand they're getting recruiter perspective, not social validation.

---

## Updated Documents

All three implementation specs have been updated with tightened guardrails:

### 1. JOB_FIT_SCORING_SPEC.md
- ✅ Concrete "Your Move" structure added to Bands 3-5
- ✅ All examples now include 3 target roles, specific evidence to add, timeline
- ✅ Word counts adjusted (125-150 words for Band 3, 100-125 for Band 4, 75-100 for Band 5)

### 2. COMPETENCY_DIAGNOSTICS_INTEGRATION.md
- ✅ Canonical messaging patterns section added (4 patterns with never-say lists)
- ✅ Strategic action template updated with concrete weekly structure
- ✅ Example competency assessment revised with specific company names, timeline
- ✅ Frontend implementation notes added with resume-leveling framing line

### 3. BACKEND_AUDIT_REQUEST.md
- ⚠️ No changes needed (audit spec remains same)

---

## What This Means

**Before**: HenryHQ told users the truth, but sometimes left them wondering "okay, so now what?"

**After**: HenryHQ is now a referee who not only calls the game honestly but tells you exactly what play to run next.

### The Voice

This is the lane: **Truth + Direction, not encouragement theater.**

- ✅ Honest about gaps (no sugarcoating)
- ✅ Calm about sensitive topics (no shaming)
- ✅ Concrete about next steps (no abstract advice)
- ✅ Timeline-aware (3 months, 6-12 months, "ready when")

---

## Testing Requirements Before Deploy

### Test Case 1: Band 3 Output (55-69%)
**Verify**:
- [ ] Includes "YOUR MOVE THIS WEEK:" section
- [ ] Lists exactly 3 target roles with company names
- [ ] Specifies 1-2 concrete resume improvements
- [ ] States what to deprioritize

### Test Case 2: Band 4 Output (25-39%)
**Verify**:
- [ ] Includes timeline ("12-18 months to readiness")
- [ ] Lists 3 specific alternative roles
- [ ] Specifies competency to build + how
- [ ] Clear "stop applying to X immediately"

### Test Case 3: Title Inflation Messaging
**Verify**:
- [ ] Uses exact canonical phrasing
- [ ] No variations ("Your title is inflated", "This looks suspicious")
- [ ] Calm, factual tone

### Test Case 4: Resume Leveling Page
**Verify**:
- [ ] Framing line appears at top: "This is how hiring managers level you, not how LinkedIn does."
- [ ] Positioned above level badge
- [ ] Styled correctly (italic, muted color)

---

## Risk Assessment

**Low Risk**: Changes are additive (more structure, more specificity), not subtractive.

**No Breaking Changes**: Existing flows remain functional. This adds clarity without removing features.

**User Impact**: Positive. Users get more actionable guidance without any UX friction.

---

## Deployment Checklist

### Backend Changes
- [ ] Update system prompts with canonical messaging patterns
- [ ] Update strategic action templates with "YOUR MOVE THIS WEEK" structure
- [ ] Test with Jordan's resume (recruiting calculator)
- [ ] Test with Maya's resume (PM calculator, regression test)
- [ ] Test with inflated title resume (title detection)

### Frontend Changes
- [ ] Add framing line to `resume-leveling.html`
- [ ] Update strategic action display with structured sections
- [ ] Test visual layout of "YOUR MOVE" section
- [ ] Verify canonical messaging displays correctly

### QA Validation
- [ ] Run full test suite (11 test cases in JOB_FIT_SCORING_SPEC.md)
- [ ] Spot-check 5 real resumes through flow
- [ ] Verify tone consistency across all bands
- [ ] Check word counts match spec (125-150, 100-125, 75-100)

---

## Final Call

✅ **GREENLIT FOR DEPLOYMENT**

Both guardrails tightened:
1. ✅ "Your Move" answers "what do I do this week"
2. ✅ Canonical messaging standardized

Result: **HenryHQ is now a referee, not just a tool.**

Deploy when backend audit complete and calculator fix verified.

---

**Next Steps**:
1. Send BACKEND_AUDIT_REQUEST.md to Claude Code
2. Wait for BACKEND_AUDIT_RESULTS.md
3. Implement Phase 1 (calculator fix)
4. Deploy with both guardrails in place
5. Monitor user feedback on new structure

---

**Prepared by**: Claude (AI Assistant)  
**Approved by**: Henry (Product Owner)  
**Implementation**: Ready for engineering handoff
