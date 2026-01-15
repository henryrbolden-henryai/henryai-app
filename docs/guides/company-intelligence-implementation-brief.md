# HenryHQ Company Intelligence Feature — Implementation Brief

**Version:** 1.0  
**Date:** January 3, 2025  
**Status:** Approved  

---

## Executive Summary

Add company health intelligence to HenryHQ that helps candidates answer: "Is this company worth my time?" This feature surfaces stability signals, risk factors, and strategic guidance that changes how candidates approach opportunities.

**Deliverables:**

1. Reality Check integration (one-liner signals in existing results flow)
2. Market Context grid update (add "Company" as fourth item)
3. Standalone Company Analysis page (full breakdown with actionable guidance)
4. Overview page update (replace Pipeline Command Center card with Company Analysis)

**Timeline:** Both deliverables ship before mid-January launch.

---

## Strategic Context

**Problem:** Candidates walk into interviews blind to company health. They invest 8-12 hours in interview processes without knowing the company just laid off 15% of staff, missed earnings, or has a CEO under fire. This information asymmetry favors the employer.

**Solution:** Surface validated company health signals with context on what they mean and how to respond. Not a data dump. Strategic intelligence.

**Positioning:** Most job search tools help you find jobs. HenryHQ helps you evaluate them.

> "This feature quietly turns HenryHQ from a job tool into a judgment engine."

---

## Feature Architecture

### Data Layer: `backend/services/company_intel.py`

Single service that fetches and synthesizes company health data. Used by Reality Check, Market Context grid, and the standalone page.

**Input:**

```python
def get_company_intelligence(
    company_name: str,
    ticker_symbol: Optional[str] = None,  # For public companies
    company_url: Optional[str] = None     # LinkedIn or website for context
) -> CompanyIntelligence:
```

**Output structure:**

```python
@dataclass
class CompanyIntelligence:
    company_name: str
    company_health_signal: HealthSignal   # GREEN, YELLOW, RED
    confidence: ConfidenceLevel           # HIGH, MEDIUM, LOW
    findings: List[CompanyFinding]        # Sourced facts
    what_this_means: str                  # Plain-language synthesis
    interview_questions: List[str]        # Questions to ask (always populated)
    negotiation_guidance: List[str]       # If you get an offer
    data_freshness: datetime              # When data was fetched
    sources_checked: List[str]            # Transparency on coverage

@dataclass
class CompanyFinding:
    finding: str                          # "Laid off 18% of workforce"
    source: str                           # "Layoffs.fyi"
    date: Optional[str]                   # "Oct 2024"
    severity: FindingSeverity             # HIGH, MEDIUM, LOW
    url: Optional[str]                    # Link to source
```

**Health Signal Logic:**

```
🟢 STABLE: No negative signals found, or only minor concerns
🟡 WATCH: One or more medium-severity signals (layoffs <15%, stock down 15-30%, stale funding)
🔴 RISK: High-severity signals (layoffs >15%, stock down >30%, leadership exodus, failed funding)
```

---

### Data Sources (Tiered Implementation)

**Tier 1 — Ship in v1 (Claude web search synthesis):**

| Source | Signal Type | Implementation |
|--------|-------------|----------------|
| Web search: "[company] layoffs 2024" | Workforce reductions | Claude synthesis |
| Web search: "[company] stock price" | Public company health | Claude synthesis |
| Web search: "[company] funding round" | Private company runway | Claude synthesis |
| Web search: "[company] CEO resignation OR leadership" | Leadership stability | Claude synthesis |

**Implementation approach:** Single Claude API call with web search tool enabled. Structured prompt that returns JSON matching the `CompanyIntelligence` schema.

**Prompt structure:**

