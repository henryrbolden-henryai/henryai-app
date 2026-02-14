/**
 * Job Discovery Module
 * Fetches and displays personalized job recommendations on the dashboard.
 * Integrates with candidate profile data and LinkedIn network for matching.
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // Cache key for localStorage
    const CACHE_KEY = 'jobDiscoveryCache';
    const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours in ms

    /**
     * JobDiscovery Class
     * Manages job fetching, caching, and rendering on the dashboard
     */
    class JobDiscovery {
        constructor() {
            this.container = document.getElementById('jobDiscoverySection');
            this.jobsList = document.getElementById('jobDiscoveryList');
            this.searchInfo = document.getElementById('jobSearchInfo');
            if (this.container) {
                this.init();
            }
        }

        /**
         * Initialize job discovery
         */
        async init() {
            // Get profile data for search
            const profile = this.getUserProfile();
            const resumeData = this.getResumeData();

            // Determine search parameters from profile
            const searchParams = this.buildSearchFromProfile(profile, resumeData);

            if (!searchParams.role_title) {
                this.renderNeedsProfile();
                return;
            }

            // Check local cache first
            const cached = this.getCachedResults(searchParams);
            if (cached) {
                this.renderJobs(cached.jobs, cached.search_query, true);
                this.container.style.display = 'block';
                return;
            }

            // Fetch from API
            this.renderLoading();
            this.container.style.display = 'block';
            await this.fetchJobs(searchParams);
        }

        /**
         * Build search parameters from user profile and resume data
         */
        buildSearchFromProfile(profile, resumeData) {
            const params = {
                role_title: null,
                location: null,
                keywords: null,
                remote_only: false,
            };

            // Priority 1: target_roles from resume
            if (resumeData?.target_roles?.length > 0) {
                params.role_title = resumeData.target_roles[0];
            }
            // Priority 2: current_title from resume (with level context)
            else if (resumeData?.current_title) {
                params.role_title = resumeData.current_title;
            }
            // Priority 3: function_area from profile (generic fallback)
            else if (profile?.function_area) {
                const functionMap = {
                    'product_management': 'Product Manager',
                    'engineering': 'Software Engineer',
                    'design': 'UX Designer',
                    'data_analytics': 'Data Analyst',
                    'sales': 'Sales Manager',
                    'marketing': 'Marketing Manager',
                    'customer_success': 'Customer Success Manager',
                    'operations': 'Operations Manager',
                    'finance': 'Finance Manager',
                    'hr_people': 'HR Manager',
                    'legal': 'Legal Counsel',
                };
                params.role_title = functionMap[profile.function_area] || profile.function_area;
            }

            // Location from profile
            if (profile?.city && profile?.state) {
                params.location = `${profile.city}, ${profile.state}`;
            } else if (profile?.city) {
                params.location = profile.city;
            } else if (profile?.state) {
                params.location = profile.state;
            }

            // Remote preference
            if (profile?.work_arrangement) {
                const arrangements = Array.isArray(profile.work_arrangement)
                    ? profile.work_arrangement
                    : [];
                params.remote_only = arrangements.length === 1 && arrangements[0] === 'remote';
            }

            // Additional keywords from profile
            if (profile?.job_search_keywords?.length > 0) {
                params.keywords = profile.job_search_keywords;
            }

            return params;
        }

        /**
         * Fetch jobs from the API
         */
        async fetchJobs(searchParams) {
            try {
                const response = await fetch(`${API_BASE}/api/jobs/discover`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(searchParams),
                });

                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }

                const data = await response.json();

                if (data.error) {
                    this.renderError(data.error);
                    return;
                }

                // Cache results locally
                this.setCachedResults(searchParams, data);

                // Render
                this.renderJobs(data.jobs, data.search_query, data.cached);

            } catch (error) {
                console.error('[JobDiscovery] Fetch error:', error);
                this.renderError('Unable to load job recommendations right now. Please try again later.');
            }
        }

        /**
         * Get cached results from localStorage
         */
        getCachedResults(searchParams) {
            try {
                const stored = localStorage.getItem(CACHE_KEY);
                if (!stored) return null;

                const cache = JSON.parse(stored);
                const cacheKey = this.getCacheKey(searchParams);

                if (cache.key !== cacheKey) return null;
                if (Date.now() - cache.timestamp > CACHE_TTL) {
                    localStorage.removeItem(CACHE_KEY);
                    return null;
                }

                return cache.data;
            } catch (e) {
                return null;
            }
        }

        /**
         * Store results in localStorage cache
         */
        setCachedResults(searchParams, data) {
            try {
                localStorage.setItem(CACHE_KEY, JSON.stringify({
                    key: this.getCacheKey(searchParams),
                    timestamp: Date.now(),
                    data: data,
                }));
            } catch (e) {
                console.warn('[JobDiscovery] Cache write failed:', e);
            }
        }

        getCacheKey(params) {
            return `${params.role_title || ''}_${params.location || ''}_${params.remote_only}`;
        }

        /**
         * Render job listings
         */
        renderJobs(jobs, searchQuery, isCached) {
            if (!this.jobsList) return;

            if (!jobs || jobs.length === 0) {
                this.renderEmpty(searchQuery);
                return;
            }

            // Update search info
            if (this.searchInfo) {
                const cacheNote = isCached ? ' (cached)' : '';
                this.searchInfo.textContent = `Showing results for "${searchQuery}"${cacheNote}`;
            }

            let html = '';
            jobs.forEach(job => {
                const salary = this.formatSalary(job);
                const daysAgo = job.days_since_posted != null
                    ? `${job.days_since_posted}d ago`
                    : 'Recent';
                const networkBadge = job.network_connection
                    ? `<span class="job-network-badge" title="You have ${job.network_connection_count || ''} connection${job.network_connection_count !== 1 ? 's' : ''} at this company">In Your Network</span>`
                    : '';
                const remoteBadge = job.is_remote
                    ? '<span class="job-remote-badge">Remote</span>'
                    : '';

                html += `
                    <div class="job-card ${job.network_connection ? 'job-card-network' : ''}">
                        <div class="job-card-main">
                            <div class="job-card-header">
                                <div class="job-card-title-row">
                                    <h4 class="job-title">${this.escapeHtml(job.title)}</h4>
                                    ${networkBadge}
                                    ${remoteBadge}
                                </div>
                                <div class="job-company">${this.escapeHtml(job.company)}</div>
                            </div>
                            <div class="job-card-meta">
                                <span class="job-location">${this.escapeHtml(job.location)}</span>
                                ${salary ? `<span class="job-salary">${salary}</span>` : ''}
                                <span class="job-posted">${daysAgo}</span>
                            </div>
                        </div>
                        <div class="job-card-actions">
                            <a href="${this.escapeHtml(job.apply_url)}" target="_blank" rel="noopener noreferrer" class="job-btn-apply">Apply</a>
                            <button class="job-btn-analyze" data-job-title="${this.escapeHtml(job.title)}" data-job-company="${this.escapeHtml(job.company)}" onclick="window.jobDiscovery.analyzeRole(this)">Analyze</button>
                        </div>
                    </div>
                `;
            });

            this.jobsList.innerHTML = html;
        }

        /**
         * Render loading state
         */
        renderLoading() {
            if (!this.jobsList) return;
            this.jobsList.innerHTML = `
                <div class="job-discovery-loading">
                    <div class="job-loading-spinner"></div>
                    <p>Finding jobs that match your profile...</p>
                </div>
            `;
        }

        /**
         * Render empty state
         */
        renderEmpty(searchQuery) {
            if (!this.jobsList) return;
            this.jobsList.innerHTML = `
                <div class="job-discovery-empty">
                    <p>No new jobs found for "${this.escapeHtml(searchQuery)}" this week.</p>
                    <p class="job-empty-hint">Try broadening your search by updating your target role in your profile, or check LinkedIn Jobs directly.</p>
                </div>
            `;
        }

        /**
         * Render error state
         */
        renderError(message) {
            if (!this.jobsList) return;
            this.jobsList.innerHTML = `
                <div class="job-discovery-error">
                    <p>${this.escapeHtml(message)}</p>
                </div>
            `;
        }

        /**
         * Render state when profile data is insufficient
         */
        renderNeedsProfile() {
            if (!this.jobsList) return;
            this.container.style.display = 'block';
            this.jobsList.innerHTML = `
                <div class="job-discovery-needs-profile">
                    <p>Upload your resume to see personalized job recommendations.</p>
                    <p class="job-empty-hint">We use your target role, location, and work preferences to find matching jobs.</p>
                    <a href="/resume" class="job-btn-upload-resume">Upload Resume</a>
                </div>
            `;
        }

        /**
         * Handle "Analyze This Role" button click
         */
        analyzeRole(button) {
            const title = button.dataset.jobTitle;
            const company = button.dataset.jobCompany;
            // Navigate to the analysis page with prefilled data
            const params = new URLSearchParams({
                company: company,
                role: title,
                source: 'job_discovery',
            });
            window.location.href = `/analyze?${params.toString()}`;
        }

        /**
         * Force refresh jobs (bypass cache)
         */
        async refresh() {
            localStorage.removeItem(CACHE_KEY);
            const profile = this.getUserProfile();
            const resumeData = this.getResumeData();
            const searchParams = this.buildSearchFromProfile(profile, resumeData);

            if (searchParams.role_title) {
                this.renderLoading();
                await this.fetchJobs(searchParams);
            }
        }

        /**
         * Format salary range for display
         */
        formatSalary(job) {
            if (!job.salary_min && !job.salary_max) return null;

            const format = (val) => {
                if (!val) return null;
                if (val >= 1000) return `$${Math.round(val / 1000)}K`;
                return `$${val}`;
            };

            const min = format(job.salary_min);
            const max = format(job.salary_max);

            if (min && max) return `${min}-${max}`;
            if (min) return `${min}+`;
            if (max) return `Up to ${max}`;
            return null;
        }

        /**
         * Get user profile from localStorage
         */
        getUserProfile() {
            try {
                const stored = localStorage.getItem('userProfile');
                return stored ? JSON.parse(stored) : null;
            } catch (e) {
                return null;
            }
        }

        /**
         * Get parsed resume data from session/local storage
         */
        getResumeData() {
            try {
                // Try sessionStorage first (most recent parse)
                let data = sessionStorage.getItem('parsedResume');
                if (data) return JSON.parse(data);

                // Try localStorage
                data = localStorage.getItem('parsedResume');
                if (data) return JSON.parse(data);

                // Try getting from stored resumes
                data = localStorage.getItem('primaryResume');
                if (data) {
                    const resume = JSON.parse(data);
                    return resume.resume_json || resume;
                }

                return null;
            } catch (e) {
                return null;
            }
        }

        /**
         * Escape HTML to prevent XSS
         */
        escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.jobDiscovery = new JobDiscovery();
        });
    } else {
        window.jobDiscovery = new JobDiscovery();
    }

})();
