# INTERVIEW DEBRIEF INTELLIGENCE SPECIFICATION v1.0

**Date:** December 25, 2025
**Status:** APPROVED - Ready for Implementation
**Purpose:** Complete the debrief intelligence loop so insights compound across interviews
**Estimated Effort:** 3-3.5 hours
**Dependencies:** Conversation History Persistence (Phase 1.5) - Complete

---

## EXECUTIVE SUMMARY

Current implementation prompts users to debrief but doesn't extract structured data or feed it back into interview prep. Users are encouraged to debrief, but the intelligence doesn't compound. This breaks the core value proposition: "Your coaching gets smarter over time."

**Current State:**
- Debriefs stored in localStorage with only: feeling, transcript, conversationHistory
- No structured extraction of questions, strengths, weaknesses, stories
- Interview prep does NOT pull from past debriefs
- No cross-interview pattern detection

**Required State:**
- Structured data extraction from every debrief
- Interview prep informed by past debriefs at same company
- Cross-interview pattern detection (weak areas, story usage, confidence trends)
- Story bank tracking with overuse alerts

---

## DATA MODEL

### What We Extract From Debriefs

| Data Point | Type | Description |
|------------|------|-------------|
| `interview_type` | string | 'recruiter', 'hiring_manager', 'technical', 'panel', 'final' |
| `interview_date` | date | When the interview occurred |
| `interviewer_name` | string | Optional, if mentioned |
| `duration_minutes` | integer | Approximate length |
| `rating_overall` | integer (1-5) | Overall self-assessment |
| `rating_confidence` | integer (1-5) | How confident they felt |
| `rating_preparation` | integer (1-5) | How prepared they felt |
| `questions_asked` | array | Questions they remember being asked |
| `question_categories` | array | Categories: behavioral, technical, motivation, culture, situational, salary |
| `stumbles` | array | Questions or moments where they struggled |
| `wins` | array | Moments that went well |
| `stories_used` | array | Examples/stories they told |
| `interviewer_signals` | object | Engagement level, red flags, next steps mentioned |
| `key_insights` | array | Hey Henry's extracted insights |
| `improvement_areas` | array | Specific areas to work on |

---

## HOW WE LEVERAGE DEBRIEF DATA

### 1. Same-Company Interview Prep

When user has upcoming interview at a company where they've already interviewed:

| Debrief Data | How Hey Henry Uses It |
|--------------|----------------------|
| Questions asked in earlier rounds | "They asked about X in recruiter screen. Expect deeper dive on that with HM." |
| Stumbles | "You stumbled on salary expectations last round. Here's a tighter answer." |
| Interviewer signals | "Recruiter seemed skeptical about remote work. Be ready to address that again." |
| Stories that landed | "Your Uber launch story resonated. Use it again if relevant." |

### 2. Cross-Company Pattern Detection

After 3+ debriefs across any companies:

| Pattern | Detection Logic | Hey Henry Response |
|---------|-----------------|-------------------|
| Weak question category | Same category rated low 3+ times | "You've struggled with 'why this company' in 3 interviews. Let's fix that permanently." |
| Answer length | Average response time > 2 min | "Your answers are running long. Tighten to 90 seconds." |
| Story overuse | Same story used 3+ times | "You've used the Uber launch story 4 times. Let's develop 2-3 alternatives." |
| Confidence trajectory | Track confidence rating over time | "Your confidence has improved from 2.5 to 4.0 over 6 interviews." |
| Stage-specific drops | Consistently fail at same stage | "You keep reaching HM rounds but not converting. Something's happening there." |

### 3. Pre-Interview Prep Generation

When user requests interview prep, Hey Henry builds it from:

| Source | What It Informs |
|--------|-----------------|
| Past debriefs at same company | Company-specific prep, known questions, interviewer style |
| Past debriefs for same role type | Common questions for PM/Eng/Legal roles |
| Identified stumbles | Targeted practice on weak areas |
| Effective stories | Recommended examples to use |
| Pattern weaknesses | Proactive coaching on recurring issues |