```
You are a company research analyst. Search for recent news about {company_name} 
focusing on:
1. Layoffs or workforce reductions (past 12 months)
2. Stock performance (if public company)
3. Funding status (if private company) 
4. Leadership changes (CEO, CFO, CPO turnover)
5. Major regulatory or legal issues

Return your findings as structured JSON. Only include findings you can verify 
from search results. Do not speculate. If you find no negative signals, say so.

IMPORTANT: Ignore opinion blogs, Medium posts, and unverified sources unless 
corroborated by primary sources (company announcements, SEC filings, major 
news outlets).

For each finding, assess severity:
- HIGH: Layoffs >15%, stock down >30%, CEO departure, failed funding round
- MEDIUM: Layoffs 5-15%, stock down 15-30%, C-suite turnover (not CEO), flat funding
- LOW: Layoffs <5%, stock down <15%, VP-level departures, successful funding

Based on findings, provide:
1. Overall health signal (GREEN/YELLOW/RED)
2. Plain-language summary of what this means for a job candidate
3. 3-4 questions the candidate should ask in interviews (even for GREEN companies)
4. 2-3 negotiation considerations if they get an offer
```

**Tier 2 — Post-launch enhancement:**

| Source | Signal Type | Implementation |
|--------|-------------|----------------|
| Layoffs.fyi | Verified layoff data | Scrape or manual curation |
| Yahoo Finance API | Stock performance | Direct API integration |
| Glassdoor | Employee sentiment trends | Scrape aggregate scores |
| LinkedIn | "Open to Work" spikes | Manual monitoring |

**Tier 3 — Future consideration:**

| Source | Signal Type | Implementation |
|--------|-------------|----------------|
| Crunchbase API | Funding details | Paid API ($) |
| SEC EDGAR | 8-K/10-K filings | Complex parsing |
| Blind | Unfiltered employee intel | Scrape (fragile) |

---

## Integration Points

### Integration Point 1: Market Context Grid (Results Page)

**File:** `frontend/results.html`

**Location:** Market Context section (lines 1464-1481)

**Change:** Add fourth grid item for Company health signal.

**Updated grid:**

| Demand | Salary | Action | Company |
|--------|--------|--------|---------|
| Competitive | $150-180K | Apply now | 🟡 Watch |

**HTML addition:**

```html
<div class="market-item">
    <span class="market-label">Company</span>
    <a href="company-analysis.html" class="market-value company-health-link" id="marketCompanyHealth">—</a>
</div>
```

**Display logic:**

- 🟢 STABLE → "✓ Stable" (green text, clickable)
- 🟡 WATCH → "⚠ Watch" (yellow text, clickable)
- 🔴 RISK → "⚠ Risk" (red text, clickable)
- No data → "—" (gray, not clickable)

**Rationale:** Company health is an external factor about the opportunity. It belongs with demand, salary, and timing. Progressive disclosure: grid shows signal, Company Analysis page shows full breakdown.

---

### Integration Point 2: Reality Check Signal

**File:** `backend/reality_check/signal_detectors.py`

**New function:**

```python
def detect_company_health_signals(
    company_name: str,
    company_intel: Optional[CompanyIntelligence] = None
) -> List[RealityCheck]:
    """
    Generate Reality Check signals based on company health data.
    
    Returns at most 1 signal to avoid overwhelming the candidate.
    Only surfaces YELLOW or RED health signals.
    """
```

**Signal class:** `SignalClass.MARKET_CLIMATE` (existing)

**Severity mapping:**

- 🟡 WATCH → `Severity.INFORMATIONAL`
- 🔴 RISK → `Severity.COACHING`

Never `BLOCKER` or `WARNING`. Company health informs, it doesn't override candidate agency.

**Example output:**

```python
RealityCheck(
    signal_class=SignalClass.MARKET_CLIMATE,
    severity=Severity.COACHING,
    message="Grindr announced 20% layoffs in Q3 2024 and stock is down 40% YTD. If you proceed, ask about runway and team stability directly.",
    strategic_alternatives=[
        "Negotiate for higher cash compensation over equity",
        "Ask whether this role is new headcount or backfill",
        "Request written offer before giving notice at current job"
    ],
    source="Company health analysis"
)
```

**Integration in pipeline:** Add to `reality_check_controller.py` orchestration. Call `get_company_intelligence()` once, pass result to detector.

---

### Integration Point 3: Company Analysis Page

**File:** `frontend/company-analysis.html` (new file)

**URL:** `/company-analysis.html` (accessed from overview.html card and Market Context grid link)

