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
                // Hide immediately via both class and style
                modal.classList.remove('show');
                modal.style.display = 'none';
                modal.style.opacity = '0';
                modal.style.visibility = 'hidden';

                // Restore body scroll
                document.body.style.overflow = '';

                // Remove from DOM after animation
                setTimeout(() => {
                    if (modal.parentNode) {
                        modal.remove();
                    }
                }, 300);
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

            // Just hide the modal - no toast, no navigation
            // User stays on results page with Apply/Pass buttons visible
            this.dismissModal();

            // Mark in sessionStorage that LinkedIn was skipped (for analytics)
            try {
                sessionStorage.setItem('linkedinSkipped', 'true');
                sessionStorage.setItem('linkedinSkippedAt', new Date().toISOString());
            } catch (e) {
                console.warn('Could not save LinkedIn skip state:', e);
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

            // Determine severity class
            const severityClass = this.getSeverityClass(optimizedData.severity);
            const severityLabel = optimizedData.severity || 'MEDIUM';

            container.innerHTML = `
                <style>
                    .linkedin-makeover { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
                    .severity-banner { padding: 16px 20px; border-radius: 12px; margin-bottom: 24px; }
                    .severity-banner.critical { background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(220, 38, 38, 0.4); }
                    .severity-banner.high { background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); }
                    .severity-banner.medium { background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.4); }
                    .severity-banner.low { background: rgba(74, 222, 128, 0.15); border: 1px solid rgba(74, 222, 128, 0.4); }
                    .severity-badge { display: inline-block; font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
                    .severity-badge.critical { background: #dc2626; color: white; }
                    .severity-badge.high { background: #f59e0b; color: black; }
                    .severity-badge.medium { background: #3b82f6; color: white; }
                    .severity-badge.low { background: #4ade80; color: black; }
                    .severity-message { color: #e0e0e0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 12px; }
                    .benefits-list { list-style: none; padding: 0; margin: 0; }
                    .benefits-list li { color: #9ca3af; font-size: 0.85rem; padding: 3px 0; }
                    .benefits-list li:before { content: "✓ "; color: #4ade80; }
                    .linkedin-sections-grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
                    .linkedin-section-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; }
                    .linkedin-section-card h4 { color: #22d3ee; font-size: 1rem; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
                    .section-priority { font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
                    .priority-critical { background: #dc2626; color: white; }
                    .priority-high { background: #f59e0b; color: black; }
                    .priority-medium { background: #3b82f6; color: white; }
                    .priority-low { background: rgba(255,255,255,0.1); color: #9ca3af; }
                    .help-text { color: #9ca3af; font-size: 0.85rem; margin-bottom: 12px; }
                    .current-vs-optimized { margin-bottom: 16px; }
                    .current-label, .optimized-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; display: block; }
                    .current-label { color: #6b7280; }
                    .optimized-label { color: #22d3ee; }
                    .current-content { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; color: #6b7280; font-size: 0.9rem; margin-bottom: 12px; font-style: italic; }
                    .copyable-field { position: relative; }
                    .copyable-field textarea { width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(34, 211, 238, 0.3); border-radius: 8px; padding: 12px; padding-right: 70px; color: #e0e0e0; font-size: 0.95rem; resize: vertical; min-height: 60px; font-family: inherit; line-height: 1.5; }
                    .copyable-field .btn-copy { position: absolute; top: 8px; right: 8px; background: rgba(34, 211, 238, 0.2); border: 1px solid rgba(34, 211, 238, 0.4); color: #22d3ee; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-weight: 500; transition: all 0.2s; }
                    .copyable-field .btn-copy:hover { background: rgba(34, 211, 238, 0.3); }
                    .why-this-works { margin-top: 12px; padding: 12px; background: rgba(74, 222, 128, 0.05); border-radius: 8px; border: 1px solid rgba(74, 222, 128, 0.1); }
                    .why-this-works-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #4ade80; margin-bottom: 8px; }
                    .why-list { list-style: none; padding: 0; margin: 0; }
                    .why-list li { color: #9ca3af; font-size: 0.85rem; padding: 3px 0; }
                    .why-list li:before { content: "✓ "; color: #4ade80; }
                    .update-reason { margin-top: 10px; padding: 10px 12px; background: rgba(245, 158, 11, 0.1); border-radius: 6px; border-left: 3px solid #f59e0b; font-size: 0.85rem; color: #fbbf24; }
                    .skills-section { display: grid; gap: 16px; }
                    .skills-group { margin-bottom: 12px; }
                    .skills-group-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; display: block; }
                    .skills-group-label.top { color: #22d3ee; }
                    .skills-group-label.add { color: #4ade80; }
                    .skills-group-label.remove { color: #f87171; }
                    .skills-list { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 0; }
                    .skills-list li { padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; }
                    .skills-list.top li { background: rgba(34, 211, 238, 0.15); border: 1px solid rgba(34, 211, 238, 0.3); color: #22d3ee; }
                    .skills-list.add li { background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.2); color: #4ade80; }
                    .skills-list.remove li { background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.2); color: #f87171; text-decoration: line-through; }
                    .experience-role { border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 16px; margin-bottom: 16px; background: rgba(0,0,0,0.2); }
                    .experience-role:last-child { margin-bottom: 0; }
                    .role-header { margin-bottom: 12px; }
                    .role-title { color: #e0e0e0; font-weight: 600; font-size: 1rem; }
                    .role-company { color: #9ca3af; font-size: 0.9rem; }
                    .role-context { color: #6b7280; font-size: 0.8rem; font-style: italic; margin-bottom: 12px; padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px; }
                    .bullets-list { list-style: none; padding: 0; margin: 0; }
                    .bullets-list li { padding: 8px 0 8px 20px; position: relative; color: #e0e0e0; font-size: 0.9rem; border-bottom: 1px solid rgba(255,255,255,0.03); line-height: 1.5; }
                    .bullets-list li:before { content: "•"; color: #22d3ee; position: absolute; left: 0; font-weight: bold; }
                    .bullets-list li:last-child { border-bottom: none; }
                    .optional-section-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 16px; }
                    .optional-section-card h5 { color: #9ca3af; font-size: 0.9rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
                    .optional-tip { color: #6b7280; font-size: 0.85rem; line-height: 1.5; }
                    .who-to-ask-list { list-style: none; padding: 0; margin: 8px 0 0 0; }
                    .who-to-ask-list li { padding: 6px 0; font-size: 0.85rem; color: #9ca3af; }
                    .who-to-ask-list li strong { color: #e0e0e0; }
                    .section-group-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #6b7280; margin: 28px 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
                    .section-group-title:first-child { margin-top: 0; }
                    .linkedin-update-confirmation { margin-top: 24px; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 8px; }
                    .linkedin-update-confirmation label { display: flex; align-items: center; gap: 10px; cursor: pointer; color: #9ca3af; }
                    .linkedin-update-confirmation input[type="checkbox"] { width: 18px; height: 18px; accent-color: #22d3ee; }
                </style>

                <div class="linkedin-makeover">
                    <!-- Severity Banner -->
                    ${optimizedData.summary_message ? `
                        <div class="severity-banner ${severityClass}">
                            <span class="severity-badge ${severityClass}">${severityLabel} UPDATES REQUIRED</span>
                            <p class="severity-message">${optimizedData.summary_message}</p>
                            ${optimizedData.benefits?.length ? `
                                <ul class="benefits-list">
                                    ${optimizedData.benefits.map(b => `<li>${b}</li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                    ` : ''}

                    <div class="linkedin-sections-grid">
                        <!-- FIRST IMPRESSION SECTIONS -->
                        <div class="section-group-title">First Impression (Recruiters see this first)</div>

                        <!-- Headline -->
                        <div class="linkedin-section-card">
                            <h4>Headline <span class="section-priority priority-critical">Critical</span></h4>
                            <p class="help-text">Your headline shows in search results and determines whether recruiters click. 220 characters max.</p>
                            ${optimizedData.current_headline ? `
                                <div class="current-vs-optimized">
                                    <span class="current-label">Current</span>
                                    <div class="current-content">${optimizedData.current_headline}</div>
                                </div>
                            ` : ''}
                            <span class="optimized-label">Optimized</span>
                            <div class="copyable-field">
                                <textarea readonly id="linkedin-headline" rows="2">${optimizedData.headline || ''}</textarea>
                                <button class="btn-copy" data-linkedin-copy="linkedin-headline">Copy</button>
                            </div>
                            ${optimizedData.headline_why?.length ? `
                                <div class="why-this-works">
                                    <div class="why-this-works-title">Why this works</div>
                                    <ul class="why-list">${optimizedData.headline_why.map(w => `<li>${w}</li>`).join('')}</ul>
                                </div>
                            ` : ''}
                            ${optimizedData.headline_update_reason ? `<div class="update-reason">💡 ${optimizedData.headline_update_reason}</div>` : ''}
                        </div>

                        <!-- About Section -->
                        <div class="linkedin-section-card">
                            <h4>About Section <span class="section-priority priority-critical">Critical</span></h4>
                            <p class="help-text">Your story: what you do, how you create value, and where you're headed. First 3 lines show before "see more".</p>
                            ${optimizedData.current_summary ? `
                                <div class="current-vs-optimized">
                                    <span class="current-label">Current</span>
                                    <div class="current-content">${optimizedData.current_summary.substring(0, 200)}${optimizedData.current_summary.length > 200 ? '...' : ''}</div>
                                </div>
                            ` : ''}
                            <span class="optimized-label">Optimized</span>
                            <div class="copyable-field">
                                <textarea readonly id="linkedin-summary" rows="12">${optimizedData.summary || ''}</textarea>
                                <button class="btn-copy" data-linkedin-copy="linkedin-summary">Copy</button>
                            </div>
                            ${optimizedData.summary_why?.length ? `
                                <div class="why-this-works">
                                    <div class="why-this-works-title">Why this works</div>
                                    <ul class="why-list">${optimizedData.summary_why.map(w => `<li>${w}</li>`).join('')}</ul>
                                </div>
                            ` : ''}
                            ${optimizedData.summary_update_reason ? `<div class="update-reason">💡 ${optimizedData.summary_update_reason}</div>` : ''}
                        </div>

                        <!-- CREDIBILITY SECTIONS -->
                        <div class="section-group-title">Credibility Signals</div>

                        <!-- Experience -->
                        ${optimizedData.experience_optimizations?.length ? `
                            <div class="linkedin-section-card">
                                <h4>Experience Bullets <span class="section-priority priority-high">High</span></h4>
                                <p class="help-text">Add these impact-first bullets to your experience section. Numbers and achievements that match your resume.</p>
                                ${optimizedData.experience_optimizations.map(exp => `
                                    <div class="experience-role">
                                        <div class="role-header">
                                            <div class="role-title">${exp.title}</div>
                                            <div class="role-company">${exp.company} • ${exp.dates}</div>
                                        </div>
                                        ${exp.company_context ? `<div class="role-context">${exp.company_context}</div>` : ''}
                                        <ul class="bullets-list">${exp.bullets.map(b => `<li>${b}</li>`).join('')}</ul>
                                        ${exp.why_these_work?.length ? `
                                            <div class="why-this-works" style="margin-top: 12px;">
                                                <div class="why-this-works-title">Why these work</div>
                                                <ul class="why-list">${exp.why_these_work.map(w => `<li>${w}</li>`).join('')}</ul>
                                            </div>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : optimizedData.experience_highlights?.length ? `
                            <div class="linkedin-section-card">
                                <h4>Experience Bullets <span class="section-priority priority-high">High</span></h4>
                                <p class="help-text">Add these to your current role. Impact-first language that matches your resume.</p>
                                <ul class="bullets-list">${optimizedData.experience_highlights.map(bullet => `<li>${bullet}</li>`).join('')}</ul>
                            </div>
                        ` : ''}

                        <!-- Skills -->
                        <div class="linkedin-section-card">
                            <h4>Skills to Feature <span class="section-priority priority-high">High</span></h4>
                            <p class="help-text">Recruiters use Boolean searches with skills. Your top 3 show in search previews.</p>
                            <div class="skills-section">
                                ${optimizedData.top_skills?.length ? `
                                    <div class="skills-group">
                                        <span class="skills-group-label top">Pin to Top 3</span>
                                        <ul class="skills-list top">${optimizedData.top_skills.map(s => `<li>${s}</li>`).join('')}</ul>
                                    </div>
                                ` : ''}
                                ${optimizedData.skills_to_add?.length ? `
                                    <div class="skills-group">
                                        <span class="skills-group-label add">Add These</span>
                                        <ul class="skills-list add">${optimizedData.skills_to_add.map(s => `<li>${s}</li>`).join('')}</ul>
                                    </div>
                                ` : ''}
                                ${optimizedData.skills_to_remove?.length ? `
                                    <div class="skills-group">
                                        <span class="skills-group-label remove">Consider Removing</span>
                                        <ul class="skills-list remove">${optimizedData.skills_to_remove.map(s => `<li>${s}</li>`).join('')}</ul>
                                    </div>
                                ` : ''}
                            </div>
                            ${optimizedData.skills_why?.length ? `
                                <div class="why-this-works" style="margin-top: 16px;">
                                    <div class="why-this-works-title">Why this prioritization</div>
                                    <ul class="why-list">${optimizedData.skills_why.map(w => `<li>${w}</li>`).join('')}</ul>
                                </div>
                            ` : ''}
                        </div>

                        <!-- OPTIONAL POWER-UPS -->
                        <div class="section-group-title">Optional Power-Ups</div>

                        <div style="display: grid; gap: 12px;">
                            <div class="optional-section-card">
                                <h5>Featured Section <span class="section-priority priority-medium">Medium</span></h5>
                                <p class="optional-tip">${optimizedData.featured_recommendation || 'Proof of work: case studies, press mentions, presentations, or portfolio pieces.'}</p>
                                ${optimizedData.featured_suggestions?.length ? `<ul class="who-to-ask-list">${optimizedData.featured_suggestions.map(s => `<li>• ${s}</li>`).join('')}</ul>` : ''}
                            </div>

                            <div class="optional-section-card">
                                <h5>Recommendations <span class="section-priority priority-medium">Medium</span></h5>
                                <p class="optional-tip">${optimizedData.recommendations_advice || '2-3 strong recommendations beat 10 generic ones. Ask people who can speak to specific accomplishments.'}</p>
                                ${optimizedData.who_to_ask?.length ? `<ul class="who-to-ask-list">${optimizedData.who_to_ask.map(w => `<li><strong>${w.person_type}:</strong> Ask them to emphasize ${w.what_to_emphasize}</li>`).join('')}</ul>` : ''}
                            </div>

                            <div class="optional-section-card">
                                <h5>Activity <span class="section-priority priority-low">Low</span></h5>
                                <p class="optional-tip">${optimizedData.activity_guidance?.recommendation || 'Recent engagement shows you are active. 2-3 thoughtful posts or comments per month beats daily generic engagement.'}</p>
                                ${optimizedData.activity_guidance?.topics?.length ? `
                                    <p style="margin-top: 8px; font-weight: 500; font-size: 0.85rem;">Focus your activity on:</p>
                                    <ul class="who-to-ask-list">${optimizedData.activity_guidance.topics.slice(0, 4).map(t => `<li>• ${t}</li>`).join('')}</ul>
                                ` : ''}
                                ${optimizedData.activity_guidance?.engagementTips?.length ? `
                                    <p style="margin-top: 8px; font-weight: 500; font-size: 0.85rem;">How to engage well:</p>
                                    <ul class="who-to-ask-list">${optimizedData.activity_guidance.engagementTips.map(t => `<li>• ${t}</li>`).join('')}</ul>
                                ` : ''}
                                ${optimizedData.activity_guidance?.avoidList?.length ? `
                                    <p style="margin-top: 8px; font-weight: 500; font-size: 0.85rem;">What to avoid:</p>
                                    <ul class="who-to-ask-list">${optimizedData.activity_guidance.avoidList.map(t => `<li>• ${t}</li>`).join('')}</ul>
                                ` : ''}
                                ${optimizedData.activity_guidance?.positioning ? `<p class="help-text" style="margin-top: 10px; font-style: italic;">💡 ${optimizedData.activity_guidance.positioning}</p>` : ''}
                            </div>
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
                </div>
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

            // Add copy button handlers
            container.querySelectorAll('[data-linkedin-copy]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const targetId = e.target.dataset.linkedinCopy;
                    const textarea = document.getElementById(targetId);
                    if (textarea) {
                        navigator.clipboard.writeText(textarea.value).then(() => {
                            const originalText = e.target.textContent;
                            e.target.textContent = 'Copied!';
                            setTimeout(() => { e.target.textContent = originalText; }, 2000);
                        });
                    }
                });
            });
        }

        /**
         * Get severity class for styling
         */
        getSeverityClass(severity) {
            const s = (severity || 'medium').toLowerCase();
            if (s === 'critical') return 'critical';
            if (s === 'high') return 'high';
            if (s === 'low') return 'low';
            return 'medium';
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
