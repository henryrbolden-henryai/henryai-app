/**
 * Strengthen Your Resume - Flow Controller
 *
 * Handles the tag-based bullet verification and enhancement flow.
 * Reads from levelingData (bullet_audit), generates questions, collects answers,
 * and stores strengthenedData for document generation.
 */

// Configuration
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://henryai-app-production.up.railway.app';

// State
let levelingData = null;
let analysisData = null;
let flaggedBullets = [];
let questions = [];
let answers = {}; // { bullet_id: { answer, skipped } }
let currentQuestionIndex = 0;

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        // Check auth
        if (typeof supabase !== 'undefined') {
            const { data: { user } } = await supabase.auth.getUser();
            if (!user) {
                console.log('User not authenticated, continuing as guest');
            }
        }

        // Load data from sessionStorage with localStorage fallback (Safari compatibility)
        let levelingDataStr = sessionStorage.getItem('levelingData');
        let analysisDataStr = sessionStorage.getItem('analysisData');

        // Safari fallback: check localStorage if sessionStorage is empty
        if (!levelingDataStr) {
            levelingDataStr = localStorage.getItem('levelingData_backup');
            if (levelingDataStr) {
                console.log('Safari fallback: loaded levelingData from localStorage');
                sessionStorage.setItem('levelingData', levelingDataStr);
            }
        }
        if (!analysisDataStr) {
            analysisDataStr = localStorage.getItem('analysisData_backup');
            if (analysisDataStr) {
                console.log('Safari fallback: loaded analysisData from localStorage');
                sessionStorage.setItem('analysisData', analysisDataStr);
            }
        }

        if (!levelingDataStr && !analysisDataStr) {
            showError('No analysis data found. Please start from the beginning.');
            return;
        }

        if (levelingDataStr) {
            levelingData = JSON.parse(levelingDataStr);
        }

        if (analysisDataStr) {
            analysisData = JSON.parse(analysisDataStr);
        }

        // Extract flagged bullets from leveling data
        flaggedBullets = extractFlaggedBullets();

        if (flaggedBullets.length === 0) {
            // No issues - auto-skip
            showNoIssuesState();
            return;
        }

        // Generate questions for flagged bullets
        await generateQuestions();

    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to load analysis data. Please try again.');
    }
});

/**
 * Extract non-VERIFIED bullets from leveling data
 */
function extractFlaggedBullets() {
    const bullets = [];

    // Try to get from bullet_audit in leveling data
    if (levelingData && levelingData.bullet_audit) {
        for (const item of levelingData.bullet_audit) {
            const tag = (item.tag || 'VAGUE').toUpperCase();
            if (tag !== 'VERIFIED') {
                bullets.push({
                    id: item.id,
                    text: item.text,
                    section: item.section,
                    tag: tag,
                    issues: item.issues || [],
                    clarifies: item.clarifies || 'outcome'
                });
            }
        }
    }

    // Fallback: extract from red_flags_enhanced if bullet_audit not available
    if (bullets.length === 0 && levelingData && levelingData.red_flags_enhanced) {
        for (let i = 0; i < levelingData.red_flags_enhanced.length; i++) {
            const flag = levelingData.red_flags_enhanced[i];
            const sourceBullet = flag.source_bullets?.[0] || flag.instance || '';

            // Map red flag type to our tag system
            let tag = 'VAGUE';
            const flagType = (flag.type || '').toLowerCase();
            if (flagType.includes('inflation') || flagType.includes('mismatch')) {
                tag = 'RISKY';
            } else if (flagType.includes('credibility') || flagType.includes('implausible')) {
                tag = 'IMPLAUSIBLE';
            }

            bullets.push({
                id: `rf-${i}`,
                text: sourceBullet,
                section: 'From red flags',
                tag: tag,
                issues: [flag.why_it_matters || ''],
                clarifies: 'ownership'
            });
        }
    }

    // Sort by priority: IMPLAUSIBLE first, then RISKY, then VAGUE
    const priorityOrder = { 'IMPLAUSIBLE': 0, 'RISKY': 1, 'VAGUE': 2 };
    bullets.sort((a, b) => (priorityOrder[a.tag] || 2) - (priorityOrder[b.tag] || 2));

    // Limit to max 5 questions
    return bullets.slice(0, 5);
}

