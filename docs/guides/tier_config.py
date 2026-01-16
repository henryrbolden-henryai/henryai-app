"""
HenryHQ Tier Configuration
==========================

Defines subscription tiers, pricing, limits, and feature access.

Tier Philosophy:
- Preview: Free orientation. Show what HenryHQ can do. Not a real tier.
- Recruiter: "I'm applying, but I want to be smart."
- Principal: "I'm running a real search." (Revenue engine - Most Popular)
- Partner: "I'm deep in interviews and need to improve."
- Coach: "I need help closing." (Human time, limited seats)

Pricing Psychology:
- $25 Recruiter: Serious enough to filter tire-kickers, cheap enough to try
- $49 Principal: Sweet spot for "serious tool" without justification needed
- $99 Partner: Under triple digits, justified by interview intelligence
- $199 Coach: Premium feel, human time justifies the jump

Annual Pricing (save ~33%):
- Recruiter: $199/year (save $101)
- Principal: $399/year (save $189)
- Partner: $799/year (save $389)
- Coach: $1,599/year (save $789)

Last Updated: January 2026
"""

from typing import Dict, Any, List, Optional

# =============================================================================
# TIER ORDER (lowest to highest)
# =============================================================================

TIER_ORDER: List[str] = [
    "preview",
    "recruiter",
    "principal",
    "partner",
    "coach"
]

# =============================================================================
# TIER DISPLAY NAMES
# =============================================================================

TIER_NAMES: Dict[str, str] = {
    "preview": "Preview",
    "recruiter": "Recruiter",
    "principal": "Principal",
    "partner": "Partner",
    "coach": "Coach"
}

# =============================================================================
# TIER PRICING (monthly and annual)
# =============================================================================

TIER_PRICES: Dict[str, int] = {
    "preview": 0,
    "recruiter": 25,
    "principal": 49,
    "partner": 99,
    "coach": 199
}

# Note: These are the canonical prices from pricing_page_copy.md
# - Preview: Free
# - Recruiter: $25/mo
# - Principal: $49/mo (Most Popular)
# - Partner: $99/mo
# - Coach: $199/mo

TIER_PRICES_ANNUAL: Dict[str, int] = {
    "preview": 0,
    "recruiter": 199,    # Save $101 (33% off)
    "principal": 399,    # Save $189 (32% off)
    "partner": 799,      # Save $389 (33% off)
    "coach": 1599        # Save $789 (33% off)
}

# =============================================================================
# TIER TAGLINES (for marketing/UI)
# =============================================================================

TIER_TAGLINES: Dict[str, str] = {
    "preview": "See what HenryHQ can do",
    "recruiter": "Apply smarter, not harder",
    "principal": "Your full search toolkit",
    "partner": "Learn from every interview",
    "coach": "Close with confidence"
}

TIER_DESCRIPTIONS: Dict[str, str] = {
    "preview": "Try one analysis to see how HenryHQ evaluates your fit.",
    "recruiter": "For job seekers who want to stop wasting time on bad-fit applications.",
    "principal": "For serious searchers running an active job search.",
    "partner": "For candidates deep in interviews who need to improve their close rate.",
    "coach": "For candidates with offers who need human judgment to close."
}

# =============================================================================
# TIER LIMITS
# =============================================================================
# -1 means unlimited
# 0 means feature not available (use features dict for boolean access)

TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    "preview": {
        # Usage limits
        "applications_per_month": 1,
        "fit_analyses_per_month": 1,
        "resumes_per_month": 0,
        "cover_letters_per_month": 0,
        "henry_conversations_per_month": 0,
        "mock_interviews_per_month": 0,
        "coaching_sessions_per_month": 0,
        
        # Feature access (boolean or "limited" for gated access)
        "features": {
            "full_fit_analysis": "limited",  # Shows 80% of analysis, gates the rest
            "reality_check": False,
            "screening_guidance": False,
            "document_generation": False,
            "interview_prep_guides": False,
            "outreach_templates": False,
            "pipeline_command_center": False,
            "pipeline_pattern_insights": False,
            "mock_interviews": False,
            "cross_interview_patterns": False,
            "story_bank": False,
            "rejection_forensics": False,
            "negotiation_prep": False,
            "full_negotiation_support": False,
            "live_coaching": False,
            "priority_henry": False
        }
    },
    
    "recruiter": {
        # Usage limits
        "applications_per_month": 10,
        "fit_analyses_per_month": 10,
        "resumes_per_month": 3,
        "cover_letters_per_month": 3,
        "henry_conversations_per_month": 10,
        "mock_interviews_per_month": 0,
        "coaching_sessions_per_month": 0,
        
        # Feature access
        "features": {
            "full_fit_analysis": True,
            "reality_check": True,
            "screening_guidance": True,
            "document_generation": True,
            "interview_prep_guides": False,
            "outreach_templates": False,
            "pipeline_command_center": False,
            "pipeline_pattern_insights": False,
            "mock_interviews": False,
            "cross_interview_patterns": False,
            "story_bank": False,
            "rejection_forensics": False,
            "negotiation_prep": False,
            "full_negotiation_support": False,
            "live_coaching": False,
            "priority_henry": False
        }
    },
    
    "principal": {
        # Usage limits
        "applications_per_month": 30,
        "fit_analyses_per_month": 30,
        "resumes_per_month": 15,
        "cover_letters_per_month": 15,
        "henry_conversations_per_month": 30,
        "mock_interviews_per_month": 5,
        "coaching_sessions_per_month": 0,
        
        # Feature access
        "features": {
            "full_fit_analysis": True,
            "reality_check": True,
            "screening_guidance": True,
            "document_generation": True,
            "interview_prep_guides": True,
            "outreach_templates": True,
            "pipeline_command_center": True,
            "pipeline_pattern_insights": True,
            "mock_interviews": True,
            "cross_interview_patterns": False,
            "story_bank": False,
            "rejection_forensics": False,
            "negotiation_prep": False,
            "full_negotiation_support": False,
            "live_coaching": False,
            "priority_henry": False
        }
    },
    
    "partner": {
        # Usage limits
        "applications_per_month": 50,
        "fit_analyses_per_month": -1,  # Unlimited
        "resumes_per_month": -1,       # Unlimited
        "cover_letters_per_month": -1, # Unlimited
        "henry_conversations_per_month": -1,  # Unlimited
        "mock_interviews_per_month": 15,
        "coaching_sessions_per_month": 0,
        
        # Feature access
        "features": {
            "full_fit_analysis": True,
            "reality_check": True,
            "screening_guidance": True,
            "document_generation": True,
            "interview_prep_guides": True,
            "outreach_templates": True,
            "pipeline_command_center": True,
            "pipeline_pattern_insights": True,
            "mock_interviews": True,
            "cross_interview_patterns": True,
            "story_bank": True,
            "rejection_forensics": True,
            "negotiation_prep": True,
            "full_negotiation_support": False,
            "live_coaching": False,
            "priority_henry": False
        }
    },
    
    "coach": {
        # Usage limits
        "applications_per_month": -1,  # Unlimited
        "fit_analyses_per_month": -1,  # Unlimited
        "resumes_per_month": -1,       # Unlimited
        "cover_letters_per_month": -1, # Unlimited
        "henry_conversations_per_month": -1,  # Unlimited
        "mock_interviews_per_month": -1,      # Unlimited
        "coaching_sessions_per_month": 2,     # Two 45-min sessions
        
        # Feature access
        "features": {
            "full_fit_analysis": True,
            "reality_check": True,
            "screening_guidance": True,
            "document_generation": True,
            "interview_prep_guides": True,
            "outreach_templates": True,
            "pipeline_command_center": True,
            "pipeline_pattern_insights": True,
            "mock_interviews": True,
            "cross_interview_patterns": True,
            "story_bank": True,
            "rejection_forensics": True,
            "negotiation_prep": True,
            "full_negotiation_support": True,
            "live_coaching": True,
            "priority_henry": True
        }
    }
}

# =============================================================================
# FEATURE METADATA (for UI display and upgrade prompts)
# =============================================================================

