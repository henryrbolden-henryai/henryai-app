// ========================================================================
// EMPATHY & ADAPTIVE MESSAGING SYSTEM
// ========================================================================
// These functions adapt tone and messaging based on the user's emotional state,
// timeline urgency, and confidence level captured during profile onboarding.
//
// INTEGRATION INSTRUCTIONS:
// 1. Add these functions to tracker.html inside the existing <script> section
// 2. Replace the existing renderDailyPulse() function with the new version below
// 3. The system will automatically load userProfile from localStorage and adapt messaging
// ========================================================================

/**
 * Load user profile with situation data
 */
function getUserProfile() {
    try {
        const profile = localStorage.getItem('userProfile');
        return profile ? JSON.parse(profile) : null;
    } catch (err) {
        console.error('Error loading user profile:', err);
        return null;
    }
}

/**
 * Get empathetic greeting based on emotional state and timeline
 */
function getPulseGreeting(profile, apps) {
    if (!profile || !profile.situation) {
        // Fallback if no profile data
        const activeCount = apps.filter(a => STATUSES[a.status]?.active).length;
        return `You have ${activeCount} active application${activeCount !== 1 ? 's' : ''}. Here's what needs attention today.`;
    }

    const { holding_up, timeline } = profile.situation;
    const activeCount = apps.filter(a => ['Hot', 'Active'].includes(a.status || getStatusLabel(a))).length;
    const hotCount = apps.filter(a => (a.status || getStatusLabel(a)) === 'Hot').length;
    
    // Count interviews this week
    const interviewsThisWeek = apps.filter(a => {
        if (!a.interviewDate) return false;
        const date = new Date(a.interviewDate);
        const today = new Date();
        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        return date >= today && date <= weekFromNow;
    }).length;

    // Crushed state (override everything)
    if (holding_up === 'crushed') {
        if (activeCount === 0) {
            return "I know this is brutal. Let's get some applications moving.";
        }
        return `I know this is brutal. You have ${activeCount} active application${activeCount !== 1 ? 's' : ''}. Let's make sure each one gets follow-up.`;
    }

    // Desperate + urgent
    if (holding_up === 'desperate' && timeline === 'urgent') {
        if (interviewsThisWeek > 0) {
            return `Let's focus. You have ${interviewsThisWeek} interview${interviewsThisWeek !== 1 ? 's' : ''} this week and ${hotCount} hot application${hotCount !== 1 ? 's' : ''}. Here's your priority list.`;
        }
        return `Let's focus. You have ${activeCount} application${activeCount !== 1 ? 's' : ''} moving. Here's what needs attention today.`;
    }

    // Desperate (without urgent timeline)
    if (holding_up === 'desperate') {
        return `You've got ${activeCount} application${activeCount !== 1 ? 's' : ''} moving. Let's make sure nothing slips through the cracks.`;
    }

    // Stressed + active
    if (holding_up === 'stressed' && timeline === 'active') {
        return `You've got ${activeCount} application${activeCount !== 1 ? 's' : ''} moving. Here's what needs attention so nothing slips.`;
    }

    // Stressed (without active timeline)
    if (holding_up === 'stressed') {
        return `You have ${activeCount} active application${activeCount !== 1 ? 's' : ''}. Here's what's happening in your pipeline.`;
    }

    // Zen + exploring
    if (holding_up === 'zen' && timeline === 'exploring') {
        return `You've got ${activeCount} active application${activeCount !== 1 ? 's' : ''}. No rush—let's keep the bar high.`;
    }

    // Zen (without exploring)
    if (holding_up === 'zen') {
        return `${activeCount} application${activeCount !== 1 ? 's are' : ' is'} active. Things are looking solid.`;
    }

    // Clock ticking (urgent timeline)
    if (timeline === 'clock_ticking') {
        return `Time matters. You have ${activeCount} application${activeCount !== 1 ? 's' : ''} active. Here's what requires immediate action.`;
    }

    // Urgent timeline
    if (timeline === 'urgent') {
        return `You have ${activeCount} active application${activeCount !== 1 ? 's' : ''}. Let's prioritize what moves fastest.`;
    }

    // Default (covers other combinations)
    return `You have ${activeCount} active application${activeCount !== 1 ? 's' : ''}. Here's what needs attention today.`;
}

/**
 * Get adaptive priority action message based on situation
 */
