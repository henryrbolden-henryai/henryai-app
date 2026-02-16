-- Migration: Add job alignment fields to candidate_profiles
-- Improves job discovery accuracy by storing explicit target roles,
-- employment type preferences, and seniority preference.
-- Run this in Supabase SQL Editor
-- Date: 2026-02-16

-- ============================================================================
-- STEP 1: Add target_roles (explicit job titles the candidate is targeting)
-- This is the single most important field for job search query construction.
-- Pre-populated from resume parse, editable by user in onboarding.
-- ============================================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'target_roles') THEN
        ALTER TABLE candidate_profiles ADD COLUMN target_roles JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.target_roles IS 'Explicit target job titles (e.g., ["Senior Product Manager", "Director of Product"]). Pre-filled from resume parse, editable by user. Max 5.';

-- ============================================================================
-- STEP 2: Add employment_type_preferences
-- Maps directly to JSearch employment_types filter (FULLTIME, CONTRACT, etc.)
-- ============================================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'employment_type_preferences') THEN
        ALTER TABLE candidate_profiles ADD COLUMN employment_type_preferences JSONB DEFAULT '["FULLTIME"]'::jsonb;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.employment_type_preferences IS 'Preferred employment types: FULLTIME, CONTRACT, PARTTIME, INTERN. Default: ["FULLTIME"].';

-- ============================================================================
-- STEP 3: Add seniority_preference
-- Used to filter job results by level alignment.
-- ============================================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'seniority_preference') THEN
        ALTER TABLE candidate_profiles ADD COLUMN seniority_preference TEXT CHECK (seniority_preference IS NULL OR seniority_preference IN (
            'entry', 'mid', 'senior', 'staff', 'director', 'vp', 'executive'
        ));
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.seniority_preference IS 'Target seniority level for job search. Inferred from resume leveling + move_type, editable by user.';

SELECT 'Job alignment fields migration completed successfully!' as status;
