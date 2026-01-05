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
