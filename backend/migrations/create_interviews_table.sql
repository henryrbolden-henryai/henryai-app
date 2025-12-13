-- Create interviews table for storing interview data
CREATE TABLE IF NOT EXISTS interviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    interview_type TEXT, -- 'Recruiter Screen', 'Hiring Manager', 'Technical', 'Panel', etc.
    interview_date DATE,
    interview_time TEXT,
    location TEXT, -- 'Virtual', 'On-site', or address
    interviewer_name TEXT,
    interviewer_title TEXT,
    interviewer_linkedin TEXT,
    notes TEXT,
    prep_notes JSONB DEFAULT '{}', -- Prep guide notes
    debrief_notes JSONB DEFAULT '{}', -- Post-interview debrief
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(interview_date);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews(application_id);

-- Enable RLS
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- RLS Policies - users can only access their own interviews
CREATE POLICY "Users can view own interviews" ON interviews
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own interviews" ON interviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own interviews" ON interviews
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own interviews" ON interviews
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_interviews_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS trigger_interviews_updated_at ON interviews;
CREATE TRIGGER trigger_interviews_updated_at
    BEFORE UPDATE ON interviews
    FOR EACH ROW
    EXECUTE FUNCTION update_interviews_updated_at();
