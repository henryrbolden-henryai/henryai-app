-- Story Bank Enhancement Migration
-- Adds AI Draft support, analytics dimensions, and templates table
-- Run this in Supabase SQL Editor

-- ============================================
-- EXTEND user_story_bank TABLE
-- ============================================

-- Add source tracking (AI Draft vs User vs Template)
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'User' CHECK (source IN ('AI Draft', 'User', 'Template'));

-- Add confidence level for AI drafts
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS confidence TEXT DEFAULT 'High' CHECK (confidence IN ('Low', 'Medium', 'High'));

-- Add role level for story scoping
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS role_level TEXT;

-- Add interview stages this story works for
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS interview_stages TEXT[] DEFAULT '{}';

-- Add company types this story works for
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS company_types TEXT[] DEFAULT '{}';

-- Core 3 Story Flow fields
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS is_core BOOLEAN DEFAULT false;

ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS locked BOOLEAN DEFAULT false;

ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE;

-- Coaching cues (JSONB for flexibility)
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS coaching_cues JSONB DEFAULT '{}'::jsonb;

-- Opening line for quick delivery
ALTER TABLE user_story_bank
ADD COLUMN IF NOT EXISTS opening_line TEXT;

-- Index for filtering by source (AI drafts vs user stories)
CREATE INDEX IF NOT EXISTS idx_stories_source ON user_story_bank(source);

-- Index for Core 3 stories
CREATE INDEX IF NOT EXISTS idx_stories_core ON user_story_bank(is_core) WHERE is_core = true;

-- Index for confidence filtering
CREATE INDEX IF NOT EXISTS idx_stories_confidence ON user_story_bank(confidence);


-- ============================================
-- EXTEND interview_debriefs TABLE
-- Analytics dimensions for story performance slicing
-- ============================================

-- Add role level for analytics (Director vs VP performance)
ALTER TABLE interview_debriefs
ADD COLUMN IF NOT EXISTS role_level TEXT;

-- Add company type for analytics (Big Tech vs startup)
ALTER TABLE interview_debriefs
ADD COLUMN IF NOT EXISTS company_type TEXT;

-- Index for analytics queries
CREATE INDEX IF NOT EXISTS idx_debriefs_role_level ON interview_debriefs(role_level);
CREATE INDEX IF NOT EXISTS idx_debriefs_company_type ON interview_debriefs(company_type);


-- ============================================
-- CREATE story_templates TABLE
-- Recruiter-grade templates for common competencies
-- ============================================

CREATE TABLE IF NOT EXISTS story_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name TEXT NOT NULL,
    template_category TEXT NOT NULL,  -- leadership, conflict, influence, execution, failure
    demonstrates TEXT[] NOT NULL,
    best_for_questions TEXT[] DEFAULT '{}',
    situation_prompt TEXT NOT NULL,
    task_prompt TEXT NOT NULL,
    action_prompt TEXT NOT NULL,
    result_prompt TEXT NOT NULL,
    example_story TEXT,
    target_levels TEXT[] DEFAULT '{}',
    target_industries TEXT[] DEFAULT '{}',
    is_premium BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for template queries
CREATE INDEX IF NOT EXISTS idx_templates_category ON story_templates(template_category);
CREATE INDEX IF NOT EXISTS idx_templates_premium ON story_templates(is_premium);


-- ============================================
-- SEED INITIAL TEMPLATES (10 templates)
-- ============================================

INSERT INTO story_templates (template_name, template_category, demonstrates, best_for_questions, situation_prompt, task_prompt, action_prompt, result_prompt, target_levels, sort_order) VALUES

-- 1. Leading through ambiguity
('Leading through ambiguity', 'leadership',
 ARRAY['Leadership', 'Strategic Thinking', 'Decision Making'],
 ARRAY['Tell me about a time you led without clear direction', 'Describe navigating uncertainty', 'How do you make decisions with incomplete information'],
 'Describe a situation where you had to make decisions without complete information or clear direction from leadership.',
 'What was your specific responsibility in navigating this uncertainty?',
 'Walk through the specific steps you took to create clarity, align stakeholders, and move forward.',
 'What were the measurable outcomes? What did you learn about leading through ambiguity?',
 ARRAY['Manager', 'Director', 'VP'], 1),

-- 2. Conflict with a peer
('Conflict with a peer', 'conflict',
 ARRAY['Conflict Resolution', 'Collaboration', 'Influence'],
 ARRAY['Tell me about a disagreement with a colleague', 'Describe a conflict at work', 'How do you handle difficult conversations'],
 'Describe a meaningful disagreement or conflict with a peer at your level.',
 'What was at stake? What was your role in resolving it?',
 'How did you approach the conversation? What specific tactics did you use to find common ground?',
 'How was it resolved? What changed in the working relationship afterward?',
 ARRAY['IC', 'Manager', 'Director'], 2),

-- 3. Executive influence without authority
('Executive influence without authority', 'influence',
 ARRAY['Influence', 'Stakeholder Management', 'Strategic Thinking'],
 ARRAY['Tell me about influencing senior leadership', 'Describe getting buy-in from executives', 'How do you influence without authority'],
 'Describe a situation where you needed buy-in from executives you did not report to.',
 'What did you need from them, and why was it challenging to get?',
 'How did you build your case? How did you navigate the politics and competing priorities?',
 'Did you get the outcome? What did you learn about influencing up?',
 ARRAY['Manager', 'Director', 'VP'], 3),

