"""
Strategic Redirect Generator

Rule-based alternative role suggestion engine.
No LLM required - uses deterministic logic based on role families and candidate profile.

Per STRATEGIC_REDIRECTS_IMPLEMENTATION.md:
- Never suggests roles above candidate's demonstrated level
- Based on CEC strengths, not aspirations
- Practical and specific, no motivational fluff
"""

from typing import Dict, Any, List, Optional
import re
from .models import (
    StrategicRedirectRole,
    StrategicRedirectsResult,
    RoleCategory,
    SeniorityLevel,
    ROLE_FAMILIES,
    COMPANY_CONTEXTS,
)


class StrategicRedirectGenerator:
    """
    Generates strategic redirects for low-fit candidates.

    Rule-based, deterministic logic - no LLM calls.
    """

    # Trigger conditions
    FIT_SCORE_THRESHOLD = 60
    LOW_FIT_RECOMMENDATIONS = ["Skip", "Do Not Apply", "Long Shot", "Apply with Caution"]

    def __init__(self):
        self.result = StrategicRedirectsResult()

    def should_trigger(
        self,
        fit_score: int,
        recommendation: str,
        primary_gap: Optional[str] = None
    ) -> bool:
        """
        Determine if strategic redirects should be generated.

        Triggers when:
        1. fit_score < 60
        2. recommendation in Skip/Do Not Apply/Long Shot
        3. primary_gap in scope/years/domain AND fit_score < 70
        """
        if fit_score < self.FIT_SCORE_THRESHOLD:
            self.result.trigger_reason = f"Fit score {fit_score}% below threshold ({self.FIT_SCORE_THRESHOLD}%)"
            return True

        if recommendation in self.LOW_FIT_RECOMMENDATIONS:
            self.result.trigger_reason = f"Recommendation is '{recommendation}'"
            return True

        if primary_gap in ["scope", "years", "domain"] and fit_score < 70:
            self.result.trigger_reason = f"Primary gap is '{primary_gap}' with fit score {fit_score}%"
            return True

        return False

    def generate(
        self,
        target_role: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        fit_score: int,
        recommendation: str,
    ) -> StrategicRedirectsResult:
        """
        Generate strategic redirect suggestions.

        Args:
            target_role: {title, level, company_type}
            candidate_profile: {current_level, cec_strengths, recent_titles, company_types}
            gap_analysis: {primary_gap, secondary_gap, specific_gaps}
            fit_score: Current fit score
            recommendation: Current recommendation

        Returns:
            StrategicRedirectsResult with suggestions
        """
        self.result = StrategicRedirectsResult()

        # Check if should trigger
        primary_gap = gap_analysis.get("primary_gap", "")
        if not self.should_trigger(fit_score, recommendation, primary_gap):
            return self.result

        self.result.triggered = True

        # Extract key information
        target_title = target_role.get("title", "").lower()
        target_level = SeniorityLevel.from_string(target_role.get("level", "mid"))
        target_company = target_role.get("company_type", "")

        candidate_level = SeniorityLevel.from_string(
            candidate_profile.get("current_level", "mid")
        )
        cec_strengths = candidate_profile.get("cec_strengths", [])
        recent_titles = candidate_profile.get("recent_titles", [])
        company_types = candidate_profile.get("company_types", [])

        # Detect role family
        role_family = self._detect_role_family(target_title, recent_titles)

        # Generate suggestions for each category
        self._generate_adjacent_titles(
            role_family, candidate_level, cec_strengths, primary_gap
        )
        self._generate_bridge_roles(
            role_family, candidate_level, target_level, cec_strengths
        )
        self._generate_context_shifts(
            target_title, candidate_level, company_types, target_company
        )

        # Ensure we have at least some suggestions
        if not self.result.has_suggestions():
            self._generate_fallback_suggestions(
                target_title, candidate_level, primary_gap
            )

        return self.result

    def _detect_role_family(
        self, target_title: str, recent_titles: List[str]
    ) -> str:
        """Detect which role family the target belongs to."""
        title_lower = target_title.lower()
        all_titles = [title_lower] + [t.lower() for t in recent_titles]

        for family, data in ROLE_FAMILIES.items():
            for core_title in data["core_titles"]:
                if any(core_title.lower() in t for t in all_titles):
                    return family

        # Keyword-based detection
        keyword_map = {
            "product": ["product", "pm", "ppm"],
            "engineering": ["engineer", "developer", "software", "swe", "sre"],
            "recruiting": ["recruit", "talent", "sourcer", "ta "],
            "sales": ["sales", "account", "bdr", "sdr", "revenue"],
            "marketing": ["marketing", "growth", "brand", "demand"],
            "design": ["design", "ux", "ui", "visual"],
            "data": ["data", "analyst", "ml", "machine learning", "bi"],
        }

        for family, keywords in keyword_map.items():
            if any(kw in title_lower for kw in keywords):
                return family

        return "general"

    def _generate_adjacent_titles(
        self,
        role_family: str,
        candidate_level: SeniorityLevel,
        cec_strengths: List[Dict],
        primary_gap: str
    ):
        """Generate adjacent title suggestions (same level, different focus)."""
        family_data = ROLE_FAMILIES.get(role_family, {})
        adjacent_titles = family_data.get("adjacent_titles", [])

        if not adjacent_titles:
            return

        # Map CEC strengths to roles
        strength_map = {
            "Execution": ["Program Manager", "Project Manager", "Operations Manager"],
            "Technical": ["Solutions Engineer", "Technical PM", "Developer Advocate"],
            "Collaboration": ["Customer Success Manager", "Account Manager", "Partner Manager"],
            "Analytics": ["Product Analyst", "Data Analyst", "Business Intelligence Analyst"],
            "Leadership": ["Team Lead", "Engineering Manager", "Product Lead"],
            "Communication": ["Product Marketing", "Developer Relations", "Content Strategy"],
        }

        suggested = set()

        # Prioritize based on CEC strengths
        for strength in cec_strengths[:3]:  # Top 3 strengths
            category = strength.get("category", "")
            score = strength.get("score", 0)

            if score >= 70 and category in strength_map:
                for role in strength_map[category]:
                    if role not in suggested and len(suggested) < 2:
                        suggested.add(role)
                        self.result.add_role(StrategicRedirectRole(
                            role_title=role,
                            level=candidate_level.value,
                            company_type=self._get_appropriate_company_type(candidate_level),
                            fit_rationale=f"Your {category} strength ({score}%) maps well to {role} requirements. This leverages your existing expertise.",
                            category=RoleCategory.ADJACENT
                        ))

        # Fill remaining slots from family adjacent titles
        for title in adjacent_titles[:3]:
            if title not in suggested and len(self.result.adjacent_titles) < 2:
                self.result.add_role(StrategicRedirectRole(
                    role_title=title,
                    level=candidate_level.value,
                    company_type=self._get_appropriate_company_type(candidate_level),
                    fit_rationale=f"This role is adjacent to your target but better matches your current experience level and background.",
                    category=RoleCategory.ADJACENT
                ))

    def _generate_bridge_roles(
        self,
        role_family: str,
        candidate_level: SeniorityLevel,
        target_level: SeniorityLevel,
        cec_strengths: List[Dict]
    ):
        """Generate bridge role suggestions (-1 level or lateral with growth path)."""
        # Skip if candidate is entry level (no -1 available)
        if candidate_level == SeniorityLevel.ENTRY:
            return

        family_data = ROLE_FAMILIES.get(role_family, {})
        bridge_titles = family_data.get("bridge_titles", [])

        # Determine bridge level
        level_order = [
            SeniorityLevel.ENTRY,
            SeniorityLevel.JUNIOR,
            SeniorityLevel.MID,
            SeniorityLevel.SENIOR,
            SeniorityLevel.STAFF,
            SeniorityLevel.PRINCIPAL,
            SeniorityLevel.DIRECTOR,
            SeniorityLevel.VP,
        ]

        current_idx = level_order.index(candidate_level)
        bridge_level = level_order[max(0, current_idx - 1)]

        # Add bridge roles
        for title in bridge_titles[:2]:
            self.result.add_role(StrategicRedirectRole(
                role_title=title,
                level=f"{bridge_level.value} to {candidate_level.value}",
                company_type="Growth companies, Scale-ups",
                fit_rationale=f"This role provides a path to demonstrate senior-level execution while building the experience you need.",
                category=RoleCategory.BRIDGE
            ))

        # Add a lateral growth role if we have strong CEC signals
        if cec_strengths and len(cec_strengths) > 0:
            top_strength = cec_strengths[0]
            if top_strength.get("score", 0) >= 75:
                lateral_title = f"Senior {role_family.title()} Lead"
                self.result.add_role(StrategicRedirectRole(
                    role_title=lateral_title,
                    level=candidate_level.value,
                    company_type="Established startups, Mid-market",
                    fit_rationale=f"Your strong {top_strength.get('category', 'track record')} positions you for lateral moves that build scope.",
                    category=RoleCategory.BRIDGE
                ))

    def _generate_context_shifts(
        self,
        target_title: str,
        candidate_level: SeniorityLevel,
        company_types: List[str],
        target_company: str
    ):
        """Generate context shift suggestions (same title, different environment)."""
        # Detect current company context
        current_context = self._detect_company_context(company_types)
        target_context = self._detect_company_context([target_company])

        # Find alternative contexts
        for context_key, context_data in COMPANY_CONTEXTS.items():
            if context_key not in [current_context, target_context]:
                shifts = context_data.get("context_shift", [])
                if shifts:
                    # Clean the target title (remove level prefixes)
                    clean_title = re.sub(r'^(senior|junior|associate|lead|staff|principal)\s+', '', target_title, flags=re.IGNORECASE)

                    self.result.add_role(StrategicRedirectRole(
                        role_title=clean_title.title() if clean_title else "Similar Role",
                        level=candidate_level.value,
                        company_type=shifts[0],
                        fit_rationale=f"Your {current_context} experience transfers well to {shifts[0]} environments, where different skills are prioritized.",
                        category=RoleCategory.CONTEXT_SHIFT
                    ))
                    break

        # Always suggest a smaller company context if not already
        if "startup" not in current_context.lower() and len(self.result.context_shifts) < 2:
            self.result.add_role(StrategicRedirectRole(
                role_title=target_title.title(),
                level=candidate_level.value,
                company_type="Early-stage startups (10-50 employees)",
                fit_rationale="Smaller teams value generalists and breadth of experience. Your range of skills is a competitive advantage here.",
                category=RoleCategory.CONTEXT_SHIFT
            ))

    def _generate_fallback_suggestions(
        self,
        target_title: str,
        candidate_level: SeniorityLevel,
        primary_gap: str
    ):
        """Generate fallback suggestions when specific role family isn't detected."""
        gap_messages = {
            "scope": "Look for roles with more defined scope where you can build toward broader ownership.",
            "years": "Focus on roles that value demonstrated impact over years of experience.",
            "domain": "Consider adjacent industries where your core skills transfer with less domain-specific requirements.",
            "credibility": "Target companies where your experience profile matches their typical hiring patterns.",
        }

        message = gap_messages.get(primary_gap, "Consider roles that better match your current experience profile.")

        self.result.add_role(StrategicRedirectRole(
            role_title=f"{target_title} (at smaller company)",
            level=candidate_level.value,
            company_type="Startups, Growth companies",
            fit_rationale=message,
            category=RoleCategory.CONTEXT_SHIFT
        ))

    def _detect_company_context(self, company_types: List[str]) -> str:
        """Detect the company context from a list of company types."""
        if not company_types:
            return "unknown"

        all_types = " ".join(company_types).lower()

        if any(kw in all_types for kw in ["f500", "enterprise", "large", "public"]):
            return "enterprise"
        if any(kw in all_types for kw in ["seed", "series a", "series b", "early"]):
            return "startup"
        if any(kw in all_types for kw in ["series c", "scale", "growth", "pre-ipo"]):
            return "scale_up"
        if any(kw in all_types for kw in ["agency", "consulting", "professional service"]):
            return "agency"

        return "mid_market"

    def _get_appropriate_company_type(self, level: SeniorityLevel) -> str:
        """Get appropriate company type suggestion based on level."""
        level_company_map = {
            SeniorityLevel.ENTRY: "Startups, Growth companies",
            SeniorityLevel.JUNIOR: "Startups, Mid-size companies",
            SeniorityLevel.MID: "Growth companies, Scale-ups",
            SeniorityLevel.SENIOR: "Scale-ups, Established companies",
            SeniorityLevel.STAFF: "Growth companies, Enterprise",
            SeniorityLevel.PRINCIPAL: "Scale-ups, Enterprise",
            SeniorityLevel.DIRECTOR: "Growth companies, Enterprise",
            SeniorityLevel.VP: "Scale-ups, Enterprise",
            SeniorityLevel.C_LEVEL: "Startups (as leader), Enterprise",
        }
        return level_company_map.get(level, "Growth companies")


def generate_strategic_redirects(
    target_role: Dict[str, Any],
    candidate_profile: Dict[str, Any],
    gap_analysis: Dict[str, Any],
    fit_score: int,
    recommendation: str,
) -> Dict[str, Any]:
    """
    Convenience function for generating strategic redirects.

    Returns the result as a dictionary for JSON serialization.
    """
    generator = StrategicRedirectGenerator()
    result = generator.generate(
        target_role=target_role,
        candidate_profile=candidate_profile,
        gap_analysis=gap_analysis,
        fit_score=fit_score,
        recommendation=recommendation,
    )
    return result.to_dict()
