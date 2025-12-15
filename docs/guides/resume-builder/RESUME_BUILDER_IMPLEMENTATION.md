# HenryAI Resume Builder Implementation Plan

**Goal:** Transform profile creation from a form-filling exercise into a conversational, AI-guided experience that extracts transferable skills and builds a professional resume from any background.

**Target Users:** Career changers, gig workers, recent graduates, and anyone who doesn't have a polished resume ready.

---

## Implementation Waves

### Wave 1: Text-Only MVP (Current Focus)

The foundational conversational interface that proves the concept before adding voice capabilities.

#### 1.1 Landing Page (`resume-builder.html`)

**Purpose:** Entry point that explains the conversational resume building experience and lets users choose their path.

**UI Elements:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         HenryAI Logo                            │
│                                                                 │
│              Let's Build Your Resume Together                   │
│                                                                 │
│     No resume? No problem. Just tell me about your             │
│     experience and I'll help you create a professional          │
│     resume that highlights your real skills.                    │
│                                                                 │
│     ┌─────────────────────────────────────────────┐            │
│     │  💬  Start Chatting with Henry              │            │
│     │  Tell me about your work experience         │            │
│     └─────────────────────────────────────────────┘            │
│                                                                 │
│     ┌─────────────────────────────────────────────┐            │
│     │  📄  I Already Have a Resume                │            │
│     │  Upload and let Henry analyze it            │            │
│     └─────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation:**
- New file: `frontend/resume-builder.html`
- Two paths: conversational (new) or upload (existing `profile-edit.html` flow)
- Clean, approachable design that reduces anxiety for users without resumes

#### 1.2 Conversational Interface (`resume-chat.html`)

**Purpose:** Full-screen chat interface where Henry guides users through sharing their experience.

**UI Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back                    Build Your Resume                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🎯 Henry                                                 │   │
│  │ Hi! I'm Henry, your job search strategist. I'm going    │   │
│  │ to help you build a resume that shows off your real     │   │
│  │ skills - no fluff, just the truth.                      │   │
│  │                                                          │   │
│  │ Let's start simple: What's been your main job or        │   │
│  │ activity over the past year or two?                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                    ┌───────────────────────┐   │
│                                    │ I've been working at  │   │
│                                    │ a restaurant...       │   │
│                                    └───────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🎯 Henry                                                 │   │
│  │ Restaurant work is great experience! What was your      │   │
│  │ role there? Server, cook, manager?                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐  📤   │
│  │ Type your response...                               │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- Message history with Henry (left) and user (right) bubbles
- Real-time typing indicator when Henry is "thinking"
- Progress indicator showing conversation stage
- Ability to go back/edit previous responses
- Auto-save conversation state to sessionStorage

**Conversation State Machine:**
```
START → CURRENT_ROLE → RESPONSIBILITIES → ACHIEVEMENTS →
PREVIOUS_ROLES → EDUCATION → SKILLS_SUMMARY → ROLE_GOALS →
ADJACENT_ROLES → GENERATE_RESUME → COMPLETE
```

#### 1.3 Backend Conversation API (`/api/resume-chat`)

**Endpoint:** `POST /api/resume-chat`

**Request:**
```json
{
  "conversation_history": [
    {"role": "assistant", "content": "Hi! I'm Henry..."},
    {"role": "user", "content": "I've been working at a restaurant..."}
  ],
  "current_state": "CURRENT_ROLE",
  "extracted_data": {
    "experiences": [],
    "skills": [],
    "education": []
  }
}
```

**Response:**
```json
{
  "response": "Restaurant work is great experience! What was your role there?",
  "next_state": "RESPONSIBILITIES",
  "extracted_data": {
    "experiences": [
      {
        "title": null,
        "company": "Restaurant (name TBD)",
        "industry": "Food Service",
        "duration": "past year or two"
      }
    ],
    "skills": [],
    "education": []
  },
  "skills_extracted": [],
  "suggested_responses": [
    "I was a server",
    "I was a cook",
    "I was a shift manager"
  ]
}
```

**System Prompt Strategy:**

The backend uses a detailed system prompt that:
1. Instructs Claude to follow the conversation state machine
2. Provides the skill taxonomy for extraction
3. Emphasizes graceful handling (per spec Part 0)
4. Returns structured JSON with extracted data

#### 1.4 Skill Extraction Engine

**Implementation:** Integrated into `/api/resume-chat` responses

**Process:**
1. As user describes experiences, Claude extracts skills using taxonomy
2. Each skill includes:
   - `skill_name`: From taxonomy (e.g., "Conflict Resolution")
   - `category`: Parent category (e.g., "customer")
   - `evidence`: User's own words that indicated skill
   - `confidence`: high/medium/low based on specificity

