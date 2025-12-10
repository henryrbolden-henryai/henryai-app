# HenryAI Resume Builder — Full Implementation Specification

## Overview

The Resume Builder is a conversational experience that helps users without an existing resume create one from scratch. Instead of forms and text fields, users have a back-and-forth conversation with HenryAI that feels like talking to a recruiter.

After the resume is complete, HenryAI analyzes the user's skills and suggests adjacent career paths they may not have considered.

---

## User Flow Summary

```
[Landing Page]
  → Name capture (first, last, nickname)
  → [Start]
  ↓
[Conversational Resume Builder]
  → Opening and expectations
  → Header info (location, contact, LinkedIn)
  → Role loop (repeat for each job):
    → Company + title
    → Dates + current status
    → Function detection
    → Function-specific responsibility questions
    → Achievement capture
    → Skills confirmation
    → Role reveal + confirmation
    → "What's before this?" → loop or exit
  → Education capture
  → Additional info (certs, languages, volunteer)
  → Final resume reveal + confirmation
  ↓
[Skills Analysis & Role Mapping]
  → Extract skills from confirmed responsibilities
  → Map to adjacent roles in other fields
  → Present 3-5 alternative career paths
  → User decision: explore alternatives or proceed
  ↓
[Save & Route to Profile Setup]
```

---

## Part 0: Interaction Modes and Graceful Handling

### Interaction Modes

Users can interact with the Resume Builder in two ways:

**Voice Mode (Default)**
- User speaks responses using device microphone
- HenryAI responds with OpenAI voice synthesis for human-like speech
- Most natural experience; feels like a recruiter intake call
- Speech-to-text converts user input; text-to-speech delivers HenryAI responses

**Text Mode (Fallback)**
- User types responses
- HenryAI responds with text
- Available for users who prefer typing or are in environments where voice is not practical

### Mode Selection UI

On the landing page, after name capture:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   How would you like to do this?                            │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  🎤  Talk with me                                   │   │
│   │  Like a phone call. Just speak naturally.           │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  ⌨️  Type instead                                   │   │
│   │  If you prefer typing or can't use audio right now. │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   You can switch modes anytime.                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Mode Switching

Users can switch modes at any point:

**Voice to Text:**
- User clicks text input field or "Switch to typing" button
- System confirms: "No problem. Just type your answers instead."
- Conversation continues seamlessly in text

**Text to Voice:**
- User clicks microphone button or "Switch to voice" button
- System prompts for microphone permission if not granted
- HenryAI confirms vocally: "Got it. Just speak naturally and I'll listen."

### Voice Interaction Technical Requirements

```typescript
interface VoiceConfig {
  speechToText: {
    provider: 'openai-whisper' | 'browser-native';
    language: string;           // e.g., 'en-US'
    continuous: boolean;        // Keep listening vs. push-to-talk
    interimResults: boolean;    // Show partial transcription
  };
  textToSpeech: {
    provider: 'openai';
    voice: string;              // OpenAI voice model ID
    speed: number;              // 0.8 to 1.2 range
  };
  silenceDetection: {
    pauseThreshold: number;     // ms of silence before assuming user is done (e.g., 1500)
    maxDuration: number;        // max recording time in ms (e.g., 60000)
  };
}
```

### Voice UX Considerations

**Listening Indicator:**
- Clear visual indicator when HenryAI is listening (pulsing mic icon, waveform animation)
- User should always know if their voice is being captured
- Different states: idle, listening, processing, speaking

**Turn-Taking:**
- HenryAI pauses briefly after speaking to allow user response
- Silence detection determines when user has finished speaking
- "Thinking" indicator while processing speech-to-text
- Avoid cutting off users mid-sentence

**Interruption Handling:**
- If user speaks while HenryAI is speaking, pause playback and listen
- Acknowledge interruption naturally: "Oh, go ahead" or "Sorry, what was that?"
- Resume context after interruption if needed

**Transcription Display:**
- Show transcribed text on screen so user can verify accuracy
- Allow text correction if speech-to-text misheard
- Editable transcript before confirming each response

**Audio Feedback:**
- Subtle audio cue when HenryAI starts listening
- Subtle audio cue when HenryAI starts speaking
- Keeps interaction feeling responsive

---

### Graceful Handling: Off-Script Conversations

Users will go off-script. They will ask questions, share concerns, tell stories, or vent. HenryAI should handle these naturally, not robotically redirect.

**Principles:**
1. Acknowledge what they said
2. Respond appropriately (answer questions, validate feelings)
3. Gently guide back to the resume when natural

**Example Scenarios:**

**User asks a question:**
> **User:** "Actually, is it bad that I've had three jobs in two years?"
>
> **HenryAI:** "Not necessarily. Job-hopping stigma has faded a lot, especially post-COVID. What matters more is whether you can tell a coherent story about why you moved. If each change was a step toward something, that's fine. We can talk about how to frame it once I see the full picture.
>
> So, you were at [Company] for about a year. What were you doing there?"

**User vents about job search:**
> **User:** "This whole process is so frustrating. I've applied to like 50 jobs and heard nothing."
>
> **HenryAI:** "That's brutal, and you're not alone. The market right now is genuinely tough, and a lot of applications go into a black hole. That's actually part of why we're doing this. A strong resume won't fix a broken system, but it gives you a better shot at getting through the filters.
>
> Let's make sure yours is working as hard as it can. Tell me about your most recent role."

**User shares personal context:**
> **User:** "I had to leave my last job because my mom got sick and I needed to take care of her."
>
> **HenryAI:** "I'm sorry to hear that. Caregiving is real work, even if it doesn't go on a traditional resume. We don't have to include details about why you left, but I'll make sure there's no awkward gap that raises questions.
>
> How long were you away from traditional work?"

**User asks about HenryAI:**
> **User:** "Wait, are you a real person or AI?"
>
> **HenryAI:** "I'm AI. I'm HenryAI, built to help people put together resumes that actually work. I don't get tired, I don't judge, and I've been trained on what recruiters actually look for. So you're in good hands, even if they're digital ones.
>
> Now, where were we? You were telling me about [last topic]."

**Detection and Response Framework:**

```typescript
type OffScriptType =
  | 'question'           // User asks something unrelated to current prompt
  | 'concern'            // User expresses worry about their candidacy
  | 'frustration'        // User vents about job search or process
  | 'personal_share'     // User shares personal circumstances
  | 'confusion'          // User is lost or doesn't understand
  | 'tangent'            // User goes off on unrelated topic
  | 'meta_question'      // User asks about HenryAI itself
  | 'request';           // User asks HenryAI to do something specific

interface OffScriptHandler {
  detect: (input: string) => OffScriptType | null;
  respond: (type: OffScriptType, context: ConversationState) => string;
  shouldRedirect: (type: OffScriptType) => boolean;
  redirectPhrase: (context: ConversationState) => string;
}
```

---

### Graceful Handling: Memory Gaps

Users will forget things. Dates, metrics, job titles, company names, achievements. The system should never block progress because of missing information.

**Principles:**
1. Normalize forgetting ("That's fine" or "No problem")
2. Offer alternatives (skip, estimate, come back later)
3. Try different angles to jog memory
4. Flag incomplete items for later review

**Example Scenarios:**

**Can't remember dates:**
> **User:** "I don't remember exactly when I started."
>
> **HenryAI:** "That's fine. Roughly how long were you there? We can work backward from when you left."

**Can't remember metrics:**
> **User:** "I have no idea what the numbers were."
>
> **HenryAI:** "No problem. Do you know if you were above or below target? Or how you compared to others on the team? Even directional info helps."

**Can't think of achievements:**
> **User:** "I can't think of anything I accomplished."
>
> **HenryAI:** "Let me ask it differently. Was there ever a problem you solved? A process you improved? A fire you put out? A time your manager or a customer thanked you?"

**Still stuck after multiple attempts:**
> **User:** "I really don't know. It was a while ago."
>
> **HenryAI:** "That's okay. We'll keep this section lighter for now. If something comes back to you later, you can always update it. Let's keep moving."

