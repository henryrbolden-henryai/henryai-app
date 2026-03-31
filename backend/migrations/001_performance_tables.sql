-- Performance Intelligence Infrastructure
-- Run this in Supabase SQL Editor

-- 1. Interview Responses — every evaluated answer
create table if not exists interview_responses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  interview_id text,
  question text,
  transcript text,
  content_score numeric,
  delivery_score numeric,
  final_score numeric,
  verdict text, -- advance | hold | reject
  rejection_reason text,
  filler_word_count integer,
  confidence_score numeric,
  pace_score numeric,
  clarity_score numeric,
  energy_score numeric,
  created_at timestamp default now()
);

-- Index for user lookups and summary computation
create index if not exists idx_interview_responses_user_id
  on interview_responses(user_id);

create index if not exists idx_interview_responses_created
  on interview_responses(user_id, created_at desc);


-- 2. Story Performance — how stories perform in interviews
create table if not exists story_performance (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  story_id text not null,
  interview_id text,
  effectiveness text, -- strong | adequate | weak
  delivery_score numeric,
  final_score numeric,
  context jsonb default '{}'::jsonb,
  created_at timestamp default now()
);

create index if not exists idx_story_performance_user_id
  on story_performance(user_id);

create index if not exists idx_story_performance_story
  on story_performance(user_id, story_id);


-- 3. User Performance Summary — cached aggregate stats
create table if not exists user_performance_summary (
  user_id uuid primary key,
  avg_confidence numeric,
  avg_clarity numeric,
  avg_delivery_score numeric,
  pass_rate numeric,
  top_issues jsonb default '[]'::jsonb,
  updated_at timestamp default now()
);
