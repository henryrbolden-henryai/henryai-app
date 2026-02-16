"""
Indeed API Client
Wraps the Indeed API (via RapidAPI) to fetch job listings.
Uses the same RapidAPI key infrastructure as JSearch.

Environment variables:
  RAPIDAPI_KEY_INDEED  — dedicated key for Indeed API
  RAPIDAPI_KEY         — fallback shared key
"""

import os
import re
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger("henryhq.indeed_api_client")

# Indeed API on RapidAPI
INDEED_API_HOST = "indeed12.p.rapidapi.com"
INDEED_SEARCH_URL = f"https://{INDEED_API_HOST}/jobs/search"


def get_api_key() -> Optional[str]:
    """Get the RapidAPI key for Indeed."""
    return os.getenv("RAPIDAPI_KEY_INDEED") or os.getenv("RAPIDAPI_KEY_JSEARCH") or os.getenv("RAPIDAPI_KEY")


def search_indeed_jobs(
    query: str,
    location: str = "",
    country_code: str = "US",
    job_type: str = None,
    num_pages: int = 1,
) -> List[Dict[str, Any]]:
    """
    Search Indeed for jobs via RapidAPI.

    Returns a list of normalized job dicts.
    Raises exception if API call fails.
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("No RapidAPI key configured for Indeed")
        return []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": INDEED_API_HOST,
    }

    params = {
        "query": query,
        "location": location,
        "page_id": "1",
        "locality": country_code.lower(),
        "fromage": "14",  # Last 14 days
        "radius": "50",
    }

    if job_type:
        params["job_type"] = job_type

    logger.info(f"Indeed API search: query='{query}', location='{location}'")

    try:
        response = requests.get(
            INDEED_SEARCH_URL,
            headers=headers,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        # The Indeed12 API returns results in various formats
        # Try to extract the jobs array
        jobs_raw = []
        if isinstance(data, list):
            jobs_raw = data
        elif isinstance(data, dict):
            jobs_raw = data.get("hits", data.get("results", data.get("jobs", [])))
            if not jobs_raw and "data" in data:
                jobs_raw = data["data"]

        logger.info(f"Indeed returned {len(jobs_raw)} results")

        # Normalize to standard format
        normalized = []
        for item in jobs_raw:
            job = _normalize_indeed_item(item)
            if job:
                normalized.append(job)

        return normalized[:15]

    except requests.exceptions.Timeout:
        logger.error("Indeed API timeout")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"Indeed API HTTP error: {e}")
        # If 403/429, the key might not have Indeed access — fail gracefully
        if e.response.status_code in (403, 429):
            logger.warning("Indeed API access denied or rate limited — skipping")
            return []
        raise
    except Exception as e:
        logger.error(f"Indeed API error: {e}")
        raise


def _normalize_indeed_item(item: Dict) -> Optional[Dict]:
    """Normalize a single Indeed API result to standard format."""
    if not item:
        return None

    # Indeed API fields vary by provider. Try common field names.
    title = (
        item.get("title")
        or item.get("job_title")
        or item.get("jobTitle")
        or "Untitled"
    )
    company = (
        item.get("company_name")
        or item.get("company")
        or item.get("employer_name")
        or "Unknown"
    )
    location = (
        item.get("location")
        or item.get("job_location")
        or item.get("formattedLocation")
        or ""
    )
    description = (
        item.get("description")
        or item.get("snippet")
        or item.get("job_description")
        or ""
    )

    # Clean HTML from description
    description_clean = re.sub(r"<[^>]+>", "", description) if description else ""

    job_id = (
        item.get("id")
        or item.get("job_id")
        or item.get("jobkey")
        or ""
    )

    apply_url = (
        item.get("link")
        or item.get("url")
        or item.get("job_url")
        or item.get("redirect_url")
        or ""
    )

    salary_str = (
        item.get("salary")
        or item.get("compensation")
        or item.get("formattedSalary")
        or item.get("salary_snippet")
        or ""
    )

    job_type_raw = (
        item.get("job_type")
        or item.get("employment_type")
        or item.get("type")
        or ""
    )

    posted_date = (
        item.get("date")
        or item.get("posted_date")
        or item.get("pubDate")
        or item.get("formattedRelativeTime")
        or ""
    )

    return {
        "job_id": str(job_id),
        "title": title,
        "company": company,
        "location": location,
        "description": description_clean[:500],
        "description_snippet": description_clean[:500],
        "compensation": str(salary_str) if salary_str else "",
        "salary": str(salary_str) if salary_str else "",
        "job_type": str(job_type_raw),
        "posted_date": str(posted_date) if posted_date else "",
        "view_job_url": apply_url,
        "apply_url": apply_url,
        "company_logo": item.get("company_logo") or item.get("employer_logo"),
    }