### 4. Post-Interview Learning

After each debrief:

| Analysis | Output |
|----------|--------|
| Compare to prep | "You prepped X but they asked Y. Adjusting for next time." |
| Update story bank | Add new stories that worked, flag overused ones |
| Refine question predictions | Weight questions that actually came up |
| Track outcome correlation | Which prep elements correlate with advancing? |

---

## DATABASE SCHEMA

### Table: `interview_debriefs`

```sql
CREATE TABLE interview_debriefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES candidate_profiles(user_id) NOT NULL,
    application_id UUID REFERENCES applications(id),
    
    -- Interview metadata
    company TEXT NOT NULL,
    role TEXT,
    interview_type TEXT NOT NULL,
    interview_date DATE,
    interviewer_name TEXT,
    duration_minutes INTEGER,
    
    -- Self-ratings (1-5)
    rating_overall INTEGER CHECK (rating_overall BETWEEN 1 AND 5),
    rating_confidence INTEGER CHECK (rating_confidence BETWEEN 1 AND 5),
    rating_preparation INTEGER CHECK (rating_preparation BETWEEN 1 AND 5),
    
    -- Structured content (JSONB)
    questions_asked JSONB DEFAULT '[]',
    question_categories JSONB DEFAULT '[]',
    stumbles JSONB DEFAULT '[]',
    wins JSONB DEFAULT '[]',
    stories_used JSONB DEFAULT '[]',
    interviewer_signals JSONB DEFAULT '{}',
    
    -- AI-generated insights
    key_insights JSONB DEFAULT '[]',
    improvement_areas JSONB DEFAULT '[]',
    
    -- Raw data
    raw_conversation TEXT,
    
    -- Outcome tracking
    outcome TEXT, -- 'advanced', 'rejected', 'pending', 'ghosted'
    outcome_updated_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_debriefs_user ON interview_debriefs(user_id);
CREATE INDEX idx_debriefs_company ON interview_debriefs(company);
CREATE INDEX idx_debriefs_type ON interview_debriefs(interview_type);
CREATE INDEX idx_debriefs_application ON interview_debriefs(application_id);

-- RLS
ALTER TABLE interview_debriefs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own debriefs"
    ON interview_debriefs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own debriefs"
    ON interview_debriefs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own debriefs"
    ON interview_debriefs FOR UPDATE
    USING (auth.uid() = user_id);
```

### Table: `user_story_bank`

```sql
CREATE TABLE user_story_bank (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES candidate_profiles(user_id) NOT NULL,
    
    -- Story content
    story_name TEXT NOT NULL,
    story_summary TEXT,
    story_context TEXT, -- When to use this story
    
    -- Categorization
    demonstrates TEXT[], -- ['leadership', 'problem_solving', 'cross_functional']
    best_for_questions TEXT[], -- ['tell me about a time', 'conflict resolution']
    
    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    effectiveness_avg DECIMAL(3,2),
    interviews_used_in UUID[], -- References to interview_debriefs
    
    -- Status
    status TEXT DEFAULT 'active', -- 'active', 'overused', 'retired'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_stories_user ON user_story_bank(user_id);
CREATE INDEX idx_stories_status ON user_story_bank(status);

-- RLS
ALTER TABLE user_story_bank ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own stories"
    ON user_story_bank FOR ALL
    USING (auth.uid() = user_id);
```

---

## STRUCTURED EXTRACTION

### Extraction Trigger

At end of debrief conversation (detected by Hey Henry), call extraction function to parse conversation and populate structured fields.

### Extraction Prompt

