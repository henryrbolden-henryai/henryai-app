/**
 * LinkedIn Upload Module
 * Handles LinkedIn profile PDF uploads, parsing, and UI updates
 */

(function() {
    'use strict';

    // Configuration
    const API_BASE = window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // LinkedIn "in" logo SVG (official brand icon)
    const LINKEDIN_ICON_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0077B5">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>`;

    // Helper function to get LinkedIn icon HTML
    function getLinkedInIcon(large = false) {
        return `<span class="linkedin-icon ${large ? 'linkedin-icon-large' : ''}">${LINKEDIN_ICON_SVG}</span>`;
    }

    /**
     * LinkedInUpload Class
     * Main controller for LinkedIn profile upload functionality
     */
    class LinkedInUpload {
        constructor() {
            this.fileInput = null;
            this.uploadSource = null;
            this.init();
        }

        /**
         * Initialize the LinkedIn upload module
         */
        init() {
            this.createFileInput();
            this.setupEventListeners();
            this.checkAndShowReminder();
        }

        /**
         * Create hidden file input element
         */
        createFileInput() {
            // Remove existing if present
            const existing = document.getElementById('linkedin-file-input');
            if (existing) existing.remove();

            // Create new file input
            this.fileInput = document.createElement('input');
            this.fileInput.type = 'file';
            this.fileInput.id = 'linkedin-file-input';
            this.fileInput.accept = '.pdf';
            this.fileInput.style.display = 'none';
            document.body.appendChild(this.fileInput);

            // Listen for file selection
            this.fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.uploadFile(file);
                }
                // Reset input for same file re-selection
                this.fileInput.value = '';
            });
        }

        /**
         * Setup global event listeners
         */
        setupEventListeners() {
            // Handle clicks on any LinkedIn upload button
            document.addEventListener('click', (e) => {
                const target = e.target;

                // Upload buttons
                if (target.matches('[data-linkedin-upload]') ||
                    target.closest('[data-linkedin-upload]')) {
                    const btn = target.closest('[data-linkedin-upload]') || target;
                    this.openFileUpload(btn.dataset.linkedinUpload || 'unknown');
                }

                // Dismiss modal buttons
                if (target.matches('[data-linkedin-dismiss-modal]') ||
                    target.closest('[data-linkedin-dismiss-modal]')) {
                    this.dismissModal();
                }

                // Dismiss reminder banner
                if (target.matches('[data-linkedin-dismiss-reminder]') ||
                    target.closest('[data-linkedin-dismiss-reminder]')) {
                    this.dismissReminder();
                }

                // Skip for now buttons
                if (target.matches('[data-linkedin-skip]') ||
                    target.closest('[data-linkedin-skip]')) {
                    const source = target.dataset.linkedinSkip ||
                                 target.closest('[data-linkedin-skip]')?.dataset.linkedinSkip || 'unknown';
                    this.skipForNow(source);
                }

                // Replace profile buttons
                if (target.matches('[data-linkedin-replace]') ||
                    target.closest('[data-linkedin-replace]')) {
                    this.openFileUpload('replace');
                }

                // Delete profile buttons
                if (target.matches('[data-linkedin-delete]') ||
                    target.closest('[data-linkedin-delete]')) {
                    this.confirmDelete();
                }

                // Copy to clipboard buttons
                if (target.matches('[data-linkedin-copy]') ||
                    target.closest('[data-linkedin-copy]')) {
                    const btn = target.closest('[data-linkedin-copy]') || target;
                    this.copyToClipboard(btn);
                }
            });

            // Close modal on overlay click
            document.addEventListener('click', (e) => {
                if (e.target.matches('.linkedin-modal-overlay')) {
                    this.dismissModal();
                }
            });

            // Close modal on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.dismissModal();
                }
            });
        }

        /**
         * Check if user should see dashboard modal or reminder
         */
        checkAndShowReminder() {
            const profile = this.getUserProfile();

            // If LinkedIn already uploaded, don't show anything
            if (profile?.linkedin_profile_uploaded) {
                return;
            }

            // Check if modal was dismissed this session
            const modalDismissed = sessionStorage.getItem('linkedin_modal_dismissed');

            // Show modal or reminder based on context
            if (this.isOnDashboard() && !modalDismissed) {
                // On dashboard, show modal if not dismissed
                this.showDashboardModal();
            } else if (!modalDismissed) {
                // On other pages, show reminder banner if available
                this.showReminderBanner();
            }
        }

        /**
         * Check if current page is dashboard
         */
        isOnDashboard() {
            return window.location.pathname.includes('dashboard.html') ||
                   window.location.pathname.endsWith('/');
        }

        /**
         * Show dashboard modal for new feature announcement
         */
        showDashboardModal() {
            // Check if modal container exists
            const container = document.getElementById('linkedin-modal-container');
            if (!container) return;

            // Create modal HTML
            const modalHTML = `
                <div class="linkedin-modal-overlay show" id="linkedinModal">
                    <div class="linkedin-modal">
                        <h2>New Feature: LinkedIn Profile Optimization</h2>

                        <p>Get found by recruiters and avoid credibility issues during interviews by optimizing your LinkedIn profile.</p>

                        <div class="linkedin-why-matters">
                            <h3>Why this matters:</h3>
                            <ul>
                                <li>Recruiters use LinkedIn Recruiter to source 70% of senior candidates</li>
                                <li>Hiring managers check your LinkedIn during interviews to validate your experience</li>
                                <li>Misalignment between your resume and LinkedIn profile kills credibility</li>
                            </ul>
                        </div>

                        <div class="linkedin-how-to">
                            <p>${getLinkedInIcon()} <strong>How to get your LinkedIn PDF:</strong></p>
                            <span class="linkedin-path">${getLinkedInIcon()} LinkedIn.com → Your Profile → More → Save to PDF</span>
                        </div>

                        <div class="linkedin-modal-actions">
                            <button class="btn-primary" data-linkedin-upload="modal">Upload LinkedIn Profile PDF</button>
                            <button class="btn-secondary" data-linkedin-dismiss-modal>I'll Do This Later</button>
                        </div>
                    </div>
                </div>
            `;

            container.innerHTML = modalHTML;
        }

        /**
         * Show reminder banner on dashboard
         */
        showReminderBanner() {
            const container = document.getElementById('linkedin-reminder-container');
            if (!container) return;

            const bannerHTML = `
                <div class="linkedin-reminder-banner" id="linkedinReminder">
                    <span class="banner-icon">💼</span>
                    <span class="banner-message">Upload your LinkedIn profile to unlock full job analysis and alignment checks</span>
                    <button class="btn-link" data-linkedin-upload="reminder">Upload Now</button>
                    <button class="btn-dismiss" data-linkedin-dismiss-reminder>×</button>
                </div>
            `;

            container.innerHTML = bannerHTML;
        }

        /**
         * Dismiss modal and mark as dismissed for session
         */
        dismissModal() {
            const modal = document.getElementById('linkedinModal');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
            }
            sessionStorage.setItem('linkedin_modal_dismissed', 'true');
        }

        /**
         * Dismiss reminder banner
         */
        dismissReminder() {
            const reminder = document.getElementById('linkedinReminder');
            if (reminder) {
                reminder.style.opacity = '0';
                reminder.style.transform = 'translateY(-10px)';
                setTimeout(() => reminder.remove(), 300);
            }
        }

        /**
         * Open file upload dialog
         * @param {string} source - Where the upload was initiated from
         */
        openFileUpload(source) {
            this.uploadSource = source;
            sessionStorage.setItem('linkedin_upload_source', source);
            this.fileInput.click();
        }

        /**
         * Handle file upload
         * @param {File} file - The selected file
         */
        async uploadFile(file) {
            // Validate file type
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                this.showToast('error', 'Please upload a PDF file. LinkedIn profiles can be downloaded as PDFs from LinkedIn.com.');
                return;
            }

            // Validate file size (10MB max)
            const maxSize = 10 * 1024 * 1024; // 10MB
            if (file.size > maxSize) {
                this.showToast('error', 'File size exceeds 10MB limit. LinkedIn PDFs are typically 1-3MB.');
                return;
            }

            // Show loading state
            this.showLoadingState();

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch(`${API_BASE}/api/linkedin/upload`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Upload failed');
                }

                const data = await response.json();

                // Handle success
                this.handleUploadSuccess(data);

            } catch (error) {
                console.error('LinkedIn upload error:', error);
                this.handleUploadError(error);
            } finally {
                this.hideLoadingState();
            }
        }

        /**
         * Handle successful upload
         * @param {Object} data - Response data from server
         */
        handleUploadSuccess(data) {
            // Update local profile
            this.updateLocalProfile(data.parsed_data);

            // Dismiss any open modals
            this.dismissModal();

            // Hide reminder if visible
            this.dismissReminder();

            // Show success toast
            this.showToast('success', 'LinkedIn profile uploaded successfully! Running alignment analysis...');

            // Track analytics
            this.trackEvent('linkedin_uploaded', { source: this.uploadSource });

            // Refresh page after brief delay to show updated state
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }

        /**
         * Handle upload error
         * @param {Error} error - The error object
         */
        handleUploadError(error) {
            let errorMessage = 'Failed to upload LinkedIn profile. Please try again.';

            if (error.message.includes('parse')) {
                errorMessage = "We couldn't parse your LinkedIn PDF. Try downloading it again from LinkedIn.";
            } else if (error.message.includes('size')) {
                errorMessage = "File size too large. Maximum is 10MB.";
            } else if (error.message.includes('PDF') || error.message.includes('pdf')) {
                errorMessage = "Please upload a valid PDF file from LinkedIn.";
            }

            this.showToast('error', errorMessage);
        }

        /**
         * Update local profile with LinkedIn data
         * @param {Object} linkedinData - Parsed LinkedIn data
         */
        updateLocalProfile(linkedinData) {
            // Get existing profile
            let profile = this.getUserProfile() || {};

            // Update LinkedIn fields
            profile.linkedin_profile_uploaded = true;
            profile.linkedin_last_updated = new Date().toISOString();
            profile.linkedin_parsed = linkedinData;

            // Save to localStorage
            localStorage.setItem('userProfile', JSON.stringify(profile));

            // Save to Supabase if available
            if (typeof HenryData !== 'undefined') {
                HenryData.saveCandidateProfile(profile).catch(err => {
                    console.error('Error saving LinkedIn data to Supabase:', err);
                });
            }
        }

        /**
         * Handle skip for now action
         * @param {string} source - Where skip was clicked
         */
        skipForNow(source) {
            this.trackEvent('linkedin_upload_skipped', { source });
            this.dismissModal();

            // Show a subtle reminder
            if (source === 'job-analysis') {
                this.showToast('info', 'Reminder: Recruiters will check your LinkedIn. Upload anytime from your Profile page.');
            }
        }

        /**
         * Confirm and delete LinkedIn profile
         */
        async confirmDelete() {
            if (!confirm('Are you sure you want to delete your LinkedIn profile? This will remove all optimization data.')) {
                return;
            }

            this.showLoadingState('Deleting...');

            try {
                const response = await fetch(`${API_BASE}/api/linkedin/profile`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    throw new Error('Delete failed');
                }

                // Update local profile
                let profile = this.getUserProfile() || {};
                profile.linkedin_profile_uploaded = false;
                profile.linkedin_last_updated = null;
                profile.linkedin_parsed = null;
                localStorage.setItem('userProfile', JSON.stringify(profile));

                // Update Supabase if available
                if (typeof HenryData !== 'undefined') {
                    await HenryData.saveCandidateProfile(profile);
                }

                this.showToast('success', 'LinkedIn profile deleted');

                setTimeout(() => {
                    window.location.reload();
                }, 1500);

            } catch (error) {
                console.error('Delete error:', error);
                this.showToast('error', 'Failed to delete LinkedIn profile');
            } finally {
                this.hideLoadingState();
            }
        }

        /**
         * Copy field content to clipboard
         * @param {HTMLElement} button - The copy button clicked
         */
        copyToClipboard(button) {
            const fieldId = button.dataset.linkedinCopy;
            const textarea = document.getElementById(fieldId) ||
                           button.previousElementSibling;

            if (!textarea) return;

            // Select and copy
            textarea.select();
            textarea.setSelectionRange(0, 99999); // For mobile
            document.execCommand('copy');

            // Visual feedback
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.classList.add('copied');

            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('copied');
            }, 2000);
        }

        /**
         * Show loading overlay
         * @param {string} message - Loading message
         */
        showLoadingState(message = 'Uploading and analyzing your LinkedIn profile...') {
            // Remove existing loader if any
            this.hideLoadingState();

            const loader = document.createElement('div');
            loader.id = 'linkedin-upload-loader';
            loader.className = 'linkedin-loader-overlay';
            loader.innerHTML = `
                <div class="linkedin-loader-content">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
            document.body.appendChild(loader);
        }

        /**
         * Hide loading overlay
         */
        hideLoadingState() {
            const loader = document.getElementById('linkedin-upload-loader');
            if (loader) loader.remove();
        }

        /**
         * Show toast notification
         * @param {string} type - 'success', 'error', or 'info'
         * @param {string} message - Toast message
         */
        showToast(type, message) {
            // Remove existing toasts
            document.querySelectorAll('.linkedin-toast').forEach(t => t.remove());

            const toast = document.createElement('div');
            toast.className = `linkedin-toast toast-${type}`;
            toast.innerHTML = `<span class="toast-message">${message}</span>`;
            document.body.appendChild(toast);

            // Trigger animation
            setTimeout(() => toast.classList.add('show'), 10);

            // Auto-hide after 5 seconds
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }

        /**
         * Get current user profile
         * @returns {Object|null} User profile data
         */
        getUserProfile() {
            try {
                const stored = localStorage.getItem('userProfile');
                return stored ? JSON.parse(stored) : null;
            } catch (e) {
                console.error('Error reading user profile:', e);
                return null;
            }
        }

        /**
         * Track analytics event
         * @param {string} event - Event name
         * @param {Object} data - Event data
         */
        trackEvent(event, data = {}) {
            console.log('LinkedIn event:', event, data);
            // Add your analytics tracking here
            // e.g., gtag('event', event, data);
        }

        /**
         * Check alignment between resume and LinkedIn
         * @param {string} jobId - Optional job ID for context
         * @returns {Promise<Object>} Alignment check results
         */
        async checkAlignment(jobId = null) {
            const profile = this.getUserProfile();

            if (!profile?.linkedin_profile_uploaded) {
                return { uploaded: false };
            }

            try {
                let url = `${API_BASE}/api/linkedin/check-alignment`;
                if (jobId) {
                    url += `?job_id=${jobId}`;
                }

                const response = await fetch(url, {
                    method: 'POST'
                });

                if (!response.ok) {
                    throw new Error('Alignment check failed');
                }

                return await response.json();

            } catch (error) {
                console.error('Alignment check error:', error);
                return { error: true, message: error.message };
            }
        }

        /**
         * Get optimized LinkedIn sections for a job
         * @param {string} jobId - The job ID
         * @returns {Promise<Object>} Optimized LinkedIn sections
         */
        async getOptimizedSections(jobId) {
            const profile = this.getUserProfile();

            if (!profile?.linkedin_profile_uploaded) {
                return { uploaded: false };
            }

            try {
                const response = await fetch(`${API_BASE}/api/linkedin/optimize?job_id=${jobId}`, {
                    method: 'POST'
                });

                if (!response.ok) {
                    throw new Error('Optimization failed');
                }

                return await response.json();

            } catch (error) {
                console.error('LinkedIn optimization error:', error);
                return { error: true, message: error.message };
            }
        }

        /**
         * Render LinkedIn profile section for profile edit page
         * @param {string} containerId - ID of container element
         */
        renderProfileSection(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const profile = this.getUserProfile();
            const isUploaded = profile?.linkedin_profile_uploaded;

            if (isUploaded) {
                this.renderUploadedState(container, profile);
            } else {
                this.renderNotUploadedState(container);
            }
        }

        /**
         * Render uploaded state for profile section
         */
        renderUploadedState(container, profile) {
            const lastUpdated = profile.linkedin_last_updated
                ? new Date(profile.linkedin_last_updated).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })
                : 'Unknown';

            container.innerHTML = `
                <div class="linkedin-uploaded-state">
                    <span class="linkedin-status-badge success">Uploaded</span>
                    <p class="timestamp">Last updated: ${lastUpdated}</p>

                    <div class="actions">
                        <button class="btn-action" data-linkedin-replace>Replace LinkedIn Profile PDF</button>
                        <button class="btn-action danger" data-linkedin-delete>Delete</button>
                    </div>

                    <p class="note">We recommend updating your LinkedIn profile every 90 days to stay visible to recruiters.</p>
                </div>
            `;
        }

        /**
         * Render not uploaded state for profile section
         */
        renderNotUploadedState(container) {
            container.innerHTML = `
                <div class="linkedin-not-uploaded-state">
                    <span class="linkedin-status-badge warning">Not Uploaded</span>

                    <div class="benefits">
                        <strong>Why upload your LinkedIn profile?</strong>
                        <ul>
                            <li>Get alignment checks for every job application</li>
                            <li>Optimize your profile for recruiter discoverability</li>
                            <li>Ensure credibility during interviews</li>
                        </ul>
                    </div>

                    <div class="linkedin-how-to">
                        <p>${getLinkedInIcon()} <strong>How to get your LinkedIn PDF:</strong></p>
                        <span class="linkedin-path">${getLinkedInIcon()} LinkedIn.com → Your Profile → More → Save to PDF</span>
                    </div>

                    <button class="btn-primary" data-linkedin-upload="profile-page">Upload LinkedIn Profile PDF</button>
                </div>
            `;
        }

        /**
         * Render LinkedIn alignment section for job analysis
         * @param {string} containerId - ID of container element
         * @param {Object} alignmentData - Alignment check results (optional)
         */
        async renderAlignmentSection(containerId, alignmentData = null) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const profile = this.getUserProfile();
            const isUploaded = profile?.linkedin_profile_uploaded;

            if (!isUploaded) {
                this.renderUploadPrompt(container);
            } else if (alignmentData) {
                this.renderAlignmentResults(container, alignmentData);
            } else {
                // Show loading state while fetching alignment
                container.innerHTML = '<div class="linkedin-loading"><div class="spinner"></div><p>Checking LinkedIn alignment...</p></div>';

                try {
                    // Get job context from session storage
                    const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
                    const jobId = analysisData._job_id;

                    // Fetch alignment check from API
                    const results = await this.checkAlignment(jobId);

                    if (results && !results.error) {
                        this.renderAlignmentResults(container, results);
                    } else {
                        // Fallback: show basic status
                        this.renderAlignmentFallback(container, profile);
                    }
                } catch (error) {
                    console.error('Error checking LinkedIn alignment:', error);
                    // Fallback: show basic status
                    this.renderAlignmentFallback(container, profile);
                }
            }
        }

        /**
         * Render fallback alignment status when API fails
         */
        renderAlignmentFallback(container, profile) {
            const lastUpdated = profile.linkedin_last_updated
                ? new Date(profile.linkedin_last_updated).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })
                : 'Unknown';

            container.innerHTML = `
                <div class="linkedin-alert-info">
                    <h3>💼 LinkedIn Profile Uploaded</h3>
                    <p>Your LinkedIn profile was uploaded on ${lastUpdated}.</p>
                    <p style="margin-top: 12px; color: var(--color-text-secondary); font-size: 0.9rem;">
                        Tip: Make sure your LinkedIn headline and summary reflect the role you're applying for.
                        Visit your <a href="documents.html" style="color: var(--color-accent);">Tailored Documents</a> to see optimized LinkedIn sections.
                    </p>
                </div>
            `;
        }

        /**
         * Render upload prompt for job analysis
         */
        renderUploadPrompt(container) {
            container.innerHTML = `
                <div class="linkedin-alert-warning">
                    <h3>LinkedIn Profile Not Uploaded</h3>

                    <p>Before you apply to this role, let's make sure your LinkedIn doesn't contradict your tailored resume.</p>

                    <div class="why-matters-job">
                        <strong>Why this matters for this application:</strong>
                        <ul>
                            <li>The recruiter will click your LinkedIn profile link when screening your application</li>
                            <li>The hiring manager will check your LinkedIn during the interview to validate your experience</li>
                            <li>Any discrepancies between your resume and LinkedIn will raise red flags</li>
                        </ul>
                    </div>

                    <div class="what-you-get">
                        <strong>Upload your LinkedIn profile to:</strong>
                        <ul>
                            <li>Check for discrepancies with your tailored resume (titles, dates, responsibilities)</li>
                            <li>Get optimized sections to copy-paste (headline, summary, skills)</li>
                            <li>Ensure you're discoverable in recruiter searches for roles like this</li>
                        </ul>
                    </div>

                    <div class="linkedin-how-to">
                        <p>${getLinkedInIcon()} <strong>How to get your LinkedIn PDF:</strong></p>
                        <span class="linkedin-path">${getLinkedInIcon()} LinkedIn.com → Your Profile → More → Save to PDF</span>
                    </div>

                    <div class="actions">
                        <button class="btn-primary" data-linkedin-upload="job-analysis">Upload LinkedIn Profile PDF</button>
                        <button class="btn-secondary" data-linkedin-skip="job-analysis">Skip for Now</button>
                    </div>

                    <p class="note">You can upload your LinkedIn profile anytime from your Profile page.</p>
                </div>
            `;
        }

        /**
         * Render alignment check results
         */
        renderAlignmentResults(container, results) {
            if (results.aligned) {
                container.innerHTML = `
                    <div class="linkedin-alert-success">
                        <h3>Your LinkedIn Aligns with Your Resume</h3>
                        <p>No discrepancies found. Your LinkedIn profile backs up your tailored resume for this role.</p>
                    </div>
                `;
            } else {
                const discrepanciesHTML = results.discrepancies.map(d => `
                    <li class="severity-${d.severity}">
                        <div class="discrepancy-type">${d.type.replace(/_/g, ' ').toUpperCase()}</div>
                        <div class="discrepancy-message">${d.message}</div>
                        ${d.resume_value || d.linkedin_value ? `
                            <div class="discrepancy-values">
                                ${d.resume_value ? `<span>Resume: "${d.resume_value}"</span>` : ''}
                                ${d.linkedin_value ? `<span>LinkedIn: "${d.linkedin_value}"</span>` : ''}
                            </div>
                        ` : ''}
                    </li>
                `).join('');

                container.innerHTML = `
                    <div class="linkedin-alert-warning">
                        <h3>${results.discrepancy_count} Alignment Issue${results.discrepancy_count > 1 ? 's' : ''} Found</h3>
                        <p>Fix these before applying—recruiters will notice these discrepancies:</p>

                        <ul class="linkedin-discrepancies-list">
                            ${discrepanciesHTML}
                        </ul>

                        <div class="actions">
                            <button class="btn-primary" onclick="document.getElementById('tailored-documents').scrollIntoView({ behavior: 'smooth' })">See Optimized LinkedIn Sections</button>
                            <button class="btn-secondary" data-linkedin-dismiss-warning>I'll Fix Manually</button>
                        </div>
                    </div>
                `;
            }
        }

        /**
         * Render optimized LinkedIn sections for documents area
         * @param {string} containerId - ID of container element
         * @param {Object} optimizedData - Optimized sections data
         */
        renderOptimizedSections(containerId, optimizedData) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const profile = this.getUserProfile();

            if (!profile?.linkedin_profile_uploaded) {
                this.renderDocumentsUploadPrompt(container);
                return;
            }

            if (!optimizedData) {
                container.innerHTML = '<div class="loading">Generating optimized LinkedIn sections...</div>';
                return;
            }

            // Get parsed LinkedIn data for section analysis
            const linkedinParsed = profile.linkedin_parsed || {};

            container.innerHTML = `
                <style>
                    .linkedin-sections-grid {
                        display: grid;
                        grid-template-columns: 1fr;
                        gap: 24px;
                    }
                    .linkedin-section-card {
                        background: rgba(255,255,255,0.03);
                        border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 12px;
                        padding: 20px;
                    }
                    .linkedin-section-card h4 {
                        color: #22d3ee;
                        font-size: 1rem;
                        margin-bottom: 4px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }
                    .linkedin-section-card .section-priority {
                        font-size: 0.7rem;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-weight: 600;
                        text-transform: uppercase;
                    }
                    .priority-critical { background: #dc2626; color: white; }
                    .priority-high { background: #f59e0b; color: black; }
                    .priority-medium { background: #3b82f6; color: white; }
                    .priority-low { background: rgba(255,255,255,0.1); color: #9ca3af; }
                    .linkedin-section-card .help-text {
                        color: #9ca3af;
                        font-size: 0.85rem;
                        margin-bottom: 12px;
                    }
                    .copyable-field {
                        position: relative;
                    }
                    .copyable-field textarea {
                        width: 100%;
                        background: rgba(0,0,0,0.3);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 8px;
                        padding: 12px;
                        color: #e0e0e0;
                        font-size: 0.95rem;
                        resize: vertical;
                        min-height: 60px;
                    }
                    .copyable-field .btn-copy {
                        position: absolute;
                        top: 8px;
                        right: 8px;
                        background: rgba(255,255,255,0.1);
                        border: none;
                        color: #9ca3af;
                        padding: 4px 12px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 0.8rem;
                    }
                    .copyable-field .btn-copy:hover {
                        background: rgba(255,255,255,0.2);
                        color: white;
                    }
                    .skills-list {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 8px;
                        list-style: none;
                        padding: 0;
                    }
                    .skills-list li {
                        background: rgba(34, 211, 238, 0.15);
                        border: 1px solid rgba(34, 211, 238, 0.3);
                        padding: 6px 14px;
                        border-radius: 20px;
                        font-size: 0.9rem;
                        color: #22d3ee;
                    }
                    .bullets-list {
                        list-style: none;
                        padding: 0;
                    }
                    .bullets-list li {
                        padding: 8px 0 8px 20px;
                        position: relative;
                        color: #e0e0e0;
                        font-size: 0.95rem;
                        border-bottom: 1px solid rgba(255,255,255,0.05);
                    }
                    .bullets-list li:before {
                        content: "•";
                        color: #22d3ee;
                        position: absolute;
                        left: 0;
                    }
                    .bullets-list li:last-child {
                        border-bottom: none;
                    }
                    .section-status {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        font-size: 0.8rem;
                        margin-top: 8px;
                    }
                    .status-good { color: #4ade80; }
                    .status-needs-work { color: #fbbf24; }
                    .status-missing { color: #f87171; }
                    .section-group-title {
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.1em;
                        color: #6b7280;
                        margin: 24px 0 12px 0;
                        padding-bottom: 8px;
                        border-bottom: 1px solid rgba(255,255,255,0.05);
                    }
                    .section-group-title:first-child {
                        margin-top: 0;
                    }
                    .linkedin-update-confirmation {
                        margin-top: 24px;
                        padding: 16px;
                        background: rgba(255,255,255,0.03);
                        border-radius: 8px;
                    }
                    .linkedin-update-confirmation label {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        cursor: pointer;
                        color: #9ca3af;
                    }
                    .linkedin-update-confirmation input[type="checkbox"] {
                        width: 18px;
                        height: 18px;
                    }
                </style>

                ${optimizedData.has_issues ? `
                    <div class="linkedin-warning-badge" style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; color: #fbbf24;">
                        ⚠️ Your LinkedIn has inconsistencies with your resume. Update these sections before applying.
                    </div>
                ` : ''}

                <div class="linkedin-sections-grid">
                    <!-- FIRST IMPRESSION SECTIONS (Critical) -->
                    <div class="section-group-title">First Impression (Recruiters see this first)</div>

                    <!-- Headline -->
                    <div class="linkedin-section-card">
                        <h4>
                            Headline
                            <span class="section-priority priority-critical">Critical</span>
                        </h4>
                        <p class="help-text">Your headline shows in search results and is the first thing recruiters scan. Make it count.</p>
                        <div class="copyable-field">
                            <textarea readonly id="linkedin-headline" rows="2">${optimizedData.headline || ''}</textarea>
                            <button class="btn-copy" data-linkedin-copy="linkedin-headline">Copy</button>
                        </div>
                        ${this.getSectionStatus(linkedinParsed.headline, optimizedData.headline)}
                    </div>

                    <!-- About Section -->
                    <div class="linkedin-section-card">
                        <h4>
                            About Section
                            <span class="section-priority priority-critical">Critical</span>
                        </h4>
                        <p class="help-text">Your story: what you do, how you create value, and where you're headed. First 3 lines show before "see more".</p>
                        <div class="copyable-field">
                            <textarea readonly id="linkedin-summary" rows="6">${optimizedData.summary || ''}</textarea>
                            <button class="btn-copy" data-linkedin-copy="linkedin-summary">Copy</button>
                        </div>
                        ${this.getSectionStatus(linkedinParsed.summary, optimizedData.summary)}
                    </div>

                    <!-- CREDIBILITY SECTIONS (High Priority) -->
                    <div class="section-group-title">Credibility Signals</div>

                    <!-- Experience -->
                    ${optimizedData.experience_highlights?.length ? `
                        <div class="linkedin-section-card">
                            <h4>
                                Experience Bullets
                                <span class="section-priority priority-high">High</span>
                            </h4>
                            <p class="help-text">Add these to your current role. Impact-first language that matches your resume.</p>
                            <ul class="bullets-list">
                                ${optimizedData.experience_highlights.map(bullet => `<li>${bullet}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    <!-- Skills -->
                    ${optimizedData.top_skills?.length ? `
                        <div class="linkedin-section-card">
                            <h4>
                                Skills to Feature
                                <span class="section-priority priority-high">High</span>
                            </h4>
                            <p class="help-text">Recruiters search by skills. Pin these to the top of your skills section.</p>
                            <ul class="skills-list">
                                ${optimizedData.top_skills.map(skill => `<li>${skill}</li>`).join('')}
                            </ul>
                            <div class="section-status status-needs-work" style="margin-top: 12px;">
                                💡 Reorder your skills so these appear first
                            </div>
                        </div>
                    ` : ''}

                    <!-- OPTIONAL POWER-UPS -->
                    <div class="section-group-title">Optional Power-Ups</div>

                    <!-- Featured Section -->
                    <div class="linkedin-section-card">
                        <h4>
                            Featured Section
                            <span class="section-priority priority-medium">Medium</span>
                        </h4>
                        <p class="help-text">Proof of work: case studies, press mentions, presentations, or portfolio pieces.</p>
                        ${linkedinParsed.featured?.length ? `
                            <div class="section-status status-good">✓ You have ${linkedinParsed.featured.length} featured item${linkedinParsed.featured.length > 1 ? 's' : ''}</div>
                        ` : `
                            <div class="section-status status-needs-work">
                                💡 Add 1-3 items that showcase your best work for this type of role
                            </div>
                        `}
                    </div>

                    <!-- Recommendations -->
                    <div class="linkedin-section-card">
                        <h4>
                            Recommendations
                            <span class="section-priority priority-medium">Medium</span>
                        </h4>
                        <p class="help-text">Social proof from managers or colleagues. 2-3 strong ones beat 10 generic ones.</p>
                        ${linkedinParsed.recommendations_count > 0 ? `
                            <div class="section-status status-good">✓ You have ${linkedinParsed.recommendations_count} recommendation${linkedinParsed.recommendations_count > 1 ? 's' : ''}</div>
                        ` : `
                            <div class="section-status status-needs-work">
                                💡 Request 2-3 recommendations from people who can speak to your impact
                            </div>
                        `}
                    </div>

                    <!-- Activity -->
                    <div class="linkedin-section-card">
                        <h4>
                            Activity
                            <span class="section-priority priority-low">Low</span>
                        </h4>
                        <p class="help-text">Recent engagement shows you're active. Even commenting counts.</p>
                        ${linkedinParsed.recent_activity ? `
                            <div class="section-status status-good">✓ Recent activity detected</div>
                        ` : `
                            <div class="section-status status-needs-work">
                                💡 Like or comment on 2-3 industry posts this week
                            </div>
                        `}
                    </div>
                </div>

                <!-- Update Confirmation -->
                <div class="linkedin-update-confirmation">
                    <label>
                        <input type="checkbox" id="linkedin-updated-checkbox">
                        I've updated my LinkedIn profile
                    </label>
                </div>

                <p class="timestamp" style="margin-top: 12px; color: #6b7280; font-size: 0.85rem;">
                    Last optimized: ${optimizedData.generated_at ? new Date(optimizedData.generated_at).toLocaleDateString() : 'Just now'}
                </p>
            `;

            // Add checkbox handler
            const checkbox = container.querySelector('#linkedin-updated-checkbox');
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        this.markLinkedInAsUpdated();
                    }
                });
            }
        }

        /**
         * Get status indicator for a LinkedIn section
         */
        getSectionStatus(currentValue, optimizedValue) {
            if (!currentValue && optimizedValue) {
                return '<div class="section-status status-missing">⚠️ Missing - add this section</div>';
            }
            if (currentValue && optimizedValue && currentValue !== optimizedValue) {
                return '<div class="section-status status-needs-work">💡 Update recommended</div>';
            }
            if (currentValue) {
                return '<div class="section-status status-good">✓ Has content</div>';
            }
            return '';
        }

        /**
         * Render upload prompt for documents section
         */
        renderDocumentsUploadPrompt(container) {
            container.innerHTML = `
                <div class="linkedin-alert-warning">
                    <p><strong>Upload your LinkedIn to see optimized sections</strong></p>

                    <p>Without your LinkedIn profile, we can't:</p>
                    <ul style="list-style: none; padding: 0; margin: 12px 0;">
                        <li style="padding: 4px 0; color: var(--color-text-secondary);">• Check alignment with your tailored resume</li>
                        <li style="padding: 4px 0; color: var(--color-text-secondary);">• Optimize your headline and summary for this role</li>
                        <li style="padding: 4px 0; color: var(--color-text-secondary);">• Ensure you're discoverable in recruiter searches</li>
                    </ul>

                    <div class="actions">
                        <button class="btn-primary" data-linkedin-upload="documents-section">Upload LinkedIn Profile PDF</button>
                        <button class="btn-secondary" data-linkedin-skip="documents-section">I'll Update LinkedIn Manually</button>
                    </div>
                </div>
            `;
        }

        /**
         * Mark LinkedIn as updated (user confirmed they made changes)
         */
        markLinkedInAsUpdated() {
            this.trackEvent('linkedin_updated', {
                job_id: sessionStorage.getItem('current_job_id') || 'unknown'
            });
            this.showToast('success', 'LinkedIn marked as updated. You\'re ready to apply!');
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.linkedInUpload = new LinkedInUpload();
        });
    } else {
        window.linkedInUpload = new LinkedInUpload();
    }

})();
