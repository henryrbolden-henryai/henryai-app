# 🔧 BACKEND INTEGRATION — MUST DO NOW

**Why you're seeing fallback text and empty sections:**
Your backend hasn't been updated with enhanced prompts yet.

**Time to fix:** 15 minutes

---

## **STEP 1: VERIFY BACKEND STATUS (2 min)**

### **Check if backend prompts were updated:**

```bash
cd your-backend-directory

# Search for the new prompt structure
grep -n "EXTRACT CANDIDATE FIRST NAME ONLY" backend.py

# If found: Backend is integrated ✅
# If not found: Backend needs integration ❌
```

**If not found, continue to Step 2.**

---

## **STEP 2: BACKUP BACKEND (30 sec)**

```bash
cp backend.py backend.py.backup.$(date +%Y%m%d_%H%M)
echo "✓ Backend backed up"
```

---

## **STEP 3: FIND THE PROMPT SECTION (1 min)**

```bash
# Open backend.py in your editor
code backend.py  # or vim, nano, etc.

# Search for (Cmd+F or Ctrl+F):
"INTELLIGENCE LAYER"

# OR search for:
"JOB QUALITY SCORE"

# You should land around line 1050-1100
# This is where the Claude prompt starts
```

---

## **STEP 4: REPLACE THE PROMPT (10 min)**

### **What to replace:**

Find this structure (around lines 1050-1400):

```python
        prompt = f"""You are an expert executive recruiter...

=== INTELLIGENCE LAYER (MANDATORY - MUST BE COMPLETE) ===

[... OLD PROMPT CONTENT - DELETE ALL OF THIS ...]

"""
```

### **Replace with:**

**Copy the enhanced prompt from** `/mnt/user-data/outputs/BACKEND_INTEGRATION_GUIDE.md`

**Key sections in the new prompt:**
1. ✅ EXTRACT CANDIDATE FIRST NAME ONLY
2. ✅ EXTRACT COMPANY NAME FROM JD
3. ✅ Comprehensive action_plan with company names
4. ✅ salary_strategy with market_data always provided
5. ✅ Outreach templates referencing actual experience
6. ✅ No em dashes
7. ✅ Always-populated arrays

**The new prompt starts with:**
```python
        prompt = f"""You are an expert executive recruiter and career strategist analyzing this job description{' and candidate resume' if resume_text else ''}.

=== CRITICAL INSTRUCTIONS ===

1. EXTRACT CANDIDATE FIRST NAME ONLY
   - Parse full name from resume
   - Use ONLY first name (e.g., "Henry R. Bolden III" → "Henry")
```

**The new prompt ends with:**
```python
=== VALIDATION CHECKLIST ===
Before returning response, verify:
1. ✅ First name extracted (not full name)
2. ✅ Company name from JD used throughout (no placeholders)
...
"""
```

---

## **STEP 5: SAVE & RESTART BACKEND (2 min)**

