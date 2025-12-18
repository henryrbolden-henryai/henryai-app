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
     */
    async getUserName() {
        const user = await this.getUser();
        if (!user) return null;

        // Try different sources for the name
        const fullName = user.user_metadata?.full_name ||
                        user.user_metadata?.name ||
                        user.email?.split('@')[0] ||
                        'there';

        // Parse first/last name
        const parts = fullName.trim().split(' ');
        return {
            fullName: fullName,
            firstName: parts[0] || fullName,
            lastName: parts.slice(1).join(' ') || ''
        };
    },

    /**
     * Sign up with email and password
     */
    async signUp(email, password, fullName) {
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: { full_name: fullName }
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
     * Sign out
     */
    async signOut() {
        const { error } = await supabase.auth.signOut();
        if (!error) {
            window.location.href = 'login.html';
        }
        return { error };
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
     * Save beta feedback from Ask Henry
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
    }
};

// Export for use in other files
window.HenryAuth = HenryAuth;
window.HenryData = HenryData;
window.supabase = supabase;

} // End of duplicate initialization check