**Memory Gap Handling Logic:**

```typescript
interface MemoryGapStrategy {
  attempts: {
    first: 'rephrase_question';    // Ask differently
    second: 'provide_examples';    // Give concrete examples
    third: 'offer_skip';           // Allow moving on
  };
  skipBehavior: 'flag_for_review' | 'use_generic' | 'omit';
}

interface IncompleteItem {
  field: string;
  phase: ConversationPhase;
  roleIndex: number | null;
  attemptCount: number;
  lastPromptUsed: string;
  skippedAt: Date;
}
```

**Review Prompt at End:**
> **HenryAI:** "Before we finalize, there were a couple things you weren't sure about earlier. Want to take another look, or leave them as is?"

---

### Graceful Handling: Stuck Users

Sometimes users don't know how to answer, give very short responses, or seem confused about what's being asked.

**Signals of a Stuck User:**
- Very short responses ("fine", "yeah", "I don't know")
- Long pauses before responding (voice mode)
- "I don't understand" or "What do you mean?"
- Repeating the same non-answer
- Silence exceeding normal pause threshold

**Response Strategies:**

**Rephrase the question:**
> **HenryAI:** "Let me put it another way. When you were at [Company], what did you spend most of your day doing?"

**Give concrete examples:**
> **HenryAI:** "For example, were you managing people, working directly with customers, building or fixing things, analyzing data, handling operations? Which sounds closest?"

**Offer choices (works well in voice):**
> **HenryAI:** "Would you say your role was more about working with people, working with numbers, working with your hands, or something else?"

**Simplify:**
> **HenryAI:** "Let's keep it simple. What's one thing you did in that job that you remember?"

**Check in:**
> **HenryAI:** "I want to make sure I'm asking the right questions. Is something unclear, or would you rather skip this part for now?"

**Stuck User Detection:**

```typescript
interface StuckUserSignals {
  shortResponseThreshold: number;      // e.g., responses under 3 words
  shortResponseCount: number;          // consecutive short responses
  silenceDuration: number;             // ms of silence in voice mode
  confusionPhrases: string[];          // "I don't know", "what?", "huh?"
  repeatCount: number;                 // same response given multiple times
}

function isUserStuck(signals: StuckUserSignals, history: ConversationTurn[]): boolean {
  // Implementation checks recent history against thresholds
}
```

---

### Graceful Handling: Frustration Signals

Users may get frustrated during the process. They might feel their experience is inadequate, the questions are too hard, or the process is taking too long.

**Signals of Frustration:**
- Sighing, groaning, or audible frustration (voice mode)
- Short, curt responses
- Repeated "I don't know" answers
- "This is taking forever"
- "I don't have good answers for this"
- "Can we just skip this"
- Negative self-talk ("My experience isn't impressive")

**Response Strategies:**

**Acknowledge the difficulty:**
> **HenryAI:** "I know this part can feel tedious. We're through the hardest part. Let me speed things up."

**Validate their experience:**
> **User:** "I don't have impressive stuff like other people."
>
> **HenryAI:** "Most people feel that way. Seriously. You're closer to your own work than anyone, so it feels ordinary. But from the outside, what you've done has real value. Let me show you what I mean once we get this down."

**Offer to simplify:**
> **HenryAI:** "Want me to ask shorter questions? We can move faster if we stick to the basics and skip the details."

**Offer a break:**
> **HenryAI:** "We can pause here if you need a break. Your progress is saved. You can come back anytime and pick up right where we left off."

**Show progress:**
> **HenryAI:** "Good news: we've got two of your three jobs done. One more and we're on to the easy stuff."

---

### Graceful Handling: Technical Issues (Voice Mode)

Voice mode introduces technical failure points: microphone issues, speech-to-text errors, background noise, connectivity problems.

**Microphone Not Working:**
> **HenryAI (text fallback):** "I'm having trouble hearing you. Can you check your microphone settings? Or if you prefer, you can type your answers instead."
>
> [Show "Switch to text mode" button prominently]

**Speech-to-Text Misheard:**
> **HenryAI:** "I heard '[transcription]'. Did I get that right?"
>
> [Display edit button for user to correct]
>
> If user says "no" or "that's wrong":
> **HenryAI:** "Sorry about that. Can you say it again, or type it out if that's easier?"

**Background Noise Issues:**
> **HenryAI:** "I'm picking up some background noise and might mishear you. If my transcriptions look off, feel free to correct them or switch to typing."

**Long Processing Delay:**
> [Visual indicator: "Processing..."]
>
> If delay exceeds 5 seconds:
> **HenryAI:** "Still working on that. One second."
>
> If delay exceeds 10 seconds:
> **HenryAI:** "Sorry, that's taking longer than usual. You were saying...?"

**Connection Lost:**
> [On reconnect]
> **HenryAI:** "Looks like we got disconnected for a second. No worries, everything's saved. You were telling me about [last topic]. Want to continue from there?"

**User's Audio Cuts Out:**
> **HenryAI:** "I think your audio cut out. Can you repeat that last part?"

---

### Quick Mode Alternative

For users who prefer structured input over open conversation, or who are struggling with the conversational format.

**When to Offer Quick Mode:**
- User selects "Type instead" from the start
- User gives very short responses repeatedly
- User explicitly asks for something faster
- User seems frustrated with open-ended questions

**Quick Mode Prompt:**
> **HenryAI:** "Would you prefer a faster approach? I can ask shorter questions with options to pick from instead of going back and forth. It's quicker but a bit less detailed."

**Quick Mode Characteristics:**
- Multiple choice for function type
- Structured form inputs for company, title, dates
- Checklist for responsibilities (not open-ended)
- Single achievement question per role (optional)
- Skips conversational probing and follow-ups
- Still generates the same resume output

**Quick Mode Question Format:**

```typescript
interface QuickModeQuestion {
  id: string;
  phase: ConversationPhase;
  question: string;
  type: 'text' | 'select' | 'multiselect' | 'date_range' | 'yes_no' | 'number';
  options?: string[];
  placeholder?: string;
  required: boolean;
  helpText?: string;
}

// Example Quick Mode flow for a role:
const quickModeRoleQuestions: QuickModeQuestion[] = [
  { id: 'company', question: 'Company name', type: 'text', required: true },
  { id: 'title', question: 'Your job title', type: 'text', required: true },
  { id: 'dates', question: 'When did you work there?', type: 'date_range', required: true },
  { id: 'current', question: 'Is this your current job?', type: 'yes_no', required: true },
  { id: 'function', question: 'What best describes your work?', type: 'select', 
    options: ['Sales', 'Marketing', 'Operations', 'Customer Service', 'Management', 'Technical', 'Administrative', 'Other'],
    required: true },
  { id: 'responsibilities', question: 'What did you do? (Select all that apply)', type: 'multiselect',
    options: [], // Populated based on function selection
    required: true },
  { id: 'achievement', question: 'One accomplishment you are proud of (optional)', type: 'text', required: false,
    helpText: 'A number, a win, a problem you solved' }
];
```

---

### State Persistence and Recovery

Because voice conversations can be interrupted (calls, browser crashes, distractions), the system must save state frequently.

**Auto-Save Triggers:**
- After each phase completion
- After each role is confirmed
- Every 30 seconds during active conversation
- Before any mode switch
- On window blur or visibility change

**Recovery Scenarios:**

**User closes browser mid-conversation:**
> [On return to landing page, if saved state exists]
>
> "Welcome back, [Name]. Looks like we were in the middle of building your resume. Want to pick up where you left off?"
>
> [Continue] [Start Over]

**User takes a long pause (voice mode):**
> [After 2 minutes of silence]
>
> **HenryAI:** "Still there? No rush. Take your time, or if you need to step away, your progress is saved. You can come back anytime."

**Session timeout:**
> [On return after extended absence]
>
> **HenryAI:** "Hey [Name], welcome back. Your resume draft is saved. Want to continue where we left off, or would you rather start fresh?"