```python
extraction_prompt = """
Analyze this interview debrief conversation and extract structured data.

CONVERSATION:
{debrief_conversation}

COMPANY: {company}
ROLE: {role}

Extract the following as JSON:
{
    "interview_type": "recruiter|hiring_manager|technical|panel|final",
    "interview_date": "YYYY-MM-DD or null",
    "interviewer_name": "name or null",
    "duration_minutes": number or null,
    "rating_overall": 1-5,
    "rating_confidence": 1-5,
    "rating_preparation": 1-5,
    "questions_asked": ["question 1", "question 2"],
    "question_categories": ["behavioral", "technical", "motivation", "culture", "situational", "salary"],
    "stumbles": [{"question": "...", "what_went_wrong": "...", "better_answer": "..."}],
    "wins": [{"moment": "...", "why_it_worked": "..."}],
    "stories_used": [{"story_name": "...", "context": "...", "effectiveness": 1-5}],
    "interviewer_signals": {
        "seemed_engaged": true/false,
        "asked_followups": true/false,
        "mentioned_next_steps": true/false,
        "red_flags": ["flag 1", "flag 2"]
    },
    "key_insights": ["insight 1", "insight 2"],
    "improvement_areas": ["area 1", "area 2"]
}

RULES:
- Only include fields where information was explicitly provided
- Infer interview_type from context if not stated
- Categorize questions into standard categories
- Extract story names as short, memorable labels (e.g., "Uber launch under pressure")
- Key insights should be actionable observations
- Return valid JSON only, no markdown or explanation
"""
```

---

## INTERVIEW PREP INTEGRATION

### Update InterviewPrepRequest Model

```python
class InterviewPrepRequest(BaseModel):
    resume_text: str
    job_description: str
    company: str
    role: str
    interview_type: Optional[str] = None
    
    # NEW: Past debrief data
    past_debriefs: Optional[List[Dict[str, Any]]] = None
    story_bank: Optional[List[Dict[str, Any]]] = None
    cross_interview_patterns: Optional[Dict[str, Any]] = None
```

### Frontend: Pull Debriefs Before Prep Request

```javascript
async function getRelevantDebriefs(company, role) {
    // Get debriefs for same company
    const companyDebriefs = await HenryData.getDebriefsByCompany(company);
    
    // Get debriefs for similar roles (same function)
    const roleDebriefs = await HenryData.getDebriefsByRoleType(role);
    
    // Get user's story bank
    const storyBank = await HenryData.getStoryBank();
    
    // Calculate cross-interview patterns
    const allDebriefs = await HenryData.getAllDebriefs();
    const patterns = calculatePatterns(allDebriefs);
    
    return {
        past_debriefs: [...companyDebriefs, ...roleDebriefs],
        story_bank: storyBank,
        cross_interview_patterns: patterns
    };
}
```

### Backend: Build Debrief Context for Prep Prompt

