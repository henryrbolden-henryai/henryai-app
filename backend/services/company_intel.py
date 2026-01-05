"""
Company Intelligence Service

Fetches and synthesizes company health data using Claude web search.
Used by Reality Check, Market Context grid, and the standalone Company Analysis page.

Per company-intelligence-implementation-brief.md:
- Returns structured CompanyIntelligence with health signal, findings, and guidance
- Uses Claude web search for real-time company data
- 24-hour backend caching to control API costs
- Graceful degradation if web search fails
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import anthropic
from fastapi import HTTPException

logger = logging.getLogger("henryhq.company_intel")

# In-memory cache for company intelligence (24-hour TTL)
_company_intel_cache: Dict[str, tuple] = {}  # {cache_key: (CompanyIntelligence, expiry_datetime)}
CACHE_TTL_HOURS = 24


class HealthSignal(str, Enum):
    """Company health signal levels."""
    GREEN = "GREEN"     # Stable: No negative signals, or only minor concerns (requires MEDIUM+ confidence)
    YELLOW = "YELLOW"   # Watch: Medium-severity signals (layoffs <15%, stock down 15-30%)
    RED = "RED"         # Risk: High-severity signals (layoffs >15%, stock down >30%, leadership exodus)
    UNKNOWN = "UNKNOWN" # Insufficient data: LOW confidence, cannot make assessment


class ConfidenceLevel(str, Enum):
    """Confidence in the health assessment."""
    HIGH = "HIGH"     # 3+ verified sources
    MEDIUM = "MEDIUM" # 1-2 verified sources
    LOW = "LOW"       # Sparse or conflicting data


class FindingSeverity(str, Enum):
    """Severity of individual findings."""
    HIGH = "HIGH"     # Layoffs >15%, stock down >30%, CEO departure, failed funding
    MEDIUM = "MEDIUM" # Layoffs 5-15%, stock down 15-30%, C-suite turnover, flat funding
    LOW = "LOW"       # Layoffs <5%, stock down <15%, VP-level departures, successful funding


@dataclass
class CompanyFinding:
    """A single verified finding about the company."""
    finding: str                    # "Laid off 18% of workforce"
    source: str                     # "Layoffs.fyi" or "TechCrunch"
    date: Optional[str] = None      # "Oct 2024"
    severity: FindingSeverity = FindingSeverity.LOW
    url: Optional[str] = None       # Link to source


@dataclass
class CompanyIntelligence:
    """Complete company intelligence result."""
    company_name: str
    company_health_signal: HealthSignal
    confidence: ConfidenceLevel
    findings: List[CompanyFinding] = field(default_factory=list)
    what_this_means: str = ""                    # Plain-language synthesis
    interview_questions: List[str] = field(default_factory=list)
    negotiation_guidance: List[str] = field(default_factory=list)
    data_freshness: Optional[datetime] = None   # When data was fetched
    sources_checked: List[str] = field(default_factory=list)
    error: Optional[str] = None                 # If fetch failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "company_name": self.company_name,
            "company_health_signal": self.company_health_signal.value,
            "confidence": self.confidence.value,
            "findings": [
                {
                    "finding": f.finding,
                    "source": f.source,
                    "date": f.date,
                    "severity": f.severity.value,
                    "url": f.url,
                }
                for f in self.findings
            ],
            "what_this_means": self.what_this_means,
            "interview_questions": self.interview_questions,
            "negotiation_guidance": self.negotiation_guidance,
            "data_freshness": self.data_freshness.isoformat() if self.data_freshness else None,
            "sources_checked": self.sources_checked,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyIntelligence':
        """Create from dictionary."""
        findings = [
            CompanyFinding(
                finding=f["finding"],
                source=f["source"],
                date=f.get("date"),
                severity=FindingSeverity(f.get("severity", "LOW")),
                url=f.get("url"),
            )
            for f in data.get("findings", [])
        ]

        return cls(
            company_name=data["company_name"],
            company_health_signal=HealthSignal(data["company_health_signal"]),
            confidence=ConfidenceLevel(data["confidence"]),
            findings=findings,
            what_this_means=data.get("what_this_means", ""),
            interview_questions=data.get("interview_questions", []),
            negotiation_guidance=data.get("negotiation_guidance", []),
            data_freshness=datetime.fromisoformat(data["data_freshness"]) if data.get("data_freshness") else None,
            sources_checked=data.get("sources_checked", []),
            error=data.get("error"),
        )


def _get_cache_key(company_name: str) -> str:
    """Generate a cache key for a company name."""
    normalized = company_name.lower().strip()
    return hashlib.md5(normalized.encode()).hexdigest()


def _get_cached_intel(company_name: str) -> Optional[CompanyIntelligence]:
    """Get cached company intelligence if not expired."""
    cache_key = _get_cache_key(company_name)

    if cache_key in _company_intel_cache:
        intel, expiry = _company_intel_cache[cache_key]
        if datetime.now() < expiry:
            logger.info(f"Cache hit for company: {company_name}")
            return intel
        else:
            # Expired, remove from cache
            del _company_intel_cache[cache_key]
            logger.info(f"Cache expired for company: {company_name}")

    return None


def _cache_intel(company_name: str, intel: CompanyIntelligence):
    """Cache company intelligence with TTL."""
    cache_key = _get_cache_key(company_name)
    expiry = datetime.now() + timedelta(hours=CACHE_TTL_HOURS)
    _company_intel_cache[cache_key] = (intel, expiry)
    logger.info(f"Cached company intel for: {company_name}, expires: {expiry}")


# System prompt for company intelligence research
COMPANY_INTEL_SYSTEM_PROMPT = """You are a company research analyst helping job candidates understand what they're walking into. Your job is to find verified, factual information about a company's health and stability.

