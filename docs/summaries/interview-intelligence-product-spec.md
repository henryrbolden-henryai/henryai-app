# Interview Intelligence — Product Spec

**Version:** 1.0  
**Date:** December 2024  
**Owner:** Henry  
**Purpose:** Strategic reference document for Interview Intelligence feature

---

## **Product Overview**

Interview Intelligence is the strategic coaching layer of HenryAI. It prepares candidates for interviews, helps them practice, and provides post-interview analysis to drive continuous improvement. This is where HenryAI acts as a trusted recruiter—not just generating documents, but actively coaching candidates through the interview process.

### **Core Philosophy**

- **Progressive Disclosure**: Don't overwhelm candidates. Generate prep only for the stage they're at.
- **Learning Loop**: Every interview makes the next one better through structured reflection.
- **Real Practice**: Force candidates to rehearse out loud, not just read prep materials.
- **Zero Fabrication**: All STAR examples, achievements, and talking points must come from the candidate's actual resume.

### **Target Stages (Phase 1)**

1. **Recruiter Screen**: Gatekeeping conversation. Goal: Advance to hiring manager.
2. **Hiring Manager Interview**: The real interview. Goal: Prove competency and fit.

### **Future Stages (Phase 2+)**

3. Panel/Peer Interviews
4. Executive/Final Round
5. Salary Negotiation (post-offer only)

---

## **User Flows**

### **Flow 1: Pre-Interview Prep**

**Trigger**: Candidate applies to a role and wants to prep for recruiter screen

**Experience**:
1. Candidate clicks "Prep for Recruiter Screen"
2. HenryAI generates stage-specific intelligence:
   - What this interview is about (2-3 sentences)
   - Key talking points (4-6 bullets)
   - Red flag mitigation (2-3 bullets)
   - Likely questions (5-7 questions)
   - Questions to ask (3-4 strategic questions)
   - Compensation strategy (1-2 sentences)
   - Timeline expectations (1 sentence)
3. Candidate reviews prep, saves it, can reference before interview

**Backend**: `POST /api/interview-prep/generate`

---

### **Flow 2: Practice Mode (60-90 Second Intro Sell)**

**Trigger**: Candidate clicks "Practice Intro Sell"

**Experience**:
1. HenryAI generates a customized template based on candidate's resume
2. Candidate types or records their version
3. HenryAI provides structured feedback:
   - Content score (1-10)
   - Structure score (1-10)
   - Tone score (1-10)
   - Delivery score (1-10, if audio)
   - Pace score (1-10, if audio)
   - Specific coaching points
   - Revised/tightened version
4. Candidate iterates until satisfied
5. Final version saved to profile for future reference

**Backend**: 
- `POST /api/interview-prep/intro-sell/generate` (template)
- `POST /api/interview-prep/intro-sell/feedback` (analysis)

---

### **Flow 3: Conversational Practice**

**Trigger**: Candidate clicks "Practice Mode" or asks to practice specific questions

**Experience**:
1. Chat interface opens
2. Candidate asks to practice a specific question (e.g., "Tell me about a time you failed")
3. HenryAI provides framework + example based on their resume
4. Candidate drafts answer
5. HenryAI provides feedback (content, structure, tone)
6. Candidate iterates
7. Session tracked (questions practiced, scores, readiness)

**Backend**: `POST /api/interview-prep/practice` (conversational endpoint)

---

### **Flow 4: Post-Interview Debrief**

**Trigger**: Candidate uploads transcript or clicks "Debrief Interview"

**Experience (Transcript Upload)**:
1. Candidate uploads .txt, .docx, or .pdf transcript
2. HenryAI analyzes:
   - Questions asked
   - Answers given
   - Moments that landed vs. didn't land
3. HenryAI provides structured feedback:
   - Overall score (1-10)
   - Dimension scores (content, clarity, delivery, tone, structure, confidence)
   - Strengths (2-3 bullets)
   - Opportunities (2-3 bullets)
   - What they should have said (rewritten answers)
   - Coaching points (3 bullets)
   - Action items (3 bullets)
