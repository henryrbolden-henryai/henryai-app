-- Resume Analysis Cache Table
-- Per P0 spec: Prevent repeated LLM calls for the same resume
-- Cache lives for 7 days, refreshes last_used_at on hit

CREATE TABLE IF NOT EXISTS resume_analysis_cache (
    resume_hash TEXT PRIMARY KEY,
    analysis_payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for cache cleanup queries
CREATE INDEX IF NOT EXISTS idx_resume_cache_created_at ON resume_analysis_cache(created_at);
CREATE INDEX IF NOT EXISTS idx_resume_cache_last_used ON resume_analysis_cache(last_used_at);

-- Add comment for documentation
COMMENT ON TABLE resume_analysis_cache IS 'Caches JD analysis results by resume hash to avoid redundant LLM calls. TTL: 7 days.';
COMMENT ON COLUMN resume_analysis_cache.resume_hash IS 'SHA-256 hash of normalized resume JSON';
COMMENT ON COLUMN resume_analysis_cache.analysis_payload IS 'Full analysis response JSON';
COMMENT ON COLUMN resume_analysis_cache.created_at IS 'When this cache entry was first created';
COMMENT ON COLUMN resume_analysis_cache.last_used_at IS 'Last time this cache entry was accessed (for TTL refresh)';
