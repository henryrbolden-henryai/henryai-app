-- Migration: Create api_usage_tracking table for tracking Claude API token usage and costs
-- Run this in Supabase SQL Editor

-- Create the api_usage_tracking table
CREATE TABLE IF NOT EXISTS api_usage_tracking (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Request metadata
    feature_type TEXT NOT NULL,  -- e.g., 'resume_generation', 'cover_letter', 'jd_analysis', 'mock_interview', 'henry_chat'
    model TEXT NOT NULL,  -- e.g., 'claude-sonnet-4-20250514'

    -- Token usage
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,

    -- Cost calculation (in USD, stored as cents to avoid float precision issues)
    cost_cents INTEGER NOT NULL DEFAULT 0,

    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Optional context
    request_id TEXT,  -- Optional unique request identifier
    metadata JSONB DEFAULT '{}'::jsonb  -- Additional context (e.g., job_id, resume_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage_tracking(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_feature_type ON api_usage_tracking(feature_type);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_created ON api_usage_tracking(user_id, created_at);

-- Enable Row Level Security
ALTER TABLE api_usage_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own usage
CREATE POLICY "Users can view own api usage" ON api_usage_tracking
    FOR SELECT USING (auth.uid() = user_id);

-- RLS Policy: Service role can manage all records (for backend operations)
CREATE POLICY "Service role can manage all api usage" ON api_usage_tracking
    FOR ALL USING (auth.role() = 'service_role');

-- Aggregated view for monthly summaries
CREATE OR REPLACE VIEW api_usage_monthly_summary AS
SELECT
    user_id,
    date_trunc('month', created_at) AS month,
    feature_type,
    COUNT(*) AS request_count,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    SUM(input_tokens + output_tokens) AS total_tokens,
    SUM(cost_cents) AS total_cost_cents
FROM api_usage_tracking
GROUP BY user_id, date_trunc('month', created_at), feature_type;

-- Function to get user's total API usage for current month
CREATE OR REPLACE FUNCTION get_current_month_api_usage(p_user_id UUID)
RETURNS TABLE (
    total_requests BIGINT,
    total_input_tokens BIGINT,
    total_output_tokens BIGINT,
    total_tokens BIGINT,
    total_cost_cents BIGINT,
    by_feature JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH monthly_data AS (
        SELECT
            COUNT(*) as requests,
            COALESCE(SUM(input_tokens), 0) as inp_tokens,
            COALESCE(SUM(output_tokens), 0) as out_tokens,
            COALESCE(SUM(cost_cents), 0) as cost
        FROM api_usage_tracking
        WHERE user_id = p_user_id
        AND created_at >= date_trunc('month', NOW())
    ),
    feature_breakdown AS (
        SELECT jsonb_object_agg(
            feature_type,
            jsonb_build_object(
                'requests', requests,
                'input_tokens', inp_tokens,
                'output_tokens', out_tokens,
                'cost_cents', cost
            )
        ) as breakdown
        FROM (
            SELECT
                feature_type,
                COUNT(*) as requests,
                COALESCE(SUM(input_tokens), 0) as inp_tokens,
                COALESCE(SUM(output_tokens), 0) as out_tokens,
                COALESCE(SUM(cost_cents), 0) as cost
            FROM api_usage_tracking
            WHERE user_id = p_user_id
            AND created_at >= date_trunc('month', NOW())
            GROUP BY feature_type
        ) sub
    )
    SELECT
        m.requests,
        m.inp_tokens,
        m.out_tokens,
        m.inp_tokens + m.out_tokens,
        m.cost,
        COALESCE(f.breakdown, '{}'::jsonb)
    FROM monthly_data m, feature_breakdown f;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comment for documentation
COMMENT ON TABLE api_usage_tracking IS 'Tracks individual Claude API calls with token usage and costs per user';