4. HenryAI drafts thank-you email tailored to interview content
5. Debrief saved to history

**Experience (Typed Debrief)**:
1. Candidate clicks "Type Debrief"
2. HenryAI asks guided prompts:
   - "On a scale of 1-10, how do you think it went?"
   - "What questions were you asked?"
   - "Which answers felt strong? Which felt weak?"
   - "What did you learn about the company?"
3. HenryAI synthesizes into structured feedback (same as transcript flow)
4. Thank-you email generated
5. Debrief saved to history

**Backend**: 
- `POST /api/interview-prep/debrief` (transcript or typed)
- `POST /api/interview-prep/thank-you-email` (generate email)

---

## **Key Design Principles**

### **1. Always Use Real Information**
- STAR examples must come from actual resume projects
- Talking points must reference real achievements
- Quantified metrics must be verifiable from resume
- Never invent experience, companies, or metrics

### **2. Progressive Disclosure**
- Don't generate hiring manager prep until they pass recruiter screen
- Don't generate panel prep until they pass hiring manager
- Each stage unlocks the next

### **3. Conversational Coaching**
- Don't dump walls of text
- Guide candidates through prep like a human coach would
- Provide frameworks, then ask them to apply
- Iterate based on their responses

### **4. Structured Reflection**
- Force candidates to debrief after every interview
- Track improvement over time
- Use insights from one interview to adjust strategy for next

### **5. Honest Market Intelligence**
- Call out red flags (job hopping, overqualification, gaps)
- Provide mitigation strategies, not sugarcoating
- Be direct about what works and what doesn't

---

## **Content Guidelines**

### **Tone & Voice**
- Direct, strategic, conversational
- Like a senior recruiter coaching a candidate
- No cheerleading, no false optimism
- Honest assessment with actionable guidance

### **What to Emphasize**
- Quantified achievements from resume
- Specific examples that map to job requirements
- Skills/experiences that differentiate candidate
- Strategic positioning (why this role, why now)

### **What to Avoid**
- Generic advice ("Be yourself," "Show enthusiasm")
- Invented examples or fabricated metrics
- Buzzwords without substance ("passionate," "team player")
- Overly long explanations (keep it tight)

---

## **Success Metrics**

### **Engagement Metrics**
- % of candidates who use prep before interviews
- # of practice sessions per candidate
- # of debrief submissions per candidate
- Time spent in practice mode

### **Quality Metrics**
- Average interview debrief score over time (are they improving?)
- % of candidates who advance from recruiter screen to hiring manager
- % of candidates who receive offers after using interview prep

### **Feature Adoption**
- % of candidates who practice intro sell
- % of candidates who upload transcripts vs. type debriefs
- % of candidates who send thank-you emails

---

## **Technical Architecture Notes**

### **Data Flow**
1. **Input**: Candidate resume + Job description + Fit analysis
2. **Processing**: Claude API generates stage-specific prep using structured prompts
3. **Storage**: Interview prep, practice sessions, debriefs stored in database
4. **Output**: Structured JSON responses formatted for frontend consumption

### **Key Dependencies**
- Existing `job_applications` table (links to specific application)
- Existing `candidate_resumes` table (source of truth for background)
- Existing `fit_analysis` table (used to generate targeted prep)
- Claude API (for prompt execution)

### **State Management**
- Track interview stage progression (applied → recruiter screen → hiring manager → panel)
- Store practice attempt history (questions practiced, scores, iterations)
- Maintain debrief history (all interviews, scores over time)

---

## **Detailed Content Examples**

### **Example: Recruiter Screen Prep Output**

**What This Interview Is About:**
The recruiter's job is simple: make sure you're not wasting the hiring manager's time. They're checking three things—can you do the job (resume match), are you in the right salary range, and can you communicate clearly. Pass this, and you get to the real interview.

