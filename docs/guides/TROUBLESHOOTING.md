# Troubleshooting Resume Upload Error

## The Error You're Seeing

**Alert message:** "Error uploading resume. Please check the console for details."

This means the frontend successfully captured the file but failed when trying to send it to the backend.

---

## Quick Diagnosis

Run this diagnostic script to identify the issue:

```bash
cd /path/to/outputs
python3 diagnose_backend.py
```

This will check:
1. ✅ Is backend running?
2. ✅ Is CORS configured correctly?
3. ✅ Does file upload endpoint work?
4. ✅ Does text endpoint work?

---

## Most Likely Causes

### Issue 1: Backend Not Running ⚠️

**Check:** Is the backend server running?

```bash
curl http://localhost:8000/
```

**If you see:** "Connection refused" or no response
**Solution:**

```bash
# Terminal 1: Start backend
export ANTHROPIC_API_KEY="your-actual-api-key"
python backend.py
```

You should see:
```
🚀 Henry Job Search Engine API starting on http://localhost:8000
```

### Issue 2: CORS / file:// Protocol Issue ⚠️

**Problem:** Opening `index.html` directly (file:// protocol) may have CORS restrictions

**Solution:** Serve via HTTP server instead

```bash
# Terminal 2: Serve frontend
python3 serve_frontend.py
```

Then open in browser: **http://localhost:8080/index.html**

### Issue 3: Wrong API Key

**Check:** Is your Anthropic API key valid?

```bash
echo $ANTHROPIC_API_KEY
```

**Solution:** Get your API key from https://console.anthropic.com/settings/keys

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Step-by-Step Fix

### Step 1: Verify Backend is Running

```bash
# Start backend (Terminal 1)
cd /path/to/outputs
export ANTHROPIC_API_KEY="your-actual-key"
python backend.py
```

**Expected output:**
```
🚀 Henry Job Search Engine API starting on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
🔑 Using Anthropic API key: sk-ant-...
```

**Test it:**
```bash
curl http://localhost:8000/
```

Should return JSON with status "running"

### Step 2: Serve Frontend via HTTP

**Instead of opening `index.html` directly, serve it:**

```bash
# Start frontend server (Terminal 2)
cd /path/to/outputs
python3 serve_frontend.py
```

**Expected output:**
```
✅ Serving index.html at: http://localhost:8080
✅ API backend should be at: http://localhost:8000
📝 Open in browser: http://localhost:8080/index.html
```

### Step 3: Open in Browser

**Go to:** http://localhost:8080/index.html

**NOT:** file:///path/to/index.html

### Step 4: Test Upload

1. Click "Upload my resume (PDF or DOCX)"
2. Select a PDF or DOCX file
3. Click "Continue"

**Success:** You'll see "Resume received and parsed. Henry will use this to build your profile."

**If still failing:** Open browser console (F12) and check for errors

---

## Debugging in Browser Console

### Open DevTools

**Chrome/Edge:** F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
**Firefox:** F12 or Ctrl+Shift+K (Cmd+Option+K on Mac)
**Safari:** Cmd+Option+I (enable Developer menu first)

### What to Look For

Go to **Console** tab and look for errors:

#### Error: "Failed to fetch" or "net::ERR_CONNECTION_REFUSED"
**Meaning:** Backend is not running
**Fix:** Start backend: `python backend.py`

#### Error: "CORS policy blocked"
**Meaning:** CORS issue with file:// protocol
**Fix:** Use HTTP server: `python3 serve_frontend.py`

#### Error: "500 Internal Server Error"
**Meaning:** Backend error (possibly API key issue)
**Fix:** Check backend terminal for error message

#### Error: "400 Bad Request - No resume provided"
**Meaning:** FormData not being sent correctly
**Fix:** Make sure you selected a file before clicking Continue

---

## Alternative: Use Interactive API Docs

If frontend still has issues, you can test the backend directly:

1. **Open:** http://localhost:8000/docs
2. **Find:** POST /api/resume/parse
3. **Click:** "Try it out"
4. **Upload:** Your resume PDF/DOCX
5. **Execute**
6. **See:** The parsed JSON response

This confirms the backend is working independently of the frontend.

---

## Quick Reference

### Complete Startup Sequence

```bash
# Terminal 1: Backend
cd /path/to/outputs
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
python backend.py

# Terminal 2: Frontend  
cd /path/to/outputs
python3 serve_frontend.py

# Browser
open http://localhost:8080/index.html
```

### Verify Everything is Working

```bash
# Test backend
curl http://localhost:8000/

# Test file upload endpoint
python3 diagnose_backend.py

# Open interactive docs
open http://localhost:8000/docs
```

---

## Common Mistakes

❌ **Wrong:** Opening file:///Users/.../index.html directly
✅ **Right:** Opening http://localhost:8080/index.html

❌ **Wrong:** Forgetting to start backend
✅ **Right:** Backend running on port 8000, frontend on 8080

❌ **Wrong:** Using wrong/expired API key
✅ **Right:** Valid Anthropic API key from console.anthropic.com

❌ **Wrong:** Clicking Continue without selecting a file
✅ **Right:** Select file first, then Continue

---

## Still Not Working?

### Check Backend Logs

Look at the backend terminal for error messages:

```
ERROR: Claude API error: ...
ERROR: PDF extraction failed: ...
ERROR: Error parsing resume: ...
```

### Check Browser Network Tab

1. Open DevTools (F12)
2. Go to **Network** tab
3. Try uploading resume
4. Look for the POST request to `/api/resume/parse`
5. Check status code and response

**Status 200:** Success ✅
**Status 400:** Bad request (missing data)
**Status 500:** Server error (check backend logs)
**Status 0 or Failed:** Connection issue (backend not running)

### Get Detailed Error

In browser console, type:

```javascript
// See what's stored
console.log("User resume:", window.userResume);

// Test API directly
fetch('http://localhost:8000/')
  .then(r => r.json())
  .then(d => console.log('Backend:', d))
  .catch(e => console.error('Error:', e));
```

---

## Contact Points

**Backend Issues:**
- Check: backend.py terminal output
- Test: http://localhost:8000/docs
- Run: python3 diagnose_backend.py

**Frontend Issues:**
- Check: Browser console (F12)
- Check: Network tab for failed requests
- Serve: python3 serve_frontend.py

**API Key Issues:**
- Verify: echo $ANTHROPIC_API_KEY
- Get key: https://console.anthropic.com/settings/keys
- Check quota: console.anthropic.com

---

## Success Checklist

Before trying to upload:

- [ ] Backend running on port 8000
- [ ] Frontend served on port 8080 (not file://)
- [ ] ANTHROPIC_API_KEY is set and valid
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:8080/index.html
- [ ] Browser console is open (F12) to see errors
- [ ] Have a valid PDF or DOCX resume file ready

If all checkboxes are ✅ and upload still fails, copy the exact error message from browser console and check backend terminal output.
