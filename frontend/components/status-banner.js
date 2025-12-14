/**
 * Status Banner Component
 *
 * A simple, toggleable banner for communicating service status to users.
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

    const STATUS_MESSAGE = "our AI provider is experiencing some hiccups. Some features may be slower than usual. We're keeping an eye on it and appreciate your patience!";

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
            .status-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%);
                border-bottom: 1px solid rgba(251, 191, 36, 0.3);
                padding: 12px 24px;
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            }

            .status-banner-icon {
                font-size: 1.2rem;
            }

            .status-banner-message {
                color: #fbbf24;
                font-size: 0.9rem;
                line-height: 1.4;
            }

            .status-banner-close {
                background: transparent;
                border: none;
                color: rgba(251, 191, 36, 0.7);
                font-size: 1.2rem;
                cursor: pointer;
                padding: 4px 8px;
                margin-left: 8px;
            }

            .status-banner-close:hover {
                color: #fbbf24;
            }

            /* Push page content down when banner is visible */
            body.has-status-banner {
                padding-top: 52px;
            }

            body.has-status-banner .strategy-nav,
            body.has-status-banner .strategy-nav-logo {
                top: calc(24px + 52px);
            }

            body.has-status-banner .strategy-nav {
                top: calc(150px + 52px);
            }
        `;
        document.head.appendChild(styles);
    }

    function createBanner() {
        const firstName = getUserFirstName();
        const greeting = firstName ? `Hey ${firstName}, ` : "Heads up — ";

        const banner = document.createElement('div');
        banner.className = 'status-banner';
        banner.id = 'statusBanner';
        banner.innerHTML = `
            <span class="status-banner-icon">⚡</span>
            <span class="status-banner-message">${greeting}${STATUS_MESSAGE}</span>
            <button class="status-banner-close" onclick="document.getElementById('statusBanner').remove(); document.body.classList.remove('has-status-banner');" aria-label="Dismiss">×</button>
        `;

        return banner;
    }

    function init() {
        // Don't show on public pages
        const publicPages = ['index', 'login', 'beta-access'];
        const currentPage = window.location.pathname.split('/').pop()?.replace('.html', '') || '';
        if (publicPages.includes(currentPage)) return;

        // Check if user is authenticated
        const hasProfile = localStorage.getItem('userProfile');
        if (!hasProfile) return;

        // Check if user already dismissed this session
        if (sessionStorage.getItem('statusBannerDismissed') === 'true') return;

        injectStyles();

        const banner = createBanner();
        document.body.insertBefore(banner, document.body.firstChild);
        document.body.classList.add('has-status-banner');

        // Update close button to remember dismissal
        const closeBtn = banner.querySelector('.status-banner-close');
        closeBtn.onclick = function() {
            banner.remove();
            document.body.classList.remove('has-status-banner');
            sessionStorage.setItem('statusBannerDismissed', 'true');
        };
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
