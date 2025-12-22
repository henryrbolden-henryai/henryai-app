# Strategic Redirects - Implementation Guide

**Feature:** Strategic Redirects for Low-Fit Roles  
**Version:** 1.0  
**Last Updated:** December 20, 2025  
**Status:** Ready for Implementation

---

## Purpose

When a candidate's fit score is below 60% or their recommendation is "Skip" or "Do Not Apply," provide actionable alternative role suggestions that leverage their existing strengths without fabrication or level inflation.

**Core Principle:** Redirect toward leverage, not aspiration.

---

## Trigger Conditions

Strategic Redirects should activate when **any** of the following conditions are met:

1. `fit_score < 60`
2. `recommendation` in `["Skip", "Do Not Apply", "Long Shot"]`
3. `primary_gap_classification` in `["scope", "years", "domain"]` AND `fit_score < 70`

---

## Input Schema

```json
{
  "target_role": {
    "title": "Senior Product Manager",
    "level": "senior",
    "company_type": "Series B SaaS"
  },
  "candidate": {
    "current_level": "mid",
    "cec_strengths": [
      {"category": "Execution", "score": 85},
      {"category": "Collaboration", "score": 78},
      {"category": "Technical Depth", "score": 72}
    ],
    "recent_titles": [
      "Product Manager at Startup Co",
      "Associate PM at BigCorp"
    ],
    "company_types": ["Early-stage startup", "Enterprise"]
  },
  "gap_analysis": {
    "primary_gap": "scope",
    "secondary_gap": "years",
    "specific_gaps": [
      "Missing 2+ years at senior level",
      "Limited experience managing other PMs",
      "No demonstrated 0-1 product launches"
    ]
  }
}
```

---

## Output Schema

```json
{
  "strategic_redirects": {
    "adjacent_titles": [
      {
        "role_title": "Product Manager (Growth)",
        "level": "mid",
        "company_type": "Series A-B startups",
        "fit_rationale": "Your execution and analytics strengths map directly to growth PM requirements. Your startup experience is valued here."
      }
    ],
    "bridge_roles": [
      {
        "role_title": "Senior Associate Product Manager",
        "level": "mid-to-senior",
        "company_type": "Enterprise SaaS",
        "fit_rationale": "This role values your enterprise experience while giving you scope to demonstrate senior-level execution without the title jump."
      }
    ],
    "context_shifts": [
      {
        "role_title": "Product Manager",
        "level": "mid",
        "company_type": "B2B SaaS (10-50 employees)",
        "fit_rationale": "Your collaboration strength is critical in smaller teams. This environment rewards generalists over specialists."
      }
    ],
    "closing_message": "These roles better align with your current evidence and give you faster interview leverage."
  }
}
```

---

## System Prompt (For Claude API)

```
You are generating Strategic Redirects for a candidate whose job fit score is below 60% or whose recommendation is Skip / Do Not Apply.

Your goal is to redirect the candidate toward roles where their existing experience is more likely to convert into interviews without fabricating experience or inflating seniority.

INPUTS YOU WILL RECEIVE:
* Target role attempted
* Candidate's current level
* Top 3 Career Evidence Categories (CEC strengths)
* Primary gap classification (domain, scope, years, credibility)
* Recent titles and company types

OUTPUT 3–6 ROLES, GROUPED INTO:
1. Adjacent Titles (same level, different function or focus area)
2. Bridge Roles (−1 level or lateral with growth path)
3. Context Shifts (same title, different company environment)

FOR EACH ROLE, INCLUDE:
* Role title
* Level
* Typical company type
* Why this role is a stronger fit right now (1–2 sentences)

STRICT RULES:
* Do NOT suggest roles above the candidate's demonstrated level
* Do NOT repeat the original target role
* Do NOT reference job boards or live postings
* Do NOT use motivational or apologetic language ("You're still great!", "Don't give up!")
* Be specific and practical
* Base suggestions on CEC strengths, not aspirations
* Never fabricate experience to justify a suggestion

TONE: Strategic, direct, supportive. No fluff.

END WITH: "These roles better align with your current evidence and give you faster interview leverage."
```

---

## User Message Template (For Claude API)

```
Generate Strategic Redirects for this candidate:

TARGET ROLE ATTEMPTED:
{
  "title": "{{target_role_title}}",
  "level": "{{target_level}}",
  "company_type": "{{company_type}}"
}

CANDIDATE PROFILE:
{
  "current_level": "{{current_level}}",
  "cec_strengths": [
    {"category": "{{cec1_name}}", "score": {{cec1_score}}},
    {"category": "{{cec2_name}}", "score": {{cec2_score}}},
    {"category": "{{cec3_name}}", "score": {{cec3_score}}}
  ],
  "recent_titles": [
    "{{title1}}",
    "{{title2}}"
  ],
  "company_types": ["{{type1}}", "{{type2}}"]
}

GAP ANALYSIS:
{
  "primary_gap": "{{primary_gap}}",
  "secondary_gap": "{{secondary_gap}}",
  "specific_gaps": [
    "{{gap1}}",
    "{{gap2}}",
    "{{gap3}}"
  ]
}

CONTEXT:
* Fit score: {{fit_score}}%
* Recommendation: {{recommendation}}

Provide Strategic Redirects in JSON format matching the output schema.
```

