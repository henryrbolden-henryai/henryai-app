# Welcome Email Automation - Implementation Guide

## Overview
Automatically send welcome email after user confirms their email address via Supabase authentication.

---

## Architecture

**Flow:**
1. User signs up with email
2. Supabase sends confirmation email (already configured)
3. User clicks confirmation link
4. Supabase confirms user account
5. **[NEW]** Frontend detects confirmation → triggers backend
6. **[NEW]** Backend sends welcome email via Resend API

---

## Files Created

1. **`send_welcome_email.py`** - Backend endpoint (FastAPI)
2. **`welcome-email-trigger.js`** - Frontend trigger (JavaScript)
3. **`henryhq_welcome_email.html`** - Email template (already created)

---

## Implementation Steps

### Step 1: Backend Setup (5 minutes)

#### 1.1 Add Backend Code
Copy code from `send_welcome_email.py` and add to your `backend.py`:

```python
# At the top with other imports
import requests
from pydantic import BaseModel

# Add environment variable
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Add the WelcomeEmailRequest model
class WelcomeEmailRequest(BaseModel):
    email: str
    name: str = None

# Add the send_welcome_email function (full code in send_welcome_email.py)
async def send_welcome_email(email: str, name: str = None):
    # ... (copy full function)

# Add the endpoint
@app.post("/api/send-welcome-email")
async def send_welcome_email_endpoint(request: WelcomeEmailRequest):
    result = await send_welcome_email(request.email, request.name)
    return result
```

#### 1.2 Set Environment Variable
Add to your backend environment (Railway, Vercel, etc.):
```bash
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
```

Get your API key from: https://resend.com/api-keys

#### 1.3 Deploy Backend
```bash
git add backend.py
git commit -m "Add welcome email endpoint"
git push origin main
```

#### 1.4 Test Endpoint
```bash
curl -X POST https://your-backend-url.com/api/send-welcome-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

Expected response:
```json
{
  "success": true,
  "message": "Welcome email sent",
  "email_id": "some-resend-id"
}
```

---

### Step 2: Frontend Setup (10 minutes)

#### 2.1 Choose Implementation Approach

**Option 1: Auth State Change Listener (RECOMMENDED)**
- Most reliable
- Works immediately after confirmation
- Easy to debug

**Option 2: Polling After Signup**
- Simpler to implement
- Less reliable (user might close tab)

**Option 3: Supabase Edge Function**
- Most robust
- Requires Supabase project configuration
- Use this for production scale

**Start with Option 1, migrate to Option 3 later if needed.**

#### 2.2 Add Frontend Code

Find your main authentication handler (likely `login.html` or a shared auth file).

Add this code:

```javascript
// Import Supabase client
import { supabase } from './supabase-client.js';

// Add auth state listener (run once on app load)
supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth event:', event);
    
    if (event === 'SIGNED_IN' && session?.user) {
        const isFirstSignIn = !localStorage.getItem('welcome_email_sent');
        
        if (isFirstSignIn) {
            console.log('First sign-in detected, sending welcome email...');
            
            try {
                const response = await fetch('https://your-backend-url.com/api/send-welcome-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: session.user.email,
                        name: session.user.user_metadata?.name
                    })
                });
                
                if (response.ok) {
                    console.log('Welcome email sent successfully');
                    localStorage.setItem('welcome_email_sent', 'true');
                } else {
                    console.error('Failed to send welcome email');
                }
            } catch (error) {
                console.error('Error sending welcome email:', error);
            }
        }
    }
});
```

#### 2.3 Update Backend URL
Replace `https://your-backend-url.com` with your actual backend URL.

#### 2.4 Deploy Frontend
```bash
git add login.html  # or whichever file you modified
git commit -m "Add welcome email trigger on first sign-in"
git push origin main
```

---

### Step 3: Testing (15 minutes)

#### 3.1 Create Test Account
1. Go to your signup page
2. Create account with **real email** (not test@example.com)
3. Check email for confirmation link
4. Click confirmation link

#### 3.2 Verify Welcome Email
1. Check inbox for welcome email
2. Subject should be: "You're in. Let's make your job search smarter."
3. Check that logo renders correctly
4. Click "Run Your First Analysis" button → should go to dashboard

#### 3.3 Check Logs
**Backend logs (Railway/Vercel):**
```
POST /api/send-welcome-email 200
Welcome email sent: {email_id: "..."}
```

**Frontend console:**
```
Auth event: SIGNED_IN
First sign-in detected, sending welcome email...
Welcome email sent successfully
```

**Resend dashboard:**
- Go to https://resend.com/emails
- Should see new email with status "Delivered"

#### 3.4 Test Deliverability
1. Send test email to yourself
2. Check mail-tester.com score: https://www.mail-tester.com
   - Should be **9-10/10** (DNS configured correctly)
   - If lower, check SPF/DKIM/DMARC records
