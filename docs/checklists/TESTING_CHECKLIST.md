# TESTING CHECKLIST
## Verify Phase 1 Features Before Beta Testing

Use this checklist to confirm everything works before giving access to beta testers.

---

## **PRE-FLIGHT CHECKS**

### **✅ Backend Implementation**

- [ ] Updated Claude prompt in `/api/jd/analyze` endpoint
- [ ] Added validation function `validate_analysis_response()`
- [ ] Endpoint returns all new fields:
  - [ ] `positioning_strategy` (with emphasize, de_emphasize, framing)
  - [ ] `action_plan` (with today, tomorrow, this_week)
  - [ ] `salary_strategy` (with all 5 sub-fields)
  - [ ] `hiring_intel` (with hiring_manager and recruiter)
- [ ] Helper functions extract company name, role, and candidate name
- [ ] Error handling catches validation failures gracefully

### **✅ Frontend Deployment**

- [ ] Replaced old `package.html` with new version
- [ ] All CSS styles intact (no broken layout)
- [ ] JavaScript loads without errors (check browser console)
- [ ] Element IDs match between HTML and JS

---

## **FUNCTIONAL TESTING**

### **Test 1: Full User Flow**

**Steps:**
1. Go to profile.html
2. Upload a resume
3. Navigate to analyze.html
4. Paste a job description
5. Click "Analyze Role"
6. See fit analysis on results.html
7. Click "Continue to Package" (or similar CTA)
8. Land on package.html

**Expected Results:**
- [ ] Page loads without errors
- [ ] All 4 new sections appear:
  - [ ] Strategic Positioning (with emphasize/de-emphasize lists)
  - [ ] Action Plan (with TODAY/TOMORROW/THIS WEEK tasks)
  - [ ] Salary Strategy (with ranges and talking points)
  - [ ] Hiring Intel (in Outreach tab)
- [ ] Existing sections still work:
  - [ ] Resume preview
  - [ ] Cover letter preview
  - [ ] Outreach templates
  - [ ] Download button

---

### **Test 2: Strategic Positioning Section**

**Location:** Top of package.html page

**Check:**
- [ ] Candidate's first name appears ("Henry, this positions you as...")
- [ ] Strategic framing text displays
- [ ] "Emphasize" column has 3-5 bullets
- [ ] "De-emphasize" column has 2-3 bullets
- [ ] Bullets use specific examples (not generic placeholders)
- [ ] Green/yellow color coding works

**Sample Data to Verify:**
```json
"positioning_strategy": {
  "emphasize": [
    "Your fintech experience at Uber and Venmo",
    "Track record building teams from scratch 3x",
    "Hands-on execution combined with strategy"
  ],
  "de_emphasize": [
    "National Grid utility context",
    "Managing 25-person teams at Spotify"
  ],
  "framing": "This positions you as someone who can step into Series B..."
}
```

---

### **Test 3: Action Plan Section**

**Location:** Below Strategic Positioning

**Check:**
- [ ] "TODAY" section has 3-4 tasks
- [ ] "TOMORROW" section has 2-3 tasks
- [ ] "THIS WEEK" section has 3-4 tasks
- [ ] Tasks reference actual company name (not placeholder)
- [ ] Checkboxes appear next to each task
- [ ] Tasks are specific (not vague like "apply for job")

**Sample Data to Verify:**
```json
"action_plan": {
  "today": [
    "Apply via Coast ATS before end of day",
    "Research hiring manager on LinkedIn",
    "Check Glassdoor for company reviews"
  ],
  "tomorrow": [
    "Send hiring manager outreach using template",
    "Reach out to network connections at Coast"
  ],
  "this_week": [
    "Follow up if no response by Day 5",
    "Review phone screen prep daily",
    "Monitor LinkedIn for recruiter outreach"
  ]
}
```

---

### **Test 4: Salary Strategy Section**

**Location:** Below Action Plan

**Check:**
- [ ] "Their Range" displays correctly
- [ ] "Your Target" displays in accent color
- [ ] "Market Data" displays
- [ ] "Negotiation Approach" paragraph displays
- [ ] "Key Talking Points" has 3-4 bullets
- [ ] All fields populated (no "undefined" or "null")

**Sample Data to Verify:**
```json
"salary_strategy": {
  "their_range": "$180K-$220K (posted)",
  "your_target": "$190K-$220K base",
  "market_data": "Glassdoor shows $195K median for this role in NYC",
  "approach": "Don't bring up salary first. If they ask early...",
  "talking_points": [
    "You've managed 25-person teams - justifies higher end",
    "Fintech background is directly relevant",
    "Taking hands-on role despite strategic experience"
  ]
}
```

---

### **Test 5: Hiring Intel Section**

**Location:** Inside "Outreach" tab

**Check:**
- [ ] Click "Outreach" tab at top of preview area
- [ ] Hiring manager section appears:
  - [ ] Title displays (e.g., "VP of Talent Acquisition")
  - [ ] Search instructions display
  - [ ] LinkedIn query is specific to company
- [ ] Recruiter section appears:
  - [ ] Title displays (e.g., "Technical Recruiter")
  - [ ] Search instructions display
  - [ ] LinkedIn query is specific to company
- [ ] Pro tip box displays at bottom
- [ ] Old "Find the Right People" section still exists below