---

## Implementation Steps (Claude Code)

### Step 1: Create Backend Endpoint

**File:** `backend/backend.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any

class StrategicRedirectRole(BaseModel):
    role_title: str
    level: str
    company_type: str
    fit_rationale: str

class StrategicRedirectsResponse(BaseModel):
    adjacent_titles: List[StrategicRedirectRole]
    bridge_roles: List[StrategicRedirectRole]
    context_shifts: List[StrategicRedirectRole]
    closing_message: str

class StrategicRedirectsRequest(BaseModel):
    target_role: Dict[str, str]
    candidate: Dict[str, Any]
    gap_analysis: Dict[str, Any]
    fit_score: int
    recommendation: str

@app.post("/api/strategic-redirects", response_model=StrategicRedirectsResponse)
async def generate_strategic_redirects(request: StrategicRedirectsRequest):
    """
    Generate alternative role suggestions for candidates with low fit scores
    """
    
    system_prompt = """You are generating Strategic Redirects for a candidate whose job fit score is below 60% or whose recommendation is Skip / Do Not Apply.

Your goal is to redirect the candidate toward roles where their existing experience is more likely to convert into interviews without fabricating experience or inflating seniority.

INPUTS YOU WILL RECEIVE:
* Target role attempted
* Candidate's current level
* Top 3 Career Evidence Categories (CEC strengths)
* Primary gap classification (domain, scope, years, credibility)
* Recent titles and company types

OUTPUT 3–6 ROLES, GROUPED INTO:
1. Adjacent Titles (same level, different function or focus area)
2. Bridge Roles (−1 level or lateral with growth path)
3. Context Shifts (same title, different company environment)

FOR EACH ROLE, INCLUDE:
* Role title
* Level
* Typical company type
* Why this role is a stronger fit right now (1–2 sentences)

STRICT RULES:
* Do NOT suggest roles above the candidate's demonstrated level
* Do NOT repeat the original target role
* Do NOT reference job boards or live postings
* Do NOT use motivational or apologetic language
* Be specific and practical
* Base suggestions on CEC strengths, not aspirations
* Never fabricate experience to justify a suggestion

TONE: Strategic, direct, supportive. No fluff.

Return as JSON matching this schema:
{
  "adjacent_titles": [{"role_title": "...", "level": "...", "company_type": "...", "fit_rationale": "..."}],
  "bridge_roles": [...],
  "context_shifts": [...],
  "closing_message": "These roles better align with your current evidence and give you faster interview leverage."
}
"""

    user_message = f"""Generate Strategic Redirects for this candidate:

TARGET ROLE ATTEMPTED:
{json.dumps(request.target_role, indent=2)}

CANDIDATE PROFILE:
{json.dumps(request.candidate, indent=2)}

GAP ANALYSIS:
{json.dumps(request.gap_analysis, indent=2)}

CONTEXT:
* Fit score: {request.fit_score}%
* Recommendation: {request.recommendation}

Provide Strategic Redirects in JSON format.
"""

    response = call_claude(system_prompt, user_message, max_tokens=2000)
    
    # Parse JSON response
    json_text = response.strip()
    if json_text.startswith("```"):
        json_text = json_text.split("```")[1]
        if json_text.startswith("json"):
            json_text = json_text[4:]
        json_text = json_text.strip()
    
    parsed = json.loads(json_text)
    
    return StrategicRedirectsResponse(**parsed)
