/**
 * Admin Alert Panel
 *
 * A dedicated panel for admin users (hb@henryhq.ai) to:
 * - View incoming feedback, bug reports, and meeting requests
 * - Reply directly to users via email
 * - Track response times and resolution status
 *
 * Position: Bottom-left corner (opposite Hey Henry)
 * Only visible to admin users
 */

(function() {
    'use strict';

    // Configuration
    const API_BASE = window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';
    const ADMIN_EMAIL = 'hb@henryhq.ai';
    const POLL_INTERVAL = 30000; // 30 seconds

    // State
    let isAdmin = false;
    let notifications = [];
    let currentNotification = null;
    let pollInterval = null;
    let panelOpen = false;

    // Alert type config
    const ALERT_TYPES = {
        'bug': { emoji: '🐛', label: 'Bug Report', color: '#ef4444' },
        'feature_request': { emoji: '💡', label: 'Feature Request', color: '#f59e0b' },
        'ux_issue': { emoji: '🎨', label: 'UX Issue', color: '#8b5cf6' },
        'praise': { emoji: '🎉', label: 'Praise', color: '#10b981' },
        'general': { emoji: '💬', label: 'Feedback', color: '#6b7280' },
        'meeting_request': { emoji: '📅', label: 'Meeting Request', color: '#3b82f6' }
    };

    // Inject styles
    const styles = `
        .admin-alerts-fab {
            position: fixed;
            bottom: 24px;
            left: 24px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            z-index: 9998;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .admin-alerts-fab:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 24px rgba(102, 126, 234, 0.5);
        }

        .admin-alerts-fab svg {
            width: 24px;
            height: 24px;
            fill: white;
        }

        .admin-alerts-badge {
            position: absolute;
            top: -4px;
            right: -4px;
            background: #ef4444;
            color: white;
            font-size: 12px;
            font-weight: 600;
            min-width: 20px;
            height: 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 6px;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
        }

        .admin-alerts-panel {
            position: fixed;
            bottom: 90px;
            left: 24px;
            width: 420px;
            max-height: 600px;
            background: #111111;
            border: 1px solid #333;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: none;
            flex-direction: column;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .admin-alerts-panel.open {
            display: flex;
        }

        .admin-alerts-header {
            padding: 16px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .admin-alerts-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: white;
        }

        .admin-alerts-close {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: background 0.2s;
        }

        .admin-alerts-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .admin-alerts-list {
            flex: 1;
            overflow-y: auto;
            max-height: 300px;
        }

        .admin-alerts-empty {
            padding: 40px 20px;
            text-align: center;
            color: #666;
        }

        .admin-alerts-empty svg {
            width: 48px;
            height: 48px;
            fill: #444;
            margin-bottom: 12px;
        }

        .admin-alert-item {
            padding: 16px 20px;
            border-bottom: 1px solid #222;
            cursor: pointer;
            transition: background 0.2s;
        }

        .admin-alert-item:hover {
            background: #1a1a1a;
        }

        .admin-alert-item.selected {
            background: #1e1e2e;
            border-left: 3px solid #667eea;
        }

        .admin-alert-item.unread {
            background: #1a1a2e;
        }

        .admin-alert-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }

        .admin-alert-type {
            font-size: 14px;
            font-weight: 600;
            color: white;
        }

        .admin-alert-time {
            font-size: 12px;
            color: #666;
            margin-left: auto;
        }

        .admin-alert-from {
            font-size: 13px;
            color: #999;
            margin-bottom: 4px;
        }

        .admin-alert-preview {
            font-size: 13px;
            color: #ccc;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .admin-alert-detail {
            padding: 20px;
            border-top: 1px solid #333;
            background: #0a0a0a;
        }

        .admin-alert-detail-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }

        .admin-alert-detail-type {
            font-size: 24px;
        }

        .admin-alert-detail-info h4 {
            margin: 0 0 4px;
            font-size: 15px;
            color: white;
        }

        .admin-alert-detail-info p {
            margin: 0;
            font-size: 13px;
            color: #888;
        }

        .admin-alert-detail-content {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }

        .admin-alert-detail-content p {
            margin: 0;
            font-size: 14px;
            color: #ddd;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        .admin-alert-detail-meta {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #666;
            margin-bottom: 16px;
        }

        .admin-alert-screenshot {
            margin-bottom: 16px;
        }

        .admin-alert-screenshot img {
            max-width: 100%;
            border-radius: 8px;
            border: 1px solid #333;
        }

        .admin-alert-screenshot-link {
            color: #667eea;
            font-size: 13px;
            text-decoration: none;
        }

        .admin-alert-screenshot-link:hover {
            text-decoration: underline;
        }

        .admin-alert-reply {
            margin-top: 16px;
        }

        .admin-alert-reply label {
            display: block;
            font-size: 13px;
            color: #888;
            margin-bottom: 8px;
        }

        .admin-alert-reply textarea {
            width: 100%;
            min-height: 80px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            color: white;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            box-sizing: border-box;
        }

        .admin-alert-reply textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .admin-alert-actions {
            display: flex;
            gap: 10px;
            margin-top: 12px;
        }

        .admin-alert-btn {
            flex: 1;
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .admin-alert-btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .admin-alert-btn-primary:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .admin-alert-btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .admin-alert-btn-secondary {
            background: #333;
            color: #ccc;
        }

        .admin-alert-btn-secondary:hover {
            background: #444;
        }

        .admin-alert-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }

        .admin-alert-status.new {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
        }

        .admin-alert-status.replied {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
        }

        .admin-alert-status.resolved {
            background: rgba(107, 114, 128, 0.2);
            color: #9ca3af;
        }

        .admin-alert-sending {
            text-align: center;
            padding: 20px;
            color: #888;
        }

        .admin-alert-url-box {
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }

        .admin-alert-url-label {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .admin-alert-url-link {
            color: #60a5fa;
            font-size: 13px;
            text-decoration: none;
            word-break: break-all;
            display: block;
        }

        .admin-alert-url-link:hover {
            text-decoration: underline;
            color: #93c5fd;
        }

        .admin-alert-scope-box {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }

        .admin-alert-scope-box.multi-page {
            background: rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.3);
        }

        .admin-alert-scope-label {
            font-size: 11px;
            color: #f59e0b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .admin-alert-scope-text {
            font-size: 13px;
            color: #fcd34d;
        }

        .admin-alert-success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            color: #34d399;
            margin-top: 12px;
        }

        @media (max-width: 500px) {
            .admin-alerts-panel {
                left: 10px;
                right: 10px;
                width: auto;
                bottom: 80px;
            }

            .admin-alerts-fab {
                left: 16px;
                bottom: 16px;
                width: 48px;
                height: 48px;
            }
        }
    `;

    // Inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Check if user is admin
    async function checkAdminStatus() {
        if (typeof HenryAuth === 'undefined') return false;

        try {
            const user = await HenryAuth.getUser();
            if (user?.email?.toLowerCase() === ADMIN_EMAIL.toLowerCase()) {
                isAdmin = true;
                return true;
            }
        } catch (e) {
            console.warn('Admin check failed:', e);
        }
        return false;
    }

    // Fetch notifications from backend
    async function fetchNotifications() {
        if (!isAdmin) return;

        try {
            const user = await HenryAuth.getUser();
            const response = await fetch(`${API_BASE}/api/admin/notifications?user_email=${encodeURIComponent(user.email)}`);
            if (!response.ok) return;

            const data = await response.json();
            if (data.notifications) {
                notifications = data.notifications;
                updateBadge();
                if (panelOpen) {
                    renderNotificationList();
                }
            }
        } catch (e) {
            console.warn('Failed to fetch notifications:', e);
        }
    }

    // Update badge count
    function updateBadge() {
        const badge = document.querySelector('.admin-alerts-badge');
        const unreadCount = notifications.filter(n => !n.read).length;

        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    // Format relative time
    function formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }

    // Render notification list
    function renderNotificationList() {
        const list = document.querySelector('.admin-alerts-list');
        if (!list) return;

        if (notifications.length === 0) {
            list.innerHTML = `
                <div class="admin-alerts-empty">
                    <svg viewBox="0 0 24 24"><path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/></svg>
                    <p>No alerts yet</p>
                </div>
            `;
            return;
        }

        list.innerHTML = notifications.map(n => {
            const type = ALERT_TYPES[n.feedback_type] || ALERT_TYPES.general;
            const isSelected = currentNotification?.id === n.id;
            const statusClass = n.replied_at ? 'replied' : (n.read ? '' : 'unread');

            return `
                <div class="admin-alert-item ${isSelected ? 'selected' : ''} ${statusClass}" data-id="${n.id}">
                    <div class="admin-alert-header">
                        <span>${type.emoji}</span>
                        <span class="admin-alert-type">${type.label}</span>
                        ${!n.read ? '<span class="admin-alert-status new">New</span>' : ''}
                        ${n.replied_at ? '<span class="admin-alert-status replied">Replied</span>' : ''}
                        <span class="admin-alert-time">${formatRelativeTime(n.created_at)}</span>
                    </div>
                    <div class="admin-alert-from">${n.from_name || 'Someone'} (${n.from_email})</div>
                    <div class="admin-alert-preview">${n.summary || n.full_content?.substring(0, 100) || 'No details'}</div>
                </div>
            `;
        }).join('');

        // Add click handlers
        list.querySelectorAll('.admin-alert-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = item.dataset.id;
                const notification = notifications.find(n => n.id === id);
                if (notification) {
                    selectNotification(notification);
                }
            });
        });
    }

    // Select and show notification detail
    function selectNotification(notification) {
        currentNotification = notification;

        // Mark as read if not already
        if (!notification.read) {
            markAsRead(notification.id);
        }

        renderNotificationList();
        renderNotificationDetail();
    }

    // Helper to extract and display page URL
    function getPageUrlHtml(notification) {
        // Try to get URL from context or full_content
        let pageUrl = null;

        // Check if URL is in the full_content (from the scope info we added)
        if (notification.full_content) {
            const urlMatch = notification.full_content.match(/Page URL: (https?:\/\/[^\s\n]+)/);
            if (urlMatch) {
                pageUrl = urlMatch[1];
            } else {
                // Try alternate format
                const altMatch = notification.full_content.match(/Reported from: [^(]+\((https?:\/\/[^)]+)\)/);
                if (altMatch) {
                    pageUrl = altMatch[1];
                }
            }
        }

        if (!pageUrl) return '';

        return `
            <div class="admin-alert-url-box">
                <div class="admin-alert-url-label">🔗 Page URL</div>
                <a href="${pageUrl}" target="_blank" class="admin-alert-url-link">${pageUrl}</a>
            </div>
        `;
    }

    // Helper to extract and display scope info for bugs
    function getScopeInfoHtml(notification) {
        if (notification.feedback_type !== 'bug') return '';

        // Check for scope info in content
        if (!notification.full_content) return '';

        const isMultiPage = notification.full_content.includes('Scope: Affects MULTIPLE pages') ||
            notification.full_content.includes('multiple') ||
            notification.full_content.includes('both pages');

        // Extract user's scope response
        const userNoteMatch = notification.full_content.match(/User noted: ([^\n]+)/);
        const scopeMatch = notification.full_content.match(/Scope: ([^\n]+)/);

        let scopeText = '';
        if (userNoteMatch) {
            scopeText = userNoteMatch[1];
        } else if (scopeMatch) {
            scopeText = scopeMatch[1];
        }

        if (!scopeText) return '';

        return `
            <div class="admin-alert-scope-box ${isMultiPage ? 'multi-page' : ''}">
                <div class="admin-alert-scope-label">${isMultiPage ? '⚠️ Multiple Pages Affected' : '📍 Scope'}</div>
                <div class="admin-alert-scope-text">${scopeText}</div>
            </div>
        `;
    }

    // Render notification detail
    function renderNotificationDetail() {
        const detailContainer = document.querySelector('.admin-alert-detail');
        if (!detailContainer || !currentNotification) {
            if (detailContainer) detailContainer.innerHTML = '';
            return;
        }

        const n = currentNotification;
        const type = ALERT_TYPES[n.feedback_type] || ALERT_TYPES.general;

        detailContainer.innerHTML = `
            <div class="admin-alert-detail-header">
                <span class="admin-alert-detail-type">${type.emoji}</span>
                <div class="admin-alert-detail-info">
                    <h4>${n.from_name || 'Someone'}</h4>
                    <p>${n.from_email}</p>
                </div>
            </div>

            <div class="admin-alert-detail-content">
                <p>${n.full_content || n.summary || 'No details provided'}</p>
            </div>

            <div class="admin-alert-detail-meta">
                <span>📍 ${n.current_page || 'Unknown page'}</span>
                <span>🕐 ${formatRelativeTime(n.created_at)}</span>
            </div>

            ${getPageUrlHtml(n)}
            ${getScopeInfoHtml(n)}

            ${n.screenshot_url ? `
                <div class="admin-alert-screenshot">
                    <a href="${n.screenshot_url}" target="_blank" class="admin-alert-screenshot-link">
                        📎 View Screenshot
                    </a>
                </div>
            ` : ''}

            <div class="admin-alert-reply">
                <label>Reply to ${n.from_name || n.from_email}:</label>
                <textarea id="adminReplyText" placeholder="Type your response..."></textarea>

                <div class="admin-alert-actions">
                    <button class="admin-alert-btn admin-alert-btn-secondary" onclick="adminAlerts.markResolved('${n.id}')">
                        Mark Resolved
                    </button>
                    <button class="admin-alert-btn admin-alert-btn-primary" onclick="adminAlerts.sendReply('${n.id}')">
                        Send Reply
                    </button>
                </div>

                <div id="adminReplyStatus"></div>
            </div>
        `;
    }

    // Mark notification as read
    async function markAsRead(notificationId) {
        try {
            const user = await HenryAuth.getUser();
            await fetch(`${API_BASE}/api/admin/notifications/${notificationId}/read?user_email=${encodeURIComponent(user.email)}`, {
                method: 'POST'
            });

            // Update local state
            const notification = notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.read = true;
            }
            updateBadge();
        } catch (e) {
            console.warn('Failed to mark as read:', e);
        }
    }

    // Mark notification as resolved
    async function markResolved(notificationId) {
        try {
            const user = await HenryAuth.getUser();
            await fetch(`${API_BASE}/api/admin/notifications/${notificationId}/resolve?user_email=${encodeURIComponent(user.email)}`, {
                method: 'POST'
            });

            // Remove from list and clear detail
            notifications = notifications.filter(n => n.id !== notificationId);
            currentNotification = null;
            renderNotificationList();
            renderNotificationDetail();
            updateBadge();
        } catch (e) {
            console.warn('Failed to mark as resolved:', e);
        }
    }

    // Send reply email
    async function sendReply(notificationId) {
        const textarea = document.getElementById('adminReplyText');
        const statusDiv = document.getElementById('adminReplyStatus');
        const replyText = textarea?.value?.trim();

        if (!replyText) {
            statusDiv.innerHTML = '<p style="color: #ef4444;">Please enter a reply message.</p>';
            return;
        }

        const notification = notifications.find(n => n.id === notificationId);
        if (!notification) return;

        // Disable button and show sending state
        const sendBtn = document.querySelector('.admin-alert-btn-primary');
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
        }

        try {
            const user = await HenryAuth.getUser();
            const response = await fetch(`${API_BASE}/api/admin/notifications/${notificationId}/reply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    admin_email: user.email,
                    reply_text: replyText,
                    to_email: notification.from_email,
                    to_name: notification.from_name
                })
            });

            const result = await response.json();

            if (result.success) {
                statusDiv.innerHTML = '<div class="admin-alert-success">Reply sent successfully!</div>';
                textarea.value = '';

                // Update local state
                notification.replied_at = new Date().toISOString();
                renderNotificationList();

                // Auto-close detail after 2 seconds
                setTimeout(() => {
                    currentNotification = null;
                    renderNotificationDetail();
                }, 2000);
            } else {
                statusDiv.innerHTML = `<p style="color: #ef4444;">Failed to send: ${result.error || 'Unknown error'}</p>`;
            }
        } catch (e) {
            statusDiv.innerHTML = `<p style="color: #ef4444;">Error: ${e.message}</p>`;
        } finally {
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send Reply';
            }
        }
    }

    // Toggle panel
    function togglePanel() {
        const panel = document.querySelector('.admin-alerts-panel');
        if (!panel) return;

        panelOpen = !panelOpen;
        panel.classList.toggle('open', panelOpen);

        if (panelOpen) {
            fetchNotifications();
            renderNotificationList();
        }
    }

    // Create the UI
    function createUI() {
        // Create FAB
        const fab = document.createElement('button');
        fab.className = 'admin-alerts-fab';
        fab.innerHTML = `
            <svg viewBox="0 0 24 24">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z"/>
            </svg>
            <span class="admin-alerts-badge" style="display: none;">0</span>
        `;
        fab.addEventListener('click', togglePanel);

        // Create panel
        const panel = document.createElement('div');
        panel.className = 'admin-alerts-panel';
        panel.innerHTML = `
            <div class="admin-alerts-header">
                <h3>Alerts</h3>
                <button class="admin-alerts-close">&times;</button>
            </div>
            <div class="admin-alerts-list"></div>
            <div class="admin-alert-detail"></div>
        `;

        panel.querySelector('.admin-alerts-close').addEventListener('click', togglePanel);

        document.body.appendChild(fab);
        document.body.appendChild(panel);
    }

    // Initialize
    async function init() {
        // Wait for auth to be ready
        if (typeof HenryAuth === 'undefined') {
            setTimeout(init, 500);
            return;
        }

        const isAdminUser = await checkAdminStatus();
        if (!isAdminUser) {
            console.log('Admin alerts: Not an admin user');
            return;
        }

        console.log('Admin alerts: Initializing...');
        createUI();
        fetchNotifications();

        // Start polling
        pollInterval = setInterval(fetchNotifications, POLL_INTERVAL);
    }

    // Expose functions globally for onclick handlers
    window.adminAlerts = {
        sendReply,
        markResolved,
        toggle: togglePanel
    };

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
