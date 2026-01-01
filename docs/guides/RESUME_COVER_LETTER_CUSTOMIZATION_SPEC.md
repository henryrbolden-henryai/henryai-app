# Resume & Cover Letter Customization Specification

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Production Ready  
**Owner:** Product Team

---

## Executive Summary

Resume & Cover Letter Customization is HenryHQ's core document generation system. It takes an existing resume and tailors it for a specific job description, producing recruiter-grade output that positions the candidate optimally for ATS systems and human reviewers.

**Target Audience:** Top 0.01% of candidates who need strategic positioning, not generic resume templates.

**What Companies Want:**
1. **Evidence of fit** - Specific proof the candidate can do THIS job
2. **Signal clarity** - Quick identification of seniority level and scope
3. **Zero friction** - No formatting issues, keyword gaps, or red flags
4. **Authenticity** - Real experience, not buzzword padding

**What We Deliver:**
1. JD-aligned resume tailored for specific role
2. Cover letter that addresses the why, not just the what
3. ATS optimization with tiered keyword strategy
4. Strategic positioning guidance based on candidate vs. role fit
5. Honest assessment of competitiveness

---

## Table of Contents

1. [Core Philosophy](#1-core-philosophy)
2. [Resume Customization System](#2-resume-customization-system)
3. [Cover Letter Generation](#3-cover-letter-generation)
4. [Fit Scoring Engine](#4-fit-scoring-engine)
5. [ATS Optimization](#5-ats-optimization)
6. [Level Calibration](#6-level-calibration)
7. [Backend API Specification](#7-backend-api-specification)
8. [Prompt Engineering](#8-prompt-engineering)
9. [Document Output Format](#9-document-output-format)
10. [Quality Validation](#10-quality-validation)
11. [Testing & Edge Cases](#11-testing--edge-cases)
12. [Implementation Checklist](#12-implementation-checklist)

---

## 1. Core Philosophy

### 1.1 Zero Fabrication Principle

**Absolute Rule:** Never invent experience, metrics, skills, or achievements.

| Allowed | Forbidden |
|---------|-----------|
| Reframing existing experience | Inventing new experience |
| Emphasizing relevant skills | Adding skills not on resume |
| Quantifying if evidence exists | Fabricating metrics |
| Inferring reasonable scope | Making up company details |
| Strategic repositioning | Creating fake achievements |

**Grounding Validation:**
Every bullet point, skill, and claim must trace back to:
1. Explicit content in the uploaded resume
2. Reasonable inference from role + company + tenure
3. Standard industry knowledge (e.g., "PM at Stripe" implies fintech context)

**Never:**
- Invent metrics (e.g., "increased revenue 40%") without source
- Add skills not evidenced in resume
- Create achievements that didn't happen
- Fabricate company descriptions

### 1.2 Presentation Gap vs. Experience Gap

**This is the #1 trust-killer for elite candidates.**

Every gap identified must be classified:

| Gap Type | Definition | User Message | Action |
|----------|------------|--------------|--------|
| `presentation` | Candidate has experience but resume doesn't show it | "You likely have this. Make it visible by..." | Rewrite guidance |
| `experience` | Candidate genuinely needs more time/roles | "This requires more time in role. Consider..." | Development path |

**Why This Matters:**
A 12-year PM being told they "lack strategic experience" when their resume just buries it is insulting. Elite candidates immediately lose trust when we conflate "you can't do this" with "your resume doesn't show this."

### 1.3 Company Stage Positioning

Different company stages want different signals:

| Company Stage | What They Want | What They Fear |
|---------------|----------------|----------------|
| **Startup (Seed-A)** | Scrappiness, wearing multiple hats, speed | Slow, process-heavy, needs hand-holding |
| **Scaleup (B-C)** | Building systems, scaling what works | Breaking things, moving too fast |
| **Enterprise (D+/Public)** | Process, stakeholder management, polish | Cowboy behavior, inability to navigate bureaucracy |

**Customization Rules:**
- Startup: Lead with impact and velocity, minimize process language
- Scaleup: Balance execution with systems thinking
- Enterprise: Emphasize cross-functional collaboration, governance, scale

### 1.4 Truth + Direction, Not Encouragement Theater

**What we provide:**
- Honest assessment of readiness without shaming
- Clear competency gaps with specific evidence
- Actionable path to close gaps
- Market reality without moral judgment

**What we never say:**
- "You're not good enough"
- "Companies won't hire you because..."
- "This is toxic to your career"
- Generic cheerleading without substance

---

## 2. Resume Customization System

### 2.1 Input Requirements

**Required:**
- Parsed resume (JSON or structured text)
- Job description (full text)

**Optional but Valuable:**
- Target company name (for company stage detection)
- Candidate's current career stage
- Candidate's target level (if different from current)
- Emotional state (zen/stressed/desperate) for tone calibration

### 2.2 Customization Process

```
[Resume Parse] → [JD Analysis] → [Fit Scoring] → [Gap Identification]
                                                       ↓
[Level Calibration] ← [Company Stage Detection] ← [ATS Keyword Extraction]
       ↓
[Summary Rewrite] → [Bullet Prioritization] → [Keyword Integration]
       ↓
[Quality Validation] → [Output Generation] → [DOCX Export]
```

### 2.3 Summary Rewrite Rules

**Purpose:** The summary is the first thing recruiters read. It must answer: "Why should I keep reading?"

**Formula:**
```
[Years of experience] + [Function] + [Domain expertise] + [Scale indicator] + [JD-aligned value prop]
```

**Examples:**

**Before (Generic):**
> "Results-driven professional with experience in product management and cross-functional collaboration."

**After (Tailored for Senior PM at Fintech Startup):**
> "8 years in product management, 4 at fintech scale (Stripe, Plaid). Owned products serving 20M+ users. Built 0-to-1 payment systems and led 3 launches that drove $50M ARR. Thrive in high-velocity environments."

**Rewrite Constraints:**
1. Maximum 4 sentences
2. Must include at least one quantified metric from resume
3. Must reference at least one JD requirement
4. Must signal appropriate seniority level
5. Never use "results-driven," "passionate," or "motivated professional"

### 2.4 Bullet Prioritization

**Order of Importance:**
1. **Impact bullets** - Quantified outcomes (revenue, users, efficiency)
2. **Scope bullets** - Scale of responsibility (team size, budget, geography)
3. **Skill bullets** - Demonstrated competencies that match JD
4. **Context bullets** - Background that aids understanding

**Reprioritization Logic:**
```python
def prioritize_bullets(resume_bullets: List[str], jd_keywords: List[str]) -> List[str]:
    """
    Score each bullet based on:
    1. Keyword match to JD (weight: 3x)
    2. Quantification present (weight: 2x)
    3. Recency of role (weight: 1.5x)
    4. Action verb strength (weight: 1x)
    """
    scored_bullets = []
    for bullet in resume_bullets:
        score = 0
        score += count_keyword_matches(bullet, jd_keywords) * 3
        score += has_quantification(bullet) * 2
        score += recency_weight(bullet) * 1.5
        score += action_verb_strength(bullet) * 1
        scored_bullets.append((bullet, score))
    
    return [b[0] for b in sorted(scored_bullets, key=lambda x: -x[1])]
```

### 2.5 Bullet Rewriting Rules

**When to Rewrite:**
1. Generic language that can be made specific
2. Missing quantification that can be inferred
3. Passive voice that can be made active
4. Buried keywords that should be surfaced

**Rewrite Constraints:**
1. Never change the factual content
2. Never add metrics not evidenced in original
3. Never remove context that adds credibility
4. Preserve any specific company/product names

**Example:**

**Before:**
> "Managed product roadmap and worked with engineering team"

**After:**
> "Owned product roadmap for [specific product]; collaborated with 12-person engineering team to ship [N] features quarterly"

**Note:** If we don't know the team size or feature count, we don't add it. Only rewrite for clarity and emphasis, not fabrication.

---

## 3. Cover Letter Generation

### 3.1 Structure (4 Paragraphs)

**Paragraph 1: The Hook (2-3 sentences)**
- Why this role, specifically
- What caught your attention about the company
- Your core value proposition for THIS role

**Paragraph 2: The Proof (3-4 sentences)**
- 1-2 specific achievements that map to JD requirements
- Quantified impact where possible
- Evidence of relevant competencies

**Paragraph 3: The Fit (2-3 sentences)**
- Why this company/team/mission resonates
- What you bring that others might not
- Subtle differentiation from generic applicants

**Paragraph 4: The Close (1-2 sentences)**
- Confident but not pushy
- Clear interest without desperation
- No "I look forward to hearing from you"

### 3.2 Cover Letter Modes

**Standard Mode (IC to Senior Manager) - 4 Paragraphs:**

| Paragraph | Purpose | Length |
|-----------|---------|--------|
| Hook | Why this role specifically | 2-3 sentences |
| Proof | Achievements mapped to JD | 3-4 sentences |
| Fit | Why this company resonates | 2-3 sentences |
| Close | Confident, not desperate | 1-2 sentences |

**Executive Mode (Director+) - 2 Paragraphs:**

Execs don't want persuasion. They want positioning and risk reduction.

| Paragraph | Purpose | Length |
|-----------|---------|--------|
| Why This, Why Now | Role alignment + value prop | 3-4 sentences |
| Why Me, Credibly | Track record + confident close | 3-4 sentences |

**Mode Selection Logic:**
```python
def select_cover_letter_mode(candidate_level: str, target_level: str) -> str:
    """
    Default intelligently based on seniority.
    User can override via preference toggle.
    """
    executive_levels = ["Director", "VP", "SVP", "EVP", "C-Suite", "Principal", "Staff"]
    
    if target_level in executive_levels or candidate_level in executive_levels:
        return "executive"  # 2 paragraphs
    return "standard"  # 4 paragraphs
```

### 3.3 Cover Letter Constraints

**Must Include:**
- At least one specific reference to the job description
- At least one quantified achievement from resume
- Company name (never generic)
- Appropriate seniority signaling

**Must Exclude:**
- "Dear Hiring Manager" if company name known
- "I am writing to express my interest in..."
- "I believe I would be a great fit because..."
- "Please find attached my resume..."
- Any claim not supported by resume

### 3.4 Tone Calibration

| Company Stage | Tone | Example Language |
|---------------|------|------------------|
| Startup | Direct, energetic, scrappy | "Built the system from scratch" |
| Scaleup | Balanced, systems-thinking | "Designed processes that scale" |
| Enterprise | Polished, collaborative | "Partnered with cross-functional teams" |

### 3.5 Header Matching

Cover letter header must match resume header format:
- Same name styling
- Same contact information order
- Consistent visual treatment (when exported to DOCX)

---

## 4. Fit Scoring Engine

### 4.1 50/30/20 Methodology

| Category | Weight | What It Measures |
|----------|--------|------------------|
| **Skills Match** | 50% | Technical and functional skills alignment |
| **Experience Match** | 30% | Domain, industry, and role type alignment |
| **Scope/Seniority Match** | 20% | Level appropriateness and scale match |

### 4.2 Skills Scoring (50%)

**Tier 1 (Must-Have) - 30% of skills score:**
- Explicitly required in JD
- Used as screening criteria
- Missing = likely auto-rejection

**Tier 2 (Important) - 15% of skills score:**
- Mentioned as preferred
- Common in role but not gating
- Presence helps, absence doesn't kill

**Tier 3 (Nice-to-Have) - 5% of skills score:**
- Implied by role context
- Industry-standard tools
- Minor differentiation

### 4.3 Experience Scoring (30%)

**Factors:**
- Years in similar roles
- Industry/domain relevance
- Company stage similarity
- Functional alignment

### 4.4 Scope/Seniority Scoring (20%)

**Factors:**
- Team size alignment
- Budget/P&L experience
- Geographic scope
- Decision-making authority

### 4.5 Score Interpretation

| Score | Label | Recommendation | Explanation |
|-------|-------|----------------|-------------|
| 85%+ | Strong Fit | **Strongly Apply** | Excellent alignment; high interview probability |
| 70-84% | Good Fit | **Apply** | Solid fit with minor gaps; worth pursuing |
| 55-69% | Moderate Fit | **Conditional Apply** | Addressable gaps; apply if conditions met |
| 40-54% | Weak Fit | **Long Shot** | Significant gaps; only if no better options |
| <40% | Poor Fit | **Do Not Apply** | Fundamental misalignment; not worth effort |

### 4.6 Hard Overrides

Certain conditions cap the score regardless of raw calculation:

| Condition | Hard Cap | Rationale |
|-----------|----------|-----------|
| Career switcher + no direct ownership | 40% | Can't fake core function experience |
| Senior role required + PM II competencies | 40% | Level mismatch too significant |
| Unverifiable company + senior claim | 45% | Can't validate scope |
| Inflated title + missing competencies | 55% | Evidence doesn't support claim |

---

## 5. ATS Optimization

### 5.1 ATS Success Definition

**Success means:** The resume passes ATS parsing, surfaces Tier 1 keywords in indexed fields, and avoids structural elements that suppress keyword weighting.

### 5.2 Keyword Extraction

**From Job Description:**
1. Extract all role-specific keywords
2. Identify tools, technologies, methodologies
3. Capture industry-specific terminology
4. Note company-specific language

**Tiering Logic:**
```python
def tier_keywords(jd_text: str) -> Dict[str, List[str]]:
    """
    Tier 1: Required section, repeated 3+ times, or explicitly gating
    Tier 2: Preferred section, mentioned 1-2 times
    Tier 3: Implied by context, industry-standard
    """
    keywords = extract_all_keywords(jd_text)
    
    tier_1 = [k for k in keywords if 
              is_in_required_section(k, jd_text) or 
              count_occurrences(k, jd_text) >= 3 or
              has_gating_language(k, jd_text)]
    
    tier_2 = [k for k in keywords if 
              k not in tier_1 and 
              (is_in_preferred_section(k, jd_text) or 
               count_occurrences(k, jd_text) >= 1)]
    
    tier_3 = [k for k in keywords if 
              k not in tier_1 and 
              k not in tier_2]
    
    return {"tier_1": tier_1, "tier_2": tier_2, "tier_3": tier_3}
```

### 5.3 Keyword Integration Rules

**Keyword Density Guardrail:** Tier 1 keywords should appear naturally 1-3 times; repetition beyond that is treated as noise.

**Do:**
- Integrate Tier 1 keywords in summary and first 2 role descriptions
- Use exact phrasing from JD when natural
- Include both acronyms and spelled-out versions
- Place keywords in context, not as lists

**Don't:**
- Keyword stuff (unnatural repetition)
- Add skills candidate doesn't have
- Use keywords out of context
- Create "skills" sections that are just keyword lists

### 5.4 ATS Formatting Rules

**Safe:**
- Standard section headers (Experience, Education, Skills)
- Reverse chronological order
- Consistent date formatting (MMM YYYY)
- Clear role titles
- Bullet points (simple characters)

**Avoid:**
- Tables, columns, text boxes
- Headers/footers with critical info
- Images, icons, graphics
- Non-standard fonts
- Colored text

---

## 6. Level Calibration

### 6.1 Detection Layers

**1. Title Analysis**
- Extract claimed title from resume
- Compare to JD required level
- Flag if mismatch detected

**2. Scope Evidence Check**
- Team size mentioned?
- Budget/P&L mentioned?
- Geographic scope mentioned?
- Decision-making authority evidenced?

**3. Company Credibility Assessment**

| Level | Definition | Impact on Scoring |
|-------|------------|-------------------|
| **Strong** | Public data available (press, funding, reviews) | No discount |
| **Weak** | Limited presence (website, LinkedIn) | 10% discount |
| **Unverifiable** | Cannot validate claims | 20% discount |

**4. Career Switcher Detection**

| Evidence Type | Examples | Interpretation |
|---------------|----------|----------------|
| DIRECT | "Owned roadmap", "Defined strategy" | Full credit |
| ADJACENT | "Supported PM team", "Contributed to" | 50% credit |
| EXPOSURE | "Participated in", "Familiar with" | 25% credit |

### 6.2 Level Definitions (PM Example)

| Level | Years | Scope | Key Distinction |
|-------|-------|-------|-----------------|
| PM I / Associate PM | 0-2 | Feature ownership | Executes on roadmap |
| PM II / Product Manager | 2-4 | Product area ownership | Defines area roadmap |
| Senior PM | 4-8 | Product/platform ownership | Sets strategy, influences org |
| Staff PM | 8-12 | Multi-product/platform | Org-level impact |
| Principal PM | 12+ | Company-level initiatives | Strategic direction |

### 6.3 Calibration Output

```json
{
  "detected_level": "PM II",
  "target_level": "Senior PM",
  "level_gap": 1,
  "confidence": 75,
  "signals": {
    "scope": "Medium - 500K users, no budget mentioned",
    "impact": "Strong - 3 quantified achievements",
    "leadership": "Weak - Peer coordination, no direct reports",
    "technical": "Medium - Tools mentioned, no architecture"
  },
  "recommendation": "Apply with positioning strategy",
  "quick_win": {
    "action": "Add team size and stakeholder levels to Spotify role",
    "gap_type": "presentation",
    "expected_impact": "Signals senior-level scope"
  }
}
```

---

## 7. Backend API Specification

### 7.1 Resume Parse Endpoint

**POST /api/resume/parse**

```json
// Request
{
  "file": "<base64 encoded resume>",
  "format": "pdf" | "docx"
}

// Response
{
  "success": true,
  "parsed_resume": {
    "contact": {
      "name": "string",
      "email": "string",
      "phone": "string",
      "location": "string",
      "linkedin": "string"
    },
    "summary": "string",
    "experience": [
      {
        "company": "string",
        "title": "string",
        "start_date": "string",
        "end_date": "string",
        "bullets": ["string"]
      }
    ],
    "education": [...],
    "skills": ["string"],
    "certifications": ["string"]
  }
}
```

### 7.2 Resume Customize Endpoint

**POST /api/resume/customize**

```json
// Request
{
  "resume": "<parsed resume JSON>",
  "job_description": "string",
  "target_company": "string",
  "preferences": {
    "preserve_formatting": true,
    "aggressive_tailoring": false
  }
}

// Response
{
  "success": true,
  "fit_analysis": {
    "fit_score": 75,
    "recommendation": "Apply",
    "fit_score_explanation": "string",
    "strengths": ["string"],
    "gaps": ["string"],
    "gap_types": {
      "gap_1": "presentation",
      "gap_2": "experience"
    }
  },
  "customized_resume": {
    "summary": "string",
    "experience": [...],
    "ats_keywords": ["string"],
    "key_qualifications": ["string"]
  },
  "interview_prep": {
    "narrative": "string",
    "talking_points": ["string"],
    "gap_mitigation": ["string"]
  },
  "outreach": {
    "hiring_manager": "string",
    "recruiter": "string",
    "linkedin_help_text": "string"
  },
  "changes_summary": {
    "resume": {
      "summary_rationale": "string",
      "qualifications_rationale": "string",
      "ats_keywords": ["string"],
      "positioning_statement": "string"
    }
  }
}
```

### 7.3 Cover Letter Generate Endpoint

**POST /api/cover-letter/generate**

```json
// Request
{
  "resume": "<parsed resume JSON>",
  "job_description": "string",
  "target_company": "string",
  "hiring_manager_name": "string" | null
}

// Response
{
  "success": true,
  "cover_letter": {
    "content": "string",
    "paragraphs": {
      "hook": "string",
      "proof": "string",
      "fit": "string",
      "close": "string"
    }
  },
  "changes_summary": {
    "cover_letter": {
      "opening_rationale": "string",
      "body_rationale": "string",
      "close_rationale": "string",
      "positioning_statement": "string"
    }
  }
}
```

### 7.4 Document Package Endpoint

**POST /api/documents/generate**

```json
// Request
{
  "resume": "<parsed resume JSON>",
  "job_description": "string",
  "target_company": "string",
  "include": {
    "resume": true,
    "cover_letter": true,
    "interview_prep": true
  }
}

// Response
{
  "success": true,
  "fit_analysis": {...},
  "resume": {...},
  "cover_letter": {...},
  "interview_prep": {...},
  "outreach": {...},
  "changes_summary": {...}
}
```

### 7.5 Download Endpoints

**GET /api/download/resume/:session_id**
Returns: DOCX file

**GET /api/download/cover-letter/:session_id**
Returns: DOCX file

---

## 8. Prompt Engineering

### 8.1 System Prompt Structure

```
You are a resume customization engine built for elite job seekers. You transform resumes to maximize fit for specific job descriptions while maintaining absolute truthfulness.

CORE PRINCIPLES:
1. Zero Fabrication - Never invent experience, metrics, or skills
2. Grounding Validation - Every claim must trace to resume content
3. Strategic Positioning - Emphasize what's relevant, de-emphasize what's not
4. Gap Classification - Distinguish presentation gaps from experience gaps

FIT SCORING (50/30/20):
- 50% Skills match (Tier 1/2/3 keyword alignment)
- 30% Experience match (domain, industry, role type)
- 20% Scope/Seniority match (level appropriateness)

COMPANY STAGE CALIBRATION:
- Startup: Speed, scrappiness, wearing multiple hats
- Scaleup: Systems thinking, scaling what works
- Enterprise: Process, stakeholder management, governance

OUTPUT REQUIREMENTS:
- All fields must be populated (never null/undefined)
- All rationales must explain WHAT changed AND WHY
- Keywords must come directly from JD
- Positioning statements must be strategic insights

TONE:
- Direct and honest, but supportive
- Coach-style, not drill-sergeant
- Evidence-based, not judgmental
```

### 8.2 Fit Analysis Prompt

```
Analyze the fit between this resume and job description.

RESUME:
{resume_json}

JOB DESCRIPTION:
{jd_text}

PROVIDE:
1. Fit score (0-100) using 50/30/20 methodology
2. Recommendation: Strongly Apply / Apply / Conditional Apply / Long Shot / Do Not Apply
3. 3+ strengths (specific to this role)
4. 3+ gaps (with gap_type: "presentation" or "experience")
5. Competitiveness assessment
6. Quick win (single highest-impact action)

For each gap, classify:
- PRESENTATION: Candidate likely has this but resume doesn't show it
- EXPERIENCE: Candidate needs more time/roles to build this

Use specific examples from both documents. Never fabricate.
```

### 8.3 Resume Customization Prompt

```
Customize this resume for the target job description.

RESUME:
{resume_json}

JOB DESCRIPTION:
{jd_text}

COMPANY STAGE: {startup/scaleup/enterprise}

INSTRUCTIONS:
1. Rewrite summary to align with JD (max 4 sentences)
2. Reprioritize bullets (impact + JD-alignment first)
3. Identify and integrate Tier 1/2/3 keywords
4. Preserve all factual content - reframe only
5. Signal appropriate seniority level

CONSTRAINTS:
- Never add experience that doesn't exist
- Never fabricate metrics
- Never add skills not evidenced
- Preserve company/product names

OUTPUT:
- Rewritten summary
- Reprioritized experience bullets (by role)
- ATS keywords to include (from JD)
- Key qualifications to highlight
- Rationale for each change
```

### 8.4 Cover Letter Prompt (Standard - 4 Paragraph)

```
Generate a cover letter for this candidate applying to this role.

RESUME:
{resume_json}

JOB DESCRIPTION:
{jd_text}

COMPANY: {company_name}
HIRING MANAGER: {hiring_manager_name or "Hiring Team"}

STRUCTURE (4 paragraphs):
1. Hook - Why this role specifically (2-3 sentences)
2. Proof - 1-2 achievements mapped to JD (3-4 sentences)
3. Fit - Why this company resonates (2-3 sentences)
4. Close - Confident, not desperate (1-2 sentences)

CONSTRAINTS:
- Reference at least one specific JD requirement
- Include at least one quantified achievement from resume
- Use company name (not "your company")
- Never use "I am writing to express my interest..."
- Never claim anything not in resume

TONE: {startup=energetic / scaleup=balanced / enterprise=polished}
```

### 8.5 Cover Letter Prompt (Executive - 2 Paragraph)

```
Generate an executive cover letter for this Director+ candidate.

RESUME:
{resume_json}

JOB DESCRIPTION:
{jd_text}

COMPANY: {company_name}
HIRING MANAGER: {hiring_manager_name or "Hiring Team"}

STRUCTURE (2 paragraphs only):
1. Why This, Why Now - Role alignment + value proposition (3-4 sentences)
   - What draws you to this specific opportunity
   - Your core thesis on the role/challenge
   - One sentence positioning your track record

2. Why Me, Credibly - Track record + confident close (3-4 sentences)
   - One quantified achievement at comparable scale
   - What you bring that reduces risk for them
   - Clean close with confidence, no ask

EXECUTIVE TONE RULES:
- No persuasion, only positioning
- No enthusiasm signaling ("excited", "passionate", "thrilled")
- No explaining yourself, only stating credentials
- Assume they know who you are (or should)
- Brevity signals seniority

CONSTRAINTS:
- Maximum 150 words total
- Reference one specific strategic challenge from JD
- Include one metric that signals executive-level scope
- Never use "I believe I would be a great fit"
- Never apologize for anything

TONE: Measured, authoritative, peer-level
```

---

## 9. Document Output Format

### 9.1 Resume DOCX Specification

**Page Setup:**
- Letter size (8.5" x 11")
- Margins: 0.75" all sides
- Single column layout

**Header:**
- Name: 14pt bold
- Contact: 10pt, pipe-separated
- LinkedIn: 10pt, hyperlinked

**Section Headers:**
- 11pt bold, ALL CAPS
- Horizontal rule below

**Experience:**
- Company + Title: 11pt bold
- Dates: 10pt, right-aligned
- Bullets: 10pt, 0.25" indent

**Fonts:**
- Primary: Calibri or Arial
- Consistent throughout
- No color (black text only)

### 9.2 Cover Letter DOCX Specification

**Header:** Matches resume header exactly

**Date:** Current date, 10pt

**Salutation:** "Dear [Name]," or "Dear Hiring Team,"

**Body:** 11pt, single-spaced, 12pt paragraph spacing

**Signature:**
```
Best regards,

[Name]
```

---

## 10. Quality Validation

### 10.1 Pre-Generation Checks

| Check | Fail Action |
|-------|-------------|
| Resume empty | Return error |
| JD < 100 words | Warn user |
| No contact info | Flag for user |
| Company not detected | Prompt for company name |

### 10.2 Post-Generation Validation

| Check | Fail Action |
|-------|-------------|
| Summary > 4 sentences | Truncate with warning |
| No JD keywords included | Flag low ATS optimization |
| Fit score undefined | Fallback to manual calculation |
| Any fabrication detected | Block generation |

### 10.3 Fabrication Detection

```python
def detect_fabrication(original_resume: Dict, customized_resume: Dict) -> List[str]:
    """
    Compare original and customized to detect added content.
    """
    fabrications = []
    
    # Check for new companies
    original_companies = extract_companies(original_resume)
    customized_companies = extract_companies(customized_resume)
    if customized_companies - original_companies:
        fabrications.append(f"New companies added: {customized_companies - original_companies}")
    
    # Check for new metrics
    original_metrics = extract_metrics(original_resume)
    customized_metrics = extract_metrics(customized_resume)
    for metric in customized_metrics:
        if not can_trace_to_original(metric, original_metrics):
            fabrications.append(f"Potentially fabricated metric: {metric}")
    
    # Check for new skills
    original_skills = set(original_resume.get("skills", []))
    customized_skills = set(customized_resume.get("skills", []))
    if customized_skills - original_skills:
        fabrications.append(f"New skills added: {customized_skills - original_skills}")
    
    return fabrications
```

---

## 11. Testing & Edge Cases

### 11.1 Standard Test Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Strong fit | Senior PM resume + Senior PM JD | 85%+ score, "Strongly Apply" |
| Moderate fit | Mid PM resume + Senior PM JD | 60-70%, "Conditional Apply" |
| Poor fit | Engineer resume + PM JD | <40%, "Do Not Apply" |
| Career switch | PMM resume + PM JD | Flag switcher, provide path |

### 11.2 Edge Cases

| Case | Handling |
|------|----------|
| Resume has no dates | Flag for user, estimate based on role progression |
| JD is vague | Use industry standards, warn about uncertainty |
| Candidate overqualified | Acknowledge, suggest repositioning strategy |
| Candidate underqualified | Honest assessment, suggest stepping stones |
| Resume is sparse | Work with available info, note limitations |
| JD is copied from another company | Detect if possible, proceed with caution |

### 11.3 Regression Tests

```python
# Test Suite

def test_no_fabrication():
    """Verify customized resume contains no invented content."""
    original = load_test_resume("pm_mid.json")
    customized = customize_resume(original, load_test_jd("senior_pm.json"))
    fabrications = detect_fabrication(original, customized)
    assert len(fabrications) == 0

def test_fit_score_stability():
    """Verify same inputs produce consistent scores."""
    resume = load_test_resume("pm_senior.json")
    jd = load_test_jd("senior_pm.json")
    scores = [calculate_fit(resume, jd) for _ in range(10)]
    assert max(scores) - min(scores) <= 5  # Max 5% variance

def test_keyword_integration():
    """Verify Tier 1 keywords appear in output."""
    resume = load_test_resume("pm_mid.json")
    jd = load_test_jd("senior_pm.json")
    customized = customize_resume(resume, jd)
    tier_1_keywords = extract_tier_1_keywords(jd)
    for keyword in tier_1_keywords:
        assert keyword.lower() in customized["summary"].lower() or \
               any(keyword.lower() in bullet.lower() 
                   for exp in customized["experience"] 
                   for bullet in exp["bullets"])

def test_gap_classification():
    """Verify gaps are classified as presentation or experience."""
    resume = load_test_resume("pm_mid.json")
    jd = load_test_jd("senior_pm.json")
    analysis = analyze_fit(resume, jd)
    for gap in analysis["gaps"]:
        assert gap["gap_type"] in ["presentation", "experience"]
```

---

## 12. Implementation Checklist

### Phase 1: Core Customization + Trust Building (Current Priority)

**Core (Complete):**
- [x] Resume parsing API
- [x] JD analysis and keyword extraction
- [x] Fit scoring (50/30/20)
- [x] Resume summary rewrite
- [x] ATS keyword integration (Tier 1/2/3)
- [x] Cover letter generation (4-paragraph)
- [x] DOCX export (resume + cover letter)
- [x] Zero fabrication enforcement

**Trust Building (Phase 1 Priority - Non-Negotiable):**
- [ ] Gap type classification (presentation vs. experience)
- [ ] Quick win identification (single highest-impact action)
- [ ] "Here's what I changed" rationale in UI

**Rationale:** For elite candidates, gap type = trust, quick win = momentum. Without them, even a great resume feels like another black box. With them, HenryHQ feels like a senior recruiter pulling you aside and telling you the truth.

### Phase 2: Detection & Executive Mode (Q1 2026)

- [ ] Company credibility assessment
- [ ] Title inflation detection
- [ ] Career switcher recognition
- [ ] Executive cover letter mode (2-paragraph)

### Phase 3: Interview Prep Integration (Q1 2026)

- [ ] Interview prep generation with documents
- [ ] Talking points tied to resume content
- [ ] Gap mitigation strategies
- [ ] Outreach templates (HM + Recruiter)
- [ ] LinkedIn search guidance

### Phase 4: Refinement & Feedback (Q2 2026)

- [ ] Document refinement via chat
- [ ] Version history
- [ ] User feedback loop
- [ ] Quality scoring on outputs
- [ ] A/B testing different customization strategies

---

## Appendix A: Tier Permission Integration

Features available by tier (from HenryHQ Tier Permissions Matrix):

| Feature | Sourcer | Recruiter | Principal | Partner | Coach |
|---------|---------|-----------|-----------|---------|-------|
| Resume parsing | ✓ | ✓ | ✓ | ✓ | ✓ |
| Fit analysis (50/30/20) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gaps + gap_type visibility | ✓ | ✓ | ✓ | ✓ | ✓ |
| Quick win identification | - | ✓ | ✓ | ✓ | ✓ |
| Tailored resume generation | - | ✓ | ✓ | ✓ | ✓ |
| Tailored cover letter | - | ✓ | ✓ | ✓ | ✓ |
| ATS keyword optimization | - | ✓ | ✓ | ✓ | ✓ |
| Quality validation score | - | - | ✓ | ✓ | ✓ |
| "Here's what I changed" | - | ✓ | ✓ | ✓ | ✓ |
| Executive cover letter mode | - | - | ✓ | ✓ | ✓ |
| Document refinement via chat | - | - | - | ✓ | ✓ |
| Version history | - | - | - | ✓ | ✓ |

**Sourcer Tier Strategy:** Free users see gaps + gap_type, but no rewritten output. They walk away thinking, "Damn... I need the rewrite." This builds trust while driving conversion. "Here's the truth, even if you don't pay" is premium behavior.

---

## Appendix B: Related Specifications

- **Resume Leveling Spec V3** - Level assessment and competency mapping
- **Fit Scoring Engine Spec** - Detailed 50/30/20 methodology
- **HenryHQ Tier Permissions Matrix** - Feature gating by subscription level
- **Interview Prep Spec** - Post-application preparation flow

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Jan 2026 | Initial unified spec | Product |

---

**Status:** Production Ready  
**Next Review:** February 2026  
**Owner:** Product Team
