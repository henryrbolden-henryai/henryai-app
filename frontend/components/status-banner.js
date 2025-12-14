/**
 * Status Banner Component
 *
 * A simple, toggleable alert box for communicating service status to users.
 * Displays inline on the page (above Today's Focus on dashboard) rather than fixed position.
 *
 * To enable the banner:
 *   1. Set SHOW_STATUS_BANNER = true
 *   2. Update STATUS_MESSAGE as needed
 *
 * To disable:
 *   1. Set SHOW_STATUS_BANNER = false
 */

(function() {
    // =========================================================================
    // CONFIGURATION - Edit these values to control the banner
    // =========================================================================

    const SHOW_STATUS_BANNER = true;  // Set to true to show the banner

    const STATUS_MESSAGE = "Our AI provider is experiencing some hiccups. Some features may be slower than usual or temporarily unavailable. We're keeping an eye on it and appreciate your patience!";

    // =========================================================================
    // BANNER IMPLEMENTATION
    // =========================================================================

    if (!SHOW_STATUS_BANNER) return;

    function getUserFirstName() {
        // Try to get name from localStorage profile
        try {
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            if (profile.name) {
                return profile.name.split(' ')[0];
            }
        } catch (e) {}
        return null;
    }

    function injectStyles() {
        const styles = document.createElement('style');
        styles.id = 'status-banner-styles';
        styles.textContent = `
            .status-alert {
                background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
                border: 1px solid rgba(251, 191, 36, 0.3);
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 24px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }

            .status-alert-icon {
                font-size: 1.3rem;
                flex-shrink: 0;
                margin-top: 2px;
            }

            .status-alert-content {
                flex: 1;
            }

            .status-alert-message {
                color: #fbbf24;
                font-size: 0.95rem;
                line-height: 1.5;
            }

            .status-alert-close {
                background: transparent;
                border: none;
                color: rgba(251, 191, 36, 0.5);
                font-size: 1.4rem;
                cursor: pointer;
                padding: 0;
                line-height: 1;
                flex-shrink: 0;
            }

            .status-alert-close:hover {
                color: #fbbf24;
            }
        `;
        document.head.appendChild(styles);
    }

    function createAlert() {
        const firstName = getUserFirstName();
        const nameGreeting = firstName ? `, ${firstName}` : "";
        const fullMessage = `Ahh damn${nameGreeting}! ${STATUS_MESSAGE}`;

        const alert = document.createElement('div');
        alert.className = 'status-alert';
        alert.id = 'statusAlert';
        alert.innerHTML = `
            <span class="status-alert-icon">😅</span>
            <div class="status-alert-content">
                <span class="status-alert-message">${fullMessage}</span>
            </div>
            <button class="status-alert-close" aria-label="Dismiss">×</button>
        `;

        return alert;
    }

    function init() {
        // Don't show on public pages
        const publicPages = ['index', 'login', 'beta-access', 'henryhq-landing'];
        const currentPage = window.location.pathname.split('/').pop()?.replace('.html', '') || '';
        if (publicPages.includes(currentPage)) return;

        // Check if user is authenticated
        const hasProfile = localStorage.getItem('userProfile');
        if (!hasProfile) return;

        // Check if user already dismissed this session
        if (sessionStorage.getItem('statusAlertDismissed') === 'true') return;

        injectStyles();

        const alert = createAlert();

        // Find the best place to insert the alert
        // Priority: before .focus-section, before .quick-stats, or at start of .container
        const focusSection = document.querySelector('.focus-section');
        const quickStats = document.querySelector('.quick-stats');
        const container = document.querySelector('.container');

        if (focusSection) {
            focusSection.parentNode.insertBefore(alert, focusSection);
        } else if (quickStats) {
            quickStats.parentNode.insertBefore(alert, quickStats);
        } else if (container) {
            container.insertBefore(alert, container.firstChild);
        } else {
            // Fallback: append to body
            document.body.appendChild(alert);
        }

        // Set up close button
        const closeBtn = alert.querySelector('.status-alert-close');
        closeBtn.onclick = function() {
            alert.remove();
            sessionStorage.setItem('statusAlertDismissed', 'true');
        };
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
