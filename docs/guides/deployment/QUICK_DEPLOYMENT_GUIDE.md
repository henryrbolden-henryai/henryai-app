# QUICK DEPLOYMENT GUIDE
## Get Phase 1 Live in 15 Minutes

---

## **STEP-BY-STEP DEPLOYMENT**

### **1. BACKUP CURRENT FILES** (2 minutes)

```bash
# In your project directory
cp backend.py backend.py.backup.$(date +%Y%m%d)
cp frontend/package.html frontend/package.html.backup.$(date +%Y%m%d)
```

---

### **2. DEPLOY UPDATED BACKEND** (3 minutes)

```bash
# Replace backend.py
cp /path/to/outputs/backend.py backend.py

# Restart your server
# Option A: If using uvicorn directly
pkill -f "uvicorn"
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &

# Option B: If using docker
docker-compose restart

# Option C: If using systemd
sudo systemctl restart henryai
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### **3. DEPLOY UPDATED FRONTEND** (1 minute)

```bash
# Replace package.html
cp /path/to/outputs/package.html frontend/package.html

# Clear browser cache if testing locally
# Chrome: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

---

### **4. SMOKE TEST** (5 minutes)

#### **Test 1: Backend Returns New Fields**

```bash
curl -X POST http://localhost:8000/api/jd/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "role_title": "Director of TA",
    "job_description": "We are hiring a Director of Talent Acquisition...",
    "resume": {
      "full_name": "Test Candidate",
      "experience": [{"company": "Previous Co", "title": "Recruiter"}]
    }
  }' | jq '.positioning_strategy'
```

**Expected:** JSON object with emphasize, de_emphasize, framing

**If error:** Check server logs: `tail -f logs/backend.log`

#### **Test 2: Frontend Displays New Sections**

1. Navigate to `http://localhost:3000` (or your frontend URL)
2. Upload a resume
3. Paste a job description
4. Click "Analyze Role"
5. Navigate to package page
6. **Verify you see:**
   - Strategic Positioning section (with emphasize/de-emphasize)
   - Action Plan section (TODAY/TOMORROW/THIS WEEK)
   - Salary Strategy section (ranges, approach, talking points)
   - Hiring Intel in Outreach tab

**If sections missing:**
- Open browser console (F12)
- Check for JavaScript errors
- Verify API response contains new fields

---

### **5. MONITOR LOGS** (4 minutes)

Watch for validation warnings:

```bash
tail -f logs/backend.log | grep "Phase 1"
```

**Good signs:**
```
✅ Phase 1 validation passed
📤 Sending analysis request to Claude...
```

**Warning signs (non-critical):**
```
⚠️ Phase 1 validation warning: positioning_strategy.emphasize must have at least 3 items
```
*Note: These are logged but don't break functionality*

**Bad signs:**
```
🔥 JSON decode error in /api/jd/analyze
```
*This means Claude returned invalid JSON - needs investigation*

---

## **VERIFICATION CHECKLIST**

After deployment, verify:

- [ ] Backend server restarted successfully
- [ ] Health check endpoint responds
- [ ] `/api/jd/analyze` returns positioning_strategy
- [ ] `/api/jd/analyze` returns action_plan
- [ ] `/api/jd/analyze` returns salary_strategy
- [ ] `/api/jd/analyze` returns hiring_intel
- [ ] Frontend package.html loads without errors
- [ ] Strategic Positioning section appears
- [ ] Action Plan section appears
- [ ] Salary Strategy section appears
- [ ] Hiring Intel appears in Outreach tab
- [ ] Download button still works
- [ ] Existing features unchanged

---

## **ROLLBACK PROCEDURE**

If something goes wrong:

### **Rollback Backend:**
```bash
# Stop server
pkill -f "uvicorn"

# Restore backup
cp backend.py.backup.$(date +%Y%m%d) backend.py

# Restart
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &
```

### **Rollback Frontend:**
```bash
# Restore backup
cp frontend/package.html.backup.$(date +%Y%m%d) frontend/package.html

# Clear browser cache
```

---

## **TROUBLESHOOTING**

### **Issue: Server won't start**

```bash
# Check if port is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Check for syntax errors
python -m py_compile backend.py
```

### **Issue: API returns 500 error**

```bash
# Check server logs
tail -100 logs/backend.log

# Common causes:
# 1. Missing ANTHROPIC_API_KEY env var
# 2. JSON parsing error
# 3. Validation too strict
```

### **Issue: Frontend sections don't appear**

```bash
# Check browser console (F12)
# Look for:
# 1. JavaScript errors
# 2. API response structure
# 3. Missing element IDs

# Verify API response
curl http://localhost:8000/api/jd/analyze -X POST \
  -H "Content-Type: application/json" \
  -d @test_request.json | jq .
```

### **Issue: Sections show "undefined" or "null"**

**Cause:** Backend validation passed but fields are empty strings

**Fix:** Check Claude prompt enforcement (may need stricter validation)

---

## **POST-DEPLOYMENT MONITORING**

### **For First 24 Hours:**

```bash
# Monitor API errors
tail -f logs/backend.log | grep "ERROR\|🔥"

# Monitor validation warnings
tail -f logs/backend.log | grep "⚠️"

# Monitor API response times
tail -f logs/backend.log | grep "Response time"
```

### **Key Metrics to Track:**

- [ ] API success rate (should be >95%)
- [ ] Average response time (should be <5 seconds)
- [ ] Validation warning rate (should be <10%)
- [ ] Frontend error rate (check browser console)
- [ ] User completion rate (do they get to download?)

---

## **BETA TESTING INSTRUCTIONS**

Give these instructions to your 5-10 beta testers:

```
Hi! You're testing the updated HenryAI platform with new strategic intelligence features.

WHAT'S NEW:
- Strategic positioning guidance (what to emphasize/de-emphasize)
- Day-by-day action plan
- Salary negotiation strategy
- Hiring manager/recruiter identification help

HOW TO TEST:
1. Go to [your URL]
2. Upload your resume
3. Paste a job description for a real role you're interested in
4. Review the analysis and new sections
5. Download the package

FEEDBACK NEEDED:
- Is this too much information at once?
- Which sections are most valuable?
- What would you remove?
- What would you add?
- Would you pay for this?

REPORT ISSUES:
- Take screenshot of any errors
- Note which browser you're using
- Send to: [your email]

Thanks for helping make this better!
```

---

## **SUCCESS CRITERIA**

**MVP is successful if:**

✅ Backend deploys without errors
✅ Frontend displays all 4 new sections
✅ Existing features still work (download, tracker)
✅ No critical bugs in first 24 hours
✅ Beta testers can complete full flow
✅ At least 3/5 testers say "this is valuable"

**MVP needs iteration if:**

❌ >20% of API calls return validation warnings
❌ Users skip new sections entirely
❌ Download functionality breaks
❌ Performance degrades significantly
❌ Users say "this is overwhelming"

---

## **TIMELINE**

**Deployment:** 15 minutes
**Monitoring:** 2-4 hours (first day)
**Beta testing:** 3-5 days
**Iteration:** 1-2 days
**Production ready:** 1 week

---

## **CONTACT INFO**

If you hit a blocker:

1. Check logs first
2. Review troubleshooting section
3. Test with simplified request
4. Verify environment variables
5. Check API response structure

**Most issues are:**
- Environment variable not set
- Port already in use
- Browser cache not cleared
- Frontend/backend out of sync

---

You're ready to deploy! Follow the steps in order and you'll be live in 15 minutes. 🚀

**Remember:** Backup first, deploy in stages, monitor closely, iterate based on feedback.
