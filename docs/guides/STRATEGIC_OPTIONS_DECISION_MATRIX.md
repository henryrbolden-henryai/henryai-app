# STRATEGIC OPTIONS - DECISION MATRIX

## Quick Reference: When to Show What

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         URGENCY CALCULATION                              │
└─────────────────────────────────────────────────────────────────────────┘

TIMELINE (from profile)          HOLDING UP (from profile)
───────────────────────          ─────────────────────────
• urgent                         • doing_well
• soon                          • stressed_but_managing
• actively_looking              • struggling
• no_rush                       • rather_not_say


┌─────────────────────────────────────────────────────────────────────────┐
│                    URGENCY LEVEL DETERMINATION                           │
└─────────────────────────────────────────────────────────────────────────┘

DESPERATE (Red Alert - Survival Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF timeline = 'urgent'  OR  holdingUp = 'struggling'
THEN urgency = 'desperate'

↓ SHOWS:
  Icon: ⚡
  Title: "Urgent: Cash Flow Options"
  Color: Red (#ef4444)
  Focus: Contract work for immediate income
  Tone: Direct, no-judgment, survival-focused


STRESSED (Yellow Warning - Tactical Bridge)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF timeline = 'soon'  OR  holdingUp = 'stressed_but_managing'
THEN urgency = 'stressed'

↓ SHOWS:
  Icon: 🎯
  Title: "Tactical Options to Consider"
  Color: Yellow (#fbbf24)
  Focus: Contract work as strategic bridge
  Tone: Practical, supportive, strategic


STANDARD (Cyan - Leverage Building)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF timeline = 'actively_looking'  
   AND (holdingUp = 'doing_well' OR 'rather_not_say')
THEN urgency = 'standard'

↓ SHOWS:
  Icon: 💡
  Title: "Other Paths Worth Exploring"
  Color: Cyan (#22d3ee)
  Focus: Advisory, portfolio, thought leadership
  Tone: Exploratory, opportunistic, neutral


NONE (Hidden)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF timeline = 'no_rush'  AND  holdingUp = 'doing_well'
THEN urgency = 'none'

↓ SHOWS:
  Section is completely hidden
  (Zen candidates don't need tactical guidance)


┌─────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE DECISION TREE                            │
└─────────────────────────────────────────────────────────────────────────┘

timeline = 'urgent'
├─ ANY holdingUp ──────────────────────────────→ DESPERATE ⚡

timeline = 'soon'  
├─ ANY holdingUp ──────────────────────────────→ STRESSED 🎯

timeline = 'actively_looking'
├─ holdingUp = 'struggling' ───────────────────→ DESPERATE ⚡
├─ holdingUp = 'stressed_but_managing' ────────→ STRESSED 🎯
├─ holdingUp = 'doing_well' ───────────────────→ STANDARD 💡
└─ holdingUp = 'rather_not_say' ───────────────→ STANDARD 💡

timeline = 'no_rush'
├─ holdingUp = 'struggling' ───────────────────→ DESPERATE ⚡
├─ holdingUp = 'stressed_but_managing' ────────→ STRESSED 🎯
├─ holdingUp = 'doing_well' ───────────────────→ NONE (hidden)
└─ holdingUp = 'rather_not_say' ───────────────→ STANDARD 💡


┌─────────────────────────────────────────────────────────────────────────┐
│                      CONTENT VARIANT DETAILS                             │
└─────────────────────────────────────────────────────────────────────────┘

DESPERATE VARIANT
━━━━━━━━━━━━━━━━━
Message:
"You need income now, not in 3-6 months. That's real, and waiting isn't 
viable. Contract work isn't giving up on your FTE search—it's buying 
yourself time and reducing desperation energy in interviews."

Benefits:
⚡ Faster time-to-income (1-2 weeks vs. 6-8 weeks for FTE)
🛡️ Reduces desperation energy in FTE interviews
📈 Shows recent activity on resume (beats employment gaps)
💪 Builds leverage: "I'm consulting but open to the right FTE role"

Primary CTA: "Show Contract Options"
Secondary CTA: "Not Right Now"


STRESSED VARIANT
━━━━━━━━━━━━━━━━
Message:
"A tight timeline means you need to expand your opportunity set 
strategically. Contract work can serve as a bridge while you find the 
right FTE role. It also reduces the pressure that shows up in interviews."

Benefits:
⏱️ Faster interview-to-start timeline than most FTE roles
🎯 Keeps you in the market while being selective about FTE
📊 Recent work on resume signals you're in-demand
🤝 Network expansion through contract engagements

Primary CTA: "Explore Options"
Secondary CTA: "Dismiss"


STANDARD VARIANT
━━━━━━━━━━━━━━━━
Message:
"You've got solid runway. Beyond your core search, here are some options 
to build leverage and expand your network."

Benefits:
🎯 Advisory/consulting work builds credibility and leverage
🌐 Industry networking groups and communities
📚 Portfolio/side projects to strengthen positioning
🎤 Speaking/writing to establish thought leadership

Primary CTA: "Learn More"
Secondary CTA: "Not Interested"


┌─────────────────────────────────────────────────────────────────────────┐
│                         USER FLOW DIAGRAM                                │
└─────────────────────────────────────────────────────────────────────────┘

User completes onboarding
         ↓
   Saves profile with
   timeline + holdingUp
         ↓
   Navigates to dashboard
         ↓
  renderDashboard() runs
         ↓
 renderStrategicOptions() called
         ↓
   Check: dismissed?
    ↙           ↘
  YES            NO
   ↓             ↓
 Hide       Check: profile exists?
 section     ↙           ↘
           YES            NO
            ↓             ↓
     calculateUrgency()  Hide section
            ↓
     Check urgency level
      ↙    ↓    ↓    ↘
 desperate stressed standard none
      ↓      ↓      ↓      ↓
   Show    Show   Show   Hide
    red   yellow  cyan  section
      ↓      ↓      ↓
   User clicks primary CTA
            ↓
   showContractGuidanceModal()
            ↓
   Modal appears with resources
            ↓
   User clicks "Close" or overlay
            ↓
   Modal disappears


┌─────────────────────────────────────────────────────────────────────────┐
│                      IMPLEMENTATION CHECKLIST                            │
└─────────────────────────────────────────────────────────────────────────┘

□ Add HTML section to dashboard.html (between Reality Check and Pipeline)
□ Add CSS styles to <style> block
□ Add JavaScript functions to <script> block
□ Add renderStrategicOptions() call to renderDashboard()
□ Verify profile.situation structure exists
□ Test desperate variant (timeline='urgent')
□ Test stressed variant (timeline='soon')
□ Test standard variant (timeline='actively_looking', holdingUp='doing_well')
□ Test hidden state (timeline='no_rush', holdingUp='doing_well')
□ Test dismissal persistence
□ Test modal opening/closing
□ Test responsive design on mobile
□ Verify no console errors
□ Verify styling doesn't conflict with existing sections


┌─────────────────────────────────────────────────────────────────────────┐
│                     TESTING PROFILE COMBINATIONS                         │
└─────────────────────────────────────────────────────────────────────────┘

Test these profile combinations in localStorage:

1. DESPERATE - Urgent Timeline
   { situation: { timeline: 'urgent', holdingUp: 'doing_well' } }
   Expected: Red variant, survival messaging

2. DESPERATE - Struggling Emotionally
   { situation: { timeline: 'actively_looking', holdingUp: 'struggling' } }
   Expected: Red variant, survival messaging

3. STRESSED - Soon Timeline
   { situation: { timeline: 'soon', holdingUp: 'doing_well' } }
   Expected: Yellow variant, tactical messaging

4. STRESSED - Stressed Emotionally
   { situation: { timeline: 'actively_looking', holdingUp: 'stressed_but_managing' } }
   Expected: Yellow variant, tactical messaging

5. STANDARD - Good State
   { situation: { timeline: 'actively_looking', holdingUp: 'doing_well' } }
   Expected: Cyan variant, leverage messaging

6. HIDDEN - Zen State
   { situation: { timeline: 'no_rush', holdingUp: 'doing_well' } }
   Expected: Section completely hidden

7. EDGE CASE - No Profile
   localStorage.removeItem('candidateProfile')
   Expected: Section hidden gracefully, no errors

8. EDGE CASE - Empty Values
   { situation: { timeline: '', holdingUp: '' } }
   Expected: Defaults to standard variant


┌─────────────────────────────────────────────────────────────────────────┐
│                         ANALYTICS TRACKING                               │
└─────────────────────────────────────────────────────────────────────────┘

Events to track (if analytics enabled):

strategic_options_viewed
  Properties: { urgency_level, timeline, holdingUp }

strategic_options_clicked
  Properties: { urgency_level, guidance_type }

strategic_options_dismissed
  Properties: { urgency_level }

contract_modal_opened
  Properties: { urgency_level }

contract_resource_clicked
  Properties: { platform, urgency_level }
