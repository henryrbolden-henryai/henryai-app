# CONVERSATION HISTORY PERSISTENCE SPECIFICATION v1.0

**Date:** December 25, 2025
**Status:** DRAFT - Priority Implementation
**Purpose:** Phase 1.5 implementation guide for cross-session conversation persistence
**Validated By:** Beta user feedback (Alex, Legal field, 2+ weeks active)

---

## EXECUTIVE SUMMARY

This document specifies the Conversation History Persistence feature, a critical Phase 1.5 enhancement that enables Hey Henry conversations to persist across sessions. This is the foundation for all longitudinal intelligence features in Phase 2.

**User Problem (Validated):**
Beta user Alex had a 45-60 minute strategic conversation with Hey Henry. He logged out, returned the next morning to reread guidance, and the conversation was gone. He explicitly stated he expected Hey Henry to remember past conversations and reference them.

**Current Behavior:**
- Conversation persists across pages (sessionStorage)
- Conversation clears on browser close
- No way to access previous conversations

**Required Behavior:**
- Conversation persists across sessions (database)
- User can access previous conversations
- Hey Henry can reference past discussions (Tier 2)

---

## USER VALIDATION

### Beta Feedback (Alex, December 2025)

| Signal | Evidence |
|--------|----------|
| Deep engagement | 45-60 minutes of continuous chat with Hey Henry |
| Product-market fit | Chose to ask Hey Henry questions vs. contacting founder |
| Value recognition | "Very valuable tool. Everything in one place." |
| Memory expectation | Returned specifically to reread previous guidance |
| Trust sensitivity | Would subscribe but needs to see reliability first |

### Key Quote
> "That's why he went back to it this morning to reread something they were discussing."

He was treating Hey Henry as a strategic advisor whose past guidance was worth revisiting. That's exactly the relationship we want, but current implementation breaks it.

---

## REQUIREMENTS

### Tier 1: Persist Chat History (URGENT)

**Goal:** Users can scroll back through previous conversations across sessions.

**User Experience:**
1. User has conversation with Hey Henry
2. User logs out or closes browser
3. User returns (hours or days later)
4. Previous conversation is visible and scrollable
5. User can continue conversation or start fresh

**Technical Requirements:**
- Store full conversation threads per user in Supabase
- Load most recent conversation on login (if < 24 hours old)
- Provide option to continue previous or start new conversation
- Access to conversation history list (last 10-20 conversations)
- Auto-save after each message

### Tier 2: Contextual Memory (STRATEGIC)

**Goal:** Hey Henry actively references past conversations when relevant.

**User Experience:**
```
Hey Henry: "Last week you mentioned concerns about the salary range at Stripe. Did that change?"

Hey Henry: "You've been targeting Series B companies consistently. This role fits that pattern."

Hey Henry: "Remember when we discussed your positioning for enterprise SaaS? This role needs similar framing."
```

**Technical Requirements:**
- Generate conversation summaries for context injection
- Identify key facts, decisions, and concerns per user
- Reference past conversations naturally (not robotically)
- Prioritize recent and relevant context

---

## DATABASE SCHEMA

### Conversations Table

```sql
CREATE TABLE hey_henry_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    
    -- Metadata
    title TEXT, -- Auto-generated from first message or topic
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Status
    status TEXT DEFAULT 'active', -- 'active', 'archived', 'deleted'
    
    -- Indexes
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user ON hey_henry_conversations(user_id);
CREATE INDEX idx_conversations_updated ON hey_henry_conversations(updated_at DESC);
```

### Messages Table

```sql
CREATE TABLE hey_henry_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES hey_henry_conversations(id) NOT NULL,
    
    -- Message content
    role TEXT NOT NULL, -- 'user', 'henry'
    content TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Optional: For Tier 2 context extraction
    extracted_topics TEXT[],
    extracted_decisions TEXT[],
    extracted_concerns TEXT[],
    
    -- Indexes
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) 
        REFERENCES hey_henry_conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation ON hey_henry_messages(conversation_id);
CREATE INDEX idx_messages_created ON hey_henry_messages(created_at);
```

### Conversation Summaries Table (Tier 2)

```sql
CREATE TABLE hey_henry_conversation_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES hey_henry_conversations(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    
    -- Summary content
    summary TEXT NOT NULL,
    key_topics TEXT[],
    key_decisions TEXT[],
    key_concerns TEXT[],
    companies_discussed TEXT[],
    roles_discussed TEXT[],
    
    -- Metadata
    message_count INTEGER,
    generated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) 
        REFERENCES hey_henry_conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_summaries_user ON hey_henry_conversation_summaries(user_id);
```