**Sample Data to Verify:**
```json
"hiring_intel": {
  "hiring_manager": {
    "likely_title": "VP of Talent Acquisition",
    "search_instructions": "LinkedIn search: \"Coast talent acquisition\"",
    "filters": "Filter by: Current employees, Director+ level"
  },
  "recruiter": {
    "likely_title": "Technical Recruiter",
    "search_instructions": "LinkedIn search: \"Coast technical recruiter\"",
    "filters": "Filter by: Current employees, recent activity"
  }
}
```

---

### **Test 6: Edge Cases**

**Test missing data gracefully:**

- [ ] Backend returns empty `emphasize` array
  - **Expected:** Section hides or shows fallback message
  
- [ ] Backend returns null for `action_plan`
  - **Expected:** Section appears empty (no errors)
  
- [ ] Backend returns "Not disclosed" for `their_range`
  - **Expected:** Displays as-is (not an error state)
  
- [ ] Company name is very long (50+ characters)
  - **Expected:** Text doesn't break layout
  
- [ ] Candidate has no first name in resume
  - **Expected:** Falls back to "You" in positioning section

---

### **Test 7: Browser Compatibility**

Test in all major browsers:

**Chrome:**
- [ ] All sections display correctly
- [ ] No console errors
- [ ] CSS renders properly

**Safari:**
- [ ] All sections display correctly
- [ ] No console errors
- [ ] CSS renders properly

**Firefox:**
- [ ] All sections display correctly
- [ ] No console errors
- [ ] CSS renders properly

**Mobile (iOS/Android):**
- [ ] Sections stack vertically
- [ ] Text is readable
- [ ] Buttons work

---

### **Test 8: Download Functionality**

**Still works after changes:**

- [ ] Click "Download All" button
- [ ] Resume downloads as .docx
- [ ] Cover letter downloads as .docx
- [ ] Files open correctly in Word/Google Docs
- [ ] No corruption or formatting issues

---

### **Test 9: Tracker Integration**

**Still works after changes:**

- [ ] Click "Track This Application" button
- [ ] Application saves to tracker
- [ ] Navigate to tracker.html
- [ ] Application appears in list
- [ ] All data intact

---

## **PERFORMANCE CHECKS**

### **Speed:**
- [ ] Page loads in < 2 seconds
- [ ] API response time < 5 seconds
- [ ] No lag when scrolling
- [ ] Tab switching is instant

### **API Calls:**
- [ ] Only one call to `/api/jd/analyze`
- [ ] No redundant requests
- [ ] Error responses handled gracefully

---

## **BETA TESTER FEEDBACK QUESTIONS**

Ask your testers:

### **Information Density:**
- "Is this too much information at once?"
- "Which sections did you read completely?"
- "Which sections did you skip?"
- "Would you prefer this split across multiple pages?"

### **Usefulness:**
- "Which section was most valuable?"
- "What section could be removed?"
- "Did the action plan feel actionable?"
- "Was the salary guidance helpful?"
- "Did you actually use the hiring intel?"

### **Accuracy:**
- "Did the positioning strategy feel accurate?"
- "Were the action plan tasks realistic?"
- "Was the salary range on target?"
- "Did the hiring intel match reality?"

### **Trust:**
- "Did anything feel fabricated or generic?"
- "Would you trust this guidance for a real application?"
- "What would make you trust it more?"

---

## **GO/NO-GO DECISION**

### **✅ READY FOR BETA if:**
- All functional tests pass
- No console errors
- Sections display correctly
- Data is accurate and specific
- Download still works
- Performance is good

### **🛑 NOT READY if:**
- Sections don't appear
- Data is generic/fabricated
- Console has errors
- Performance is slow
- Download broken
- Mobile layout broken

---

## **ROLLBACK PLAN**

If beta testing reveals major issues:

1. **Quick fix:** Hide problematic sections with CSS
2. **Moderate fix:** Revert to old package.html
3. **Long-term fix:** Address feedback and re-deploy

**Keep old package.html backed up just in case.**

---

## **POST-TESTING ACTION ITEMS**

After beta testing, based on feedback:

**If testers love it:**
- [ ] Keep as-is
- [ ] Plan Phase 1.5 (automation)
- [ ] Start LinkedIn CSV upload feature

**If testers say "too much":**
- [ ] Add "Show More" toggles for sections
- [ ] Split into multiple pages (strategy.html + outreach.html)
- [ ] Make sections opt-in with checkboxes

**If testers say "not enough":**
- [ ] Add company research protocol
- [ ] Add follow-up decision tree
- [ ] Add interview debrief feature

---

## **FINAL CHECK BEFORE BETA**

- [ ] All tests passed
- [ ] No critical bugs
- [ ] Backup of old version saved
- [ ] Beta testers have instructions
- [ ] Feedback form prepared
- [ ] You're confident in the build

**If all boxes checked:** SHIP IT! 🚀

---

## **DEBUGGING TIPS**

**Sections not appearing:**
```javascript
// Open browser console, check:
console.log(analysisData);
// Look for: positioning_strategy, action_plan, salary_strategy, hiring_intel
```

**Backend returning errors:**
```python
# Check server logs for:
print(f"Analysis data: {json.dumps(analysis_data, indent=2)}")
# Verify all required fields present
```

**CSS looks broken:**
```
Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

**Data looks generic:**
```
Review Claude prompt - ensure it says:
"Use specific examples from candidate's resume"
"Reference actual company name in tasks"
```

Good luck! 🎯
