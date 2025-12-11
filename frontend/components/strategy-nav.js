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
                label: 'Network Intelligence & Outreach',
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
        ]
    };

    // Determine current page from URL
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'overview.html';
        return filename.replace('.html', '');
    }

    // Get company and role from session storage for context
    function getJobContext() {
        try {
            const analysisData = sessionStorage.getItem('analysisData');
            if (analysisData) {
                const data = JSON.parse(analysisData);
                return {
                    company: data._company_name || data._company || '',
                    role: data.role_title || data._role || ''
                };
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
                top: 50%;
                transform: translateY(-50%);
                z-index: 90;
                display: flex;
                align-items: center;
            }

            .strategy-nav-toggle {
                width: 32px;
                height: 32px;
                background: rgba(34, 211, 238, 0.15);
                border: 1px solid rgba(34, 211, 238, 0.3);
                border-radius: 0 8px 8px 0;
                color: #22d3ee;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.3s ease;
            }

            .strategy-nav-toggle:hover {
                background: rgba(34, 211, 238, 0.25);
                border-color: #22d3ee;
            }

            .strategy-nav.expanded .strategy-nav-toggle {
                border-radius: 8px 0 0 8px;
            }

            .strategy-nav-panel {
                background: rgba(15, 15, 15, 0.98);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: none;
                border-radius: 0 12px 12px 0;
                padding: 0;
                max-height: 0;
                width: 0;
                opacity: 0;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .strategy-nav.expanded .strategy-nav-panel {
                max-height: 500px;
                width: 220px;
                opacity: 1;
                padding: 16px;
            }

            .strategy-nav-context {
                padding: 8px 12px;
                background: rgba(34, 211, 238, 0.1);
                border-radius: 8px;
                margin-bottom: 12px;
                border-left: 3px solid #22d3ee;
            }

            .strategy-nav-context-company {
                font-weight: 600;
                color: #ffffff;
                font-size: 0.9rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .strategy-nav-context-role {
                color: #9ca3af;
                font-size: 0.75rem;
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
                margin-bottom: 2px;
            }

            .strategy-nav-parent {
                display: block;
                padding: 10px 12px;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.9rem;
                font-weight: 600;
                transition: all 0.2s ease;
            }

            .strategy-nav-parent:hover {
                color: #22d3ee;
            }

            .strategy-nav-parent.active {
                color: #22d3ee;
            }

            .strategy-nav-children {
                list-style: none;
                margin: 0;
                padding: 0 0 0 12px;
                border-left: 1px solid rgba(255, 255, 255, 0.1);
                margin-left: 8px;
            }

            .strategy-nav-child {
                margin-bottom: 2px;
            }

            .strategy-nav-child-link {
                display: block;
                padding: 8px 12px;
                color: #9ca3af;
                text-decoration: none;
                font-size: 0.85rem;
                transition: all 0.2s ease;
                border-radius: 6px;
            }

            .strategy-nav-child-link:hover {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }

            .strategy-nav-child-link.active {
                background: rgba(34, 211, 238, 0.15);
                color: #22d3ee;
            }

            .strategy-nav-child-link::before {
                content: '•';
                margin-right: 8px;
                color: #4b5563;
            }

            .strategy-nav-child-link.active::before {
                color: #22d3ee;
            }

            /* Floating dots indicator for collapsed state */
            .strategy-nav-dots {
                display: flex;
                flex-direction: column;
                gap: 6px;
                padding: 8px 6px;
                background: rgba(15, 15, 15, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: none;
                border-radius: 0 8px 8px 0;
            }

            .strategy-nav.expanded .strategy-nav-dots {
                display: none;
            }

            .strategy-nav-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transition: all 0.2s;
            }

            .strategy-nav-dot.active {
                background: #22d3ee;
                box-shadow: 0 0 8px rgba(34, 211, 238, 0.5);
            }

            .strategy-nav-dot:hover {
                background: rgba(255, 255, 255, 0.5);
                transform: scale(1.3);
            }

            /* Responsive adjustments */
            @media (max-width: 768px) {
                .strategy-nav {
                    bottom: 80px;
                    top: auto;
                    transform: none;
                }

                .strategy-nav.expanded .strategy-nav-panel {
                    width: 200px;
                }
            }

            /* Adjust main content when nav is present */
            body.has-strategy-nav .container {
                margin-left: 40px;
            }

            body.has-strategy-nav.nav-expanded .container {
                margin-left: 260px;
            }

            @media (max-width: 768px) {
                body.has-strategy-nav .container,
                body.has-strategy-nav.nav-expanded .container {
                    margin-left: 0;
                }
            }
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

        // Create dots indicator (for collapsed state) - all items including parent
        const allItems = [NAV_STRUCTURE.parent, ...NAV_STRUCTURE.children];
        const dotsHtml = allItems.map(item => {
            const isActive = currentPage === item.id;
            return `<a href="${item.href}" class="strategy-nav-dot ${isActive ? 'active' : ''}" title="${item.label}"></a>`;
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

        // Build context section if available
        const contextHtml = jobContext && jobContext.company ? `
            <div class="strategy-nav-context">
                <div class="strategy-nav-context-company">${jobContext.company}</div>
                <div class="strategy-nav-context-role">${jobContext.role}</div>
            </div>
        ` : '';

        nav.innerHTML = `
            <div class="strategy-nav-dots">${dotsHtml}</div>
            <button class="strategy-nav-toggle" aria-expanded="${isExpanded}" aria-controls="strategyNavPanel">
                ${isExpanded ? '◀' : '▶'}
            </button>
            <div class="strategy-nav-panel" id="strategyNavPanel">
                ${contextHtml}
                <ul class="strategy-nav-list">
                    <li class="strategy-nav-item">
                        <a href="${NAV_STRUCTURE.parent.href}" class="strategy-nav-parent ${isParentActive ? 'active' : ''}">${NAV_STRUCTURE.parent.label}</a>
                        <ul class="strategy-nav-children">
                            ${childrenHtml}
                        </ul>
                    </li>
                </ul>
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
        document.body.classList.toggle('nav-expanded', isExpanded);
    }

    // Initialize the navigation
    function init() {
        // Don't add navigation to certain pages
        const excludedPages = ['index', 'login', 'analyze', 'analyzing', 'results', 'generating', 'strengthen', 'profile', 'profile-edit'];
        const currentPage = getCurrentPage();

        if (excludedPages.includes(currentPage)) {
            return;
        }

        // Check if we have analysis data (needed for context)
        const hasContext = sessionStorage.getItem('analysisData') !== null;

        // Inject styles
        injectStyles();

        // Create and append navigation
        const nav = createNavigation();
        document.body.appendChild(nav);
        document.body.classList.add('has-strategy-nav');

        // Set up toggle behavior
        const toggle = nav.querySelector('.strategy-nav-toggle');
        toggle.addEventListener('click', () => toggleNav(nav, toggle));

        // Set initial expanded state class on body
        if (nav.classList.contains('expanded')) {
            document.body.classList.add('nav-expanded');
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
