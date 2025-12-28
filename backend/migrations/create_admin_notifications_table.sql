-- Admin Notifications Table
-- Stores notifications for real-time Hey Henry alerts to admin users

CREATE TABLE IF NOT EXISTS admin_notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    notification_type TEXT NOT NULL,  -- 'feedback', 'system', 'user_activity'
    feedback_type TEXT,  -- 'bug', 'feature_request', 'praise', 'ux_issue', 'general'
    from_email TEXT,
    from_name TEXT,
    summary TEXT,
    full_content TEXT,
    current_page TEXT,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for quick unread notification queries
CREATE INDEX IF NOT EXISTS idx_admin_notifications_unread
ON admin_notifications(read, created_at DESC)
WHERE read = FALSE;

-- RLS Policies
ALTER TABLE admin_notifications ENABLE ROW LEVEL SECURITY;

-- Allow service role to insert (from backend)
CREATE POLICY "Service role can insert notifications" ON admin_notifications
FOR INSERT TO service_role
WITH CHECK (true);

-- Allow service role to read all
CREATE POLICY "Service role can read notifications" ON admin_notifications
FOR SELECT TO service_role
USING (true);

-- Allow service role to update (mark as read)
CREATE POLICY "Service role can update notifications" ON admin_notifications
FOR UPDATE TO service_role
USING (true);

-- Allow authenticated users to read (for admin check on frontend)
CREATE POLICY "Authenticated can read notifications" ON admin_notifications
FOR SELECT TO authenticated
USING (true);

-- Allow authenticated to update (mark as read)
CREATE POLICY "Authenticated can update notifications" ON admin_notifications
FOR UPDATE TO authenticated
USING (true);
