-- Migration: Create user_settings table for Strategic Control system
-- Run this in Supabase SQL Editor

-- Create the user_settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Strategy configuration (Career Strategy section)
    strategy_config JSONB DEFAULT '{}'::jsonb,

    -- Automation configuration (Application Engine section)
    automation_config JSONB DEFAULT '{}'::jsonb,

    -- Notification configuration
    notification_config JSONB DEFAULT '{}'::jsonb,

    -- Privacy configuration
    privacy_config JSONB DEFAULT '{}'::jsonb,

    -- Strategy Health (computed, cached)
    strategy_health_score FLOAT DEFAULT 0,
    strategy_health_components JSONB DEFAULT '{}'::jsonb,

    -- Optimal defaults calculation
    optimal_defaults JSONB DEFAULT '{}'::jsonb,
    optimal_profile_hash TEXT,
    last_optimal_calculation TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_settings UNIQUE(user_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_settings_strategy_health ON user_settings(strategy_health_score);
CREATE INDEX IF NOT EXISTS idx_user_settings_updated_at ON user_settings(updated_at);

-- Enable Row Level Security
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own settings
CREATE POLICY "Users can view own settings" ON user_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON user_settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own settings" ON user_settings
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_user_settings_updated_at ON user_settings;
CREATE TRIGGER trigger_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_user_settings_updated_at();

-- Documentation
COMMENT ON TABLE user_settings IS 'User strategic control settings with JSONB configs for strategy, automation, notifications, and privacy';
COMMENT ON COLUMN user_settings.strategy_config IS 'Career strategy settings: strategy_mode, fit_score_threshold, target_roles, industry_focus, location_strategy';
COMMENT ON COLUMN user_settings.automation_config IS 'Application engine settings: application_velocity, document_generation, follow_up_timing_days, max_applications_per_week';
COMMENT ON COLUMN user_settings.notification_config IS 'Notification preferences: email_notifications, dashboard_alerts, weekly_digest, interview_prep_reminders, alert_types';
COMMENT ON COLUMN user_settings.privacy_config IS 'Privacy settings: data_sharing, analytics_opt_in, visible_to_employers';
COMMENT ON COLUMN user_settings.strategy_health_score IS 'Cached strategy health score 0-100, recalculated on demand and nightly';
COMMENT ON COLUMN user_settings.strategy_health_components IS 'Breakdown of 5 health components: fit_alignment, application_velocity, interview_yield, outreach_consistency, profile_strength';
COMMENT ON COLUMN user_settings.optimal_defaults IS 'Cached optimal default values computed from user history';
COMMENT ON COLUMN user_settings.optimal_profile_hash IS 'Hash of input data used for last optimal calculation, for change detection';
