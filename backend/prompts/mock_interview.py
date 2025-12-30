"""Mock interview prompts for HenryAI backend"""

MOCK_GENERATE_QUESTION_PROMPT = """You are conducting a mock interview for a {interview_stage} stage.

CANDIDATE NAME: {candidate_name}

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
Company: {company}
Role: {role_title}

JOB DESCRIPTION:
{job_description}

INTERVIEW STAGE: {interview_stage}
DIFFICULTY LEVEL: {difficulty}
QUESTIONS ALREADY ASKED: {asked_questions}

Generate a behavioral or technical question that:
1. Tests competency in {competency_area}
2. Is realistic for this interview stage
3. Is answerable using candidate's actual work experience
4. Matches the difficulty level
5. Does not repeat previously asked questions
6. IMPORTANT: Start the question with a natural, conversational opener that uses the candidate's first name (e.g., "Okay {candidate_name},", "So {candidate_name},", "Alright {candidate_name},", "{candidate_name},")

DIFFICULTY GUIDELINES:
- Easy: Straightforward STAR questions, clear scenarios
- Medium: Multi-faceted situations, requires prioritization or tradeoffs
- Hard: Ambiguous scenarios, strategic thinking, handling conflict/failure

OUTPUT FORMAT:
Return JSON:
{{
    "question_text": "string (the actual question, starting with the candidate's name)",
    "competency_tested": "string (primary competency being evaluated)",
    "difficulty": "easy|medium|hard"
}}

No markdown, no preamble."""


MOCK_ANALYZE_RESPONSE_PROMPT = """Analyze this candidate's COMPLETE response to a mock interview question, including all their follow-up answers.

QUESTION: {question_text}
EXPECTED COMPETENCY: {competency}
TARGET LEVEL: {target_level}
ROLE TYPE: {role_type}

COMPLETE RESPONSE HISTORY:
{all_responses}

CANDIDATE BACKGROUND:
{resume_text}

IMPORTANT: Score based on the CUMULATIVE quality of ALL responses, not just the latest one. If the candidate's follow-up answers filled gaps or added valuable details, their score should improve significantly.

## SIGNAL TRACKING
For each response, evaluate these 11 signals (score 0.0 to 1.0):

1. **functional_competency** - Does the candidate demonstrate relevant functional knowledge for their role?
2. **leadership** - Team direction, influence, decision-making
3. **collaboration** - Cross-team work, partnership, relationship building
4. **ownership** - End-to-end accountability, "I" statements, taking responsibility
5. **strategic_thinking** - High-level planning, long-term vision, business context
6. **problem_solving** - Structured thinking, root cause analysis, creative solutions
7. **communication_clarity** - Concise, clear, well-structured responses
8. **metrics_orientation** - Uses numbers, percentages, measurable outcomes
9. **stakeholder_management** - Managing up/across, influencing without authority
10. **executive_presence** - Confidence, gravitas, ability to communicate to senior leaders (if applicable)
11. **user_centricity** - Customer/user focus (for PM/UX/UI roles)

## FOLLOW-UP TRIGGER RULES
Trigger a follow-up when you detect:
- **missing_metrics**: Answer lacks numbers or measurable outcomes
- **vague_answer**: Too broad, no specifics, missing "what YOU did"
- **no_conflict**: Too polished, no mention of challenges or obstacles
- **no_strategy**: Jumps to solution without explaining thinking process
- **no_user_focus**: (PM/UX) Missing user insight or customer perspective
- **no_technical_depth**: (SWE) Missing architectural or technical reasoning

## LEVEL GUIDELINES
- **Mid-level**: Strong functional competency + okay communication
- **Senior**: Strong functional + problem solving + some strategy
- **Director**: Solid strategy + cross-functional influence + leadership
- **Executive**: Vision + executive presence + organizational impact

OUTPUT FORMAT:
Return JSON:
{{
    "score": integer (1-10, reflecting cumulative quality),
    "level_demonstrated": "mid" | "senior" | "director" | "executive",
    "signals": {{
        "functional_competency": float (0.0-1.0),
        "leadership": float (0.0-1.0),
        "collaboration": float (0.0-1.0),
        "ownership": float (0.0-1.0),
        "strategic_thinking": float (0.0-1.0),
        "problem_solving": float (0.0-1.0),
        "communication_clarity": float (0.0-1.0),
        "metrics_orientation": float (0.0-1.0),
        "stakeholder_management": float (0.0-1.0),
        "executive_presence": float (0.0-1.0),
        "user_centricity": float (0.0-1.0)
    }},
    "signal_strengths": ["signals >= 0.7"],
    "signal_gaps": ["signals <= 0.4"],
    "follow_up_trigger": "missing_metrics" | "vague_answer" | "no_conflict" | "no_strategy" | "no_user_focus" | "no_technical_depth" | null,
    "follow_up_questions": ["question1", "question2"],
    "brief_feedback": "string (1-2 sentences of immediate coaching)",
    "resume_content": {{
        "metrics": ["specific metric or number mentioned"],
        "achievements": ["specific accomplishment they described"],
        "stories": ["brief summary of any STAR story they told"]
    }}
}}

RULES:
- Score should INCREASE if follow-up responses added valuable detail
- Be specific about gaps (not "needs more detail" but "didn't mention stakeholder alignment")
- Only generate follow-ups if there's a clear trigger; otherwise set follow_up_trigger to null
- Extract concrete numbers, percentages, or metrics for resume enhancement

No markdown, no preamble."""


