/**
 * Ask Henry - Floating Chat Widget
 * A contextually-aware AI assistant available from any page
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://henryai-production.up.railway.app';

    // Inject styles
    const styles = `
        /* Ask Henry Floating Widget */
        .ask-henry-fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(34, 211, 238, 0.4);
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }

        .ask-henry-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 30px rgba(34, 211, 238, 0.5);
        }

        .ask-henry-fab.hidden {
            transform: scale(0);
            opacity: 0;
            pointer-events: none;
        }

        .ask-henry-fab-icon {
            font-size: 1.6rem;
        }

        .ask-henry-fab-pulse {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: rgba(34, 211, 238, 0.4);
            animation: pulse 2s ease-out infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.5; }
            100% { transform: scale(1.5); opacity: 0; }
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
            background: #111827;
            border: 1px solid #374151;
            border-radius: 16px;
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            transform: scale(0.9) translateY(20px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            transform-origin: bottom right;
        }

        .ask-henry-drawer.open {
            transform: scale(1) translateY(0);
            opacity: 1;
            pointer-events: auto;
        }

        /* Drawer Header */
        .ask-henry-header {
            padding: 16px 20px;
            background: linear-gradient(135deg, #1e3a5f 0%, #1a2e44 100%);
            border-bottom: 1px solid #374151;
            border-radius: 16px 16px 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ask-henry-title {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ask-henry-title-icon {
            font-size: 1.3rem;
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
        }

        .ask-henry-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .ask-henry-message.assistant {
            align-self: flex-start;
            background: #1f2937;
            border: 1px solid #374151;
            color: #e0e0e0;
        }

        .ask-henry-message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
            color: #000000;
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
            color: #22d3ee;
        }

        .ask-henry-message.user strong {
            color: #000000;
        }

        /* Typing Indicator */
        .ask-henry-typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
            width: fit-content;
        }

        .ask-henry-typing .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #22d3ee;
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
        }

        .ask-henry-suggestion {
            background: rgba(34, 211, 238, 0.1);
            border: 1px solid rgba(34, 211, 238, 0.3);
            border-radius: 16px;
            padding: 6px 12px;
            font-size: 0.8rem;
            color: #22d3ee;
            cursor: pointer;
            transition: all 0.2s;
        }

        .ask-henry-suggestion:hover {
            background: rgba(34, 211, 238, 0.2);
            border-color: #22d3ee;
        }

        /* Input Area */
        .ask-henry-input-area {
            padding: 12px 16px;
            border-top: 1px solid #374151;
            display: flex;
            gap: 10px;
        }

        .ask-henry-input {
            flex: 1;
            background: #1f2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 10px 14px;
            color: #ffffff;
            font-size: 0.9rem;
            resize: none;
            max-height: 100px;
        }

        .ask-henry-input:focus {
            outline: none;
            border-color: #22d3ee;
        }

        .ask-henry-input::placeholder {
            color: #6b7280;
        }

        .ask-henry-send {
            background: #22d3ee;
            border: none;
            border-radius: 8px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .ask-henry-send:hover {
            background: #06b6d4;
        }

        .ask-henry-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .ask-henry-send svg {
            width: 18px;
            height: 18px;
            fill: #000000;
        }

        /* Mobile Responsive */
        @media (max-width: 480px) {
            .ask-henry-drawer {
                bottom: 0;
                right: 0;
                width: 100%;
                max-width: 100%;
                height: 70vh;
                border-radius: 16px 16px 0 0;
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

        return contexts[page] || { name: 'HenryAI', description: 'Your AI career coach' };
    }

    // Get contextual suggestions based on current page
    function getContextualSuggestions() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';

        const suggestions = {
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

    // Create widget HTML
    function createWidget() {
        const context = getPageContext();
        const suggestions = getContextualSuggestions();

        const widget = document.createElement('div');
        widget.id = 'ask-henry-widget';
        widget.innerHTML = `
            <!-- Floating Action Button -->
            <button class="ask-henry-fab" id="askHenryFab" aria-label="Ask Henry">
                <div class="ask-henry-fab-pulse"></div>
                <span class="ask-henry-fab-icon">💬</span>
            </button>

            <!-- Chat Drawer -->
            <div class="ask-henry-drawer" id="askHenryDrawer">
                <div class="ask-henry-header">
                    <div class="ask-henry-title">
                        <span class="ask-henry-title-icon">🤖</span>
                        <div>
                            <div class="ask-henry-title-text">Ask Henry</div>
                            <div class="ask-henry-title-context" id="askHenryContext">${context.description}</div>
                        </div>
                    </div>
                    <button class="ask-henry-close" id="askHenryClose" aria-label="Close">×</button>
                </div>

                <div class="ask-henry-messages" id="askHenryMessages">
                    <div class="ask-henry-message assistant">
                        Hey! I'm Henry, your AI career coach. I can see you're on the <strong>${context.name}</strong> page. How can I help you right now?
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
                        has_resume: !!resumeData.name
                    },
                    analysis_data: analysisData,
                    resume_data: resumeData
                })
            });

            removeTypingIndicator();

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            addMessage('assistant', data.response);
            conversationHistory.push({ role: 'assistant', content: data.response });

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
