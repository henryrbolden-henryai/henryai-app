// ============================================================================
// HENRYAI CALENDAR INTEGRATION
// Generates personalized .ics calendar events with human-friendly reminders
// ============================================================================

/**
 * Generate personalized message based on context
 */
function generatePersonalizedMessage(context) {
    const {
        firstName = 'Hey',
        company = 'this company',
        role = 'this role',
        fitScore = 0,
        actionType = 'apply', // apply, follow-up, interview, research
        strengths = [],
        gaps = []
    } = context;

    const greeting = `${firstName},\n\n`;
    let message = '';

    // Choose message based on action type and fit score
    if (actionType === 'apply') {
        if (fitScore >= 85) {
            message = `This is your shot. You're ${fitScore}% fit for this role and ${strengths[0] || 'your background'} is exactly what ${company} needs.\n\nTake 30 minutes right now to nail this application. Lead with your strongest experience and show them you can operate at this level.\n\nYou've got this. 🚀`;
        } else if (fitScore >= 70) {
            message = `You're ${fitScore}% fit for this role. Solid, but you'll need to position strategically.\n\nEmphasize ${strengths[0] || 'your unique experience'}. That's your edge over other candidates.\n\nTake your time on this application. Quality over speed.`;
        } else {
            message = `This one's a stretch at ${fitScore}% fit, but here's why you should still apply:\n\n${strengths[0] || 'Your experience'} gives you an angle most candidates don't have. Play that up in your cover letter.\n\nDon't spend more than 15 minutes on this. It's a numbers game at this level.`;
        }
    } else if (actionType === 'follow-up') {
        message = `It's been 2 weeks since you applied to ${company}. Time to follow up.\n\nHere's why you're not being pushy: ${fitScore}% fit candidates don't grow on trees. You're doing them a favor by staying visible.\n\nSend that follow-up email today. Use the template we built.`;
    } else if (actionType === 'interview') {
        message = `Your interview with ${company} is coming up. Let's make sure you're ready.\n\nKey talking points:\n${strengths.slice(0, 3).map(s => `• ${s}`).join('\n')}\n\nYou know this cold. Just be yourself and show strategic thinking.`;
    } else if (actionType === 'research') {
        message = `Time to do your homework on ${company}.\n\nSpend 15 minutes finding:\n• Recent news/product launches\n• Hiring manager's background\n• Company pain points you can solve\n\nThis research will pay off in your application and interviews.`;
    } else {
        message = `Time to take action on your ${company} application.\n\n${fitScore}% fit. ${strengths[0] || 'Your background is strong'}. You can do this.`;
    }

    return greeting + message + '\n\n— HenryAI';
}

/**
 * Generate .ics calendar file content
 */
function generateICSFile(eventData) {
    const {
        title,
        description,
        startTime, // Date object
        endTime,   // Date object
        location = '',
        reminder = 60 // minutes before
    } = eventData;

    // Format dates for ICS (YYYYMMDDTHHMMSS in UTC)
    const formatICSDate = (date) => {
        const pad = (n) => n.toString().padStart(2, '0');
        const year = date.getUTCFullYear();
        const month = pad(date.getUTCMonth() + 1);
        const day = pad(date.getUTCDate());
        const hour = pad(date.getUTCHours());
        const minute = pad(date.getUTCMinutes());
        const second = pad(date.getUTCSeconds());
        return `${year}${month}${day}T${hour}${minute}${second}Z`;
    };

    const now = new Date();
    const dtstamp = formatICSDate(now);
    const dtstart = formatICSDate(startTime);
    const dtend = formatICSDate(endTime);
    
    // Generate unique ID
    const uid = `henryai-${Date.now()}@henryai.app`;

    // Format description (escape special characters)
    const escapeICS = (str) => {
        return str.replace(/\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
    };

    const icsContent = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//HenryAI//Job Search Assistant//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        `UID:${uid}`,
        `DTSTAMP:${dtstamp}`,
        `DTSTART:${dtstart}`,
        `DTEND:${dtend}`,
        `SUMMARY:${escapeICS(title)}`,
        `DESCRIPTION:${escapeICS(description)}`,
        location ? `LOCATION:${escapeICS(location)}` : '',
        'STATUS:CONFIRMED',
        'SEQUENCE:0',
        'BEGIN:VALARM',
        'TRIGGER:-PT' + reminder + 'M',
        'ACTION:DISPLAY',
        `DESCRIPTION:${escapeICS(title)}`,
        'END:VALARM',
        'END:VEVENT',
        'END:VCALENDAR'
    ].filter(line => line).join('\r\n');

    return icsContent;
}

/**
 * Download ICS file
 */
function downloadICS(icsContent, filename) {
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Parse timing text to Date object
 */
function parseTimingToDate(timing) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 14, 0, 0); // 2 PM today
    
    if (timing.toLowerCase().includes('today')) {
        return today;
    } else if (timing.toLowerCase().includes('tomorrow')) {
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        return tomorrow;
    } else if (timing.toLowerCase().includes('this week')) {
        const thisWeek = new Date(today);
        thisWeek.setDate(thisWeek.getDate() + 3); // 3 days from now
        return thisWeek;
    } else if (timing.toLowerCase().includes('2 weeks') || timing.toLowerCase().includes('two weeks')) {
        const twoWeeks = new Date(today);
        twoWeeks.setDate(twoWeeks.getDate() + 14);
        return twoWeeks;
    } else {
        return today;
    }
}

