# CONTEXT-AWARE RESUME SELECTION — IMPLEMENTATION GUIDE

## **OVERVIEW**

Allow users to upload and manage multiple resumes (up to 5), label them for easy reference, and select which resume to use when analyzing a job. This maintains strategic control while supporting multi-track job searches.

**Status:** Planned for Phase 2 (requires authentication infrastructure)

**Dependencies:**
- User authentication system (Supabase Auth)
- Backend database persistence for user data
- File storage (Supabase Storage)

---

## **BACKEND CHANGES**

### **1. Database Schema Updates**

**Current State:**
- Single `resume_text` field per user
- Single `resume_filename` field

**New State:**
- Array of resume objects with metadata

```python
# Update User model or create new Resume model
class Resume(BaseModel):
    id: str  # UUID
    user_id: str
    label: str  # User-defined label (e.g., "Technical Recruiting")
    filename: str
    file_path: str  # Storage location
    resume_text: str  # Parsed content
    uploaded_at: datetime
    is_primary: bool  # Default resume for new analyses

# Update User model
class User(BaseModel):
    # ... existing fields ...
    resumes: List[Resume] = []
    primary_resume_id: Optional[str] = None
```

**Migration Strategy:**
- Existing users with `resume_text`: convert to single Resume object with label "Primary Resume", set `is_primary=True`
- New users: empty `resumes` array

---

### **2. API Endpoints**

#### **Upload Resume**
```python
@router.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile,
    label: str = Form(...),  # User-provided label
    set_as_primary: bool = Form(False),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse a new resume.

    Validation:
    - Max 5 resumes per user
    - Label must be unique for this user
    - Label max 50 characters
    - File must be .pdf or .docx
    """

    # Validate resume count
    if len(current_user.resumes) >= 5:
        raise HTTPException(400, "Maximum 5 resumes allowed")

    # Validate unique label
    if any(r.label == label for r in current_user.resumes):
        raise HTTPException(400, f"Label '{label}' already exists")

    # Parse resume
    resume_text = await parse_resume(file)

    # Create Resume object
    new_resume = Resume(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        label=label,
        filename=file.filename,
        file_path=f"resumes/{current_user.id}/{uuid.uuid4()}_{file.filename}",
        resume_text=resume_text,
        uploaded_at=datetime.now(),
        is_primary=set_as_primary or len(current_user.resumes) == 0
    )

    # If setting as primary, unset other primary flags
    if new_resume.is_primary:
        for resume in current_user.resumes:
            resume.is_primary = False

    # Add to user's resumes
    current_user.resumes.append(new_resume)
    await save_user(current_user)

    return {"resume_id": new_resume.id, "label": new_resume.label}
```

#### **List Resumes**
```python
@router.get("/api/resume/list")
async def list_resumes(current_user: User = Depends(get_current_user)):
    """
    Get all resumes for current user.
    """
    return {
        "resumes": [
            {
                "id": r.id,
                "label": r.label,
                "filename": r.filename,
                "uploaded_at": r.uploaded_at,
                "is_primary": r.is_primary
            }
            for r in current_user.resumes
        ]
    }
```

#### **Update Resume Label**
```python
@router.put("/api/resume/{resume_id}/label")
async def update_resume_label(
    resume_id: str,
    new_label: str = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Update the label for a specific resume.
    """
    resume = next((r for r in current_user.resumes if r.id == resume_id), None)
    if not resume:
        raise HTTPException(404, "Resume not found")

    # Validate unique label
    if any(r.label == new_label and r.id != resume_id for r in current_user.resumes):
        raise HTTPException(400, f"Label '{new_label}' already exists")

    resume.label = new_label
    await save_user(current_user)

    return {"success": True}
```

#### **Set Primary Resume**
```python
@router.put("/api/resume/{resume_id}/set-primary")
async def set_primary_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Set a resume as the primary/default.
    """
    resume = next((r for r in current_user.resumes if r.id == resume_id), None)
    if not resume:
        raise HTTPException(404, "Resume not found")

    # Unset all primary flags
    for r in current_user.resumes:
        r.is_primary = False

    # Set this one as primary
    resume.is_primary = True
    current_user.primary_resume_id = resume_id
    await save_user(current_user)

    return {"success": True}
```

