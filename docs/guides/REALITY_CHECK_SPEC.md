# HenryHQ Reality Check System - Product Specification

**Version:** 1.0  
**Last Updated:** December 20, 2025  
**Status:** Approved for Implementation  
**Owner:** Product Team

---

## Executive Summary

The Reality Check System is HenryHQ's market-truth intervention framework. It surfaces risk, friction, and market behavior patterns early enough for candidates to make informed strategic decisions. Reality Checks never modify fit scores, never reward bias, and never fabricate advantage. They exist to tell candidates the truth about market dynamics without endorsing unfair patterns.

**Core Principle:** Transparency over false hope. Strategy over suppression.

---

## 1. Purpose & Philosophy

### What Reality Checks Are

Market-truth interventions that help candidates make informed decisions about where to invest time, effort, and emotional energy in their job search.

### What Reality Checks Are NOT

- Score modifiers or boosters
- Eligibility gates (unless explicitly defined)
- Moral judgments about candidate worth
- Values filters that suppress identity
- Hidden penalties that degrade output quality

### Design Philosophy

HenryHQ doesn't pretend bias doesn't exist. It doesn't reward it either. It names it, contains it, and gives candidates strategic leverage.

---

## 2. Severity Levels

### Blocker

**Purpose:** Prevents action due to fundamental misalignment  
**Use Cases:** Eligibility failures, fabrication risk, terminal gaps  
**Example:** "Do Not Apply" recommendation  
**UI Treatment:** Red, clear stop signal  
**User Override:** Not allowed for eligibility and fabrication blockers. May be allowed for severe fit mismatches (e.g., "Do Not Apply" based on fit score alone).

### Warning

**Purpose:** Strong discouragement with accountability  
**Use Cases:** Significant gaps, credibility concerns, high competition  
**Example:** "Apply with Caution" recommendation  
**UI Treatment:** Orange/amber, explicit acknowledge-to-proceed  
**User Override:** Allowed with explicit acknowledgment

### Coaching

**Purpose:** Strategic guidance to improve positioning  
**Use Cases:** Reframing opportunities, prioritization advice, timing guidance  
**Example:** "Conditional Apply" with specific conditions  
**UI Treatment:** Blue/informational, actionable recommendations  
**User Override:** Not applicable (guidance only)

### Informational

**Purpose:** Context provision without behavioral change  
**Use Cases:** Market insights, industry patterns, company culture signals  
**Example:** "This company values consulting backgrounds"  
**UI Treatment:** Neutral gray, non-intrusive  
**User Override:** Not applicable (information only)

---

## 3. Placement & Visibility

Reality Checks may appear in:

1. **Job Analysis Results** - Primary placement after fit scoring
2. **"Your Move" Section** - Strategic recommendations
3. **Resume Leveling** - Scope and credibility assessments
4. **LinkedIn Scoring** - Profile optimization guidance
5. **Interview Prep** - Risk mitigation strategies
6. **Dashboard/Tracker** - Application-level warnings
7. **Hey Henry Proactive Nudges** - Contextual coaching

**Critical Rule:** Reality Checks must NEVER silently change outcomes or scores.

---

## 4. Tone & Messaging Standards

### Approved Framing

**Objective & Protective:**
> "This affects screening behavior, not capability."

**Market-Aware:**
> "In the current hiring climate, some companies scrutinize [X] more heavily."

**Strategic:**
> "If you proceed, referrals and signal density matter more here."

**Evidence-Based:**
> "Companies with [pattern] typically filter for [requirement]."

### Forbidden Framing

❌ "You shouldn't mention this"  
❌ "This is a weakness"  
❌ "Hiring managers don't like people like you"  
❌ "Hide your background"  
❌ "You're not qualified for this"

### Tone Principles

1. **Direct, not shaming** - State market reality without judgment
2. **Protective, not prescriptive** - Warn about friction without dictating identity
3. **Strategic, not defeatist** - Provide paths forward, not just obstacles
4. **Explanatory, not judgmental** - Explain market behavior, don't endorse it

---

## 5. Signal Classes

Reality Checks are triggered by six distinct Signal Classes. Each has strict boundaries and allowed outputs.

### 5.1 Eligibility Signals

**Purpose:** Enforce hard requirements  

**Examples:**
- Missing required domain expertise
- Seniority mismatch (Director role, IC experience)
- Non-transferable ownership gaps
- Work authorization requirements
- Education/certification mandates

**Allowed Outputs:** Blocker only  
**Forbidden:** Coaching-only handling without clear path to eligibility  

**Example:**
> "This role requires PMP certification and you don't have it. This is an automatic filter. Do Not Apply unless you plan to get certified first."

