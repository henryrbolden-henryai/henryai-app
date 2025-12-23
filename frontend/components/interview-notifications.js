/**
 * Interview Notification System for HenryHQ
 * Provides in-app toast notifications and optional browser notifications
 * for interview reminders (24hr, day-of, post-interview)
 */

(function() {
    'use strict';

    // ============================================================================
    // CONFIGURATION
    // ============================================================================
    const NOTIFICATION_CHECK_INTERVAL = 60 * 1000; // Check every minute
    const SHOWN_NOTIFICATIONS_KEY = 'shownInterviewNotifications';

    // ============================================================================
    // TOAST NOTIFICATION SYSTEM
    // ============================================================================
    function createToastContainer() {
        let container = document.getElementById('interviewToastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'interviewToastContainer';
            container.innerHTML = `
                <style>
                    #interviewToastContainer {
                        position: fixed;
                        top: 80px;
                        right: 20px;
                        z-index: 10000;
                        display: flex;
                        flex-direction: column;
                        gap: 12px;
                        max-width: 380px;
                    }

                    .interview-toast {
                        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                        border: 1px solid #374151;
                        border-radius: 12px;
                        padding: 16px;
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
                        animation: slideInRight 0.3s ease-out;
                        display: flex;
                        gap: 12px;
                        align-items: flex-start;
                    }

                    .interview-toast.dismissing {
                        animation: slideOutRight 0.3s ease-in forwards;
                    }

                    @keyframes slideInRight {
                        from {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                        to {
                            transform: translateX(0);
                            opacity: 1;
                        }
                    }

                    @keyframes slideOutRight {
                        to {
                            transform: translateX(100%);
                            opacity: 0;
                        }
                    }

                    .toast-icon {
                        font-size: 1.5rem;
                        flex-shrink: 0;
                    }

                    .toast-content {
                        flex: 1;
                    }

                    .toast-title {
                        color: #ffffff;
                        font-weight: 600;
                        font-size: 0.95rem;
                        margin-bottom: 4px;
                    }

                    .toast-message {
                        color: #9ca3af;
                        font-size: 0.85rem;
                        line-height: 1.4;
                    }

                    .toast-actions {
                        display: flex;
                        gap: 8px;
                        margin-top: 12px;
                    }

                    .toast-action {
                        padding: 8px 14px;
                        border-radius: 6px;
                        font-size: 0.85rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s;
                        border: none;
                    }

                    .toast-action.primary {
                        background: linear-gradient(135deg, #22d3ee, #06b6d4);
                        color: #000;
                    }

                    .toast-action.primary:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);
                    }

                    .toast-action.secondary {
                        background: transparent;
                        border: 1px solid #374151;
                        color: #9ca3af;
                    }

                    .toast-action.secondary:hover {
                        border-color: #9ca3af;
                        color: #e5e7eb;
                    }

                    .toast-close {
                        background: none;
                        border: none;
                        color: #6b7280;
                        cursor: pointer;
                        padding: 0;
                        font-size: 1.2rem;
                        line-height: 1;
                    }

                    .toast-close:hover {
                        color: #9ca3af;
                    }

                    .toast-type-24hr .toast-icon { color: #f59e0b; }
                    .toast-type-dayof .toast-icon { color: #22d3ee; }
                    .toast-type-post .toast-icon { color: #10b981; }
                </style>
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    function showToast(options) {
        const container = createToastContainer();

        const toast = document.createElement('div');
        toast.className = `interview-toast toast-type-${options.type || 'default'}`;

        let actionsHtml = '';
        if (options.actions && options.actions.length > 0) {
            actionsHtml = `
                <div class="toast-actions">
                    ${options.actions.map(action => `
                        <button class="toast-action ${action.primary ? 'primary' : 'secondary'}"
                                onclick="${action.onclick}">${action.label}</button>
                    `).join('')}
                </div>
            `;
        }

        toast.innerHTML = `
            <div class="toast-icon">${options.icon || '🔔'}</div>
            <div class="toast-content">
                <div class="toast-title">${options.title}</div>
                <div class="toast-message">${options.message}</div>
                ${actionsHtml}
            </div>
            <button class="toast-close" onclick="this.closest('.interview-toast').remove()">&times;</button>
        `;

        container.appendChild(toast);

        // Auto-dismiss after timeout
        const timeout = options.timeout || 15000;
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('dismissing');
                setTimeout(() => toast.remove(), 300);
            }
        }, timeout);

        return toast;
    }

    // ============================================================================
    // NOTIFICATION LOGIC
    // ============================================================================
    function getShownNotifications() {
        try {
            return JSON.parse(localStorage.getItem(SHOWN_NOTIFICATIONS_KEY) || '{}');
        } catch (e) {
            return {};
        }
    }

    function markNotificationShown(key) {
        const shown = getShownNotifications();
        shown[key] = Date.now();
        localStorage.setItem(SHOWN_NOTIFICATIONS_KEY, JSON.stringify(shown));
    }

    function isNotificationShown(key) {
        const shown = getShownNotifications();
        // Only consider notifications shown in the last 24 hours
        return shown[key] && (Date.now() - shown[key]) < 24 * 60 * 60 * 1000;
    }

    function checkInterviewNotifications() {
        const now = new Date();

        // Get upcoming interviews
        const upcomingInterviews = JSON.parse(localStorage.getItem('upcomingInterviews') || '[]');
        const trackedApps = JSON.parse(localStorage.getItem('trackedApplications') || '[]');
        const completedInterviews = JSON.parse(localStorage.getItem('completedInterviews') || '[]');

        // Combine all interviews with dates
        const allInterviews = [
            ...upcomingInterviews,
            ...trackedApps.filter(app => app.interviewDate).map(app => ({
                id: `app-${app.id}`,
                company: app.company,
                role: app.role,
                date: app.interviewDate,
                type: app.interviewType || 'Interview'
            }))
        ];

        allInterviews.forEach(interview => {
            if (!interview.date) return;

            const interviewDate = new Date(interview.date);
            const hoursUntil = (interviewDate - now) / (1000 * 60 * 60);
            const notifKey = `interview-${interview.id || interview.company + interview.role}`;

            // 24 hours before notification
            if (hoursUntil > 20 && hoursUntil <= 24) {
                const key = `${notifKey}-24hr`;
                if (!isNotificationShown(key)) {
                    showToast({
                        type: '24hr',
                        icon: '📅',
                        title: 'Interview Tomorrow',
                        message: `Your interview with ${interview.company} for ${interview.role} is tomorrow. Time to review your prep!`,
                        actions: [
                            {
                                label: 'Review Prep',
                                primary: true,
                                onclick: `window.location.href='prep-guide.html?id=${interview.id}'`
                            },
                            {
                                label: 'Dismiss',
                                onclick: `this.closest('.interview-toast').remove()`
                            }
                        ],
                        timeout: 30000
                    });
                    markNotificationShown(key);
                }
            }

            // Day-of notification (within 8 hours)
            if (hoursUntil > 0 && hoursUntil <= 8) {
                const key = `${notifKey}-dayof`;
                if (!isNotificationShown(key)) {
                    const timeStr = interviewDate.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
                    showToast({
                        type: 'dayof',
                        icon: '🎯',
                        title: 'Interview Today!',
                        message: `Your ${interview.type || 'interview'} with ${interview.company} is today at ${timeStr}. You've got this!`,
                        actions: [
                            {
                                label: 'Quick Prep',
                                primary: true,
                                onclick: `window.location.href='prep-guide.html?id=${interview.id}'`
                            },
                            {
                                label: 'Got It',
                                onclick: `this.closest('.interview-toast').remove()`
                            }
                        ],
                        timeout: 60000
                    });
                    markNotificationShown(key);
                }
            }
        });

        // Post-interview notifications (for interviews that happened 1-4 hours ago)
        completedInterviews.forEach(interview => {
            if (!interview.date) return;
            if (interview.debriefCompleted) return; // Already debriefed

            const interviewDate = new Date(interview.date);
            const hoursSince = (now - interviewDate) / (1000 * 60 * 60);
            const notifKey = `interview-${interview.id || interview.company + interview.role}-post`;

            if (hoursSince >= 1 && hoursSince <= 4 && !isNotificationShown(notifKey)) {
                showToast({
                    type: 'post',
                    icon: '💭',
                    title: 'How did it go?',
                    message: `Your interview with ${interview.company} just wrapped up. Want to do a quick debrief while it's fresh?`,
                    actions: [
                        {
                            label: 'Start Debrief',
                            primary: true,
                            onclick: `window.location.href='interview-debrief.html?id=${interview.id}'`
                        },
                        {
                            label: 'Later',
                            onclick: `this.closest('.interview-toast').remove()`
                        }
                    ],
                    timeout: 60000
                });
                markNotificationShown(notifKey);
            }
        });

        // Also check trackedApps for interviews that happened but aren't in completedInterviews
        trackedApps.forEach(app => {
            if (!app.interviewDate) return;
            if (app.debriefCompleted) return;

            const interviewDate = new Date(app.interviewDate);
            const hoursSince = (now - interviewDate) / (1000 * 60 * 60);
            const notifKey = `app-${app.id}-post`;

            if (hoursSince >= 1 && hoursSince <= 4 && !isNotificationShown(notifKey)) {
                showToast({
                    type: 'post',
                    icon: '💭',
                    title: 'How did it go?',
                    message: `Your interview with ${app.company} just wrapped up. Want to do a quick debrief?`,
                    actions: [
                        {
                            label: 'Start Debrief',
                            primary: true,
                            onclick: `window.location.href='interview-debrief.html?id=app-${app.id}'`
                        },
                        {
                            label: 'Later',
                            onclick: `this.closest('.interview-toast').remove()`
                        }
                    ],
                    timeout: 60000
                });
                markNotificationShown(notifKey);
            }
        });
    }

    // ============================================================================
    // BROWSER NOTIFICATIONS (OPTIONAL)
    // ============================================================================
    async function requestBrowserNotificationPermission() {
        if (!('Notification' in window)) {
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    }

    function showBrowserNotification(title, options) {
        if (Notification.permission === 'granted') {
            const notif = new Notification(title, {
                icon: '/favicon.ico',
                badge: '/favicon.ico',
                ...options
            });

            notif.onclick = function(event) {
                event.preventDefault();
                window.focus();
                if (options.url) {
                    window.location.href = options.url;
                }
                notif.close();
            };
        }
    }

    // ============================================================================
    // INITIALIZATION
    // ============================================================================
    function init() {
        // Initial check
        checkInterviewNotifications();

        // Set up interval to check periodically
        setInterval(checkInterviewNotifications, NOTIFICATION_CHECK_INTERVAL);
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export for use in other scripts
    window.InterviewNotifications = {
        showToast,
        checkNow: checkInterviewNotifications,
        requestPermission: requestBrowserNotificationPermission
    };
})();