function getAdaptivePriorityAction(profile, apps, upcomingInterviews, followUpsDue, activeApps) {
    const { holding_up, timeline } = profile?.situation || {};

    // Priority 1: Upcoming interviews
    if (upcomingInterviews.length > 0) {
        const nextInterview = upcomingInterviews[0];
        return `
            <span class="pulse-action-text">
                <strong>Priority:</strong> Prepare for your ${nextInterview.status.toLowerCase()} at ${nextInterview.company}
            </span>
            <a href="interview-intelligence.html" class="pulse-action-btn">Prep Now</a>
        `;
    }

    // Priority 2: Follow-ups
    if (followUpsDue.length > 0) {
        const oldestFollowUp = followUpsDue.sort((a, b) =>
            new Date(a.dateApplied || a.dateAdded) - new Date(b.dateApplied || b.dateAdded)
        )[0];
        const daysSince = getDaysSince(oldestFollowUp.dateApplied || oldestFollowUp.dateAdded);
        
        // Adapt tone based on timeline urgency
        let actionText = `<strong>Priority:</strong> Follow up with ${oldestFollowUp.company} (${daysSince} days since applying)`;
        if (timeline === 'clock_ticking' || timeline === 'urgent') {
            actionText = `<strong>Action needed:</strong> ${oldestFollowUp.company} hasn't responded in ${daysSince} days. Follow up now.`;
        }
        
        return `
            <span class="pulse-action-text">${actionText}</span>
            <button class="pulse-action-btn" onclick="navigateWithAnalysis('${oldestFollowUp.id}', 'outreach.html')">Draft Follow-up</button>
        `;
    }

    // Priority 3: Pipeline too thin
    if (activeApps.length < 5) {
        // Adapt messaging based on emotional state
        let suggestionText = '';
        let buttonText = 'Analyze New Role';
        
        if (holding_up === 'zen' && timeline === 'exploring') {
            suggestionText = `<strong>Suggestion:</strong> Your pipeline has ${activeApps.length} active apps. Room to add higher-quality matches.`;
        } else if (timeline === 'clock_ticking' || holding_up === 'desperate') {
            suggestionText = `<strong>Pipeline thin:</strong> Only ${activeApps.length} active apps. You need more options—broaden your search.`;
            buttonText = 'Find More Roles';
        } else if (holding_up === 'stressed' || timeline === 'urgent') {
            suggestionText = `<strong>Pipeline check:</strong> ${activeApps.length} active apps. Consider adding 2-3 more to strengthen your position.`;
        } else {
            suggestionText = `<strong>Suggestion:</strong> Your pipeline has ${activeApps.length} active apps. Consider adding more to increase your odds.`;
        }
        
        return `
            <span class="pulse-action-text">${suggestionText}</span>
            <a href="analyze.html" class="pulse-action-btn">${buttonText}</a>
        `;
    }

    // Priority 4: Pipeline healthy
    let encouragementText = '';
    if (holding_up === 'crushed' || holding_up === 'desperate') {
        encouragementText = `<strong>Keep pushing:</strong> ${activeApps.length} active applications. You're doing the work.`;
    } else if (holding_up === 'stressed') {
        encouragementText = `<strong>On track:</strong> ${activeApps.length} active applications in your pipeline. Keep the momentum going.`;
    } else {
        encouragementText = `<strong>Looking good!</strong> ${activeApps.length} active applications in your pipeline. Keep the momentum going.`;
    }
    
    return `
        <span class="pulse-action-text">${encouragementText}</span>
        <a href="analyze.html" class="pulse-action-btn">Add Another</a>
    `;
}

/**
 * MODIFIED renderDailyPulse function - REPLACE THE EXISTING ONE
 * This version integrates empathy-driven messaging
 */
function renderDailyPulse(apps) {
    const pulseEl = document.getElementById('dailyPulse');

    // Only show if there are active applications
    const activeApps = apps.filter(a => STATUSES[a.status]?.active);
    if (activeApps.length === 0) {
        pulseEl.style.display = 'none';
        return;
    }

    pulseEl.style.display = 'block';

    // Load user profile for adaptive messaging
    const profile = getUserProfile();

    // Set greeting based on profile situation (or fallback to time-based)
    if (profile && profile.situation) {
        const greeting = getPulseGreeting(profile, apps);
        document.getElementById('pulseGreeting').textContent = greeting;
    } else {
        // Fallback to time-based greeting if no profile
        const hour = new Date().getHours();
        let greeting = 'Good morning';
        if (hour >= 12 && hour < 17) greeting = 'Good afternoon';
        else if (hour >= 17) greeting = 'Good evening';
        document.getElementById('pulseGreeting').textContent = `${greeting}! Here's your job search pulse:`;
    }

    // Count active apps
    document.getElementById('pulseActive').textContent = activeApps.length;

    // Count follow-ups due (applied 5+ days ago without progress)
    const followUpsDue = apps.filter(a => {
        const daysSince = getDaysSince(a.dateApplied || a.dateAdded);
        return ['Applied', 'Reached Out'].includes(a.status) && daysSince >= 5;
    });
    const followUpStat = document.getElementById('pulseFollowUpStat');
    if (followUpsDue.length > 0) {
        document.getElementById('pulseFollowUps').textContent = followUpsDue.length;
        followUpStat.style.display = 'flex';
    } else {
        followUpStat.style.display = 'none';
    }

    // Count upcoming interviews (interviewing statuses)
    const interviewingStatuses = ['Recruiter Screen', 'Hiring Manager', 'Technical Round',
                                  'Panel Interview', 'Final Round', 'Executive Interview'];
    const upcomingInterviews = apps.filter(a => interviewingStatuses.includes(a.status));
    const interviewStat = document.getElementById('pulseInterviewStat');
    if (upcomingInterviews.length > 0) {
        document.getElementById('pulseInterviews').textContent = upcomingInterviews.length;
        interviewStat.style.display = 'flex';
    } else {
        interviewStat.style.display = 'none';
    }

    // Determine priority action with adaptive messaging
    const pulseAction = document.getElementById('pulseAction');
    const actionHtml = getAdaptivePriorityAction(profile, apps, upcomingInterviews, followUpsDue, activeApps);
    pulseAction.innerHTML = actionHtml;
}

