# 🚀 HENRY JOB SEARCH ENGINE - QUICK START

## The Problem You're Seeing

**Error:** "Error uploading resume. Please check the console for details."

**Root Cause:** The backend server is not running at http://localhost:8000

---

## ✅ SOLUTION: Start Both Servers

You need TWO terminals running:

### Terminal 1: Backend API Server

```bash
cd /path/to/outputs
export ANTHROPIC_API_KEY="sk-ant-your-actual-key"
python backend.py
```

**Expected output:**
```
🚀 Henry Job Search Engine API starting on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
🔑 Using Anthropic API key: sk-ant-...
```

### Terminal 2: Frontend Web Server

```bash
cd /path/to/outputs
python3 -m http.server 8080
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

### Browser

**Open:** http://localhost:8080/index.html

**NOT file:///path/to/index.html** ← This causes CORS errors!

---

## 🔍 Quick Verification

### 1. Is Backend Running?

```bash
curl http://localhost:8000/
```

**Should return:**
```json
{
  "status": "running",
  "service": "Henry Job Search Engine API",
  "version": "1.2.0",
  "endpoints": [...]
}
```

**If you get "Connection refused"** → Backend is NOT running. Go start it!

### 2. Is Frontend Accessible?

Open browser to: http://localhost:8080/index.html

You should see the Henry landing page.

### 3. Test Resume Upload

1. Click "Upload my resume (PDF or DOCX)"
2. Select a PDF or DOCX file
3. Click "Continue"
4. **Success:** "Resume received and parsed..."
5. **Failure:** Check browser console (F12) for error details

---

## 🐛 Debugging Checklist

If upload still fails, check these:

### ✓ Backend Running?
```bash
ps aux | grep "python.*backend.py"
curl http://localhost:8000/
```

### ✓ API Key Set?
```bash
echo $ANTHROPIC_API_KEY
# Should show: sk-ant-...
```

### ✓ Using HTTP not file://?
Browser URL should be: `http://localhost:8080/index.html`
NOT: `file:///Users/.../index.html`

### ✓ No Port Conflicts?
```bash
lsof -i :8000  # Should show Python process
lsof -i :8080  # Should show Python process
```

### ✓ Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Try upload again
4. Look for red error messages

### ✓ Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Try upload again
4. Find POST request to `/api/resume/parse`
5. Check status code:
   - **200** = Success ✅
   - **0 or Failed** = Backend not running ❌
   - **400** = Bad request (check what was sent)
   - **500** = Server error (check backend terminal)

---

## 📁 File Structure

```
/outputs/
├── backend.py              ← Backend API server
├── index.html              ← Frontend UI
├── test_*.py              ← Test scripts
├── *.md                   ← Documentation
└── *_stubs.js             ← Integration code
```

---

## 🎯 Complete Startup Process

### Step 1: Get Your API Key

1. Go to https://console.anthropic.com/settings/keys
2. Create an API key (starts with `sk-ant-`)
3. Copy it

### Step 2: Set Environment Variable

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Verify it's set:**
```bash
echo $ANTHROPIC_API_KEY
```

### Step 3: Start Backend

```bash
cd /path/to/outputs
python backend.py
```

**Wait for:** "Henry Job Search Engine API starting on http://localhost:8000"

**Leave this terminal running!**

### Step 4: Start Frontend (New Terminal)

```bash
cd /path/to/outputs
python3 -m http.server 8080
```

**Wait for:** "Serving HTTP on 0.0.0.0 port 8080"

**Leave this terminal running!**

### Step 5: Open Browser

```bash
open http://localhost:8080/index.html
# Or manually navigate to http://localhost:8080/index.html
```

### Step 6: Upload Resume

1. Click "Upload my resume"
2. Select your PDF or DOCX
3. Click "Continue"
4. Should see success message
5. Proceed to preferences

---

## 💡 Common Errors & Solutions

### Error: "Connection refused"
**Cause:** Backend not running
**Fix:** Start backend in Terminal 1

### Error: "CORS policy blocked"
**Cause:** Using file:// protocol
**Fix:** Serve via HTTP: `python3 -m http.server 8080`

