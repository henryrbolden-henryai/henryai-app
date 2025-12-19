# HenryHQ Command Center — Visual Design Spec

**Version:** 1.0  
**Date:** December 18, 2025  
**Dependencies:** COMMAND_CENTER_IMPLEMENTATION_SPEC.md (v2.0)  
**Scope:** UI/UX design, layout, visual hierarchy, interaction patterns

---

## **Design Philosophy**

The Command Center is not a dashboard. It's a cockpit.

Every visual element must answer:
- **What's urgent?** (what needs attention now)
- **What's working?** (where to double down)
- **What's failing?** (where to disengage)

If a design element doesn't serve one of those three questions, cut it.

---

## **1. Visual Hierarchy Principles**

### **Priority-Driven Layout**

Information hierarchy follows urgency:

1. **Critical actions** — Above the fold, impossible to miss
2. **High-priority applications** — Primary visual weight
3. **Medium-priority applications** — Secondary visual weight
4. **Low-priority / archived** — Dimmed or hidden

### **Color as Signal, Not Decoration**

Color must always mean something:
- **Green** = High confidence, keep going
- **Yellow** = Medium confidence, watch closely
- **Red** = Low confidence, consider disengaging
- **Gray** = Archived, low priority

Never use color for aesthetics alone.

### **Whitespace as Focus**

More whitespace around high-priority items. Less around low-priority items.

Focus Mode: Everything but top 2-3 actions fades to 30% opacity.

---

## **2. Layout Structure**

### **Three-Section Layout**

```
┌─────────────────────────────────────────────────────┐
│                    HEADER                            │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         DAILY PULSE (Intelligence)           │  │
│  │  • What matters today                        │  │
│  │  • Top 2-3 actions                           │  │
│  │  • Pipeline health status                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         VIEW SELECTOR                        │  │
│  │  [Board] [List] [Timeline]                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │                                              │  │
│  │         APPLICATIONS VIEW                    │  │
│  │  (Board / List / Timeline based on toggle)  │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## **3. Daily Pulse Banner (Intelligence Hub)**

### **Purpose**
Single source of truth for "what should I do today?"

### **Layout**

```
┌───────────────────────────────────────────────────────────┐
│  Good morning, Jordan! Here's what matters today:         │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │  ⚠️  Stripe       │  │  🔥  Plaid        │             │
│  │  Send follow-up  │  │  Interview prep   │             │
│  │  [Take Action]   │  │  [Review Guide]   │             │
│  └──────────────────┘  └──────────────────┘             │
│                                                            │
│  Pipeline Health: Healthy ✅                              │
│  Good volume. Shift energy to conversion.                 │
└───────────────────────────────────────────────────────────┘
```

### **Visual Specs**

**Container:**
- Background: `linear-gradient(135deg, rgba(34, 211, 238, 0.1), rgba(96, 165, 250, 0.1))`
- Border: `1px solid rgba(34, 211, 238, 0.3)`
- Border radius: `16px`
- Padding: `24px`
- Margin bottom: `32px`

**Greeting:**
- Font size: `1.1rem`
- Font weight: `500`
- Color: `--color-text`
- Margin bottom: `16px`

**Action Cards (inline):**
- Display: `flex`, `gap: 16px`
- Each card:
  - Background: `rgba(0, 0, 0, 0.2)`
  - Border radius: `12px`
  - Padding: `16px`
  - Width: `auto` (flexible)

**Action Card Content:**
- Icon: `font-size: 1.5rem`, margin bottom `8px`
- Company: `font-weight: 600`, `font-size: 1rem`
- Action text: `font-size: 0.9rem`, `color: --color-text-secondary`
- Button: 
  - Background: `--color-accent`
  - Color: `#000`
  - Padding: `8px 16px`
  - Border radius: `8px`
  - Font weight: `600`

**Pipeline Health:**
- Font size: `0.95rem`
- Icon inline with text
- Color based on tone:
  - Steady: `--color-active` (green)
  - Caution: `#f59e0b` (yellow)
  - Urgent: `#ef4444` (red)

