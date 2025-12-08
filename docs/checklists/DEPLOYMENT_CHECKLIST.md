# Deployment Checklist - Simplified Flow v1.0

## Pre-Deployment

### Backup Current Version
- [ ] Backup current `index.html` to `index.html.v0.9.backup`
- [ ] Backup current `backend.py` (unchanged, but good practice)
- [ ] Document current git commit if using version control
- [ ] Take screenshots of current flow for reference

### Code Review
- [ ] Verify all 3 upload handlers skip intake
- [ ] Verify auto-focus code is present in all handlers
- [ ] Verify button text says "Generate my resume and cover letter"
- [ ] Verify no calls to `startIntakeFlow()` in upload handlers
- [ ] Verify marketing sections are intact
- [ ] Check for console errors in browser dev tools

### Environment Check
- [ ] Backend server is running
- [ ] API endpoints are accessible
- [ ] Document generation libraries loaded (docx.js, FileSaver.js)
- [ ] No CORS issues between frontend and backend

## Deployment Steps

### Local Testing First
1. [ ] Load modified `index.html` in browser
2. [ ] Complete full workflow: Upload → JD → Analysis → Documents
3. [ ] Test all three upload methods (file, paste, LinkedIn)
4. [ ] Verify downloads work
5. [ ] Check browser console for errors
6. [ ] Test on mobile viewport (responsive check)

### Deploy to Server
1. [ ] Replace production `index.html` with modified version
2. [ ] Clear browser cache
3. [ ] Test production URL
4. [ ] Verify static assets load correctly
5. [ ] Check backend connection works

### Post-Deployment Smoke Tests
- [ ] Load production URL
- [ ] Upload resume → verify goes to JD submission
- [ ] Paste JD → verify analysis runs
- [ ] Generate documents → verify downloads work
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile device

## Rollback Plan

### If Critical Issues Found
1. Stop: Document the issue immediately
2. Restore backup: `cp index.html.v0.9.backup index.html`
3. Clear cache: Force refresh (Cmd/Ctrl + Shift + R)
4. Verify old version works
5. Debug issue in local environment

### Common Issues and Fixes

**Issue:** Resume upload doesn't go to JD submission
- **Check:** Browser console for JavaScript errors
- **Fix:** Verify `showScreen('jd-submission')` exists in handler
- **Rollback:** Restore backup if can't fix immediately

**Issue:** JD textarea doesn't auto-focus
- **Impact:** Low (not critical, just UX polish)
- **Fix:** Check for `setTimeout(() => jdTextarea.focus(), 300)`
- **Workaround:** Users can click into field manually

**Issue:** Documents don't generate
- **Check:** Backend logs for errors
- **Check:** Network tab for failed API calls
- **Note:** This shouldn't be affected by frontend changes
- **Action:** Check if backend is running

**Issue:** Marketing sections missing
- **Check:** View page source to verify HTML
- **Check:** CSS not blocking display
- **Action:** Restore backup and investigate

## User Testing Plan

### Phase 1: Internal Testing (You)
- [ ] Test full workflow 3 times
- [ ] Try to break it (edge cases)
- [ ] Time the workflow (should be <2 min start to download)
- [ ] Note any UX friction points

### Phase 2: Friendly Users (2-3 people)
- [ ] Share link with 2-3 trusted users
- [ ] Ask them to think aloud while using
- [ ] Don't guide them - observe where they struggle
- [ ] Note questions they ask
- [ ] Gather feedback on:
  * Was it intuitive?
  * Did they miss having intake questions?
  * Was the flow too fast/jarring?
  * Do the outputs meet expectations?

### Phase 3: Real Users (5-10 people)
- [ ] Recruit 5-10 actual job seekers
- [ ] Let them use it without guidance
- [ ] Follow up with survey:
  * How easy was it to use? (1-5)
  * Did you get the outputs you expected? (Y/N)
  * Would you recommend this? (Y/N)
  * What would make it better? (open-ended)
- [ ] Track metrics:
  * Completion rate (upload → download)
  * Time from start to download
  * Drop-off points (where do they abandon?)

## Success Criteria

### Must Have
- ✅ Resume upload → JD submission works 100% of time
- ✅ Documents generate successfully
- ✅ No console errors
- ✅ Marketing sections visible
- ✅ Downloads work

### Should Have
- ✅ Auto-focus works on JD textarea
- ✅ Flow feels smooth and natural
- ✅ Users complete workflow without confusion
- ✅ Time to first download < 2 minutes
- ✅ Users find value in outputs

### Nice to Have
- ⚪ Mobile experience is good
- ⚪ Users understand new button text
- ⚪ Users don't ask for intake questions
- ⚪ Users share with others

## Monitoring After Launch

### First 24 Hours
- [ ] Check for error reports
- [ ] Monitor completion rates
- [ ] Watch for user feedback/questions
- [ ] Check server logs for issues

### First Week
- [ ] Gather qualitative feedback
- [ ] Track conversion funnel metrics
- [ ] Note common user questions
- [ ] Identify any UX friction

### Decision Point: 1 Week
Based on feedback, decide:
- ✅ Keep simplified flow as-is
- 🔄 Add intake back (optionally or required)
- 🔧 Iterate on current flow
- 📊 Need more data before deciding

## Documentation Updates

### Update README
- [ ] Document new simplified flow
- [ ] Update screenshots/GIFs if applicable
- [ ] Note that intake is temporarily disabled
- [ ] Explain how to re-enable if needed

### Update User-Facing Copy
- [ ] Ensure marketing sections set expectations
- [ ] Update any help text that references intake
- [ ] Check for mentions of "preferences" that no longer apply

## Communication Plan

### Internal Team
- Brief team on changes
- Share testing results
- Get alignment on rollout plan

### Users (if applicable)
- Announce simplified flow
- Explain faster time to value
- Invite feedback

## Final Checks Before Launch

- [ ] All tests pass
- [ ] Backup created
- [ ] Rollback plan documented
- [ ] Success criteria defined
- [ ] Monitoring plan in place
- [ ] Team briefed
- [ ] Go/no-go decision made

## Launch Decision

**Ready to launch if:**
- All smoke tests pass
- No critical bugs found
- Rollback plan is clear
- Monitoring is set up

**Don't launch yet if:**
- Critical bugs present
- Major UX issues discovered
- Backend not stable
- Rollback not tested

---

## Post-Launch Review (After 1 Week)

### Metrics to Review
- Completion rate: __%
- Avg time to download: __ minutes
- User satisfaction (survey): __/5
- Feature requests mentioning intake: __

### Decision
- [ ] Keep simplified flow
- [ ] Add intake back
- [ ] Iterate on simplified flow
- [ ] Need more data

### Action Items
1. __________
2. __________
3. __________