**Key Talking Points:**
- Lead with your Spotify monetization work—18% conversion lift, $12M revenue. That's your proof you can execute at scale.
- Emphasize cross-functional leadership. This role requires managing eng, design, and data teams—you've done that at two companies.
- Highlight B2B experience from Uber. They're scaling a B2B product, and most PMs don't have that background.
- Be ready to explain why you're leaving Spotify. Don't badmouth—frame it as seeking [specific thing this role offers].

**Red Flag Mitigation:**
- **Job hopping concern**: You've had 3 roles in 5 years. Frame it as strategic career progression (utility → consumer → B2B SaaS), not restlessness.
- **Overqualification**: You're senior for this mid-level role. Address it upfront: "I'm looking for the right fit, not just a title bump. This role aligns with where I want to take my career."

**Questions They'll Ask:**
1. "Walk me through your background." (Use your 60-90 second intro sell)
2. "Why are you interested in this role?"
3. "Why are you leaving Spotify?"
4. "What are your salary expectations?"
5. "Tell me about a time you managed a cross-functional project."
6. "When could you start if we moved forward?"
7. "Do you have any questions for me?"

**Questions You Should Ask:**
- "What's the biggest challenge this team is facing right now?" (Shows strategic thinking)
- "What does success look like in the first 90 days?" (Shows execution focus)
- "How is the product team structured? Who would I be working with most closely?" (Shows collaboration awareness)
- "What's the timeline for next steps?" (Shows interest without desperation)

**Compensation Discussion Strategy:**
If they ask about salary expectations, anchor high but reasonable: "Based on my research and experience, I'm targeting $[X]-$[Y] depending on total comp structure. Is that in range for this role?" Don't go first if you can avoid it—ask what the budget is.

**Timeline Expectations:**
If they ask when you can start, say: "I'd need to give [2-4 weeks] notice, but I'm motivated to move quickly for the right opportunity." Don't say you can start tomorrow—it signals desperation.

---

### **Example: Hiring Manager Prep Output**

**What This Interview Is About:**
This is where you prove you can do the job. The hiring manager has a problem—they need someone who can step in and own product strategy for a scaling B2B SaaS product. Your job is to show them you've done this before, you understand their challenges, and you can execute from day one.

**Strengths to Emphasize:**
- **B2B Product Experience**: Most consumer PMs don't have this. Your Uber fleet management work is directly applicable. Emphasize the 5,000 commercial accounts and the complexity of B2B stakeholder management.
- **Revenue Impact**: You've shipped features that drove $12M in incremental revenue at Spotify. That's not just execution—that's business impact. Make sure this comes up early.
- **Cross-Functional Leadership**: You've led eng, design, data, and marketing teams. This role requires the same. Be ready with specific examples of how you aligned stakeholders.
- **Data-Driven Decision Making**: Both Spotify and Uber required rigorous A/B testing and metrics-driven prioritization. That's table stakes for this role.

**Gaps to Mitigate:**
- **Limited Enterprise Experience**: Your Uber work was SMB/mid-market. They're targeting enterprise. Mitigation: Emphasize transferable skills (stakeholder complexity, longer sales cycles, multi-user workflows). Acknowledge the gap but show you've researched their enterprise motion.
- **Series B Stage Experience**: You've worked at post-IPO companies. They're Series B. Mitigation: Frame it as a feature, not a bug. "I've seen what good looks like at scale. I can help you avoid common pitfalls and build for where you're going, not just where you are."

**STAR Examples (Prepare These):**

**1. Cross-Functional Leadership**
- **Situation**: At Spotify, we needed to launch a new Premium pricing tier in 6 months to hit Q3 revenue targets.
- **Task**: I was responsible for coordinating eng, design, marketing, and finance to ship on time.
- **Action**: I ran weekly stakeholder syncs, built a shared roadmap, and created a decision-making framework to resolve conflicts quickly. When eng pushback threatened the timeline, I negotiated scope cuts that preserved 80% of the value.
- **Result**: We launched on time, drove 18% conversion lift, and generated $12M in incremental revenue in the first year.

