-- Migration V2: Add enhanced candidate profile fields for B2B matching
-- This version handles existing tables by adding columns if missing
-- Run this in Supabase SQL Editor
-- Date: 2025-01-05

-- ============================================================================
-- STEP 1: Add missing columns to candidate_profiles if table exists
-- ============================================================================

-- Add columns one by one (safe for existing tables)
DO $$ BEGIN
    -- Basic Info
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'first_name') THEN
        ALTER TABLE candidate_profiles ADD COLUMN first_name TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'last_name') THEN
        ALTER TABLE candidate_profiles ADD COLUMN last_name TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'pronouns') THEN
        ALTER TABLE candidate_profiles ADD COLUMN pronouns TEXT;
    END IF;

    -- Professional Info
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'function_area') THEN
        ALTER TABLE candidate_profiles ADD COLUMN function_area TEXT CHECK (function_area IS NULL OR function_area IN (
            'product_management', 'engineering', 'design', 'data_analytics',
            'sales', 'marketing', 'customer_success', 'operations',
            'finance', 'hr_people', 'legal', 'other'
        ));
    END IF;

    -- Current Industry
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'current_industry') THEN
        ALTER TABLE candidate_profiles ADD COLUMN current_industry TEXT CHECK (current_industry IS NULL OR current_industry IN (
            'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
            'manufacturing', 'energy', 'real_estate', 'education', 'government',
            'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
        ));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'secondary_industry') THEN
        ALTER TABLE candidate_profiles ADD COLUMN secondary_industry TEXT CHECK (secondary_industry IS NULL OR secondary_industry IN (
            'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
            'manufacturing', 'energy', 'real_estate', 'education', 'government',
            'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
        ));
    END IF;

    -- Work Authorization
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'work_authorization') THEN
        ALTER TABLE candidate_profiles ADD COLUMN work_authorization TEXT CHECK (work_authorization IS NULL OR work_authorization IN (
            'us_citizen', 'green_card', 'h1b', 'h1b_transfer', 'l1',
            'opt', 'opt_stem', 'tn', 'other_visa'
        ));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'requires_sponsorship') THEN
        ALTER TABLE candidate_profiles ADD COLUMN requires_sponsorship BOOLEAN DEFAULT false;
    END IF;

    -- Veteran Status
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'is_veteran') THEN
        ALTER TABLE candidate_profiles ADD COLUMN is_veteran BOOLEAN DEFAULT false;
    END IF;

    -- Location (structured)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'city') THEN
        ALTER TABLE candidate_profiles ADD COLUMN city TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'state') THEN
        ALTER TABLE candidate_profiles ADD COLUMN state TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'country') THEN
        ALTER TABLE candidate_profiles ADD COLUMN country TEXT;
    END IF;

    -- Work Preferences
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'work_arrangement') THEN
        ALTER TABLE candidate_profiles ADD COLUMN work_arrangement JSONB DEFAULT '[]'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'open_to_relocate') THEN
        ALTER TABLE candidate_profiles ADD COLUMN open_to_relocate TEXT CHECK (open_to_relocate IS NULL OR open_to_relocate IN ('yes', 'maybe', 'no'));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'relocation_targets') THEN
        ALTER TABLE candidate_profiles ADD COLUMN relocation_targets JSONB DEFAULT '[]'::jsonb;
    END IF;

    -- Compensation
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'comp_min') THEN
        ALTER TABLE candidate_profiles ADD COLUMN comp_min INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'comp_target') THEN
        ALTER TABLE candidate_profiles ADD COLUMN comp_target INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'comp_stretch') THEN
        ALTER TABLE candidate_profiles ADD COLUMN comp_stretch INTEGER;
    END IF;

    -- Target Industries
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'target_industry_primary') THEN
        ALTER TABLE candidate_profiles ADD COLUMN target_industry_primary TEXT CHECK (target_industry_primary IS NULL OR target_industry_primary IN (
            'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
            'manufacturing', 'energy', 'real_estate', 'education', 'government',
            'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
        ));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'target_industry_secondary') THEN
        ALTER TABLE candidate_profiles ADD COLUMN target_industry_secondary TEXT CHECK (target_industry_secondary IS NULL OR target_industry_secondary IN (
            'technology', 'healthcare', 'fintech', 'ecommerce', 'media',
            'manufacturing', 'energy', 'real_estate', 'education', 'government',
            'consulting', 'telecom', 'transportation', 'hospitality', 'nonprofit', 'other'
        ));
    END IF;

    -- Job Search Situation
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'situation_holding_up') THEN
        ALTER TABLE candidate_profiles ADD COLUMN situation_holding_up TEXT CHECK (situation_holding_up IS NULL OR situation_holding_up IN (
            'doing_well', 'stressed_but_managing', 'struggling', 'rather_not_say'
        ));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'situation_timeline') THEN
        ALTER TABLE candidate_profiles ADD COLUMN situation_timeline TEXT CHECK (situation_timeline IS NULL OR situation_timeline IN (
            'no_rush', 'actively_looking', 'soon', 'urgent'
        ));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'situation_confidence') THEN
        ALTER TABLE candidate_profiles ADD COLUMN situation_confidence TEXT CHECK (situation_confidence IS NULL OR situation_confidence IN (
            'strong', 'shaky', 'low', 'need_validation'
        ));
    END IF;

    -- B2B Marketplace fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'visible_to_employers') THEN
        ALTER TABLE candidate_profiles ADD COLUMN visible_to_employers BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'actively_seeking') THEN
        ALTER TABLE candidate_profiles ADD COLUMN actively_seeking BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'available_date') THEN
        ALTER TABLE candidate_profiles ADD COLUMN available_date DATE;
    END IF;

    -- Computed/cached fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'years_experience') THEN
        ALTER TABLE candidate_profiles ADD COLUMN years_experience INTEGER;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'current_level_id') THEN
        ALTER TABLE candidate_profiles ADD COLUMN current_level_id TEXT;
    END IF;

    -- Pedigree fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'pedigree_summary') THEN
        ALTER TABLE candidate_profiles ADD COLUMN pedigree_summary JSONB DEFAULT '{}'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'candidate_profiles' AND column_name = 'has_pedigree') THEN
        ALTER TABLE candidate_profiles ADD COLUMN has_pedigree BOOLEAN DEFAULT false;
    END IF;