---

## **4. View Selector**

### **Purpose**
Switch between Board, List, and Timeline views.

### **Layout**

```
┌─────────────────────────────────────┐
│  [Board]  [List]  [Timeline]        │
└─────────────────────────────────────┘
```

### **Visual Specs**

**Container:**
- Display: `flex`
- Gap: `4px`
- Background: `--color-surface`
- Border: `1px solid --color-border`
- Border radius: `10px`
- Padding: `4px`
- Margin bottom: `24px`

**Tab Buttons:**
- Padding: `10px 20px`
- Border radius: `8px`
- Background: `transparent`
- Color: `--color-text-secondary`
- Font weight: `500`
- Font size: `0.9rem`
- Cursor: `pointer`
- Transition: `all 0.2s`

**Active State:**
- Background: `--color-accent-muted`
- Color: `--color-accent`
- Font weight: `600`

**Hover State (inactive tabs):**
- Background: `rgba(255, 255, 255, 0.05)`
- Color: `--color-text`

---

## **5. Board View (Default)**

### **Purpose**
Kanban-style columns by status. Visual grouping of pipeline stages.

### **Layout**

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  Applied    │  Screening  │  Interviews │  Final      │
│  (3)        │  (2)        │  (4)        │  (1)        │
│             │             │             │             │
│  [Card]     │  [Card]     │  [Card]     │  [Card]     │
│  [Card]     │  [Card]     │  [Card]     │             │
│  [Card]     │             │  [Card]     │             │
│             │             │  [Card]     │             │
│             │             │  [Card]     │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### **Visual Specs**

**Board Container:**
- Display: `grid`
- Grid template columns: `repeat(4, 1fr)`
- Gap: `16px`
- Min height: `600px`

**Column:**
- Background: `--color-surface`
- Border: `1px solid --color-border`
- Border radius: `12px`
- Padding: `16px`

**Column Header:**
- Font size: `0.85rem`
- Font weight: `600`
- Color: `--color-text-secondary`
- Text transform: `uppercase`
- Letter spacing: `0.5px`
- Margin bottom: `16px`
- Display: `flex`
- Justify content: `space-between`

**Count Badge:**
- Background: `--color-border`
- Color: `--color-text`
- Padding: `2px 8px`
- Border radius: `12px`
- Font size: `0.75rem`

**Card Spacing:**
- Gap: `12px` between cards
- Cards stack vertically

---

## **6. Application Card (Core Component)**

### **Purpose**
Single source of truth for each application. Must surface urgency, confidence, and next action.

### **Anatomy**

```
┌─────────────────────────────────────────────────┐
│  🔥  Stripe - Senior Product Manager            │  ← Header (icon + title)
│                                          [📊]    │  ← Badges
│                                                  │
│  Fit: 72% (Directional)   Confidence: Medium   │  ← Stats row
│  7 days since activity                          │
│                                                  │
│  Next: Send follow-up email                     │  ← Action (bold)
│  70% respond by now. Silence = ghosting.        │  ← Reason (muted)
│                                                  │
│  [Draft Email]                                  │  ← One-click button
└─────────────────────────────────────────────────┘
```

### **Visual Specs**

**Container:**
- Background: `--color-surface-elevated`
- Border: `2px solid [color based on confidence]`
  - High confidence: `#10b981` (green)
  - Medium confidence: `#f59e0b` (yellow)
  - Low confidence: `#ef4444` (red)
- Border radius: `12px`
- Padding: `16px`
- Transition: `all 0.2s`

**Header:**
- Display: `flex`
- Justify content: `space-between`
- Align items: `flex-start`
- Margin bottom: `12px`

**Icon:**
- Font size: `1.2rem`
- Margin right: `8px`
- Position: `inline`

**Title:**
- Font size: `1rem`
- Font weight: `600`
- Color: `--color-text`
- Line height: `1.3`

