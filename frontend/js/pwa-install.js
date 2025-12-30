// HenryHQ PWA Install Prompt
(function() {
  'use strict';

  let deferredPrompt = null;
  let installBanner = null;

  // Check if already installed
  function isInstalled() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }

  // Check if install was dismissed recently (within 7 days)
  function wasDismissedRecently() {
    const dismissed = localStorage.getItem('henryhq-install-dismissed');
    if (!dismissed) return false;
    const dismissedDate = new Date(parseInt(dismissed, 10));
    const daysSince = (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24);
    return daysSince < 7;
  }

  // Create the install banner
  function createInstallBanner() {
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.innerHTML = `
      <div class="pwa-install-content">
        <div class="pwa-install-icon">
          <img src="/assets/henryhq-logo.png" alt="HenryHQ" width="40" height="40">
        </div>
        <div class="pwa-install-text">
          <strong>Install HenryHQ</strong>
          <span>Add to your home screen for quick access</span>
        </div>
        <div class="pwa-install-actions">
          <button class="pwa-install-btn" id="pwa-install-accept">Install</button>
          <button class="pwa-dismiss-btn" id="pwa-install-dismiss">Not now</button>
        </div>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      #pwa-install-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #0a0a0a;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
        z-index: 10000;
        transform: translateY(100%);
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0));
      }

      #pwa-install-banner.visible {
        transform: translateY(0);
      }

      .pwa-install-content {
        max-width: 600px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        gap: 1rem;
      }

      .pwa-install-icon img {
        border-radius: 10px;
        display: block;
      }

      .pwa-install-text {
        flex: 1;
        min-width: 0;
      }

      .pwa-install-text strong {
        display: block;
        color: #fafafa;
        font-size: 1rem;
        margin-bottom: 0.125rem;
      }

      .pwa-install-text span {
        display: block;
        color: #a1a1aa;
        font-size: 0.875rem;
      }

      .pwa-install-actions {
        display: flex;
        gap: 0.5rem;
        flex-shrink: 0;
      }

      .pwa-install-btn {
        background: #22d3ee;
        color: #000;
        border: none;
        padding: 0.625rem 1.25rem;
        font-size: 0.875rem;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        transition: opacity 0.2s;
      }

      .pwa-install-btn:hover {
        opacity: 0.9;
      }

      .pwa-dismiss-btn {
        background: transparent;
        color: #a1a1aa;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 0.625rem 1rem;
        font-size: 0.875rem;
        border-radius: 8px;
        cursor: pointer;
        transition: border-color 0.2s;
      }

      .pwa-dismiss-btn:hover {
        border-color: rgba(255, 255, 255, 0.3);
      }

      @media (max-width: 480px) {
        .pwa-install-content {
          flex-wrap: wrap;
        }

        .pwa-install-text {
          flex-basis: calc(100% - 56px);
        }

        .pwa-install-actions {
          width: 100%;
          margin-top: 0.5rem;
        }

        .pwa-install-btn,
        .pwa-dismiss-btn {
          flex: 1;
        }
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(banner);

    // Add event listeners
    document.getElementById('pwa-install-accept').addEventListener('click', handleInstall);
    document.getElementById('pwa-install-dismiss').addEventListener('click', handleDismiss);

    return banner;
  }

  // Show the banner
  function showBanner() {
    if (!installBanner) {
      installBanner = createInstallBanner();
    }
    // Delay to allow CSS transition
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        installBanner.classList.add('visible');
      });
    });
  }

  // Hide the banner
  function hideBanner() {
    if (installBanner) {
      installBanner.classList.remove('visible');
    }
  }

  // Handle install click
  async function handleInstall() {
    if (!deferredPrompt) {
      // For iOS, show instructions
      if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
        alert('To install HenryHQ:\n\n1. Tap the Share button\n2. Scroll down and tap "Add to Home Screen"\n3. Tap "Add"');
      }
      hideBanner();
      return;
    }

    // Show the install prompt
    deferredPrompt.prompt();

    // Wait for user response
    const { outcome } = await deferredPrompt.userChoice;
    console.log('[PWA] Install prompt outcome:', outcome);

    // Clear the prompt
    deferredPrompt = null;
    hideBanner();
  }

  // Handle dismiss click
  function handleDismiss() {
    localStorage.setItem('henryhq-install-dismissed', Date.now().toString());
    hideBanner();
  }

  // Register service worker
  async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('[PWA] Service worker registered:', registration.scope);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content available
              console.log('[PWA] New content available');
            }
          });
        });
      } catch (error) {
        console.error('[PWA] Service worker registration failed:', error);
      }
    }
  }

  // Initialize
  function init() {
    // Don't show if already installed
    if (isInstalled()) {
      console.log('[PWA] App is already installed');
      registerServiceWorker();
      return;
    }

    // Don't show if dismissed recently
    if (wasDismissedRecently()) {
      console.log('[PWA] Install prompt dismissed recently');
      registerServiceWorker();
      return;
    }

    // Register service worker
    registerServiceWorker();

    // Listen for beforeinstallprompt (Chrome, Edge, etc.)
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      console.log('[PWA] Install prompt available');

      // Show banner after a short delay (let user see the page first)
      setTimeout(showBanner, 3000);
    });

    // For iOS Safari - show banner after delay since there's no beforeinstallprompt
    if (/iPhone|iPad|iPod/.test(navigator.userAgent) && !window.navigator.standalone) {
      setTimeout(() => {
        if (!deferredPrompt) {
          showBanner();
        }
      }, 5000);
    }

    // Listen for successful install
    window.addEventListener('appinstalled', () => {
      console.log('[PWA] App installed successfully');
      hideBanner();
      deferredPrompt = null;
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
