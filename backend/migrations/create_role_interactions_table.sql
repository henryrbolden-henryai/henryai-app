-- ============================================================================
-- CANDIDATE ROLE INTERACTIONS
-- Unified table for all candidate-role touchpoints
-- Interaction types: analyzed, skipped, applied, reconsidered, override
-- Version: 1.0
-- Date: January 2026
-- ============================================================================

CREATE TABLE IF NOT EXISTS candidate_role_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Role identification (composite key for deduplication)
    company TEXT NOT NULL,
    role_title TEXT NOT NULL,
    job_url TEXT,

    -- Interaction details
    interaction_type TEXT NOT NULL,  -- 'analyzed', 'skipped', 'applied', 'reconsidered', 'override'
    interaction_at TIMESTAMPTZ DEFAULT NOW(),

    -- Analysis context (captured at time of interaction)
    fit_score INTEGER,
    recommendation TEXT,  -- 'Apply', 'Do Not Apply', 'Apply with Caution'
    analysis_snapshot JSONB,  -- Full analysis for reconsideration
    job_description TEXT,  -- Store JD for re-analysis

    -- Interaction-specific metadata
    pass_reason TEXT,  -- For 'skipped': low_fit, wrong_level, wrong_domain, etc.
    override_type TEXT,  -- For 'override': applied_despite_dna, applied_low_fit
    source TEXT DEFAULT 'results_page',  -- Where interaction occurred

    -- Outcome tracking (for applied/override)
    application_id UUID,  -- Links to applications table if they applied
    outcome TEXT,  -- 'pending', 'rejected', 'advanced', 'offered'
    outcome_updated_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary access patterns
CREATE INDEX IF NOT EXISTS idx_cri_user_id ON candidate_role_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_cri_interaction_type ON candidate_role_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_cri_interaction_at ON candidate_role_interactions(interaction_at DESC);

-- Analytics queries
CREATE INDEX IF NOT EXISTS idx_cri_fit_score ON candidate_role_interactions(fit_score);
CREATE INDEX IF NOT EXISTS idx_cri_recommendation ON candidate_role_interactions(recommendation);
CREATE INDEX IF NOT EXISTS idx_cri_outcome ON candidate_role_interactions(outcome) WHERE outcome IS NOT NULL;

-- Role journey queries (find all interactions for a specific role)
CREATE INDEX IF NOT EXISTS idx_cri_role_lookup ON candidate_role_interactions(user_id, company, role_title);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE candidate_role_interactions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own interactions" ON candidate_role_interactions;
CREATE POLICY "Users can view own interactions"
    ON candidate_role_interactions FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own interactions" ON candidate_role_interactions;
CREATE POLICY "Users can insert own interactions"
    ON candidate_role_interactions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own interactions" ON candidate_role_interactions;
CREATE POLICY "Users can update own interactions"
    ON candidate_role_interactions FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own interactions" ON candidate_role_interactions;
CREATE POLICY "Users can delete own interactions"
    ON candidate_role_interactions FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- HELPER VIEW: Current skipped roles (not yet reconsidered)
-- Used by Command Center Review History section
-- ============================================================================

CREATE OR REPLACE VIEW skipped_roles_current AS
SELECT
    cri.*,
    cri.interaction_at AS skipped_at
FROM candidate_role_interactions cri
WHERE cri.interaction_type = 'skipped'
  AND NOT EXISTS (
      SELECT 1 FROM candidate_role_interactions later
      WHERE later.user_id = cri.user_id
        AND later.company = cri.company
        AND later.role_title = cri.role_title
        AND later.interaction_type IN ('reconsidered', 'applied')
        AND later.interaction_at > cri.interaction_at
  );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE candidate_role_interactions IS 'Unified tracking of all candidate-role touchpoints for journey analytics';
COMMENT ON COLUMN candidate_role_interactions.interaction_type IS 'analyzed=viewed results, skipped=passed on role, applied=submitted application, reconsidered=revisited skipped role, override=applied despite guidance';
COMMENT ON COLUMN candidate_role_interactions.analysis_snapshot IS 'Full analysis JSONB for restoring results page state';
COMMENT ON COLUMN candidate_role_interactions.pass_reason IS 'User-selected reason for skipping: low_fit, wrong_level, wrong_domain, comp_mismatch, location, company_culture, following_guidance, other';
COMMENT ON COLUMN candidate_role_interactions.override_type IS 'Type of guidance override: applied_despite_dna, applied_low_fit';
COMMENT ON COLUMN candidate_role_interactions.source IS 'Where interaction occurred: results_page, tracker_reconsider, email, recommendations';
