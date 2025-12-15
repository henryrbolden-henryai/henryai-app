# CLAUDE CODE IMPLEMENTATION INSTRUCTIONS
## Tracker.html Empathy Modifications

## OBJECTIVE
Integrate adaptive, empathy-driven messaging into tracker.html that adjusts tone and content based on the user's emotional state, timeline urgency, and confidence level captured during profile onboarding.

---

## FILES PROVIDED
1. `tracker_empathy_modifications.js` - All new functions and modified renderDailyPulse()
2. `INTEGRATION_GUIDE.md` - Detailed integration steps and testing
3. `TONE_MATRIX.md` - Visual reference for tone variations

---

## IMPLEMENTATION STEPS

### STEP 1: Backup Current File
Before making any changes, create a backup of the current tracker.html file.

### STEP 2: Add New Helper Functions

**Location:** Inside the `<script>` tag in tracker.html, after the STATUSES object definition (approximately line 2700).

**Functions to add:** (Copy from tracker_empathy_modifications.js)
```javascript
// Add these functions in this order:
1. getUserProfile()
2. getPulseGreeting(profile, apps)
3. getAdaptivePriorityAction(profile, apps, upcomingInterviews, followUpsDue, activeApps)
4. getStalledAppsMessage(stalledApps, situation)
5. getStrategicRecommendations(apps, profile)
6. getInterviewPrepIntro(confidence)
```

**Important:**
- Add the full comment block at the top that explains the empathy system
- Include all helper functions EXCEPT `renderDailyPulse()` (that gets replaced separately)
- Preserve all existing code—these are additions, not replacements

### STEP 3: Replace renderDailyPulse Function

**Location:** Find the existing `renderDailyPulse()` function (approximately line 5206).

**Action:** 
- Delete the ENTIRE existing `renderDailyPulse()` function (from `function renderDailyPulse(apps) {` to the closing `}`)
- Replace it with the new version from tracker_empathy_modifications.js

**Key changes in new version:**
- Loads user profile at start: `const profile = getUserProfile();`
- Uses `getPulseGreeting()` for adaptive greeting instead of time-based
- Uses `getAdaptivePriorityAction()` for adaptive action messages
- Falls back to time-based greeting if no profile exists

### STEP 4: Verify Integration

**Check these points:**
1. All 6 new functions are added to the script section
2. The renderDailyPulse() function is completely replaced (not modified)
3. No syntax errors (check for missing brackets, commas)
4. No duplicate function definitions
5. All existing code remains intact

---

## TESTING REQUIREMENTS

### Test 1: No Profile (Fallback Behavior)
**Setup:**
- Clear localStorage in browser console: `localStorage.clear()`
- Load tracker.html

**Expected:**
- Daily Pulse shows time-based greeting: "Good morning/afternoon/evening! Here's your job search pulse:"
- No console errors
- All existing functionality works

### Test 2: Profile with Zen State
**Setup:**
- Complete profile.html onboarding with:
  - `holding_up: "zen"`
  - `timeline: "exploring"`
- Add 3 tracked applications
- Load tracker.html

**Expected:**
- Greeting: "You've got 3 active applications. No rush—let's keep the bar high."
- Action message (if < 5 apps): "Suggestion: Your pipeline has 3 active apps. Room to add higher-quality matches."
- Button text: "Analyze New Role"

### Test 3: Profile with Stressed State
**Setup:**
- Update profile in localStorage:
  - `holding_up: "stressed"`
  - `timeline: "active"`
- Load tracker.html

**Expected:**
- Greeting: "You've got 3 applications moving. Here's what needs attention so nothing slips."
- More focused, supportive tone

### Test 4: Profile with Desperate State
**Setup:**
- Update profile:
  - `holding_up: "desperate"`
  - `timeline: "urgent"`
- Load tracker.html

**Expected:**
- Greeting: "Let's focus. You have 3 applications moving. Here's what needs attention today."
- Action message (if < 5 apps): "Pipeline thin: Only 3 active apps. You need more options—broaden your search."
- Button text: "Find More Roles"

### Test 5: Profile with Crushed State
**Setup:**
- Update profile:
  - `holding_up: "crushed"`
  - `timeline: "clock_ticking"`
- Load tracker.html

