# Known Issues - Six-Tier Recommendation System

**Last Updated:** Post Round 8 Testing (December 2025)

---

## P0 - Em Dash in "Do Not Apply" Reality Check

**Status:** ✅ FIXED (commit 396ae51)

**Issue:** Reality Check text for "Do Not Apply" candidates contained em dash: "I'll be straight with you—this is a stretch"

**Affected:** All "Do Not Apply" candidates (Kendra, Derek)

**Not Affected:** "Apply" and "Apply with Caution" candidates (Priya)

**Root Cause:** Hardcoded template string in `frontend/results.html` line 1954 contained em dash

**Fix Applied:** Changed em dash to colon: "I'll be straight with you: this is a stretch"

---

## P1 - Frontend Role Title Extraction Includes JD Preamble

**Status:** 🔧 PARTIALLY FIXED

**Issue:** Frontend `extractCompanyAndRole()` in `analyze.html` extracts JD preamble as part of role title

**Example:** Sends "We're seeking a Global Vice President of Talent Acquisition" instead of "Global Vice President of Talent Acquisition"

**Affected:** JDs that start with preamble patterns ("We're seeking...", "We're looking for...", etc.)

**Impact:** Role title displayed incorrectly in UI, affects downstream level detection for GENERAL roles

**Current Mitigations:**
1. Backend `_final_sanitize_text()` strips JD preamble patterns from all text fields
2. Backend ignores placeholder role_title values ('Role', 'Position', etc.)
3. Backend `_sanitize_role_title()` in coaching controller handles preamble extraction

**Remaining Fix Needed:** Add preamble stripping to frontend `extractCompanyAndRole()` function before sending to backend

**Location:** `frontend/analyze.html` lines 959-990

---

## P2 - Generic Explanation for GENERAL "Do Not Apply" Candidates

**Status:** 🔧 PARTIALLY FIXED (depends on P1)

**Issue:** Explanation shows "This role requires 8+ years of experience" instead of specific level/leadership gap

**Affected:** GENERAL path "Do Not Apply" candidates (Derek)

**Not Affected:** RECRUITING path (Kendra gets specific explanation)

**Root Cause:** When frontend sends placeholder role title, backend level detection fails, explanation falls back to generic years message

**Fix:** Will fully resolve once P1 (frontend role title) is fixed. Backend now has fallback logic to check `role_title` for level signals in addition to `role_level`.

---

## P2 - Generic Your Move for "Do Not Apply" Candidates

**Status:** ⚪ ACCEPTABLE

**Issue:** Your Move shows generic text like "Build required experience before applying" instead of resume-specific guidance

**Affected:** All "Do Not Apply" candidates

**Why Acceptable:** Since we're telling them not to apply, generic guidance is reasonable. Resume-specific coaching still appears in Gaps to Address section.

**Future Enhancement:** Could generate resume-specific Your Move that suggests what roles they should target instead

---

## What's Working Well

- ✅ Score calibration accurate across all archetypes
- ✅ Action/recommendation consistency (timing always matches recommendation)
- ✅ Strengths extraction fallback working (extracts from resume when Claude returns 0)
- ✅ Explanation quality for RECRUITING "Do Not Apply" (Kendra)
- ✅ All fields working for "Apply" and "Apply with Caution" candidates
- ✅ Resume-specific strengths, gaps, and coaching
- ✅ "You're early" UX for stretch candidates
- ✅ Em dash removal via `_final_sanitize_text()`
- ✅ JD preamble sanitization in all text fields
- ✅ Role title placeholder rejection in backend

---

## Test Archetypes

| Archetype | Path | Recommendation | Status |
|-----------|------|----------------|--------|
| Kendra (Recruiter) | RECRUITING | Do Not Apply | Working |
| Derek (PM) | GENERAL | Do Not Apply | Working (with P2 caveats) |
| Priya (Strong Fit) | GENERAL | Apply | Fully Working |

---

## Related Files

- `frontend/results.html` - Reality Check templates, timing extraction
- `frontend/analyze.html` - Role title extraction, request payload
- `backend/backend.py` - `_final_sanitize_text()`, role title validation, level detection
- `backend/coaching/coaching_controller.py` - `_sanitize_role_title()`, Your Move generation
- `backend/postprocessors/__init__.py` - Action/recommendation consistency

---

## Changelog

### Round 8 (December 2025)
- Fixed P0 em dash in Reality Check template
- Added JD preamble patterns to `_final_sanitize_text()`
- Added role title placeholder rejection in backend
- Added `market_context.action` to FINAL consistency check
- Added fallback strengths extraction from resume
