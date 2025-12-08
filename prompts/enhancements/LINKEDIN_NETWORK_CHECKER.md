# 🤝 LINKEDIN NETWORK CHECKER FEATURE

## CONCEPT:

Add a contextual prompt on the Outreach page that offers to check the user's LinkedIn network for connections at the target company.

**Value Proposition:**
- Warm intros get 3x higher response rates
- Shows direct connections (1st degree)
- Shows connections of connections (2nd degree)
- Suggests introduction paths

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## VISUAL DESIGN:

### Option 1: Top Prompt (Recommended)

Place this RIGHT AFTER the page title, BEFORE the two-column layout:

```html
<!-- LinkedIn Network Checker Prompt -->
<div class="linkedin-prompt" id="linkedinPrompt">
    <div class="linkedin-prompt-icon">🤝</div>
    <div class="linkedin-prompt-content">
        <h3><span id="firstNamePrompt">Hey</span>, I can check your LinkedIn network for you</h3>
        <p>Upload your LinkedIn connections (CSV) and I'll show you who you know at <strong><span id="companyNamePrompt">this company</span></strong>. Warm intros get 3x higher response rates than cold outreach.</p>
        
        <div class="linkedin-prompt-actions">
            <input type="file" id="linkedinUpload" accept=".csv" style="display: none;">
            <button onclick="document.getElementById('linkedinUpload').click()" class="linkedin-btn linkedin-btn-primary">
                📤 Upload LinkedIn CSV
            </button>
            <button onclick="showLinkedInHelp()" class="linkedin-btn linkedin-btn-secondary">
                ❓ How to Export
            </button>
            <button onclick="dismissLinkedInPrompt()" class="linkedin-btn linkedin-btn-text">
                Maybe Later
            </button>
        </div>
        
        <div id="linkedinResults" class="linkedin-results" style="display: none;"></div>
    </div>
    <button onclick="dismissLinkedInPrompt()" class="linkedin-prompt-close">×</button>
</div>
```

### CSS:

```css
/* LinkedIn Network Checker Prompt */
.linkedin-prompt {
    background: linear-gradient(135deg, rgba(10, 102, 194, 0.1) 0%, rgba(0, 119, 181, 0.05) 100%);
    border: 1px solid rgba(10, 102, 194, 0.3);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 40px;
    display: flex;
    gap: 20px;
    align-items: flex-start;
    position: relative;
}

.linkedin-prompt-icon {
    font-size: 2.5rem;
    line-height: 1;
    flex-shrink: 0;
}

.linkedin-prompt-content {
    flex: 1;
}

.linkedin-prompt-content h3 {
    font-size: 1.3rem;
    margin-bottom: 10px;
    color: #60a5fa;
}

.linkedin-prompt-content p {
    color: #d1d5db;
    margin-bottom: 20px;
    line-height: 1.6;
}

.linkedin-prompt-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.linkedin-btn {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    font-weight: 500;
}

.linkedin-btn-primary {
    background: #0a66c2;
    color: white;
}

.linkedin-btn-primary:hover {
    background: #004182;
    transform: translateY(-1px);
}

.linkedin-btn-secondary {
    background: rgba(96, 165, 250, 0.1);
    color: #60a5fa;
    border: 1px solid rgba(96, 165, 250, 0.3);
}

.linkedin-btn-secondary:hover {
    background: rgba(96, 165, 250, 0.2);
    border-color: rgba(96, 165, 250, 0.5);
}

.linkedin-btn-text {
    background: transparent;
    color: #9ca3af;
}

.linkedin-btn-text:hover {
    color: #d1d5db;
}

.linkedin-prompt-close {
    position: absolute;
    top: 12px;
    right: 12px;
    background: transparent;
    border: none;
    color: #6b7280;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 4px 8px;
    line-height: 1;
    transition: color 0.2s;
}

.linkedin-prompt-close:hover {
    color: #d1d5db;
}

/* LinkedIn Results */
.linkedin-results {
    margin-top: 24px;
    padding: 20px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid rgba(96, 165, 250, 0.2);
}

.linkedin-results h4 {
    color: #10b981;
    margin-bottom: 16px;
    font-size: 1.1rem;
}

.connection-group {
    margin-bottom: 24px;
}

.connection-group h5 {
    color: #60a5fa;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

.connection-item {
    background: rgba(0, 0, 0, 0.4);
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    border-left: 3px solid #10b981;
}

.connection-item.second-degree {
    border-left-color: #fbbf24;
}

.connection-name {
    font-weight: 600;
    color: #e5e7eb;
    margin-bottom: 4px;
}

.connection-title {
    color: #9ca3af;
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.connection-meta {
    display: flex;
    gap: 16px;
    font-size: 0.85rem;
    color: #6b7280;
}

.connection-intro-path {
    margin-top: 8px;
    padding: 12px;
    background: rgba(251, 191, 36, 0.1);
    border-radius: 6px;
    font-size: 0.9rem;
    color: #d1d5db;
}
</style>
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## JAVASCRIPT FUNCTIONALITY:

```javascript
// LinkedIn Network Checker