**Data flow:**

1. Page loads, reads `analysisData` from sessionStorage
2. Extracts company name from `data._company_name` or `data.company_name`
3. If company intel not in sessionStorage, calls API endpoint
4. Renders full company health snapshot

**API endpoint:** `GET /api/company-intel?company={name}`

Returns `CompanyIntelligence` JSON.

**Caching:** 24-hour backend cache. Don't re-fetch on page refresh. This controls API costs as beta grows.

**Page structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Strategy Overview                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  COMPANY ANALYSIS                                           │
│  {Company Name}                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HEALTH SIGNAL: 🟡 WATCH                            │   │
│  │  Confidence: High (3 verified sources)              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  KEY FINDINGS                                               │
│  ─────────────────────────────────────────────────────────  │
│  • Laid off 18% of workforce (Oct 2024) — Layoffs.fyi      │
│  • Stock down 34% YTD — Yahoo Finance                       │
│  • Last funding: Series C, Apr 2023 — Crunchbase           │
│                                                             │
│  WHAT THIS MEANS                                            │
│  ─────────────────────────────────────────────────────────  │
│  Company is in contraction mode. This role may be backfill  │
│  or could be cut in the next reduction. Proceed with clear  │
│  eyes and protect yourself in negotiation.                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  QUESTIONS TO ASK IN INTERVIEWS                             │
│  ─────────────────────────────────────────────────────────  │
│  • "How has the team structure evolved over the past year?" │
│  • "What's the runway, and how is leadership thinking       │
│     about growth vs. efficiency?"                           │
│  • "Is this a new headcount or backfill?"                   │
│  • "What's the plan for the next 12-18 months?"             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  IF YOU GET AN OFFER                                        │
│  ─────────────────────────────────────────────────────────  │
│  • Push for more cash, less equity — equity may be diluted  │
│    or worthless if company continues to struggle            │
│  • Ask about retention packages and cliff timelines         │
│  • Get the offer in writing before giving notice            │
│  • Consider asking for sign-on bonus as hedge               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  DO YOUR OWN RESEARCH                                       │
│  ─────────────────────────────────────────────────────────  │
│  TikTok: Search #{company}layoffs, #techLayoffs             │
│  Blind: Search {company} for unfiltered employee intel      │
│  Glassdoor: Check review trends (trajectory, not outliers)  │
│  LinkedIn: Look for "Open to Work" spikes from employees    │
│                                                             │
│  [Pre-built search links where possible]                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Data last updated: Jan 3, 2025                             │
│  Sources checked: Web search, news aggregators              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**GREEN company interview questions (different focus):**

For healthy companies, still generate interview questions but focus on growth, not risk:

- "What does the growth roadmap look like for this team over the next 12 months?"
- "How is the company thinking about scaling while maintaining culture?"
- "What's the biggest challenge the team is facing right now?"
- "How does this role contribute to the company's strategic priorities?"

---

### Integration Point 4: Overview Page Card Swap

**File:** `frontend/overview.html`

**Change:** Replace Pipeline Command Center card (lines 383-397) with Company Analysis card.

**New card:**

```html
<!-- Card 5: Company Analysis -->
<a href="company-analysis.html" class="nav-card">
    <span class="beta-badge">Beta</span>
    <span class="card-icon">🏢</span>
    <h2 class="card-title">Company Analysis</h2>
    <p class="card-subtitle">Health signals, risk factors, and what to ask</p>
    <p class="card-insight" id="companyInsight"></p>
    <p class="card-description">
        Understand what you're walking into. Recent layoffs, financial health,
        leadership changes, and employee sentiment — so you know whether this
        opportunity is worth your time.
    </p>
    <div class="card-cta">
        View Analysis <span>→</span>
    </div>
</a>
```

**Insight teaser logic** (add to `generateTeaserInsights()`):