CRITICAL RULES:
1. Only include findings you can verify from search results
2. Do not speculate or make assumptions
3. Ignore opinion blogs, Medium posts, and unverified sources unless corroborated by primary sources (company announcements, SEC filings, major news outlets like Bloomberg, TechCrunch, WSJ, Reuters)
4. If you find no negative signals, say so clearly
5. Always provide interview questions, even for healthy companies
6. Use proper grammar and punctuation. Do not use em dashes.

For each finding, assess severity:
- HIGH: Layoffs >15%, stock down >30%, CEO departure, failed funding round, major lawsuit
- MEDIUM: Layoffs 5-15%, stock down 15-30%, C-suite turnover (not CEO), flat funding
- LOW: Layoffs <5%, stock down <15%, VP-level departures, successful funding

Based on findings, determine overall health signal:
- GREEN: No negative signals found, or only LOW severity concerns. Company appears stable.
- YELLOW: One or more MEDIUM severity signals. Warrants attention but not alarming.
- RED: One or more HIGH severity signals. Significant risk factors present.

You must respond with valid JSON matching this exact structure:
{
    "company_health_signal": "GREEN" | "YELLOW" | "RED",
    "confidence": "HIGH" | "MEDIUM" | "LOW",
    "findings": [
        {
            "finding": "Brief factual statement",
            "source": "Source name (e.g., TechCrunch, Bloomberg)",
            "date": "Month Year or null",
            "severity": "HIGH" | "MEDIUM" | "LOW",
            "url": "URL if available or null"
        }
    ],
    "what_this_means": "2-3 sentences explaining what this means for a job candidate. Be direct and actionable.",
    "interview_questions": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4"
    ],
    "negotiation_guidance": [
        "Guidance point 1",
        "Guidance point 2",
        "Guidance point 3"
    ],
    "sources_checked": ["List of sources you searched"]
}

For GREEN companies, focus interview questions on growth and opportunity:
- "What does the growth roadmap look like for this team over the next 12 months?"
- "How is the company thinking about scaling while maintaining culture?"

For YELLOW/RED companies, focus on stability and protection:
- "How has the team structure evolved over the past year?"
- "What is the runway, and how is leadership thinking about growth versus efficiency?"
- "Is this a new headcount or backfill?"

IMPORTANT: Always populate interview_questions and negotiation_guidance, even for GREEN companies."""


def get_company_intelligence(
    company_name: str,
    ticker_symbol: Optional[str] = None,
    company_url: Optional[str] = None,
    bypass_cache: bool = False,
) -> CompanyIntelligence:
    """
    Fetch and synthesize company health data.

    Args:
        company_name: Name of the company to research
        ticker_symbol: Optional stock ticker for public companies
        company_url: Optional company website or LinkedIn URL for context
        bypass_cache: If True, skip cache and fetch fresh data

    Returns:
        CompanyIntelligence with health signal, findings, and guidance
    """
    # Check cache first (unless bypassing)
    if not bypass_cache:
        cached = _get_cached_intel(company_name)
        if cached:
            return cached

    # Get Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set")
        return _create_error_intel(company_name, "API configuration error. Unable to fetch company data.")

    client = anthropic.Anthropic(api_key=api_key, timeout=60.0)

    # Build the research query - explicit search instructions
    # Use current year in searches for freshness
    current_year = datetime.now().year
    last_year = current_year - 1

    user_message = f"""Research "{company_name}" and provide a health assessment for a job candidate considering employment there.