**Badge (Directional/Refined):**
- Background: `rgba(34, 211, 238, 0.15)`
- Color: `--color-accent`
- Padding: `2px 8px`
- Border radius: `6px`
- Font size: `0.7rem`
- Font weight: `600`
- Text transform: `uppercase`
- Letter spacing: `0.5px`

**Stats Row:**
- Display: `flex`
- Gap: `16px`
- Flex wrap: `wrap`
- Margin bottom: `12px`
- Font size: `0.85rem`
- Color: `--color-text-secondary`

**Stat Item:**
- Display: `inline-flex`
- Align items: `center`
- Gap: `4px`

**Next Action Section:**
- Background: `rgba(34, 211, 238, 0.08)`
- Border left: `3px solid --color-accent`
- Padding: `12px`
- Border radius: `6px`
- Margin bottom: `12px`

**Next Action Text:**
- Font size: `0.9rem`
- Font weight: `600`
- Color: `--color-text`
- Margin bottom: `4px`

**Action Reason:**
- Font size: `0.85rem`
- Color: `--color-text-secondary`
- Line height: `1.4`

**One-Click Button:**
- Background: `--color-accent`
- Color: `#000`
- Border: `none`
- Padding: `10px 16px`
- Border radius: `8px`
- Font size: `0.85rem`
- Font weight: `600`
- Cursor: `pointer`
- Width: `100%`
- Transition: `all 0.2s`

**Button Hover:**
- Opacity: `0.9`
- Transform: `translateY(-1px)`

**Dimmed State (Focus Mode):**
- Opacity: `0.3`
- Pointer events: `none` (unless card is clicked)

**Urgent State:**
- Add pulsing animation to icon
- Border glow effect

---

## **7. List View**

### **Purpose**
Dense, sortable table view. For users who want to see everything at once.

### **Layout**

```
┌──────────┬──────────────┬────────┬────────────┬─────────────┬──────────┐
│ Priority │ Company      │ Fit    │ Confidence │ Next Action │ Days     │
├──────────┼──────────────┼────────┼────────────┼─────────────┼──────────┤
│ 🔥 High  │ Stripe       │ 72%    │ Medium     │ Follow-up   │ 7 days   │
│ ⏳ Med   │ Plaid        │ 68%    │ Medium     │ Prep guide  │ 2 days   │
│ ❄️ Low   │ Coinbase     │ 45%    │ Low        │ Deprioritize│ 14 days  │
└──────────┴──────────────┴────────┴────────────┴─────────────┴──────────┘
```

### **Visual Specs**

**Table Container:**
- Background: `--color-surface`
- Border: `1px solid --color-border`
- Border radius: `12px`
- Overflow: `hidden`

**Table:**
- Width: `100%`
- Border collapse: `separate`
- Border spacing: `0`

**Header Row:**
- Background: `--color-surface-elevated`
- Border bottom: `2px solid --color-border`

**Header Cell:**
- Padding: `12px 16px`
- Font size: `0.8rem`
- Font weight: `600`
- Color: `--color-text-secondary`
- Text transform: `uppercase`
- Letter spacing: `0.5px`
- Text align: `left`
- Cursor: `pointer` (sortable)

**Header Cell Hover:**
- Color: `--color-text`

**Body Row:**
- Border bottom: `1px solid --color-border`
- Transition: `background 0.2s`

**Body Row Hover:**
- Background: `rgba(255, 255, 255, 0.02)`

**Body Cell:**
- Padding: `14px 16px`
- Font size: `0.9rem`
- Color: `--color-text`

**Priority Cell:**
- Display: `flex`
- Align items: `center`
- Gap: `8px`

**Icon + Text:**
- Icon: `font-size: 1.1rem`
- Text: `font-size: 0.85rem`, `font-weight: 500`

**Fit Cell:**
- Font variant numeric: `tabular-nums`
- Font weight: `600`

**Confidence Cell:**
- Pill-style badge:
  - Background: color-coded
  - Padding: `4px 10px`
  - Border radius: `12px`
  - Font size: `0.8rem`
  - Font weight: `500`

