# HenryHQ Pre-Launch Test Suite

## Quick Start

```bash
# Install dependencies
pip install pytest requests

# Run all tests
pytest henryhq_prelaunch_tests.py -v

# Run by priority
pytest henryhq_prelaunch_tests.py -v -m p0    # Launch blockers only
pytest henryhq_prelaunch_tests.py -v -m p1    # Critical functionality
pytest henryhq_prelaunch_tests.py -v -m p2    # Important features

# Generate report
python henryhq_prelaunch_tests.py --report
```

---

## Priority Breakdown

### P0 - Launch Blockers (Must pass by 01/15)

| Category | Tests | Focus |
|----------|-------|-------|
| QA Validation | 5 | Fix regex false positives, re-enable validation |
| Strengthen Resume | 9 | Full integration test + merge to main |
| User Flow | 9 | End-to-end tests 1-9 from checklist |

**Total P0: 23 tests**

### P1 - Critical (Should pass by 01/15)

| Category | Tests | Focus |
|----------|-------|-------|
| Screening Questions | 6 | Yes/no, salary, essay, knockouts |
| Document Refine | 7 | Version tracking, fabrication blocking |

**Total P1: 13 tests**

### P2 - Important (Nice to have)

| Category | Tests | Focus |
|----------|-------|-------|
| Success Metrics | 4 | Quality score, keyword coverage, response time |
| Browser | 6 | CORS, Chrome, Safari, Firefox, mobile |

**Total P2: 10 tests**

---

## Timeline

| Week | Dates | Focus |
|------|-------|-------|
| Week 1 | Jan 6-8 | P0: QA Validation + Strengthen Resume |
| Week 2 | Jan 9-12 | P1: Screening Questions + Doc Refine |
| Week 2 | Jan 13-14 | P2: Metrics + Browser Testing |
| Launch | Jan 15 | Go/No-Go Decision |

---

## Critical Path Items

### 1. QA Validation Regex (P0)
**File:** `backend/backend.py:14088`

**Issue:** QA validation disabled due to false positives on "improved pipeline"

**Fix needed:**
- Update regex to not flag common phrases
- Re-enable validation
- Test with synthetic cases

### 2. Strengthen Resume Integration (P0)
**Tests to complete:**
- [ ] Leveling API returns bullet_audit
- [ ] Flagged bullets load from levelingData
- [ ] Questions without example answers
- [ ] Blank answers marked UNVERIFIED
- [ ] "No" answers downgrade claims
- [ ] Enhanced bullets use candidate info only
- [ ] Skip option logs reason
- [ ] strengthenedData persists to sessionStorage
- [ ] Document generation respects declined_items
- [ ] Full flow integration
- [ ] Merge to main

### 3. Full User Flow (P0)
**Tests 1-9:**
1. Resume upload/parse
2. JD upload/analyze
3. Strategic positioning
4. Action plan
5. Salary strategy
6. Hiring intel
7. Edge case: minimal resume
8. Edge case: overqualified
9. Document download

---

## Tier Impact Matrix

| Feature | Sourcer | Recruiter | Principal | Partner | Coach |
|---------|---------|-----------|-----------|---------|-------|
| Resume parsing | ✓ | ✓ | ✓ | ✓ | ✓ |
| Fit analysis | ✓ | ✓ | ✓ | ✓ | ✓ |
| Doc generation | - | ✓ | ✓ | ✓ | ✓ |
| Screening questions | - | ✓ | ✓ | ✓ | ✓ |
| Quality validation | - | - | ✓ | ✓ | ✓ |
| Interview prep | - | - | ✓ | ✓ | ✓ |
| Doc refinement | - | - | - | ✓ | ✓ |
| Mock interviews | - | - | - | ✓ | ✓ |

---

## Go/No-Go Criteria (01/15)

### Must Have (Launch Blockers)
- [ ] QA validation re-enabled and working
- [ ] Strengthen Resume merged to main
- [ ] Full user flow passes (upload → analyze → documents → download)
- [ ] No console errors
- [ ] Downloads work correctly

### Should Have
- [ ] Screening questions tested
- [ ] Document refine tested
- [ ] Mobile works

### Nice to Have
- [ ] Success metrics dashboard
- [ ] A/B testing infrastructure

---

## Files Included

| File | Description |
|------|-------------|
| `henryhq_prelaunch_tests.py` | Full pytest test suite |
| `HenryHQ_Test_Matrix.xlsx` | Excel tracking spreadsheet |
| `TEST_GUIDE.md` | This quick reference |

---

## Running Against Local Backend

```bash
# Start backend first
cd backend && python backend.py

# In another terminal, run tests
pytest henryhq_prelaunch_tests.py -v

# Or with coverage
pytest henryhq_prelaunch_tests.py --cov=backend --cov-report=html
```

---

## Contact

Questions? Bugs? Reach out via the HenryHQ project channels.
