# Resume Parse Test Suite - Expected Values & Validation Checklist

## How to Use This Document

1. Upload each test resume to HenryHQ
2. Check the parsed JSON against the expected values below
3. Mark each field as ✅ PASS or ❌ FAIL
4. Note any issues in the "Actual Result" column

---

## Test 1: Multi-Column Creative (01_multicolumn_creative.pdf)

**Edge Case:** Two-column layout - tests if parser reads columns correctly
**Expected Failure:** Columns read left-to-right instead of column-by-column

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Alexandra Chen | | |
| contact.email | alex.chen@email.com | | |
| contact.phone | (415) 555-0192 | | |
| contact.location | San Francisco, CA | | |
| current_title | Senior UX Designer OR Product Design Lead | | |
| experience[0].company | Airbnb | | |
| experience[0].title | Senior Product Designer | | |
| experience[0].dates | 2021 - Present | | |
| experience[0].bullets | Should have 4 bullets (host onboarding, team of 3, design system, 200+ interviews) | | |
| experience[1].company | Dropbox | | |
| experience[1].title | Product Designer | | |
| experience[1].dates | 2018 - 2021 | | |
| skills | Should include: Figma, Sketch, Adobe XD, Prototyping, User Research, etc. | | |
| education | Stanford MS HCI 2018, UCLA BA Psychology 2016 | | |

**Critical Check:** Are the LEFT column skills mixed into the RIGHT column experience bullets?

---

## Test 2: Table Finance (02_table_finance.pdf)

**Edge Case:** Resume uses tables for all layout
**Expected Failure:** Table structure lost, data becomes jumbled text

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Michael Richardson | | |
| contact.email | michael.richardson@email.com | | |
| contact.phone | (212) 555-0147 | | |
| contact.location | New York, NY | | |
| current_title | Investment Banking Associate | | |
| experience[0].company | Goldman Sachs | | |
| experience[0].title | Associate | | |
| experience[0].dates | 2021 - Present | | |
| experience[0].bullets | Should have 4 bullets ($12B M&A, due diligence, financial models, C-suite) | | |
| experience[1].company | Morgan Stanley | | |
| experience[1].title | Analyst | | |
| experience[1].dates | 2019 - 2021 | | |
| education | Harvard MBA 2019, UPenn BS 2017 | | |
| skills | Should include: Excel/VBA, Bloomberg, Capital IQ, FactSet, CFA Level III | | |

**Critical Check:** Is table data parsed in correct order, or is it scrambled?

---

## Test 3: Standard Baseline (03_standard_baseline.pdf)

**Edge Case:** Standard single-column format - SHOULD WORK
**Expected:** Clean parse with all fields populated

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Sarah Johnson | | |
| contact.email | sarah.johnson@email.com | | |
| contact.phone | (650) 555-0123 | | |
| contact.location | San Jose, CA | | |
| contact.linkedin | github.com/sjohnson | | |
| current_title | Senior Software Engineer | | |
| years_experience | 8 | | |
| experience[0].company | Stripe | | |
| experience[0].title | Senior Software Engineer | | |
| experience[0].dates | 2020 - Present | | |
| experience[1].company | Uber | | |
| experience[1].title | Software Engineer II | | |
| experience[1].dates | 2017 - 2020 | | |
| experience[2].company | Google | | |
| experience[2].title | Software Engineer | | |
| experience[2].dates | 2015 - 2017 | | |
| education | Stanford MS CS 2015, UC Berkeley BS CS 2013 | | |
| skills | Python, Go, Java, JavaScript, SQL, Django, Flask, React, AWS, GCP, Kubernetes, Docker | | |

**If this fails, there's a fundamental parsing bug.**

---

## Test 4: International Characters (04_international_chars.pdf)

**Edge Case:** Non-ASCII characters (é, ü, ø, ñ, €)
**Expected Failure:** Characters become garbled or missing

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | François Müller-Søndergaard | | |
| contact.email | françois.müller@société.fr | | |
| contact.phone | +33 6 12 34 56 78 | | |
| contact.location | Paris, France | | |
| experience[0].company | Société Générale | | |
| experience[0].title | Architecte Logiciel | | |
| experience[0].bullets | Should include "50M€" (Euro symbol) | | |
| experience[1].company | Capgemini España | | |
| education | École Polytechnique Fédérale de Lausanne, Université Pierre et Marie Curie | | |

**Critical Check:** Are special characters (é, ü, ø, ñ, €) preserved or garbled?

---

## Test 5: Career Gap (05_career_gap.pdf)

**Edge Case:** 18-month gap between jobs (Dec 2021 - Present with no job)
**Expected:** Gap should be detected and flagged

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | David Martinez | | |
| contact.email | david.martinez@email.com | | |
| contact.location | Austin, TX | | |
| experience[0].company | Slack | | |
| experience[0].dates | March 2018 - December 2021 | | |
| experience[1].company | Atlassian | | |
| experience[1].dates | June 2015 - February 2018 | | |
| experience[2].company | IBM | | |
| experience[2].dates | July 2013 - May 2015 | | |

**Critical Check:** 
- Gap: December 2021 to Present (~2+ years)
- Is the gap mentioned in summary ("career break for family caregiving")?
- Does the system flag this gap?

---

## Test 6: Concurrent Roles (06_concurrent_roles.pdf)

**Edge Case:** Multiple overlapping dates (consultant with concurrent clients)
**Expected Failure:** Dates may confuse parser, roles may merge

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Jennifer Wong | | |
| contact.email | jennifer.wong@consultant.com | | |
| experience[0].company | Wong Strategy Consulting | | |
| experience[0].dates | January 2020 - Present | | |