**Row Click:**
- Expands inline to show full card details
- Or opens modal with full card

---

## **8. Timeline View**

### **Purpose**
Visual momentum tracker. See application velocity and patterns over time.

### **Layout**

```
Applications & Interviews Over Time

    │
 15 │     ●
    │    ╱ ╲
 10 │   ●   ●     ●
    │  ╱     ╲   ╱ ╲
  5 │ ●       ● ●   ●
    │
  0 └─────────────────────────
      W1  W2  W3  W4  W5  W6

Legend:
● Applied    ● Interview    ● Offer    ● Rejection
```

### **Visual Specs**

**Container:**
- Background: `--color-surface`
- Border: `1px solid --color-border`
- Border radius: `12px`
- Padding: `24px`
- Min height: `400px`

**Chart:**
- Use Chart.js or similar
- Line chart with multiple series
- Color-coded by event type:
  - Applied: `#60a5fa` (blue)
  - Interview: `#f59e0b` (yellow)
  - Offer: `#10b981` (green)
  - Rejection: `#ef4444` (red)

**Insight Callouts:**
- Position above/below chart
- Background: `rgba(34, 211, 238, 0.1)`
- Border left: `3px solid --color-accent`
- Padding: `12px`
- Font size: `0.9rem`
- Border radius: `6px`

**Example Callout:**
```
Week of Nov 18: 5 applications → 2 interviews
Your tailoring strategy is working.
```

---

## **9. Focus Mode**

### **Purpose**
Reduce cognitive load. Show only top 2-3 actions.

### **Trigger**
- Button in header: "Focus Mode"
- Keyboard shortcut: `F`

### **Behavior**

**When enabled:**
1. Daily Pulse stays fully visible
2. Top 2-3 priority applications stay at 100% opacity
3. All other applications fade to 30% opacity
4. "View all" button appears below priority apps

**Visual Changes:**
```css
.application-card.dimmed {
  opacity: 0.3;
  pointer-events: none;
}

.application-card.priority-high,
.application-card.priority-medium.urgent {
  opacity: 1;
  box-shadow: 0 4px 20px rgba(34, 211, 238, 0.2);
}
```

**"View All" Button:**
- Background: `transparent`
- Border: `1px dashed --color-border`
- Padding: `12px`
- Border radius: `8px`
- Color: `--color-text-secondary`
- Font size: `0.9rem`
- Cursor: `pointer`
- Text align: `center`

**Button Hover:**
- Border color: `--color-accent`
- Color: `--color-accent`

---

## **10. User Override Indicator**

### **Purpose**
Show when user has manually overridden system guidance.

### **Visual Treatment**

**Override Badge:**
- Position: Top right of card
- Background: `rgba(251, 191, 36, 0.2)`
- Border: `1px solid #f59e0b`
- Padding: `4px 8px`
- Border radius: `6px`
- Font size: `0.7rem`
- Font weight: `600`
- Color: `#f59e0b`
- Text: "Manual Override"

**Tooltip (on hover):**
- Background: `--color-surface-elevated`
- Border: `1px solid --color-border`
- Padding: `8px 12px`
- Border radius: `8px`
- Max width: `200px`
- Font size: `0.85rem`
- Box shadow: `0 4px 12px rgba(0, 0, 0, 0.3)`

**Tooltip Content:**
```
Manual Override Active
Reason: Strategic relationship. 
Worth staying on radar.
```

---

## **11. Strategic Stop Warning**

### **Purpose**
Circuit breaker visual. Impossible to miss.

### **Layout**

```
┌─────────────────────────────────────────────────┐
│  ⛔ Strategic Stop Triggered                     │
│                                                  │
│  You've applied to 10+ roles with <5% interview │
│  rate. Something's broken.                      │
│                                                  │
│  Recommended Actions:                           │
│  • Review resume positioning                    │
│  • Analyze rejection patterns                   │
│  • Get second-pass analysis                     │
│                                                  │
│  Applications paused for 7 days.                │
│                                                  │
│  [Review Strategy] [Override (not recommended)] │
└─────────────────────────────────────────────────┘
```