/**
 * Create action plan calendar event
 */
function createActionPlanEvent(actionItem, analysisData) {
    const firstName = analysisData._candidate_first_name || 'Hey';
    const company = analysisData._company_name || 'Company';
    const role = analysisData.role_title || 'Role';
    const fitScore = analysisData.fit_score || 0;
    const strengths = analysisData.positioning_strategy?.emphasize || [];

    // Determine action type from text
    let actionType = 'apply';
    if (actionItem.toLowerCase().includes('follow up') || actionItem.toLowerCase().includes('follow-up')) {
        actionType = 'follow-up';
    } else if (actionItem.toLowerCase().includes('research') || actionItem.toLowerCase().includes('find')) {
        actionType = 'research';
    } else if (actionItem.toLowerCase().includes('interview') || actionItem.toLowerCase().includes('prep')) {
        actionType = 'interview';
    }

    // Generate personalized message
    const personalizedNote = generatePersonalizedMessage({
        firstName,
        company,
        role,
        fitScore,
        actionType,
        strengths
    });

    // Parse timing from action item
    const timing = actionItem.split(':')[0] || 'today'; // Extract "TODAY" or "TOMORROW" prefix
    const startTime = parseTimingToDate(timing);
    const endTime = new Date(startTime);
    endTime.setHours(endTime.getHours() + 1); // 1 hour duration

    // Build event title
    const actionText = actionItem.replace(/^(TODAY|TOMORROW|THIS WEEK):\s*/i, '').substring(0, 50);
    const title = `⚡ HenryAI Alert: ${actionText}`;

    // Build full description
    const description = [
        personalizedNote,
        '',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        `📋 ACTION ITEM: ${actionItem}`,
        '',
        `🎯 ROLE: ${role}`,
        `🏢 COMPANY: ${company}`,
        `📊 FIT SCORE: ${fitScore}%`,
        '',
        strengths.length > 0 ? '💪 YOUR STRENGTHS:' : '',
        ...strengths.slice(0, 3).map(s => `• ${s}`),
        '',
        'Need help? Review your full analysis package in HenryAI.'
    ].filter(line => line !== null && line !== undefined).join('\n');

    return {
        title,
        description,
        startTime,
        endTime,
        location: '',
        reminder: 60
    };
}

/**
 * Create tracker follow-up event
 */
function createTrackerReminderEvent(application) {
    const firstName = application.analysis?._candidate_first_name || 'Hey';
    const company = application.company || 'Company';
    const role = application.role || 'Role';
    const fitScore = application.fitScore || 0;
    const status = application.status || 'To Apply';
    const strengths = application.analysis?.positioning_strategy?.emphasize || [];

    // Determine timing based on status
    let startTime = new Date();
    let actionType = 'apply';

    if (status === 'To Apply') {
        // Today at 2pm
        startTime = new Date();
        startTime.setHours(14, 0, 0, 0);
        actionType = 'apply';
    } else if (status === 'Applied' || status === 'Package Generated') {
        // 2 weeks from now
        startTime = new Date();
        startTime.setDate(startTime.getDate() + 14);
        startTime.setHours(14, 0, 0, 0);
        actionType = 'follow-up';
    } else if (status === 'Interviewing') {
        // Tomorrow (day before interview)
        startTime = new Date();
        startTime.setDate(startTime.getDate() + 1);
        startTime.setHours(18, 0, 0, 0); // 6 PM for evening prep
        actionType = 'interview';
    } else {
        // Default: today at 2pm
        startTime = new Date();
        startTime.setHours(14, 0, 0, 0);
    }

    const endTime = new Date(startTime);
    endTime.setHours(endTime.getHours() + 1);

    // Generate personalized message
    const personalizedNote = generatePersonalizedMessage({
        firstName,
        company,
        role,
        fitScore,
        actionType,
        strengths
    });

    // Build event title
    let title = '';
    if (actionType === 'apply') {
        title = `⚡ HenryAI Alert: Apply to ${company}`;
    } else if (actionType === 'follow-up') {
        title = `⚡ HenryAI Alert: Follow up with ${company}`;
    } else if (actionType === 'interview') {
        title = `⚡ HenryAI Alert: Prep for ${company} interview`;
    } else {
        title = `⚡ HenryAI Alert: ${company} - ${role}`;
    }

    // Build full description
    const description = [
        personalizedNote,
        '',
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        `🎯 ROLE: ${role}`,
        `🏢 COMPANY: ${company}`,
        `📊 FIT SCORE: ${fitScore}%`,
        `📍 STATUS: ${status}`,
        '',
        strengths.length > 0 ? '💪 YOUR STRENGTHS:' : '',
        ...strengths.slice(0, 3).map(s => `• ${s}`),
        '',
        'Check your HenryAI tracker for full details and next steps.'
    ].filter(line => line !== null && line !== undefined).join('\n');

    return {
        title,
        description,
        startTime,
        endTime,
        location: '',
        reminder: 60
    };
}

// Export functions (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generatePersonalizedMessage,
        generateICSFile,
        downloadICS,
        parseTimingToDate,
        createActionPlanEvent,
        createTrackerReminderEvent
    };
}
