/**
 * Command Center Intelligence Module
 * Handles all backend API calls for tracker intelligence
 * Version: 2.0
 */

const CommandCenter = {
    // API base URL - adjust for production
    API_BASE: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://henry-job-search-engine-production.up.railway.app',

    // Cache for intelligence data
    cache: {
        intelligence: null,
        lastFetch: null,
        cacheDuration: 5 * 60 * 1000 // 5 minutes
    },

    /**
     * Fetch tracker intelligence for all applications
     * @param {string} userId - The user's ID
     * @param {Array} applications - Array of application objects
     * @returns {Promise<Object>} Intelligence response
     */
    async fetchIntelligence(userId, applications) {
        // Check cache first
        if (this.cache.intelligence &&
            this.cache.lastFetch &&
            (Date.now() - this.cache.lastFetch) < this.cache.cacheDuration) {
            console.log('[CommandCenter] Returning cached intelligence');
            return this.cache.intelligence;
        }

        // Transform applications for the API
        const transformedApps = applications.map(app => ({
            id: String(app.id),
            status: app.status || 'applied',
            company: app.company || '',
            role: app.role || app.roleTitle || '',
            date_applied: app.dateApplied || app.date_applied || null,
            decision_confidence: app.decision_confidence || null,
            jd_source: app.jd_source || (app.jobDescription ? 'user_provided' : 'missing'),
            fit_score: app.fitScore || app.fit_score || null,
            last_activity_date: app.lastActivityDate || app.last_activity_date || app.dateApplied || null,
            days_since_last_activity: app.days_since_last_activity || null,
            interview_count: app.interviews?.length || 0,
            substatus: app.substatus || null,
            manual_lock: app.manual_lock || false,
            user_override: app.user_override || false,
            user_override_reason: app.user_override_reason || null
        }));

        try {
            console.log('[CommandCenter] Fetching intelligence for', transformedApps.length, 'applications');
            const response = await fetch(`${this.API_BASE}/api/tracker/intelligence`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    applications: transformedApps
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            // Update cache
            this.cache.intelligence = data;
            this.cache.lastFetch = Date.now();

            console.log('[CommandCenter] Intelligence received:', {
                priorityActions: data.priority_actions?.length || 0,
                pipelineHealth: data.pipeline_health?.status,
                applications: data.applications?.length || 0
            });

            return data;
        } catch (error) {
            console.error('[CommandCenter] Error fetching intelligence:', error);
            // Return fallback data structure
            return this.getFallbackIntelligence(applications);
        }
    },

    /**
     * Generate provisional profile when JD is missing
     * @param {string} roleTitle - Role title
     * @param {string} companyName - Company name
     * @param {string} [industry] - Optional industry
     * @param {string} [seniority] - Optional seniority level
     * @returns {Promise<Object>} Provisional profile response
     */
    async reconstructJD(roleTitle, companyName, industry = null, seniority = null) {
        try {
            console.log('[CommandCenter] Reconstructing JD for:', roleTitle, 'at', companyName);
            const response = await fetch(`${this.API_BASE}/api/jd/reconstruct`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    role_title: roleTitle,
                    company_name: companyName,
                    industry: industry,
                    seniority: seniority
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('[CommandCenter] Error reconstructing JD:', error);
            return null;
        }
    },

    /**
     * Calculate decision confidence for a single application
     * @param {Object} params - Confidence calculation parameters
     * @returns {Promise<Object>} Confidence response
     */
    async calculateConfidence(params) {
        try {
            const response = await fetch(`${this.API_BASE}/api/tracker/calculate-confidence`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    application_id: params.applicationId,
                    fit_score: params.fitScore || 50,
                    jd_source: params.jdSource || 'missing',
                    days_since_applied: params.daysSinceApplied || 0,
                    status: params.status || 'applied',
                    interview_count: params.interviewCount || 0,
                    response_time_days: params.responseTimeDays || null,
                    days_since_last_activity: params.daysSinceLastActivity || null
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('[CommandCenter] Error calculating confidence:', error);
            return {
                decision_confidence: 50,
                label: 'medium',
                factors: { alignment_score: 50, momentum_score: 50, jd_confidence: 50 },
                guidance: 'Unable to calculate. Check connection.'
            };
        }
    },

    /**
     * Get fallback intelligence when API is unavailable
     * @param {Array} applications - Application data
     * @returns {Object} Fallback intelligence structure
     */
    getFallbackIntelligence(applications) {
        const activeApps = applications.filter(a =>
            !['rejected', 'withdrawn', 'archived'].includes(a.status?.toLowerCase())
        );

        // Calculate interview rate locally for proper pipeline health detection
        const interviewStatuses = ['recruiter screen', 'hiring manager', 'technical round',
            'panel interview', 'final round', 'executive interview', 'recruiter screen scheduled',
            'awaiting screen result', 'awaiting decision'];
        const interviews = activeApps.filter(a => {
            const s = (a.status || '').toLowerCase();
            return s.includes('interview') || s.includes('screen') || s.includes('recruiter');
        }).length;
        const interviewRate = activeApps.length > 0 ? (interviews / activeApps.length) * 100 : 0;

        // Determine status — match backend logic from tracker_helpers.py
        let status, color, icon, tone, recommendation, reason;
        if (activeApps.length < 3) {
            status = 'thin'; color = 'yellow'; icon = '📉'; tone = 'urgent';
            recommendation = 'Apply to 3 new roles now';
            reason = "Pipeline's too thin. You need momentum.";
        } else if (interviewRate < 5 && activeApps.length >= 5) {
            status = 'stalled'; color = 'red'; icon = '🚨'; tone = 'urgent';
            recommendation = 'Stop applying. Fix your positioning.';
            reason = "Something's broken. Diagnose before continuing.";
        } else if (activeApps.length > 10) {
            status = 'overloaded'; color = 'yellow'; icon = '📈'; tone = 'caution';
            recommendation = 'Pause applications. Focus on interviews only.';
            reason = "You're spreading thin. Convert what you have.";
        } else {
            status = 'healthy'; color = 'green'; icon = '✅'; tone = 'steady';
            recommendation = 'None—maintain pace, focus on interviews';
            reason = 'Good volume. Shift energy to conversion.';
        }

        return {
            priority_actions: [],
            pipeline_health: {
                active_count: activeApps.length,
                status: status,
                color: color,
                icon: icon,
                tone: tone,
                recommendation: recommendation,
                reason: reason + ' Running in offline mode.',
                priority_count: 0
            },
            focus_mode: {
                enabled: false,
                top_actions: [],
                dim_others: false
            },
            applications: applications.map(app => ({
                id: String(app.id),
                next_action: 'Review application',
                next_action_reason: 'Intelligence unavailable',
                priority_level: 'medium',
                one_click_action: null,
                ui_signals: {
                    priority: 'medium',
                    confidence: 'medium',
                    urgency: 'routine',
                    color_code: 'yellow',
                    icon: '📋',
                    badge: null,
                    action_available: false,
                    dimmed: false
                },
                decision_confidence: 50,
                days_since_last_activity: 0,
                substatus: 'unknown'
            }))
        };
    },

    /**
     * Invalidate the intelligence cache
     */
    invalidateCache() {
        this.cache.intelligence = null;
        this.cache.lastFetch = null;
        console.log('[CommandCenter] Cache invalidated');
    },

    /**
     * Get UI color class based on confidence level
     * @param {string} confidence - high, medium, low
     * @returns {string} CSS class name
     */
    getConfidenceColorClass(confidence) {
        const map = {
            'high': 'confidence-high',
            'medium': 'confidence-medium',
            'low': 'confidence-low'
        };
        return map[confidence] || 'confidence-medium';
    },

    /**
     * Get UI color class based on priority level
     * @param {string} priority - high, medium, low, archive
     * @returns {string} CSS class name
     */
    getPriorityColorClass(priority) {
        const map = {
            'high': 'priority-high',
            'medium': 'priority-medium',
            'low': 'priority-low',
            'archive': 'priority-archive'
        };
        return map[priority] || 'priority-medium';
    },

    /**
     * Get border color for application card based on confidence
     * @param {string} confidence - high, medium, low
     * @returns {string} CSS color value
     */
    getConfidenceBorderColor(confidence) {
        const colors = {
            'high': '#10b981',    // green
            'medium': '#f59e0b',  // yellow
            'low': '#ef4444'      // red
        };
        return colors[confidence] || colors.medium;
    },

    /**
     * Get one-click action button config
     * @param {Object} oneClickAction - Action object from API
     * @returns {Object} Button configuration
     */
    getOneClickButtonConfig(oneClickAction) {
        if (!oneClickAction) return null;

        const configs = {
            'draft_email': {
                label: 'Draft Email',
                icon: '✉️',
                class: 'btn-primary'
            },
            'archive': {
                label: 'Archive',
                icon: '📦',
                class: 'btn-secondary',
                confirm: true
            },
            'open_prep': {
                label: 'Review Prep',
                icon: '📋',
                class: 'btn-primary'
            },
            'block_time': {
                label: 'Block Time',
                icon: '📅',
                class: 'btn-secondary'
            }
        };

        return configs[oneClickAction.type] || {
            label: 'Take Action',
            icon: '⚡',
            class: 'btn-primary'
        };
    },

    /**
     * Check if strategic stop should be triggered
     * @param {Object} pipelineHealth - Pipeline health data
     * @param {number} interviewRate - Interview conversion rate
     * @returns {Object|null} Strategic stop config or null
     */
    checkStrategicStop(pipelineHealth, interviewRate) {
        // Trigger if: 10+ applications with <5% interview rate
        if (pipelineHealth.active_count >= 10 && interviewRate < 5) {
            return {
                triggered: true,
                reason: `You've applied to ${pipelineHealth.active_count} roles with <5% interview rate. Something's broken.`,
                actions: [
                    'Review resume positioning',
                    'Analyze rejection patterns',
                    'Get second-pass analysis'
                ],
                pauseDays: 7
            };
        }

        // Trigger if stalled status
        if (pipelineHealth.status === 'stalled') {
            return {
                triggered: true,
                reason: pipelineHealth.reason,
                actions: [
                    pipelineHealth.recommendation
                ],
                pauseDays: 0
            };
        }

        return null;
    }
};

// Export for use in tracker.html
window.CommandCenter = CommandCenter;
