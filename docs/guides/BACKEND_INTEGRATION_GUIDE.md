# 🚀 BACKEND INTEGRATION — TONIGHT
## Get Enhanced Prompts Working (15 Minutes)

---

## **THE BLOCKER**

Your backend is returning:
- Empty action plans
- Generic strategic framing
- Missing market data
- "[Company Name]" placeholders
- Robotic content

**Why:** Enhanced prompts not integrated into backend.py yet

---

## **THE FIX (3 STEPS)**

### **Step 1: Open backend.py (2 min)**

```bash
# Navigate to your project
cd your-project-directory

# Backup first
cp backend.py backend.py.backup.TONIGHT

# Open in editor
code backend.py  # or vim, nano, etc.
```

### **Step 2: Find the Prompt Section (1 min)**

Search for this line (should be around line 1050-1100):

```python
=== INTELLIGENCE LAYER (MANDATORY - MUST BE COMPLETE) ===
```

OR search for:

```python
## 1. JOB QUALITY SCORE (REQUIRED)
```

This is the start of your Claude prompt section.

### **Step 3: Replace the Entire Prompt (10 min)**

**Find:** Lines approximately 1050-1400 (the entire Claude prompt)

**Replace with:** The enhanced prompt below

---

## **ENHANCED PROMPT TO INSERT**