```

---

### Step 2: Frontend Integration

**File:** `frontend/results.html`

Add after the recommendation section:

```javascript
// Check if Strategic Redirects should be shown
if (analysisData.fit_score < 60 || 
    ['Skip', 'Do Not Apply', 'Long Shot'].includes(analysisData.recommendation)) {
    
    // Fetch Strategic Redirects
    const redirectsResponse = await fetch(`${API_BASE_URL}/api/strategic-redirects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            target_role: {
                title: analysisData.role_title,
                level: analysisData.level || 'mid',
                company_type: analysisData.company_name
            },
            candidate: {
                current_level: analysisData.candidate_level || 'mid',
                cec_strengths: analysisData.cec_strengths || [],
                recent_titles: analysisData.recent_titles || [],
                company_types: analysisData.company_types || []
            },
            gap_analysis: {
                primary_gap: analysisData.primary_gap,
                secondary_gap: analysisData.secondary_gap,
                specific_gaps: analysisData.gaps
            },
            fit_score: analysisData.fit_score,
            recommendation: analysisData.recommendation
        })
    });
    
    if (redirectsResponse.ok) {
        const redirects = await redirectsResponse.json();
        displayStrategicRedirects(redirects);
    }
}

function displayStrategicRedirects(redirects) {
    const container = document.createElement('div');
    container.className = 'strategic-redirects-section';
    container.innerHTML = `
        <h2>Stronger Fits for You</h2>
        <p class="redirects-intro">Based on your current evidence, these roles give you better interview leverage:</p>
        
        ${renderRedirectGroup('Adjacent Roles', redirects.adjacent_titles)}
        ${renderRedirectGroup('Bridge Roles', redirects.bridge_roles)}
        ${renderRedirectGroup('Context Shifts', redirects.context_shifts)}
        
        <p class="redirects-closing">${redirects.closing_message}</p>
    `;
    
    // Insert after recommendation section
    const recommendationSection = document.querySelector('.recommendation-section');
    recommendationSection.after(container);
}

function renderRedirectGroup(title, roles) {
    if (!roles || roles.length === 0) return '';
    
    return `
        <div class="redirect-group">
            <h3>${title}</h3>
            ${roles.map(role => `
                <div class="redirect-card">
                    <div class="redirect-header">
                        <span class="redirect-title">${role.role_title}</span>
                        <span class="redirect-meta">${role.level} • ${role.company_type}</span>
                    </div>
                    <p class="redirect-rationale">${role.fit_rationale}</p>
                </div>
            `).join('')}
        </div>
    `;
}
```

---

### Step 3: Styling

**File:** `frontend/styles/main.css`

```css
.strategic-redirects-section {
    margin-top: 40px;
    padding: 32px;
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-radius: 16px;
}

.strategic-redirects-section h2 {
    font-size: 1.5rem;
    color: #60a5fa;
    margin-bottom: 12px;
}

.redirects-intro {
    color: #9ca3af;
    margin-bottom: 32px;
    font-size: 1rem;
}

.redirect-group {
    margin-bottom: 32px;
}

.redirect-group h3 {
    font-size: 1.1rem;
    color: #d1d5db;
    margin-bottom: 16px;
    font-weight: 600;
}

.redirect-card {
    background: rgba(96, 165, 250, 0.05);
    border: 1px solid rgba(96, 165, 250, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    transition: all 0.2s;
}

.redirect-card:hover {
    border-color: rgba(96, 165, 250, 0.4);
    background: rgba(96, 165, 250, 0.08);
}

.redirect-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 12px;
}

.redirect-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
}

.redirect-meta {
    font-size: 0.85rem;
    color: #9ca3af;
}

.redirect-rationale {
    color: #d1d5db;
    line-height: 1.6;
    margin: 0;
}

.redirects-closing {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #374151;
    color: #60a5fa;
    font-weight: 500;
    text-align: center;
}
```

---

## Testing Checklist

- [ ] Trigger conditions work correctly (fit_score < 60)
- [ ] No level inflation (suggested roles never above candidate's level)
- [ ] CEC strengths properly inform suggestions
- [ ] No motivational/apologetic language in output
- [ ] Bridge roles are actually -1 level or lateral
- [ ] Context shifts maintain same title, different environment
- [ ] JSON parsing handles malformed responses gracefully
- [ ] UI displays all three groups correctly
- [ ] Closing message always appears

---

## Example Output

**Input:**
- Target Role: Senior Product Manager at Series B
- Candidate Level: Mid
- Fit Score: 42%
- Primary Gap: Scope (missing senior-level ownership)

**Output:**

**Adjacent Roles:**
1. **Product Manager (Growth)** • Mid • Series A-B startups  
   *Your execution and analytics strengths map directly to growth PM requirements. Your startup experience is valued here.*

2. **Technical Product Manager** • Mid • B2B SaaS  
   *Your technical depth CEC score (72) positions you well for more engineering-adjacent PM work.*

**Bridge Roles:**
1. **Senior Associate Product Manager** • Mid-to-Senior • Enterprise SaaS  
   *This role values your enterprise experience while giving you scope to demonstrate senior-level execution without the title jump.*

**Context Shifts:**
1. **Product Manager** • Mid • Early-stage startups (5-20 employees)  
   *Your collaboration strength is critical in smaller teams. This environment rewards generalists over specialists.*

*These roles better align with your current evidence and give you faster interview leverage.*

---

## Edge Cases

### No CEC Data Available
- Fall back to generic role suggestions based on target role family
- Focus on level-appropriate alternatives only

### All Suggestions Too Similar
- Expand to 2-3 industries/contexts
- Include at least one context shift

### Candidate at Entry Level
- Skip Bridge Roles section (no -1 level available)
- Focus on Adjacent Titles and Context Shifts

---

## Future Enhancements

1. **Live Job Matching** - Connect suggestions to actual open roles (requires job board API)
2. **Success Rate Data** - Track which redirects lead to interviews
3. **Personalized Weighting** - Adjust suggestions based on user's stated preferences
4. **Salary Ranges** - Include expected comp for each suggested role

---

**Status:** Ready for implementation  
**Priority:** Medium (enhances low-fit user experience)  
**Estimated Effort:** 1-2 days (backend + frontend + testing)