---

### 5.2 Fit Signals

**Purpose:** Match experience quality and quantity to role requirements  

**Examples:**
- Fit score below 40% threshold
- Skill alignment gaps
- Experience level mismatch
- Scope disconnect

**Critical Rule:** Internships never count toward years of experience. This applies to all experience calculations regardless of internship quality or duration.

**Allowed Outputs:** Warning, Coaching  
**Forbidden:** Market bias commentary, identity-based guidance  

**Example:**
> "Your fit score is 38% (below our 40% threshold). Your skills are strong, but you're missing 3+ years of required experience. Conditional Apply: only if you have exceptional referrals."

---

### 5.3 Credibility Signals

**Purpose:** Assess believability of scope and achievement claims  

**Examples:**
- Title inflation ("CEO" of 2-person startup)
- Implausible metrics ($50M revenue at seed stage)
- Press-release resume language
- Scope mismatches (VP title, coordinator responsibilities)

**Allowed Outputs:** Warning, Coaching  
**Forbidden:** Moral judgment, accusation of lying  

**Example:**
> "Your 'VP Product' title at a 5-person startup may trigger credibility questions. Consider leading with scope and outcomes rather than title in your positioning."

---

### 5.4 Risk Signals

**Purpose:** Identify patterns that raise recruiter skepticism  

**Examples:**
- Job hopping (4+ jobs in 2 years)
- Unexplained career gaps
- Overqualification
- Lateral moves after senior roles
- Industry pivots

**Allowed Outputs:** Warning, Coaching  
**Forbidden:** Automatic disqualification unless paired with eligibility failure  

**Example:**
> "You've had 4 roles in 24 months. Recruiters will ask about stability. Your cover letter should proactively address this with a cohesive narrative."

---

### 5.5 Market Bias Signal 🔴 CRITICAL

**Purpose:** Expose hiring market preferences WITHOUT endorsing them  

**Definition:** Patterns in job descriptions or company behavior that indicate narrow background preferences unrelated to capability.

**Inputs (Examples):**
- Selective school name-dropping (e.g., "Ivy League preferred")
- Employer brand clustering ("Ex-FAANG only")
- Narrow leadership background homogeneity
- "Culture fit" proxies
- Geographic or industry bias patterns

**STRICT RULES:**

1. **NEVER modifies fit_score**
2. **NEVER boosts candidates who match the bias**
3. **NEVER penalizes non-traditional paths**
4. **NEVER instructs identity suppression**
5. **ALWAYS names the pattern explicitly**
6. **ALWAYS provides strategic alternatives**

**Allowed Outputs:**
- Coaching overlays
- "Your Move" strategy adjustments
- Outreach and referral emphasis
- Application prioritization guidance

**Forbidden Outputs:**
- Fit score adjustments
- Eligibility changes
- Resume content suppression
- Identity-based filtering

**Approved Copy Template:**

> "**Market Bias Signal:** This role shows preference for [specific pattern]. This affects screening speed, not capability. Your background is strong. If you proceed: [strategic alternatives]."

**Examples:**

**School Bias:**
> "Market Bias Signal: This company strongly favors Ivy League backgrounds in their hiring patterns. This affects resume screening, not your capability. If you proceed, prioritize referrals from current employees and emphasize outcomes over credentials."

**Brand Bias:**
> "Market Bias Signal: This role's language suggests preference for FAANG experience. Your startup background is equally valid. If you proceed, lead with scale and impact metrics that translate across contexts."

---

### 5.6 Market Climate Signal 🔴 CRITICAL

**Purpose:** Reflect current political, regulatory, and social hiring headwinds WITHOUT endorsing them  

**Definition:** Temporary market conditions that create friction for certain types of experience, not based on capability.

**Inputs (Examples):**
- DEI-focused roles or language during political backlash
- Climate/sustainability work during regulatory uncertainty
- Political advocacy or campaign work
- Industry sensitivity by time period (e.g., crypto in 2023, cannabis in conservative states)
- Regulatory role emphasis during compliance crackdowns

**STRICT RULES:**

1. **NEVER blocks by itself**
2. **NEVER changes eligibility or fit scoring**
3. **NEVER instructs identity suppression**
4. **NEVER suggests hiding legitimate work**
5. **ALWAYS validates the work's importance**
6. **ALWAYS frames as market friction, not personal failing**

**Allowed Outputs:**
- Framing guidance (outcomes first, identity-neutral language)
- Resume and cover letter prioritization advice
- Company targeting strategy
- Application timing recommendations

