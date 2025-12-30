/**
 * Tier Service for HenryHQ
 *
 * Frontend service for managing tier access, usage limits, and upgrade prompts.
 */

const TierService = {
    // API base URL
    API_BASE: window.API_BASE || 'https://henryai-production.up.railway.app',

    // Cache for user tier/usage data
    _cache: null,
    _cacheExpiry: null,
    _cacheDuration: 5 * 60 * 1000, // 5 minutes

    /**
     * Get current user's tier and usage information
     * @returns {Promise<Object>} User tier, features, and usage data
     */
    async getUserUsage() {
        // Check cache first
        if (this._cache && this._cacheExpiry && Date.now() < this._cacheExpiry) {
            return this._cache;
        }

        const user = await HenryAuth.getUser();
        if (!user) {
            throw new Error('User not authenticated');
        }

        try {
            const response = await fetch(`${this.API_BASE}/api/user/usage?user_id=${user.id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch user usage');
            }

            const data = await response.json();

            // Cache the result
            this._cache = data;
            this._cacheExpiry = Date.now() + this._cacheDuration;

            // Store in window for quick access
            window.userTier = data.tier;
            window.userFeatures = data.features;
            window.userUsage = data.usage;

            return data;
        } catch (error) {
            console.error('Error fetching user usage:', error);
            // Return default sourcer tier on error
            return {
                tier: 'sourcer',
                tier_display: 'Sourcer',
                tier_price: 0,
                is_beta_user: false,
                usage: {},
                features: {}
            };
        }
    },

    /**
     * Clear the usage cache (call after actions that change usage)
     */
    clearCache() {
        this._cache = null;
        this._cacheExpiry = null;
    },

    /**
     * Check if user can access a feature
     * @param {string} featureName - Name of the feature to check
     * @returns {Promise<boolean>} Whether user can access the feature
     */
    async canAccessFeature(featureName) {
        const usage = await this.getUserUsage();
        const featureValue = usage.features[featureName];
        return featureValue === true || featureValue === 'limited';
    },

    /**
     * Check if a feature is in limited mode
     * @param {string} featureName - Name of the feature to check
     * @returns {Promise<boolean>} Whether feature is limited
     */
    async isFeatureLimited(featureName) {
        const usage = await this.getUserUsage();
        return usage.features[featureName] === 'limited';
    },

    /**
     * Check if user has remaining usage for a type
     * @param {string} usageType - Type of usage (applications, resumes, etc.)
     * @returns {Promise<boolean>} Whether user has remaining usage
     */
    async hasUsageRemaining(usageType) {
        const usage = await this.getUserUsage();
        const usageData = usage.usage[usageType];
        if (!usageData) return false;
        return usageData.is_unlimited || usageData.remaining > 0;
    },

    /**
     * Get usage details for a type
     * @param {string} usageType - Type of usage
     * @returns {Promise<Object>} Usage details (used, limit, remaining)
     */
    async getUsageDetails(usageType) {
        const usage = await this.getUserUsage();
        return usage.usage[usageType] || null;
    },

    /**
     * Increment usage after a successful action
     * @param {string} usageType - Type of usage to increment
     */
    async incrementUsage(usageType) {
        const user = await HenryAuth.getUser();
        if (!user) return;

        try {
            await fetch(`${this.API_BASE}/api/user/usage/increment/${usageType}?user_id=${user.id}`, {
                method: 'POST'
            });
            // Clear cache so next fetch gets updated data
            this.clearCache();
        } catch (error) {
            console.error('Error incrementing usage:', error);
        }
    },

    /**
     * Show upgrade modal when a feature is locked or limit reached
     * @param {Object} options - Modal options
     */
    showUpgradeModal(options) {
        const { type, feature, usageType, used, limit, upgradeTo, message } = options;

        // Remove existing modal if any
        const existingModal = document.getElementById('upgrade-modal');
        if (existingModal) existingModal.remove();

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'upgrade-modal';
        modal.className = 'upgrade-modal-overlay';
        modal.innerHTML = `
            <div class="upgrade-modal">
                <button class="upgrade-modal-close" onclick="TierService.closeUpgradeModal()">&times;</button>
                <div class="upgrade-modal-icon">${type === 'limit_reached' ? '📊' : '🔒'}</div>
                <h3 class="upgrade-modal-title">
                    ${type === 'limit_reached' ? 'Monthly Limit Reached' : 'Feature Locked'}
                </h3>
                <p class="upgrade-modal-message">
                    ${message || (type === 'limit_reached'
                        ? `You've used ${used}/${limit} ${usageType.replace('_', ' ')} this month.`
                        : `Upgrade to ${this._getTierDisplay(upgradeTo)} to unlock ${feature.replace('_', ' ')}.`)}
                </p>
                ${type === 'limit_reached' ? `
                    <p class="upgrade-modal-reset">
                        Your limit resets on the first of next month.
                    </p>
                ` : ''}
                <div class="upgrade-modal-cta">
                    <a href="pricing.html" class="btn btn-primary upgrade-modal-btn">View Plans</a>
                    <button class="btn btn-secondary upgrade-modal-dismiss" onclick="TierService.closeUpgradeModal()">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add styles if not already present
        if (!document.getElementById('upgrade-modal-styles')) {
            const styles = document.createElement('style');
            styles.id = 'upgrade-modal-styles';
            styles.textContent = `
                .upgrade-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.85);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    animation: fadeIn 0.2s ease;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                .upgrade-modal {
                    background: #0a0a0a;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 16px;
                    padding: 40px;
                    max-width: 420px;
                    width: 90%;
                    text-align: center;
                    position: relative;
                    animation: slideUp 0.3s ease;
                }
                @keyframes slideUp {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .upgrade-modal-close {
                    position: absolute;
                    top: 16px;
                    right: 16px;
                    background: none;
                    border: none;
                    color: #a1a1aa;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 4px;
                    line-height: 1;
                }
                .upgrade-modal-close:hover {
                    color: #fff;
                }
                .upgrade-modal-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                }
                .upgrade-modal-title {
                    font-family: 'Instrument Serif', Georgia, serif;
                    font-size: 1.5rem;
                    font-weight: 400;
                    margin-bottom: 12px;
                    color: #fafafa;
                }
                .upgrade-modal-message {
                    color: #a1a1aa;
                    font-size: 0.95rem;
                    line-height: 1.6;
                    margin-bottom: 8px;
                }
                .upgrade-modal-reset {
                    color: #71717a;
                    font-size: 0.85rem;
                    margin-bottom: 24px;
                }
                .upgrade-modal-cta {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                .upgrade-modal-btn {
                    width: 100%;
                    padding: 14px 24px;
                    font-size: 1rem;
                }
                .upgrade-modal-dismiss {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: #a1a1aa;
                }
                .upgrade-modal-dismiss:hover {
                    background: rgba(255, 255, 255, 0.05);
                    border-color: rgba(255, 255, 255, 0.2);
                }
            `;
            document.head.appendChild(styles);
        }
    },

    /**
     * Close the upgrade modal
     */
    closeUpgradeModal() {
        const modal = document.getElementById('upgrade-modal');
        if (modal) {
            modal.remove();
        }
    },

    /**
     * Get display name for a tier
     * @param {string} tier - Tier ID
     * @returns {string} Display name
     */
    _getTierDisplay(tier) {
        const names = {
            'sourcer': 'Sourcer',
            'recruiter': 'Recruiter',
            'principal': 'Principal',
            'partner': 'Partner',
            'coach': 'Coach'
        };
        return names[tier] || tier;
    },

    /**
     * Handle API error responses for tier-related errors
     * @param {Response} response - Fetch response object
     * @returns {Promise<Object|null>} Parsed error or null if not tier-related
     */
    async handleTierError(response) {
        if (response.status === 403) {
            const error = await response.json();
            if (error.error === 'feature_locked') {
                this.showUpgradeModal({
                    type: 'feature_locked',
                    feature: error.feature,
                    upgradeTo: error.upgrade_to,
                    message: error.message
                });
                return error;
            }
        }

        if (response.status === 429) {
            const error = await response.json();
            if (error.error === 'limit_reached') {
                this.showUpgradeModal({
                    type: 'limit_reached',
                    usageType: error.usage_type,
                    used: error.used,
                    limit: error.limit,
                    message: error.message
                });
                return error;
            }
        }

        return null;
    },

    /**
     * Wrapper for fetch that handles tier errors
     * @param {string} url - URL to fetch
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>} Fetch response
     */
    async fetchWithTierCheck(url, options = {}) {
        const response = await fetch(url, options);

        if (!response.ok) {
            const tierError = await this.handleTierError(response.clone());
            if (tierError) {
                return null;
            }
        }

        return response;
    },

    /**
     * Display usage meter component
     * @param {string} containerId - ID of container element
     * @param {string} usageType - Type of usage to display
     */
    async renderUsageMeter(containerId, usageType) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const usageDetails = await this.getUsageDetails(usageType);
        if (!usageDetails) {
            container.innerHTML = '<span class="usage-unavailable">Usage data unavailable</span>';
            return;
        }

        const { used, limit, is_unlimited, remaining } = usageDetails;

        if (is_unlimited) {
            container.innerHTML = `
                <div class="usage-meter unlimited">
                    <span class="usage-label">${this._formatUsageType(usageType)}</span>
                    <span class="usage-value">Unlimited</span>
                </div>
            `;
        } else {
            const percentage = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
            const isLow = remaining <= Math.ceil(limit * 0.2);

            container.innerHTML = `
                <div class="usage-meter ${isLow ? 'low' : ''}">
                    <div class="usage-header">
                        <span class="usage-label">${this._formatUsageType(usageType)}</span>
                        <span class="usage-value">${used}/${limit}</span>
                    </div>
                    <div class="usage-bar">
                        <div class="usage-fill" style="width: ${percentage}%"></div>
                    </div>
                    ${isLow ? `<span class="usage-warning">${remaining} remaining</span>` : ''}
                </div>
            `;
        }
    },

    /**
     * Format usage type for display
     * @param {string} usageType - Usage type
     * @returns {string} Formatted string
     */
    _formatUsageType(usageType) {
        const formats = {
            'applications': 'Applications',
            'resumes': 'Resumes',
            'cover_letters': 'Cover Letters',
            'henry_conversations': 'Henry Conversations',
            'mock_interviews': 'Mock Interviews',
            'coaching_sessions': 'Coaching Sessions'
        };
        return formats[usageType] || usageType;
    }
};

// Make available globally
window.TierService = TierService;