**Nested client engagements (should be captured somehow):**
- Fintech Startup: March 2023 - Present
- Retail Chain: January 2023 - September 2023
- Healthcare Startup: June 2022 - March 2023

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| (Advisory role - concurrent) | HealthTech Ventures, January 2021 - Present | | |
| experience[last].company | McKinsey & Company | | |
| experience[last].dates | 2014 - 2019 | | |

**Critical Check:** 
- Are overlapping client engagements preserved?
- Is the part-time advisory role captured separately?
- Are dates accurate despite overlaps?

---

## Test 7: Long Executive (07_long_executive.pdf)

**Edge Case:** 4-page resume with 7 jobs spanning 25+ years
**Expected Failure:** May truncate, drop earlier jobs, or hit token limits

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Robert Thompson III | | |
| contact.email | robert.thompson@email.com | | |
| contact.location | Palo Alto, CA | | |
| years_experience | 25+ | | |

**All 7 jobs should be captured:**

| # | Company | Title | Dates | Captured? |
|---|---------|-------|-------|-----------|
| 1 | Snowflake | CTO | 2019 - Present | |
| 2 | Uber | VP Engineering, Platform | 2015 - 2019 | |
| 3 | Twitter | Senior Director of Engineering | 2012 - 2015 | |
| 4 | LinkedIn | Director of Engineering | 2009 - 2012 | |
| 5 | Yahoo | Senior Engineering Manager | 2005 - 2009 | |
| 6 | Amazon | Software Development Manager | 2001 - 2005 | |
| 7 | Microsoft | Senior Software Engineer | 1998 - 2001 | |

**Critical Check:** Are ALL 7 jobs captured, or are early-career jobs dropped?

---

## Test 8: Functional Career Changer (08_functional_career_changer.pdf)

**Edge Case:** Skills-first format with minimal work history
**Expected Failure:** Experience section may be empty or wrong

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Emily Nakamura | | |
| contact.email | emily.nakamura@email.com | | |
| contact.location | Portland, OR | | |
| current_title | Teacher (transitioning to UX Researcher) | | |
| experience[0].company | Lincoln High School | | |
| experience[0].title | AP Psychology & Social Studies Teacher | | |
| experience[0].dates | 2015 - 2023 | | |
| experience[1].company | Roosevelt Middle School | | |
| experience[1].title | Social Studies Teacher | | |
| experience[1].dates | 2013 - 2015 | | |
| skills | Figma, UserTesting, Optimal Workshop, Miro, Google Analytics, Excel, SQL, Tableau | | |
| education | Google UX Design Certificate 2023, Portland State MA 2013, U of Oregon BA 2011 | | |

**Critical Check:** 
- Does it capture the job titles despite skills-first format?
- Are the "Relevant Skills" bullets captured as skills?
- Is the career transition context preserved?

---

## Test 9: DOCX with Tables (09_docx_with_tables.docx)

**Edge Case:** DOCX format using tables
**Expected:** SHOULD WORK - DOCX table extraction is implemented

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | James Wilson | | |
| contact.email | james.wilson@email.com | | |
| contact.phone | (206) 555-0189 | | |
| contact.location | Seattle, WA | | |
| experience[0].company | Amazon | | |
| experience[0].title | Senior Data Scientist | | |
| experience[0].dates | 2020 - Present | | |
| experience[0].bullets | Should have 3 bullets (ML models $50M, recommendation system, team of 5) | | |
| experience[1].company | Microsoft | | |
| experience[1].title | Data Scientist | | |
| experience[1].dates | 2017 - 2020 | | |
| skills | Python, R, SQL, Scala, TensorFlow, PyTorch, scikit-learn, AWS SageMaker, Azure ML | | |
| education | UW PhD CS 2017, UC Berkeley BS CS 2012 | | |

**If this fails, check the DOCX table extraction code (lines 3863-3869 in backend.py).**

---

## Test 10: Minimal Sparse (10_minimal_sparse.pdf)

**Edge Case:** Very sparse resume with minimal information
**Expected:** Many null/empty fields, but should not error

### Expected Values

| Field | Expected Value | Actual Result | Pass/Fail |
|-------|---------------|---------------|-----------|
| full_name | Kevin Park | | |
| contact.email | kevin.park@email.com | | |
| contact.phone | null or empty | | |
| contact.location | null or empty | | |
| contact.linkedin | null or empty | | |
| summary | null or empty (none provided) | | |
| experience[0].company | TechCorp | | |
| experience[0].title | Software Developer | | |
| experience[0].dates | 2022 - Present | | |
| experience[0].bullets | empty array (no bullets provided) | | |
| experience[1].company | StartupXYZ | | |
| experience[1].title | Junior Developer | | |
| experience[1].dates | 2020 - 2022 | | |
| education | State University - Computer Science (no year) | | |
| skills | null or empty (no skills section) | | |

**Critical Check:** 
- Does it handle missing fields gracefully (null vs error)?
- Does it invent/fabricate any data that wasn't there?

---

## Summary Scorecard

After testing all 10 resumes, fill in:

| Test | Resume | Expected Behavior | Result | Notes |
|------|--------|-------------------|--------|-------|
| 1 | Multi-column | May scramble columns | | |
| 2 | Tables (PDF) | May lose structure | | |
| 3 | Standard | Should work | | |
| 4 | International | May garble chars | | |
| 5 | Career gap | Should detect gap | | |
| 6 | Concurrent | May confuse dates | | |
| 7 | Long exec | May truncate | | |
| 8 | Functional | May miss experience | | |
| 9 | DOCX tables | Should work | | |
| 10 | Minimal | Should handle nulls | | |

**Overall Score:** ___/10 tests passing

---

## Critical Failures to Fix

List any tests that fail in ways that would break the user experience:

1. 
2. 
3. 

## Acceptable Limitations

List any failures that are edge cases you can document/warn about:

1. 
2. 
3. 