**State Recovery Data:**

```typescript
interface SavedSession {
  sessionId: string;
  userId: string;
  state: ConversationState;
  lastActiveAt: Date;
  createdAt: Date;
  interactionMode: 'voice' | 'text';
  completionPercentage: number;
  lastPhase: ConversationPhase;
  lastRoleIndex: number | null;
}
```

---

## Part 1: Landing Page

### Purpose
Capture user's name before entering the conversational flow. The nickname allows HenryAI to address them naturally throughout the conversation.

### UI Elements

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│        Let's build your resume together.                    │
│                                                             │
│   Most resume builders make you do all the work.            │
│   HenryAI doesn't.                                          │
│                                                             │
│   Answer a few questions about your experience, and         │
│   I'll write your resume for you. Formatted, optimized,     │
│   and ready to use.                                         │
│                                                             │
│   Takes about 10-15 minutes. No templates. No guesswork.    │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ First Name                                          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Last Name                                           │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ What should I call you? (optional)                  │   │
│   └─────────────────────────────────────────────────────┘   │
│   Leave blank if your first name works fine.                │
│                                                             │
│                    [ Start ]                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Model

```typescript
interface UserIdentity {
  firstName: string;        // Required. Used on resume header.
  lastName: string;         // Required. Used on resume header.
  nickname: string | null;  // Optional. Used in conversation.
  displayName: string;      // Computed: nickname || firstName
}
```

### Validation Rules

| Field | Required | Validation |
|-------|----------|------------|
| firstName | Yes | Non-empty, max 50 chars |
| lastName | Yes | Non-empty, max 50 chars |
| nickname | No | Max 50 chars if provided |

### Logic

```typescript
function getDisplayName(user: UserIdentity): string {
  return user.nickname?.trim() || user.firstName;
}
```

---

## Part 2: Conversation State Machine

### State Definition

```typescript
interface ConversationState {
  phase: ConversationPhase;
  user: UserIdentity;
  header: HeaderInfo | null;
  roles: WorkRole[];
  currentRoleIndex: number;
  education: Education[];
  skills: string[];
  certifications: string[];
  languages: Language[];
  volunteerWork: string[];
  resumeComplete: boolean;
  skillAnalysisComplete: boolean;
}

type ConversationPhase =
  | 'opening'
  | 'header'
  | 'role_basic'
  | 'role_function'
  | 'role_responsibilities'
  | 'role_achievements'
  | 'role_skills'
  | 'role_reveal'
  | 'role_transition'
  | 'education'
  | 'additional_info'
  | 'final_reveal'
  | 'skill_analysis'
  | 'complete';
```

### Header Info Model

```typescript
interface HeaderInfo {
  city: string;
  state: string | null;
  remoteOpen: boolean;
  relocationOpen: boolean;
  email: string;
  phone: string;
  linkedIn: string | null;
}
```

### Work Role Model

```typescript
interface WorkRole {
  company: string;
  title: string;
  startDate: string;           // Format: "MMM YYYY" or "YYYY"
  endDate: string | null;      // null = "Present"
  isCurrent: boolean;
  function: WorkFunction;
  responsibilities: ResponsibilityConfirmation;
  achievements: Achievement[];
  skills: string[];
  bullets: string[];           // Generated resume bullets
  confirmed: boolean;
}

type WorkFunction =
  | 'sales'
  | 'marketing'
  | 'operations'
  | 'finance'
  | 'hr'
  | 'engineering'
  | 'product'
  | 'customer_success'
  | 'executive'
  | 'administrative'
  | 'retail_hospitality'
  | 'skilled_trades'
  | 'freelance'
  | 'gig_work'
  | 'military'
  | 'student'
  | 'career_break'
  | 'other';
```

---

## Part 3: Conversation Scripts

### 3.1 Opening

**Trigger:** User clicks "Start" on landing page.

**Script:**

```
"Hey {displayName}! I'm HenryAI. I'm here to help you build a resume that actually works.

Here's how this goes: I'll ask about your work history, you tell me what you did, and I'll turn it into resume bullets. No writing on your part. Just answer my questions honestly and I'll handle the rest.

The whole thing takes about 10-15 minutes. Ready to get started?"
```

**User Response:** Any affirmative response advances to header phase.

---

### 3.2 Header Info Collection

**Script Sequence:**

```
1. "Perfect. Let's knock out the basics first, {displayName}.

   What city are you based in? And if you're open to remote or relocation, let me know that too."

   [Wait for response]

2. "Got it. {city}, {remote/relocation status}. What's the best email and phone number for your resume?"

   [Wait for response]

3. "Great. Do you have a LinkedIn profile? If so, drop the URL. If not, no worries. We can skip it."

   [Wait for response]

4. "Alright {displayName}, header's done. Now let's get into the good stuff. Your experience."
```

**Extraction Rules:**

| Input Pattern | Extracted Data |
|---------------|----------------|
| "Chicago" | city: "Chicago", state: "IL" (inferred) |
| "Chicago, open to remote" | city: "Chicago", remoteOpen: true |
| "NYC, willing to relocate" | city: "New York", relocationOpen: true |
| "Remote only" | city: null, remoteOpen: true |

---

### 3.3 Role Collection — Basic Info

**Script:**

```
"Let's start with your most recent job, or your current one if you're still employed. Where are you working, and what's your title?"

[Wait for response]

"{title} at {company}. {affirmation}. How long have you been there?"

[Wait for response]

"And are you still there, or have you moved on?"

[Wait for response]

"{Acknowledgment based on employment status}. So tell me about the gig, {displayName}. What's your day-to-day? Are you {function-specific examples}? What's the shape of it?"
```

**Employment Status Responses:**

| Status | Response |
|--------|----------|
| Currently employed, looking | "Got it. Actively looking while employed. That's actually a good position to be in, {displayName}. Gives you leverage." |
| Currently employed, not looking | "Got it. Still there and not actively looking. Good to capture this anyway." |
| Recently left | "Got it. Recently moved on. Let's make sure we capture what you did there." |
| Left a while ago | "Got it. Let's document what you accomplished there." |

---

### 3.4 Function Detection

Based on the user's description of their day-to-day, HenryAI classifies them into a function category. If ambiguous, HenryAI asks a clarifying question.

**Classification Prompt (Internal):**

```
Based on the user's description of their role, classify into one of these functions:
- sales: Revenue generation, pipeline, quotas, closing deals
- marketing: Demand gen, content, campaigns, brand
- operations: Process, logistics, supply chain, inventory
- finance: Accounting, FP&A, budgeting, audit
- hr: Recruiting, people ops, L&D, compensation
- engineering: Software, hardware, infrastructure, QA
- product: Roadmap, specs, user research, product strategy
- customer_success: Account management, retention, support
- executive: C-suite, VP+, P&L ownership
- administrative: Office management, coordination, scheduling
- retail_hospitality: Store, restaurant, hotel, service industry
- skilled_trades: Electrical, plumbing, HVAC, construction
- freelance: Independent contractor with multiple clients
- gig_work: Platform-based work (DoorDash, Uber, TaskRabbit)
- military: Active duty or veteran transitioning
- student: No work history, recent graduate
- career_break: Returning after gap (caregiving, health, etc.)
- other: Does not fit above categories
```

---

### 3.5 Function-Specific Responsibility Questions

Each function has a tailored set of questions. HenryAI asks these conversationally, not as a checklist.

#### Sales / Business Development

```typescript
interface SalesResponsibilities {
  ownPipeline: boolean;
  closeDeals: boolean;
  dealSizeRange: 'under_50k' | '50k_250k' | '250k_1m' | 'over_1m';
  manageReps: boolean;
  salesMotion: 'inbound' | 'outbound' | 'partner' | 'mix';
  crossFunctional: boolean;
  namedAccounts: boolean;
}
```

**Conversational Flow:**

