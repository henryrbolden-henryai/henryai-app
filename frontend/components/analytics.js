/**
 * Google Analytics 4 - HenryHQ
 * Measurement ID: G-27RFZHTCKX
 *
 * This component initializes GA4 tracking.
 * Include this script on all pages that need analytics.
 */

(function() {
    // Don't load analytics in development/localhost
    const isDev = window.location.hostname === 'localhost' ||
                  window.location.hostname === '127.0.0.1';

    if (isDev) {
        console.log('[Analytics] Development mode - GA4 disabled');
        // Create stub functions so gtag calls don't error
        window.dataLayer = window.dataLayer || [];
        window.gtag = function() {
            console.log('[Analytics] gtag call (dev mode):', arguments);
        };
        return;
    }

    // Load GA4 script
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-27RFZHTCKX';
    document.head.appendChild(script);

    // Initialize dataLayer and gtag
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;

    gtag('js', new Date());
    gtag('config', 'G-27RFZHTCKX');

    console.log('[Analytics] GA4 initialized');
})();