**2. Data-Driven Decision Making**
- **Situation**: At Uber, our fleet management dashboard had low adoption (22% of target accounts).
- **Task**: Figure out why and fix it.
- **Action**: I ran user interviews with 30 fleet managers, identified 3 core friction points, and prioritized fixes based on impact vs. effort. We A/B tested each change.
- **Result**: Adoption jumped to 68% within 3 months, and we expanded to 5,000 accounts by year-end.

**3. Strategic Problem-Solving**
- **Situation**: At Spotify, leadership wanted to test a freemium-to-premium conversion strategy, but eng was resource-constrained.
- **Task**: Deliver a high-impact test with minimal eng investment.
- **Action**: I proposed a targeted experiment using existing infrastructure—just changing UI copy and pricing display. Worked with data science to design a rigorous test.
- **Result**: We proved the concept with <40 eng hours, got buy-in for a full build, and eventually drove 18% conversion lift.

**4. Stakeholder Management (B2B Context)**
- **Situation**: At Uber, we had 200+ feature requests from commercial accounts, but no clear prioritization framework.
- **Task**: Build a system that balanced customer needs with business priorities.
- **Action**: I created a scoring model (revenue impact, user count, strategic alignment) and ran quarterly prioritization sessions with sales, support, and eng.
- **Result**: Feature delivery improved by 35%, churn dropped by 12%, and customer satisfaction scores increased from 6.2 to 7.8.

**Technical/Functional Questions They'll Ask:**
1. "How do you prioritize competing feature requests?" (Be ready with a framework—RICE, value vs. effort, etc.)
2. "Tell me about a time you launched a feature that failed. What did you learn?"
3. "How do you balance technical debt with new feature development?"
4. "Walk me through how you'd approach [specific product challenge from the JD]."
5. "How do you work with engineering teams to define scope and timelines?"
6. "What metrics would you track for this product?"
7. "How do you handle disagreements with stakeholders?"

**Questions You Should Ask:**
- "What's the biggest product challenge you're facing right now?" (Gets at their pain points)
- "How do you currently prioritize roadmap decisions? Is there a framework in place?" (Shows strategic thinking)
- "What does the product org look like today, and where do you see it in 12 months?" (Shows long-term thinking)
- "Can you tell me about a recent product decision that didn't go as planned? How did the team respond?" (Tests for learning culture)
- "What would make someone successful in this role in the first 6 months?" (Shows execution focus)

**What Success Looks Like:**
Close strong. At the end, restate your fit: "Based on what we've discussed, it sounds like you need someone who can [their pain point]. I've done that at [company], where I [specific result]. I'm confident I can do the same here." Don't ask "What are next steps?"—assume you're advancing and say: "I'm excited about this. What's the timeline for next steps?"

---

### **Example: Intro Sell Template**

**YOUR 60-90 SECOND INTRO SELL:**

"I'm currently a Senior Product Manager at Spotify, where I lead cross-functional teams building monetization features for our Premium tier. Last year, we launched a pricing test that increased conversion by 18% and drove $12M in incremental revenue.

Before Spotify, I was at Uber leading B2B product strategy, where I built our first fleet management dashboard—now used by over 5,000 commercial accounts.

I'm here because you're scaling a B2B SaaS product in a competitive market, and I've done exactly that at two high-growth companies. This role is a great fit because I can step in and own product strategy from day one, and you're at the stage where that kind of execution matters most."

**Word Count:** 115 words  
**Estimated Time:** 55 seconds

**Coaching Note:**
Lead with the Spotify revenue impact—that's your strongest proof point. Keep the Uber section tight (one sentence). End confidently, not tentatively. Practice this out loud until you can deliver it without looking at notes.