```
"Okay, so you're in sales at {company}. Let me understand the setup.

Were you running your own book of business, or more of a team selling motion?"

[Response]

"And what was the typical deal size you were working? Ballpark is fine."

[Response]

"Got it. Were you mostly closing inbound leads, doing your own prospecting, or a mix?"

[Response]

"Did you work with other teams like marketing, product, or customer success to close deals?"

[Response]
```

#### Marketing / Communications

```typescript
interface MarketingResponsibilities {
  focusArea: 'demand_gen' | 'content' | 'brand' | 'product_marketing' | 'comms' | 'mix';
  ownBudget: boolean;
  budgetSize: string | null;
  manageTeam: boolean;
  teamSize: number | null;
  handsOnTools: boolean;
  reportToLeadership: boolean;
  channels: string[];
}
```

**Conversational Flow:**

```
"Marketing at {company}. What was your focus? Demand gen, content, brand, product marketing, or a mix of everything?"

[Response]

"Were you hands-on in the tools, or more strategic with a team executing?"

[Response]

"Did you own a budget? If so, roughly how much?"

[Response]

"What channels were you primarily working with?"

[Response]
```

#### Operations / Supply Chain

```typescript
interface OperationsResponsibilities {
  focusArea: 'logistics' | 'supply_chain' | 'process_improvement' | 'facilities' | 'general_ops';
  manageVendors: boolean;
  manageBudget: boolean;
  manageTeam: boolean;
  teamSize: number | null;
  implementedSystems: boolean;
  metricsOwned: string[];
}
```

**Conversational Flow:**

```
"Operations at {company}. What part of ops were you focused on? Logistics, supply chain, process improvement, facilities, or general operations?"

[Response]

"Were you managing vendors or external partners?"

[Response]

"Did you own any specific metrics or KPIs?"

[Response]

"Any systems or processes you implemented or improved?"

[Response]
```

#### Finance / Accounting

```typescript
interface FinanceResponsibilities {
  focusArea: 'accounting' | 'fpa' | 'audit' | 'tax' | 'treasury' | 'general';
  closeBooks: boolean;
  budgetForecasting: boolean;
  reporting: boolean;
  teamSize: number | null;
  systemsUsed: string[];
  complianceWork: boolean;
}
```

**Conversational Flow:**

```
"Finance at {company}. Were you more on the accounting side, FP&A, audit, or something else?"

[Response]

"Were you involved in closing the books? Monthly, quarterly?"

[Response]

"Any budgeting or forecasting work?"

[Response]

"What systems were you working in? NetSuite, SAP, Excel, something else?"

[Response]
```

#### HR / People / Talent

```typescript
interface HRResponsibilities {
  focusArea: 'recruiting' | 'people_ops' | 'learning_development' | 'compensation' | 'hrbp' | 'general';
  hiringVolume: string | null;
  manageTeam: boolean;
  teamSize: number | null;
  systemsUsed: string[];
  policyWork: boolean;
  employeeRelations: boolean;
}
```

**Conversational Flow:**

```
"HR at {company}. What was your focus? Recruiting, people ops, L&D, comp, HRBP work, or a mix?"

[Response]

"If recruiting, roughly how many hires were you responsible for? Per year or per quarter is fine."

[Response]

"Did you handle any employee relations or policy work?"

[Response]

"What systems were you using? Workday, Greenhouse, Lever, something else?"

[Response]
```

#### Engineering / Technical

```typescript
interface EngineeringResponsibilities {
  focusArea: 'frontend' | 'backend' | 'fullstack' | 'infrastructure' | 'data' | 'qa' | 'security' | 'hardware' | 'other';
  techStack: string[];
  manageTeam: boolean;
  teamSize: number | null;
  architectureWork: boolean;
  onCall: boolean;
  shipFrequency: 'daily' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly';
}
```

**Conversational Flow:**

```
"Engineering at {company}. What's your focus? Frontend, backend, fullstack, infra, data, something else?"

[Response]

"What's your tech stack? Languages, frameworks, tools."

[Response]

"Are you an individual contributor, or do you manage other engineers?"

[Response]

"How often are you shipping? Daily, weekly, sprint-based?"

[Response]
```

#### Product / Design

```typescript
interface ProductResponsibilities {
  focusArea: 'product_management' | 'product_design' | 'ux_research' | 'product_ops';
  ownRoadmap: boolean;
  writePRDs: boolean;
  workWithEngineering: boolean;
  userResearch: boolean;
  releaseFrequency: 'weekly' | 'biweekly' | 'monthly' | 'quarterly';
  presentToLeadership: boolean;
}
```

**Conversational Flow:**

```
"Product at {company}. Are you on the PM side, design side, or research?"

[Response]

"Do you own a roadmap, or are you executing on someone else's?"

[Response]

"How closely do you work with engineering? Are you in the weeds with them?"

[Response]

"Do you do any user research yourself, or is there a separate team for that?"

[Response]
```

#### Customer Success / Support

```typescript
interface CustomerSuccessResponsibilities {
  focusArea: 'csm' | 'support' | 'implementation' | 'renewals' | 'mix';
  portfolioSize: number | null;
  revenueOwned: string | null;
  manageTeam: boolean;
  teamSize: number | null;
  escalationHandling: boolean;
  churnPrevention: boolean;
}
```

**Conversational Flow:**

```
"Customer success at {company}. Are you a CSM with a book of accounts, more on the support side, or focused on implementation?"

[Response]

"Roughly how many accounts or customers are you responsible for?"

[Response]

"Do you have any revenue responsibility? Renewals, upsells?"

[Response]

"How do you handle escalations? Do those come to you?"

[Response]
```

#### General Management / Executive

```typescript
interface ExecutiveResponsibilities {
  scope: 'department' | 'business_unit' | 'region' | 'company';
  pnlOwnership: boolean;
  revenueResponsibility: string | null;
  teamSize: number | null;
  directReports: number | null;
  boardInteraction: boolean;
  strategyWork: boolean;
}
```

**Conversational Flow:**

```
"You're at the executive level at {company}. What's your scope? Running a department, a business unit, a region, or the whole company?"

[Response]

"Do you have P&L ownership? If so, what's the rough size?"

[Response]

"How big is your organization? Total headcount and direct reports."

[Response]

"Are you interacting with the board or investors?"

[Response]
```

#### Administrative / Coordination

```typescript
interface AdministrativeResponsibilities {
  focusArea: 'executive_assistant' | 'office_manager' | 'coordinator' | 'receptionist' | 'general_admin';
  supportedExecutives: number | null;
  calendarManagement: boolean;
  travelArrangements: boolean;
  eventPlanning: boolean;
  vendorManagement: boolean;
  officeOperations: boolean;
}
```

**Conversational Flow:**

```
"Admin work at {company}. Are you supporting specific executives, managing the office, or more of a general coordinator role?"

[Response]

"Are you handling calendars and travel for anyone?"

[Response]

"Any event planning or office operations in your scope?"

[Response]

"Do you manage any vendors or suppliers for the office?"

[Response]
```

#### Retail, Restaurant, or Hospitality

```typescript
interface RetailHospitalityResponsibilities {
  role: 'associate' | 'cashier' | 'server' | 'shift_lead' | 'supervisor' | 'manager' | 'gm';
  manageTeam: boolean;
  teamSize: number | null;
  openClose: 'open' | 'close' | 'both' | 'neither';
  cashHandling: boolean;
  inventoryManagement: boolean;
  laborTargets: boolean;
  trainingNewHires: boolean;
  customerEscalations: boolean;
  salesTargets: boolean;
}
```

**Conversational Flow:**

```
"Got it. {title} at {company}. Let me understand the setup.

Were you managing a team, or more of an individual contributor?"

[If managing]
"How many people were typically on your shift?"

[Response]

"Were you handling opening, closing, or both?"

[Response]

"Did you deal with cash handling and register management?"

[Response]

"What about inventory? Were you doing ordering, stock management, waste tracking?"

[Response]

"Were you responsible for hitting any targets? Labor costs, sales goals, customer scores?"

[Response]

"Did you train new employees?"

[Response]

"How about customer complaints? Did those come to you?"

[Response]
```

