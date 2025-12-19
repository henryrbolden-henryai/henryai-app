# send_welcome_email.py
# Add this endpoint to your FastAPI backend (backend.py)

import os
import requests
from fastapi import HTTPException
from pydantic import BaseModel

# Resend API Configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")  # Add to environment variables
RESEND_API_URL = "https://api.resend.com/emails"

class WelcomeEmailRequest(BaseModel):
    email: str
    name: str = None  # Optional - extract from user profile if available

# HTML template for welcome email
WELCOME_EMAIL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to HenryHQ</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', sans-serif; background-color: #0a0a0a;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0a0a0a;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #111111; border: 1px solid #222222; border-radius: 12px; padding: 48px;">
                    <tr>
                        <td align="center">
                            <!-- Minimal Ring Logo -->
                            <div style="margin-bottom: 32px;">
                                <svg width="100" height="100" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <defs>
                                        <linearGradient id="ringGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                        </linearGradient>
                                        <linearGradient id="strokeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                        </linearGradient>
                                    </defs>
                                    <circle cx="100" cy="100" r="85" stroke="url(#ringGradient)" stroke-width="4" fill="none"/>
                                    <path d="M55 130 L55 70" stroke="#667eea" stroke-width="9" stroke-linecap="round" fill="none"/>
                                    <path d="M145 130 L145 50" stroke="url(#strokeGradient)" stroke-width="9" stroke-linecap="round" fill="none"/>
                                    <path d="M55 100 L145 100" stroke="#764ba2" stroke-width="9" stroke-linecap="round" fill="none"/>
                                    <circle cx="145" cy="50" r="9" fill="#764ba2"/>
                                </svg>
                            </div>
                            
                            <!-- Main Content -->
                            <h1 style="margin: 0 0 16px; font-size: 32px; font-weight: 600; color: #ffffff; letter-spacing: -0.5px; text-align: center;">
                                You're in.
                            </h1>
                            
                            <p style="margin: 0 0 32px; font-size: 16px; line-height: 1.6; color: #9ca3af; text-align: center;">
                                Most job search tools flood you with volume. We focus on strategic positioning. Here's how it works:
                            </p>
                            
                            <!-- 3-Step Process -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 32px; background-color: #0a0a0a; border: 1px solid #222222; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 8px 20px; font-size: 15px; line-height: 1.5; color: #d1d5db; text-align: left;">
                                        <strong style="color: #ffffff;">1. Upload your resume</strong><br>
                                        We parse it, analyze your background, and identify your positioning.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 20px; font-size: 15px; line-height: 1.5; color: #d1d5db; text-align: left; border-top: 1px solid #222222;">
                                        <strong style="color: #ffffff;">2. Paste a job description</strong><br>
                                        We calculate your fit score, flag gaps, and tell you whether to apply.
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 20px; font-size: 15px; line-height: 1.5; color: #d1d5db; text-align: left; border-top: 1px solid #222222;">
                                        <strong style="color: #ffffff;">3. Get your strategy</strong><br>
                                        Tailored resume, cover letter, interview prep, and outreach guidance.
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 30px;">
                                <tr>
                                    <td align="center">
                                        <a href="https://henryhq.ai/dashboard.html" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                                            Run Your First Analysis
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Closing line -->
                            <p style="margin: 0 0 8px; font-size: 15px; line-height: 1.6; color: #9ca3af; font-style: italic; text-align: center;">
                                No fluff. No mass-apply nonsense.
                            </p>
                            <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #9ca3af; font-style: italic; text-align: center;">
                                Just honest guidance that respects your time.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="600" cellpadding="0" cellspacing="0" style="margin-top: 24px;">
                    <tr>
                        <td style="text-align: center; font-size: 13px; color: #6b7280;">
                            <p style="margin: 0 0 8px;">
                                <strong style="font-style: italic; color: #ffffff;">P.S.</strong> 
                                <span style="font-style: italic;">Have questions? Hit reply. I'm here to help.</span>
                            </p>
                            <p style="margin: 0; color: #4b5563;">
                                HenryHQ | Strategic job search intelligence
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

async def send_welcome_email(email: str, name: str = None):
    """
    Send welcome email via Resend API after user confirms their email.
    Called from Supabase webhook or frontend after confirmation.
    """
    
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY not configured")
    
    # Personalize subject line if name is provided
    subject = "You're in. Let's make your job search smarter."
    
    payload = {
        "from": "hello@henryhq.ai",
        "to": email,
        "subject": subject,
        "html": WELCOME_EMAIL_HTML
    }
    
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return {"success": True, "message": "Welcome email sent", "email_id": response.json().get("id")}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send welcome email: {str(e)}")


# Add this endpoint to your FastAPI app (backend.py)
@app.post("/api/send-welcome-email")
async def send_welcome_email_endpoint(request: WelcomeEmailRequest):
    """
    Public endpoint to trigger welcome email.
    Can be called from frontend after Supabase confirms user email.
    """
    result = await send_welcome_email(request.email, request.name)
    return result
