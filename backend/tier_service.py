"""
Tier Service for HenryHQ

This module provides helper functions for tier access control and usage tracking.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

from fastapi import HTTPException, Depends
from supabase import Client

from tier_config import (
    TIER_LIMITS,
    TIER_PRICES,
    TIER_ORDER,
    TIER_NAMES,
    NAMED_BETA_USERS,
    DEFAULT_BETA_CONFIG,
    LAUNCH_DATE,
    get_unlock_tier,
    get_tier_index,
)


class TierService:
    """Service for managing user tiers and usage limits."""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with tier information."""
        try:
            response = self.supabase.table('user_profiles').select('*').eq('id', user_id).single().execute()
            return response.data
        except Exception:
            return None

    async def ensure_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Ensure user profile exists and return it."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            # Create profile with default tier
            response = self.supabase.table('user_profiles').insert({
                'id': user_id,
                'tier': 'sourcer',
            }).execute()
            profile = response.data[0] if response.data else {'id': user_id, 'tier': 'sourcer'}
        return profile

    def get_effective_tier(self, profile: Dict[str, Any]) -> str:
        """
        Returns the user's effective tier, considering beta overrides and subscription status.

        Priority:
        1. Active beta override (not expired) → beta tier
        2. Active/past_due subscription → subscription tier
        3. Canceled subscription with time remaining → subscription tier until period ends
        4. Canceled subscription with expired period → 'preview'
        5. Default → 'preview'
        """
        # Check beta override first
        if profile.get('is_beta_user') and profile.get('beta_tier_override'):
            beta_expires = profile.get('beta_expires_at')
            if beta_expires is None:
                return profile['beta_tier_override']
            # Parse datetime if string
            if isinstance(beta_expires, str):
                beta_expires = datetime.fromisoformat(beta_expires.replace('Z', '+00:00'))
            if beta_expires > datetime.utcnow().replace(tzinfo=beta_expires.tzinfo if beta_expires.tzinfo else None):
                return profile['beta_tier_override']

        # Check subscription status
        subscription_status = profile.get('subscription_status')
        tier = profile.get('tier') or 'sourcer'

        if subscription_status == 'canceled':
            # Allow access until current_period_end
            period_end = profile.get('current_period_end')
            if period_end:
                if isinstance(period_end, str):
                    period_end = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
                if period_end > datetime.utcnow().replace(tzinfo=period_end.tzinfo if period_end.tzinfo else None):
                    return tier  # Still within paid period
            return 'sourcer'  # Period expired, downgrade to free tier

        # active, past_due, trialing all keep current tier
        return tier

    def check_feature_access(self, tier: str, feature_name: str) -> Dict[str, Any]:
        """
        Check if a tier has access to a feature.

        Returns {
            'allowed': bool,
            'limited': bool,  # True if 'limited' access (not full)
            'upgrade_to': str or None,  # Tier needed to unlock
        }
        """
        if tier not in TIER_LIMITS:
            tier = 'sourcer'

        feature_value = TIER_LIMITS[tier]['features'].get(feature_name, False)

        if feature_value is True:
            return {'allowed': True, 'limited': False, 'upgrade_to': None}
        elif feature_value == 'limited':
            return {'allowed': True, 'limited': True, 'upgrade_to': get_unlock_tier(feature_name)}
        else:
            return {'allowed': False, 'limited': False, 'upgrade_to': get_unlock_tier(feature_name)}

    async def get_or_create_current_usage(self, user_id: str) -> Dict[str, Any]:
        """Get or create usage tracking for current billing period."""
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate period end (first of next month)
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)

        # Try to get existing record
        try:
            response = self.supabase.table('usage_tracking').select('*').eq(
                'user_id', user_id
            ).eq(
                'period_start', period_start.isoformat()
            ).single().execute()
            return response.data
        except Exception:
            pass

        # Create new record
        try:
            response = self.supabase.table('usage_tracking').insert({
                'user_id': user_id,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
            }).execute()
            return response.data[0] if response.data else {
                'user_id': user_id,
                'applications_used': 0,
                'resumes_generated': 0,
                'cover_letters_generated': 0,
                'henry_conversations_used': 0,
                'mock_interviews_used': 0,
                'coaching_sessions_used': 0,
            }
        except Exception:
            return {
                'user_id': user_id,
                'applications_used': 0,
                'resumes_generated': 0,
                'cover_letters_generated': 0,
                'henry_conversations_used': 0,
                'mock_interviews_used': 0,
                'coaching_sessions_used': 0,
            }

    async def check_usage_limit(self, user_id: str, tier: str, usage_type: str) -> Dict[str, Any]:
        """
        Check if user has remaining usage for a type.

        Returns {
            'allowed': bool,
            'used': int,
            'limit': int,  # -1 means unlimited/strategic
            'remaining': int or None,
            'is_unlimited': bool,
        }
        """
        limit_key = f'{usage_type}_per_month'
        limit = TIER_LIMITS.get(tier, TIER_LIMITS['sourcer']).get(limit_key, 0)

        # Get current period usage
        usage = await self.get_or_create_current_usage(user_id)
        used_key = f'{usage_type}_used' if usage_type != 'resumes' else 'resumes_generated'
        if usage_type == 'cover_letters':
            used_key = 'cover_letters_generated'
        used = usage.get(used_key, 0)

        if limit == -1:  # Unlimited/strategic
            return {
                'allowed': True,
                'used': used,
                'limit': -1,
                'remaining': None,
                'is_unlimited': True,
            }

        remaining = max(0, limit - used)
        return {
            'allowed': used < limit,
            'used': used,
            'limit': limit,
            'remaining': remaining,
            'is_unlimited': False,
        }

    async def increment_usage(self, user_id: str, usage_type: str) -> None:
        """Increment usage counter for the current billing period."""
        usage = await self.get_or_create_current_usage(user_id)

        # Map usage type to field name
        field_map = {
            'applications': 'applications_used',
            'resumes': 'resumes_generated',
            'cover_letters': 'cover_letters_generated',
            'henry_conversations': 'henry_conversations_used',
            'mock_interviews': 'mock_interviews_used',
            'coaching_sessions': 'coaching_sessions_used',
        }

        field = field_map.get(usage_type)
        if not field:
            return

        current = usage.get(field, 0)
        self.supabase.table('usage_tracking').update({
            field: current + 1
        }).eq('id', usage['id']).execute()

    def get_upgrade_prompt(self, current_tier: str, feature_name: str = None, usage_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Returns upgrade messaging for paywalls.
        """
        current_index = get_tier_index(current_tier)

        # Find next tier up
        if current_index < len(TIER_ORDER) - 1:
            next_tier = TIER_ORDER[current_index + 1]
            return {
                'upgrade_to': next_tier,
                'upgrade_name': TIER_NAMES[next_tier],
                'price': TIER_PRICES[next_tier],
                'message': f'Upgrade to {TIER_NAMES[next_tier]} to unlock this feature',
            }

        return None

    async def get_user_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """Get complete usage summary for a user."""
        profile = await self.ensure_user_profile(user_id)
        tier = self.get_effective_tier(profile)
        limits = TIER_LIMITS.get(tier, TIER_LIMITS['sourcer'])

        usage_types = [
            'applications',
            'resumes',
            'cover_letters',
            'henry_conversations',
            'mock_interviews',
            'coaching_sessions'
        ]

        usage_stats = {}
        for usage_type in usage_types:
            usage_stats[usage_type] = await self.check_usage_limit(user_id, tier, usage_type)

        return {
            'tier': tier,
            'tier_display': TIER_NAMES.get(tier, 'Sourcer'),
            'tier_price': TIER_PRICES.get(tier, 0),
            'is_beta_user': profile.get('is_beta_user', False),
            'beta_expires_at': profile.get('beta_expires_at'),
            'usage': usage_stats,
            'features': limits.get('features', {}),
        }


def require_feature(feature_name: str):
    """Decorator to protect endpoints by feature access."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, tier_service: TierService = None, user_id: str = None, **kwargs):
            if not tier_service or not user_id:
                raise HTTPException(status_code=401, detail='Authentication required')

            profile = await tier_service.ensure_user_profile(user_id)
            tier = tier_service.get_effective_tier(profile)
            access = tier_service.check_feature_access(tier, feature_name)

            if not access['allowed']:
                raise HTTPException(
                    status_code=403,
                    detail={
                        'error': 'feature_locked',
                        'feature': feature_name,
                        'upgrade_to': access['upgrade_to'],
                        'message': f'Upgrade to {TIER_NAMES.get(access["upgrade_to"], "a higher tier")} to access this feature'
                    }
                )
            return await func(*args, tier_service=tier_service, user_id=user_id, **kwargs)
        return wrapper
    return decorator


def require_usage(usage_type: str):
    """Decorator to check and increment usage limits."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, tier_service: TierService = None, user_id: str = None, **kwargs):
            if not tier_service or not user_id:
                raise HTTPException(status_code=401, detail='Authentication required')

            profile = await tier_service.ensure_user_profile(user_id)
            tier = tier_service.get_effective_tier(profile)
            usage = await tier_service.check_usage_limit(user_id, tier, usage_type)

            if not usage['allowed']:
                raise HTTPException(
                    status_code=429,
                    detail={
                        'error': 'limit_reached',
                        'usage_type': usage_type,
                        'used': usage['used'],
                        'limit': usage['limit'],
                        'message': f'Monthly limit reached ({usage["used"]}/{usage["limit"]}). Upgrade for more.'
                    }
                )

            # Execute function
            result = await func(*args, tier_service=tier_service, user_id=user_id, **kwargs)

            # Increment usage after successful execution
            await tier_service.increment_usage(user_id, usage_type)

            return result
        return wrapper
    return decorator


async def migrate_beta_users(supabase: Client):
    """
    Migration script to set beta user flags.
    Run once before launch.
    """
    from datetime import timedelta

    # Get all users who signed up before launch
    response = supabase.auth.admin.list_users()
    users = response.users if hasattr(response, 'users') else []

    for user in users:
        created_at = user.created_at
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        if created_at < LAUNCH_DATE.replace(tzinfo=created_at.tzinfo if created_at.tzinfo else None):
            email = user.email

            # Check if named beta user
            if email in NAMED_BETA_USERS:
                config = NAMED_BETA_USERS[email]
                supabase.table('user_profiles').upsert({
                    'id': user.id,
                    'is_beta_user': True,
                    'beta_tier_override': config['tier'],
                    'beta_expires_at': config['expires'],
                    'beta_discount_percent': config['discount_after'],
                }).execute()
            else:
                # Default beta config
                expires_at = LAUNCH_DATE + timedelta(days=DEFAULT_BETA_CONFIG['expires_days_after_launch'])
                supabase.table('user_profiles').upsert({
                    'id': user.id,
                    'is_beta_user': True,
                    'beta_tier_override': DEFAULT_BETA_CONFIG['tier'],
                    'beta_expires_at': expires_at.isoformat(),
                    'beta_discount_percent': DEFAULT_BETA_CONFIG['discount_after'],
                }).execute()

    print(f"Migrated {len(users)} beta users")
