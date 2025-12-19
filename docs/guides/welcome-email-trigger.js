// welcome-email-trigger.js
// Add this to your Supabase authentication flow (likely in login.html or signup flow)

/**
 * Frontend approach: Trigger welcome email after Supabase email confirmation
 * 
 * IMPLEMENTATION OPTIONS:
 * 
 * Option 1: Listen for auth state change (RECOMMENDED)
 * Option 2: Call after signup with delay
 * Option 3: Supabase Edge Function webhook
 */

// =============================================================================
// OPTION 1: Auth State Change Listener (RECOMMENDED)
// =============================================================================
// Add this to your main authentication handler

import { supabase } from './supabase-client.js';

// Listen for auth state changes
supabase.auth.onAuthStateChange(async (event, session) => {
    console.log('Auth event:', event);
    
    // When user confirms their email, trigger welcome email
    if (event === 'SIGNED_IN' && session?.user) {
        const user = session.user;
        
        // Check if this is first sign-in (email just confirmed)
        const isFirstSignIn = checkIfFirstSignIn(user);
        
        if (isFirstSignIn) {
            console.log('First sign-in detected, sending welcome email...');
            await sendWelcomeEmail(user.email, user.user_metadata?.name);
        }
    }
});

function checkIfFirstSignIn(user) {
    // Method 1: Check if profile exists in database
    // If no profile = first time
    const profileExists = localStorage.getItem('profile_created');
    return !profileExists;
    
    // Method 2: Check user metadata
    // return !user.user_metadata?.welcome_email_sent;
}

async function sendWelcomeEmail(email, name = null) {
    try {
        // Call your backend endpoint
        const response = await fetch('https://your-backend-url.com/api/send-welcome-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                name: name
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send welcome email');
        }
        
        const result = await response.json();
        console.log('Welcome email sent:', result);
        
        // Mark as sent to prevent duplicate sends
        localStorage.setItem('welcome_email_sent', 'true');
        
        return result;
    } catch (error) {
        console.error('Error sending welcome email:', error);
        // Don't block user flow if email fails
    }
}

// =============================================================================
// OPTION 2: Direct Call After Signup (Simple but less reliable)
// =============================================================================
// Add this to your signup handler

async function handleSignup(email, password) {
    try {
        // 1. Sign up user with Supabase
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
        });
        
        if (error) throw error;
        
        // 2. Show confirmation message
        showMessage('Check your email to confirm your account!');
        
        // 3. Wait for email confirmation (polling approach)
        // Note: This is less reliable than Option 1
        setTimeout(async () => {
            // Check if user confirmed email
            const { data: { session } } = await supabase.auth.getSession();
            
            if (session?.user?.email_confirmed_at) {
                // User confirmed! Send welcome email
                await sendWelcomeEmail(session.user.email);
            }
        }, 60000); // Check after 1 minute
        
    } catch (error) {
        console.error('Signup error:', error);
    }
}

// =============================================================================
// OPTION 3: Supabase Edge Function (Most Robust - Requires Supabase Setup)
// =============================================================================
/**
 * Create a Supabase Edge Function that listens for auth.users INSERT events
 * This runs server-side and is the most reliable approach
 * 
 * Setup:
 * 1. Create edge function: supabase functions new send-welcome-email
 * 2. Add this code to the function
 * 3. Deploy: supabase functions deploy send-welcome-email
 * 4. Create database webhook to trigger function on auth.users INSERT
 */

// Edge Function Code (Deno/TypeScript):
/*
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  try {
    const { record } = await req.json();
    
    // Only send welcome email when email is confirmed
    if (record.email_confirmed_at) {
      const resendResponse = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: "hello@henryhq.ai",
          to: record.email,
          subject: "You're in. Let's make your job search smarter.",
          html: WELCOME_EMAIL_HTML, // Import from separate file
        }),
      });
      
      const result = await resendResponse.json();
      console.log("Welcome email sent:", result);
    }
    
    return new Response(JSON.stringify({ success: true }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
*/

// =============================================================================
// IMPLEMENTATION RECOMMENDATION
// =============================================================================

/**
 * RECOMMENDED APPROACH:
 * 
 * Start with Option 1 (Auth State Change Listener) because:
 * - Works immediately without server-side setup
 * - Reliable for most use cases
 * - Easy to debug and test
 * - Can migrate to Option 3 later if needed
 * 
 * SETUP STEPS:
 * 1. Add the auth state change listener to your main auth handler
 * 2. Add the backend endpoint from send_welcome_email.py to your FastAPI app
 * 3. Set RESEND_API_KEY environment variable in your backend
 * 4. Test by creating a new account and confirming email
 * 5. Check Resend dashboard to verify email was sent
 * 
 * TESTING:
 * - Create test account with real email
 * - Confirm email via link
 * - Check console logs for "Welcome email sent"
 * - Check inbox for welcome email
 * - Verify mail-tester.com score (should be 9-10/10)
 */

// =============================================================================
// EXAMPLE INTEGRATION WITH EXISTING AUTH FLOW
// =============================================================================

// If your existing signup flow looks like this:
async function existingSignupFlow() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const { data, error } = await supabase.auth.signUp({
        email: email,
        password: password,
    });
    
    if (error) {
        showError(error.message);
        return;
    }
    
    showMessage('Check your email to confirm your account!');
}

// Just add the auth state listener once at app initialization:
document.addEventListener('DOMContentLoaded', () => {
    // Add auth state listener
    supabase.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
            const isFirstSignIn = !localStorage.getItem('welcome_email_sent');
            
            if (isFirstSignIn) {
                await sendWelcomeEmail(session.user.email);
                localStorage.setItem('welcome_email_sent', 'true');
            }
        }
    });
});