```python
def build_interview_prep_context(request: InterviewPrepRequest) -> str:
    context = ""
    
    if not request.past_debriefs:
        return context
    
    # Same-company debriefs
    company_debriefs = [d for d in request.past_debriefs if d.get('company') == request.company]
    if company_debriefs:
        context += f"\n\nPREVIOUS INTERVIEWS AT {request.company.upper()}:\n"
        for d in company_debriefs:
            context += f"- {d['interview_type'].title()}: "
            if d.get('stumbles'):
                stumble_questions = [s.get('question', 'unknown') for s in d['stumbles'][:2]]
                context += f"Struggled with: {', '.join(stumble_questions)}. "
            if d.get('wins'):
                win_moments = [w.get('moment', 'unknown') for w in d['wins'][:2]]
                context += f"Strong on: {', '.join(win_moments)}. "
            if d.get('interviewer_signals', {}).get('red_flags'):
                context += f"Red flags noted: {', '.join(d['interviewer_signals']['red_flags'][:2])}. "
            context += "\n"
    
    # Cross-interview patterns
    patterns = request.cross_interview_patterns or {}
    if patterns.get('weak_categories'):
        context += f"\nRECURRING WEAK AREAS (address these proactively):\n"
        for cat in patterns['weak_categories']:
            context += f"- {cat['category']}: struggled in {cat['count']} of {cat['total']} interviews ({cat['rate']}%)\n"
    
    # Confidence trend
    if patterns.get('confidence_trend'):
        trend = patterns['confidence_trend']
        if trend['direction'] == 'improving':
            context += f"\nCONFIDENCE TREND: Improving from {trend['early_avg']} to {trend['recent_avg']} (acknowledge this progress)\n"
        elif trend['direction'] == 'declining':
            context += f"\nCONFIDENCE TREND: Declining from {trend['early_avg']} to {trend['recent_avg']} (address this supportively)\n"
    
    # Story bank
    if request.story_bank:
        overused = [s for s in request.story_bank if s.get('times_used', 0) >= 3]
        if overused:
            context += f"\nOVERUSED STORIES (suggest alternatives):\n"
            for s in overused:
                context += f"- '{s['story_name']}' used {s['times_used']} times\n"
        
        effective = [s for s in request.story_bank if s.get('effectiveness_avg', 0) >= 4]
        if effective:
            context += f"\nHIGH-IMPACT STORIES (recommend using):\n"
            for s in effective[:3]:
                context += f"- '{s['story_name']}': {s.get('story_context', 'No context')}\n"
    
    return context
```

### System Prompt Addition for Debrief-Aware Prep

```
=== DEBRIEF-INFORMED PREP ===

You have context from the candidate's previous interviews. USE THIS INTELLIGENCE:

{debrief_context}

REQUIRED BEHAVIORS:
1. If they struggled with a question type before, proactively address it
2. If they have overused stories, suggest alternatives
3. If they have a weak category, include targeted practice
4. Reference specific past performance: "In your recruiter screen, you mentioned X. Build on that."
5. If confidence is improving, acknowledge it. If declining, address it supportively.

Do NOT:
- Ignore the debrief data
- Give generic prep that doesn't account for their history
- Recommend stories they've overused
- Pretend you don't know about their past interviews
```

---

## CROSS-INTERVIEW PATTERN DETECTION

### Pattern Calculation Function

