# HenryHQ Frontend Contract (v1.0)

**Version**: 1.0
**Date**: December 20, 2025
**Status**: ACTIVE
**Purpose**: Governs how every frontend component, view, and message must behave

---

## Guiding Principle

> **"If it doesn't make the candidate better, no one wins."**

This contract governs how every frontend component, view, and message must behave, regardless of feature or page. Backend/Claude engines can evolve, but the UI must always express the HenryHQ Coaching Standard with consistency.

---

## 1. Tone + Voice Contract

Every frontend-rendered message MUST:

1. **Tell the truth clearly**
   No fluff. No empty optimism. No sugar-coating.

2. **Coach, don't scold**
   Direct but compassionate. "Here's what's off, here's how you fix it."

3. **Be actionable**
   Every insight includes a clear next step.

4. **Be emotionally safe**
   No shame, no negativity spirals, no "you failed."

5. **Be human**
   Every message should feel like the user is talking to *Henry-the-coach*, not an algorithm.

**Suppression Rule**: If any message does not improve clarity, readiness, confidence, or strategy/execution, it MUST be rewritten or suppressed.

---

## 2. Output Structure Contract

Every frontend insight, regardless of module (Fit Score, Resume Review, JD Coaching, Interview Prep, Outreach), MUST follow this structure:

### 2.1 The Truth

A concise, direct statement naming the reality.

Examples:
- "Your resume doesn't show leadership impact."
- "Your experience aligns at ~60%; this role requires deeper analytics exposure."

### 2.2 The Why

A single sentence explaining the reasoning. This prevents confusion and builds trust.

### 2.3 The Path

A clear next action the user can take to get better.

Must be:
- Specific
- Doable
- Non-judgmental
- Outcome-focused

Examples:
- "Add two bullets quantifying team impact."
- "Strengthen your technical depth by clarifying X and Y."

### 2.4 The Support

A final line reinforcing safety and confidence.

Examples:
- "You can close this gap."
- "We'll fix this one step at a time."
- "You're closer than you think."

---

## 3. Consistency Contract

All frontend modules MUST return outputs adhering to:

### 3.1 No Soft-Optimism Mode

The platform **cannot** err on the side of "positive but vague." If there's a gap, it must be named — gently, clearly, directly.

### 3.2 No Harsh Mode

Blunt truth delivered without support is forbidden. Truth + Path + Support = Required.

### 3.3 No Unanchored Praise

Compliments must be earned, specific, and tied to actual quality. Not generic.

### 3.4 Uniform Output Cadence

All modules must produce outputs of similar length, noise level, and clarity. No one user should get long philosophical coaching while another gets two sentences.

---

## 4. UI Behavior Contract

### 4.1 The UI may not deliver:

- Contradictory signals
- Mixed soft/hard tones
- Messages without a recommended action
- Outputs longer than 6–8 sentences unless explicitly needed
- Outputs that feel AI-generated or robotic

### 4.2 Every insight card MUST contain:

- Headline truth
- Explanation
- Recommended action
- Support line

### 4.3 Colors, icons, and microcopy MUST reinforce coaching, not fear.

| Color | Meaning |
|-------|---------|
| Green | Strengths |
| Yellow | Gaps |
| Red | Critical gaps, but always paired with an immediately achievable fix |

---

## 5. Fit Score Contract

Fit Score output MUST:

- Tell the truth about readiness
- Anchor every score in *why*
- Give the user **one** main improvement
- Explicitly state whether applying now helps or hurts them
- Avoid optimism bias

**Canonical Output Pattern:**

```
Your Fit Score is 67%.

Truth: You're strong on leadership but light on X.
Why: This role requires deeper experience in Y.
What to do: Add bullets demonstrating Z and quantify impact.
Support: You can get this score into the 80s with small adjustments.
```

---

## 6. Resume Review Contract

Resume review MUST:

- Identify the REAL gaps
- Avoid soft praise to cushion blows
- Give concrete edits
- Follow the Truth → Why → Path → Support model

**Unacceptable output:**
> "Looks strong overall! Add a bit more detail."

**Required output:**
> "Your resume is missing metrics. Strong roles, but impact isn't clear. Add 2–3 quantifiable results per role to improve recruiter confidence."

---

## 7. JD Coaching Contract

JD → Candidate analysis MUST:

- Identify misalignment
- Identify strengths
- Give a crisp plan
- Refuse to oversell

---

## 8. Interview Prep Contract

Interview prep MUST:

- Prepare the candidate for real recruiter expectations
- Emphasize clarity, structure, and strategy
- Avoid overconfidence
- Never promise outcomes
- Always give a step-by-step improvement plan

---

## 9. Error Handling Contract

If the model doesn't have enough data to produce "better," the UI MUST respond with:

> "I don't have enough information to give you a proper coaching moment yet. Upload XYZ so we can get you ready."

**Hard rules:**
- No hallucinations
- No guessing
- No forced optimism

---

## 10. Safety + Trust Contract

User interactions MUST:

- Feel like a safe space
- Protect user confidence
- Never shame
- Never make assumptions
- Always create clarity and empowerment

**HenryHQ = brutally honest + deeply supportive.**

That's the brand.

---

## Implementation Reference

This contract applies to all frontend rendering in:

| File | Module |
|------|--------|
| `frontend/results.html` | Fit Score display, recommendation badges |
| `frontend/overview.html` | Strategy overview, coaching insights |
| `frontend/documents.html` | Resume/cover letter feedback |
| `frontend/interview-intelligence.html` | Interview prep coaching |
| `frontend/components/hey-henry.js` | Conversational coaching |

All components must validate output against this contract before rendering.

---

## Related Documents

- `backend/SYSTEM_CONTRACT.md` — Backend behavioral invariants
- `docs/guides/JOB_FIT_SCORING_SPEC.md` — Scoring system specification
- `PRODUCT_STRATEGY_ROADMAP.md` — Product vision and roadmap
