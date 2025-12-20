"""
Strategic Redirects - Data Models

Defines the data structures for alternative role suggestions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RoleCategory(Enum):
    """Categories of alternative roles."""
    ADJACENT = "adjacent_titles"      # Same level, different function/focus
    BRIDGE = "bridge_roles"           # -1 level or lateral with growth path
    CONTEXT_SHIFT = "context_shifts"  # Same title, different environment


class SeniorityLevel(Enum):
    """Seniority levels for role matching."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"

    @classmethod
    def from_string(cls, level_str: str) -> "SeniorityLevel":
        """Convert string to SeniorityLevel."""
        level_map = {
            "entry": cls.ENTRY,
            "junior": cls.JUNIOR,
            "associate": cls.JUNIOR,
            "mid": cls.MID,
            "mid-level": cls.MID,
            "senior": cls.SENIOR,
            "sr": cls.SENIOR,
            "staff": cls.STAFF,
            "principal": cls.PRINCIPAL,
            "lead": cls.STAFF,
            "director": cls.DIRECTOR,
            "head": cls.DIRECTOR,
            "vp": cls.VP,
            "vice president": cls.VP,
            "c-level": cls.C_LEVEL,
            "chief": cls.C_LEVEL,
            "cto": cls.C_LEVEL,
            "cpo": cls.C_LEVEL,
            "ceo": cls.C_LEVEL,
        }
        return level_map.get(level_str.lower().strip(), cls.MID)

    def can_suggest(self, target_level: "SeniorityLevel") -> bool:
        """Check if target_level is at or below this level."""
        level_order = [
            SeniorityLevel.ENTRY,
            SeniorityLevel.JUNIOR,
            SeniorityLevel.MID,
            SeniorityLevel.SENIOR,
            SeniorityLevel.STAFF,
            SeniorityLevel.PRINCIPAL,
            SeniorityLevel.DIRECTOR,
            SeniorityLevel.VP,
            SeniorityLevel.C_LEVEL,
        ]
        return level_order.index(target_level) <= level_order.index(self)


@dataclass
class StrategicRedirectRole:
    """A single alternative role suggestion."""
    role_title: str
    level: str
    company_type: str
    fit_rationale: str
    category: RoleCategory

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_title": self.role_title,
            "level": self.level,
            "company_type": self.company_type,
            "fit_rationale": self.fit_rationale,
        }


@dataclass
class StrategicRedirectsResult:
    """Container for all strategic redirect suggestions."""
    adjacent_titles: List[StrategicRedirectRole] = field(default_factory=list)
    bridge_roles: List[StrategicRedirectRole] = field(default_factory=list)
    context_shifts: List[StrategicRedirectRole] = field(default_factory=list)
    closing_message: str = "These roles better align with your current evidence and give you faster interview leverage."
    triggered: bool = False
    trigger_reason: str = ""

    def add_role(self, role: StrategicRedirectRole):
        """Add a role to the appropriate category."""
        if role.category == RoleCategory.ADJACENT:
            self.adjacent_titles.append(role)
        elif role.category == RoleCategory.BRIDGE:
            self.bridge_roles.append(role)
        elif role.category == RoleCategory.CONTEXT_SHIFT:
            self.context_shifts.append(role)

    def has_suggestions(self) -> bool:
        """Check if any suggestions were generated."""
        return bool(self.adjacent_titles or self.bridge_roles or self.context_shifts)

    def total_count(self) -> int:
        """Total number of suggestions."""
        return len(self.adjacent_titles) + len(self.bridge_roles) + len(self.context_shifts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adjacent_titles": [r.to_dict() for r in self.adjacent_titles],
            "bridge_roles": [r.to_dict() for r in self.bridge_roles],
            "context_shifts": [r.to_dict() for r in self.context_shifts],
            "closing_message": self.closing_message,
            "triggered": self.triggered,
            "trigger_reason": self.trigger_reason,
            "total_suggestions": self.total_count(),
        }


