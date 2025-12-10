/**
 * Auth Check Script
 * Include this on pages that require authentication
 *
 * Usage: Add these scripts to your page (in this order):
 *   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
 *   <script src="js/supabase-client.js"></script>
 *   <script src="js/auth-check.js"></script>
 */

(async function() {
    // Wait for Supabase to be ready
    if (typeof HenryAuth === 'undefined') {
        console.error('HenryAuth not loaded. Make sure supabase-client.js is included before auth-check.js');
        return;
    }

    const session = await HenryAuth.getSession();

    if (!session) {
        // Not logged in - redirect to login
        sessionStorage.setItem('redirectAfterLogin', window.location.href);
        window.location.href = 'login.html';
        return;
    }

    // User is logged in - migrate any localStorage data if needed
    await HenryData.migrateFromLocalStorage();

    // Add user info to header if there's a nav element
    const user = await HenryAuth.getUser();
    if (user) {
        // Look for header nav to add user menu
        const headerNav = document.querySelector('.header-nav');
        if (headerNav) {
            // Check if sign out link already exists
            if (!headerNav.querySelector('.sign-out-link')) {
                const signOutLink = document.createElement('a');
                signOutLink.href = '#';
                signOutLink.className = 'nav-link sign-out-link';
                signOutLink.textContent = 'Sign Out';
                signOutLink.onclick = async (e) => {
                    e.preventDefault();
                    await HenryAuth.signOut();
                };
                headerNav.appendChild(signOutLink);
            }
        }
    }

    // Dispatch event so pages know auth is ready
    window.dispatchEvent(new CustomEvent('henryAuthReady', { detail: { session, user } }));
})();
