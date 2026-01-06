"""
Resume Amplification

When strength assessment triggers needs_amplification, this module runs
an amplification pass on weak bullets to strengthen them without fabricating.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# =============================================================================
# AMPLIFICATION SYSTEM PROMPT
# =============================================================================
AMPLIFICATION_SYSTEM_PROMPT = """
You are an elite executive resume writer. Your job is to strengthen resume bullets without fabricating facts.

## YOUR TASK
For each weak bullet provided, rewrite it to be stronger while preserving factual accuracy.

## WHAT MAKES A STRONG BULLET
1. **Explicit Scope**: Team size, budget, user count, geography, or authority level
2. **Specific Outcome**: Metric + business consequence (not just activity)
3. **Power Verb**: Led, drove, owned, defined, built, launched, scaled (not helped, supported, worked on)
4. **Comparative Context**: vs prior state, vs benchmark, ranking, percentile
5. **Business Impact**: Revenue, cost, efficiency, risk, retention, growth

## RULES (CRITICAL - VIOLATION = FAILURE)
- Do NOT add facts that aren't reasonably implied by the original
- Do NOT inflate titles, scope, or outcomes
- Do NOT fabricate metrics or percentages
- Do NOT change the core claim or job function
- DO sharpen verb choice (helped → drove, worked on → built)
- DO make implicit scope explicit IF reasonable (e.g., "managed team" can ask "how many?")
- DO add comparative framing where logical ("reduced X" → "reduced X by [asking for metric]")
- DO elevate language to match the target seniority level

## WHAT YOU CAN REASONABLY INFER
- If someone "managed a team" at a restaurant, a shift team of 5-15 is reasonable
- If someone "led a project," there were likely stakeholders and deliverables
- If someone "improved a process," there was a measurable before/after state
- Industry context: Tech PM = agile, scrum, sprints. Finance = compliance, risk. Retail = inventory, shrink.

## WHAT YOU CANNOT INFER (SET needs_user_input = true)
- Specific percentages without basis in the original text
- Dollar amounts or revenue figures
- Rankings or competitive comparisons
- Specific team sizes when not implied
- Metrics that would require data to verify

## CONFIDENCE LEVELS
- **high**: Rewrite only sharpens language, adds no new facts
- **medium**: Rewrite makes reasonable inferences from context
- **low**: Rewrite needs user confirmation for added details

## OUTPUT FORMAT
Return a JSON array. For each bullet, return:
```json
{
  "original": "The original bullet text",
  "rewritten": "The strengthened bullet text",
  "changes": "Brief description of what changed and why",
  "missing_signal_addressed": ["scope", "outcome", "verb_strength", "comparative", "business_impact"],
  "confidence": "high" | "medium" | "low",
  "needs_user_input": true | false,
  "user_prompt": "Question to ask if needs_user_input is true, otherwise null"
}
```

Your response must be ONLY valid JSON array. No markdown, no explanation outside the JSON.
"""


def build_amplification_prompt(
    weak_bullets: List[Dict[str, Any]],
    level: str,
    target_role: Optional[str] = None,
    company_context: Optional[str] = None
) -> str:
    """
    Build the user prompt for amplification pass.

    Args:
        weak_bullets: List of weak bullet dicts with 'bullet', 'score', 'missing' keys
        level: Candidate level ('entry', 'mid', 'senior', 'director')
        target_role: The role they're applying for (optional)
        company_context: Context about target company (optional)
    """
    # Format bullets for the prompt
    bullets_formatted = []
    for i, b in enumerate(weak_bullets, 1):
        bullets_formatted.append(
            f"{i}. Original: \"{b['bullet']}\"\n"
            f"   Score: {b.get('score', 'N/A')}/100\n"
            f"   Missing: {', '.join(b.get('missing', ['unknown']))}"
        )

    bullets_text = "\n\n".join(bullets_formatted)

    # Build context section
    context_parts = [f"## CANDIDATE LEVEL\n{level.upper()}"]

    if target_role:
        context_parts.append(f"## TARGET ROLE\n{target_role}")

    if company_context:
        context_parts.append(f"## COMPANY CONTEXT\n{company_context}")

    context_section = "\n\n".join(context_parts)

    return f"""
{context_section}