```javascript
// Company Analysis Insight
const companyEl = document.getElementById('companyInsight');
const companyIntel = data.company_intelligence || {};
const companyName = data._company_name || data.company_name || 'this company';

if (companyIntel.company_health_signal === 'RED') {
    companyEl.innerHTML = `<span class="insight-highlight">⚠️ Risk signals detected.</span> See what this means for your candidacy.`;
    companyEl.classList.add('visible');
} else if (companyIntel.company_health_signal === 'YELLOW') {
    const topFinding = companyIntel.findings?.[0]?.finding || 'Review before proceeding.';
    companyEl.innerHTML = `<span class="insight-highlight">🟡 Watch signals found.</span> ${topFinding}`;
    companyEl.classList.add('visible');
} else if (companyIntel.company_health_signal === 'GREEN') {
    companyEl.innerHTML = `<span class="insight-highlight">✓ ${companyName} appears stable.</span> See interview questions and negotiation guidance.`;
    companyEl.classList.add('visible');
} else {
    companyEl.innerHTML = `<span class="insight-highlight">Research ${companyName}</span> before investing time in interviews.`;
    companyEl.classList.add('visible');
}
```

**Pipeline Command Center:** Remains accessible via nav/Command Center. Not deleted, just demoted from the strategic overview.

---

## Implementation Sequence

### Week 1: Data Layer + Reality Check + Market Context Integration

**Day 1-2:**

- [ ] Create `backend/services/company_intel.py`
- [ ] Implement `get_company_intelligence()` with Claude web search
- [ ] Define data classes (`CompanyIntelligence`, `CompanyFinding`, enums)
- [ ] Write prompt template for Claude synthesis (include instruction to ignore opinion blogs/Medium)
- [ ] Implement 24-hour backend caching

**Day 3-4:**

- [ ] Add `detect_company_health_signals()` to `signal_detectors.py`
- [ ] Integrate into `reality_check_controller.py` pipeline
- [ ] Add company intel fetch to main analysis flow (call once, pass to detector)
- [ ] Update Market Context grid in results.html (add fourth "Company" item)
- [ ] Wire grid item to display health signal with appropriate styling

**Day 5:**

- [ ] Test with known companies (Grindr, Meta, Stripe — mix of health states)
- [ ] Validate signal quality and synthesis accuracy
- [ ] Ship to beta users (Jordan, Adam, Darnel)

### Week 2: Standalone Page + Overview Update

**Day 1-2:**

- [ ] Create `frontend/company-analysis.html` with full layout
- [ ] Style consistent with existing HenryHQ pages
- [ ] Add loading state and error handling
- [ ] Implement interview questions for all signal types (including GREEN)

**Day 3:**