// Populate personalization on page load
window.addEventListener('DOMContentLoaded', () => {
    const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
    const firstName = analysisData._candidate_first_name || 'Hey';
    const company = analysisData._company_name || 'this company';
    
    const firstNameEl = document.getElementById('firstNamePrompt');
    const companyEl = document.getElementById('companyNamePrompt');
    
    if (firstNameEl) firstNameEl.textContent = `Hey ${firstName}`;
    if (companyEl) companyEl.textContent = company;
    
    // Check if user already dismissed this prompt
    const dismissed = sessionStorage.getItem('linkedinPromptDismissed');
    if (dismissed === 'true') {
        const prompt = document.getElementById('linkedinPrompt');
        if (prompt) prompt.style.display = 'none';
    }
    
    // Check if LinkedIn data already uploaded
    const linkedinData = localStorage.getItem('linkedinConnections');
    if (linkedinData) {
        // Auto-check on page load if they've previously uploaded
        checkLinkedInNetwork(JSON.parse(linkedinData));
    }
});

// Handle CSV upload
document.getElementById('linkedinUpload')?.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async (e) => {
        const csv = e.target.result;
        const connections = parseLinkedInCSV(csv);
        
        // Store for future use
        localStorage.setItem('linkedinConnections', JSON.stringify(connections));
        
        // Check network
        checkLinkedInNetwork(connections);
    };
    reader.readAsText(file);
});

// Parse LinkedIn CSV
function parseLinkedInCSV(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const connections = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
        const connection = {};
        
        headers.forEach((header, index) => {
            connection[header] = values[index] || '';
        });
        
        connections.push(connection);
    }
    
    return connections;
}

// Check network for connections at target company
function checkLinkedInNetwork(connections) {
    const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
    const targetCompany = analysisData._company_name || '';
    
    if (!targetCompany) {
        alert('No target company found. Please analyze a job first.');
        return;
    }
    
    // Filter connections at target company
    const directConnections = connections.filter(conn => {
        const company = conn['Company'] || conn['company'] || '';
        return company.toLowerCase().includes(targetCompany.toLowerCase());
    });
    
    // Filter 2nd degree connections (connections who have connections at target)
    const secondDegreeConnections = [];
    // This would require more sophisticated logic - for MVP, just show direct
    
    // Display results
    displayLinkedInResults(directConnections, secondDegreeConnections, targetCompany);
}