### **Visual Specs**

**Container:**
- Background: `linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.15))`
- Border: `2px solid #ef4444`
- Border radius: `12px`
- Padding: `24px`
- Margin bottom: `32px`
- Position: Above all applications

**Icon + Title:**
- Font size: `1.3rem`
- Font weight: `700`
- Color: `#ef4444`
- Display: `flex`
- Align items: `center`
- Gap: `12px`
- Margin bottom: `16px`

**Body Text:**
- Font size: `0.95rem`
- Color: `--color-text`
- Line height: `1.6`
- Margin bottom: `16px`

**Recommended Actions:**
- Bullet list
- Font size: `0.9rem`
- Color: `--color-text-secondary`
- Margin bottom: `16px`

**Pause Notice:**
- Font size: `0.85rem`
- Color: `#fca5a5`
- Font weight: `600`
- Margin bottom: `16px`

**Buttons:**
- Display: `flex`
- Gap: `12px`

**Primary Button (Review Strategy):**
- Background: `#ef4444`
- Color: `#fff`
- Padding: `12px 24px`
- Border: `none`
- Border radius: `8px`
- Font weight: `600`
- Cursor: `pointer`

**Secondary Button (Override):**
- Background: `transparent`
- Color: `--color-text-secondary`
- Border: `1px solid --color-border`
- Padding: `12px 24px`
- Border radius: `8px`
- Font weight: `500`
- Cursor: `pointer`

---

## **12. Mobile Responsive**

### **Breakpoints**

- Desktop: `> 1024px` — Full layout
- Tablet: `768px - 1024px` — 2-column board, full list
- Mobile: `< 768px` — Single column, list view default

### **Mobile Adaptations**

**Daily Pulse:**
- Stack action cards vertically
- Full width buttons

**Board View:**
- Single column (scrollable horizontally if needed)
- Or force List view on mobile

**Application Card:**
- Maintain full detail
- Stack stats vertically if needed

**List View:**
- Show priority, company, next action only
- Tap to expand full details

---

## **13. Interaction States**

### **Loading States**

**Initial Load:**
- Skeleton loaders for cards
- Pulse animation
- Gray rectangles matching card dimensions

**Action in Progress:**
- Button shows spinner
- Button text: "Sending..." / "Archiving..." / etc.
- Disable button during action

**Data Refresh:**
- Subtle indicator in header
- No jarring full-page reload

### **Hover States**

**Application Card:**
- Slight elevation: `transform: translateY(-2px)`
- Box shadow increase

**Buttons:**
- Opacity: `0.9`
- Slight elevation

**List Row:**
- Background: `rgba(255, 255, 255, 0.02)`

### **Active/Selected States**

**Selected Application:**
- Border glow
- Slight background tint

**Active View Tab:**
- Background: `--color-accent-muted`
- Color: `--color-accent`

---

## **14. Animation Guidelines**

### **Principles**
- Animations serve function, not aesthetics
- Duration: 150-300ms max
- Easing: `ease-out` for entrances, `ease-in` for exits

### **Key Animations**

**Card Entrance:**
```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.application-card {
  animation: slideIn 200ms ease-out;
}
```

**Focus Mode Transition:**
```css
.application-card {
  transition: opacity 300ms ease-out, transform 300ms ease-out;
}

.application-card.dimmed {
  opacity: 0.3;
  transform: scale(0.98);
}
```

**Urgent Pulse (for immediate actions):**
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.icon.urgent {
  animation: pulse 2s ease-in-out infinite;
}
```

---

## **15. Color System (Extended)**

### **Core Palette** (from existing design)

```css
--color-bg: #0a0a0b;
--color-surface: #141416;
--color-surface-elevated: #1c1c1f;
--color-border: rgba(255, 255, 255, 0.08);
--color-text: #fafafa;
--color-text-secondary: #71717a;
--color-accent: #22d3ee;
```

### **New Signal Colors**

```css
/* Confidence levels */
--color-confidence-high: #10b981;
--color-confidence-medium: #f59e0b;
--color-confidence-low: #ef4444;

