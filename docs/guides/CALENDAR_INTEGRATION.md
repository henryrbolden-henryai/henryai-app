# Calendar Integration - Application Tracker

## Feature Overview

Added calendar integration to help candidates actually follow through on next steps instead of just reading them and forgetting. Users can now add reminders directly to their calendar with one click.

---

## What Was Added

### 1. **"Add Reminder" Button**
- Location: Next to "What to Do Next" heading in each application card
- Design: Blue calendar icon button (📅 Add Reminder)
- Hover effect: Lifts slightly on hover for tactile feedback

### 2. **Smart Reminder Timing**
Automatically calculates when to set the reminder based on application status:

| Status | Reminder Time | Logic |
|--------|--------------|-------|
| To Apply | Tomorrow at 9 AM | Apply within 24-48 hours |
| Applied | 5 days later at 9 AM | Follow up in 5-7 days |
| Phone Screen | Tomorrow at 2 PM | Send thank you within 24 hours |
| Onsite | Tomorrow at 2 PM | Send thank you within 24 hours |
| Other | Tomorrow at 9 AM | Default reminder |

### 3. **Calendar Options Modal**
When user clicks "Add Reminder", they see:
- **Google Calendar** - Opens Google Calendar in new tab with pre-filled event
- **Apple/Outlook (.ics)** - Downloads .ics file that works with Apple Calendar, Outlook, etc.

### 4. **Pre-Filled Event Details**

**Title:**
```
Follow up: [Company] - [Role]
```

**Description:**
```
[Context from "What to Do Next"]

→ [Specific action]

Fit Score: [X]%
Salary: [Range if available]
```

**Time:**
- 30-minute duration
- 30-minute advance reminder

---

## User Flow

1. **User sees next step guidance** in application card
2. **Clicks "📅 Add Reminder"** button
3. **Modal appears** with two calendar options
4. **User selects their calendar:**
   - **Google Calendar:** Opens in new tab with event pre-filled, user clicks "Save"
   - **Apple/Outlook:** Downloads .ics file, user double-clicks to import
5. **Reminder appears in their calendar** at the smart-scheduled time

---

## Technical Implementation

### Files Modified
- `tracker.html` (only file changed)

### Key Functions Added

1. **`addToCalendar(appId)`**
   - Finds application by ID
   - Determines optimal reminder time based on status
   - Shows calendar options modal

2. **`formatDateForCalendar(date)`**
   - Converts JavaScript Date to calendar format (YYYYMMDDTHHMMSSZ)

3. **`showCalendarOptions(...)`**
   - Creates and displays modal with calendar choices
   - Passes event details to selected calendar function

4. **`addToGoogleCalendar(...)`**
   - Builds Google Calendar URL with query parameters
   - Opens in new tab

5. **`downloadICS(...)`**
   - Generates RFC 5545 compliant .ics file
   - Includes event details and 30-minute reminder
   - Triggers browser download

6. **`closeCalendarModal()`**
   - Removes modal from DOM with fade animation

---

## CSS Added

### Calendar Button
- Blue accent color matching app theme
- Hover: Lifts with transform
- Fits inline with "What to Do Next" heading

### Calendar Modal
- Full-screen overlay (semi-transparent black)
- Centered content card
- Two large option buttons
- Cancel button at bottom
- Smooth fade-in animation

---

## .ics File Format

The downloaded calendar file includes:
- Event title and description
- Start and end times (30-minute duration)
- 30-minute advance reminder (VALARM)
- Proper escaping of newlines in description
- Unique UID for event tracking
- Works with Apple Calendar, Outlook, and most calendar apps

---

## Why This Matters

**Problem:** Candidates read the "What to Do Next" guidance but forget to act on it. They don't set reminders, and opportunities slip through the cracks.

**Solution:** One-click calendar integration removes friction. The reminder appears at the optimal time with all context needed to take action.

**Impact:**
- Higher follow-through rate on applications
- Better timing (reminds at strategic moments, not random times)
- Context preservation (description includes fit score, salary, specific action)
- Works with candidate's existing workflow (their calendar app)

---

## Future Enhancements (Optional)

1. **Recurring Reminders**
   - For ongoing job searches, set weekly "apply to 3 jobs" reminders

2. **Interview Prep Reminders**
   - Auto-schedule prep time before confirmed interviews

3. **Custom Timing**
   - Let users adjust when the reminder fires

4. **Calendar Sync**
   - Two-way sync with calendar to auto-update status when event is marked complete

5. **Multiple Reminders**
   - Initial reminder + follow-up reminder if not completed

---

## Testing Checklist

- [ ] Click "Add Reminder" on application with status "To Apply"
- [ ] Verify modal appears with two options
- [ ] Select Google Calendar, verify event opens in new tab
- [ ] Check event has correct title, time, description
- [ ] Save event in Google Calendar, verify it appears
- [ ] Click "Add Reminder" again
- [ ] Select "Apple/Outlook (.ics)"
- [ ] Verify .ics file downloads
- [ ] Double-click .ics file, verify it opens in default calendar app
- [ ] Import event, verify details are correct
- [ ] Verify 30-minute reminder is set
- [ ] Test with different application statuses (Applied, Phone Screen, etc.)
- [ ] Verify reminder times adjust based on status
- [ ] Click "Cancel" in modal, verify it closes smoothly

---

## Browser Compatibility

- **Google Calendar option:** Works in all modern browsers
- **.ics download:** Works in all modern browsers (Chrome, Safari, Firefox, Edge)
- **Modal:** CSS animations work in all modern browsers

---

## Notes

- Calendar reminders are set locally (not stored in HenryAI)
- Users can edit/delete reminders in their calendar app
- .ics files work offline once downloaded
- No server-side storage or API calls required (pure client-side)