---

### **Example: Intro Sell Feedback**

**Overall: 7.5/10** — Solid foundation, but you're over time and burying your strongest achievement. Let's tighten it.

**Content: 8/10**
You led with current role and included quantified impact—strong. You connected your background to what they need. Issue: You spent 2 sentences on your college major. Cut it. They don't care.

**Structure: 6/10**
You followed the formula, but you're at 175 words (about 105 seconds). Target is 100-150 words. The middle section about National Grid doesn't map to this role—cut it entirely.

**Tone: 7/10**
Mostly confident, but you used passive voice in one spot: "I was responsible for managing..." That's weak. Change to: "I managed..." or "I led..."

**Strengths:**
- Led with Spotify revenue impact—your strongest proof point
- Quantified achievements (18% conversion, $12M revenue, 5,000 accounts)
- Clear connection between your background and what they need

**Opportunities:**
- Cut the college major reference—irrelevant for senior roles
- Remove the National Grid example—it doesn't map to B2B SaaS
- Tighten the ending—you're asking for permission instead of stating fit

**Revised Version:**
"I'm currently a Senior Product Manager at Spotify, where I lead cross-functional teams building monetization features for our Premium tier. Last year, we launched a pricing test that increased conversion by 18% and drove $12M in incremental revenue.

Before Spotify, I was at Uber leading B2B product strategy, where I built our first fleet management dashboard—now used by over 5,000 commercial accounts.

I'm here because you're scaling a B2B SaaS product, and I've done exactly that at two high-growth companies. This role is a great fit because I can step in and own product strategy from day one."

**Word count:** 115 words (target: 100-150) ✓  
**Estimated time:** 55 seconds ✓

**Next Step:**
Practice this revised version out loud 3-5 times. Record yourself and listen back. You'll catch filler words and pacing issues. Once it feels natural, you're ready.

---

### **Example: Interview Debrief Output**

**OVERALL PERFORMANCE: 7/10**

**Dimension Scores:**
- **Content: 8/10** — You hit the key competencies they care about
- **Clarity: 6/10** — You rambled on the "Tell me about a time you failed" question
- **Delivery: 7/10** — Confident tone, good energy
- **Tone: 8/10** — Professional, warm. No red flags
- **Structure: 7/10** — Solid STAR on most answers, but you skipped the "Result" on one example
- **Confidence: 7/10** — Strong overall, but you second-guessed yourself twice

**What Landed:**
- Your answer about the Spotify pricing test was excellent. You tied it directly to what they need, quantified impact, and showed leadership.
- Your questions at the end were sharp—especially asking about their biggest product challenge. That signaled strategic thinking.
- You opened strong with your intro sell. Tight, confident, grounded in real achievements.

**What Didn't Land:**
- Your "greatest weakness" answer felt generic. You said "I'm a perfectionist," which is a cliché. They've heard that 100 times.
- You talked too much about your National Grid utility work. That's not what they're hiring for, and it diluted your positioning.
- When they asked about handling stakeholder disagreements, you gave a vague answer. You needed a specific STAR example there.

**What You Should Have Said:**

**Question:** "What's your greatest weakness?"

**Your Answer:** "I'm a perfectionist—I always want everything to be perfect before shipping."

**Better Answer:** "Early in my career, I struggled with delegating technical decisions to engineering teams. I wanted to be involved in every detail. I've worked on this by building trust with my eng partners and focusing on outcomes rather than outputs. Now I'm at the point where I can step back and let the team own implementation while I focus on strategy. It's still something I'm refining, but I've made significant progress."

**Why This Is Better:** It's honest, self-aware, shows growth, and uses a real developmental area that's relevant to the PM role.

**Coaching Points:**
1. **Lead with impact.** Don't bury your wins in the middle of long stories. Start with the result, then explain how you got there.
2. **Cut utility sector examples** unless they explicitly ask. They're not relevant to B2B SaaS product work.
3. **Practice your "Why this company?" answer.** Yours was fine, but it wasn't memorable. Reference something specific about their product or market that excites you.