**Expected:**
- Greeting: "I know this is brutal. You have 3 active applications. Let's make sure each one gets follow-up."
- Empathetic, reality-acknowledging tone
- Direct action guidance

### Test 6: Priority Actions Adapt
**Setup:**
- Create different scenarios:
  - Scenario A: 0 follow-ups, 3 apps → Should suggest adding more
  - Scenario B: 2 follow-ups due → Should prioritize follow-up
  - Scenario C: 1 upcoming interview → Should prioritize prep

**Expected:**
- Action message adapts to highest priority item
- Button text and tone adapt to emotional state
- Follow-up messages show days since applying

---

## PROFILE DATA STRUCTURE

The system expects this structure in `localStorage.userProfile`:

```javascript
{
  situation: {
    holding_up: "zen" | "stressed" | "desperate" | "crushed",
    timeline: "exploring" | "active" | "urgent" | "clock_ticking",
    confidence: "high" | "medium" | "low"
  },
  // ... other profile fields from onboarding
}
```

This data is already captured by profile.html during onboarding.

---

## VALIDATION CHECKLIST

Before marking complete, verify:

- [ ] All 6 helper functions added correctly
- [ ] renderDailyPulse() completely replaced (not modified)
- [ ] No syntax errors in browser console
- [ ] Test 1 passes (no profile fallback)
- [ ] Test 2 passes (zen state)
- [ ] Test 3 passes (stressed state)
- [ ] Test 4 passes (desperate state)
- [ ] Test 5 passes (crushed state)
- [ ] Test 6 passes (priority actions adapt)
- [ ] No existing functionality broken
- [ ] Daily Pulse banner displays correctly
- [ ] All buttons clickable and functional

---

## TROUBLESHOOTING

### Issue: Greeting doesn't change with profile
**Solution:** 
- Check that getUserProfile() is returning data: `console.log(getUserProfile())`
- Verify profile.situation exists in localStorage
- Confirm renderDailyPulse() is calling getPulseGreeting()

### Issue: Console errors about undefined functions
**Solution:**
- Verify all 6 helper functions were added
- Check function names match exactly (case-sensitive)
- Ensure functions are added BEFORE renderDailyPulse() uses them

### Issue: Fallback not working (no profile shows error)
**Solution:**
- Confirm the `if (profile && profile.situation)` check exists
- Verify the else block with time-based greeting is present
- Check getUserProfile() returns null (not undefined) when no profile

### Issue: Priority actions don't adapt
**Solution:**
- Verify getAdaptivePriorityAction() is being called with correct parameters
- Check that profile is passed as first parameter
- Confirm all 5 parameters are provided: (profile, apps, upcomingInterviews, followUpsDue, activeApps)

---

## ROLLBACK PROCEDURE

If integration causes issues:

1. Restore the backup tracker.html file
2. The new functions don't modify existing data structures
3. No database changes are made
4. Simply reverting the file restores original behavior

---

## PHASE 2 NOTES

Three functions are included but not yet used:
- `getStalledAppsMessage()` - For Analytics mode stalled apps alert
- `getStrategicRecommendations()` - For Analytics mode recommendations
- `getInterviewPrepIntro()` - For interview prep tone adjustment

These can be called when building future Analytics toggle view. They don't affect current functionality.

---

## SUCCESS CRITERIA

Integration is successful when:
1. All tests pass without errors
2. Greeting adapts to emotional state when profile exists
3. Greeting falls back to time-based when no profile exists
4. Priority actions adapt tone based on timeline urgency
5. Button text changes appropriately (e.g., "Find More Roles" vs "Analyze New Role")
6. No existing tracker functionality is broken
7. User experience feels more empathetic and context-aware

---

## ESTIMATED COMPLEXITY
- Time: 15-30 minutes
- Risk: Low (graceful fallback, no breaking changes)
- Files modified: 1 (tracker.html)
- Lines added: ~350
- Lines modified: ~90 (renderDailyPulse function)

---

## QUESTIONS OR ISSUES?

Refer to:
- INTEGRATION_GUIDE.md for detailed step-by-step
- TONE_MATRIX.md for expected tone variations by state
- tracker_empathy_modifications.js for complete code

If you encounter any issues during implementation, check:
1. Browser console for JavaScript errors
2. localStorage.userProfile structure matches expected format
3. All functions copied correctly with no truncation
4. renderDailyPulse was fully replaced, not just modified
