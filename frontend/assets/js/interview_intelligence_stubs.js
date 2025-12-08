/**
 * Henry Job Search Engine - Interview Intelligence Frontend Integration
 * 
 * This file contains JavaScript functions to integrate Interview Intelligence
 * features into your existing frontend. These are STUB functions that call
 * the backend but don't modify any UI yet.
 * 
 * FEATURES:
 * 1. Parse interview transcript and extract/classify questions
 * 2. Get AI feedback on interview performance
 * 3. Generate personalized thank-you email
 */

// ============================================================================
// INTERVIEW INTELLIGENCE - QUESTION PARSING
// ============================================================================

/**
 * Upload or paste interview transcript and extract questions
 * Stores result in window.interviewQuestions
 * 
 * @param {string} transcriptText - Full interview transcript
 * @param {string} roleTitle - Role being interviewed for
 * @param {string} company - Company name
 * @param {Object} jdAnalysis - Optional JD analysis for context
 * @returns {Promise<Object>} Parsed questions, themes, and warnings
 */
async function parseInterviewTranscript(transcriptText, roleTitle, company, jdAnalysis = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interview/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript_text: transcriptText,
        role_title: roleTitle,
        company: company,
        jd_analysis: jdAnalysis
      })
    });
    
    if (!response.ok) {
      throw new Error(`Interview parsing failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store globally for other functions and future UI
    window.interviewQuestions = result.questions;
    window.interviewThemes = result.themes;
    window.interviewWarnings = result.warnings;
    
    console.log(`✅ Extracted ${result.questions.length} questions from interview`);
    console.log('Themes:', result.themes);
    if (result.warnings.length > 0) {
      console.warn('⚠️ Warnings:', result.warnings);
    }
    
    return result;
    
  } catch (error) {
    console.error('Error parsing interview:', error);
    alert('Could not parse interview transcript. Please try again.');
    return null;
  }
}

/**
 * Convenience function to handle file upload
 * Reads file content and calls parseInterviewTranscript
 * 
 * @param {File} file - Uploaded file
 * @param {string} roleTitle - Role title
 * @param {string} company - Company name
 * @param {Object} jdAnalysis - Optional JD analysis
 */
async function uploadInterviewTranscript(file, roleTitle, company, jdAnalysis = null) {
  try {
    const text = await file.text();
    return await parseInterviewTranscript(text, roleTitle, company, jdAnalysis);
  } catch (error) {
    console.error('Error reading file:', error);
    alert('Could not read file. Please try again.');
    return null;
  }
}

// ============================================================================
// INTERVIEW INTELLIGENCE - PERFORMANCE FEEDBACK
// ============================================================================

/**
 * Get AI feedback on interview performance
 * Stores result in window.interviewFeedback
 * 
 * @param {string} transcriptText - Full interview transcript
 * @param {string} roleTitle - Role being interviewed for
 * @param {string} company - Company name
 * @param {Array} questions - Questions array from parseInterviewTranscript
 * @returns {Promise<Object>} Feedback with scores, strengths, improvements, recommendations
 */
async function getInterviewFeedback(transcriptText, roleTitle, company, questions) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interview/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript_text: transcriptText,
        role_title: roleTitle,
        company: company,
        questions: questions
      })
    });
    
    if (!response.ok) {
      throw new Error(`Interview feedback failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store globally
    window.interviewFeedback = result;
    
    console.log(`✅ Interview Feedback - Overall Score: ${result.overall_score}/100`);
    console.log('Strengths:', result.strengths);
    console.log('Areas for improvement:', result.areas_for_improvement);
    console.log('Recommendations:', result.recommendations);
    
    return result;
    
  } catch (error) {
    console.error('Error getting interview feedback:', error);
    alert('Could not analyze interview performance. Please try again.');
    return null;
  }
}

/**
 * Complete interview analysis flow
 * Parse transcript → Get feedback in one call
 * 
 * @param {string} transcriptText - Full interview transcript
 * @param {string} roleTitle - Role title
 * @param {string} company - Company name
 * @param {Object} jdAnalysis - Optional JD analysis
 * @returns {Promise<Object>} Combined parse and feedback results
 */
async function analyzeInterviewPerformance(transcriptText, roleTitle, company, jdAnalysis = null) {
  console.log('🔍 Analyzing interview performance...');
  
  // Step 1: Parse and extract questions
  const parseResult = await parseInterviewTranscript(transcriptText, roleTitle, company, jdAnalysis);
  if (!parseResult) return null;
  
  // Step 2: Get performance feedback
  const feedbackResult = await getInterviewFeedback(
    transcriptText, 
    roleTitle, 
    company, 
    parseResult.questions
  );
  
  if (feedbackResult) {
    console.log('✅ Complete interview analysis ready');
    return {
      questions: parseResult.questions,
      themes: parseResult.themes,
      warnings: parseResult.warnings,
      feedback: feedbackResult
    };
  }
  
  return null;
}

// ============================================================================
// INTERVIEW INTELLIGENCE - THANK YOU EMAIL
// ============================================================================

