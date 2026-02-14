-- Migration: Add job discovery and network matching fields to candidate_profiles
-- Run this in Supabase SQL Editor
-- Date: 2026-02-14

-- ============================================================================
-- STEP 1: Add job discovery fields to candidate_profiles
-- ============================================================================

-- Optional search keywords (supplements target_roles from resume)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'job_search_keywords') THEN
        ALTER TABLE candidate_profiles ADD COLUMN job_search_keywords JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.job_search_keywords IS 'Optional additional keywords for job discovery (e.g., ["fintech", "B2B SaaS", "API"]). Supplements target_roles from resume.';

-- Companies to exclude from job results
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'excluded_companies') THEN
        ALTER TABLE candidate_profiles ADD COLUMN excluded_companies JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.excluded_companies IS 'Companies to exclude from job discovery results (e.g., former employers, companies with bad experience).';

-- ============================================================================
-- STEP 2: Add LinkedIn network fields
-- ============================================================================

-- Companies from LinkedIn connections CSV upload
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'linkedin_network_companies') THEN
        ALTER TABLE candidate_profiles ADD COLUMN linkedin_network_companies JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.linkedin_network_companies IS 'Companies where candidate has LinkedIn connections. Array of {"company": "Stripe", "count": 3}. From CSV upload.';

-- Track when LinkedIn connections were last uploaded
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'linkedin_connections_uploaded_at') THEN
        ALTER TABLE candidate_profiles ADD COLUMN linkedin_connections_uploaded_at TIMESTAMPTZ;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.linkedin_connections_uploaded_at IS 'When LinkedIn connections CSV was last uploaded for network matching.';

-- Total connections count
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'linkedin_connections_count') THEN
        ALTER TABLE candidate_profiles ADD COLUMN linkedin_connections_count INTEGER DEFAULT 0;
    END IF;
END $$;

COMMENT ON COLUMN candidate_profiles.linkedin_connections_count IS 'Total number of LinkedIn connections parsed from CSV upload.';

-- ============================================================================
-- STEP 3: Add job discovery cache table
-- Caches job search results per user to minimize API calls
-- ============================================================================

CREATE TABLE IF NOT EXISTS job_discovery_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cache_key TEXT NOT NULL,
    search_query TEXT NOT NULL,
    results JSONB NOT NULL DEFAULT '[]'::jsonb,
    total_found INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '24 hours'),

    UNIQUE(user_id, cache_key)
);

CREATE INDEX IF NOT EXISTS idx_job_discovery_cache_user ON job_discovery_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_job_discovery_cache_expires ON job_discovery_cache(expires_at);

-- Enable RLS
ALTER TABLE job_discovery_cache ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "Users can view own job cache" ON job_discovery_cache;
DROP POLICY IF EXISTS "Users can insert own job cache" ON job_discovery_cache;
DROP POLICY IF EXISTS "Users can update own job cache" ON job_discovery_cache;
DROP POLICY IF EXISTS "Users can delete own job cache" ON job_discovery_cache;
DROP POLICY IF EXISTS "Service role can manage all job cache" ON job_discovery_cache;

CREATE POLICY "Users can view own job cache" ON job_discovery_cache FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own job cache" ON job_discovery_cache FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own job cache" ON job_discovery_cache FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own job cache" ON job_discovery_cache FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can manage all job cache" ON job_discovery_cache FOR ALL USING (auth.role() = 'service_role');

COMMENT ON TABLE job_discovery_cache IS 'Caches job discovery API results per user. 24-hour TTL to minimize external API calls.';

SELECT 'Job discovery migration completed successfully!' as status;