#### **Delete Resume**
```python
@router.delete("/api/resume/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a resume. Cannot delete if it's the only resume.
    """
    if len(current_user.resumes) == 1:
        raise HTTPException(400, "Cannot delete your only resume")

    resume = next((r for r in current_user.resumes if r.id == resume_id), None)
    if not resume:
        raise HTTPException(404, "Resume not found")

    # Remove from list
    current_user.resumes = [r for r in current_user.resumes if r.id != resume_id]

    # If deleted resume was primary, set another as primary
    if resume.is_primary and current_user.resumes:
        current_user.resumes[0].is_primary = True
        current_user.primary_resume_id = current_user.resumes[0].id

    await save_user(current_user)

    return {"success": True}
```

#### **Get Resume Content**
```python
@router.get("/api/resume/{resume_id}/content")
async def get_resume_content(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the full text content of a specific resume.
    Used when analyzing a job.
    """
    resume = next((r for r in current_user.resumes if r.id == resume_id), None)
    if not resume:
        raise HTTPException(404, "Resume not found")

    return {
        "resume_id": resume.id,
        "label": resume.label,
        "resume_text": resume.resume_text
    }
```

---

### **3. Job Analysis Flow Updates**

Update the job analysis endpoint to accept a `resume_id` parameter:

```python
@router.post("/api/analyze-job")
async def analyze_job(
    job_description: str = Body(...),
    resume_id: Optional[str] = Body(None),  # New parameter
    current_user: User = Depends(get_current_user)
):
    """
    Analyze job fit using specified resume.
    If resume_id not provided, use primary resume.
    """

    # Determine which resume to use
    if resume_id:
        resume = next((r for r in current_user.resumes if r.id == resume_id), None)
        if not resume:
            raise HTTPException(404, "Resume not found")
    else:
        # Use primary resume
        resume = next((r for r in current_user.resumes if r.is_primary), None)
        if not resume:
            raise HTTPException(400, "No resume on file")

    # Run analysis with selected resume
    analysis_result = await analyze_job_fit(
        resume_text=resume.resume_text,
        job_description=job_description,
        # ... other parameters ...
    )

    # Include resume info in response
    analysis_result["resume_used"] = {
        "id": resume.id,
        "label": resume.label
    }

    return analysis_result
```

---

## **FRONTEND CHANGES**

### **1. Profile/Onboarding Page Updates**

**Current Flow:**
- Upload single resume
- Show filename and upload date

**New Flow:**
- Upload multiple resumes with labels
- Manage resume library
- Set primary resume

**HTML Structure:**
```html
<!-- Replace existing single resume upload -->
<section id="resume-library">
    <h2>Your Resumes</h2>
    <p class="helper-text">Upload up to 5 resumes for different job tracks. Label them so you can easily select the right one when analyzing a role.</p>

    <!-- Resume List -->
    <div id="resume-list">
        <!-- Dynamically populated -->
    </div>

    <!-- Add Resume Button -->
    <button id="add-resume-btn" class="secondary-btn">
        <span>+ Add Resume</span>
    </button>

    <!-- Add Resume Modal -->
    <div id="add-resume-modal" class="modal" style="display: none;">
        <div class="modal-content">
            <h3>Add Resume</h3>
            <form id="add-resume-form">
                <label>Resume Label *</label>
                <input
                    type="text"
                    id="resume-label"
                    placeholder="e.g., Technical Recruiting, Executive Search, GTM"
                    maxlength="50"
                    required
                />
                <p class="helper-text">Give this resume a name so you can identify it later (max 50 characters)</p>

                <label>Upload Resume *</label>
                <input
                    type="file"
                    id="resume-file"
                    accept=".pdf,.docx"
                    required
                />

                <label>
                    <input type="checkbox" id="set-as-primary" />
                    Set as primary resume (used by default for new analyses)
                </label>

                <div class="modal-actions">
                    <button type="button" id="cancel-add-resume">Cancel</button>
                    <button type="submit" class="primary-btn">Upload Resume</button>
                </div>
            </form>
        </div>
    </div>
</section>
```

**Resume Card Component:**
```html
<!-- Generated for each resume -->
<div class="resume-card" data-resume-id="{resume_id}">
    <div class="resume-header">
        <h3 class="resume-label">{label}</h3>
        {#if is_primary}
        <span class="primary-badge">Primary</span>
        {/if}
    </div>

    <div class="resume-meta">
        <span class="filename">{filename}</span>
        <span class="upload-date">{uploaded_at}</span>
    </div>

    <div class="resume-actions">
        <button class="edit-label-btn" data-resume-id="{resume_id}">
            Edit Label
        </button>
        {#if !is_primary}
        <button class="set-primary-btn" data-resume-id="{resume_id}">
            Set as Primary
        </button>
        {/if}
        {#if total_resumes > 1}
        <button class="delete-resume-btn" data-resume-id="{resume_id}">
            Delete
        </button>
        {/if}
    </div>
</div>
```

