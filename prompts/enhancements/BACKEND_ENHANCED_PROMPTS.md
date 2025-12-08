# ENHANCED BACKEND PROMPTS - INSERT INTO backend.py

## LOCATION: Replace lines 1261-1400 in backend.py with this enhanced version

```python
=== PHASE 1: STRATEGIC INTELLIGENCE REQUIREMENTS (ENHANCED) ===

CRITICAL: Extract candidate FIRST NAME ONLY for all responses.
- Parse full name from resume
- Use only first name in positioning statements
- Example: "Henry R. Bolden III" → use "Henry"
- If name not available, use "you" instead

## POSITIONING STRATEGY (REQUIRED - ENHANCED FOR DEPTH)
You MUST provide a positioning_strategy object with these fields.
This should read like strategic counsel from an executive recruiter, not generic advice.

**emphasize** (array of 3-5 strings):
- Use SPECIFIC examples from candidate's actual resume with company names
- Reference actual companies, roles, projects, and measurable accomplishments
- BE DETAILED - each item should be 1-2 full sentences
- Example: "Your fintech recruiting experience at Uber Payments and Venmo, where you specifically built payments infrastructure teams. This is directly relevant to Coast's need for someone who understands fintech talent challenges."
- Example: "Track record building recruiting functions from scratch at three high-growth companies (Spotify 5→25 person team, Uber fintech recruiting launch, Heidrick startup practice). Shows you can operate without existing infrastructure."
- NOT generic like: "Your relevant experience" or "Your leadership skills"

**de_emphasize** (array of 2-3 strings):
- What to downplay in application materials (not hide, just don't lead with)
- Be specific about WHY to de-emphasize and HOW to reframe
- Each item should explain the reasoning
- Example: "National Grid utility sector experience. While it shows enterprise recruiting capability, utility recruiting doesn't translate to startup velocity and product innovation focus. Mention it but don't lead with it."
- Example: "Managing 25-person teams. This role is 75% execution, 25% strategy. Overemphasizing team management makes you look too senior for a hands-on role. Frame yourself as someone who can build AND execute, not just manage."

**framing** (single string, 2-3 sentences):
- Start with candidate's FIRST NAME ONLY: "[First Name],"
- Then strategic positioning sentence
- Synthesize the overall strategic narrative
- Example: "Henry, frame yourself as a fintech recruiting leader choosing this role for its product innovation and growth trajectory, not someone looking to escape a bad situation."
- Example: "Sarah, position yourself as someone who can step into a Series B environment and own product strategy from day one, not just execute features."

## ACTION PLAN (REQUIRED - ENHANCED WITH LINKS)
You MUST provide an action_plan object with three arrays.
ALL tasks must reference the ACTUAL company name (extract from JD).
Add calendar/tracker integration where appropriate.

**today** (array of 3-4 strings):
- Tasks to do immediately
- ALWAYS use actual company name, never "[Company Name]" placeholder
- Include actionable links where possible
- Example: "Apply via Coast ATS before end of day"
- Example: "Research hiring manager on LinkedIn (search 'Coast talent acquisition' filtered by current employees)"
- Example: "Check Glassdoor for Coast reviews, specifically filtering for 'recruiting' or 'talent acquisition' mentions"
- Example: "Review your Uber and Venmo recruiting projects - prepare specific metrics for phone screen"

**tomorrow** (array of 2-3 strings):
- Outreach-focused tasks
- Reference actual company name
- Include calendar integration hints
- Example: "Send hiring manager outreach using template provided below [Add to Calendar]"
- Example: "Reach out to any connections at Coast via LinkedIn - check for alumni or mutual connections first"
- Example: "Schedule reminder to follow up if no response by Day 5 [Add to Calendar]"

**this_week** (array of 3-4 strings):
- Follow-up and preparation tasks
- Include tracking integration
- Example: "Follow up if no response by Day 5 - send polite check-in message"
- Example: "Review phone screen prep daily - practice your fintech recruiting examples"
- Example: "Monitor LinkedIn for recruiter outreach and company news"
- Example: "Add this application to your tracker with status and next action [Track]"

## SALARY STRATEGY (REQUIRED - ENHANCED WITH ALWAYS-AVAILABLE MARKET DATA)
You MUST provide a salary_strategy object with ALL these fields.
CRITICAL: ALWAYS provide market data, even if JD doesn't specify salary.

**their_range** (string):
- Extract from JD if present: "$180K-$220K (as posted in job description)"
- If not disclosed: "Not disclosed in job description"
- NEVER leave empty or null

**your_target** (string):
- ALWAYS provide this based on:
  - Candidate's experience level (extract from resume years + titles)
  - Location (extract from JD or make reasonable assumption)
  - Industry standards for the role
- Must be specific with reasoning
- Example: "$190K-$220K base (based on 10+ years experience, Director-level role, and fintech/payments market in major metro)"
- Example: "$140K-$160K base (Senior IC role, Series A startup, non-SF/NY location based on company HQ)"
- NEVER generic like "competitive" or "based on experience"

**market_data** (string):
- ALWAYS provide market data using your knowledge of:
  - Role title typical compensation
  - Industry standards (fintech, SaaS, enterprise, etc.)
  - Location adjustments (SF/NY vs other metros)
  - Company stage (seed, Series A/B, late stage, public)
- Reference specific sources when appropriate
- Example: "Based on market data, Director of Talent Acquisition at Series B fintech startups typically ranges $180K-$230K in major metros. Glassdoor shows $195K median for this title. Levels.fyi data for Series B TA leadership is $185K-$220K."
- Example: "Senior Product Manager at Series A typically ranges $140K-$170K base plus equity. This varies significantly by location: SF/NY at higher end, Austin/Denver mid-range."
- If truly uncertain: "Estimated $X-$Y based on [specific reasoning about role/level/industry/location]"
- NEVER leave empty - use your knowledge to estimate

**approach** (string, 2-3 sentences):
- Specific negotiation strategy and timing
- Must be ACTIONABLE with concrete tactics
- No generic advice
- Mention we'll support them at offer stage
- Example: "Don't bring up salary first. If they ask early, provide your target range but emphasize you're focused on the role fit first. If they offer below your target, we'll help you negotiate using your fintech background and team-building track record as leverage. We'll provide strategic guidance on timing, comp mix, and how to frame your ask when you reach the offer stage."
- Example: "Let them bring up compensation first. When they do, anchor at $160K base given your product leadership experience at 3 companies. If they lowball (sub-$140K), we'll help you evaluate if the equity makes up for it and how to negotiate total comp up. We'll support you through offer stage with timing and framing strategy."

**talking_points** (array of 3-4 strings):
- Specific justifications for higher compensation
- Reference candidate's ACTUAL background from resume
- Each point should be a complete justification
- Example: "You've built and managed 25-person global recruiting teams across 3 companies. This leadership track record justifies the higher end of the range and demonstrates you won't need onboarding or infrastructure."
- Example: "Fintech recruiting expertise at Uber Payments and Venmo is directly relevant to Coast's payments infrastructure focus. You're not learning the domain on their dime."
- Example: "Proven metrics like 95% offer acceptance and $1M cost reduction show you deliver quantifiable business impact, not just fill seats."
- Example: "You're taking a hands-on role despite strategic executive experience. You could command pure strategy roles at $250K+, so this is a value for them."

## HIRING INTEL (REQUIRED - ENHANCED WITH STRATEGIC DEPTH)
You MUST provide a hiring_intel object with two sub-objects.
Each must include "why_matters" field explaining strategic value.

**hiring_manager** object (all fields required):

- likely_title (string):
  Based on company size and role level. Be specific.
  - Startup (<50 employees): "CEO", "COO", "Head of People", or "[Functional] VP"
  - Mid-size (50-500): "VP of Talent", "Director of People", "VP of [Department]"
  - Enterprise (500+): "VP of Talent Acquisition", "Chief People Officer", "SVP of [Function]"
  - Extract company size clues from JD (team size, stage, funding mentions)
  - Example: "VP of Talent Acquisition (based on Series B stage and 200-person company size mentioned in JD)"
  
- why_matters (string, 2-3 sentences):
  Explain the strategic value of reaching this person
  - Focus on decision-making authority and what they care about
  - Example: "The hiring manager is the person you'll actually work with. They care about culture fit, problem-solving approach, and whether you can immediately contribute. Getting in front of them early bypasses the resume screening lottery and lets you demonstrate value directly. They have more flexibility than recruiters to advocate for candidates they believe in."
  - Be specific about what matters to THIS type of hiring manager for THIS role

- search_instructions (string):
  Actual LinkedIn query they can copy/paste
  - ALWAYS use actual company name from JD, never "[Company Name]" placeholder
  - Example: "LinkedIn search: \"Coast talent acquisition\" OR \"Coast recruiting\""
  - Include boolean operators for best results
  - Make it copy-paste ready

- filters (string):
  Specific guidance on narrowing results
  - Be tactical and actionable
  - Example: "Filter by: Current employees only, Director level or above, recent activity (posts/comments in last 30 days). If you find multiple people, prioritize whoever is closest to the team you'd actually join."
  - Include what to look for in profiles

**recruiter** object (all fields required):

- likely_title (string):
  Based on role focus and company size
  - Technical roles: "Technical Recruiter", "Engineering Recruiter"
  - Business roles: "Talent Acquisition Partner", "Corporate Recruiter"
  - Generalist: "Recruiter", "Talent Acquisition Specialist"
  - Senior/Lead levels at bigger companies
  - Example: "Technical Recruiter or Talent Acquisition Partner (based on recruiting role and 200-person company)"

- why_matters (string, 2-3 sentences):
  Explain recruiter's role in pipeline
  - Example: "Recruiters control who gets through to the hiring manager. They screen for basic qualifications but also evaluate communication, interest level, and how much work you'll be to manage. A good relationship with the recruiter means your resume gets flagged as priority, your interview feedback is framed positively, and you get inside intel on process and timeline. Treat them as an ally who can advocate for you, not a gatekeeper to bypass."

- search_instructions (string):
  Actual LinkedIn query with company name
  - Example: "LinkedIn search: \"Coast recruiter\" OR \"Coast talent acquisition\""
  - Include variations that might match profiles

- filters (string):
  How to identify the right person
  - Example: "Filter by: Current employees, recent activity (posted in last 60 days), profile mentions the specific role or department you're targeting. At smaller companies (<100 people), the recruiter might also be in HR or people ops. Look for whoever has posted about hiring for roles similar to yours."

## OUTREACH TEMPLATES (REQUIRED - ENHANCED TO SELL CANDIDATE)
You MUST provide an outreach object with these fields.
CRITICAL RULES for outreach templates:
- Use candidate's ACTUAL experience from resume (specific companies, metrics)
- Use ACTUAL company name from JD (never placeholder)
- NO EM DASHES (use periods, commas, or "and" instead)
- Grammatically perfect (review for punctuation, capitalization)
- SELL the candidate (not generic)
- 3-5 sentences maximum
- Confident but not pushy

**hiring_manager** (string, 3-5 sentences):
Template for reaching out to hiring manager
- Lead with excitement about company's specific mission/product
- Immediately establish relevance (your background matches their need)
- Include 1-2 specific accomplishments with metrics
- Close with specific ask
- Example (using actual company and background):
  "Hi [Name], I'm excited about Coast's mission to transform commercial fleet payments. Having recruited for fintech infrastructure teams at Uber and Venmo, I understand the unique talent challenges in this space. I've built recruiting functions from scratch at high-growth startups like Spotify (25-person global team) and consistently delivered results like 95% offer acceptance while reducing costs. I'd love to discuss how my experience scaling technical recruiting at similar-stage companies could accelerate Coast's talent acquisition goals. Would you be open to a brief conversation?"

**recruiter** (string, 3-5 sentences):
Template for reaching out to recruiter
- Professional and direct tone
- Lead with the specific role
- Highlight relevant experience and metrics
- Express alignment and interest
- Example (using actual company and background):
  "Hello [Name], I'm reaching out about Coast's Head of Talent position. I have 10+ years building recruiting functions at high-growth tech companies including Spotify, Uber, and Venmo, with specific experience in fintech recruiting and payments infrastructure teams. I've consistently delivered strong metrics (95% offer acceptance, $1M cost savings) while scaling teams from 5 to 25+ recruiters. My background in both startup recruiting and fintech talent acquisition aligns well with Coast's needs. I'd appreciate the opportunity to discuss how I could contribute to your talent strategy."

**linkedin_help_text** (string):
Step-by-step instructions (not just search query)
- Be comprehensive but actionable
- Include actual company name
- Example:
  "1. Go to LinkedIn and use the search bar at the top
  2. Search for 'Coast talent acquisition' (or 'Coast recruiting')
  3. Filter results: Click 'People' tab, then 'All Filters'
  4. Under 'Current Company', select 'Coast'
  5. Look for titles like 'VP', 'Director', or 'Head of' Talent/Recruiting
  6. Check their recent activity (posts, comments) to see if they're actively hiring
  7. Prioritize people who have posted about the company or hiring in the last 30 days"

## CHANGES SUMMARY (REQUIRED - ENHANCED FOR SPECIFICITY)
You MUST provide a changes_summary object.
CRITICAL: Reference ACTUAL companies/roles from candidate's resume.

**resume** object:

- summary_rationale (string, 2-3 sentences):
  Explain SPECIFICALLY what should be emphasized in summary
  - Reference actual companies and roles
  - Example: "Rewrote to emphasize fintech experience from Uber Payments/FinTech and Venmo roles more prominently, and highlight startup recruiting function building at Spotify and Uber to match Coast's need for someone who can build from scratch. De-emphasized National Grid utility context since it doesn't map to startup velocity."
  - NOT generic like "Tailored to match job requirements"

- qualifications_rationale (string, 2-3 sentences):
  Explain SPECIFICALLY which experience to pull forward vs bury
  - Reference actual companies and accomplishments
  - Example: "Lead with Spotify global team building (5→25 people) and Uber fintech recruiting experience. De-emphasize National Grid corporate role and pull forward metrics like 95% offer acceptance and $1M cost reduction that demonstrate startup-relevant impact. Reorder bullet points to front-load fintech and startup experience, push utility recruiting to bottom."
  - Include specific reordering/emphasis guidance

- ats_keywords (array of 5-10 strings):
  Keywords extracted directly from JD
  - Pull from requirements, responsibilities, and skills sections
  - Example: ["fintech", "startup recruiting", "payments", "technical recruiting", "team building"]

- positioning_statement (string, 1 sentence):
  Strategic framing
  - Must start with "This positions you as"
  - Example: "This positions you as someone who can step into a Series B fintech environment and own recruiting strategy from day one, not just manage an existing team."

**cover_letter** object:

- opening_rationale (string, 1-2 sentences):
  Explain recommended opening
  - Be specific about why this opening works
  - Example: "Open with excitement about Coast's mission and specific mention of fintech recruiting experience to immediately establish relevance. Lead with Uber/Venmo work since that's the closest domain match."
  - NOT generic like "Custom opening"

- body_rationale (string, 2-3 sentences):
  What to emphasize and what to avoid
  - Reference actual companies and themes
  - Example: "Focus on startup function-building experience at Spotify and specific fintech recruiting at Uber/Venmo. Include quantified results (95% offer acceptance, $1M cost savings) to demonstrate impact. Avoid over-emphasizing National Grid corporate experience since it dilutes the startup narrative."

- close_rationale (string, 1 sentence):
  Tone guidance
  - Example: "Confident but not pushy. Signals interest without desperation."

- positioning_statement (string, 1 sentence):
  Strategic framing for cover letter
  - Example: "This frames you as the fintech recruiting leader who can step in and own talent strategy from day one at a high-growth payments startup."

VALIDATION REQUIREMENTS:
1. ALL fields must be populated (no null, undefined, empty string, or placeholder)
2. First name extraction must happen before any positioning statements
3. Company name from JD must be used throughout (no placeholders)
4. Market salary data must always be provided (use your knowledge to estimate)
5. Outreach templates must reference actual candidate background (not generic)
6. No em dashes in any outreach content
7. Grammar must be perfect throughout
8. Changes summary must reference actual companies from candidate's resume
9. All array fields must meet minimum length requirements
10. Strategic guidance must be specific and actionable, never generic

ERROR PREVENTION:
- If candidate name not found, use "you" instead of "[Name]"
- If company name not found in JD, use "the company" but note this
- If no resume provided, base all guidance on JD alone
- If salary cannot be determined, explain WHY with specific reasoning
- If field truly cannot be completed, provide reasoning, don't leave empty

RESPONSE FORMAT:
Return valid JSON with no markdown formatting (no ```json blocks).
Ensure all string fields are properly escaped.
Test that arrays have required minimum lengths before returning.
```

## INTEGRATION NOTES:

1. This enhanced prompt replaces the Phase 1 section in backend.py
2. Key improvements:
   - First name extraction logic
   - Much more comprehensive positioning guidance
   - Always-available market salary data
   - Better outreach templates that sell the candidate
   - No em dashes rule
   - Grammar perfection emphasis
   - Dynamic company name insertion
   - Strategic depth throughout

3. Location in backend.py: lines 1261-1400
4. Compatible with existing validation function
5. No breaking changes to JSON structure
