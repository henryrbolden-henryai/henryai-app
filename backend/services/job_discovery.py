"""
Job Discovery Service
Fetches job listings from external APIs (JSearch/RapidAPI) with caching.
Builds search queries from candidate profile data.
Supports multi-query strategy for better alignment.
"""

import os
import time
import hashlib
import logging
import requests
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger("henryhq.job_discovery")

# Cache TTL: 12 hours (jobs go stale quickly)
CACHE_TTL_SECONDS = 43200

# Function area to readable search term mapping
FUNCTION_AREA_MAP = {
    'product_management': 'Product Manager',
    'engineering': 'Software Engineer',
    'design': 'UX Designer',
    'data_analytics': 'Data Analyst',
    'sales': 'Sales',
    'marketing': 'Marketing Manager',
    'customer_success': 'Customer Success Manager',
    'operations': 'Operations Manager',
    'finance': 'Finance Manager',
    'hr_people': 'HR Manager',
    'legal': 'Legal Counsel',
}


class JobDiscoveryService:
    """Fetches and caches job listings from JSearch API."""

    JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY_JSEARCH") or os.getenv("RAPIDAPI_KEY")
        self._cache: Dict[str, tuple] = {}  # {cache_key: (timestamp, results)}

    @property
    def is_configured(self) -> bool:
        """Check if the API key is configured."""
        return bool(self.api_key)

    def build_search_params(
        self,
        target_roles: List[str] = None,
        function_area: str = None,
        job_search_keywords: List[str] = None,
        city: str = None,
        state: str = None,
        country: str = None,
        work_arrangement: List[str] = None,
        remote_only: bool = False,
        excluded_companies: List[str] = None,
        employment_types: List[str] = None,
        years_experience: int = None,
    ) -> Dict[str, Any]:
        """
        Build JSearch API query parameters from candidate profile data.

        Priority for search query:
        1. target_roles (from resume parsing) - most specific
        2. job_search_keywords (user-provided overrides)
        3. function_area (fallback)
        """
        # Build the query string
        query_parts = []

        if target_roles:
            # Use the first target role as primary query
            query_parts.append(target_roles[0])
        elif function_area:
            query_parts.append(FUNCTION_AREA_MAP.get(function_area, function_area))

        if job_search_keywords:
            query_parts.extend(job_search_keywords[:3])  # Limit to 3 extra keywords

        query = " ".join(query_parts) if query_parts else "jobs"

        # Build location string
        location_parts = []
        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if country and country.lower() != "us" and country.lower() != "united states":
            location_parts.append(country)

        # Determine remote filter
        is_remote = remote_only
        if not is_remote and work_arrangement:
            is_remote = work_arrangement == ["remote"] or (
                len(work_arrangement) == 1 and "remote" in work_arrangement
            )

        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",  # JSearch "week" filter is unreliable
        }

        if location_parts:
            params["query"] = f"{query} in {', '.join(location_parts)}"

        if is_remote:
            params["remote_jobs_only"] = "true"

        # Employment type filter
        if employment_types:
            params["employment_types"] = ",".join(employment_types)

        # Experience level filter
        if years_experience is not None:
            if years_experience < 3:
                params["job_requirements"] = "under_3_years_experience"
            elif years_experience >= 3:
                params["job_requirements"] = "more_than_3_years_experience"

        return params

    @staticmethod
    def _prepend_seniority(role: str, seniority: str) -> str:
        """
        Prepend a seniority prefix to a role title if it doesn't already contain one.

        Examples:
          ("Product Manager", "senior") -> "Senior Product Manager"
          ("Senior Product Manager", "senior") -> "Senior Product Manager"  (unchanged)
          ("Engineering Manager", "director") -> "Director of Engineering Manager"
        """
        if not seniority or not role:
            return role

        # Common seniority indicators already in the title
        SENIORITY_INDICATORS = [
            "senior", "sr.", "sr ", "staff", "principal", "lead",
            "director", "vp", "vice president", "chief", "head of",
            "junior", "jr.", "entry", "intern", "executive", "c-suite",
        ]

        role_lower = role.lower()
        if any(indicator in role_lower for indicator in SENIORITY_INDICATORS):
            return role  # Already has seniority indicator

        PREFIX_MAP = {
            "senior": "Senior",
            "staff": "Staff",
            "director": "Director of",
            "vp": "VP of",
            "executive": "Chief",
            "entry": "Junior",
            "mid": "",  # No prefix for mid-level
        }

        prefix = PREFIX_MAP.get(seniority, "")
        if prefix:
            return f"{prefix} {role}"
        return role

    def build_multi_query_params(
        self,
        target_roles: List[str] = None,
        function_area: str = None,
        target_industry: str = None,
        job_search_keywords: List[str] = None,
        location: str = None,
        remote_only: bool = False,
        employment_types: List[str] = None,
        years_experience: int = None,
        seniority: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Build multiple search query parameter sets for better coverage.

        Returns 2-3 query param dicts that together capture:
        1. Primary role match (most specific, with seniority prefix)
        2. Secondary role variant (if available)
        3. Industry + function broadening query
        """
        queries = []
        base_params = {
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",
        }

        if remote_only:
            base_params["remote_jobs_only"] = "true"

        if employment_types:
            base_params["employment_types"] = ",".join(employment_types)

        if years_experience is not None:
            if years_experience < 3:
                base_params["job_requirements"] = "under_3_years_experience"
            elif years_experience >= 3:
                base_params["job_requirements"] = "more_than_3_years_experience"

        loc_suffix = f" in {location}" if location else ""

        # Query 1: Primary target role with seniority prefix (most specific)
        if target_roles and len(target_roles) > 0:
            primary_role = self._prepend_seniority(target_roles[0], seniority)
            q1 = {**base_params, "query": f"{primary_role}{loc_suffix}"}
            queries.append(q1)

        # Query 2: Secondary target role (if different from primary)
        if target_roles and len(target_roles) > 1:
            q2 = {**base_params, "query": f"{target_roles[1]}{loc_suffix}"}
            queries.append(q2)

        # Query 3: Industry + function broadening query
        if target_industry or function_area:
            industry_term = target_industry or ""
            function_term = FUNCTION_AREA_MAP.get(function_area, "") if function_area else ""
            broad_query = f"{function_term} {industry_term}".strip()
            if broad_query and broad_query != (target_roles[0] if target_roles else ""):
                q3 = {**base_params, "query": f"{broad_query}{loc_suffix}"}
                queries.append(q3)

        # Fallback: If no queries built, use function_area or keywords
        if not queries:
            fallback = function_area or "jobs"
            if function_area:
                fallback = FUNCTION_AREA_MAP.get(function_area, function_area)
            if job_search_keywords:
                fallback = f"{fallback} {' '.join(job_search_keywords[:2])}"
            queries.append({**base_params, "query": f"{fallback}{loc_suffix}"})

        logger.info(f"Built {len(queries)} search queries: {[q['query'] for q in queries]}")
        return queries

    def search_multi_query(
        self,
        query_params_list: List[Dict[str, Any]],
        excluded_companies: List[str] = None,
        max_results: int = 15,
    ) -> Dict[str, Any]:
        """
        Execute multiple search queries and merge/deduplicate results.

        Returns a single result dict with merged, deduplicated jobs.
        """
        if not self.is_configured:
            return {
                "jobs": [],
                "total_found": 0,
                "search_queries": [p.get("query", "") for p in query_params_list],
                "cached": False,
                "error": "Job discovery API not configured. Set RAPIDAPI_KEY_JSEARCH environment variable.",
            }

        # Check if we have a cached result for the combined query set
        combined_key = self._get_cache_key({"queries": str(query_params_list)})
        cached = self._get_cached(combined_key)
        if cached:
            logger.info(f"Multi-query cache hit for key {combined_key[:8]}")
            cached["cached"] = True
            return cached

        all_jobs = []
        seen_job_ids = set()
        queries_executed = []
        total_found = 0

        # Execute queries sequentially (JSearch rate limits are tight)
        for params in query_params_list:
            result = self.search_jobs(params, excluded_companies)
            queries_executed.append(params.get("query", ""))

            if result.get("error"):
                logger.warning(f"Query failed: {params.get('query')}: {result['error']}")
                continue

            total_found += result.get("total_found", 0)

            for job in result.get("jobs", []):
                job_id = job.get("job_id", "")
                if job_id and job_id not in seen_job_ids:
                    seen_job_ids.add(job_id)
                    all_jobs.append(job)

        # Limit total results
        all_jobs = all_jobs[:max_results]

        result = {
            "jobs": all_jobs,
            "total_found": total_found,
            "search_queries": queries_executed,
            "search_query": queries_executed[0] if queries_executed else "",
            "cached": False,
            "cache_expires_at": time.time() + CACHE_TTL_SECONDS,
            "queries_executed": len(queries_executed),
        }

        self._set_cache(combined_key, result)
        return result

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

    def search_jobs(
        self,
        params: Dict[str, Any],
        excluded_companies: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for jobs via JSearch API.

        Returns normalized results with caching.
        """
        if not self.is_configured:
            logger.warning("RAPIDAPI_KEY_JSEARCH not configured - job discovery unavailable")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": params.get("query", ""),
                "cached": False,
                "error": "Job discovery API not configured. Set RAPIDAPI_KEY_JSEARCH environment variable.",
            }

        cache_key = self._get_cache_key(params)
        cached = self._get_cached(cache_key)
        if cached:
            logger.info(f"Job discovery cache hit for key {cache_key[:8]}")
            cached["cached"] = True
            return cached

        try:
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            }

            logger.info(f"Fetching jobs from JSearch: query='{params.get('query')}'")
            response = requests.get(
                self.JSEARCH_BASE_URL,
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            # Normalize results
            jobs = self._normalize_results(data, excluded_companies)

            result = {
                "jobs": jobs,
                "total_found": data.get("total", len(jobs)),
                "search_query": params.get("query", ""),
                "cached": False,
                "cache_expires_at": time.time() + CACHE_TTL_SECONDS,
            }

            self._set_cache(cache_key, result)
            return result

        except requests.exceptions.Timeout:
            logger.error("JSearch API timeout")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": params.get("query", ""),
                "cached": False,
                "error": "Job search timed out. Please try again.",
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"JSearch API HTTP error: {e}")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": params.get("query", ""),
                "cached": False,
                "error": f"Job search API error: {e.response.status_code}",
            }
        except Exception as e:
            logger.error(f"JSearch API error: {e}")
            return {
                "jobs": [],
                "total_found": 0,
                "search_query": params.get("query", ""),
                "cached": False,
                "error": "Job search temporarily unavailable.",
            }

    def _normalize_results(
        self, raw_data: Dict, excluded_companies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Normalize JSearch API response to standard format."""
        jobs = []
        excluded_lower = (
            [c.lower() for c in excluded_companies] if excluded_companies else []
        )

        for item in raw_data.get("data", []):
            company = item.get("employer_name", "Unknown")

            # Skip excluded companies
            if excluded_lower and company.lower() in excluded_lower:
                continue

            job = {
                "job_id": item.get("job_id", ""),
                "title": item.get("job_title", "Untitled"),
                "company": company,
                "company_logo": item.get("employer_logo"),
                "location": self._build_location_string(item),
                "salary_min": item.get("job_min_salary"),
                "salary_max": item.get("job_max_salary"),
                "salary_currency": item.get("job_salary_currency", "USD"),
                "salary_period": item.get("job_salary_period"),
                "posted_date": item.get("job_posted_at_datetime_utc"),
                "days_since_posted": self._calc_days_since(
                    item.get("job_posted_at_timestamp")
                ),
                "apply_url": item.get("job_apply_link", ""),
                "description_snippet": self._truncate(
                    item.get("job_description", ""), 500
                ),
                "employment_type": item.get("job_employment_type", "FULLTIME"),
                "is_remote": item.get("job_is_remote", False),
                "publisher": item.get("job_publisher", ""),
                "source": "jsearch",
                "network_connection": False,
                "network_connection_count": 0,
                # Rich data fields from JSearch (used by scorer)
                "job_required_experience": item.get("job_required_experience") or {},
                "job_required_skills": item.get("job_required_skills") or [],
                "job_highlights": item.get("job_highlights") or {},
            }
            jobs.append(job)

        return jobs[:15]  # Return max 15 results per query

    def _build_location_string(self, item: Dict) -> str:
        """Build a readable location string from job data."""
        parts = []
        city = item.get("job_city")
        state = item.get("job_state")
        country = item.get("job_country")

        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country and country not in ("US", "United States"):
            parts.append(country)

        if item.get("job_is_remote"):
            if parts:
                return f"{', '.join(parts)} (Remote)"
            return "Remote"

        return ", ".join(parts) if parts else "Location not specified"

    def _calc_days_since(self, timestamp) -> Optional[int]:
        """Calculate days since a Unix timestamp."""
        if not timestamp:
            return None
        try:
            return max(0, int((time.time() - float(timestamp)) / 86400))
        except (ValueError, TypeError):
            return None

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text to max length with ellipsis."""
        if not text:
            return ""
        # Strip HTML tags
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        if len(clean) <= max_len:
            return clean
        return clean[:max_len].rsplit(" ", 1)[0] + "..."

    def flag_network_companies(
        self, jobs: List[Dict], network_companies: List[str]
    ) -> List[Dict]:
        """
        Cross-reference job results with the candidate's LinkedIn network.
        Flags jobs where the candidate has connections at the company.
        """
        if not network_companies:
            return jobs

        # Normalize network company names for matching
        network_lower = {}
        for company in network_companies:
            normalized = company.lower().strip()
            network_lower[normalized] = network_lower.get(normalized, 0) + 1

        for job in jobs:
            company_lower = job["company"].lower().strip()
            # Check for exact match or substring match
            for net_company, count in network_lower.items():
                if (
                    net_company == company_lower
                    or net_company in company_lower
                    or company_lower in net_company
                ):
                    job["network_connection"] = True
                    job["network_connection_count"] = count
                    break

        # Sort: network connections first, then by posted date
        jobs.sort(
            key=lambda j: (
                not j.get("network_connection", False),
                j.get("days_since_posted") or 999,
            )
        )

        return jobs


# Singleton instance
job_discovery_service = JobDiscoveryService()