END $$;

-- ============================================================================
-- STEP 2: Create indexes (IF NOT EXISTS handles duplicates)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_candidate_profiles_function ON candidate_profiles(function_area);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_industry ON candidate_profiles(current_industry);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_location ON candidate_profiles(country, state, city);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_work_auth ON candidate_profiles(work_authorization);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_sponsorship ON candidate_profiles(requires_sponsorship) WHERE requires_sponsorship = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_veteran ON candidate_profiles(is_veteran) WHERE is_veteran = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_visible ON candidate_profiles(visible_to_employers) WHERE visible_to_employers = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_seeking ON candidate_profiles(actively_seeking) WHERE actively_seeking = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_has_pedigree ON candidate_profiles(has_pedigree) WHERE has_pedigree = true;
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_pedigree_summary ON candidate_profiles USING GIN(pedigree_summary);

-- ============================================================================
-- STEP 3: Create candidate_companies table
-- ============================================================================

CREATE TABLE IF NOT EXISTS candidate_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    company_normalized TEXT,
    company_domain TEXT,
    pedigree_tags TEXT[] DEFAULT '{}',
    title TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    duration_months INTEGER,
    source TEXT DEFAULT 'resume' CHECK (source IN ('resume', 'linkedin', 'manual')),
    resume_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_candidate_companies_user ON candidate_companies(user_id);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_normalized ON candidate_companies(company_normalized);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_pedigree ON candidate_companies USING GIN(pedigree_tags);
CREATE INDEX IF NOT EXISTS idx_candidate_companies_current ON candidate_companies(user_id, is_current) WHERE is_current = true;

ALTER TABLE candidate_companies ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist, then create
DROP POLICY IF EXISTS "Users can view own companies" ON candidate_companies;
DROP POLICY IF EXISTS "Users can insert own companies" ON candidate_companies;
DROP POLICY IF EXISTS "Users can update own companies" ON candidate_companies;
DROP POLICY IF EXISTS "Users can delete own companies" ON candidate_companies;
DROP POLICY IF EXISTS "Service role can manage all companies" ON candidate_companies;

