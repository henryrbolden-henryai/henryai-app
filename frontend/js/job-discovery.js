/**
 * Job Discovery Module
 * Fetches and displays personalized job recommendations on the dashboard.
 *
 * Network matching consolidation:
 * - LinkedIn connections: Reads from henryhq_linkedin_connections (set by outreach.html)
 * - Prior employers: Reads from parsedResume experience[].company (set by resume upload)
 * - NO duplicate upload flows -- points users to Network & Outreach page for CSV upload
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // Cache key for localStorage
    const CACHE_KEY = 'jobDiscoveryCache';
    const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours in ms

    // Key used by outreach.html for LinkedIn connections
    const LINKEDIN_CONNECTIONS_KEY = 'henryhq_linkedin_connections';

    /**
     * JobDiscovery Class
     * Manages job fetching, caching, and rendering on the dashboard
     */
    class JobDiscovery {
        constructor() {
            this.container = document.getElementById('jobDiscoverySection');
            this.jobsList = document.getElementById('jobDiscoveryList');
            this.searchInfo = document.getElementById('jobSearchInfo');
            this.networkCompanies = [];  // Companies from LinkedIn + resume
            this.priorEmployers = [];    // Companies from resume experience
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
            let resumeData = this.getResumeData();

            // If no resume in localStorage, fetch the default resume from Supabase
            if (!resumeData) {
                resumeData = await this.fetchDefaultResume();
            }

            // Build network context from existing data sources
            this.buildNetworkContext(resumeData);

            // Determine search parameters from profile
            const searchParams = this.buildSearchFromProfile(profile, resumeData);

            // If authenticated, the backend will enrich from Supabase profile.
            // Only show "needs profile" if there's no user_id AND no local role data.
            const userId = await this.getUserId();
            if (!searchParams.role_title && !userId) {
                this.renderNeedsProfile();
                return;
            }

            // Check local cache first
            const cached = this.getCachedResults(searchParams);
            if (cached) {
                // Re-apply network matching (connections may have been uploaded since cache)
                const flaggedJobs = this.applyNetworkFlags(cached.jobs);
                this.renderJobs(flaggedJobs, cached.search_query, true);
                this.container.style.display = 'block';
                return;
            }

            // Fetch from API
            this.renderLoading();
            this.container.style.display = 'block';
            await this.fetchJobs(searchParams);
        }

        /**
         * Fetch the user's default resume from the API (Supabase user_resumes table).
         * This covers the case where the resume was uploaded on the profile page
         * but isn't in localStorage on the dashboard.
         */
        async fetchDefaultResume() {
            try {
                const userId = await this.getUserId();
                if (!userId) return null;

                const response = await fetch(`${API_BASE}/api/resumes?user_id=${encodeURIComponent(userId)}`);
                if (!response.ok) return null;

                const data = await response.json();
                if (!data.resumes || data.resumes.length === 0) return null;

                // Find default resume, or fall back to the first one
                const defaultResume = data.resumes.find(r => r.is_default) || data.resumes[0];
                const resumeJson = defaultResume.resume_json;
                if (!resumeJson) return null;

                // Cache it in localStorage so subsequent visits don't need the fetch
                try {
                    localStorage.setItem('primaryResume', JSON.stringify(defaultResume));
                } catch (e) {
                    // Storage full or unavailable - not critical
                }

                return resumeJson;
            } catch (e) {
                console.warn('[JobDiscovery] Could not fetch default resume from API:', e);
                return null;
            }
        }

        /**
         * Build network context by consolidating data from:
         * 1. LinkedIn connections CSV (uploaded via Network & Outreach page)
         * 2. Prior employers from parsed resume
         */
        buildNetworkContext(resumeData) {
            const companySet = new Map(); // company_lower -> { company, source, count }

            // Source 1: LinkedIn connections (from outreach.html upload)
            const linkedInData = this.getLinkedInConnections();
            if (linkedInData?.connections) {
                for (const conn of linkedInData.connections) {
                    const company = (conn.company || '').trim();
                    if (!company) continue;
                    const key = company.toLowerCase();
                    if (companySet.has(key)) {
                        const existing = companySet.get(key);
                        existing.count++;
                        existing.source = 'linkedin';
                    } else {
                        companySet.set(key, {
                            company: company,
                            source: 'linkedin',
                            count: 1,
                        });
                    }
                }
            }

            // Source 2: Prior employers from resume
            if (resumeData?.experience) {
                for (const exp of resumeData.experience) {
                    const company = (exp.company || '').trim();
                    if (!company) continue;
                    const key = company.toLowerCase();
                    this.priorEmployers.push(company);
                    if (!companySet.has(key)) {
                        companySet.set(key, {
                            company: company,
                            source: 'resume',
                            count: 0, // Not a "connection" -- it's a prior employer
                        });
                    }
                }
            }

            this.networkCompanies = Array.from(companySet.values());
            console.log(`[JobDiscovery] Network context: ${this.networkCompanies.length} companies (${linkedInData?.connectionCount || 0} LinkedIn connections, ${this.priorEmployers.length} prior employers)`);
        }

        /**
         * Get LinkedIn connections from outreach.html's localStorage
         * Format: { version, uploadedAt, connectionCount, connections: [{company, ...}] }
         */
        getLinkedInConnections() {
            try {
                const stored = localStorage.getItem(LINKEDIN_CONNECTIONS_KEY);
                if (!stored) return null;
                const data = JSON.parse(stored);
                if (data.version !== 1) return null;
                return data;
            } catch (e) {
                return null;
            }
        }

        /**
         * Apply network flags to job results (client-side matching)
         * This runs after API response so we can match against LinkedIn + resume data
         */
        applyNetworkFlags(jobs) {
            if (!this.networkCompanies.length) return jobs;

            const flagged = jobs.map(job => {
                const jobCompany = (job.company || '').toLowerCase().trim();
                let matched = null;

                for (const net of this.networkCompanies) {
                    const netCompany = net.company.toLowerCase().trim();
                    // Fuzzy match: exact, contains, or contained-by
                    if (netCompany === jobCompany ||
                        netCompany.includes(jobCompany) ||
                        jobCompany.includes(netCompany)) {
                        matched = net;
                        break;
                    }
                }

                if (matched) {
                    return {
                        ...job,
                        network_connection: true,
                        network_connection_count: matched.count,
                        network_source: matched.source, // 'linkedin' or 'resume'
                    };
                }
                return job;
            });

            // Sort: network connections first (LinkedIn > resume), then by recency
            flagged.sort((a, b) => {
                const aNet = a.network_connection ? (a.network_source === 'linkedin' ? 2 : 1) : 0;
                const bNet = b.network_connection ? (b.network_source === 'linkedin' ? 2 : 1) : 0;
                if (aNet !== bNet) return bNet - aNet;
                return (a.days_since_posted || 999) - (b.days_since_posted || 999);
            });

            return flagged;
        }

        /**
         * Get the current user's ID from HenryAuth (if available)
         */
        async getUserId() {
            try {
                if (typeof HenryAuth === 'undefined') return null;
                const user = await HenryAuth.getUser();
                return user?.id || null;
            } catch (e) {
                return null;
            }
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
                // Send user_id so backend fetches profile/resume/network from Supabase.
                // Only include frontend overrides if Supabase lookup won't be available.
                const userId = await this.getUserId();
                const requestBody = {};
                if (userId) {
                    requestBody.user_id = userId;
                } else {
                    // No authenticated user — fall back to frontend-derived params
                    Object.assign(requestBody, searchParams);
                }

                const response = await fetch(`${API_BASE}/api/jobs/discover`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody),
                });

                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }

                const data = await response.json();

                if (data.error) {
                    // Hide developer-facing config errors; show user-friendly message
                    if (data.error.includes('not configured') || data.error.includes('environment variable')) {
                        console.warn('[JobDiscovery] Service not configured:', data.error);
                        this.container.style.display = 'none';
                    } else {
                        this.renderError('Job recommendations are temporarily unavailable. Please try again later.');
                    }
                    return;
                }

                // Apply network flags client-side (LinkedIn + resume companies)
                data.jobs = this.applyNetworkFlags(data.jobs || []);

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
                const daysAgo = this.formatPostedDate(job);

                // Build badges based on network source
                let networkBadge = '';
                if (job.network_connection) {
                    if (job.network_source === 'linkedin') {
                        const countText = job.network_connection_count > 0
                            ? `${job.network_connection_count} connection${job.network_connection_count !== 1 ? 's' : ''}`
                            : 'Connections';
                        networkBadge = `<span class="job-network-badge" title="You have ${countText} at this company">${countText}</span>`;
                    } else if (job.network_source === 'resume') {
                        networkBadge = `<span class="job-former-employer-badge" title="You previously worked at this company">Former Employer</span>`;
                    }
                }

                const remoteBadge = job.is_remote
                    ? '<span class="job-remote-badge">Remote</span>'
                    : '';

                html += `
                    <div class="job-card ${job.network_connection ? (job.network_source === 'linkedin' ? 'job-card-network' : 'job-card-former') : ''}">
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
                                ${job.publisher ? `<span class="job-source">via ${this.escapeHtml(job.publisher)}</span>` : ''}
                            </div>
                        </div>
                        <div class="job-card-actions">
                            <a href="${this.escapeHtml(job.apply_url)}" target="_blank" rel="noopener noreferrer" class="job-btn-apply">View Job Description</a>
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
            let resumeData = this.getResumeData();

            // If no resume in localStorage, fetch from Supabase
            if (!resumeData) {
                resumeData = await this.fetchDefaultResume();
            }

            // Rebuild network context (user may have uploaded connections since last load)
            this.buildNetworkContext(resumeData);

            const searchParams = this.buildSearchFromProfile(profile, resumeData);

            if (searchParams.role_title) {
                this.renderLoading();
                await this.fetchJobs(searchParams);
            }
        }

        /**
         * Format the posted date for display.
         * Uses "Xd ago" for recent posts, actual date for older ones.
         */
        formatPostedDate(job) {
            // If we have the actual posted_date string, calculate from that
            if (job.posted_date) {
                try {
                    const posted = new Date(job.posted_date);
                    const now = new Date();
                    const diffMs = now - posted;
                    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

                    if (diffDays <= 0) return 'Today';
                    if (diffDays === 1) return '1d ago';
                    if (diffDays <= 14) return `${diffDays}d ago`;
                    // Older than 2 weeks: show the actual date
                    return posted.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                } catch (e) {
                    // Fall through to days_since_posted
                }
            }

            if (job.days_since_posted != null) {
                if (job.days_since_posted <= 0) return 'Today';
                if (job.days_since_posted <= 14) return `${job.days_since_posted}d ago`;
                return `${job.days_since_posted}d ago`;
            }

            return 'Recent';
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
