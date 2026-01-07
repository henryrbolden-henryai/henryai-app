-- Update Admin Notifications Table
-- Adds columns for reply tracking and resolution status

-- Add new columns for reply and resolution tracking
ALTER TABLE admin_notifications
ADD COLUMN IF NOT EXISTS resolved BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS replied_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS reply_text TEXT,
ADD COLUMN IF NOT EXISTS reply_email_id TEXT,
ADD COLUMN IF NOT EXISTS screenshot_url TEXT;

-- Add index for resolved notifications
CREATE INDEX IF NOT EXISTS idx_admin_notifications_resolved
ON admin_notifications(resolved, created_at DESC)
WHERE resolved = FALSE;

-- Update the unread query to exclude resolved
DROP INDEX IF EXISTS idx_admin_notifications_unread;
CREATE INDEX IF NOT EXISTS idx_admin_notifications_active
ON admin_notifications(read, resolved, created_at DESC)
WHERE read = FALSE AND (resolved = FALSE OR resolved IS NULL);
