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
                id: 'results',
                label: 'Job Fit Score',
                href: 'results.html'
            },
            {
                id: 'skills-analysis',
                label: 'Skills Analysis',
                href: 'skills-analysis.html'
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
        return filename.replace('.html', '');
    }

    // Get company and role from session/local storage for context
    function getJobContext() {
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

            // Fallback: try to get from tracked applications in localStorage
            const trackedApps = localStorage.getItem('trackedApplications');
            if (trackedApps) {
                const apps = JSON.parse(trackedApps);
                // Get the most recently updated active application
                const activeApps = apps.filter(a => a.status !== 'Rejected' && a.status !== 'Withdrawn');
                if (activeApps.length > 0) {
                    // Sort by lastUpdated descending
                    activeApps.sort((a, b) => new Date(b.lastUpdated || b.dateAdded) - new Date(a.lastUpdated || a.dateAdded));
                    const mostRecent = activeApps[0];
                    const company = mostRecent.company || '';
                    // Only return if we have a real company name
                    if (company && company !== 'Company' && company !== 'Unknown Company') {
                        return {
                            company: company,
                            role: mostRecent.role || ''
                        };
                    }
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
            /* Strategy Navigation Sidebar */
            .strategy-nav {
                position: fixed;
                left: 0;
                top: 120px;
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
                max-height: 500px;
                width: 200px;
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
                padding: 6px 10px;
                color: #6b7280;
                text-decoration: none;
                font-size: 0.8rem;
                transition: all 0.2s ease;
                border-radius: 4px;
                margin-bottom: 2px;
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

            /* No margin adjustments - nav overlays content */
        `;
        document.head.appendChild(styles);
    }

    // Create the navigation HTML
    function createNavigation() {
        const currentPage = getCurrentPage();
        const jobContext = getJobContext();
        const isExpanded = localStorage.getItem('strategyNavExpanded') === 'true';

        // Create nav container
        const nav = document.createElement('nav');
        nav.className = `strategy-nav ${isExpanded ? 'expanded' : ''}`;
        nav.setAttribute('aria-label', 'Strategy Navigation');

        // Create dots indicator (for collapsed state) - all items
        const allItems = [...NAV_STRUCTURE.topLevel, NAV_STRUCTURE.parent, ...NAV_STRUCTURE.children, ...(NAV_STRUCTURE.bottomLevel || [])];
        const dotsHtml = allItems.map(item => {
            const isActive = currentPage === item.id;
            return `<a href="${item.href}" class="strategy-nav-dot ${isActive ? 'active' : ''}" title="${item.label}"></a>`;
        }).join('');

        // Create top-level items (Analyze, Job Fit Score)
        const topLevelHtml = NAV_STRUCTURE.topLevel.map(item => {
            const isActive = currentPage === item.id;
            return `<a href="${item.href}" class="strategy-nav-top-link ${isActive ? 'active' : ''}">${item.label}</a>`;
        }).join('');

        // Check if parent is active
        const isParentActive = currentPage === NAV_STRUCTURE.parent.id;

        // Create children list items
        const childrenHtml = NAV_STRUCTURE.children.map(item => {
            const isActive = currentPage === item.id;
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

        // Create bottom-level items (Analyze New Role)
        const bottomLevelHtml = (NAV_STRUCTURE.bottomLevel || []).map(item => {
            const isActive = currentPage === item.id;
            return `<a href="${item.href}" class="strategy-nav-top-link ${isActive ? 'active' : ''}">${item.label}</a>`;
        }).join('');

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
                        <a href="${NAV_STRUCTURE.parent.href}" class="strategy-nav-parent ${isParentActive ? 'active' : ''}">${NAV_STRUCTURE.parent.label}</a>
                        <ul class="strategy-nav-children">
                            ${childrenHtml}
                        </ul>
                    </li>
                </ul>
                ${bottomLevelHtml ? '<div class="strategy-nav-divider"></div>' + bottomLevelHtml : ''}
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
    function init() {
        // Don't add navigation to certain pages
        const excludedPages = ['index', 'login', 'analyze', 'analyzing', 'results', 'generating', 'strengthen', 'profile', 'profile-edit', 'resume-leveling', 'skills-analysis'];
        const currentPage = getCurrentPage();

        if (excludedPages.includes(currentPage)) {
            return;
        }

        // Inject styles
        injectStyles();

        // Create and append navigation
        const nav = createNavigation();
        document.body.appendChild(nav);

        // Add toggle event listener
        const toggle = nav.querySelector('.strategy-nav-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => toggleNav(nav, toggle));
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
