/**
 * Ask Henry - Floating Chat Widget
 * A contextually-aware AI assistant available from any page
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // Inject styles
    const styles = `
        /* Ask Henry Floating Widget */
        .ask-henry-fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            cursor: pointer;
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            background: transparent;
            border: none;
            padding: 0;
        }

        .ask-henry-fab:hover .ask-henry-logo {
            filter: drop-shadow(0 0 12px rgba(102, 126, 234, 0.6));
        }

        .ask-henry-fab.hidden {
            transform: scale(0);
            opacity: 0;
            pointer-events: none;
        }

        .ask-henry-logo {
            width: 56px;
            height: 56px;
            transition: filter 0.3s ease;
        }

        /* Breathing animation for the logo */
        @keyframes breathe {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.12);
            }
        }

        .ask-henry-logo {
            animation: breathe 2.5s ease-in-out infinite;
        }

        /* When chat is open, use subtle pulse instead */
        .ask-henry-fab.active .ask-henry-logo {
            animation: pulse-active 1.5s ease-in-out infinite;
        }

        @keyframes pulse-active {
            0%, 100% {
                transform: scale(1);
                filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.4));
            }
            50% {
                transform: scale(1.08);
                filter: drop-shadow(0 0 16px rgba(102, 126, 234, 0.6));
            }
        }

        /* Chat Drawer */
        .ask-henry-drawer {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 380px;
            max-width: calc(100vw - 48px);
            height: 520px;
            max-height: calc(100vh - 100px);
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            transform: scale(0.9) translateY(20px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            transform-origin: bottom right;
            overflow: hidden;
        }

        .ask-henry-drawer.open {
            transform: scale(1) translateY(0);
            opacity: 1;
            pointer-events: auto;
        }

        /* Drawer Header */
        .ask-henry-header {
            padding: 18px 20px;
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ask-henry-title {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ask-henry-header-logo {
            flex-shrink: 0;
        }

        .ask-henry-title-text {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
        }

        .ask-henry-title-context {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-top: 2px;
        }

        .ask-henry-close {
            background: none;
            border: none;
            color: #9ca3af;
            font-size: 1.3rem;
            cursor: pointer;
            padding: 4px;
            transition: color 0.2s;
        }

        .ask-henry-close:hover {
            color: #ffffff;
        }

        /* Messages Area */
        .ask-henry-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: linear-gradient(180deg, #0d0d0d 0%, #000000 100%);
        }

        .ask-henry-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .ask-henry-message.assistant {
            align-self: flex-start;
            background: linear-gradient(145deg, #2a2a2a 0%, #1a1a1a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #e5e5e5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .ask-henry-message.user {
            align-self: flex-end;
            background: linear-gradient(145deg, #4a4a4a 0%, #333333 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .ask-henry-message p {
            margin: 0 0 8px 0;
        }

        .ask-henry-message p:last-child {
            margin-bottom: 0;
        }

        .ask-henry-message ul, .ask-henry-message ol {
            margin: 8px 0;
            padding-left: 18px;
        }

        .ask-henry-message li {
            margin-bottom: 4px;
        }

        .ask-henry-message strong {
            color: #ffffff;
        }

        .ask-henry-message.user strong {
            color: #ffffff;
        }

        /* Typing Indicator */
        .ask-henry-typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: linear-gradient(145deg, #2a2a2a 0%, #1a1a1a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            width: fit-content;
        }

        .ask-henry-typing .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #888888;
            animation: typing-bounce 1.4s infinite ease-in-out;
        }

        .ask-henry-typing .dot:nth-child(1) { animation-delay: 0s; }
        .ask-henry-typing .dot:nth-child(2) { animation-delay: 0.2s; }
        .ask-henry-typing .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        /* Quick Suggestions */
        .ask-henry-suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 0 16px 12px;
            background: transparent;
        }

        .ask-henry-suggestion {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.8rem;
            color: #a0a0a0;
            cursor: pointer;
            transition: all 0.2s;
        }

        .ask-henry-suggestion:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            color: #ffffff;
        }

        /* Input Area */
        .ask-henry-input-area {
            padding: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .ask-henry-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px 16px;
            color: #ffffff;
            font-size: 0.95rem;
            line-height: 1.4;
            resize: none;
            min-height: 48px;
            max-height: 120px;
        }

        .ask-henry-input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.25);
            background: rgba(255, 255, 255, 0.08);
        }

        .ask-henry-input::placeholder {
            color: #666666;
        }

        .ask-henry-send {
            background: linear-gradient(145deg, #4a4a4a 0%, #333333 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            width: 48px;
            height: 48px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .ask-henry-send:hover {
            background: linear-gradient(145deg, #5a5a5a 0%, #444444 100%);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .ask-henry-send:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .ask-henry-send svg {
            width: 18px;
            height: 18px;
            fill: #ffffff;
        }

        /* Mobile Responsive */
        @media (max-width: 480px) {
            .ask-henry-drawer {
                bottom: 0;
                right: 0;
                width: 100%;
                max-width: 100%;
                height: 70vh;
                border-radius: 20px 20px 0 0;
            }

            .ask-henry-fab {
                bottom: 16px;
                right: 16px;
            }
        }
    `;

    // Inject stylesheet
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // State
    let isOpen = false;
    let isLoading = false;
    let conversationHistory = [];

    // Load conversation history from sessionStorage (persists across page navigation)
    function loadConversationHistory() {
        try {
            const saved = sessionStorage.getItem('askHenryConversation');
            if (saved) {
                conversationHistory = JSON.parse(saved);
            }
        } catch (e) {
            console.error('Error loading conversation history:', e);
            conversationHistory = [];
        }
    }

    // Save conversation history to sessionStorage
    function saveConversationHistory() {
        try {
            // Keep last 20 messages to avoid storage limits
            const toSave = conversationHistory.slice(-20);
            sessionStorage.setItem('askHenryConversation', JSON.stringify(toSave));
        } catch (e) {
            console.error('Error saving conversation history:', e);
        }
    }

    // Clear conversation history (for starting fresh)
    function clearConversationHistory() {
        conversationHistory = [];
        sessionStorage.removeItem('askHenryConversation');
    }

    // Get user's first name from profile
    function getUserName() {
        try {
            // Check resumeData in sessionStorage first (most recent)
            const resumeData = JSON.parse(sessionStorage.getItem('resumeData') || '{}');
            if (resumeData.name) {
                return resumeData.name.split(' ')[0];
            }
            // Check localStorage for saved profile
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            if (profile.name) {
                return profile.name.split(' ')[0];
            }
        } catch (e) {
            console.error('Error getting user name:', e);
        }
        return null;
    }

    // Get current page context
    function getPageContext() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';

        const contexts = {
            'index': { name: 'Home', description: 'Getting started with HenryAI' },
            'analyze': { name: 'Job Analysis', description: 'Analyzing a new job posting' },
            'results': { name: 'Analysis Results', description: 'Reviewing job match analysis' },
            'overview': { name: 'Strategy Overview', description: 'Viewing your application strategy' },
            'positioning': { name: 'Positioning Strategy', description: 'Reviewing positioning recommendations' },
            'documents': { name: 'Tailored Documents', description: 'Reviewing resume and cover letter' },
            'outreach': { name: 'Network Intelligence', description: 'Planning outreach strategy' },
            'interview-intelligence': { name: 'Interview Intelligence', description: 'Preparing for interviews' },
            'prep-guide': { name: 'Interview Prep', description: 'Reviewing interview prep guide' },
            'interview-debrief': { name: 'Interview Debrief', description: 'Debriefing after an interview' },
            'mock-interview': { name: 'Mock Interview', description: 'Practicing interview skills' },
            'tracker': { name: 'Application Tracker', description: 'Managing job applications' },
            'profile-edit': { name: 'Profile', description: 'Editing your profile' }
        };

        const context = contexts[page] || { name: 'HenryAI', description: 'Your personal job search guide' };
        context.page = page; // Include the page key for greeting lookup
        return context;
    }

    // Get pipeline data from localStorage (for tracker page context)
    function getPipelineData() {
        try {
            const apps = JSON.parse(localStorage.getItem('trackedApplications') || '[]');
            if (apps.length === 0) return null;

            // Calculate metrics
            const activeApps = apps.filter(a => {
                const activeStatuses = ['Preparing', 'To Apply', 'Applied', 'Reached Out', 'Response Received',
                    'Recruiter Screen', 'Awaiting Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                    'Awaiting Next Round', 'Final Round', 'Executive Interview', 'Awaiting Decision', 'Interviewed', 'Offer Received'];
                return activeStatuses.includes(a.status);
            });

            const interviewingApps = apps.filter(a =>
                ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview', 'Interviewed', 'Awaiting Next Round', 'Awaiting Decision'].includes(a.status)
            );

            const appliedApps = apps.filter(a => !['Preparing', 'To Apply'].includes(a.status));
            const respondedApps = apps.filter(a =>
                ['Response Received', 'Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview', 'Interviewed', 'Offer Received', 'Awaiting Next Round', 'Awaiting Decision'].includes(a.status)
            );

            const rejectedApps = apps.filter(a => a.status === 'Rejected');
            const ghostedApps = apps.filter(a => a.status === 'No Response' ||
                (a.status === 'Applied' && getDaysSinceDate(a.dateApplied) > 14));

            // Get high priority apps (hot/active with high fit)
            const hotApps = activeApps.filter(a => {
                const daysSince = getDaysSinceDate(a.lastUpdated || a.dateAdded);
                const isInterviewing = ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                    'Final Round', 'Executive Interview'].includes(a.status);
                return isInterviewing || (daysSince <= 3 && a.fitScore >= 70);
            });

            // Average fit score
            const avgFit = activeApps.length > 0
                ? Math.round(activeApps.reduce((sum, a) => sum + (a.fitScore || 50), 0) / activeApps.length)
                : 0;

            // Interview rate
            const interviewRate = appliedApps.length > 0
                ? Math.round((respondedApps.length / appliedApps.length) * 100)
                : 0;

            return {
                total: apps.length,
                active: activeApps.length,
                interviewing: interviewingApps.length,
                applied: appliedApps.length,
                rejected: rejectedApps.length,
                ghosted: ghostedApps.length,
                hot: hotApps.length,
                avgFitScore: avgFit,
                interviewRate: interviewRate,
                // Include details of top apps for context
                topApps: activeApps.slice(0, 5).map(a => ({
                    company: a.company,
                    role: a.role,
                    status: a.status,
                    fitScore: a.fitScore,
                    daysSinceUpdate: getDaysSinceDate(a.lastUpdated || a.dateAdded)
                })),
                // Summary for the AI
                summary: generatePipelineSummary(activeApps, interviewingApps, appliedApps, respondedApps, rejectedApps, ghostedApps, avgFit, interviewRate)
            };
        } catch (e) {
            console.error('Error getting pipeline data:', e);
            return null;
        }
    }

    function getDaysSinceDate(dateString) {
        if (!dateString) return 0;
        const date = new Date(dateString);
        const now = new Date();
        return Math.floor((now - date) / (1000 * 60 * 60 * 24));
    }

    function generatePipelineSummary(activeApps, interviewingApps, appliedApps, respondedApps, rejectedApps, ghostedApps, avgFit, interviewRate) {
        const parts = [];

        parts.push(`${activeApps.length} active application${activeApps.length !== 1 ? 's' : ''}`);

        if (interviewingApps.length > 0) {
            parts.push(`${interviewingApps.length} in interview stages`);
        }

        if (appliedApps.length > 0) {
            parts.push(`${interviewRate}% interview rate`);
        }

        if (avgFit > 0) {
            parts.push(`${avgFit}% average fit score`);
        }

        if (rejectedApps.length > 0) {
            parts.push(`${rejectedApps.length} rejected`);
        }

        if (ghostedApps.length > 0) {
            parts.push(`${ghostedApps.length} likely ghosted`);
        }

        return parts.join(', ');
    }

    // Get contextual suggestions based on current page
    function getContextualSuggestions() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';
        const userName = getUserName();

        // For first-time visitors on home page, don't show suggestions
        // Let the greeting speak for itself
        if (page === 'index' && !userName) {
            return [];
        }

        const suggestions = {
            'index': [
                'Analyze a job for me',
                'Help me update my resume',
                'What should I work on?'
            ],
            'positioning': [
                'Why this positioning?',
                'What if they ask about gaps?',
                'How do I stand out?'
            ],
            'documents': [
                'Why did you change this?',
                'Should I include more metrics?',
                'Is this ATS-friendly?'
            ],
            'outreach': [
                'Best time to reach out?',
                'How do I find the HM?',
                'Should I follow up?'
            ],
            'interview-intelligence': [
                'How do I prepare?',
                'What questions should I expect?',
                'Tips for this stage?'
            ],
            'prep-guide': [
                'What stories should I use?',
                'How do I handle salary talk?',
                'Questions to ask them?'
            ],
            'tracker': [
                'What should I focus on?',
                'When to follow up?',
                'How to prioritize?'
            ],
            'default': [
                'Help me stand out',
                'Review my strategy',
                'What should I do next?'
            ]
        };

        return suggestions[page] || suggestions['default'];
    }

    // Generate personalized greeting
    function getPersonalizedGreeting(userName, context) {
        if (userName) {
            return `Hey ${userName}! How can I help you?`;
        }
        return `Hi, I'm Henry! I'm always around if you need to chat. How can I help you?`;
    }

    // Create widget HTML
    function createWidget() {
        const context = getPageContext();
        const suggestions = getContextualSuggestions();
        const userName = getUserName();
        const greeting = getPersonalizedGreeting(userName, context);

        const widget = document.createElement('div');
        widget.id = 'ask-henry-widget';
        widget.innerHTML = `
            <!-- Floating Action Button -->
            <button class="ask-henry-fab" id="askHenryFab" aria-label="Ask Henry">
                <svg class="ask-henry-logo" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="fabRingGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                        </linearGradient>
                        <linearGradient id="fabStrokeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <circle cx="100" cy="100" r="85" stroke="url(#fabRingGradient)" stroke-width="4" fill="none"/>
                    <path d="M55 130 L55 70" stroke="#667eea" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <path d="M145 130 L145 50" stroke="url(#fabStrokeGradient)" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <path d="M55 100 L145 100" stroke="#764ba2" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <circle cx="145" cy="50" r="9" fill="#764ba2"/>
                </svg>
            </button>

            <!-- Chat Drawer -->
            <div class="ask-henry-drawer" id="askHenryDrawer">
                <div class="ask-henry-header">
                    <div class="ask-henry-title">
                        <svg class="ask-henry-header-logo" width="28" height="28" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="headerRingGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                </linearGradient>
                                <linearGradient id="headerStrokeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle cx="100" cy="100" r="85" stroke="url(#headerRingGradient)" stroke-width="4" fill="none"/>
                            <path d="M55 130 L55 70" stroke="#667eea" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <path d="M145 130 L145 50" stroke="url(#headerStrokeGradient)" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <path d="M55 100 L145 100" stroke="#764ba2" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <circle cx="145" cy="50" r="9" fill="#764ba2"/>
                        </svg>
                        <div>
                            <div class="ask-henry-title-text">Ask Henry</div>
                            <div class="ask-henry-title-context" id="askHenryContext">${context.description}</div>
                        </div>
                    </div>
                    <button class="ask-henry-close" id="askHenryClose" aria-label="Close">×</button>
                </div>

                <div class="ask-henry-messages" id="askHenryMessages">
                    <div class="ask-henry-message assistant">
                        ${greeting}
                    </div>
                </div>

                <div class="ask-henry-suggestions" id="askHenrySuggestions">
                    ${suggestions.map(s => `<button class="ask-henry-suggestion">${s}</button>`).join('')}
                </div>

                <div class="ask-henry-input-area">
                    <textarea
                        class="ask-henry-input"
                        id="askHenryInput"
                        placeholder="Ask me anything..."
                        rows="1"
                    ></textarea>
                    <button class="ask-henry-send" id="askHenrySend" aria-label="Send">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(widget);

        // Load previous conversation history
        loadConversationHistory();

        // If there's existing conversation, restore the messages
        if (conversationHistory.length > 0) {
            const messagesContainer = document.getElementById('askHenryMessages');
            // Clear the default greeting
            messagesContainer.innerHTML = '';

            // Add a "conversation continued" indicator
            messagesContainer.innerHTML = `
                <div class="ask-henry-message assistant" style="font-size: 0.85rem; opacity: 0.8;">
                    <em>Continuing our conversation...</em>
                </div>
            `;

            // Restore previous messages
            conversationHistory.forEach(msg => {
                const formattedContent = formatMessage(msg.content);
                const messageEl = document.createElement('div');
                messageEl.className = `ask-henry-message ${msg.role}`;
                messageEl.innerHTML = formattedContent;
                messagesContainer.appendChild(messageEl);
            });

            // Hide suggestions since conversation is ongoing
            document.getElementById('askHenrySuggestions').style.display = 'none';

            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Bind events
        document.getElementById('askHenryFab').addEventListener('click', toggleDrawer);
        document.getElementById('askHenryClose').addEventListener('click', closeDrawer);
        document.getElementById('askHenrySend').addEventListener('click', sendMessage);
        document.getElementById('askHenryInput').addEventListener('keydown', handleKeyDown);

        // Suggestion clicks
        document.querySelectorAll('.ask-henry-suggestion').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('askHenryInput').value = btn.textContent;
                sendMessage();
            });
        });

        // Auto-resize textarea
        document.getElementById('askHenryInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
    }

    function toggleDrawer() {
        isOpen ? closeDrawer() : openDrawer();
    }

    function openDrawer() {
        isOpen = true;
        document.getElementById('askHenryDrawer').classList.add('open');
        document.getElementById('askHenryFab').classList.add('hidden');
        document.getElementById('askHenryInput').focus();
    }

    function closeDrawer() {
        isOpen = false;
        document.getElementById('askHenryDrawer').classList.remove('open');
        document.getElementById('askHenryFab').classList.remove('hidden');
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    async function sendMessage() {
        const input = document.getElementById('askHenryInput');
        const message = input.value.trim();
        if (!message || isLoading) return;

        // Add user message to UI
        addMessage('user', message);
        conversationHistory.push({ role: 'user', content: message });
        saveConversationHistory();
        input.value = '';
        input.style.height = 'auto';

        // Hide suggestions after first message
        document.getElementById('askHenrySuggestions').style.display = 'none';

        // Show typing indicator
        isLoading = true;
        addTypingIndicator();

        try {
            // Gather context
            const context = getPageContext();
            const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
            const resumeData = JSON.parse(sessionStorage.getItem('resumeData') || '{}');
            const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            const pipelineData = getPipelineData();
            const userName = getUserName();

            const response = await fetch(`${API_BASE}/api/ask-henry`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(0, -1),
                    context: {
                        current_page: context.name,
                        page_description: context.description,
                        company: analysisData._company_name || analysisData.company || null,
                        role: analysisData.role_title || analysisData.role || null,
                        has_analysis: !!analysisData._company_name,
                        has_resume: !!resumeData.name,
                        has_pipeline: !!pipelineData,
                        user_name: userName
                    },
                    analysis_data: analysisData,
                    resume_data: resumeData,
                    user_profile: userProfile,
                    pipeline_data: pipelineData
                })
            });

            removeTypingIndicator();

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            addMessage('assistant', data.response);
            conversationHistory.push({ role: 'assistant', content: data.response });
            saveConversationHistory();

        } catch (error) {
            console.error('Ask Henry error:', error);
            removeTypingIndicator();
            addMessage('assistant', "Sorry, I'm having trouble connecting right now. Try again in a moment!");
        }

        isLoading = false;
    }

    function addMessage(role, content) {
        const messagesContainer = document.getElementById('askHenryMessages');
        const formattedContent = formatMessage(content);

        const messageEl = document.createElement('div');
        messageEl.className = `ask-henry-message ${role}`;
        messageEl.innerHTML = formattedContent;

        messagesContainer.appendChild(messageEl);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatMessage(content) {
        return content
            .split('\n\n').map(para => {
                if (para.match(/^[-•]\s/m)) {
                    const items = para.split('\n')
                        .filter(line => line.trim())
                        .map(line => `<li>${line.replace(/^[-•]\s*/, '')}</li>`)
                        .join('');
                    return `<ul>${items}</ul>`;
                }
                if (para.match(/^\d+\.\s/m)) {
                    const items = para.split('\n')
                        .filter(line => line.trim())
                        .map(line => `<li>${line.replace(/^\d+\.\s*/, '')}</li>`)
                        .join('');
                    return `<ol>${items}</ol>`;
                }
                return `<p>${para
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.+?)\*/g, '<em>$1</em>')
                }</p>`;
            })
            .join('');
    }

    function addTypingIndicator() {
        const messagesContainer = document.getElementById('askHenryMessages');
        const indicator = document.createElement('div');
        indicator.className = 'ask-henry-typing';
        indicator.id = 'askHenryTyping';
        indicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('askHenryTyping');
        if (indicator) indicator.remove();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})();