## WEAK BULLETS TO STRENGTHEN
{bullets_text}

Strengthen each bullet following the rules in the system prompt. Return ONLY a JSON array with one object per bullet.
"""


# =============================================================================
# AMPLIFICATION RUNNER
# =============================================================================
async def run_amplification(
    weak_bullets: List[Dict[str, Any]],
    level: str,
    call_claude_fn,
    target_role: Optional[str] = None,
    company_context: Optional[str] = None,
    max_tokens: int = 2000
) -> List[Dict[str, Any]]:
    """
    Run the amplification pass on weak bullets.

    Args:
        weak_bullets: List of weak bullet dicts
        level: Candidate level
        call_claude_fn: Function to call Claude API
        target_role: Target role for context
        company_context: Company context for tailoring
        max_tokens: Max tokens for response

    Returns:
        List of amplification results
    """
    if not weak_bullets:
        return []

    user_prompt = build_amplification_prompt(
        weak_bullets=weak_bullets,
        level=level,
        target_role=target_role,
        company_context=company_context
    )

    try:
        response = call_claude_fn(
            system_prompt=AMPLIFICATION_SYSTEM_PROMPT,
            user_message=user_prompt,
            max_tokens=max_tokens
        )

        # Clean and parse response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # Remove markdown code blocks
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        results = json.loads(cleaned)

        # Validate structure
        if not isinstance(results, list):
            results = [results]

        # Ensure each result has required fields
        validated_results = []
        for r in results:
            validated_results.append({
                "original": r.get("original", ""),
                "rewritten": r.get("rewritten", r.get("original", "")),
                "changes": r.get("changes", ""),
                "missing_signal_addressed": r.get("missing_signal_addressed", []),
                "confidence": r.get("confidence", "medium"),
                "needs_user_input": r.get("needs_user_input", False),
                "user_prompt": r.get("user_prompt")
            })

        return validated_results

    except json.JSONDecodeError as e:
        print(f"Failed to parse amplification response: {e}")
        # Return empty results that preserve originals
        return [
            {
                "original": b["bullet"],
                "rewritten": b["bullet"],
                "changes": "Amplification failed - keeping original",
                "missing_signal_addressed": [],
                "confidence": "low",
                "needs_user_input": True,
                "user_prompt": f"Please provide more details about: {b['bullet'][:50]}..."
            }
            for b in weak_bullets
        ]
    except Exception as e:
        print(f"Amplification error: {e}")
        raise


# =============================================================================
# SINGLE BULLET AMPLIFICATION (for Phase 2 follow-ups)
# =============================================================================
SINGLE_BULLET_PROMPT = """
You are strengthening a single resume bullet based on new information the user provided.

## ORIGINAL BULLET
{original}

## USER'S ADDITIONAL CONTEXT
{user_context}

## TASK
Rewrite the bullet incorporating the user's context. Follow these rules:
1. Use ONLY what the user explicitly stated - no embellishment
2. Integrate their context naturally into the bullet
3. Use strong action verbs appropriate for {level} level
4. Include any metrics they provided
5. Keep it concise (under 30 words ideally)