// Display results
function displayLinkedInResults(directConnections, secondDegreeConnections, company) {
    const resultsContainer = document.getElementById('linkedinResults');
    if (!resultsContainer) return;
    
    if (directConnections.length === 0 && secondDegreeConnections.length === 0) {
        resultsContainer.innerHTML = `
            <h4>No direct connections found at ${company}</h4>
            <p style="color: #9ca3af; margin-top: 8px;">
                No problem! Cold outreach can still be effective with the right positioning. 
                Use the templates above and reference your relevant experience.
            </p>
        `;
        resultsContainer.style.display = 'block';
        return;
    }
    
    let html = `<h4>🎯 Found ${directConnections.length} connection(s) at ${company}</h4>`;
    
    if (directConnections.length > 0) {
        html += `<div class="connection-group">`;
        html += `<h5>Direct Connections (1st Degree)</h5>`;
        
        directConnections.forEach(conn => {
            const name = conn['First Name'] + ' ' + conn['Last Name'];
            const title = conn['Position'] || 'Position not available';
            const connectedDate = conn['Connected On'] || 'Unknown';
            
            html += `
                <div class="connection-item">
                    <div class="connection-name">${name}</div>
                    <div class="connection-title">${title}</div>
                    <div class="connection-meta">
                        <span>📅 Connected: ${connectedDate}</span>
                    </div>
                    <div style="margin-top: 12px; padding: 12px; background: rgba(16, 185, 129, 0.1); border-radius: 6px; font-size: 0.9rem;">
                        <strong>Suggested approach:</strong> Send a personalized message referencing your shared background and expressing interest in the role. Mention specific projects or achievements that align with ${company}'s needs.
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
}

// Show help modal
function showLinkedInHelp() {
    alert(`How to Export LinkedIn Connections:

1. Go to linkedin.com/mynetwork/invite-connect/connections/
2. Click "Manage synced and imported contacts" (top right)
3. Click "Export contacts"
4. Select "Connections" (not "Contacts")
5. Click "Request archive"
6. Wait for email from LinkedIn (usually 10 minutes)
7. Download the CSV file
8. Upload it here

The CSV includes: Name, Company, Position, Connected Date`);
}

// Dismiss prompt
function dismissLinkedInPrompt() {
    const prompt = document.getElementById('linkedinPrompt');
    if (prompt) {
        prompt.style.display = 'none';
        sessionStorage.setItem('linkedinPromptDismissed', 'true');
    }
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## INTEGRATION STEPS:

### 1. Add HTML

In `outreach.html`, add the prompt HTML RIGHT AFTER the page title/subtitle, BEFORE the two-column grid:

```html
<h1>
    <span>🤝</span> Network Intelligence & Strategic Outreach
</h1>
<p class="subtitle">
    Strategic guidance on identifying key decision-makers...
</p>

<!-- ADD THIS HERE -->
<div class="linkedin-prompt" id="linkedinPrompt">
    <!-- Full HTML from above -->
</div>

<!-- Existing two-column layout starts here -->
<div class="two-column-grid">
    ...
```

### 2. Add CSS

Add all the CSS to the `<style>` section in `outreach.html`

### 3. Add JavaScript

Add all the JavaScript to the `<script>` section in `outreach.html`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## USER EXPERIENCE:

### Flow 1: First Time User
1. User lands on Outreach page
2. Sees personalized prompt: "Hey Henry, I can check your LinkedIn network for you"
3. Clicks "How to Export" → Gets instructions
4. Exports LinkedIn CSV
5. Uploads CSV
6. Sees: "🎯 Found 3 connections at ServiceNow"
7. Gets names, titles, suggested approach

### Flow 2: Returning User
1. User lands on Outreach page (new job)
2. System auto-checks their previously uploaded LinkedIn data
3. Immediately shows relevant connections
4. No re-upload needed

### Flow 3: No Connections Found
1. User uploads CSV
2. No matches at target company
3. Shows: "No direct connections found at ServiceNow. No problem! Cold outreach can still be effective..."
4. Encourages them to use the templates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## FUTURE ENHANCEMENTS:

### Phase 2:
- 2nd degree connections (connections of connections)
- Suggested introduction paths
- Connection strength scoring (recent interactions, shared groups)
- Auto-draft personalized messages using connection context

### Phase 3:
- Direct LinkedIn API integration (no CSV needed)
- Real-time connection suggestions
- Track which connections have been contacted
- Connection response rates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## PREMIUM TIER POSITIONING:

This could be:
- **Free tier:** Upload CSV manually, see direct connections
- **Paid tier:** Direct API integration, 2nd degree connections, auto-messaging

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## BENEFITS:

✅ **Immediate value:** Users see connections at target company
✅ **Contextual:** Right when they're thinking about outreach
✅ **Personalized:** Uses first name + company name
✅ **Actionable:** Provides suggested approach for each connection
✅ **Sticky:** Stores data for future job analyses
✅ **Premium feature:** Clear upgrade path

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