# Role family mappings for adjacent title suggestions
ROLE_FAMILIES = {
    "product": {
        "core_titles": ["Product Manager", "Product Owner", "Technical PM"],
        "adjacent_titles": [
            "Program Manager",
            "Product Operations Manager",
            "Technical Program Manager",
            "Product Analyst",
            "Growth Product Manager",
            "Platform Product Manager",
        ],
        "bridge_titles": [
            "Associate Product Manager",
            "Junior Product Manager",
            "Product Coordinator",
        ],
    },
    "engineering": {
        "core_titles": ["Software Engineer", "Developer", "SWE"],
        "adjacent_titles": [
            "Solutions Engineer",
            "Developer Advocate",
            "QA Engineer",
            "DevOps Engineer",
            "Site Reliability Engineer",
            "Technical Support Engineer",
        ],
        "bridge_titles": [
            "Junior Engineer",
            "Associate Engineer",
            "Engineering Intern",
        ],
    },
    "recruiting": {
        "core_titles": ["Recruiter", "Technical Recruiter", "Talent Acquisition"],
        "adjacent_titles": [
            "Sourcer",
            "Recruiting Coordinator",
            "HR Business Partner",
            "People Operations",
            "Talent Partner",
            "University Recruiter",
        ],
        "bridge_titles": [
            "Recruiting Coordinator",
            "Sourcing Specialist",
            "HR Coordinator",
        ],
    },
    "sales": {
        "core_titles": ["Account Executive", "Sales Rep", "BDR", "SDR"],
        "adjacent_titles": [
            "Customer Success Manager",
            "Account Manager",
            "Sales Engineer",
            "Solutions Consultant",
            "Business Development Manager",
        ],
        "bridge_titles": [
            "Sales Development Representative",
            "Business Development Representative",
            "Inside Sales Rep",
        ],
    },
    "marketing": {
        "core_titles": ["Marketing Manager", "Growth Manager", "Brand Manager"],
        "adjacent_titles": [
            "Product Marketing Manager",
            "Content Marketing Manager",
            "Demand Generation Manager",
            "Marketing Operations Manager",
            "Community Manager",
        ],
        "bridge_titles": [
            "Marketing Coordinator",
            "Marketing Associate",
            "Content Specialist",
        ],
    },
    "design": {
        "core_titles": ["Product Designer", "UX Designer", "UI Designer"],
        "adjacent_titles": [
            "UX Researcher",
            "Visual Designer",
            "Interaction Designer",
            "Design Systems Designer",
            "Brand Designer",
        ],
        "bridge_titles": [
            "Junior Designer",
            "Associate Designer",
            "Design Intern",
        ],
    },
    "data": {
        "core_titles": ["Data Scientist", "Data Analyst", "ML Engineer"],
        "adjacent_titles": [
            "Business Intelligence Analyst",
            "Analytics Engineer",
            "Data Engineer",
            "Research Scientist",
            "Quantitative Analyst",
        ],
        "bridge_titles": [
            "Junior Data Analyst",
            "Associate Data Scientist",
            "Data Analyst",
        ],
    },
}

# Company type mappings
COMPANY_CONTEXTS = {
    "enterprise": {
        "name": "Enterprise",
        "types": ["F500", "Large Enterprise", "Public Company"],
        "context_shift": ["Growth-stage startup", "Mid-size company", "Series C+ startup"],
    },
    "startup": {
        "name": "Startup",
        "types": ["Early-stage", "Seed", "Series A-B"],
        "context_shift": ["Scale-up", "Growth company", "Established startup"],
    },
    "scale_up": {
        "name": "Growth Company",
        "types": ["Series C+", "Scale-up", "Pre-IPO"],
        "context_shift": ["Early-stage startup", "Enterprise", "Mid-market"],
    },
    "agency": {
        "name": "Agency/Consulting",
        "types": ["Agency", "Consulting firm", "Professional services"],
        "context_shift": ["In-house role", "Product company", "Tech company"],
    },
}
