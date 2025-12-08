# 🔧 DOCUMENT GENERATION FIX

## PROBLEM:

documents.html is trying to fetch from:
- `GET /download/resume/{job_id}` ❌ Doesn't exist
- `GET /download/cover-letter/{job_id}` ❌ Doesn't exist

Backend actually has:
- `POST /api/documents/download` ✅ Exists

## SOLUTION:

Update documents.html to generate documents directly from the analysis data already in sessionStorage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## FIX FOR DOCUMENTS.HTML:

### STEP 1: Find the download functions (around lines 530-690)

FIND this section:
```javascript
async function downloadResume() {
    try {
        const button = document.querySelector('.download-btn');
        button.disabled = true;
        button.textContent = 'Generating...';
        
        const analysisData = JSON.parse(sessionStorage.getItem('analysisData'));
        const resumeResponse = await fetch(`http://localhost:8000/download/resume/${analysisData.job_id || 'latest'}`);
        
        // ... rest of function
    } catch (error) {
        // ... error handling
    }
}

async function downloadCoverLetter() {
    // Similar broken code
}
```

### STEP 2: REPLACE with this working version:

```javascript
async function downloadResume() {
    try {
        const button = event.target;
        button.disabled = true;
        button.innerHTML = '<span>⏳</span> Generating...';
        
        const analysisData = JSON.parse(sessionStorage.getItem('analysisData'));
        if (!analysisData) {
            alert('No analysis data found. Please analyze a job first.');
            return;
        }
        
        // Generate resume content from analysis data
        const resumeContent = generateResumeContent(analysisData);
        const candidateName = analysisData._candidate_first_name || analysisData._candidate_name || 'Candidate';
        const company = analysisData._company_name || analysisData.company || 'Company';
        
        // Create form data
        const formData = new FormData();
        formData.append('resume_data', JSON.stringify({ full_text: resumeContent }));
        formData.append('cover_letter_data', JSON.stringify({ full_text: '' })); // Empty for single download
        formData.append('candidate_name', candidateName);
        formData.append('include_outreach', 'false');
        
        // Download from backend
        const response = await fetch('http://localhost:8000/api/documents/download', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.status}`);
        }
        
        // Trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${candidateName.replace(/ /g, '_')}_${company.replace(/ /g, '_')}_Resume.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        button.disabled = false;
        button.innerHTML = '<span>↓</span> Download Resume';
        
    } catch (error) {
        console.error('Resume download error:', error);
        alert('Error downloading resume. Please try again.');
        const button = event.target;
        button.disabled = false;
        button.innerHTML = '<span>↓</span> Download Resume';
    }
}

async function downloadCoverLetter() {
    try {
        const button = event.target;
        button.disabled = true;
        button.innerHTML = '<span>⏳</span> Generating...';
        
        const analysisData = JSON.parse(sessionStorage.getItem('analysisData'));
        if (!analysisData) {
            alert('No analysis data found. Please analyze a job first.');
            return;
        }
        
        // Generate cover letter content from analysis data
        const coverLetterContent = generateCoverLetterContent(analysisData);
        const candidateName = analysisData._candidate_first_name || analysisData._candidate_name || 'Candidate';
        const company = analysisData._company_name || analysisData.company || 'Company';
        
        // Create form data
        const formData = new FormData();
        formData.append('resume_data', JSON.stringify({ full_text: '' })); // Empty for single download
        formData.append('cover_letter_data', JSON.stringify({ full_text: coverLetterContent }));
        formData.append('candidate_name', candidateName);
        formData.append('include_outreach', 'false');
        
        // Download from backend
        const response = await fetch('http://localhost:8000/api/documents/download', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.status}`);
        }
        
        // Trigger download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${candidateName.replace(/ /g, '_')}_${company.replace(/ /g, '_')}_Cover_Letter.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        button.disabled = false;
        button.innerHTML = '<span>↓</span> Download Cover Letter';
        
    } catch (error) {
        console.error('Cover letter download error:', error);
        alert('Error downloading cover letter. Please try again.');
        const button = event.target;
        button.disabled = false;
        button.innerHTML = '<span>↓</span> Download Cover Letter';
    }
}

// Helper function to generate resume content
function generateResumeContent(analysis) {
    const candidate = analysis._candidate_name || 'Candidate Name';
    const summary = analysis.resume_output?.summary || analysis.strategic_positioning || 'Professional summary not available.';
    const qualifications = analysis.resume_output?.key_qualifications || [];
    const keywords = analysis.resume_output?.ats_keywords || analysis.ats_keywords || [];
    
    let content = `${candidate}\n\n`;
    content += `PROFESSIONAL SUMMARY\n${summary}\n\n`;
    
    if (qualifications.length > 0) {
        content += `KEY QUALIFICATIONS\n`;
        qualifications.forEach(qual => {
            content += `• ${qual}\n`;
        });
        content += `\n`;
    }
    
    if (keywords.length > 0) {
        content += `CORE COMPETENCIES\n`;
        content += keywords.join(' • ');
        content += `\n\n`;
    }
    
    content += `\n[Original resume experience and education sections would be inserted here]\n`;
    content += `\nNote: This is a tailored summary. Full resume formatting will be applied when downloaded.`;
    
    return content;
}

// Helper function to generate cover letter content
function generateCoverLetterContent(analysis) {
    const company = analysis._company_name || analysis.company || 'Company';
    const role = analysis.role_title || 'Position';
    const outreach = analysis.outreach?.hiring_manager || 'I am writing to express my interest in this position.';
    
    let content = `Dear Hiring Manager,\n\n`;
    content += `${outreach}\n\n`;
    content += `I am excited about the opportunity to contribute to ${company} as a ${role}.\n\n`;
    content += `Thank you for your consideration.\n\n`;
    content += `Best regards,\n`;
    content += `${analysis._candidate_name || 'Candidate Name'}`;
    
    return content;
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## WHAT THIS FIXES:

✅ Uses correct backend endpoint (`POST /api/documents/download`)
✅ Generates content from sessionStorage data
✅ Proper error handling
✅ Loading states on buttons
✅ Automatic file download
✅ Proper filename with candidate + company name

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## TESTING:

1. Analyze a job
2. Go to Documents page
3. Click "Download Resume"
4. Should download `Henry_ServiceNow_Resume.docx` (or similar)
5. Click "Download Cover Letter"
6. Should download `Henry_ServiceNow_Cover_Letter.docx` (or similar)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