-- 4. Shipping under pressure
('Shipping under pressure', 'execution',
 ARRAY['Execution', 'Prioritization', 'Problem Solving'],
 ARRAY['Tell me about delivering under a tight deadline', 'Describe a time you had to move fast', 'How do you handle pressure'],
 'Describe a project or deliverable with a non-negotiable deadline and real stakes.',
 'What was your role? What made the timeline tight?',
 'What did you cut? What did you prioritize? How did you keep the team focused?',
 'Did you ship on time? What tradeoffs did you make and what was the outcome?',
 ARRAY['IC', 'Manager'], 4),

-- 5. Learning from failure
('Learning from failure', 'failure',
 ARRAY['Growth', 'Accountability', 'Self-Awareness'],
 ARRAY['Tell me about a time you failed', 'Describe your biggest mistake', 'What have you learned from failure'],
 'Describe a significant failure or mistake you made at work.',
 'What was your responsibility in the failure?',
 'How did you respond? What did you do to address it?',
 'What did you learn? How have you applied that learning since?',
 ARRAY['IC', 'Manager', 'Director', 'VP'], 5),

-- 6. Cross-functional alignment
('Cross-functional alignment', 'collaboration',
 ARRAY['Collaboration', 'Influence', 'Communication'],
 ARRAY['Tell me about working across teams', 'Describe aligning competing priorities', 'How do you collaborate cross-functionally'],
 'Describe a project that required alignment across multiple teams with different priorities.',
 'What was your role in driving alignment?',
 'How did you navigate competing priorities and build consensus?',
 'What was the outcome? How did you maintain alignment throughout?',
 ARRAY['Manager', 'Director'], 6),

-- 7. Technical deep-dive decision
('Technical deep-dive decision', 'technical',
 ARRAY['Technical Depth', 'Decision Making', 'Problem Solving'],
 ARRAY['Walk me through a technical decision', 'Describe a complex technical problem', 'How do you approach architecture decisions'],
 'Describe a complex technical decision where you had to go deep to make the right call.',
 'What was the technical challenge? What were the options?',
 'How did you evaluate the tradeoffs? What analysis did you do?',
 'What did you decide? What was the outcome and what would you do differently?',
 ARRAY['IC', 'Manager'], 7),

-- 8. Managing up when blocked
('Managing up when blocked', 'influence',
 ARRAY['Influence', 'Communication', 'Problem Solving'],
 ARRAY['Tell me about managing up', 'Describe getting unblocked', 'How do you handle roadblocks from leadership'],
 'Describe a situation where you were blocked by a decision or inaction from someone above you.',
 'What were you trying to accomplish? Why was it blocked?',
 'How did you approach the conversation? What did you do to change their mind or find an alternative?',
 'Did you get unblocked? What did you learn about managing up?',
 ARRAY['IC', 'Manager'], 8),

-- 9. Scaling a team or process
('Scaling a team or process', 'leadership',
 ARRAY['Leadership', 'Scaling', 'Strategic Thinking'],
 ARRAY['Tell me about scaling something', 'Describe growing a team', 'How do you think about scale'],
 'Describe a team, process, or system you scaled significantly.',
 'What was the starting point? What did "scale" mean in this context?',
 'What changes did you make? What broke along the way and how did you fix it?',
 'What did you achieve? What would you do differently at the next scale?',
 ARRAY['Manager', 'Director', 'VP'], 9),

-- 10. Customer/user obsession
('Customer obsession', 'product',
 ARRAY['User Centricity', 'Product Sense', 'Empathy'],
 ARRAY['Tell me about understanding customers', 'Describe a user-focused decision', 'How do you stay close to users'],
 'Describe a time when deep customer/user understanding changed your approach.',
 'What were you trying to solve? How did you get close to the user?',
 'What insight did you gain? How did it change your approach?',
 'What was the outcome for the user? How do you maintain that closeness?',
 ARRAY['IC', 'Manager', 'Director', 'VP'], 10)

ON CONFLICT DO NOTHING;


-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON COLUMN user_story_bank.source IS 'Origin of story: AI Draft (generated), User (written/edited), Template (from template)';
COMMENT ON COLUMN user_story_bank.confidence IS 'Confidence level: Low (AI draft), Medium (from template), High (user-verified)';
COMMENT ON COLUMN user_story_bank.role_level IS 'Target role level: IC, Manager, Director, VP, Executive';
COMMENT ON COLUMN user_story_bank.interview_stages IS 'Interview stages where story works: recruiter_screen, hiring_manager, technical, panel, executive';
COMMENT ON COLUMN user_story_bank.company_types IS 'Company types where story resonates: big_tech, startup, enterprise, consulting';
COMMENT ON COLUMN user_story_bank.is_core IS 'Part of Core 3 stories (Leadership, Execution, Failure)';
COMMENT ON COLUMN user_story_bank.locked IS 'Story is locked - enables tracking and recommendations';
COMMENT ON COLUMN user_story_bank.locked_at IS 'When the story was locked by user';
COMMENT ON COLUMN user_story_bank.coaching_cues IS 'JSON with emphasize[], avoid[], stop_talking_when, recovery_line';
COMMENT ON COLUMN user_story_bank.opening_line IS 'One-sentence hook to start the story';

COMMENT ON COLUMN interview_debriefs.role_level IS 'Role level of the position interviewed for';
COMMENT ON COLUMN interview_debriefs.company_type IS 'Company type: big_tech, startup, enterprise, consulting';

COMMENT ON TABLE story_templates IS 'Recruiter-grade story templates for common competencies. Gated to Partner+ tier.';