FEATURE_METADATA: Dict[str, Dict[str, Any]] = {
    "full_fit_analysis": {
        "display_name": "Full Fit Analysis",
        "description": "Complete breakdown of your fit score with actionable insights",
        "minimum_tier": "recruiter",
        "compute_type": "expensive"
    },
    "reality_check": {
        "display_name": "Reality Check",
        "description": "Market context, salary benchmarks, and competitive landscape",
        "minimum_tier": "recruiter",
        "compute_type": "cheap"
    },
    "screening_guidance": {
        "display_name": "Screening Question Guidance",
        "description": "Avoid auto-rejection by answering screening questions strategically",
        "minimum_tier": "recruiter",
        "compute_type": "cheap"
    },
    "document_generation": {
        "display_name": "Resume & Cover Letter Generation",
        "description": "AI-tailored documents optimized for ATS and human readers",
        "minimum_tier": "recruiter",
        "compute_type": "expensive"
    },
    "interview_prep_guides": {
        "display_name": "Interview Prep Guides",
        "description": "Company-specific prep with likely questions and talking points",
        "minimum_tier": "principal",
        "compute_type": "expensive"
    },
    "outreach_templates": {
        "display_name": "Outreach Templates",
        "description": "Personalized messages for recruiters and hiring managers",
        "minimum_tier": "principal",
        "compute_type": "medium"
    },
    "pipeline_command_center": {
        "display_name": "Pipeline Command Center",
        "description": "Track all your applications with status, priority, and next actions",
        "minimum_tier": "principal",
        "compute_type": "cheap"
    },
    "pipeline_pattern_insights": {
        "display_name": "Pipeline Pattern Insights",
        "description": "See conversion rates, weak spots, and where applications stall",
        "minimum_tier": "principal",
        "compute_type": "cheap"
    },
    "mock_interviews": {
        "display_name": "Mock Interviews",
        "description": "Practice with AI interviewer and get detailed feedback",
        "minimum_tier": "principal",
        "compute_type": "expensive"
    },
    "cross_interview_patterns": {
        "display_name": "Cross-Interview Pattern Analysis",
        "description": "Spot recurring weak areas across all your interviews",
        "minimum_tier": "partner",
        "compute_type": "cheap"
    },
    "story_bank": {
        "display_name": "Story Bank",
        "description": "Track which STAR stories land and which to retire",
        "minimum_tier": "partner",
        "compute_type": "cheap"
    },
    "rejection_forensics": {
        "display_name": "Rejection Forensics",
        "description": "Analyze rejection patterns to find the leak in your funnel",
        "minimum_tier": "partner",
        "compute_type": "medium"
    },
    "negotiation_prep": {
        "display_name": "Negotiation Prep",
        "description": "Comp benchmarks, talking points, and counter-offer strategy",
        "minimum_tier": "partner",
        "compute_type": "medium"
    },
    "full_negotiation_support": {
        "display_name": "Full Negotiation Support",
        "description": "Human-assisted strategy sessions and counter-offer drafts",
        "minimum_tier": "coach",
        "compute_type": "human"
    },
    "live_coaching": {
        "display_name": "Live Coaching Sessions",
        "description": "Two 45-minute sessions per month with a human coach",
        "minimum_tier": "coach",
        "compute_type": "human"
    },
    "priority_henry": {
        "display_name": "Priority Hey Henry",
        "description": "Faster responses and deeper context in AI coaching",
        "minimum_tier": "coach",
        "compute_type": "expensive"
    }
}

# =============================================================================
# UPGRADE TRIGGERS (for proactive upgrade prompts)
# =============================================================================