#### Skilled Trades / Technical Services

```typescript
interface SkilledTradesResponsibilities {
  trade: 'electrical' | 'plumbing' | 'hvac' | 'carpentry' | 'welding' | 'automotive' | 'other';
  certifications: string[];
  journeyman: boolean;
  masterLevel: boolean;
  manageTeam: boolean;
  teamSize: number | null;
  projectTypes: 'residential' | 'commercial' | 'industrial' | 'mix';
  estimating: boolean;
  clientFacing: boolean;
  safetyCompliance: boolean;
}
```

**Conversational Flow:**

```
"Skilled trades at {company}. What's your trade? Electrical, plumbing, HVAC, carpentry, something else?"

[Response]

"Are you a journeyman, master, or still in apprenticeship?"

[Response]

"Do you have any certifications I should know about?"

[Response]

"What kind of projects? Residential, commercial, industrial?"

[Response]

"Do you do any estimating or bidding work?"

[Response]

"Are you client-facing, or mostly on the job site?"

[Response]
```

#### Freelance / Contract Work

```typescript
interface FreelanceResponsibilities {
  serviceType: string;
  clientTypes: 'small_business' | 'startup' | 'agency' | 'enterprise' | 'individual' | 'mix';
  totalClients: 'under_10' | '10_25' | '26_50' | 'over_50';
  projectSizeRange: 'under_500' | '500_2k' | '2k_5k' | '5k_10k' | 'over_10k';
  soloOrCollaborate: 'solo' | 'collaborate';
  directClientCommunication: boolean;
  notableClients: string[];
}
```

**Conversational Flow:**

```
"Freelance work. What kind of services do you provide?"

[Response]

"What type of clients do you typically work with? Small businesses, startups, agencies, bigger companies?"

[Response]

"Roughly how many clients have you worked with total?"

[Response]

"What's a typical project size for you? Dollar range is fine."

[Response]

"Do you manage everything yourself, or do you collaborate with other freelancers?"

[Response]

"Have you worked with any recognizable brands or companies?"

[Response]
```

#### Gig Work

```typescript
interface GigResponsibilities {
  platforms: string[];
  hoursPerWeek: 'under_20' | '20_30' | '30_40' | 'over_40';
  rating: number | null;
  totalDeliveries: number | null;
  statusTiers: string[];
  ownSchedule: boolean;
  specialOrders: boolean;
}
```

**Conversational Flow:**

```
"Gig work. What platforms have you worked on?"

[Response]

"How many hours per week do you typically work?"

[Response]

"Do you have a rating on any of the platforms? And roughly how many deliveries or jobs have you completed?"

[Response]

"Have you achieved any status tiers? Top Dasher, Diamond, anything like that?"

[Response]
```

#### Military Service

```typescript
interface MilitaryResponsibilities {
  branch: 'army' | 'navy' | 'air_force' | 'marines' | 'coast_guard' | 'space_force';
  rank: string;
  mos: string;
  yearsOfService: number;
  leadership: boolean;
  teamSize: number | null;
  deployments: number;
  specializations: string[];
  clearance: string | null;
}
```

**Conversational Flow:**

```
"Military service. Which branch?"

[Response]

"What was your rank when you separated?"

[Response]

"And your MOS or job specialty?"

[Response]

"How many years did you serve?"

[Response]

"Did you have leadership responsibilities? If so, how many people?"

[Response]

"Any deployments?"

[Response]

"Do you have any security clearances that are still active?"

[Response]
```

#### Student / Recent Grad / No Experience

```typescript
interface StudentInfo {
  school: string;
  degree: string;
  major: string;
  graduationDate: string;
  gpa: number | null;
  internships: WorkRole[];
  projects: Project[];
  clubs: ClubLeadership[];
  volunteerWork: string[];
}

interface Project {
  name: string;
  description: string;
  role: string;
  outcomes: string[];
}

interface ClubLeadership {
  organization: string;
  role: string;
  description: string;
}
```

**Conversational Flow:**

```
"Got it. You're just getting started, so we'll build your resume a little differently. Instead of work history, we'll focus on education, projects, volunteer work, and anything else that shows what you can do.

Where did you go to school, and what did you study?"

[Response]

"When did you graduate, or when do you expect to?"

[Response]

"Did you do any internships while you were there?"

[Response]

"What about projects, clubs, or leadership roles? Anything where you took ownership of something?"

[Response]

"Any volunteer work or community involvement?"

[Response]
```

#### Returning After Career Break

```typescript
interface CareerBreakInfo {
  reason: 'caregiving' | 'health' | 'education' | 'travel' | 'personal' | 'prefer_not_to_say';
  duration: string;
  anyWorkDuring: boolean;
  volunteerDuring: boolean;
  educationDuring: boolean;
  skillsDeveloped: string[];
}
```

**Conversational Flow:**

```
"Got it. You're returning after some time away. That's more common than people think, and we can absolutely build a strong resume.

If you're comfortable sharing, what was the reason for the break? Totally fine if you'd rather not say."

[Response]

"How long were you away from traditional work?"

[Response]

"During that time, did you do any freelance work, volunteer work, or take any courses?"

[Response]

"What skills do you feel you developed or maintained during that time? Even informal skills count."

[Response]
```

---

### 3.6 Achievement Capture

After responsibility questions, HenryAI asks about achievements. This is the most important part for resume quality.

**Script:**

```
"Alright {displayName}, here's the important part. What's something you're proud of from {company}? A problem you solved, a metric you improved, a situation you handled well. Doesn't have to sound fancy."

[Wait for response]

[Probe for specifics based on what they share]

"That's a real {metric/accomplishment}. {Explanation of why it matters}."

[If they mention a number]
"Do you know the exact figure, or is that an estimate?"

[If vague]
"Can you give me a rough number? Even a ballpark helps."

[If they can't think of anything]
"Nothing's coming to mind? That's fine. Let me ask differently. Was there a problem you solved, a process you fixed, or a fire you put out?"

[Continue probing until you have 1-3 achievements]
```

**Achievement Data Model:**

```typescript
interface Achievement {
  description: string;
  metric: string | null;
  metricValue: string | null;
  isEstimate: boolean;
  context: string | null;
}
```

---

### 3.7 Skills Confirmation

After achievements, HenryAI confirms skills based on what was discussed.

**Script:**

```
"Based on what you've told me, I'm assuming you're solid on {inferred skills}. What am I missing? What should I add or drop?"

[Wait for response]

"Done. {skills} added."
```

**Skill Inference Rules:**

| Function | Role Type | Inferred Skills |
|----------|-----------|-----------------|
| sales | AE | CRM (Salesforce), pipeline management, prospecting, negotiation, forecasting |
| marketing | demand_gen | Marketing automation (HubSpot/Marketo), campaign management, analytics, A/B testing |
| engineering | backend | Primary language, frameworks mentioned, databases, cloud platforms |
| retail_hospitality | manager | Team leadership, scheduling, inventory management, P&L awareness, customer service |

---

### 3.8 Role Reveal

After collecting all information for a role, HenryAI generates bullets and presents them.

**Script:**

```
"Here's what I've got for {company}, {displayName}. Tell me if anything's off:

**{title} | {company} | {startDate} to {endDate}**
- {bullet 1}
- {bullet 2}
- {bullet 3}
- {bullet 4}

How's that feel? Anything you'd add or change?"

[Wait for response]

[If changes requested]
"Done. {change description}."

[Transition]
"Alright, let's go back further. What were you doing before {company}?"
```

**Bullet Generation Rules:**

1. Lead with impact verbs (Led, Built, Drove, Increased, Reduced, Managed)
2. Include metrics when available
3. Show scope (team size, budget, revenue, geography)
4. Use "to" instead of em dashes for date ranges
5. No fabrication. Only use information the user provided.
6. If no achievement metrics, write responsibility-focused bullets

---

### 3.9 Role Transition & Loop

