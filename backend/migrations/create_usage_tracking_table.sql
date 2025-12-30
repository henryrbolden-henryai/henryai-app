-- Migration: Create usage_tracking table for tier usage limits
-- Run this in Supabase SQL Editor

-- Create the usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,

    -- Usage counters
    applications_used INTEGER DEFAULT 0,
    resumes_generated INTEGER DEFAULT 0,
    cover_letters_generated INTEGER DEFAULT 0,
    henry_conversations_used INTEGER DEFAULT 0,
    mock_interviews_used INTEGER DEFAULT 0,
    coaching_sessions_used INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one record per user per billing period
    CONSTRAINT unique_user_period UNIQUE (user_id, period_start)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_period ON usage_tracking(user_id, period_start);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_period_end ON usage_tracking(period_end);

-- Enable Row Level Security
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own usage
CREATE POLICY "Users can view own usage" ON usage_tracking
    FOR SELECT USING (auth.uid() = user_id);

-- RLS Policy: Users can insert their own usage (for creating new periods)
CREATE POLICY "Users can insert own usage" ON usage_tracking
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can update their own usage
CREATE POLICY "Users can update own usage" ON usage_tracking
    FOR UPDATE USING (auth.uid() = user_id);

-- Service role can manage all usage records (for admin operations)
CREATE POLICY "Service role can manage all usage" ON usage_tracking
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_usage_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_usage_tracking_updated_at ON usage_tracking;
CREATE TRIGGER trigger_usage_tracking_updated_at
    BEFORE UPDATE ON usage_tracking
    FOR EACH ROW EXECUTE FUNCTION update_usage_tracking_updated_at();

-- Function to get or create current period usage for a user
CREATE OR REPLACE FUNCTION get_or_create_current_usage(p_user_id UUID)
RETURNS usage_tracking AS $$
DECLARE
    v_period_start TIMESTAMPTZ;
    v_period_end TIMESTAMPTZ;
    v_usage usage_tracking;
BEGIN
    -- Calculate current period (first of current month to first of next month)
    v_period_start := date_trunc('month', NOW());
    v_period_end := date_trunc('month', NOW() + INTERVAL '1 month');

    -- Try to get existing record
    SELECT * INTO v_usage
    FROM usage_tracking
    WHERE user_id = p_user_id AND period_start = v_period_start;

    -- Create if not exists
    IF v_usage IS NULL THEN
        INSERT INTO usage_tracking (user_id, period_start, period_end)
        VALUES (p_user_id, v_period_start, v_period_end)
        RETURNING * INTO v_usage;
    END IF;

    RETURN v_usage;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment a usage counter
CREATE OR REPLACE FUNCTION increment_usage(p_user_id UUID, p_usage_type TEXT)
RETURNS usage_tracking AS $$
DECLARE
    v_usage usage_tracking;
BEGIN
    -- Get or create current period usage
    v_usage := get_or_create_current_usage(p_user_id);

    -- Increment the appropriate counter
    CASE p_usage_type
        WHEN 'applications' THEN
            UPDATE usage_tracking SET applications_used = applications_used + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        WHEN 'resumes' THEN
            UPDATE usage_tracking SET resumes_generated = resumes_generated + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        WHEN 'cover_letters' THEN
            UPDATE usage_tracking SET cover_letters_generated = cover_letters_generated + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        WHEN 'henry_conversations' THEN
            UPDATE usage_tracking SET henry_conversations_used = henry_conversations_used + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        WHEN 'mock_interviews' THEN
            UPDATE usage_tracking SET mock_interviews_used = mock_interviews_used + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        WHEN 'coaching_sessions' THEN
            UPDATE usage_tracking SET coaching_sessions_used = coaching_sessions_used + 1 WHERE id = v_usage.id RETURNING * INTO v_usage;
        ELSE
            RAISE EXCEPTION 'Unknown usage type: %', p_usage_type;
    END CASE;

    RETURN v_usage;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comment for documentation
COMMENT ON TABLE usage_tracking IS 'Tracks monthly usage of tier-limited features for each user';
