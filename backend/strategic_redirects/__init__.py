"""
Strategic Redirects Module

Generates alternative role suggestions for candidates with low fit scores.
Rule-based implementation - no LLM required.

Per STRATEGIC_REDIRECTS_IMPLEMENTATION.md:
- Triggers when fit_score < 60 or recommendation is Skip/Do Not Apply
- Outputs 3-6 roles grouped into: Adjacent Titles, Bridge Roles, Context Shifts
- Never suggests roles above candidate's demonstrated level
- Based on CEC strengths, not aspirations

Core Principle: Redirect toward leverage, not aspiration.
"""

from .redirect_generator import (
    StrategicRedirectGenerator,
    generate_strategic_redirects,
)
from .models import (
    StrategicRedirectRole,
    StrategicRedirectsResult,
    RoleCategory,
)

__all__ = [
    'StrategicRedirectGenerator',
    'generate_strategic_redirects',
    'StrategicRedirectRole',
    'StrategicRedirectsResult',
    'RoleCategory',
]
