-- Command Center: Add intelligence columns to applications table
-- Version: 2.0
-- Date: December 18, 2025
-- Spec: COMMAND_CENTER_IMPLEMENTATION_SPEC (REVISED).md

-- Add new columns to applications table for Command Center intelligence
ALTER TABLE applications ADD COLUMN IF NOT EXISTS jd_source VARCHAR(50);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS provisional_profile JSONB;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS confidence_label VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS decision_confidence INTEGER;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS substatus VARCHAR(50);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS days_since_last_activity INTEGER;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_activity_date DATE;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS next_action VARCHAR(100);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS next_action_reason VARCHAR(200);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS priority_level VARCHAR(20);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS user_override BOOLEAN DEFAULT FALSE;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS user_override_reason TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS manual_lock BOOLEAN DEFAULT FALSE;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_applications_jd_source ON applications(jd_source);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_substatus ON applications(substatus);
CREATE INDEX IF NOT EXISTS idx_applications_decision_confidence ON applications(decision_confidence);
CREATE INDEX IF NOT EXISTS idx_applications_next_action ON applications(next_action);
CREATE INDEX IF NOT EXISTS idx_applications_priority_level ON applications(priority_level);
CREATE INDEX IF NOT EXISTS idx_applications_last_activity_date ON applications(last_activity_date);

-- Add comments for documentation
COMMENT ON COLUMN applications.jd_source IS 'Track JD provenance: user_provided, url_fetched, inferred, missing, link_failed';
COMMENT ON COLUMN applications.provisional_profile IS 'Store reconstructed role profile when JD is missing';
COMMENT ON COLUMN applications.confidence_label IS 'Trust preservation: directional or refined';
COMMENT ON COLUMN applications.decision_confidence IS 'Strategic guidance score (0-100)';
COMMENT ON COLUMN applications.substatus IS 'Granular state: waiting, follow_up_sent, prep_needed, ghosted_14d, etc.';
COMMENT ON COLUMN applications.days_since_last_activity IS 'Momentum tracking - days since last activity';
COMMENT ON COLUMN applications.last_activity_date IS 'For calculating staleness';
COMMENT ON COLUMN applications.next_action IS 'Explicit instruction: Send follow-up email, Archive, None—wait';
COMMENT ON COLUMN applications.next_action_reason IS 'Contextual why: 70% respond by now. Silence = ghosting.';
COMMENT ON COLUMN applications.priority_level IS 'Focus guidance: high, medium, low, archive';
COMMENT ON COLUMN applications.user_override IS 'User manually set priority/action';
COMMENT ON COLUMN applications.user_override_reason IS 'Why user overrode system recommendation';
COMMENT ON COLUMN applications.manual_lock IS 'Prevent system from changing action';
