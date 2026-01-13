/**
 * Flow State Manager
 *
 * Manages session state across the Job Fit -> Resume Level -> Strategy flow.
 * Ensures data persists when users navigate back and forth.
 *
 * Storage keys managed:
 * - analysisData: Job fit analysis results
 * - levelingData: Resume leveling analysis results
 * - strengthenedData: Bullet strengthening results
 * - linkedinScoringResults: LinkedIn optimization results
 *
 * All data is stored in both sessionStorage (primary) and localStorage (Safari fallback).
 */

const FlowState = (function() {
    'use strict';

    // Keys we manage for the application flow
    const FLOW_KEYS = [
        'analysisData',
        'levelingData',
        'strengthenedData',
        'linkedinScoringResults',
        'linkedinData',
        'resumeData',
        'proceeded_despite_guidance'
    ];

    // Backup suffix for localStorage fallback
    const BACKUP_SUFFIX = '_backup';

    /**
     * Get data from storage with localStorage fallback (Safari compatibility)
     * @param {string} key - Storage key
     * @returns {any} Parsed data or null
     */
    function get(key) {
        try {
            let dataStr = sessionStorage.getItem(key);

            // Safari fallback: check localStorage if sessionStorage is empty
            if (!dataStr) {
                dataStr = localStorage.getItem(key + BACKUP_SUFFIX);
                if (dataStr) {
                    console.log(`[FlowState] Safari fallback: loaded ${key} from localStorage`);
                    sessionStorage.setItem(key, dataStr);
                }
            }

            if (!dataStr) return null;

            return JSON.parse(dataStr);
        } catch (e) {
            console.error(`[FlowState] Error reading ${key}:`, e);
            return null;
        }
    }

    /**
     * Save data to both sessionStorage and localStorage backup
     * @param {string} key - Storage key
     * @param {any} data - Data to store (will be JSON stringified)
     */
    function set(key, data) {
        try {
            const dataStr = JSON.stringify(data);
            sessionStorage.setItem(key, dataStr);
            localStorage.setItem(key + BACKUP_SUFFIX, dataStr);
            console.log(`[FlowState] Saved ${key}`);
        } catch (e) {
            console.error(`[FlowState] Error saving ${key}:`, e);
        }
    }

    /**
     * Remove data from both storages
     * @param {string} key - Storage key
     */
    function remove(key) {
        sessionStorage.removeItem(key);
        localStorage.removeItem(key + BACKUP_SUFFIX);
        console.log(`[FlowState] Removed ${key}`);
    }

    /**
     * Check if key exists in storage
     * @param {string} key - Storage key
     * @returns {boolean}
     */
    function has(key) {
        return sessionStorage.getItem(key) !== null ||
               localStorage.getItem(key + BACKUP_SUFFIX) !== null;
    }

    /**
     * Get the current application context (company/role being analyzed)
     * @returns {{company: string, role: string, fitScore: number} | null}
     */
    function getContext() {
        const analysis = get('analysisData');
        if (!analysis) return null;

        return {
            company: analysis._company_name || analysis._company || analysis.company_name || '',
            role: analysis.role_title || analysis._role || '',
            fitScore: analysis.fit_score,
            analysisId: analysis._analysis_id || null
        };
    }

    /**
     * Check if flow data is consistent (same job being analyzed)
     * Helps detect if user switched jobs mid-flow
     * @returns {boolean}
     */
    function isFlowConsistent() {
        const analysis = get('analysisData');
        const leveling = get('levelingData');

        if (!analysis) return false;
        if (!leveling) return true; // No leveling yet, still consistent

        // Check if leveling data matches analysis context
        const analysisRole = analysis.role_title || analysis._role || '';
        const levelingRole = leveling.target_role || leveling.target_title || '';

        // If both have roles, they should match
        if (analysisRole && levelingRole && analysisRole !== levelingRole) {
            console.warn('[FlowState] Flow inconsistency detected - roles don\'t match');
            return false;
        }

        return true;
    }

    /**
     * Clear all flow data (for starting fresh or on logout)
     */
    function clearAll() {
        FLOW_KEYS.forEach(key => remove(key));
        console.log('[FlowState] Cleared all flow data');
    }

    /**
     * Clear flow data but preserve analysis (for re-running from Job Fit)
     */
    function clearDownstreamData() {
        ['levelingData', 'strengthenedData'].forEach(key => remove(key));
        console.log('[FlowState] Cleared downstream flow data');
    }

    /**
     * Export all flow state for debugging
     * @returns {object}
     */
    function exportState() {
        const state = {};
        FLOW_KEYS.forEach(key => {
            const data = get(key);
            if (data) {
                state[key] = {
                    exists: true,
                    size: JSON.stringify(data).length,
                    preview: typeof data === 'object' ? Object.keys(data).slice(0, 5) : typeof data
                };
            } else {
                state[key] = { exists: false };
            }
        });
        return state;
    }

    /**
     * Ensure analysisData has localStorage backup (for pages that only use sessionStorage)
     */
    function ensureBackups() {
        FLOW_KEYS.forEach(key => {
            const sessionData = sessionStorage.getItem(key);
            const localData = localStorage.getItem(key + BACKUP_SUFFIX);

            // If sessionStorage has data but localStorage doesn't, create backup
            if (sessionData && !localData) {
                localStorage.setItem(key + BACKUP_SUFFIX, sessionData);
                console.log(`[FlowState] Created backup for ${key}`);
            }
            // If localStorage has data but sessionStorage doesn't (Safari case), restore
            else if (!sessionData && localData) {
                sessionStorage.setItem(key, localData);
                console.log(`[FlowState] Restored ${key} from backup`);
            }
        });
    }

    // Public API
    return {
        get,
        set,
        remove,
        has,
        getContext,
        isFlowConsistent,
        clearAll,
        clearDownstreamData,
        exportState,
        ensureBackups,
        FLOW_KEYS
    };
})();

// Auto-ensure backups when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FlowState.ensureBackups());
} else {
    FlowState.ensureBackups();
}

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlowState;
}