/**
 * Generate clarifying questions from API
 */
async function generateQuestions() {
    try {
        const response = await fetch(`${API_BASE}/api/strengthen/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                flagged_bullets: flaggedBullets,
                resume_context: {
                    role: levelingData?.current_level || analysisData?._role || 'Unknown',
                    tenure: levelingData?.years_in_role_type ? `${levelingData.years_in_role_type} years` : 'Unknown',
                    company_size: 'Unknown'
                }
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        questions = data.questions || [];

        if (questions.length === 0) {
            // No questions generated - auto-skip
            showNoIssuesState();
            return;
        }

        // Show the questions UI
        showQuestionsUI();

    } catch (error) {
        console.error('Error generating questions:', error);
        showError('Failed to generate questions. ' + error.message);
    }
}

/**
 * Show the questions UI
 */
function showQuestionsUI() {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('progressContainer').style.display = 'block';
    document.getElementById('submitSection').style.display = 'block';

    renderQuestions();
    updateProgress();
}

/**
 * Render all question cards
 */
function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';

    questions.forEach((q, index) => {
        const tagClass = q.tag.toLowerCase();
        const card = document.createElement('div');
        card.className = 'question-card';
        card.id = `question-${index}`;
        card.innerHTML = `
            <div class="bullet-context">
                <span class="tag ${tagClass}">${q.tag}</span>
                <p class="original-bullet">"${escapeHtml(q.original_bullet)}"</p>
                <p class="bullet-source">Needs clarification on: ${q.clarifies}</p>
            </div>

            <div class="question-section">
                <p class="question-text">${escapeHtml(q.question)}</p>
                <textarea
                    class="answer-input"
                    id="answer-${index}"
                    placeholder="Be specific. If you didn't own this, just say so."
                    data-bullet-id="${q.bullet_id}"
                    oninput="handleAnswerInput(${index})"
                ></textarea>
            </div>

            <div class="question-actions">
                <button class="btn btn-secondary" onclick="skipQuestion(${index})">
                    Skip - Keep Original
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

/**
 * Handle answer input
 */
function handleAnswerInput(index) {
    const textarea = document.getElementById(`answer-${index}`);
    const bulletId = textarea.dataset.bulletId;
    const value = textarea.value.trim();
    const card = document.getElementById(`question-${index}`);

    if (value) {
        answers[bulletId] = { answer: value, skipped: false };
        card.classList.add('active');
        card.classList.remove('completed');
    } else {
        delete answers[bulletId];
        card.classList.remove('active');
    }

    updateProgress();
}

/**
 * Skip a question
 */
function skipQuestion(index) {
    const textarea = document.getElementById(`answer-${index}`);
    const bulletId = textarea.dataset.bulletId;
    const card = document.getElementById(`question-${index}`);

    textarea.value = '';
    answers[bulletId] = { answer: '', skipped: true };
    card.classList.remove('active');
    card.classList.add('completed');

    updateProgress();
}

/**
 * Update progress indicators
 */
function updateProgress() {
    const total = questions.length;
    const answered = Object.values(answers).filter(a => a.answer && !a.skipped).length;
    const skipped = Object.values(answers).filter(a => a.skipped).length;
    const progress = total > 0 ? ((answered + skipped) / total) * 100 : 0;

    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('progressLabel').textContent = `${total} question${total !== 1 ? 's' : ''}`;
    document.getElementById('answeredCount').textContent = `${answered} answered, ${skipped} skipped`;

    // Update submit button
    const submitBtn = document.getElementById('submitBtn');
    if (answered > 0) {
        submitBtn.textContent = `Apply ${answered} Enhancement${answered !== 1 ? 's' : ''}`;
        submitBtn.disabled = false;
    } else if (skipped === total) {
        submitBtn.textContent = 'Continue Without Changes';
        submitBtn.disabled = false;
    } else {
        submitBtn.textContent = 'Answer Questions or Skip';
        submitBtn.disabled = true;
    }
}

/**
 * Submit answers and apply enhancements
 */
async function submitAnswers() {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
        // Build answers array for API
        const answersForApi = [];
        for (const q of questions) {
            const answerData = answers[q.bullet_id];
            if (answerData && answerData.answer && !answerData.skipped) {
                answersForApi.push({
                    bullet_id: q.bullet_id,
                    original_bullet: q.original_bullet,
                    answer: answerData.answer,
                    tag: q.tag
                });
            }
        }

        if (answersForApi.length === 0) {
            // All skipped - save and continue
            saveStrengthendData([], [], [], true, 'All questions skipped');
            proceedToLinkedIn();
            return;
        }

        // Call apply endpoint
        const response = await fetch(`${API_BASE}/api/strengthen/apply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                answers: answersForApi,
                resume_data: {
                    years_experience: levelingData?.years_experience || 0,
                    current_level: levelingData?.current_level || 'Unknown',
                    detected_function: levelingData?.detected_function || 'Unknown'
                }
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();

        // Save to sessionStorage
        saveStrengthendData(
            result.enhancements || [],
            result.declined || [],
            result.unresolved || [],
            false,
            null
        );

        // Show results
        showResults(result);

    } catch (error) {
        console.error('Error applying enhancements:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Try Again';
        showError('Failed to apply enhancements. ' + error.message);
    }
}

/**
 * Save strengthened data to sessionStorage
 */
function saveStrengthendData(enhancements, declined, unresolved, skipped, skipReason) {
    const answeredCount = Object.values(answers).filter(a => a.answer && !a.skipped).length;

    const strengthenedData = {
        status: skipped ? 'skipped' : 'completed',
        verified_enhancements: enhancements.map(e => ({
            bullet_id: e.bullet_id,
            original_bullet: e.original_bullet,
            enhanced_bullet: e.enhanced_bullet,
            confidence: e.confidence,
            changes_made: e.changes_made
        })),
        declined_items: declined,
        unresolved_items: unresolved,
        skipped_reason: skipReason,
        questions_asked: questions.length,
        questions_answered: answeredCount,
        timestamp: Date.now()
    };

    sessionStorage.setItem('strengthenedData', JSON.stringify(strengthenedData));
}

/**
 * Show results section
 */
function showResults(result) {
    // Hide questions
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('questionsContainer').innerHTML = '';
    document.getElementById('submitSection').style.display = 'none';

    // Show results
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.add('show');

    // Summary
    const enhanceCount = result.enhancements?.length || 0;
    const declinedCount = result.declined?.length || 0;
    document.getElementById('resultsSummary').textContent =
        `${enhanceCount} bullet${enhanceCount !== 1 ? 's' : ''} strengthened` +
        (declinedCount > 0 ? `, ${declinedCount} declined` : '');

    // Render enhancements
    const list = document.getElementById('enhancementsList');
    list.innerHTML = '';

    if (result.enhancements) {
        for (const e of result.enhancements) {
            const card = document.createElement('div');
            card.className = 'enhancement-card';
            card.innerHTML = `
                <div class="enhancement-label">Before</div>
                <div class="enhancement-before">${escapeHtml(e.original_bullet)}</div>
                <div class="enhancement-label">After</div>
                <div class="enhancement-after">${escapeHtml(e.enhanced_bullet)}</div>
                <div class="enhancement-why">${escapeHtml(e.changes_made)}</div>
            `;
            list.appendChild(card);
        }
    }

    if (result.enhancements?.length === 0) {
        list.innerHTML = '<p class="no-issues-text">No enhancements were made.</p>';
    }
}

/**
 * Skip all and continue
 */
function skipAll() {
    saveStrengthendData([], [], [], true, 'User skipped');
    proceedToLinkedIn();
}

/**
 * Proceed to LinkedIn analysis
 */
function proceedToLinkedIn() {
    // Check if LinkedIn data exists
    const linkedinData = sessionStorage.getItem('linkedinData');

    if (linkedinData) {
        // Profile already uploaded - go to analysis
        window.location.href = 'linkedin-analysis.html';
    } else {
        // No profile - prompt upload
        window.location.href = 'linkedin-upload.html';
    }
}

/**
 * Show no issues state
 */
function showNoIssuesState() {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('noIssuesState').style.display = 'block';

    // Auto-save as skipped
    saveStrengthendData([], [], [], true, 'No issues detected');
}

/**
 * Show error state
 */
function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('errorState').classList.add('show');
    document.getElementById('errorText').textContent = message;
}

/**
 * Retry loading
 */
function retryLoad() {
    window.location.reload();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