**Example Extraction:**
```json
{
  "skills_extracted": [
    {
      "skill_name": "Conflict Resolution",
      "category": "customer",
      "evidence": "handled difficult customers when they complained about wait times",
      "confidence": "high"
    },
    {
      "skill_name": "Team Coordination",
      "category": "leadership",
      "evidence": "made sure the kitchen and servers were on the same page",
      "confidence": "medium"
    }
  ]
}
```

#### 1.5 Skills Dashboard (`skills-analysis.html`)

**Purpose:** Visual presentation of extracted skills after conversation completes.

**UI Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back                Your Skills Analysis                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Your Top Skills                                         │   │
│  │                                                          │   │
│  │  Leadership        ████████████░░░░  75%                │   │
│  │  Customer Service  █████████████████  92%                │   │
│  │  Operations        ██████████░░░░░░  62%                │   │
│  │  Communication     ████████████████░  88%                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Skills by Category                                      │   │
│  │                                                          │   │
│  │  🎯 Customer (5 skills)                                 │   │
│  │     • Conflict Resolution - "handled difficult..."      │   │
│  │     • Customer Service - "made sure guests were..."     │   │
│  │     • Problem Solving - "figured out how to..."         │   │
│  │                                                          │   │
│  │  👥 Leadership (3 skills)                               │   │
│  │     • Team Coordination - "made sure kitchen and..."    │   │
│  │     • Training - "showed new hires how to..."           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Roles That Match Your Skills                           │   │
│  │                                                          │   │
│  │  Customer Success Associate          87% match          │   │
│  │  $45,000 - $65,000 | Easy transition                    │   │
│  │  Why: Your conflict resolution and customer focus...    │   │
│  │                                                          │   │
│  │  Operations Coordinator              82% match          │   │
│  │  $42,000 - $58,000 | Easy transition                    │   │
│  │  Why: Your team coordination and process skills...      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           [Generate My Resume →]                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Visual skill bars by category
- Individual skills with evidence from conversation
- Adjacent role recommendations with match percentages
- Clear CTA to generate resume

#### 1.6 Resume Generation (`/api/generate-resume-from-chat`)

**Endpoint:** `POST /api/generate-resume-from-chat`

**Request:**
```json
{
  "extracted_data": {
    "contact": {
      "name": "Marcus Johnson",
      "email": "marcus@email.com",
      "phone": "555-123-4567",
      "location": "Chicago, IL"
    },
    "experiences": [...],
    "skills": [...],
    "education": [...]
  },
  "target_role": "Customer Success Associate"  // optional
}
```

**Response:**
```json
{
  "resume_text": "MARCUS JOHNSON\n...",
  "resume_html": "<div class='resume'>...",
  "sections": {
    "summary": "Customer-focused professional with 3+ years...",
    "experience": [...],
    "skills": [...],
    "education": [...]
  }
}
```

**Generation Logic:**
1. Transform conversation data into resume sections
2. Use skill evidence to write experience bullets
3. Organize skills by category
4. Generate professional summary based on top skills and target role

---

### Wave 2: Voice Integration (Future)

#### 2.1 Voice Input (OpenAI Whisper)

**Implementation:**
```javascript
// Browser MediaRecorder API → Send audio to backend
async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  // Record audio chunks, send to /api/transcribe on stop
}
```

**Backend Endpoint:** `POST /api/transcribe`
- Receives audio blob
- Sends to OpenAI Whisper API
- Returns transcribed text

#### 2.2 Voice Output (OpenAI TTS)

**Implementation:**
```javascript
// After receiving Henry's response, optionally play audio
async function playResponse(text) {
  const response = await fetch('/api/speak', {
    method: 'POST',
    body: JSON.stringify({ text })
  });
  const audioBlob = await response.blob();
  const audio = new Audio(URL.createObjectURL(audioBlob));
  audio.play();
}
```

**Backend Endpoint:** `POST /api/speak`
- Receives text
- Sends to OpenAI TTS API
- Returns audio stream

#### 2.3 Voice/Text Toggle

**UI Enhancement:**
- Microphone button next to text input
- Speaker toggle for Henry's responses
- Visual feedback during recording/playback
- Graceful fallback if microphone access denied

---

### Wave 3: Adjacent Role Engine (Future)

#### 3.1 Role Matching Algorithm

**Process:**
1. Load `henryai-adjacent-roles.json` role database
2. For each role, calculate skill match percentage
3. Weight required skills higher than preferred
4. Filter by transition difficulty preference
5. Sort by match percentage

**Match Calculation:**
```javascript
function calculateRoleMatch(userSkills, role) {
  let score = 0;
  let maxScore = 0;

  // Required skills (weighted 2x)
  role.required_skills.forEach(skill => {
    maxScore += 2;
    if (userSkills.includes(skill)) score += 2;
  });

  // Preferred skills (weighted 1x)
  role.preferred_skills.forEach(skill => {
    maxScore += 1;
    if (userSkills.includes(skill)) score += 1;
  });

  return (score / maxScore) * 100;
}
```

#### 3.2 Career Path Visualization