---

## API ENDPOINTS

### Get Recent Conversations

```
GET /api/hey-henry/conversations
```

**Query Parameters:**
- `limit` (optional, default 10, max 20)
- `status` (optional, default 'active')

**Response:**
```json
{
    "conversations": [
        {
            "id": "uuid",
            "title": "Stripe PM Role Discussion",
            "started_at": "2025-12-24T10:30:00Z",
            "updated_at": "2025-12-24T11:15:00Z",
            "message_count": 24,
            "preview": "Let's analyze this Stripe PM role..."
        }
    ]
}
```

### Get Conversation Messages

```
GET /api/hey-henry/conversations/:id/messages
```

**Query Parameters:**
- `limit` (optional, default 50)
- `before` (optional, cursor for pagination)

**Response:**
```json
{
    "conversation_id": "uuid",
    "messages": [
        {
            "id": "uuid",
            "role": "user",
            "content": "Can you analyze this job description?",
            "created_at": "2025-12-24T10:30:00Z"
        },
        {
            "id": "uuid",
            "role": "henry",
            "content": "Alright, let's break this down...",
            "created_at": "2025-12-24T10:30:15Z"
        }
    ],
    "has_more": false
}
```

### Create/Continue Conversation

```
POST /api/hey-henry/conversations/:id/messages
```

**Request:**
```json
{
    "content": "What about the salary range?"
}
```

**Response:**
```json
{
    "user_message": {
        "id": "uuid",
        "role": "user",
        "content": "What about the salary range?",
        "created_at": "2025-12-24T11:20:00Z"
    },
    "henry_response": {
        "id": "uuid",
        "role": "henry",
        "content": "Based on the role and location...",
        "created_at": "2025-12-24T11:20:05Z"
    }
}
```

### Start New Conversation

```
POST /api/hey-henry/conversations
```

**Request:**
```json
{
    "initial_message": "I want to discuss my job search strategy"
}
```

**Response:**
```json
{
    "conversation": {
        "id": "uuid",
        "title": "Job Search Strategy",
        "started_at": "2025-12-25T09:00:00Z"
    },
    "henry_response": {
        "id": "uuid",
        "role": "henry",
        "content": "Let's talk strategy. What's your current situation?",
        "created_at": "2025-12-25T09:00:05Z"
    }
}
```

---

## FRONTEND IMPLEMENTATION

### Hey Henry Chat Component Updates

**On Component Load:**
1. Check for existing conversations via API
2. If recent conversation exists (< 24 hours), show continuation prompt
3. Load conversation history into chat view

**Continuation Prompt:**
```
"Welcome back! Want to continue where we left off, or start fresh?"

[Continue Previous] [Start Fresh]
```

**Chat History Access:**
- Add "Previous Conversations" link in Hey Henry header
- Show list of past conversations with date and preview
- Click to load full conversation
- Current conversation auto-saves on each message

### UI Components

**Conversation List View:**
```
Previous Conversations

[Dec 24] Stripe PM Role Discussion
"Let's analyze this Stripe PM role..."

[Dec 23] Resume Positioning Strategy  
"Here's how to reframe your experience..."

[Dec 20] Interview Prep for Uber
"For the hiring manager round, focus on..."
```

**Conversation Header:**
```
Hey Henry
[< Back to List] [New Conversation]

Stripe PM Role Discussion
Started Dec 24, 2025 | 24 messages
```

### Mobile Considerations

