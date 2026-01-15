# LinkedIn Network Intelligence Enhancement Spec

**Version:** 1.0  
**Date:** January 7, 2026  
**For:** Claude Code Implementation  
**Feature Tier:** Principal ($69/mo) and above for basic network matching; Partner ($129/mo) and above for Hey Henry integration

---

## Problem Statement

The current LinkedIn CSV parsing in `outreach.html` has two critical issues:

1. **Broken CSV parsing**: The naive `split(',')` approach breaks on commas inside quoted fields (e.g., "Director, Engineering" or "Google, LLC"), corrupting row data and causing match failures.

2. **Underutilized data**: LinkedIn exports seven fields, but we only display three. We're leaving valuable outreach intelligence on the table.

---

## LinkedIn CSV Export Structure

Every LinkedIn connection export contains these seven fields (universal across all users):

| Field | Availability | Example |
|-------|-------------|---------|
| First Name | Always | Jennifer |
| Last Name | Always | Coffin |
| URL | Always | https://www.linkedin.com/in/jennifervivier |
| Email Address | Sometimes (user-shared only) | ada.dummer@gmail.com |
| Company | Usually (blank if not set) | Veeam Software |
| Position | Usually (blank if not set) | Senior Recruiting & Sourcing Leader, AMERS |
| Connected On | Always | 19 Nov 2025 |

**Not available (do not attempt to extract):**
- Prior employers
- Mutual connections count
- Profile photos
- Connection notes
- 2nd/3rd degree connections

---

## Part 1: CSV Parsing Fix

### Current (Broken)
```javascript
function parseLinkedInCSV(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const connections = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
        // THIS BREAKS ON: "John","Smith","Director, Product","Google, LLC"
        // ...
    }
}
```

### Required Fix

**Option A: Use PapaParse (Recommended)**

