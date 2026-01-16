"""
Story Bank prompts for AI story generation, coaching cues, and recommendations.
"""

# ============================================
# CORE 3 STORY GENERATION PROMPT
# ============================================

STORY_GENERATION_PROMPT = """You are a recruiter-grade interview coach.
Using the candidate's resume and the target role, generate 2–3 **STAR interview stories** scoped to the **interview stage** (Recruiter Screen, Hiring Manager, Executive).

Rules:

* Stories must be **truth-adjacent** to resume experience. No fabrication.
* Anchor to real roles, companies, scope, and outcomes from the resume.
* Adjust depth and framing by stage:

  * Recruiter: clarity, scope, basics
  * Hiring Manager: execution, tradeoffs, impact
  * Executive: influence, ambiguity, scale
* Keep each section concise. No buzzwords.

Output format (JSON array):

* Title
* Competency demonstrated
* STAR (Situation, Task, Action, Result)
* Best used for these questions
* Confidence level: Low (AI draft)

These are drafts. The candidate will edit and finalize.

=== RESUME ===
{resume_text}

=== TARGET CONTEXT ===
Target Role: {target_role}
Role Level: {role_level}
Interview Stage: {interview_stage}
Competencies to Cover: {competencies}

Return valid JSON only."""


# ============================================
# CORE 3 STORY GENERATION (SPECIFIC)
# ============================================

CORE_3_GENERATION_PROMPT = """You are a recruiter-grade interview coach.
Using the candidate's resume, generate exactly 3 **Core Interview Stories** tailored for their target role and company.

1. **Leadership / Influence** - Leading a team, driving alignment, influencing without authority
2. **Execution / Problem-Solving** - Shipping under pressure, debugging complex issues, delivering results
3. **Failure / Conflict** - Learning from mistakes, resolving disagreements, handling setbacks

Rules:

* Stories must be **truth-adjacent** to resume experience. No fabrication.
* Anchor to real roles, companies, scope, and outcomes from the resume.
* **Tailor stories to the target company and role** - emphasize relevant experience that would resonate with this specific opportunity.
* Each story needs a **one-sentence opening line** that hooks the interviewer immediately.
* Adjust depth for the interview stage: {interview_stage}
  * Recruiter: clarity, scope, basics (2 min max)
  * Hiring Manager: execution, tradeoffs, impact (3 min max)
  * Executive: influence, ambiguity, scale (2-3 min)
* Keep each STAR section concise. No buzzwords.

=== RESUME ===
{resume_text}

=== TARGET CONTEXT ===
Target Company: {target_company}
Target Role: {target_role}
Role Level: {role_level}
Interview Stage: {interview_stage}

=== OUTPUT FORMAT (JSON) ===

Return an array of exactly 3 stories:

[
  {{
    "title": "Short memorable name (e.g., 'Uber Launch Crisis')",
    "core_category": "Leadership / Influence",
    "opening_line": "One sentence that hooks - e.g., 'I had to ship a product in 3 weeks that was supposed to take 3 months.'",
    "demonstrates": ["Leadership", "Influence", "Strategic Thinking"],
    "situation": "2-3 sentences setting the scene with stakes",
    "task": "What YOU were specifically responsible for",
    "action": "3-5 specific steps YOU took (first person, not 'we')",
    "result": "Quantified outcome or clear impact",
    "best_for_questions": ["Tell me about a time you led...", "Describe influencing without authority..."],
    "interview_stages": ["recruiter_screen", "hiring_manager"],
    "role_level": "{role_level}",
    "resume_evidence": "The specific bullet or experience this is based on",
    "is_core": true,
    "source": "AI Draft",
    "confidence": "Low"
  }},
  {{
    "title": "...",
    "core_category": "Execution / Problem-Solving",
    ...
  }},
  {{
    "title": "...",
    "core_category": "Failure / Conflict",
    ...
  }}
]

Return ONLY valid JSON, no markdown or preamble."""


# ============================================
# COACHING CUES GENERATION
# ============================================