- [ ] Create API endpoint `GET /api/company-intel`
- [ ] Wire frontend to fetch data if not in sessionStorage
- [ ] Add company intel to main analysis response (so it's cached)

**Day 4:**

- [ ] Update `overview.html`: swap Pipeline card for Company Analysis card
- [ ] Add insight teaser logic
- [ ] Verify Pipeline Command Center still accessible via nav

**Day 5:**

- [ ] End-to-end testing
- [ ] Beta user feedback
- [ ] Ship

---

## Success Metrics

**Functional:**

- Company intel fetches complete in <5 seconds
- Health signal accuracy >80% (validated against known company states)
- Zero false RED signals on healthy companies
- Interview questions generated for all signal types (GREEN, YELLOW, RED)

**User value:**

- Beta users report the signal changed their approach (asked different questions, negotiated differently)
- At least one beta user passes on a role or negotiates harder based on company intel

**Technical:**

- No impact on existing analysis flow latency (company intel fetched in parallel)
- Graceful degradation if web search fails (show "Unable to fetch company data" not error)
- 24-hour cache reduces API costs by >80% for repeat company lookups

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Claude web search returns garbage | Validate with known companies before shipping. Add confidence score. Show "Low confidence" when data is sparse. Explicitly exclude opinion blogs and Medium posts. |
| Stale data misleads candidate | Show "Data last updated" timestamp. Add "Do your own research" section with manual search prompts. 24-hour cache refresh. |
| Legal/defamation concerns | Only surface verifiable facts with sources. Frame as "what this means for you as a candidate" not company judgment. Never editorialize beyond candidate impact. |
| Feature creep delays launch | Strict scope: v1 is web search synthesis only. Tier 2/3 data sources are post-launch. |
| API costs spike | 24-hour backend cache (not session-only). Don't re-fetch on page refresh. |
| GREEN companies feel broken | Always generate interview questions, even for healthy companies. Different focus (growth vs. risk) but section is never empty. |

---

## Guardrails

**Legal and brand shield:**

- Keep the "What this means for you" framing
- Never drift into company judgment
- Only surface verifiable facts with sources
- This is decision intelligence, not gossip

**Candidate agency:**

- Company health signals use `INFORMATIONAL` or `COACHING` severity only
- Never `BLOCKER` or `WARNING`
- Signals inform, they don't override candidate choice
- Always provide strategic alternatives, not commands

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Where does company health appear on results page? | Market Context grid as fourth item (Demand, Salary, Action, Company) |
| Caching strategy? | 24-hour backend cache in v1 |
| What about GREEN companies? | Still generate interview questions (growth-focused, not risk-focused) |
| Variable naming? | Use `company_health_signal` not `stability_signal` |
| Source quality? | Explicitly instruct Claude to ignore opinion blogs and Medium posts unless corroborated |

---

## Appendix: Sample Outputs

**Example 1: High-risk company (RED)**

```
HEALTH SIGNAL: 🔴 RISK
Confidence: High

KEY FINDINGS:
• Laid off 25% of workforce (Nov 2024) — TechCrunch
• Stock down 52% YTD — Yahoo Finance
• CEO resigned, interim leadership in place — Bloomberg
• Missed Q3 revenue targets by 18% — Earnings call

WHAT THIS MEANS:
This company is in significant distress. The role you're applying for 
may be eliminated in the next reduction. If you proceed, treat any 
equity compensation as worthless and negotiate accordingly.

QUESTIONS TO ASK:
• "What's the plan for stabilizing the business over the next 12 months?"
• "How has this team been affected by recent organizational changes?"
• "Is this role new headcount or backfill?"
• "What does success look like in this role given current priorities?"

IF YOU GET AN OFFER:
• Push for maximum cash, minimal equity
• Ask for sign-on bonus as hedge against instability
• Get written offer before giving notice
• Negotiate shorter cliff on any equity
```

**Example 2: Watch signals (YELLOW)**

```
HEALTH SIGNAL: 🟡 WATCH
Confidence: Medium

KEY FINDINGS:
• Laid off 12% of workforce (Aug 2024) — Layoffs.fyi
• Last funding round was 18 months ago — Crunchbase
• Glassdoor rating dropped from 4.2 to 3.6 in past year

WHAT THIS MEANS:
Company is tightening but not in crisis. Ask about team stability 
and growth plans. Equity is still potentially valuable but negotiate 
for a balanced cash/equity mix.

QUESTIONS TO ASK:
• "How has the team structure evolved over the past year?"
• "What's the runway, and how is leadership thinking about growth vs. efficiency?"
• "Is this a new headcount or backfill?"
• "What's the biggest challenge the team is facing right now?"

IF YOU GET AN OFFER:
• Negotiate for balanced cash/equity mix
• Ask about retention packages
• Clarify reporting structure and team stability
```

**Example 3: Healthy company (GREEN)**

```
HEALTH SIGNAL: 🟢 STABLE
Confidence: High

KEY FINDINGS:
• No layoffs reported in past 12 months
• Stock up 23% YTD — Yahoo Finance
• Raised Series D ($150M) in Sep 2024 — TechCrunch
• Glassdoor rating steady at 4.1

WHAT THIS MEANS:
Company appears financially healthy and growing. Standard interview 
and negotiation approach applies. Equity compensation likely has 
real upside potential.

QUESTIONS TO ASK:
• "What does the growth roadmap look like for this team over the next 12 months?"
• "How is the company thinking about scaling while maintaining culture?"
• "What's the biggest challenge the team is facing right now?"
• "How does this role contribute to the company's strategic priorities?"

IF YOU GET AN OFFER:
• Standard negotiation approach applies
• Equity likely has real upside — factor into total comp evaluation
• Ask about promotion velocity and career growth paths
```

---

**End of implementation brief.**