Add to `<head>`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
```

Replace function:
```javascript
function parseLinkedInCSV(csv) {
    const result = Papa.parse(csv, {
        header: true,
        skipEmptyLines: true,
        transformHeader: h => h.trim()
    });
    return result.data.filter(row => row['First Name'] || row['Last Name']);
}
```

**Option B: Proper CSV Parser (No Dependency)**

```javascript
function parseLinkedInCSV(csv) {
    const lines = [];
    let currentLine = '';
    let insideQuotes = false;
    
    for (let i = 0; i < csv.length; i++) {
        const char = csv[i];
        if (char === '"') {
            insideQuotes = !insideQuotes;
            currentLine += char;
        } else if (char === '\n' && !insideQuotes) {
            if (currentLine.trim()) lines.push(currentLine);
            currentLine = '';
        } else {
            currentLine += char;
        }
    }
    if (currentLine.trim()) lines.push(currentLine);
    
    const parseRow = (row) => {
        const values = [];
        let current = '';
        let inQuotes = false;
        for (let i = 0; i < row.length; i++) {
            const char = row[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        values.push(current.trim());
        return values;
    };
    
    const headers = parseRow(lines[0]);
    const connections = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = parseRow(lines[i]);
        if (values.length < 2) continue;
        
        const connection = {};
        headers.forEach((header, index) => {
            connection[header] = values[index] || '';
        });
        
        if (connection['First Name'] || connection['Last Name']) {
            connections.push(connection);
        }
    }
    
    return connections;
}
```

---

## Part 2: Enhanced Connection Card Design

### Data Model

```typescript
interface ProcessedConnection {
    // Display fields
    name: string;                    // "Jennifer Coffin"
    title: string;                   // "Senior Recruiting & Sourcing Leader, AMERS"
    company: string;                 // "Veeam Software"
    linkedinUrl: string;             // "https://www.linkedin.com/in/jennifervivier"
    email: string | null;            // "ada.dummer@gmail.com" or null
    connectedOn: Date;               // Date object
    
    // Computed fields
    connectionAge: number;           // Days since connection
    connectionRecency: 'recent' | 'warm' | 'cold';  // <90 days, 90-365 days, >365 days
    seniorityLevel: 'executive' | 'senior' | 'mid' | 'entry' | 'unknown';
    isRecruiter: boolean;            // Title contains recruiting keywords
    isTalentAcquisition: boolean;    // Broader TA function
    isHiringManager: boolean;        // Manager/Director/VP/Head without recruiting
    relevanceScore: number;          // 0-100 computed score
}
```

### Seniority Detection

```javascript
function detectSeniority(title) {
    const titleLower = title.toLowerCase();
    
    const executivePatterns = [
        /\b(ceo|cfo|cto|coo|cmo|cpo|chief)\b/,
        /\b(president|founder|owner|partner)\b/,
        /\bvp\b/, /\bvice president\b/,
        /\bevp\b/, /\bsvp\b/
    ];
    
    const seniorPatterns = [
        /\b(director|head of|principal)\b/,
        /\bsenior\b/, /\bsr\.?\b/,
        /\blead\b/, /\bstaff\b/
    ];
    
    const midPatterns = [
        /\bmanager\b/,
        /\bspecialist\b/,
        /\banalyst\b/,
        /\bconsultant\b/
    ];
    
    const entryPatterns = [
        /\b(associate|coordinator|assistant|intern|junior|jr\.?)\b/,
        /\bentry level\b/
    ];
    
    if (executivePatterns.some(p => p.test(titleLower))) return 'executive';
    if (seniorPatterns.some(p => p.test(titleLower))) return 'senior';
    if (midPatterns.some(p => p.test(titleLower))) return 'mid';
    if (entryPatterns.some(p => p.test(titleLower))) return 'entry';
    return 'unknown';
}
```

### Recruiter Detection

```javascript
function detectRecruiterType(title) {
    const titleLower = title.toLowerCase();
    
    const recruiterKeywords = [
        'recruiter', 'recruiting', 'recruitment',
        'sourcer', 'sourcing',
        'talent acquisition', 'talent partner',
        'headhunter', 'executive search'
    ];
    
    const taKeywords = [
        'talent', 'people operations', 'hr business partner',
        'human resources', 'hrbp'
    ];
    
    const isRecruiter = recruiterKeywords.some(k => titleLower.includes(k));
    const isTalentAcquisition = taKeywords.some(k => titleLower.includes(k));
    
    return { isRecruiter, isTalentAcquisition };
}
```

### Connection Recency

```javascript
function calculateRecency(connectedOnStr) {
    // Parse "19 Nov 2025" format
    const date = new Date(connectedOnStr);
    const now = new Date();
    const daysDiff = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    return {
        connectionAge: daysDiff,
        connectionRecency: daysDiff < 90 ? 'recent' : daysDiff < 365 ? 'warm' : 'cold'
    };
}
```

### Relevance Scoring

```javascript
function calculateRelevance(connection, targetCompany, targetRole) {
    let score = 0;
    
    // Direct company match (highest value)
    if (connection.company.toLowerCase().includes(targetCompany.toLowerCase())) {
        score += 50;
    }
    
    // Recruiter at target company (very high value)
    if (score >= 50 && connection.isRecruiter) {
        score += 25;
    }
    
    // Seniority bonus for non-recruiters (potential hiring managers)
    if (!connection.isRecruiter) {
        if (connection.seniorityLevel === 'executive') score += 15;
        if (connection.seniorityLevel === 'senior') score += 10;
    }
    
    // Connection recency
    if (connection.connectionRecency === 'recent') score += 10;
    if (connection.connectionRecency === 'warm') score += 5;
    
    // Email available (direct outreach possible)
    if (connection.email) score += 5;
    
    return Math.min(score, 100);
}
```

---

## Part 3: Enhanced Connection Card UI

### Card Structure

```html
<div class="connection-card" data-relevance="{score}">
    <!-- Header Row -->
    <div class="connection-header">
        <div class="connection-identity">
            <a href="{linkedinUrl}" target="_blank" class="connection-name">
                {name}
                <svg class="external-icon"><!-- LinkedIn icon --></svg>
            </a>
            <div class="connection-title">{title}</div>
            <div class="connection-company">at {company}</div>
        </div>
        <div class="connection-badges">
            <span class="badge badge-degree">1st</span>
            {if isRecruiter}
            <span class="badge badge-recruiter">Recruiter</span>
            {/if}
            {if seniorityLevel === 'executive' || seniorityLevel === 'senior'}
            <span class="badge badge-seniority">{seniorityLevel}</span>
            {/if}
        </div>
    </div>
    
    <!-- Meta Row -->
    <div class="connection-meta">
        <span class="meta-item">
            <svg class="icon-calendar"></svg>
            Connected {connectionAge} days ago
        </span>
        {if email}
        <span class="meta-item">
            <svg class="icon-email"></svg>
            <a href="mailto:{email}">{email}</a>
        </span>
        {/if}
    </div>
    
    <!-- Approach Guidance -->
    <div class="connection-approach">
        <strong class="approach-label">Recommended approach:</strong>
        <span class="approach-text">{dynamicApproachGuidance}</span>
    </div>
    
    <!-- Action Buttons -->
    <div class="connection-actions">
        <a href="{linkedinUrl}" target="_blank" class="btn btn-primary btn-sm">
            View Profile
        </a>
        {if email}
        <a href="mailto:{email}?subject=..." class="btn btn-secondary btn-sm">
            Send Email
        </a>
        {/if}
        <button class="btn btn-ghost btn-sm" onclick="copyOutreachTemplate('{name}', '{company}')">
            Copy Template
        </button>
    </div>
</div>
```

### Dynamic Approach Guidance

```javascript
function generateApproachGuidance(connection, targetRole) {
    const { isRecruiter, seniorityLevel, connectionRecency, email } = connection;
    
    if (isRecruiter) {
        if (connectionRecency === 'recent') {
            return `You connected recently. Send a direct message mentioning the ${targetRole} role and ask if they're the right person to speak with or can point you to the hiring team.`;
        }
        return `As a recruiter, they can likely provide insight into the hiring process or connect you with the hiring manager. Reference your existing connection and express interest in the ${targetRole} role.`;
    }
    
    if (seniorityLevel === 'executive' || seniorityLevel === 'senior') {
        return `This is likely a decision-maker or peer to the hiring manager. Ask for an informational conversation about the team and culture. Do not lead with asking for a referral.`;
    }
    
    if (connectionRecency === 'recent') {
        return `Recent connection. A warm outreach asking about their experience at the company and any advice for someone interested in the ${targetRole} role.`;
    }
    
    if (email) {
        return `You have their email. Consider a brief, professional note asking for 15 minutes to learn about their experience. LinkedIn message as backup.`;
    }
    
    return `Send a personalized LinkedIn message referencing how you're connected and your interest in the ${targetRole} opportunity. Ask for insights or advice rather than directly asking for a referral.`;
}
```

### CSS Styling

```css
.connection-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}