UPGRADE_TRIGGERS: Dict[str, Dict[str, Any]] = {
    "preview_to_recruiter": {
        "triggers": [
            "completed_first_analysis",
            "tried_to_generate_document",
            "tried_to_chat_with_henry"
        ],
        "message": "Unlock full fit analysis and document generation",
        "cta": "Upgrade to Recruiter"
    },
    "recruiter_to_principal": {
        "triggers": [
            "hit_application_limit",
            "hit_document_limit",
            "asked_about_interview_prep",
            "asked_about_mock_interviews",
            "has_3_plus_applications"
        ],
        "message": "Get interview prep, mock interviews, and pipeline tracking",
        "cta": "Upgrade to Principal"
    },
    "principal_to_partner": {
        "triggers": [
            "has_3_plus_debriefs",
            "asked_why_rejected",
            "hit_mock_interview_limit_twice",
            "asked_about_patterns",
            "multiple_rejections_same_stage"
        ],
        "message": "See patterns across your interviews and find your weak spots",
        "cta": "Upgrade to Partner"
    },
    "partner_to_coach": {
        "triggers": [
            "in_final_rounds",
            "has_offer",
            "asked_about_negotiation_strategy",
            "asked_for_human_help"
        ],
        "message": "Get human coaching to close your offer",
        "cta": "Upgrade to Coach"
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_tier_index(tier: str) -> int:
    """Get the index of a tier in the tier order. Lower is lower tier."""
    try:
        return TIER_ORDER.index(tier.lower())
    except ValueError:
        return 0  # Default to preview if unknown


def is_tier_at_least(user_tier: str, required_tier: str) -> bool:
    """Check if user's tier is at least the required tier."""
    return get_tier_index(user_tier) >= get_tier_index(required_tier)


def get_next_tier(current_tier: str) -> Optional[str]:
    """Get the next tier up from the current tier."""
    current_index = get_tier_index(current_tier)
    if current_index < len(TIER_ORDER) - 1:
        return TIER_ORDER[current_index + 1]
    return None


def get_tier_limit(tier: str, limit_name: str) -> int:
    """Get a specific limit for a tier. Returns 0 if not found."""
    return TIER_LIMITS.get(tier, {}).get(limit_name, 0)


def get_tier_feature(tier: str, feature_name: str) -> Any:
    """Get feature access for a tier. Returns False if not found."""
    return TIER_LIMITS.get(tier, {}).get("features", {}).get(feature_name, False)


def is_feature_available(tier: str, feature_name: str) -> bool:
    """Check if a feature is available (True or 'limited') for a tier."""
    feature_value = get_tier_feature(tier, feature_name)
    return feature_value is True or feature_value == "limited"


def is_feature_limited(tier: str, feature_name: str) -> bool:
    """Check if a feature is in limited/gated mode for a tier."""
    return get_tier_feature(tier, feature_name) == "limited"


def get_minimum_tier_for_feature(feature_name: str) -> Optional[str]:
    """Get the minimum tier required for full access to a feature."""
    return FEATURE_METADATA.get(feature_name, {}).get("minimum_tier")


def get_all_tier_info() -> Dict[str, Dict[str, Any]]:
    """Get complete tier information for API response."""
    result = {}
    for tier in TIER_ORDER:
        result[tier] = {
            "name": TIER_NAMES.get(tier, tier.title()),
            "tagline": TIER_TAGLINES.get(tier, ""),
            "description": TIER_DESCRIPTIONS.get(tier, ""),
            "price_monthly": TIER_PRICES.get(tier, 0),
            "price_annual": TIER_PRICES_ANNUAL.get(tier, 0),
            "limits": {
                k: v for k, v in TIER_LIMITS.get(tier, {}).items() 
                if k != "features"
            },
            "features": TIER_LIMITS.get(tier, {}).get("features", {})
        }
    return result


def get_upgrade_prompt(from_tier: str, trigger: str) -> Optional[Dict[str, str]]:
    """Get upgrade prompt based on trigger event."""
    to_tier = get_next_tier(from_tier)
    if not to_tier:
        return None
    
    trigger_key = f"{from_tier}_to_{to_tier}"
    trigger_config = UPGRADE_TRIGGERS.get(trigger_key, {})
    
    if trigger in trigger_config.get("triggers", []):
        return {
            "to_tier": to_tier,
            "message": trigger_config.get("message", ""),
            "cta": trigger_config.get("cta", f"Upgrade to {TIER_NAMES.get(to_tier, to_tier.title())}")
        }
    return None


# =============================================================================
# COMPUTE COST TRACKING (for internal metrics)
# =============================================================================

COMPUTE_COSTS: Dict[str, float] = {
    "expensive": 0.015,   # Full Claude call (~$0.015)
    "medium": 0.008,      # Templated/lighter Claude call
    "cheap": 0.001,       # Rules-based or cached
    "human": 50.00        # Human time (per session)
}


def estimate_feature_cost(feature_name: str) -> float:
    """Estimate the compute cost of a feature invocation."""
    compute_type = FEATURE_METADATA.get(feature_name, {}).get("compute_type", "cheap")
    return COMPUTE_COSTS.get(compute_type, 0.001)