---

### **2. JavaScript Implementation**

**Load Resume Library:**
```javascript
async function loadResumeLibrary() {
    try {
        const response = await fetch('/api/resume/list', {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (!response.ok) throw new Error('Failed to load resumes');

        const data = await response.json();
        renderResumeLibrary(data.resumes);

        // Show/hide add button based on count
        const addBtn = document.getElementById('add-resume-btn');
        if (data.resumes.length >= 5) {
            addBtn.style.display = 'none';
        } else {
            addBtn.style.display = 'block';
        }

    } catch (error) {
        console.error('Error loading resumes:', error);
        showToast('Failed to load resumes', 'error');
    }
}

function renderResumeLibrary(resumes) {
    const container = document.getElementById('resume-list');

    if (resumes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No resumes uploaded yet. Add your first resume to get started.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = resumes.map(resume => `
        <div class="resume-card" data-resume-id="${resume.id}">
            <div class="resume-header">
                <h3 class="resume-label">${escapeHtml(resume.label)}</h3>
                ${resume.is_primary ? '<span class="primary-badge">Primary</span>' : ''}
            </div>

            <div class="resume-meta">
                <span class="filename">${escapeHtml(resume.filename)}</span>
                <span class="upload-date">${formatDate(resume.uploaded_at)}</span>
            </div>

            <div class="resume-actions">
                <button class="edit-label-btn" data-resume-id="${resume.id}">
                    Edit Label
                </button>
                ${!resume.is_primary ? `
                    <button class="set-primary-btn" data-resume-id="${resume.id}">
                        Set as Primary
                    </button>
                ` : ''}
                ${resumes.length > 1 ? `
                    <button class="delete-resume-btn" data-resume-id="${resume.id}">
                        Delete
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');

    // Attach event listeners
    attachResumeCardListeners();
}
```

**Add Resume:**
```javascript
document.getElementById('add-resume-btn').addEventListener('click', () => {
    document.getElementById('add-resume-modal').style.display = 'flex';
});

document.getElementById('cancel-add-resume').addEventListener('click', () => {
    document.getElementById('add-resume-modal').style.display = 'none';
    document.getElementById('add-resume-form').reset();
});

document.getElementById('add-resume-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const label = document.getElementById('resume-label').value.trim();
    const file = document.getElementById('resume-file').files[0];
    const setAsPrimary = document.getElementById('set-as-primary').checked;

    if (!label || !file) {
        showToast('Please provide both a label and resume file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('label', label);
    formData.append('set_as_primary', setAsPrimary);

    try {
        const response = await fetch('/api/resume/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upload resume');
        }

        showToast('Resume uploaded successfully', 'success');
        document.getElementById('add-resume-modal').style.display = 'none';
        document.getElementById('add-resume-form').reset();

        // Reload library
        await loadResumeLibrary();

    } catch (error) {
        console.error('Error uploading resume:', error);
        showToast(error.message, 'error');
    }
});
```

**Edit Label:**
```javascript
function attachResumeCardListeners() {
    // Edit Label
    document.querySelectorAll('.edit-label-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const resumeId = btn.dataset.resumeId;
            const card = btn.closest('.resume-card');
            const currentLabel = card.querySelector('.resume-label').textContent;

            const newLabel = prompt('Enter new label:', currentLabel);
            if (!newLabel || newLabel === currentLabel) return;

            try {
                const response = await fetch(`/api/resume/${resumeId}/label`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${getToken()}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ new_label: newLabel })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to update label');
                }

                showToast('Label updated', 'success');
                await loadResumeLibrary();

            } catch (error) {
                console.error('Error updating label:', error);
                showToast(error.message, 'error');
            }
        });
    });

    // Set Primary
    document.querySelectorAll('.set-primary-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const resumeId = btn.dataset.resumeId;

            try {
                const response = await fetch(`/api/resume/${resumeId}/set-primary`, {
                    method: 'PUT',
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                });

                if (!response.ok) throw new Error('Failed to set primary resume');

                showToast('Primary resume updated', 'success');
                await loadResumeLibrary();

            } catch (error) {
                console.error('Error setting primary:', error);
                showToast('Failed to set primary resume', 'error');
            }
        });
    });

    // Delete
    document.querySelectorAll('.delete-resume-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const resumeId = btn.dataset.resumeId;
            const card = btn.closest('.resume-card');
            const label = card.querySelector('.resume-label').textContent;

            if (!confirm(`Delete "${label}"? This cannot be undone.`)) return;

            try {
                const response = await fetch(`/api/resume/${resumeId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to delete resume');
                }

                showToast('Resume deleted', 'success');
                await loadResumeLibrary();

            } catch (error) {
                console.error('Error deleting resume:', error);
                showToast(error.message, 'error');
            }
        });
    });
}
```

---

### **3. Job Analysis Page Updates**

**Resume Selection UI:**
```html
<!-- Add before job description textarea -->
<section id="resume-selection">
    <label>Which resume should I use for this analysis?</label>
    <select id="selected-resume" required>
        <!-- Dynamically populated -->
    </select>
    <p class="helper-text">
        I'll use this resume to calculate fit and generate tailored outputs.
    </p>