```javascript
function calculatePatterns(debriefs) {
    if (!debriefs || debriefs.length < 3) return null;
    
    const patterns = {
        weak_categories: [],
        strong_categories: [],
        story_usage: [],
        confidence_trend: null,
        total_debriefs: debriefs.length
    };
    
    // Aggregate question categories and performance
    const categoryPerformance = {};
    debriefs.forEach(d => {
        (d.question_categories || []).forEach(cat => {
            if (!categoryPerformance[cat]) {
                categoryPerformance[cat] = { total: 0, struggles: 0 };
            }
            categoryPerformance[cat].total++;
            
            // Check if stumbled on this category
            const stumbledOnCategory = (d.stumbles || []).some(s => {
                const question = (s.question || '').toLowerCase();
                return question.includes(cat.toLowerCase()) || 
                       (d.question_categories || []).includes(cat);
            });
            if (stumbledOnCategory) {
                categoryPerformance[cat].struggles++;
            }
        });
    });
    
    // Identify weak categories (struggled 50%+ of time, minimum 2 occurrences)
    Object.entries(categoryPerformance).forEach(([cat, data]) => {
        const struggleRate = data.struggles / data.total;
        if (struggleRate >= 0.5 && data.total >= 2) {
            patterns.weak_categories.push({
                category: cat,
                count: data.struggles,
                total: data.total,
                rate: Math.round(struggleRate * 100)
            });
        } else if (struggleRate <= 0.2 && data.total >= 2) {
            patterns.strong_categories.push({
                category: cat,
                count: data.total - data.struggles,
                total: data.total
            });
        }
    });
    
    // Sort weak categories by struggle rate
    patterns.weak_categories.sort((a, b) => b.rate - a.rate);
    
    // Track story usage
    const storyCount = {};
    const storyEffectiveness = {};
    debriefs.forEach(d => {
        (d.stories_used || []).forEach(s => {
            const name = s.story_name || s.name;
            if (name) {
                storyCount[name] = (storyCount[name] || 0) + 1;
                if (s.effectiveness) {
                    if (!storyEffectiveness[name]) {
                        storyEffectiveness[name] = [];
                    }
                    storyEffectiveness[name].push(s.effectiveness);
                }
            }
        });
    });
    
    patterns.story_usage = Object.entries(storyCount)
        .map(([name, count]) => ({
            name,
            count,
            avg_effectiveness: storyEffectiveness[name] 
                ? (storyEffectiveness[name].reduce((a, b) => a + b, 0) / storyEffectiveness[name].length).toFixed(1)
                : null,
            overused: count >= 3
        }))
        .sort((a, b) => b.count - a.count);
    
    // Confidence trend
    const sortedDebriefs = debriefs
        .filter(d => d.rating_confidence)
        .sort((a, b) => new Date(a.interview_date || a.created_at) - new Date(b.interview_date || b.created_at));
    
    if (sortedDebriefs.length >= 3) {
        const midpoint = Math.ceil(sortedDebriefs.length / 2);
        const firstHalf = sortedDebriefs.slice(0, midpoint);
        const secondHalf = sortedDebriefs.slice(midpoint);
        
        const firstAvg = firstHalf.reduce((sum, d) => sum + d.rating_confidence, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((sum, d) => sum + d.rating_confidence, 0) / secondHalf.length;
        
        const difference = secondAvg - firstAvg;
        
        patterns.confidence_trend = {
            direction: difference > 0.3 ? 'improving' : difference < -0.3 ? 'declining' : 'stable',
            early_avg: Math.round(firstAvg * 10) / 10,
            recent_avg: Math.round(secondAvg * 10) / 10,
            change: Math.round(difference * 10) / 10
        };
    }
    
    return patterns;
}
```

---

## API ENDPOINTS

### POST /api/debriefs/extract

Extract structured data from debrief conversation.

**Request:**
```python
class DebriefExtractionRequest(BaseModel):
    conversation: str  # Raw conversation text
    company: str
    role: str
    application_id: Optional[str] = None
```

**Response:**
```python
class DebriefExtractionResponse(BaseModel):
    structured_data: Dict[str, Any]  # All extracted fields
    insights: List[str]  # Immediate insights to surface
    story_bank_updates: List[Dict]  # New or updated stories
```

### GET /api/debriefs

Get user's debriefs with optional filters.

**Query Parameters:**
- `company` (optional): Filter by company name
- `interview_type` (optional): Filter by type
- `limit` (optional, default 10): Number to return
- `include_patterns` (optional, default false): Include cross-interview patterns

**Response:**
```python
class DebriefListResponse(BaseModel):
    debriefs: List[Dict[str, Any]]
    patterns: Optional[Dict[str, Any]]  # If include_patterns=true
    total_count: int
```

### GET /api/debriefs/patterns

Get cross-interview pattern analysis.

**Response:**
```python
class PatternAnalysisResponse(BaseModel):
    weak_categories: List[Dict]
    strong_categories: List[Dict]
    story_usage: List[Dict]
    confidence_trend: Optional[Dict]
    total_debriefs: int
    insights: List[str]  # Human-readable pattern insights
```

### GET /api/story-bank

Get user's story bank with usage stats.

**Response:**
```python
class StoryBankResponse(BaseModel):
    stories: List[Dict[str, Any]]
    overused_count: int
    high_impact_count: int
```

### POST /api/story-bank

Add or update a story.

**Request:**
```python
class StoryBankRequest(BaseModel):
    story_name: str
    story_summary: Optional[str]
    story_context: Optional[str]
    demonstrates: Optional[List[str]]
    best_for_questions: Optional[List[str]]
```

