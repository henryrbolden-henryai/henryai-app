-- Migration: Add enhanced candidate profile fields for B2B matching
-- Run this in Supabase SQL Editor
-- Date: 2025-01-05

-- Create candidate_profiles table if it doesn't exist
-- This table extends user_profiles with job-search-specific data
CREATE TABLE IF NOT EXISTS candidate_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Basic Info
    first_name TEXT,
    last_name TEXT,

    -- Pronouns
    pronouns TEXT,

    -- Professional Info
    function_area TEXT CHECK (function_area IS NULL OR function_area IN (
        'product_management', 'engineering', 'design', 'data_analytics',
        'sales', 'marketing', 'customer_success', 'operations',
        'finance', 'hr_people', 'legal', 'other'
    )),

    -- Current Industry
    current_industry TEXT CHECK (current_industry IS NULL OR current_industry IN (
        'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
        'manufacturing', 'energy', 'real_estate', 'education', 'government',
        'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
    )),
    secondary_industry TEXT CHECK (secondary_industry IS NULL OR secondary_industry IN (
        'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
        'manufacturing', 'energy', 'real_estate', 'education', 'government',
        'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
    )),

    -- Work Authorization
    work_authorization TEXT CHECK (work_authorization IS NULL OR work_authorization IN (
        'us_citizen', 'green_card', 'h1b', 'h1b_transfer', 'l1',
        'opt', 'opt_stem', 'tn', 'other_visa'
    )),
    requires_sponsorship BOOLEAN DEFAULT false,

    -- Veteran Status
    is_veteran BOOLEAN DEFAULT false,

    -- Location (structured)
    city TEXT,
    state TEXT,
    country TEXT,

    -- Work Preferences (JSON for flexibility)
    work_arrangement JSONB DEFAULT '[]'::jsonb,  -- Array of: remote, hybrid, onsite
    open_to_relocate TEXT CHECK (open_to_relocate IS NULL OR open_to_relocate IN ('yes', 'maybe', 'no')),
    relocation_targets JSONB DEFAULT '[]'::jsonb,  -- Array of cities/regions

    -- Compensation (stored as integers, cents)
    comp_min INTEGER,
    comp_target INTEGER,
    comp_stretch INTEGER,

    -- Target Industries (what they're looking for)
    target_industry_primary TEXT CHECK (target_industry_primary IS NULL OR target_industry_primary IN (
        'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
        'manufacturing', 'energy', 'real_estate', 'education', 'government',
        'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
    )),
    target_industry_secondary TEXT CHECK (target_industry_secondary IS NULL OR target_industry_secondary IN (
        'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
        'manufacturing', 'energy', 'real_estate', 'education', 'government',
        'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
    )),

    -- Job Search Situation
    situation_holding_up TEXT CHECK (situation_holding_up IS NULL OR situation_holding_up IN (
        'doing_well', 'stressed_but_managing', 'struggling', 'rather_not_say'
    )),
    situation_timeline TEXT CHECK (situation_timeline IS NULL OR situation_timeline IN (
        'no_rush', 'actively_looking', 'soon', 'urgent'
    )),
    situation_confidence TEXT CHECK (situation_confidence IS NULL OR situation_confidence IN (
        'strong', 'shaky', 'low', 'need_validation'
    )),

    -- B2B Marketplace fields (future use)
    visible_to_employers BOOLEAN DEFAULT false,
    actively_seeking BOOLEAN DEFAULT false,
    available_date DATE,

    -- Computed/cached fields for faster querying
    years_experience INTEGER,  -- Cached from resume leveling
    current_level_id TEXT,     -- Cached from resume leveling

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_function ON candidate_profiles(function_area);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_industry ON candidate_profiles(current_industry);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_location ON candidate_profiles(country, state, city);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_work_auth ON candidate_profiles(work_authorization);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_sponsorship ON candidate_profiles(requires_sponsorship) WHERE requires_sponsorship = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_veteran ON candidate_profiles(is_veteran) WHERE is_veteran = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_visible ON candidate_profiles(visible_to_employers) WHERE visible_to_employers = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_seeking ON candidate_profiles(actively_seeking) WHERE actively_seeking = true;

-- Enable Row Level Security
ALTER TABLE candidate_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own profile
CREATE POLICY "Users can view own candidate profile" ON candidate_profiles
    FOR SELECT USING (auth.uid() = id);

-- RLS Policy: Users can insert their own profile
CREATE POLICY "Users can insert own candidate profile" ON candidate_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policy: Users can update their own profile
CREATE POLICY "Users can update own candidate profile" ON candidate_profiles
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policy: Users can delete their own profile
CREATE POLICY "Users can delete own candidate profile" ON candidate_profiles
    FOR DELETE USING (auth.uid() = id);

-- Service role can manage all profiles (for admin operations)
CREATE POLICY "Service role can manage all candidate profiles" ON candidate_profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_candidate_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS trigger_candidate_profiles_updated_at ON candidate_profiles;
CREATE TRIGGER trigger_candidate_profiles_updated_at
    BEFORE UPDATE ON candidate_profiles
    FOR EACH ROW EXECUTE FUNCTION update_candidate_profiles_updated_at();

-- Add comment for documentation
COMMENT ON TABLE candidate_profiles IS 'Job seeker profile data for job fit analysis and future B2B employer matching. Includes professional info, work preferences, and job search situation.';

-- Add comments for key columns
COMMENT ON COLUMN candidate_profiles.function_area IS 'Primary functional area (PM, Engineering, Sales, etc.)';
COMMENT ON COLUMN candidate_profiles.current_industry IS 'Current industry the candidate works in';
COMMENT ON COLUMN candidate_profiles.requires_sponsorship IS 'Whether candidate needs employer visa sponsorship';
COMMENT ON COLUMN candidate_profiles.is_veteran IS 'Whether candidate is a U.S. military veteran (for veteran-friendly employer filtering)';
COMMENT ON COLUMN candidate_profiles.visible_to_employers IS 'Whether candidate has opted-in to be visible in B2B employer search';
COMMENT ON COLUMN candidate_profiles.actively_seeking IS 'Whether candidate is actively looking for new opportunities';

-- ============================================================================
-- CANDIDATE COMPANIES TABLE
-- Tracks prior employers with pedigree tagging for B2B filtering
-- ============================================================================

CREATE TABLE IF NOT EXISTS candidate_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Company Info
    company_name TEXT NOT NULL,                    -- Original name from resume
    company_normalized TEXT,                       -- Normalized: "Google" not "Google LLC"
    company_domain TEXT,                           -- e.g., "google.com" for deduplication

    -- Pedigree Tags (array for multiple categories)
    pedigree_tags TEXT[] DEFAULT '{}',             -- e.g., ['faang', 'big_tech', 'public']

    -- Role Info
    title TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    duration_months INTEGER,                       -- Computed for easy querying

    -- Source tracking
    source TEXT DEFAULT 'resume' CHECK (source IN ('resume', 'linkedin', 'manual')),
    resume_id UUID REFERENCES user_resumes(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for company queries
CREATE INDEX IF NOT EXISTS idx_candidate_companies_user ON candidate_companies(user_id);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_normalized ON candidate_companies(company_normalized);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_pedigree ON candidate_companies USING GIN(pedigree_tags);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_current ON candidate_companies(user_id, is_current) WHERE is_current = true;

-- Enable RLS
ALTER TABLE candidate_companies ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own companies" ON candidate_companies
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own companies" ON candidate_companies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own companies" ON candidate_companies
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own companies" ON candidate_companies
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all companies" ON candidate_companies
    FOR ALL USING (auth.role() = 'service_role');

-- Updated_at trigger
DROP TRIGGER IF EXISTS trigger_candidate_companies_updated_at ON candidate_companies;
CREATE TRIGGER trigger_candidate_companies_updated_at
    BEFORE UPDATE ON candidate_companies
    FOR EACH ROW EXECUTE FUNCTION update_candidate_profiles_updated_at();

-- ============================================================================
-- COMPANY PEDIGREE LOOKUP TABLE
-- Maps company names to pedigree categories
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_pedigree_lookup (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Company identification
    company_normalized TEXT NOT NULL UNIQUE,       -- Normalized name (lowercase, trimmed)
    company_aliases TEXT[] DEFAULT '{}',           -- Alternative names: ["Google LLC", "Alphabet"]
    company_domain TEXT,                           -- e.g., "google.com"

    -- Pedigree classification
    pedigree_tags TEXT[] DEFAULT '{}',             -- Categories this company belongs to

    -- Metadata
    employee_count_estimate INTEGER,               -- For company size filtering
    is_public BOOLEAN DEFAULT false,
    founded_year INTEGER,
    headquarters_country TEXT,

    -- Admin tracking
    verified BOOLEAN DEFAULT false,                -- Admin-verified entry
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_company_pedigree_normalized ON company_pedigree_lookup(company_normalized);
CREATE INDEX IF NOT EXISTS idx_company_pedigree_tags ON company_pedigree_lookup USING GIN(pedigree_tags);
CREATE INDEX IF NOT EXISTS idx_company_pedigree_aliases ON company_pedigree_lookup USING GIN(company_aliases);

-- No RLS needed - this is a reference table, readable by all authenticated users
-- But only admins/service role can modify

-- ============================================================================
-- SEED DATA: Initial company pedigree mappings
-- ============================================================================

INSERT INTO company_pedigree_lookup (company_normalized, company_aliases, pedigree_tags, is_public) VALUES
-- FAANG / Big Tech
('google', ARRAY['alphabet', 'google llc', 'google inc'], ARRAY['faang', 'big_tech', 'public'], true),
('meta', ARRAY['facebook', 'meta platforms', 'facebook inc'], ARRAY['faang', 'big_tech', 'public'], true),
('amazon', ARRAY['amazon.com', 'amazon web services', 'aws'], ARRAY['faang', 'big_tech', 'public'], true),
('apple', ARRAY['apple inc', 'apple computer'], ARRAY['faang', 'big_tech', 'public'], true),
('netflix', ARRAY['netflix inc'], ARRAY['faang', 'big_tech', 'public'], true),
('microsoft', ARRAY['microsoft corp', 'msft'], ARRAY['big_tech', 'public'], true),

-- Other Big Tech
('salesforce', ARRAY['salesforce.com', 'sfdc'], ARRAY['big_tech', 'public', 'enterprise_saas'], true),
('adobe', ARRAY['adobe systems', 'adobe inc'], ARRAY['big_tech', 'public'], true),
('oracle', ARRAY['oracle corp'], ARRAY['big_tech', 'public', 'enterprise'], true),
('ibm', ARRAY['international business machines'], ARRAY['big_tech', 'public', 'enterprise'], true),
('cisco', ARRAY['cisco systems'], ARRAY['big_tech', 'public', 'enterprise'], true),
('intel', ARRAY['intel corp'], ARRAY['big_tech', 'public', 'hardware'], true),
('nvidia', ARRAY['nvidia corp'], ARRAY['big_tech', 'public', 'hardware', 'ai'], true),

-- Top Unicorns / High-Growth
('stripe', ARRAY['stripe inc'], ARRAY['unicorn', 'fintech', 'high_growth'], false),
('airbnb', ARRAY['airbnb inc'], ARRAY['unicorn', 'public', 'marketplace'], true),
('uber', ARRAY['uber technologies'], ARRAY['unicorn', 'public', 'marketplace'], true),
('doordash', ARRAY['doordash inc'], ARRAY['unicorn', 'public', 'marketplace'], true),
('coinbase', ARRAY['coinbase global'], ARRAY['unicorn', 'public', 'fintech', 'crypto'], true),
('databricks', ARRAY['databricks inc'], ARRAY['unicorn', 'data', 'ai', 'high_growth'], false),
('openai', ARRAY['open ai'], ARRAY['unicorn', 'ai', 'high_growth'], false),
('anthropic', ARRAY[], ARRAY['unicorn', 'ai', 'high_growth'], false),

-- MBB Consulting
('mckinsey', ARRAY['mckinsey & company', 'mckinsey and company'], ARRAY['mbb', 'consulting', 'top_tier'], false),
('bain', ARRAY['bain & company', 'bain and company'], ARRAY['mbb', 'consulting', 'top_tier'], false),
('bcg', ARRAY['boston consulting group'], ARRAY['mbb', 'consulting', 'top_tier'], false),

-- Big 4 Consulting/Accounting
('deloitte', ARRAY['deloitte consulting', 'deloitte llp'], ARRAY['big4', 'consulting'], false),
('pwc', ARRAY['pricewaterhousecoopers', 'price waterhouse coopers'], ARRAY['big4', 'consulting'], false),
('ey', ARRAY['ernst & young', 'ernst and young'], ARRAY['big4', 'consulting'], false),
('kpmg', ARRAY['kpmg llp'], ARRAY['big4', 'consulting'], false),

-- Top Finance
('goldman sachs', ARRAY['goldman sachs group', 'gs'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('morgan stanley', ARRAY['morgan stanley & co'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('jpmorgan', ARRAY['jp morgan', 'jpmorgan chase', 'j.p. morgan'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('blackstone', ARRAY['blackstone group'], ARRAY['pe', 'finance', 'public'], true),
('blackrock', ARRAY['blackrock inc'], ARRAY['asset_management', 'finance', 'public'], true),

-- Additional Big Tech
('linkedin', ARRAY['linkedin corp'], ARRAY['big_tech', 'public'], true),
('twitter', ARRAY['x corp', 'twitter inc'], ARRAY['big_tech', 'public'], true),
('snap', ARRAY['snapchat', 'snap inc'], ARRAY['big_tech', 'public'], true),
('pinterest', ARRAY['pinterest inc'], ARRAY['big_tech', 'public'], true),
('spotify', ARRAY['spotify ab', 'spotify technology'], ARRAY['big_tech', 'public', 'media'], true),
('shopify', ARRAY['shopify inc'], ARRAY['big_tech', 'public', 'ecommerce'], true),
('atlassian', ARRAY['atlassian corp'], ARRAY['big_tech', 'public', 'enterprise_saas'], true),
('workday', ARRAY['workday inc'], ARRAY['big_tech', 'public', 'enterprise_saas'], true),
('servicenow', ARRAY['servicenow inc'], ARRAY['big_tech', 'public', 'enterprise_saas'], true),
('snowflake', ARRAY['snowflake inc'], ARRAY['big_tech', 'public', 'data'], true),
('palantir', ARRAY['palantir technologies'], ARRAY['big_tech', 'public', 'data'], true),
('square', ARRAY['block inc', 'square inc'], ARRAY['big_tech', 'public', 'fintech'], true),
('paypal', ARRAY['paypal holdings'], ARRAY['big_tech', 'public', 'fintech'], true),

-- High-Growth Unicorns / Late-Stage Startups
('figma', ARRAY['figma inc'], ARRAY['unicorn', 'high_growth', 'design'], false),
('notion', ARRAY['notion labs'], ARRAY['unicorn', 'high_growth', 'productivity'], false),
('canva', ARRAY['canva pty'], ARRAY['unicorn', 'high_growth', 'design'], false),
('discord', ARRAY['discord inc'], ARRAY['unicorn', 'high_growth', 'social'], false),
('plaid', ARRAY['plaid inc'], ARRAY['unicorn', 'high_growth', 'fintech'], false),
('chime', ARRAY['chime financial'], ARRAY['unicorn', 'high_growth', 'fintech'], false),
('instacart', ARRAY['maplebear inc'], ARRAY['unicorn', 'high_growth', 'marketplace'], false),
('klarna', ARRAY['klarna bank'], ARRAY['unicorn', 'high_growth', 'fintech'], false),
('scale ai', ARRAY['scale ai inc'], ARRAY['unicorn', 'high_growth', 'ai'], false),
('airtable', ARRAY['formagic inc'], ARRAY['unicorn', 'high_growth', 'productivity'], false),
('ramp', ARRAY['ramp business'], ARRAY['unicorn', 'high_growth', 'fintech'], false),
('brex', ARRAY['brex inc'], ARRAY['unicorn', 'high_growth', 'fintech'], false),
('robinhood', ARRAY['robinhood markets'], ARRAY['unicorn', 'public', 'fintech'], true),
('affirm', ARRAY['affirm holdings'], ARRAY['unicorn', 'public', 'fintech'], true),

-- Healthcare / Life Sciences
('unitedhealth', ARRAY['unitedhealth group', 'uhg'], ARRAY['healthcare', 'public', 'fortune_500'], true),
('cvs health', ARRAY['cvs', 'cvs health corp'], ARRAY['healthcare', 'public', 'fortune_500'], true),
('johnson & johnson', ARRAY['j&j', 'jnj'], ARRAY['healthcare', 'pharma', 'public', 'fortune_500'], true),
('pfizer', ARRAY['pfizer inc'], ARRAY['healthcare', 'pharma', 'public', 'fortune_500'], true),
('abbvie', ARRAY['abbvie inc'], ARRAY['healthcare', 'pharma', 'public'], true),
('merck', ARRAY['merck & co'], ARRAY['healthcare', 'pharma', 'public', 'fortune_500'], true),
('moderna', ARRAY['moderna inc'], ARRAY['healthcare', 'biotech', 'public'], true),
('illumina', ARRAY['illumina inc'], ARRAY['healthcare', 'biotech', 'public'], true),

-- Additional Finance / Investment Banks
('bank of america', ARRAY['bofa', 'boa', 'bank of america corp'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('citigroup', ARRAY['citi', 'citibank'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('wells fargo', ARRAY['wells fargo & co'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('barclays', ARRAY['barclays plc'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('ubs', ARRAY['ubs group'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('credit suisse', ARRAY['cs'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('deutsche bank', ARRAY['db'], ARRAY['bulge_bracket', 'finance', 'public'], true),

-- Private Equity / VC
('kkr', ARRAY['kohlberg kravis roberts'], ARRAY['pe', 'finance'], false),
('carlyle', ARRAY['carlyle group'], ARRAY['pe', 'finance', 'public'], true),
('apollo', ARRAY['apollo global'], ARRAY['pe', 'finance', 'public'], true),
('tpg', ARRAY['tpg capital'], ARRAY['pe', 'finance', 'public'], true),
('sequoia', ARRAY['sequoia capital'], ARRAY['vc', 'finance'], false),
('andreessen horowitz', ARRAY['a16z'], ARRAY['vc', 'finance'], false),
('benchmark', ARRAY['benchmark capital'], ARRAY['vc', 'finance'], false),
('accel', ARRAY['accel partners'], ARRAY['vc', 'finance'], false),

-- Other Consulting
('accenture', ARRAY['accenture plc'], ARRAY['consulting', 'public'], true),
('booz allen', ARRAY['booz allen hamilton'], ARRAY['consulting', 'public', 'government'], true),
('oliver wyman', ARRAY['oliver wyman group'], ARRAY['consulting'], false),
('strategy&', ARRAY['strategy and'], ARRAY['consulting'], false),
('roland berger', ARRAY['roland berger gmbh'], ARRAY['consulting'], false),
('lego', ARRAY['l.e.k. consulting'], ARRAY['consulting'], false),

-- Fortune 500 / Major Corps
('walmart', ARRAY['walmart inc'], ARRAY['fortune_500', 'public', 'retail'], true),
('exxon', ARRAY['exxonmobil', 'exxon mobil'], ARRAY['fortune_500', 'public', 'energy'], true),
('chevron', ARRAY['chevron corp'], ARRAY['fortune_500', 'public', 'energy'], true),
('berkshire hathaway', ARRAY['berkshire'], ARRAY['fortune_500', 'public', 'conglomerate'], true),
('at&t', ARRAY['att', 'at and t'], ARRAY['fortune_500', 'public', 'telecom'], true),
('verizon', ARRAY['verizon communications'], ARRAY['fortune_500', 'public', 'telecom'], true),
('disney', ARRAY['walt disney', 'disney company'], ARRAY['fortune_500', 'public', 'media'], true),
('comcast', ARRAY['comcast corp'], ARRAY['fortune_500', 'public', 'media'], true),
('general motors', ARRAY['gm'], ARRAY['fortune_500', 'public', 'automotive'], true),
('ford', ARRAY['ford motor'], ARRAY['fortune_500', 'public', 'automotive'], true),
('tesla', ARRAY['tesla inc', 'tesla motors'], ARRAY['fortune_500', 'public', 'automotive', 'high_growth'], true),
('boeing', ARRAY['boeing company'], ARRAY['fortune_500', 'public', 'aerospace'], true),
('lockheed martin', ARRAY['lockheed'], ARRAY['fortune_500', 'public', 'aerospace', 'defense'], true),
('raytheon', ARRAY['rtx', 'raytheon technologies'], ARRAY['fortune_500', 'public', 'aerospace', 'defense'], true),
('general electric', ARRAY['ge'], ARRAY['fortune_500', 'public', 'conglomerate'], true),
('procter & gamble', ARRAY['p&g', 'pg'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('coca-cola', ARRAY['coke', 'coca cola'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('pepsico', ARRAY['pepsi'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('nike', ARRAY['nike inc'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('3m', ARRAY['3m company', 'mmm'], ARRAY['fortune_500', 'public', 'conglomerate'], true),
('target', ARRAY['target corp'], ARRAY['fortune_500', 'public', 'retail'], true),
('costco', ARRAY['costco wholesale'], ARRAY['fortune_500', 'public', 'retail'], true),
('home depot', ARRAY['the home depot'], ARRAY['fortune_500', 'public', 'retail'], true),
('lowes', ARRAY['lowe''s'], ARRAY['fortune_500', 'public', 'retail'], true)

ON CONFLICT (company_normalized) DO UPDATE SET
    company_aliases = EXCLUDED.company_aliases,
    pedigree_tags = EXCLUDED.pedigree_tags,
    is_public = EXCLUDED.is_public,
    updated_at = NOW();

-- ============================================================================
-- PEDIGREE SUMMARY ON CANDIDATE PROFILES
-- Add computed field for quick filtering
-- ============================================================================

-- Add pedigree summary column to candidate_profiles if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'candidate_profiles'
        AND column_name = 'pedigree_summary'
    ) THEN
        ALTER TABLE candidate_profiles ADD COLUMN pedigree_summary JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- Add has_pedigree boolean for quick filtering
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'candidate_profiles'
        AND column_name = 'has_pedigree'
    ) THEN
        ALTER TABLE candidate_profiles ADD COLUMN has_pedigree BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Index for pedigree filtering
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_has_pedigree ON candidate_profiles(has_pedigree) WHERE has_pedigree = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_pedigree_summary ON candidate_profiles USING GIN(pedigree_summary);

-- Comments
COMMENT ON TABLE candidate_companies IS 'Prior employers for each candidate, with pedigree tags for B2B filtering';
COMMENT ON TABLE company_pedigree_lookup IS 'Reference table mapping company names to pedigree categories (FAANG, MBB, etc.)';
COMMENT ON COLUMN candidate_profiles.pedigree_summary IS 'Cached summary of pedigree tags from candidate_companies, e.g., {faang: true, mbb: false}';
COMMENT ON COLUMN candidate_profiles.has_pedigree IS 'Quick boolean filter: true if candidate has any recognized pedigree companies';