```python
        prompt = f"""You are an expert executive recruiter and career strategist analyzing this job description{' and candidate resume' if resume_text else ''}.

=== CRITICAL INSTRUCTIONS ===

1. EXTRACT CANDIDATE FIRST NAME ONLY
   - Parse full name from resume
   - Use ONLY first name (e.g., "Henry R. Bolden III" → "Henry")
   - If no name found, use "you"
   
2. EXTRACT COMPANY NAME FROM JD
   - Find actual company name in job description
   - Use throughout (no "[Company Name]" placeholders)
   - If not found, use "the company"

3. ALL CONTENT MUST BE:
   - Specific (reference actual companies/roles from resume)
   - Comprehensive (detailed strategic guidance)
   - Actionable (not generic advice)
   - Grammatically perfect
   - NO EM DASHES in outreach templates

=== JOB DESCRIPTION ===
{jd_text}

{f"=== CANDIDATE RESUME ==={chr(10)}{resume_text}" if resume_text else ""}

=== RESPONSE REQUIREMENTS ===

You MUST return valid JSON (no markdown) with ALL these fields populated.

{{
  "_candidate_name": "First Last",
  "_candidate_first_name": "First",
  "_company_name": "Actual Company Name from JD",
  
  "company": "Company name",
  "role_title": "Job title",
  "company_context": "2-3 substantive sentences about company",
  "role_overview": "2-3 substantive sentences about role",
  "key_responsibilities": ["4-6 main responsibilities"],
  "required_skills": ["array of required skills"],
  "preferred_skills": ["array of nice-to-have skills"],
  "ats_keywords": ["10-15 important keywords for ATS"],
  "salary_info": "string if mentioned, otherwise null",
  
  "fit_score": 85,
  "strengths": ["3-4 candidate strengths"] or [],
  "gaps": ["2-3 potential gaps"] or [],
  
  "positioning_strategy": {{
    "emphasize": [
      "SPECIFIC strength 1 from resume (1-2 sentences). Example: Your fintech recruiting experience at Uber Payments and Venmo, where you specifically built payments infrastructure teams. This is directly relevant to this company's need for someone who understands fintech talent challenges.",
      "SPECIFIC strength 2 (1-2 sentences with actual company names)",
      "SPECIFIC strength 3 (1-2 sentences with actual accomplishments)"
    ],
    "de_emphasize": [
      "What to downplay 1 WITH REASONING. Example: National Grid utility sector experience. While it shows enterprise recruiting capability, utility recruiting doesn't translate to startup velocity and product innovation focus. Mention it but don't lead with it.",
      "What to downplay 2 with specific reasoning"
    ],
    "framing": "[First Name], frame yourself as [comprehensive strategic positioning - 2-3 sentences explaining HOW to position for THIS specific role and company]"
  }},
  
  "action_plan": {{
    "today": [
      "Apply via [ACTUAL COMPANY NAME] ATS before end of day",
      "Research hiring manager on LinkedIn (search '[ACTUAL COMPANY] talent acquisition' filtered by current employees)",
      "Check Glassdoor for [ACTUAL COMPANY] reviews, specifically filtering for 'recruiting' or 'talent acquisition' mentions",
      "Review your [SPECIFIC PAST COMPANY] projects - prepare specific metrics for phone screen"
    ],
    "tomorrow": [
      "Send hiring manager outreach using template provided below",
      "Reach out to any connections at [ACTUAL COMPANY] via LinkedIn - check for alumni or mutual connections first",
      "Schedule reminder to follow up if no response by Day 5"
    ],
    "this_week": [
      "Follow up if no response by Day 5 - send polite check-in message",
      "Review phone screen prep daily - practice your [SPECIFIC DOMAIN] examples",
      "Monitor LinkedIn for recruiter outreach and company news",
      "Add this application to your tracker with status and next action"
    ]
  }},
  
  "salary_strategy": {{
    "their_range": "Extracted from JD if present, otherwise 'Not disclosed in job description'",
    "your_target": "ALWAYS PROVIDE: $X-$Y base (based on [SPECIFIC REASONING: years experience, level, location, industry]). Example: $190K-$220K base (based on 10+ years experience, Director-level role, and fintech/payments market in major metro)",
    "market_data": "ALWAYS PROVIDE using your knowledge. Example: Based on market data, Director of Talent Acquisition at Series B fintech startups typically ranges $180K-$230K in major metros. Glassdoor shows $195K median for this title. Levels.fyi data for Series B TA leadership is $185K-$220K.",
    "approach": "2-3 sentences with SPECIFIC negotiation tactics. Example: Don't bring up salary first. If they ask early, provide your target range but emphasize you're focused on the role fit first. If they offer below your target, we'll help you negotiate using your [SPECIFIC BACKGROUND] and [SPECIFIC ACCOMPLISHMENTS] as leverage. We'll provide strategic guidance on timing, comp mix, and how to frame your ask when you reach the offer stage.",
    "talking_points": [
      "SPECIFIC justification 1 from actual resume. Example: You've built and managed 25-person global recruiting teams across 3 companies. This leadership track record justifies the higher end of the range.",
      "SPECIFIC justification 2 referencing actual experience",
      "SPECIFIC justification 3 with metrics if available"
    ]
  }},
  
  "hiring_intel": {{
    "hiring_manager": {{
      "likely_title": "Specific title based on company size. Startup (<50): CEO/COO/Head of People. Mid-size (50-500): VP of Talent/Director of People. Enterprise (500+): VP of Talent Acquisition/Chief People Officer",
      "why_matters": "2-3 sentences explaining strategic value. The hiring manager is the person you'll actually work with. They care about culture fit, problem-solving approach, and whether you can immediately contribute. Getting in front of them early bypasses the resume screening lottery and lets you demonstrate value directly.",
      "search_instructions": "[ACTUAL COMPANY NAME] AND (talent acquisition OR recruiting) AND (VP OR director OR head)",
      "filters": "Filter by: Current employees only, Director level or above, recent activity (posts/comments in last 30 days). If you find multiple people, prioritize whoever is closest to the team you'd actually join."
    }},
    "recruiter": {{
      "likely_title": "Based on role type: Technical Recruiter, Talent Acquisition Partner, or Corporate Recruiter",
      "why_matters": "Recruiters control the pipeline. They decide who gets through to the hiring manager. A good relationship with the recruiter means your resume gets flagged as priority, your interview feedback is framed positively, and you get inside intel on process and timeline.",
      "search_instructions": "[ACTUAL COMPANY NAME] AND (recruiter OR talent acquisition OR people operations)",
      "filters": "Filter by: Current employees, recent activity (posted in last 60 days), profile mentions the specific role or department you're targeting."
    }}
  }},
  
  "outreach": {{
    "hiring_manager": "3-5 sentences. MUST reference candidate's ACTUAL experience with SPECIFIC companies and metrics. NO EM DASHES. Grammatically perfect. Example: Hi [Name], I'm excited about [ACTUAL COMPANY]'s mission to [SPECIFIC MISSION]. Having recruited for fintech infrastructure teams at Uber and Venmo, I understand the unique talent challenges in this space. I've built recruiting functions from scratch at high-growth startups like Spotify (25-person global team) and consistently delivered results like 95% offer acceptance while reducing costs. I'd love to discuss how my experience scaling technical recruiting at similar-stage companies could accelerate [ACTUAL COMPANY]'s talent acquisition goals. Would you be open to a brief conversation?",
    "recruiter": "3-5 sentences. Reference ACTUAL background. NO EM DASHES. Example: Hello [Name], I'm reaching out about [ACTUAL COMPANY]'s [ACTUAL ROLE TITLE] position. I have 10+ years building recruiting functions at high-growth tech companies including Spotify, Uber, and Venmo, with specific experience in fintech recruiting and payments infrastructure teams. I've consistently delivered strong metrics (95% offer acceptance, $1M cost savings) while scaling teams from 5 to 25+ recruiters. My background in both startup recruiting and fintech talent acquisition aligns well with [ACTUAL COMPANY]'s needs. I'd appreciate the opportunity to discuss how I could contribute to your talent strategy.",
    "linkedin_help_text": "Step-by-step: 1. Go to LinkedIn search. 2. Search for '[ACTUAL COMPANY] talent acquisition'. 3. Filter: People tab > Current Company > [ACTUAL COMPANY]. 4. Look for VP/Director titles. 5. Check recent activity (last 30 days). 6. Prioritize those posting about hiring."
  }},
  
  "interview_prep": {{
    "narrative": "3-4 sentence story tailored to this role",
    "talking_points": [
      "Key point 1 for recruiter screen",
      "Key point 2",
      "Key point 3",
      "Key point 4"
    ],
    "gap_mitigation": [
      "Concern 1 + mitigation strategy",
      "Concern 2 + mitigation",
      "Concern 3 + mitigation"
    ]
  }},
  
  "changes_summary": {{
    "resume": {{
      "summary_rationale": "SPECIFIC explanation referencing ACTUAL companies from resume. Example: Rewrote to emphasize fintech experience from Uber Payments/FinTech and Venmo roles more prominently, and highlight startup recruiting function building at Spotify and Uber to match [ACTUAL COMPANY]'s need for someone who can build from scratch.",
      "qualifications_rationale": "SPECIFIC reordering guidance with ACTUAL companies. Example: Lead with Spotify global team building (5→25 people) and Uber fintech recruiting experience. De-emphasize National Grid corporate role and pull forward metrics like 95% offer acceptance and $1M cost reduction.",
      "ats_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
      "positioning_statement": "This positions you as [specific strategic framing for this role]"
    }},
    "cover_letter": {{
      "opening_rationale": "Specific strategy. Example: Open with excitement about [ACTUAL COMPANY]'s mission and specific mention of fintech recruiting experience to immediately establish relevance.",
      "body_rationale": "What to emphasize/avoid with ACTUAL companies. Example: Focus on startup function-building experience at Spotify and specific fintech recruiting at Uber/Venmo. Avoid over-emphasizing National Grid corporate experience.",
      "close_rationale": "Confident but not pushy. Signals interest without desperation.",
      "positioning_statement": "This frames you as [strategic positioning]"
    }}
  }},
  
  "intelligence_layer": {{
    "job_quality_score": "Apply|Apply with caution|Skip — poor quality or low close rate",
    "quality_explanation": "3-5 substantive sentences explaining the rating",
    "strategic_positioning": {{
      "lead_with_strengths": ["2-3 specific items"],
      "gaps_and_mitigation": ["2-3 specific items"],
      "emphasis_points": ["2-3 actionable items"],
      "avoid_points": ["2-3 specific items"],
      "positioning_strategy": "1-2 substantive sentences"
    }},
    "salary_market_context": {{
      "typical_range": "Realistic estimate with reasoning",
      "posted_comp_assessment": "not mentioned|low|fair|strong",
      "recommended_expectations": "Specific and actionable guidance",
      "market_competitiveness": "2-3 substantive sentences",
      "risk_indicators": ["specific risks"] or []
    }},
    "apply_decision": {{
      "recommendation": "Apply|Apply with caution|Skip",
      "reasoning": "1-2 substantive sentences",
      "timing_guidance": "Specific guidance"
    }}
  }}
}}

=== VALIDATION CHECKLIST ===
Before returning response, verify:
1. ✅ First name extracted (not full name)
2. ✅ Company name from JD used throughout (no placeholders)
3. ✅ All arrays meet minimum lengths
4. ✅ No null/undefined/empty required fields
5. ✅ Outreach references ACTUAL candidate experience
6. ✅ No em dashes anywhere
7. ✅ Grammar perfect
8. ✅ Market data always provided
9. ✅ Action plan references actual company name
10. ✅ Changes summary references actual resume companies

Return ONLY valid JSON with no markdown formatting.
"""
```