---

## SUPABASE CLIENT FUNCTIONS

Add to `frontend/js/supabase-client.js`:

```javascript
// =========================================================================
// INTERVIEW DEBRIEFS
// =========================================================================

async createDebrief(data) {
    const { data: debrief, error } = await supabase
        .from('interview_debriefs')
        .insert([{ user_id: this.userId, ...data }])
        .select()
        .single();
    
    if (error) throw error;
    return debrief;
},

async getDebriefs(filters = {}) {
    let query = supabase
        .from('interview_debriefs')
        .select('*')
        .eq('user_id', this.userId)
        .order('created_at', { ascending: false });
    
    if (filters.company) {
        query = query.ilike('company', `%${filters.company}%`);
    }
    if (filters.interview_type) {
        query = query.eq('interview_type', filters.interview_type);
    }
    if (filters.limit) {
        query = query.limit(filters.limit);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
},

async getDebriefsByCompany(company) {
    return this.getDebriefs({ company });
},

async getDebriefsByRoleType(roleType) {
    // This would need role categorization logic
    // For now, return all debriefs and filter client-side
    return this.getDebriefs({});
},

async getAllDebriefs() {
    return this.getDebriefs({ limit: 50 });
},

async updateDebrief(id, data) {
    const { data: debrief, error } = await supabase
        .from('interview_debriefs')
        .update({ ...data, updated_at: new Date().toISOString() })
        .eq('id', id)
        .eq('user_id', this.userId)
        .select()
        .single();
    
    if (error) throw error;
    return debrief;
},

async updateDebriefOutcome(id, outcome) {
    return this.updateDebrief(id, {
        outcome,
        outcome_updated_at: new Date().toISOString()
    });
},

// =========================================================================
// STORY BANK
// =========================================================================

async getStoryBank() {
    const { data, error } = await supabase
        .from('user_story_bank')
        .select('*')
        .eq('user_id', this.userId)
        .order('times_used', { ascending: false });
    
    if (error) throw error;
    return data;
},

async addStory(story) {
    const { data, error } = await supabase
        .from('user_story_bank')
        .insert([{ user_id: this.userId, ...story }])
        .select()
        .single();
    
    if (error) throw error;
    return data;
},

async updateStoryUsage(storyId, interviewId, effectiveness) {
    // Get current story
    const { data: story, error: fetchError } = await supabase
        .from('user_story_bank')
        .select('*')
        .eq('id', storyId)
        .single();
    
    if (fetchError) throw fetchError;
    
    // Calculate new effectiveness average
    const currentAvg = story.effectiveness_avg || 0;
    const currentCount = story.times_used || 0;
    const newAvg = ((currentAvg * currentCount) + effectiveness) / (currentCount + 1);
    
    // Update interviews used in
    const interviewsUsedIn = story.interviews_used_in || [];
    if (!interviewsUsedIn.includes(interviewId)) {
        interviewsUsedIn.push(interviewId);
    }
    
    // Determine status
    const newTimesUsed = currentCount + 1;
    const status = newTimesUsed >= 4 ? 'overused' : 'active';
    
    const { data: updated, error } = await supabase
        .from('user_story_bank')
        .update({
            times_used: newTimesUsed,
            last_used_at: new Date().toISOString(),
            effectiveness_avg: Math.round(newAvg * 100) / 100,
            interviews_used_in: interviewsUsedIn,
            status,
            updated_at: new Date().toISOString()
        })
        .eq('id', storyId)
        .select()
        .single();
    
    if (error) throw error;
    return updated;
},

async retireStory(storyId) {
    const { data, error } = await supabase
        .from('user_story_bank')
        .update({
            status: 'retired',
            updated_at: new Date().toISOString()
        })
        .eq('id', storyId)
        .eq('user_id', this.userId)
        .select()
        .single();
    
    if (error) throw error;
    return data;
}
```

