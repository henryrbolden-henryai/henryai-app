# Outreach Template Quality Control — Backend Changes

## Summary

Added strict quality control rules and validation for outreach templates to ensure they use correct grammar, professional punctuation, and position candidates for success. This addresses the requirement that outreach messages should never contain em dashes, exclamation points, generic phrases, or poor positioning.

---

## What Changed

### 1. **Added Strict Rules to System Prompts**

Both `/api/jd/analyze` and `/api/documents/generate` endpoints now include explicit outreach template rules:

**Critical Rules Added:**
- Use ONLY professional punctuation (periods, commas, semicolons, colons)
- NO em dashes (—) or en dashes (–)
- NO exclamation points (signal desperation)
- Every claim must be traceable to candidate's actual resume
- NO generic phrases like "I'm excited about this opportunity", "I'd love to chat", etc.
- Reference specific companies, roles, and metrics from resume
- Use active voice only
- Each sentence under 30 words
- End with clear, specific ask
- Lead with value, not flattery

**Good Example Included:**
```
"Hi [Name], I'm reaching out about the Senior PM role. I've spent 5 years building B2B products at Uber and Spotify, most recently launching a marketplace feature that drove $12M ARR. Your focus on payment infrastructure aligns with my fintech background. Would you be open to a 20-minute call next week?"
```

**Bad Example (to avoid):**
```
"Hi [Name]! I'm super excited about this opportunity—it seems like a great fit for my background. I'd love to chat about how I could contribute to the team!"
```

---

### 2. **New Validation Function**

Added `validate_outreach_template()` function that checks for:
- Em dashes and en dashes
- Exclamation points
- Generic phrases (comprehensive list)
- Sentence length (flags if >35 words)
- Passive voice indicators
- Clear call-to-action
- Minimum/maximum length requirements

Returns `(is_valid, error_messages)` tuple.

---

### 3. **New Cleanup Function**

Added `cleanup_outreach_template()` function that automatically fixes:
- Replaces em dashes (—) with colons
- Replaces en dashes (–) with colons
- Removes exclamation points (replaces with periods)
- Fixes double spaces
- Fixes double periods

---

### 4. **Automatic Validation & Cleanup**

Both endpoints now automatically:
1. Parse the outreach templates from Claude's response
2. Validate hiring manager and recruiter templates
3. Log warnings if quality issues are detected
4. Apply automatic cleanup for common formatting issues
5. Return cleaned templates to frontend

This happens transparently — the frontend receives properly formatted templates.

---

## Files Modified

- `backend.py` (lines 276-384, 1310-1336, 1500-1530, 1700-1730, 1950-1980)

---

## Impact

**Before:**
- Outreach templates might contain em dashes, exclamation points, generic phrases
- No validation or quality control
- Templates could be unprofessional or poorly positioned

**After:**
- System prompt explicitly forbids common mistakes
- Automatic validation catches issues
- Automatic cleanup fixes formatting problems
- Logged warnings help monitor quality
- Templates are professional, specific, and well-positioned

---

## Testing Recommendations

1. **Test with Various Resumes:**
   - Entry-level candidate (limited experience)
   - Senior candidate (extensive experience with metrics)
   - Career switcher (transferable skills)

2. **Check for:**
   - No em dashes in any outreach template
   - No exclamation points
   - Specific company/role references from actual resume
   - Clear, direct asks
   - Professional tone throughout

3. **Monitor Logs:**
   - Watch for validation warnings
   - Review flagged templates
   - Adjust rules if needed

---

## Future Enhancements (Optional)

1. **Stricter Regeneration:**
   - If validation fails badly, automatically call Claude again with stricter prompt
   - Only return after passing validation

2. **Frontend Regeneration Button:**
   - Let users regenerate outreach templates if they're not satisfied
   - Track which templates get regenerated most (quality signal)

3. **A/B Testing:**
   - Test response rates for templates that pass validation vs. those that don't
   - Refine rules based on actual performance data

4. **User Customization:**
   - Allow users to set tone preferences (formal vs. conversational)
   - Maintain quality rules while adapting to user style

---

## Questions?

If you need clarification on any of these changes or want to adjust the validation rules, let me know.
