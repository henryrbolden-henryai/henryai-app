# CLAUDE CODE IMPLEMENTATION INSTRUCTIONS
# Strategic Options Section - Dashboard Enhancement

## OBJECTIVE
Add a conditional "Strategic Options" section to dashboard.html that provides contextual guidance based on the candidate's timeline and emotional state. The section adapts its messaging and recommendations from urgent cash flow options (for desperate candidates) to leverage-building opportunities (for candidates with runway).

## CONTEXT
The candidate's situation is captured during onboarding in profile-edit.html through two key fields:
- `situation.timeline`: urgent, soon, actively_looking, no_rush
- `situation.holdingUp`: doing_well, stressed_but_managing, struggling, rather_not_say

This data determines which version of Strategic Options to display.

## FILES TO MODIFY

### 1. dashboard.html

**Location to insert:** Between the Reality Check section (ends around line 240) and the Pipeline Overview section (starts around line 245).

**Changes required:**

#### A. Add HTML Section
Insert the Strategic Options HTML block from strategic-options-implementation.html:
- Copy lines 9-32 (the HTML section)
- Paste after the Reality Check closing `</div>` tag
- Before the Pipeline Overview opening tag

#### B. Add CSS Styles
Add to the existing `<style>` block (starts around line 10):
- Copy lines 37-157 (all CSS from strategic-options-implementation.html)
- Paste at the end of the existing `<style>` block, before the closing `</style>`
- Ensure no duplicate class names exist

#### C. Add JavaScript Implementation
Add to the main `<script>` block (starts around line 800):
- Copy lines 162-551 (all JavaScript from strategic-options-implementation.html)
- Paste before the "INITIALIZATION" comment section (around line 1487)
- This includes:
  - STRATEGIC_CONTENT configuration object
  - calculateUrgency() function
  - renderStrategicOptions() function
  - updateStrategicContent() function
  - openStrategicGuidance() function
  - dismissStrategicOptions() function
  - showContractGuidanceModal() function
  - closeContractGuidanceModal() function
  - trackEvent() function (optional analytics)

#### D. Integrate with renderDashboard()
Find the `renderDashboard()` function (around line 900).

**Add this call** after the reality check rendering logic:
```javascript
// Render strategic options section
renderStrategicOptions();
```

**Exact placement:**
- After any existing reality check rendering (if present)
- Before pipeline overview rendering
- Typically after line 950 in the current structure

### 2. Verify Profile Data Structure

Ensure the `getCandidateProfile()` function returns an object with this structure:
```javascript
{
  situation: {
    timeline: 'urgent' | 'soon' | 'actively_looking' | 'no_rush',
    holdingUp: 'doing_well' | 'stressed_but_managing' | 'struggling' | 'rather_not_say'
  },
  // ... other profile fields
}
```

If the structure differs, update the following lines in renderStrategicOptions():
```javascript
const timeline = profile.situation.timeline || 'actively_looking';
const holdingUp = profile.situation.holdingUp || 'doing_well';
```

## DECISION LOGIC REFERENCE

The section visibility and content are determined by this matrix:

| Timeline | Holding Up | Display? | Urgency Level | Content Focus |
|----------|-----------|----------|---------------|---------------|
| urgent | any | ✅ Yes | desperate | Contract work (survival mode) |
| soon | any | ✅ Yes | stressed | Contract work (tactical bridge) |
| actively_looking | struggling | ✅ Yes | desperate | Contract work (survival mode) |
| actively_looking | stressed_but_managing | ✅ Yes | stressed | Contract work (tactical bridge) |
| actively_looking | doing_well | ✅ Yes | standard | Advisory/portfolio building |
| actively_looking | rather_not_say | ✅ Yes | standard | Advisory/portfolio building |
| no_rush | doing_well | ❌ No | none | Section hidden |
| no_rush | struggling | ✅ Yes | desperate | Contract work (survival mode) |

## TESTING CHECKLIST

After implementation, test these scenarios:

### Test 1: Desperate Candidate
- Set `timeline: 'urgent'` in localStorage profile
- Reload dashboard
- Verify section shows "⚡ Urgent: Cash Flow Options"
- Verify red/urgent styling is applied
- Verify 4 benefits focused on speed and survival
- Click "Show Contract Options" → verify modal opens
- Click "Not Right Now" → verify section disappears
- Reload page → verify section stays dismissed