Return JSON:
```json
{{
  "rewritten": "The strengthened bullet",
  "changes": "What was incorporated from user input",
  "confidence": "high"
}}
```
"""


async def amplify_with_user_input(
    original_bullet: str,
    user_context: str,
    level: str,
    call_claude_fn
) -> Dict[str, Any]:
    """
    Amplify a single bullet with user-provided context.

    Args:
        original_bullet: The original bullet text
        user_context: User's answer to the Phase 2 question
        level: Candidate level
        call_claude_fn: Function to call Claude API

    Returns:
        Amplification result dict
    """
    prompt = SINGLE_BULLET_PROMPT.format(
        original=original_bullet,
        user_context=user_context,
        level=level
    )

    try:
        response = call_claude_fn(
            system_prompt="You are a resume writing expert. Return only valid JSON.",
            user_message=prompt,
            max_tokens=500
        )

        # Clean and parse
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        result = json.loads(cleaned)

        return {
            "original": original_bullet,
            "rewritten": result.get("rewritten", original_bullet),
            "changes": result.get("changes", "Incorporated user context"),
            "confidence": result.get("confidence", "high"),
            "needs_user_input": False,
            "user_prompt": None,
            "user_input_used": True
        }

    except Exception as e:
        print(f"Single bullet amplification error: {e}")
        return {
            "original": original_bullet,
            "rewritten": original_bullet,
            "changes": "Failed to incorporate context",
            "confidence": "low",
            "needs_user_input": False,
            "user_prompt": None
        }


# =============================================================================
# BATCH PROCESSING
# =============================================================================
@dataclass
class AmplificationBatch:
    """Result of a batch amplification run."""
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
    needs_user_input: List[Dict[str, Any]]
    total_improvement: int  # Sum of score improvements


async def process_amplification_batch(
    weak_bullets: List[Dict[str, Any]],
    level: str,
    call_claude_fn,
    target_role: Optional[str] = None
) -> AmplificationBatch:
    """
    Process a batch of weak bullets through amplification.

    Args:
        weak_bullets: List of weak bullet dicts
        level: Candidate level
        call_claude_fn: Function to call Claude API
        target_role: Target role for context

    Returns:
        AmplificationBatch with categorized results
    """
    from resume_strength_gate import bullet_strength_score, apply_amplification

    # Run amplification
    amplified_results = await run_amplification(
        weak_bullets=weak_bullets,
        level=level,
        call_claude_fn=call_claude_fn,
        target_role=target_role
    )

    successful = []
    failed = []
    needs_user_input = []
    total_improvement = 0

    # Process each result
    for i, amp_result in enumerate(amplified_results):
        if i < len(weak_bullets):
            original_bullet = weak_bullets[i]["bullet"]
            original_score = weak_bullets[i].get("score", 0)
        else:
            continue

        # Apply the amplification
        applied = apply_amplification(amp_result, original_bullet, level)

        result_with_context = {
            **amp_result,
            "original_score": original_score,
            "new_score": applied.score_after,
            "improvement": applied.improvement,
            "action": applied.action,
            "applied": applied.applied
        }

        if applied.action == "apply":
            successful.append(result_with_context)
            total_improvement += applied.improvement
        elif applied.action == "queue_for_phase_2":
            needs_user_input.append(result_with_context)
        else:
            failed.append(result_with_context)

    return AmplificationBatch(
        successful=successful,
        failed=failed,
        needs_user_input=needs_user_input,
        total_improvement=total_improvement
    )


# =============================================================================
# INTEGRATION HELPER
# =============================================================================
def prepare_amplification_summary(batch: AmplificationBatch) -> Dict[str, Any]:
    """
    Prepare a summary of amplification results for the frontend.

    Args:
        batch: AmplificationBatch result

    Returns:
        Summary dict for API response
    """
    return {
        "amplification_complete": True,
        "bullets_strengthened": len(batch.successful),
        "bullets_need_input": len(batch.needs_user_input),
        "bullets_unchanged": len(batch.failed),
        "total_score_improvement": batch.total_improvement,
        "strengthened_bullets": [
            {
                "original": s["original"],
                "rewritten": s["rewritten"],
                "score_before": s["original_score"],
                "score_after": s["new_score"],
                "improvement": s["improvement"],
                "changes": s["changes"]
            }
            for s in batch.successful
        ],
        "needs_user_input": [
            {
                "original": n["original"],
                "question": n.get("user_prompt", "Can you provide more details about this?"),
                "score": n["original_score"]
            }
            for n in batch.needs_user_input
        ],
        "unchanged_bullets": [
            {
                "bullet": f["original"],
                "reason": f.get("changes", "Could not strengthen")
            }
            for f in batch.failed
        ]
    }