Company: {company_name}
{f"Stock Ticker: {ticker_symbol}" if ticker_symbol else ""}
{f"Company URL: {company_url}" if company_url else ""}

YOU MUST PERFORM MULTIPLE SEARCHES. Search for each of these queries separately:

1. FIRST SEARCH: "{company_name} layoffs {current_year}"
2. SECOND SEARCH: "{company_name} layoffs {last_year}"
3. THIRD SEARCH: "{company_name} acquisition buyout going private {current_year}"
4. FOURTH SEARCH: "{company_name} lawsuit investigation SEC {current_year}"
5. FIFTH SEARCH: "{company_name} CEO leadership changes {current_year}"
6. SIXTH SEARCH: "{company_name} stock price funding valuation {current_year}"
7. SEVENTH SEARCH: "{company_name} news" (for recent press coverage)

IMPORTANT SEARCH GUIDANCE:
- If you find any lawsuits, investigations, or SEC filings, dig deeper with a follow-up search
- Look specifically at sources like: PR Newswire, Bloomberg, TechCrunch, Reuters, WSJ, Business Insider, The Verge, Layoffs.fyi
- For app companies, also check: The Verge, Engadget, 9to5Mac/Google
- Include the FULL company name and common variations in your searches

CLASSIFICATION GUIDANCE:
- Pending acquisition/buyout/going-private deals: YELLOW (uncertainty for employees)
- Terminated/failed acquisitions: YELLOW (instability signal)
- Active lawsuits against the company or leadership: YELLOW or RED based on severity
- SEC investigations or fiduciary duty lawsuits: RED
- Layoffs announced in past 6 months: Check percentage to determine severity