**Important:** Framing guidance may prioritize outcomes over identity-focused language, but must not prescribe exact word substitutions. Strategic advice, not résumé micromanagement.

**Forbidden Outputs:**
- Fit score penalties
- Experience discrediting
- Work history omission instructions
- Values-based filtering

**Approved Copy Template:**

> "**Market Climate Signal:** In the current hiring climate, some companies are scrutinizing [type of work] more heavily due to [external factor]. Your work is valid and valuable. Strategic framing: [specific guidance]."

**Examples:**

**DEI Roles:**
> "Market Climate Signal: In the current political climate, some companies are reducing emphasis on DEI-titled roles. Your work driving inclusion and belonging is legitimate business impact. Strategic framing: Lead with business outcomes (retention, engagement, performance) and team effectiveness metrics. This reduces early screening friction without hiding your work."

**Climate/Sustainability:**
> "Market Climate Signal: Some companies are currently de-prioritizing climate-focused initiatives due to regulatory uncertainty. Your sustainability work demonstrates strategic thinking and stakeholder management. Strategic framing: Emphasize cost savings, operational efficiency, and risk mitigation over mission-driven language."

**Political Work:**
> "Market Climate Signal: Campaign and advocacy work can trigger political concerns in some hiring contexts. Your organizing and coalition-building skills are directly transferable. Strategic framing: Lead with project management, stakeholder alignment, and measurable outcomes. Let the substance speak for itself."

---

## 6. Forbidden Interactions (Hard Guardrails)

Reality Checks may **NEVER**:

1. Change `fit_score` calculation
2. Alter Career Evidence Categories (CEC) thresholds
3. Inflate leadership credit to offset bias
4. Count internships as years of experience
5. Create hidden score boosts or penalties
6. Rewrite candidate identity or background
7. Suppress legitimate work experience
8. Modify ATS keyword requirements
9. Adjust experience penalty calculations
10. Override backend safety nets (hard caps)

**Enforcement:** These guardrails are validated in post-processing. Any Reality Check that violates these rules triggers a system error and blocks the response.

---

## 7. Accountability & User Override

### When User Proceeds Despite Warning

If a user chooses to apply despite a Warning-level Reality Check:

**System Behavior:**
1. Show explicit acknowledgment modal
2. Continue optimizing materials **within the constraint**
3. Never punish or degrade output quality
4. Never insert passive-aggressive language
5. Track override for analytics (learn from patterns)

**Example Acknowledgment:**

> "Got it. You're proceeding with this application despite the low fit score. I'll optimize your positioning within the constraints we identified. Here's your strategy..."

### When User Requests Explanation

Reality Checks must always provide transparent reasoning when asked:

- Cite specific job description language
- Reference market data or patterns
- Explain the screening behavior, not the candidate's worth
- Offer strategic alternatives

---

## 8. Implementation Requirements

### Data Structure

```json
{
  "reality_check": {
    "signal_class": "market_bias",
    "severity": "warning",
    "trigger": "School selectivity pattern detected in JD",
    "message": "Market Bias Signal: This role shows preference for...",
    "strategic_alternatives": [
      "Prioritize employee referrals",
      "Lead with outcomes over credentials",
      "Apply within first 48 hours"
    ],
    "allowed_outputs": ["coaching", "outreach_emphasis"],
    "forbidden_outputs": ["fit_score_modification", "eligibility_change"]
  }
}
```

### Validation Checklist

Before any Reality Check fires:

- [ ] Signal class explicitly declared
- [ ] Severity level specified
- [ ] Trigger condition documented
- [ ] Allowed outputs verified
- [ ] Forbidden interactions checked
- [ ] Tone standards validated
- [ ] Strategic alternatives provided (if Warning/Coaching)

---

## 9. Single Source of Truth

All Reality Checks must:

1. **Declare signal class** - One of six defined classes
2. **Declare severity** - Blocker, Warning, Coaching, or Informational
3. **Declare allowed outputs** - Explicit list of permitted responses
4. **Declare forbidden outputs** - Explicit list of prohibited behaviors
5. **Provide evidence** - Cite specific triggers or patterns
6. **Offer alternatives** - When blocking or warning, provide strategic path forward

**No silent logic. No vibes-based branching. No implicit penalties.**

---

## 10. Testing & Validation

### Unit Tests

Each signal class must have:
- Trigger condition tests (when should it fire)
- Non-trigger tests (when should it NOT fire)
- Severity escalation tests
- Forbidden interaction tests (ensure no score modification)

### Integration Tests

- Reality Check + Fit Score (verify no cross-contamination)
- Reality Check + Document Generation (verify no quality degradation)
- Reality Check + User Override (verify graceful continuation)