// ========================================================================
// ADDITIONAL EMPATHY FUNCTIONS FOR PHASE 2
// ========================================================================
// These functions can be used when building the Analytics toggle view
// ========================================================================

/**
 * Get adaptive message for stalled applications
 */
function getStalledAppsMessage(stalledApps, situation) {
    if (!situation) {
        return `${stalledApps.length} application${stalledApps.length !== 1 ? 's' : ''} haven't moved in 14+ days. Consider following up or deprioritizing.`;
    }

    const { holding_up, timeline } = situation;
    const count = stalledApps.length;
    const days = Math.max(...stalledApps.map(a => getDaysSince(a.dateApplied || a.dateAdded)));

    if (holding_up === 'crushed') {
        return `${count} application${count !== 1 ? 's' : ''} ghosted you at ${days}+ days. That's on them, not you. Let's focus on the ones that are responding.`;
    }

    if (timeline === 'clock_ticking' || timeline === 'urgent') {
        const activeCount = stalledApps.filter(a => STATUSES[a.status]?.active).length;
        return `${count} application${count !== 1 ? 's' : ''} dead at ${days}+ days with no response. Recommendation: deprioritize and focus on the ${activeCount} that are actually moving.`;
    }

    if (holding_up === 'stressed') {
        return `${count} application${count !== 1 ? 's' : ''} stalled at ${days}+ days. Quick check: are these still worth pursuing, or should we focus energy elsewhere?`;
    }

    // Default (zen/exploring)
    return `${count} application${count !== 1 ? 's' : ''} stalled at ${days}+ days. Not urgent, but worth deciding—follow up or deprioritize?`;
}

/**
 * Get strategic recommendations based on profile situation
 * Returns array of recommendation objects with type, message, and action
 */
function getStrategicRecommendations(apps, profile) {
    if (!profile || !profile.situation) {
        return [];
    }

    const { holding_up, timeline, confidence } = profile.situation;
    const activeApps = apps.filter(a => STATUSES[a.status]?.active);
    const lowFitCount = activeApps.filter(a => a.fitScore && a.fitScore < 70).length;
    const recommendations = [];

    // Timeline-based pacing recommendations
    if (timeline === 'exploring') {
        recommendations.push({
            type: 'pacing',
            message: 'Target pace: 2-3 high-quality applications per week.',
            action: 'Focus on 85%+ fit roles'
        });
    } else if (timeline === 'active') {
        const pacingAdvice = activeApps.length < 5 ? 'Need to accelerate—find more matches' : 'On track';
        recommendations.push({
            type: 'pacing',
            message: 'Target pace: 5-7 applications per week.',
            action: pacingAdvice
        });
    } else if (timeline === 'urgent') {
        const pacingAdvice = activeApps.length < 8 ? 'Falling behind—broaden to 65%+ fit roles' : 'Keep pushing';
        recommendations.push({
            type: 'pacing',
            message: 'Target pace: 8-10 applications per week.',
            action: pacingAdvice
        });
    } else if (timeline === 'clock_ticking') {
        recommendations.push({
            type: 'pacing',
            message: 'Survival mode: apply to everything 60%+ fit.',
            action: 'Follow up on everything 7+ days old, reach out directly to hiring managers'
        });
    }

    // Fit quality check for stressed/desperate candidates
    if (lowFitCount > 5 && (holding_up === 'desperate' || holding_up === 'stressed')) {
        recommendations.push({
            type: 'quality',
            message: `You have ${lowFitCount} applications under 70% fit. You might be mass-applying out of anxiety.`,
            action: 'Let's recalibrate and focus on stronger matches'
        });
    }

    // Confidence-based positioning
    if (confidence === 'low' && activeApps.length > 0) {
        recommendations.push({
            type: 'mindset',
            message: 'You wouldn't have these interviews if they didn't think you could do the job.',
            action: 'Review your strengths before each interview'
        });
    }

    return recommendations;
}

/**
 * Get interview prep intro text adjusted for confidence level
 */
function getInterviewPrepIntro(confidence) {
    if (confidence === 'high') {
        return "You know your value. Here's how to frame your experience for this role:";
    }
    
    if (confidence === 'medium') {
        return "You're qualified for this role—here's proof. Use these talking points:";
    }
    
    if (confidence === 'low') {
        return "Listen: you wouldn't have made it to this interview if they didn't think you could do the job. Here's exactly what they need to hear:";
    }
    
    return "Here's how to position yourself for this role:";
}

// ========================================================================
// END OF EMPATHY MODIFICATIONS
// ========================================================================
