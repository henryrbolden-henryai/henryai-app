-- Interview Debriefs Intelligence Tables
-- Run this in Supabase SQL Editor
-- Spec: INTERVIEW_DEBRIEF_INTELLIGENCE_SPEC_v1.0

-- ============================================
-- TABLE: interview_debriefs
-- Stores structured debrief data extracted from Hey Henry conversations
-- ============================================

CREATE TABLE IF NOT EXISTS interview_debriefs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    application_id UUID, -- Optional reference to tracked application

    -- Interview metadata
    company TEXT NOT NULL,
    role TEXT,
    interview_type TEXT NOT NULL, -- 'recruiter', 'hiring_manager', 'technical', 'panel', 'final'
    interview_date DATE,
    interviewer_name TEXT,
    duration_minutes INTEGER,

    -- Self-ratings (1-5)
    rating_overall INTEGER CHECK (rating_overall BETWEEN 1 AND 5),
    rating_confidence INTEGER CHECK (rating_confidence BETWEEN 1 AND 5),
    rating_preparation INTEGER CHECK (rating_preparation BETWEEN 1 AND 5),

    -- Structured content (JSONB)
    -- questions_asked: [{"question": "...", "category": "behavioral|technical|motivation"}]
    questions_asked JSONB DEFAULT '[]'::jsonb,
    -- question_categories: ["behavioral", "technical", "motivation", "culture", "experience"]
    question_categories JSONB DEFAULT '[]'::jsonb,
    -- stumbles: [{"question": "...", "what_went_wrong": "..."}]
    stumbles JSONB DEFAULT '[]'::jsonb,
    -- wins: [{"moment": "...", "why_it_worked": "..."}]
    wins JSONB DEFAULT '[]'::jsonb,
    -- stories_used: [{"name": "...", "context": "...", "effectiveness": 1-5}]
    stories_used JSONB DEFAULT '[]'::jsonb,
    -- interviewer_signals: {"engaged": true/false, "red_flags": [], "next_steps_mentioned": true/false}
    interviewer_signals JSONB DEFAULT '{}'::jsonb,

    -- AI-generated insights
    key_insights JSONB DEFAULT '[]'::jsonb,
    improvement_areas JSONB DEFAULT '[]'::jsonb,

    -- Raw conversation data (for reprocessing if needed)
    raw_conversation TEXT,

    -- Outcome tracking (updated when application status changes)
    outcome TEXT CHECK (outcome IN ('advanced', 'rejected', 'pending', 'ghosted', NULL)),
    outcome_updated_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_debriefs_user_id ON interview_debriefs(user_id);
CREATE INDEX IF NOT EXISTS idx_debriefs_company ON interview_debriefs(company);
CREATE INDEX IF NOT EXISTS idx_debriefs_interview_type ON interview_debriefs(interview_type);
CREATE INDEX IF NOT EXISTS idx_debriefs_application_id ON interview_debriefs(application_id);
CREATE INDEX IF NOT EXISTS idx_debriefs_interview_date ON interview_debriefs(interview_date DESC);
CREATE INDEX IF NOT EXISTS idx_debriefs_created_at ON interview_debriefs(created_at DESC);

-- Enable Row Level Security
ALTER TABLE interview_debriefs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own debriefs" ON interview_debriefs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own debriefs" ON interview_debriefs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own debriefs" ON interview_debriefs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own debriefs" ON interview_debriefs
    FOR DELETE USING (auth.uid() = user_id);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_interview_debriefs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS interview_debriefs_updated_at ON interview_debriefs;
CREATE TRIGGER interview_debriefs_updated_at
    BEFORE UPDATE ON interview_debriefs
    FOR EACH ROW
    EXECUTE FUNCTION update_interview_debriefs_updated_at();


-- ============================================
-- TABLE: user_story_bank
-- Tracks stories/examples users have used across interviews
-- ============================================

CREATE TABLE IF NOT EXISTS user_story_bank (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Story content
    story_name TEXT NOT NULL,
    story_summary TEXT,
    story_context TEXT, -- When to use this story

    -- Categorization
    -- demonstrates: ['leadership', 'problem_solving', 'cross_functional', 'technical', 'conflict_resolution']
    demonstrates TEXT[] DEFAULT '{}',
    -- best_for_questions: ['tell me about a time', 'conflict resolution', 'leadership example']
    best_for_questions TEXT[] DEFAULT '{}',

    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    effectiveness_avg DECIMAL(3,2), -- Average effectiveness rating (1-5)
    -- interviews_used_in: Array of debrief IDs where this story was used
    interviews_used_in UUID[] DEFAULT '{}',

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'overused', 'retired')),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_stories_user_id ON user_story_bank(user_id);
CREATE INDEX IF NOT EXISTS idx_stories_status ON user_story_bank(status);
CREATE INDEX IF NOT EXISTS idx_stories_times_used ON user_story_bank(times_used DESC);

-- Enable Row Level Security
ALTER TABLE user_story_bank ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own stories" ON user_story_bank
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own stories" ON user_story_bank
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own stories" ON user_story_bank
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own stories" ON user_story_bank
    FOR DELETE USING (auth.uid() = user_id);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_story_bank_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_story_bank_updated_at ON user_story_bank;
CREATE TRIGGER user_story_bank_updated_at
    BEFORE UPDATE ON user_story_bank
    FOR EACH ROW
    EXECUTE FUNCTION update_user_story_bank_updated_at();

-- Auto-mark stories as overused when times_used >= 3
CREATE OR REPLACE FUNCTION check_story_overuse()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.times_used >= 3 AND NEW.status = 'active' THEN
        NEW.status = 'overused';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS story_overuse_check ON user_story_bank;
CREATE TRIGGER story_overuse_check
    BEFORE UPDATE ON user_story_bank
    FOR EACH ROW
    EXECUTE FUNCTION check_story_overuse();