</section>
```

**Load Resume Options:**
```javascript
async function loadResumeOptions() {
    try {
        const response = await fetch('/api/resume/list', {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (!response.ok) throw new Error('Failed to load resumes');

        const data = await response.json();
        const select = document.getElementById('selected-resume');

        if (data.resumes.length === 0) {
            select.innerHTML = '<option value="">No resumes on file</option>';
            select.disabled = true;
            return;
        }

        // Populate dropdown
        select.innerHTML = data.resumes.map(resume => `
            <option
                value="${resume.id}"
                ${resume.is_primary ? 'selected' : ''}
            >
                ${escapeHtml(resume.label)}${resume.is_primary ? ' (Primary)' : ''}
            </option>
        `).join('');

    } catch (error) {
        console.error('Error loading resume options:', error);
        showToast('Failed to load resumes', 'error');
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadResumeOptions);
```

**Update Analysis Request:**
```javascript
async function analyzeJob() {
    const jobDescription = document.getElementById('job-description').value;
    const selectedResumeId = document.getElementById('selected-resume').value;

    if (!jobDescription || !selectedResumeId) {
        showToast('Please provide both a job description and select a resume', 'error');
        return;
    }

    try {
        const response = await fetch('/api/analyze-job', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_description: jobDescription,
                resume_id: selectedResumeId
            })
        });

        if (!response.ok) throw new Error('Analysis failed');

        const result = await response.json();

        // Show which resume was used
        showToast(`Analysis complete using ${result.resume_used.label}`, 'success');

        // Display results
        displayAnalysisResults(result);

    } catch (error) {
        console.error('Error analyzing job:', error);
        showToast('Analysis failed', 'error');
    }
}
```

---

## **CSS ADDITIONS**

```css
/* Resume Library */
#resume-library {
    margin: 2rem 0;
}

#resume-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.resume-card {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    background: var(--card-background);
}

.resume-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.resume-label {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0;
}

.primary-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: var(--primary-color);
    color: white;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.resume-meta {
    display: flex;
    gap: 1.5rem;
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.resume-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.resume-actions button {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.875rem;
}

.resume-actions button:hover {
    background: var(--hover-background);
}

.delete-resume-btn {
    color: var(--error-color);
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-muted);
}

/* Modal */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
}

.modal-content h3 {
    margin-top: 0;
}

.modal-content form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.modal-actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}

/* Resume Selection */
#resume-selection {
    margin-bottom: 1.5rem;
}

#selected-resume {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 1rem;
}

.helper-text {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}
```

---

## **VALIDATION RULES**

1. **Max 5 resumes per user** — Block uploads beyond this limit
2. **Unique labels per user** — No duplicate labels allowed
3. **Label max 50 characters** — Enforce on frontend and backend
4. **Cannot delete only resume** — Must have at least 1 resume on file
5. **File types** — Only .pdf and .docx allowed
6. **Primary resume required** — Always have exactly one resume marked as primary

---

## **MIGRATION CHECKLIST**

- [ ] Update database schema (add Resume model or update User model)
- [ ] Create migration script for existing users
- [ ] Implement all backend endpoints
- [ ] Add frontend resume library UI
- [ ] Add resume selection to job analysis flow
- [ ] Update CSS with new styles
- [ ] Test upload flow (single resume)
- [ ] Test upload flow (multiple resumes)
- [ ] Test label editing
- [ ] Test primary resume switching
- [ ] Test deletion (cannot delete last resume)
- [ ] Test job analysis with selected resume
- [ ] Test validation rules (max 5, unique labels, etc.)
- [ ] Update onboarding documentation

---

## **FUTURE ENHANCEMENTS (POST-LAUNCH)**

- Resume comparison view (side-by-side)
- Bulk label updates
- Resume versioning (upload new version of same label)
- Analytics (which resume gets used most often)
- Smart suggestions based on job description keywords

---

**This implementation guide is ready for when authentication infrastructure is in place.**