3. Test in multiple email clients:
   - Gmail ✓
   - Outlook ✓
   - Apple Mail ✓
   - Yahoo ✓

---

## Troubleshooting

### Problem: Welcome email not sending

**Check 1: Backend endpoint**
```bash
curl -X POST https://your-backend-url.com/api/send-welcome-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```
- If 500 error → Check RESEND_API_KEY environment variable
- If 404 error → Endpoint not deployed, check backend.py

**Check 2: Frontend trigger**
- Open browser console
- Sign in with confirmed account
- Should see: "Auth event: SIGNED_IN"
- Should see: "Welcome email sent successfully"
- If not, check auth state listener is registered

**Check 3: Resend API**
- Check Resend dashboard for failed emails
- Check API key is valid
- Check daily sending limits (100 emails/day on free tier)

### Problem: Email goes to spam

**Fix 1: DNS Records**
Verify all DNS records are set correctly in Cloudflare:
- SPF: `v=spf1 include:_spf.resend.com ~all`
- DKIM: `resend._domainkey` CNAME to Resend
- DMARC: `v=DMARC1; p=none; rua=mailto:hello@henryhq.ai`

**Fix 2: Warm Up Domain**
- Start by sending to yourself and close contacts
- Gradually increase volume
- Wait 24-48 hours for reputation to build

**Fix 3: Email Content**
- Avoid spam trigger words: "free", "act now", "click here"
- Include unsubscribe link (add if needed)
- Use professional sender name: "HenryHQ" not "noreply"

### Problem: Duplicate emails

**Check localStorage flag:**
```javascript
// Should be set after first email sent
localStorage.getItem('welcome_email_sent') // Should return 'true'
```

**Clear flag for testing:**
```javascript
localStorage.removeItem('welcome_email_sent')
```

**Add backend deduplication:**
```python
# In send_welcome_email function, add check:
# Query database to see if welcome email already sent to this email
# Only send if not already sent
```

---

## Production Checklist

Before launching to beta users:

- [ ] Backend endpoint deployed and tested
- [ ] RESEND_API_KEY environment variable set
- [ ] Frontend trigger tested with real account
- [ ] Welcome email received in inbox (not spam)
- [ ] Logo renders correctly in email
- [ ] CTA button works (goes to dashboard)
- [ ] Mail-tester.com score is 9-10/10
- [ ] Tested in Gmail, Outlook, Apple Mail
- [ ] No duplicate emails sent
- [ ] Backend logs show successful sends
- [ ] Resend dashboard shows delivered emails

---

## Monitoring

### Week 1 After Launch
- Check Resend dashboard daily
- Monitor delivery rates (target: 99%+)
- Check spam complaints (target: <0.1%)
- Review backend logs for errors

### Metrics to Track
- **Delivery rate:** Emails delivered / Emails sent (target: 99%+)
- **Open rate:** Emails opened / Emails delivered (target: 40-60%)
- **Click rate:** Clicks on CTA / Emails delivered (target: 20-30%)
- **Spam complaints:** Should be 0

### Resend Dashboard Monitoring
1. Go to https://resend.com/emails
2. Check:
   - Delivered (green) vs Bounced (red)
   - Open rates
   - Click rates
   - Any spam complaints

---

## Migration to Production Scale (Optional - Later)

Once you have 100+ users, consider upgrading to Option 3 (Supabase Edge Function):

### Why Migrate?
- More reliable (server-side execution)
- Doesn't depend on user keeping browser open
- Handles rate limiting better
- Better for compliance (user can't bypass)

### How to Migrate
1. Create Supabase Edge Function
2. Set up database webhook (auth.users INSERT)
3. Move welcome email logic to Edge Function
4. Remove frontend trigger
5. Test with new signups

Estimated time: 30 minutes

---

## Cost Analysis

**Resend Costs:**
- Free tier: 100 emails/day, 3,000 emails/month
- Pro tier ($20/month): 50,000 emails/month
- At 10 signups/day: Free tier is sufficient for first 3 months
- At 100 signups/day: Need Pro tier

**Backend Costs:**
- Negligible (1 API call per signup)
- No additional hosting costs

**Total Cost: $0/month** (on free tier until you hit 100 emails/day)

---

## Next Steps

1. **Immediate:** Implement backend endpoint (5 min)
2. **Today:** Add frontend trigger (10 min)
3. **This Week:** Test with 3-5 beta users
4. **Before Public Launch:** Ensure 99%+ delivery rate

---

## Support

If you encounter issues:
1. Check Resend dashboard: https://resend.com/emails
2. Check backend logs (Railway/Vercel dashboard)
3. Check frontend console (browser DevTools)
4. Test manually with curl command
5. Review this guide's troubleshooting section

---

**Last Updated:** December 17, 2025
**Status:** Ready to implement
**Estimated Setup Time:** 30 minutes
**Priority:** High (blocking beta launch polish)
