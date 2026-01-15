# Interview Intelligence Pre-Launch Test Script

**Tester:** _______________  
**Date:** _______________  
**Environment:** Production / Staging (circle one)

---

## Setup Before Testing

1. Open browser dev tools (F12)
2. Keep Console and Network tabs visible
3. Clear localStorage: `localStorage.clear()` in console
4. Hard refresh the page (Ctrl+Shift+R / Cmd+Shift+R)

---

## Test 1: Mock Interview - Full Lifecycle

### 1.1 Session Start

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1.1.1 | Navigate to Interview Intelligence | Page loads, "Start Mock Interview" button visible | ☐ | |
| 1.1.2 | Click "Start Mock Interview" | Setup card appears with form fields | ☐ | |
| 1.1.3 | Fill in: Company = "Test Corp", Role = "Product Manager", Type = "Recruiter Screen" | Fields accept input | ☐ | |
| 1.1.4 | Click "Start Interview" | Chat interface appears, first question displays | ☐ | |
| 1.1.5 | Check Network tab | `POST /api/mock-interview/start` returns 200 | ☐ | |
| 1.1.6 | Check Console | "Session synced to Supabase" or similar log appears | ☐ | |

### 1.2 Mid-Session Responses

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1.2.1 | Type a response to Question 1: "I have 5 years of PM experience at tech companies" | Message appears in chat as user bubble | ☐ | |
| 1.2.2 | Click Send or press Enter | Typing indicator shows, then interviewer responds | ☐ | |
| 1.2.3 | Check Network tab | `POST /api/mock-interview/response` returns 200 | ☐ | |
| 1.2.4 | Answer Question 2 with any response | Follow-up question or coaching appears | ☐ | |
| 1.2.5 | Check progress bar | Shows "Question 2 of X" | ☐ | |

### 1.3 Persistence Test (Critical)

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1.3.1 | Note current question number | Record: Q___ of ___ | ☐ | |
| 1.3.2 | Hard refresh page (Ctrl+Shift+R) | Page reloads | ☐ | |
| 1.3.3 | Check if session resumes | Either: resumes at same question OR prompts to continue | ☐ | |
| 1.3.4 | If session lost, note in comments | This is a bug if data doesn't persist | ☐ | |

### 1.4 Session Completion

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1.4.1 | Complete remaining questions (or answer 3 total) | "End Interview" button appears or auto-prompts | ☐ | |
| 1.4.2 | Click "End Interview" | Loading overlay: "Generating your debrief..." | ☐ | |
| 1.4.3 | Check Network tab | `POST /api/mock-interview/end` returns 200 | ☐ | |
| 1.4.4 | Redirects to mock-debrief.html | Debrief page loads with analysis | ☐ | |
| 1.4.5 | Debrief contains actual responses | Your answers are referenced, not placeholders | ☐ | |
| 1.4.6 | Ratings display (Content, Clarity, etc.) | Scores 1-5 visible for each category | ☐ | |

### 1.5 Edge Cases

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 1.5.1 | Start a new mock interview immediately | Fresh session starts, no stale data from previous | ☐ | |
| 1.5.2 | Mid-interview, click "Exit" button | Confirmation dialog: "Are you sure? Progress will be lost" | ☐ | |
| 1.5.3 | Click Cancel on confirmation | Stays in interview | ☐ | |
| 1.5.4 | Click Confirm on exit | Returns to Interview Intelligence main page | ☐ | |

---

## Test 2: Interview Prep Generation

### 2.1 Recruiter Screen Prep

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 2.1.1 | Navigate to Interview Intelligence | Page loads | ☐ | |
| 2.1.2 | Add an upcoming interview (or select existing) | Interview card appears | ☐ | |
| 2.1.3 | Click "Prepare" or equivalent | Prep generation starts | ☐ | |
| 2.1.4 | Select "Recruiter Screen" type | Prep generates for recruiter context | ☐ | |
| 2.1.5 | Talking points render | 4-6 bullet points visible | ☐ | |
| 2.1.6 | Points are grounded in candidate resume | No fabricated experience or metrics | ☐ | |

### 2.2 Hiring Manager Prep

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 2.2.1 | Generate prep for "Hiring Manager" type | Prep generates with different focus | ☐ | |
| 2.2.2 | STAR examples present | At least 2 behavioral examples with Situation/Task/Action/Result | ☐ | |
| 2.2.3 | Gap mitigation strategies included | Addresses potential concerns proactively | ☐ | |
| 2.2.4 | Questions to ask interviewer | 3-5 relevant questions listed | ☐ | |

### 2.3 Context Validation

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 2.3.1 | If linked to tracked application | JD context reflected in prep | ☐ | |
| 2.3.2 | Company name appears correctly | Matches what was entered | ☐ | |
| 2.3.3 | Role title appears correctly | Matches what was entered | ☐ | |

---

## Test 3: Debrief Chat

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 3.1 | After completing mock interview, navigate to debrief | Debrief page loads | ☐ | |
| 3.2 | Start debrief conversation (if chat available) | Chat interface responds | ☐ | |
| 3.3 | Ask for coaching on a specific answer | Response references your actual answer | ☐ | |
| 3.4 | Coaching is specific, not generic | Actionable feedback tied to your responses | ☐ | |

---

## Test 4: Error Handling

| Step | Action | Expected Result | Pass/Fail | Notes |
|------|--------|-----------------|-----------|-------|
| 4.1 | Disconnect network, try to send message | Graceful error message, not crash | ☐ | |
| 4.2 | Submit empty response | Validation prevents send OR graceful handling | ☐ | |
| 4.3 | Rapidly click Send 10 times | No duplicate messages, no 429 errors | ☐ | |

---

## Test Summary

| Section | Tests Passed | Tests Failed | Critical Issues |
|---------|--------------|--------------|-----------------|
| Mock Interview - Lifecycle | /6 | | |
| Mock Interview - Responses | /5 | | |
| Mock Interview - Persistence | /4 | | |
| Mock Interview - Completion | /6 | | |
| Mock Interview - Edge Cases | /4 | | |
| Interview Prep | /10 | | |
| Debrief Chat | /4 | | |
| Error Handling | /3 | | |
| **TOTAL** | **/42** | | |

---

## Critical Issues Log

| Issue # | Description | Severity (High/Med/Low) | Steps to Reproduce |
|---------|-------------|------------------------|-------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## Sign-Off

**Testing Complete:** ☐ Yes ☐ No  
**Ready for Launch:** ☐ Yes ☐ No ☐ Conditional (explain below)

**Conditional Notes:**
_____________________________________________
_____________________________________________

**Tester Signature:** _______________  
**Date:** _______________