/* Priority levels */
--color-priority-high: #ef4444;
--color-priority-medium: #f59e0b;
--color-priority-low: #71717a;
--color-priority-archive: #52525b;

/* Urgency indicators */
--color-urgent: #dc2626;
--color-urgent-muted: rgba(220, 38, 38, 0.15);

/* Override indicator */
--color-override: #f59e0b;
--color-override-muted: rgba(251, 191, 36, 0.2);

/* Pipeline health */
--color-healthy: #10b981;
--color-caution: #f59e0b;
--color-stalled: #ef4444;
```

---

## **16. Typography System**

### **Font Stack**

```css
--font-display: 'Instrument Serif', Georgia, serif;
--font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'SF Mono', Monaco, 'Courier New', monospace;
```

### **Type Scale**

```css
/* Headers */
--text-xxl: 2.25rem;  /* Page title */
--text-xl: 1.5rem;    /* Section headers */
--text-lg: 1.25rem;   /* Card titles */

/* Body */
--text-base: 1rem;    /* Primary text */
--text-sm: 0.9rem;    /* Secondary text */
--text-xs: 0.85rem;   /* Metadata */
--text-xxs: 0.75rem;  /* Labels, badges */

/* Weights */
--weight-bold: 700;
--weight-semibold: 600;
--weight-medium: 500;
--weight-normal: 400;
```

---

## **17. Implementation Checklist**

### **Phase 1: Core Components**
- [ ] Daily Pulse banner with intelligence integration
- [ ] Application card with UI signals binding
- [ ] View selector (Board/List/Timeline tabs)
- [ ] Board view layout
- [ ] List view table

### **Phase 2: Advanced Features**
- [ ] Focus Mode toggle and dimming
- [ ] Timeline view with Chart.js
- [ ] User override badge and tooltip
- [ ] Strategic stop warning banner

### **Phase 3: Polish**
- [ ] Loading states and skeletons
- [ ] Hover/active states
- [ ] Animations (card entrance, focus transition, urgent pulse)
- [ ] Mobile responsive layouts

### **Phase 4: Edge Cases**
- [ ] Empty states
- [ ] Error states
- [ ] Offline indicators
- [ ] Keyboard navigation

---

## **18. Design Tokens (CSS Variables)**

Complete reference for developers:

```css
:root {
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;
  --space-xxl: 32px;
  
  /* Border radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4);
  
  /* Transitions */
  --transition-fast: 150ms ease-out;
  --transition-base: 200ms ease-out;
  --transition-slow: 300ms ease-out;
}
```

---

## **19. Accessibility Requirements**

### **Keyboard Navigation**
- Tab through all interactive elements
- Enter/Space to activate buttons
- Escape to close modals/tooltips
- Focus visible indicator: `outline: 2px solid --color-accent`

### **Screen Reader Support**
- All icons have `aria-label`
- Card status announced: "High priority, Stripe, 7 days since activity"
- Confidence level announced: "Medium confidence"
- Action buttons have descriptive labels

### **Color Contrast**
- Minimum 4.5:1 for body text
- Minimum 3:1 for large text
- Test with tools like WebAIM Contrast Checker

### **Focus Indicators**
```css
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

---

## **20. Success Criteria**

The visual design succeeds if:

1. **Users can identify top priority in <2 seconds**
2. **Confidence signals are immediately understood** (green/yellow/red)
3. **Next actions are impossible to miss**
4. **Focus Mode reduces visual noise by 70%+**
5. **Strategic stop warning is jarring (by design)**
6. **No user asks "what should I do next?"**

---

**End of Visual Spec**

This design is opinionated, function-first, and binds directly to UI signals from the backend. No business logic in the frontend. Pure presentation layer.