```bash
# Save backend.py in your editor

# Kill current backend
pkill -f "uvicorn"

# Restart backend
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &

# Wait for startup
sleep 5

# Verify running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

---

## **STEP 6: TEST THE FIX (5 min)**

### **Run a complete analysis:**

1. Go to your app
2. Upload resume + paste job description
3. Click "Analyze This Role"
4. Wait for completion
5. Click "Get Your Package"

### **Check for these changes:**

**✅ Positioning Strategy:**
- Should show: "Henry, frame yourself as..." (first name only)
- Should have: 3+ comprehensive emphasize items (1-2 sentences each)
- Should have: 2+ de-emphasize items with reasoning
- NOT: "Strategic emphasis points will be generated..."

**✅ Action Plan:**
- Should have: 3-4 tasks under TODAY
- Should reference: Actual company name (not "[Company Name]")
- Should include: Specific actions like "Apply via Coast ATS..."
- NOT: "Action items will be generated..."

**✅ Salary Strategy:**
- Their Range: Extracted or "Not disclosed in job description"
- Your Target: Specific range with reasoning (e.g., "$190K-$220K base based on...")
- Market Data: Specific data (e.g., "Director of TA at Series B fintech: $180K-$230K...")
- Talking Points: 3-4 specific items from resume
- NOT: "Market data available"

**✅ Documents:**
- Resume should load (not stuck on error)
- Cover letter should load (not stuck on error)
- Download buttons should work

---

## **VERIFICATION CHECKLIST**

After testing, confirm:

- [ ] First name only appears ("Henry," not "Henry R. Bolden III,")
- [ ] Actual company name throughout (no "[Company Name]")
- [ ] Action plan populated with 3-4 tasks per section
- [ ] Company name in action items (e.g., "Apply via Coast ATS...")
- [ ] Market data shows actual data (not "Market data available")
- [ ] Talking points populated (3-4 items)
- [ ] Emphasize/de-emphasize comprehensive (1-2 sentences each)
- [ ] Strategic framing comprehensive (not just "frame yourself...")
- [ ] Outreach templates reference actual experience
- [ ] No em dashes in outreach
- [ ] Documents generate and load successfully

---

## **IF IT STILL DOESN'T WORK**

### **Issue 1: Still seeing fallback text**

**Cause:** Prompt wasn't fully replaced or backend didn't restart properly

**Fix:**
```bash
# Verify prompt was replaced
grep -n "EXTRACT CANDIDATE FIRST NAME" backend.py

# If not found, prompt wasn't replaced correctly
# Try again, making sure to:
# 1. Select entire old prompt (lines 1050-1400)
# 2. Delete completely
# 3. Paste new prompt
# 4. Save file
# 5. Restart backend
```

### **Issue 2: Documents still not loading**

**Cause:** Document generation may have separate issues

**Fix:**
```bash
# Check backend logs
tail -f logs/backend.log | grep "document"

# Look for errors in document generation
```

### **Issue 3: Backend won't start**

**Cause:** Syntax error in prompt

**Fix:**
```bash
# Check for Python syntax errors
python -m py_compile backend.py

# If errors, check:
# - All opening quotes have closing quotes
# - All opening brackets have closing brackets
# - No stray characters in prompt
```

---

## **ROLLBACK IF NEEDED**

```bash
pkill -f "uvicorn"
cp backend.py.backup.* backend.py
uvicorn backend:app --reload --host 0.0.0.0 --port 8000 &
```

---

## **SUCCESS LOOKS LIKE**

**Positioning Page:**
```
Strategic Framing:
Henry, frame yourself as a fintech recruiting leader who can step 
into a Series B environment and own product strategy from day one...

✓ EMPHASIZE:
Your fintech recruiting experience at Uber Payments and Venmo, where 
you specifically built payments infrastructure teams. This is directly 
relevant to Coast's need for someone who understands fintech talent 
challenges.

📅 Your Action Plan
🎯 TODAY
☐ Apply via Coast ATS before end of day
☐ Research hiring manager on LinkedIn (search 'Coast talent acquisition')
☐ Check Glassdoor for Coast reviews

💰 Salary Strategy
THEIR RANGE: Not disclosed in job description
YOUR TARGET: $190K-$220K base (based on 10+ years experience, 
Director-level role, and fintech market in major metro)
MARKET DATA: Director of TA at Series B fintech startups typically 
ranges $180K-$230K in major metros. Glassdoor shows $195K median.
```

**Documents Page:**
```
[Resume loads successfully]
[Cover letter loads successfully]
[Download buttons work]
```

---

## **NEXT STEPS**

Once backend is integrated and working:

1. ✅ Test with 2-3 different job descriptions
2. ✅ Verify all content is personalized
3. ✅ Check documents download correctly
4. ✅ Deploy clean overview.html (without extra buttons)
5. ✅ Ready for beta testing tomorrow

---

**The backend integration is the critical blocker.** Once this is done, everything else will work.

Follow these steps carefully and you'll be ready to test tonight! 🚀