MOCK_QUESTION_FEEDBACK_PROMPT = """Provide comprehensive coaching feedback after this mock interview question.

QUESTION: {question_text}
COMPETENCY TESTED: {competency}
TARGET LEVEL: {target_level}

ALL CANDIDATE RESPONSES:
{all_responses_text}

ANALYSIS:
{analysis_json}

CANDIDATE BACKGROUND:
{resume_text}

Generate detailed feedback covering:
1. Overall assessment (2-3 sentences)
2. What landed (2-3 specific things they did well)
3. What didn't land (2-3 specific gaps or weaknesses)
4. Coaching (actionable advice for improvement)
5. Revised answer (rewrite their response at the target level using their actual experience)

OUTPUT FORMAT:
Return JSON:
{{
    "overall_assessment": "string (2-3 sentences)",
    "what_landed": ["bullet1", "bullet2", "bullet3"],
    "what_didnt_land": ["bullet1", "bullet2", "bullet3"],
    "coaching": "string (2-3 paragraphs of specific advice)",
    "revised_answer": "string (their answer rewritten at target level)"
}}

RULES FOR REVISED ANSWER:
- Use only their actual work experience (no fabrication)
- Elevate to target level (L4 → L5A → L5B)
- Include specific metrics, outcomes, and scope
- Follow STAR structure (Situation, Task, Action, Result)
- Keep it realistic (what they COULD have said, not fantasy)

COACHING GUIDELINES:
- Be direct and specific
- Reference actual gaps from their responses
- Provide tactical fixes (not just "be more strategic")
- Connect to competency frameworks

No markdown, no preamble."""


MOCK_SESSION_FEEDBACK_PROMPT = """Generate comprehensive feedback for this completed mock interview session.

SESSION DETAILS:
- Interview Stage: {interview_stage}
- Role Type: {role_type}
- Questions Completed: {num_questions}
- Average Score: {average_score}
- Level Demonstrated: {level_demonstrated}

## AGGREGATED SIGNAL SCORES (0.0 - 1.0)
{signal_summary}

## SIGNAL STRENGTHS (≥ 0.7)
{signal_strengths}

## SIGNAL GAPS (≤ 0.4)
{signal_gaps}

QUESTION SUMMARIES:
{questions_summary}

CANDIDATE BACKGROUND:
{resume_text}

TARGET ROLE:
Company: {company}
Role: {role_title}

JOB DESCRIPTION:
{job_description}

Generate session-level feedback covering:
1. Overall assessment (2-3 sentences on readiness)
2. Key strengths (3 specific things based on signal strengths)
3. Areas to improve (3 specific things based on signal gaps)
4. Coaching priorities (3 specific drills/exercises based on gaps)
5. Recommended drills (map to weak signals)
6. Readiness score: "Ready" | "Almost Ready" | "Needs Practice"
7. Level estimate: "mid" | "senior" | "director" | "executive"

READINESS CRITERIA:
- Ready: Average score ≥8, no signal gaps below 0.3, level-appropriate
- Almost Ready: Average score 6-7.9, 1-2 minor signal gaps, mostly level-appropriate
- Needs Practice: Average score <6, multiple signal gaps, below-level

DRILL MAPPING:
- Low metrics_orientation → "Practice adding specific numbers and outcomes to every story"
- Low ownership → "Rewrite stories using 'I' statements and personal accountability"
- Low strategic_thinking → "Practice framing answers with business context first"
- Low stakeholder_management → "Add examples of cross-functional influence to your stories"
- Low communication_clarity → "Practice STAR structure: Situation, Task, Action, Result"
- Low problem_solving → "Practice explaining your decision-making framework step by step"

OUTPUT FORMAT:
Return JSON:
{{
    "overall_assessment": "string (2-3 sentences)",
    "key_strengths": ["strength1", "strength2", "strength3"],
    "areas_to_improve": ["area1", "area2", "area3"],
    "coaching_priorities": ["priority1", "priority2", "priority3"],
    "recommended_drills": ["drill1", "drill2", "drill3"],
    "readiness_score": "Ready" | "Almost Ready" | "Needs Practice",
    "level_estimate": "mid" | "senior" | "director" | "executive",
    "next_steps": "string (what to do next)"
}}

RULES:
- Strengths should be specific and tied to signals (not "good communication" but "strong ownership signals - consistently used 'I' statements")
- Improvements should be actionable and tied to signal gaps
- Drills should directly address the weakest signals
- Level estimate should match demonstrated signals across all questions

No markdown, no preamble."""