CREATE POLICY "Users can view own companies" ON candidate_companies FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own companies" ON candidate_companies FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own companies" ON candidate_companies FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own companies" ON candidate_companies FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can manage all companies" ON candidate_companies FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- STEP 4: Create company_pedigree_lookup table
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_pedigree_lookup (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_normalized TEXT NOT NULL UNIQUE,
    company_aliases TEXT[] DEFAULT '{}',
    company_domain TEXT,
    pedigree_tags TEXT[] DEFAULT '{}',
    employee_count_estimate INTEGER,
    is_public BOOLEAN DEFAULT false,
    founded_year INTEGER,
    headquarters_country TEXT,
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company_pedigree_normalized ON company_pedigree_lookup(company_normalized);
CREATE INDEX IF NOT EXISTS idx_company_pedigree_tags ON company_pedigree_lookup USING GIN(pedigree_tags);
CREATE INDEX IF NOT EXISTS idx_company_pedigree_aliases ON company_pedigree_lookup USING GIN(company_aliases);

-- ============================================================================
-- STEP 5: Seed company pedigree data
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

-- Unicorns / High-Growth
('stripe', ARRAY['stripe inc'], ARRAY['unicorn', 'fintech', 'high_growth'], false),
('airbnb', ARRAY['airbnb inc'], ARRAY['unicorn', 'public', 'marketplace'], true),
('uber', ARRAY['uber technologies'], ARRAY['unicorn', 'public', 'marketplace'], true),
('doordash', ARRAY['doordash inc'], ARRAY['unicorn', 'public', 'marketplace'], true),
('coinbase', ARRAY['coinbase global'], ARRAY['unicorn', 'public', 'fintech', 'crypto'], true),
('databricks', ARRAY['databricks inc'], ARRAY['unicorn', 'data', 'ai', 'high_growth'], false),
('openai', ARRAY['open ai'], ARRAY['unicorn', 'ai', 'high_growth'], false),
('anthropic', ARRAY[]::TEXT[], ARRAY['unicorn', 'ai', 'high_growth'], false),
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

-- MBB Consulting
('mckinsey', ARRAY['mckinsey & company', 'mckinsey and company'], ARRAY['mbb', 'consulting', 'top_tier'], false),
('bain', ARRAY['bain & company', 'bain and company'], ARRAY['mbb', 'consulting', 'top_tier'], false),
('bcg', ARRAY['boston consulting group'], ARRAY['mbb', 'consulting', 'top_tier'], false),

-- Big 4
('deloitte', ARRAY['deloitte consulting', 'deloitte llp'], ARRAY['big4', 'consulting'], false),
('pwc', ARRAY['pricewaterhousecoopers', 'price waterhouse coopers'], ARRAY['big4', 'consulting'], false),
('ey', ARRAY['ernst & young', 'ernst and young'], ARRAY['big4', 'consulting'], false),
('kpmg', ARRAY['kpmg llp'], ARRAY['big4', 'consulting'], false),

-- Other Consulting
('accenture', ARRAY['accenture plc'], ARRAY['consulting', 'public'], true),
('booz allen', ARRAY['booz allen hamilton'], ARRAY['consulting', 'public', 'government'], true),

-- Finance
('goldman sachs', ARRAY['goldman sachs group', 'gs'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('morgan stanley', ARRAY['morgan stanley & co'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('jpmorgan', ARRAY['jp morgan', 'jpmorgan chase', 'j.p. morgan'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('blackstone', ARRAY['blackstone group'], ARRAY['pe', 'finance', 'public'], true),
('blackrock', ARRAY['blackrock inc'], ARRAY['asset_management', 'finance', 'public'], true),
('bank of america', ARRAY['bofa', 'boa', 'bank of america corp'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('citigroup', ARRAY['citi', 'citibank'], ARRAY['bulge_bracket', 'finance', 'public'], true),
('wells fargo', ARRAY['wells fargo & co'], ARRAY['bulge_bracket', 'finance', 'public'], true),

-- PE / VC
('kkr', ARRAY['kohlberg kravis roberts'], ARRAY['pe', 'finance'], false),
('carlyle', ARRAY['carlyle group'], ARRAY['pe', 'finance', 'public'], true),
('sequoia', ARRAY['sequoia capital'], ARRAY['vc', 'finance'], false),
('andreessen horowitz', ARRAY['a16z'], ARRAY['vc', 'finance'], false),

-- Healthcare
('unitedhealth', ARRAY['unitedhealth group', 'uhg'], ARRAY['healthcare', 'public', 'fortune_500'], true),
('johnson & johnson', ARRAY['j&j', 'jnj'], ARRAY['healthcare', 'pharma', 'public', 'fortune_500'], true),
('pfizer', ARRAY['pfizer inc'], ARRAY['healthcare', 'pharma', 'public', 'fortune_500'], true),

-- Fortune 500
('walmart', ARRAY['walmart inc'], ARRAY['fortune_500', 'public', 'retail'], true),
('disney', ARRAY['walt disney', 'disney company'], ARRAY['fortune_500', 'public', 'media'], true),
('tesla', ARRAY['tesla inc', 'tesla motors'], ARRAY['fortune_500', 'public', 'automotive', 'high_growth'], true),
('boeing', ARRAY['boeing company'], ARRAY['fortune_500', 'public', 'aerospace'], true),
('general electric', ARRAY['ge'], ARRAY['fortune_500', 'public', 'conglomerate'], true),
('procter & gamble', ARRAY['p&g', 'pg'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('coca-cola', ARRAY['coke', 'coca cola'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('nike', ARRAY['nike inc'], ARRAY['fortune_500', 'public', 'consumer_goods'], true),
('target', ARRAY['target corp'], ARRAY['fortune_500', 'public', 'retail'], true),
('costco', ARRAY['costco wholesale'], ARRAY['fortune_500', 'public', 'retail'], true)

ON CONFLICT (company_normalized) DO UPDATE SET
    company_aliases = EXCLUDED.company_aliases,
    pedigree_tags = EXCLUDED.pedigree_tags,
    is_public = EXCLUDED.is_public,
    updated_at = NOW();

-- ============================================================================
-- STEP 6: Add comments
-- ============================================================================

COMMENT ON TABLE candidate_companies IS 'Prior employers for each candidate, with pedigree tags for B2B filtering';
COMMENT ON TABLE company_pedigree_lookup IS 'Reference table mapping company names to pedigree categories (FAANG, MBB, etc.)';

SELECT 'Migration completed successfully!' as status;
