# Quick Testing Guide - Simplified Flow

## Setup
1. Replace your current `index.html` with the modified version
2. Keep your existing `backend.py` (no changes needed)
3. Open the page in a browser

## Critical Tests

### Test 1: Resume Upload Flow
1. Load the page
2. Click "Let's get started"
3. Click "Upload a file" 
4. Select a resume file
5. Click "Submit"

**Expected:**
- ✅ Goes directly to "Submit a job description" screen
- ✅ Does NOT show "Where are you in your job search?" questions
- ✅ Cursor is auto-focused in the JD textarea

### Test 2: Resume Paste Flow
1. Load the page
2. Click "Let's get started"
3. Click "Paste resume text"
4. Paste resume content
5. Click "Submit"

**Expected:**
- ✅ Goes directly to "Submit a job description" screen
- ✅ Does NOT show intake questions
- ✅ Cursor is auto-focused in the JD textarea

### Test 3: Marketing Sections Visible
1. Load the page
2. Scroll through the top sections

**Expected:**
- ✅ "About Henry" section is visible
- ✅ "How we work together" section with 4 steps is visible
- ✅ "What makes working with Henry different?" section is visible
- ✅ "Core capabilities" section with 6 cards is visible

### Test 4: JD Analysis and Document Generation
1. Complete resume upload
2. Enter company name, role title, and JD text
3. Click "Analyze this role"
4. Review fit analysis
5. Click "Generate my resume and cover letter"

**Expected:**
- ✅ Button text says "Generate my resume and cover letter" (not "Create my tailored application")
- ✅ Analysis runs normally
- ✅ Documents generate successfully
- ✅ "Here's what I changed" sections appear
- ✅ Download buttons work

## Known Behavior

### What Still Exists (But Hidden)
- `screen-intake` section is still in the HTML
- `startIntakeFlow()` function still exists
- All intake question data still exists
- Can be re-enabled easily if needed

### What Was Changed
- Upload handlers skip intake flow
- Button text updated to be more specific
- Auto-focus added to JD textarea

### What Was Preserved
- All marketing content
- All analysis logic
- All document generation
- All interview prep features
- All tracker functionality

## Quick Validation Checklist

### Page Load
- [ ] Marketing sections visible at top
- [ ] No intake screen auto-shows
- [ ] "Let's get started" button works

### Resume Input
- [ ] Upload → JD submission (skip intake)
- [ ] Paste → JD submission (skip intake)
- [ ] LinkedIn PDF → JD submission (skip intake)
- [ ] JD textarea auto-focused

### Main Workflow
- [ ] JD analysis works
- [ ] Fit scoring works
- [ ] "Generate my resume and cover letter" button visible
- [ ] Documents generate
- [ ] Changes summary appears
- [ ] Downloads work

### Edge Cases
- [ ] Can analyze multiple roles in sequence
- [ ] Tracker still saves applications
- [ ] Interview prep still populates
- [ ] Outreach messages still generate

## Rollback Plan
If something breaks:
1. Restore the original `index.html` from your backup
2. Check console for errors
3. Verify backend is running

## Next Steps for User Testing
Once validation passes:
1. Test with 5-10 real users
2. Gather feedback on:
   - Is the flow intuitive?
   - Do they miss having context about their job search?
   - Do they notice the button text change?
   - Does auto-focus feel natural?
3. Decide whether to keep simplified flow or add back intake
