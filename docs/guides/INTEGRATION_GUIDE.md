# TRACKER.HTML EMPATHY MODIFICATIONS - INTEGRATION GUIDE

## Overview
This modification adds adaptive, empathy-driven messaging to the Pipeline Command Center based on the user's emotional state, timeline urgency, and confidence level captured during profile onboarding.

## Files
- `tracker_empathy_modifications.js` - Contains all new functions and the modified renderDailyPulse()

## Integration Steps

### Step 1: Locate the Script Section
In `tracker.html`, find the `<script>` tag that contains all the JavaScript (around line 2600+).

### Step 2: Add New Functions
Copy all functions from `tracker_empathy_modifications.js` EXCEPT the `renderDailyPulse()` function and paste them into tracker.html's script section. Recommended location: right after the `STATUSES` object definition (around line 2700).

The functions to add are:
1. `getUserProfile()`
2. `getPulseGreeting(profile, apps)`
3. `getAdaptivePriorityAction(profile, apps, upcomingInterviews, followUpsDue, activeApps)`
4. `getStalledAppsMessage(stalledApps, situation)` (Phase 2)
5. `getStrategicRecommendations(apps, profile)` (Phase 2)
6. `getInterviewPrepIntro(confidence)` (Phase 2)

### Step 3: Replace renderDailyPulse Function
Find the existing `renderDailyPulse()` function (around line 5206) and REPLACE it entirely with the new version from `tracker_empathy_modifications.js`.

The key differences:
- Loads user profile at the start
- Uses `getPulseGreeting()` for adaptive greeting
- Uses `getAdaptivePriorityAction()` for adaptive action messaging
- Falls back to time-based greeting if no profile exists

### Step 4: Test the Integration

#### Test 1: No Profile (Fallback)
1. Clear localStorage
2. Load tracker.html
3. Should see time-based greeting ("Good morning/afternoon/evening")

#### Test 2: Profile with Different States
1. Complete profile onboarding with different emotional states:
   - Zen + Exploring
   - Stressed + Active
   - Desperate + Urgent
   - Crushed + Clock Ticking
2. Add some tracked applications
3. Load tracker.html
4. Verify greeting adapts to emotional state

#### Test 3: Adaptive Priority Actions
1. Create scenarios:
   - No follow-ups, < 5 apps → Should suggest adding more
   - Follow-ups due → Should prioritize follow-up
   - Upcoming interviews → Should prioritize prep
2. Verify action button text and tone adapt to timeline/emotional state

## Expected Behavior Changes

### Daily Pulse Greeting
**Before:**
"Good morning! Here's your job search pulse:"

**After (Zen + Exploring):**
"You've got 3 active applications. No rush—let's keep the bar high."

**After (Desperate + Urgent):**
"Let's focus. You have 3 applications moving. Here's what needs attention today."

**After (Crushed):**
"I know this is brutal. You have 3 active applications. Let's make sure each one gets follow-up."

### Priority Action Messages
**Before:**
"Suggestion: Your pipeline has 3 active apps. Consider adding more to increase your odds."

**After (Clock Ticking):**
"Pipeline thin: Only 3 active apps. You need more options—broaden your search."

**After (Zen + Exploring):**
"Suggestion: Your pipeline has 3 active apps. Room to add higher-quality matches."

## Data Requirements

### Required Profile Structure
```javascript
{
  situation: {
    holding_up: "zen" | "stressed" | "desperate" | "crushed",
    timeline: "exploring" | "active" | "urgent" | "clock_ticking",
    confidence: "high" | "medium" | "low"
  },
  // ... other profile fields
}
```

This data is already captured in `profile.html` during onboarding and stored in `localStorage.userProfile`.

## Phase 2 Functions (Future Use)

The following functions are included for Phase 2 when you add Analytics mode:

1. **getStalledAppsMessage()** - For displaying stalled application alerts with adaptive tone
2. **getStrategicRecommendations()** - For showing pacing and quality recommendations
3. **getInterviewPrepIntro()** - For adjusting interview prep tone based on confidence

These can be called when building the Analytics toggle view or other dashboard features.

## Rollback Plan

If you need to rollback:
1. Keep a backup of the original `tracker.html`
2. The new functions don't break existing functionality—they only add features
3. If profile data is missing, system falls back to time-based greeting
4. Remove the new functions and restore original `renderDailyPulse()` to revert

## Testing Checklist

- [ ] No profile → Falls back to time-based greeting
- [ ] Zen + Exploring → Calm, patient tone
- [ ] Stressed + Active → Focused, supportive tone  
- [ ] Desperate + Urgent → Direct, action-oriented tone
- [ ] Crushed → Empathetic, reality-acknowledging tone
- [ ] Clock Ticking → Survival mode messaging
- [ ] Priority actions adapt to timeline urgency
- [ ] Button text changes based on emotional state
- [ ] No console errors
- [ ] All existing tracker functionality still works

## Notes

- All empathy logic is centralized in these functions
- Easy to adjust tone without touching multiple files
- Composable: each function takes profile/situation as input
- Maintainable: clear separation of concerns
- Testable: can validate tone changes across states

## Questions?

If you encounter issues:
1. Check browser console for errors
2. Verify userProfile exists in localStorage
3. Verify profile.situation structure matches expected format
4. Ensure all functions are added to the script section
5. Confirm renderDailyPulse() was fully replaced (not just modified)