/**
 * Generate personalized thank-you email based on interview
 * Stores result in window.thankYouEmail
 * 
 * @param {string} transcriptText - Full interview transcript
 * @param {string} roleTitle - Role title
 * @param {string} company - Company name
 * @param {string} interviewerName - Optional interviewer name
 * @param {Object} jdAnalysis - Optional JD analysis
 * @returns {Promise<Object>} Email subject, body, and key points used
 */
async function generateThankYouEmail(
  transcriptText, 
  roleTitle, 
  company, 
  interviewerName = null,
  jdAnalysis = null
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/interview/thank_you`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript_text: transcriptText,
        role_title: roleTitle,
        company: company,
        interviewer_name: interviewerName,
        jd_analysis: jdAnalysis
      })
    });
    
    if (!response.ok) {
      throw new Error(`Thank you email generation failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store globally
    window.thankYouEmail = result;
    
    console.log('✅ Thank-you email generated');
    console.log('Subject:', result.subject);
    console.log('Key points used:', result.key_points_used);
    
    return result;
    
  } catch (error) {
    console.error('Error generating thank-you email:', error);
    alert('Could not generate thank-you email. Please try again.');
    return null;
  }
}

// ============================================================================
// COMPLETE WORKFLOW FUNCTION
// ============================================================================

/**
 * Complete post-interview workflow
 * Parse → Analyze → Generate thank-you email
 * 
 * @param {string} transcriptText - Interview transcript
 * @param {string} roleTitle - Role title
 * @param {string} company - Company name
 * @param {string} interviewerName - Optional interviewer name
 * @param {Object} jdAnalysis - Optional JD analysis
 * @returns {Promise<Object>} All results combined
 */
async function completeInterviewReview(
  transcriptText,
  roleTitle,
  company,
  interviewerName = null,
  jdAnalysis = null
) {
  console.log('🚀 Starting complete interview review...');
  
  // Step 1: Analyze interview
  const analysis = await analyzeInterviewPerformance(transcriptText, roleTitle, company, jdAnalysis);
  if (!analysis) return null;
  
  // Step 2: Generate thank-you email
  const thankYou = await generateThankYouEmail(
    transcriptText,
    roleTitle,
    company,
    interviewerName,
    jdAnalysis
  );
  
  if (thankYou) {
    console.log('✅ Complete interview review ready');
    
    // All data now stored in window.* variables:
    // - window.interviewQuestions
    // - window.interviewThemes
    // - window.interviewWarnings
    // - window.interviewFeedback
    // - window.thankYouEmail
    
    return {
      questions: analysis.questions,
      themes: analysis.themes,
      warnings: analysis.warnings,
      feedback: analysis.feedback,
      thank_you: thankYou
    };
  }
  
  return null;
}

// ============================================================================
// INTEGRATION WITH EXISTING JD FLOW
// ============================================================================

/**
 * Hook into existing application flow
 * Call after user completes interview for a role they applied to
 */
async function processPostInterview(applicationId) {
  // Get application data
  const application = window.userApplications?.find(app => app.id === applicationId);
  if (!application) {
    console.error('Application not found');
    return;
  }
  
  // Get interview transcript (from user input - build UI for this)
  const transcriptText = window.currentInterviewTranscript;
  if (!transcriptText) {
    console.error('No interview transcript available');
    return;
  }
  
  // Get JD analysis if available
  const jdAnalysis = application.jd_analysis || window.currentJDAnalysis;
  
  // Run complete review
  const review = await completeInterviewReview(
    transcriptText,
    application.role_title,
    application.company,
    null, // interviewer name - get from user
    jdAnalysis
  );
  
  if (review) {
    // Store interview data with application
    application.interview_review = review;
    application.interview_date = new Date().toISOString();
    
    // Log outcome
    if (window.logApplicationOutcome) {
      await window.logApplicationOutcome(
        applicationId,
        'interview',
        `Completed interview - overall score: ${review.feedback.overall_score}/100`
      );
    }
    
    console.log('✅ Interview review saved to application');
  }
}

// ============================================================================
// DATA STRUCTURE EXAMPLES
// ============================================================================

/**
 * Example: Interview transcript structure
 */
const exampleTranscript = `
Interviewer: Thanks for joining us today. Let's start with you telling me about your experience scaling recruiting teams.

Candidate: Absolutely. At National Grid, I led a team of 12 recruiters across 15 countries. We achieved 95% hiring plan attainment while reducing time-to-fill by 22%. The key was implementing a data-driven framework that...

Interviewer: That's impressive. Can you tell me about a time when you had to deal with a difficult hiring situation?

Candidate: Sure. At Spotify during a hypergrowth phase, we were competing for engineering talent in a very tight market...
`;

/**
 * Example: Question classification output
 */
const exampleQuestionOutput = {
  question: "Can you tell me about a time when you had to deal with a difficult hiring situation?",
  type: "behavioral",
  competency_tag: "Problem Solving",
  difficulty: 3
};

/**
 * Example: Feedback output structure
 */
