# CLAUDE CODE INSTRUCTIONS: CREATE DASHBOARD.HTML

## OBJECTIVE
Create a new dashboard.html page that serves as the post-login landing page. This is separate from tracker.html (Command Center). The dashboard provides a high-level overview with adaptive empathy messaging, while the Command Center shows detailed application management.

---

## CONTEXT
Currently, the Daily Pulse with empathy messaging was incorrectly added to tracker.html. We need to:
1. Create a new dashboard.html file
2. Move Daily Pulse functionality to dashboard.html
3. Add high-level analytics (not full pipeline view)
4. Update login redirect to dashboard.html
5. Keep tracker.html as the detailed Command Center

---

## DASHBOARD.HTML REQUIREMENTS

### Page Structure

**Header:**
- HenryAI logo (same as other pages)
- Navigation links: Dashboard (active) | Command Center | Analyze Role | Profile
- User email/logout in top-right

**Main Content (in order):**
1. Daily Pulse Banner (with empathy greeting)
2. Quick Stats Cards (3-4 cards in a row)
3. Today's Focus Section (priority actions)
4. Quick Actions (button row)
5. Recent Activity (last 3-5 applications)

**Footer/Bottom:**
- "View Full Pipeline →" button linking to tracker.html

---

## DETAILED SPECIFICATIONS

### 1. DAILY PULSE BANNER
**Location:** Top of page, below header
**Styling:** Same gradient background as in tracker.html (rgba(34, 211, 238, 0.1))

**Content:**
- Empathy-driven greeting (use `getPulseGreeting(profile, apps)`)
- NO stats in the banner itself (those go in Quick Stats Cards)
- Single line of adaptive text based on emotional state

**Example greetings:**
- Zen: "You've got 3 active applications. No rush—let's keep the bar high."
- Desperate: "Let's focus. You have 3 applications moving. Here's what needs attention today."
- Crushed: "I know this is brutal. You have 3 active applications. Let's make sure each one gets follow-up."

### 2. QUICK STATS CARDS
**Layout:** 4 cards in a row (responsive: 2x2 on mobile)

**Card 1: Active Applications**
- Number: Count of apps with active status
- Label: "Active Applications"
- Icon: 📊

**Card 2: Interviews This Week**
- Number: Count of interviews in next 7 days
- Label: "Interviews This Week"
- Icon: 📅
- Highlight in orange if > 0

**Card 3: Follow-ups Due**
- Number: Count of apps applied 5+ days ago without progress
- Label: "Follow-ups Due"
- Icon: 🔔
- Highlight in red if > 0

**Card 4: Avg Response Time**
- Number: Average days from apply to response (or "—" if no data)
- Label: "Avg Response Time"
- Icon: ⏱️

**Styling:**
- Background: var(--color-surface)
- Border: 1px solid var(--color-border)
- Border-radius: 12px
- Padding: 20px
- Hover effect: slight elevation

### 3. TODAY'S FOCUS SECTION
**Purpose:** Show the #1 priority action based on situation

**Content:**
- Section title: "Today's Focus"
- Single priority card with:
  - Priority description (from `getAdaptivePriorityAction()`)
  - Call-to-action button
  - Styled prominently

**Priority hierarchy:**
1. Upcoming interview → "Prep for [company] interview"
2. Follow-up due → "Follow up with [company]"
3. Thin pipeline → "Add more applications"
4. Healthy pipeline → "Keep momentum going"

**Styling:**
- Larger card, visually distinct
- Action button in accent color (--color-accent)

### 4. QUICK ACTIONS
**Layout:** Horizontal button row

**Buttons:**
1. "Analyze New Role" (primary accent button)
2. "View Full Pipeline" (secondary button)
3. "Interview Prep" (secondary button)

**Styling:**
- Primary: Background var(--color-accent), color #000
- Secondary: Background var(--color-surface), border var(--color-border)

### 5. RECENT ACTIVITY
**Purpose:** Show last 3-5 tracked applications for quick reference

**Content:**
- Section title: "Recent Activity"
- List of 3-5 most recent applications (by lastUpdated or dateAdded)
- Each item shows:
  - Company name
  - Role title
  - Current status badge
  - Days since last update
  - Quick "View" link (opens in Command Center with that app highlighted)

**Styling:**
- Compact list view (not full cards like Command Center)
- Each item: padding 12px, border-bottom separator
- Status badge: pill-shaped, colored by status (Hot=orange, Active=green, etc.)

---

