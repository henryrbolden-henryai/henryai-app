# SYSTEM CONTRACT BLOCK

**Job Fit Analysis Engine — Non-Negotiable Constraints**

> **"If it doesn't make the candidate better, no one wins."**

This contract defines the hard constraints that govern HenryAI's behavior. These are not suggestions—they are architectural invariants that protect candidate outcomes. The system is opinionated by design: it refuses to support mass-apply behavior, refuses to fabricate experience, and refuses to override market reality to preserve optimism.

---

## 0. Core Invariant: Candidate Improvement

All HenryHQ outputs must satisfy the following condition:

> **If it doesn't make the candidate better, no one wins.**

"Better" means:
- Improved clarity about market reality
- Better decision-making and prioritization
- Stronger positioning, skill development, or strategy
- Reduced wasted effort or false optimism

This invariant **supersedes**:
- Encouragement for its own sake
- Engagement-driven output
- User preference for reassurance
- Optimistic framing that obscures reality

HenryHQ prioritizes long-term candidate improvement over short-term comfort.

This invariant is **binding** and equivalent in weight to:
- No fabrication (§5, §8)
- Final recommendation immutability (§6)
- Trust Principle (§10)

---

## 1. Stateless Candidate Isolation

Each analysis run must be fully stateless at the **candidate level**.

* Resume data, extracted strengths, gaps, narratives, coaching language, and recommendations **must not persist** beyond the current analysis.
* No candidate-derived signal may influence any future run.
* Each run must be treated as a sealed execution environment.

---

## 2. Allowed Persistent State (Global Only)

The following are the **only** elements permitted to persist across runs:

* Leveling frameworks
* Role taxonomy (e.g., Engineering, Product, Data)
* Scoring weights by level and role
* General leadership heuristics
* System controllers and decision logic

All persistent state must be **candidate-agnostic**.

---

## 3. JD-Scoped vs Candidate-Scoped Data

Data must be strictly separated:

**JD-Scoped (Ephemeral, Per Run)**

* Role requirements
* Domain expectations
* Tooling and stack emphasis
* Capability definitions
* Evaluation criteria

**Candidate-Scoped (Ephemeral, Per Run)**

* Resume evidence
* Strengths
* Gaps
* Dominant narrative
* Coaching language
* "Your Move" guidance

Candidate-scoped data must be discarded immediately after output rendering.

---

## 4. Explicit Ban on Candidate → Global Promotion

Candidate-derived signals must **never**:

* Be added to shared keyword lists
* Modify role signal profiles
* Influence scoring weights
* Affect future analyses

If a signal is not present in the **job description**, it cannot influence role scoring or narrative priority.

---

## 5. JD-First Narrative Ordering

All narrative and coaching output must follow this order:

1. JD-required capability + explicit resume evidence
2. JD-adjacent transferable capability + resume evidence
3. Leadership narrative **only as fallback**

If Step 1 exists, Step 3 is not allowed.

Generic leadership language must never override role-specific evidence.

---

## 6. Decision Authority Lock

Only the **Final Recommendation Controller** may set:

* Apply
* Conditional Apply
* Pass

All other systems (CEC, CAE, LEPE, Coaching) are **advisory only** and must not override or influence the final decision.

---

## 7. Analysis ID Enforcement

Each run must generate a unique `analysis_id`.

* All extracted data must be tagged to this ID.
* No data may be accessed outside its originating `analysis_id`.
* All tagged data must be destroyed at completion.

---

## 8. Strength Extraction Failure Handling

If zero strengths are extracted:

* Coaching generation must halt.
* No fallback narratives are permitted.
* An internal error must be surfaced.

Fallbacks are prohibited as they mask data integrity issues.

---

## 9. No Cross-Candidate Memory

The system must not:

* Learn from prior candidates
* Reuse phrasing patterns
* Infer defaults from previous runs

Every output must be earned **solely** from the current JD and resume.

---

## 10. Trust Principle

This system exists to deliver **honest, candidate-specific, role-specific guidance**.

If evidence is missing, say so.
If alignment is partial, reflect it accurately.
Never optimize for reassurance at the expense of truth.

**The goal is not convenience—it's better decision-making that compounds.**

HenryAI teaches candidates how recruiters think. Every honest assessment, every hard constraint, every locked recommendation exists to build positioning instincts that transfer to every future job search. Comfortable fiction helps no one.

---

## Implementation Reference

See these files for enforcement:

- `backend/recommendation/final_controller.py` - Decision Authority Lock (§6)
- `backend/coaching/coaching_controller.py` - JD-First Narrative Ordering (§5), Strength Failure Handling (§8)
- `backend/calibration/calibration_controller.py` - Gap Classification, Staff+ PM Rules
- `backend/backend.py` - Analysis Flow, Controller Integration
