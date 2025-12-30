"""Date and time utility functions"""

from datetime import datetime
from typing import Optional


def calculate_days_since(date_str: Optional[str]) -> int:
    """Calculate days since a given date string (ISO format)."""
    if not date_str:
        return 0
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if date.tzinfo:
            date = date.replace(tzinfo=None)
        return (datetime.now() - date).days
    except (ValueError, TypeError):
        return 0
