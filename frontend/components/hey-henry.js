/**
 * Hey Henry - Floating Chat Widget
 * A contextually-aware AI assistant available from any page
 *
 * CORE INVARIANT (SYSTEM_CONTRACT.md §0):
 * "If it doesn't make the candidate better, no one wins."
 *
 * All responses must improve candidate decision quality.
 * Do not soften, inflate, or redirect unless it materially makes the candidate better.
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://henryai-app-production.up.railway.app';

    // Inject styles
    const styles = `
        /* Hey Henry Floating Widget */
        .ask-henry-fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            cursor: pointer;
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            background: transparent;
            border: none;
            padding: 0;
        }

        .ask-henry-fab:hover .ask-henry-logo {
            filter: drop-shadow(0 0 12px rgba(102, 126, 234, 0.6));
        }

        /* Hey Henry Tooltip - Now JavaScript controlled */
        .ask-henry-tooltip {
            position: absolute;
            right: 70px;
            top: 50%;
            transform: translateY(-50%);
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            color: #fff;
            padding: 10px 16px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            font-family: 'DM Sans', -apple-system, sans-serif;
            pointer-events: none;
        }

        .ask-henry-tooltip::after {
            content: '';
            position: absolute;
            right: -12px;
            top: 50%;
            transform: translateY(-50%);
            border: 6px solid transparent;
            border-left-color: #1a1a1a;
        }

        .ask-henry-tooltip.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(-50%) translateX(-5px);
        }

        .ask-henry-fab.active .ask-henry-tooltip {
            display: none;
        }

        .ask-henry-fab.hidden {
            transform: scale(0);
            opacity: 0;
            pointer-events: none;
        }

        .ask-henry-logo {
            width: 72px;
            height: 72px;
            transition: filter 0.3s ease;
        }

        /* Breathing animation for the logo */
        @keyframes breathe {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.12);
            }
        }

        .ask-henry-logo {
            animation: breathe 2.5s ease-in-out infinite;
        }

        /* When chat is open, use subtle pulse instead */
        .ask-henry-fab.active .ask-henry-logo {
            animation: pulse-active 1.5s ease-in-out infinite;
        }

        @keyframes pulse-active {
            0%, 100% {
                transform: scale(1);
                filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.4));
            }
            50% {
                transform: scale(1.08);
                filter: drop-shadow(0 0 16px rgba(102, 126, 234, 0.6));
            }
        }

        /* Chat Drawer */
        .ask-henry-drawer {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 380px;
            max-width: calc(100vw - 48px);
            height: 520px;
            max-height: calc(100vh - 100px);
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            transform: scale(0.9) translateY(20px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            transform-origin: bottom right;
            overflow: hidden;
        }

        .ask-henry-drawer.open {
            transform: scale(1) translateY(0);
            opacity: 1;
            pointer-events: auto;
        }

        /* Drawer Header */
        .ask-henry-header {
            padding: 18px 20px;
            background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ask-henry-title {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ask-henry-header-logo {
            flex-shrink: 0;
        }

        .ask-henry-title-text {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
        }

        .ask-henry-title-context {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-top: 2px;
        }

        .ask-henry-header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .ask-henry-close {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            color: #9ca3af;
            font-size: 1.1rem;
            cursor: pointer;
            padding: 6px 10px;
            border-radius: 8px;
            transition: all 0.2s;
            line-height: 1;
        }

        .ask-henry-close:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.1);
        }

        .ask-henry-expand {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            color: #9ca3af;
            cursor: pointer;
            padding: 6px;
            border-radius: 8px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .ask-henry-expand:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.1);
        }

        .ask-henry-expand svg {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }

        /* Expanded/Popped-out Mode */
        .ask-henry-drawer.expanded {
            width: 600px;
            max-width: calc(100vw - 48px);
            height: 80vh;
            max-height: calc(100vh - 100px);
        }

        .ask-henry-drawer.expanded .ask-henry-expand svg {
            transform: rotate(180deg);
        }

        /* Mobile-friendly expanded state */
        @media (max-width: 640px) {
            .ask-henry-drawer.expanded {
                width: calc(100vw - 24px);
                height: calc(100vh - 100px);
                bottom: 12px;
                right: 12px;
                border-radius: 16px;
            }
        }

        /* Messages Area */
        .ask-henry-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: linear-gradient(180deg, #0d0d0d 0%, #000000 100%);
        }

        .ask-henry-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .ask-henry-message.assistant {
            align-self: flex-start;
            background: linear-gradient(145deg, #2a2a2a 0%, #1a1a1a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #e5e5e5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .ask-henry-message.user {
            align-self: flex-end;
            background: linear-gradient(145deg, #4a4a4a 0%, #333333 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .ask-henry-message p {
            margin: 0 0 8px 0;
        }

        .ask-henry-message p:last-child {
            margin-bottom: 0;
        }

        .ask-henry-message ul, .ask-henry-message ol {
            margin: 8px 0;
            padding-left: 18px;
        }

        .ask-henry-message li {
            margin-bottom: 4px;
        }

        .ask-henry-message strong {
            color: #ffffff;
        }

        .ask-henry-message.user strong {
            color: #ffffff;
        }

        /* Timestamp */
        .ask-henry-timestamp {
            display: block;
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.4);
            margin-top: 6px;
            text-align: right;
        }

        .ask-henry-message.user .ask-henry-timestamp {
            color: rgba(255, 255, 255, 0.5);
        }

        /* Typing Indicator */
        .ask-henry-typing {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: linear-gradient(145deg, #2a2a2a 0%, #1a1a1a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            width: fit-content;
        }

        .ask-henry-typing .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #888888;
            animation: typing-bounce 1.4s infinite ease-in-out;
        }

        .ask-henry-typing .dot:nth-child(1) { animation-delay: 0s; }
        .ask-henry-typing .dot:nth-child(2) { animation-delay: 0.2s; }
        .ask-henry-typing .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        /* Quick Suggestions */
        .ask-henry-suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 0 16px 12px;
            background: transparent;
        }

        .ask-henry-suggestion {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.8rem;
            color: #a0a0a0;
            cursor: pointer;
            transition: all 0.2s;
        }

        .ask-henry-suggestion:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            color: #ffffff;
        }

        /* Input Area */
        .ask-henry-input-area {
            padding: 12px 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            display: flex;
            flex-wrap: nowrap;
            gap: 8px;
            align-items: flex-end;
            width: 100%;
            box-sizing: border-box;
        }

        .ask-henry-input {
            flex: 1;
            min-width: 0;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px 16px;
            color: #ffffff;
            font-size: 1rem;
            line-height: 1.5;
            resize: none;
            min-height: 52px;
            max-height: 120px;
            order: 0; /* Input first */
            box-sizing: border-box;
            overflow-wrap: break-word;
            word-wrap: break-word;
        }

        .ask-henry-input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.25);
            background: rgba(255, 255, 255, 0.08);
        }

        .ask-henry-input::placeholder {
            color: #666666;
        }

        .ask-henry-send {
            background: linear-gradient(145deg, #4a4a4a 0%, #333333 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            width: 36px;
            height: 36px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            order: 2; /* Send button last */
        }

        .ask-henry-send:hover {
            background: linear-gradient(145deg, #5a5a5a 0%, #444444 100%);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .ask-henry-send:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .ask-henry-send svg {
            width: 14px;
            height: 14px;
            fill: #ffffff;
        }

        /* Attachment Button - compact, positioned after input */
        .ask-henry-attach {
            background: transparent;
            border: none;
            border-radius: 8px;
            width: 36px;
            height: 36px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            order: 1; /* Move after textarea in flex layout */
        }

        .ask-henry-attach:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .ask-henry-attach svg {
            width: 16px;
            height: 16px;
            fill: #666666;
            transition: fill 0.2s;
        }

        .ask-henry-attach:hover svg {
            fill: #999999;
        }

        /* Attachment Preview Area */
        .ask-henry-attachments {
            display: none;
            padding: 12px 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            background: rgba(0, 0, 0, 0.3);
            gap: 8px;
            flex-wrap: wrap;
        }

        .ask-henry-attachments.has-files {
            display: flex;
        }

        .ask-henry-attachment-preview {
            position: relative;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            max-width: 200px;
        }

        .ask-henry-attachment-preview img {
            width: 40px;
            height: 40px;
            object-fit: cover;
            border-radius: 4px;
        }

        .ask-henry-attachment-preview .file-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(102, 126, 234, 0.2);
            border-radius: 4px;
            font-size: 1.2rem;
        }

        .ask-henry-attachment-info {
            flex: 1;
            min-width: 0;
        }

        .ask-henry-attachment-name {
            font-size: 0.8rem;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .ask-henry-attachment-size {
            font-size: 0.7rem;
            color: #888888;
        }

        .ask-henry-attachment-remove {
            position: absolute;
            top: -6px;
            right: -6px;
            width: 20px;
            height: 20px;
            background: #ff4444;
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .ask-henry-attachment-remove:hover {
            background: #ff6666;
        }

        /* Drag and drop overlay */
        .ask-henry-drop-overlay {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(102, 126, 234, 0.1);
            border: 2px dashed rgba(102, 126, 234, 0.5);
            border-radius: 16px;
            z-index: 100;
            align-items: center;
            justify-content: center;
            color: #667eea;
            font-size: 1rem;
            font-weight: 500;
        }

        .ask-henry-drawer.drag-over .ask-henry-drop-overlay {
            display: flex;
        }

        /* ==========================================
           Proactive Check-In Nudge Styles
           ========================================== */
        .ask-henry-nudge {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 320px;
            background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            z-index: 9997;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px) scale(0.95);
            transition: all 0.3s ease;
            font-family: 'DM Sans', -apple-system, sans-serif;
        }

        .ask-henry-nudge.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .ask-henry-nudge-content {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            position: relative;
        }

        .ask-henry-nudge-avatar {
            width: 128px;
            height: 128px;
            flex-shrink: 0;
        }

        .ask-henry-nudge-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }

        .ask-henry-nudge-avatar svg {
            width: 100%;
            height: 100%;
        }

        .ask-henry-nudge-avatar .pulse-ring {
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        .ask-henry-nudge-text {
            flex: 1;
            color: #fff;
            font-size: 14px;
            line-height: 1.5;
            padding-right: 20px;
        }

        .ask-henry-nudge-dismiss {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.5);
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            line-height: 1;
            transition: color 0.2s ease;
        }

        .ask-henry-nudge-dismiss:hover {
            color: rgba(255, 255, 255, 0.8);
        }

        .ask-henry-nudge-actions {
            display: flex;
            gap: 8px;
            padding: 0 16px 16px;
        }

        .ask-henry-nudge-open {
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            font-weight: 500;
            padding: 10px 16px;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }

        .ask-henry-nudge-open:hover {
            opacity: 0.9;
        }

        .ask-henry-nudge-later {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            font-weight: 500;
            padding: 10px 16px;
            cursor: pointer;
            transition: background 0.2s ease, color 0.2s ease;
        }

        .ask-henry-nudge-later:hover {
            background: rgba(255, 255, 255, 0.15);
            color: rgba(255, 255, 255, 0.9);
        }

        @media (max-width: 480px) {
            .ask-henry-nudge {
                right: 16px;
                left: 16px;
                width: auto;
                bottom: 80px;
            }
        }

        /* Mobile Responsive */
        @media (max-width: 480px) {
            .ask-henry-drawer {
                bottom: 0;
                right: 0;
                width: 100%;
                max-width: 100%;
                height: 70vh;
                border-radius: 20px 20px 0 0;
            }

            .ask-henry-fab {
                bottom: 16px;
                right: 16px;
            }
        }

        /* ==========================================
           GENIE MODE (Welcome Flow) Styles
           ========================================== */

        /* Dark overlay for genie mode */
        .ask-henry-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 9998;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }

        .ask-henry-overlay.visible {
            opacity: 1;
            visibility: visible;
        }

        /* Genie mode drawer (centered modal) */
        .ask-henry-drawer.genie-mode {
            bottom: 50%;
            right: 50%;
            transform: translate(50%, 50%) scale(1);
            width: 500px;
            max-width: calc(100vw - 48px);
            height: auto;
            max-height: 80vh;
            border-radius: 24px;
            transform-origin: center center;
        }

        .ask-henry-drawer.genie-mode.open {
            transform: translate(50%, 50%) scale(1);
        }

        /* Welcome content area */
        .ask-henry-welcome-content {
            padding: 32px 28px;
            text-align: left;
        }

        .ask-henry-welcome-content h2 {
            font-size: 1.4rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0 0 20px 0;
            line-height: 1.3;
        }

        .ask-henry-welcome-content p {
            font-size: 0.95rem;
            line-height: 1.6;
            color: #e5e5e5;
            margin: 0 0 16px 0;
        }

        .ask-henry-welcome-content p:last-of-type {
            margin-bottom: 0;
        }

        /* Welcome actions area */
        .ask-henry-welcome-actions {
            padding: 20px 28px;
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .ask-henry-welcome-btn {
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            text-decoration: none !important;
            display: block;
            font-family: 'DM Sans', -apple-system, sans-serif;
            border: none;
            outline: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            width: 100%;
            box-sizing: border-box;
        }

        .ask-henry-welcome-btn.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            border: none;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }

        .ask-henry-welcome-btn.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .ask-henry-welcome-btn.secondary {
            background: rgba(255, 255, 255, 0.05);
            color: #a0a0a0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ask-henry-welcome-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* FAB pulse animation for welcome */
        @keyframes fab-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }

        .ask-henry-fab.pulsing {
            animation: fab-pulse 0.8s ease-in-out 3;
        }

        /* Genie expand animation */
        @keyframes genie-expand {
            0% {
                bottom: 24px;
                right: 24px;
                width: 56px;
                height: 56px;
                border-radius: 28px;
                transform: translate(0, 0) scale(1);
            }
            100% {
                bottom: 50%;
                right: 50%;
                width: 500px;
                height: auto;
                border-radius: 24px;
                transform: translate(50%, 50%) scale(1);
            }
        }

        .ask-henry-drawer.genie-animating {
            animation: genie-expand 0.6s ease-out forwards;
        }

        /* Hide close button in genie mode (for required actions) */
        .ask-henry-drawer.genie-mode.no-dismiss .ask-henry-close {
            display: none;
        }

        /* Mobile genie mode */
        @media (max-width: 480px) {
            .ask-henry-drawer.genie-mode {
                width: calc(100vw - 32px);
                max-height: 85vh;
            }
        }

        /* Conversation picker buttons */
        .ask-henry-picker-btn {
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'DM Sans', -apple-system, sans-serif;
            border: none;
            outline: none;
        }

        .ask-henry-picker-btn.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }

        .ask-henry-picker-btn.primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .ask-henry-picker-btn.secondary {
            background: rgba(255, 255, 255, 0.08);
            color: #a0a0a0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .ask-henry-picker-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.12);
            color: #ffffff;
        }

        /* Previous conversations header link */
        .ask-henry-history-link {
            font-size: 0.75rem;
            color: #667eea;
            cursor: pointer;
            opacity: 0.8;
            transition: opacity 0.2s ease;
            text-decoration: none;
        }

        .ask-henry-history-link:hover {
            opacity: 1;
            text-decoration: underline;
        }

        /* Conversation history list */
        .ask-henry-history-list {
            padding: 12px;
        }

        .ask-henry-history-item {
            padding: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: background 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .ask-henry-history-item:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(102, 126, 234, 0.3);
        }

        .ask-henry-history-item-date {
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 4px;
        }

        .ask-henry-history-item-preview {
            font-size: 0.85rem;
            color: #ccc;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .ask-henry-history-back {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 12px;
            color: #667eea;
            cursor: pointer;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .ask-henry-history-back:hover {
            background: rgba(102, 126, 234, 0.1);
        }
    `;

    // Inject stylesheet
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // State
    let isOpen = false;
    let isLoading = false;
    let conversationHistory = [];
    let tooltipTimer = null;
    let tooltipHideTimer = null;
    let welcomeFlowState = null; // 'proactive_welcome' | 'first_action_prompt' | 'welcome_back' | null
    let isGenieMode = false;
    let lastGreetingIndex = -1; // Track last greeting to avoid repetition
    let pendingAttachments = []; // Files waiting to be sent with next message

    // Conversation persistence state
    let currentConversationId = null; // UUID of active conversation in Supabase
    let saveDebounceTimer = null; // Debounce timer for saving to Supabase
    let isLoadingConversations = false; // Loading state for conversation list
    let showingConversationPicker = false; // Whether we're showing the "Continue vs Start Fresh" prompt

    // Attachment configuration
    const ATTACHMENT_CONFIG = {
        maxFileSize: 5 * 1024 * 1024, // 5MB
        maxFiles: 3,
        allowedTypes: {
            images: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
            documents: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        }
    };

    // Get file icon based on type
    function getFileIcon(mimeType) {
        if (mimeType.startsWith('image/')) return '🖼️';
        if (mimeType === 'application/pdf') return '📄';
        if (mimeType.includes('word')) return '📝';
        if (mimeType === 'text/plain') return '📃';
        return '📎';
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    // Validate file for attachment
    function validateAttachment(file) {
        const allAllowed = [...ATTACHMENT_CONFIG.allowedTypes.images, ...ATTACHMENT_CONFIG.allowedTypes.documents];

        if (!allAllowed.includes(file.type)) {
            return { valid: false, error: 'File type not supported. Please use images (PNG, JPG, GIF, WebP) or documents (PDF, DOCX, TXT).' };
        }

        if (file.size > ATTACHMENT_CONFIG.maxFileSize) {
            return { valid: false, error: 'File is too large. Maximum size is 5MB.' };
        }

        if (pendingAttachments.length >= ATTACHMENT_CONFIG.maxFiles) {
            return { valid: false, error: `Maximum ${ATTACHMENT_CONFIG.maxFiles} files per message.` };
        }

        return { valid: true };
    }

    // Add attachment to pending list
    async function addAttachment(file) {
        const validation = validateAttachment(file);
        if (!validation.valid) {
            alert(validation.error);
            return false;
        }

        // Create preview data
        const attachment = {
            file: file,
            name: file.name,
            size: file.size,
            type: file.type,
            preview: null
        };

        // Generate preview for images
        if (file.type.startsWith('image/')) {
            attachment.preview = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(file);
            });
        }

        pendingAttachments.push(attachment);
        updateAttachmentUI();
        return true;
    }

    // Remove attachment from pending list
    function removeAttachment(index) {
        pendingAttachments.splice(index, 1);
        updateAttachmentUI();
    }

    // Update the attachment preview UI
    function updateAttachmentUI() {
        const container = document.getElementById('askHenryAttachments');
        if (!container) return;

        container.innerHTML = '';

        if (pendingAttachments.length === 0) {
            container.classList.remove('has-files');
            return;
        }

        container.classList.add('has-files');

        pendingAttachments.forEach((attachment, index) => {
            const preview = document.createElement('div');
            preview.className = 'ask-henry-attachment-preview';

            const isImage = attachment.type.startsWith('image/');

            preview.innerHTML = `
                ${isImage && attachment.preview
                    ? `<img src="${attachment.preview}" alt="${attachment.name}">`
                    : `<div class="file-icon">${getFileIcon(attachment.type)}</div>`
                }
                <div class="ask-henry-attachment-info">
                    <div class="ask-henry-attachment-name">${attachment.name}</div>
                    <div class="ask-henry-attachment-size">${formatFileSize(attachment.size)}</div>
                </div>
                <button class="ask-henry-attachment-remove" data-index="${index}">×</button>
            `;

            preview.querySelector('.ask-henry-attachment-remove').onclick = (e) => {
                e.stopPropagation();
                removeAttachment(index);
            };

            container.appendChild(preview);
        });
    }

    // Clear all pending attachments
    function clearAttachments() {
        pendingAttachments = [];
        updateAttachmentUI();
        const fileInput = document.getElementById('askHenryFileInput');
        if (fileInput) fileInput.value = '';
    }

    // Convert file to base64 for API
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    // Default tooltip messages (used when no context available)
    const defaultTooltipMessages = [
        "Got questions?",
        "Need strategy help?",
        "Ready when you are!",
        "Let me help!",
        "Thinking about your next move?",
        "Applying now? I can help with those questions!"
    ];

    // Get context-aware tooltip message (prioritizes meaningful context over random)
    function getContextAwareTooltip() {
        const pipeline = getPipelineData();
        const emotionalState = getUserEmotionalState();

        // Priority 1: Pipeline stalled (apps but no movement)
        if (pipeline && pipeline.activeCount > 0 && pipeline.stalledDays >= 3) {
            return `${pipeline.activeCount} app${pipeline.activeCount !== 1 ? 's' : ''}, no movement. Want to review strategy?`;
        }

        // Priority 2: Upcoming interview (interviewing status)
        if (pipeline && pipeline.interviewingCount > 0) {
            const interviewApp = pipeline.topApps?.find(a =>
                ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview'].includes(a.status)
            );
            if (interviewApp) {
                return `Interview at ${interviewApp.company} coming up. Prepped?`;
            }
            return 'Interview coming up. Want to prep?';
        }

        // Priority 3: Emotional state - struggling
        if (emotionalState.holding_up === 'crushed' || emotionalState.holding_up === 'desperate') {
            return "Rough day? Let's talk strategy.";
        }

        // Priority 4: Recent rejection (check for rejected apps)
        if (pipeline && pipeline.rejectedCount > 0) {
            const recentReject = pipeline.topApps?.find(a => a.status === 'Rejected' && a.daysSinceUpdate <= 3);
            // Only show if we have recent reject data, otherwise use generic
            if (recentReject) {
                return `That ${recentReject.company} rejection sucked. Want to talk through it?`;
            }
            if (pipeline.rejectedCount >= 3) {
                return "Noticing some patterns. Want to dig in?";
            }
        }

        // Priority 5: No activity in 3+ days (different from stalled - no active apps)
        if (!pipeline || pipeline.activeCount === 0) {
            return "Taking a break, or stuck on something?";
        }

        // Default: Rotate through helpful defaults
        return defaultTooltipMessages[Math.floor(Math.random() * defaultTooltipMessages.length)];
    }

    // Alias for backwards compatibility (used in hover event)
    function getRandomTooltipMessage() {
        return getContextAwareTooltip();
    }

    // Show tooltip with context-aware message
    function showRandomTooltip() {
        if (isOpen) return; // Don't show if chat is open

        const tooltip = document.getElementById('askHenryTooltip');
        if (!tooltip) return;

        tooltip.textContent = getContextAwareTooltip();
        tooltip.classList.add('visible');

        // Hide after 3 seconds
        if (tooltipHideTimer) clearTimeout(tooltipHideTimer);
        tooltipHideTimer = setTimeout(() => {
            tooltip.classList.remove('visible');
        }, 3000);
    }

    // Start random tooltip appearances
    function startTooltipTimer() {
        // Show first tooltip after 5-10 seconds
        const initialDelay = 5000 + Math.random() * 5000;

        tooltipTimer = setTimeout(() => {
            showRandomTooltip();
            // Then show every 20-40 seconds
            scheduleNextTooltip();
        }, initialDelay);
    }

    function scheduleNextTooltip() {
        const nextDelay = 20000 + Math.random() * 20000; // 20-40 seconds
        tooltipTimer = setTimeout(() => {
            showRandomTooltip();
            scheduleNextTooltip();
        }, nextDelay);
    }

    // Stop tooltip timer (when chat is opened)
    function stopTooltipTimer() {
        if (tooltipTimer) {
            clearTimeout(tooltipTimer);
            tooltipTimer = null;
        }
        if (tooltipHideTimer) {
            clearTimeout(tooltipHideTimer);
            tooltipHideTimer = null;
        }
        const tooltip = document.getElementById('askHenryTooltip');
        if (tooltip) tooltip.classList.remove('visible');
    }

    // ==========================================
    // Proactive Check-Ins (Phase 1.5)
    // ==========================================

    let proactiveCheckInTimer = null;
    let lastCheckInType = null;
    let checkInDismissedTypes = new Set(); // Types dismissed this session

    // Check-in configuration
    const PROACTIVE_CONFIG = {
        checkInterval: 60000, // Check every 60 seconds
        minTimeBetweenCheckIns: 300000, // 5 minutes between check-ins
        staleDays: 3, // Days without activity = stalled
        rejectionThreshold: 3, // Number of rejections to trigger pattern detection
        highFitThreshold: 85, // Fit score above this = high-stakes
        lowFitThreshold: 40 // Fit score below this = high-stakes
    };

    // Proactive check-in messages by type
    const PROACTIVE_MESSAGES = {
        momentum_stall: "You've been sitting on a few roles for a bit. Want help deciding which are actually worth your time?",
        rejection_pattern: "I'm noticing a pattern in the roles you're getting screened out of. Want to dig into it together?",
        confidence_dip: "Quick check-in. This market's rough. If you want to talk through what's working and what's not, I'm here.",
        high_stakes_high: "This role's a real inflection point. If you want a second set of eyes live, we can book time.",
        high_stakes_low: "This role might not be the best fit. Want to talk through whether it's worth your time?",
        celebration_interview: "Interview booked. That's progress. Want help prepping or just taking the win today?",
        celebration_milestone: "You're making progress. Nice work staying consistent."
    };

    // Check if a proactive check-in should be shown
    function checkForProactiveCheckIn() {
        // Don't show if chat is already open
        const drawer = document.getElementById('askHenryDrawer');
        if (drawer && drawer.classList.contains('open')) return null;

        // Don't show if we recently showed a check-in
        const lastCheckInTime = sessionStorage.getItem('heyHenryLastCheckIn');
        if (lastCheckInTime) {
            const timeSince = Date.now() - parseInt(lastCheckInTime);
            if (timeSince < PROACTIVE_CONFIG.minTimeBetweenCheckIns) return null;
        }

        const pipeline = getPipelineData();
        const emotional = getUserEmotionalState();
        const currentPage = window.location.pathname;

        // Priority order of check-ins

        // 1. Confidence dip (crushed or desperate)
        if (['crushed', 'desperate'].includes(emotional.holding_up)) {
            if (!checkInDismissedTypes.has('confidence_dip')) {
                return { type: 'confidence_dip', message: PROACTIVE_MESSAGES.confidence_dip };
            }
        }

        // 2. High-stakes decision (on results page with extreme fit)
        if (currentPage.includes('results')) {
            try {
                const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
                const fitScore = analysisData.fit_score || analysisData.overall_score || 0;
                if (fitScore >= PROACTIVE_CONFIG.highFitThreshold) {
                    if (!checkInDismissedTypes.has('high_stakes_high')) {
                        return { type: 'high_stakes_high', message: PROACTIVE_MESSAGES.high_stakes_high };
                    }
                } else if (fitScore > 0 && fitScore <= PROACTIVE_CONFIG.lowFitThreshold) {
                    if (!checkInDismissedTypes.has('high_stakes_low')) {
                        return { type: 'high_stakes_low', message: PROACTIVE_MESSAGES.high_stakes_low };
                    }
                }
            } catch (e) {}
        }

        // 3. Celebration - interview scheduled (check pipeline for recent interview)
        if (pipeline && pipeline.interviewing > 0) {
            // Check if this is a new interview (would need to track in sessionStorage)
            const seenInterviews = parseInt(sessionStorage.getItem('heyHenrySeenInterviews') || '0');
            if (pipeline.interviewing > seenInterviews) {
                sessionStorage.setItem('heyHenrySeenInterviews', pipeline.interviewing.toString());
                if (!checkInDismissedTypes.has('celebration_interview')) {
                    return { type: 'celebration_interview', message: PROACTIVE_MESSAGES.celebration_interview };
                }
            }
        }

        // 4. Momentum stall (active apps but no recent activity)
        if (pipeline && pipeline.active > 0) {
            // Check if any apps have been stale for 3+ days
            const topApps = pipeline.topApps || [];
            const staleApps = topApps.filter(app => app.daysSinceUpdate >= PROACTIVE_CONFIG.staleDays);
            if (staleApps.length >= 2) {
                if (!checkInDismissedTypes.has('momentum_stall')) {
                    return { type: 'momentum_stall', message: PROACTIVE_MESSAGES.momentum_stall };
                }
            }
        }

        // 5. Rejection pattern (3+ rejections)
        if (pipeline && pipeline.rejected >= PROACTIVE_CONFIG.rejectionThreshold) {
            // Only trigger once per session
            if (!sessionStorage.getItem('heyHenryRejectionCheckin')) {
                sessionStorage.setItem('heyHenryRejectionCheckin', 'true');
                if (!checkInDismissedTypes.has('rejection_pattern')) {
                    return { type: 'rejection_pattern', message: PROACTIVE_MESSAGES.rejection_pattern };
                }
            }
        }

        return null;
    }

    // Show a proactive check-in nudge
    function showProactiveCheckIn(checkIn) {
        if (!checkIn) return;

        lastCheckInType = checkIn.type;
        sessionStorage.setItem('heyHenryLastCheckIn', Date.now().toString());

        // Create nudge element if it doesn't exist
        let nudge = document.getElementById('askHenryNudge');
        if (!nudge) {
            nudge = document.createElement('div');
            nudge.id = 'askHenryNudge';
            nudge.className = 'ask-henry-nudge';
            nudge.innerHTML = `
                <div class="ask-henry-nudge-content">
                    <div class="ask-henry-nudge-text"></div>
                    <button class="ask-henry-nudge-dismiss" aria-label="Dismiss">&times;</button>
                </div>
                <div class="ask-henry-nudge-actions">
                    <button class="ask-henry-nudge-open">Let's Talk</button>
                    <button class="ask-henry-nudge-later">Maybe Later</button>
                </div>
            `;

            // Add to body
            document.body.appendChild(nudge);

            // Add event listeners
            nudge.querySelector('.ask-henry-nudge-dismiss').addEventListener('click', dismissProactiveCheckIn);
            nudge.querySelector('.ask-henry-nudge-later').addEventListener('click', dismissProactiveCheckIn);
            nudge.querySelector('.ask-henry-nudge-open').addEventListener('click', () => {
                dismissProactiveCheckIn();
                // Open chat with the check-in context
                if (window.openHeyHenryWithPrompt) {
                    window.openHeyHenryWithPrompt(checkIn.message);
                } else if (window.openHeyHenry) {
                    window.openHeyHenry();
                }
            });
        }

        // Update message
        nudge.querySelector('.ask-henry-nudge-text').textContent = checkIn.message;

        // Show with animation
        setTimeout(() => nudge.classList.add('visible'), 100);

        // Auto-dismiss after 30 seconds
        setTimeout(() => {
            if (nudge.classList.contains('visible')) {
                dismissProactiveCheckIn();
            }
        }, 30000);
    }

    // Dismiss the proactive check-in
    function dismissProactiveCheckIn() {
        const nudge = document.getElementById('askHenryNudge');
        if (nudge) {
            nudge.classList.remove('visible');
            // Mark this type as dismissed for the session
            if (lastCheckInType) {
                checkInDismissedTypes.add(lastCheckInType);
            }
        }
    }

    // Start proactive check-in monitoring
    function startProactiveCheckIns() {
        // Initial check after 30 seconds
        setTimeout(() => {
            const checkIn = checkForProactiveCheckIn();
            if (checkIn) showProactiveCheckIn(checkIn);
        }, 30000);

        // Then check periodically
        proactiveCheckInTimer = setInterval(() => {
            const checkIn = checkForProactiveCheckIn();
            if (checkIn) showProactiveCheckIn(checkIn);
        }, PROACTIVE_CONFIG.checkInterval);
    }

    // Stop proactive check-ins
    function stopProactiveCheckIns() {
        if (proactiveCheckInTimer) {
            clearInterval(proactiveCheckInTimer);
            proactiveCheckInTimer = null;
        }
    }

    // Load conversation history from sessionStorage (for immediate access) and Supabase (for persistence)
    function loadConversationHistory() {
        try {
            // First, load from sessionStorage for immediate display
            const saved = sessionStorage.getItem('heyHenryConversation');
            const savedId = sessionStorage.getItem('heyHenryConversationId');
            if (saved) {
                conversationHistory = JSON.parse(saved);
                currentConversationId = savedId || null;
            }
        } catch (e) {
            console.error('Error loading conversation history:', e);
            conversationHistory = [];
        }
    }

    // Load conversation from Supabase (async, called after initial render)
    async function loadConversationFromSupabase() {
        // Check if HenryData is available (Supabase client loaded)
        if (typeof window.HenryData === 'undefined') {
            console.log('HenryData not available, using sessionStorage only');
            return;
        }

        try {
            // Check if we already have a conversation ID in this session
            const sessionConvoId = sessionStorage.getItem('heyHenryConversationId');
            if (sessionConvoId && conversationHistory.length > 0) {
                // Already loaded from sessionStorage, just verify the ID is valid
                currentConversationId = sessionConvoId;
                return;
            }

            // Check for recent conversation in Supabase
            const recentConvo = await window.HenryData.getMostRecentHeyHenryConversation();

            if (recentConvo && recentConvo.messages && recentConvo.messages.length > 0) {
                // Show the "Continue vs Start Fresh" prompt
                showConversationPicker(recentConvo);
            }
        } catch (e) {
            console.error('Error loading conversation from Supabase:', e);
        }
    }

    // Show the conversation picker prompt
    function showConversationPicker(recentConvo) {
        if (showingConversationPicker) return;
        showingConversationPicker = true;

        const messagesContainer = document.getElementById('askHenryMessages');
        if (!messagesContainer) return;

        // Get a preview of the last message
        const lastMessage = recentConvo.messages[recentConvo.messages.length - 1];
        const preview = lastMessage ? (lastMessage.content || '').substring(0, 100) + (lastMessage.content?.length > 100 ? '...' : '') : '';
        const timeAgo = getTimeAgo(new Date(recentConvo.updated_at));

        // Create picker UI
        const pickerHtml = `
            <div class="ask-henry-conversation-picker" id="askHenryConvoPicker">
                <div class="ask-henry-message assistant">
                    <p style="margin-bottom: 12px;">Welcome back! You have a recent conversation from ${timeAgo}.</p>
                    <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 16px; font-size: 0.9rem; color: #a0a0a0;">
                        <em>"${preview || 'Previous conversation'}"</em>
                    </div>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <button class="ask-henry-picker-btn primary" id="askHenryContinueConvo">Continue Conversation</button>
                        <button class="ask-henry-picker-btn secondary" id="askHenryStartFresh">Start Fresh</button>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.innerHTML = pickerHtml;

        // Bind button events
        document.getElementById('askHenryContinueConvo').addEventListener('click', () => {
            continueConversation(recentConvo);
        });

        document.getElementById('askHenryStartFresh').addEventListener('click', () => {
            startFreshConversation();
        });
    }

    // Continue a previous conversation
    function continueConversation(conversation) {
        showingConversationPicker = false;
        currentConversationId = conversation.id;
        conversationHistory = conversation.messages || [];

        // Save to sessionStorage for fast access
        sessionStorage.setItem('heyHenryConversationId', conversation.id);
        sessionStorage.setItem('heyHenryConversation', JSON.stringify(conversationHistory));

        // Render the conversation
        const messagesContainer = document.getElementById('askHenryMessages');
        messagesContainer.innerHTML = `
            <div class="ask-henry-message assistant" style="font-size: 0.85rem; opacity: 0.8;">
                <em>Continuing our conversation...</em>
            </div>
        `;

        conversationHistory.forEach(msg => {
            const formattedContent = formatMessage(msg.content);
            const messageEl = document.createElement('div');
            messageEl.className = `ask-henry-message ${msg.role === 'user' ? 'user' : 'assistant'}`;
            messageEl.innerHTML = formattedContent;
            messagesContainer.appendChild(messageEl);
        });

        // Hide suggestions
        const suggestions = document.getElementById('askHenrySuggestions');
        if (suggestions) suggestions.style.display = 'none';

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Start a fresh conversation
    function startFreshConversation() {
        showingConversationPicker = false;
        currentConversationId = null;
        conversationHistory = [];

        // Clear sessionStorage
        sessionStorage.removeItem('heyHenryConversationId');
        sessionStorage.removeItem('heyHenryConversation');

        // Restore default greeting
        const messagesContainer = document.getElementById('askHenryMessages');
        const userName = getUserName();
        const greeting = getContextualGreeting(userName);

        messagesContainer.innerHTML = `
            <div class="ask-henry-message assistant">
                ${greeting}
            </div>
        `;

        // Show suggestions
        const suggestions = document.getElementById('askHenrySuggestions');
        if (suggestions) suggestions.style.display = 'flex';
    }

    // Save conversation history to sessionStorage and Supabase (debounced)
    function saveConversationHistory() {
        try {
            // Keep last 50 messages (increased from 20 for persistence)
            const toSave = conversationHistory.slice(-50);

            // Always save to sessionStorage immediately for fast page navigation
            sessionStorage.setItem('heyHenryConversation', JSON.stringify(toSave));
            if (currentConversationId) {
                sessionStorage.setItem('heyHenryConversationId', currentConversationId);
            }

            // Debounce Supabase save (save after 1 second of no activity)
            if (saveDebounceTimer) {
                clearTimeout(saveDebounceTimer);
            }

            saveDebounceTimer = setTimeout(() => {
                saveConversationToSupabase(toSave);
            }, 1000);
        } catch (e) {
            console.error('Error saving conversation history:', e);
        }
    }

    // Save conversation to Supabase
    async function saveConversationToSupabase(messages) {
        // Check if HenryData is available
        if (typeof window.HenryData === 'undefined') {
            return;
        }

        try {
            if (currentConversationId) {
                // Update existing conversation
                await window.HenryData.updateHeyHenryConversation(currentConversationId, messages);
            } else if (messages.length > 0) {
                // Create new conversation
                const { data, error } = await window.HenryData.createHeyHenryConversation(messages);
                if (data && !error) {
                    currentConversationId = data.id;
                    sessionStorage.setItem('heyHenryConversationId', data.id);
                }
            }
        } catch (e) {
            console.error('Error saving conversation to Supabase:', e);
        }
    }

    // Clear conversation history (for starting fresh)
    function clearConversationHistory() {
        conversationHistory = [];
        currentConversationId = null;
        sessionStorage.removeItem('heyHenryConversation');
        sessionStorage.removeItem('heyHenryConversationId');
    }

    // Helper: Get time ago string
    function getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        return date.toLocaleDateString();
    }

    // Show conversation history list
    async function showConversationHistory() {
        if (typeof window.HenryData === 'undefined') {
            console.log('HenryData not available');
            return;
        }

        const messagesContainer = document.getElementById('askHenryMessages');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');

        // Show loading state
        messagesContainer.innerHTML = `
            <div class="ask-henry-history-back" id="askHenryHistoryBack">
                ← Back to chat
            </div>
            <div class="ask-henry-history-list">
                <div style="text-align: center; padding: 20px; color: #888;">Loading conversations...</div>
            </div>
        `;
        suggestionsContainer.style.display = 'none';

        // Bind back button
        document.getElementById('askHenryHistoryBack').addEventListener('click', () => {
            restoreCurrentConversation();
        });

        try {
            const conversations = await window.HenryData.getHeyHenryConversations(10);

            if (conversations.length === 0) {
                messagesContainer.innerHTML = `
                    <div class="ask-henry-history-back" id="askHenryHistoryBack">
                        ← Back to chat
                    </div>
                    <div class="ask-henry-history-list">
                        <div style="text-align: center; padding: 40px 20px; color: #888;">
                            <p>No previous conversations yet.</p>
                            <p style="font-size: 0.85rem; margin-top: 8px;">Your conversations will appear here after you chat with Henry.</p>
                        </div>
                    </div>
                `;
                document.getElementById('askHenryHistoryBack').addEventListener('click', () => {
                    restoreCurrentConversation();
                });
                return;
            }

            let historyHtml = `
                <div class="ask-henry-history-back" id="askHenryHistoryBack">
                    ← Back to chat
                </div>
                <div class="ask-henry-history-list">
            `;

            conversations.forEach(convo => {
                const date = new Date(convo.updated_at);
                const timeStr = getTimeAgo(date);
                const messages = convo.messages || [];
                const lastUserMsg = messages.filter(m => m.role === 'user').pop();
                const preview = lastUserMsg ? (lastUserMsg.content || '').substring(0, 80) + (lastUserMsg.content?.length > 80 ? '...' : '') : 'Conversation';

                historyHtml += `
                    <div class="ask-henry-history-item" data-convo-id="${convo.id}">
                        <div class="ask-henry-history-item-date">${timeStr}</div>
                        <div class="ask-henry-history-item-preview">${preview}</div>
                    </div>
                `;
            });

            historyHtml += '</div>';
            messagesContainer.innerHTML = historyHtml;

            // Bind back button
            document.getElementById('askHenryHistoryBack').addEventListener('click', () => {
                restoreCurrentConversation();
            });

            // Bind conversation item clicks
            document.querySelectorAll('.ask-henry-history-item').forEach(item => {
                item.addEventListener('click', async () => {
                    const convoId = item.dataset.convoId;
                    const convo = conversations.find(c => c.id === convoId);
                    if (convo) {
                        continueConversation(convo);
                    }
                });
            });
        } catch (e) {
            console.error('Error loading conversation history:', e);
            messagesContainer.innerHTML = `
                <div class="ask-henry-history-back" id="askHenryHistoryBack">
                    ← Back to chat
                </div>
                <div class="ask-henry-history-list">
                    <div style="text-align: center; padding: 20px; color: #888;">Error loading conversations. Please try again.</div>
                </div>
            `;
            document.getElementById('askHenryHistoryBack').addEventListener('click', () => {
                restoreCurrentConversation();
            });
        }
    }

    // Restore current conversation after viewing history
    function restoreCurrentConversation() {
        const messagesContainer = document.getElementById('askHenryMessages');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');

        if (conversationHistory.length > 0) {
            messagesContainer.innerHTML = `
                <div class="ask-henry-message assistant" style="font-size: 0.85rem; opacity: 0.8;">
                    <em>Continuing our conversation...</em>
                </div>
            `;

            conversationHistory.forEach(msg => {
                const formattedContent = formatMessage(msg.content);
                const messageEl = document.createElement('div');
                messageEl.className = `ask-henry-message ${msg.role === 'user' ? 'user' : 'assistant'}`;
                messageEl.innerHTML = formattedContent;
                messagesContainer.appendChild(messageEl);
            });

            suggestionsContainer.style.display = 'none';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
            // Restore default greeting
            const userName = getUserName();
            const greeting = getContextualGreeting(userName);

            messagesContainer.innerHTML = `
                <div class="ask-henry-message assistant">
                    ${greeting}
                </div>
            `;
            suggestionsContainer.style.display = 'flex';
        }
    }

    // Get contextual greeting for restoring chat
    function getContextualGreeting(userName) {
        const greetings = [
            `Hey${userName ? ` ${userName}` : ''}! What's on your mind?`,
            `Hey${userName ? ` ${userName}` : ''}! What are you working on?`,
            `Hey${userName ? ` ${userName}` : ''}! How can I help?`,
            `Hey${userName ? ` ${userName}` : ''}! What do you need?`
        ];
        return greetings[Math.floor(Math.random() * greetings.length)];
    }

    // Get user's preferred name (nickname first, then first name)
    function getUserName() {
        try {
            // Check localStorage for saved profile (includes nickname)
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');

            // Priority 1: Use nickname if set
            if (profile.nickname) {
                return profile.nickname;
            }

            // Priority 2: Use first_name from profile
            if (profile.first_name) {
                return profile.first_name;
            }

            // Priority 3: Parse from full name in profile
            if (profile.name) {
                return profile.name.split(' ')[0];
            }

            // Priority 4: Check resumeData in sessionStorage
            const resumeData = JSON.parse(sessionStorage.getItem('resumeData') || '{}');
            if (resumeData.name) {
                return resumeData.name.split(' ')[0];
            }
        } catch (e) {
            console.error('Error getting user name:', e);
        }
        return null;
    }

    // ==========================================
    // Welcome Flow Detection & Management
    // ==========================================

    // Check if user has a profile (indicates they've completed setup)
    function hasUserProfile() {
        try {
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            // Profile exists if it has a name
            return !!profile.name;
        } catch (e) {
            return false;
        }
    }

    // Get user's emotional state from profile
    function getUserEmotionalState() {
        try {
            const profile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            return {
                holding_up: profile.holding_up || 'zen',
                confidence: profile.confidence || 'strong',
                timeline: profile.timeline || 'actively_looking'
            };
        } catch (e) {
            return { holding_up: 'zen', confidence: 'strong', timeline: 'actively_looking' };
        }
    }

    // Generate tone guidance based on emotional state for backend
    function getToneGuidance(emotionalState) {
        const guidance = [];

        // Tone based on holding_up state
        const holdingUpGuidance = {
            'zen': 'Professional and efficient. Get to the point quickly.',
            'stressed': 'Reassuring but direct. Acknowledge the pressure, then provide clear guidance.',
            'struggling': 'Supportive and steady. Break things into manageable steps.',
            'desperate': 'Empathetic but realistic. Acknowledge difficulty, focus on actionable steps.',
            'crushed': 'Gentle and direct. Acknowledge the pain, but keep moving forward with small wins.'
        };
        guidance.push(holdingUpGuidance[emotionalState.holding_up] || holdingUpGuidance['zen']);

        // Strategy based on timeline
        const timelineGuidance = {
            'urgent': 'Move fast but smart. Prioritize high-probability opportunities.',
            'soon': 'Make every application count. No spray-and-pray.',
            'actively_looking': 'Time to be selective. Focus on quality over quantity.',
            'no_rush': 'Only roles worth making a move for. Be picky.'
        };
        guidance.push(timelineGuidance[emotionalState.timeline] || timelineGuidance['actively_looking']);

        // Support based on confidence
        const confidenceGuidance = {
            'low': 'Provide more explanation. Build confidence through logic and facts.',
            'need_validation': 'Validate their concerns, then redirect to evidence.',
            'shaky': 'Acknowledge feelings, but anchor responses in facts and progress.',
            'strong': 'Peer-level conversation. Be direct and strategic.'
        };
        guidance.push(confidenceGuidance[emotionalState.confidence] || confidenceGuidance['strong']);

        return guidance.join(' ');
    }

    // Determine which welcome flow state to show
    function determineWelcomeFlowState() {
        const hasProfile = hasUserProfile();
        const hasSeenWelcome = localStorage.getItem('heyHenrySeenWelcome') === 'true';
        const hasSeenWelcomeBack = sessionStorage.getItem('heyHenrySeenWelcomeBack') === 'true';
        const urlParams = new URLSearchParams(window.location.search);
        const fromProfileSetup = urlParams.get('from') === 'profile-setup';
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'index';

        // State 2: First-time user (no profile, hasn't seen welcome)
        // Only trigger on dashboard page
        if (!hasProfile && !hasSeenWelcome && currentPage === 'dashboard') {
            return 'proactive_welcome';
        }

        // State 3: Just completed profile setup
        if (hasProfile && fromProfileSetup && currentPage === 'dashboard') {
            return 'first_action_prompt';
        }

        // State 4: Returning user (has profile, new session, hasn't seen welcome back)
        if (hasProfile && !hasSeenWelcomeBack && currentPage === 'dashboard') {
            // Check if enough time has passed since signup (1 hour minimum)
            const signupTime = localStorage.getItem('heyHenrySignupTime');
            if (signupTime) {
                const hoursSinceSignup = (Date.now() - parseInt(signupTime)) / (1000 * 60 * 60);
                if (hoursSinceSignup >= 1) {
                    return 'welcome_back';
                }
            }
        }

        return null; // No welcome flow needed
    }

    // Get welcome content based on state
    function getWelcomeContent(state) {
        const userName = getUserName() || 'there';
        const emotionalState = getUserEmotionalState();

        if (state === 'proactive_welcome') {
            return {
                title: `Hey ${userName}, welcome to HenryHQ.`,
                message: `I'm Henry. I'll be your strategic advisor through this job search.

No mass applying. No fluff. Just honest fit checks, clear positioning, and materials grounded in your real experience. Never fabricated.

To get started, I need your resume, LinkedIn profile, and job search preferences. Takes about 3 to 5 minutes. After that, you're ready to analyze roles and move with intention.

I'm always here. If you're unsure about a role or how to position yourself, just ask.`,
                primaryCta: { text: 'Create My Profile', action: 'create_profile' },
                secondaryCta: null, // No secondary - profile required
                noDismiss: true
            };
        }

        if (state === 'first_action_prompt') {
            return {
                title: `Alright ${userName}, you're all set.`,
                message: `Ready to analyze your first role?`,
                primaryCta: { text: 'Analyze a Role', action: 'analyze_role' },
                secondaryCta: { text: "I'll Look Around First", action: 'close' },
                noDismiss: false
            };
        }

        if (state === 'welcome_back') {
            // Timeline-based context
            const timelineMessages = {
                'urgent': "I know you're under pressure. Let's find roles that are actually worth your time so you're not spinning your wheels.",
                'soon': "You need to move fast, so let's make every application count. No spray-and-pray.",
                'actively_looking': "You've got a solid window. Let's be strategic so you land something good, not just something fast.",
                'no_rush': "You're in a good position. Let's find roles that are actually worth making a move for."
            };

            // Confidence-based closing
            const confidenceMessages = {
                'low': "If you're ever unsure about a role or how to position yourself, just ask. I'm here to help you see what's actually working.",
                'need_validation': "If you're ever unsure about a role or how to position yourself, just ask. I'm here to help you see what's actually working.",
                'shaky': "Look, rejections suck, but they don't mean you're not good enough. They just mean the fit wasn't right. Let's find roles where it is.",
                'strong': "Got questions about a role or how to position yourself? Just ask. I'm here to help you stay sharp."
            };

            const timelineContext = timelineMessages[emotionalState.timeline] || timelineMessages['actively_looking'];
            const confidenceClosing = confidenceMessages[emotionalState.confidence] || confidenceMessages['strong'];

            return {
                title: `Welcome back, ${userName}!`,
                message: `${timelineContext}

Here's what you can do:
• **Analyze New Role:** Paste job description, I'll score fit
• **Command Center:** Track applications and interviews
• **Edit Profile:** Update anytime

${confidenceClosing}`,
                primaryCta: { text: 'Got It', action: 'close' },
                secondaryCta: null,
                noDismiss: false
            };
        }

        return null;
    }

    // Show welcome flow with genie animation
    function showWelcomeFlow(state) {
        welcomeFlowState = state;
        const content = getWelcomeContent(state);
        if (!content) return;

        const drawer = document.getElementById('askHenryDrawer');
        const fab = document.getElementById('askHenryFab');
        const messagesContainer = document.getElementById('askHenryMessages');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');
        const inputArea = document.querySelector('.ask-henry-input-area');

        // Create overlay if doesn't exist
        let overlay = document.getElementById('askHenryOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'askHenryOverlay';
            overlay.className = 'ask-henry-overlay';
            document.getElementById('ask-henry-widget').appendChild(overlay);
        }

        // Hide normal chat elements
        if (suggestionsContainer) suggestionsContainer.style.display = 'none';
        if (inputArea) inputArea.style.display = 'none';

        // Build welcome content
        const welcomeHTML = `
            <div class="ask-henry-welcome-content">
                <h2>${content.title}</h2>
                ${content.message.split('\n\n').map(p => `<p>${formatWelcomeMessage(p)}</p>`).join('')}
            </div>
            <div class="ask-henry-welcome-actions">
                <button class="ask-henry-welcome-btn primary" data-action="${content.primaryCta.action}">
                    ${content.primaryCta.text}
                </button>
                ${content.secondaryCta ? `
                <button class="ask-henry-welcome-btn secondary" data-action="${content.secondaryCta.action}">
                    ${content.secondaryCta.text}
                </button>
                ` : ''}
            </div>
        `;

        messagesContainer.innerHTML = welcomeHTML;

        // For proactive welcome, use genie animation
        if (state === 'proactive_welcome') {
            isGenieMode = true;

            // Pulse FAB first
            fab.classList.add('pulsing');

            setTimeout(() => {
                fab.classList.remove('pulsing');
                fab.classList.add('hidden');

                // Show overlay
                overlay.classList.add('visible');

                // Enable genie mode on drawer
                drawer.classList.add('genie-mode');
                if (content.noDismiss) {
                    drawer.classList.add('no-dismiss');
                }

                // Open the drawer
                drawer.classList.add('open');
                isOpen = true;

                // Bind welcome action buttons
                bindWelcomeActions(state);
            }, 2400); // After 3 pulses (0.8s * 3)
        } else {
            // Normal drawer open for other states
            drawer.classList.add('open');
            isOpen = true;
            fab.classList.add('hidden');
            bindWelcomeActions(state);
        }

        stopTooltipTimer();
    }

    // Format welcome message (handle bold, bullets)
    function formatWelcomeMessage(text) {
        return text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^• /gm, '&bull; ');
    }

    // Bind welcome action button clicks
    function bindWelcomeActions(state) {
        document.querySelectorAll('.ask-henry-welcome-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                handleWelcomeAction(action, state);
            });
        });
    }

    // Handle welcome flow action
    function handleWelcomeAction(action, state) {
        if (action === 'create_profile') {
            localStorage.setItem('heyHenrySeenWelcome', 'true');
            localStorage.setItem('heyHenrySignupTime', Date.now().toString());
            window.location.href = 'profile-edit.html';
        } else if (action === 'analyze_role') {
            // Remove URL param
            const url = new URL(window.location);
            url.searchParams.delete('from');
            window.history.replaceState({}, '', url);
            sessionStorage.setItem('heyHenrySeenWelcomeBack', 'true');
            window.location.href = 'analyze.html';
        } else if (action === 'close') {
            // Remove URL param if present
            const url = new URL(window.location);
            url.searchParams.delete('from');
            window.history.replaceState({}, '', url);
            sessionStorage.setItem('heyHenrySeenWelcomeBack', 'true');
            closeWelcomeFlow();
        }
    }

    // Close welcome flow and restore normal chat
    function closeWelcomeFlow() {
        const drawer = document.getElementById('askHenryDrawer');
        const fab = document.getElementById('askHenryFab');
        const overlay = document.getElementById('askHenryOverlay');
        const suggestionsContainer = document.getElementById('askHenrySuggestions');
        const inputArea = document.querySelector('.ask-henry-input-area');
        const messagesContainer = document.getElementById('askHenryMessages');

        // Hide overlay
        if (overlay) overlay.classList.remove('visible');

        // Remove genie mode classes
        if (drawer) drawer.classList.remove('genie-mode', 'no-dismiss', 'genie-animating');

        // Close drawer
        if (drawer) drawer.classList.remove('open');
        if (fab) fab.classList.remove('hidden');

        // Reset state
        isOpen = false;
        isGenieMode = false;
        welcomeFlowState = null;

        // Restore normal chat UI
        const userName = getUserName();
        const context = getPageContext();
        const greeting = getPersonalizedGreeting(userName, context);
        const suggestions = getContextualSuggestions();

        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="ask-henry-message assistant">
                    ${greeting}
                </div>
            `;
        }

        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = suggestions.map(s => `<button class="ask-henry-suggestion">${s}</button>`).join('');
            suggestionsContainer.style.display = '';
            // Re-bind suggestion clicks
            document.querySelectorAll('.ask-henry-suggestion').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.getElementById('askHenryInput').value = btn.textContent;
                    sendMessage();
                });
            });
        }
        if (inputArea) inputArea.style.display = '';

        // Restart tooltip timer
        startTooltipTimer();
    }

    // Check and trigger welcome flow on init
    function checkWelcomeFlow() {
        // Skip on dashboard - dashboard.html has its own welcome flow system
        // that properly syncs with Supabase server-side profile data
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'index';
        if (currentPage === 'dashboard') {
            return false;
        }

        const state = determineWelcomeFlowState();
        if (state) {
            // Small delay to let the page settle
            setTimeout(() => {
                showWelcomeFlow(state);
            }, 500);
            return true;
        }
        return false;
    }

    // Get current page context
    function getPageContext() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';

        const contexts = {
            'index': { name: 'Home', description: 'Getting started with HenryHQ' },
            'analyze': { name: 'Job Analysis', description: 'Analyzing a new job posting' },
            'results': { name: 'Analysis Results', description: 'Reviewing job match analysis' },
            'overview': { name: 'Strategy Overview', description: 'Viewing your application strategy' },
            'positioning': { name: 'Positioning Strategy', description: 'Reviewing positioning recommendations' },
            'documents': { name: 'Tailored Documents', description: 'Reviewing resume and cover letter' },
            'outreach': { name: 'Network Intelligence', description: 'Planning outreach strategy' },
            'interview-intelligence': { name: 'Interview Intelligence', description: 'Preparing for interviews' },
            'prep-guide': { name: 'Interview Prep', description: 'Reviewing interview prep guide' },
            'interview-debrief': { name: 'Interview Debrief', description: 'Debriefing after an interview' },
            'mock-interview': { name: 'Mock Interview', description: 'Practicing interview skills' },
            'tracker': { name: 'Application Tracker', description: 'Managing job applications' },
            'profile-edit': { name: 'Profile', description: 'Editing your profile' }
        };

        const context = contexts[page] || { name: 'HenryHQ', description: 'Your personal job search guide' };
        context.page = page; // Include the page key for greeting lookup
        return context;
    }

    // Get pipeline data from localStorage (for tracker page context)
    function getPipelineData() {
        try {
            const apps = JSON.parse(localStorage.getItem('trackedApplications') || '[]');
            if (apps.length === 0) return null;

            // Calculate metrics
            const activeApps = apps.filter(a => {
                const activeStatuses = ['Preparing', 'To Apply', 'Applied', 'Reached Out', 'Response Received',
                    'Recruiter Screen', 'Awaiting Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                    'Awaiting Next Round', 'Final Round', 'Executive Interview', 'Awaiting Decision', 'Interviewed', 'Offer Received'];
                return activeStatuses.includes(a.status);
            });

            const interviewingApps = apps.filter(a =>
                ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview', 'Interviewed', 'Awaiting Next Round', 'Awaiting Decision'].includes(a.status)
            );

            const appliedApps = apps.filter(a => !['Preparing', 'To Apply'].includes(a.status));
            const respondedApps = apps.filter(a =>
                ['Response Received', 'Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                 'Final Round', 'Executive Interview', 'Interviewed', 'Offer Received', 'Awaiting Next Round', 'Awaiting Decision'].includes(a.status)
            );

            const rejectedApps = apps.filter(a => a.status === 'Rejected');
            const ghostedApps = apps.filter(a => a.status === 'No Response' ||
                (a.status === 'Applied' && getDaysSinceDate(a.dateApplied) > 14));

            // Get high priority apps (hot/active with high fit)
            const hotApps = activeApps.filter(a => {
                const daysSince = getDaysSinceDate(a.lastUpdated || a.dateAdded);
                const isInterviewing = ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview',
                    'Final Round', 'Executive Interview'].includes(a.status);
                return isInterviewing || (daysSince <= 3 && a.fitScore >= 70);
            });

            // Average fit score
            const avgFit = activeApps.length > 0
                ? Math.round(activeApps.reduce((sum, a) => sum + (a.fitScore || 50), 0) / activeApps.length)
                : 0;

            // Interview rate
            const interviewRate = appliedApps.length > 0
                ? Math.round((respondedApps.length / appliedApps.length) * 100)
                : 0;

            // Calculate days since last activity for stalled detection
            const lastActivityDates = activeApps.map(a => new Date(a.lastUpdated || a.dateAdded || a.dateApplied));
            const mostRecentActivity = lastActivityDates.length > 0 ? Math.max(...lastActivityDates) : Date.now();
            const stalledDays = Math.floor((Date.now() - mostRecentActivity) / (1000 * 60 * 60 * 24));

            // ==========================================
            // PIPELINE PATTERN ANALYSIS (Phase 2.2)
            // ==========================================

            // Fit distribution analysis
            const fitDistribution = {
                strong: apps.filter(a => (a.fitScore || 50) >= 80).length,
                moderate: apps.filter(a => (a.fitScore || 50) >= 60 && (a.fitScore || 50) < 80).length,
                reach: apps.filter(a => (a.fitScore || 50) >= 40 && (a.fitScore || 50) < 60).length,
                longShot: apps.filter(a => (a.fitScore || 50) < 40).length
            };
            const reachPercentage = apps.length > 0
                ? Math.round(((fitDistribution.reach + fitDistribution.longShot) / apps.length) * 100)
                : 0;

            // Stage conversion analysis
            const stageProgression = {
                applied: appliedApps.length,
                responded: respondedApps.length,
                recruiterScreen: apps.filter(a => ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview', 'Final Round', 'Executive Interview', 'Offer Received'].includes(a.status)).length,
                hiringManager: apps.filter(a => ['Hiring Manager', 'Technical Round', 'Panel Interview', 'Final Round', 'Executive Interview', 'Offer Received'].includes(a.status)).length,
                finalRound: apps.filter(a => ['Final Round', 'Executive Interview', 'Offer Received'].includes(a.status)).length,
                offer: apps.filter(a => a.status === 'Offer Received').length
            };

            // Calculate conversion rates
            const conversionRates = {
                applicationToResponse: appliedApps.length > 0 ? Math.round((stageProgression.responded / appliedApps.length) * 100) : 0,
                responseToRecruiter: stageProgression.responded > 0 ? Math.round((stageProgression.recruiterScreen / stageProgression.responded) * 100) : 0,
                recruiterToHM: stageProgression.recruiterScreen > 0 ? Math.round((stageProgression.hiringManager / stageProgression.recruiterScreen) * 100) : 0,
                hmToFinal: stageProgression.hiringManager > 0 ? Math.round((stageProgression.finalRound / stageProgression.hiringManager) * 100) : 0,
                finalToOffer: stageProgression.finalRound > 0 ? Math.round((stageProgression.offer / stageProgression.finalRound) * 100) : 0
            };

            // Rejection stage analysis
            const rejectionsByStage = {
                resume: rejectedApps.filter(a => !a.lastInterviewStage || a.lastInterviewStage === 'Applied').length,
                recruiter: rejectedApps.filter(a => a.lastInterviewStage === 'Recruiter Screen').length,
                hiringManager: rejectedApps.filter(a => a.lastInterviewStage === 'Hiring Manager').length,
                finalRound: rejectedApps.filter(a => ['Final Round', 'Executive Interview'].includes(a.lastInterviewStage)).length,
                offer: rejectedApps.filter(a => a.lastInterviewStage === 'Offer').length
            };

            // Application velocity (apps per week)
            const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
            const twoWeeksAgo = Date.now() - (14 * 24 * 60 * 60 * 1000);
            const appsThisWeek = apps.filter(a => new Date(a.dateApplied || a.dateAdded) >= weekAgo).length;
            const appsLastWeek = apps.filter(a => {
                const appDate = new Date(a.dateApplied || a.dateAdded);
                return appDate >= twoWeeksAgo && appDate < weekAgo;
            }).length;
            const velocityTrend = appsThisWeek < appsLastWeek ? 'slowing' : (appsThisWeek > appsLastWeek ? 'accelerating' : 'steady');

            // Company clustering (find patterns in company types)
            const companyPatterns = {};
            apps.forEach(a => {
                // Track company size if available
                if (a.companySize) {
                    companyPatterns[a.companySize] = (companyPatterns[a.companySize] || 0) + 1;
                }
            });

            // Identify weak spots (stages with highest drop-off)
            const weakSpots = [];
            if (conversionRates.applicationToResponse < 20 && appliedApps.length >= 5) {
                weakSpots.push({ stage: 'resume_screen', dropOff: 100 - conversionRates.applicationToResponse, message: 'Your resume may not be passing ATS or resonating with recruiters' });
            }
            if (conversionRates.recruiterToHM < 50 && stageProgression.recruiterScreen >= 3) {
                weakSpots.push({ stage: 'recruiter_to_hm', dropOff: 100 - conversionRates.recruiterToHM, message: 'Something is happening in recruiter screens that is not advancing you' });
            }
            if (conversionRates.hmToFinal < 50 && stageProgression.hiringManager >= 3) {
                weakSpots.push({ stage: 'hm_to_final', dropOff: 100 - conversionRates.hmToFinal, message: 'You are getting to hiring managers but not converting. Dig into those conversations.' });
            }
            if (conversionRates.finalToOffer < 33 && stageProgression.finalRound >= 2) {
                weakSpots.push({ stage: 'final_to_offer', dropOff: 100 - conversionRates.finalToOffer, message: 'Getting to finals but not closing. Competition or late-stage issues.' });
            }

            // Pattern insights (auto-generated)
            const patternInsights = [];
            if (reachPercentage >= 60) {
                patternInsights.push(`${reachPercentage}% of your applications are reaches or long shots. You are overreaching on scope.`);
            }
            if (ghostedApps.length >= 3 && ghostedApps.length >= appliedApps.length * 0.3) {
                patternInsights.push(`${ghostedApps.length} applications likely ghosted. These companies may be overwhelmed or the role filled.`);
            }
            if (velocityTrend === 'slowing' && appsLastWeek >= 3) {
                patternInsights.push(`Application momentum is slowing: ${appsThisWeek} this week vs ${appsLastWeek} last week.`);
            }
            if (weakSpots.length > 0) {
                weakSpots.forEach(ws => patternInsights.push(ws.message));
            }

            return {
                total: apps.length,
                active: activeApps.length,
                interviewing: interviewingApps.length,
                applied: appliedApps.length,
                rejected: rejectedApps.length,
                ghosted: ghostedApps.length,
                hot: hotApps.length,
                avgFitScore: avgFit,
                interviewRate: interviewRate,
                // Aliased properties for greeting function
                activeCount: activeApps.length,
                interviewingCount: interviewingApps.length,
                rejectedCount: rejectedApps.length,
                stalledDays: stalledDays,
                // Include details of top apps for context
                topApps: activeApps.slice(0, 5).map(a => ({
                    company: a.company,
                    role: a.role,
                    status: a.status,
                    fitScore: a.fitScore,
                    daysSinceUpdate: getDaysSinceDate(a.lastUpdated || a.dateAdded)
                })),
                // Summary for the AI
                summary: generatePipelineSummary(activeApps, interviewingApps, appliedApps, respondedApps, rejectedApps, ghostedApps, avgFit, interviewRate),
                // PATTERN ANALYSIS DATA (Phase 2.2)
                patternAnalysis: {
                    fitDistribution,
                    reachPercentage,
                    stageProgression,
                    conversionRates,
                    rejectionsByStage,
                    velocity: {
                        thisWeek: appsThisWeek,
                        lastWeek: appsLastWeek,
                        trend: velocityTrend
                    },
                    weakSpots,
                    patternInsights,
                    // All apps for detailed analysis (not just top 5)
                    allApps: apps.map(a => ({
                        company: a.company,
                        role: a.role,
                        status: a.status,
                        fitScore: a.fitScore || 50,
                        dateApplied: a.dateApplied || a.dateAdded,
                        lastUpdated: a.lastUpdated || a.dateAdded,
                        daysSinceUpdate: getDaysSinceDate(a.lastUpdated || a.dateAdded),
                        lastInterviewStage: a.lastInterviewStage || null
                    }))
                }
            };
        } catch (e) {
            console.error('Error getting pipeline data:', e);
            return null;
        }
    }

    function getDaysSinceDate(dateString) {
        if (!dateString) return 0;
        const date = new Date(dateString);
        const now = new Date();
        return Math.floor((now - date) / (1000 * 60 * 60 * 24));
    }

    function generatePipelineSummary(activeApps, interviewingApps, appliedApps, respondedApps, rejectedApps, ghostedApps, avgFit, interviewRate) {
        const parts = [];

        parts.push(`${activeApps.length} active application${activeApps.length !== 1 ? 's' : ''}`);

        if (interviewingApps.length > 0) {
            parts.push(`${interviewingApps.length} in interview stages`);
        }

        if (appliedApps.length > 0) {
            parts.push(`${interviewRate}% interview rate`);
        }

        if (avgFit > 0) {
            parts.push(`${avgFit}% average fit score`);
        }

        if (rejectedApps.length > 0) {
            parts.push(`${rejectedApps.length} rejected`);
        }

        if (ghostedApps.length > 0) {
            parts.push(`${ghostedApps.length} likely ghosted`);
        }

        return parts.join(', ');
    }

    // =========================================================================
    // GENERATED CONTENT DATA - Henry is the AUTHOR of these
    // =========================================================================

    function getDocumentsData() {
        try {
            // Get generated resume and cover letter
            const resumeOutput = JSON.parse(sessionStorage.getItem('resumeOutput') || 'null');
            const coverLetter = JSON.parse(sessionStorage.getItem('coverLetter') || 'null');
            const changesApplied = JSON.parse(sessionStorage.getItem('changesApplied') || '[]');

            if (!resumeOutput && !coverLetter) return null;

            return {
                resume_output: resumeOutput,
                cover_letter: coverLetter,
                changes_summary: changesApplied.length > 0
                    ? changesApplied.slice(0, 5).join('; ')
                    : 'Strategic optimization for role alignment'
            };
        } catch (e) {
            console.error('Error getting documents data:', e);
            return null;
        }
    }

    function getOutreachData() {
        try {
            const outreachTemplates = JSON.parse(sessionStorage.getItem('outreachTemplates') || 'null');
            if (!outreachTemplates) return null;

            return {
                templates: outreachTemplates
            };
        } catch (e) {
            console.error('Error getting outreach data:', e);
            return null;
        }
    }

    function getInterviewPrepData() {
        try {
            const interviewPrep = JSON.parse(sessionStorage.getItem('interviewPrep') || 'null');
            const prepModules = JSON.parse(sessionStorage.getItem('prepModules') || 'null');

            if (!interviewPrep && !prepModules) return null;

            return {
                modules: prepModules || interviewPrep?.modules || [],
                focus_areas: interviewPrep?.focus_areas || []
            };
        } catch (e) {
            console.error('Error getting interview prep data:', e);
            return null;
        }
    }

    function getPositioningData() {
        try {
            const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
            const positioningStrategy = analysisData.strategic_positioning ||
                                        analysisData.positioning_strategy ||
                                        analysisData.reality_check?.strategic_action;

            if (!positioningStrategy) return null;

            return {
                positioning_strategy: positioningStrategy,
                talking_points: analysisData.talking_points || [],
                differentiation: analysisData.differentiation || analysisData.key_differentiators || []
            };
        } catch (e) {
            console.error('Error getting positioning data:', e);
            return null;
        }
    }

    // =========================================================================
    // NETWORK DATA - LinkedIn Connections (Phase 2.1)
    // =========================================================================

    function getNetworkData(targetCompany) {
        try {
            const connectionsRaw = localStorage.getItem('linkedinConnections');
            if (!connectionsRaw) return null;

            const connections = JSON.parse(connectionsRaw);
            if (!connections || connections.length === 0) return null;

            // If no target company, just return summary
            if (!targetCompany) {
                return {
                    hasConnections: true,
                    totalConnections: connections.length,
                    directAtCompany: [],
                    relevantConnections: []
                };
            }

            // Normalize company name for matching
            const normalizeCompany = (name) => {
                if (!name) return '';
                return name.toLowerCase()
                    .replace(/,?\s*(inc\.?|llc\.?|ltd\.?|corp\.?|corporation|company|co\.?)$/i, '')
                    .replace(/[^a-z0-9]/g, '')
                    .trim();
            };

            const targetNormalized = normalizeCompany(targetCompany);

            // Find direct connections at target company
            const directConnections = connections.filter(conn => {
                const connCompany = normalizeCompany(conn.company || conn.Company || '');
                return connCompany === targetNormalized || connCompany.includes(targetNormalized) || targetNormalized.includes(connCompany);
            });

            // Find relevant connections (same industry or function, for 2nd-degree suggestions)
            // For now, we'll focus on direct connections
            const relevantConnections = [];

            return {
                hasConnections: true,
                totalConnections: connections.length,
                directAtCompany: directConnections.slice(0, 10).map(conn => ({
                    firstName: conn.firstName || conn['First Name'] || conn.first_name || '',
                    lastName: conn.lastName || conn['Last Name'] || conn.last_name || '',
                    fullName: (conn.firstName || conn['First Name'] || conn.first_name || '') + ' ' + (conn.lastName || conn['Last Name'] || conn.last_name || ''),
                    company: conn.company || conn.Company || '',
                    position: conn.position || conn.Position || conn.title || '',
                    connectedOn: conn.connectedOn || conn['Connected On'] || ''
                })),
                relevantConnections: relevantConnections
            };
        } catch (e) {
            console.error('Error getting network data:', e);
            return null;
        }
    }

    // =========================================================================
    // OUTREACH TRACKING - Follow-up prompts (Phase 2.7)
    // =========================================================================

    function getOutreachLogData() {
        try {
            const outreachLog = JSON.parse(localStorage.getItem('outreachLog') || '[]');
            if (outreachLog.length === 0) return null;

            const now = Date.now();
            const fiveDaysMs = 5 * 24 * 60 * 60 * 1000;
            const tenDaysMs = 10 * 24 * 60 * 60 * 1000;

            // Categorize outreach by status
            const pending = outreachLog.filter(o => o.status === 'pending');
            const responded = outreachLog.filter(o => o.status === 'responded');
            const noResponse = outreachLog.filter(o => o.status === 'no_response');

            // Find outreach due for follow-up (sent 5+ days ago, still pending)
            const dueForFollowUp = pending.filter(o => {
                const sentDate = new Date(o.sentAt).getTime();
                const daysSince = (now - sentDate) / (24 * 60 * 60 * 1000);
                return daysSince >= 5 && daysSince < 10 && !o.followedUpAt;
            });

            // Find outreach due for final follow-up (sent 10+ days ago)
            const dueForFinalFollowUp = pending.filter(o => {
                const sentDate = new Date(o.sentAt).getTime();
                const daysSince = (now - sentDate) / (24 * 60 * 60 * 1000);
                return daysSince >= 10 && (!o.followedUpAt || ((now - new Date(o.followedUpAt).getTime()) / (24 * 60 * 60 * 1000)) >= 5);
            });

            return {
                total: outreachLog.length,
                pending: pending.length,
                responded: responded.length,
                noResponse: noResponse.length,
                dueForFollowUp: dueForFollowUp.map(o => ({
                    contactName: o.contactName,
                    company: o.company,
                    channel: o.channel,
                    sentAt: o.sentAt,
                    daysSince: Math.floor((now - new Date(o.sentAt).getTime()) / (24 * 60 * 60 * 1000))
                })),
                dueForFinalFollowUp: dueForFinalFollowUp.map(o => ({
                    contactName: o.contactName,
                    company: o.company,
                    channel: o.channel,
                    sentAt: o.sentAt,
                    daysSince: Math.floor((now - new Date(o.sentAt).getTime()) / (24 * 60 * 60 * 1000))
                })),
                recentOutreach: outreachLog.slice(0, 5).map(o => ({
                    contactName: o.contactName,
                    company: o.company,
                    channel: o.channel,
                    status: o.status,
                    sentAt: o.sentAt
                }))
            };
        } catch (e) {
            console.error('Error getting outreach log data:', e);
            return null;
        }
    }

    // Log new outreach (called when user confirms they sent a message)
    function logOutreach(contactName, company, channel, messageContent = '') {
        try {
            const outreachLog = JSON.parse(localStorage.getItem('outreachLog') || '[]');

            const newEntry = {
                id: Date.now().toString(),
                contactName,
                company,
                channel,
                messageContent: messageContent.substring(0, 500), // Limit stored content
                sentAt: new Date().toISOString(),
                status: 'pending',
                followedUpAt: null,
                responseDate: null,
                responseNotes: ''
            };

            outreachLog.unshift(newEntry); // Add to beginning

            // Keep only last 100 entries
            if (outreachLog.length > 100) {
                outreachLog.length = 100;
            }

            localStorage.setItem('outreachLog', JSON.stringify(outreachLog));
            return newEntry;
        } catch (e) {
            console.error('Error logging outreach:', e);
            return null;
        }
    }

    // Update outreach status
    function updateOutreachStatus(outreachId, status, notes = '') {
        try {
            const outreachLog = JSON.parse(localStorage.getItem('outreachLog') || '[]');
            const entry = outreachLog.find(o => o.id === outreachId);

            if (entry) {
                entry.status = status;
                if (status === 'responded') {
                    entry.responseDate = new Date().toISOString();
                    entry.responseNotes = notes;
                }
                localStorage.setItem('outreachLog', JSON.stringify(outreachLog));
                return entry;
            }
            return null;
        } catch (e) {
            console.error('Error updating outreach status:', e);
            return null;
        }
    }

    // Mark outreach as followed up
    function markOutreachFollowedUp(outreachId) {
        try {
            const outreachLog = JSON.parse(localStorage.getItem('outreachLog') || '[]');
            const entry = outreachLog.find(o => o.id === outreachId);

            if (entry) {
                entry.followedUpAt = new Date().toISOString();
                localStorage.setItem('outreachLog', JSON.stringify(outreachLog));
                return entry;
            }
            return null;
        } catch (e) {
            console.error('Error marking outreach followed up:', e);
            return null;
        }
    }

    // =========================================================================
    // INTERVIEW DEBRIEF TRACKING - Missing debrief detection (Phase 2.3)
    // =========================================================================

    function getInterviewDebriefData() {
        try {
            const completedInterviews = JSON.parse(localStorage.getItem('completedInterviews') || '[]');
            const trackedApps = JSON.parse(localStorage.getItem('trackedApplications') || '[]');

            if (completedInterviews.length === 0 && trackedApps.length === 0) return null;

            // Find completed interviews without debriefs
            const missingDebriefs = completedInterviews.filter(interview => {
                // Interview happened but no debrief completed
                return !interview.debriefCompleted && interview.date;
            });

            // Also check tracked applications for interview stages without debriefs
            const interviewStages = ['Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview', 'Final Round', 'Executive Interview'];
            const appsInInterviewStages = trackedApps.filter(app => {
                return interviewStages.includes(app.status) && !app.debriefCompleted;
            });

            // Find apps that have advanced stages but may have skipped debriefs
            // e.g., someone at Panel Interview who never debriefed Recruiter Screen or HM
            const stageOrder = ['Applied', 'Recruiter Screen', 'Hiring Manager', 'Technical Round', 'Panel Interview', 'Final Round', 'Executive Interview', 'Offer Received'];
            const appsWithSkippedDebriefs = trackedApps.filter(app => {
                const currentStageIndex = stageOrder.indexOf(app.status);
                // If at Panel Interview (index 4) or later, check if earlier interviews were debriefed
                if (currentStageIndex >= 4) {
                    // Check if any earlier interview stages were completed without debrief
                    const hasEarlierInterview = completedInterviews.some(
                        i => i.company === app.company && !i.debriefCompleted
                    );
                    return hasEarlierInterview || !app.debriefCompleted;
                }
                return false;
            });

            // Count total debriefs completed
            const totalDebriefs = completedInterviews.filter(i => i.debriefCompleted).length;

            // Get interviews that need debriefs (prioritized)
            const needsDebrief = [];

            // Priority 1: Recent completed interviews without debrief (within 7 days)
            const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
            missingDebriefs.forEach(interview => {
                const interviewDate = new Date(interview.date).getTime();
                if (interviewDate >= sevenDaysAgo) {
                    needsDebrief.push({
                        company: interview.company || interview.companyName,
                        role: interview.role || interview.roleName,
                        interviewType: interview.interviewType || interview.type || 'Interview',
                        date: interview.date,
                        daysSince: Math.floor((Date.now() - interviewDate) / (24 * 60 * 60 * 1000)),
                        priority: 'high',
                        reason: 'Recent interview needs debrief while details are fresh'
                    });
                }
            });

            // Priority 2: Apps at advanced stages with no prior debriefs
            appsWithSkippedDebriefs.forEach(app => {
                needsDebrief.push({
                    company: app.company,
                    role: app.role,
                    interviewType: app.status,
                    date: app.lastUpdated || app.dateApplied,
                    daysSince: 0,
                    priority: 'medium',
                    reason: `At ${app.status} but earlier interviews not debriefed. Compounding insights missed.`
                });
            });

            return {
                totalCompletedInterviews: completedInterviews.length,
                totalDebriefs: totalDebriefs,
                missingDebriefCount: missingDebriefs.length,
                needsDebrief: needsDebrief.slice(0, 5), // Top 5 priority
                hasSkippedDebriefs: appsWithSkippedDebriefs.length > 0
            };
        } catch (e) {
            console.error('Error getting interview debrief data:', e);
            return null;
        }
    }

    // DEBRIEF PATTERN ANALYSIS - Cross-interview intelligence (Phase 2.3)
    // Fetches and analyzes patterns across user's interview debriefs
    let cachedPatternAnalysis = null;
    let patternAnalysisTimestamp = null;

    async function getDebriefPatternAnalysis() {
        try {
            // Check if HenryData is available
            if (typeof window.HenryData === 'undefined') {
                return null;
            }

            // Cache for 5 minutes to avoid repeated calls
            const now = Date.now();
            if (cachedPatternAnalysis && patternAnalysisTimestamp && (now - patternAnalysisTimestamp) < 300000) {
                return cachedPatternAnalysis;
            }

            // Fetch debriefs from Supabase
            const debriefs = await window.HenryData.getDebriefsForPatternAnalysis();

            if (!debriefs || debriefs.length < 3) {
                // Need at least 3 debriefs for meaningful patterns
                return null;
            }

            console.log(`📊 Analyzing patterns across ${debriefs.length} debriefs...`);

            // Call the pattern analysis endpoint
            const response = await fetch(`${API_BASE}/api/debriefs/analyze-patterns`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(debriefs)
            });

            if (!response.ok) {
                console.error('Pattern analysis failed:', response.status);
                return null;
            }

            const patternData = await response.json();
            console.log('✅ Pattern analysis complete:', patternData.insights?.length || 0, 'insights');

            // Cache the result
            cachedPatternAnalysis = patternData;
            patternAnalysisTimestamp = now;

            return patternData;
        } catch (e) {
            console.error('Error getting debrief pattern analysis:', e);
            return null;
        }
    }

    // Get contextual suggestions based on current page
    function getContextualSuggestions() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '') || 'index';
        const userName = getUserName();

        // For first-time visitors on home page, don't show suggestions
        // Let the greeting speak for itself
        if (page === 'index' && !userName) {
            return [];
        }

        const suggestions = {
            'index': [
                'Analyze a job for me',
                'Help me update my resume',
                'What should I work on?'
            ],
            'positioning': [
                'Why this positioning?',
                'What if they ask about gaps?',
                'How do I stand out?'
            ],
            'documents': [
                'Why did you change this?',
                'Should I include more metrics?',
                'Help me answer application questions'
            ],
            'outreach': [
                'Best time to reach out?',
                'How do I find the HM?',
                'Should I follow up?'
            ],
            'interview-intelligence': [
                'How do I prepare?',
                'What questions should I expect?',
                'Tips for this stage?'
            ],
            'prep-guide': [
                'What stories should I use?',
                'How do I handle salary talk?',
                'Questions to ask them?'
            ],
            'tracker': [
                'What should I focus on?',
                'When to follow up?',
                'How to prioritize?'
            ],
            'overview': [
                'What should I do first?',
                'Help me answer application questions',
                'Am I ready to apply?'
            ],
            'default': [
                'Help me stand out',
                'Review my strategy',
                'Help me answer application questions'
            ]
        };

        return suggestions[page] || suggestions['default'];
    }

    // Generate personalized greeting with rotation and context-awareness
    function getPersonalizedGreeting(userName, context) {
        // No name - first time visitor
        if (!userName) {
            return `Hi, I'm Henry! I'm always around if you need to chat. How can I help you?`;
        }

        // Get emotional state and pipeline data for context-aware greetings
        const emotionalState = getUserEmotionalState();
        const pipeline = getPipelineData();

        // Context-aware greetings based on emotional state (highest priority)
        if (emotionalState.holding_up === 'crushed' || emotionalState.holding_up === 'desperate') {
            return `Hey ${userName}. This market's brutal. Let's figure out what's not working.`;
        }

        if (emotionalState.holding_up === 'stressed' || emotionalState.holding_up === 'struggling') {
            return `Hey ${userName}. I know you're under pressure. What do you need?`;
        }

        // Context-aware greetings based on pipeline (second priority)
        if (pipeline) {
            // Upcoming interviews
            if (pipeline.interviewingCount > 0) {
                return `Hey ${userName}! I see you've got ${pipeline.interviewingCount} interview${pipeline.interviewingCount !== 1 ? 's' : ''} lined up. Want to prep?`;
            }

            // Recent rejections pattern
            if (pipeline.rejectedCount >= 3) {
                return `Hey ${userName}. I'm noticing some patterns in your applications. Want to dig into what might be happening?`;
            }

            // Stalled pipeline (apps but no recent activity)
            if (pipeline.activeCount > 0 && pipeline.stalledDays >= 3) {
                return `Hey ${userName}! You've been sitting on a few roles. Want help deciding which are worth your time?`;
            }
        }

        // Standard greetings rotation (avoid repetition)
        const standardGreetings = [
            `Hey ${userName}! What's on your mind?`,
            `Hey ${userName}! What are you working on?`,
            `Hey ${userName}! How can I help?`,
            `Hey ${userName}! What are you thinking about?`,
            `Hey ${userName}! What do you need?`,
            `Hey ${userName}! What's up?`
        ];

        // Select next greeting, avoiding the last one used
        let greetingIndex;
        do {
            greetingIndex = Math.floor(Math.random() * standardGreetings.length);
        } while (greetingIndex === lastGreetingIndex && standardGreetings.length > 1);

        lastGreetingIndex = greetingIndex;
        return standardGreetings[greetingIndex];
    }

    // ==========================================
    // Clarification Detection
    // ==========================================

    // Detect if a message is vague and might need clarification
    function detectClarificationNeeds(message) {
        const lowerMessage = message.toLowerCase().trim();
        const needs = [];

        // Vague bug reports - no specifics
        const vagueIssuePatterns = [
            /^(it'?s?|this is) (broken|not working|buggy|messed up)\.?$/i,
            /^(something'?s?|something is) (wrong|off|weird)\.?$/i,
            /^(doesn'?t|does not|won'?t|will not) work\.?$/i,
            /^(there'?s|there is) (a|an)? ?(bug|issue|problem)\.?$/i
        ];
        if (vagueIssuePatterns.some(p => p.test(lowerMessage))) {
            needs.push({
                type: 'vague_bug',
                hint: 'Ask: What specifically happened? What were you trying to do? A screenshot would help.'
            });
        }

        // Vague feedback - no actionable details
        const vagueFeedbackPatterns = [
            /^(this is|it'?s?) (confusing|unclear|hard to use)\.?$/i,
            /^i (don'?t|do not) (get|understand) (it|this)\.?$/i,
            /^(confusing|unclear|frustrating)\.?$/i
        ];
        if (vagueFeedbackPatterns.some(p => p.test(lowerMessage))) {
            needs.push({
                type: 'vague_feedback',
                hint: 'Ask: What part specifically felt unclear? What were you trying to do?'
            });
        }

        // Feature requests without use case
        const featureRequestPatterns = [
            /^(you should|can you|could you|please) add/i,
            /^add (a|an|the)/i,
            /^(i want|i need|i wish)/i
        ];
        const hasUseCase = lowerMessage.includes('so i can') ||
                         lowerMessage.includes('because') ||
                         lowerMessage.includes('so that') ||
                         lowerMessage.includes('for when') ||
                         lowerMessage.includes('to help');
        if (featureRequestPatterns.some(p => p.test(lowerMessage)) && !hasUseCase && lowerMessage.length < 60) {
            needs.push({
                type: 'feature_no_usecase',
                hint: 'Ask: How would you use this in your job search? What problem would it solve?'
            });
        }

        // Very short messages that could mean many things
        if (lowerMessage.length < 20 && !lowerMessage.includes('?')) {
            const ambiguousPatterns = [
                /^help\.?$/i,
                /^help me\.?$/i,
                /^i'?m stuck\.?$/i,
                /^what now\.?$/i,
                /^what should i do\.?$/i,
                /^i'?m not sure\.?$/i
            ];
            if (ambiguousPatterns.some(p => p.test(lowerMessage))) {
                needs.push({
                    type: 'ambiguous_request',
                    hint: 'Ask: What are you working on right now? What decision or step are you trying to figure out?'
                });
            }
        }

        // Messages with pronouns but no clear referent
        const pronounOnlyPatterns = [
            /^(fix|change|update|modify|edit) (it|this|that)\.?$/i,
            /^(what about|how about) (it|this|that)\??$/i,
            /^(do|make|try) (it|this|that)\.?$/i
        ];
        if (pronounOnlyPatterns.some(p => p.test(lowerMessage))) {
            needs.push({
                type: 'unclear_reference',
                hint: 'Ask: What specifically would you like me to look at or change?'
            });
        }

        return {
            needs_clarification: needs.length > 0,
            clarification_hints: needs
        };
    }

    // ==========================================
    // Document Refinement Detection (Phase 1.5)
    // ==========================================

    // Triggers that indicate user wants to modify a document
    const REFINEMENT_TRIGGERS = [
        'make it more', 'make this more', 'can you make',
        'add more', 'remove the', 'change the',
        'too generic', 'more specific', 'more senior',
        'less formal', 'more formal', 'shorter', 'longer',
        'rewrite', 'update the', 'modify the',
        'make my resume', 'make the resume', 'make my cover letter',
        'add keywords', 'more impactful', 'more action verbs',
        'sound more', 'tone down', 'emphasize', 'highlight'
    ];

    // ==========================================
    // Beta Feedback Collection
    // ==========================================

    // Triggers that indicate user is providing feedback
    const FEEDBACK_TRIGGERS = [
        // Bug reports
        'bug', 'broken', 'not working', 'doesn\'t work', 'error', 'issue', 'problem',
        'crashed', 'stuck', 'freezing', 'slow', 'glitch',
        // Feedback/suggestions
        'feedback', 'suggestion', 'suggest', 'would be nice', 'wish it could',
        'should have', 'would love', 'feature request', 'idea for',
        'could you add', 'can you add', 'please add',
        // Complaints/confusion
        'confusing', 'confused', 'don\'t understand', 'unclear', 'hard to use',
        'frustrating', 'annoying', 'wrong', 'incorrect',
        // Praise (also valuable)
        'love this', 'great feature', 'really helpful', 'awesome', 'works great',
        'thank you', 'thanks for', 'amazing'
    ];

    // State for feedback flow
    let pendingFeedback = null;
    let feedbackFlowState = null; // 'awaiting_details' | 'awaiting_confirmation' | null

    function detectFeedbackIntent(message) {
        const lowerMessage = message.toLowerCase();
        return FEEDBACK_TRIGGERS.some(trigger => lowerMessage.includes(trigger));
    }

    function getFollowUpQuestion(feedbackType, originalMessage) {
        const lowerMessage = originalMessage.toLowerCase();

        if (feedbackType === 'bug') {
            // Check if they already provided details
            const hasDetails = lowerMessage.length > 60 ||
                lowerMessage.includes('when i') ||
                lowerMessage.includes('after i') ||
                lowerMessage.includes('tried to');

            if (hasDetails) {
                return null; // Already detailed enough
            }
            return "Thanks for flagging. To help the team fix this fast:\n\n1. What were you trying to do?\n2. What happened instead?\n3. What page were you on?\n\nA screenshot helps too if you can attach one.";
        }

        if (feedbackType === 'feature_request') {
            const hasContext = lowerMessage.length > 50 ||
                lowerMessage.includes('would help') ||
                lowerMessage.includes('because') ||
                lowerMessage.includes('so that');

            if (hasContext) {
                return null;
            }
            return "Interesting idea. What problem would this solve for you? And have you seen this done well somewhere else?";
        }

        if (feedbackType === 'ux_issue') {
            const hasContext = lowerMessage.length > 50 ||
                lowerMessage.includes('expected') ||
                lowerMessage.includes('thought it');

            if (hasContext) {
                return null;
            }
            return "What were you trying to do, and what did you expect to happen? Knowing the gap helps us fix it.";
        }

        if (feedbackType === 'praise') {
            // For praise, ask specific questions to understand what's working
            const hasContext = lowerMessage.length > 60;
            if (hasContext) {
                return null;
            }
            return "That means a lot! Which feature or part of the experience stood out most? And anything we could do even better?";
        }

        // General feedback - ask targeted questions
        return "Thanks for sharing. A few quick questions:\n\n1. What page or feature is this about?\n2. What were you trying to accomplish?\n3. What would make it better?";
    }

    function categorizeFeedback(message) {
        const lowerMessage = message.toLowerCase();

        // Bug/Issue
        if (['bug', 'broken', 'not working', 'doesn\'t work', 'error', 'crashed', 'stuck', 'glitch'].some(t => lowerMessage.includes(t))) {
            return 'bug';
        }
        // Feature request
        if (['wish', 'could you add', 'can you add', 'please add', 'feature', 'suggestion', 'suggest', 'would be nice', 'should have', 'would love', 'idea'].some(t => lowerMessage.includes(t))) {
            return 'feature_request';
        }
        // Praise
        if (['love', 'great', 'helpful', 'awesome', 'amazing', 'thank', 'works great'].some(t => lowerMessage.includes(t))) {
            return 'praise';
        }
        // Confusion/UX issue
        if (['confusing', 'confused', 'don\'t understand', 'unclear', 'hard to use', 'frustrating'].some(t => lowerMessage.includes(t))) {
            return 'ux_issue';
        }
        // General feedback
        return 'general';
    }

    // Helper to convert file to base64
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async function submitFeedback(feedbackText, feedbackType) {
        try {
            // Get recent conversation for context (last 6 messages)
            const conversationSnippet = conversationHistory.slice(-6).map(m => ({
                role: m.role,
                content: m.content.substring(0, 500) // Truncate long messages
            }));

            const context = getPageContext();

            // Handle screenshot if present
            let screenshotData = null;
            if (pendingFeedback?.screenshot) {
                try {
                    screenshotData = await fileToBase64(pendingFeedback.screenshot);
                    console.log('📸 Screenshot attached to feedback');
                } catch (e) {
                    console.error('Failed to process screenshot:', e);
                }
            }

            // Use HenryData if available, otherwise store locally
            if (typeof HenryData !== 'undefined' && HenryData.saveFeedback) {
                const result = await HenryData.saveFeedback({
                    type: feedbackType,
                    text: feedbackText,
                    currentPage: context.name,
                    context: {
                        pageDescription: context.description,
                        url: window.location.href,
                        userAgent: navigator.userAgent,
                        timestamp: new Date().toISOString(),
                        hasScreenshot: !!screenshotData
                    },
                    conversationSnippet: conversationSnippet,
                    screenshot: screenshotData
                });

                // Send acknowledgment email if feedback was saved successfully
                if (!result.error && typeof HenryAuth !== 'undefined') {
                    try {
                        const user = await HenryAuth.getUser();
                        if (user?.email) {
                            const userName = await HenryAuth.getUserName();
                            const displayName = userName?.firstName && userName.firstName !== 'there'
                                ? userName.firstName
                                : null;

                            // Build conversation context for admin notification
                            const recentConvo = conversationHistory.slice(-6).map(m =>
                                `${m.role === 'user' ? 'User' : 'Henry'}: ${m.content.substring(0, 300)}`
                            ).join('\n\n');

                            // Fire and forget - don't block on email
                            fetch(`${API_BASE}/api/send-feedback-acknowledgment`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    email: user.email,
                                    name: displayName,
                                    feedback_type: feedbackType,
                                    feedback_summary: feedbackText.substring(0, 100),
                                    full_feedback: feedbackText,
                                    current_page: context.name || window.location.pathname,
                                    conversation_context: recentConvo
                                })
                            }).then(response => {
                                if (response.ok) {
                                    console.log('📧 Feedback acknowledgment email sent');
                                }
                            }).catch(e => {
                                console.warn('📧 Could not send acknowledgment email:', e.message);
                            });
                        }
                    } catch (emailError) {
                        // Don't fail feedback submission if email fails
                        console.warn('📧 Email acknowledgment skipped:', emailError.message);
                    }
                }

                return { success: !result.error, id: result.data?.id };
            } else {
                // Fallback: store in localStorage for later sync
                const storedFeedback = JSON.parse(localStorage.getItem('pendingFeedback') || '[]');
                storedFeedback.push({
                    type: feedbackType,
                    text: feedbackText,
                    currentPage: context.name,
                    timestamp: new Date().toISOString(),
                    conversationSnippet: conversationSnippet,
                    screenshot: screenshotData
                });
                localStorage.setItem('pendingFeedback', JSON.stringify(storedFeedback));
                console.log('📝 Feedback stored locally (HenryData not available)');
                return { success: true, local: true };
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            return { success: false, error: error.message };
        }
    }

    function handleFeedbackConfirmation(confirmed) {
        if (!pendingFeedback) return;

        // Remove the confirmation buttons
        const confirmContainer = document.getElementById('feedbackConfirmContainer');
        if (confirmContainer) confirmContainer.remove();

        if (confirmed) {
            // Submit the feedback
            submitFeedback(pendingFeedback.text, pendingFeedback.type).then(result => {
                if (result.success) {
                    addMessage('assistant', "Thanks! I've shared your feedback with the Henry team. They review everything and it really helps make HenryHQ better. Is there anything else I can help you with?");
                    conversationHistory.push({
                        role: 'assistant',
                        content: "Thanks! I've shared your feedback with the Henry team. They review everything and it really helps make HenryHQ better. Is there anything else I can help you with?"
                    });
                } else {
                    addMessage('assistant', "I tried to send your feedback but hit a snag. Don't worry though - you can always email the team directly at hello@henryhq.ai. What else can I help with?");
                    conversationHistory.push({
                        role: 'assistant',
                        content: "I tried to send your feedback but hit a snag. Don't worry though - you can always email the team directly at hello@henryhq.ai. What else can I help with?"
                    });
                }
                saveConversationHistory();
            });
        } else {
            // User declined, continue normally
            addMessage('assistant', "No problem! Is there anything else I can help you with?");
            conversationHistory.push({ role: 'assistant', content: "No problem! Is there anything else I can help you with?" });
            saveConversationHistory();
        }

        // Reset feedback flow state
        pendingFeedback = null;
        feedbackFlowState = null;
    }

    function addFeedbackConfirmation(feedbackType) {
        const messagesContainer = document.getElementById('askHenryMessages');

        const confirmContainer = document.createElement('div');
        confirmContainer.id = 'feedbackConfirmContainer';
        confirmContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin: 12px 0;
        `;

        // Screenshot upload area (especially useful for bugs)
        const screenshotArea = document.createElement('div');
        screenshotArea.id = 'screenshotUploadArea';
        screenshotArea.style.cssText = `
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        `;
        screenshotArea.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <span style="color: #9ca3af; font-size: 0.85rem;">Add a screenshot (optional)</span>
        `;

        // Hidden file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        fileInput.id = 'feedbackScreenshotInput';

        // Screenshot preview container
        const previewContainer = document.createElement('div');
        previewContainer.id = 'screenshotPreview';
        previewContainer.style.cssText = `
            display: none;
            position: relative;
            max-width: 200px;
        `;

        screenshotArea.onclick = () => fileInput.click();
        screenshotArea.onmouseenter = () => {
            screenshotArea.style.borderColor = 'rgba(255, 255, 255, 0.4)';
            screenshotArea.style.background = 'rgba(255, 255, 255, 0.08)';
        };
        screenshotArea.onmouseleave = () => {
            screenshotArea.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            screenshotArea.style.background = 'rgba(255, 255, 255, 0.05)';
        };

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Screenshot must be under 5MB');
                    return;
                }

                // Store for later submission
                pendingFeedback.screenshot = file;

                // Show preview
                const reader = new FileReader();
                reader.onload = (event) => {
                    previewContainer.style.display = 'block';
                    previewContainer.innerHTML = `
                        <img src="${event.target.result}" style="max-width: 200px; max-height: 150px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2);">
                        <button id="removeScreenshot" style="
                            position: absolute;
                            top: -8px;
                            right: -8px;
                            width: 24px;
                            height: 24px;
                            border-radius: 50%;
                            background: #ef4444;
                            border: none;
                            color: white;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 14px;
                        ">×</button>
                    `;
                    // Update upload area text
                    screenshotArea.querySelector('span').textContent = 'Change screenshot';

                    // Add remove handler
                    document.getElementById('removeScreenshot').onclick = (e) => {
                        e.stopPropagation();
                        previewContainer.style.display = 'none';
                        previewContainer.innerHTML = '';
                        pendingFeedback.screenshot = null;
                        fileInput.value = '';
                        screenshotArea.querySelector('span').textContent = 'Add a screenshot (optional)';
                    };
                };
                reader.readAsDataURL(file);
            }
        };

        // Button row
        const buttonRow = document.createElement('div');
        buttonRow.style.cssText = `
            display: flex;
            gap: 10px;
        `;

        const yesBtn = document.createElement('button');
        yesBtn.textContent = 'Yes, send it';
        yesBtn.style.cssText = `
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: transform 0.2s;
        `;
        yesBtn.onclick = () => handleFeedbackConfirmation(true);

        const noBtn = document.createElement('button');
        noBtn.textContent = 'No thanks';
        noBtn.style.cssText = `
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            color: #a0a0a0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        `;
        noBtn.onclick = () => handleFeedbackConfirmation(false);

        buttonRow.appendChild(yesBtn);
        buttonRow.appendChild(noBtn);

        // Only show screenshot option for bugs and ux issues
        if (feedbackType === 'bug' || feedbackType === 'ux_issue') {
            confirmContainer.appendChild(screenshotArea);
            confirmContainer.appendChild(fileInput);
            confirmContainer.appendChild(previewContainer);
        }
        confirmContainer.appendChild(buttonRow);

        messagesContainer.appendChild(confirmContainer);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function detectRefinementRequest(message) {
        const lowerMessage = message.toLowerCase();
        return REFINEMENT_TRIGGERS.some(trigger => lowerMessage.includes(trigger));
    }

    // Persist refined document to Supabase applications table
    async function persistRefinedDocumentToSupabase(company, role, documentsData) {
        if (typeof window.HenryData === 'undefined') {
            console.log('HenryData not available, skipping Supabase persistence');
            return;
        }

        if (!company || !role) {
            console.log('Missing company or role, skipping Supabase persistence');
            return;
        }

        try {
            // Find matching application in Supabase
            const apps = await window.HenryData.getApplications();
            const matchingApp = apps.find(app =>
                app.company.toLowerCase() === company.toLowerCase() &&
                app.role.toLowerCase() === role.toLowerCase()
            );

            if (matchingApp) {
                // Update the application with new documents data
                matchingApp.documentsData = documentsData;
                await window.HenryData.saveApplication(matchingApp);
                console.log('📝 Saved refined document to Supabase (updated existing)');
            } else {
                // No matching application exists - create one to store the documents
                // This ensures refined documents persist even if user hasn't added job to tracker
                const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
                const newApp = {
                    company: company,
                    role: role,
                    status: 'Preparing',
                    fitScore: analysisData.fit_score || null,
                    dateApplied: null,
                    analysisData: analysisData,
                    documentsData: documentsData,
                    source: 'hey-henry-refinement'
                };
                await window.HenryData.saveApplication(newApp);
                console.log('📝 Saved refined document to Supabase (created new application)');
            }
        } catch (e) {
            console.error('Error persisting refined document to Supabase:', e);
        }
    }

    async function handleRefinementRequest(message) {
        const currentPage = window.location.pathname;

        // Only handle refinements on document-related pages
        if (!currentPage.includes('documents') && !currentPage.includes('overview')) {
            return null; // Let normal chat handle it
        }

        const documentsData = JSON.parse(sessionStorage.getItem('documentsData') || '{}');
        const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');

        // Check if we have documents to refine
        if (!documentsData.resume_output && !documentsData.cover_letter) {
            return null; // No document to refine
        }

        // Determine document type from context or default to resume
        let documentType = 'resume';
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('cover letter')) {
            documentType = 'cover_letter';
        } else if (lowerMessage.includes('outreach')) {
            documentType = 'outreach';
        }

        const currentDoc = documentType === 'resume'
            ? documentsData.resume_output
            : documentsData.cover_letter;

        if (!currentDoc) {
            return null; // Specific document not available
        }

        try {
            const response = await fetch(`${API_BASE}/api/documents/refine`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_command: message,
                    target_document: documentType,
                    current_document_data: currentDoc,
                    original_jd_analysis: analysisData,
                    original_resume_data: analysisData._resume_json || {},
                    conversation_history: conversationHistory.slice(-10),
                    version: documentsData._version || 1
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Refinement failed');
            }

            const result = await response.json();

            // Update stored documents
            if (documentType === 'resume') {
                documentsData.resume_output = result.updated_document;
            } else {
                documentsData.cover_letter = result.updated_document;
            }
            documentsData._version = result.updated_document.version || (documentsData._version || 1) + 1;
            documentsData._lastRefinement = {
                timestamp: new Date().toISOString(),
                changes: result.changes_summary,
                summary: result.conversational_response
            };

            // Persist to sessionStorage (immediate access)
            sessionStorage.setItem('documentsData', JSON.stringify(documentsData));

            // Also persist to localStorage for durability across sessions
            const company = analysisData._company || analysisData.company_name || '';
            const role = analysisData._role || analysisData.role_title || '';
            if (company && role) {
                const documentsKey = `documents_${company}_${role}`.toLowerCase().replace(/[^a-z0-9_]/g, '_');
                localStorage.setItem(documentsKey, JSON.stringify(documentsData));
                console.log('📝 Saved refined document to localStorage:', documentsKey);
            }

            // Also update in Supabase via applications table (async, non-blocking)
            persistRefinedDocumentToSupabase(company, role, documentsData);

            // Format response with changes
            let changesText = '';
            if (result.changes_summary && result.changes_summary.sections_modified) {
                changesText = '\n\n**Changes made:**\n';
                result.changes_summary.sections_modified.forEach(section => {
                    changesText += `• ${section}\n`;
                });
            }

            const docName = documentType.replace('_', ' ');
            return {
                message: `I've updated your ${docName} (now v${documentsData._version}).\n\n${result.conversational_response}${changesText}\n\n*Refresh the page to see the updated document.*`,
                showRefreshButton: true,
                validation: result.validation
            };

        } catch (error) {
            console.error('Refinement error:', error);
            return {
                message: `I couldn't refine the document: ${error.message}. Try rephrasing your request or ask me a different question.`,
                showRefreshButton: false
            };
        }
    }

    function addRefreshButton() {
        const messagesContainer = document.getElementById('askHenryMessages');
        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'ask-henry-refresh-btn';
        refreshBtn.innerHTML = 'Refresh to see changes';
        refreshBtn.onclick = () => window.location.reload();

        // Add some basic inline styles for the button
        refreshBtn.style.cssText = `
            display: block;
            margin: 12px auto;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        `;
        refreshBtn.onmouseover = () => {
            refreshBtn.style.transform = 'translateY(-2px)';
            refreshBtn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
        };
        refreshBtn.onmouseout = () => {
            refreshBtn.style.transform = 'translateY(0)';
            refreshBtn.style.boxShadow = 'none';
        };

        messagesContainer.appendChild(refreshBtn);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Create widget HTML
    function createWidget() {
        const context = getPageContext();
        const suggestions = getContextualSuggestions();
        const userName = getUserName();
        const greeting = getPersonalizedGreeting(userName, context);

        const widget = document.createElement('div');
        widget.id = 'ask-henry-widget';
        widget.innerHTML = `
            <!-- Floating Action Button -->
            <button class="ask-henry-fab" id="askHenryFab" aria-label="Chat with Henry">
                <span class="ask-henry-tooltip" id="askHenryTooltip">Hey, it's Henry!</span>
                <svg class="ask-henry-logo" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="fabRingGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                        </linearGradient>
                        <linearGradient id="fabStrokeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <circle cx="100" cy="100" r="85" stroke="url(#fabRingGradient)" stroke-width="4" fill="none"/>
                    <path d="M55 130 L55 70" stroke="#667eea" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <path d="M145 130 L145 50" stroke="url(#fabStrokeGradient)" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <path d="M55 100 L145 100" stroke="#764ba2" stroke-width="9" stroke-linecap="round" fill="none"/>
                    <circle cx="145" cy="50" r="9" fill="#764ba2"/>
                </svg>
            </button>

            <!-- Chat Drawer -->
            <div class="ask-henry-drawer" id="askHenryDrawer">
                <div class="ask-henry-header">
                    <div class="ask-henry-title">
                        <svg class="ask-henry-header-logo" width="28" height="28" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="headerRingGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                </linearGradient>
                                <linearGradient id="headerStrokeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle cx="100" cy="100" r="85" stroke="url(#headerRingGradient)" stroke-width="4" fill="none"/>
                            <path d="M55 130 L55 70" stroke="#667eea" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <path d="M145 130 L145 50" stroke="url(#headerStrokeGradient)" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <path d="M55 100 L145 100" stroke="#764ba2" stroke-width="9" stroke-linecap="round" fill="none"/>
                            <circle cx="145" cy="50" r="9" fill="#764ba2"/>
                        </svg>
                        <div>
                            <div class="ask-henry-title-text">Hey Henry <a class="ask-henry-history-link" id="askHenryHistoryLink" title="View previous conversations">History</a></div>
                            <div class="ask-henry-title-context" id="askHenryContext">${context.description}</div>
                        </div>
                    </div>
                    <div class="ask-henry-header-actions">
                        <button class="ask-henry-expand" id="askHenryExpand" aria-label="Expand" title="Expand chat">
                            <svg viewBox="0 0 24 24"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
                        </button>
                        <button class="ask-henry-close" id="askHenryClose" aria-label="Close" title="Close chat">×</button>
                    </div>
                </div>

                <div class="ask-henry-messages" id="askHenryMessages">
                    <div class="ask-henry-message assistant">
                        ${greeting}
                    </div>
                </div>

                <div class="ask-henry-suggestions" id="askHenrySuggestions">
                    ${suggestions.map(s => `<button class="ask-henry-suggestion">${s}</button>`).join('')}
                </div>

                <div class="ask-henry-attachments" id="askHenryAttachments"></div>
                <div class="ask-henry-input-area">
                    <textarea
                        class="ask-henry-input"
                        id="askHenryInput"
                        placeholder="Ask me anything..."
                        rows="1"
                    ></textarea>
                    <button class="ask-henry-attach" id="askHenryAttach" aria-label="Attach file" title="Attach file">
                        <svg viewBox="0 0 24 24"><path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/></svg>
                    </button>
                    <input type="file" id="askHenryFileInput" style="display: none;" multiple accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,.doc,.docx,text/plain">
                    <button class="ask-henry-send" id="askHenrySend" aria-label="Send">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                    </button>
                </div>
                <div class="ask-henry-drop-overlay">Drop files here</div>
            </div>
        `;

        document.body.appendChild(widget);

        // Load previous conversation history from sessionStorage (immediate)
        loadConversationHistory();

        // If there's existing conversation from sessionStorage, restore the messages
        if (conversationHistory.length > 0) {
            const messagesContainer = document.getElementById('askHenryMessages');
            // Clear the default greeting
            messagesContainer.innerHTML = '';

            // Add a "conversation continued" indicator
            messagesContainer.innerHTML = `
                <div class="ask-henry-message assistant" style="font-size: 0.85rem; opacity: 0.8;">
                    <em>Continuing our conversation...</em>
                </div>
            `;

            // Restore previous messages
            conversationHistory.forEach(msg => {
                const formattedContent = formatMessage(msg.content);
                const messageEl = document.createElement('div');
                messageEl.className = `ask-henry-message ${msg.role === 'user' ? 'user' : 'assistant'}`;
                messageEl.innerHTML = formattedContent;
                messagesContainer.appendChild(messageEl);
            });

            // Hide suggestions since conversation is ongoing
            document.getElementById('askHenrySuggestions').style.display = 'none';

            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } else {
            // No session conversation - check Supabase for recent conversation (async)
            // Small delay to ensure HenryData is loaded
            setTimeout(() => {
                loadConversationFromSupabase();
            }, 500);
        }

        // Bind events
        document.getElementById('askHenryFab').addEventListener('click', toggleDrawer);
        document.getElementById('askHenryClose').addEventListener('click', closeDrawer);
        document.getElementById('askHenrySend').addEventListener('click', sendMessage);
        document.getElementById('askHenryInput').addEventListener('keydown', handleKeyDown);

        // Expand/collapse button
        document.getElementById('askHenryExpand').addEventListener('click', toggleExpanded);

        // History link
        document.getElementById('askHenryHistoryLink').addEventListener('click', (e) => {
            e.preventDefault();
            showConversationHistory();
        });

        // Attachment button and file input
        const attachBtn = document.getElementById('askHenryAttach');
        const fileInput = document.getElementById('askHenryFileInput');

        attachBtn.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async (e) => {
            const files = Array.from(e.target.files);
            for (const file of files) {
                await addAttachment(file);
            }
            fileInput.value = ''; // Reset to allow re-selecting same file
        });

        // Drag and drop support
        const drawer = document.getElementById('askHenryDrawer');

        drawer.addEventListener('dragenter', (e) => {
            e.preventDefault();
            drawer.classList.add('drag-over');
        });

        drawer.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        drawer.addEventListener('dragleave', (e) => {
            // Only remove if leaving the drawer entirely
            if (!drawer.contains(e.relatedTarget)) {
                drawer.classList.remove('drag-over');
            }
        });

        drawer.addEventListener('drop', async (e) => {
            e.preventDefault();
            drawer.classList.remove('drag-over');

            const files = Array.from(e.dataTransfer.files);
            for (const file of files) {
                await addAttachment(file);
            }
        });

        // Suggestion clicks
        document.querySelectorAll('.ask-henry-suggestion').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('askHenryInput').value = btn.textContent;
                sendMessage();
            });
        });

        // Auto-resize textarea
        document.getElementById('askHenryInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });

        // Start random tooltip appearances
        startTooltipTimer();

        // Start proactive check-in monitoring (Phase 1.5)
        startProactiveCheckIns();

        // Also show tooltip on hover as fallback
        const fab = document.getElementById('askHenryFab');
        const tooltip = document.getElementById('askHenryTooltip');
        fab.addEventListener('mouseenter', () => {
            if (!isOpen) {
                tooltip.textContent = getRandomTooltipMessage();
                tooltip.classList.add('visible');
            }
        });
        fab.addEventListener('mouseleave', () => {
            tooltip.classList.remove('visible');
        });

        // Check if welcome flow should be triggered
        checkWelcomeFlow();
    }

    function toggleDrawer() {
        isOpen ? closeDrawer() : openDrawer();
    }

    function openDrawer() {
        isOpen = true;
        stopTooltipTimer(); // Stop random tooltips when chat is open
        document.getElementById('askHenryDrawer').classList.add('open');
        document.getElementById('askHenryFab').classList.add('hidden');
        document.getElementById('askHenryInput').focus();
    }

    function closeDrawer() {
        isOpen = false;
        document.getElementById('askHenryDrawer').classList.remove('open');
        document.getElementById('askHenryDrawer').classList.remove('expanded'); // Also collapse when closing
        document.getElementById('askHenryFab').classList.remove('hidden');
        startTooltipTimer(); // Resume random tooltips when chat is closed
    }

    function toggleExpanded() {
        const drawer = document.getElementById('askHenryDrawer');
        const expandBtn = document.getElementById('askHenryExpand');
        const isExpanded = drawer.classList.toggle('expanded');

        // Update button title
        expandBtn.title = isExpanded ? 'Collapse chat' : 'Expand chat';
        expandBtn.setAttribute('aria-label', isExpanded ? 'Collapse' : 'Expand');
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    async function sendMessage() {
        const input = document.getElementById('askHenryInput');
        const message = input.value.trim();
        if (!message || isLoading) return;

        // Add user message to UI
        addMessage('user', message);
        conversationHistory.push({ role: 'user', content: message });
        saveConversationHistory();
        input.value = '';
        input.style.height = 'auto';

        // Hide suggestions after first message
        document.getElementById('askHenrySuggestions').style.display = 'none';

        // Show typing indicator
        isLoading = true;
        addTypingIndicator();

        try {
            // Handle ongoing feedback flow - user is providing additional details
            if (feedbackFlowState === 'awaiting_details' && pendingFeedback) {
                // User provided follow-up details - append to feedback and ask for confirmation
                pendingFeedback.details = message;
                pendingFeedback.text = `${pendingFeedback.text}\n\nAdditional context: ${message}`;
                feedbackFlowState = 'awaiting_confirmation';

                removeTypingIndicator();

                // Now ask for confirmation to send
                let confirmMessage;
                if (pendingFeedback.type === 'bug') {
                    confirmMessage = "Got it, that's really helpful. Would you like me to send this to the team so they can look into it?";
                } else if (pendingFeedback.type === 'feature_request') {
                    confirmMessage = "That makes sense! Would you like me to pass this along to the Henry team?";
                } else if (pendingFeedback.type === 'praise') {
                    confirmMessage = "Love it! Would you like me to share this with the team? They'll appreciate hearing it.";
                } else {
                    confirmMessage = "Thanks for the context. Would you like me to send this to the team?";
                }

                addMessage('assistant', confirmMessage);
                conversationHistory.push({ role: 'assistant', content: confirmMessage });
                saveConversationHistory();
                addFeedbackConfirmation(pendingFeedback.type);
                isLoading = false;
                return;
            }

            // Check if user is asking HOW to give feedback or attach screenshots
            const lowerMessage = message.toLowerCase();
            const askingAboutFeedback = (
                (lowerMessage.includes('how') || lowerMessage.includes('can i') || lowerMessage.includes('where')) &&
                (lowerMessage.includes('feedback') || lowerMessage.includes('screenshot') || lowerMessage.includes('report') || lowerMessage.includes('bug') || lowerMessage.includes('attach'))
            );

            if (askingAboutFeedback && !pendingFeedback && !feedbackFlowState) {
                removeTypingIndicator();
                const helpMessage = "To share feedback, just tell me what's on your mind! Say something like 'I found a bug' or 'I have a suggestion' and I'll walk you through it. For bugs and UX issues, you'll get the option to attach a screenshot before sending. What would you like to share?";
                addMessage('assistant', helpMessage);
                conversationHistory.push({ role: 'assistant', content: helpMessage });
                saveConversationHistory();
                isLoading = false;
                return;
            }

            // Check for NEW feedback intent (not already in a flow)
            if (detectFeedbackIntent(message) && !pendingFeedback && !feedbackFlowState) {
                const feedbackType = categorizeFeedback(message);
                pendingFeedback = { text: message, type: feedbackType };

                removeTypingIndicator();

                // Check if we need a follow-up question
                const followUpQuestion = getFollowUpQuestion(feedbackType, message);

                if (followUpQuestion) {
                    // Ask for more details first
                    feedbackFlowState = 'awaiting_details';
                    addMessage('assistant', followUpQuestion);
                    conversationHistory.push({ role: 'assistant', content: followUpQuestion });
                    saveConversationHistory();
                    isLoading = false;
                    return;
                }

                // Already has enough detail - go straight to confirmation
                feedbackFlowState = 'awaiting_confirmation';

                // Craft a contextual response based on feedback type
                let promptMessage;
                if (feedbackType === 'bug') {
                    promptMessage = "That sounds like something the team should know about. Would you like me to send this to them so they can look into it?";
                } else if (feedbackType === 'feature_request') {
                    promptMessage = "That's a great idea! Would you like me to pass this suggestion along to the Henry team?";
                } else if (feedbackType === 'praise') {
                    promptMessage = "That's awesome to hear! Would you like me to share this with the team? They love knowing what's working well.";
                } else if (feedbackType === 'ux_issue') {
                    promptMessage = "Thanks for letting me know - that's helpful feedback. Would you like me to share this with the team so they can improve it?";
                } else {
                    promptMessage = "That sounds like valuable feedback. Would you like me to send this to the Henry team?";
                }

                addMessage('assistant', promptMessage);
                conversationHistory.push({ role: 'assistant', content: promptMessage });
                saveConversationHistory();
                addFeedbackConfirmation(feedbackType);
                isLoading = false;
                return;
            }

            // Check for document refinement requests (Phase 1.5)
            if (detectRefinementRequest(message)) {
                const currentPage = window.location.pathname;
                const isOnDocumentsPage = currentPage.includes('documents') || currentPage.includes('overview');

                if (!isOnDocumentsPage) {
                    // User wants to refine but isn't on documents page - redirect them
                    removeTypingIndicator();
                    const redirectMessage = "To make changes to your resume or cover letter, head over to the **Documents** page first. I can refine your documents there in real-time. Want me to explain what I'd change once you're there?";
                    addMessage('assistant', redirectMessage);
                    conversationHistory.push({ role: 'assistant', content: redirectMessage });
                    saveConversationHistory();
                    isLoading = false;
                    return;
                }

                const refinementResult = await handleRefinementRequest(message);
                if (refinementResult) {
                    removeTypingIndicator();
                    addMessage('assistant', refinementResult.message);
                    conversationHistory.push({ role: 'assistant', content: refinementResult.message });
                    saveConversationHistory();
                    if (refinementResult.showRefreshButton) {
                        addRefreshButton();
                    }
                    isLoading = false;
                    return;
                }
                // If refinementResult is null (e.g., no documents data), continue with normal chat
            }

            // Gather context
            const context = getPageContext();
            const analysisData = JSON.parse(sessionStorage.getItem('analysisData') || '{}');
            const resumeData = JSON.parse(sessionStorage.getItem('resumeData') || '{}');
            const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
            const pipelineData = getPipelineData();
            const userName = getUserName();
            const emotionalState = getUserEmotionalState();

            // Gather generated content - Henry is the AUTHOR of these
            const documentsData = getDocumentsData();
            const outreachData = getOutreachData();
            const interviewPrepData = getInterviewPrepData();
            const positioningData = getPositioningData();

            // Gather network data for proactive connection surfacing (Phase 2.1)
            const targetCompany = analysisData._company_name || analysisData.company || null;
            const networkData = getNetworkData(targetCompany);

            // Gather outreach log data for follow-up prompts (Phase 2.7)
            const outreachLogData = getOutreachLogData();

            // Gather interview debrief data for missing debrief prompts (Phase 2.3)
            const interviewDebriefData = getInterviewDebriefData();

            // Get cross-interview pattern analysis (Phase 2.3)
            const patternAnalysis = await getDebriefPatternAnalysis();

            // Generate tone guidance based on emotional state
            const toneGuidance = getToneGuidance(emotionalState);

            // Detect if message needs clarification
            const clarificationNeeds = detectClarificationNeeds(message);

            // Process attachments if any
            let attachmentsData = null;
            if (pendingAttachments.length > 0) {
                attachmentsData = await Promise.all(pendingAttachments.map(async (att) => ({
                    name: att.name,
                    type: att.type,
                    size: att.size,
                    data: await fileToBase64(att.file)
                })));
                clearAttachments(); // Clear after capturing
            }

            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

            // Build request body with error handling
            let requestBody;
            try {
                requestBody = JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(0, -1),
                    context: {
                        current_page: context.name,
                        page_description: context.description,
                        company: analysisData._company_name || analysisData.company || null,
                        role: analysisData.role_title || analysisData.role || null,
                        has_analysis: !!analysisData._company_name,
                        has_resume: !!resumeData.name,
                        has_pipeline: !!pipelineData,
                        user_name: userName,
                        // Emotional state for tone adaptation
                        emotional_state: emotionalState.holding_up,
                        confidence_level: emotionalState.confidence,
                        timeline: emotionalState.timeline,
                        tone_guidance: toneGuidance,
                        // Clarification detection
                        needs_clarification: clarificationNeeds.needs_clarification,
                        clarification_hints: clarificationNeeds.clarification_hints,
                        // Attachment info
                        has_attachments: !!attachmentsData && attachmentsData.length > 0
                    },
                    analysis_data: analysisData,
                    resume_data: resumeData,
                    user_profile: userProfile,
                    pipeline_data: pipelineData,
                    attachments: attachmentsData,
                    // Generated content - Henry is the AUTHOR
                    documents_data: documentsData,
                    outreach_data: outreachData,
                    interview_prep_data: interviewPrepData,
                    positioning_data: positioningData,
                    // Network data for proactive connection surfacing (Phase 2.1)
                    network_data: networkData,
                    // Outreach log data for follow-up prompts (Phase 2.7)
                    outreach_log_data: outreachLogData,
                    // Interview debrief data for missing debrief prompts (Phase 2.3)
                    interview_debrief_data: interviewDebriefData,
                    // Cross-interview pattern analysis (Phase 2.3)
                    debrief_pattern_analysis: patternAnalysis
                });
                console.log('Hey Henry request body size:', requestBody.length, 'bytes');
            } catch (jsonError) {
                console.error('Hey Henry JSON stringify error:', jsonError);
                throw new Error('Failed to prepare request');
            }

            // Log the request for debugging
            console.log('Hey Henry request:', {
                url: `${API_BASE}/api/hey-henry`,
                message: message.substring(0, 50),
                hasAnalysis: !!analysisData._company_name,
                hasResume: !!resumeData.name,
                bodySize: requestBody.length
            });

            const response = await fetch(`${API_BASE}/api/hey-henry`, {
                method: 'POST',
                mode: 'cors',
                credentials: 'omit',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                signal: controller.signal,
                body: requestBody
            });

            clearTimeout(timeoutId);
            console.log('Hey Henry response received:', { status: response.status, ok: response.ok });

            removeTypingIndicator();

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Hey Henry server error:', { status: response.status, body: errorText });
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            console.log('Hey Henry response parsed successfully');
            addMessage('assistant', data.response);
            conversationHistory.push({ role: 'assistant', content: data.response });
            saveConversationHistory();

        } catch (error) {
            console.error('Hey Henry error:', error);
            console.error('Error details:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            removeTypingIndicator();
            // More helpful error message with retry suggestion
            let errorMessage;
            if (error.name === 'AbortError') {
                errorMessage = "That took longer than expected. The server might be busy - try again in a moment.";
            } else if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
                // Network error - could be CORS, connectivity, or server down
                console.error('Network error - checking connectivity...');
                errorMessage = "I'm having trouble connecting. Please check your internet connection and try again.";
            } else if (error.message === 'Failed to get response') {
                errorMessage = "The server had an issue processing that. Let me try again - just resend your message.";
            } else {
                errorMessage = "Something unexpected happened. Try sending your message again.";
            }
            addMessage('assistant', errorMessage);
        }

        isLoading = false;
    }

    function addMessage(role, content) {
        const messagesContainer = document.getElementById('askHenryMessages');
        const formattedContent = formatMessage(content);

        // Format timestamp
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });

        const messageEl = document.createElement('div');
        messageEl.className = `ask-henry-message ${role}`;
        messageEl.innerHTML = `
            ${formattedContent}
            <span class="ask-henry-timestamp">${timeStr}</span>
        `;

        messagesContainer.appendChild(messageEl);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Auto-expand drawer for long assistant responses
        if (role === 'assistant' && content.length > 400) {
            const drawer = document.getElementById('askHenryDrawer');
            if (!drawer.classList.contains('expanded')) {
                drawer.classList.add('expanded');
                const expandBtn = document.getElementById('askHenryExpand');
                if (expandBtn) {
                    expandBtn.title = 'Collapse chat';
                    expandBtn.setAttribute('aria-label', 'Collapse');
                }
            }
        }
    }

    function formatMessage(content) {
        return content
            .split('\n\n').map(para => {
                if (para.match(/^[-•]\s/m)) {
                    const items = para.split('\n')
                        .filter(line => line.trim())
                        .map(line => `<li>${line.replace(/^[-•]\s*/, '')}</li>`)
                        .join('');
                    return `<ul>${items}</ul>`;
                }
                if (para.match(/^\d+\.\s/m)) {
                    const items = para.split('\n')
                        .filter(line => line.trim())
                        .map(line => `<li>${line.replace(/^\d+\.\s*/, '')}</li>`)
                        .join('');
                    return `<ol>${items}</ol>`;
                }
                return `<p>${para
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.+?)\*/g, '<em>$1</em>')
                }</p>`;
            })
            .join('');
    }

    function addTypingIndicator() {
        const messagesContainer = document.getElementById('askHenryMessages');
        const indicator = document.createElement('div');
        indicator.className = 'ask-henry-typing';
        indicator.id = 'askHenryTyping';
        indicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('askHenryTyping');
        if (indicator) indicator.remove();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }

    // Expose global functions for external access
    window.openHeyHenry = function() {
        openDrawer();
    };

    // Keep legacy function for backwards compatibility
    window.openAskHenry = window.openHeyHenry;

    window.openHeyHenryWithPrompt = function(prompt) {
        openDrawer();
        // Small delay to ensure drawer is open and input is ready
        setTimeout(() => {
            const input = document.getElementById('askHenryInput');
            if (input) {
                input.value = prompt;
                sendMessage();
            }
        }, 100);
    };

    // Keep legacy function for backwards compatibility
    window.openAskHenryWithPrompt = window.openHeyHenryWithPrompt;

    // Close functions for external access
    window.closeHeyHenry = function() {
        closeDrawer();
    };

    // Keep legacy function for backwards compatibility
    window.closeAskHenry = window.closeHeyHenry;

    // ==========================================
    // Admin Notification Polling (Real-time alerts)
    // ==========================================

    let adminNotificationInterval = null;
    let lastNotificationCheck = 0;
    const NOTIFICATION_CHECK_INTERVAL = 30000; // 30 seconds

    async function checkAdminNotifications() {
        // Only check if HenryAuth is available
        if (typeof HenryAuth === 'undefined') return;

        try {
            const user = await HenryAuth.getUser();
            if (!user?.email) return;

            const response = await fetch(`${API_BASE}/api/admin/notifications?user_email=${encodeURIComponent(user.email)}`);
            if (!response.ok) return;

            const data = await response.json();

            // Not an admin, stop polling
            if (!data.is_admin) {
                if (adminNotificationInterval) {
                    clearInterval(adminNotificationInterval);
                    adminNotificationInterval = null;
                }
                return;
            }

            // Show notifications in Hey Henry
            if (data.notifications && data.notifications.length > 0) {
                const notification = data.notifications[0]; // Show most recent

                // Open Hey Henry drawer
                openDrawer();

                // Add notification message
                const typeEmoji = {
                    'bug': '🐛', 'feature_request': '💡', 'praise': '🎉',
                    'ux_issue': '🎨', 'general': '💬'
                }[notification.feedback_type] || '📬';

                const fromDisplay = notification.from_name || notification.from_email || 'Someone';
                const notificationMessage = `**${typeEmoji} New Feedback Alert**\n\n**From:** ${fromDisplay} (${notification.from_email})\n**Type:** ${notification.feedback_type?.replace('_', ' ')}\n**Page:** ${notification.current_page || 'Unknown'}\n\n> ${notification.summary || notification.full_content?.substring(0, 200) || 'No details'}\n\n*Click here or reply to respond to them directly.*`;

                addMessage('assistant', notificationMessage);
                conversationHistory.push({ role: 'assistant', content: notificationMessage });
                saveConversationHistory();

                // Mark as read
                fetch(`${API_BASE}/api/admin/notifications/${notification.id}/read?user_email=${encodeURIComponent(user.email)}`, {
                    method: 'POST'
                }).catch(e => console.warn('Could not mark notification read:', e));

                // Play a subtle sound or visual indicator
                const fab = document.querySelector('.ask-henry-fab');
                if (fab) {
                    fab.style.animation = 'pulse 0.5s ease-in-out 3';
                    setTimeout(() => fab.style.animation = '', 1500);
                }
            }
        } catch (e) {
            console.warn('Admin notification check failed:', e);
        }
    }

    // Start polling after widget is created
    function startAdminNotificationPolling() {
        // Initial check after 5 seconds
        setTimeout(checkAdminNotifications, 5000);

        // Then poll every 30 seconds
        adminNotificationInterval = setInterval(checkAdminNotifications, NOTIFICATION_CHECK_INTERVAL);
    }

    // Start polling when widget initializes
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startAdminNotificationPolling);
    } else {
        startAdminNotificationPolling();
    }
})();