After confirming one role, HenryAI asks about previous roles.

**Script:**

```
"Alright, let's go back further. What were you doing before {company}?"
```

**Exit Conditions:**

- User says they have no more relevant experience
- User mentions education (triggers education capture)
- User indicates a career gap (triggers gap handling)
- More than 7 years of history captured

**Gap Handling:**

```
"So you left {previous_company} in {date}, but {current_company} started in {date}. What was happening in between?"

[Wait for response]

[If caregiving/health/personal]
"Understood. I won't put that on the resume unless you want to. Just needed to know so I don't leave a gap unexplained. We good to move on?"

[If education]
"Got it. Let's capture that in your Education section."

[If other work]
"Tell me more about that."
```

---

### 3.10 Education Capture

**Script:**

```
"Let's talk about education. What's your highest level of education, and where did you go?"

[Wait for response]

"What did you study?"

[Wait for response]

"When did you graduate?"

[Wait for response]

[If impressive school or recent grad]
"That's a strong signal. We'll make sure it's prominent on your resume."

[If older education]
"Got it. We'll include it but keep the focus on your experience."
```

**Education Data Model:**

```typescript
interface Education {
  institution: string;
  degree: string;
  field: string;
  graduationYear: number;
  honors: string | null;
  gpa: number | null;
  includeGpa: boolean;
}
```

---

### 3.11 Additional Info

**Script:**

```
"Last question: anything else you want on here? Certifications, languages, volunteer work, anything?"

[Wait for response]

[For each item mentioned]
"{item} goes on. {Explanation of why it's valuable}."
```

---

### 3.12 Final Resume Reveal

**Script:**

```
"Here's your full resume, {displayName}. Read through it and let me know if anything needs tweaking:

---

**{firstName} {lastName}**
{city}, {state} | {remote/relocation status}
{email} | {phone} | {linkedIn}

**{title} | {company} | {startDate} to {endDate}**
- {bullet}
- {bullet}
- {bullet}

**{title} | {company} | {startDate} to {endDate}**
- {bullet}
- {bullet}

**Education**
{degree}, {field}, {institution}, {year}

**Skills**
{skills list}

**Certifications**
{certifications list}

**Languages**
{languages list}

---

How's that looking? Anything you want me to adjust before we save it?"

[Wait for response]

[Make any requested changes]

"Alright {displayName}, your resume's done. I'm saving this to your profile now. You can download it anytime, and when you start analyzing job descriptions, this is what I'll use to assess your fit.

But before we move on, I want to show you something about your skills."
```

---

## Part 4: Skills Taxonomy

### Master Skill List

```typescript
const SKILL_TAXONOMY = {
  leadership: [
    'team-management',
    'supervision',
    'delegation',
    'mentoring',
    'coaching',
    'performance-management',
    'hiring',
    'termination',
    'conflict-resolution-team'
  ],
  
  operations: [
    'inventory-management',
    'scheduling',
    'process-improvement',
    'compliance',
    'logistics',
    'supply-chain',
    'vendor-management',
    'quality-control',
    'safety-compliance',
    'facilities-management'
  ],
  
  customer: [
    'customer-service',
    'conflict-resolution-customer',
    'escalation-handling',
    'relationship-management',
    'retention',
    'upselling',
    'account-management',
    'client-communication'
  ],
  
  financial: [
    'cash-handling',
    'budgeting',
    'cost-control',
    'forecasting',
    'pnl-management',
    'financial-reporting',
    'expense-management',
    'revenue-management'
  ],
  
  communication: [
    'written-communication',
    'verbal-communication',
    'presentation',
    'negotiation',
    'stakeholder-management',
    'cross-functional-collaboration',
    'executive-communication'
  ],
  
  technical: [
    'pos-systems',
    'crm',
    'spreadsheets',
    'data-entry',
    'data-analysis',
    'reporting',
    'software-specific'
  ],
  
  sales: [
    'prospecting',
    'pipeline-management',
    'closing',
    'contract-negotiation',
    'territory-management',
    'quota-attainment',
    'solution-selling'
  ],
  
  marketing: [
    'campaign-management',
    'demand-generation',
    'content-creation',
    'seo',
    'paid-media',
    'email-marketing',
    'analytics',
    'brand-management'
  ],
  
  administrative: [
    'calendar-management',
    'travel-coordination',
    'document-management',
    'meeting-coordination',
    'office-operations',
    'event-planning'
  ],
  
  self_management: [
    'time-management',
    'prioritization',
    'independence',
    'reliability',
    'adaptability',
    'attention-to-detail',
    'multitasking'
  ],
  
  training: [
    'onboarding',
    'training-delivery',
    'curriculum-development',
    'knowledge-transfer',
    'documentation'
  ]
};
```

### Responsibility to Skill Mapping

```typescript
const RESPONSIBILITY_SKILL_MAP: Record<string, string[]> = {
  // Retail/Hospitality
  'manage-team': ['team-management', 'supervision', 'delegation', 'scheduling'],
  'cash-handling': ['cash-handling', 'accuracy', 'attention-to-detail'],
  'inventory': ['inventory-management', 'forecasting', 'cost-control'],
  'train-employees': ['onboarding', 'training-delivery', 'coaching', 'knowledge-transfer'],
  'customer-escalations': ['conflict-resolution-customer', 'customer-service', 'escalation-handling'],
  'open-close': ['reliability', 'operations', 'compliance', 'cash-handling'],
  'labor-targets': ['budgeting', 'cost-control', 'scheduling', 'forecasting'],
  'sales-targets': ['sales', 'upselling', 'performance-management'],
  
  // Sales
  'own-pipeline': ['pipeline-management', 'forecasting', 'crm'],
  'close-deals': ['closing', 'negotiation', 'solution-selling'],
  'outbound-prospecting': ['prospecting', 'cold-outreach', 'lead-generation'],
  'named-accounts': ['account-management', 'relationship-management', 'strategic-selling'],
  
  // Marketing
  'demand-gen': ['demand-generation', 'campaign-management', 'lead-generation'],
  'content-marketing': ['content-creation', 'seo', 'written-communication'],
  'paid-media': ['paid-media', 'analytics', 'budget-management'],
  'own-budget': ['budgeting', 'cost-control', 'financial-reporting'],
  
  // Operations
  'process-improvement': ['process-improvement', 'data-analysis', 'problem-solving'],
  'vendor-management': ['vendor-management', 'negotiation', 'relationship-management'],
  'logistics': ['logistics', 'supply-chain', 'coordination'],
  
  // Customer Success
  'manage-accounts': ['account-management', 'relationship-management', 'retention'],
  'handle-renewals': ['retention', 'negotiation', 'revenue-management'],
  'onboard-customers': ['onboarding', 'training-delivery', 'client-communication'],
  
  // Gig Work
  'delivery-driving': ['time-management', 'customer-service', 'reliability', 'navigation'],
  'maintain-rating': ['customer-service', 'attention-to-detail', 'reliability'],
  'self-scheduling': ['time-management', 'independence', 'prioritization'],
  
  // Freelance
  'manage-clients': ['client-communication', 'project-management', 'relationship-management'],
  'deliver-projects': ['project-management', 'time-management', 'quality-control'],
  'business-development': ['prospecting', 'negotiation', 'sales']
};
```

---

## Part 5: Role Mapping Engine

### Adjacent Role Database

