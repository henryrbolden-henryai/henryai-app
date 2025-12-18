-- Beta Feedback Table
-- Run this in your Supabase SQL Editor (Dashboard > SQL Editor)

-- Create the beta_feedback table
CREATE TABLE IF NOT EXISTS beta_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    user_email TEXT NOT NULL DEFAULT 'anonymous',
    feedback_type TEXT NOT NULL DEFAULT 'general',
    feedback_text TEXT NOT NULL,
    current_page TEXT,
    context JSONB DEFAULT '{}',
    conversation_snippet JSONB DEFAULT '[]',
    screenshot TEXT,  -- Base64 encoded image data
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMPTZ,
    reviewed_by TEXT,
    notes TEXT
);

-- Add comments for documentation
COMMENT ON TABLE beta_feedback IS 'Stores beta user feedback collected via Ask Henry';
COMMENT ON COLUMN beta_feedback.feedback_type IS 'Type: bug, feature_request, praise, ux_issue, general';
COMMENT ON COLUMN beta_feedback.context IS 'Additional context like URL, user agent, etc.';
COMMENT ON COLUMN beta_feedback.conversation_snippet IS 'Last few messages from Ask Henry conversation';
COMMENT ON COLUMN beta_feedback.screenshot IS 'Base64 encoded screenshot image (optional)';

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_beta_feedback_created_at ON beta_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_beta_feedback_type ON beta_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_beta_feedback_reviewed ON beta_feedback(reviewed);

-- Enable Row Level Security (RLS)
ALTER TABLE beta_feedback ENABLE ROW LEVEL SECURITY;

-- Policy: Users can insert their own feedback
CREATE POLICY "Users can insert feedback" ON beta_feedback
    FOR INSERT
    WITH CHECK (true);  -- Allow all inserts (including anonymous)

-- Policy: Users can view their own feedback
CREATE POLICY "Users can view own feedback" ON beta_feedback
    FOR SELECT
    USING (auth.uid() = user_id OR user_id IS NULL);

-- Note: You (admin) can view all feedback via the Supabase dashboard
-- or by creating a service role connection

-- Grant permissions
GRANT INSERT ON beta_feedback TO authenticated;
GRANT INSERT ON beta_feedback TO anon;
GRANT SELECT ON beta_feedback TO authenticated;