COACHING_CUES_PROMPT = """You are a senior interview coach generating delivery cues for a candidate's story.

=== THE STORY ===
Title: {story_title}
Opening Line: {opening_line}

Situation: {situation}
Task: {task}
Action: {action}
Result: {result}

Demonstrates: {demonstrates}
Interview Stage: {interview_stage}

=== GENERATE COACHING CUES ===

For this story, generate:

1. **emphasize** (1-2 bullets): What to lean into - the parts that make this story land.
2. **avoid** (1-2 bullets): What NOT to say - tangents, weak framings, or filler.
3. **stop_talking_when**: A single hard-stop signal - the exact moment to wrap up. Be specific.
4. **recovery_line**: A pivot phrase if they're losing the interviewer. Format: "If you want the short version..."

=== OUTPUT FORMAT (JSON) ===

{{
  "emphasize": [
    "Highlight the specific metric in the result - it's concrete proof",
    "Emphasize the tradeoff you made - shows judgment"
  ],
  "avoid": [
    "Don't dive into the technical details of X unless asked",
    "Skip the backstory about the team dynamics"
  ],
  "stop_talking_when": "After you land the result, stop. Don't add the lesson learned unless asked.",
  "recovery_line": "If you want the short version: I inherited a broken process, rebuilt it in 3 weeks, and it became the template for the org."
}}

Return ONLY valid JSON."""


# ============================================
# RECOMMENDATION SCORING (CONTEXT PROMPT)
# ============================================

RECOMMENDATION_CONTEXT_PROMPT = """You are analyzing which stories best match an interview context.

=== INTERVIEW CONTEXT ===
Company: {company}
Role: {role_title}
Interview Stage: {interview_stage}
Role Level: {role_level}
Company Type: {company_type}
Key Competencies Expected: {competencies}

=== CANDIDATE'S STORY BANK ===
{stories_json}

=== SCORING CRITERIA ===

Score = (effectiveness_avg × 0.4)
      + (competency_match × 0.25)
      + (stage_fit × 0.2)
      + (recency_bonus × 0.1)
      - (overuse_penalty × 0.15)

Assign tiers:
- "Lead with this" - score >= 70 and times_used < 3
- "Strong backup" - score >= 50
- "Retire soon" - times_used >= 3 AND effectiveness_avg < 3.5

=== OUTPUT FORMAT (JSON) ===

{{
  "primary_recommendations": [
    {{
      "story_id": "uuid",
      "story_name": "Story Title",
      "score": 85,
      "recommendation_tier": "Lead with this",
      "reason": "Strong leadership story with 4.2 effectiveness. Not overused. Matches HM stage.",
      "competency_match": ["Leadership", "Influence"],
      "freshness_penalty": 0
    }}
  ],
  "backup_recommendations": [...],
  "retire_soon": [...],
  "coverage_gaps": ["Technical depth not well-covered"]
}}

Return top 3 primary, top 2 backup, any stories flagged for retirement."""


# ============================================
# INSIGHTS GENERATION
# ============================================

INSIGHTS_GENERATION_PROMPT = """Analyze the candidate's story performance data and generate actionable insights.

=== STORY PERFORMANCE DATA ===
{performance_data}

=== GENERATE INSIGHTS ===

Look for patterns:
- Which stories work best for Director vs VP roles?
- Which land with Big Tech vs startups?
- Which die in recruiter screens but win with hiring managers?
- Any stories that are overused but still performing?
- Any underused gems with high effectiveness?

=== OUTPUT FORMAT (JSON) ===

{{
  "actionable_insights": [
    "Your 'Launch Crisis' story kills with hiring managers (4.5 avg) but bombs with recruiters (2.3 avg). Lead with something simpler in screens.",
    "You're over-relying on 'Team Conflict' (used 5x). It's still effective but rotate in your 'Cross-Functional' story.",
    "Your startup stories underperform at Big Tech. Emphasize scale and process when interviewing there."
  ]
}}

Be specific. Reference actual story names and numbers. No generic advice."""


# ============================================
# TEMPLATE STORY GENERATION
# ============================================

TEMPLATE_STORY_PROMPT = """You are helping a candidate build a STAR story from a template.

=== TEMPLATE ===
Name: {template_name}
Category: {template_category}
Demonstrates: {demonstrates}

=== USER'S RESPONSES ===
Situation: {user_situation}
Task: {user_task}
Action: {user_action}
Result: {user_result}

=== YOUR JOB ===

1. Clean up the user's responses into polished STAR format
2. Generate a one-sentence opening line
3. Generate coaching cues for delivery
4. Flag any sections that need more detail (mark as [NEEDS DETAIL])

=== OUTPUT FORMAT (JSON) ===

{{
  "story_name": "Short memorable title based on content",
  "opening_line": "One sentence hook",
  "situation": "Cleaned up situation (2-3 sentences)",
  "task": "Cleaned up task",
  "action": "Cleaned up action (3-5 steps)",
  "result": "Cleaned up result with metrics if provided",
  "needs_detail": ["result - add a specific metric if possible"],
  "coaching_cues": {{
    "emphasize": [...],
    "avoid": [...],
    "stop_talking_when": "...",
    "recovery_line": "..."
  }}
}}

Return ONLY valid JSON."""