.connection-card:hover {
    border-color: rgba(255, 255, 255, 0.15);
}

.connection-card[data-relevance="high"] {
    border-left: 3px solid #10b981;
}

.connection-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.connection-name {
    font-weight: 600;
    font-size: 1.1rem;
    color: #ffffff;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.connection-name:hover {
    color: #60a5fa;
}

.external-icon {
    width: 14px;
    height: 14px;
    opacity: 0.5;
}

.connection-title {
    color: #d1d5db;
    margin-top: 4px;
    font-size: 0.95rem;
}

.connection-company {
    color: #9ca3af;
    font-size: 0.9rem;
}

.connection-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-degree {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.badge-recruiter {
    background: rgba(96, 165, 250, 0.2);
    color: #60a5fa;
}

.badge-seniority {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
    text-transform: capitalize;
}

.connection-meta {
    display: flex;
    gap: 20px;
    margin-bottom: 16px;
    font-size: 0.85rem;
    color: #9ca3af;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.meta-item a {
    color: #60a5fa;
    text-decoration: none;
}

.connection-approach {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    line-height: 1.6;
    border-left: 3px solid #10b981;
}

.approach-label {
    color: #10b981;
    margin-right: 8px;
}

.approach-text {
    color: #d1d5db;
}

.connection-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.btn-sm {
    padding: 8px 16px;
    font-size: 0.85rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.btn-primary {
    background: #0077b5;
    color: white;
}

.btn-primary:hover {
    background: #006399;
}

.btn-secondary {
    background: rgba(96, 165, 250, 0.2);
    color: #60a5fa;
}

.btn-secondary:hover {
    background: rgba(96, 165, 250, 0.3);
}

.btn-ghost {
    background: transparent;
    color: #9ca3af;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-ghost:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #e0e0e0;
}
```

---

## Part 4: Connection Sorting and Grouping

### Sort Priority

Connections should be displayed in this order:

1. **Recruiters at target company** (highest priority)
2. **Senior/Executive at target company** (potential hiring managers)
3. **Other employees at target company**
4. **Recruiters in same industry** (may have intel or referrals)
5. **Senior connections in same function** (may know people)

### Grouping Logic

```javascript
function groupAndSortConnections(connections, targetCompany, targetRole) {
    const atCompany = connections.filter(c => 
        c.company.toLowerCase().includes(targetCompany.toLowerCase())
    );
    
    const notAtCompany = connections.filter(c => 
        !c.company.toLowerCase().includes(targetCompany.toLowerCase())
    );
    
    // Sort within groups
    const sortByRelevance = (a, b) => b.relevanceScore - a.relevanceScore;
    
    const directRecruiters = atCompany
        .filter(c => c.isRecruiter || c.isTalentAcquisition)
        .sort(sortByRelevance);
    
    const directOthers = atCompany
        .filter(c => !c.isRecruiter && !c.isTalentAcquisition)
        .sort(sortByRelevance);
    
    const relevantOthers = notAtCompany
        .filter(c => c.relevanceScore > 20)
        .sort(sortByRelevance)
        .slice(0, 10); // Limit to top 10
    
    return {
        directRecruiters,
        directOthers,
        relevantOthers,
        totalAtCompany: atCompany.length,
        totalConnections: connections.length
    };
}
```

---

## Part 5: Hey Henry Integration

Hey Henry should leverage the LinkedIn connection data to provide personalized coaching and outreach guidance. This applies to Partner ($129/mo) and Coach ($199/mo) tiers.

### Data Available to Hey Henry

When a user has uploaded LinkedIn connections, Hey Henry has access to:

```javascript
const heyHenryContext = {
    // Summary stats
    totalConnections: 4800,
    connectionsAtTargetCompany: 12,
    recruitersAtTargetCompany: 2,
    
    // Specific connections (for personalized guidance)
    topConnections: [
        {
            name: "Jennifer Coffin",
            title: "Senior Recruiting & Sourcing Leader, AMERS",
            company: "Target Company",
            linkedinUrl: "https://linkedin.com/in/...",
            email: null,
            connectionRecency: "recent",
            isRecruiter: true
        },
        // ... top 5 most relevant
    ],
    
    // Network insights
    hasRecruitersAtCompany: true,
    hasSeniorConnectionsAtCompany: true,
    hasEmailsAvailable: true,
    warmestConnection: "Jennifer Coffin (connected 45 days ago)"
};
```

### Hey Henry Conversation Scenarios

**Scenario 1: User asks "How should I approach this company?"**

```
Hey Henry should reference specific connections:

"You've got a strong in at {company}. Jennifer Coffin is a Senior Recruiting Leader 
there and you connected just 45 days ago. That's warm. I'd start with her.

Here's my suggested approach:
1. Send Jennifer a LinkedIn message (I can draft one for you)
2. Reference your recent connection and express interest in the {role} role
3. Ask if she's the right person or can point you to the hiring team

You also have 2 other connections there who could provide backup paths if Jennifer 
doesn't respond within a week. Want me to draft the outreach?"
```

**Scenario 2: User asks "Who should I reach out to first?"**

```
"Looking at your network for {company}, here's my priority order:

1. Jennifer Coffin (Recruiter, connected 45 days ago) - Your best shot. 
   Recruiters can fast-track you into the process.

2. Michael Chen (Engineering Manager, connected 8 months ago) - Could be 
   the hiring manager or peers with them. Good for intel on team culture.

3. Sarah Williams (Product Lead, connected 2 years ago) - Cold connection 
   but senior. Worth a shot if the first two don't pan out.

Start with Jennifer. If she doesn't respond in 5 business days, move to Michael.
Want me to draft messages for each?"
```

**Scenario 3: User asks "What should I say to the recruiter?"**

```
Hey Henry generates a personalized template:

"Here's a message for Jennifer Coffin:

---

Hi Jennifer,

Hope you're doing well. I saw {company} has an open {role} position and wanted 
to reach out since we're connected.

I've spent the last 8 years in [relevant experience from resume], and this role 
caught my attention because [specific reason from job analysis].

Are you the right person to speak with about this, or could you point me toward 
the hiring team?

Thanks,
[Name]

---

Keep it short. Recruiters get hundreds of messages. This one respects her time 
and makes it easy to respond. Want me to adjust the tone?"
```

**Scenario 4: User has no connections at target company**

```
"I checked your network for {company} and you don't have any direct connections there.

Here's what I'd do:

1. Check LinkedIn for 2nd-degree connections (people your connections know 
   who work there). I can only see your 1st-degree exports.

2. Use the cold outreach templates on this page to reach the hiring manager 
   and recruiter directly. These are your best bet without a warm intro.

3. Look for alumni connections. Did you go to {university from resume}? 
   Search LinkedIn for "{company} + {university}" to find potential warm paths.

Want me to help you find the right people to cold message?"
```

**Scenario 5: User asks about timing**

```
"Your warmest connection at {company} is Jennifer Coffin. You connected 45 days ago.

Rule of thumb on timing:
- Under 90 days: You're still fresh in their memory. Reach out now.
- 90-365 days: Warm but fading. Reference something specific about how you met.
- Over a year: Cold. You'll need a stronger hook or reason to reconnect.

Jennifer is in the sweet spot. I'd reach out this week while you're still recent. 
Monday or Tuesday morning tends to get better response rates than Friday afternoon.

Want me to draft the message?"
```

### Hey Henry Proactive Check-ins (Partner/Coach Tiers)

When Pipeline Integration is enabled, Hey Henry can proactively reference network data:

```
"Hey, I noticed you applied to {company} 5 days ago but haven't heard back. 
You've got Jennifer Coffin in your network who's a recruiter there.

This might be a good time to reach out and express interest. Sometimes a 
LinkedIn message from a mutual connection can move your application to the 
top of the pile.

Want me to draft something?"
```

### Hey Henry Memory Integration (Partner/Coach Tiers)

Hey Henry should remember:

- Which connections the user has already reached out to
- Which outreach attempts got responses
- Which connections the user has marked as "not helpful"
- Preferred outreach style (formal vs casual)

```javascript
// Example memory structure
const heyHenryMemory = {
    outreachHistory: [
        {
            connectionName: "Jennifer Coffin",
            company: "Target Company",
            outreachDate: "2026-01-03",
            method: "linkedin",
            gotResponse: true,
            outcome: "referred to hiring manager"
        }
    ],
    preferences: {
        outreachTone: "professional",
        preferEmail: false
    }
};
```

---

## Part 6: localStorage Schema

```javascript
// Stored in localStorage under 'linkedinConnections'
const storedData = {
    uploadedAt: "2026-01-07T12:00:00Z",
    connectionCount: 4800,
    connections: [
        {
            firstName: "Jennifer",
            lastName: "Coffin",
            url: "https://www.linkedin.com/in/jennifervivier",
            email: null,
            company: "Veeam Software",
            position: "Senior Recruiting & Sourcing Leader, AMERS",
            connectedOn: "2025-11-19"
        },
        // ... all connections
    ]
};

// Processed cache (regenerated on page load)
const processedCache = {
    generatedAt: "2026-01-07T12:05:00Z",
    targetCompany: "Google",
    targetRole: "Senior Product Manager",
    grouped: {
        directRecruiters: [...],
        directOthers: [...],
        relevantOthers: [...]
    }
};
```

---

## Part 7: Implementation Checklist

### Phase 1: CSV Parsing Fix (Critical)
- [ ] Add PapaParse library to outreach.html
- [ ] Replace parseLinkedInCSV function
- [ ] Test with real LinkedIn export containing commas in fields
- [ ] Verify empty row handling

### Phase 2: Enhanced Connection Processing
- [ ] Implement ProcessedConnection data model
- [ ] Add seniority detection function
- [ ] Add recruiter detection function
- [ ] Add recency calculation
- [ ] Add relevance scoring

### Phase 3: Enhanced UI
- [ ] Update connection card HTML structure
- [ ] Add clickable LinkedIn profile links
- [ ] Add email display/mailto links when available
- [ ] Add badge system (degree, recruiter, seniority)
- [ ] Add dynamic approach guidance
- [ ] Add action buttons (View Profile, Send Email, Copy Template)
- [ ] Implement sorting and grouping

### Phase 4: Hey Henry Integration (Partner+ Tiers)
- [ ] Pass connection data to Hey Henry context
- [ ] Add connection-aware response templates
- [ ] Implement proactive check-in triggers
- [ ] Add memory for outreach tracking

### Phase 5: Testing
- [ ] Test with CSV files of varying sizes (100, 1000, 5000+ connections)
- [ ] Test with edge cases (blank companies, blank titles, special characters)
- [ ] Test matching logic with partial company names
- [ ] Test Hey Henry responses with and without connections
- [ ] Verify tier restrictions are enforced

---

## Appendix: Test Data Edge Cases

```csv
First Name,Last Name,URL,Email Address,Company,Position,Connected On
John,Smith,https://linkedin.com/in/john,john@example.com,"Google, LLC","Director, Engineering",01 Jan 2025
Jane,Doe,https://linkedin.com/in/jane,,"","",15 Dec 2024
"Mary Ann",Johnson,https://linkedin.com/in/maryann,,Acme Corp,CEO,01 Jun 2020
Test,User,https://linkedin.com/in/test,,"Company with ""quotes""",Manager,01 Jan 2024
Empty,Fields,https://linkedin.com/in/empty,,,,01 Jan 2023
```

These cases should all parse correctly and handle gracefully in the UI.