## JAVASCRIPT FUNCTIONS NEEDED

### Load Data Functions
```javascript
// Load user profile
function getUserProfile() {
    try {
        const profile = localStorage.getItem('userProfile');
        return profile ? JSON.parse(profile) : null;
    } catch (err) {
        console.error('Error loading user profile:', err);
        return null;
    }
}

// Load applications
function getApplications() {
    try {
        const apps = localStorage.getItem('trackedApplications');
        return apps ? JSON.parse(apps) : [];
    } catch (err) {
        console.error('Error loading applications:', err);
        return [];
    }
}

// Get active applications
function getActiveApplications(apps) {
    return apps.filter(a => STATUSES[a.status]?.active);
}
```

### Stats Calculation Functions
```javascript
// Count interviews this week
function getInterviewsThisWeek(apps) {
    const today = new Date();
    const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    return apps.filter(a => {
        if (!a.interviewDate) return false;
        const date = new Date(a.interviewDate);
        return date >= today && date <= weekFromNow;
    }).length;
}

// Count follow-ups due
function getFollowUpsDue(apps) {
    return apps.filter(a => {
        const daysSince = getDaysSince(a.dateApplied || a.dateAdded);
        return ['Applied', 'Reached Out'].includes(a.status) && daysSince >= 5;
    }).length;
}

// Calculate average response time
function getAvgResponseTime(apps) {
    const withResponse = apps.filter(a => {
        return a.dateApplied && (a.dateResponseReceived || a.dateInterviewed);
    });
    
    if (withResponse.length === 0) return null;
    
    const total = withResponse.reduce((sum, a) => {
        const responseDate = a.dateResponseReceived || a.dateInterviewed;
        const applied = new Date(a.dateApplied);
        const responded = new Date(responseDate);
        return sum + Math.floor((responded - applied) / (1000 * 60 * 60 * 24));
    }, 0);
    
    return Math.round(total / withResponse.length);
}

// Get recent applications (last 5)
function getRecentApplications(apps) {
    return [...apps]
        .sort((a, b) => {
            const aDate = new Date(a.lastUpdated || a.dateAdded);
            const bDate = new Date(b.lastUpdated || b.dateAdded);
            return bDate - aDate;
        })
        .slice(0, 5);
}
```

### Empathy Functions (REUSE FROM TRACKER.HTML)
```javascript
// Copy these functions from tracker.html:
// - getPulseGreeting(profile, apps)
// - getAdaptivePriorityAction(profile, apps, upcomingInterviews, followUpsDue, activeApps)
// - getDaysSince(dateString)
```

### Render Functions
```javascript
function renderDashboard() {
    const profile = getUserProfile();
    const apps = getApplications();
    const activeApps = getActiveApplications(apps);
    
    renderDailyPulse(profile, apps);
    renderQuickStats(apps, activeApps);
    renderTodaysFocus(profile, apps, activeApps);
    renderRecentActivity(apps);
}

function renderDailyPulse(profile, apps) {
    const greeting = getPulseGreeting(profile, apps);
    document.getElementById('pulseGreeting').textContent = greeting;
}

function renderQuickStats(apps, activeApps) {
    document.getElementById('statActive').textContent = activeApps.length;
    
    const interviewsThisWeek = getInterviewsThisWeek(apps);
    document.getElementById('statInterviews').textContent = interviewsThisWeek;
    if (interviewsThisWeek > 0) {
        document.getElementById('cardInterviews').classList.add('highlight');
    }
    
    const followUpsDue = getFollowUpsDue(apps);
    document.getElementById('statFollowUps').textContent = followUpsDue;
    if (followUpsDue > 0) {
        document.getElementById('cardFollowUps').classList.add('urgent');
    }
    
    const avgResponseTime = getAvgResponseTime(apps);
    document.getElementById('statResponseTime').textContent = avgResponseTime ? `${avgResponseTime} days` : '—';
}

function renderTodaysFocus(profile, apps, activeApps) {
    // Get priority action
    const interviewsThisWeek = apps.filter(a => {
        if (!a.interviewDate) return false;
        const date = new Date(a.interviewDate);
        const today = new Date();
        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        return date >= today && date <= weekFromNow;
    });
    
    const followUpsDue = apps.filter(a => {
        const daysSince = getDaysSince(a.dateApplied || a.dateAdded);
        return ['Applied', 'Reached Out'].includes(a.status) && daysSince >= 5;
    });
    
    const actionMessage = getAdaptivePriorityAction(profile, apps, interviewsThisWeek, followUpsDue, activeApps);
    document.getElementById('focusMessage').textContent = actionMessage;
    
    // Set appropriate action button
    if (interviewsThisWeek.length > 0) {
        document.getElementById('focusButton').textContent = 'Prep Interview';
        document.getElementById('focusButton').onclick = () => window.location.href = 'interview-prep.html';
    } else if (followUpsDue.length > 0) {
        document.getElementById('focusButton').textContent = 'Draft Follow-up';
        document.getElementById('focusButton').onclick = () => window.location.href = 'outreach.html';
    } else {
        document.getElementById('focusButton').textContent = 'Analyze New Role';
        document.getElementById('focusButton').onclick = () => window.location.href = 'analyze.html';
    }
}

function renderRecentActivity(apps) {
    const recent = getRecentApplications(apps);
    const container = document.getElementById('recentActivity');
    
    container.innerHTML = recent.map(app => `
        <div class="activity-item">
            <div class="activity-info">
                <div class="activity-company">${app.company}</div>
                <div class="activity-role">${app.role}</div>
            </div>
            <div class="activity-meta">
                <span class="status-badge ${getStatusClass(app.status)}">${app.status}</span>
                <span class="activity-time">${getDaysSince(app.lastUpdated || app.dateAdded)}d ago</span>
            </div>
            <a href="tracker.html?highlight=${app.id}" class="activity-link">View →</a>
        </div>
    `).join('');
}

function getStatusClass(status) {
    if (status === 'Hot') return 'status-hot';
    if (['Active', 'Recruiter Screen', 'Hiring Manager'].includes(status)) return 'status-active';
    if (['Applied', 'Reached Out'].includes(status)) return 'status-waiting';
    return 'status-default';
}
```

