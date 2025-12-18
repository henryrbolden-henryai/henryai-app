/**
 * Hey Henry - Floating Chat Widget
 * A contextually-aware AI assistant available from any page
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // Inject styles
    const styles = `
        /* Hey Henry Floating Widget */
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

        /* Hey Henry Tooltip - Now JavaScript controlled */
        .ask-henry-tooltip {
            position: absolute;
            right: 70px;
            top: 50%;
            transform: translateY(-50%);
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            color: #fff;
            padding: 10px 16px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            font-family: 'DM Sans', -apple-system, sans-serif;
            pointer-events: none;
        }

        .ask-henry-tooltip::after {
            content: '';
            position: absolute;
            right: -12px;
            top: 50%;
            transform: translateY(-50%);
            border: 6px solid transparent;
            border-left-color: #1a1a1a;
        }

        .ask-henry-tooltip.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(-50%) translateX(-5px);
        }

        .ask-henry-fab.active .ask-henry-tooltip {
            display: none;
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

        /* ==========================================
           GENIE MODE (Welcome Flow) Styles
           ========================================== */

        /* Dark overlay for genie mode */
        .ask-henry-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 9998;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }

        .ask-henry-overlay.visible {
            opacity: 1;
            visibility: visible;
        }

        /* Genie mode drawer (centered modal) */
        .ask-henry-drawer.genie-mode {
            bottom: 50%;
            right: 50%;
            transform: translate(50%, 50%) scale(1);
            width: 500px;
            max-width: calc(100vw - 48px);
            height: auto;
            max-height: 80vh;
            border-radius: 24px;
            transform-origin: center center;
        }

        .ask-henry-drawer.genie-mode.open {
            transform: translate(50%, 50%) scale(1);
        }

        /* Welcome content area */
        .ask-henry-welcome-content {
            padding: 32px 28px;
            text-align: left;
        }

        .ask-henry-welcome-content h2 {
            font-size: 1.4rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 20px 0;
            line-height: 1.3;
        }

        .ask-henry-welcome-content p {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #e5e5e5;
            margin: 0 0 16px 0;
        }

        .ask-henry-welcome-content p:last-of-type {
            margin-bottom: 0;
        }

        /* Welcome actions area */
        .ask-henry-welcome-actions {
            padding: 20px 28px;
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .ask-henry-welcome-btn {
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            text-decoration: none;
            display: block;
        }

        .ask-henry-welcome-btn.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            border: none;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }

        .ask-henry-welcome-btn.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .ask-henry-welcome-btn.secondary {
            background: rgba(255, 255, 255, 0.05);
            color: #a0a0a0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ask-henry-welcome-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* FAB pulse animation for welcome */
        @keyframes fab-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }

        .ask-henry-fab.pulsing {
            animation: fab-pulse 0.8s ease-in-out 3;
        }

        /* Genie expand animation */
        @keyframes genie-expand {
            0% {
                bottom: 24px;
                right: 24px;
                width: 56px;
                height: 56px;
                border-radius: 28px;
                transform: translate(0, 0) scale(1);
            }
            100% {
                bottom: 50%;
                right: 50%;
                width: 500px;
                height: auto;
                border-radius: 24px;
                transform: translate(50%, 50%) scale(1);
            }
        }

        .ask-henry-drawer.genie-animating {
            animation: genie-expand 0.6s ease-out forwards;
        }

        /* Hide close button in genie mode (for required actions) */
        .ask-henry-drawer.genie-mode.no-dismiss .ask-henry-close {
            display: none;
        }

        /* Mobile genie mode */
        @media (max-width: 480px) {
            .ask-henry-drawer.genie-mode {
                width: calc(100vw - 32px);
                max-height: 85vh;
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
    let tooltipTimer = null;
    let tooltipHideTimer = null;
    let welcomeFlowState = null; // 'proactive_welcome' | 'first_action_prompt' | 'welcome_back' | null
    let isGenieMode = false;
    let lastGreetingIndex = -1; // Track last greeting to avoid repetition

    // Default tooltip messages (used when no context available)
    const defaultTooltipMessages = [
        "Got questions?",
        "Need strategy help?",
        "Ready when you are!",
        "Let me help!",
        "Thinking about your next move?"
    ];

    // Get context-aware tooltip message (prioritizes meaningful context over random)
    function getContextAwareTooltip() {
        const pipeline = getPipelineData();
        const emotionalState = getUserEmotionalState();

        // Priority 1: Pipeline stalled (apps but no movement)
        if (pipeline && pipeline.activeCount > 0 && pipeline.stalledDays >= 3) {
            return `${pipeline.activeCount} app${pipeline.activeCount !== 1 ? 's' : ''}, no movement. Want to review strategy?`;
        }

        // Priority 2: Upcoming interview (interviewing status)
        if (pipeline && pipeline.interviewingCount > 0) {
            const interviewApp = pipeline.topApps?.find(a =>
                ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview'].includes(a.status)
            );
            if (interviewApp) {
                return `Interview at ${interviewApp.company} coming up. Prepped?`;
            }
            return 'Interview coming up. Want to prep?';
        }

        // Priority 3: Emotional state - struggling
        if (emotionalState.holding_up === 'crushed' || emotionalState.holding_up === 'desperate') {
            return "Rough day? Let's talk strategy.";
        }

        // Priority 4: Recent rejection (check for rejected apps)
        if (pipeline && pipeline.rejectedCount > 0) {
            const recentReject = pipeline.topApps?.find(a => a.status === 'Rejected' && a.daysSinceUpdate <= 3);
            // Only show if we have recent reject data, otherwise use generic
            if (recentReject) {
                return `That ${recentReject.company} rejection sucked. Want to talk through it?`;
            }
            if (pipeline.rejectedCount >= 3) {
                return "Noticing some patterns. Want to dig in?";
            }
        }

        // Priority 5: No activity in 3+ days (different from stalled - no active apps)
        if (!pipeline || pipeline.activeCount === 0) {
            return "Taking a break, or stuck on something?";
        }

        // Default: Rotate through helpful defaults
        return defaultTooltipMessages[Math.floor(Math.random() * defaultTooltipMessages.length)];
    }

    // Alias for backwards compatibility (used in hover event)
    function getRandomTooltipMessage() {
        return getContextAwareTooltip();
    }

    // Show tooltip with context-aware message
    function showRandomTooltip() {
        if (isOpen) return; // Don't show if chat is open

        const tooltip = document.getElementById('askHenryTooltip');
        if (!tooltip) return;

        tooltip.textContent = getContextAwareTooltip();
        tooltip.classList.add('visible');

        // Hide after 3 seconds
        if (tooltipHideTimer) clearTimeout(tooltipHideTimer);
        tooltipHideTimer = setTimeout(() => {
            tooltip.classList.remove('visible');
        }, 3000);
    }

    // Start random tooltip appearances
    function startTooltipTimer() {
        // Show first tooltip after 5-10 seconds
        const initialDelay = 5000 + Math.random() * 5000;

        tooltipTimer = setTimeout(() => {
            showRandomTooltip();
            // Then show every 20-40 seconds
            scheduleNextTooltip();
        }, initialDelay);
    }

    function scheduleNextTooltip() {
        const nextDelay = 20000 + Math.random() * 20000; // 20-40 seconds
        tooltipTimer = setTimeout(() => {
            showRandomTooltip();
            scheduleNextTooltip();
        }, nextDelay);
    }

    // Stop tooltip timer (when chat is opened)
    function stopTooltipTimer() {
        if (tooltipTimer) {
            clearTimeout(tooltipTimer);
            tooltipTimer = null;
        }
        if (tooltipHideTimer) {
            clearTimeout(tooltipHideTimer);
            tooltipHideTimer = null;
        }
        const tooltip = document.getElementById('askHenryTooltip');
        if (tooltip) tooltip.classList.remove('visible');
    }

    // Load conversation history from sessionStorage (persists across page navigation)
    function loadConversationHistory() {
        try {
            const saved = sessionStorage.getItem('heyHenryConversation');
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
            sessionStorage.setItem('heyHenryConversation', JSON.stringify(toSave));
        } catch (e) {
            console.error('Error saving conversation history:', e);
        }
    }

    // Clear conversation history (for starting fresh)
    function clearConversationHistory() {
        conversationHistory = [];
        sessionStorage.removeItem('heyHenryConversation');
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

    // ==========================================
    // Welcome Flow Detection & Management
    // ==========================================

    // Check if user has a profile (indicates they've completed setup)
    function hasUserProfile() {
        try {
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            // Profile exists if it has a name
            return !!profile.name;
        } catch (e) {
            return false;
        }
    }

    // Get user's emotional state from profile
    function getUserEmotionalState() {
        try {
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            return {
                holding_up: profile.holding_up || 'zen',
                confidence: profile.confidence || 'strong',
                timeline: profile.timeline || 'actively_looking'
            };
        } catch (e) {
            return { holding_up: 'zen', confidence: 'strong', timeline: 'actively_looking' };
        }
    }

    // Generate tone guidance based on emotional state for backend
    function getToneGuidance(emotionalState) {
        const guidance = [];

        // Tone based on holding_up state
        const holdingUpGuidance = {
            'zen': 'Professional and efficient. Get to the point quickly.',
            'stressed': 'Reassuring but direct. Acknowledge the pressure, then provide clear guidance.',
            'struggling': 'Supportive and steady. Break things into manageable steps.',
            'desperate': 'Empathetic but realistic. Acknowledge difficulty, focus on actionable steps.',
            'crushed': 'Gentle and direct. Acknowledge the pain, but keep moving forward with small wins.'
        };
        guidance.push(holdingUpGuidance[emotionalState.holding_up] || holdingUpGuidance['zen']);

        // Strategy based on timeline
        const timelineGuidance = {
            'urgent': 'Move fast but smart. Prioritize high-probability opportunities.',
            'soon': 'Make every application count. No spray-and-pray.',
            'actively_looking': 'Time to be selective. Focus on quality over quantity.',
            'no_rush': 'Only roles worth making a move for. Be picky.'
        };
        guidance.push(timelineGuidance[emotionalState.timeline] || timelineGuidance['actively_looking']);

        // Support based on confidence
        const confidenceGuidance = {
            'low': 'Provide more explanation. Build confidence through logic and facts.',
            'need_validation': 'Validate their concerns, then redirect to evidence.',
            'shaky': 'Acknowledge feelings, but anchor responses in facts and progress.',
            'strong': 'Peer-level conversation. Be direct and strategic.'
        };
        guidance.push(confidenceGuidance[emotionalState.confidence] || confidenceGuidance['strong']);

        return guidance.join(' ');
    }

    // Determine which welcome flow state to show
    function determineWelcomeFlowState() {
        const hasProfile = hasUserProfile();
        const hasSeenWelcome = localStorage.getItem('heyHenrySeenWelcome') === 'true';
        const hasSeenWelcomeBack = sessionStorage.getItem('heyHenrySeenWelcomeBack') === 'true';
        const urlParams = new URLSearchParams(window.location.search);
        const fromProfileSetup = urlParams.get('from') === 'profile-setup';
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'index';

        // State 2: First-time user (no profile, hasn't seen welcome)
        // Only trigger on dashboard page
        if (!hasProfile && !hasSeenWelcome && currentPage === 'dashboard') {
            return 'proactive_welcome';
        }

        // State 3: Just completed profile setup
        if (hasProfile && fromProfileSetup && currentPage === 'dashboard') {
            return 'first_action_prompt';
        }

        // State 4: Returning user (has profile, new session, hasn't seen welcome back)
        if (hasProfile && !hasSeenWelcomeBack && currentPage === 'dashboard') {
            // Check if enough time has passed since signup (1 hour minimum)
            const signupTime = localStorage.getItem('heyHenrySignupTime');
            if (signupTime) {
                const hoursSinceSignup = (Date.now() - parseInt(signupTime)) / (1000 * 60 * 60);
                if (hoursSinceSignup >= 1) {
                    return 'welcome_back';
                }
            }
        }

        return null; // No welcome flow needed
    }

    // Get welcome content based on state
    function getWelcomeContent(state) {
        const userName = getUserName() || 'there';
        const emotionalState = getUserEmotionalState();

        if (state === 'proactive_welcome') {
            return {
                title: `Hey ${userName}, welcome to HenryHQ.`,
                message: `I'm Henry. I'll be your strategic advisor through this job search.

No mass applying. No fluff. Just honest fit checks, clear positioning, and materials grounded in your real experience. Never fabricated.

To get started, I need your resume, LinkedIn profile, and job search preferences. Takes about 3 to 5 minutes. After that, you're ready to analyze roles and move with intention.

I'm always here. If you're unsure about a role or how to position yourself, just ask.`,
                primaryCta: { text: 'Create My Profile', action: 'create_profile' },
                secondaryCta: null, // No secondary - profile required
                noDismiss: true
            };
        }

        if (state === 'first_action_prompt') {
            return {
                title: `Alright ${userName}, you're all set.`,
                message: `Ready to analyze your first role?`,
                primaryCta: { text: 'Analyze a Role', action: 'analyze_role' },
                secondaryCta: { text: "I'll Look Around First", action: 'close' },
                noDismiss: false
            };
        }

        if (state === 'welcome_back') {
            // Timeline-based context
            const timelineMessages = {
                'urgent': "I know you're under pressure. Let's find roles that are actually worth your time so you're not spinning your wheels.",
                'soon': "You need to move fast, so let's make every application count. No spray-and-pray.",
                'actively_looking': "You've got a solid window. Let's be strategic so you land something good, not just something fast.",
                'no_rush': "You're in a good position. Let's find roles that are actually worth making a move for."
            };

            // Confidence-based closing
            const confidenceMessages = {
                'low': "If you're ever unsure about a role or how to position yourself, just ask. I'm here to help you see what's actually working.",
                'need_validation': "If you're ever unsure about a role or how to position yourself, just ask. I'm here to help you see what's actually working.",
                'shaky': "Look, rejections suck, but they don't mean you're not good enough. They just mean the fit wasn't right. Let's find roles where it is.",
                'strong': "Got questions about a role or how to position yourself? Just ask. I'm here to help you stay sharp."
            };

            const timelineContext = timelineMessages[emotionalState.timeline] || timelineMessages['actively_looking'];
            const confidenceClosing = confidenceMessages[emotionalState.confidence] || confidenceMessages['strong'];

            return {
                title: `Welcome back, ${userName}!`,
                message: `${timelineContext}

Here's what you can do:
• **Analyze New Role:** Paste job description, I'll score fit
• **Command Center:** Track applications and interviews
• **Edit Profile:** Update anytime

${confidenceClosing}`,
                primaryCta: { text: 'Got It', action: 'close' },
                secondaryCta: null,
                noDismiss: false
            };
        }

        return null;
    }

    // Show welcome flow with genie animation
    function showWelcomeFlow(state) {
        welcomeFlowState = state;
        const content = getWelcomeContent(state);
        if (!content) return;

        const drawer = document.getElementById('askHenryDrawer');
        const fab = document.getElementById('askHenryFab');
        const messagesContainer = document.getElementById('askHenryMessages');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');
        const inputArea = document.querySelector('.ask-henry-input-area');

        // Create overlay if doesn't exist
        let overlay = document.getElementById('askHenryOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'askHenryOverlay';
            overlay.className = 'ask-henry-overlay';
            document.getElementById('ask-henry-widget').appendChild(overlay);
        }

        // Hide normal chat elements
        if (suggestionsContainer) suggestionsContainer.style.display = 'none';
        if (inputArea) inputArea.style.display = 'none';

        // Build welcome content
        const welcomeHTML = `
            <div class="ask-henry-welcome-content">
                <h2>${content.title}</h2>
                ${content.message.split('\n\n').map(p => `<p>${formatWelcomeMessage(p)}</p>`).join('')}
            </div>
            <div class="ask-henry-welcome-actions">
                <button class="ask-henry-welcome-btn primary" data-action="${content.primaryCta.action}">
                    ${content.primaryCta.text}
                </button>
                ${content.secondaryCta ? `
                <button class="ask-henry-welcome-btn secondary" data-action="${content.secondaryCta.action}">
                    ${content.secondaryCta.text}
                </button>
                ` : ''}
            </div>
        `;

        messagesContainer.innerHTML = welcomeHTML;

        // For proactive welcome, use genie animation
        if (state === 'proactive_welcome') {
            isGenieMode = true;

            // Pulse FAB first
            fab.classList.add('pulsing');

            setTimeout(() => {
                fab.classList.remove('pulsing');
                fab.classList.add('hidden');

                // Show overlay
                overlay.classList.add('visible');

                // Enable genie mode on drawer
                drawer.classList.add('genie-mode');
                if (content.noDismiss) {
                    drawer.classList.add('no-dismiss');
                }

                // Open the drawer
                drawer.classList.add('open');
                isOpen = true;

                // Bind welcome action buttons
                bindWelcomeActions(state);
            }, 2400); // After 3 pulses (0.8s * 3)
        } else {
            // Normal drawer open for other states
            drawer.classList.add('open');
            isOpen = true;
            fab.classList.add('hidden');
            bindWelcomeActions(state);
        }

        stopTooltipTimer();
    }

    // Format welcome message (handle bold, bullets)
    function formatWelcomeMessage(text) {
        return text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^• /gm, '&bull; ');
    }

    // Bind welcome action button clicks
    function bindWelcomeActions(state) {
        document.querySelectorAll('.ask-henry-welcome-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                handleWelcomeAction(action, state);
            });
        });
    }

    // Handle welcome flow action
    function handleWelcomeAction(action, state) {
        if (action === 'create_profile') {
            localStorage.setItem('heyHenrySeenWelcome', 'true');
            localStorage.setItem('heyHenrySignupTime', Date.now().toString());
            window.location.href = 'profile-edit.html';
        } else if (action === 'analyze_role') {
            // Remove URL param
            const url = new URL(window.location);
            url.searchParams.delete('from');
            window.history.replaceState({}, '', url);
            sessionStorage.setItem('heyHenrySeenWelcomeBack', 'true');
            window.location.href = 'analyze.html';
        } else if (action === 'close') {
            // Remove URL param if present
            const url = new URL(window.location);
            url.searchParams.delete('from');
            window.history.replaceState({}, '', url);
            sessionStorage.setItem('heyHenrySeenWelcomeBack', 'true');
            closeWelcomeFlow();
        }
    }

    // Close welcome flow and restore normal chat
    function closeWelcomeFlow() {
        const drawer = document.getElementById('askHenryDrawer');
        const fab = document.getElementById('askHenryFab');
        const overlay = document.getElementById('askHenryOverlay');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');
        const inputArea = document.querySelector('.ask-henry-input-area');
        const messagesContainer = document.getElementById('askHenryMessages');

        // Hide overlay
        if (overlay) overlay.classList.remove('visible');

        // Remove genie mode classes
        drawer.classList.remove('genie-mode', 'no-dismiss', 'genie-animating');

        // Close drawer
        drawer.classList.remove('open');
        fab.classList.remove('hidden');

        // Reset state
        isOpen = false;
        isGenieMode = false;
        welcomeFlowState = null;

        // Restore normal chat UI
        const userName = getUserName();
        const context = getPageContext();
        const greeting = getPersonalizedGreeting(userName, context);
        const suggestions = getContextualSuggestions();

        messagesContainer.innerHTML = `
            <div class="ask-henry-message assistant">
                ${greeting}
            </div>
        `;

        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = suggestions.map(s => `<button class="ask-henry-suggestion">${s}</button>`).join('');
            suggestionsContainer.style.display = '';
            // Re-bind suggestion clicks
            document.querySelectorAll('.ask-henry-suggestion').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.getElementById('askHenryInput').value = btn.textContent;
                    sendMessage();
                });
            });
        }
        if (inputArea) inputArea.style.display = '';

        // Restart tooltip timer
        startTooltipTimer();
    }

    // Check and trigger welcome flow on init
    function checkWelcomeFlow() {
        const state = determineWelcomeFlowState();
        if (state) {
            // Small delay to let the page settle
            setTimeout(() => {
                showWelcomeFlow(state);
            }, 500);
            return true;
        }
        return false;
    }

    // Get current page context
    function getPageContext() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';

        const contexts = {
            'index': { name: 'Home', description: 'Getting started with HenryHQ' },
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

        const context = contexts[page] || { name: 'HenryHQ', description: 'Your personal job search guide' };
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

            // Calculate days since last activity for stalled detection
            const lastActivityDates = activeApps.map(a => new Date(a.lastUpdated || a.dateAdded || a.dateApplied));
            const mostRecentActivity = lastActivityDates.length > 0 ? Math.max(...lastActivityDates) : Date.now();
            const stalledDays = Math.floor((Date.now() - mostRecentActivity) / (1000 * 60 * 60 * 24));

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
                // Aliased properties for greeting function
                activeCount: activeApps.length,
                interviewingCount: interviewingApps.length,
                rejectedCount: rejectedApps.length,
                stalledDays: stalledDays,
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

    // Generate personalized greeting with rotation and context-awareness
    function getPersonalizedGreeting(userName, context) {
        // No name - first time visitor
        if (!userName) {
            return `Hi, I'm Henry! I'm always around if you need to chat. How can I help you?`;
        }

        // Get emotional state and pipeline data for context-aware greetings
        const emotionalState = getUserEmotionalState();
        const pipeline = getPipelineData();

        // Context-aware greetings based on emotional state (highest priority)
        if (emotionalState.holding_up === 'crushed' || emotionalState.holding_up === 'desperate') {
            return `Hey ${userName}. This market's brutal. Let's figure out what's not working.`;
        }

        if (emotionalState.holding_up === 'stressed' || emotionalState.holding_up === 'struggling') {
            return `Hey ${userName}. I know you're under pressure. What do you need?`;
        }

        // Context-aware greetings based on pipeline (second priority)
        if (pipeline) {
            // Upcoming interviews
            if (pipeline.interviewingCount > 0) {
                return `Hey ${userName}! I see you've got ${pipeline.interviewingCount} interview${pipeline.interviewingCount !== 1 ? 's' : ''} lined up. Want to prep?`;
            }

            // Recent rejections pattern
            if (pipeline.rejectedCount >= 3) {
                return `Hey ${userName}. I'm noticing some patterns in your applications. Want to dig into what might be happening?`;
            }

            // Stalled pipeline (apps but no recent activity)
            if (pipeline.activeCount > 0 && pipeline.stalledDays >= 3) {
                return `Hey ${userName}! You've been sitting on a few roles. Want help deciding which are worth your time?`;
            }
        }

        // Standard greetings rotation (avoid repetition)
        const standardGreetings = [
            `Hey ${userName}! What's on your mind?`,
            `Hey ${userName}! What are you working on?`,
            `Hey ${userName}! How can I help?`,
            `Hey ${userName}! What are you thinking about?`,
            `Hey ${userName}! What do you need?`,
            `Hey ${userName}! What's up?`
        ];

        // Select next greeting, avoiding the last one used
        let greetingIndex;
        do {
            greetingIndex = Math.floor(Math.random() * standardGreetings.length);
        } while (greetingIndex === lastGreetingIndex && standardGreetings.length > 1);

        lastGreetingIndex = greetingIndex;
        return standardGreetings[greetingIndex];
    }

    // ==========================================
    // Document Refinement Detection (Phase 1.5)
    // ==========================================

    // Triggers that indicate user wants to modify a document
    const REFINEMENT_TRIGGERS = [
        'make it more', 'make this more', 'can you make',
        'add more', 'remove the', 'change the',
        'too generic', 'more specific', 'more senior',
        'less formal', 'more formal', 'shorter', 'longer',
        'rewrite', 'update the', 'modify the',
        'make my resume', 'make the resume', 'make my cover letter',
        'add keywords', 'more impactful', 'more action verbs',
        'sound more', 'tone down', 'emphasize', 'highlight'
    ];

    // ==========================================
    // Beta Feedback Collection
    // ==========================================

    // Triggers that indicate user is providing feedback
    const FEEDBACK_TRIGGERS = [
        // Bug reports
        'bug', 'broken', 'not working', 'doesn\'t work', 'error', 'issue', 'problem',
        'crashed', 'stuck', 'freezing', 'slow', 'glitch',
        // Feedback/suggestions
        'feedback', 'suggestion', 'suggest', 'would be nice', 'wish it could',
        'should have', 'would love', 'feature request', 'idea for',
        'could you add', 'can you add', 'please add',
        // Complaints/confusion
        'confusing', 'confused', 'don\'t understand', 'unclear', 'hard to use',
        'frustrating', 'annoying', 'wrong', 'incorrect',
        // Praise (also valuable)
        'love this', 'great feature', 'really helpful', 'awesome', 'works great',
        'thank you', 'thanks for', 'amazing'
    ];

    // State for feedback flow
    let pendingFeedback = null;
    let feedbackFlowState = null; // 'awaiting_details' | 'awaiting_confirmation' | null

    function detectFeedbackIntent(message) {
        const lowerMessage = message.toLowerCase();
        return FEEDBACK_TRIGGERS.some(trigger => lowerMessage.includes(trigger));
    }

    function getFollowUpQuestion(feedbackType, originalMessage) {
        const lowerMessage = originalMessage.toLowerCase();

        if (feedbackType === 'bug') {
            // Check if they already provided details
            const hasDetails = lowerMessage.length > 50 ||
                lowerMessage.includes('when i') ||
                lowerMessage.includes('after i') ||
                lowerMessage.includes('tried to');

            if (hasDetails) {
                return null; // Already detailed enough
            }
            return "Can you tell me what you were trying to do when this happened? That'll help the team track it down faster.";
        }

        if (feedbackType === 'feature_request') {
            const hasContext = lowerMessage.length > 40 ||
                lowerMessage.includes('would help') ||
                lowerMessage.includes('because') ||
                lowerMessage.includes('so that');

            if (hasContext) {
                return null;
            }
            return "What would that help you accomplish? Understanding the 'why' helps the team prioritize.";
        }

        if (feedbackType === 'ux_issue') {
            const hasContext = lowerMessage.length > 40 ||
                lowerMessage.includes('expected') ||
                lowerMessage.includes('thought it');

            if (hasContext) {
                return null;
            }
            return "What were you expecting to happen instead? That context really helps.";
        }

        if (feedbackType === 'praise') {
            // For praise, we can ask what specifically worked well
            return "That's great to hear! What specifically made it helpful for you?";
        }

        // General feedback - ask for more context
        return "Can you tell me more about that? The more detail, the better the team can act on it.";
    }

    function categorizeFeedback(message) {
        const lowerMessage = message.toLowerCase();

        // Bug/Issue
        if (['bug', 'broken', 'not working', 'doesn\'t work', 'error', 'crashed', 'stuck', 'glitch'].some(t => lowerMessage.includes(t))) {
            return 'bug';
        }
        // Feature request
        if (['wish', 'could you add', 'can you add', 'please add', 'feature', 'suggestion', 'suggest', 'would be nice', 'should have', 'would love', 'idea'].some(t => lowerMessage.includes(t))) {
            return 'feature_request';
        }
        // Praise
        if (['love', 'great', 'helpful', 'awesome', 'amazing', 'thank', 'works great'].some(t => lowerMessage.includes(t))) {
            return 'praise';
        }
        // Confusion/UX issue
        if (['confusing', 'confused', 'don\'t understand', 'unclear', 'hard to use', 'frustrating'].some(t => lowerMessage.includes(t))) {
            return 'ux_issue';
        }
        // General feedback
        return 'general';
    }

    // Helper to convert file to base64
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async function submitFeedback(feedbackText, feedbackType) {
        try {
            // Get recent conversation for context (last 6 messages)
            const conversationSnippet = conversationHistory.slice(-6).map(m => ({
                role: m.role,
                content: m.content.substring(0, 500) // Truncate long messages
            }));

            const context = getPageContext();

            // Handle screenshot if present
            let screenshotData = null;
            if (pendingFeedback?.screenshot) {
                try {
                    screenshotData = await fileToBase64(pendingFeedback.screenshot);
                    console.log('📸 Screenshot attached to feedback');
                } catch (e) {
                    console.error('Failed to process screenshot:', e);
                }
            }

            // Use HenryData if available, otherwise store locally
            if (typeof HenryData !== 'undefined' && HenryData.saveFeedback) {
                const result = await HenryData.saveFeedback({
                    type: feedbackType,
                    text: feedbackText,
                    currentPage: context.name,
                    context: {
                        pageDescription: context.description,
                        url: window.location.href,
                        userAgent: navigator.userAgent,
                        timestamp: new Date().toISOString(),
                        hasScreenshot: !!screenshotData
                    },
                    conversationSnippet: conversationSnippet,
                    screenshot: screenshotData
                });

                return { success: !result.error, id: result.data?.id };
            } else {
                // Fallback: store in localStorage for later sync
                const storedFeedback = JSON.parse(localStorage.getItem('pendingFeedback') || '[]');
                storedFeedback.push({
                    type: feedbackType,
                    text: feedbackText,
                    currentPage: context.name,
                    timestamp: new Date().toISOString(),
                    conversationSnippet: conversationSnippet,
                    screenshot: screenshotData
                });
                localStorage.setItem('pendingFeedback', JSON.stringify(storedFeedback));
                console.log('📝 Feedback stored locally (HenryData not available)');
                return { success: true, local: true };
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            return { success: false, error: error.message };
        }
    }

    function handleFeedbackConfirmation(confirmed) {
        if (!pendingFeedback) return;

        // Remove the confirmation buttons
        const confirmContainer = document.getElementById('feedbackConfirmContainer');
        if (confirmContainer) confirmContainer.remove();

        if (confirmed) {
            // Submit the feedback
            submitFeedback(pendingFeedback.text, pendingFeedback.type).then(result => {
                if (result.success) {
                    addMessage('assistant', "Thanks! I've shared your feedback with the Henry team. They review everything and it really helps make HenryHQ better. Is there anything else I can help you with?");
                    conversationHistory.push({
                        role: 'assistant',
                        content: "Thanks! I've shared your feedback with the Henry team. They review everything and it really helps make HenryHQ better. Is there anything else I can help you with?"
                    });
                } else {
                    addMessage('assistant', "I tried to send your feedback but hit a snag. Don't worry though - you can always email the team directly at hello@henryhq.ai. What else can I help with?");
                    conversationHistory.push({
                        role: 'assistant',
                        content: "I tried to send your feedback but hit a snag. Don't worry though - you can always email the team directly at hello@henryhq.ai. What else can I help with?"
                    });
                }
                saveConversationHistory();
            });
        } else {
            // User declined, continue normally
            addMessage('assistant', "No problem! Is there anything else I can help you with?");
            conversationHistory.push({ role: 'assistant', content: "No problem! Is there anything else I can help you with?" });
            saveConversationHistory();
        }

        // Reset feedback flow state
        pendingFeedback = null;
        feedbackFlowState = null;
    }

    function addFeedbackConfirmation(feedbackType) {
        const messagesContainer = document.getElementById('askHenryMessages');

        const confirmContainer = document.createElement('div');
        confirmContainer.id = 'feedbackConfirmContainer';
        confirmContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin: 12px 0;
        `;

        // Screenshot upload area (especially useful for bugs)
        const screenshotArea = document.createElement('div');
        screenshotArea.id = 'screenshotUploadArea';
        screenshotArea.style.cssText = `
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        `;
        screenshotArea.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <span style="color: #9ca3af; font-size: 0.85rem;">Add a screenshot (optional)</span>
        `;

        // Hidden file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        fileInput.id = 'feedbackScreenshotInput';

        // Screenshot preview container
        const previewContainer = document.createElement('div');
        previewContainer.id = 'screenshotPreview';
        previewContainer.style.cssText = `
            display: none;
            position: relative;
            max-width: 200px;
        `;

        screenshotArea.onclick = () => fileInput.click();
        screenshotArea.onmouseenter = () => {
            screenshotArea.style.borderColor = 'rgba(255, 255, 255, 0.4)';
            screenshotArea.style.background = 'rgba(255, 255, 255, 0.08)';
        };
        screenshotArea.onmouseleave = () => {
            screenshotArea.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            screenshotArea.style.background = 'rgba(255, 255, 255, 0.05)';
        };

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Screenshot must be under 5MB');
                    return;
                }

                // Store for later submission
                pendingFeedback.screenshot = file;

                // Show preview
                const reader = new FileReader();
                reader.onload = (event) => {
                    previewContainer.style.display = 'block';
                    previewContainer.innerHTML = `
                        <img src="${event.target.result}" style="max-width: 200px; max-height: 150px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                        <button id="removeScreenshot" style="
                            position: absolute;
                            top: -8px;
                            right: -8px;
                            width: 24px;
                            height: 24px;
                            border-radius: 50%;
                            background: #ef4444;
                            border: none;
                            color: white;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 14px;
                        ">×</button>
                    `;
                    // Update upload area text
                    screenshotArea.querySelector('span').textContent = 'Change screenshot';

                    // Add remove handler
                    document.getElementById('removeScreenshot').onclick = (e) => {
                        e.stopPropagation();
                        previewContainer.style.display = 'none';
                        previewContainer.innerHTML = '';
                        pendingFeedback.screenshot = null;
                        fileInput.value = '';
                        screenshotArea.querySelector('span').textContent = 'Add a screenshot (optional)';
                    };
                };
                reader.readAsDataURL(file);
            }
        };

        // Button row
        const buttonRow = document.createElement('div');
        buttonRow.style.cssText = `
            display: flex;
            gap: 10px;
        `;

        const yesBtn = document.createElement('button');
        yesBtn.textContent = 'Yes, send it';
        yesBtn.style.cssText = `
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: transform 0.2s;
        `;
        yesBtn.onclick = () => handleFeedbackConfirmation(true);

        const noBtn = document.createElement('button');
        noBtn.textContent = 'No thanks';
        noBtn.style.cssText = `
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            color: #a0a0a0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        `;
        noBtn.onclick = () => handleFeedbackConfirmation(false);

        buttonRow.appendChild(yesBtn);
        buttonRow.appendChild(noBtn);

        // Only show screenshot option for bugs and ux issues
        if (feedbackType === 'bug' || feedbackType === 'ux_issue') {
            confirmContainer.appendChild(screenshotArea);
            confirmContainer.appendChild(fileInput);
            confirmContainer.appendChild(previewContainer);
        }
        confirmContainer.appendChild(buttonRow);

        messagesContainer.appendChild(confirmContainer);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function detectRefinementRequest(message) {
        const lowerMessage = message.toLowerCase();
        return REFINEMENT_TRIGGERS.some(trigger => lowerMessage.includes(trigger));
    }

    async function handleRefinementRequest(message) {
        const currentPage = window.location.pathname;

        // Only handle refinements on document-related pages
        if (!currentPage.includes('documents') && !currentPage.includes('overview')) {
            return null; // Let normal chat handle it
        }

        const documentsData = JSON.parse(sessionStorage.getItem('documentsData') || '{}');
        const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');

        // Check if we have documents to refine
        if (!documentsData.resume_output && !documentsData.cover_letter) {
            return null; // No document to refine
        }

        // Determine document type from context or default to resume
        let documentType = 'resume';
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('cover letter')) {
            documentType = 'cover_letter';
        } else if (lowerMessage.includes('outreach')) {
            documentType = 'outreach';
        }

        const currentDoc = documentType === 'resume'
            ? documentsData.resume_output
            : documentsData.cover_letter;

        if (!currentDoc) {
            return null; // Specific document not available
        }

        try {
            const response = await fetch(`${API_BASE}/api/documents/refine`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_command: message,
                    target_document: documentType,
                    current_document_data: currentDoc,
                    original_jd_analysis: analysisData,
                    original_resume_data: analysisData._resume_json || {},
                    conversation_history: conversationHistory.slice(-10),
                    version: documentsData._version || 1
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Refinement failed');
            }

            const result = await response.json();

            // Update stored documents
            if (documentType === 'resume') {
                documentsData.resume_output = result.updated_document;
            } else {
                documentsData.cover_letter = result.updated_document;
            }
            documentsData._version = result.updated_document.version || (documentsData._version || 1) + 1;
            documentsData._lastRefinement = {
                timestamp: new Date().toISOString(),
                changes: result.changes_summary,
                summary: result.conversational_response
            };
            sessionStorage.setItem('documentsData', JSON.stringify(documentsData));

            // Format response with changes
            let changesText = '';
            if (result.changes_summary && result.changes_summary.sections_modified) {
                changesText = '\n\n**Changes made:**\n';
                result.changes_summary.sections_modified.forEach(section => {
                    changesText += `• ${section}\n`;
                });
            }

            const docName = documentType.replace('_', ' ');
            return {
                message: `I've updated your ${docName} (now v${documentsData._version}).\n\n${result.conversational_response}${changesText}\n\n*Refresh the page to see the updated document.*`,
                showRefreshButton: true,
                validation: result.validation
            };

        } catch (error) {
            console.error('Refinement error:', error);
            return {
                message: `I couldn't refine the document: ${error.message}. Try rephrasing your request or ask me a different question.`,
                showRefreshButton: false
            };
        }
    }

    function addRefreshButton() {
        const messagesContainer = document.getElementById('askHenryMessages');
        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'ask-henry-refresh-btn';
        refreshBtn.innerHTML = 'Refresh to see changes';
        refreshBtn.onclick = () => window.location.reload();

        // Add some basic inline styles for the button
        refreshBtn.style.cssText = `
            display: block;
            margin: 12px auto;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        `;
        refreshBtn.onmouseover = () => {
            refreshBtn.style.transform = 'translateY(-2px)';
            refreshBtn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
        };
        refreshBtn.onmouseout = () => {
            refreshBtn.style.transform = 'translateY(0)';
            refreshBtn.style.boxShadow = 'none';
        };

        messagesContainer.appendChild(refreshBtn);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
            <button class="ask-henry-fab" id="askHenryFab" aria-label="Hey Henry">
                <span class="ask-henry-tooltip" id="askHenryTooltip">Hey, it's Henry!</span>
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
                            <div class="ask-henry-title-text">Hey Henry</div>
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

        // Start random tooltip appearances
        startTooltipTimer();

        // Also show tooltip on hover as fallback
        const fab = document.getElementById('askHenryFab');
        const tooltip = document.getElementById('askHenryTooltip');
        fab.addEventListener('mouseenter', () => {
            if (!isOpen) {
                tooltip.textContent = getRandomTooltipMessage();
                tooltip.classList.add('visible');
            }
        });
        fab.addEventListener('mouseleave', () => {
            tooltip.classList.remove('visible');
        });

        // Check if welcome flow should be triggered
        checkWelcomeFlow();
    }

    function toggleDrawer() {
        isOpen ? closeDrawer() : openDrawer();
    }

    function openDrawer() {
        isOpen = true;
        stopTooltipTimer(); // Stop random tooltips when chat is open
        document.getElementById('askHenryDrawer').classList.add('open');
        document.getElementById('askHenryFab').classList.add('hidden');
        document.getElementById('askHenryInput').focus();
    }

    function closeDrawer() {
        isOpen = false;
        document.getElementById('askHenryDrawer').classList.remove('open');
        document.getElementById('askHenryFab').classList.remove('hidden');
        startTooltipTimer(); // Resume random tooltips when chat is closed
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
            // Handle ongoing feedback flow - user is providing additional details
            if (feedbackFlowState === 'awaiting_details' && pendingFeedback) {
                // User provided follow-up details - append to feedback and ask for confirmation
                pendingFeedback.details = message;
                pendingFeedback.text = `${pendingFeedback.text}\n\nAdditional context: ${message}`;
                feedbackFlowState = 'awaiting_confirmation';

                removeTypingIndicator();

                // Now ask for confirmation to send
                let confirmMessage;
                if (pendingFeedback.type === 'bug') {
                    confirmMessage = "Got it, that's really helpful. Would you like me to send this to the team so they can look into it?";
                } else if (pendingFeedback.type === 'feature_request') {
                    confirmMessage = "That makes sense! Would you like me to pass this along to the Henry team?";
                } else if (pendingFeedback.type === 'praise') {
                    confirmMessage = "Love it! Would you like me to share this with the team? They'll appreciate hearing it.";
                } else {
                    confirmMessage = "Thanks for the context. Would you like me to send this to the team?";
                }

                addMessage('assistant', confirmMessage);
                conversationHistory.push({ role: 'assistant', content: confirmMessage });
                saveConversationHistory();
                addFeedbackConfirmation(pendingFeedback.type);
                isLoading = false;
                return;
            }

            // Check if user is asking HOW to give feedback or attach screenshots
            const lowerMessage = message.toLowerCase();
            const askingAboutFeedback = (
                (lowerMessage.includes('how') || lowerMessage.includes('can i') || lowerMessage.includes('where')) &&
                (lowerMessage.includes('feedback') || lowerMessage.includes('screenshot') || lowerMessage.includes('report') || lowerMessage.includes('bug') || lowerMessage.includes('attach'))
            );

            if (askingAboutFeedback && !pendingFeedback && !feedbackFlowState) {
                removeTypingIndicator();
                const helpMessage = "To share feedback, just tell me what's on your mind! Say something like 'I found a bug' or 'I have a suggestion' and I'll walk you through it. For bugs and UX issues, you'll get the option to attach a screenshot before sending. What would you like to share?";
                addMessage('assistant', helpMessage);
                conversationHistory.push({ role: 'assistant', content: helpMessage });
                saveConversationHistory();
                isLoading = false;
                return;
            }

            // Check for NEW feedback intent (not already in a flow)
            if (detectFeedbackIntent(message) && !pendingFeedback && !feedbackFlowState) {
                const feedbackType = categorizeFeedback(message);
                pendingFeedback = { text: message, type: feedbackType };

                removeTypingIndicator();

                // Check if we need a follow-up question
                const followUpQuestion = getFollowUpQuestion(feedbackType, message);

                if (followUpQuestion) {
                    // Ask for more details first
                    feedbackFlowState = 'awaiting_details';
                    addMessage('assistant', followUpQuestion);
                    conversationHistory.push({ role: 'assistant', content: followUpQuestion });
                    saveConversationHistory();
                    isLoading = false;
                    return;
                }

                // Already has enough detail - go straight to confirmation
                feedbackFlowState = 'awaiting_confirmation';

                // Craft a contextual response based on feedback type
                let promptMessage;
                if (feedbackType === 'bug') {
                    promptMessage = "That sounds like something the team should know about. Would you like me to send this to them so they can look into it?";
                } else if (feedbackType === 'feature_request') {
                    promptMessage = "That's a great idea! Would you like me to pass this suggestion along to the Henry team?";
                } else if (feedbackType === 'praise') {
                    promptMessage = "That's awesome to hear! Would you like me to share this with the team? They love knowing what's working well.";
                } else if (feedbackType === 'ux_issue') {
                    promptMessage = "Thanks for letting me know - that's helpful feedback. Would you like me to share this with the team so they can improve it?";
                } else {
                    promptMessage = "That sounds like valuable feedback. Would you like me to send this to the Henry team?";
                }

                addMessage('assistant', promptMessage);
                conversationHistory.push({ role: 'assistant', content: promptMessage });
                saveConversationHistory();
                addFeedbackConfirmation(feedbackType);
                isLoading = false;
                return;
            }

            // Check for document refinement requests (Phase 1.5)
            if (detectRefinementRequest(message)) {
                const refinementResult = await handleRefinementRequest(message);
                if (refinementResult) {
                    removeTypingIndicator();
                    addMessage('assistant', refinementResult.message);
                    conversationHistory.push({ role: 'assistant', content: refinementResult.message });
                    saveConversationHistory();
                    if (refinementResult.showRefreshButton) {
                        addRefreshButton();
                    }
                    isLoading = false;
                    return;
                }
                // If refinementResult is null, continue with normal chat
            }

            // Gather context
            const context = getPageContext();
            const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
            const resumeData = JSON.parse(sessionStorage.getItem('resumeData') || '{}');
            const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            const pipelineData = getPipelineData();
            const userName = getUserName();
            const emotionalState = getUserEmotionalState();

            // Generate tone guidance based on emotional state
            const toneGuidance = getToneGuidance(emotionalState);

            const response = await fetch(`${API_BASE}/api/hey-henry`, {
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
                        user_name: userName,
                        // Emotional state for tone adaptation
                        emotional_state: emotionalState.holding_up,
                        confidence_level: emotionalState.confidence,
                        timeline: emotionalState.timeline,
                        tone_guidance: toneGuidance
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
            console.error('Hey Henry error:', error);
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

    // Expose global functions for external access
    window.openHeyHenry = function() {
        openDrawer();
    };

    // Keep legacy function for backwards compatibility
    window.openAskHenry = window.openHeyHenry;

    window.openHeyHenryWithPrompt = function(prompt) {
        openDrawer();
        // Small delay to ensure drawer is open and input is ready
        setTimeout(() => {
            const input = document.getElementById('askHenryInput');
            if (input) {
                input.value = prompt;
                sendMessage();
            }
        }, 100);
    };

    // Keep legacy function for backwards compatibility
    window.openAskHenryWithPrompt = window.openHeyHenryWithPrompt;
})();
