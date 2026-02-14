"""
LinkedIn Network Parser
Parses LinkedIn connections CSV exports to extract company data.
Used for network-aware job discovery.

LinkedIn CSV format (exported from Settings > Data Privacy > Get a copy of your data):
First Name,Last Name,URL,Email Address,Company,Position,Connected On
"""

import csv
import io
import logging
from typing import List, Dict, Optional
from collections import Counter

logger = logging.getLogger("henryhq.linkedin_network")


class LinkedInNetworkParser:
    """Parses LinkedIn connections CSV to extract company network data."""

    # Expected CSV headers (LinkedIn export format)
    EXPECTED_HEADERS = {
        "first name", "last name", "url", "email address",
        "company", "position", "connected on"
    }

    def parse_csv(self, csv_content: str) -> List[Dict[str, str]]:
        """
        Parse a LinkedIn connections CSV export.

        Args:
            csv_content: Raw CSV string content

        Returns:
            List of connection dicts with keys:
            first_name, last_name, company, position, connected_on
        """
        connections = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))

            if not reader.fieldnames:
                logger.warning("CSV has no headers")
                return []

            # Normalize headers to lowercase for matching
            header_map = {}
            for field in reader.fieldnames:
                header_map[field.lower().strip()] = field

            # Check for required 'company' column
            company_key = None
            for key in ("company", "organization"):
                if key in header_map:
                    company_key = header_map[key]
                    break

            if not company_key:
                logger.warning("CSV missing 'Company' column")
                return []

            for row in reader:
                company = (row.get(company_key) or "").strip()
                if not company:
                    continue

                connection = {
                    "first_name": (row.get(header_map.get("first name", "First Name")) or "").strip(),
                    "last_name": (row.get(header_map.get("last name", "Last Name")) or "").strip(),
                    "company": company,
                    "position": (row.get(header_map.get("position", "Position")) or "").strip(),
                    "connected_on": (row.get(header_map.get("connected on", "Connected On")) or "").strip(),
                }
                connections.append(connection)

        except csv.Error as e:
            logger.error(f"CSV parsing error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing LinkedIn CSV: {e}")
            return []

        logger.info(f"Parsed {len(connections)} connections from LinkedIn CSV")
        return connections

    def extract_companies(self, connections: List[Dict[str, str]]) -> List[Dict[str, int]]:
        """
        Extract unique companies with connection counts.

        Returns:
            List of dicts: [{"company": "Stripe", "count": 3}, ...]
            Sorted by count descending.
        """
        company_counts = Counter()

        for conn in connections:
            company = conn.get("company", "").strip()
            if company:
                # Normalize: trim whitespace, basic dedup
                company_counts[company] += 1

        # Sort by count descending
        result = [
            {"company": company, "count": count}
            for company, count in company_counts.most_common()
        ]

        logger.info(f"Extracted {len(result)} unique companies from {len(connections)} connections")
        return result

    def get_company_names(self, connections: List[Dict[str, str]]) -> List[str]:
        """
        Get a flat list of unique company names from connections.
        Used for cross-referencing with job search results.
        """
        companies = set()
        for conn in connections:
            company = conn.get("company", "").strip()
            if company:
                companies.add(company)
        return sorted(companies)

    def get_connections_at_company(
        self, connections: List[Dict[str, str]], company_name: str
    ) -> List[Dict[str, str]]:
        """
        Get all connections at a specific company.
        Useful for showing "You know X people at this company".
        """
        company_lower = company_name.lower().strip()
        return [
            conn for conn in connections
            if conn.get("company", "").lower().strip() == company_lower
            or company_lower in conn.get("company", "").lower().strip()
        ]


# Singleton instance
linkedin_network_parser = LinkedInNetworkParser()
