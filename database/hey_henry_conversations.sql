-- Hey Henry Conversations Table
-- Run this in Supabase SQL Editor

-- Create the conversations table
CREATE TABLE IF NOT EXISTS hey_henry_conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  messages JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- Index for fast user lookups
CREATE INDEX IF NOT EXISTS idx_hey_henry_conversations_user_id
  ON hey_henry_conversations(user_id);

-- Index for recent conversations (sorted by updated_at)
CREATE INDEX IF NOT EXISTS idx_hey_henry_conversations_updated
  ON hey_henry_conversations(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE hey_henry_conversations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own conversations
CREATE POLICY "Users can view own conversations" ON hey_henry_conversations
  FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own conversations
CREATE POLICY "Users can insert own conversations" ON hey_henry_conversations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own conversations
CREATE POLICY "Users can update own conversations" ON hey_henry_conversations
  FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can delete their own conversations
CREATE POLICY "Users can delete own conversations" ON hey_henry_conversations
  FOR DELETE USING (auth.uid() = user_id);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_hey_henry_conversations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function on update
DROP TRIGGER IF EXISTS hey_henry_conversations_updated_at ON hey_henry_conversations;
CREATE TRIGGER hey_henry_conversations_updated_at
  BEFORE UPDATE ON hey_henry_conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_hey_henry_conversations_updated_at();
