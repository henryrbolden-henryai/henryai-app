# Resume Preview Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER ACTION                               │
│              Upload Resume → Analyze Job → Generate              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: CLAUDE API                           │
│                                                                   │
│  Backend sends prompt with MANDATORY full_text requirement       │
│  Claude returns JSON with resume_output.full_text                │
│                                                                   │
│  ✅ Success: full_text exists → Send to frontend                │
│  ❌ Missing: full_text empty → Go to Layer 2                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 2: BACKEND FALLBACK                       │
│                                                                   │
│  Backend checks: if (!full_text) generate it                     │
│  Function: generate_resume_full_text(resume_output)              │
│  Uses structured fields: summary, experience, skills, etc.       │
│                                                                   │
│  Logs: "⚠️ WARNING: full_text missing, generating fallback"     │
│                                                                   │
│  ✅ Success: full_text generated → Send to frontend             │
│  ❌ Failed: empty result → frontend gets structured fields      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 LAYER 3: FRONTEND FALLBACK                       │
│                                                                   │
│  Frontend checks: if (!full_text) generate it                    │
│  Function: generateResumeFullTextFrontend(resumeOut)             │
│  Uses structured fields from API response                        │
│                                                                   │
│  Logs: "⚠️ Frontend: full_text missing, generating from fields" │
│                                                                   │
│  ✅ Success: full_text generated → Display in preview           │
│  ❌ Failed: no data → Show error message                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESUME PREVIEW                               │
│                                                                   │
│  <div id="resume-preview-full-text">                             │
│    [Complete formatted resume text]                              │
│  </div>                                                          │
│                                                                   │
│  Styled with:                                                    │
│  - white-space: pre-wrap (preserves line breaks)                │
│  - font-family: monospace (resume-like appearance)              │
│  - line-height: 1.6 (readable spacing)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Claude Response
    ↓
Backend Parsing
    ↓
Check full_text?
    ├─ YES → Send to Frontend
    └─ NO  → Generate from structured fields → Send to Frontend
         ↓
Frontend Receives Data
    ↓
Check full_text?
    ├─ YES → Render in preview
    └─ NO  → Generate from structured fields → Render in preview
         ↓
User sees complete resume
```

## Debugging Points

**Backend Console** (Terminal/Server Logs):
```
[1] Claude API response received
[2] ⚠️ WARNING: full_text missing (if Layer 2 triggered)
[3] Generated full_text length: XXX characters
[4] Response sent to frontend
```

**Frontend Console** (Browser DevTools):
```
[1] API response received
[2] ⚠️ Frontend: full_text missing (if Layer 3 triggered)
[3] Resume preview populated: [preview text]...
```

## Success Path (No Fallbacks Needed)

```
Claude generates full_text
    ↓
Backend sends it directly
    ↓
Frontend displays it immediately
    ↓
User sees resume
```

## Fallback Path 1 (Backend Fallback)

```
Claude missing full_text
    ↓
Backend detects missing
    ↓
Backend generates from structured fields
    ↓
Backend sends generated full_text
    ↓
Frontend displays it
    ↓
User sees resume
```

## Fallback Path 2 (Frontend Fallback)

```
Claude missing full_text
    ↓
Backend fails to generate (or sends empty)
    ↓
Frontend receives structured fields only
    ↓
Frontend detects missing full_text
    ↓
Frontend generates from structured fields
    ↓
Frontend displays generated text
    ↓
User sees resume
```

## Failure Scenarios

**Scenario 1**: Claude returns empty resume_output
- **Detection**: Backend logs show `experience_sections count: 0`
- **Cause**: Resume parsing failed or resume data not sent
- **Fix**: Check resume upload/parsing step

**Scenario 2**: Backend receives data but can't generate full_text
- **Detection**: Backend logs show very short full_text (< 50 chars)
- **Cause**: Structured fields are empty
- **Fix**: Check resume_output has summary, experience_sections, skills

**Scenario 3**: Frontend receives empty resume_output
- **Detection**: Console shows "Frontend fallback failed - no resume data"
- **Cause**: Backend didn't send resume_output at all
- **Fix**: Check API response in Network tab

**Scenario 4**: Resume preview element doesn't exist
- **Detection**: Console error about getElementById
- **Cause**: HTML template issue
- **Fix**: Verify `<div id="resume-preview-full-text">` exists
```