**Action Items:**
1. Send a thank-you email within 24 hours (see draft below)
2. Prep a tighter "Why this company?" answer for the next round
3. Have 2-3 STAR examples ready that emphasize cross-functional leadership—they asked about it twice

**Thank-You Email:**

---

Subject: Thank you — Senior Product Manager Interview

Hi [Interviewer Name],

Thank you for taking the time to speak with me today about the Senior PM role. I especially appreciated hearing about the challenge you're facing with enterprise customer adoption—it's exactly the kind of problem I enjoy solving.

Our conversation reinforced my interest in this role. At Uber, I tackled a similar adoption challenge with our fleet dashboard (22% → 68% adoption in 3 months), and I'm confident I could bring that same data-driven approach to your product roadmap.

I'm excited about the opportunity and happy to provide any additional information. What's the timeline for next steps?

Best,
[Candidate Name]

---

**Next Stage Adjustments:**

For your hiring manager round (if you advance):
- Emphasize your B2B product experience more prominently—they care about this
- Prepare a tighter "greatest weakness" answer using the framework above
- Have 3-4 STAR examples ready that showcase cross-functional leadership
- Research their enterprise customers so you can speak intelligently about their market

---

## **Future Enhancements (Phase 2+)**

### **Audio Analysis for Intro Sell**
- Speech-to-text for recorded intro sell
- Pace analysis (words per minute)
- Filler word detection ("um," "uh," "like")
- Upspeak detection (rising intonation at end of sentences)
- Pause quality analysis (natural vs. awkward)

### **Mock Interview Mode**
- HenryAI asks a series of questions in sequence
- Candidate responds in real-time
- Live feedback after each answer
- Full session summary at end with scores and coaching

### **Company Intelligence Integration**
- Web search for recent news (funding, layoffs, pivots, leadership changes)
- Glassdoor sentiment analysis (culture, comp, interview process)
- LinkedIn intel (hiring manager background, team size, recent hires)
- Market position analysis (growth stage, competitive landscape)

### **Panel Interview Prep**
- Multiple interviewer preparation (eng, design, product, data)
- Role-specific questions for each interviewer
- Collaboration stories emphasized over individual achievements
- Technical depth preparation for peer interviews

### **Executive Interview Prep**
- Strategic framing (how you think about the business, not just the role)
- Vision and judgment questions
- Leadership potential assessment
- Long-term alignment questions

### **Salary Negotiation Prep**
- Market data for role + location + experience level
- Leverage assessment (strong vs. weak negotiating position)
- Anchoring strategy (should you go first or wait?)
- Counteroffer scripts (exact language for pushing back)
- Non-salary lever negotiation (equity, bonus, remote flexibility, title, start date)

---

## **Implementation Phasing**

### **MVP (Phase 1) — Target: January 2025**
- Recruiter screen prep (static generation)
- Hiring manager prep (static generation)
- Intro sell practice (text-based feedback only)
- Typed debrief (guided prompts, no transcript upload)
- Thank-you email generation

**Success Criteria:**
- 50% of beta users complete at least one practice session
- Average debrief score improves by 1 point after 3 interviews
- 80% of users report prep was "helpful" or "very helpful"

### **Phase 1.5 — Target: February 2025**
- Conversational practice mode (full chat interface)
- Transcript upload + parsing
- Audio upload for intro sell (pace/tone analysis)
- Interview history timeline view

**Success Criteria:**
- 30% of users upload transcripts for debrief
- Average practice sessions per user increases to 3+
- 70% of users send thank-you emails

### **Phase 2 — Target: Q2 2025**
- Panel interview prep
- Executive interview prep
- Mock interview mode (you ask questions, they respond in real-time)
- Salary negotiation prep (unlocks after offer)
- Company intelligence integration (web search + Glassdoor)

