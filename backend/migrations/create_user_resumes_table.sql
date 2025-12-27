-- Migration: Create user_resumes table for multi-resume support
-- Run this in Supabase SQL Editor

-- Create the user_resumes table
CREATE TABLE IF NOT EXISTS user_resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_name TEXT NOT NULL,
    resume_json JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    accuracy_confirmed BOOLEAN DEFAULT false,
    linkedin_verified BOOLEAN DEFAULT NULL,
    verification_notes JSONB DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_resumes_user_id ON user_resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_resumes_default ON user_resumes(user_id, is_default);

-- Enable Row Level Security
ALTER TABLE user_resumes ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own resumes
CREATE POLICY "Users can view own resumes" ON user_resumes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own resumes" ON user_resumes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own resumes" ON user_resumes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own resumes" ON user_resumes
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_resumes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_user_resumes_updated_at ON user_resumes;
CREATE TRIGGER trigger_user_resumes_updated_at
    BEFORE UPDATE ON user_resumes
    FOR EACH ROW EXECUTE FUNCTION update_user_resumes_updated_at();

-- Function to ensure only one default resume per user
CREATE OR REPLACE FUNCTION ensure_single_default_resume()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = true THEN
        UPDATE user_resumes
        SET is_default = false
        WHERE user_id = NEW.user_id
        AND id != NEW.id
        AND is_default = true;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce single default
DROP TRIGGER IF EXISTS trigger_single_default_resume ON user_resumes;
CREATE TRIGGER trigger_single_default_resume
    BEFORE INSERT OR UPDATE ON user_resumes
    FOR EACH ROW EXECUTE FUNCTION ensure_single_default_resume();

-- Add constraint to limit resumes per user (5 max)
-- Note: This is enforced at application level, but we add a comment for documentation
COMMENT ON TABLE user_resumes IS 'User resumes with 5 max limit enforced at application level';