```typescript
interface AdjacentRole {
  title: string;
  field: string;
  requiredSkills: string[];
  preferredSkills: string[];
  seniorityLevel: 'entry' | 'mid' | 'senior' | 'management' | 'executive';
  typicalSalaryRange: {
    min: number;
    max: number;
    currency: string;
  };
  transitionDifficulty: 'easy' | 'moderate' | 'stretch';
  whyItFits: string;
}

const ADJACENT_ROLES: AdjacentRole[] = [
  // From Retail/Hospitality Manager
  {
    title: 'Operations Coordinator',
    field: 'Operations',
    requiredSkills: ['scheduling', 'inventory-management', 'process-improvement'],
    preferredSkills: ['vendor-management', 'budgeting', 'team-management'],
    seniorityLevel: 'mid',
    typicalSalaryRange: { min: 45000, max: 65000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your inventory, scheduling, and process management experience translates directly.'
  },
  {
    title: 'HR Coordinator',
    field: 'Human Resources',
    requiredSkills: ['onboarding', 'training-delivery', 'scheduling'],
    preferredSkills: ['compliance', 'documentation', 'employee-relations'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 40000, max: 55000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'You have already done onboarding, training, and retention work.'
  },
  {
    title: 'Customer Success Associate',
    field: 'Customer Success',
    requiredSkills: ['customer-service', 'conflict-resolution-customer', 'relationship-management'],
    preferredSkills: ['retention', 'upselling', 'crm'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 45000, max: 60000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your customer escalation and service skills are a direct match.'
  },
  {
    title: 'Office Manager',
    field: 'Administration',
    requiredSkills: ['team-management', 'scheduling', 'vendor-management'],
    preferredSkills: ['budgeting', 'facilities-management', 'event-planning'],
    seniorityLevel: 'mid',
    typicalSalaryRange: { min: 50000, max: 70000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'Your team coordination, vendor management, and operational skills apply here.'
  },
  {
    title: 'Retail Store Manager',
    field: 'Retail',
    requiredSkills: ['team-management', 'pnl-management', 'inventory-management'],
    preferredSkills: ['sales', 'merchandising', 'loss-prevention'],
    seniorityLevel: 'management',
    typicalSalaryRange: { min: 55000, max: 80000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Same skill set, different environment. Your food service management is directly applicable.'
  },
  
  // From Cashier/Associate
  {
    title: 'Bank Teller',
    field: 'Banking',
    requiredSkills: ['cash-handling', 'customer-service', 'accuracy'],
    preferredSkills: ['sales', 'compliance', 'attention-to-detail'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 35000, max: 45000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your cash handling accuracy and customer service experience are exactly what banks need.'
  },
  {
    title: 'Call Center Representative',
    field: 'Customer Service',
    requiredSkills: ['customer-service', 'conflict-resolution-customer', 'verbal-communication'],
    preferredSkills: ['data-entry', 'multitasking', 'crm'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 32000, max: 42000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your customer service and conflict resolution skills transfer directly to phone-based support.'
  },
  {
    title: 'Medical Receptionist',
    field: 'Healthcare Administration',
    requiredSkills: ['customer-service', 'scheduling', 'multitasking'],
    preferredSkills: ['data-entry', 'attention-to-detail', 'compliance'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 35000, max: 45000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'Your customer service and multitasking abilities apply well to healthcare front desk work.'
  },
  {
    title: 'Sales Development Representative',
    field: 'Sales',
    requiredSkills: ['verbal-communication', 'customer-service', 'reliability'],
    preferredSkills: ['prospecting', 'crm', 'resilience'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 40000, max: 55000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'Your upselling experience and customer interaction skills are the foundation of outbound sales.'
  },
  
  // From Gig Work
  {
    title: 'Courier (Corporate)',
    field: 'Logistics',
    requiredSkills: ['time-management', 'reliability', 'navigation'],
    preferredSkills: ['customer-service', 'independence'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 35000, max: 50000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your delivery experience with verified reliability metrics makes you a strong candidate.'
  },
  {
    title: 'Warehouse Associate',
    field: 'Logistics',
    requiredSkills: ['reliability', 'time-management', 'physical-stamina'],
    preferredSkills: ['inventory-management', 'attention-to-detail'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 35000, max: 50000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your logistics experience and proven reliability translate to warehouse operations.'
  },
  {
    title: 'Field Service Technician',
    field: 'Technical Services',
    requiredSkills: ['time-management', 'customer-service', 'independence'],
    preferredSkills: ['technical-aptitude', 'problem-solving'],
    seniorityLevel: 'entry',
    typicalSalaryRange: { min: 40000, max: 60000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'Your route management and independent work style fit field service roles well.'
  },
  
  // From Freelance
  {
    title: 'In-House Designer/Developer/Writer',
    field: 'Creative',
    requiredSkills: ['project-management', 'client-communication', 'quality-control'],
    preferredSkills: ['collaboration', 'deadline-management'],
    seniorityLevel: 'mid',
    typicalSalaryRange: { min: 55000, max: 85000, currency: 'USD' },
    transitionDifficulty: 'easy',
    whyItFits: 'Your freelance portfolio demonstrates the skills. In-house offers stability and benefits.'
  },
  {
    title: 'Project Manager',
    field: 'Project Management',
    requiredSkills: ['project-management', 'client-communication', 'deadline-management'],
    preferredSkills: ['budgeting', 'team-management', 'stakeholder-management'],
    seniorityLevel: 'mid',
    typicalSalaryRange: { min: 60000, max: 90000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'You have been managing projects and clients. This formalizes those skills.'
  },
  {
    title: 'Account Manager',
    field: 'Sales',
    requiredSkills: ['client-communication', 'relationship-management', 'negotiation'],
    preferredSkills: ['upselling', 'retention', 'crm'],
    seniorityLevel: 'mid',
    typicalSalaryRange: { min: 55000, max: 80000, currency: 'USD' },
    transitionDifficulty: 'moderate',
    whyItFits: 'Your client management and repeat business skills are the core of account management.'
  }
];
```

### Role Matching Algorithm

```typescript
interface SkillMatch {
  role: AdjacentRole;
  overlapScore: number;
  matchedSkills: string[];
  missingSkills: string[];
}

function findAdjacentRoles(
  userSkills: string[],
  currentField: string,
  seniorityLevel: string,
  limit: number = 5
): SkillMatch[] {
  
  const matches: SkillMatch[] = [];
  
  for (const role of ADJACENT_ROLES) {
    // Skip roles in the same field (we want to show NEW paths)
    if (role.field.toLowerCase() === currentField.toLowerCase()) {
      continue;
    }
    
    // Skip roles that are too far above or below their level
    if (!isSeniorityCompatible(seniorityLevel, role.seniorityLevel)) {
      continue;
    }
    
    // Calculate skill overlap
    const matchedRequired = role.requiredSkills.filter(s => userSkills.includes(s));
    const matchedPreferred = role.preferredSkills.filter(s => userSkills.includes(s));
    const missingRequired = role.requiredSkills.filter(s => !userSkills.includes(s));
    
    // Must match at least 50% of required skills
    const requiredMatchRate = matchedRequired.length / role.requiredSkills.length;
    if (requiredMatchRate < 0.5) {
      continue;
    }
    
    // Calculate overall score
    const requiredScore = matchedRequired.length * 2;  // Required skills worth 2x
    const preferredScore = matchedPreferred.length;
    const totalPossible = (role.requiredSkills.length * 2) + role.preferredSkills.length;
    const overlapScore = ((requiredScore + preferredScore) / totalPossible) * 100;
    
    matches.push({
      role,
      overlapScore: Math.round(overlapScore),
      matchedSkills: [...matchedRequired, ...matchedPreferred],
      missingSkills: missingRequired
    });
  }
  
  // Sort by overlap score descending
  matches.sort((a, b) => b.overlapScore - a.overlapScore);
  
  return matches.slice(0, limit);
}

function isSeniorityCompatible(userLevel: string, roleLevel: string): boolean {
  const levels = ['entry', 'mid', 'senior', 'management', 'executive'];
  const userIndex = levels.indexOf(userLevel);
  const roleIndex = levels.indexOf(roleLevel);
  
  // Allow +/- 1 level
  return Math.abs(userIndex - roleIndex) <= 1;
}
```

---

## Part 6: Skills Analysis Presentation

### Script

After the resume is complete:

