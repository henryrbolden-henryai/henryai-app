"""
Tier Configuration for HenryHQ

This module defines the subscription tiers, their prices, limits, and feature access.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Tier prices in USD per month
TIER_PRICES = {
    'sourcer': 0,
    'recruiter': 25,
    'principal': 69,
    'partner': 129,
    'coach': 225,
}

# Tier order for comparison
TIER_ORDER = ['sourcer', 'recruiter', 'principal', 'partner', 'coach']

# Tier display names
TIER_NAMES = {
    'sourcer': 'Sourcer',
    'recruiter': 'Recruiter',
    'principal': 'Principal',
    'partner': 'Partner',
    'coach': 'Coach',
}

# Tier limits configuration
# -1 means unlimited/strategic
TIER_LIMITS = {
    'sourcer': {
        'applications_per_month': 3,
        'resumes_per_month': 3,
        'cover_letters_per_month': 3,
        'henry_conversations_per_month': 0,
        'mock_interviews_per_month': 0,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': False,
            'outreach_templates': False,
            'application_tracker': False,
            'company_intelligence': False,
            'linkedin_recommendations': False,
            'linkedin_optimization': False,
            'interview_prep_full': False,
            'interview_prep_limited': False,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': False,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': False,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': False,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'recruiter': {
        'applications_per_month': 15,
        'resumes_per_month': 15,
        'cover_letters_per_month': 15,
        'henry_conversations_per_month': 15,
        'mock_interviews_per_month': 1,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': 'limited',
            'application_tracker': True,
            'company_intelligence': False,
            'linkedin_recommendations': False,
            'linkedin_optimization': False,
            'interview_prep_full': False,
            'interview_prep_limited': True,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': False,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': True,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': False,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'principal': {
        'applications_per_month': 30,
        'resumes_per_month': 30,
        'cover_letters_per_month': 30,
        'henry_conversations_per_month': 30,
        'mock_interviews_per_month': 5,
        'coaching_sessions_per_month': 0,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': False,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': False,
            'story_bank': False,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': True,
            'negotiation_guidance': False,
            'negotiation_full': False,
            'conversation_memory': False,
            'dashboard_full': True,
            'dashboard_insights': False,
            'dashboard_benchmarking': False,
            'application_alerts': True,
            'career_level_assessment': False,
            'live_coaching': False,
        }
    },
    'partner': {
        'applications_per_month': -1,  # Unlimited/strategic
        'resumes_per_month': -1,
        'cover_letters_per_month': -1,
        'henry_conversations_per_month': -1,
        'mock_interviews_per_month': 10,
        'coaching_sessions_per_month': 1,
        'coaching_session_minutes': 30,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': True,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': True,
            'story_bank': True,
            'pattern_analysis': False,
            'rejection_forensics': False,
            'salary_benchmarking': True,
            'negotiation_guidance': True,
            'negotiation_full': False,
            'conversation_memory': True,
            'dashboard_full': True,
            'dashboard_insights': True,
            'dashboard_benchmarking': False,
            'application_alerts': True,
            'career_level_assessment': False,
            'live_coaching': True,
        }
    },
    'coach': {
        'applications_per_month': -1,
        'resumes_per_month': -1,
        'cover_letters_per_month': -1,
        'henry_conversations_per_month': -1,
        'mock_interviews_per_month': -1,
        'coaching_sessions_per_month': 2,
        'coaching_session_minutes': 45,
        'features': {
            'job_fit_analysis': True,
            'linkedin_analysis': True,
            'interview_debrief': True,
            'dashboard_core': True,
            'ats_optimization': True,
            'screening_questions': True,
            'outreach_templates': True,
            'application_tracker': True,
            'company_intelligence': True,
            'linkedin_recommendations': True,
            'linkedin_optimization': True,
            'interview_prep_full': True,
            'interview_prep_limited': True,
            'document_refinement': True,
            'story_bank': True,
            'pattern_analysis': True,
            'rejection_forensics': True,
            'salary_benchmarking': True,
            'negotiation_guidance': True,
            'negotiation_full': True,
            'conversation_memory': True,
            'dashboard_full': True,
            'dashboard_insights': True,
            'dashboard_benchmarking': True,
            'application_alerts': True,
            'career_level_assessment': True,
            'live_coaching': True,
        }
    },
}

# Beta user configuration
# Named beta users with permanent access
NAMED_BETA_USERS = {
    # Identify by email - update these with actual emails
    # 'jordan@example.com': {
    #     'tier': 'coach',
    #     'expires': None,  # Never expires
    #     'discount_after': 0,
    # },
    # 'adam@example.com': {
    #     'tier': 'coach',
    #     'expires': None,
    #     'discount_after': 0,
    # },
    # 'alex@example.com': {
    #     'tier': 'partner',
    #     'expires': None,
    #     'discount_after': 0,
    # },
    # 'darnel@example.com': {
    #     'tier': 'coach',
    #     'expires': None,
    #     'discount_after': 0,
    # },
}

# Default beta user config for non-named beta users
DEFAULT_BETA_CONFIG = {
    'tier': 'partner',
    'expires_days_after_launch': 90,  # 3 months from launch
    'discount_after': 0,  # No discount after expiration
}

# Launch date - update this before launch
LAUNCH_DATE = datetime(2025, 1, 15)


def get_tier_index(tier: str) -> int:
    """Get the index of a tier in the tier order."""
    try:
        return TIER_ORDER.index(tier)
    except ValueError:
        return 0  # Default to sourcer


def is_tier_higher_or_equal(tier_a: str, tier_b: str) -> bool:
    """Check if tier_a is higher or equal to tier_b."""
    return get_tier_index(tier_a) >= get_tier_index(tier_b)


def get_unlock_tier(feature_name: str) -> Optional[str]:
    """Find the lowest tier that fully unlocks a feature."""
    for tier in TIER_ORDER:
        feature_value = TIER_LIMITS[tier]['features'].get(feature_name)
        if feature_value is True:
            return tier
    return 'coach'  # Default to highest tier


def get_tier_features(tier: str) -> Dict[str, Any]:
    """Get the features configuration for a tier."""
    if tier not in TIER_LIMITS:
        tier = 'sourcer'
    return TIER_LIMITS[tier]['features']


def get_tier_limit(tier: str, limit_type: str) -> int:
    """Get a specific limit for a tier."""
    if tier not in TIER_LIMITS:
        tier = 'sourcer'
    return TIER_LIMITS[tier].get(limit_type, 0)


def get_all_tier_info() -> List[Dict[str, Any]]:
    """Get information about all tiers for display."""
    return [
        {
            'id': tier,
            'name': TIER_NAMES[tier],
            'price': TIER_PRICES[tier],
            'limits': {k: v for k, v in TIER_LIMITS[tier].items() if k != 'features'},
            'features': TIER_LIMITS[tier]['features'],
        }
        for tier in TIER_ORDER
    ]