---

## **WHERE TO INSERT**

**Location in backend.py:**
- Start: Around line 1050 (search for "INTELLIGENCE LAYER")
- End: Around line 1400 (end of prompt)
- Replace everything between these points

**Visual Guide:**

```python
# BEFORE (around line 1050):
        prompt = f"""You are an expert executive recruiter...

=== INTELLIGENCE LAYER (MANDATORY - MUST BE COMPLETE) ===

[OLD PROMPT CONTENT - DELETE ALL OF THIS]

"""  # ← prompt ends around line 1400

# AFTER:
        prompt = f"""You are an expert executive recruiter...

=== CRITICAL INSTRUCTIONS ===

[NEW ENHANCED PROMPT CONTENT - INSERT HERE]

"""  # ← keep same ending
```

---

## **EXACT STEPS**

1. Open `backend.py` in your editor
2. Press `Cmd+F` (Mac) or `Ctrl+F` (Windows)
3. Search for: `INTELLIGENCE LAYER`
4. Select from that line down to the closing `"""` (around line 1400)
5. Delete selected text
6. Paste the enhanced prompt above
7. Save file
8. Restart backend

---

## **RESTART BACKEND**

```bash
# Kill current process
pkill -f "uvicorn"

# Start with reload
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &

# Verify running
curl http://localhost:8000/health
```

