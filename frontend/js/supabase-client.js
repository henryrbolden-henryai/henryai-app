/**
 * HenryAI Supabase Client
 * Handles authentication and data persistence
 */

// Prevent duplicate initialization
if (typeof window.HenryAuth !== 'undefined') {
    console.log('Supabase client already initialized, skipping...');
} else {

const SUPABASE_URL = 'https://xmbappvomvmanvybdavs.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtYmFwcHZvbXZtYW52eWJkYXZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUzOTczNjEsImV4cCI6MjA4MDk3MzM2MX0.hswKgjSEQalsJCyjPTcs4ngJH_BGrYKhUmAEEx5QmuU';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Auth Helper Functions
 */
const HenryAuth = {
    /**
     * Get current user session
     */
    async getSession() {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) console.error('Session error:', error);
        return session;
    },

    /**
     * Get current user
     */
    async getUser() {
        const { data: { user }, error } = await supabase.auth.getUser();
        if (error) console.error('User error:', error);
        return user;
    },

    /**
     * Get user's display name (from signup or Google)
     * Now supports first_name/last_name stored separately
     */
    async getUserName() {
        const user = await this.getUser();
        if (!user) return null;

        // Try to get first/last name from metadata (new format)
        const firstName = user.user_metadata?.first_name;
        const lastName = user.user_metadata?.last_name;

        if (firstName) {
            return {
                fullName: lastName ? `${firstName} ${lastName}` : firstName,
                firstName: firstName,
                lastName: lastName || ''
            };
        }

        // Fallback to old full_name format for existing users
        const fullName = user.user_metadata?.full_name ||
                        user.user_metadata?.name ||
                        user.email?.split('@')[0] ||
                        'there';

        // Parse first/last name from full_name
        const parts = fullName.trim().split(' ');
        return {
            fullName: fullName,
            firstName: parts[0] || fullName,
            lastName: parts.slice(1).join(' ') || ''
        };
    },

    /**
     * Sign up with email and password
     * Now accepts firstName and lastName separately
     * Backward compatible: if lastName is undefined, treats firstName as fullName
     */
    async signUp(email, password, firstName, lastName) {
        // Build metadata - support both old (fullName) and new (first/last) formats
        let metadata;
        if (lastName !== undefined) {
            // New format: separate first/last name
            metadata = {
                first_name: firstName,
                last_name: lastName,
                full_name: `${firstName} ${lastName}`.trim()  // For backward compatibility
            };
        } else {
            // Old format: single fullName (for backward compatibility)
            metadata = { full_name: firstName };
        }

        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: metadata
            }
        });
        return { data, error };
    },

    /**
     * Sign in with email and password
     */
    async signIn(email, password) {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });
        return { data, error };
    },

    /**
     * Sign out - clears all user-specific data
     */
    async signOut() {
        const { error } = await supabase.auth.signOut();
        if (!error) {
            // Clear all user-specific localStorage data
            this.clearUserData();
            window.location.href = 'login.html';
        }
        return { error };
    },

    /**
     * Clear all user-specific localStorage data
     * Called on sign out and when a different user signs in
     */
    clearUserData() {
        const userDataKeys = [
            'userProfile',
            'candidateProfile',
            'trackedApplications',
            'upcomingInterviews',
            'completedInterviews',
            'celebratedMilestones',
            'strategicOptionsDismissed',
            'linkedinConnections',
            'resumeConversation',
            'lastResumeAnalysis',
            'interventionState',
            'henryai_current_user_id',
            'henryai_needs_onboarding',
            'henryai_migrated_to_supabase',
            'beta_verified'
        ];

        userDataKeys.forEach(key => localStorage.removeItem(key));

        // Also clear sessionStorage
        sessionStorage.clear();

        console.log('User data cleared from local storage');
    },

    /**
     * Check if current user matches stored data, clear if different user
     */
    async validateUserData() {
        const user = await this.getUser();
        if (!user) return;

        const storedUserId = localStorage.getItem('henryai_current_user_id');

        if (storedUserId && storedUserId !== user.id) {
            // Different user logged in - clear old data
            console.log('Different user detected, clearing old data');
            this.clearUserData();
        }

        // Store current user ID
        localStorage.setItem('henryai_current_user_id', user.id);
    },

    /**
     * Send password reset email
     */
    async resetPassword(email) {
        const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password.html`
        });
        return { data, error };
    },

    /**
     * Check if user is authenticated, redirect to login if not
     */
    async requireAuth() {
        const session = await this.getSession();
        if (!session) {
            // Save current URL to redirect back after login
            sessionStorage.setItem('redirectAfterLogin', window.location.href);
            window.location.href = 'login.html';
            return null;
        }
        return session;
    },

    /**
     * Listen for auth state changes
     */
    onAuthStateChange(callback) {
        return supabase.auth.onAuthStateChange((event, session) => {
            callback(event, session);
        });
    }
};

/**
 * Data Storage Functions - Replaces localStorage
 */
const HenryData = {
    /**
     * Get user's candidate profile
     */
    async getCandidateProfile() {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('candidate_profiles')
            .select('profile_data')
            .eq('user_id', user.id)
            .single();

        if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
            console.error('Error fetching profile:', error);
        }
        return data?.profile_data || null;
    },

    /**
     * Save user's candidate profile
     */
    async saveCandidateProfile(profileData) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('candidate_profiles')
            .upsert({
                user_id: user.id,
                profile_data: profileData,
                updated_at: new Date().toISOString()
            }, {
                onConflict: 'user_id'
            });

        if (error) console.error('Error saving profile:', error);
        return { data, error };
    },

    /**
     * Get all applications for current user
     */
    async getApplications() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('applications')
            .select('*')
            .eq('user_id', user.id)
            .order('created_at', { ascending: false });

        if (error) {
            console.error('Error fetching applications:', error);
            return [];
        }

        // Transform to match existing localStorage format
        return data.map(app => ({
            id: app.id,
            company: app.company,
            role: app.role,
            status: app.status,
            fitScore: app.fit_score,
            dateApplied: app.date_applied,
            salary: app.salary,
            location: app.location,
            notes: app.notes,
            jobUrl: app.job_url,
            jobDescription: app.job_description,
            interviewDate: app.interview_date,
            analysisKey: app.id, // Use app id as key
            analysisData: app.analysis_data,
            documentsData: app.documents_data,
            ...app.metadata
        }));
    },

    /**
     * Save application
     */
    async saveApplication(app) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const appData = {
            user_id: user.id,
            company: app.company,
            role: app.role,
            status: app.status || 'Preparing',
            fit_score: app.fitScore,
            date_applied: app.dateApplied,
            salary: app.salary,
            location: app.location,
            notes: app.notes,
            job_url: app.jobUrl || null,
            job_description: app.jobDescription || null,
            interview_date: app.interviewDate || null,
            analysis_data: app.analysisData || {},
            documents_data: app.documentsData || {},
            metadata: {
                source: app.source,
                statusHistory: app.statusHistory,
                interviewRounds: app.interviewRounds,
                lastInteractionDate: app.lastInteractionDate
            },
            updated_at: new Date().toISOString()
        };

        // If app has a UUID id (string with dashes), update it; otherwise insert new
        // Convert id to string first since localStorage IDs may be numbers
        const appIdStr = String(app.id || '');
        if (appIdStr && appIdStr.includes('-')) {
            const { data, error } = await supabase
                .from('applications')
                .update(appData)
                .eq('id', app.id)
                .eq('user_id', user.id)
                .select()
                .single();
            return { data, error };
        } else {
            const { data, error } = await supabase
                .from('applications')
                .insert(appData)
                .select()
                .single();
            return { data, error };
        }
    },

    /**
     * Delete application
     */
    async deleteApplication(appId) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { error } = await supabase
            .from('applications')
            .delete()
            .eq('id', appId)
            .eq('user_id', user.id);

        return { error };
    },

    /**
     * Delete all applications for current user
     */
    async deleteAllApplications() {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { error } = await supabase
            .from('applications')
            .delete()
            .eq('user_id', user.id);

        if (error) console.error('Error deleting all applications:', error);
        return { error };
    },

    /**
     * Delete candidate profile for current user
     */
    async deleteCandidateProfile() {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { error } = await supabase
            .from('candidate_profiles')
            .delete()
            .eq('user_id', user.id);

        if (error) console.error('Error deleting candidate profile:', error);
        return { error };
    },

    /**
     * Save all applications (bulk update)
     */
    async saveAllApplications(apps) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        // This is used for status updates, etc.
        const results = await Promise.all(
            apps.map(app => this.saveApplication(app))
        );

        const errors = results.filter(r => r.error);
        if (errors.length > 0) {
            console.error('Errors saving applications:', errors);
        }
        return { errors };
    },

    /**
     * Update application documents data
     */
    async updateApplicationDocuments(appId, documentsData) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('applications')
            .update({
                documents_data: documentsData,
                updated_at: new Date().toISOString()
            })
            .eq('id', appId)
            .eq('user_id', user.id)
            .select()
            .single();

        return { data, error };
    },

    /**
     * Get resume conversation data
     */
    async getResumeConversation() {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('resume_conversations')
            .select('*')
            .eq('user_id', user.id)
            .single();

        if (error && error.code !== 'PGRST116') {
            console.error('Error fetching conversation:', error);
        }

        return data ? {
            conversationState: data.conversation_data,
            allExtractedSkills: data.extracted_data?.skills || []
        } : null;
    },

    /**
     * Save resume conversation data
     */
    async saveResumeConversation(conversationState, extractedSkills) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('resume_conversations')
            .upsert({
                user_id: user.id,
                conversation_data: conversationState,
                extracted_data: { skills: extractedSkills },
                updated_at: new Date().toISOString()
            }, {
                onConflict: 'user_id'
            });

        if (error) console.error('Error saving conversation:', error);
        return { data, error };
    },

    /**
     * Get all interviews for current user
     */
    async getInterviews() {
        const user = await HenryAuth.getUser();
        if (!user) return { upcoming: [], completed: [] };

        const { data, error } = await supabase
            .from('interviews')
            .select('*')
            .eq('user_id', user.id)
            .order('interview_date', { ascending: true });

        if (error) {
            console.error('Error fetching interviews:', error);
            return { upcoming: [], completed: [] };
        }

        const now = new Date();
        const upcoming = [];
        const completed = [];

        data.forEach(interview => {
            const formatted = {
                id: interview.id,
                company: interview.company,
                role: interview.role,
                type: interview.interview_type,
                date: interview.interview_date,
                time: interview.interview_time,
                location: interview.location,
                interviewerName: interview.interviewer_name,
                interviewerTitle: interview.interviewer_title,
                interviewerLinkedIn: interview.interviewer_linkedin,
                notes: interview.notes,
                prepNotes: interview.prep_notes,
                debriefNotes: interview.debrief_notes,
                applicationId: interview.application_id,
                status: interview.status,
                ...interview.metadata
            };

            if (interview.status === 'completed') {
                completed.push(formatted);
            } else {
                upcoming.push(formatted);
            }
        });

        return { upcoming, completed };
    },

    /**
     * Save interview
     */
    async saveInterview(interview) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const interviewData = {
            user_id: user.id,
            company: interview.company,
            role: interview.role,
            interview_type: interview.type,
            interview_date: interview.date,
            interview_time: interview.time,
            location: interview.location,
            interviewer_name: interview.interviewerName,
            interviewer_title: interview.interviewerTitle,
            interviewer_linkedin: interview.interviewerLinkedIn,
            notes: interview.notes,
            prep_notes: interview.prepNotes,
            debrief_notes: interview.debriefNotes,
            application_id: interview.applicationId,
            status: interview.status || 'scheduled',
            metadata: {
                source: interview.source,
                linkedFromTracker: interview.linkedFromTracker
            },
            updated_at: new Date().toISOString()
        };

        // If interview has a UUID id, update it; otherwise insert new
        const interviewIdStr = String(interview.id || '');
        if (interviewIdStr && interviewIdStr.includes('-')) {
            const { data, error } = await supabase
                .from('interviews')
                .update(interviewData)
                .eq('id', interview.id)
                .eq('user_id', user.id)
                .select()
                .single();
            return { data, error };
        } else {
            const { data, error } = await supabase
                .from('interviews')
                .insert(interviewData)
                .select()
                .single();
            return { data, error };
        }
    },

    /**
     * Delete interview
     */
    async deleteInterview(interviewId) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { error } = await supabase
            .from('interviews')
            .delete()
            .eq('id', interviewId)
            .eq('user_id', user.id);

        return { error };
    },

    /**
     * Mark interview as completed with debrief
     */
    async completeInterview(interviewId, debriefNotes) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('interviews')
            .update({
                status: 'completed',
                debrief_notes: debriefNotes,
                updated_at: new Date().toISOString()
            })
            .eq('id', interviewId)
            .eq('user_id', user.id)
            .select()
            .single();

        return { data, error };
    },

    /**
     * Save beta feedback from Hey Henry
     */
    async saveFeedback(feedbackData) {
        const user = await HenryAuth.getUser();

        const { data, error } = await supabase
            .from('beta_feedback')
            .insert({
                user_id: user?.id || null,
                user_email: user?.email || 'anonymous',
                feedback_type: feedbackData.type || 'general',
                feedback_text: feedbackData.text,
                current_page: feedbackData.currentPage || window.location.pathname,
                context: feedbackData.context || {},
                conversation_snippet: feedbackData.conversationSnippet || [],
                screenshot: feedbackData.screenshot || null,
                created_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) {
            console.error('Error saving feedback:', error);
        } else {
            console.log('✅ Feedback saved:', data.id);
        }

        return { data, error };
    },

    /**
     * Get user profile data
     */
    async getProfile() {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('candidate_profiles')
            .select('*')
            .eq('user_id', user.id)
            .single();

        if (error && error.code !== 'PGRST116') {
            console.error('Error fetching profile:', error);
        }
        return data?.profile_data || null;
    },

    /**
     * Migrate localStorage data to Supabase (run once on first login)
     */
    async migrateFromLocalStorage() {
        const user = await HenryAuth.getUser();
        if (!user) return;

        // Check if already migrated
        const migrated = localStorage.getItem('henryai_migrated_to_supabase');
        if (migrated === user.id) {
            console.log('Already migrated for this user');
            return;
        }

        console.log('Starting migration from localStorage to Supabase...');

        // Migrate candidate profile
        const candidateProfile = localStorage.getItem('candidateProfile');
        if (candidateProfile) {
            try {
                await this.saveCandidateProfile(JSON.parse(candidateProfile));
                console.log('✅ Migrated candidate profile');
            } catch (e) {
                console.error('Failed to migrate candidate profile:', e);
            }
        }

        // Migrate applications
        const applications = localStorage.getItem('trackedApplications');
        if (applications) {
            try {
                const apps = JSON.parse(applications);
                for (const app of apps) {
                    // Get associated analysis and documents data
                    if (app.analysisKey) {
                        const analysisData = localStorage.getItem(`analysis_${app.analysisKey}`);
                        const documentsData = localStorage.getItem(`documents_${app.analysisKey}`);
                        app.analysisData = analysisData ? JSON.parse(analysisData) : {};
                        app.documentsData = documentsData ? JSON.parse(documentsData) : {};
                    }
                    await this.saveApplication(app);
                }
                console.log(`✅ Migrated ${apps.length} applications`);
            } catch (e) {
                console.error('Failed to migrate applications:', e);
            }
        }

        // Migrate resume conversation
        const resumeConversation = localStorage.getItem('resumeConversation');
        if (resumeConversation) {
            try {
                const data = JSON.parse(resumeConversation);
                await this.saveResumeConversation(
                    data.conversationState,
                    data.allExtractedSkills || []
                );
                console.log('✅ Migrated resume conversation');
            } catch (e) {
                console.error('Failed to migrate resume conversation:', e);
            }
        }

        // Migrate upcoming interviews
        const upcomingInterviews = localStorage.getItem('upcomingInterviews');
        if (upcomingInterviews) {
            try {
                const interviews = JSON.parse(upcomingInterviews);
                for (const interview of interviews) {
                    interview.status = 'scheduled';
                    await this.saveInterview(interview);
                }
                console.log(`✅ Migrated ${interviews.length} upcoming interviews`);
            } catch (e) {
                console.error('Failed to migrate upcoming interviews:', e);
            }
        }

        // Migrate completed interviews
        const completedInterviews = localStorage.getItem('completedInterviews');
        if (completedInterviews) {
            try {
                const interviews = JSON.parse(completedInterviews);
                for (const interview of interviews) {
                    interview.status = 'completed';
                    await this.saveInterview(interview);
                }
                console.log(`✅ Migrated ${interviews.length} completed interviews`);
            } catch (e) {
                console.error('Failed to migrate completed interviews:', e);
            }
        }

        // Mark as migrated
        localStorage.setItem('henryai_migrated_to_supabase', user.id);
        console.log('✅ Migration complete!');
    },

    // ==========================================
    // Hey Henry Conversation Persistence
    // ==========================================

    /**
     * Get user's Hey Henry conversations (most recent first)
     * @param {number} limit - Max number of conversations to return (default 10)
     */
    async getHeyHenryConversations(limit = 10) {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('hey_henry_conversations')
            .select('id, created_at, updated_at, messages')
            .eq('user_id', user.id)
            .order('updated_at', { ascending: false })
            .limit(limit);

        if (error) {
            console.error('Error fetching Hey Henry conversations:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Get a specific Hey Henry conversation by ID
     * @param {string} conversationId - UUID of the conversation
     */
    async getHeyHenryConversation(conversationId) {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('hey_henry_conversations')
            .select('*')
            .eq('id', conversationId)
            .eq('user_id', user.id)
            .single();

        if (error) {
            console.error('Error fetching Hey Henry conversation:', error);
            return null;
        }

        return data;
    },

    /**
     * Get the most recent Hey Henry conversation (if updated within last 24 hours)
     * @returns {Object|null} - The conversation or null if none recent
     */
    async getMostRecentHeyHenryConversation() {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

        const { data, error } = await supabase
            .from('hey_henry_conversations')
            .select('*')
            .eq('user_id', user.id)
            .gte('updated_at', twentyFourHoursAgo)
            .order('updated_at', { ascending: false })
            .limit(1)
            .single();

        if (error && error.code !== 'PGRST116') {
            console.error('Error fetching recent Hey Henry conversation:', error);
        }

        return data || null;
    },

    /**
     * Create a new Hey Henry conversation
     * @param {Array} messages - Initial messages array
     * @returns {Object} - The created conversation with id
     */
    async createHeyHenryConversation(messages = []) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('hey_henry_conversations')
            .insert({
                user_id: user.id,
                messages: messages
            })
            .select()
            .single();

        if (error) {
            console.error('Error creating Hey Henry conversation:', error);
        } else {
            console.log('✅ Created Hey Henry conversation:', data.id);
        }

        return { data, error };
    },

    /**
     * Update a Hey Henry conversation with new messages
     * @param {string} conversationId - UUID of the conversation
     * @param {Array} messages - Updated messages array
     */
    async updateHeyHenryConversation(conversationId, messages) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('hey_henry_conversations')
            .update({
                messages: messages
            })
            .eq('id', conversationId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating Hey Henry conversation:', error);
        }

        return { data, error };
    },

    /**
     * Delete a Hey Henry conversation
     * @param {string} conversationId - UUID of the conversation
     */
    async deleteHeyHenryConversation(conversationId) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { error } = await supabase
            .from('hey_henry_conversations')
            .delete()
            .eq('id', conversationId)
            .eq('user_id', user.id);

        if (error) {
            console.error('Error deleting Hey Henry conversation:', error);
        } else {
            console.log('✅ Deleted Hey Henry conversation:', conversationId);
        }

        return { error };
    },

    // ==========================================
    // Interview Debriefs (Phase 2.3)
    // ==========================================

    /**
     * Create a new interview debrief
     * @param {Object} debriefData - Structured debrief data
     */
    async createDebrief(debriefData) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('interview_debriefs')
            .insert({
                user_id: user.id,
                company: debriefData.company,
                role: debriefData.role,
                interview_type: debriefData.interview_type,
                interview_date: debriefData.interview_date,
                interviewer_name: debriefData.interviewer_name,
                duration_minutes: debriefData.duration_minutes,
                rating_overall: debriefData.rating_overall,
                rating_confidence: debriefData.rating_confidence,
                rating_preparation: debriefData.rating_preparation,
                questions_asked: debriefData.questions_asked || [],
                question_categories: debriefData.question_categories || [],
                stumbles: debriefData.stumbles || [],
                wins: debriefData.wins || [],
                stories_used: debriefData.stories_used || [],
                interviewer_signals: debriefData.interviewer_signals || {},
                key_insights: debriefData.key_insights || [],
                improvement_areas: debriefData.improvement_areas || [],
                raw_conversation: debriefData.raw_conversation,
                application_id: debriefData.application_id
            })
            .select()
            .single();

        if (error) {
            console.error('Error creating debrief:', error);
        } else {
            console.log('✅ Created interview debrief:', data.id);
        }

        return { data, error };
    },

    /**
     * Get user's debriefs with optional filters
     * @param {Object} filters - { company, interview_type, limit }
     */
    async getDebriefs(filters = {}) {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        let query = supabase
            .from('interview_debriefs')
            .select('*')
            .eq('user_id', user.id)
            .order('interview_date', { ascending: false, nullsFirst: false });

        if (filters.company) {
            query = query.ilike('company', `%${filters.company}%`);
        }

        if (filters.interview_type) {
            query = query.eq('interview_type', filters.interview_type);
        }

        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query;

        if (error) {
            console.error('Error fetching debriefs:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Get debriefs for a specific company
     * @param {string} company - Company name
     */
    async getDebriefsByCompany(company) {
        return this.getDebriefs({ company });
    },

    /**
     * Get all debriefs for pattern analysis
     */
    async getDebriefsForPatternAnalysis() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('interview_debriefs')
            .select('id, company, role, interview_type, interview_date, rating_overall, rating_confidence, rating_preparation, question_categories, stumbles, wins, stories_used, improvement_areas')
            .eq('user_id', user.id)
            .order('interview_date', { ascending: true });

        if (error) {
            console.error('Error fetching debriefs for analysis:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Update a debrief
     * @param {string} debriefId - UUID of the debrief
     * @param {Object} updates - Fields to update
     */
    async updateDebrief(debriefId, updates) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('interview_debriefs')
            .update(updates)
            .eq('id', debriefId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating debrief:', error);
        }

        return { data, error };
    },

    /**
     * Update debrief outcome (when application status changes)
     * @param {string} debriefId - UUID of the debrief
     * @param {string} outcome - 'advanced', 'rejected', 'pending', 'ghosted'
     */
    async updateDebriefOutcome(debriefId, outcome) {
        return this.updateDebrief(debriefId, {
            outcome,
            outcome_updated_at: new Date().toISOString()
        });
    },

    // ==========================================
    // Story Bank (Phase 2.3)
    // ==========================================

    /**
     * Get user's story bank
     */
    async getStoryBank() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('user_story_bank')
            .select('*')
            .eq('user_id', user.id)
            .order('times_used', { ascending: false });

        if (error) {
            console.error('Error fetching story bank:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Add or update a story in the bank
     * @param {Object} story - Story data
     */
    async addStory(story) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        // Check if story with same name exists
        const { data: existing } = await supabase
            .from('user_story_bank')
            .select('id')
            .eq('user_id', user.id)
            .ilike('story_name', story.story_name)
            .single();

        if (existing) {
            // Update existing story
            return this.updateStoryUsage(existing.id, story.interview_id, story.effectiveness);
        }

        // Create new story
        const { data, error } = await supabase
            .from('user_story_bank')
            .insert({
                user_id: user.id,
                story_name: story.story_name,
                story_summary: story.story_summary,
                story_context: story.story_context,
                demonstrates: story.demonstrates || [],
                best_for_questions: story.best_for_questions || [],
                times_used: 1,
                last_used_at: new Date().toISOString(),
                effectiveness_avg: story.effectiveness || null,
                interviews_used_in: story.interview_id ? [story.interview_id] : []
            })
            .select()
            .single();

        if (error) {
            console.error('Error adding story:', error);
        } else {
            console.log('✅ Added story to bank:', story.story_name);
        }

        return { data, error };
    },

    /**
     * Update story usage (increment count, update effectiveness)
     * @param {string} storyId - UUID of the story
     * @param {string} interviewId - UUID of the interview where story was used
     * @param {number} effectiveness - Effectiveness rating 1-5
     */
    async updateStoryUsage(storyId, interviewId, effectiveness) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        // First get current story data
        const { data: current, error: fetchError } = await supabase
            .from('user_story_bank')
            .select('times_used, effectiveness_avg, interviews_used_in')
            .eq('id', storyId)
            .eq('user_id', user.id)
            .single();

        if (fetchError) {
            return { data: null, error: fetchError };
        }

        // Calculate new effectiveness average
        const timesUsed = (current.times_used || 0) + 1;
        let newEffectivenessAvg = current.effectiveness_avg;
        if (effectiveness) {
            if (current.effectiveness_avg) {
                newEffectivenessAvg = ((current.effectiveness_avg * current.times_used) + effectiveness) / timesUsed;
            } else {
                newEffectivenessAvg = effectiveness;
            }
        }

        // Update interviews_used_in array
        const interviewsUsedIn = current.interviews_used_in || [];
        if (interviewId && !interviewsUsedIn.includes(interviewId)) {
            interviewsUsedIn.push(interviewId);
        }

        const { data, error } = await supabase
            .from('user_story_bank')
            .update({
                times_used: timesUsed,
                last_used_at: new Date().toISOString(),
                effectiveness_avg: newEffectivenessAvg,
                interviews_used_in: interviewsUsedIn
            })
            .eq('id', storyId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating story usage:', error);
        }

        return { data, error };
    },

    /**
     * Retire a story (mark as no longer active)
     * @param {string} storyId - UUID of the story
     */
    async retireStory(storyId) {
        const user = await HenryAuth.getUser();
        if (!user) return { data: null, error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('user_story_bank')
            .update({ status: 'retired' })
            .eq('id', storyId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error retiring story:', error);
        }

        return { data, error };
    },

    /**
     * Get active stories (not overused or retired)
     */
    async getActiveStories() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('user_story_bank')
            .select('*')
            .eq('user_id', user.id)
            .eq('status', 'active')
            .order('effectiveness_avg', { ascending: false, nullsFirst: false });

        if (error) {
            console.error('Error fetching active stories:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Get overused stories
     */
    async getOverusedStories() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('user_story_bank')
            .select('*')
            .eq('user_id', user.id)
            .eq('status', 'overused')
            .order('times_used', { ascending: false });

        if (error) {
            console.error('Error fetching overused stories:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Update a story
     * @param {string} storyId - UUID of the story
     * @param {Object} updates - Fields to update
     */
    async updateStory(storyId, updates) {
        const user = await HenryAuth.getUser();
        if (!user) throw new Error('Not authenticated');

        const { data, error } = await supabase
            .from('user_story_bank')
            .update({
                ...updates,
                updated_at: new Date().toISOString()
            })
            .eq('id', storyId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating story:', error);
            throw error;
        }

        return data;
    },

    /**
     * Delete a story permanently
     * @param {string} storyId - UUID of the story
     */
    async deleteStory(storyId) {
        const user = await HenryAuth.getUser();
        if (!user) throw new Error('Not authenticated');

        const { error } = await supabase
            .from('user_story_bank')
            .delete()
            .eq('id', storyId)
            .eq('user_id', user.id);

        if (error) {
            console.error('Error deleting story:', error);
            throw error;
        }

        return true;
    },

    // ==========================================
    // Multi-Resume Management
    // ==========================================

    /**
     * Get all resumes for the current user
     * @returns {Array} - List of resume objects
     */
    async getResumes() {
        const user = await HenryAuth.getUser();
        if (!user) return [];

        const { data, error } = await supabase
            .from('user_resumes')
            .select('*')
            .eq('user_id', user.id)
            .order('created_at', { ascending: false });

        if (error) {
            console.error('Error fetching resumes:', error);
            return [];
        }

        return data || [];
    },

    /**
     * Get the default resume for the current user
     * @returns {Object|null} - The default resume or null
     */
    async getDefaultResume() {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('user_resumes')
            .select('*')
            .eq('user_id', user.id)
            .eq('is_default', true)
            .single();

        if (error && error.code !== 'PGRST116') {
            console.error('Error fetching default resume:', error);
        }

        return data || null;
    },

    /**
     * Get a specific resume by ID
     * @param {string} resumeId - UUID of the resume
     * @returns {Object|null} - The resume or null
     */
    async getResume(resumeId) {
        const user = await HenryAuth.getUser();
        if (!user) return null;

        const { data, error } = await supabase
            .from('user_resumes')
            .select('*')
            .eq('id', resumeId)
            .eq('user_id', user.id)
            .single();

        if (error) {
            console.error('Error fetching resume:', error);
            return null;
        }

        return data;
    },

    /**
     * Save a new resume
     * @param {string} resumeName - Display name for the resume
     * @param {Object} resumeJson - Parsed resume data
     * @param {boolean} accuracyConfirmed - User confirmed accuracy
     * @param {boolean} isDefault - Set as default resume
     * @returns {Object} - { data, error }
     */
    async saveResume(resumeName, resumeJson, accuracyConfirmed = false, isDefault = false) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        if (!accuracyConfirmed) {
            return { error: 'You must confirm the resume accuracy' };
        }

        // Check count limit (5 max)
        const existing = await this.getResumes();
        if (existing.length >= 5) {
            return { error: 'Maximum 5 resumes allowed. Please delete one before adding another.' };
        }

        // First resume is always default
        const shouldBeDefault = isDefault || existing.length === 0;

        // If setting as default, clear other defaults first
        if (shouldBeDefault && existing.length > 0) {
            await supabase
                .from('user_resumes')
                .update({ is_default: false })
                .eq('user_id', user.id)
                .eq('is_default', true);
        }

        const { data, error } = await supabase
            .from('user_resumes')
            .insert({
                user_id: user.id,
                resume_name: resumeName,
                resume_json: resumeJson,
                is_default: shouldBeDefault,
                accuracy_confirmed: accuracyConfirmed
            })
            .select()
            .single();

        if (error) {
            console.error('Error saving resume:', error);
        } else {
            console.log('✅ Resume saved:', data.id);

            // Extract and save companies from resume with pedigree tagging
            if (resumeJson.experience && Array.isArray(resumeJson.experience)) {
                await this.extractAndSaveCompaniesFromResume(user.id, data.id, resumeJson.experience);
            }

            // Extract and save location from resume if available
            await this.extractAndSaveLocationFromResume(user.id, resumeJson);

            // Check for name mismatch between signup and resume
            await this.checkNameMismatch(user.id, resumeJson);
        }

        return { data, error };
    },

    /**
     * Check if resume name matches signup name and flag if different
     * @param {string} userId - User's UUID
     * @param {object} resumeJson - Parsed resume JSON
     */
    async checkNameMismatch(userId, resumeJson) {
        if (!resumeJson) return;

        // Get resume name from various possible fields
        const resumeName = resumeJson.name ||
                          resumeJson.full_name ||
                          resumeJson.contact?.name ||
                          resumeJson.basics?.name ||
                          resumeJson.header?.name;

        if (!resumeName) return;

        // Get signup name from auth metadata
        const nameData = await HenryAuth.getUserName();
        if (!nameData) return;

        const signupFullName = nameData.fullName?.toLowerCase().trim() || '';
        const resumeFullName = resumeName.toLowerCase().trim();

        // Normalize names for comparison (remove extra spaces, punctuation)
        const normalize = (name) => name.replace(/[^a-z\s]/g, '').replace(/\s+/g, ' ').trim();
        const normalizedSignup = normalize(signupFullName);
        const normalizedResume = normalize(resumeFullName);

        // Check for mismatch
        if (normalizedSignup && normalizedResume && normalizedSignup !== normalizedResume) {
            // Check if it's a minor mismatch (same first name, different format)
            const signupFirst = normalizedSignup.split(' ')[0];
            const resumeFirst = normalizedResume.split(' ')[0];
            const isMajorMismatch = signupFirst !== resumeFirst;

            // Store mismatch status for Hey Henry to reference
            const mismatchData = {
                signup_name: nameData.fullName,
                resume_name: resumeName,
                mismatch_type: isMajorMismatch ? 'major' : 'minor',
                detected_at: new Date().toISOString()
            };

            // Save to localStorage for Hey Henry to pick up
            localStorage.setItem('henryai_name_mismatch', JSON.stringify(mismatchData));
            console.log('⚠️ Name mismatch detected:', mismatchData);

            // Update candidate profile with mismatch flag
            await supabase
                .from('candidate_profiles')
                .upsert({
                    id: userId,
                    name_match_status: isMajorMismatch ? 'major_mismatch' : 'minor_mismatch',
                    updated_at: new Date().toISOString()
                });
        } else {
            // Names match - clear any previous mismatch
            localStorage.removeItem('henryai_name_mismatch');
        }
    },

    /**
     * Extract location from resume and update candidate profile
     * @param {string} userId - User's UUID
     * @param {object} resumeJson - Parsed resume JSON
     */
    async extractAndSaveLocationFromResume(userId, resumeJson) {
        if (!resumeJson) return;

        // Try to find location from various possible fields in resume
        let location = resumeJson.location ||
                       resumeJson.contact?.location ||
                       resumeJson.basics?.location ||
                       resumeJson.header?.location ||
                       resumeJson.personalInfo?.location;

        if (!location) return;

        // Parse location string or object
        let city = null, state = null, country = null;

        if (typeof location === 'string') {
            // Parse "City, State" or "City, State, Country" format
            const parts = location.split(',').map(p => p.trim());
            if (parts.length >= 1) city = parts[0];
            if (parts.length >= 2) state = parts[1];
            if (parts.length >= 3) country = parts[2];

            // Try to detect US states and default country
            if (state && !country) {
                const usStates = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC',
                    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'];
                if (usStates.some(s => state.toLowerCase() === s.toLowerCase())) {
                    country = 'US';
                }
            }
        } else if (typeof location === 'object') {
            // Handle structured location object
            city = location.city || location.City;
            state = location.state || location.State || location.region || location.Region;
            country = location.country || location.Country || location.countryCode;
        }

        if (!city && !state && !country) return;

        // Check if user already has location set - don't override
        const { data: existingProfile } = await supabase
            .from('candidate_profiles')
            .select('city, state, country')
            .eq('id', userId)
            .single();

        // Only update if fields are empty
        const updates = {};
        if (city && (!existingProfile?.city)) updates.city = city;
        if (state && (!existingProfile?.state)) updates.state = state;
        if (country && (!existingProfile?.country)) updates.country = country;

        if (Object.keys(updates).length === 0) return;

        const { error } = await supabase
            .from('candidate_profiles')
            .upsert({
                id: userId,
                ...updates,
                updated_at: new Date().toISOString()
            });

        if (error) {
            console.error('Error saving location from resume:', error);
        } else {
            console.log('✅ Extracted location from resume:', updates);
        }
    },

    /**
     * Extract companies from resume experience and save with pedigree tagging
     * @param {string} userId - User's UUID
     * @param {string} resumeId - Resume UUID
     * @param {Array} experience - Array of experience objects from resume
     */
    async extractAndSaveCompaniesFromResume(userId, resumeId, experience) {
        if (!experience || !Array.isArray(experience)) return;

        // Get the pedigree lookup table
        const { data: pedigreeLookup } = await supabase
            .from('company_pedigree_lookup')
            .select('company_normalized, company_aliases, pedigree_tags');

        // Build a lookup map for fast matching
        const pedigreeMap = new Map();
        if (pedigreeLookup) {
            pedigreeLookup.forEach(company => {
                // Add normalized name
                pedigreeMap.set(company.company_normalized, company.pedigree_tags);
                // Add aliases
                if (company.company_aliases) {
                    company.company_aliases.forEach(alias => {
                        pedigreeMap.set(alias.toLowerCase(), company.pedigree_tags);
                    });
                }
            });
        }

        // Helper to normalize company name
        const normalizeCompany = (name) => {
            if (!name) return '';
            return name.toLowerCase()
                .replace(/,?\s*(inc\.?|llc|ltd\.?|corp\.?|corporation|company|co\.?)$/i, '')
                .replace(/[.,]/g, '')
                .trim();
        };

        // Helper to parse date (handles various formats)
        const parseDate = (dateStr) => {
            if (!dateStr) return null;
            // Handle "Present", "Current", etc.
            if (/present|current|now/i.test(dateStr)) return null;
            // Try to parse
            const parsed = new Date(dateStr);
            if (!isNaN(parsed.getTime())) {
                return parsed.toISOString().split('T')[0]; // Return YYYY-MM-DD
            }
            return null;
        };

        // Helper to calculate duration in months
        const calculateDuration = (startDate, endDate) => {
            if (!startDate) return null;
            const start = new Date(startDate);
            const end = endDate ? new Date(endDate) : new Date();
            const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
            return Math.max(1, months); // At least 1 month
        };

        // Process each experience entry
        const companiesToSave = [];
        const seenCompanies = new Set(); // Avoid duplicates

        for (const exp of experience) {
            const companyName = exp.company || exp.organization || exp.employer;
            if (!companyName) continue;

            const normalized = normalizeCompany(companyName);
            if (!normalized || seenCompanies.has(normalized)) continue;
            seenCompanies.add(normalized);

            // Look up pedigree tags
            const pedigreeTags = pedigreeMap.get(normalized) || [];

            // Parse dates
            const startDate = parseDate(exp.start_date || exp.startDate || exp.from);
            const endDate = parseDate(exp.end_date || exp.endDate || exp.to);
            const isCurrent = !endDate || /present|current|now/i.test(exp.end_date || exp.endDate || exp.to || '');

            companiesToSave.push({
                user_id: userId,
                company_name: companyName,
                company_normalized: normalized,
                pedigree_tags: pedigreeTags,
                title: exp.title || exp.position || exp.role,
                start_date: startDate,
                end_date: endDate,
                is_current: isCurrent,
                duration_months: calculateDuration(startDate, endDate),
                source: 'resume',
                resume_id: resumeId
            });
        }

        if (companiesToSave.length === 0) return;

        // Delete existing companies from this resume (to handle updates)
        await supabase
            .from('candidate_companies')
            .delete()
            .eq('user_id', userId)
            .eq('resume_id', resumeId);

        // Insert new companies
        const { error } = await supabase
            .from('candidate_companies')
            .insert(companiesToSave);

        if (error) {
            console.error('Error saving companies from resume:', error);
        } else {
            console.log(`✅ Extracted ${companiesToSave.length} companies from resume`);

            // Update candidate profile with pedigree summary
            await this.updateCandidatePedigreeSummary(userId);
        }
    },

    /**
     * Update candidate profile with aggregated pedigree summary
     * @param {string} userId - User's UUID
     */
    async updateCandidatePedigreeSummary(userId) {
        // Get all companies for this user
        const { data: companies } = await supabase
            .from('candidate_companies')
            .select('pedigree_tags')
            .eq('user_id', userId);

        if (!companies) return;

        // Aggregate all pedigree tags
        const tagCounts = {};
        let hasPedigree = false;

        companies.forEach(company => {
            if (company.pedigree_tags && company.pedigree_tags.length > 0) {
                hasPedigree = true;
                company.pedigree_tags.forEach(tag => {
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                });
            }
        });

        // Build summary object: { faang: true, mbb: false, ... }
        const pedigreeSummary = {};
        const knownTags = ['faang', 'big_tech', 'mbb', 'big4', 'unicorn', 'bulge_bracket', 'consulting', 'finance'];
        knownTags.forEach(tag => {
            pedigreeSummary[tag] = tagCounts[tag] > 0;
        });

        // Update candidate profile
        const { error } = await supabase
            .from('candidate_profiles')
            .update({
                pedigree_summary: pedigreeSummary,
                has_pedigree: hasPedigree,
                updated_at: new Date().toISOString()
            })
            .eq('id', userId);

        if (error) {
            console.error('Error updating pedigree summary:', error);
        } else {
            console.log('✅ Updated pedigree summary:', pedigreeSummary);
        }
    },

    /**
     * Update a resume's name or default status
     * @param {string} resumeId - UUID of the resume
     * @param {Object} updates - { resume_name, is_default }
     * @returns {Object} - { data, error }
     */
    async updateResume(resumeId, updates) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        // If setting as default, clear other defaults first
        if (updates.is_default) {
            await supabase
                .from('user_resumes')
                .update({ is_default: false })
                .eq('user_id', user.id)
                .eq('is_default', true);
        }

        const { data, error } = await supabase
            .from('user_resumes')
            .update({
                ...updates,
                updated_at: new Date().toISOString()
            })
            .eq('id', resumeId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating resume:', error);
        }

        return { data, error };
    },

    /**
     * Delete a resume
     * @param {string} resumeId - UUID of the resume
     * @returns {Object} - { success, error }
     */
    async deleteResume(resumeId) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        // Check if this is the default
        const resume = await this.getResume(resumeId);
        const wasDefault = resume?.is_default;

        const { error } = await supabase
            .from('user_resumes')
            .delete()
            .eq('id', resumeId)
            .eq('user_id', user.id);

        if (error) {
            console.error('Error deleting resume:', error);
            return { error };
        }

        // If deleted was default, set another as default
        if (wasDefault) {
            const remaining = await this.getResumes();
            if (remaining.length > 0) {
                await this.updateResume(remaining[0].id, { is_default: true });
            }
        }

        console.log('✅ Resume deleted:', resumeId);
        return { success: true };
    },

    /**
     * Set a resume as the default
     * @param {string} resumeId - UUID of the resume
     * @returns {Object} - { data, error }
     */
    async setDefaultResume(resumeId) {
        return this.updateResume(resumeId, { is_default: true });
    },

    /**
     * Update resume verification status after LinkedIn comparison
     * @param {string} resumeId - UUID of the resume
     * @param {boolean} verified - Whether it matches LinkedIn
     * @param {Object} notes - Mismatch details if any
     * @returns {Object} - { data, error }
     */
    async updateResumeVerification(resumeId, verified, notes = null) {
        const user = await HenryAuth.getUser();
        if (!user) return { error: 'Not authenticated' };

        const { data, error } = await supabase
            .from('user_resumes')
            .update({
                linkedin_verified: verified,
                verification_notes: notes,
                updated_at: new Date().toISOString()
            })
            .eq('id', resumeId)
            .eq('user_id', user.id)
            .select()
            .single();

        if (error) {
            console.error('Error updating resume verification:', error);
        }

        return { data, error };
    },

    /**
     * Get resume count for current user
     * @returns {number} - Number of resumes
     */
    async getResumeCount() {
        const resumes = await this.getResumes();
        return resumes.length;
    }
};

// Export for use in other files
window.HenryAuth = HenryAuth;
window.HenryData = HenryData;
window.supabase = supabase;

} // End of duplicate initialization check
