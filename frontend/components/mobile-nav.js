// HenryHQ Mobile Navigation Menu
(function() {
  'use strict';

  // Only show on mobile
  function isMobile() {
    return window.innerWidth <= 768;
  }

  // Check if on landing page
  function isLandingPage() {
    const path = window.location.pathname;
    return path === '/' || path === '/index.html' || path.endsWith('/index.html');
  }

  // Landing page navigation (matches desktop nav)
  const landingNavItems = [
    { label: 'About', href: '#about-henry' },
    { label: 'How it works', href: '#how-it-works' },
    { label: 'Features', href: '#capabilities' },
    { label: 'Pricing', href: '#pricing' }
  ];

  // App navigation (for logged-in users) - matches platform sidebar
  const appNavItems = [
    { label: 'Dashboard', href: '/dashboard.html' },
    { label: 'Job Fit Score', href: '/results.html' },
    { label: 'Resume Level Analysis', href: '/resume-leveling.html' },
    { label: 'LinkedIn Scoring', href: '/linkedin-scoring.html' }
  ];

  // Strategy Overview section
  const strategyItems = [
    { label: 'Positioning Strategy', href: '/positioning.html' },
    { label: 'Tailored Documents', href: '/documents.html' },
    { label: 'Screening Questions', href: '/screening-questions.html' },
    { label: 'Network & Outreach', href: '/outreach.html' },
    { label: 'Interview Intelligence', href: '/interview-prep.html' },
    { label: 'Command Center', href: '/tracker.html' }
  ];

  function createMobileNav() {
    // Create hamburger button
    const hamburger = document.createElement('button');
    hamburger.id = 'mobile-nav-hamburger';
    hamburger.setAttribute('aria-label', 'Open navigation menu');
    hamburger.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;

    // Create mobile nav drawer
    const drawer = document.createElement('nav');
    drawer.id = 'mobile-nav-drawer';
    drawer.setAttribute('aria-label', 'Mobile navigation');

    const currentPath = window.location.pathname;
    const onLanding = isLandingPage();

    // Choose nav items based on page
    const navItems = onLanding ? landingNavItems : appNavItems;

    drawer.innerHTML = onLanding ? `
      <div class="mobile-nav-header">
        <a href="/index.html" class="mobile-nav-logo-text"><em>Henry</em>HQ</a>
        <button class="mobile-nav-close" aria-label="Close navigation">&times;</button>
      </div>
      <ul class="mobile-nav-links">
        ${landingNavItems.map(item => `
          <li>
            <a href="${item.href}">${item.label}</a>
          </li>
        `).join('')}
      </ul>
      <div class="mobile-nav-footer">
        <a href="/login.html" class="mobile-nav-signin">Sign In</a>
      </div>
    ` : `
      <div class="mobile-nav-header">
        <a href="/index.html" class="mobile-nav-logo-text"><em>Henry</em>HQ</a>
        <button class="mobile-nav-close" aria-label="Close navigation">&times;</button>
      </div>
      <div class="mobile-nav-content">
        <ul class="mobile-nav-links">
          ${appNavItems.map(item => `
            <li>
              <a href="${item.href}" class="${currentPath.endsWith(item.href) ? 'active' : ''}">${item.label}</a>
            </li>
          `).join('')}
        </ul>
        <div class="mobile-nav-section">
          <h3 class="mobile-nav-section-title">Strategy Overview</h3>
          <ul class="mobile-nav-links mobile-nav-sub">
            ${strategyItems.map(item => `
              <li>
                <a href="${item.href}" class="${currentPath.endsWith(item.href) ? 'active' : ''}">${item.label}</a>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>
      <div class="mobile-nav-footer">
        <a href="/analyze.html" class="mobile-nav-cta">Analyze New Role</a>
      </div>
    `;

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'mobile-nav-overlay';

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      #mobile-nav-hamburger {
        display: none;
        position: fixed;
        top: 16px;
        left: 16px;
        z-index: 9999;
        width: 44px;
        height: 44px;
        background: rgba(10, 10, 11, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        cursor: pointer;
        padding: 12px 10px;
        flex-direction: column;
        justify-content: space-between;
        -webkit-tap-highlight-color: transparent;
      }

      #mobile-nav-hamburger span {
        display: block;
        width: 100%;
        height: 2px;
        background: #fafafa;
        border-radius: 1px;
        transition: all 0.3s ease;
      }

      #mobile-nav-hamburger.open span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
      }

      #mobile-nav-hamburger.open span:nth-child(2) {
        opacity: 0;
      }

      #mobile-nav-hamburger.open span:nth-child(3) {
        transform: rotate(-45deg) translate(6px, -6px);
      }

      #mobile-nav-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 9998;
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      #mobile-nav-overlay.visible {
        opacity: 1;
      }

      #mobile-nav-drawer {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        width: 280px;
        max-width: 85vw;
        background: #0a0a0b;
        z-index: 10000;
        transform: translateX(-100%);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: env(safe-area-inset-bottom, 0);
      }

      #mobile-nav-drawer.open {
        transform: translateX(0);
      }

      .mobile-nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }

      .mobile-nav-logo-text {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 1.75rem;
        font-weight: 400;
        color: #fafafa;
        text-decoration: none;
      }

      .mobile-nav-logo-text em {
        font-style: italic;
        color: #22d3ee;
      }

      .mobile-nav-close {
        width: 36px;
        height: 36px;
        background: transparent;
        border: none;
        color: #a1a1aa;
        font-size: 28px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        transition: background 0.2s;
      }

      .mobile-nav-close:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .mobile-nav-links {
        list-style: none;
        margin: 0;
        padding: 12px 0;
        flex: 1;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
      }

      .mobile-nav-links li {
        margin: 0;
      }

      .mobile-nav-links a {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 24px;
        color: #a1a1aa;
        text-decoration: none;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.2s;
      }

      .mobile-nav-links a:hover,
      .mobile-nav-links a:active {
        background: rgba(255, 255, 255, 0.05);
        color: #fafafa;
      }

      .mobile-nav-links a.active {
        background: rgba(34, 211, 238, 0.1);
        color: #22d3ee;
        border-left: 3px solid #22d3ee;
      }

      .mobile-nav-links .nav-icon {
        font-size: 20px;
        width: 28px;
        text-align: center;
      }

      .mobile-nav-footer {
        padding: 20px 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
      }

      .mobile-nav-footer a {
        color: #71717a;
        text-decoration: none;
        font-size: 14px;
      }

      .mobile-nav-signin {
        display: inline-block;
        background: #22d3ee;
        color: #000 !important;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        width: 100%;
      }

      .mobile-nav-content {
        flex: 1;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
      }

      .mobile-nav-section {
        padding: 8px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
      }

      .mobile-nav-section-title {
        font-size: 14px;
        font-weight: 600;
        color: #fafafa;
        padding: 16px 24px 8px;
        margin: 0;
      }

      .mobile-nav-sub a {
        padding-left: 36px;
        font-size: 15px;
        color: #71717a;
      }

      .mobile-nav-sub a::before {
        content: '•';
        position: absolute;
        left: 24px;
        color: #52525b;
      }

      .mobile-nav-sub li {
        position: relative;
      }

      .mobile-nav-cta {
        display: block;
        background: #22d3ee;
        color: #000 !important;
        padding: 14px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        width: 100%;
      }

      @media (max-width: 768px) {
        #mobile-nav-hamburger {
          display: flex;
        }

        #mobile-nav-overlay.visible {
          display: block;
        }
      }

      @media (min-width: 769px) {
        #mobile-nav-hamburger,
        #mobile-nav-drawer,
        #mobile-nav-overlay {
          display: none !important;
        }
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(hamburger);
    document.body.appendChild(overlay);
    document.body.appendChild(drawer);

    // Event handlers
    function openNav() {
      hamburger.classList.add('open');
      drawer.classList.add('open');
      overlay.style.display = 'block';
      requestAnimationFrame(() => {
        overlay.classList.add('visible');
      });
      document.body.style.overflow = 'hidden';
    }

    function closeNav() {
      hamburger.classList.remove('open');
      drawer.classList.remove('open');
      overlay.classList.remove('visible');
      document.body.style.overflow = '';
      setTimeout(() => {
        overlay.style.display = 'none';
      }, 300);
    }

    hamburger.addEventListener('click', () => {
      if (drawer.classList.contains('open')) {
        closeNav();
      } else {
        openNav();
      }
    });

    overlay.addEventListener('click', closeNav);
    drawer.querySelector('.mobile-nav-close').addEventListener('click', closeNav);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawer.classList.contains('open')) {
        closeNav();
      }
    });

    // Close on resize to desktop
    window.addEventListener('resize', () => {
      if (!isMobile() && drawer.classList.contains('open')) {
        closeNav();
      }
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createMobileNav);
  } else {
    createMobileNav();
  }
})();
