/**
 * Top Navigation Component
 * A consistent top navigation bar with HenryHQ logo and My Account dropdown
 *
 * Usage: Include this script in any page that needs the top nav
 * <script src="components/top-nav.js"></script>
 */

(function() {
    // Inject styles
    function injectStyles() {
        if (document.getElementById('top-nav-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'top-nav-styles';
        styles.textContent = `
            /* TOP NAVIGATION BAR */
            .top-nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
                background: var(--color-bg, #0a0a0b);
                border-bottom: 1px solid var(--color-border, rgba(255, 255, 255, 0.08));
                padding: 12px 24px;
            }

            .top-nav-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
            }

            .top-nav-logo {
                font-family: 'Instrument Serif', Georgia, serif;
                font-size: 1.5rem;
                font-weight: 400;
                color: var(--color-text, #fafafa);
                text-decoration: none;
            }

            .top-nav-logo em {
                font-style: italic;
                color: var(--color-accent, #22d3ee);
            }

            /* Account Dropdown */
            .account-dropdown {
                position: relative;
            }

            .account-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                background: transparent;
                border: 1px solid var(--color-border, rgba(255, 255, 255, 0.08));
                border-radius: 8px;
                padding: 8px 14px;
                color: var(--color-text, #fafafa);
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.2s ease;
                font-family: inherit;
            }

            .account-btn:hover {
                border-color: var(--color-accent, #22d3ee);
                color: var(--color-accent, #22d3ee);
            }

            .account-btn svg {
                width: 16px;
                height: 16px;
                transition: transform 0.2s ease;
            }

            .account-dropdown.open .account-btn svg {
                transform: rotate(180deg);
            }

            .account-menu {
                position: absolute;
                top: calc(100% + 8px);
                right: 0;
                min-width: 180px;
                background: var(--color-surface, #141416);
                border: 1px solid var(--color-border, rgba(255, 255, 255, 0.08));
                border-radius: 10px;
                padding: 8px 0;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: all 0.2s ease;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            }

            .account-dropdown.open .account-menu {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }

            .account-menu-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 16px;
                color: var(--color-text-secondary, #71717a);
                text-decoration: none;
                font-size: 0.9rem;
                transition: all 0.15s ease;
            }

            .account-menu-item:hover {
                background: var(--color-surface-elevated, #1c1c1f);
                color: var(--color-text, #fafafa);
            }

            .account-menu-item svg {
                width: 16px;
                height: 16px;
                opacity: 0.7;
            }

            .account-menu-divider {
                height: 1px;
                background: var(--color-border, rgba(255, 255, 255, 0.08));
                margin: 8px 0;
            }

            .account-menu-item.danger {
                color: #f87171;
            }

            .account-menu-item.danger:hover {
                background: rgba(248, 113, 113, 0.1);
                color: #f87171;
            }

            /* Ensure body has padding for fixed nav */
            body.has-top-nav {
                padding-top: 60px !important;
            }

            /* Hide old headers when top-nav is present */
            body.has-top-nav > header:not(.top-nav),
            body.has-top-nav > .header:not(.top-nav) {
                display: none !important;
            }
        `;
        document.head.appendChild(styles);
    }

    // Create the navigation HTML
    function createNav() {
        const nav = document.createElement('nav');
        nav.className = 'top-nav';
        nav.innerHTML = `
            <div class="top-nav-container">
                <a href="/dashboard" class="top-nav-logo"><em>Henry</em>HQ</a>
                <div class="account-dropdown" id="accountDropdown">
                    <button class="account-btn" id="accountBtn">
                        My Account
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    <div class="account-menu">
                        <a href="/profile-edit" class="account-menu-item">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z" />
                            </svg>
                            Edit Profile
                        </a>
                        <a href="/settings" class="account-menu-item">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M7.84 1.804A1 1 0 018.82 1h2.36a1 1 0 01.98.804l.331 1.652a6.993 6.993 0 011.929 1.115l1.598-.54a1 1 0 011.186.447l1.18 2.044a1 1 0 01-.205 1.251l-1.267 1.113a7.047 7.047 0 010 2.228l1.267 1.113a1 1 0 01.206 1.25l-1.18 2.045a1 1 0 01-1.187.447l-1.598-.54a6.993 6.993 0 01-1.929 1.115l-.33 1.652a1 1 0 01-.98.804H8.82a1 1 0 01-.98-.804l-.331-1.652a6.993 6.993 0 01-1.929-1.115l-1.598.54a1 1 0 01-1.186-.447l-1.18-2.044a1 1 0 01.205-1.251l1.267-1.114a7.05 7.05 0 010-2.227L1.821 7.773a1 1 0 01-.206-1.25l1.18-2.045a1 1 0 011.187-.447l1.598.54A6.993 6.993 0 017.51 3.456l.33-1.652zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                            </svg>
                            Settings
                        </a>
                        <div class="account-menu-divider"></div>
                        <a href="#" class="account-menu-item danger" id="signOutBtn">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M3 4.25A2.25 2.25 0 015.25 2h5.5A2.25 2.25 0 0113 4.25v2a.75.75 0 01-1.5 0v-2a.75.75 0 00-.75-.75h-5.5a.75.75 0 00-.75.75v11.5c0 .414.336.75.75.75h5.5a.75.75 0 00.75-.75v-2a.75.75 0 011.5 0v2A2.25 2.25 0 0110.75 18h-5.5A2.25 2.25 0 013 15.75V4.25z" clip-rule="evenodd" />
                                <path fill-rule="evenodd" d="M19 10a.75.75 0 00-.75-.75H8.704l1.048-.943a.75.75 0 10-1.004-1.114l-2.5 2.25a.75.75 0 000 1.114l2.5 2.25a.75.75 0 101.004-1.114l-1.048-.943h9.546A.75.75 0 0019 10z" clip-rule="evenodd" />
                            </svg>
                            Sign Out
                        </a>
                    </div>
                </div>
            </div>
        `;
        return nav;
    }

    // Toggle dropdown
    function toggleDropdown() {
        const dropdown = document.getElementById('accountDropdown');
        if (dropdown) {
            dropdown.classList.toggle('open');
        }
    }

    // Close dropdown when clicking outside
    function handleClickOutside(e) {
        const dropdown = document.getElementById('accountDropdown');
        if (dropdown && !dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    }

    // Sign out function
    function signOut() {
        // Clear all auth data
        localStorage.removeItem('supabase_session');
        localStorage.removeItem('beta_verified');
        localStorage.removeItem('henryhq_user');
        localStorage.removeItem('userProfile');
        sessionStorage.clear();
        // Redirect to login
        window.location.href = '/login';
    }

    // Initialize
    function init() {
        // Don't initialize if already present
        if (document.querySelector('.top-nav')) return;

        // Inject styles
        injectStyles();

        // Create and insert nav at the start of body
        const nav = createNav();
        document.body.insertBefore(nav, document.body.firstChild);

        // Add class to body for padding
        document.body.classList.add('has-top-nav');

        // Add event listeners
        const accountBtn = document.getElementById('accountBtn');
        if (accountBtn) {
            accountBtn.addEventListener('click', toggleDropdown);
        }

        const signOutBtn = document.getElementById('signOutBtn');
        if (signOutBtn) {
            signOutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                signOut();
            });
        }

        document.addEventListener('click', handleClickOutside);
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