**Success Criteria:**
- 40% of users who reach final round use salary negotiation prep
- Average offer amount for users who use negotiation prep is 10%+ higher
- Mock interview mode used by 25% of active users

---

## **Key Product Decisions & Rationale**

### **Why Progressive Disclosure?**
Candidates are overwhelmed. Showing them prep for all interview stages at once creates decision paralysis. Progressive disclosure reduces cognitive load and keeps focus on the immediate next step.

### **Why Force Practice?**
Reading prep materials doesn't translate to interview performance. Forcing candidates to type out answers (or record themselves) creates muscle memory and exposes weaknesses they wouldn't notice otherwise.

### **Why Debrief After Every Interview?**
Most candidates don't reflect—they just move to the next application. Structured debriefs force reflection, track improvement, and provide coaching that compounds over time.

### **Why Start With Recruiter + Hiring Manager Only?**
These two stages account for 80% of interview dropoff. Panel and executive rounds are important, but if candidates can't pass the first two stages, the later prep doesn't matter.

### **Why Thank-You Emails?**
Many candidates don't send them. Those who do often send generic ones. Auto-generating a tailored email based on interview content is a quick win that shows attention to detail and reinforces fit.

### **Why Track Interview History?**
Candidates need to see progress. Knowing their debrief scores are improving (7 → 7.5 → 8) builds confidence and validates that practice is working.

---

## **Competitive Differentiation**

**What Others Do:**
- Generic interview question banks (no personalization)
- Resume keyword matching for ATS
- Mock interviews with humans (expensive, not scalable)
- Behavioral question frameworks (STAR, etc.) without practice

**What HenryAI Does Differently:**
- **Personalized prep** based on candidate's actual resume + specific job
- **Zero fabrication rule** — all examples grounded in real experience
- **Recruiter-grade coaching** — strategic positioning, not just "be yourself"
- **Practice + debrief loop** — continuous improvement, not one-time prep
- **Honest market intelligence** — calls out red flags and provides mitigation
- **Thank-you email generation** — small touch that most candidates skip

---

## **Risk Mitigation**

### **Risk: AI Generates Fabricated Content**
**Mitigation:**
- Strict prompts that require grounding in resume
- Validation layer that checks for generic phrases
- Manual spot-checks of generated content
- User feedback mechanism ("Flag fabricated content")

### **Risk: Candidates Become Too Scripted**
**Mitigation:**
- Coaching emphasizes natural delivery, not memorization
- Practice mode provides frameworks, not word-for-word scripts
- Debrief feedback penalizes overly rehearsed answers

### **Risk: Interview Prep Feels Generic**
**Mitigation:**
- Every output references specific achievements from candidate's resume
- STAR examples pulled from actual work history
- Questions tailored to job description requirements
- Company-specific research integrated (Phase 2)

### **Risk: Low Engagement (Candidates Don't Practice)**
**Mitigation:**
- Gamification (track practice sessions, readiness score)
- Nudges before scheduled interviews ("Your interview is tomorrow—have you practiced?")
- Social proof ("Candidates who practice 3+ times advance 40% more often")

---

## **Open Questions (To Validate)**

1. **Should we show readiness scores?** (e.g., "You're 75% ready for this interview")
   - Pro: Motivates practice
   - Con: Could create anxiety if score is low

2. **Should we allow candidates to skip stages?** (e.g., jump straight to hiring manager prep)
   - Pro: User flexibility
   - Con: Breaks progressive disclosure philosophy

3. **Should we auto-generate prep or wait for user trigger?**
   - Pro (auto): Reduces friction
   - Con (auto): May feel pushy

4. **Should we track which STAR examples perform best?**
   - Pro: Data-driven improvement
   - Con: Hard to measure objectively

5. **Should we integrate with calendar to auto-remind about interviews?**
   - Pro: Reduces no-shows for practice
   - Con: Scope creep for MVP

---

**End of Product Spec**
