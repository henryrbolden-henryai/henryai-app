-- JD Cache Table
-- Per P0 spec: Prevent repeated LLM calls for the same JD
-- Caches parsed JD context (role_title, role_type, leadership, etc.)
-- TTL: 7 days

CREATE TABLE IF NOT EXISTS jd_cache (
    jd_hash TEXT PRIMARY KEY,
    parsed_role_title TEXT,
    role_type TEXT,
    role_level TEXT,
    leadership_required BOOLEAN DEFAULT FALSE,
    required_years NUMERIC DEFAULT 0,
    domain_tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Index for TTL-based cleanup
CREATE INDEX IF NOT EXISTS idx_jd_cache_expires_at ON jd_cache(expires_at);

-- Add comments for documentation
COMMENT ON TABLE jd_cache IS 'Caches parsed JD context to avoid redundant role detection. TTL: 7 days.';
COMMENT ON COLUMN jd_cache.jd_hash IS 'SHA-256 hash of normalized JD text';
COMMENT ON COLUMN jd_cache.parsed_role_title IS 'Extracted role title from JD';
COMMENT ON COLUMN jd_cache.role_type IS 'Detected role type (product, engineering, etc.)';
COMMENT ON COLUMN jd_cache.role_level IS 'Detected role level (IC, Manager, Director, etc.)';
COMMENT ON COLUMN jd_cache.leadership_required IS 'Whether JD requires leadership experience';
COMMENT ON COLUMN jd_cache.required_years IS 'Required years of experience from JD';
COMMENT ON COLUMN jd_cache.domain_tags IS 'Top 5 domain/skill tags from JD';