---

## HTML STRUCTURE

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | HenryAI</title>
    <!-- Reuse same CSS variables and fonts from tracker.html -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
</head>
<body>
    <!-- HEADER (same as tracker.html) -->
    <header>
        <div class="header-container">
            <a href="dashboard.html" class="logo">Henry<em>AI</em></a>
            <nav class="header-nav">
                <a href="dashboard.html" class="nav-link active">Dashboard</a>
                <a href="tracker.html" class="nav-link">Command Center</a>
                <a href="analyze.html" class="nav-link">Analyze Role</a>
                <a href="profile.html" class="nav-link">Profile</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <!-- DAILY PULSE BANNER -->
        <div class="daily-pulse">
            <div class="pulse-greeting" id="pulseGreeting">Loading...</div>
        </div>

        <!-- QUICK STATS CARDS -->
        <div class="quick-stats">
            <div class="stat-card" id="cardActive">
                <div class="stat-icon">📊</div>
                <div class="stat-value" id="statActive">0</div>
                <div class="stat-label">Active Applications</div>
            </div>
            <div class="stat-card" id="cardInterviews">
                <div class="stat-icon">📅</div>
                <div class="stat-value" id="statInterviews">0</div>
                <div class="stat-label">Interviews This Week</div>
            </div>
            <div class="stat-card" id="cardFollowUps">
                <div class="stat-icon">🔔</div>
                <div class="stat-value" id="statFollowUps">0</div>
                <div class="stat-label">Follow-ups Due</div>
            </div>
            <div class="stat-card" id="cardResponseTime">
                <div class="stat-icon">⏱️</div>
                <div class="stat-value" id="statResponseTime">—</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
        </div>

        <!-- TODAY'S FOCUS -->
        <div class="focus-section">
            <h2>Today's Focus</h2>
            <div class="focus-card">
                <div class="focus-message" id="focusMessage">Loading...</div>
                <button class="focus-button" id="focusButton">Take Action</button>
            </div>
        </div>

        <!-- QUICK ACTIONS -->
        <div class="quick-actions">
            <a href="analyze.html" class="action-btn primary">Analyze New Role</a>
            <a href="tracker.html" class="action-btn secondary">View Full Pipeline</a>
            <a href="interview-prep.html" class="action-btn secondary">Interview Prep</a>
        </div>

        <!-- RECENT ACTIVITY -->
        <div class="recent-section">
            <h2>Recent Activity</h2>
            <div class="recent-activity" id="recentActivity">
                <!-- Populated by JS -->
            </div>
        </div>
    </div>

    <script>
        // Add all JavaScript functions here
        // STATUSES constant (copy from tracker.html)
        // All helper functions listed above
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            renderDashboard();
        });
    </script>
    
    <!-- Auth scripts (same as tracker.html) -->
    <script src="js/supabase-client.js"></script>
    <script src="js/auth-check.js"></script>