```
"Alright {displayName}, your resume's done. But before we move on, I want to show you something based on what you've told me.

You've been working in {current_field}, but the skills you've built actually transfer to a lot of other fields. Here's what I'm seeing:

**Your Core Skills:**
- {skill 1} ({evidence})
- {skill 2} ({evidence})
- {skill 3} ({evidence})
- {skill 4} ({evidence})
- {skill 5} ({evidence})

**Roles You Might Not Have Considered:**

1. **{role_title_1}** ({field}) — {overlapScore}% skill match
   {whyItFits}
   Salary range: {min} - {max}

2. **{role_title_2}** ({field}) — {overlapScore}% skill match
   {whyItFits}
   Salary range: {min} - {max}

3. **{role_title_3}** ({field}) — {overlapScore}% skill match
   {whyItFits}
   Salary range: {min} - {max}

These are not stretches. They're lateral moves that use the same skills in a different context.

Want me to help you target one of these? Or do you already have something specific in mind?"
```

### User Decision Handling

```typescript
type SkillAnalysisDecision =
  | { type: 'explore_alternative'; roleIndex: number }
  | { type: 'know_what_i_want'; targetRole: string }
  | { type: 'skip' };
```

**If user wants to explore an alternative:**

```
"Great choice. {role_title} is a strong fit for your background. Let me adjust your resume positioning to highlight the skills that matter most for this path.

[Adjust resume summary and bullet emphasis]

Here's how I'd reframe your experience for {role_title} roles:

**Summary:**
{adjusted_summary}

**Key bullets to emphasize:**
- {bullet emphasizing relevant skill}
- {bullet emphasizing relevant skill}

When you search for jobs, look for titles like: {related_titles}

Ready to finish setting up your profile?"
```

**If user knows what they want:**

```
"Got it. What kind of role are you targeting?"

[Capture target role]

"Understood. When you drop in job descriptions for {target_role} positions, I'll assess your fit and help you position your experience accordingly.

Ready to finish setting up your profile?"
```

**If user wants to skip:**

```
"No problem. We can always revisit this later. Your resume is saved, and when you start analyzing job descriptions, I'll help you position your experience for whatever roles you're targeting.

Ready to finish setting up your profile?"
```

---

## Part 7: Data Models Summary

### Complete State Object

```typescript
interface ResumeBuilderState {
  // User identity
  user: {
    firstName: string;
    lastName: string;
    nickname: string | null;
    displayName: string;
  };
  
  // Contact/header
  header: {
    city: string;
    state: string | null;
    remoteOpen: boolean;
    relocationOpen: boolean;
    email: string;
    phone: string;
    linkedIn: string | null;
  } | null;
  
  // Work history
  roles: WorkRole[];
  
  // Education
  education: Education[];
  
  // Skills (confirmed by user)
  skills: string[];
  
  // Additional info
  certifications: string[];
  languages: Language[];
  volunteerWork: string[];
  
  // Skill analysis results
  extractedSkills: ExtractedSkill[];
  adjacentRoles: SkillMatch[];
  selectedPath: SkillAnalysisDecision | null;
  
  // Conversation state
  currentPhase: ConversationPhase;
  currentRoleIndex: number;
  conversationHistory: ConversationTurn[];
  
  // Completion flags
  resumeComplete: boolean;
  skillAnalysisComplete: boolean;
  savedToProfile: boolean;
}

interface ExtractedSkill {
  skill: string;
  category: string;
  evidence: string;  // How it was demonstrated
  source: string;    // Which role it came from
}

interface Language {
  language: string;
  proficiency: 'basic' | 'conversational' | 'professional' | 'native';
}

interface ConversationTurn {
  role: 'assistant' | 'user';
  content: string;
  timestamp: Date;
  phase: ConversationPhase;
}
```

---

## Part 8: Resume Output Format

### Final Resume Structure

```typescript
interface GeneratedResume {
  header: {
    fullName: string;
    location: string;
    contact: string;
    linkedIn: string | null;
  };
  
  experience: {
    title: string;
    company: string;
    dateRange: string;
    bullets: string[];
  }[];
  
  education: {
    degree: string;
    field: string;
    institution: string;
    year: number;
    honors: string | null;
  }[];
  
  skills: string[];
  
  certifications: string[];
  
  languages: {
    language: string;
    proficiency: string;
  }[];
}
```

### Output Formatting Rules

1. **Name:** First and last name, properly capitalized
2. **Location:** City, State abbreviation | Remote status if applicable
3. **Contact:** Email | Phone | LinkedIn (as URL)
4. **Date ranges:** Use "to" not em dashes (e.g., "Jan 2022 to Present")
5. **Bullets:** Start with action verbs, include metrics when available
6. **Skills:** Comma-separated, tools first, then competencies
7. **Education:** Degree, Field, Institution, Year (one line)

---

## Part 9: API Endpoints

### Required Endpoints

```typescript
// Initialize a new resume builder session
POST /api/resume-builder/start
Body: { firstName: string, lastName: string, nickname?: string }
Response: { sessionId: string, displayName: string }

// Send a message in the conversation
POST /api/resume-builder/message
Body: { sessionId: string, message: string }
Response: { 
  reply: string, 
  phase: ConversationPhase,
  stateUpdate?: Partial<ResumeBuilderState>
}

// Get current state
GET /api/resume-builder/state/:sessionId
Response: ResumeBuilderState

// Save completed resume to profile
POST /api/resume-builder/save
Body: { sessionId: string }
Response: { success: boolean, resumeId: string }

// Get skill analysis
GET /api/resume-builder/skills/:sessionId
Response: { 
  extractedSkills: ExtractedSkill[],
  adjacentRoles: SkillMatch[]
}

// Export resume
GET /api/resume-builder/export/:sessionId
Query: { format: 'pdf' | 'docx' | 'json' }
Response: File download or JSON
```

---

## Part 10: Implementation Notes

### Conversation Management

1. **State persistence:** Store conversation state in database or session storage
2. **Context window:** Pass relevant state to Claude for each message
3. **Phase transitions:** Use explicit state machine logic, not implicit detection
4. **Error recovery:** Allow users to go back or correct information

### Claude Integration

1. **System prompt:** Include current state, phase, and user info
2. **Response parsing:** Extract structured data from Claude's responses
3. **Validation:** Verify extracted data before updating state
4. **Fallbacks:** Handle cases where Claude's response doesn't match expected format

### Quality Controls

1. **No fabrication:** Only use information explicitly provided by user
2. **Confirmation loops:** Always show generated content and ask for approval
3. **Edit capability:** Allow users to modify any section at any time
4. **Consistent voice:** Maintain HenryAI's tone throughout

### Performance

1. **Incremental saves:** Save state after each phase completion
2. **Resume capability:** Allow users to return and continue later
3. **Timeout handling:** Save state if user becomes inactive

---

## Part 11: Testing Scenarios

### Happy Path
- User with 3 jobs, clear progression, strong achievements
- Should complete in 10-15 minutes with clean output

### Edge Cases
1. **Single job:** User has only worked one place
2. **Many short stints:** User has 5+ jobs in 3 years
3. **Career changer:** User switching from military to corporate
4. **Gig only:** User has only done DoorDash/Uber
5. **Recent grad:** User has no work history
6. **Career gap:** User returning after 3+ years away
7. **Vague answers:** User gives one-word responses
8. **No achievements:** User cannot articulate any wins
9. **Overqualified:** Executive with 20+ years experience

### Validation Tests
1. Resume contains no fabricated information
2. All dates are properly formatted
3. Skills match what was discussed
4. Adjacent roles are actually relevant
5. Conversation feels natural, not robotic

---

## Part 12: Future Enhancements

### Phase 2
- LinkedIn import as alternative to manual entry
- Resume file upload with parsing and enhancement
- Multiple resume versions for different targets

### Phase 3
- Video/audio conversation option
- Real-time collaboration with career coach
- Integration with job search and application tracking

---

## Appendix A: Sample Conversations

See separate file: `henryai-resume-builder-sample-conversations.md`

## Appendix B: Complete Skill Taxonomy

See separate file: `henryai-skill-taxonomy.json`

## Appendix C: Adjacent Role Database

See separate file: `henryai-adjacent-roles.json`
