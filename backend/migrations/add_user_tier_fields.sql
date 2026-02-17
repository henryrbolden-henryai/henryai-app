-- Migration: Add tier-related fields to users (via user_profiles table)
-- Run this in Supabase SQL Editor

-- Create user_profiles table for extended user data
-- Note: auth.users is managed by Supabase, so we create a separate profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Tier subscription fields
    tier TEXT DEFAULT 'sourcer' CHECK (tier IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach')),
    tier_started_at TIMESTAMPTZ DEFAULT NULL,

    -- Stripe integration fields
    stripe_customer_id TEXT DEFAULT NULL,
    stripe_subscription_id TEXT DEFAULT NULL,

    -- Beta user fields
    is_beta_user BOOLEAN DEFAULT false,
    beta_tier_override TEXT DEFAULT NULL CHECK (beta_tier_override IS NULL OR beta_tier_override IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach')),
    beta_expires_at TIMESTAMPTZ DEFAULT NULL,
    beta_discount_percent INTEGER DEFAULT 0 CHECK (beta_discount_percent >= 0 AND beta_discount_percent <= 100),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_tier ON user_profiles(tier);
CREATE INDEX IF NOT EXISTS idx_user_profiles_stripe_customer ON user_profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_beta ON user_profiles(is_beta_user) WHERE is_beta_user = true;

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

-- RLS Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policy: Users can update their own profile
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Service role can manage all profiles (for admin/webhook operations)
CREATE POLICY "Service role can manage all profiles" ON user_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER trigger_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_user_profiles_updated_at();

-- Function to automatically create profile when user signs up
CREATE OR REPLACE FUNCTION create_user_profile_on_signup()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
DROP TRIGGER IF EXISTS trigger_create_user_profile ON auth.users;
CREATE TRIGGER trigger_create_user_profile
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION create_user_profile_on_signup();

-- Add comment for documentation
COMMENT ON TABLE user_profiles IS 'Extended user profile data including subscription tier and beta user status';