### User Acceptance Tests

- Test copy with diverse candidate backgrounds
- Validate tone is protective, not shaming
- Confirm strategic alternatives are actionable
- Verify no identity suppression language

---

## 11. Monitoring & Iteration

### Metrics to Track

1. **Reality Check Frequency** - How often each signal fires
2. **User Override Rate** - How often users proceed despite warnings
3. **Application Success Rate** - Do Reality Checks correlate with outcomes
4. **User Feedback** - Qualitative responses to Reality Check messaging

### Review Cadence

- **Weekly:** Monitor new signal patterns
- **Monthly:** Review override patterns and outcomes
- **Quarterly:** Audit tone and messaging standards
- **Annually:** Re-validate market climate signals against current reality

---

## 12. Escalation & Edge Cases

### When Multiple Signals Fire

**Priority Order:**
1. Eligibility Signals (blockers first)
2. Fit Signals (core matching)
3. Credibility Signals (if affecting strategy)
4. Risk Signals (if significant)
5. Market Bias Signals (if applicable)
6. Market Climate Signals (context only)

**Display Rule:** Show maximum 2 Reality Checks per analysis. Prioritize by severity, then by signal class order. Market Bias and Market Climate signals may never be the only Reality Check shown—they must be paired with Fit, Eligibility, Credibility, or Risk signals to maintain focus on capability over context.

### When Signals Conflict

If a Market Bias Signal would boost and a Fit Signal would warn:
- **Fit Signal takes precedence** (reality check on bias)
- Display both with clear separation
- Emphasize that bias doesn't create capability

### Unknown Patterns

When encountering a new pattern not covered by existing signals:
- Log for manual review
- Default to Informational severity
- Do not modify scores or eligibility
- Flag for product team review

---

## 13. Future Enhancements

### Planned Additions

1. **Company-Specific Signals** - Historical hiring pattern data
2. **Industry Trend Signals** - Sector-level hiring climate tracking
3. **Geographic Signals** - Location-based market dynamics
4. **Timing Signals** - Hiring cycle and budget season awareness

### Under Consideration

- User-configurable Reality Check sensitivity
- Industry-specific signal calibration
- Historical outcome correlation analysis

---

## Appendix A: Quick Reference

### Signal Class Decision Tree

```
Is this about basic eligibility? → Eligibility Signal
Is this about experience matching? → Fit Signal
Is this about claim believability? → Credibility Signal
Is this about candidate history patterns? → Risk Signal
Is this about hiring preference bias? → Market Bias Signal
Is this about external market conditions? → Market Climate Signal
```

### Severity Decision Tree

```
Does this prevent application entirely? → Blocker
Does this strongly discourage application? → Warning
Does this suggest strategic adjustment? → Coaching
Does this provide helpful context only? → Informational
```

---

## Appendix B: Copy Examples by Signal Class

### Eligibility Signal (Blocker)

> "This role requires active security clearance. You don't have one, and clearances can't be obtained independently. **Do Not Apply.** Focus on roles that don't require clearance or look for companies willing to sponsor."

### Fit Signal (Warning)

> "Your fit score is 35% (below our 40% threshold). You're missing 4+ years of required experience and 2 critical technical skills. **Apply with Caution.** Only proceed if you have exceptional referrals or inside connections."

### Credibility Signal (Coaching)

> "Your title progression (IC → Director → VP in 18 months at early-stage startups) may trigger credibility questions. This doesn't mean your work wasn't real—just that recruiters will scrutinize it. **Strategic framing:** Lead with scope, team size, and outcomes rather than titles."

### Risk Signal (Coaching)

> "You've had 5 roles in 3 years. Recruiters will ask about stability. Your work shows clear skill progression, not just job hopping. **Strategic framing:** Create a narrative arc in your cover letter that explains the transitions as strategic career building."

### Market Bias Signal (Warning)

> "**Market Bias Signal:** This company's hiring patterns show strong preference for candidates from 5 specific companies (all enterprise SaaS). This affects resume screening, not your capability. **If you proceed:** Prioritize employee referrals, apply within first 24 hours, and lead with metrics that translate across company scales."

### Market Climate Signal (Informational)

> "**Market Climate Signal:** The current political climate has some companies reducing emphasis on DEI-focused roles and language. Your work building inclusive cultures is legitimate business impact. **Strategic framing:** Lead with retention rates, engagement scores, and team performance improvements. Let the outcomes demonstrate the value."

---

**Document Status:** Approved for implementation  
**Next Review:** Q1 2026  
**Change Log:** See Git history