### Error: "No resume provided"
**Cause:** File not attached to request
**Fix:** Make sure you selected a file before clicking Continue

### Error: "Failed to parse Claude response"
**Cause:** Invalid API key or API error
**Fix:** Check your ANTHROPIC_API_KEY

### Error: "Unsupported file type"
**Cause:** File is not PDF, DOCX, or TXT
**Fix:** Convert your file or use "Paste my resume text" option

---

## 🧪 Test Backend Directly

Visit the interactive API docs:

**URL:** http://localhost:8000/docs

1. Find `POST /api/resume/parse`
2. Click "Try it out"
3. Upload your resume file
4. Click "Execute"
5. See the parsed JSON response

This confirms backend is working independently of frontend.

---

## 📊 All 11 Endpoints Available

Your backend provides:

**Core:**
1. POST /api/resume/parse (file upload)
2. POST /api/resume/parse/text (JSON text)
3. POST /api/jd/analyze
4. POST /api/documents/generate

**MVP+1:**
5. POST /api/tasks/prioritize
6. POST /api/outcomes/log
7. POST /api/strategy/review
8. POST /api/network/recommend

**Interview Intelligence:**
9. POST /api/interview/parse
10. POST /api/interview/feedback
11. POST /api/interview/thank_you

---

## 🎬 Video Walkthrough (Text Version)

```
Terminal 1:
┌─────────────────────────────────────┐
│ $ cd /path/to/outputs               │
│ $ export ANTHROPIC_API_KEY="sk..." │
│ $ python backend.py                 │
│ 🚀 Starting on port 8000...         │
│ [Keep running]                      │
└─────────────────────────────────────┘

Terminal 2:
┌─────────────────────────────────────┐
│ $ cd /path/to/outputs               │
│ $ python3 -m http.server 8080       │
│ Serving on port 8080...             │
│ [Keep running]                      │
└─────────────────────────────────────┘

Browser:
┌─────────────────────────────────────┐
│ http://localhost:8080/index.html    │
│ ↓                                    │
│ Upload Resume → Continue → Success! │
└─────────────────────────────────────┘
```

---

## ✅ Success Indicators

You know it's working when:

- ✅ Backend terminal shows "Starting on http://localhost:8000"
- ✅ Frontend terminal shows "Serving HTTP on 0.0.0.0 port 8080"
- ✅ http://localhost:8000/ returns JSON with "status": "running"
- ✅ http://localhost:8080/index.html loads the UI
- ✅ Upload → Continue → "Resume received and parsed"
- ✅ Browser console (F12) shows "Parsed resume:" with JSON data

---

## 🆘 Still Not Working?

### Run Diagnostics

```bash
cd /path/to/outputs
python3 diagnose_backend.py
```

This will check:
- Is backend running?
- Is CORS configured?
- Do endpoints work?

### Get Help

1. Check backend terminal for errors
2. Check browser console (F12) for errors
3. Check Network tab for failed requests
4. Copy exact error messages
5. Check if ports 8000 and 8080 are available

---

## 🎉 Next Steps After Success

Once resume upload works:

1. **Enter preferences** → See your personalized snapshot
2. **Paste a job description** → Get fit score and analysis
3. **Generate materials** → Download tailored resume and cover letter
4. **Try MVP+1 features** → Task prioritization, strategy review
5. **Try Interview Intelligence** → Upload interview transcripts

---

## 📚 Additional Resources

- **Full API Docs:** API_DOCUMENTATION.md
- **Troubleshooting:** TROUBLESHOOTING.md
- **Interview Features:** INTERVIEW_INTELLIGENCE_DOCS.md
- **Test Scripts:** test_mvp_plus_features.py, test_interview_intelligence.py

---

## 🔑 Remember

**TWO servers must be running:**
1. Backend (port 8000) ← Provides the API
2. Frontend (port 8080) ← Serves the UI

**Use HTTP, not file://**
Browser should show: http://localhost:8080/index.html

**API key must be set:**
Backend needs ANTHROPIC_API_KEY environment variable

That's it! Now start both servers and you're ready to use Henry! 🚀