const exampleFeedback = {
  overall_score: 82,
  strengths: [
    "Strong use of specific metrics (95% attainment, 22% reduction)",
    "Clear STAR structure in behavioral responses",
    "Demonstrated strategic thinking about talent acquisition"
  ],
  areas_for_improvement: [
    "Some answers could be more concise (aim for 90-120 seconds)",
    "Could strengthen connection to company's specific challenges",
    "Missed opportunity to ask clarifying questions"
  ],
  delivery_feedback: {
    tone: "Professional and confident throughout. Good energy level.",
    pacing: "Generally good, but tended to speed up when discussing metrics. Practice pausing for emphasis.",
    clarity: "Very clear communication. Complex ideas explained well.",
    structure: "Strong STAR structure on behavioral questions. Technical answers well-organized."
  },
  recommendations: [
    "Prepare 2-3 questions about the company's specific recruiting challenges to show deeper preparation",
    "Practice the '90-second rule' - answer in 90 seconds, then ask if they want more detail",
    "Work on transitioning from answer to question: 'That's my experience with X. I'm curious - how does your team approach this?'"
  ]
};

/**
 * Example: Thank-you email output
 */
const exampleThankYou = {
  subject: "Thank you - Director of Talent Acquisition conversation",
  body: `Hi [Interviewer Name],

Thank you for taking the time to speak with me today about the Director of Talent Acquisition role at Stripe. I really enjoyed our conversation about scaling recruiting operations during hypergrowth phases and the unique challenges of competing for technical talent in today's market.

Our discussion about implementing data-driven hiring frameworks particularly resonated with my experience at Spotify, where we took a similar approach to optimize for both speed and quality. The challenge you mentioned around maintaining culture fit while scaling quickly is something I'm excited to tackle.

I'm very enthusiastic about the opportunity to bring my experience in building high-performing recruiting teams to Stripe. Please let me know if there's any additional information I can provide.

Best regards,
[Your Name]`,
  key_points_used: [
    "Scaling recruiting operations during hypergrowth",
    "Data-driven hiring frameworks",
    "Competing for technical talent",
    "Maintaining culture fit while scaling"
  ]
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/**
 * Example 1: Basic interview analysis
 */
async function exampleBasicAnalysis() {
  const transcript = document.getElementById('interview-transcript').value;
  const roleTitle = "Director of Talent Acquisition";
  const company = "Stripe";
  
  // Parse and analyze
  const result = await analyzeInterviewPerformance(transcript, roleTitle, company);
  
  console.log('Questions asked:', result.questions.length);
  console.log('Overall score:', result.feedback.overall_score);
  
  // Data is now available in:
  // - window.interviewQuestions
  // - window.interviewFeedback
}

/**
 * Example 2: Complete workflow with thank-you email
 */
async function exampleCompleteWorkflow() {
  const transcript = document.getElementById('interview-transcript').value;
  const roleTitle = "Director of Talent Acquisition";
  const company = "Stripe";
  const interviewer = "Sarah Chen";
  
  // Run complete review
  const review = await completeInterviewReview(
    transcript,
    roleTitle,
    company,
    interviewer,
    window.currentJDAnalysis // if available
  );
  
  if (review) {
    // Show feedback to user
    console.log(`Score: ${review.feedback.overall_score}/100`);
    console.log('Email ready:', review.thank_you.subject);
    
    // Future: Display in UI
    // displayInterviewFeedback(review);
  }
}

/**
 * Example 3: File upload handling
 */
async function exampleFileUpload() {
  const fileInput = document.getElementById('transcript-upload');
  const file = fileInput.files[0];
  
  if (file) {
    const result = await uploadInterviewTranscript(
      file,
      "Director of Talent Acquisition",
      "Stripe",
      window.currentJDAnalysis
    );
    
    if (result) {
      console.log('Transcript processed:', result.questions.length, 'questions found');
    }
  }
}

// ============================================================================
// UI INTEGRATION NOTES
// ============================================================================

/**
 * TO INTEGRATE INTERVIEW INTELLIGENCE:
 * 
 * 1. ADD INTERVIEW CAPTURE:
 *    - Text area for pasting transcript
 *    - File upload for .txt or .docx transcripts
 *    - Store in window.currentInterviewTranscript
 * 
 * 2. LINK TO APPLICATIONS:
 *    - When user has interview, capture which application
 *    - Store interview data with that application
 *    - Update stage to 'interview' or 'post-interview'
 * 
 * 3. CALL FUNCTIONS AT RIGHT TIME:
 *    - After transcript upload: parseInterviewTranscript()
 *    - User clicks "Analyze Performance": getInterviewFeedback()
 *    - User clicks "Generate Thank You": generateThankYouEmail()
 *    - Or use completeInterviewReview() for all at once
 * 
 * 4. BUILD UI TO DISPLAY (future):
 *    - Questions by type (behavioral, technical, etc.)
 *    - Feedback score with breakdown
 *    - Strengths and improvements
 *    - Recommendations
 *    - Thank-you email preview/copy
 * 
 * 5. STORE FOR LATER:
 *    - Add interview_review to application object
 *    - Track interview_date
 *    - Use for outcome logging
 *    - Include in strategy review data
 * 
 * The backend is ready - these stubs give you the plumbing.
 * Build UI when you're ready to show interview intelligence features.
 */
