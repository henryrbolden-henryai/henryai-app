-- ============================================================================
-- Migration: Create user_profiles table + Add Stripe subscription fields
-- Run this in Supabase SQL Editor
--
-- This is a combined, idempotent migration that:
-- 1. Creates user_profiles table if it doesn't exist
-- 2. Updates tier CHECK constraints to include 'preview'
-- 3. Adds Stripe subscription columns (subscription_status, current_period_end)
-- 4. Sets up RLS policies and triggers
--
-- Safe to run multiple times — uses IF NOT EXISTS / IF EXISTS throughout.
-- ============================================================================

-- ============================================================================
-- STEP 1: Create user_profiles table (if it doesn't exist)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Tier subscription fields
    tier TEXT DEFAULT 'sourcer' CHECK (tier IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach')),
    tier_started_at TIMESTAMPTZ DEFAULT NULL,

    -- Stripe integration fields
    stripe_customer_id TEXT DEFAULT NULL,
    stripe_subscription_id TEXT DEFAULT NULL,

    -- Stripe subscription status fields
    subscription_status TEXT DEFAULT NULL
        CHECK (subscription_status IS NULL OR subscription_status IN ('active', 'past_due', 'canceled', 'trialing')),
    current_period_end TIMESTAMPTZ DEFAULT NULL,

    -- Beta user fields
    is_beta_user BOOLEAN DEFAULT false,
    beta_tier_override TEXT DEFAULT NULL CHECK (beta_tier_override IS NULL OR beta_tier_override IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach')),
    beta_expires_at TIMESTAMPTZ DEFAULT NULL,
    beta_discount_percent INTEGER DEFAULT 0 CHECK (beta_discount_percent >= 0 AND beta_discount_percent <= 100),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- STEP 2: If the table already existed, add missing columns & fix constraints
-- ============================================================================

-- Add subscription_status column (may already exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'subscription_status'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN subscription_status TEXT DEFAULT NULL;
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_subscription_status_check
            CHECK (subscription_status IS NULL OR subscription_status IN ('active', 'past_due', 'canceled', 'trialing'));
    END IF;
END $$;

-- Add current_period_end column (may already exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user_profiles' AND column_name = 'current_period_end'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN current_period_end TIMESTAMPTZ DEFAULT NULL;
    END IF;
END $$;

-- Update tier CHECK constraint to include 'preview' (drop old, add new)
-- This handles the case where the table was created with the old constraint
DO $$
BEGIN
    -- Drop the old tier constraint if it exists (name varies by Postgres version)
    -- Try the common auto-generated name first
    BEGIN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_tier_check;
    EXCEPTION WHEN undefined_object THEN NULL;
    END;

    -- Re-add with 'preview' included
    BEGIN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_tier_check
            CHECK (tier IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach'));
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;

    -- Same for beta_tier_override
    BEGIN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_beta_tier_override_check;
    EXCEPTION WHEN undefined_object THEN NULL;
    END;

    BEGIN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_beta_tier_override_check
            CHECK (beta_tier_override IS NULL OR beta_tier_override IN ('preview', 'sourcer', 'recruiter', 'principal', 'partner', 'coach'));
    EXCEPTION WHEN duplicate_object THEN NULL;
    END;
END $$;

-- ============================================================================
-- STEP 3: Indexes
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_user_profiles_tier ON user_profiles(tier);
CREATE INDEX IF NOT EXISTS idx_user_profiles_stripe_customer ON user_profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_beta ON user_profiles(is_beta_user) WHERE is_beta_user = true;
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_status ON user_profiles(subscription_status) WHERE subscription_status IS NOT NULL;

-- ============================================================================
-- STEP 4: Row Level Security
-- ============================================================================
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies first (bare statements, not inside DO block)
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON user_profiles;

-- Recreate them
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Service role can manage all profiles" ON user_profiles FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- STEP 5: Triggers
-- ============================================================================

-- Auto-update updated_at on row change
CREATE OR REPLACE FUNCTION update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER trigger_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_user_profiles_updated_at();

-- Auto-create user_profiles row when a new user signs up
CREATE OR REPLACE FUNCTION create_user_profile_on_signup()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id)
    VALUES (NEW.id)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trigger_create_user_profile ON auth.users;
CREATE TRIGGER trigger_create_user_profile
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION create_user_profile_on_signup();

-- ============================================================================
-- DONE
-- ============================================================================
COMMENT ON TABLE user_profiles IS 'Extended user profile data including subscription tier, Stripe billing, and beta user status';
