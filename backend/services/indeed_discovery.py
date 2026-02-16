"""
Indeed Discovery Service
Fetches job listings from Indeed via the Indeed MCP search_jobs endpoint.
Normalizes results to the same format as JSearch for unified scoring.
"""

import re
import time
import hashlib
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger("henryhq.indeed_discovery")

# Cache TTL: 12 hours (same as JSearch)
CACHE_TTL_SECONDS = 43200


class IndeedDiscoveryService:
    """Fetches and caches job listings from Indeed API (via MCP search_jobs endpoint)."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # {cache_key: (timestamp, results)}

    def search_jobs(
        self,
        query: str,
        location: str = "",
        country_code: str = "US",
        job_type: str = None,
    ) -> Dict[str, Any]:
        """
        Search for jobs via Indeed search_jobs MCP endpoint.

        This calls the local MCP-based Indeed tool. In production,
        this would be an HTTP call to the Indeed API wrapper.

        Returns normalized results matching JSearch format.
        """
        cache_key = self._get_cache_key({
            "query": query,
            "location": location,
            "country_code": country_code,
            "job_type": job_type or "",
        })

        cached = self._get_cached(cache_key)
        if cached:
            logger.info(f"Indeed cache hit for key {cache_key[:8]}")
            cached["cached"] = True
            return cached

        try:
            # Call Indeed API via the available endpoint
            # The Indeed integration uses a wrapper that returns markdown-formatted results
            logger.info(f"Searching Indeed: query='{query}', location='{location}'")

            from backend.services.indeed_api_client import search_indeed_jobs
            raw_results = search_indeed_jobs(
                query=query,
                location=location,
                country_code=country_code,
                job_type=job_type,
            )

            jobs = self._normalize_results(raw_results)

            result = {
                "jobs": jobs,
                "total_found": len(jobs),
                "search_query": query,
                "cached": False,
                "cache_expires_at": time.time() + CACHE_TTL_SECONDS,
                "source": "indeed",
            }

            self._set_cache(cache_key, result)
            return result

        except ImportError:
            logger.warning("Indeed API client not available — skipping Indeed source")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": query,
                "cached": False,
                "source": "indeed",
                "error": "Indeed integration not configured.",
            }
        except Exception as e:
            logger.error(f"Indeed search error: {e}")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": query,
                "cached": False,
                "source": "indeed",
                "error": f"Indeed search failed: {str(e)}",
            }

    def _normalize_results(self, raw_results: List[Dict]) -> List[Dict[str, Any]]:
        """
        Normalize Indeed API response to match JSearch standard format.

        Indeed results come as dicts with keys like:
        - job_id, title, company, location, posted_date, job_type,
          compensation, view_job_url, description
        """
        jobs = []
        for item in raw_results:
            salary_min, salary_max, salary_period = self._parse_salary(
                item.get("compensation") or item.get("salary") or ""
            )

            location_str = item.get("location", "")
            is_remote = bool(
                re.search(r"remote", location_str, re.IGNORECASE)
                or re.search(r"remote", item.get("title", ""), re.IGNORECASE)
            )

            description = item.get("description") or item.get("description_snippet") or ""
            # Strip HTML if present
            description_clean = re.sub(r"<[^>]+>", "", description)

            job = {
                "job_id": item.get("job_id") or item.get("id") or "",
                "title": item.get("title", "Untitled"),
                "company": item.get("company") or item.get("employer_name") or "Unknown",
                "company_logo": item.get("company_logo") or item.get("employer_logo"),
                "location": location_str or "Location not specified",
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "USD",
                "salary_period": salary_period,
                "posted_date": item.get("posted_date"),
                "days_since_posted": self._calc_days_since_str(item.get("posted_date")),
                "apply_url": item.get("view_job_url") or item.get("apply_url") or "",
                "description_snippet": description_clean[:500] if description_clean else "",
                "employment_type": self._map_job_type(item.get("job_type")),
                "is_remote": is_remote,
                "publisher": "Indeed",
                "source": "indeed",
                "network_connection": False,
                "network_connection_count": 0,
                # Indeed often provides richer descriptions
                "job_highlights": {},
                "job_required_skills": [],
                "job_required_experience": {},
            }
            jobs.append(job)

        return jobs[:15]  # Max 15 results

    def _parse_salary(self, salary_str: str) -> tuple:
        """
        Parse salary string like "$150,000 - $180,000 a year" or "$45 - $55 an hour".

        Returns (salary_min, salary_max, period).
        """
        if not salary_str:
            return None, None, None

        salary_str = str(salary_str)

        # Determine period
        period = None
        if "year" in salary_str.lower() or "annual" in salary_str.lower():
            period = "YEAR"
        elif "hour" in salary_str.lower():
            period = "HOUR"
        elif "month" in salary_str.lower():
            period = "MONTH"

        # Extract numbers
        numbers = re.findall(r"[\$]?([\d,]+(?:\.\d+)?)", salary_str)
        parsed = []
        for n in numbers:
            try:
                val = float(n.replace(",", ""))
                parsed.append(val)
            except ValueError:
                continue

        if not parsed:
            return None, None, period

        # If hourly, convert to annual (2080 hours/year)
        if period == "HOUR":
            parsed = [p * 2080 for p in parsed]
            period = "YEAR"
        elif period == "MONTH":
            parsed = [p * 12 for p in parsed]
            period = "YEAR"

        salary_min = parsed[0] if len(parsed) >= 1 else None
        salary_max = parsed[1] if len(parsed) >= 2 else parsed[0]

        return salary_min, salary_max, period

    def _map_job_type(self, job_type: str) -> str:
        """Map Indeed job types to standard format."""
        if not job_type:
            return "FULLTIME"

        jt = job_type.lower()
        if "full" in jt:
            return "FULLTIME"
        elif "part" in jt:
            return "PARTTIME"
        elif "contract" in jt or "temp" in jt:
            return "CONTRACT"
        elif "intern" in jt:
            return "INTERN"
        return "FULLTIME"

    def _calc_days_since_str(self, date_str: str) -> Optional[int]:
        """Calculate days since a date string (various formats)."""
        if not date_str:
            return None
        try:
            # Try common formats
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_str.split(".")[0].split("Z")[0], fmt)
                    delta = datetime.now() - dt
                    return max(0, delta.days)
                except ValueError:
                    continue

            # Try relative strings like "3 days ago", "Just posted"
            if "just" in date_str.lower() or "today" in date_str.lower():
                return 0
            match = re.search(r"(\d+)\s*day", date_str.lower())
            if match:
                return int(match.group(1))
            return None
        except Exception:
            return None

    def _get_cache_key(self, params: Dict[str, Any]) -> str:
        """Generate a deterministic cache key from search params."""
        param_str = str(sorted(params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Return cached results if valid, None otherwise."""
        if cache_key in self._cache:
            timestamp, results = self._cache[cache_key]
            if time.time() - timestamp < CACHE_TTL_SECONDS:
                return results
            else:
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, results: Dict):
        """Store results in cache."""
        self._cache[cache_key] = (time.time(), results)


def merge_and_deduplicate(
    jsearch_jobs: List[Dict],
    indeed_jobs: List[Dict],
    max_total: int = 20,
) -> List[Dict]:
    """
    Merge jobs from JSearch and Indeed, deduplicating by (company, title).

    When duplicates exist, prefer the version with more data (longer description).
    """
    seen = {}  # key: (company_lower, title_lower) -> job dict

    # JSearch first (existing source)
    for job in jsearch_jobs:
        key = (job["company"].lower().strip(), job["title"].lower().strip())
        job.setdefault("source", "jsearch")
        seen[key] = job

    # Indeed second — prefer Indeed if it has richer description
    for job in indeed_jobs:
        key = (job["company"].lower().strip(), job["title"].lower().strip())
        job.setdefault("source", "indeed")
        if key in seen:
            existing = seen[key]
            # Prefer the version with more description data
            existing_desc_len = len(existing.get("description_snippet", ""))
            indeed_desc_len = len(job.get("description_snippet", ""))
            if indeed_desc_len > existing_desc_len * 1.5:
                seen[key] = job
        else:
            seen[key] = job

    merged = list(seen.values())
    return merged[:max_total]


# Singleton instance
indeed_discovery_service = IndeedDiscoveryService()