</body>
</html>
```

---

## CSS STYLING NOTES

**Reuse from tracker.html:**
- CSS variables (colors, fonts)
- Header styling
- Container max-width
- Card base styling

**New styles needed:**
- `.quick-stats` - 4-column grid (2x2 on mobile)
- `.stat-card` - Individual stat card with icon, value, label
- `.stat-card.highlight` - Orange border for interviews
- `.stat-card.urgent` - Red border for follow-ups
- `.focus-section` - Today's focus container
- `.focus-card` - Prominent card with message + button
- `.quick-actions` - Button row
- `.recent-activity` - List view for recent apps
- `.activity-item` - Individual recent activity row
- `.status-badge` - Colored pill for status

**Color coding:**
- Hot: #FF6B35 (orange)
- Active: #4CAF50 (green)
- Waiting: #546E7A (gray)
- Urgent: #E57373 (red)

---

## UPDATE LOGIN REDIRECT

**File:** login.html

**Current:**
```javascript
const redirect = sessionStorage.getItem('redirectAfterLogin') || 'tracker.html';
```

**Change to:**
```javascript
const redirect = sessionStorage.getItem('redirectAfterLogin') || 'dashboard.html';
```

---

## TESTING REQUIREMENTS

### Test 1: Dashboard Loads
1. Sign in
2. Verify redirect to dashboard.html
3. Verify Daily Pulse greeting appears
4. Verify all 4 stat cards show correct numbers
5. Verify Today's Focus shows appropriate priority

### Test 2: Empathy Messaging Works
1. Set profile with different emotional states (zen, stressed, desperate, crushed)
2. Reload dashboard
3. Verify greeting adapts appropriately

### Test 3: Navigation Works
1. Click "View Full Pipeline" → Goes to tracker.html
2. Click "Analyze New Role" → Goes to analyze.html
3. Click "Interview Prep" → Goes to interview-prep.html
4. Click "Command Center" in nav → Goes to tracker.html

### Test 4: Recent Activity Links
1. Click "View →" on any recent activity item
2. Verify goes to tracker.html with that application highlighted

### Test 5: Empty State
1. Clear all applications from localStorage
2. Reload dashboard
3. Verify appropriate empty state messaging
4. Verify primary CTA is "Analyze New Role"

### Test 6: Stats Calculation
1. Add apps with different statuses
2. Add interview dates (some this week, some not)
3. Add applied dates (some 5+ days ago, some recent)
4. Verify all stat cards calculate correctly

---

## VALIDATION CHECKLIST

- [ ] dashboard.html file created
- [ ] Daily Pulse banner with empathy greeting
- [ ] 4 Quick Stats cards with correct calculations
- [ ] Today's Focus section with adaptive messaging
- [ ] Quick Actions button row
- [ ] Recent Activity list (last 5 apps)
- [ ] All navigation links work
- [ ] login.html redirects to dashboard.html
- [ ] Empathy messaging adapts to profile situation
- [ ] Stats update when applications change
- [ ] Empty state shows appropriate messaging
- [ ] Mobile responsive (2x2 grid for stats)
- [ ] No console errors
- [ ] Styling matches HenryAI design system

---

## KEY DIFFERENCES: DASHBOARD vs COMMAND CENTER

**Dashboard (dashboard.html):**
- High-level overview
- Single priority focus
- Quick stats
- Recent activity list
- Landing page after login

**Command Center (tracker.html):**
- Full pipeline view
- All application cards
- Filtering and sorting
- Detailed metrics
- Import/export functionality
- Accessed from dashboard

---

## ESTIMATED COMPLEXITY
- Time: 45-60 minutes
- Risk: Low (new file, no breaking changes)
- Files created: 1 (dashboard.html)
- Files modified: 1 (login.html redirect)

---

## SUCCESS CRITERIA

Integration is successful when:
1. Sign-in redirects to dashboard.html
2. Dashboard shows empathetic greeting based on profile
3. All 4 stat cards calculate correctly
4. Today's Focus shows appropriate priority action
5. Recent Activity shows last 5 applications
6. All navigation links work correctly
7. "View Full Pipeline" goes to tracker.html (Command Center)
8. Empty state shows appropriate messaging
9. Mobile responsive layout works
10. No console errors