**UI:** Interactive diagram showing:
- Current inferred role/level
- Recommended adjacent roles
- Skill gaps for each path
- Salary ranges and transition difficulty

---

## File Structure

```
frontend/
├── resume-builder.html      # Landing page (new)
├── resume-chat.html         # Conversational interface (new)
├── skills-analysis.html     # Skills dashboard (new)
├── components/
│   └── resume-chat.js       # Chat component logic (new)
├── css/
│   └── resume-builder.css   # Styles for new pages (new)

backend/
├── server.py                # Existing - add new endpoints
├── prompts/
│   └── resume_chat.py       # System prompt for conversation (new)

docs/guides/
├── henryai-resume-builder-spec.md        # Full spec (exists)
├── henryai-skill-taxonomy.json           # Skill data (exists)
├── henryai-adjacent-roles.json           # Role data (exists)
├── henryai-resume-builder-sample-conversations.md  # Examples (exists)
└── RESUME_BUILDER_IMPLEMENTATION.md      # This document
```

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Wave |
|----------|--------|---------|------|
| `/api/resume-chat` | POST | Handle conversation turns | 1 |
| `/api/generate-resume-from-chat` | POST | Generate resume from extracted data | 1 |
| `/api/transcribe` | POST | Convert speech to text (Whisper) | 2 |
| `/api/speak` | POST | Convert text to speech (TTS) | 2 |
| `/api/match-roles` | POST | Calculate adjacent role matches | 3 |

---

## Data Models

### ConversationState
```typescript
interface ConversationState {
  state: 'START' | 'CURRENT_ROLE' | 'RESPONSIBILITIES' | 'ACHIEVEMENTS' |
         'PREVIOUS_ROLES' | 'EDUCATION' | 'SKILLS_SUMMARY' | 'ROLE_GOALS' |
         'ADJACENT_ROLES' | 'GENERATE_RESUME' | 'COMPLETE';
  messages: Message[];
  extracted_data: ExtractedData;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ExtractedData {
  contact: ContactInfo;
  experiences: Experience[];
  skills: ExtractedSkill[];
  education: Education[];
  certifications: string[];
}
```

### ExtractedSkill
```typescript
interface ExtractedSkill {
  skill_name: string;
  category: string;
  evidence: string;
  confidence: 'high' | 'medium' | 'low';
}
```

---

## Testing Strategy

### Conversation Flow Tests
- Test each state transition in the conversation
- Verify graceful handling of edge cases (hesitant, rambling, emotional)
- Test skill extraction accuracy against sample conversations

### Integration Tests
- Full flow from landing → chat → skills → resume generation
- Verify extracted data persists correctly
- Test resume output quality

### User Acceptance Tests
- Test with users from each target segment (career changers, gig workers, etc.)
- Measure completion rates and drop-off points
- Gather feedback on conversation tone and helpfulness

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Conversation completion rate | >70% |
| Skills extracted per user | 8+ skills |
| Time to complete conversation | <10 minutes |
| Resume generation success | >95% |
| User satisfaction (survey) | >4/5 stars |
| Users who proceed to analyze a job | >50% |

---

## Implementation Checklist - Wave 1

### Frontend
- [ ] Create `resume-builder.html` landing page
- [ ] Create `resume-chat.html` chat interface
- [ ] Create `resume-chat.js` chat component
- [ ] Create `skills-analysis.html` dashboard
- [ ] Create `resume-builder.css` styles
- [ ] Add navigation links from profile-edit.html
- [ ] Implement sessionStorage for conversation state

### Backend
- [ ] Create `/api/resume-chat` endpoint
- [ ] Create conversation system prompt with skill taxonomy
- [ ] Implement skill extraction logic
- [ ] Create `/api/generate-resume-from-chat` endpoint
- [ ] Add resume generation from extracted data

### Testing
- [ ] Test conversation flow with all sample conversations
- [ ] Test skill extraction accuracy
- [ ] Test resume generation quality
- [ ] Test mobile responsiveness

---

## Dependencies

- **OpenAI API** - Already integrated for Claude/GPT calls
- **Skill Taxonomy** - `henryai-skill-taxonomy.json` (exists)
- **Adjacent Roles** - `henryai-adjacent-roles.json` (exists)
- **Sample Conversations** - For testing and prompt engineering

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Conversation goes off-track | System prompt includes redirection strategies |
| Users abandon mid-conversation | Auto-save progress, allow resume later |
| Skill extraction misses skills | Review and iterate on extraction prompts |
| Voice costs too high | Start text-only, add voice as opt-in premium |
| Users expect perfect resume | Set expectations that this is a starting point |

---

## Next Steps

1. **Wave 1 Implementation** - Start with landing page and chat interface
2. **Prompt Engineering** - Refine system prompts using sample conversations
3. **Beta Testing** - Test with 5-10 users from target segments
4. **Iterate** - Improve based on feedback before Wave 2