---

## **TEST IT WORKS**

```bash
# Run a test analysis
# Should now see:
# - First name only in positioning
# - Actual company name (not [Company Name])
# - Populated action plan
# - Market data present
# - Comprehensive content

# Check logs for validation
tail -f logs/backend.log | grep "Phase 1"
```

---

## **VERIFICATION CHECKLIST**

After restart, test one job analysis:

- [ ] Positioning shows first name only ("Henry," not "Henry R. Bolden III,")
- [ ] Action plan has 3-4 tasks under TODAY
- [ ] Action plan references actual company name
- [ ] Salary strategy shows market data (not empty)
- [ ] Salary talking points populated (3-4 items)
- [ ] Outreach templates reference actual candidate experience
- [ ] No "[Company Name]" placeholders
- [ ] No em dashes in outreach
- [ ] Content feels personalized, not robotic

---

## **IF IT DOESN'T WORK**

### **Issue: Validation errors in logs**

**Fix:** Check that all required arrays are populated

### **Issue: Still seeing placeholders**

**Fix:** Company name not being extracted. Check JD has clear company name.

### **Issue: Still generic content**

**Fix:** Resume not being parsed correctly. Check resume format.

### **Issue: Backend won't start**

**Fix:** Syntax error in prompt. Check closing quotes and brackets.

**Rollback:**
```bash
pkill -f "uvicorn"
cp backend.py.backup.TONIGHT backend.py
uvicorn backend:app --reload &
```

---

## **TIMELINE**

- **Backup:** 30 seconds
- **Find section:** 1 minute
- **Replace prompt:** 5 minutes (copy/paste/verify)
- **Restart backend:** 30 seconds
- **Test:** 5 minutes
- **Total:** 12 minutes

---

## **SUCCESS LOOKS LIKE**

**Before (Current):**
```
Action Plan: [empty]
Strategic Framing: "frame yourself strategically..."
Market Data: "Market data available"
Outreach: "[Company Name]" placeholders
```

**After (Fixed):**
```
Action Plan:
  TODAY:
  - Apply via Coast ATS before end of day
  - Research hiring manager on LinkedIn...
  
Strategic Framing: "Henry, frame yourself as a fintech recruiting leader..."

Market Data: "Director of TA at Series B fintech: $180K-$230K in SF/NY..."

Outreach: "I'm excited about Coast's mission... my Uber/Venmo experience..."
```

---

You're ready to integrate! This should take 12 minutes max.

Let me know when backend is restarted and I'll verify it's working.