- Conversation list should be accessible via hamburger menu or swipe
- History loads efficiently (paginate older messages)
- Auto-save handles intermittent connectivity
- Works on iPhone (Alex's primary device)

---

## TIER 2: CONTEXTUAL MEMORY

### Implementation Approach

**Option A: Summary Injection**
- Generate conversation summary after each session ends
- Inject relevant summaries into Hey Henry's context
- Pros: Lower token usage, faster responses
- Cons: May miss nuance

**Option B: Key Facts Extraction**
- Extract key facts, decisions, concerns from each conversation
- Store as structured data
- Query relevant facts based on current context
- Pros: More precise, queryable
- Cons: More complex extraction logic

**Option C: Hybrid**
- Extract key facts for structured queries
- Generate summaries for broader context
- Use both based on conversation needs
- Pros: Best of both
- Cons: Most complex

**Recommendation:** Start with Option A (Summary Injection) for simplicity, evolve to Option C as usage patterns emerge.

### Context Injection Example

**When user analyzes a new role:**
```
System context injected to Hey Henry:

Recent conversation context for this user:
- Dec 24: Discussed Stripe PM role, user concerned about salary range being below expectations
- Dec 23: Refined resume positioning to emphasize cross-functional leadership
- Dec 20: Prepped for Uber interview, focused on stakeholder management stories
- User preference: Targeting Series B companies, prefers product roles over program management
```

**Hey Henry response with context:**
```
"This role at [Company] looks interesting. A few things stand out:

The scope is similar to that Stripe role we discussed, but the salary range here is 15% higher. That might address your concern about comp.

Your cross-functional positioning we worked on last week fits well here. They're emphasizing stakeholder alignment, which plays to your strengths."
```

### Privacy and Control

- Users can view what Hey Henry "remembers"
- Users can delete specific conversations or all history
- Users can disable contextual memory (Tier 2) while keeping history (Tier 1)
- Clear data retention policy (90 days default, configurable)

---

## MIGRATION PLAN

### Phase 1: Database Setup
1. Create tables in Supabase
2. Add indexes
3. Test with sample data

### Phase 2: API Implementation
1. Build conversation CRUD endpoints
2. Integrate with existing Hey Henry backend
3. Add message persistence to chat flow

### Phase 3: Frontend Integration
1. Update hey-henry.js to use new APIs
2. Add conversation list view
3. Implement continuation prompt
4. Add "Previous Conversations" access

### Phase 4: Tier 2 (Contextual Memory)
1. Build summary generation pipeline
2. Implement context injection
3. Test contextual references
4. Roll out to beta users

---

## TESTING CHECKLIST

### Tier 1: Persistence
- [ ] Conversation saves after each message
- [ ] Conversation loads on returning session
- [ ] "Continue" vs "Start Fresh" option works
- [ ] Previous conversations list displays correctly
- [ ] Clicking past conversation loads it
- [ ] Conversation title auto-generates
- [ ] Message timestamps display correctly
- [ ] Pagination works for long conversations
- [ ] Delete conversation works
- [ ] Mobile: history accessible and usable
- [ ] Mobile: auto-save handles connectivity issues

### Tier 2: Contextual Memory
- [ ] Summaries generate after session ends
- [ ] Context injection includes relevant history
- [ ] Hey Henry references past conversations naturally
- [ ] References are accurate (not hallucinated)
- [ ] User can view what Hey Henry "remembers"
- [ ] User can disable contextual memory
- [ ] Context doesn't bloat token usage excessively

---

## SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Conversation persistence rate | 100% of messages saved |
| History load time | < 1 second for recent conversation |
| User return rate | Increase in returning users within 24 hours |
| Continuation rate | 50%+ of returning users continue previous conversation |
| User satisfaction | "Hey Henry remembers our conversations" feedback |

---

## ANTI-PATTERNS

### Losing Context (NEVER)

**BAD:**
```
User: "What did we discuss about Stripe?"
Henry: "I don't have access to our previous conversations."
```

**GOOD:**
```
User: "What did we discuss about Stripe?"
Henry: "We talked about the PM role there on December 24th. You were concerned about the salary range being below your target. Want me to pull up the full conversation?"
```

### Robotic References (NEVER)

**BAD:**
```
Henry: "According to my records from conversation ID 12345 on December 24, 2025, you expressed concern about compensation."
```

**GOOD:**
```
Henry: "Last week you mentioned the Stripe salary felt low. This role pays better, might be worth a look."
```

### Over-Referencing (NEVER)

**BAD:**
```
Henry: "As we discussed before, and building on our previous conversation, remembering what you said last time..."
```

**GOOD:**
```
Henry: "This is similar to the Stripe role. Same concerns apply."
```

---

## RELATED DOCUMENTS

- HEY_HENRY_IMPLEMENTATION_SPEC_v2.1.md (Core Hey Henry spec)
- STRATEGIC_INTELLIGENCE_ENGINE_SPEC_v1.md (Phase 2, depends on this)

---

**END OF CONVERSATION HISTORY PERSISTENCE SPECIFICATION**

This is a priority implementation for Phase 1.5. The feature has been validated by beta user feedback and is a prerequisite for Phase 2 Strategic Intelligence features.
