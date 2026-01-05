# Profile Enhancement Implementation Plan

## Overview

This document outlines the enhanced candidate profile data collection system designed to:
1. Improve job fit analysis accuracy
2. Enable B2B employer matching (future revenue stream)
3. Track company pedigree for hiring pattern analysis

## Implementation Status

| Feature | Status | File(s) |
|---------|--------|---------|
| Section reordering (About You first) | Complete | `profile-edit.html` |
| First/Last Name at signup | Complete | `login.html`, `supabase-client.js` |
| Function Area dropdown | Complete | `profile-edit.html` |
| Current Industry + Secondary | Complete | `profile-edit.html` |
| Work Authorization + Sponsorship | Complete | `profile-edit.html` |
| Veteran Status checkbox | Complete | `profile-edit.html`, `add_candidate_profile_fields.sql` |
| Structured Location (City/State/Country) | Complete | `profile-edit.html` |
| Target Industries (What You're Looking For) | Complete | `profile-edit.html` |
| Company extraction from resume | Complete | `supabase-client.js` |
| Pedigree tagging system | Complete | `add_candidate_profile_fields.sql` |
| Database migration | Complete | `add_candidate_profile_fields.sql` |

---

## Section 1: About You (Expanded)

### Fields Added

| Field | Type | Required | Source |
|-------|------|----------|--------|
| First Name | Text | Yes | Auth metadata (signup) |
| Last Name | Text | Yes | Auth metadata (signup) |
| Email | Display only | - | Auth (non-editable) |
| Pronouns | Text | No | User input |
| Function Area | Dropdown | Yes | User selection |
| Current Industry | Dropdown | Yes | User selection |
| Secondary Industry | Dropdown | Conditional | If "multi-industry" checked |
| Work Authorization | Dropdown | Yes | User selection |
| Requires Sponsorship | Radio | Conditional | If visa type selected |
| Veteran Status | Checkbox | No | User input |

### Function Area Options
- Product Management
- Engineering
- Design
- Data / Analytics
- Sales
- Marketing
- Customer Success
- Operations
- Finance
- HR / People
- Legal
- Other

### Industry Options
- Technology / Software
- Healthcare & Life Sciences
- Financial Services / Fintech
- E-commerce / Retail
- Media & Entertainment
- Manufacturing
- Energy / Cleantech
- Real Estate / PropTech
- Education / EdTech
- Government / Public Sector
- Consulting / Professional Services
- Telecommunications
- Transportation / Logistics
- Hospitality / Travel
- Nonprofit
- Other

### Work Authorization Options
- US Citizen
- Green Card / Permanent Resident
- H1B Visa
- H1B Transfer (currently employed)
- L1 Visa
- OPT (with EAD)
- OPT STEM Extension
- TN Visa (Canadian/Mexican)
- Other Visa

---

## Section 4: Location & Work Style (Consolidated)

### Fields
- City (text input)
- State / Province (text input)
- Country (dropdown)
- Work Arrangement (multi-select: Remote, Hybrid, On-site)
- Open to Relocating (radio: Yes, Maybe, No)
- Relocation Target Cities (tag input)

### Backward Compatibility
- Hidden `currentLocation` field maintains old format ("City, State")
- Auto-populated from structured fields on save

---

## Section 5: What You're Looking For

### Fields
- Target Industry (Primary) - dropdown
- Target Industry (Secondary) - dropdown (optional)
- Compensation Expectations (Min/Target/Stretch)

---

## Database Schema

### candidate_profiles Table (New Fields)

```sql
-- Basic Info
first_name TEXT
last_name TEXT
pronouns TEXT

-- Professional
function_area TEXT (constrained values)
current_industry TEXT (constrained values)
secondary_industry TEXT (constrained values)

-- Work Authorization
work_authorization TEXT (constrained values)
requires_sponsorship BOOLEAN

-- Veteran Status
is_veteran BOOLEAN

-- Location (structured)
city TEXT
state TEXT
country TEXT

-- Targets
target_industry_primary TEXT
target_industry_secondary TEXT

-- Pedigree (computed)
pedigree_summary JSONB  -- {faang: true, mbb: false, ...}
has_pedigree BOOLEAN
```

### candidate_companies Table (New)

```sql
CREATE TABLE candidate_companies (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    company_name TEXT NOT NULL,
    company_normalized TEXT,
    pedigree_tags TEXT[],
    title TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN,
    duration_months INTEGER,
    source TEXT,  -- 'resume', 'linkedin', 'manual'
    resume_id UUID REFERENCES user_resumes(id)
);
```

### company_pedigree_lookup Table (New)

```sql
CREATE TABLE company_pedigree_lookup (
    company_normalized TEXT PRIMARY KEY,
    company_aliases TEXT[],
    pedigree_tags TEXT[],
    is_public BOOLEAN
);
```

### Pedigree Tag Categories

| Tag | Description | Examples |
|-----|-------------|----------|
| `faang` | Facebook, Amazon, Apple, Netflix, Google | Google, Meta, Amazon, Apple, Netflix |
| `big_tech` | Large tech companies | Microsoft, Salesforce, Adobe, Oracle |
| `mbb` | Top-tier consulting | McKinsey, Bain, BCG |
| `big4` | Big 4 accounting/consulting | Deloitte, PwC, EY, KPMG |
| `unicorn` | Unicorn startups | Stripe, Databricks, OpenAI |
| `bulge_bracket` | Top investment banks | Goldman Sachs, Morgan Stanley, JPMorgan |
| `consulting` | All consulting firms | MBB + Big4 + others |
| `finance` | Financial services | Banks, PE, asset management |
| `high_growth` | High-growth companies | Late-stage startups |

---

## Auto-Extraction Flow

```
Resume Upload
    ↓
Parse experience[] array
    ↓
For each company:
    1. Extract company_name
    2. Normalize (lowercase, remove Inc/LLC/etc)
    3. Lookup in company_pedigree_lookup
    4. Apply pedigree_tags if found
    5. Save to candidate_companies
    ↓
Aggregate all tags
    ↓
Update candidate_profiles.pedigree_summary
Update candidate_profiles.has_pedigree
```

---

## B2B Implications

### Employer Search Filters (Future)

With this data, employers can filter candidates by:

1. **Function**: "Show me all Product Managers"
2. **Industry**: "Who has healthcare experience?"
3. **Location**: "Candidates in SF Bay Area"
4. **Work Authorization**: "No sponsorship required"
5. **Pedigree**: "FAANG experience preferred"
6. **Availability**: "Actively seeking" (future field)

### Analytics Enabled

1. **Pedigree vs. Hire Rate**: Do FAANG candidates get hired faster?
2. **Industry Transfer Success**: How do cross-industry moves perform?
3. **Sponsorship Impact**: Conversion rates by authorization type
4. **Function Mobility**: PM → Engineering transitions, etc.

---

## Files Modified

| File | Changes |
|------|---------|
| `frontend/login.html` | Split name into First/Last, added CSS for form-row |
| `frontend/profile-edit.html` | Reordered sections, added all new fields, updated JS |
| `frontend/js/supabase-client.js` | Updated signUp(), added company extraction functions |
| `backend/migrations/add_candidate_profile_fields.sql` | Full schema with seed data |

---

## Testing Checklist

- [ ] Signup flow captures First Name and Last Name separately
- [ ] Name appears in auth.users.user_metadata as `first_name`, `last_name`
- [ ] Profile edit auto-populates name from auth metadata
- [ ] All dropdowns populate correctly
- [ ] Work Authorization → Sponsorship conditional display works
- [ ] Multi-industry checkbox reveals secondary dropdown
- [ ] Location fields save as structured + backward-compatible string
- [ ] Resume upload extracts companies
- [ ] Companies matched against pedigree lookup
- [ ] pedigree_summary updated on candidate_profiles
- [ ] Validation errors display for required fields

---

## Migration Steps

1. Run `add_candidate_profile_fields.sql` in Supabase SQL Editor
2. Verify tables created: `candidate_profiles`, `candidate_companies`, `company_pedigree_lookup`
3. Verify seed data in `company_pedigree_lookup` (30+ companies)
4. Test signup → profile → resume upload flow
5. Verify company extraction in `candidate_companies` table