After completing your searches, provide your findings as structured JSON matching the schema in your system prompt."""

    try:
        logger.info(f"Fetching company intelligence for: {company_name}")
        print(f"🔍 Fetching company intelligence for: {company_name}")

        # Call Claude with web search tool
        # Web search is a "server tool" - Anthropic's API executes searches automatically
        # and injects results into the response. No tool_use loop needed.
        messages = [{"role": "user", "content": user_message}]

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,  # Increased for detailed responses with citations
            temperature=0,
            system=COMPANY_INTEL_SYSTEM_PROMPT,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 15,  # Increased for more thorough research
                }
            ],
            messages=messages
        )

        # Handle pause_turn stop reason - API paused a long-running turn
        # Continue the conversation to let Claude finish
        while response.stop_reason == "pause_turn":
            logger.info(f"Received pause_turn, continuing search for: {company_name}")
            print(f"🔄 Continuing company intel search for: {company_name}")

            # Add assistant's partial response to continue
            messages.append({"role": "assistant", "content": response.content})

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0,
                system=COMPANY_INTEL_SYSTEM_PROMPT,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 15,
                    }
                ],
                messages=messages
            )

        # Log web search usage for monitoring
        if hasattr(response, 'usage') and response.usage:
            server_tool_use = getattr(response.usage, 'server_tool_use', None)
            if server_tool_use:
                web_searches = getattr(server_tool_use, 'web_search_requests', 0)
                logger.info(f"Web searches performed for {company_name}: {web_searches}")
                print(f"🔍 Web searches performed: {web_searches}")

        # Extract final text response - combine all text blocks
        result_text = None
        text_parts = []
        for block in response.content:
            if hasattr(block, 'text'):
                text_parts.append(block.text)

        if text_parts:
            result_text = ''.join(text_parts)

        if not result_text:
            logger.warning(f"No text response from Claude for company: {company_name}")
            return _create_error_intel(company_name, "Unable to retrieve company data. Please try again.")

        # Parse the JSON response
        intel = _parse_intel_response(company_name, result_text)

        # Cache the result
        _cache_intel(company_name, intel)

        print(f"✅ Company intelligence retrieved: {company_name} - {intel.company_health_signal.value}")
        return intel

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error for {company_name}: {e}")
        print(f"🔥 Company intel API error: {e}")
        return _create_error_intel(company_name, "Unable to fetch company data at this time.")
    except Exception as e:
        logger.error(f"Error fetching company intelligence for {company_name}: {e}")
        print(f"🔥 Company intel error: {e}")
        import traceback
        traceback.print_exc()
        return _create_error_intel(company_name, "An error occurred while researching this company.")


def _parse_intel_response(company_name: str, response_text: str) -> CompanyIntelligence:
    """Parse Claude's JSON response into CompanyIntelligence."""
    try:
        # Clean the response text (remove markdown code blocks if present)
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)

        # Parse findings
        findings = []
        for f in data.get("findings", []):
            findings.append(CompanyFinding(
                finding=f.get("finding", ""),
                source=f.get("source", "Unknown"),
                date=f.get("date"),
                severity=FindingSeverity(f.get("severity", "LOW")),
                url=f.get("url"),
            ))

        # Determine confidence based on number of findings
        raw_confidence = data.get("confidence", "MEDIUM")
        try:
            confidence = ConfidenceLevel(raw_confidence)
        except ValueError:
            confidence = ConfidenceLevel.MEDIUM

        # Parse health signal
        raw_signal = data.get("company_health_signal", "GREEN")
        try:
            health_signal = HealthSignal(raw_signal)
        except ValueError:
            health_signal = HealthSignal.GREEN

        # CRITICAL RULE: LOW confidence MUST result in UNKNOWN signal
        # We cannot claim STABLE (GREEN) without sufficient data to verify it
        # YELLOW and RED are allowed with LOW confidence (we found something concerning)
        if confidence == ConfidenceLevel.LOW and health_signal == HealthSignal.GREEN:
            health_signal = HealthSignal.UNKNOWN
            # Update the messaging for UNKNOWN state
            what_this_means = data.get("what_this_means", "")
            if not what_this_means or "no significant" in what_this_means.lower():
                what_this_means = "Henry could not find enough verified data to assess this company's health. This does not mean safe or risky. Validate directly before investing significant time in this opportunity."

            interview_questions = data.get("interview_questions", [])
            if not interview_questions:
                interview_questions = [
                    "What does the growth roadmap look like for this team over the next 12 months?",
                    "How has the team structure evolved over the past year?",
                    "What is the company's current runway and funding status?",
                    "Have there been any recent organizational changes I should know about?",
                ]

            negotiation_guidance = data.get("negotiation_guidance", [])
            if not negotiation_guidance:
                negotiation_guidance = [
                    "Research the company independently. Henry does not have enough data to guide you here.",
                    "Ask directly about team stability, runway, and recent organizational changes.",
                    "Verify funding status and leadership stability through your own network.",
                ]

            return CompanyIntelligence(
                company_name=company_name,
                company_health_signal=health_signal,
                confidence=confidence,
                findings=findings,
                what_this_means=what_this_means,
                interview_questions=interview_questions,
                negotiation_guidance=negotiation_guidance,
                data_freshness=datetime.now(),
                sources_checked=data.get("sources_checked", []),
            )

        return CompanyIntelligence(
            company_name=company_name,
            company_health_signal=health_signal,
            confidence=confidence,
            findings=findings,
            what_this_means=data.get("what_this_means", ""),
            interview_questions=data.get("interview_questions", []),
            negotiation_guidance=data.get("negotiation_guidance", []),
            data_freshness=datetime.now(),
            sources_checked=data.get("sources_checked", []),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse company intel JSON: {e}")
        logger.error(f"Response text: {response_text[:500]}")
        return _create_error_intel(company_name, "Unable to process company data.")


def _create_error_intel(company_name: str, error_message: str) -> CompanyIntelligence:
    """Create a CompanyIntelligence object for error/unknown cases.

    CRITICAL: When confidence is LOW, health_signal MUST be UNKNOWN.
    We cannot claim STABLE (GREEN) without sufficient data to verify it.
    """
    return CompanyIntelligence(
        company_name=company_name,
        company_health_signal=HealthSignal.UNKNOWN,  # UNKNOWN when we can't verify - never falsely claim stable
        confidence=ConfidenceLevel.LOW,
        findings=[],
        what_this_means="Henry could not find enough verified data to assess this company's health. This does not mean safe or risky. Validate directly before investing significant time in this opportunity.",
        interview_questions=[
            "What does the growth roadmap look like for this team over the next 12 months?",
            "How has the team structure evolved over the past year?",
            "What is the company's current runway and funding status?",
            "Have there been any recent organizational changes I should know about?",
        ],
        negotiation_guidance=[
            "Research the company independently. Henry does not have enough data to guide you here.",
            "Ask directly about team stability, runway, and recent organizational changes.",
            "Verify funding status and leadership stability through your own network.",
        ],
        data_freshness=datetime.now(),
        sources_checked=[],
        error=error_message,
    )


def clear_company_intel_cache():
    """Clear all cached company intelligence. Useful for testing."""
    global _company_intel_cache
    _company_intel_cache = {}
    logger.info("Company intelligence cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring."""
    now = datetime.now()
    active_entries = sum(1 for _, (_, expiry) in _company_intel_cache.items() if now < expiry)
    expired_entries = len(_company_intel_cache) - active_entries

    return {
        "total_entries": len(_company_intel_cache),
        "active_entries": active_entries,
        "expired_entries": expired_entries,
        "cache_ttl_hours": CACHE_TTL_HOURS,
    }


# =============================================================================
# COMPANY SCALE LOOKUP - Lightweight scale detection for experience evaluation
# =============================================================================

# Cache for company scale lookups (separate from full intel cache)
_company_scale_cache: Dict[str, tuple] = {}  # {company_name: (scale_info, expiry_datetime)}
SCALE_CACHE_TTL_HOURS = 168  # 7 days - scale doesn't change often


@dataclass
class CompanyScale:
    """Lightweight company scale information for experience evaluation."""
    company_name: str
    scale: str  # "startup" | "mid" | "enterprise"
    employee_count: Optional[str] = None  # "50-200", "1000-5000", "10000+"
    is_public: bool = False
    funding_stage: Optional[str] = None  # "Series A", "Series D", "Public", etc.
    confidence: str = "medium"  # "high" | "medium" | "low"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "scale": self.scale,
            "employee_count": self.employee_count,
            "is_public": self.is_public,
            "funding_stage": self.funding_stage,
            "confidence": self.confidence,
        }


# Well-known companies with pre-defined scale (no API call needed)
KNOWN_COMPANY_SCALES: Dict[str, CompanyScale] = {
    # FAANG / Big Tech (Enterprise)
    "google": CompanyScale("Google", "enterprise", "100000+", True, "Public", "high"),
    "alphabet": CompanyScale("Alphabet", "enterprise", "100000+", True, "Public", "high"),
    "meta": CompanyScale("Meta", "enterprise", "50000+", True, "Public", "high"),
    "facebook": CompanyScale("Facebook", "enterprise", "50000+", True, "Public", "high"),
    "amazon": CompanyScale("Amazon", "enterprise", "1000000+", True, "Public", "high"),
    "aws": CompanyScale("AWS", "enterprise", "100000+", True, "Public", "high"),
    "apple": CompanyScale("Apple", "enterprise", "100000+", True, "Public", "high"),
    "microsoft": CompanyScale("Microsoft", "enterprise", "200000+", True, "Public", "high"),
    "netflix": CompanyScale("Netflix", "enterprise", "10000+", True, "Public", "high"),
    "nvidia": CompanyScale("NVIDIA", "enterprise", "20000+", True, "Public", "high"),

    # Major Tech Companies (Enterprise)
    "uber": CompanyScale("Uber", "enterprise", "30000+", True, "Public", "high"),
    "lyft": CompanyScale("Lyft", "enterprise", "5000+", True, "Public", "high"),
    "airbnb": CompanyScale("Airbnb", "enterprise", "6000+", True, "Public", "high"),
    "salesforce": CompanyScale("Salesforce", "enterprise", "70000+", True, "Public", "high"),
    "oracle": CompanyScale("Oracle", "enterprise", "140000+", True, "Public", "high"),
    "ibm": CompanyScale("IBM", "enterprise", "280000+", True, "Public", "high"),
    "cisco": CompanyScale("Cisco", "enterprise", "80000+", True, "Public", "high"),
    "intel": CompanyScale("Intel", "enterprise", "120000+", True, "Public", "high"),
    "adobe": CompanyScale("Adobe", "enterprise", "25000+", True, "Public", "high"),

    # Fintech (Enterprise/Mid)
    "stripe": CompanyScale("Stripe", "enterprise", "8000+", False, "Series I", "high"),
    "square": CompanyScale("Square", "enterprise", "10000+", True, "Public", "high"),
    "block": CompanyScale("Block", "enterprise", "10000+", True, "Public", "high"),
    "paypal": CompanyScale("PayPal", "enterprise", "25000+", True, "Public", "high"),
    "venmo": CompanyScale("Venmo", "enterprise", "25000+", True, "Public", "high"),
    "coinbase": CompanyScale("Coinbase", "enterprise", "3000+", True, "Public", "high"),
    "robinhood": CompanyScale("Robinhood", "mid", "2000+", True, "Public", "high"),
    "plaid": CompanyScale("Plaid", "mid", "1000+", False, "Series D", "high"),

    # Social/Consumer (Enterprise)
    "spotify": CompanyScale("Spotify", "enterprise", "10000+", True, "Public", "high"),
    "twitter": CompanyScale("Twitter", "enterprise", "2000+", False, "Private", "high"),
    "x": CompanyScale("X", "enterprise", "2000+", False, "Private", "high"),
    "linkedin": CompanyScale("LinkedIn", "enterprise", "20000+", True, "Public", "high"),
    "snap": CompanyScale("Snap", "enterprise", "5000+", True, "Public", "high"),
    "snapchat": CompanyScale("Snapchat", "enterprise", "5000+", True, "Public", "high"),
    "pinterest": CompanyScale("Pinterest", "enterprise", "3000+", True, "Public", "high"),
    "reddit": CompanyScale("Reddit", "mid", "2000+", True, "Public", "high"),
    "discord": CompanyScale("Discord", "mid", "1000+", False, "Series H", "high"),
    "tiktok": CompanyScale("TikTok", "enterprise", "10000+", False, "Private", "high"),
    "bytedance": CompanyScale("ByteDance", "enterprise", "100000+", False, "Private", "high"),

    # SaaS / B2B (Mid/Enterprise)
    "slack": CompanyScale("Slack", "enterprise", "3000+", True, "Public", "high"),
    "zoom": CompanyScale("Zoom", "enterprise", "8000+", True, "Public", "high"),
    "dropbox": CompanyScale("Dropbox", "enterprise", "3000+", True, "Public", "high"),
    "atlassian": CompanyScale("Atlassian", "enterprise", "10000+", True, "Public", "high"),
    "notion": CompanyScale("Notion", "mid", "500+", False, "Series C", "high"),
    "figma": CompanyScale("Figma", "mid", "1000+", False, "Acquired", "high"),
    "asana": CompanyScale("Asana", "mid", "2000+", True, "Public", "high"),
    "hubspot": CompanyScale("HubSpot", "enterprise", "7000+", True, "Public", "high"),
    "zendesk": CompanyScale("Zendesk", "enterprise", "5000+", False, "Private", "high"),
    "twilio": CompanyScale("Twilio", "enterprise", "8000+", True, "Public", "high"),
    "datadog": CompanyScale("Datadog", "enterprise", "5000+", True, "Public", "high"),
    "snowflake": CompanyScale("Snowflake", "enterprise", "5000+", True, "Public", "high"),
    "databricks": CompanyScale("Databricks", "enterprise", "5000+", False, "Series I", "high"),
    "palantir": CompanyScale("Palantir", "enterprise", "3000+", True, "Public", "high"),
    "splunk": CompanyScale("Splunk", "enterprise", "8000+", False, "Acquired", "high"),
    "servicenow": CompanyScale("ServiceNow", "enterprise", "20000+", True, "Public", "high"),
    "workday": CompanyScale("Workday", "enterprise", "15000+", True, "Public", "high"),
    "shopify": CompanyScale("Shopify", "enterprise", "10000+", True, "Public", "high"),

    # AI Companies (Startup/Mid)
    "openai": CompanyScale("OpenAI", "mid", "1000+", False, "Series E", "high"),
    "anthropic": CompanyScale("Anthropic", "mid", "500+", False, "Series D", "high"),
    "cohere": CompanyScale("Cohere", "startup", "200+", False, "Series D", "high"),
    "scale ai": CompanyScale("Scale AI", "mid", "500+", False, "Series F", "high"),
    "hugging face": CompanyScale("Hugging Face", "mid", "200+", False, "Series D", "high"),

    # Delivery/Logistics (Enterprise)
    "doordash": CompanyScale("DoorDash", "enterprise", "10000+", True, "Public", "high"),
    "instacart": CompanyScale("Instacart", "enterprise", "10000+", True, "Public", "high"),
    "grubhub": CompanyScale("Grubhub", "enterprise", "3000+", False, "Acquired", "high"),

    # Travel (Enterprise)
    "booking": CompanyScale("Booking.com", "enterprise", "20000+", True, "Public", "high"),
    "expedia": CompanyScale("Expedia", "enterprise", "15000+", True, "Public", "high"),

    # Traditional Enterprise / Fortune 500
    "walmart": CompanyScale("Walmart", "enterprise", "2000000+", True, "Public", "high"),
    "target": CompanyScale("Target", "enterprise", "400000+", True, "Public", "high"),
    "jpmorgan": CompanyScale("JPMorgan", "enterprise", "300000+", True, "Public", "high"),
    "jp morgan": CompanyScale("JP Morgan", "enterprise", "300000+", True, "Public", "high"),
    "goldman sachs": CompanyScale("Goldman Sachs", "enterprise", "45000+", True, "Public", "high"),
    "morgan stanley": CompanyScale("Morgan Stanley", "enterprise", "80000+", True, "Public", "high"),
    "bank of america": CompanyScale("Bank of America", "enterprise", "200000+", True, "Public", "high"),
    "citibank": CompanyScale("Citibank", "enterprise", "200000+", True, "Public", "high"),
    "citi": CompanyScale("Citi", "enterprise", "200000+", True, "Public", "high"),
    "wells fargo": CompanyScale("Wells Fargo", "enterprise", "230000+", True, "Public", "high"),
    "capital one": CompanyScale("Capital One", "enterprise", "50000+", True, "Public", "high"),
    "american express": CompanyScale("American Express", "enterprise", "60000+", True, "Public", "high"),
    "visa": CompanyScale("Visa", "enterprise", "25000+", True, "Public", "high"),
    "mastercard": CompanyScale("Mastercard", "enterprise", "30000+", True, "Public", "high"),

    # Consulting
    "mckinsey": CompanyScale("McKinsey", "enterprise", "40000+", False, "Private", "high"),
    "bain": CompanyScale("Bain", "enterprise", "15000+", False, "Private", "high"),
    "bcg": CompanyScale("BCG", "enterprise", "25000+", False, "Private", "high"),
    "boston consulting": CompanyScale("Boston Consulting Group", "enterprise", "25000+", False, "Private", "high"),
    "deloitte": CompanyScale("Deloitte", "enterprise", "400000+", False, "Private", "high"),
    "pwc": CompanyScale("PwC", "enterprise", "300000+", False, "Private", "high"),
    "kpmg": CompanyScale("KPMG", "enterprise", "250000+", False, "Private", "high"),
    "ey": CompanyScale("EY", "enterprise", "350000+", False, "Private", "high"),
    "ernst young": CompanyScale("Ernst & Young", "enterprise", "350000+", False, "Private", "high"),
    "accenture": CompanyScale("Accenture", "enterprise", "700000+", True, "Public", "high"),

    # Executive Search Firms (for recruiting experience)
    "heidrick": CompanyScale("Heidrick & Struggles", "mid", "2000+", True, "Public", "high"),
    "heidrick & struggles": CompanyScale("Heidrick & Struggles", "mid", "2000+", True, "Public", "high"),
    "korn ferry": CompanyScale("Korn Ferry", "enterprise", "8000+", True, "Public", "high"),
    "spencer stuart": CompanyScale("Spencer Stuart", "mid", "1000+", False, "Private", "high"),
    "egon zehnder": CompanyScale("Egon Zehnder", "mid", "500+", False, "Private", "high"),
    "russell reynolds": CompanyScale("Russell Reynolds", "mid", "500+", False, "Private", "high"),

    # Energy / Utilities
    "national grid": CompanyScale("National Grid", "enterprise", "29000+", True, "Public", "high"),

    # Automotive / EV
    "tesla": CompanyScale("Tesla", "enterprise", "120000+", True, "Public", "high"),
    "rivian": CompanyScale("Rivian", "enterprise", "15000+", True, "Public", "high"),
    "lucid": CompanyScale("Lucid", "mid", "7000+", True, "Public", "high"),
    "ford": CompanyScale("Ford", "enterprise", "170000+", True, "Public", "high"),
    "gm": CompanyScale("GM", "enterprise", "160000+", True, "Public", "high"),
    "general motors": CompanyScale("General Motors", "enterprise", "160000+", True, "Public", "high"),
    "waymo": CompanyScale("Waymo", "mid", "2500+", False, "Subsidiary", "high"),
    "cruise": CompanyScale("Cruise", "mid", "2000+", False, "Subsidiary", "high"),

    # Aerospace
    "spacex": CompanyScale("SpaceX", "enterprise", "13000+", False, "Private", "high"),
    "blue origin": CompanyScale("Blue Origin", "mid", "10000+", False, "Private", "high"),
    "boeing": CompanyScale("Boeing", "enterprise", "140000+", True, "Public", "high"),
    "lockheed martin": CompanyScale("Lockheed Martin", "enterprise", "120000+", True, "Public", "high"),

    # Healthcare Tech
    "epic systems": CompanyScale("Epic Systems", "enterprise", "13000+", False, "Private", "high"),
    "cerner": CompanyScale("Cerner", "enterprise", "25000+", False, "Acquired", "high"),

    # Legal Tech (for Harvey context)
    "harvey": CompanyScale("Harvey", "startup", "200+", False, "Series D", "high"),
}


def _normalize_company_name(name: str) -> str:
    """Normalize company name for lookup."""
    normalized = name.lower().strip()
    # Remove common suffixes
    for suffix in [" inc", " inc.", " llc", " ltd", " corp", " corporation", " co", " co."]:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    return normalized


def get_company_scale(company_name: str) -> CompanyScale:
    """
    Get company scale information for experience evaluation.

    This is a lightweight lookup that:
    1. First checks known companies (no API call)
    2. Falls back to heuristic-based detection
    3. Uses cached results when available

    Args:
        company_name: Name of the company

    Returns:
        CompanyScale with scale classification
    """
    if not company_name or not company_name.strip():
        return CompanyScale(
            company_name="Unknown",
            scale="mid",  # Default to mid when unknown
            confidence="low"
        )

    normalized = _normalize_company_name(company_name)

    # Check known companies first (instant, no API call)
    if normalized in KNOWN_COMPANY_SCALES:
        known = KNOWN_COMPANY_SCALES[normalized]
        logger.info(f"Company scale lookup (known): {company_name} -> {known.scale}")
        return known

    # Check cache
    cache_key = hashlib.md5(normalized.encode()).hexdigest()
    if cache_key in _company_scale_cache:
        scale_info, expiry = _company_scale_cache[cache_key]
        if datetime.now() < expiry:
            logger.info(f"Company scale lookup (cached): {company_name} -> {scale_info.scale}")
            return scale_info

    # Heuristic-based detection for unknown companies
    # This avoids expensive API calls for every company
    scale_info = _infer_company_scale_heuristic(company_name)

    # Cache the result
    expiry = datetime.now() + timedelta(hours=SCALE_CACHE_TTL_HOURS)
    _company_scale_cache[cache_key] = (scale_info, expiry)

    logger.info(f"Company scale lookup (heuristic): {company_name} -> {scale_info.scale}")
    return scale_info


def _infer_company_scale_heuristic(company_name: str) -> CompanyScale:
    """
    Infer company scale using heuristics when not in known list.

    This is a best-effort classification that avoids API calls.
    """
    name_lower = company_name.lower()

    # Startup indicators
    startup_signals = [
        "ai", "labs", "studio", "ventures", "stealth",
        "technologies", "tech", "software", "solutions", "digital",
        "health", "bio", "medical", "therapeutics", "genomics"
    ]

    # Enterprise indicators (usually older, established names)
    enterprise_signals = [
        "bank", "financial", "insurance", "capital", "group",
        "international", "global", "national", "american", "united",
        "general", "electric", "motors", "airlines", "telecom"
    ]

    # Check for startup signals
    startup_score = sum(1 for s in startup_signals if s in name_lower)

    # Check for enterprise signals
    enterprise_score = sum(1 for s in enterprise_signals if s in name_lower)

    if enterprise_score > startup_score:
        return CompanyScale(
            company_name=company_name,
            scale="enterprise",
            confidence="low"  # Low confidence for heuristic
        )
    elif startup_score > 0:
        return CompanyScale(
            company_name=company_name,
            scale="startup",
            confidence="low"
        )
    else:
        # Default to mid for unknown companies
        return CompanyScale(
            company_name=company_name,
            scale="mid",
            confidence="low"
        )


def get_candidate_employer_scales(resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get company scale information for all employers in a candidate's resume.

    This function processes the candidate's work history and returns
    scale information for each employer, which can be used in
    credibility/scope evaluation.

    Args:
        resume_data: Parsed resume data with "experience" array

    Returns:
        List of employer scale dictionaries with company name and scale info
    """
    if not resume_data:
        return []

    experience = resume_data.get("experience", [])
    if not experience or not isinstance(experience, list):
        return []

    employer_scales = []
    seen_companies = set()  # Avoid duplicate lookups

    for exp in experience:
        if not isinstance(exp, dict):
            continue

        company = exp.get("company", "")
        if not company or company.lower() in seen_companies:
            continue

        seen_companies.add(company.lower())

        # Get scale info
        scale_info = get_company_scale(company)

        employer_scales.append({
            "company": company,
            "title": exp.get("title", ""),
            "dates": exp.get("dates", ""),
            "scale": scale_info.scale,
            "employee_count": scale_info.employee_count,
            "is_public": scale_info.is_public,
            "funding_stage": scale_info.funding_stage,
            "confidence": scale_info.confidence,
        })

    # Log summary
    scale_summary = {}
    for emp in employer_scales:
        s = emp["scale"]
        scale_summary[s] = scale_summary.get(s, 0) + 1

    print(f"📊 Candidate employer scale analysis: {scale_summary}")
    for emp in employer_scales:
        conf_marker = "✓" if emp["confidence"] == "high" else "?"
        print(f"   {conf_marker} {emp['company']}: {emp['scale'].upper()}")

    return employer_scales