---

## HEY HENRY INTEGRATION

### Debrief Conversation End Detection

Add to `hey-henry.js`:

```javascript
function isDebriefConversationComplete(messages) {
    // Check if this was a debrief conversation that's reached a natural end
    const hasDebriefContext = messages.some(m => 
        m.content?.toLowerCase().includes('debrief') ||
        m.content?.toLowerCase().includes('how did the interview go') ||
        m.content?.toLowerCase().includes('tell me about your interview')
    );
    
    if (!hasDebriefContext) return false;
    
    // Check for wrap-up signals in last few messages
    const recentMessages = messages.slice(-3);
    const wrapUpSignals = [
        'anything else',
        'good luck',
        'let me know how',
        'you\'re ready',
        'sounds good',
        'thanks henry',
        'that helps'
    ];
    
    return recentMessages.some(m => 
        wrapUpSignals.some(signal => 
            m.content?.toLowerCase().includes(signal)
        )
    );
}
```

### Post-Debrief Extraction Trigger

```javascript
async function handleDebriefComplete(conversationHistory, company, role, applicationId) {
    try {
        // Call extraction endpoint
        const response = await fetch('/api/debriefs/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation: conversationHistory.map(m => `${m.role}: ${m.content}`).join('\n'),
                company,
                role,
                application_id: applicationId
            })
        });
        
        const result = await response.json();
        
        // Store structured debrief
        await HenryData.createDebrief({
            company,
            role,
            application_id: applicationId,
            ...result.structured_data,
            raw_conversation: JSON.stringify(conversationHistory)
        });
        
        // Update story bank if new stories extracted
        for (const story of result.story_bank_updates || []) {
            await HenryData.addStory(story);
        }
        
        // Surface immediate insights
        if (result.insights?.length > 0) {
            return result.insights;
        }
        
        return null;
    } catch (error) {
        console.error('Debrief extraction failed:', error);
        return null;
    }
}
```

### Pattern Insight Surfacing

After debrief is complete, Hey Henry should check for patterns:

```javascript
async function checkForPatternInsights() {
    const debriefs = await HenryData.getAllDebriefs();
    if (debriefs.length < 3) return null;
    
    const patterns = calculatePatterns(debriefs);
    const insights = [];
    
    // Weak category alert
    if (patterns.weak_categories?.length > 0) {
        const worst = patterns.weak_categories[0];
        if (worst.count >= 3) {
            insights.push(
                `I've noticed you've struggled with "${worst.category}" questions in ${worst.count} of your last ${worst.total} interviews. Want to work on a stronger approach?`
            );
        }
    }
    
    // Story overuse alert
    const overusedStories = patterns.story_usage?.filter(s => s.overused);
    if (overusedStories?.length > 0) {
        const story = overusedStories[0];
        insights.push(
            `You've used your "${story.name}" story ${story.count} times now. It might be time to develop some alternatives so you don't sound rehearsed.`
        );
    }
    
    // Confidence trend
    if (patterns.confidence_trend?.direction === 'improving') {
        insights.push(
            `Your confidence has improved from ${patterns.confidence_trend.early_avg} to ${patterns.confidence_trend.recent_avg} over your recent interviews. The prep is working.`
        );
    } else if (patterns.confidence_trend?.direction === 'declining') {
        insights.push(
            `I've noticed your confidence ratings have dipped recently. Let's talk about what's happening and how to get back on track.`
        );
    }
    
    return insights.length > 0 ? insights : null;
}
```

---

## TESTING CHECKLIST

### Extraction
- [ ] Debrief conversation triggers extraction at natural end
- [ ] Structured data correctly parsed from conversation
- [ ] All fields extracted when information is present
- [ ] Missing fields handled gracefully (null, not error)
- [ ] Data persists to Supabase interview_debriefs table
- [ ] Raw conversation stored for reference

### Interview Prep Integration
- [ ] Prep request includes past_debriefs when available
- [ ] Same-company debriefs surfaced in prep context
- [ ] Stumbles from past rounds addressed proactively
- [ ] Weak categories included in prep focus
- [ ] Overused stories flagged with alternatives suggested
- [ ] High-impact stories recommended

### Pattern Detection
- [ ] Patterns calculated after 3+ debriefs
- [ ] Weak categories identified correctly (50%+ struggle rate)
- [ ] Story usage tracked accurately
- [ ] Confidence trend calculated (improving/declining/stable)
- [ ] Insights generated and surfaced to user

### Story Bank
- [ ] Stories extracted from debriefs automatically
- [ ] Usage count increments on each use
- [ ] Effectiveness ratings tracked and averaged
- [ ] Overused status set at 4+ uses
- [ ] Retire story functionality works

### Hey Henry Behaviors
- [ ] Surfaces pattern insights after debrief: "This is the 3rd time..."
- [ ] References past debriefs in prep: "In your recruiter screen..."
- [ ] Recommends story alternatives when overused
- [ ] Acknowledges confidence improvements
- [ ] Addresses confidence declines supportively
- [ ] Does NOT give generic prep when debrief data exists

---

## SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Debriefs with structured data extracted | 90%+ of completed debriefs |
| Prep sessions using debrief data | 100% when relevant debriefs exist |
| Pattern insights surfaced | After every 3rd+ debrief |
| Story overuse alerts | When story used 3+ times |
| User feedback | "Prep felt more relevant to my history" |

---

## IMPLEMENTATION SEQUENCE

| Step | Task | Effort |
|------|------|--------|
| 1 | Create database tables (interview_debriefs, user_story_bank) | 15 min |
| 2 | Add Supabase client functions | 30 min |
| 3 | Build extraction endpoint (POST /api/debriefs/extract) | 45 min |
| 4 | Add debrief end detection + extraction trigger in hey-henry.js | 30 min |
| 5 | Implement pattern calculation function | 30 min |
| 6 | Update interview prep to pull debriefs + inject context | 30 min |
| 7 | Add pattern insight surfacing after debriefs | 20 min |
| 8 | Testing full flow | 30 min |

**Total Estimated Effort: 3.5 hours**

---

## ANTI-PATTERNS

### Ignoring Debrief Data (NEVER)

**BAD:**
```
User: "Help me prep for my HM interview at Stripe"
Henry: "Here are common hiring manager questions..."
(ignores that user already interviewed at Stripe and stumbled on salary questions)
```

**GOOD:**
```
User: "Help me prep for my HM interview at Stripe"
Henry: "Based on your recruiter screen there, you mentioned struggling with 
the salary expectations question. Let's nail that before the HM round. 
Here's a tighter answer..."
```

### Generic Pattern Insights (NEVER)

**BAD:**
```
Henry: "You might want to work on your interview skills."
```

**GOOD:**
```
Henry: "You've struggled with 'why this company' questions in 3 of your 
last 4 interviews. Let's build a framework you can adapt to any company."
```

### Missing the Confidence Trend (NEVER)

**BAD:**
```
(User's confidence has dropped from 4.0 to 2.5 over 5 interviews)
Henry: "Good luck with your next interview!"
```

**GOOD:**
```
Henry: "I've noticed your confidence ratings have dipped over your last 
few interviews. That's normal in a tough market. Let's talk about what's 
happening and rebuild some momentum."
```

---

## RELATED DOCUMENTS

- HEY_HENRY_IMPLEMENTATION_SPEC_v2.2.md
- CONVERSATION_HISTORY_SPEC_v1.md
- STRATEGIC_INTELLIGENCE_ENGINE_SPEC_v1.md

---

**END OF SPECIFICATION**

This document provides the complete implementation guide for the Interview Debrief Intelligence system. The data model is locked, integration points are defined, and testing criteria will verify the intelligence loop is closed.
