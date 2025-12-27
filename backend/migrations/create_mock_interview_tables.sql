-- Create mock interview tables for persistent storage
-- Replaces in-memory storage that was lost on server restart

-- Mock Interview Sessions
CREATE TABLE IF NOT EXISTS mock_interview_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_json JSONB NOT NULL,
    job_description TEXT,
    company TEXT,
    role_title TEXT,
    interview_stage TEXT CHECK (interview_stage IN ('recruiter_screen', 'hiring_manager', 'technical', 'behavioral')),
    difficulty_level TEXT DEFAULT 'medium' CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    session_feedback JSONB,
    current_question_number INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mock Interview Questions
CREATE TABLE IF NOT EXISTS mock_interview_questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES mock_interview_sessions(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    competency_tested TEXT,
    difficulty TEXT DEFAULT 'medium',
    asked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mock Interview Responses
CREATE TABLE IF NOT EXISTS mock_interview_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question_id UUID NOT NULL REFERENCES mock_interview_questions(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES mock_interview_sessions(id) ON DELETE CASCADE,
    response_text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    feedback JSONB,
    strengths TEXT[],
    improvements TEXT[],
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Mock Interview Analyses (final session analysis)
CREATE TABLE IF NOT EXISTS mock_interview_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE REFERENCES mock_interview_sessions(id) ON DELETE CASCADE,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    competency_scores JSONB,
    key_strengths TEXT[],
    areas_for_improvement TEXT[],
    recommendations TEXT[],
    detailed_feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_mock_sessions_user_id ON mock_interview_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_mock_sessions_created_at ON mock_interview_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mock_questions_session_id ON mock_interview_questions(session_id);
CREATE INDEX IF NOT EXISTS idx_mock_responses_session_id ON mock_interview_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_mock_responses_question_id ON mock_interview_responses(question_id);

-- Enable RLS on all tables
ALTER TABLE mock_interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_interview_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_interview_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_interview_analyses ENABLE ROW LEVEL SECURITY;

-- RLS Policies for mock_interview_sessions
CREATE POLICY "Users can view own sessions" ON mock_interview_sessions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own sessions" ON mock_interview_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own sessions" ON mock_interview_sessions
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own sessions" ON mock_interview_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for mock_interview_questions (via session ownership)
CREATE POLICY "Users can view own questions" ON mock_interview_questions
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can insert own questions" ON mock_interview_questions
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can update own questions" ON mock_interview_questions
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can delete own questions" ON mock_interview_questions
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );

-- RLS Policies for mock_interview_responses (via session ownership)
CREATE POLICY "Users can view own responses" ON mock_interview_responses
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can insert own responses" ON mock_interview_responses
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can update own responses" ON mock_interview_responses
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can delete own responses" ON mock_interview_responses
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );

-- RLS Policies for mock_interview_analyses (via session ownership)
CREATE POLICY "Users can view own analyses" ON mock_interview_analyses
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can insert own analyses" ON mock_interview_analyses
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can update own analyses" ON mock_interview_analyses
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );
CREATE POLICY "Users can delete own analyses" ON mock_interview_analyses
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM mock_interview_sessions WHERE id = session_id AND user_id = auth.uid())
    );

-- Service role bypass policy (for backend using service key)
-- The backend uses the service key which bypasses RLS by default

-- Auto-update updated_at for sessions
CREATE OR REPLACE FUNCTION update_mock_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_mock_sessions_updated_at ON mock_interview_sessions;
CREATE TRIGGER trigger_mock_sessions_updated_at
    BEFORE UPDATE ON mock_interview_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_mock_sessions_updated_at();