### Test 2: Stressed Candidate
- Set `timeline: 'soon'` in localStorage profile
- Reload dashboard
- Verify section shows "🎯 Tactical Options to Consider"
- Verify yellow/warning styling is applied
- Verify 4 benefits focused on tactical bridge
- Click "Explore Options" → verify modal opens
- Click "Dismiss" → verify section disappears

### Test 3: Standard Candidate
- Set `timeline: 'actively_looking'` and `holdingUp: 'doing_well'`
- Reload dashboard
- Verify section shows "💡 Other Paths Worth Exploring"
- Verify cyan/standard styling is applied
- Verify 4 benefits focused on leverage building
- Click "Learn More" → verify modal opens

### Test 4: Zen Candidate (Hidden)
- Set `timeline: 'no_rush'` and `holdingUp: 'doing_well'`
- Reload dashboard
- Verify section does NOT appear

### Test 5: Edge Cases
- Set `timeline: ''` (empty) → should default to 'standard' urgency
- Set `holdingUp: null` → should default to 'doing_well'
- Set profile to `null` → section should hide gracefully

### Test 6: Dismissal Persistence
- Show section (any urgency level)
- Click dismiss button
- Reload page
- Verify section stays dismissed
- Clear `localStorage.strategicOptionsDismissed`
- Reload page
- Verify section re-appears

## VALIDATION POINTS

Before marking complete, verify:

1. ✅ No console errors on page load
2. ✅ Section appears/hides based on profile data
3. ✅ All three content variations render correctly
4. ✅ Styling adapts to urgency level (desperate=red, stressed=yellow, standard=cyan)
5. ✅ Modal opens when clicking primary CTA
6. ✅ Modal contains 4 contract platform links
7. ✅ Modal closes when clicking "Close" or overlay
8. ✅ Dismissal persists across page reloads
9. ✅ Responsive design works on mobile (buttons stack vertically)
10. ✅ No conflicts with existing dashboard sections

## COMMON ISSUES & SOLUTIONS

### Issue: Section doesn't appear at all
**Solution:** Check that:
- `renderStrategicOptions()` is called from `renderDashboard()`
- `getCandidateProfile()` returns valid data
- Profile has `situation.timeline` and `situation.holdingUp` fields
- `strategicOptionsDismissed` is not set in localStorage

### Issue: Wrong content variation shows
**Solution:** 
- Verify `calculateUrgency()` logic matches decision matrix
- Check profile data values match expected strings exactly
- Console.log the urgency level to debug

### Issue: Styling looks broken
**Solution:**
- Ensure all CSS classes are properly namespaced (no conflicts)
- Verify CSS variables (--color-accent, --color-text, etc.) are defined
- Check browser console for CSS parsing errors

### Issue: Modal doesn't open
**Solution:**
- Verify `showContractGuidanceModal()` is defined
- Check that modal HTML is being appended to document.body
- Verify no JavaScript errors in console

## FUTURE ENHANCEMENTS (Phase 2)

The following features are planned but NOT part of this initial implementation:

1. **Dedicated Guidance Page** - Replace modal with full page at `/contract-guidance.html`
2. **Contract Resume Generator** - Generate contract-optimized resume
3. **Rate Calculator** - FTE salary → contract rate converter with 1099 tax implications
4. **Contract-to-FTE Strategy** - Positioning scripts for returning to FTE search
5. **Analytics Integration** - Track engagement with strategic options
6. **A/B Testing** - Test different messaging variations
7. **Personalized Resources** - Filter contract platforms by industry/role

## ROLLBACK PLAN

If issues arise post-deployment:

1. **Quick Fix:** Set `strategicOptionsDismissed = 'true'` for all users via script
2. **CSS Fix:** Add `#strategicOptions { display: none !important; }` temporarily
3. **Full Rollback:** Remove the section rendering call from `renderDashboard()`

## DEPLOYMENT NOTES

- This is a pure frontend feature (no backend changes required)
- No database migrations needed
- Safe to deploy independently
- Can be feature-flagged if needed by wrapping in `if (FEATURE_FLAGS.strategicOptions)`

## QUESTIONS TO RESOLVE BEFORE IMPLEMENTATION

1. Should we add analytics tracking for strategic options engagement?
2. Do we want to A/B test different messaging variations?
3. Should dismissal be permanent or reset after X days?
4. Do we want to add a "Re-assess my situation" link to un-dismiss?
5. Should we show a different variant if the candidate's situation changes?

## CONTACT

For questions during implementation:
- Review strategic-options-implementation.html for full reference code
- Check dashboard.html lines 800-1500 for existing patterns
- Refer to profile-edit.html lines 875-916 for profile structure
