/**
 * Strategy Navigation Component
 * A consistent sidebar navigation for strategy pages after the Overview
 *
 * Features:
 * - Collapsible sidebar on the left
 * - Shows current page indicator
 * - Remembers collapsed state
 * - Works across all strategy pages
 */

(function() {
    // Navigation items configuration - hierarchical structure
    const NAV_STRUCTURE = {
        topLevel: [
            {
                id: 'dashboard',
                label: 'Dashboard',
                href: 'dashboard.html'
            },
            {
                id: 'results',
                label: 'Job Fit Score',
                href: 'results.html'
            },
            {
                id: 'resume-leveling',
                label: 'Resume Level Analysis',
                href: 'resume-leveling.html'
            },
            {
                id: 'linkedin-scoring',
                label: 'LinkedIn Scoring',
                href: 'linkedin-scoring.html'
            }
        ],
        parent: {
            id: 'overview',
            label: 'Strategy Overview',
            href: 'overview.html'
        },
        children: [
            {
                id: 'positioning',
                label: 'Positioning Strategy',
                href: 'positioning.html'
            },
            {
                id: 'documents',
                label: 'Tailored Documents',
                href: 'documents.html'
            },
            {
                id: 'outreach',
                label: 'Network & Outreach',
                href: 'outreach.html'
            },
            {
                id: 'interview-intelligence',
                label: 'Interview Intelligence',
                href: 'interview-intelligence.html'
            },
            {
                id: 'tracker',
                label: 'Command Center',
                href: 'tracker.html'
            }
        ],
        bottomLevel: [
            {
                id: 'analyze',
                label: 'Analyze New Role',
                href: 'analyze.html'
            }
        ]
    };

    // Determine current page from URL
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'overview.html';
        const page = filename.replace('.html', '');

        // Map sub-pages to their parent nav item
        const pageMapping = {
            'interview-debrief': 'interview-intelligence',
            'interview-prep': 'interview-intelligence',
            'prep-guide': 'interview-intelligence',
            'practice-intro': 'interview-intelligence',
            'practice-drills': 'interview-intelligence',
            'mock-interview': 'interview-intelligence',
            'mock-debrief': 'interview-intelligence',
            'analyzing': 'analyze',
            'generating': 'overview',
            'strengthen': 'resume-leveling'
        };

        return pageMapping[page] || page;
    }

    // Get company and role from session/local storage for context
    // Only show context on job-specific pages (strategy pages), not on dashboard/tracker
    function getJobContext() {
        // Don't show context on general pages
        const currentPage = getCurrentPage();
        const generalPages = ['dashboard', 'tracker', 'analyze', 'profile'];
        if (generalPages.includes(currentPage)) {
            return null;
        }

        try {
            // First try sessionStorage analysisData
            let analysisData = sessionStorage.getItem('analysisData');
            if (analysisData) {
                const data = JSON.parse(analysisData);
                // Check all possible field names for company
                const company = data._company_name || data._company || data.company_name || data.company || '';
                const role = data.role_title || data._role || data.role || '';
                // Only return if we have a real company name (not "Company" placeholder)
                if (company && company !== 'Company' && company !== 'Unknown Company') {
                    return { company, role };
                }
            }
        } catch (e) {
            console.error('Error getting job context:', e);
        }
        return null;
    }

    // Create and inject the navigation styles
    function injectStyles() {
        const existingStyles = document.getElementById('strategy-nav-styles');
        if (existingStyles) return;

        const styles = document.createElement('style');
        styles.id = 'strategy-nav-styles';
        styles.textContent = `
            /* Logo now handled by top-nav.js component */

            /* Strategy Navigation Sidebar - positioned below top-nav (60px) */
            .strategy-nav {
                position: fixed;
                left: 0;
                top: 80px;
                z-index: 90;
                display: flex;
                align-items: flex-start;
            }

            .strategy-nav-toggle {
                width: 28px;
                height: 28px;
                background: #1a1a1a;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-left: none;
                border-radius: 0 6px 6px 0;
                color: #ffffff;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                transition: all 0.3s ease;
            }

            .strategy-nav-toggle:hover {
                background: #2a2a2a;
                border-color: rgba(255, 255, 255, 0.4);
            }

            .strategy-nav.expanded .strategy-nav-toggle {
                border-radius: 6px 0 0 6px;
            }

            .strategy-nav-panel {
                background: #0a0a0a;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: none;
                border-radius: 0 8px 8px 0;
                padding: 0;
                max-height: 0;
                width: 0;
                opacity: 0;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .strategy-nav.expanded .strategy-nav-panel {
                max-height: 600px;
                width: 240px;
                opacity: 1;
                padding: 12px;
            }

            .strategy-nav-context {
                padding: 8px 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin-bottom: 10px;
                border-left: 2px solid #ffffff;
            }

            .strategy-nav-context-company {
                font-weight: 600;
                color: #ffffff;
                font-size: 0.85rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .strategy-nav-context-role {
                color: #6b7280;
                font-size: 0.7rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .strategy-nav-list {
                list-style: none;
                margin: 0;
                padding: 0;
            }

            .strategy-nav-item {
                margin-bottom: 0;
            }

            .strategy-nav-top-link {
                display: block;
                padding: 8px 12px;
                color: #6b7280;
                text-decoration: none;
                font-size: 0.85rem;
                transition: all 0.2s ease;
                border-radius: 4px;
                margin-bottom: 2px;
                white-space: nowrap;
                overflow: visible;
            }

            .strategy-nav-top-link:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }

            .strategy-nav-top-link.active {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }

            .strategy-nav-divider {
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 8px 0;
            }

            .strategy-nav-parent {
                display: block;
                padding: 8px 10px;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.85rem;
                font-weight: 600;
                transition: all 0.2s ease;
            }

            .strategy-nav-parent:hover {
                color: #d1d5db;
            }

            .strategy-nav-parent.active {
                color: #ffffff;
            }

            .strategy-nav-children {
                list-style: none;
                margin: 0;
                padding: 0 0 0 10px;
                border-left: 1px solid rgba(255, 255, 255, 0.15);
                margin-left: 6px;
            }

            .strategy-nav-child {
                margin-bottom: 0;
            }

            .strategy-nav-child-link {
                display: block;
                padding: 6px 10px;
                color: #6b7280;
                text-decoration: none;
                font-size: 0.8rem;
                transition: all 0.2s ease;
                border-radius: 4px;
            }

            .strategy-nav-child-link:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }

            .strategy-nav-child-link.active {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }

            .strategy-nav-child-link::before {
                content: '•';
                margin-right: 6px;
                color: #4b5563;
            }

            .strategy-nav-child-link.active::before {
                color: #ffffff;
            }

            /* Disabled state for items requiring context */
            .strategy-nav-top-link.disabled,
            .strategy-nav-parent.disabled,
            .strategy-nav-child-link.disabled {
                opacity: 0.35;
                cursor: not-allowed;
                pointer-events: none;
            }

            .strategy-nav-top-link.disabled:hover,
            .strategy-nav-parent.disabled:hover,
            .strategy-nav-child-link.disabled:hover {
                background: transparent;
                color: #6b7280;
            }

            /* Floating dots indicator for collapsed state */
            .strategy-nav-dots {
                display: flex;
                flex-direction: column;
                gap: 5px;
                padding: 6px 5px;
                background: #0a0a0a;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: none;
                border-radius: 0 6px 6px 0;
            }

            .strategy-nav.expanded .strategy-nav-dots {
                display: none;
            }

            .strategy-nav-dot {
                width: 5px;
                height: 5px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transition: all 0.2s;
            }

            .strategy-nav-dot.active {
                background: #ffffff;
            }

            .strategy-nav-dot:hover {
                background: rgba(255, 255, 255, 0.6);
                transform: scale(1.2);
            }

            /* Highlighted Analyze button */
            .strategy-nav-analyze-btn {
                display: block;
                padding: 10px 14px;
                background: linear-gradient(135deg, #22d3ee 0%, #0ea5e9 100%);
                color: #000;
                text-decoration: none;
                font-size: 0.85rem;
                font-weight: 600;
                border-radius: 8px;
                text-align: center;
                transition: all 0.2s ease;
                margin-top: 4px;
            }

            .strategy-nav-analyze-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);
            }

            /* Footer section for profile/signout */
            .strategy-nav-footer {
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .strategy-nav-footer-link {
                display: block;
                padding: 6px 10px;
                color: #6b7280;
                text-decoration: none;
                font-size: 0.75rem;
                transition: all 0.2s ease;
                border-radius: 4px;
            }

            .strategy-nav-footer-link:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }

            /* Responsive adjustments */
            @media (max-width: 768px) {
                .strategy-nav {
                    top: auto;
                    bottom: 80px;
                }

                .strategy-nav.expanded .strategy-nav-panel {
                    width: 180px;
                }
            }

            /* Auto-hide nav at 60% width or less (approx 900px) */
            @media (max-width: 900px) {
                .strategy-nav-logo {
                    display: none;
                }

                .strategy-nav {
                    opacity: 0.3;
                    transition: opacity 0.3s ease;
                }

                .strategy-nav:hover,
                .strategy-nav.expanded {
                    opacity: 1;
                }

                .strategy-nav.expanded .strategy-nav-panel {
                    max-width: 200px;
                }
            }

            /* Hide page headers when strategy-nav is present (but NOT .top-nav) */
            body.has-strategy-nav header:not(.top-nav),
            body.has-strategy-nav .header:not(.top-nav),
            body.has-strategy-nav .header-container .logo {
                display: none !important;
            }

            /* No margin adjustments - nav overlays content */
        `;
        document.head.appendChild(styles);
    }

    // Check if there's an ACTIVE job context (user has selected a specific job)
    // This is different from just having tracked apps - user must click into a job
    function hasActiveJobContext() {
        // Only check sessionStorage for active analysis data
        // This is set when user clicks on a job in Command Center or analyzes a new role
        const analysisData = sessionStorage.getItem('analysisData');
        if (analysisData) {
            try {
                const data = JSON.parse(analysisData);
                if (data._company_name || data._company || data.company_name) {
                    return true;
                }
            } catch (e) {}
        }
        return false;
    }

    // Create the navigation HTML
    function createNavigation() {
        const currentPage = getCurrentPage();
        const jobContext = getJobContext();
        const isExpanded = localStorage.getItem('strategyNavExpanded') === 'true';
        const hasJobContext = hasActiveJobContext();

        // Pages that don't need active job context (always accessible)
        const alwaysAccessiblePages = ['dashboard', 'tracker', 'analyze'];

        // Create nav container
        const nav = document.createElement('nav');
        nav.className = `strategy-nav ${isExpanded ? 'expanded' : ''}`;
        nav.setAttribute('aria-label', 'Strategy Navigation');

        // Create dots indicator (for collapsed state) - all items
        const allItems = [...NAV_STRUCTURE.topLevel, NAV_STRUCTURE.parent, ...NAV_STRUCTURE.children, ...(NAV_STRUCTURE.bottomLevel || [])];
        const dotsHtml = allItems.map(item => {
            const isActive = currentPage === item.id;
            const needsContext = !alwaysAccessiblePages.includes(item.id);
            const isDisabled = needsContext && !hasJobContext;
            if (isDisabled) {
                return `<span class="strategy-nav-dot disabled" title="${item.label} (select an application first)"></span>`;
            }
            return `<a href="${item.href}" class="strategy-nav-dot ${isActive ? 'active' : ''}" title="${item.label}"></a>`;
        }).join('');

        // Create top-level items (Dashboard, Job Fit Score, Resume Level Analysis)
        const topLevelHtml = NAV_STRUCTURE.topLevel.map(item => {
            const isActive = currentPage === item.id;
            const needsContext = !alwaysAccessiblePages.includes(item.id);
            const isDisabled = needsContext && !hasJobContext;
            if (isDisabled) {
                return `<span class="strategy-nav-top-link disabled" title="Select an application first">${item.label}</span>`;
            }
            return `<a href="${item.href}" class="strategy-nav-top-link ${isActive ? 'active' : ''}">${item.label}</a>`;
        }).join('');

        // Check if parent is active
        const isParentActive = currentPage === NAV_STRUCTURE.parent.id;

        // Parent (Strategy Overview) needs context
        const parentNeedsContext = !alwaysAccessiblePages.includes(NAV_STRUCTURE.parent.id);
        const parentDisabled = parentNeedsContext && !hasJobContext;

        // Create children list items
        const childrenHtml = NAV_STRUCTURE.children.map(item => {
            const isActive = currentPage === item.id;
            const needsContext = !alwaysAccessiblePages.includes(item.id);
            const isDisabled = needsContext && !hasJobContext;
            if (isDisabled) {
                return `
                <li class="strategy-nav-child">
                    <span class="strategy-nav-child-link disabled" title="Select an application first">${item.label}</span>
                </li>
            `;
            }
            return `
                <li class="strategy-nav-child">
                    <a href="${item.href}" class="strategy-nav-child-link ${isActive ? 'active' : ''}">${item.label}</a>
                </li>
            `;
        }).join('');

        // Build context section if available - use actual company name
        const contextHtml = jobContext && jobContext.company ? `
            <div class="strategy-nav-context">
                <div class="strategy-nav-context-company">${jobContext.company}</div>
                <div class="strategy-nav-context-role">${jobContext.role}</div>
            </div>
        ` : '';

        // Create bottom-level items (Analyze New Role) - now with highlighted button style
        const bottomLevelHtml = (NAV_STRUCTURE.bottomLevel || []).map(item => {
            const isActive = currentPage === item.id;
            // Use highlighted button style for Analyze New Role
            if (item.id === 'analyze') {
                return `<a href="${item.href}" class="strategy-nav-analyze-btn">${item.label}</a>`;
            }
            return `<a href="${item.href}" class="strategy-nav-top-link ${isActive ? 'active' : ''}">${item.label}</a>`;
        }).join('');

        // Footer section removed - now handled by top nav "My Account" dropdown
        const footerHtml = '';

        // Parent link HTML (may be disabled)
        const parentLinkHtml = parentDisabled
            ? `<span class="strategy-nav-parent disabled" title="Select an application first">${NAV_STRUCTURE.parent.label}</span>`
            : `<a href="${NAV_STRUCTURE.parent.href}" class="strategy-nav-parent ${isParentActive ? 'active' : ''}">${NAV_STRUCTURE.parent.label}</a>`;

        nav.innerHTML = `
            <div class="strategy-nav-dots">${dotsHtml}</div>
            <button class="strategy-nav-toggle" aria-expanded="${isExpanded}" aria-controls="strategyNavPanel">
                ${isExpanded ? '◀' : '▶'}
            </button>
            <div class="strategy-nav-panel" id="strategyNavPanel">
                ${contextHtml}
                ${topLevelHtml}
                <div class="strategy-nav-divider"></div>
                <ul class="strategy-nav-list">
                    <li class="strategy-nav-item">
                        ${parentLinkHtml}
                        <ul class="strategy-nav-children">
                            ${childrenHtml}
                        </ul>
                    </li>
                </ul>
                ${bottomLevelHtml ? '<div class="strategy-nav-divider"></div>' + bottomLevelHtml : ''}
                ${footerHtml}
            </div>
        `;

        return nav;
    }

    // Toggle navigation expanded state
    function toggleNav(nav, toggle) {
        const isExpanded = nav.classList.toggle('expanded');
        toggle.setAttribute('aria-expanded', isExpanded);
        toggle.innerHTML = isExpanded ? '◀' : '▶';
        localStorage.setItem('strategyNavExpanded', isExpanded);
    }

    // Initialize the navigation
    async function init() {
        // Don't add navigation to public pages (before sign-in)
        // Note: profile-edit should show nav, only exclude initial profile setup
        const excludedPages = ['index', 'login'];
        const currentPage = getCurrentPage();
        const rawPage = window.location.pathname.split('/').pop()?.replace('.html', '') || '';

        if (excludedPages.includes(rawPage)) {
            return;
        }

        // Check if user is authenticated (localStorage profile OR Supabase session)
        const hasLocalProfile = localStorage.getItem('userProfile');
        let hasSupabaseSession = false;

        if (typeof HenryAuth !== 'undefined') {
            try {
                const session = await HenryAuth.getSession();
                hasSupabaseSession = !!session;
            } catch (e) {
                console.log('Could not check Supabase session');
            }
        }

        if (!hasLocalProfile && !hasSupabaseSession) {
            return;
        }

        // Inject styles
        injectStyles();

        // Add class to body for styling (top-nav.js now handles the header on all pages)
        document.body.classList.add('has-strategy-nav');

        // Logo is now handled by top-nav.js component - no longer injected here

        // Create and append navigation
        const nav = createNavigation();
        document.body.appendChild(nav);

        // Add toggle event listener
        const toggle = nav.querySelector('.strategy-nav-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => toggleNav(nav, toggle));
        }

        // Add sign out event listener
        const signOutLink = nav.querySelector('#navSignOut');
        if (signOutLink) {
            signOutLink.addEventListener('click', async (e) => {
                e.preventDefault();
                // Try Supabase sign out first
                if (typeof HenryAuth !== 'undefined') {
                    await HenryAuth.signOut();
                } else {
                    // Fallback: clear local storage and redirect
                    localStorage.removeItem('userProfile');
                    window.location.href = 'index.html';
                }
            });
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
