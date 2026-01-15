Multi-Resume Support Implementation Plan
Overview
Allow users to upload and manage multiple resumes, selecting which one to use when analyzing a job.
Current Architecture
	•	Single resume stored in userProfile.resume (localStorage) and candidate_profiles.profile_data (Supabase)
	•	Resume passed directly to /api/jd/analyze in request body
	•	No resume ID concept exists
Proposed Approach: New user_resumes Table
Why a Separate Table (vs JSONB array)?
	•	Cleaner CRUD operations
	•	Easier to query/list resumes
	•	Better for future features (resume versioning, sharing)
	•	Avoids bloating profile_data

Implementation Steps
Phase 1: Database Schema
Create user_resumes table in Supabase:

sql
CREATE TABLE user_resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_name TEXT NOT NULL,
    resume_json JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_resumes_user_id ON user_resumes(user_id);
CREATE INDEX idx_user_resumes_default ON user_resumes(user_id, is_default);

-- RLS
ALTER TABLE user_resumes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own resumes" ON user_resumes
    FOR ALL USING (auth.uid() = user_id);

-- Trigger for updated_at
CREATE TRIGGER trigger_user_resumes_updated_at
    BEFORE UPDATE ON user_resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
Files to create:
	•	backend/migrations/create_user_resumes_table.sql

Phase 2: Backend API Endpoints
New endpoints in backend/backend.py:
Endpoint
Method
Purpose
/api/resumes
GET
List user's resumes
/api/resumes
POST
Save new resume
/api/resumes/{id}
PUT
Update resume name/set default
/api/resumes/{id}
DELETE
Delete resume
Modify existing:
	•	Update /api/resume/parse to optionally save to user_resumes table
	•	Analysis endpoints already accept full resume JSON (no change needed)

Phase 3: Frontend - Supabase Client
Add to frontend/js/supabase-client.js:

javascript
// Resume management methods
async listResumes() { ... }
async saveResume(name, resumeJson) { ... }
async updateResume(id, updates) { ... }
async deleteResume(id) { ... }
async setDefaultResume(id) { ... }

Phase 4: Frontend - Profile Page
Modify frontend/profile-edit.html:
	1	Replace single resume display with resume list
	2	Add "Name this resume" input after upload
	3	Show list of saved resumes with:
	•	Resume name
	•	Created date
	•	"Set as Default" button
	•	"Delete" button
	4	Keep backward compatibility: if no resumes in table, show legacy single resume
UI Mockup:

Your Resumes
┌────────────────────────────────────────────────┐
│ Growth PM Resume          ★ Default            │
│ Uploaded Dec 15, 2024     [Set Default] [Delete]│
├────────────────────────────────────────────────┤
│ Enterprise PM Resume                           │
│ Uploaded Dec 20, 2024     [Set Default] [Delete]│
├────────────────────────────────────────────────┤
│ [+ Upload New Resume]                          │
└────────────────────────────────────────────────┘

Phase 5: Frontend - Analyze Page
Modify frontend/analyze.html:
	1	Add resume selector dropdown in profile banner area
	2	Load resume list on page load
	3	Default to user's default resume
	4	Selected resume used in analysis request
UI Placement: After profile banner, before JD input

Using resume: [Growth PM Resume ▼]

File Changes Summary
File
Change
backend/migrations/create_user_resumes_table.sql
New - SQL schema
backend/backend.py
Add 4 resume CRUD endpoints
frontend/js/supabase-client.js
Add resume management methods
frontend/profile-edit.html
Resume list UI, upload with naming
frontend/analyze.html
Resume selector dropdown

Migration Strategy
	1	New users: Use new multi-resume flow
	2	Existing users: On first visit to profile page, migrate userProfile.resume to user_resumes table as their default resume
	3	Fallback: If no resumes in table, check localStorage for legacy resume

Scope Estimate
	•	Database: ~30 min
	•	Backend endpoints: ~1 hour
	•	Supabase client: ~30 min
	•	Profile page UI: ~2 hours
	•	Analyze page selector: ~1 hour
	•	Testing: ~1 hour
Total: ~6 hours

Questions for User
	1	Should there be a limit on number of resumes? (Suggest: 5 max)
	2	When uploading, require naming immediately or auto-name based on date?
	3	Show resume preview/details in list, or just name + date?
